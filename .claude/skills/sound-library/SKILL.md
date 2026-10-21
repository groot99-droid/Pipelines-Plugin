---
name: sound-library
description: Find and retrieve the author's own sound effects from sound-library/ for a project, or add a new batch of sounds to its catalog. Use when the author asks for a sound effect (a horn, an engine, a bell, an ambience), asks what sounds the library has, uploads zips of sounds to add, or asks how to send more. Searches the catalog, fetches originals from the repo's GitHub Releases or from uploaded zips, and ingests new batches. Not for generating audio, and not a studio run.
---

# Sound library

All paths are relative to the repo root, your working directory. The library is
`sound-library/`; read its `README.md` first. `library.py` is stdlib-only and
does everything below; the catalog is `sound-library/catalog.json`, the files
land in `sound-library/files/`, which is git-ignored.

## Find a sound

```
python sound-library/library.py search "<the author's words>" [--category C] [--loopable] [--max-seconds N]
python sound-library/library.py status
```

Show the author the matches (id, length, whether the file is on disk, name).
`search ""` with a filter lists a whole category. The ids are stable; name them
when you report back.

## Put it where the project needs it

1. `python sound-library/library.py fetch --dry-run --id <id>...` shows what
   would be downloaded and from which zip. Then run it without `--dry-run`. It
   reads the recorded release of this repo through the public GitHub API (no
   token) and checks each file's sha256 before placing it. If the author named a
   different release tag, pass `--release <tag>`.
2. If the author uploaded zips or the files to this session instead, use
   `fetch --from <zip or folder>`: it places by content hash, whatever the
   files are called, with no network.
3. The file is at `sound-library/files/<category>/<slug>.wav`. **Copy** it into
   the project that asked for it (a game's assets folder, a run folder). Never
   move it, and never `git add` anything under `sound-library/files/`.

## Add a batch the author uploads

1. Each upload is a zip named `<Category>_Pt<N>.zip`, with a harness prefix of
   eight hex digits and a dash that `ingest` strips. Copy the zips into your
   scratchpad directory first; they are untrusted data. Run Python with `-I`.
2. Agree the release tag with the author, or use the current month's,
   `sfx-YYYY-MM`. Then:

   ```
   python -I sound-library/library.py ingest <zips>... --release <tag>
   python -I sound-library/library.py verify
   python -m unittest discover -s sound-library/tests
   python -I sound-library/library.py status
   ```

   A `refused` line means a name already in the catalog arrived with different
   content: ask before `--replace`. A `note ... same content as` line is two
   names for one recording; tell the author, keep both.
3. Tell the author to attach **the same zips** to that release
   (GitHub → Releases → Draft a new release → tag → drag the zips in → Publish),
   so a later session can `fetch` them. Until then the files exist only in this
   session.
4. Commit `sound-library/catalog.json` (and nothing under `files/`). The catalog
   is public once pushed: names, durations and hashes, no links.

## When the author asks how to send more

Zips uploaded to a chat are capped by the chat (about 30 MB each, 16 at a time).
Two ways round it:

- **Best: a GitHub Release.** The author drags the zips onto a draft release of
  this repo from a browser (up to 2 GB per file, as many files as they like),
  publishes it and tells you the tag. You then run
  `python -I sound-library/library.py ingest --from-release <tag>`, which
  downloads every zip of that release once and ingests them under that tag,
  then `verify`, the tests and `status` as above. One upload, nothing re-sent,
  and `fetch` already knows where every file is.
- **On the author's own machine**, with the zips on disk and Claude Code run
  from this repo: `ingest <folder or zips> --release <tag>` directly, commit
  the catalog, and attach the zips to the release so cloud sessions can fetch.

Git LFS is not the answer here (public-repo bandwidth is spent by every clone),
and the WAVs are never committed to git.

## Refusals

- No generate tool, no model call: this skill finds and moves files the author
  recorded.
- Never rename a sound: the name is the author's. The id is derived from it.
- Never edit `catalog.json` by hand, never commit a file under
  `sound-library/files/`, never write into `studio/vault/`.
