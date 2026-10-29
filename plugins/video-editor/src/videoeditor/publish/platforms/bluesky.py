"""Bluesky: app password -> PDS session -> video.bsky.app upload -> post record with a video embed.

Lexicons used (canonical source: github.com/bluesky-social/social-app/lexicons): app.bsky.video.uploadVideo
(input video/mp4, returns jobStatus), app.bsky.video.getJobStatus, app.bsky.video.getUploadLimits,
app.bsky.embed.video (mp4, max 300 MB), app.bsky.feed.post (300 graphemes), com.atproto.server.createSession /
getServiceAuth, com.atproto.repo.createRecord. The service-auth audience (did:web of the user's PDS) and
lxm (com.atproto.repo.uploadBlob) follow Bluesky's own client and are not spelled out in the lexicons.
Bluesky has no private or draft posts, so this platform can only be used with an explicit public opt-in.
"""
from __future__ import annotations

import getpass
import re
import time
import urllib.parse
from pathlib import Path

from videoeditor.publish import net as http, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import poll, utc_now_iso

VIDEO_HOST = "https://video.bsky.app"
VIDEO_AUD = "did:web:video.bsky.app"
SPEC = Spec(
    name="bluesky", title="Bluesky", modes=("public",),
    draft_note="none: Bluesky has no private or draft posts",
    max_caption=300, soft_limits=("caption",),          # 300 is graphemes; len() here counts code points
    max_bytes=300_000_000, extensions=(".mp4",),
    docs=("https://atproto.com/guides/video-handling",),
)


def hashtag_facets(text: str) -> list[dict]:
    """app.bsky.richtext.facet tag facets. Indices are UTF-8 byte offsets."""
    facets = []
    for m in re.finditer(r"(?<![\w&])#([^\s\d\W][\w]*)", text):
        start = len(text[:m.start()].encode())
        end = start + len(m.group(0).encode())
        facets.append({"index": {"byteStart": start, "byteEnd": end},
                       "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]})
    return facets


def pds_from_session(session: dict, fallback: str) -> str:
    for svc in (session.get("didDoc") or {}).get("service", []) or []:
        if str(svc.get("id", "")).endswith("#atproto_pds") and svc.get("serviceEndpoint"):
            return svc["serviceEndpoint"].rstrip("/")
    return fallback.rstrip("/")


class Bluesky(Publisher):
    spec = SPEC

    def is_configured(self) -> bool:
        return bool(secrets.get("bluesky", "identifier") and secrets.get("bluesky", "app_password"))

    def auth_help(self) -> str:
        return "Create an APP PASSWORD (not your main password): Bluesky > Settings > Privacy and security > App passwords."

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        return ["com.atproto.server.createSession (app password)",
                "com.atproto.server.getServiceAuth for the video service, then app.bsky.video.getUploadLimits",
                "POST video.bsky.app app.bsky.video.uploadVideo, poll getJobStatus until JOB_STATE_COMPLETED",
                "com.atproto.repo.createRecord: app.bsky.feed.post with an app.bsky.embed.video (PUBLIC, cannot be private)"]

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        ask_secret = ask_secret or getpass.getpass
        say(self.auth_help())
        ident = ask("Handle or email: ").strip()
        pw = ask_secret("App password (hidden): ").strip()
        try:
            secrets.set("bluesky", "identifier", ident)
            secrets.set("bluesky", "app_password", pw)
        except RuntimeError as e:
            return str(e)
        s = self._session(self._service())
        return f"saved; logged in as {s.get('handle')}"

    def _service(self) -> str:
        return (secrets.get("bluesky", "service") or "https://bsky.social").rstrip("/")

    def _session(self, service: str) -> dict:
        ident, pw = secrets.get("bluesky", "identifier"), secrets.get("bluesky", "app_password")
        if not ident or not pw:
            raise AuthError("bluesky: not configured. Run `ve publish init bluesky` "
                            "(or set VE_BLUESKY_IDENTIFIER and VE_BLUESKY_APP_PASSWORD).")
        return http.request("bluesky", "POST", f"{service}/xrpc/com.atproto.server.createSession",
                            json={"identifier": ident, "password": pw}, ok=(200,), retries=1).json()

    def _service_auth(self, pds: str, jwt: str, aud: str, lxm: str) -> str:
        q = urllib.parse.urlencode({"aud": aud, "lxm": lxm, "exp": int(time.time()) + 1800})
        r = http.request("bluesky", "GET", f"{pds}/xrpc/com.atproto.server.getServiceAuth?{q}",
                         headers={"Authorization": f"Bearer {jwt}"}, ok=(200,))
        return r.json()["token"]

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        service = self._service()
        sess = self._session(service)
        did, jwt = sess["did"], sess["accessJwt"]
        pds = pds_from_session(sess, service)
        host = urllib.parse.urlparse(pds).hostname

        # 1. daily limits (best effort: a failure here should not block an otherwise valid upload)
        try:
            tok = self._service_auth(pds, jwt, VIDEO_AUD, "app.bsky.video.getUploadLimits")
            lim = http.request("bluesky", "GET", f"{VIDEO_HOST}/xrpc/app.bsky.video.getUploadLimits",
                               headers={"Authorization": f"Bearer {tok}"}, ok=(200,), retries=0).json()
            if lim.get("canUpload") is False:
                raise PublishError(f"bluesky: video uploads are not allowed right now: {lim.get('message') or lim.get('error')}")
        except PublishError as e:
            if "not allowed right now" in str(e):
                raise
        except Exception:
            pass

        # 2. upload to the video service with a token bound to the PDS blob upload
        token = self._service_auth(pds, jwt, f"did:web:{host}", "com.atproto.repo.uploadBlob")
        video = Path(pkg.video)
        with open(video, "rb") as f:
            up = http.request("bluesky", "POST", f"{VIDEO_HOST}/xrpc/app.bsky.video.uploadVideo",
                              params={"did": did, "name": video.name},
                              headers={"Authorization": f"Bearer {token}", "Content-Type": "video/mp4"},
                              data=f, ok=(200, 409), retries=0, timeout=900)
        job = up.json().get("jobStatus") or up.json()
        job_id = job.get("jobId")
        if not job_id:
            raise PublishError(f"bluesky: upload returned no job id: {str(up.text)[:200]}")

        def status():
            return http.request("bluesky", "GET", f"{VIDEO_HOST}/xrpc/app.bsky.video.getJobStatus",
                                params={"jobId": job_id}, ok=(200,)).json()["jobStatus"]

        job = poll(status, lambda j: j.get("state") in ("JOB_STATE_COMPLETED", "JOB_STATE_FAILED") or j.get("blob"),
                   interval=2, timeout=600)
        if job.get("state") == "JOB_STATE_FAILED" or job.get("error"):
            raise PublishError(f"bluesky: video processing failed: {job.get('failureCode') or job.get('error')} "
                               f"{job.get('message') or ''}".strip())
        blob = job.get("blob")
        if not blob:
            raise PublishError(f"bluesky: video still processing after 10 minutes (job {job_id}); not posted")

        # 3. the post
        text = pkg.full_text("bluesky")
        embed = {"$type": "app.bsky.embed.video", "video": blob}
        if pkg.alt_text:
            embed["alt"] = pkg.alt_text
        if pkg.info.get("width") and pkg.info.get("height"):
            embed["aspectRatio"] = {"width": int(pkg.info["width"]), "height": int(pkg.info["height"])}
        record = {"$type": "app.bsky.feed.post", "text": text, "createdAt": utc_now_iso(), "embed": embed}
        facets = hashtag_facets(text)
        if facets:
            record["facets"] = facets
        res = http.request("bluesky", "POST", f"{pds}/xrpc/com.atproto.repo.createRecord",
                           headers={"Authorization": f"Bearer {jwt}"}, ok=(200,),
                           json={"repo": did, "collection": "app.bsky.feed.post", "record": record}).json()
        rkey = res["uri"].rsplit("/", 1)[-1]
        return Result("bluesky", mode, "ok", id=res["uri"], url=f"https://bsky.app/profile/{did}/post/{rkey}")


PUBLISHER = Bluesky
