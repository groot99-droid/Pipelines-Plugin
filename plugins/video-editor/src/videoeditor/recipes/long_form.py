"""One cleaned-up edit: cut filler and retakes, grade, caption, QA."""
from videoeditor.recipes import Recipe, publish_step, register


def steps(b: dict) -> list[str]:
    srcs = " ".join(b["sources"])
    out = ["# long_form: raw takes -> one polished edit",
           f"ve transcribe {srcs}",
           "ve pack --edit-dir <edit>            # read takes_packed.md; pre-scan for slips; propose a plain-English strategy",
           "# WAIT for the user to confirm the strategy before touching the cut (Hard Rule 11)",
           "ve edl --source NAME=PATH ... --ranges ranges.json -o <edit>/edl.json   # ranges on word boundaries, padded 30-200ms"]
    grade = b.get("grade", "none")
    if grade != "none":
        out.append(f'# set "grade": "{grade}" in the EDL (applied per segment)')
    cap = b.get("captions", "none")
    if cap != "none":
        out.append(f"ve captions <edit>/edl.json --style {cap}   # then set \"subtitles\" in the EDL; applied LAST")
    out += ["ve render <edit>/edl.json -o <edit>/preview.mp4 --preview",
            "ve timeline <edit>/preview.mp4 START END   # at every cut boundary (+-1.5s); fix, re-render, max 3 passes",
            "ve render <edit>/edl.json -o <edit>/final.mp4   # on user confirmation"]
    return out + publish_step(b, "<edit>/final.mp4")


register(Recipe("long_form", "Long-form edit", "Cut filler and retakes into one polished video.", steps))
