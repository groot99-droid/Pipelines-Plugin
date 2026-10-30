---
name: brush-tag-backfill
description: Runs (or re-runs) the brush-tagger subagent over the brush library, one contact-sheet batch at a time, and has brushes/vault/tools/brush_tags.py validate each reply and write the brushes/vault/_BrushTags/ sidecars. Use when backfilling tags and visual descriptions across the brush vault, or re-tagging one set after its brushes or the vocabulary changed. Supervised, resumable and idempotent -- a brush whose sidecar entry matches its content hash is skipped unless --force is given. Nothing is written until the author has approved the first batch.
---

# Brush-tag backfill

Fills `brushes/vault/_BrushTags/<note>.tags.json` so `brush_search.py` can
filter and rank by `medium`, `mark`, `texture`, `edge`, `motif` and `use`.
How a brush is tagged is in `.claude/agents/brush-tagger.md`; the closed
vocabulary is `brushes/vault/_BrushTags/vocabulary.yaml`; the block grammar
is `brushes/docs/CONTRACTS.md` F8. This skill is only the loop. It must run
as a skill: tagging needs the Agent tool, and the tagger looks at images.

## Paths and the one rule

Your working directory is the Pipelines repo root; the vault is
`brushes/vault/`. A `<note>` is a vault-relative note path
(`02_Vendor_Packs/everything-watercolour.md`) or a set slug.
**You never write a sidecar or a log yourself**, with Write, Edit or a shell
redirect. `brush_tags.py apply --confirm` is the only writer of
`_BrushTags/*.tags.json` and the two `.jsonl` logs. The tagger's reply goes
to a scratch file in the session scratchpad directory, never into the repo.

## Arguments

Parse from `args` (space-separated, any order):
- `--only <substring>` -- notes whose path contains it (`brush_tags.py plan --only`).
- `--force` -- re-tag brushes whose entry is current (`plan --force`).
- `--dry-run` -- print the plan; make zero tagger calls and write nothing.
- `--limit <n>` -- at most n tagger calls this run (`plan --limit`).

No arguments means the pilot, below, not the whole library.

## Procedure

1. **Plan.**
   ```
   python -I brushes/vault/tools/brush_tags.py plan --json [--only S] [--force] [--limit N]
   ```
   Each `calls[]` entry is one tagger call: `file` (the note), `set`,
   `sheets` (at most two contact sheets of 8 brushes each, under
   `brushes/vault/_Previews/_sheets/<set>/`), `ids`, `decisions`
   (`tag`, `retag`, `force`) and `chunks` (chunk number, lines, fp per id).
   Skipped brushes (a current entry exists anywhere) are not listed, which
   is what makes a rerun resumable. If it exits 1 with `missing_sheets`, or
   lists `blocked` notes, **stop**: tell the author to run
   `python -I brushes/pipeline/previews.py render --sheets-only --confirm`
   or `notes.py write --confirm`. Never tag blind (`--allow-no-sheets` only
   lists). In `--dry-run`, print the counts and calls and stop.

2. **Dispatch one tagger per call** via the Agent tool (`brush-tagger`).
   Give it only the facts it needs, so it cannot be biased:
   ```
   note: <file>
   sheets: <sheet-01.png, sheet-02.png>
   ids: <id1,id2,...>
   ```
   No set title, no earlier tags, no hints. Calls of different notes may run
   side by side (at most three); never two at once for one note.

3. **Parse and dry-run it.** Write the reply, byte for byte, to a scratch
   file, then:
   ```
   python -I brushes/vault/tools/brush_tags.py apply --file "<note>" --ids <ids> --from <scratch file>
   ```
   No `--confirm`: it prints `blocks, accepted, rejected, missing,
   suggestions`, each `REJECTED <id>: <reason>` and ends
   `DRY RUN   nothing is written without --confirm.` It rejects a block whose
   id is not in the note or `--ids`, whose `fp` differs from the catalog, with
   a tag outside the vocabulary, over a cap (medium 2, mark 2, texture 3,
   edge 2, motif 2, use 3), or with an empty `visual` while evidence is not
   `none`. Exit 1 means at least one block was rejected or is missing, even
   if the others are fine. Never repair a block by hand.

4. **Pilot, then approval.** The first batch is 2 or 3 calls of different
   kinds, one `plan --only S --limit 1` each: for example
   `everything-watercolour`, `autumn-stamps` (a stamp set) and `p5-inking`
   (whose second sheet holds brushes with no thumbnail). Show the author, per
   brush, the tags, `visual`, `evidence` and `notes` beside its sheet row
   (Read the sheet PNG so they can compare), and every suggestion.
   **Do not run `--confirm` until the author has said the pilot is good.**
   Fix systematic problems in the agent file or vocabulary only if the
   author asks; re-run the pilot after any such edit.

5. **Write.** After approval, per call:
   ```
   python -I brushes/vault/tools/brush_tags.py apply --file "<note>" --ids <ids> --from <scratch file> --confirm
   ```
   Accepted blocks are merged into the note's sidecar even when others in the
   reply were rejected, and both logs are appended. Re-invoke the tagger
   **once** for the rejected or missing ids (same inputs, with the rejection
   reason in one added line); if they fail again, leave them and report them.
   Apply one call at a time: calls on one note share a sidecar.

6. **After each batch:**
   ```
   python -I brushes/vault/tools/brush_tags.py check
   python -I brushes/vault/tools/brush_search.py index
   python -I brushes/vault/tools/brush_search.py index --check
   ```
   `check` exit 1 means a sidecar is malformed: stop. Warnings (stale entry,
   orphan, another vocabulary) are reported, not hidden. The index is an
   ignored cache, so rebuilding it is not a vault write; a stale index would
   serve tagged brushes as untagged.

7. **Report**: brushes tagged, re-tagged, rejected, missing; what is left
   (`plan` counts); `python -I brushes/vault/tools/brush_tags.py suggestions`.
   Never act on a suggestion: adopting one is the author editing
   `vocabulary.yaml`, after which `plan --force --only <note>` re-tags.

## Batching for the whole library

Today `plan` reports 990 brushes in 93 calls (up to 16 brushes per call,
fewer for the last sheet of a set). After the pilot, work in batches of about
10 calls (roughly 100 to 130 brushes, at most three taggers at a time) and
stop for the author's review between batches. Do not run the library in one
unattended pass. Rerunning `plan` after any interruption is the resume: only
what has no current entry comes back.

**Stale handling.** An entry is stale when the brush's `content_sha256`
changed (the catalog was rebuilt from changed originals). `plan` lists it as
`retag`, `check` warns, and re-tagging replaces the entry. A reply whose `fp`
no longer matches means the catalog moved under you: stop, rebuild the notes
and the index, and re-plan. A vocabulary change leaves entries current but
`check` warns "written under another vocabulary": re-tag with `--force`
only what the author names.

## Stop conditions

Stop and report, without another call, when: the tool exits 2; sheets or
notes are missing; a tagger call has more than two rejected blocks, or the
same rejection reason appears in two calls (a vocabulary or format
problem, not noise); `check` exits 1; the index and catalog disagree
(`fp` mismatch); the same suggestion appears for five or more brushes (the
author may want to adopt it); the author's review of a batch finds
systematic errors; or the author says stop.
