# brushes

A library of Procreate brushes with tag-based search, and a brush designer that
reads and writes the brush file format.

**This tool is under construction.** What exists today is the foundation: the
contract, the identity and path modules, the zip writer, the two scripts that
fill the library, a stub of the MCP server, the builder of the first device
test, the test fixtures, the library manifest, and the old designer copied in
as it was received. There is no search, no catalog and no working export yet,
and nothing here has written a file that Procreate is known to open.

## What is here now

| Path | State |
|---|---|
| `spec.yaml` | the declared contract; `build.exists` lists what is on disk |
| `docs/CONTRACTS.md` | the same contract in prose, with the exact shapes every module is written to |
| `pipeline/identity.py` | how a brush, a texture and a brushset are named |
| `pipeline/brush_common.py` | where the data lives, the exit codes, safe file writes |
| `pipeline/zip_writer.py` | the one zip writer: it writes a container with the header values Procreate's own files carry |
| `pipeline/fetch_base_library.py` | `list`, `fetch` and `verify` for the 40 official sets. `fetch` downloads only with `--confirm`, and only from the one host |
| `pipeline/ingest.py` | `where`, and `adopt`, which copies a folder of brush files into `library/user/`. The catalog verbs (`build`, `report`, `census`) are not built yet |
| `pipeline/mcp_server.py` | a stub of the MCP server: the protocol and one tool, `library_status`. Registered in the repository's `.mcp.json` |
| `pipeline/device_tests.py` | `build` and `verify` for the first sitting with the iPad: a control set of eight library brushes in a container of ours |
| `pipeline/tests/` | the tests, and `fixtures.py`, which builds synthetic brush files for them |
| `library/sources.json` | which packs the library holds and where the 40 official sets come from |
| `library/user/` | the author's 19 packs, adopted: 72 brush files |
| `library/official/` | not there until the official sets are fetched (below) |
| `device-tests/` | one folder per sitting, written by `device_tests.py build --confirm` |
| `app/` | the earlier designer, unchanged, byte for byte as it was received (nine of its files have CRLF line endings, and `.gitattributes` keeps them so). It cannot import a brush file, and what it exports is not in the real brush format |

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

## Filling the library, and the first device test

```
python -I brushes/pipeline/fetch_base_library.py list
python -I brushes/pipeline/fetch_base_library.py fetch              # a dry run: prints the plan
python -I brushes/pipeline/fetch_base_library.py fetch --confirm    # downloads 40 files, 174 MB
python -I brushes/pipeline/fetch_base_library.py verify
python -I brushes/pipeline/device_tests.py build sitting-1 --confirm
python -I brushes/pipeline/device_tests.py verify sitting-1
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
