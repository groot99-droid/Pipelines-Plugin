"""Finishing pass for "She Does Not Run": transitions between ve-rendered segments, then the sound mix.

ve render only cuts hard, so this joins its graded segments (clips_graded/seg_NN_<src>.mp4) itself:
runs of hard cuts are concatenated, and runs are joined with xfade / acrossfade. Then the clips' own audio
(ducked) is mixed with beds, music and SFX from the sound library, and the result is loudness-normalised.

    python finish.py finish.json -o She_Does_Not_Run.mp4 [--segments clips_graded]

finish.json:
  "transitions": {"<src before>": {"type": "fadeblack"|"fade"|..., "dur": 1.0}}   boundary after that source
  "native_gain_db": -6
  "cues": [{"file": path, "seg": "<src>", "offset": s, "gain_db": g, "dur": s|null, "fade_in": s, "fade_out": s,
            "loop": bool}]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

FPS = 24
SR = 48000


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{r.stderr[-3000:]}")


def probe_dur(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip()
    return int(out) / FPS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("config", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--segments", default="clips_graded")
    ap.add_argument("--edl", type=Path, default=Path("edl.json"))
    a = ap.parse_args()

    cfg = json.loads(a.config.read_text(encoding="utf-8"))
    edl = json.loads(a.edl.read_text(encoding="utf-8"))
    srcs = [r["source"] for r in edl["ranges"]]
    seg_dir = Path(a.segments)
    segs = [seg_dir / f"seg_{i:02d}_{s}.mp4" for i, s in enumerate(srcs)]
    for p in segs:
        if not p.exists():
            sys.exit(f"missing segment {p}; run ve render first")
    lens = [probe_dur(p) for p in segs]
    trans = cfg.get("transitions", {})

    # timeline: where each segment starts in the output, accounting for overlaps
    starts, t = [], 0.0
    for i, (s, L) in enumerate(zip(srcs, lens)):
        starts.append(t)
        t += L
        if i < len(srcs) - 1 and s in trans:
            t -= trans[s]["dur"]
    total = t
    seg_start = dict(zip(srcs, starts))

    # runs of hard cuts -> one file each (concat copy)
    work = a.output.parent / "_finish"
    work.mkdir(exist_ok=True)
    runs, cur = [], []
    for i, s in enumerate(srcs):
        cur.append(segs[i])
        if i == len(srcs) - 1 or s in trans:
            runs.append((cur, trans.get(s)))
            cur = []
    run_files, run_lens = [], []
    for k, (files, _) in enumerate(runs):
        lst = work / f"run_{k:02d}.txt"
        lst.write_text("".join(f"file '{f.resolve().as_posix()}'\n" for f in files), encoding="utf-8")
        out = work / f"run_{k:02d}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        run_files.append(out)
        run_lens.append(sum(lens[segs.index(f)] for f in files))

    # xfade chain
    inputs, fc = [], []
    for f in run_files:
        inputs += ["-i", str(f)]
    v, au, acc = "[0:v]", "[0:a]", run_lens[0]
    for k in range(1, len(run_files)):
        tr = runs[k - 1][1]
        d = tr["dur"]
        off = acc - d
        fc.append(f"{v}[{k}:v]xfade=transition={tr['type']}:duration={d}:offset={off:.4f}[v{k}]")
        fc.append(f"{au}[{k}:a]acrossfade=d={d}:c1=tri:c2=tri[a{k}]")
        v, au = f"[v{k}]", f"[a{k}]"
        acc = acc + run_lens[k] - d
    native_db = cfg.get("native_gain_db", -6)
    fc.append(f"{au}volume={native_db}dB,aresample={SR}[nat]")

    # cues
    mix, narr = ["[nat]"], []
    n_in = len(run_files)
    for j, c in enumerate(cfg.get("cues", [])):
        at = c["at"] if "at" in c else seg_start[c["seg"]] + c.get("offset", 0.0)
        dur = c.get("dur")
        if c.get("loop"):
            inputs += ["-stream_loop", "-1"]
        inputs += ["-i", c["file"]]
        idx = n_in + j
        chain = f"[{idx}:a]aresample={SR},aformat=channel_layouts=stereo"
        if c.get("start_in_file"):
            chain += f",atrim=start={c['start_in_file']},asetpts=PTS-STARTPTS"
        if dur:
            chain += f",atrim=0:{dur}"
            if c.get("fade_out"):
                chain += f",afade=t=out:st={max(0, dur - c['fade_out']):.3f}:d={c['fade_out']}"
        if c.get("fade_in"):
            chain += f",afade=t=in:st=0:d={c['fade_in']}"
        chain += f",volume={c.get('gain_db', 0)}dB,adelay={int(at * 1000)}|{int(at * 1000)}[c{j}]"
        fc.append(chain)
        (narr if c.get("narration") else mix).append(f"[c{j}]")
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{total:.4f}[bed]")
    if narr:
        # narration on its own bus; it ducks everything else (music, beds, SFX, the clips' own sound)
        d = cfg.get("duck", {})
        fc.append(f"{''.join(narr)}amix=inputs={len(narr)}:normalize=0,apad,atrim=0:{total:.4f},"
                  f"asplit=2[nkey][nvox]")
        fc.append(f"[bed][nkey]sidechaincompress=threshold={d.get('threshold', 0.015)}:ratio={d.get('ratio', 8)}:"
                  f"attack={d.get('attack_ms', 20)}:release={d.get('release_ms', 400)}[ducked]")
        fc.append("[ducked][nvox]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[mixed]")
    else:
        fc.append("[bed]alimiter=limit=0.89[mixed]")

    pre = work / "prenorm.mp4"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", v, "-map", "[mixed]",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "pcm_s16le", "-t", f"{total:.4f}", str(pre.with_suffix(".mov"))])
    pre = pre.with_suffix(".mov")

    # two-pass loudnorm to -14 LUFS / -1 dBTP
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(pre), "-af",
                        "loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(pre), "-c:v", "copy", "-af", f"{ln},aresample={SR}",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(a.output)])
    print(json.dumps({"total_s": round(total, 3), "runs": len(run_files),
                      "seg_starts": {s: round(x, 3) for s, x in seg_start.items()}}, indent=1))


if __name__ == "__main__":
    main()
