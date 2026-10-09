---
name: higgsfield-library-sync
description: Import the author's Higgsfield generations (images, videos, audio, 3D models) into the studio's generations library at studio/library/, or bring it up to date. Pages the connector's generation history, merges it into catalog.json, makes thumbnails, and on request downloads originals into the git-ignored files/ folder. Use when the author asks to import, sync, refresh or download their Higgsfield generations or library. Not a studio run, and not for making anything new.
---

# Higgsfield library sync

All paths are relative to the repo root, your working directory. The library is
`studio/library/`; read its `README.md` first.

The connector exists only in this session, so you page the history and
`studio/library/library.py` does the rest. It never calls the connector.

## 1. Page the history

Call `mcp__Higgsfield__show_generations` with `size: 100` (no `type`, default
`only_completed`). Each page is `{"items": [...], "next_cursor": ...}`.

- A large page is saved to a file by the harness and the error names the path:
  use that path. A page returned inline: write it, unchanged, to a file in your
  scratchpad directory (never into the repo — a page holds links to the
  author's uploads).
- After each page run
  `python studio/library/library.py ingest <that page's file>`. It prints
  `N new`.
- **Stop** when `next_cursor` is null, or when a page adds `0 new` (for a sync;
  for a first import, page to the end). Otherwise pass `next_cursor` as
  `cursor` and continue.

This browses only; it never spends credits. Do not call any generate tool.

## 2. Thumbnails

`python studio/library/library.py thumbs` makes `thumbs/<id>.webp` for what is
new. It needs ffmpeg on PATH. A failure names the item; report it and go on.

## 3. Originals, only if asked

Originals are large (a 3D model is ~70 MB). Run
`python studio/library/library.py fetch --dry-run` with the author's filters
(`--type`, `--since`, `--id`, `--limit`) and show the count before downloading
anything; then run it without `--dry-run`. They land in `studio/library/files/`,
which is not versioned. Never add them to git.

## 4. Report and check

`python studio/library/library.py status`, then
`python -m unittest discover -s studio/library/tests`. Tell the author how many
items are new by type, and that the page is at
`python -m http.server 8770 --directory studio/library` → `http://127.0.0.1:8770/`.

`catalog.json` and `thumbs/` are versioned, and the repo is public: the prompts
and the links to the originals become public when pushed. Committing and pushing
are the author's call.
