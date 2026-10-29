"""TikTok Content Posting API. Draft mode = "Upload": the video lands in the creator's TikTok inbox and the creator
finishes and posts it in the app. Public mode = Direct Post (needs the video.publish scope and, per TikTok, an
audited client for non-private posts).

Docs: developers.tiktok.com/doc/content-posting-api-reference-upload-video, ...-direct-post, ...-media-transfer-guide.
Upload mode documents no caption field, so the caption is NOT sent in draft mode; it is printed for you to paste.
The PKCE flag is off: TikTok documents code_verifier for mobile/desktop apps only.
"""
from __future__ import annotations

from videoeditor.publish import net as http, oauth, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import poll, read_chunks

API = "https://open.tiktokapis.com"
MIN_CHUNK, MAX_CHUNK = 5 * 1024 * 1024, 64 * 1024 * 1024
CHUNK = 10 * 1024 * 1024
SPEC = Spec(
    name="tiktok", title="TikTok", modes=("draft", "public"),
    draft_note="inbox upload: finish and post it in the TikTok app (your caption is not sent; it is shown for pasting)",
    gated_note="Direct Post to the public needs the video.publish scope and, for non-private posts, a TikTok-audited app",
    max_caption=2200, max_duration_s=600, max_bytes=4 * 1024**3, extensions=(".mp4", ".mov", ".webm"),
    orientation="prefer-vertical", docs=("https://developers.tiktok.com/doc/content-posting-api-get-started",),
)


def chunk_plan(size: int) -> tuple[int, int]:
    """(chunk_size, total_chunk_count) per TikTok's rules: >=5 MB and <=64 MB chunks, trailing bytes join the last
    chunk, files under 5 MB are one chunk of the whole file."""
    if size < MIN_CHUNK:
        return size, 1
    if size <= MAX_CHUNK:
        return size, 1
    return CHUNK, size // CHUNK


def oauth_config(client_id: str, client_secret: str | None) -> oauth.OAuthConfig:
    return oauth.OAuthConfig(
        platform="tiktok", auth_url="https://www.tiktok.com/v2/auth/authorize/", token_url=f"{API}/v2/oauth/token/",
        client_id=client_id, client_secret=client_secret, client_id_param="client_key", scopes=["user.info.basic", "video.upload"],
        scope_sep=",", pkce=False)


class TikTok(Publisher):
    spec = SPEC

    def _cfg(self, scopes: list[str] | None = None) -> oauth.OAuthConfig:
        cid = secrets.get("tiktok", "client_id")
        if not cid:
            raise AuthError("tiktok: not configured. Run `ve publish init tiktok`.")
        cfg = oauth_config(cid, secrets.get("tiktok", "client_secret"))
        if scopes:
            cfg.scopes = scopes
        return cfg

    def is_configured(self) -> bool:
        return oauth.load_token("tiktok") is not None

    def auth_help(self) -> str:
        return ("developers.tiktok.com: create an app, add Login Kit and Content Posting API, register a redirect URI, "
                "and (for Direct Post) request the video.publish scope.")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        say(self.auth_help())
        direct = ask("Also request Direct Post (video.publish)? [y/N] ").strip().lower() == "y"

        def build(cid, sec):
            c = oauth_config(cid, sec)
            if direct:
                c.scopes.append("video.publish")
            return c

        redirect = ask("Redirect URI registered on the app: ").strip() if manual else "http://127.0.0.1:8080/"
        return oauth.run_init("tiktok", build, ask=ask, ask_secret=ask_secret, say=say, manual=manual, port=port,
                              redirect_uri=redirect, needs_secret=True)

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        size, count = chunk_plan(pkg.info["bytes"])
        if mode == "draft":
            return [f"POST {API}/v2/post/publish/inbox/video/init/ ({count} chunk(s) of up to {size // 1048576 or 1} MB)",
                    "PUT each chunk with Content-Range", "poll /v2/post/publish/status/fetch/ until SEND_TO_USER_INBOX",
                    "then open TikTok: the draft is in your inbox notifications; paste the caption yourself"]
        return ["POST /v2/post/publish/creator_info/query/ (allowed privacy levels, max duration)",
                f"POST {API}/v2/post/publish/video/init/ (privacy_level=PUBLIC_TO_EVERYONE, title=caption)",
                "PUT chunks, then poll status/fetch until PUBLISH_COMPLETE"]

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        scopes = ["user.info.basic", "video.upload"] if mode == "draft" else ["user.info.basic", "video.publish"]
        token = oauth.access_token(self._cfg(scopes))
        h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"}
        total = pkg.info["bytes"]
        chunk_size, count = chunk_plan(total)
        source = {"source": "FILE_UPLOAD", "video_size": total, "chunk_size": chunk_size, "total_chunk_count": count}
        if mode == "draft":
            init = http.request("tiktok", "POST", f"{API}/v2/post/publish/inbox/video/init/", headers=h,
                                json={"source_info": source}, ok=(200,)).json()
        else:
            ci = http.request("tiktok", "POST", f"{API}/v2/post/publish/creator_info/query/", headers=h, ok=(200,)).json().get("data", {})
            if "PUBLIC_TO_EVERYONE" not in ci.get("privacy_level_options", []):
                raise PublishError("tiktok: this account/app cannot post publicly (allowed: "
                                   f"{ci.get('privacy_level_options')}). Use draft mode, or get the app audited.")
            if ci.get("max_video_post_duration_sec") and pkg.info.get("duration", 0) > ci["max_video_post_duration_sec"]:
                raise PublishError(f"tiktok: video is longer than this creator's limit of {ci['max_video_post_duration_sec']}s")
            post_info = {"title": pkg.for_platform("tiktok")["caption"][:2200], "privacy_level": "PUBLIC_TO_EVERYONE",
                         "is_aigc": bool(pkg.ai_generated)}
            if pkg.branded_content:
                post_info["brand_content_toggle"] = True
            init = http.request("tiktok", "POST", f"{API}/v2/post/publish/video/init/", headers=h,
                                json={"post_info": post_info, "source_info": source}, ok=(200,)).json()
        data = init.get("data") or {}
        upload_url, publish_id = data.get("upload_url"), data.get("publish_id")
        if not upload_url or not publish_id:
            raise PublishError(f"tiktok: init returned no upload_url/publish_id: {str(init)[:200]}")
        ctype = "video/quicktime" if pkg.video.lower().endswith(".mov") else "video/webm" if pkg.video.lower().endswith(".webm") else "video/mp4"
        sent = 0
        for i, (offset, block) in enumerate(read_chunks(pkg.video, chunk_size)):
            last = i == count - 1
            if last:                       # trailing bytes belong to the final chunk
                with open(pkg.video, "rb") as f:
                    f.seek(offset)
                    block = f.read()
            end = offset + len(block) - 1
            http.request("tiktok", "PUT", upload_url, data=block, ok=(201, 206), timeout=600,
                         headers={"Content-Type": ctype, "Content-Length": str(len(block)),
                                  "Content-Range": f"bytes {offset}-{end}/{total}"})
            sent += len(block)
            if last or sent >= total:
                break
        want = "SEND_TO_USER_INBOX" if mode == "draft" else "PUBLISH_COMPLETE"

        def status():
            return http.request("tiktok", "POST", f"{API}/v2/post/publish/status/fetch/", headers=h, ok=(200,),
                                json={"publish_id": publish_id}).json().get("data", {})

        st = poll(status, lambda d: d.get("status") in (want, "PUBLISH_COMPLETE", "FAILED"), interval=5, timeout=600)
        if st.get("status") == "FAILED":
            raise PublishError(f"tiktok: processing failed: {st.get('fail_reason')}")
        if st.get("status") not in (want, "PUBLISH_COMPLETE"):
            raise PublishError(f"tiktok: still {st.get('status')} after 10 minutes (publish_id {publish_id}); check the app before retrying")
        if mode == "draft":
            return Result("tiktok", mode, "draft", id=publish_id,
                          note="in your TikTok inbox: open the notification, add the caption below and post it:\n"
                               + pkg.full_text("tiktok"))
        return Result("tiktok", mode, "ok", id=publish_id, note="public post")


PUBLISHER = TikTok
