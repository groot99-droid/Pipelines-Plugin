# brushes

A library of Procreate brushes with tag-based search, and a brush designer that
reads and writes the brush file format.

**This tool is under construction.** What exists today is the foundation, the
file codec, the library and its search: the contract, the identity and path
modules, the codec that reads and writes brush files byte for byte, the scripts
that fill the library and build the catalog, previews and notes, the search and
tag tools, the MCP server and the loopback app server, the builder of the first
two device tests, and the test fixtures. The designer app in `app/` opens, edits and
exports brushes; its stroke engine is not built. Nothing here has written a file that
Procreate is known to open.

## What is here now

| Path | State |
|---|---|
| `spec.yaml` | the declared contract; `build.exists` lists what is on disk |
| `docs/CONTRACTS.md` | the same contract in prose, with the exact shapes every module is written to |
| `pipeline/identity.py` | how a brush, a texture and a brushset are named |
| `pipeline/brush_common.py` | where the data lives, the exit codes, safe file writes |
| `pipeline/zip_writer.py` | the one zip writer: it writes a container in the three forms Procreate's own files carry |
| `pipeline/bplist.py` | binary property lists, read and written byte for byte; the codec's error classes |
| `pipeline/keyed_archive.py` | the archive graph inside `Brush.archive`: decode, re-encode with either of the two profiles, renumber |
| `pipeline/brush_model.py` | a brush as settings: eras, JSON forms, patches, new brushes from a pinned donor, the census |
| `pipeline/container.py` | the one reader of `.brush` and `.brushset` files, under the caps; writes them back through `zip_writer.py` |
| `pipeline/png_io.py` | PNG read and write in the standard library (PIL only makes it faster) |
| `pipeline/gbr.py` | the GIMP `.gbr` brush, read and write |
| `pipeline/brush_file.py` | `inspect`, `export` and `roundtrip` of one brush file or a folder of them. `export` writes only with `--confirm` and `--out` |
| `pipeline/fetch_base_library.py` | `list`, `fetch` and `verify` for the 40 official sets. `fetch` downloads only with `--confirm`, and only from the one host |
| `pipeline/ingest.py` | `where`; `adopt`, which copies a folder of brush files into `library/user/`; `census`, which counts what the library's archives hold and writes nothing; `build`, which reads every brush file and writes `catalog/` (deterministic, nothing to confirm); and `report`, which prints what the catalog holds |
| `pipeline/previews.py` | `render`, which makes the stroke, shape and grain previews and the contact sheets, and writes `vault/_Previews/`, `catalog/thumbnails.json` and the texture statistics (a dry run without `--confirm`) |
| `pipeline/notes.py` | `write`, which renders one note per brushset, the folder indexes and `00_INDEX.md` from `catalog/` (a dry run without `--confirm`; only the generated part of a note is rewritten), and `check`, which exits 1 when any note differs from the catalog |
| `pipeline/mcp_server.py` | the MCP server over stdio: nine read-only tools (search, similar, get_brush, get_set, list_sets, facets, get_preview, vocabulary and `library_status`), and `export_brush` only when started with `--export-dir`. Registered in the repository's `.mcp.json` |
| `pipeline/service.py` | `BrushService`, the one layer both servers call: search, brush and set records, previews, patch validation, and the export builder |
| `pipeline/app_server.py` | the loopback HTTP server (127.0.0.1:8719, a token per run) that serves `app/` and the JSON API; it writes nothing |
| `pipeline/device_tests.py` | `build` and `verify` for the two sittings with the iPad: sitting 1, a control set of eight library brushes in a container of ours; sitting 2, brushes we edited and brushes we made from nothing |
| `pipeline/tests/` | the tests, and `fixtures.py`, which builds synthetic brush files for them |
| `schema/silica_keys.json` | every archive key once: its type, eras, defaults, observed values, and the inferred labels (F4) |
| `schema/patch_cases.json` | the settings-patch cases Python and the app both run |
| `library/sources.json` | which packs the library holds and where the 40 official sets come from |
| `library/user/` | the author's 19 packs, adopted: 72 brush files |
| `library/official/` | the 40 official sets, fetched by `fetch_base_library.py fetch --confirm` (below) |
| `device-tests/` | one folder per sitting, written by `device_tests.py build --confirm` |
| `app/` | the designer and a library browser: plain ES modules in `js/`, no build step, served by `app_server.py`. It opens a brush from the library or from a file, edits it as a patch of changed keys, and exports through the server, which owns the encoding. `selftest.html` runs its checks in the browser. The stroke preview is a placeholder until the engine lands |

## What is planned

```
brushes/
  spec.yaml, docs/CONTRACTS.md   the contract
  schema/                        every archive key, once; the facet rules
  pipeline/                      the file codec, ingest, previews, notes, the MCP
                                 server and the app server; standard library only
  catalog/                       generated: one JSON record per brush and per set
  vault/                         an Obsidian vault: one note per brushset, tags,
                                 previews, and the search tool
  app/                           the designer and a library browser; no build step
  library/                       the original brush files (Git LFS) and their manifest
```

The contract for all of it is frozen in `docs/CONTRACTS.md`. Read that before
writing a module, and `spec.yaml` before changing a constant: a change is made
in code first, then declared there, and the tests fail when the two disagree.

## Rules that already hold

- Runtime code uses the Python standard library only and runs on Python 3.10.
- A command that writes is a dry run unless it is given `--confirm`.
- A brush file is untrusted data: it is opened in memory, never extracted by
  entry name, and read only by `python -I`.
- The original brush files are committed through Git LFS. Run `git lfs install`
  once in a clone before committing or pushing brush files: without it a push
  sends pointers and not the files, and is refused. A clone made without Git
  LFS holds small pointer files in `library/`; run `git lfs pull` to get the
  brushes. No test needs them.
- What the drawing app accepts is recorded in `spec.yaml` under `device_test`,
  one answer per kind of file. Every answer is `untested` today.

## Filling the library, and the device tests

```
python -I brushes/pipeline/fetch_base_library.py list
python -I brushes/pipeline/fetch_base_library.py fetch              # a dry run: prints the plan
python -I brushes/pipeline/fetch_base_library.py fetch --confirm    # downloads 40 files, 174 MB
python -I brushes/pipeline/fetch_base_library.py verify
python -I brushes/pipeline/device_tests.py build sitting-1 --confirm
python -I brushes/pipeline/device_tests.py verify sitting-1
python -I brushes/pipeline/device_tests.py build sitting-2 --confirm
python -I brushes/pipeline/device_tests.py verify sitting-2
```

The official sets are not on disk until `fetch --confirm` has run. Five of the
eight brushes of the control set come from them, so until then
`device_tests.py build` refuses (exit 1, nothing written): a set with stand-ins
is not the control set, and there are only two sittings with the iPad.
`--allow-substitutes` builds one anyway and marks it as what it is.

## Checking it

```
python -m unittest discover -s brushes/pipeline/tests
```

The tests build their data in temporary folders. They never read the real
library, and they need neither the network nor Git LFS content.

Tests that need the real library are opt-in, and run under an isolated
interpreter. With the round trip of every library file, they make gate G1
(`docs/CONTRACTS.md`, "Test fixtures"):

```
ROSW_BRUSHES_CORPUS=brushes/library python -I -m unittest discover -s brushes/pipeline/tests -k RealLibrary -k Corpus
python -I brushes/pipeline/brush_file.py roundtrip brushes/library
```
