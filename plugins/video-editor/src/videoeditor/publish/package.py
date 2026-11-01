"""PostPackage: everything a post needs, validated once and written to <edit>/publish.json."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from videoeditor.core.platform import probe

FILE_NAME = "publish.json"


@dataclass
class PostPackage:
    video: str
    caption: str
    title: str | None = None
    tags: list[str] = field(default_factory=list)
    alt_text: str | None = None
    platforms: list[str] = field(default_factory=list)
    # per-platform overrides: {"x": {"caption": "...", "title": "..."}} so posts are never one identical blast
    overrides: dict[str, dict] = field(default_factory=dict)
    ai_generated: bool = False        # disclosure flag, passed to platforms that have a field for it
    branded_content: bool = False
    made_for_kids: bool | None = None   # a legal declaration (YouTube): never defaulted, the user must state it
    info: dict = field(default_factory=dict)   # probed: width, height, duration, bytes, orientation, has_audio

    def for_platform(self, platform: str) -> dict:
        """Caption/title as this platform should see them (override wins)."""
        o = self.overrides.get(platform, {})
        caption = o.get("caption", self.caption)
        title = o.get("title", self.title)
        return {"caption": caption, "title": title, "tags": o.get("tags", self.tags)}

    def full_text(self, platform: str, hashtag_prefix: bool = True) -> str:
        """Caption plus hashtags, as one string, for platforms that take a single text field."""
        v = self.for_platform(platform)
        tags = [("#" + t.lstrip("#")) if hashtag_prefix else t for t in v["tags"]]
        return (v["caption"] + ("\n\n" + " ".join(tags) if tags else "")).strip()

    def fingerprint(self) -> str:
        """sha256 of the video bytes: the same file posted twice is detected even if it was renamed."""
        h = hashlib.sha256()
        with open(self.video, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest()


def build(video: Path, caption: str, *, title: str | None = None, tags: list[str] | None = None,
          platforms: list[str] | None = None, alt_text: str | None = None, ai_generated: bool = False,
          branded_content: bool = False, made_for_kids: bool | None = None,
          overrides: dict | None = None) -> PostPackage:
    video = Path(video).resolve()
    if not video.is_file():
        raise FileNotFoundError(f"video not found: {video}")
    info = probe(video)
    info["bytes"] = video.stat().st_size
    return PostPackage(video=str(video), caption=caption.strip(), title=title, tags=list(tags or []),
                       alt_text=alt_text, platforms=list(platforms or []), overrides=dict(overrides or {}),
                       ai_generated=ai_generated, branded_content=branded_content, made_for_kids=made_for_kids,
                       info=info)


def save(pkg: PostPackage, edit_dir: Path) -> Path:
    edit_dir.mkdir(parents=True, exist_ok=True)
    p = edit_dir / FILE_NAME
    p.write_text(json.dumps(asdict(pkg), indent=2), encoding="utf-8")
    return p


def load(edit_dir: Path) -> PostPackage:
    p = edit_dir / FILE_NAME
    if not p.exists():
        raise FileNotFoundError(f"no publishing package at {p}; run `ve publish prepare` first")
    return PostPackage(**json.loads(p.read_text(encoding="utf-8")))
