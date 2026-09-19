---
name: chunk-tag-backfill
description: Runs (or re-runs) the creative-writing-chunk-tagger subagent over the vault's work files, writing/updating each one's creative-writing/vault/_ChunkTags/ sidecar. Use when backfilling per-chunk tags across the vault, or re-tagging specific files after an edit. Resumable and idempotent -- skips files whose sidecar is already valid unless --force is given.
---

# Chunk-tag backfill

Populates `creative-writing/vault/_ChunkTags/<path>.tags.json` sidecars so
`creative-writing/vault/tools/vault_search.py` can filter/rank by per-chunk `plot_tags`/
`context_tags`/`mood_tags`/`motif_tags` (see
`creative-writing/vault/_ChunkTags/vocabulary.yaml` for the closed vocabulary and
`.claude/agents/creative-writing-chunk-tagger.md` for how tagging
actually happens — this skill is the loop that drives it across many
files, not the tagging logic itself).

This must run as a skill, not a standalone script: tagging needs the
Agent tool to invoke the subagent, which only exists in a live Claude
Code session.

## Paths

Your working directory is the Pipelines repo root; the vault is at `creative-writing/vault/`.
`<path>` throughout this file means a **vault-relative** work path as
`vault_search.py` reports it (`03_Stories/06_Melting_Away.md`). Prefix it with
`creative-writing/vault/` whenever you Read or Write that path — the sidecar you write is at
`creative-writing/vault/_ChunkTags/<path>.tags.json`.

## Arguments

Parse from the skill's `args` (space-separated, any order):
- `--only <substring>` — limit to work files whose vault-relative path
  contains this substring (case-insensitive). Use this for the
  test-a-few-files-first step and for small supervised batches.
- `--force` — re-tag a file even if its sidecar already looks valid.
- `--dry-run` — report what would be (re)tagged; make zero subagent
  calls and write zero files.

With no arguments: process every work file that doesn't already have a
valid sidecar (the normal "continue the backfill" invocation).

## Procedure

1. **Enumerate work files:**
   ```
   python creative-writing/vault/tools/vault_search.py files --type work --json
   ```
   If `--only` was given, filter to paths containing
   that substring (case-insensitive).

2. **For each file, decide whether it needs (re)tagging:**
   - Run `python creative-writing/vault/tools/vault_search.py chunks "<path>" --json` to get its
     current `body_fingerprint`, `chunker_version`, and chunk list.
   - If `--force` was passed: needs tagging.
   - Else if no sidecar exists at `creative-writing/vault/_ChunkTags/<path>.tags.json`: needs
     tagging.
   - Else read the existing sidecar: if its `body_fingerprint` and
     `chunker_version` both match the fresh values from `chunks`, it's
     already valid — **skip it** (this is what makes reruns after an
     interrupted session resumable without redoing work). Otherwise it's
     stale — needs tagging.
   - In `--dry-run` mode: just report the decision (tag / skip / stale)
     for every file considered, then stop — no subagent calls, no writes.

3. **For each file that needs tagging** (skip this whole step in
   `--dry-run`): invoke the `creative-writing-chunk-tagger` subagent via
   the Agent tool, giving it the file's vault-relative path. Parse its
   per-chunk output blocks. For each block:
   - Cross-check the returned `chunk_index` + `content_fingerprint`
     against the `chunks` data you already fetched in step 2 — if they
     don't line up, something's wrong (the subagent may have miscounted
     or the file changed mid-run); don't write a sidecar entry you can't
     verify matches an actual current chunk.
   - Collect any `suggestions` lines separately (see step 5).
   - Assemble the sidecar JSON per the schema in
     `.claude/agents/creative-writing-chunk-tagger.md` (file, generated
     timestamp, `generator: "creative-writing-chunk-tagger v1"`,
     `chunker_version`, `body_fingerprint`, and the per-chunk records).
   - Write it to `creative-writing/vault/_ChunkTags/<path>.tags.json` (create parent dirs as
     needed — mirror the work's own folder structure the way
     `_Annotations/` does).

4. **Log the outcome** — append one line per file to
   `creative-writing/vault/_ChunkTags/_backfill_log.jsonl`: `{"file": ..., "timestamp": ...,
   "action": "tagged"|"retagged"|"skipped_valid", "chunk_count": ...}`.
   This is a cheap audit trail, not the source of resumability — the
   fingerprint check in step 2 is what actually makes reruns safe.

5. **Collect suggestions** — if any subagent output included a non-
   "(none)" `suggestions` line, append it to
   `creative-writing/vault/_ChunkTags/_vocabulary_suggestions.jsonl` (`file`, `chunk_index`,
   the raw suggestion text). Don't act on a suggestion yourself — that's
   the author's call, made by editing `vocabulary.yaml` directly.

6. **Report a summary** to the author at the end: files tagged,
   retagged, skipped (already valid), and how many suggestions were
   logged — plus a reminder that a fresh
   `python creative-writing/vault/tools/vault_search.py index` run is needed to pick up any new
   sidecars written this run (this skill does NOT rebuild the index
   itself, since that's a separate, cheap, explicit step the author may
   want to time deliberately, e.g. after reviewing a batch's tag quality
   rather than automatically after every file).

## Pacing note

Per the author's own approved plan: test on 2-3 files first (`--only` a
specific filename or two), hand-inspect the resulting sidecars for tag
quality and vocabulary fit, *then* proceed in supervised batches of
roughly 10 files at a time across the rest of the vault — not the full
~63 in one uninterrupted pass. Stop and let the author review between
batches rather than plowing through automatically.
