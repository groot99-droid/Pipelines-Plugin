---
title: "Craft notes"
type: craft-index
folder: _Craft
provenance: "Analysis of the vault's works, written with Claude. Not the author's prose."
tags: [craft-note, index]
---

# Craft notes

Cross-cutting analysis of the works: what the vault does structurally, what it does not yet do, and the rules that follow. The [[_Annotations/03_Stories/07_Project_-_Man_Eater|annotations]] describe one work each; these notes describe patterns that run across several, and they carry the reasoning behind the pipeline's **plot logic** and **registers**.

**These are not the author's writing.** They are analysis, written with Claude, and marked `provenance` in each note's frontmatter. `vault_search.py` indexes them as `[craft]`, separate from `[work]` and `[annotation]`, so a search result says what it is. Treat them as guidance and evidence, never as text to quote as the author's voice.

## Notes

- [[_Craft/plot-logic|Plot logic (but / therefore)]]: the rule, the causal ledger, and worked ledgers of the vault's own pieces.
- [[_Craft/liminality|Liminality]]: thresholds, the clock-keyed door, the frame slip. Register `liminal`.
- [[_Craft/psychedelia|Psychedelia]]: the Trip Tracker's phases read as a causal chain; perception as landscape; the ethical rule. Register `psychedelic`.
- [[_Craft/cosmic-horror|Cosmic (Lovecraftian) design]]: the ladder of knowledge, and what the Testament of Lira Calyx already does. Register `cosmic`.

## How these are kept honest

Every ledger in these notes carries an `Expect:` line, and `creative-writing/pipeline/tests/test_craft_notes.py` runs the checker over each one and fails if the verdict differs. The same test checks every quotation of three or more words against the vault's own files and fails on a quotation that is not there. Quotation is verbatim from the works, with typography (curly quotes, dashes, spacing) ignored.

Line numbers, where a note gives them, are file lines as an editor shows them, not the body-relative ranges `vault_search.py` reports. Most citations here are by quotation instead.

## Related

- [[CLAUDE.md]]: section "Plot logic" holds the rules these notes explain.
- [[_Pipelines/creative-writing|The creative-writing pipeline]]
- [[_ChunkTags/vocabulary.yaml|Chunk-tag vocabulary]]: the register tags added alongside these notes.
