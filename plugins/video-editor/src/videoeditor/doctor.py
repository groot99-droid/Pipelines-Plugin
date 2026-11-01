"""`ve doctor`: what is installed and what is configured, by name only. It never prints a credential value.

Required for every recipe: ffmpeg, ffprobe, numpy, Pillow. Everything else is an optional extra and is reported
with the pip extra that adds it, so an agent can say exactly what is missing for the job at hand.
"""
from __future__ import annotations

import importlib.util
import json
import shlex
import shutil
import subprocess
import sys

REQUIRED_PY = (("numpy", "numpy"), ("PIL", "Pillow"))
# (import name, pip extra, what it is for, the package to pip install directly; the plugin is not on PyPI)
OPTIONAL_PY = (
    ("faster_whisper", "videoeditor[speech]", "local transcription (every dialogue recipe)", "faster-whisper"),
    ("whisperx", "videoeditor[speech-plus]", "tighter word timing, optional speaker labels (several GB)", "whisperx"),
    ("demucs", "videoeditor[stems]", "stem separation: music under speech, drums for action montages (several GB)", "demucs>=4.1"),
    ("requests", "videoeditor[publish]", "ve publish: HTTP client", "requests"),
    ("keyring", "videoeditor[publish]", "ve publish: token storage in the OS keyring", "keyring"),
)


def _first_line(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15, encoding="utf-8", errors="replace").stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return (out.splitlines() or [""])[0].strip() or None


def _ffmpeg_has_filter(name: str) -> bool | None:
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True, timeout=15, encoding="utf-8", errors="replace").stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return any(line.split()[1:2] == [name] for line in out.splitlines() if line.strip())


def report() -> dict:
    tools = {}
    for name in ("ffmpeg", "ffprobe", "node", "npm", "fc-match"):
        path = shutil.which(name)
        tools[name] = {"found": bool(path), "version": _first_line([name, "-version"]) if path and name in ("ffmpeg", "node", "npm") else None}
    tools["ffmpeg"]["subtitles_filter"] = _ffmpeg_has_filter("subtitles") if tools["ffmpeg"]["found"] else None
    required = {pkg: importlib.util.find_spec(mod) is not None for mod, pkg in REQUIRED_PY}
    optional = {mod: {"installed": importlib.util.find_spec(mod) is not None, "extra": extra, "for": why, "pip": pip}
                for mod, extra, why, pip in OPTIONAL_PY}
    publish = {}
    try:
        from videoeditor.publish.platforms import NAMES, get

        publish = {n: get(n).is_configured() for n in NAMES}
    except Exception:       # never let a missing optional dependency break the report
        publish = {}
    problems = []
    if not (tools["ffmpeg"]["found"] and tools["ffprobe"]["found"]):
        problems.append("ffmpeg and ffprobe must be on PATH")
    if tools["ffmpeg"].get("subtitles_filter") is False:
        problems.append("this ffmpeg has no 'subtitles' filter (libass): burned-in captions will fail")
    problems += [f"python package {pkg} is missing (required)" for pkg, ok in required.items() if not ok]
    return {"python": sys.version.split()[0], "tools": tools, "required_python": required,
            "optional_python": optional, "publish_configured": publish, "problems": problems, "ok": not problems}


def render(rep: dict) -> str:
    lines = [f"python {rep['python']}", ""]
    for name, t in rep["tools"].items():
        extra = f"  {t['version']}" if t.get("version") else ""
        lines.append(f"  {'ok ' if t['found'] else '-- '} {name}{extra}")
    lines += ["", "required python packages:"] + [f"  {'ok ' if ok else 'MISSING'} {pkg}" for pkg, ok in rep["required_python"].items()]
    lines += ["", "optional extras:"]
    for mod, o in rep["optional_python"].items():
        lines.append(f"  {'ok ' if o['installed'] else '-- '} {mod:15s} pip install {shlex.quote(o['pip'])}  ({o['for']})")
    if rep["publish_configured"]:
        lines += ["", "publishing credentials found (names only):"] + [f"  {'yes' if v else 'no '} {k}" for k, v in rep["publish_configured"].items()]
    lines += ["", "OK" if rep["ok"] else "PROBLEMS:"] + [f"  - {p}" for p in rep["problems"]]
    return "\n".join(lines)


def main(as_json: bool = False) -> int:
    rep = report()
    print(json.dumps(rep, indent=2) if as_json else render(rep))
    return 0 if rep["ok"] else 1
