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
| 2026-09-18 | [[_Idea_Library/2026-09-18_the-wordless-room/draft_revised\|The Wordless Room]] | essay-self-help | personal-philosophy, self-help | self-revised, not integrated |
| 2026-09-18 | [[_Idea_Library/2026-09-18_the-nightly-inventory/draft_revised\|The Nightly Inventory]] | horror-prose | horror | self-revised, not integrated |
| 2026-09-18 | [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/draft_revised\|The Two Who Woke the Sea]] | epic-fantasy | high-fantasy | self-revised, not integrated |
| 2026-09-18 | [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/draft_revised\|What I Kept From the Fire]] | confessional-poetry | confessional | self-revised, not integrated |
| 2026-09-18 | [[_Idea_Library/2026-09-18_the-fitting/draft_revised\|The Fitting]] | horror-prose | body-horror | self-revised, not integrated |

## Artifact trails

Each idea's full checkpoint trail, in the order the pipeline produced it.

### The Wordless Room  <sub>essay-self-help</sub>

[[_Idea_Library/2026-09-18_the-wordless-room/idea|idea]] → [[_Idea_Library/2026-09-18_the-wordless-room/references|references]] → [[_Idea_Library/2026-09-18_the-wordless-room/outline|outline]] → [[_Idea_Library/2026-09-18_the-wordless-room/draft|draft]] → [[_Idea_Library/2026-09-18_the-wordless-room/draft_revised|revised draft]] → [[_Idea_Library/2026-09-18_the-wordless-room/revision_notes|revision notes]]

### The Nightly Inventory  <sub>horror-prose</sub>

[[_Idea_Library/2026-09-18_the-nightly-inventory/idea|idea]] → [[_Idea_Library/2026-09-18_the-nightly-inventory/references|references]] → [[_Idea_Library/2026-09-18_the-nightly-inventory/outline|outline]] → [[_Idea_Library/2026-09-18_the-nightly-inventory/draft|draft]] → [[_Idea_Library/2026-09-18_the-nightly-inventory/draft_revised|revised draft]] → [[_Idea_Library/2026-09-18_the-nightly-inventory/revision_notes|revision notes]]

### The Two Who Woke the Sea  <sub>epic-fantasy</sub>

[[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/idea|idea]] → [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/references|references]] → [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/outline|outline]] → [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/draft|draft]] → [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/draft_revised|revised draft]] → [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/revision_notes|revision notes]]

### What I Kept From the Fire  <sub>confessional-poetry</sub>

[[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/idea|idea]] → [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/references|references]] → [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/outline|outline]] → [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/draft|draft]] → [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/draft_revised|revised draft]] → [[_Idea_Library/2026-09-18_what-i-kept-from-the-fire/revision_notes|revision notes]]

### The Fitting  <sub>horror-prose</sub>

[[_Idea_Library/2026-09-18_the-fitting/idea|idea]] → [[_Idea_Library/2026-09-18_the-fitting/references|references]] → [[_Idea_Library/2026-09-18_the-fitting/outline|outline]] → [[_Idea_Library/2026-09-18_the-fitting/draft|draft]] → [[_Idea_Library/2026-09-18_the-fitting/draft_revised|revised draft]] → [[_Idea_Library/2026-09-18_the-fitting/revision_notes|revision notes]]

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

## Related

- [[_Pipelines/creative-writing|The creative-writing pipeline]] — what produced these.
- [[_Pipelines/_index|Pipelines index]]
- [[00_INDEX.md|The Living Archive — Index]] — where a promoted piece ends up.
- [[CLAUDE.md]] — the rules an integration has to satisfy.
