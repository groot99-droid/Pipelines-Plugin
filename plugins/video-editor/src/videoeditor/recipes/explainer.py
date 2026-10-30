"""Add-on: animated overlays (titles, diagrams, charts) composited under captions."""
from videoeditor.recipes import Recipe, register


def steps(b: dict) -> list[str]:
    engine = b.get("overlays", "pil")
    out = ["# explainer add-on: overlays",
           "# agree palette, font and visual language with the user BEFORE building anything"]
    if engine == "pil":
        out.append('ve overlay "Headline" --duration 4 -o <edit>/animations/slot_1/render.mp4   # zero-setup text card')
    elif engine == "manim":
        out.append("# build each slot with Manim; read skills/manim-video/SKILL.md (needs LaTeX + `pip install manim`)")
    elif engine == "hyperframes":
        out.append("# scaffold in <edit>/animations/slot_N/: npx --yes hyperframes init . --example blank --non-interactive --skip-skills")
    elif engine == "remotion":
        out.append("# scaffold in <edit>/animations/slot_N/ with Remotion; render to render.mp4")
    out += ["# several animations: build them in PARALLEL sub-agents, one slot each",
            '# add {"file", "start_in_output", "duration"} entries to the EDL "overlays"; sync the payoff frame to the spoken payoff word',
            "# render.py composites overlays, then captions LAST"]
    return out


register(Recipe("explainer", "Animated overlays", "Add animated overlays composited beneath captions.", steps))
