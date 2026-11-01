"""The single caption engine.

Styles:
  bold-overlay  2-word UPPERCASE SRT cues, burned with render.SUB_FORCE_STYLE (video-use default)
  opus          3-word chunks, big bold white, yellow active word (ASS)
  karaoke       4-word chunks, green active word (ASS)
  minimal       6-word chunks, clean, no highlight (ASS)

All styles read words on the OUTPUT timeline (offset math from video-use Hard Rule 5), so they
work for any EDL. Captions must be applied LAST in the filter chain (Hard Rule 1); render.py does that.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from videoeditor.core import render
from videoeditor.core.platform import fc_match

STYLES = ("bold-overlay", "opus", "karaoke", "minimal")

ASS_PRESETS = {
    "opus":    dict(font="Arial Black", size=100, chunk=3, highlight="&H0000FFFF&", outline=8, shadow=3),
    "karaoke": dict(font="Arial Black", size=110, chunk=4, highlight="&H0000FF00&", outline=6, shadow=2),
    "minimal": dict(font="Helvetica",   size=70,  chunk=6, highlight=None,          outline=4, shadow=1),
}
WHITE = "&H00FFFFFF&"
OUTLINE = "&H00000000&"


def installed_family(preferred: str, fallback: str = "DejaVu Sans") -> str:
    """Return a font family fontconfig can actually render (libass silently substitutes otherwise).

    Without fontconfig (Windows, stock macOS) libass asks the system's own font provider, so the
    preferred family is passed through unchanged."""
    if not shutil.which("fc-match"):
        return preferred
    got = fc_match("%{family}", f"{preferred}:bold")
    return got.split(",")[0].strip() if got else fallback


def output_timeline_words(edl: dict, edit_dir: Path) -> list[dict]:
    """All spoken words shifted onto the output timeline: out = word.start - seg_start + seg_offset."""
    out: list[dict] = []
    offset = 0.0
    for r in edl["ranges"]:
        s, e = float(r["start"]), float(r["end"])
        tr = edit_dir / "transcripts" / f"{r['source']}.json"
        if tr.exists():
            for w in render._words_in_range(json.loads(tr.read_text(encoding="utf-8")), s, e):
                out.append({
                    "text": (w.get("text") or "").strip(),
                    "start": max(0.0, max(w["start"], s) - s) + offset,
                    "end": max(0.0, min(w["end"], e) - s) + offset,
                })
        offset += e - s
    return [w for w in out if w["text"]]


def _ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(words: list[dict], style: str, out_path: Path, play_res: tuple[int, int] = (1080, 1920)) -> int:
    """Word-by-word highlighted captions. Returns number of events written."""
    p = ASS_PRESETS[style]
    font = installed_family(p["font"])
    chunks = [words[i:i + p["chunk"]] for i in range(0, len(words), p["chunk"])]
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_res[0]}
PlayResY: {play_res[1]}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{p["size"]},{WHITE},&H000000FF,{OUTLINE},&H00000000,1,0,0,0,100,100,0,0,1,{p["outline"]},{p["shadow"]},2,60,60,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    timed: list[tuple[float, float, str]] = []
    for chunk in chunks:
        chunk_end = chunk[-1]["end"]
        for i, w in enumerate(chunk):
            a = w["start"]
            b = chunk[i + 1]["start"] if i + 1 < len(chunk) else chunk_end
            if b <= a:
                b = a + 0.05
            if p["highlight"]:
                line = " ".join(
                    f"{{\\c{p['highlight']}}}{ww['text']}{{\\c{WHITE}}}" if j == i else ww["text"]
                    for j, ww in enumerate(chunk))
            else:
                line = " ".join(ww["text"] for ww in chunk)
            timed.append((a, b, line))
    # Whisper word times can overlap by a few ms; libass stacks overlapping events upward, so clamp each
    # event to end where the next begins.
    timed.sort(key=lambda e: e[0])
    events: list[str] = []
    for i, (a, b, line) in enumerate(timed):
        if i + 1 < len(timed):
            b = min(b, timed[i + 1][0])
        if b <= a:
            continue
        events.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Default,,0,0,0,,{line}")
    out_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return len(events)


def build_captions(edl: dict, edit_dir: Path, style: str = "bold-overlay") -> Path:
    """Write captions for the EDL; returns the file to put in edl['subtitles']."""
    if style not in STYLES:
        raise SystemExit(f"unknown caption style '{style}' (choose from {', '.join(STYLES)})")
    if style == "bold-overlay":
        out = edit_dir / "master.srt"
        render.build_master_srt(edl, edit_dir, out)
        return out
    out = edit_dir / f"captions_{style}.ass"
    words = output_timeline_words(edl, edit_dir)
    if not words:
        raise SystemExit("no transcript words found for this EDL; run `ve transcribe` first")
    n = build_ass(words, style, out)
    print(f"{style} captions -> {out.name} ({n} events)")
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Build captions for an EDL")
    ap.add_argument("edl", type=Path)
    ap.add_argument("--style", choices=STYLES, default="bold-overlay")
    a = ap.parse_args(argv)
    edl_path = a.edl.resolve()
    print(build_captions(json.loads(edl_path.read_text(encoding="utf-8")), edl_path.parent, a.style))


if __name__ == "__main__":
    main()
