"""Instagram Reels through the Instagram Graph API (professional account + a Meta app).

Flow (developers.facebook.com/docs/instagram-platform/content-publishing): create a REELS media container, upload
the file (resumable upload to rupload.facebook.com, or a public `video_url` you supply), poll the container until
FINISHED, then media_publish. The API has no draft or private state; the nearest thing is the unpublished container
(expires after 24 hours), so "draft" mode stops after the container is ready and publishes nothing.
Auth: a long-lived access token and your Instagram user id, from the environment or the OS keyring (the Meta
login/app-review flow is not automated here). Graph API version is v26.0 in the current docs (VE_INSTAGRAM_GRAPH to change).
"""
from __future__ import annotations

import getpass
import os

from videoeditor.publish import net as http, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import poll

GRAPH = "https://graph.facebook.com/v26.0"
SPEC = Spec(
    name="instagram", title="Instagram Reels", modes=("draft", "public"),
    draft_note="container only: the Reel is uploaded and checked but NOT published; the container expires in 24 hours",
    gated_note="the account must be a professional (Business/Creator) account; other people's accounts need Meta app review",
    max_caption=2200, min_duration_s=3, max_duration_s=900, max_bytes=300_000_000, extensions=(".mp4", ".mov"),
    orientation="prefer-vertical", docs=("https://developers.facebook.com/docs/instagram-platform/content-publishing",),
)


class Instagram(Publisher):
    spec = SPEC

    def _creds(self) -> tuple[str, str, str]:
        tok, uid = secrets.get("instagram", "token"), secrets.get("instagram", "user_id")
        if not tok or not uid:
            raise AuthError("instagram: not configured. Run `ve publish init instagram` "
                            "(or set VE_INSTAGRAM_TOKEN and VE_INSTAGRAM_USER_ID).")
        return tok, uid, os.environ.get("VE_INSTAGRAM_GRAPH", GRAPH).rstrip("/")

    def is_configured(self) -> bool:
        return bool(secrets.get("instagram", "token") and secrets.get("instagram", "user_id"))

    def auth_help(self) -> str:
        return ("Needs an Instagram professional account and a Meta app with instagram_content_publish (Business Login "
                "variant: instagram_business_content_publish). Generate a long-lived access token (about 60 days) and note "
                "your Instagram user id in the Meta developer dashboard.")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        ask_secret = ask_secret or getpass.getpass
        say(self.auth_help())
        uid = ask("Instagram user id: ").strip()
        tok = ask_secret("Long-lived access token (hidden): ").strip()
        try:
            secrets.set("instagram", "user_id", uid)
            secrets.set("instagram", "token", tok)
        except RuntimeError as e:
            return str(e)
        return "saved (token lasts about 60 days; refresh it before it expires)"

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        steps = [f"POST {GRAPH}/<user-id>/media (media_type=REELS, upload_type=resumable, caption)",
                 "POST the file to the returned rupload.facebook.com URI (offset 0, file_size)",
                 "poll GET /<container-id>?fields=status_code until FINISHED (the docs advise one check a minute for up to 5)"]
        steps.append("POST /<user-id>/media_publish (PUBLIC)" if mode == "public"
                     else "stop here: nothing is published (container expires in 24 h)")
        return steps

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None, interval: float = 60,
             max_polls: int = 5) -> Result:
        token, uid, graph = self._creds()
        body = {"access_token": token, "media_type": "REELS", "caption": pkg.full_text("instagram")}
        if pkg.ai_generated:
            body["is_ai_generated"] = "true"
        video_url = os.environ.get("VE_INSTAGRAM_VIDEO_URL")
        if video_url:                     # you host the file; Meta fetches it
            body["video_url"] = video_url
        else:
            body["upload_type"] = "resumable"
        c = http.request("instagram", "POST", f"{graph}/{uid}/media", data=body, ok=(200,)).json()
        cid = c["id"]
        if not video_url:
            uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/v26.0/{cid}"
            with open(pkg.video, "rb") as f:
                http.request("instagram", "POST", uri, data=f, ok=(200,), retries=0, timeout=900,
                             headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(pkg.info["bytes"])})

        def status():
            return http.request("instagram", "GET", f"{graph}/{cid}", params={"fields": "status_code", "access_token": token},
                                ok=(200,)).json().get("status_code")

        n = {"i": 0}

        def check():
            n["i"] += 1
            return status()

        st = poll(check, lambda s: s in ("FINISHED", "ERROR", "EXPIRED") or n["i"] >= max_polls, interval=interval,
                  timeout=1e9)      # the poll count, not the clock, ends this loop
        if st in ("ERROR", "EXPIRED"):
            raise PublishError(f"instagram: container {cid} ended in {st}")
        if st != "FINISHED":
            raise PublishError(f"instagram: container {cid} is still {st} after {max_polls} checks; re-check it later "
                               "(nothing was published)")
        if mode == "draft":
            return Result("instagram", mode, "draft", id=cid, note="container ready, NOT published; expires in 24 hours. "
                                                                   "Re-run with --public --yes to publish.")
        pub = http.request("instagram", "POST", f"{graph}/{uid}/media_publish",
                           data={"creation_id": cid, "access_token": token}, ok=(200,)).json()
        return Result("instagram", mode, "ok", id=pub.get("id"), note="published")


PUBLISHER = Instagram
