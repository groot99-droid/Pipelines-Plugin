# _Context/brand/ — the brand gates

Constants for this studio's output: its palette, its voice, its render rules.
Every pipeline needs two or three of them resolved before it makes anything.

**The author writes these.** A gate encodes taste and prior decisions. It cannot
be generated, and no pipeline may write one from a search result, a library or an
inference. The `brand-gate` pipeline transcribes what the author says and nothing
more.

This folder sits inside the vault so the gates open in Obsidian and a note's
wikilink to one resolves. Its name starts with `_`, so nothing here is counted as
a Content MD.

`studio/pipeline/spec.yaml` lists the ten under `gates:`, and what each must
answer. What a gate does answer is read from the file itself: each `## N. Title`
section is an answer, and a `## N. Unresolved` section, last, is what it declares
it does not answer. Replacing a gate is replacing its file.

A gate is written through the `brand-gate` pipeline: the author is interviewed,
the gate is built from the transcript alone, the whole file is shown, and
`studio/pipeline/gate_md.py` writes it only after a yes. Its section 0,
Provenance, names the author, the date and the run.

## The ten

| Gate | State | Must answer | Needed by |
|---|---|---|---|
| `visual_identity` | **authored**, with a declared gap | What does work from this studio look like? Motifs, framing, texture, what is off-limits. | ui-direction, ui-build, brush, still-image, video-shot |
| `typography_system` | **authored** | Typefaces, scale, tracking, hierarchy, licensing. | ui-direction, ui-build |
| `color_science` | **authored**, with a declared gap | Working space, LUTs, palette with hex values, grading rules. | ui-direction, still-image, edit-2d |
| `motion_language` | not authored | Camera grammar, easing, shot lengths, transitions to avoid. | video-shot, scene-3d |
| `sound_identity` | not authored | Instrumentation, tempo range, mix targets, sonic signature. | music-cue |
| `brand_voice` | not authored | Diction, register, person, banned phrasings. | ui-build, music-cue |
| `narrative_continuity` | not authored | Canon rules, character and environment persistence, what may not be retconned. | video-shot |
| `render_philosophy` | not authored | Quality bar, when to re-render and when to accept, output specs. | edit-2d, scene-3d |
| `pipeline_ethics` | not authored | Disclosure, provenance, sourcing rules, what is never generated. | none yet |
| `memory_discipline` | not authored | Quotable against summarizable, retention, what leaves the machine. | none yet |

## Authored is not complete

Two of the three authored gates say what they do not answer:

- `visual_identity` section 7: what **generated imagery** looks like. It answers
  interface identity only.
- `color_science` section 5: **working space, LUTs and grading**. It is a UI
  palette in sRGB hex, not a colour pipeline.

A run that needs one of those treats it as unresolved, though the file exists.

## A gate that is not authored

It does not stop the studio. The ladder in [CLAUDE.md](../../CLAUDE.md) looks for
the constraint in past notes, and failing that the context stage asks the author.
What they state goes into the note and is recalled the next time.

A good moment to author a gate is when the same constraint keeps being asked for.
The studio is telling you what it keeps having to ask.

## tokens.json

The token dictionary the three authored gates were transcribed from. In
Creative-Headquarters it was embedded in a skill file as "ARTIFACT A" and had
never existed as a file.

**The author commits; an agent proposes.** A change is proposed as a diff, with
what it would break.

Several of its string values were broken across lines in the source, which JSON
does not allow. They were joined. No value was changed.

## Carried unchanged

The three gate files are byte for byte what Creative-Headquarters held on
2026-09-28. Their provenance sections therefore name paths from that repo:

| They say | Here |
|---|---|
| `skills/css_html_ui.skill.md` ARTIFACT A | `tokens.json`, in this folder |
| `tools/verify_system.py → check_palette_parity` | left behind. `studio/pipeline/tests/test_spec.py` checks that `tokens.json` and `color_science` section 2 agree |
| `control_room.html`, `hub/` | left behind, until the hub is rebuilt |
| `DECISIONS.md` § D9, § D10 | summarised in `studio/docs/IDEAS.md` |
| `tools/ui-ux-pro-max/` | `plugins/ui-design/catalog/` |
| `context/brand/README.md` | this file |
| `Router.md` | [CLAUDE.md](../../CLAUDE.md) |

Bringing those sections up to date is an edit to a gate, so it is the author's to
make.

One disagreement travels with them: the token dictionary's font policy says two
weights and no third, while the type scale and `typography_system` section 2 use
400, 500 and 800. Until the author settles it, 500 is for a status word only, as
section 2 says, and no other use of a third weight is in force. `spec.yaml`
records this under `known_conflicts`.
