"""Overlay engines for the explainer add-on.

  pil       zero-setup: an animated text card rendered to MP4 (ease_out_cubic slide + fade in)
  remotion  React/CSS compositions from our own template (templates/remotion_overlay); needs Node and a browser
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from videoeditor.core.platform import find_font


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def render_text_card(text: str, out: Path, duration: float = 4.0, size: tuple[int, int] = (1920, 1080),
                     fps: int = 30, reveal: float = 0.6, font_size: int = 76,
                     bg: tuple[int, int, int] = (10, 10, 10), fg: tuple[int, int, int] = (255, 90, 0),
                     font_path: str | None = None) -> Path:
    """Render a centered text card. Explicit font path is used; a missing font is an error, not a silent fallback."""
    font_path = font_path or find_font("DejaVu Sans Mono", bold=True)
    if not font_path:
        raise SystemExit("no usable font found; pass --font /path/to/font.ttf")
    font = ImageFont.truetype(font_path, font_size)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = int(round(duration * fps))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
           "-r", str(fps), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
           "-t", f"{duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac",
           "-shortest", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    probe_draw = ImageDraw.Draw(Image.new("RGB", size))
    # anchor on the FULL string width so text does not drift as it animates
    tw = probe_draw.textlength(text, font=font)
    x0, y0 = (size[0] - tw) / 2, (size[1] - font_size) / 2
    for i in range(n):
        t = i / fps
        p = ease_out_cubic(min(1.0, t / reveal)) if reveal > 0 else 1.0
        img = Image.new("RGB", size, bg)
        layer = Image.new("RGB", size, bg)
        ImageDraw.Draw(layer).text((x0, y0 + (1 - p) * 40), text, font=font, fill=fg)
        img = Image.blend(img, layer, p)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed while encoding the overlay")
    return out


# -------- Remotion slots ----------------------------------------------------

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "remotion_overlay"


def caption_pages_from_edl(edl: dict, edit_dir: Path) -> list[dict]:
    """Caption pages on the output timeline, chunked exactly like the burned-in captions."""
    from videoeditor.core.captions import output_timeline_words
    from videoeditor.core.render import chunk_words

    pages = []
    for chunk in chunk_words(output_timeline_words(edl, edit_dir)):
        text = " ".join(w["text"] for w in chunk).rstrip(",;:")
        pages.append({"text": text, "start": round(chunk[0]["start"], 3), "end": round(max(chunk[-1]["end"], chunk[0]["start"] + 0.4), 3)})
    return pages


def build_overlay_spec(*, title: str | None = None, pages: list[dict] | None = None, duration: float = 4.0,
                       size: tuple[int, int] = (1920, 1080), fps: int = 30, transparent: bool = False,
                       font_family: str | None = None) -> dict:
    from videoeditor.core.captions import installed_family

    items: list[dict] = []
    if title:
        items.append({"type": "title", "text": title, "start": 0.0, "end": duration})
    if pages:
        items.append({"type": "captions", "pages": pages})
    if not items:
        raise SystemExit("an overlay needs a title or caption pages")
    return {
        "width": size[0], "height": size[1], "fps": fps, "durationSeconds": duration,
        "background": "transparent" if transparent else "#0a0a0a",
        "color": "#ffffff", "accent": "#ff5a00",
        "fontFamily": font_family or installed_family("DejaVu Sans Mono"),
        "items": items,
    }


def scaffold_remotion_slot(slot_dir: Path, spec: dict) -> Path:
    """Copy the template into slot_dir (never inside the videoeditor repo) and write overlay.json."""
    slot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, slot_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules", "*.mp4", "*.webm"))
    (slot_dir / "overlay.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return slot_dir


def render_remotion(slot_dir: Path, out_name: str = "render.mp4", transparent: bool = False,
                    browser: str | None = None) -> Path:
    """npm install (once) and `remotion render`. Transparent output is VP8 WebM with alpha."""
    if shutil.which("node") is None or shutil.which("npm") is None:
        raise SystemExit("the remotion engine needs Node.js 20.19+/22.13+ and npm on PATH")
    if not (slot_dir / "node_modules").exists():
        subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=slot_dir, check=True)
    out = Path(out_name)
    if transparent and out.suffix != ".webm":
        out = out.with_suffix(".webm")
    cmd = ["npx", "remotion", "render", "src/index.ts", "Overlay", str(out), "--props=overlay.json"]
    if transparent:
        cmd += ["--codec=vp8", "--image-format=png", "--pixel-format=yuva420p"]
    browser = browser or os.environ.get("REMOTION_BROWSER_EXECUTABLE")
    if browser:
        cmd.append(f"--browser-executable={browser}")
    subprocess.run(cmd, cwd=slot_dir, check=True)
    return slot_dir / out
