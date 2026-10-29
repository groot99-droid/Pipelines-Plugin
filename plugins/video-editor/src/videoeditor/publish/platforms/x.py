"""X (Twitter) API v2: chunked video upload (/2/media/upload/initialize|append|finalize) then POST /2/tweets.

Docs: docs.x.com/x-api/media/quickstart/media-upload-chunked and /x-api/posts/create-post. X has no private or
draft mode and the API is pay-per-use (the pricing page lists $0.015 per post and $0.20 per post with a URL; whether
media upload calls are billed is not documented), so this platform needs BOTH --public and --accept-cost.
"""
from __future__ import annotations

from videoeditor.publish import net as http, oauth, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import poll, read_chunks

API = "https://api.x.com"
SEGMENT = 5 * 1024 * 1024         # docs: keep segments at or below 5 MB (server maximum 8 MB)
SPEC = Spec(
    name="x", title="X", modes=("public",), draft_note="none: X has no private or draft posts",
    cost_note="pay-per-use: about $0.015 per post, $0.20 if the post contains a URL (X pricing page)",
    max_caption=280, max_duration_s=1200, max_bytes=8 * 1024**3, soft_limits=("caption", "duration", "bytes"),
    extensions=(".mp4",), docs=("https://docs.x.com/x-api/posts/create-post",),
)


def oauth_config(client_id: str, client_secret: str | None) -> oauth.OAuthConfig:
    return oauth.OAuthConfig(
        platform="x", auth_url="https://x.com/i/oauth2/authorize", token_url=f"{API}/2/oauth2/token",
        client_id=client_id, client_secret=client_secret, scopes=["tweet.read", "tweet.write", "users.read", "media.write", "offline.access"],
        token_auth="basic" if client_secret else "body")


class X(Publisher):
    spec = SPEC

    def _cfg(self) -> oauth.OAuthConfig:
        cid = secrets.get("x", "client_id")
        if not cid:
            raise AuthError("x: not configured. Run `ve publish init x`.")
        return oauth_config(cid, secrets.get("x", "client_secret"))

    def is_configured(self) -> bool:
        return oauth.load_token("x") is not None

    def auth_help(self) -> str:
        return ("developer.x.com console: create an app with OAuth 2.0 user authentication, a localhost-style callback URL "
                "(http://127.0.0.1:PORT/callback) and buy API credits. Confidential apps also have a client secret.")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        say(self.auth_help())
        return oauth.run_init("x", oauth_config, ask=ask, ask_secret=ask_secret, say=say, manual=manual, port=port,
                              redirect_uri="http://127.0.0.1:8080/callback")

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        n = max(1, -(-pkg.info["bytes"] // SEGMENT))
        return [f"POST {API}/2/media/upload/initialize (video/mp4, tweet_video)",
                f"POST /2/media/upload/<id>/append x {n} segment(s) of up to {SEGMENT // 1048576} MB",
                "POST /2/media/upload/<id>/finalize, poll GET /2/media/upload?command=STATUS until succeeded",
                f"POST {API}/2/tweets (PUBLIC; COSTS MONEY: {SPEC.cost_note})"]

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        h = {"Authorization": f"Bearer {oauth.access_token(self._cfg())}"}
        total = pkg.info["bytes"]
        init = http.request("x", "POST", f"{API}/2/media/upload/initialize", headers=h, ok=(200, 201),
                            json={"media_type": "video/mp4", "total_bytes": total, "media_category": "tweet_video"}).json()["data"]
        mid = init["id"]
        for i, (_, block) in enumerate(read_chunks(pkg.video, SEGMENT)):
            http.request("x", "POST", f"{API}/2/media/upload/{mid}/append", headers=h, ok=(200, 201, 204), timeout=300,
                         data={"segment_index": str(i)}, files={"media": ("chunk", block, "application/octet-stream")})
        fin = http.request("x", "POST", f"{API}/2/media/upload/{mid}/finalize", headers=h, ok=(200, 201)).json().get("data", {})
        info = fin.get("processing_info")
        if info and info.get("state") != "succeeded":
            def status():
                d = http.request("x", "GET", f"{API}/2/media/upload", headers=h, ok=(200,),
                                 params={"command": "STATUS", "media_id": mid}).json().get("data", {})
                return d.get("processing_info") or {"state": "succeeded"}

            info = poll(status, lambda p: p.get("state") in ("succeeded", "failed"), interval=max(2, info.get("check_after_secs", 5)),
                        timeout=600)
            if info.get("state") != "succeeded":
                raise PublishError(f"x: video processing {info.get('state')}: {info.get('error') or ''}".strip())
        body = {"text": pkg.full_text("x"), "media": {"media_ids": [mid]}}
        if pkg.ai_generated:
            body["made_with_ai"] = True
        if pkg.branded_content:
            body["paid_partnership"] = True
        t = http.request("x", "POST", f"{API}/2/tweets", headers=h, ok=(201,), json=body).json()["data"]
        return Result("x", mode, "ok", id=t["id"], url=f"https://x.com/i/status/{t['id']}")


PUBLISHER = X
