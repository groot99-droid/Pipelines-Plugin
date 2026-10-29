"""Mastodon: user access token against your own instance. Draft mode = followers-only visibility."""
from __future__ import annotations

import getpass
from pathlib import Path

from videoeditor.publish import net as http, secrets
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import AuthError, PublishError
from videoeditor.publish.package import PostPackage
from videoeditor.publish.util import mime_for, poll

# Docs: https://docs.joinmastodon.org/methods/media/ , /methods/statuses/ , /methods/instance/
SPEC = Spec(
    name="mastodon", title="Mastodon", modes=("draft", "public"),
    draft_note="followers-only (visibility=private); Mastodon has no draft state",
    max_caption=500, soft_limits=("caption",),   # instance-configurable: the real limit is read at send time
    docs=("https://docs.joinmastodon.org/methods/statuses/",),
)


class Mastodon(Publisher):
    spec = SPEC

    def _creds(self) -> tuple[str, str]:
        inst, tok = secrets.get("mastodon", "instance"), secrets.get("mastodon", "token")
        if not inst or not tok:
            raise AuthError("mastodon: not configured. Run `ve publish init mastodon` "
                            "(or set VE_MASTODON_INSTANCE and VE_MASTODON_TOKEN).")
        return inst.rstrip("/"), tok

    def is_configured(self) -> bool:
        return bool(secrets.get("mastodon", "instance") and secrets.get("mastodon", "token"))

    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        vis = "public" if mode == "public" else "private (followers only)"
        return ["GET /api/v2/instance (read this instance's real limits)",
                "POST /api/v2/media (video, alt text) and wait until processing finishes",
                f"POST /api/v1/statuses with visibility={vis}, Idempotency-Key set"]

    def auth_help(self) -> str:
        return ("On your instance: Preferences > Development > New application, scopes write:media and "
                "write:statuses, then copy 'Your access token'. (Menu names vary by version.)")

    def init(self, *, ask=input, ask_secret=None, say=print, manual=False, port=0) -> str:
        ask_secret = ask_secret or getpass.getpass
        say(self.auth_help())
        inst = ask("Instance URL (https://...): ").strip().rstrip("/")
        tok = ask_secret("Access token (hidden): ").strip()
        try:
            secrets.set("mastodon", "instance", inst)
            secrets.set("mastodon", "token", tok)
        except RuntimeError as e:
            return str(e)
        r = http.request("mastodon", "GET", f"{inst}/api/v1/accounts/verify_credentials",
                         headers={"Authorization": f"Bearer {tok}"}, ok=(200,), retries=0)
        return f"saved; logged in as @{r.json().get('acct')}"

    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        inst, tok = self._creds()
        auth = {"Authorization": f"Bearer {tok}"}
        cfg = http.request("mastodon", "GET", f"{inst}/api/v2/instance", ok=(200,)).json().get("configuration", {})
        text = pkg.full_text("mastodon")
        limit = cfg.get("statuses", {}).get("max_characters")
        if limit and len(text) > limit:
            raise PublishError(f"mastodon: caption is {len(text)} characters; this instance allows {limit}")
        vlimit = cfg.get("media_attachments", {}).get("video_size_limit")
        if vlimit and pkg.info.get("bytes", 0) > vlimit:
            raise PublishError(f"mastodon: video is {pkg.info['bytes']} bytes; this instance allows {vlimit}")
        video = Path(pkg.video)
        with open(video, "rb") as f:
            media = http.request("mastodon", "POST", f"{inst}/api/v2/media", headers=auth,
                                 files={"file": (video.name, f, mime_for(video))},
                                 data={"description": pkg.alt_text or ""}, ok=(200, 202), timeout=600).json()
        mid = media["id"]
        if not media.get("url"):     # 202: video is processed asynchronously
            ready = poll(lambda: http.request("mastodon", "GET", f"{inst}/api/v1/media/{mid}", headers=auth, ok=(200, 206)),
                         lambda r: r.status_code == 200, interval=3, timeout=300)
            if ready.status_code != 200:
                raise PublishError("mastodon: the instance is still processing the video after 5 minutes; try again later")
        headers = dict(auth)
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        visibility = "public" if mode == "public" else "private"
        st = http.request("mastodon", "POST", f"{inst}/api/v1/statuses", headers=headers, ok=(200,),
                          json={"status": text, "media_ids": [mid], "visibility": visibility, "sensitive": False}).json()
        return Result("mastodon", mode, "ok" if mode == "public" else "draft", id=st.get("id"), url=st.get("url"),
                      note=f"visibility={visibility}")


PUBLISHER = Mastodon
