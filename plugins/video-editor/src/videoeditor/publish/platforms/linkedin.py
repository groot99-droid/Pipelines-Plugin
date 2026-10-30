"""LinkedIn (personal profile): Videos API + Posts API with the w_member_social scope.

Docs (learn.microsoft.com/linkedin/marketing/community-management/shares/videos-api and posts-api): create upload
-> PUT 4 MB parts and keep each ETag -> finalize -> POST /rest/posts. Posts can only be created as PUBLISHED, so
LinkedIn has no draft; "draft" mode here means connections-only visibility. Access tokens last 60 days and
self-serve apps get no refresh token: run `ve publish init linkedin` again when it expires. The token exchange
needs the client secret; PKCE is not documented. The redirect URI must be one registered on the app, so
`ve publish init linkedin --manual` lets you paste it back instead of listening on localhost.
"""
from __future__ import annotations

import os
import re
import urllib.parse

from videoeditor.publish import net as http, oauth, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import poll

API = "https://api.linkedin.com"
VERSION = "202610"                    # Linkedin-Version header (YYYYMM); older months are sunset on a schedule
PART = 4 * 1024 * 1024
SPEC = Spec(
    name="linkedin", title="LinkedIn", modes=("draft", "public"),
    draft_note="connections-only visibility (LinkedIn has no draft state for API posts)",
    max_caption=3000, soft_limits=("caption",), extensions=(".mp4",), orientation="any",
    docs=("https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api",),
)
_LITTLE_RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")


def little_escape(text: str) -> str:
    """Posts API commentary uses the 'little' text format: reserved characters must be backslash-escaped."""
    return _LITTLE_RESERVED.sub(r"\\\1", text)


def oauth_config(client_id: str, client_secret: str | None) -> oauth.OAuthConfig:
    return oauth.OAuthConfig(
        platform="linkedin", auth_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken", client_id=client_id, client_secret=client_secret,
        scopes=["openid", "profile", "w_member_social"], pkce=False)


class LinkedIn(Publisher):
    spec = SPEC

    def _cfg(self) -> oauth.OAuthConfig:
        cid = secrets.get("linkedin", "client_id")
        if not cid:
            raise AuthError("linkedin: not configured. Run `ve publish init linkedin`.")
        return oauth_config(cid, secrets.get("linkedin", "client_secret"))

    def is_configured(self) -> bool:
        return oauth.load_token("linkedin") is not None

    def auth_help(self) -> str:
        return ("developer.linkedin.com: create an app, add the products 'Share on LinkedIn' and 'Sign In with LinkedIn "
                "using OpenID Connect', and register a redirect URL.")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        say(self.auth_help())
        redirect = ask("Redirect URL registered on the app (Enter to use a localhost listener): ").strip() if manual else None
        return oauth.run_init("linkedin", oauth_config, ask=ask, ask_secret=ask_secret, say=say,
                              manual=manual, port=port, redirect_uri=redirect or "http://127.0.0.1:8080/", needs_secret=True)

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        vis = "PUBLIC" if mode == "public" else "CONNECTIONS"
        return ["GET /v2/userinfo (member id)",
                f"POST /rest/videos?action=initializeUpload, PUT {PART // 1048576} MB parts, finalizeUpload",
                f"POST /rest/posts (visibility={vis}, lifecycleState=PUBLISHED; text is escaped for the 'little' format)"]

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Linkedin-Version": os.environ.get("VE_LINKEDIN_VERSION", VERSION),
                "X-Restli-Protocol-Version": "2.0.0"}

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        token = oauth.access_token(self._cfg())
        h = self._headers(token)
        person = os.environ.get("VE_LINKEDIN_PERSON_ID")
        if not person:
            me = http.request("linkedin", "GET", f"{API}/v2/userinfo", headers={"Authorization": f"Bearer {token}"}, ok=(200,)).json()
            person = me["sub"]       # assumed to be the id used in urn:li:person (override with VE_LINKEDIN_PERSON_ID)
        author = f"urn:li:person:{person}"
        total = pkg.info["bytes"]
        init = http.request("linkedin", "POST", f"{API}/rest/videos?action=initializeUpload", headers=h, ok=(200,),
                            json={"initializeUploadRequest": {"owner": author, "fileSizeBytes": total,
                                                              "uploadCaptions": False, "uploadThumbnail": False}}).json()["value"]
        etags = []
        with open(pkg.video, "rb") as f:
            for ins in init["uploadInstructions"]:
                f.seek(ins["firstByte"])
                block = f.read(ins["lastByte"] - ins["firstByte"] + 1)
                r = http.request("linkedin", "PUT", ins["uploadUrl"], data=block, ok=(200,), timeout=300,
                                 headers={"Content-Type": "application/octet-stream"})
                etag = r.headers.get("ETag") or r.headers.get("etag")
                if not etag:
                    raise PublishError("linkedin: a part upload returned no ETag; cannot finalize")
                etags.append(etag)
        http.request("linkedin", "POST", f"{API}/rest/videos?action=finalizeUpload", headers=h, ok=(200,),
                     json={"finalizeUploadRequest": {"video": init["video"], "uploadToken": init.get("uploadToken", ""),
                                                     "uploadedPartIds": etags}})
        urn = init["video"]

        def status():
            try:
                return http.request("linkedin", "GET", f"{API}/rest/videos/{urllib.parse.quote(urn, safe='')}",
                                    headers=h, ok=(200,), retries=0).json().get("status")
            except PublishError:
                return "UNKNOWN"      # status endpoint trouble should not block the post attempt

        st = poll(status, lambda s: s in ("AVAILABLE", "PROCESSING_FAILED", "UNKNOWN"), interval=5, timeout=300)
        if st == "PROCESSING_FAILED":
            raise PublishError("linkedin: video processing failed")
        media = {"id": urn}
        if pkg.for_platform("linkedin")["title"]:
            media["title"] = pkg.for_platform("linkedin")["title"]
        if pkg.alt_text:
            media["altText"] = pkg.alt_text
        body = {"author": author, "commentary": little_escape(pkg.full_text("linkedin")),
                "visibility": "PUBLIC" if mode == "public" else "CONNECTIONS",
                "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
                "content": {"media": media}, "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
        r = http.request("linkedin", "POST", f"{API}/rest/posts", headers=h, ok=(201,), json=body)
        post = r.headers.get("x-restli-id") or r.headers.get("X-RestLi-Id")
        return Result("linkedin", mode, "ok", id=post, url=f"https://www.linkedin.com/feed/update/{post}/" if post else None,
                      note=f"visibility={body['visibility']}; video status {st}")


PUBLISHER = LinkedIn
