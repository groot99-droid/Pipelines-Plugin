"""Publisher interface and the generic part of validation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from videoeditor.publish.package import PostPackage


@dataclass
class Issue:
    severity: str          # "error" blocks sending, "warn" is shown
    message: str


@dataclass
class Result:
    platform: str
    mode: str
    status: str            # "ok" | "draft" | "dry-run"
    id: str | None = None
    url: str | None = None
    note: str | None = None


@dataclass
class Spec:
    name: str
    title: str
    modes: tuple[str, ...]                 # subset of ("draft", "public")
    draft_note: str = ""                   # what "draft" means here (private upload, inbox, container, followers-only)
    max_caption: int | None = None
    min_duration_s: float | None = None
    max_duration_s: float | None = None
    max_bytes: int | None = None
    # limits named here are not confirmed on the platform's own docs (or depend on the account): over-limit is a
    # warning, not a blocker. Names: "caption", "duration", "bytes".
    soft_limits: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()       # accepted file extensions, lower case, with dot
    orientation: str = "any"               # "vertical" (required), "prefer-vertical", "any"
    cost_note: str | None = None           # set => `accept_cost` must be given to send
    gated_note: str | None = None          # e.g. "posts are forced private until the app passes an audit"
    docs: tuple[str, ...] = field(default_factory=tuple)


class Publisher(ABC):
    spec: Spec

    # -------- no network ------------------------------------------------
    def validate(self, pkg: PostPackage) -> list[Issue]:
        s, info, issues = self.spec, pkg.info, []
        def over(kind: str, msg: str) -> None:
            issues.append(Issue("warn" if kind in s.soft_limits else "error",
                                msg + (" (limit not confirmed by the platform's docs)" if kind in s.soft_limits else "")))

        text = pkg.full_text(s.name)
        if s.max_caption is not None and len(text) > s.max_caption:
            over("caption", f"caption is {len(text)} characters; {s.title} allows {s.max_caption}")
        dur = info.get("duration")
        if s.max_duration_s and dur and dur > s.max_duration_s:
            over("duration", f"video is {dur:.0f}s; {s.title} allows {s.max_duration_s:.0f}s")
        if s.min_duration_s and dur and dur < s.min_duration_s:
            issues.append(Issue("error", f"video is {dur:.1f}s; {s.title} needs at least {s.min_duration_s:.0f}s"))
        size = info.get("bytes")
        if s.max_bytes and size and size > s.max_bytes:
            over("bytes", f"video is {size / 1e6:.0f} MB; {s.title} allows {s.max_bytes / 1e6:.0f} MB")
        ext = Path(pkg.video).suffix.lower()
        if s.extensions and ext not in s.extensions:
            issues.append(Issue("error", f"{s.title} accepts {'/'.join(s.extensions)} files; this is {ext or 'unknown'}"))
        if info.get("orientation") and s.orientation == "vertical" and info["orientation"] != "vertical":
            issues.append(Issue("error", f"{s.title} needs a vertical (9:16) video; this one is {info['orientation']}"))
        elif s.orientation == "prefer-vertical" and info.get("orientation") not in (None, "vertical"):
            issues.append(Issue("warn", f"{s.title} favours vertical video; this one is {info['orientation']}"))
        if info.get("has_audio") is False:
            issues.append(Issue("warn", "the video has no audio track"))
        issues += self.extra_validation(pkg)
        return issues

    def extra_validation(self, pkg: PostPackage) -> list[Issue]:
        return []

    @abstractmethod
    def plan(self, pkg: PostPackage, mode: str) -> list[str]:
        """Human-readable steps that `send` would perform. Must not touch the network."""

    # -------- network ---------------------------------------------------
    @abstractmethod
    def send(self, pkg: PostPackage, mode: str, *, idempotency_key: str | None = None) -> Result:
        """Perform the upload/post. Called only by service.send after every safety check has passed."""

    def auth_help(self) -> str:
        return ""

    def init(self, *, ask=input, ask_secret=None, say=print, manual: bool = False, port: int = 0) -> str:
        """Interactive credential setup; returns a status line. Default: nothing to do."""
        return "nothing to set up"

    def is_configured(self) -> bool:
        return False
