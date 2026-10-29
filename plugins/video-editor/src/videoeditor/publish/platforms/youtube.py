"""YouTube: Data API v3 resumable upload with OAuth (youtube.upload scope). Draft mode = privacyStatus private.

Docs: developers.google.com/youtube/v3/guides/using_resumable_upload_protocol and docs/videos/insert.
The current insert page says unverified API projects are NOT forced private; this tool still defaults to
private by its own safety rule. `selfDeclaredMadeForKids` is a legal declaration, so it is never defaulted.
"""
from __future__ import annotations

from videoeditor.publish import net as http, oauth, secrets
from videoeditor.publish.base import Issue, Publisher, Result, Spec
from videoeditor.publish.errors import ApiError, AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import first_line, read_chunks

UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
CHUNK = 8 * 1024 * 1024          # a multiple of 256 KiB, as the protocol requires
SPEC = Spec(
    name="youtube", title="YouTube", modes=("draft", "public"),
    draft_note="uploaded as private (privacyStatus=private); you make it public in YouTube Studio",
    max_bytes=256 * 1024**3, orientation="prefer-vertical",
    docs=("https://developers.google.com/youtube/v3/docs/videos/insert",),
)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def oauth_config(client_id: str, client_secret: str | None) -> oauth.OAuthConfig:
    return oauth.OAuthConfig(
        platform="youtube", auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret,
        scopes=SCOPES, extra_auth_params={"access_type": "offline", "prompt": "consent"})


def is_short_candidate(info: dict) -> bool:
    """YouTube's own Help page defines Shorts; the developer docs do not. Heuristic only (vertical/square, <= 3 min)."""
    return info.get("orientation") in ("vertical", "square") and (info.get("duration") or 0) <= 180


class YouTube(Publisher):
    spec = SPEC

    def _cfg(self) -> oauth.OAuthConfig:
        cid = secrets.get("youtube", "client_id")
        if not cid:
            raise AuthError("youtube: not configured. Run `ve publish init youtube`.")
        return oauth_config(cid, secrets.get("youtube", "client_secret"))

    def is_configured(self) -> bool:
        return oauth.load_token("youtube") is not None

    def auth_help(self) -> str:
        return ("Google Cloud Console: create a project, enable 'YouTube Data API v3', create an OAuth client of type "
                "'Desktop app', and add yourself as a test user on the consent screen.")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        say(self.auth_help())
        return oauth.run_init("youtube", oauth_config, ask=ask, ask_secret=ask_secret, say=say, manual=manual,
                              port=port, redirect_uri="http://127.0.0.1:8080/")

    def extra_validation(self, pkg: PostPackage) -> list[Issue]:
        issues = []
        if pkg.made_for_kids is None:
            issues.append(Issue("error", "declare whether this video is made for kids "
                                         "(--made-for-kids or --not-made-for-kids); YouTube requires the declaration "
                                         "and it is yours to make"))
        if not is_short_candidate(pkg.info):
            issues.append(Issue("warn", "this will not be treated as a Short (needs vertical/square and about 3 minutes or less); "
                                        "it will upload as a normal video"))
        return issues

    def metadata(self, pkg: PostPackage, mode: str) -> dict:
        v = pkg.for_platform("youtube")
        title = (v["title"] or first_line(v["caption"], 100) or "Untitled")[:100]
        desc = v["caption"]
        if is_short_candidate(pkg.info) and "#shorts" not in desc.lower():
            desc = (desc + "\n\n#Shorts").strip()
        status = {"privacyStatus": "public" if mode == "public" else "private",
                  "selfDeclaredMadeForKids": bool(pkg.made_for_kids)}
        if pkg.ai_generated:
            status["containsSyntheticMedia"] = True
        return {"snippet": {"title": title, "description": desc, "tags": [t.lstrip("#") for t in v["tags"]],
                            "categoryId": "22"}, "status": status}

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        md = self.metadata(pkg, mode)
        return [f"POST upload/youtube/v3/videos?uploadType=resumable&part=snippet,status "
                f"(privacyStatus={md['status']['privacyStatus']}, title={md['snippet']['title']!r})",
                f"PUT the file in {CHUNK // 1048576} MiB chunks, resuming after interruptions"]

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        cfg = self._cfg()
        total = pkg.info["bytes"]
        auth = {"Authorization": f"Bearer {oauth.access_token(cfg)}"}
        init = http.request("youtube", "POST", UPLOAD_URL,
                            params={"uploadType": "resumable", "part": "snippet,status"},
                            headers={**auth, "Content-Type": "application/json; charset=UTF-8",
                                     "X-Upload-Content-Length": str(total), "X-Upload-Content-Type": "video/*"},
                            json=self.metadata(pkg, mode), ok=(200,))
        session = init.headers.get("Location")
        if not session:
            raise PublishError("youtube: no upload session URL returned")
        video_id = None
        for offset, block in read_chunks(pkg.video, CHUNK):
            end = offset + len(block) - 1
            for attempt in range(3):
                try:
                    r = http.request("youtube", "PUT", session, data=block, ok=(200, 201, 308), retries=2, timeout=300,
                                     headers={"Content-Length": str(len(block)), "Content-Type": "video/*",
                                              "Content-Range": f"bytes {offset}-{end}/{total}"})
                    break
                except ApiError as e:
                    if e.status == 404:
                        raise PublishError("youtube: upload session expired; start again") from e
                    if attempt == 2:
                        raise
            if r.status_code in (200, 201):
                video_id = r.json().get("id")
        if not video_id:
            raise PublishError("youtube: upload finished without a video id; check YouTube Studio before retrying")
        return Result("youtube", mode, "ok" if mode == "public" else "draft", id=video_id,
                      url=f"https://studio.youtube.com/video/{video_id}/edit",
                      note=f"privacyStatus={'public' if mode == 'public' else 'private'}")


PUBLISHER = YouTube
