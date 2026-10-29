"""Cut on every strike/beat. No transcription, no captions."""
from videoeditor.recipes import Recipe, publish_step, register


def steps(b: dict) -> list[str]:
    srcs = b["sources"]
    out = ["# action_montage: cut on each impact; skip Whisper and captions"]
    for s in srcs:
        out.append(f"ve find {s} --shots -o <edit>/strikes_{{name}}.json   # tune --band/--min-flux/--min-gap per playbook; add --stem drums if music is playing (extra: stems)")
    out += ["ve verify <video> <edit>/strikes_NAME.json --out <edit>/verify   # sample a frame per strike; DROP off-screen ones",
            "# pick a varied set across angles (~0.9s/beat; 50-65 beats for a 45-60s montage)",
            "ve edl --source NAME=PATH ... --ranges kept_ranges.json -o <edit>/edl.json"]
    if b.get("grade", "none") != "none":
        out.append(f'# set "grade": "{b["grade"]}" in the EDL')
    out += ["ve render <edit>/edl.json -o <edit>/preview.mp4 --preview",
            "ve render <edit>/edl.json -o <edit>/final.mp4"]
    if b["deliverable"] == "vertical" and b.get("source_orientation") == "landscape":
        out.append("ve reframe <edit>/final.mp4 --mode center -o <edit>/final_vertical.mp4   # center crop; pan/split need talking faces")
    final = "<edit>/final_vertical.mp4" if b["deliverable"] == "vertical" and b.get("source_orientation") == "landscape" else "<edit>/final.mp4"
    return out + publish_step(b, final)


register(Recipe("action_montage", "Action / rhythm montage", "Cut on every strike or beat using audio transients.", steps))
