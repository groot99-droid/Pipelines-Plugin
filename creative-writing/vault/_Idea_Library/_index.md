# Idea Library

Ideas developed through `creative-writing/pipeline`'s checkpointed pipeline
(intake → reference pull → outline → draft → self-revision) but **not yet
integrated into the vault proper**. Each subfolder holds a complete
artifact trail (`idea.md`, `references.md`, `outline.md`, `draft.md`,
`draft_revised.md`, `revision_notes.md`) for one idea.

This is a staging area, not a finished-works folder — none of these carry
frontmatter, none are in `00_INDEX.md`, and none have companion
annotations. Promoting one to a real vault piece still means running the
pipeline's `vault_integration` stage (or the skill's stage 6) on it: file
under the right folder, frontmatter, `_index.md` entry, annotation,
reindex — the presence of a folder here is not equivalent to integration.

| Logged | Working title | Mode | Genre | Status |
|---|---|---|---|---|
| 2026-09-18 | [The Wordless Room](2026-09-18_the-wordless-room/draft_revised.md) | essay-self-help | personal-philosophy, self-help | self-revised, not integrated |
| 2026-09-18 | [The Nightly Inventory](2026-09-18_the-nightly-inventory/draft_revised.md) | horror-prose | horror | self-revised, not integrated |
| 2026-09-18 | [The Two Who Woke the Sea](2026-09-18_the-two-who-woke-the-sea/draft_revised.md) | epic-fantasy | high-fantasy | self-revised, not integrated |
| 2026-09-18 | [What I Kept From the Fire](2026-09-18_what-i-kept-from-the-fire/draft_revised.md) | confessional-poetry | confessional | self-revised, not integrated |
| 2026-09-18 | [The Fitting](2026-09-18_the-fitting/draft_revised.md) | horror-prose | body-horror | self-revised, not integrated |

## Notes from this batch

- Piece 2 and piece 5 both landed in horror-prose mode and both modeled
  their central technique on *The Stuffed Ones* (ellipsed alteration +
  willing complicity + cyclical ending) — a deliberate craft choice, not
  an asserted connection to that work; neither draft names or gestures at
  it.
- Piece 3's proper nouns and cosmology were verified against the
  Wyrmreach project's namespace during self-revision (empty
  `vault_search.py` results for all three character names; zero matches
  against the do-not-reuse vocabulary list) — see its `revision_notes.md`.
- Reference-pull for all five pieces routed through the
  `creative-writing-librarian-native` subagent, not `librarian.py`/Ollama.
