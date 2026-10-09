# Generations library

Everything the author has made on Higgsfield — images, videos, audio and 3D
models — catalogued in one place, with a page to look through it.

| What | Versioned | |
|---|---|---|
| `catalog.json` | yes | one entry per generation: id, type, model, date, prompt, a few settings, the ids of its inputs, the link to the original |
| `thumbs/<id>.webp` | yes | 320 px; images, videos, and 3D models made from an image in the catalog. Audio has none |
| `files/<type>/<id>.<ext>` | **no** | the originals, downloaded on request. A 3D model is ~70 MB; the whole library several GB |
| `index.html` | yes | the page |
| `library.py` | yes | `ingest`, `thumbs`, `fetch`, `status` |

## Look through it

```
python -m http.server 8770 --directory studio/library
```

then open `http://127.0.0.1:8770/`. Filter by type and model, search prompts,
open an item to see, play or turn it (3D through `<model-viewer>`, loaded from
jsdelivr only when a model is opened), its prompt and settings, what it was made
from and what was made from it. It plays the downloaded original when there is
one, and Higgsfield's copy otherwise.

## Bring it up to date

In a Claude Code session on this repo, ask to sync the Higgsfield library: the
`higgsfield-library-sync` skill pages the connector's history and runs:

```
python studio/library/library.py ingest <page.json>...   # merge pages into catalog.json
python studio/library/library.py thumbs                  # needs ffmpeg
python studio/library/library.py status
```

Keep originals on this machine:

```
python studio/library/library.py fetch --dry-run --type 3d
python studio/library/library.py fetch --type video --since 2026-09-01
python studio/library/library.py fetch --id <id>
```

Exit codes: 0 done, 1 some items failed, 2 usage error.

## What it keeps, and what it does not

- The catalog keeps the link to each original on Higgsfield's CDN, and the
  prompt. The repo is public, so both are public once pushed.
- It keeps the id of an uploaded input (a photo the author gave Higgsfield), never
  its link.
- It is not a studio run. It writes nothing into `studio/vault/` or
  `studio/assets/`, and spends no credits: it only reads the history.
- A generation deleted on Higgsfield stays in the catalog; its link stops
  working.

## Checking it

```
python -m unittest discover -s studio/library/tests
```
