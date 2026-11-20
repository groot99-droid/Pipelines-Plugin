"""Fit each narration line to its window, then write the narration cues for finish.json and the .srt.

For each line in script.json:
  1. shorten any pause longer than 0.6 s to 0.6 s (the TTS leaves long gaps at ellipses and full stops),
  2. if it is still longer than its window, speed it up, at most MAX_TEMPO (pitch is kept),
  3. normalise it to -16 LUFS,
and write fitted/<id>.wav. Lines are placed at their window start. A line that still does not fit is reported,
not squeezed further.

    python fit.py            # from edit/narration
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_TEMPO = 1.08
TARGET_LUFS = -16.0


def dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout)


def lufs(p: Path) -> float:
    e = subprocess.run(["ffmpeg", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)[-1])


def ff(args: list[str]) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)


def srt_ts(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main() -> None:
    script = json.loads((HERE / "script.json").read_text(encoding="utf-8"))
    out_dir = HERE / "fitted"
    out_dir.mkdir(exist_ok=True)
    cues, srt, problems = [], [], []
    for n, line in enumerate(script["lines"], 1):
        src = HERE / f"{line['id']}.wav"
        a, b = line.get("place", line["window"])
        room = b - a
        tmp = out_dir / f"{line['id']}_tight.wav"
        # trim leading/trailing silence, and cap inner pauses at 0.6 s
        ff(["-i", str(src), "-af",
            "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,"
            "silenceremove=stop_periods=-1:stop_duration=0.6:stop_threshold=-42dB:stop_silence=0.6,"
            "areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.15,areverse",
            "-ar", "48000", "-ac", "2", str(tmp)])
        length = dur(tmp)
        tempo = max(1.0, length / room)
        if tempo > MAX_TEMPO:
            problems.append(f"{line['id']}: {length:.2f}s needs x{tempo:.2f} to fit {room:.1f}s; held at x{MAX_TEMPO}")
            tempo = MAX_TEMPO
        fitted = out_dir / f"{line['id']}.wav"
        gain = TARGET_LUFS - lufs(tmp)
        ff(["-i", str(tmp), "-af", f"atempo={tempo:.4f},volume={gain:.2f}dB", "-ar", "48000", str(fitted)])
        tmp.unlink()
        flen = dur(fitted)
        line["fitted"] = {"start": a, "length": round(flen, 3), "tempo": round(tempo, 3)}
        cues.append({"file": fitted.as_posix(), "at": a, "narration": True, "gain_db": 0})
        srt.append(f"{n}\n{srt_ts(a)} --> {srt_ts(a + flen)}\n{line['text']}\n")
        print(f"{line['id']}  {length:5.2f}s -> {flen:5.2f}s at x{tempo:.3f}  room {room:4.1f}s  at {a:6.2f}")
    (HERE / "script.json").write_text(json.dumps(script, indent=1, ensure_ascii=False), encoding="utf-8")
    (HERE / "narration_cues.json").write_text(json.dumps(cues, indent=1), encoding="utf-8")
    (HERE.parent / "She_Does_Not_Run.srt").write_text("\n".join(srt), encoding="utf-8")
    for p in problems:
        print("DOES NOT FIT:", p)


if __name__ == "__main__":
    main()
