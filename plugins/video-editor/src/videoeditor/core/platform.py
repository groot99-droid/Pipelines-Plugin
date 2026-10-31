"""Linux-friendly helpers: tool checks and font lookup (no macOS paths)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def require_tools(*names: str) -> None:
    missing = [n for n in names if shutil.which(n) is None]
    if missing:
        raise SystemExit(f"missing required tool(s) on PATH: {', '.join(missing)}")


def fc_match(fmt: str, pattern: str) -> str | None:
    """Ask fontconfig (`fc-match`) about a font; None where it is absent (Windows, stock macOS) or fails."""
    if not shutil.which("fc-match"):
        return None
    try:
        out = subprocess.run(["fc-match", "-f", fmt, pattern], capture_output=True, text=True, check=True,
                             timeout=15, encoding="utf-8", errors="replace").stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None
    return out or None


# Where common monospace fonts live when fontconfig cannot say, per platform (macOS has none: it falls to None).
FALLBACK_FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
)


def find_font(family: str = "DejaVu Sans Mono", bold: bool = False) -> str | None:
    """Resolve a font file via fontconfig when present, else a common per-platform location; None if neither."""
    out = fc_match("%{file}", f"{family}:bold" if bold else family)
    if out and Path(out).exists():
        return out
    for fp in FALLBACK_FONTS:
        if Path(fp).exists():
            return fp
    return None


def probe(video: Path) -> dict:
    """Width, height, duration, fps, has_audio for a media file."""
    import json

    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)],
        capture_output=True, text=True, check=True, encoding="utf-8", errors="replace").stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    info = {
        "duration": float(data["format"].get("duration", 0) or 0),
        "has_audio": a is not None,
        "width": None, "height": None, "fps": None,
    }
    if v:
        info["width"], info["height"] = int(v["width"]), int(v["height"])
        num, _, den = v.get("avg_frame_rate", "0/1").partition("/")
        info["fps"] = float(num) / float(den or 1) if float(den or 1) else None
        # honor rotation metadata so phone portrait clips read as portrait
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
        rot = rot or int((v.get("tags") or {}).get("rotate", 0) or 0)
        if abs(rot) % 180 == 90:
            info["width"], info["height"] = info["height"], info["width"]
    info["orientation"] = (
        "unknown" if not info["width"]
        else "vertical" if info["height"] > info["width"]
        else "square" if info["height"] == info["width"]
        else "landscape"
    )
    return info
