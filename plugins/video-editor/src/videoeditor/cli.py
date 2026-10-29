"""`ve`: one entry point. Run `ve ask` first; it selects the recipe and `ve plan` prints its steps."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _edit_dir(arg: Path | None, fallback_from: str | None = None) -> Path:
    if arg:
        return arg.resolve()
    if fallback_from:
        return Path(fallback_from).resolve().parent / "edit"
    return Path.cwd() / "edit"


def cmd_ask(a) -> None:
    from videoeditor import questionnaire as Q

    if a.schema:
        print(json.dumps(Q.schema(), indent=2))
        return
    if not a.sources:
        sys.exit("give at least one source video, or use --schema")
    answers = json.loads(a.answers) if a.answers else None
    interactive = answers is None and sys.stdin.isatty() and not a.defaults
    brief = Q.build_brief(a.sources, answers, Q.ask_interactive if interactive else None)
    edit = _edit_dir(a.edit_dir, a.sources[0])
    path = Q.save_brief(brief, edit)
    print(f"\nrecipe: {brief['recipe']}" + (f" + {', '.join(brief['addons'])}" if brief["addons"] else ""))
    for w in brief["warnings"]:
        print(f"warning: {w}")
    print(f"brief saved: {path}\nnext: ve plan --edit-dir {edit}")


def cmd_plan(a) -> None:
    from videoeditor import questionnaire as Q
    from videoeditor import recipes

    brief = Q.load_brief(_edit_dir(a.edit_dir))
    for name in [brief["recipe"], *brief["addons"]]:
        r = recipes.get(name)
        print(f"\n== {r.title} ==  ({r.summary})")
        print(f"playbook: {r.playbook}")
        for s in r.steps(brief):
            print(f"  {s}")


def cmd_transcribe(a) -> None:
    from videoeditor.core import transcribe as T

    for v in a.video:
        edit = _edit_dir(a.edit_dir, str(v))
        T.transcribe(v.resolve(), edit, a.model, None if a.language == "auto" else a.language, a.vad, a.force,
                     backend=a.backend, diarize=a.diarize, hf_token=a.hf_token, min_speakers=a.min_speakers,
                     max_speakers=a.max_speakers, clean_speech=a.clean_speech)


def cmd_pack(a) -> None:
    from videoeditor.core import pack

    sys.argv = ["ve pack", "--edit-dir", str(_edit_dir(a.edit_dir)), *(["-o", str(a.output)] if a.output else [])]
    pack.main()


def cmd_find(a) -> None:
    from videoeditor.core import moments as M
    import tempfile

    lo, hi = (int(x) for x in a.band.split(":"))
    with tempfile.TemporaryDirectory() as td:
        if a.stem:
            from videoeditor.core import stems

            wav = stems.separate(a.video, _edit_dir(a.edit_dir, str(a.video)) / "stems", [a.stem], mono_16k=True)[a.stem]
        else:
            wav = Path(td) / "a.wav"
            M.extract_wav(a.video, wav)
        peaks = M.detect_transients(wav, lo, hi, a.min_flux, a.min_gap)
    if a.top:
        peaks = sorted(peaks, key=lambda x: -x["flux"])[: a.top]
        peaks.sort(key=lambda x: x["time"])
    from videoeditor.core.platform import probe
    out = M.shots_around(peaks, duration=probe(a.video)["duration"]) if a.shots else peaks
    text = json.dumps(out, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text)
        print(f"{len(out)} {'shots' if a.shots else 'strikes'} -> {a.output}")
    else:
        print(text)


def cmd_verify(a) -> None:
    from videoeditor.core import moments as M

    items = json.loads(a.candidates.read_text())
    times = [float(i["strike"] if "strike" in i else i["time"]) for i in items]
    paths = M.verify_frames(a.video, times, a.out)
    print(f"{len(paths)} frames in {a.out}; view them and drop any candidate where the event is not visible")


def cmd_cut(a) -> None:
    a.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-to", str(a.end), "-i", str(a.video),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    str(a.output)], check=True)
    print(a.output)


def cmd_reframe(a) -> None:
    from videoeditor.core import reframe

    argv = [str(a.clip), "-o", str(a.output), "--mode", a.mode, "--min-dwell", str(a.min_dwell)]
    if a.left_roi:
        argv += ["--left-roi", a.left_roi]
    if a.right_roi:
        argv += ["--right-roi", a.right_roi]
    if a.turns:
        argv += ["--turns", str(a.turns), "--speaker-map", a.speaker_map or "", "--clip-start", str(a.clip_start)]
    reframe.main(argv)


def cmd_separate(a) -> None:
    from videoeditor.core import stems

    paths = stems.separate(a.media.resolve(), _edit_dir(a.edit_dir, str(a.media)) / "stems", a.stems,
                           model=a.model, device=a.device)
    for name, p in paths.items():
        print(f"{name}: {p}")


def cmd_edl(a) -> None:
    sources = {}
    for s in a.source:
        name, _, path = s.partition("=")
        if not path:
            sys.exit(f"--source expects NAME=PATH, got {s!r}")
        sources[name] = str(Path(path).resolve())
    ranges = json.loads(a.ranges.read_text())
    for r in ranges:
        if "source" not in r:
            if len(sources) != 1:
                sys.exit("ranges without 'source' need exactly one --source")
            r["source"] = next(iter(sources))
        if r["source"] not in sources:
            sys.exit(f"range references unknown source {r['source']!r}")
    edl = {"version": 1, "sources": sources,
           "ranges": [{k: v for k, v in r.items() if k in ("source", "start", "end", "beat", "quote", "reason")} for r in ranges],
           "total_duration_s": round(sum(float(r["end"]) - float(r["start"]) for r in ranges), 3)}
    if a.grade:
        edl["grade"] = a.grade
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(edl, indent=2))
    print(f"{a.output} ({len(ranges)} ranges, {edl['total_duration_s']}s)")


def cmd_captions(a) -> None:
    from videoeditor.core import captions

    captions.main([str(a.edl), "--style", a.style])


def cmd_render(a) -> None:
    from videoeditor.core import render

    sys.argv = ["ve render", str(a.edl), "-o", str(a.output), *a.extra]
    render.main()


def cmd_grade(a) -> None:
    from videoeditor.core import grade

    sys.argv = ["ve grade", *a.extra]
    grade.main()


def cmd_timeline(a) -> None:
    from videoeditor.core import timeline

    sys.argv = ["ve timeline", *a.extra]
    timeline.main()


def cmd_overlay(a) -> None:
    from videoeditor.core import overlays

    if a.engine == "pil":
        if not a.text:
            sys.exit("the pil engine needs the card text")
        print(overlays.render_text_card(a.text, a.output, a.duration, font_path=a.font))
        return
    pages, duration = None, a.duration
    if a.captions_from:
        edl_path = a.captions_from.resolve()
        edl = json.loads(edl_path.read_text())
        pages = overlays.caption_pages_from_edl(edl, edl_path.parent)
        duration = a.duration if a.duration_set else float(edl.get("total_duration_s") or a.duration)
    w, h = (int(v) for v in a.size.lower().split("x"))
    spec = overlays.build_overlay_spec(title=a.text, pages=pages, duration=duration, size=(w, h),
                                       transparent=a.transparent, font_family=a.font_family)
    slot = overlays.scaffold_remotion_slot(a.output.resolve().parent, spec)
    print(overlays.render_remotion(slot, a.output.name, a.transparent, a.browser))


def cmd_doctor(a) -> None:
    from videoeditor import doctor

    raise SystemExit(doctor.main(as_json=a.json))


def cmd_publish(a) -> None:
    from videoeditor.publish import cli as publish_cli

    publish_cli.main(a.extra)


def cmd_finish(a) -> None:
    """Single video in -> optional captions + grade + loudnorm -> out. Used for per-clip finishing."""
    from videoeditor.core import captions, transcribe as T
    from videoeditor.core.platform import probe

    video = a.video.resolve()
    edit = a.edit_dir.resolve() if a.edit_dir else a.output.resolve().parent / f"edit_{video.stem}"
    edit.mkdir(parents=True, exist_ok=True)
    dur = probe(video)["duration"]
    edl = {"version": 1, "sources": {video.stem: str(video)},
           "ranges": [{"source": video.stem, "start": 0.0, "end": dur}], "total_duration_s": dur}
    if a.grade:
        edl["grade"] = a.grade
    if a.captions != "none":
        T.transcribe(video, edit, a.model, None if a.language == "auto" else a.language)
        edl["subtitles"] = str(captions.build_captions(edl, edit, a.captions))
    edl_path = edit / "edl.json"
    edl_path.write_text(json.dumps(edl, indent=2))
    from videoeditor.core import render
    sys.argv = ["ve render", str(edl_path), "-o", str(a.output.resolve())]
    render.main()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="ve", description="Questionnaire-driven video editor")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ask", help="questionnaire -> brief.json -> recipe")
    p.add_argument("sources", nargs="*")
    p.add_argument("--answers", help="JSON of answers (skips prompts for those keys)")
    p.add_argument("--defaults", action="store_true", help="use defaults for unanswered questions, no prompts")
    p.add_argument("--schema", action="store_true", help="print the questions as JSON and exit")
    p.add_argument("--edit-dir", type=Path)
    p.set_defaults(fn=cmd_ask)

    p = sub.add_parser("plan", help="print the selected recipe's steps")
    p.add_argument("--edit-dir", type=Path)
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("transcribe", help="local Whisper -> Scribe-shaped JSON (cached)")
    p.add_argument("video", type=Path, nargs="+")
    p.add_argument("--edit-dir", type=Path)
    p.add_argument("--model", default="base.en")
    p.add_argument("--language", default="en")
    p.add_argument("--vad", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--backend", default="faster-whisper", choices=["faster-whisper", "whisperx"],
                   help="whisperx = tighter word timing + optional speaker labels (extra: speech-plus)")
    p.add_argument("--diarize", action="store_true", help="label speakers (whisperx backend, needs HF_TOKEN)")
    p.add_argument("--hf-token", help="Hugging Face token for diarization (or set HF_TOKEN)")
    p.add_argument("--min-speakers", type=int)
    p.add_argument("--max-speakers", type=int)
    p.add_argument("--clean-speech", action="store_true",
                   help="separate the vocals stem first (Demucs, extra: stems); for music under speech")
    p.set_defaults(fn=cmd_transcribe)

    p = sub.add_parser("pack", help="transcripts -> takes_packed.md")
    p.add_argument("--edit-dir", type=Path)
    p.add_argument("-o", "--output", type=Path)
    p.set_defaults(fn=cmd_pack)

    p = sub.add_parser("find", help="detect audio impact transients")
    p.add_argument("video", type=Path)
    p.add_argument("--band", default="1000:6000")
    p.add_argument("--min-flux", type=float, default=30.0)
    p.add_argument("--min-gap", type=float, default=0.6)
    p.add_argument("--top", type=int, default=0)
    p.add_argument("--shots", action="store_true", help="emit cut ranges (0.4s before, 0.5s after each strike)")
    p.add_argument("--stem", help="detect on an isolated stem (e.g. drums) when music is playing (extra: stems)")
    p.add_argument("--edit-dir", type=Path)
    p.add_argument("-o", "--output", type=Path)
    p.set_defaults(fn=cmd_find)

    p = sub.add_parser("verify", help="grab a frame per candidate so off-screen events can be dropped")
    p.add_argument("video", type=Path)
    p.add_argument("candidates", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("cut", help="accurate re-encoded cut of one range")
    p.add_argument("video", type=Path)
    p.add_argument("--start", type=float, required=True)
    p.add_argument("--end", type=float, required=True)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.set_defaults(fn=cmd_cut)

    p = sub.add_parser("reframe", help="landscape -> 1080x1920 (center | pan | split)")
    p.add_argument("clip", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--mode", choices=["center", "pan", "split"], default="center")
    p.add_argument("--left-roi")
    p.add_argument("--right-roi")
    p.add_argument("--min-dwell", type=float, default=1.0)
    p.add_argument("--turns", type=Path, help="diarized transcript JSON: use real speaker turns instead of motion")
    p.add_argument("--speaker-map", help="SPEAKER_00=left,SPEAKER_01=right")
    p.add_argument("--clip-start", type=float, default=0.0, help="clip start time within the transcribed source")
    p.set_defaults(fn=cmd_reframe)

    p = sub.add_parser("separate", help="split audio into stems with Demucs (extra: stems)")
    p.add_argument("media", type=Path)
    p.add_argument("--stems", nargs="+", default=["vocals", "no_vocals"],
                   help="e.g. vocals drums bass other, or no_vocals for everything else")
    p.add_argument("--model", default="htdemucs")
    p.add_argument("--device", default="cpu")
    p.add_argument("--edit-dir", type=Path)
    p.set_defaults(fn=cmd_separate)

    p = sub.add_parser("edl", help="build edl.json from sources and a ranges JSON list")
    p.add_argument("--source", action="append", required=True, metavar="NAME=PATH")
    p.add_argument("--ranges", type=Path, required=True)
    p.add_argument("--grade")
    p.add_argument("-o", "--output", type=Path, required=True)
    p.set_defaults(fn=cmd_edl)

    p = sub.add_parser("captions", help="build captions for an EDL")
    p.add_argument("edl", type=Path)
    p.add_argument("--style", default="bold-overlay", choices=["bold-overlay", "opus", "karaoke", "minimal"])
    p.set_defaults(fn=cmd_captions)

    p = sub.add_parser("render", help="EDL -> video (extra flags pass through to render.py)")
    p.add_argument("edl", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("grade", help="colour grade (flags pass through to grade.py)")
    p.set_defaults(fn=cmd_grade)

    p = sub.add_parser("timeline", help="filmstrip + waveform PNG (args pass through to timeline.py)")
    p.set_defaults(fn=cmd_timeline)

    p = sub.add_parser("overlay", help="overlay clip: PIL text card, or a Remotion slot (titles/captions)")
    p.add_argument("text", nargs="?", help="title / card text")
    p.add_argument("--engine", choices=["pil", "remotion"], default="pil")
    p.add_argument("--duration", type=float, default=None, help="seconds (default 4, or the EDL length with --captions-from)")
    p.add_argument("--font", help="pil: path to a .ttf")
    p.add_argument("--font-family", help="remotion: installed font family name")
    p.add_argument("--captions-from", type=Path, help="remotion: EDL whose captions become overlay pages")
    p.add_argument("--transparent", action="store_true", help="remotion: WebM with alpha instead of an opaque MP4")
    p.add_argument("--size", default="1920x1080", help="remotion: WxH")
    p.add_argument("--browser", help="remotion: Chrome/Chromium executable (or set REMOTION_BROWSER_EXECUTABLE)")
    p.add_argument("-o", "--output", type=Path, required=True)
    p.set_defaults(fn=cmd_overlay)

    p = sub.add_parser("doctor", help="what is installed and configured (names only, never credential values)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("publish", add_help=False, help="send a finished video through official platform APIs (dry run by default)")
    p.set_defaults(fn=cmd_publish)

    p = sub.add_parser("finish", help="caption/grade/loudnorm one finished clip")
    p.add_argument("video", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--captions", default="none", choices=["none", "bold-overlay", "opus", "karaoke", "minimal"])
    p.add_argument("--grade")
    p.add_argument("--model", default="base.en")
    p.add_argument("--language", default="en")
    p.add_argument("--edit-dir", type=Path)
    p.set_defaults(fn=cmd_finish)

    a, extra = ap.parse_known_args(argv)
    if a.cmd == "overlay":  # distinguish "default 4s" from "user asked for 4s" (EDL length wins only by default)
        a.duration_set = a.duration is not None
        a.duration = a.duration if a.duration is not None else 4.0
    if extra and a.cmd not in ("render", "grade", "timeline", "publish"):
        ap.error(f"unrecognized arguments: {' '.join(extra)}")
    a.extra = extra  # render/grade/timeline pass these through to their own parsers
    a.fn(a)


if __name__ == "__main__":
    main()
