---
name: brush-designer
description: Runs the brush designer app for the author and helps them change or build a Procreate brush in it. Starts brushes/pipeline/app_server.py, proposes a validated settings patch the author pastes into the app, exports the result, and checks the exported file with brush_file.py inspect. Use when the author wants to open a library brush in the designer, tweak its settings, make a new brush, or export a .brush or .brushset. Not for finding a brush, which is brush-library. Nothing it writes is proven to open in Procreate until the iPad sittings in brushes/device-tests have been done.
---

# Brush designer

All paths are relative to the **Pipelines repo root**. The designer is the
browser app in `brushes/app/`, served by `brushes/pipeline/app_server.py`.
Python is the authority on every setting: the app's own checks are advisory.
Read `brushes/docs/CONTRACTS.md` F3 ("Patches", "Export") and F10 when in doubt.

**The honest caveat, say it every time a file is produced.** No file this tool
has written has been opened in Procreate. `brushes/spec.yaml` `device_test`
records every path (`container`, `edit_legacy`, `edit_modern`,
`scratch_m220`, `scratch_e4`, `thumbnail_policy`) as `untested`, until the
author does the iPad sittings in `brushes/device-tests/sitting-1` and
`sitting-2` (each has a `CHECKLIST.md`). Say "has not been opened in
Procreate". Never say a file will import, works, or is accepted.

## 1. Is the app there?

`brushes/pipeline/app_server.py` is part of the rebuild; check
`ls brushes/pipeline/app_server.py` and that `brushes/library/` holds brush
files (a clone without Git LFS holds pointers: `git lfs pull`). If the server
is missing, the app is not available yet: say so and use the headless path
in section 5, which needs no server.

## 2. Start it

```
python -I brushes/pipeline/app_server.py --no-browser
```
Run it in the background (it serves until stopped). Its first stdout line is
`Open http://localhost:8719/#t=<token>`. Give that URL to the author to open
(or navigate a Browser pane to it if the session has one). The token is made
per run and travels only in the URL fragment: do not write it to a file, a
note, a commit or any other tool. The port is fixed; a busy port is exit 2
and the server never picks another, so tell the author something already
holds 8719 (an earlier designer). Stop the background process when the
author is done; the app also has a quit route.

## 3. Find the brush, then open it

Find a brush with the `brush-library` skill and note its id (`b_` and 12 hex)
and name. In the app the **Library** tab searches the same catalog and opens a
brush from its original in the library (`GET /api/brush/<id>/open`); tell the
author the id to open. The app edits a copy: originals are never changed.

## 4. Propose a patch the author pastes

You do not drive the app. Claude's route into it is a **settings patch**,
validated here and pasted by the author into the app's patch box; there is
no inbox on the server.

1. Gather facts first, never from memory: the brush's current values
   (`python -I brushes/vault/tools/brush_search.py brush <id> --settings`),
   neighbours for realistic values (`similar <id> --other-sets`), and the
   rows of `brushes/schema/silica_keys.json` for the keys you will touch (type,
   `limits`, `enum`, `eras`, `preview`). Only keys the schema lists for the
   brush's own era exist; there is no free "add key". Observed limits are not
   rules: a value outside them is applied with an `outside_observed` warning.
2. Build the envelope, sending only the keys that change:
   ```json
   {"schema": "rosw-brushes-patch/1", "base_id": "b_72dacfda3c12",
    "summary": "Tighter spacing, larger minimum size",
    "changes": {"plotSpacing": 0.02, "minSize": 0.1}}
   ```
   `base_id` is the library brush id (or `null` for a new brush). Values:
   a number for a real or int key, `true`/`false` for a bool, the enum
   number for a select. Do not send curves unless asked, and then check the
   shape with the validator. Never send `color` (read-only in v1).
3. **Validate before you hand it over.** With the MCP tool
   `validate_settings_patch` (`changes`, `base_id`), when `tools/list` offers
   it (the server is a stub today), you get the PatchReport and a
   `patch_text` to paste. Otherwise validate through the export dry run,
   which applies the same rules and writes nothing:
   ```
   python -I brushes/pipeline/brush_file.py export --from <brush id> --change plotSpacing=0.02 --change minSize=0.1
   ```
   It lists each key `applied` or `rejected` with a code (`unknown_key`,
   `wrong_type`, `not_in_enum`, `non_finite`, `read_only`, `not_in_era`,
   `curve_invalid`, `out_of_range`), plus warnings. Exit 1 means nothing was
   applied. Fix and repeat until nothing is rejected; tell the author about
   every `clamped` and `outside_observed` result.
4. Give the author the envelope as one JSON block, with `summary` saying
   what it does in plain words and the list of changed keys with before and
   after. They paste it into the app's patch box, review the diff there and
   apply it. The app re-validates; if it disagrees, Python's answer wins.

## 5. Export, then inspect

In the app, the Export menu returns a `.brush`, `.brushset` or `.gbr` to the
browser, which saves it as a download; the server writes nothing. The
headless route, for a library brush plus changes:

```
python -I brushes/pipeline/brush_file.py export --from <id|file> [--brush SEL] [--set NAME] [--change K=V ...] --out <DIR>
python -I brushes/pipeline/brush_file.py export --from <id|file> [...] --out <DIR> --confirm
```
The first line is a dry run: it lists every member as `verbatim`,
`re-encoded`, `replaced` or `dropped`. A `dropped` nobody asked for is an
error. Show it to the author, agree the `--out` folder with them (it is
refused inside `brushes/`, the library, the catalog or the vault; their
Downloads folder or the scratchpad will do), then run it with `--confirm`.
`--change K=V` reads V as JSON, else as text (`--change "name=My Pen"` renames).
`--set NAME` wraps the brush in a `.brushset`. Only `Brush.archive` is
re-encoded; shape, grain and thumbnail stay original bytes, so the
thumbnail is stale after an edit (`stale_thumbnail` warning): say so.
`archive canonical` means written by the rules that reproduce Procreate's own
files; `valid` means well-formed but not known to match them. Neither is
tested on a device.

Then check the file you made:
```
python -I brushes/pipeline/brush_file.py inspect <exported file>
python -I brushes/pipeline/brush_file.py roundtrip <exported file>
```
`inspect` prints the era, fidelity, texture sources, members and warnings;
check the name, era and member list are what you meant. `roundtrip` exits 1
on any difference when the file is decoded, re-encoded and rebuilt. Both
prove only that **this tool reads its own file back**, nothing about Procreate.

## Report to the author

Name the file and folder, its size and sha256 (from the export output), what
changed (keys, before and after), every warning, and the caveat: it has not
been opened in Procreate. If they want to know whether it opens, the answer
is the device sitting, and its `returned/` folder is where the result is kept.

## Never

Write into `brushes/library/`, `brushes/catalog/` or `brushes/vault/`; use
`--confirm` before the author has seen the dry run; put an export inside
`brushes/`; run `device_tests.py build --confirm` unasked (it writes the
sittings); describe a bundled shape or grain (a file name only) as if seen;
or claim a brush made here is better, equivalent or compatible with anything.
