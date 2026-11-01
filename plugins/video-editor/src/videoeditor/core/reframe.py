"""Reframe landscape video to vertical 9:16: center crop, speaker-following pan, or split-screen.

Ported from clipify (analyze.py + build_pan.py + the split-screen recipe). By default, speaker detection
uses frame-difference motion inside two hand-placed face ROIs; no face-detection model. If a diarized
transcript exists (whisperX backend), pass real speaker turns instead. Camera must be static within the clip.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from videoeditor.core.platform import probe

OUT_W, OUT_H = 1080, 1920


def _even(n: float) -> int:
    return max(2, int(n) // 2 * 2)


def strip_width(src_h: int, out_w: int = OUT_W, out_h: int = OUT_H) -> int:
    """Width of the source-pixel crop that scales to the vertical output."""
    return _even(src_h * out_w / out_h)


def motion_energy(clip: Path, roi: tuple[int, int, int, int], fps: float = 30.0) -> np.ndarray:
    """Mean absolute frame difference inside roi=(x, y, w, h), one value per frame at `fps`."""
    x, y, w, h = roi
    w, h = _even(w), _even(h)
    cmd = ["ffmpeg", "-v", "error", "-i", str(clip), "-vf", f"fps={fps},crop={w}:{h}:{x}:{y},format=gray",
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, dtype=np.uint8)
    n = len(frames) // (w * h)
    if n < 2:
        return np.zeros(max(n, 1))
    frames = frames[: n * w * h].reshape(n, h, w).astype(np.int16)
    diff = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    return np.concatenate([[diff[0]], diff])


def speaker_segments(left: np.ndarray, right: np.ndarray, fps: float = 30.0,
                     min_dur: float = 1.0, margin: float = 1.15, smooth_win: int = 15) -> list[dict]:
    """Who is speaking when, from two motion curves. Short interjections merge into the prior speaker."""
    n = min(len(left), len(right))
    if n == 0:
        return []

    def norm(v):
        m = float(np.mean(v))
        return v / m if m > 0 else np.zeros_like(v)

    def smooth(v):
        k = np.ones(smooth_win) / smooth_win
        pad = smooth_win // 2
        return np.convolve(np.pad(v, pad, mode="edge"), k, mode="valid")[: len(v)]

    sl, sr = smooth(norm(left[:n])), smooth(norm(right[:n]))
    cur = 0 if sl[0] >= sr[0] else 1
    who = []
    for i in range(n):
        if cur == 0 and sr[i] > sl[i] * margin:
            cur = 1
        elif cur == 1 and sl[i] > sr[i] * margin:
            cur = 0
        who.append(cur)

    segs: list[dict] = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and who[j + 1] == who[i]:
            j += 1
        segs.append({"start": i / fps, "end": (j + 1) / fps, "speaker": "left" if who[i] == 0 else "right"})
        i = j + 1

    merged: list[dict] = []
    for s in segs:
        if merged and (s["end"] - s["start"]) < min_dur:
            merged[-1]["end"] = s["end"]
        else:
            merged.append(s)
    out: list[dict] = []
    for s in merged:
        if out and out[-1]["speaker"] == s["speaker"]:
            out[-1]["end"] = s["end"]
        else:
            out.append(s)
    return out


def speaker_segments_from_words(words: list[dict], speaker_map: dict[str, str], min_dur: float = 1.0) -> list[dict]:
    """Speaker turns from a diarized transcript (words carry `speaker_id`, see transcribe_whisperx) instead of
    face-box motion. `speaker_map` says which side of the frame each speaker sits on, e.g.
    {"SPEAKER_00": "left", "SPEAKER_01": "right"}. Words from unmapped speakers are ignored; short turns
    merge into the previous one exactly like the motion method."""
    turns: list[dict] = []
    for w in words:
        if w.get("type", "word") != "word":
            continue
        side = speaker_map.get(w.get("speaker_id") or "")
        if side not in ("left", "right") or w.get("start") is None:
            continue
        if turns and turns[-1]["speaker"] == side:
            turns[-1]["end"] = w["end"]
        else:
            turns.append({"start": w["start"], "end": w["end"], "speaker": side})
    if not turns:
        return []
    # a camera cut holds on the previous speaker through gaps: extend each turn to the next one's start
    for a, b in zip(turns, turns[1:]):
        a["end"] = b["start"]
    turns[0]["start"] = 0.0
    merged: list[dict] = []
    for t in turns:
        if merged and (t["end"] - t["start"]) < min_dur:
            merged[-1]["end"] = t["end"]
        else:
            merged.append(t)
    out: list[dict] = []
    for t in merged:
        if out and out[-1]["speaker"] == t["speaker"]:
            out[-1]["end"] = t["end"]
        else:
            out.append(t)
    return out


def pan_expr(segments: list[dict], left_x: int, right_x: int) -> str:
    """ffmpeg crop x-expression with hard cuts between the two speaker positions."""
    def x_for(s: str) -> int:
        return left_x if s == "left" else right_x

    expr = str(x_for(segments[-1]["speaker"]))
    for seg in reversed(segments[:-1]):
        expr = f"if(lt(t\\,{seg['end']:.4f})\\,{x_for(seg['speaker'])}\\,{expr})"
    return expr


def pan_positions(face_left_cx: int, face_right_cx: int, src_w: int, crop_w: int) -> tuple[int, int]:
    half = crop_w // 2
    clamp = lambda v: int(min(max(0, v), src_w - crop_w))
    return clamp(face_left_cx - half), clamp(face_right_cx - half)


def center_crop_filter(src_w: int, src_h: int) -> str:
    cw = min(strip_width(src_h), _even(src_w))
    return f"crop={cw}:{src_h}:(iw-{cw})/2:0,scale={OUT_W}:{OUT_H}:flags=lanczos"


def pan_filter(src_h: int, expr: str) -> str:
    cw = strip_width(src_h)
    return f"crop={cw}:{src_h}:x='{expr}':y=0,scale={OUT_W}:{OUT_H}:flags=lanczos"


def split_filter(segments: list[dict], left_face: tuple[int, int], right_face: tuple[int, int],
                 src_w: int, src_h: int) -> str:
    """Two stacked 1080x960 tiles; the active speaker's tile is on top. Returns a filter_complex ending in [v]."""
    tile_h = _even(src_h * 0.6)
    tile_w = min(_even(tile_h * 1080 / 960), _even(src_w))
    tile_h = min(tile_h, _even(tile_w * 960 / 1080))

    def origin(face):
        cx, cy = face
        return (int(min(max(0, cx - tile_w // 2), src_w - tile_w)),
                int(min(max(0, cy - tile_h // 2), src_h - tile_h)))

    lx, ly = origin(left_face)
    rx, ry = origin(right_face)
    right_on = "+".join(f"between(t,{s['start']:.3f},{s['end']:.3f})" for s in segments if s["speaker"] == "right") or "0"
    return (
        f"[0:v]split=2[a0][a1];"
        f"[a0]crop={tile_w}:{tile_h}:{lx}:{ly},scale=1080:960,split=2[lt0][lt1];"
        f"[a1]crop={tile_w}:{tile_h}:{rx}:{ry},scale=1080:960,split=2[rt0][rt1];"
        f"[lt0][rt0]vstack[layoutL];"
        f"[rt1][lt1]vstack[layoutR];"
        f"[layoutL][layoutR]overlay=0:0:enable='{right_on}'[v]"
    )


def reframe(clip: Path, out: Path, mode: str, *, left_roi=None, right_roi=None, fps: float = 30.0,
            min_dur: float = 1.0, crf: int = 20, segments: list[dict] | None = None) -> dict:
    """Render `clip` to 1080x1920. mode: 'center' | 'pan' | 'split'. ROIs are (x, y, w, h) in source pixels."""
    info = probe(clip)
    sw, sh = info["width"], info["height"]
    if mode in ("pan", "split"):
        if not (left_roi and right_roi):
            raise SystemExit(f"mode '{mode}' needs --left-roi and --right-roi (x,y,w,h in source pixels)")
        if segments is None:  # no diarized turns supplied: fall back to motion inside the two face boxes
            segments = speaker_segments(motion_energy(clip, left_roi, fps), motion_energy(clip, right_roi, fps), fps, min_dur)
        if not segments:
            raise SystemExit("could not derive speaker segments (clip too short?)")

    segments = segments or []
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
    base = ["ffmpeg", "-y", "-v", "error", "-i", str(clip)]
    amap = ["-map", "0:a?"]
    if mode == "center":
        cmd = base + ["-vf", center_crop_filter(sw, sh), "-map", "0:v"] + amap + enc
    elif mode == "pan":
        lx, rx = pan_positions(left_roi[0] + left_roi[2] // 2, right_roi[0] + right_roi[2] // 2, sw, strip_width(sh))
        cmd = base + ["-filter_complex", f"[0:v]{pan_filter(sh, pan_expr(segments, lx, rx))}[v]", "-map", "[v]"] + amap + enc
    elif mode == "split":
        lf = (left_roi[0] + left_roi[2] // 2, left_roi[1] + left_roi[3] // 2)
        rf = (right_roi[0] + right_roi[2] // 2, right_roi[1] + right_roi[3] // 2)
        cmd = base + ["-filter_complex", split_filter(segments, lf, rf, sw, sh), "-map", "[v]"] + amap + enc
    else:
        raise SystemExit(f"unknown mode '{mode}' (center | pan | split)")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd + [str(out)], check=True)
    return {"mode": mode, "segments": segments, "output": str(out)}


def _roi(s: str) -> tuple[int, int, int, int]:
    x, y, w, h = (int(v) for v in s.split(","))
    return x, y, w, h


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Reframe a landscape clip to 1080x1920")
    ap.add_argument("clip", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--mode", choices=["center", "pan", "split"], default="center")
    ap.add_argument("--left-roi", type=_roi, help="x,y,w,h around the left face's mouth+chin")
    ap.add_argument("--right-roi", type=_roi, help="x,y,w,h around the right face's mouth+chin")
    ap.add_argument("--min-dwell", type=float, default=1.0)
    ap.add_argument("--turns", type=Path, help="diarized transcript JSON (ve transcribe --backend whisperx --diarize); "
                    "uses real speaker turns instead of face-box motion")
    ap.add_argument("--speaker-map", help="which side each speaker sits on, e.g. SPEAKER_00=left,SPEAKER_01=right")
    ap.add_argument("--clip-start", type=float, default=0.0,
                    help="where this clip starts in the transcribed source, so turn times line up")
    a = ap.parse_args(argv)
    segments = None
    if a.turns:
        if not a.speaker_map:
            raise SystemExit("--turns needs --speaker-map SPEAKER_00=left,SPEAKER_01=right")
        mapping = dict(kv.split("=", 1) for kv in a.speaker_map.split(","))
        words = json.loads(a.turns.read_text(encoding="utf-8"))["words"]
        shifted = [dict(w, start=w["start"] - a.clip_start, end=w["end"] - a.clip_start)
                   for w in words if w.get("type") == "word" and w["end"] > a.clip_start]
        segments = speaker_segments_from_words(shifted, mapping, a.min_dwell)
        if not segments:
            raise SystemExit("no usable speaker turns: check the transcript has speaker_id and the --speaker-map names")
    res = reframe(a.clip, a.output, a.mode, left_roi=a.left_roi, right_roi=a.right_roi, min_dur=a.min_dwell,
                  segments=segments)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
