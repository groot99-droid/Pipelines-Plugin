"""Linux-friendly helpers: tool checks and font lookup (no macOS paths)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def require_tools(*names: str) -> None:
    missing = [n for n in names if shutil.which(n) is None]
    if missing:
        raise SystemExit(f"missing required tool(s) on PATH: {', '.join(missing)}")


def find_font(family: str = "DejaVu Sans Mono", bold: bool = False) -> str | None:
    """Resolve a font file via fontconfig; fall back to common Linux locations."""
    pattern = f"{family}:bold" if bold else family
    if shutil.which("fc-match"):
        try:
            out = subprocess.run(
                ["fc-match", "-f", "%{file}", pattern],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            if out and Path(out).exists():
                return out
        except subprocess.CalledProcessError:
            pass
    for fp in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ):
        if Path(fp).exists():
            return fp
    return None


def probe(video: Path) -> dict:
    """Width, height, duration, fps, has_audio for a media file."""
    import json

    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout
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
