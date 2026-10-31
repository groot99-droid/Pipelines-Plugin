"""Use-case questionnaire. Answers are saved as brief.json and select ONE primary recipe.

Asking first is what keeps competing tools out of the way: a vertical-clips job never sees the
long-form playbook, an action montage never touches Whisper or captions, and so on.
Run interactively (`ve ask`) or pass answers as JSON (`ve ask --answers '{...}'`) when an agent
has already collected them from the user.
"""
from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from videoeditor.core.platform import probe


@dataclass
class Question:
    key: str
    prompt: str
    choices: list[str]
    default: str
    applies: Callable[[dict], bool] = lambda brief: True
    help: dict[str, str] = field(default_factory=dict)


QUESTIONS: list[Question] = [
    Question(
        "deliverable", "What should the output be?", ["vertical", "landscape", "square"], "landscape",
        help={"vertical": "9:16 for TikTok/Reels/Shorts", "landscape": "16:9 for YouTube/desktop", "square": "1:1 feed"},
    ),
    Question(
        "reframe", "Source is landscape but you want vertical. How should it be reframed?",
        ["pan", "split", "center", "turns"], "center",
        applies=lambda b: b["deliverable"] == "vertical" and b.get("source_orientation") == "landscape",
        help={"pan": "hard-cut pan following whoever speaks (needs two face ROIs)",
              "split": "stacked split-screen, active speaker on top (needs two face ROIs)",
              "center": "plain center crop (single subject)",
              "turns": "pan using real speaker turns from a diarized transcript (needs the speech-plus extra + HF token)"},
    ),
    Question(
        "content", "What is in the footage?", ["dialogue", "action", "mixed"], "dialogue",
        help={"dialogue": "people talking: interview, podcast, talking head, tutorial",
              "action": "repeated impacts or beats: chopping, drumming, sports (no speech needed)",
              "mixed": "both; dialogue sections plus action sections"},
    ),
    Question(
        "goal", "What do you want from it?", ["highlights", "single_edit"], "single_edit",
        applies=lambda b: b["content"] != "action",
        help={"highlights": "find the best moments and cut several short clips",
              "single_edit": "one cleaned-up video: cut filler/retakes, polish"},
    ),
    Question(
        "captions", "Burn in captions?", ["none", "bold-overlay", "opus", "karaoke", "minimal"], "none",
        applies=lambda b: b["content"] != "action",
        help={"bold-overlay": "2-word UPPERCASE, safe-zone placed", "opus": "3-word, yellow active word",
              "karaoke": "4-word, green active word", "minimal": "6-word, clean"},
    ),
    Question(
        "grade", "Colour grade?", ["none", "warm_cinematic", "neutral_punch", "auto"], "none",
    ),
    Question(
        "overlays", "Animated overlays (titles, diagrams, charts)?", ["none", "pil", "remotion", "manim"], "none",
        help={"pil": "simple cards/counters, no extra install",
              "remotion": "React compositions (needs Node)", "manim": "math/technical diagrams (needs LaTeX)"},
    ),
    Question(
        "publish", "Prepare the result for publishing?", ["none", "prepare"], "none",
        help={"none": "just produce the video file",
              "prepare": "also add a `ve publish prepare` step: caption, per-platform checks, dry-run plan. Nothing is ever "
                         "sent without an explicit --yes, and private/draft is the default where a platform has one"},
    ),
]

QUESTION_KEYS = [q.key for q in QUESTIONS]


def select_recipes(brief: dict) -> tuple[str, list[str]]:
    """Return (primary recipe, add-on recipes)."""
    if brief["content"] == "action":
        primary = "action_montage"
    elif brief.get("goal") == "highlights":
        primary = "highlight_clips"
    else:
        primary = "long_form"
    addons = ["explainer"] if brief.get("overlays", "none") != "none" else []
    return primary, addons


def validate(brief: dict) -> list[str]:
    """Non-fatal warnings about answers that fight each other."""
    warns: list[str] = []
    if brief["content"] == "action" and brief.get("captions", "none") != "none":
        warns.append("captions ignored for action montage: the strike sounds are the rhythm")
    if brief["deliverable"] == "landscape" and brief.get("source_orientation") == "vertical":
        warns.append("vertical source with landscape deliverable: output will be letterboxed or cropped hard")
    if brief.get("reframe") == "turns" and importlib.util.find_spec("whisperx") is None:
        warns.append("reframe=turns needs whisperx: pip install 'videoeditor[speech-plus]' (and an HF_TOKEN); "
                     "without it use pan, which follows motion in two face boxes")
    if brief.get("reframe") in ("pan", "split", "turns") and brief.get("content") == "action":
        warns.append("speaker pan/split need talking faces; use center crop for action footage")
    return warns


def _check(q: Question, value: str) -> str:
    if value not in q.choices:
        raise SystemExit(f"invalid answer for '{q.key}': {value!r} (choose from {', '.join(q.choices)})")
    return value


def build_brief(sources: list[str], answers: dict | None = None, ask: Callable[[Question], str] | None = None) -> dict:
    """Fill the brief from `answers`, asking (via `ask`) for anything missing, else using defaults."""
    answers = dict(answers or {})
    brief: dict = {"sources": [str(Path(s).resolve()) for s in sources]}
    if sources and Path(sources[0]).exists():
        info = probe(Path(sources[0]))
        brief["source_orientation"] = info["orientation"]
        brief["source_probe"] = {k: info[k] for k in ("width", "height", "duration", "fps", "has_audio")}
    for q in QUESTIONS:
        if not q.applies(brief):
            continue
        if q.key in answers:
            brief[q.key] = _check(q, answers[q.key])
        elif ask is not None:
            brief[q.key] = _check(q, ask(q))
        else:
            brief[q.key] = q.default
    unknown = set(answers) - set(QUESTION_KEYS)
    if unknown:
        raise SystemExit(f"unknown answer key(s): {', '.join(sorted(unknown))}")
    brief["recipe"], brief["addons"] = select_recipes(brief)
    brief["warnings"] = validate(brief)
    return brief


def ask_interactive(q: Question) -> str:
    print(f"\n{q.prompt}")
    for i, c in enumerate(q.choices, 1):
        mark = " (default)" if c == q.default else ""
        note = f"  - {q.help[c]}" if c in q.help else ""
        print(f"  {i}. {c}{mark}{note}")
    while True:
        raw = input("> ").strip()
        if not raw:
            return q.default
        if raw.isdigit() and 1 <= int(raw) <= len(q.choices):
            return q.choices[int(raw) - 1]
        if raw in q.choices:
            return raw
        print(f"  pick 1-{len(q.choices)} or a name")


def save_brief(brief: dict, edit_dir: Path) -> Path:
    edit_dir.mkdir(parents=True, exist_ok=True)
    p = edit_dir / "brief.json"
    p.write_text(json.dumps(brief, indent=2), encoding="utf-8")
    return p


def load_brief(edit_dir: Path) -> dict:
    p = edit_dir / "brief.json"
    if not p.exists():
        raise SystemExit(f"no brief at {p}; run `ve ask` first")
    return json.loads(p.read_text(encoding="utf-8"))


def schema() -> list[dict]:
    """Machine-readable questions, for agents that ask the user themselves."""
    return [{"key": q.key, "prompt": q.prompt, "choices": q.choices, "default": q.default, "help": q.help}
            for q in QUESTIONS]


__all__ = ["QUESTIONS", "build_brief", "ask_interactive", "save_brief", "load_brief", "schema"]
