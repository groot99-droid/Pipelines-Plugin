# brushes/library

The original brush files, kept as they were received, and the manifest that
says what each one is.

```
library/
  sources.json                             the manifest; authored, never written by a script
  user/<pack_id>/<file>.brushset|.brush    packs the author obtained, one copy of each file
  official/<pack_id>/<set_slug>.brushset   Procreate's older default sets, as downloaded
  official/fetch_log.jsonl                 what the fetch script downloaded, and its checksums
  bundled/<file name>                      optional: textures supplied by hand (ignored by git)
  user/<pack_id>/_docs/                    optional: a pack's documents (ignored by git)
```

`user/` is adopted: 72 brush files in 19 packs. `official/` is not there until
the fetch has run:

```
python -I brushes/pipeline/fetch_base_library.py fetch              # a dry run: prints the plan
python -I brushes/pipeline/fetch_base_library.py fetch --confirm    # 40 files, 174,197,966 bytes
python -I brushes/pipeline/fetch_base_library.py verify             # every file against its pinned size and MD5
```

## What is committed

The brush files are committed, through Git LFS: the `.gitattributes` file at
the repository root routes `brushes/library/**/*.brushset` and
`brushes/library/**/*.brush` through it.
One set is larger than the size a plain git blob may have on GitHub, so LFS is
not optional here.

- **Run `git lfs install` once in a clone before committing or pushing brush
  files.** It puts the `pre-push` hook in `.git/hooks/` that uploads the files
  themselves. Without it `git add` still stores pointers, but a push sends the
  pointers alone and GitHub refuses it. Afterwards `git lfs ls-files` lists
  what is tracked, and `git lfs push --dry-run origin <branch>` shows what a
  push would upload.
- A clone made without Git LFS holds a small pointer file in place of each
  brush file. Run `git lfs pull` to fetch the real ones. The scripts recognise a
  pointer and say so rather than failing on it.
- The repository ignores `*.zip`. A set that arrived as `Name.brushset.zip` is
  stored as `Name.brushset`; the bytes are the same.
- `official/fetch_log.jsonl` is committed as plain text, not through LFS.
- `user/<pack_id>/_docs/`, `bundled/` and `*.part` (an unfinished download) are
  never committed.

## sources.json

Schema `rosw-brushes-sources/1`, described in `../docs/CONTRACTS.md`.

- `packs`: the 19 packs under `user/`. Each has an id (a slug of at most 42
  characters), the vendor where the pack itself names one, the evidence for
  that, the patterns that recognise the pack's files in an unsorted folder, and
  the slug and title of each set.
- `official`: the download host and the 40 official set files, each pinned by
  size and MD5.

**Licences.** No pack in `user/` carries a licence file, so every entry says
`"redistribute": "unknown"` and `"licence_note": "none in pack; store terms
apply"`. The official sets are recorded the same way. That field is
information for a reader. It does not decide what is committed: the author
chose to keep the original files in the repository. Where a pack's vendor is
`null`, nothing in the pack names one.

## Rules

- Nothing here is edited. A brush file is replaced only by adopting or fetching
  it again.
- `user/` is written only by `python brushes/pipeline/ingest.py adopt <folder> --confirm`;
  `official/` only by `python brushes/pipeline/fetch_base_library.py fetch --confirm`.
  Without `--confirm` each prints what it would do and writes nothing.
- `fetch` opens a connection to one host, `download-assets.procreate.art`, and
  to no other, whatever a manifest says.
- Brush files are untrusted data. Every script opens them in memory, never
  extracts an entry by its name, and applies size limits.
