# brushes: the contracts

This document fixes the interfaces the parts of `brushes/` share: how a brush is
named, where data lives, what the file codec returns, what the catalog, the
previews, the notes and the tag sidecars look like, what the search tool, the
two servers and the command lines accept and return, and which script may write
which file.

`brushes/spec.yaml` declares the same contract as data, and
`brushes/pipeline/tests/test_spec_agreement.py` fails when the code, that file
and this one disagree. This document carries the shapes that do not fit a YAML
value. Paths are relative to `brushes/` unless they start with `repo:`.

**Status.** The tool is under construction. A section below describes what a
module must do when it exists; `spec.yaml` `build.exists` lists what exists.
Nothing here has yet written a file that the drawing app is known to open
(`spec.yaml` `device_test`).

Sections F1 to F12 are frozen: a module is written to them, and a change to one
is made here and in `spec.yaml` first.

## 0. Rules for every module

| Rule | Detail |
|---|---|
| Language | Python 3.10 syntax and standard library. No `match`, no `tomllib`, no `typing.Self`, no `datetime.UTC`, no `ExceptionGroup`. A module that writes `X \| Y` annotations starts with `from __future__ import annotations`. |
| Dependencies | `pipeline/` and `vault/tools/` import the standard library and their own siblings, nothing else. `PIL` may be used as a faster image decoder inside a `try` in `png_io.py` and `previews.py`; every result must be identical without it. Tests use `unittest` and may import `yaml`. |
| Network | Only `pipeline/fetch_base_library.py` opens a connection: HTTPS, host `download-assets.procreate.art`, nothing else, redirects to another host refused. The host is the script's own constant (`ALLOWED_HOSTS`), not whatever a manifest names: `fetch` on a manifest that names another host is exit 2, and no opener is built for it. |
| Text | Every `open()`, `read_text()` and `write_text()` names `encoding="utf-8"`. Text is written with `newline="\n"`. |
| Console | `main()` calls `brush_common.open_console()` (vault tools reconfigure both streams themselves) before printing. |
| Entry point | A script defines `main(argv=None) -> int` and ends with `raise SystemExit(main())`. It resolves every path from `__file__` and starts with `sys.path.insert(0, <its own folder>)`, so `python -I path/to/script.py` works from any directory. The command is `python`, never `python3`. |
| Exit codes | `0` ok (also an empty result and a clean dry run), `1` refused or failed, `2` usage or environment (a bad argument, a missing folder, a missing index, a busy port). |
| Writers | A command that writes into `library/`, `catalog/` (previews only), `vault/` or an export folder is a dry run unless `--confirm` is given, and ends a dry run with the line `DRY RUN   nothing is written without --confirm.` The two exceptions are `ingest.py build` and `brush_search.py index`, whose output is generated and rebuildable. |
| Atomic writes | Files are written through `<name>.tmp` and `os.replace` (`brush_common.write_text`, `write_bytes`, `write_json`). |
| Determinism | Committed generated data holds no timestamp and no absolute path. Two builds of the same input, in any directory order, are the same bytes. Sort every directory listing. Generated JSON is spelled by `brush_common.json_text`. |
| Untrusted input | A brush file is data from a stranger. Open a zip in memory, never extract by entry name, apply the caps in F3, and run any Python that reads one with `python -I`. The two servers are not exempt: they open library originals, so their registrations pass `-I` (F10). |
| Tests | `python -m unittest discover -s brushes/pipeline/tests`. Tests build synthetic data in temporary folders with `pipeline/tests/fixtures.py`; none reads the real library, catalog or vault, the network, or a file tracked through Git LFS. |

**Fixed words.** One spelling each, everywhere (catalog, notes, index, wire):

| Word | Values | Means |
|---|---|---|
| `library` | `user`, `official` | which half of `library/` a container came from |
| `pack_kind` | `vendor`, `official`, `mine` | the kind of pack in `library/sources.json` |
| `source_type` | `brush`, `set`, `index`, `moc`, `guide` | the kind of chunk a search result is |
| `family` | `legacy`, `modern` | the two generations of archive |
| `stroke_source` | `thumbnail`, `reset-thumbnail`, `none`, `rendered-approx` | where a stroke preview came from |
| `shape_source` | `embedded`, `bundled`, `bundled-supplied`, `none` | where the shape image is |
| `grain_source` | the same, plus `blank` | `blank` is the bundled name `Brush-Preset-Blank.png` |
| `visual_basis` | `described-not-measured` | a tagger's sentence is a description of a preview |
| preview kinds | `stroke`, `shape`, `grain` | the only preview kinds |

There is no bare `source` field anywhere. The handle of a brushset is its
`set_slug`; `set_id` is a field, never a lookup key.

## F1. Identity

Module: `pipeline/identity.py`. No other module computes an id.

```
part(x)        = b"\x00" if x is None else b"\x01" + len(x).to_bytes(8, "big") + x
content_sha256 = sha256(b"rosw-brush-v1\x00" + part(archive) + part(shape) + part(grain)
                 + for each SubNN ascending: b"\x02" + part(a) + part(s) + part(g)).hexdigest()
brush_id       = "b_" + content_sha256[:12]                       ^b_[0-9a-f]{12}$
texture_id     = "t_" + sha256(png_bytes).hexdigest()[:12]        ^t_[0-9a-f]{12}$
set_id         = "s_" + sha256(b"rosw-set-v1\x00" + name_utf8 + b"\x00"
                 + "\n".join(brush_ids).encode()).hexdigest()[:12]   ^s_[0-9a-f]{12}$
set_slug       = ^[a-z0-9][a-z0-9-]{0,47}$
```

- `archive` is the `Brush.archive` bytes.
- `shape` and `grain` are the image bytes the brush file itself carries and the
  archive uses: `Shape.png` (`Grain.png`), else the folder member named exactly
  by `bundledShapePath` (`bundledGrainPath`), else `None`.
- **Secondaries.** Every `SubNN/` folder that holds a `Brush.archive` is
  hashed, in ascending order of its folder name, whether or not the typed view
  of F3 exposes it: a `Sub02/` that F3 files under `extras` still enters the
  hash. A secondary's shape and grain are resolved inside its own folder by the
  same rule as the primary's (`SubNN/Shape.png`, else the member of that folder
  named by the secondary archive's `bundledShapePath`, else `None`).
- A file under `library/bundled/` never enters the hash.
- Not hashed: the thumbnail, `Reset/` (and anything under it), the author
  picture, the signature, a `.empty` placeholder, any other member.
- `content_sha256` is always the bare 64 hex characters, no prefix. The
  tagger's `fp` is its first 16.
- `name_utf8` is the set name exactly as the plist holds it (a trailing space
  counts). `brush_ids` are the members in plist order.
- A set's id changes when its membership or order changes.

**Golden vectors** (asserted in `pipeline/tests/test_identity.py`):

| Input | Id |
|---|---|
| archive `b"A"`, no shape, no grain | `b_8f525da47bd2` |
| archive `b"A"`, shape `b"S"`, grain `b"G"` | `b_747322c04223` |
| the same, plus one sub `(b"A2", None, b"G2")` | `b_7795500d8ec4` |
| set `"Demo Set "` (trailing space) of the first two ids, in that order | `s_41c10a3b97f2` |
| texture `b"PNG"` | `t_796120837694` |

**Collisions.** Twelve hex characters of two different full hashes may not
coincide. `identity.Registry` records the full hash behind every id it hands
out and raises `PrefixCollision`; a command that meets one exits 1 and writes
nothing.

**Slugs.** `identity.slugify(text, fallback)`:

1. drop apostrophes (`'`, `‘`, `’`, `ʼ`);
2. NFKD, drop combining marks, drop every non-ASCII character, lower-case;
3. replace each run outside `[a-z0-9]` with one `-`, strip `-` from both ends;
4. an empty result is the fallback; a Windows device name (`con`, `prn`, `aux`,
   `nul`, `com1`-`com9`, `lpt1`-`lpt9`) gets `x-` in front;
5. cut to 48 characters and strip `-` again.

| Name | Slug |
|---|---|
| `Sargent’s Oils` | `sargents-oils` |
| `Broken Conté` | `broken-conte` |
| `3D` | `3d` |
| `Autumn Stamps ` | `autumn-stamps` |
| a name with no ASCII letters or digits | the fallback |

- A set's slug is `sets[name].slug` from `library/sources.json` when given, else
  `slugify(name)`. An official set always takes `official.files[].slug`.
- Two sets with one slug is an error (exit 1) that asks for a slug in the manifest.
- Brush slugs are informational. Files are named by id.

**Loose brushes.** A pack's loose `.brush` files form one pseudo-set. It has no
plist, so everything a plist would give is fixed here:

| Of a pseudo-set | Is |
|---|---|
| `set_slug` | `<pack_id>-loose` (`identity.loose_set_slug`) |
| `kind` | `loose` (a real set is `set`) |
| member order | the pack's stored `.brush` files sorted by `(file name lower-cased, file name)`; that order gives each member its `position` |
| `name`, the text `set_id` hashes | the slug itself, `<pack_id>-loose` |
| `title` | `<product> (loose brushes)`, with the pack's `product` from the manifest |
| `set_id` | the F1 formula over that `name` and the member ids in that order, duplicates of set members included |

- A pack id is a set slug of at most 42 characters (`identity.PACK_ID_MAX`,
  `identity.is_pack_id`), so that `<pack_id>-loose` is itself a slug. The
  manifest readers in `ingest.py` and `fetch_base_library.py` refuse a longer
  one with exit 2.
- A pseudo-set none of whose members has its home there (every loose file
  repeats a brush of a real set; see F5 "Duplicates and homes") keeps its row
  in `catalog.json` and its `sets/<set_slug>.json`, with `"note": null`. It
  gets no note and no sidecar (F7).

## F2. Roots and shared helpers

Module: `pipeline/brush_common.py`.

```
resolve_paths(root=None, library=None, catalog=None, vault=None)
    -> Paths(root, schema, catalog, vault, previews, tags, vocabulary, index, library, app)
EXIT_OK, EXIT_REFUSED, EXIT_USAGE = 0, 1, 2
APP_PORT = 8719
TOOL_ROOT = Path(__file__).resolve().parents[1]          # the brushes/ folder
```

| Path | Flag | Environment | Default |
|---|---|---|---|
| `root` | `--root` | `ROSW_BRUSHES_ROOT` | `TOOL_ROOT` |
| `library` | `--library` | `ROSW_BRUSHES_LIBRARY` | `<root>/library` |
| `catalog` | `--catalog` | `ROSW_BRUSHES_CATALOG` | `<root>/catalog` |
| `vault` | `--vault` | `ROSW_BRUSHES_VAULT` | `<root>/vault` |
| `index` | none in `resolve_paths` | `ROSW_BRUSHES_INDEX` | `<vault>/tools/rag_index/index.json` |
| `schema` | none | none | `TOOL_ROOT/schema`, always |
| `app` | none | none | `TOOL_ROOT/app`, always |
| `previews` | | | `<vault>/_Previews` |
| `tags` | | | `<vault>/_BrushTags` |
| `vocabulary` | | | `<vault>/_BrushTags/vocabulary.yaml` |

- **`root` is the data root.** It moves `library/`, `catalog/` and `vault/`.
  `schema/` and `app/` are code assets, not data: they are always the folders
  beside `pipeline/`, whatever `--root` or `ROSW_BRUSHES_ROOT` says. Every
  test runs against a temporary data root and still reads the one schema;
  `brush_model.load_schema()` (F3) and the app server's static files (F10)
  read `paths.schema` and `paths.app`, which are those two folders.
- Order: flag, then environment, then default. An empty value counts as absent.
- `resolve_paths` returns absolute paths, creates nothing and checks nothing. A
  script that needs a folder that is missing says which and exits 2.
- `add_path_arguments(parser, names)` adds the flags; `paths_from_args(args)`
  resolves from parsed arguments.
- `ENV_ROOT`, `ENV_LIBRARY`, `ENV_CATALOG`, `ENV_VAULT`, `ENV_INDEX` and the
  mapping `ENV_NAMES` hold the environment names; `FLAGS` the flag spellings.
- The tools in `vault/tools/` do not import `pipeline/`. They take `--vault`,
  `--catalog` and `--index` (`--index` exists only there), and resolve each
  folder in this order: the flag; the folder's own variable
  (`ROSW_BRUSHES_VAULT`, `ROSW_BRUSHES_CATALOG`, `ROSW_BRUSHES_INDEX`); then
  `ROSW_BRUSHES_ROOT`, as `<ROOT>/vault` and `<ROOT>/catalog`; then the tool's
  own vault and the `catalog/` beside it. With only `ROSW_BRUSHES_ROOT` set,
  the command-line search therefore reads the same vault and catalog as the
  pipeline scripts and both servers. `ROSW_BRUSHES_LIBRARY` is spelled the
  same way wherever a vault tool names it. A test keeps all five names equal
  to `ENV_NAMES`.
- **Stored paths** are POSIX and relative: `preview.*` and `note` to the vault
  (`_Previews/…`, `02_Vendor_Packs/…`), `container` to the library
  (`user/<pack>/<file>`). `stored_path(path, base)` makes one.

Other helpers: `open_console()`; `read_text(path)`; `write_text(path, text)`,
`write_bytes(path, data)` and `write_json(path, value)`, each through
`<name>.tmp` and `os.replace`; `json_text(value)`, which is
`json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"`.

## F3. The file codec

Modules, all libraries with no command line of their own: `pipeline/bplist.py`,
`keyed_archive.py`, `brush_model.py`, `container.py`, `png_io.py`, `gbr.py`, and
`zip_writer.py`, the one zip writer, which exists today ("Writing" below). The
one file-level command is `pipeline/brush_file.py` (F11).

Errors: `CodecError(code, detail)` is the base; `BplistError`, `ArchiveError`,
`BrushModelError`, `ContainerError`, `LimitExceeded(ContainerError)`,
`PngError`, `PngUnsupported(PngError)` derive from it.

### Model

```
brush_model.decode(data: bytes) -> Brush          encode(b: Brush) -> bytes
brush_model.from_archive(a) -> Brush              to_archive(b) -> Archive
brush_model.to_json(b) -> {"schema": "rosw-brushes-model/1", "era", "family", "profile",
                           "top_order": [...], "root_class": [...], "key_order": [...], "params": {...}}
brush_model.from_json(obj) -> Brush
brush_model.apply_patch(b, changes, *, mode="strict"|"clamp", allow_unknown=False) -> (Brush, PatchReport)
brush_model.new_brush(name, *, era="M220", overrides=None, now=None) -> Brush
brush_model.detect_era(keys) -> (era_id, exact, missing, extra)
brush_model.nearest_era(keys) -> era_id           # the era itself on an exact match
brush_model.validate(b) -> [Issue]                Issue(level, code, key, message)
brush_model.curve_points(b, key) -> [(x, y)]      set_curve(b, key, points)
brush_model.census(archives) -> dict
brush_model.load_schema() -> dict                 # TOOL_ROOT/schema/silica_keys.json: never under a data root (F2)

keyed_archive.decode(data, *, verify=True) -> Archive      encode(archive, *, profile=None) -> bytes
keyed_archive.PROFILES = {"ios_legacy": ..., "ios_modern": ...}
Archive(top_order, version, archiver, objects, profile, fidelity, source)   # fidelity "byte" | "table"

bplist.parse_table(data, *, max_objects=100_000, max_bytes=1 << 20) -> ObjectTable
bplist.serialize_table(table) -> bytes     bplist.loads(data)     bplist.dumps(value, *, shared)
```

- `Brush.params` keeps insertion order, which is the root key order. `to_json`
  repeats it as `key_order`, because JSON written with sorted keys loses it.
- `decode` re-encodes with each profile and compares with the input. A match
  sets the profile and `fidelity="byte"`; no match sets `fidelity="table"` and
  keeps the source bytes.
- An unmodified archive always exports as its source bytes. A modified one is
  rule-encoded with its own profile and top order; a `table` archive that is
  modified uses its family's default profile and raises a warning Issue. A
  modified archive of an unknown era is rule-encoded and reported as
  `fidelity: valid`, not canonical.
- A brush is re-exported in the era it was read in. Unknown keys and unknown
  classes are written back as read.

### Eras

Detected from the root key set, never from the `version` key.

| Era | Root keys (with `$class`) | Family |
|---|---|---|
| `E0` | 52 | legacy |
| `E1` | 61 | legacy |
| `E1b` | 62 | legacy |
| `E1c` | 63 | legacy |
| `E2` | 67 | legacy |
| `E3` | 88 | legacy |
| `E4` | 101 | legacy |
| `M172` | 172 | modern |
| `M173` | 173 | modern |
| `M220` | 220, or 221 to 223 with optional curve keys | modern |
| `M242` | 242 | modern |
| `X<count>` | any other key set, named by its key count (`^X[0-9]+$`) | that of its nearest era |

- **An era matches only on an exact root key set.** The key count alone decides
  nothing: 88 keys that are not E3's 88 keys are `X88`, not `E3`. `M220` is the
  one era with a range: its 220 keys plus any subset of its named optional
  curve keys.
- `detect_era(keys)` returns `(era_id, True, [], [])` on a match. Otherwise the
  id is `X<count>`, `exact` is false, and `missing` and `extra` are measured
  against the **nearest era**: the one whose key set has the smallest symmetric
  difference with `keys`, the earlier row of the table on a tie.
  `nearest_era(keys)` names it.
- The family of an `X<count>` archive is its nearest era's. Nothing else is
  borrowed from that era: an unmodified archive still exports its source bytes,
  and a modified one is rule-encoded and reported `fidelity: valid`.
- Until `brush_model` exists, `device_tests.py` names an era by key count
  alone, to choose test members. That is a stand-in, not this rule, and it
  writes no id into any catalog.

Profiles: `ios_legacy`, `ios_modern`.

**New brushes.** The default era is `M220`; `E4` can be chosen. One constant in
`brush_model` holds the default, `spec.yaml` `format.new_brush_era` declares
it, and `GET /api/status` reports it. The template is the parameter set of one
real donor archive of that era, read from the library when the brush is made;
only the name, the date and the textures are replaced. A brush may gain a key
only if the schema lists it as optional for the brush's own era; there is no
free "add key".

### JSON value forms

The catalog, HTTP and MCP all carry these forms.

| Value | JSON |
|---|---|
| real | a number (the 32-bit float, widened) |
| int, bool | a number, `true`/`false` |
| string reference | a string, or `null` for nil; a wrapped one is `{"string": s, "wrapper": "NSMutableString"}` |
| data | `{"$data": "<hex>"}` (the `color` key; read-only in v1) |
| curve | `{"points": ["{0.000000, 0.000000}", ...]}`, plus `"resolution": 1024` in a legacy archive |
| roll parameters | `{"mode", "activationFalloff", "activationOrigin", "activationRange"}` |
| array | a list of numbers |
| date | `{"time": <seconds since 2001-01-01, 64-bit>}` |
| unknown class | `{"$class", "$classes", "$fields": [[key, value], ...]}`, kept verbatim |
| a scalar under a key the schema does not know | `{"$real32": x}`, `{"$real64": x}` or `{"$int": n}` |

- JSON is written with `allow_nan=False`.
- The canonical text of a real is the shortest decimal that round-trips the
  32-bit float. Equality compares 32-bit patterns.
- A patch may send curve points as numeric pairs. `apply_patch` rewrites them
  as `"{%.6f, %.6f}"`, the two endpoints first and interior points after. An
  untouched curve keeps its strings.

### Patches

A client never sends a full settings object. It sends `changes`: the keys it
means to change.

```
PatchReport = {"ok": bool, "era": str,
               "applied":   {key: value},
               "clamped":   [{"key", "from", "to", "min", "max"}],
               "rejected":  [{"key", "value", "code", "reason"}],
               "unchanged": [key],
               "warnings":  [{"key", "code"}]}
rejected codes: unknown_key | wrong_type | not_in_enum | non_finite | read_only | not_in_era | curve_invalid
warning codes:  outside_observed | stale_thumbnail
```

- Values are coerced by schema type (`1` on a real key becomes `1.0`) and reals
  are rounded to 32 bits.
- A key absent from `changes` is never touched.
- A change equal to the base value at the 32-bit level is listed in `unchanged`
  and changes nothing.
- A value is clamped (`mode="clamp"`) or rejected (`mode="strict"`) against
  `limits` only when the schema row says `"limits_hard": true`. Otherwise it is
  applied and the report warns `outside_observed`: observed ranges are not rules.
- Patch envelope, for handing a patch to the app by paste:
  `{"schema": "rosw-brushes-patch/1", "base_id": <brush_id>|null, "summary": str, "changes": {key: value}}`.
- Python is the authority (`POST /api/validate-patch`, MCP
  `validate_settings_patch`, both `service.validate_patch`). The app's own
  check is advisory. Both run the cases in `schema/patch_cases.json`.

### Containers

```
container.read_any(data, hint="", *, limits=DEFAULT_LIMITS) -> [BrushSet | BrushFolder]
container.read_brush(data) -> BrushFolder          read_brushset(data) -> BrushSet
container.write_brush(folder, *, mtime=ZIP_EPOCH) -> bytes
container.write_brushset(s, *, mtime=ZIP_EPOCH, preserve_order=False) -> bytes
container.resolve_textures(folder, params) -> {"shape": (bytes|None, source), "grain": (bytes|None, source)}
container.new_uuid() -> str                        # upper-case version 4
container.safe_filename(name) -> str

BrushSet(name, brushes: [(uuid, BrushFolder)], entry_order, origin, plist_extra: dict)
BrushFolder(archive, shape, grain, thumbnail, author_picture, signature, sub, reset, extras)
```

A `BrushFolder` is the folder's members as an ordered list of (path, bytes),
with the typed views above over it: one `sub` (`Sub01/`), one `reset`
(`Reset/`), and `extras` for everything else. Identity is `identity.py`'s;
`container` has no id function.

```
BrushFolder := Brush.archive [Shape.png] [Grain.png] [QuickLook/Thumbnail.png]
               [AuthorPicture/AuthorPicture.png] [Signature/SignaturePicture.png]
               [Sub01/ BrushFolder] [Reset/ BrushFolder]
```

**Reading**

- `zipfile` over `BytesIO`. Nothing is extracted to disk and no entry name is
  used as a path.
- Sniff by content, never by extension: a root `brushset.plist` is a set; a
  root `Brush.archive` is a brush; one shared top folder that holds
  `brushset.plist` is a set.
- Anything else is searched for entries ending `.brush`, `.brushset`,
  `.brushset.zip` or `.zip`, to nesting depth 3.
- **Junk is part of no folder.** An entry under `__MACOSX/`, and an entry named
  `.DS_Store`, `Thumbs.db` or `desktop.ini` (compared without regard to case),
  is dropped wherever it sits, and so is an entry that is only a folder.
  Nothing else is ever dropped by a reader.
- **Inside a brush folder every other entry is a member.** It is kept, in
  source order, in the folder's member list, and is written back: a zero-byte
  `.empty`, a file nobody knows, a `Sub02/`. A member no typed view claims is
  listed in `extras` and raises an unknown-member warning. A `.empty` is a
  member like any other, with two exemptions only: it raises no such warning,
  and it never enters identity (F1). It also never decides what a container is
  when the sniff looks for one shared top folder.
- An entry of a set that lies outside every brush folder and is not
  `brushset.plist` (a stray file at the root) belongs to no folder: it is
  reported as skipped and is not written back.
- A duplicate entry name: the first wins, with a warning, and the later ones
  are dropped. Stored (uncompressed) entries are accepted.
- `ingest.py` and `device_tests.py`, which read containers before
  `container.py` exists, follow these same rules (`JUNK_FOLDERS`, `JUNK_NAMES`
  and `EMPTY` in each; a test keeps the two spellings equal).
- The plist's `brushes` array is the only brush order. A folder the plist does
  not list is kept and flagged.
- Extra plist keys (for example `iconName`) are kept in `plist_extra`, in
  source order, and written back.
- Names are kept exactly, with their spaces and non-ASCII characters.
- Refused, and reported as skipped: an encrypted entry; an absolute name, a
  name with `..` or a backslash. On Windows `zipfile` rewrites a backslash in
  `ZipInfo.filename` to a slash, so the test is made on `orig_filename`.
- A file that begins `version https://git-lfs.github.com/spec/v1` is a pointer,
  not a brush: exit 2 with "run git lfs pull".
- A secondary folder beyond `Sub01` goes to `extras` with a warning.

**Texture resolution**, once, in `resolve_textures`: `Shape.png`; else the
folder member named exactly by `bundledShapePath`; else
`library/bundled/<that name>` (source `bundled-supplied`); else the brush only
names an image inside the drawing app (source `bundled`). The same for grain,
where the name `Brush-Preset-Blank.png` is source `blank` and no name and no
image is `none`. `validate` flags only a `Shape.png` (`Grain.png`) present
together with a bundled path.

**Caps** (`spec.yaml` `format.caps` mirrors the code constants)

| Cap | Value |
|---|---|
| Entries in one container | 5,000 |
| One `Brush.archive` | 1 MiB |
| One inflated entry | 64 MiB |
| One container, inflated | 2 GiB |
| Inflation ratio | above 200:1 on an entry over 16 MiB is refused |
| Nesting depth | 3 |
| An upload, or a nested container | 512 MiB |
| Objects in one property list | 100,000 |
| Depth of a property list | 64 |
| Pixels in one image | 8192 x 8192 |

Exceeding one raises `LimitExceeded`. A container that cannot be read is
skipped and listed; `--strict` turns that into exit 1.

**Writing**

- **One writer.** Every zip this tool makes is written by
  `zip_writer.write_zip(entries, *, date_time=DEFAULT_DATE_TIME) -> bytes`,
  where `entries` is `(name, data)` or `(name, data, date_time)` in the order
  to store them. `container.write_brush` and `write_brushset` call it and write
  no zip of their own; nothing uses `zipfile` to write. `zip_writer.check_name`
  says whether a name can be stored, and `ZipWriteError` is what it raises.
- What it writes, in every entry: deflate (method 8) as a raw stream made at
  **zlib level 1** with the default window and memory level; flag bits
  `0x0006`; `create_system` 0, `create_version` 0, `extract_version` 20;
  `external_attr` 0; **internal attribute bit 0 set to 1 when the entry's data
  is text** by zlib's own rule (`zip_writer.is_text`), so `brushset.plist`
  carries 1 and every archive and image 0; no extra fields, no comment, no
  directory entries, no zip64, ASCII entry names.
- These values were read from the 72 files of `library/user/`, and the writer
  reproduced each of those files byte for byte from its entries and dates.
  That is not yet shown for the official sets: two of them are reported to hold
  stored (method 0) entries, which this writer re-writes as deflate. A stored
  mode and non-ASCII entry names are added only from header values read off a
  real file.
- A brush folder is named by an upper-case version-4 UUID. A modified or new
  brush gets a fresh one.
- Entry order per brush, contiguous: `Brush.archive`, `Shape.png`, `Grain.png`,
  `QuickLook/Thumbnail.png`, `AuthorPicture/…`, `Signature/…`, `Sub01/…`,
  `Reset/…`, then other members sorted. `brushset.plist` is last.
  `preserve_order=True` replays the source order.
- Every source member that the caller did not replace is written back
  byte-identical, including `.empty` members and unknown files: exactly the
  member list "Reading" keeps. What a reader dropped (junk, a folder entry, a
  later duplicate) was never a member, so its absence is not a `dropped` in an
  export report.
- The default `mtime` is a fixed constant (`zip_writer.DEFAULT_DATE_TIME`).
- Tests never assert zip bytes: deflate output depends on the zlib build.

`brushset.plist` is XML, UTF-8, LF, tab-indented, with a final newline, keys
`brushes` then `name` (then any extra keys), and `&`, `<`, `>` escaped:

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>brushes</key>
	<array>
		<string>UUID</string>
	</array>
	<key>name</key>
	<string>NAME</string>
</dict>
</plist>
```

### Images

```
png_io.Image(width, height, mode, pixels, chunks)      # mode L | LA | RGB | RGBA
png_io.png_info(data) -> dict                          # header and chunk list only
png_io.read_png(data, *, max_pixels=8192 * 8192) -> Image
png_io.write_png(width, height, mode, pixels, *, level=6, chunks=()) -> bytes
png_io.to_gray8(img) -> Image                          # luminance x alpha over black
png_io.write_thumbnail(alpha: bytes) -> bytes          # 1060x324 coverage in, RGBA PNG out
png_io.HAVE_PIL: bool                                  # ROSW_BRUSHES_NO_PIL=1 forces the stdlib path
```

- Read: 8 and 16 bit, colour types 0, 2, 3, 4, 6, all five filters, not
  interlaced. An interlaced image raises `PngUnsupported` unless PIL is present.
- A shape or grain is written as 8-bit grey (colour type 0), not interlaced,
  chunks `IHDR, IDAT, IEND`, filter 0, zlib level 6. White is paint when
  `shapeInverted` is false.
- A thumbnail is written 1060x324 RGBA, colour 255 wherever alpha is above 0
  and 0 elsewhere, chunks `IHDR, sRGB(0), pHYs(2835, 2835, 1), IDAT, IEND`.
- An imported image is passed through untouched. It is re-encoded only when the
  user replaced it; an image sent back whose sha256 equals the base member's is
  kept, never converted.
- A bundled name is kept verbatim through model, JSON and export. No image is
  ever made up for one.

`pipeline/gbr.py` writes the GIMP `.gbr` form in Python.

### Export

One function builds an export for every surface (`service.build_export`); only
`service.write_export` puts one on disk (F12).

- The base of an export is always original bytes: a library original, or the
  members the client sends back. Catalog `settings` is read-only data and is
  never a base.
- Empty `changes` and every texture kept returns the source archive bytes.
- The dry run and the result list every member as `verbatim`, `re-encoded`,
  `replaced` or `dropped`. A `dropped` the request did not ask for is an error.
- Thumbnail: `keep`, a supplied PNG, or `omit`. A supplied PNG is decoded and
  rewritten through `png_io.write_thumbnail`. The command line and the MCP tool
  keep the existing thumbnail after an edit and warn `stale_thumbnail`.
- `Reset/` is kept verbatim, and the dry run says so.

## F4. Schema row

File: `schema/silica_keys.json`. It is the only list of archive keys.

```
top level: schema_version, sources, profiles, eras, classes, encode_order,
           groups: [{id, label, order}], keys

row: {"key", "type": "real|int|bool|string_ref|data_ref|curve_ref|roll_ref|array_ref|date_ref",
      "eras": [...], "default",
      "limits": [min, max] | null, "limits_hard": bool, "observed": {...},
      "enum": {value: {"label", "verified"}} | null, "aliases": [key, ...],
      "retired": bool, "replaced_by": [...],
      "group": <tab id>, "section": str, "label": str,
      "confidence": "verified|inferred|unknown",
      "ui": "slider|toggle|select|stepper|curve|text|readonly|hidden",
      "display": "percent|signedPercent|factor|raw|enum",
      "step", "hint", "ai": bool, "preview": "honoured|approx|ignored", "advanced": bool, "notes"}
```

- `group` is a tab id from F10's list of 14. `section` is the heading inside it.
- `eras` rows carry the era id, key count, `key_order`, `top_order`, profile and
  encode family. `classes` gives each class chain and field order.
- `aliases` names the same setting under another era's key
  (`dynamicsGlazeFlow` and `dynamicsGlazedFlow`). The stroke engine and the
  facet code read aliases; neither hard-codes one era's names.
- `preview` starts as `approx` and becomes `honoured` only with a recorded
  measurement.
- The codec fills every column. The app may later change only `group`,
  `section`, `label`, `display`, `step`, `hint`, `ai`, `preview`, `advanced`.
- **How the file is made.** It is authored: no script writes under `schema/`
  (F12). Its census columns (`type`, `eras`, `default`, `observed`, and the
  top-level `eras`, `classes` and `encode_order`) are taken from what
  `python -I brushes/pipeline/ingest.py census --json` prints. That command
  writes nothing; the person running it merges its output into the file by
  hand, and the remaining columns are written by hand. An opt-in corpus test
  compares the census columns with a fresh census, so a copy that has gone
  stale fails. "Generated from a census" in the plan means this. A script that
  wrote the file would be a new writer: it needs a row in F11 and in F12, and
  `--confirm`, before it is written.
- Bundled texture names and their stand-ins live in
  `schema/bundled_textures.json`, which the app owns. There are no brush
  templates in the schema.

Other files in `schema/`: `facets.json` (F5), `preview_calibration.json` (shared
by the app and `previews.py`), `patch_cases.json` (F3).

## F5. Catalog

Folder: `catalog/`, generated and committed. Written by `ingest.py build`, and
in part by `previews.py render --confirm` (F12).

| File | Holds |
|---|---|
| `catalog.json` | the assembled index: packs, sets, brush rows, counts |
| `brushes/<brush_id>.json` | one full record per brush. **The one home of a brush's facets, facet words and preview object** |
| `sets/<set_slug>.json` | one record per brushset |
| `textures.json` | one record per `texture_id`: `{sha256, width, height, used_as, shape_tiles: {"n", "i"}, grain_tile, stats}`. The tile paths and `stats` (the pixel statistics) are filled by `previews.py` and are `null` before it has run |
| `thumbnails.json` | per brush id: `{source_sha256, stroke, stroke_source, alpha_max, alpha_hi, gain, ink_fraction, bbox}`, written by `previews.py`. `source_sha256` is the hash of the thumbnail file the stroke was made from |
| `containers.json` | container sha256 to parsed summary, so a re-ingest can skip |
| `ingest_report.json` | counts, duplicates, skipped files, warnings, keys the schema lacks |

All are written with `brush_common.json_text`. No timestamp, no absolute path.

**The run order.** Each step reads what the one before it wrote:

```
fetch_base_library.py fetch --confirm      library/official/
ingest.py adopt <src> --confirm            library/user/
ingest.py build                            catalog/, in its form before previews
previews.py render --confirm               vault/_Previews/, then the three preview fields of each brush record
notes.py write --confirm                   the notes
brush_search.py index                      the index
```

**Preview-derived fields.** Three fields of a brush record depend on what
`previews.py` measured: `facets`, `facet_words` and `preview`. One rule covers
who writes them and who reads them.

- **One function writes them:** `ingest.apply_preview_results(paths)`. It reads
  `thumbnails.json` and `textures.json`, and for each brush record sets
  `preview`, the measured facets (`stroke_source`, `has_grain`, and the six
  texture facets `shape_coverage`, `shape_aspect`, `shape_midtone`,
  `shape_edge_touch`, `grain_mean`, `grain_contrast`) and `facet_words`. It
  changes no other field, rewrites a record only when its text changes, and
  then calls `ingest.assemble_index`. It is the only code that derives a facet
  word from a measurement, so the facet rules stay in `ingest.py`.
- **Two commands call it:** `previews.py render --confirm`, as its last step,
  after it has written the preview files, `thumbnails.json` and the texture
  statistics; and `ingest.py build`, as its last step, so that a re-ingest
  keeps what was measured before. `previews.py` writes no brush record itself.
- **Before previews has run for a brush** (no `thumbnails.json` entry for it,
  or one whose `source_sha256` is not the hash of the brush's current thumbnail
  file) its record is in the pre-preview form: `preview.stroke`, `.shape` and
  `.grain` are `null`; `preview.stroke_source` is told from which member
  exists (`thumbnail` for `QuickLook/Thumbnail.png`, else `reset-thumbnail`
  for `Reset/QuickLook/Thumbnail.png`, else `none`); the six texture facets
  are `null`; `has_grain` is true for an embedded grain; and `facet_words`
  holds no `shape-even|wide|tall`, `shape-hard|mixed|soft` or
  `grain-flat|subtle|medium|strong` word. `shape_source` and `grain_source`
  never depend on previews: `ingest.py build` sets them from
  `resolve_textures`.
- **After it has run** `preview.stroke_source` may differ from the provisional
  value in one case: a thumbnail whose alpha is all zero falls back to the
  `Reset/` thumbnail or to `none` (F6).
- **Everyone reads the brush record.** `notes.py`, `brush_search.py` and
  `service.py` take `facets`, `facet_words` and `preview` from
  `brushes/<brush_id>.json`. The same three values in a row of `catalog.json`
  are copies made by `assemble_index`, for listing; `thumbnails.json` and
  `textures.json` are inputs to the function above and are read by nobody else
  for these values. A note written before `previews.py render` therefore shows
  no texture numbers; `notes.py check` reports it as changed once they exist.

**`brushes/<brush_id>.json`**

```json
{"schema": "rosw-brushes-brush/1",
 "id": "b_0123456789ab", "content_sha256": "<64 hex>",
 "name": "Demo  Pencil", "display_name": "Demo  Pencil", "slug": "demo-pencil",
 "library": "user", "pack": "demo-pack", "family": "legacy", "era": "E3",
 "format": {"key_count": 88, "version": 2, "ref_size": 1, "archive_bytes": 2970,
            "archive_sha256": "<64 hex>", "classes": ["SilicaBrush", "ValkyrieBrush", "NSObject"]},
 "home": {"set_slug": "demo-set", "position": 2},
 "occurrences": [{"set_slug": "demo-set", "set_id": "s_0123456789ab", "position": 2, "pack": "demo-pack",
                  "container": "user/demo-pack/Demo_Set.brushset", "container_sha256": "<64 hex>",
                  "entry_prefix": "401B8E73-5721-492C-BB16-BD8DF8A0419B/"}],
 "shape": {"source": "bundled", "bundled_name": "Brush-Preset-Hard.png", "texture_id": null, "inverted": false},
 "grain": {"source": "blank", "bundled_name": "Brush-Preset-Blank.png", "texture_id": null, "inverted": false},
 "thumbnail": {"present": true, "sha256": "<64 hex>", "width": 1060, "height": 324, "color_type": 6},
 "secondary": null,
 "reset": null,
 "author": {"name": null, "has_picture": false, "has_signature": false, "creation_date": null},
 "settings": {"...": "to_json(brush)[\"params\"], every root key, read-only"},
 "facets": {"...": "see below"},
 "facet_words": ["stroke", "spacing-continuous"],
 "preview": {"stroke": "_Previews/demo-set/b_0123456789ab.stroke.png", "stroke_source": "thumbnail",
             "shape": null, "shape_source": "bundled",
             "grain": null, "grain_source": "blank"},
 "warnings": []}
```

- `preview.stroke`, `.shape`, `.grain` are vault-relative paths or `null`.
- `secondary`, for a dual brush: `{"name", "component_sha256", "era", "settings",
  "shape", "grain"}`. It is never a brush of its own, has no id and no note
  section, and is not counted.
- `reset`, when a `Reset/` folder exists: `{"archive_sha256", "same_as_live",
  "differing_keys": [up to 20], "has_secondary"}`.
- The author picture and the signature are recorded by presence only. They are
  personal images and are never copied to a preview.
- `name` is verbatim (trailing and doubled spaces kept).
  `display_name = name.strip() or "Untitled"`.

**`catalog.json`**

```json
{"schema": "rosw-brushes-catalog/1", "ingest_version": 1, "facet_rules_version": 1,
 "library_fingerprint": "sha256:16:<16 hex>",
 "counts": {"brushes": 0, "occurrences": 0, "sets": 0, "notes": 0, "packs": 0, "textures": 0,
            "by_library": {"user": 0, "official": 0}},
 "packs": [{"...": "the manifest fields of each pack, plus counts"}],
 "sets": [{"set_slug", "set_id", "name", "title", "kind", "library", "pack", "pack_kind",
           "brush_count", "note", "brushes": ["<brush_id>", "..."]}],
 "brushes": [{"id", "name", "display_name", "home_set", "position", "library", "family", "era",
              "key_count", "facets", "facet_words", "preview", "occurrence_count"}]}
```

`sets[].kind` is `set` or `loose` (F1 "Loose brushes" fixes a pseudo-set's
order, name and title). `sets[].note` is the note's vault-relative path, or
`null` for a pseudo-set with no home brush. `sets/<set_slug>.json` holds that
set's row as its own file.

`counts.sets` counts every row of `sets`, real sets and pseudo-sets alike,
with or without a note. `counts.notes` counts the rows whose `note` is not
`null`; it is the number of notes `notes.py` writes. On today's library that
is 65 set rows (21 user sets, 4 pseudo-sets, 40 official sets) and 64 notes:
all 15 loose files of `rsco-dry-brush-pack` repeat brushes of its set, so
`rsco-dry-brush-pack-loose` has no home brush and no note. (The user half was
counted in memory for this document: 615 occurrences, 597 brush ids. The
official half is the manifest's 40 files, not yet counted.)

`catalog.json` is a pure function of the brush records and `textures.json`
(`ingest.assemble_index`). It is assembled by `apply_preview_results`, which
runs at the end of `build` and again at the end of `previews.py render`. A
re-ingest keeps texture statistics by `texture_id` and leaves
`thumbnails.json` as it is, so what was measured survives a rebuild.

**Duplicates and homes**

- A container already seen (same sha256) is recorded as a location and not
  parsed again.
- One brush id is one record, however many times it occurs. `occurrences` lists
  each place; `home` prefers a real set over a loose pseudo-set, then the
  smallest `(pack, set_slug, position)`.
- Two brushes with one name in one set are two ids; a note distinguishes their
  headings with ` (2)`, ` (3)` in plist order.
- Pack assignment: a path under `user/<pack_id>/` or `official/<pack_id>/`;
  else the manifest's `match` patterns; else pack `unsorted`, with a warning.

**Facets.** `ingest.py` computes them, with thresholds read from
`schema/facets.json`; a test asserts that every facet has both a JSON entry and
a function, and that the names equal `spec.yaml` `facets`. The search tool
reads `facets` and `facet_words` from the record and never derives one. Values
are rounded to 4 decimal places. `S(k)` below means the setting `k`, tried
under its schema aliases. A facet name uses `_`; a facet word uses `-`.

| Facet | Rule | Facet words |
|---|---|---|
| `kind`, `is_stamp` | `S("stamp")` is true | `stamp` or `stroke` |
| `spacing`, `spacing_class` | `plotSpacing`: up to 0.02 `continuous`; up to 0.10 `tight`; up to 0.50 `visible`; above `dotted` | `spacing-<class>` |
| `shape_source`, `uses_bundled_shape` | from `resolve_textures` | `shape-embedded`, `shape-bundled` |
| `grain_source`, `has_grain`, `uses_bundled_grain` | `has_grain` when embedded (contrast at least 0.01 once measured) or bundled and not blank | `grain-embedded`, `grain-bundled`, `grain-blank`, `grain-none` |
| `grain_movement`, `grain_application_code` | `textureMovement` 0 `static`; 0.999 or more `rolling`; else `partial`. `textureApplication` kept raw | none |
| `wet_mix` | `dynamicsRenderType == 3` when that key exists, else `dynamicsMix > 0` | `wet-mix` |
| `render_code` | `render-type-<n>`; `glaze-type-<n>` for E0; modern `transfer-<max\|std>.<mod\|flat>.<rec\|simple>` from the three `rendering*` keys | none |
| `taper`, `taper_start`, `taper_end` | start: `max(taperStartLength, pencilTaperStartLength) > 0.01`; end likewise; class `none`, `start`, `end`, `both` | `taper-<class>` unless none |
| `pressure_size`, `pressure_size_class` | `dynamicsPressureSize`: below -0.02 `inverse`; below 0.02 `none`; below 0.35 `low`; below 0.70 `medium`; else `high` | `pressure-size-<class>` unless none |
| `pressure_opacity`, `pressure_opacity_class` | the same thresholds on `dynamicsPressureOpacity` | `pressure-opacity-<class>` unless none |
| `tilt` | any of `dynamicsTiltSize`, `dynamicsTiltOpacity`, `dynamicsTiltGradation`, `dynamicsTiltBleed` above 0.02 | `tilt` |
| `speed` | absolute `dynamicsSpeedSize` or `dynamicsSpeedOpacity` above 0.02 | `speed` |
| `size_min`, `size_max`, `size_class` | `minSize`, `maxSize`; max up to 1 `fine`; up to 6 `medium`; up to 12 `broad`; else `max` | `size-<class>` |
| `opacity_min`, `opacity_max`, `translucent` | `maxOpacity < 0.999` | `translucent` |
| `dual`, `dual_blend_code` | a `Sub01/Brush.archive` exists (not the `dualBlendMode` key) | `dual` |
| `blend_code`, `blend_extended_code` | `blendMode`, `extendedBlend` | `blend-<n>` when not 0 |
| `scatter`, `shape_rotation`, `randomised`, `azimuth` | `shapeScatter > 0.02`; `shapeRotation != 0`; `shapeRandomise`; `shapeAzimuth` | `scatter`, `shape-rotation`, `randomised`, `azimuth` |
| `jitter_size`, `jitter_opacity`, `jitter_position` | `dynamicsJitterSize`, `dynamicsJitterOpacity`, `plotJitter` above 0.02 | `jitter-size`, `jitter-opacity`, `jitter-position` |
| `streamline` | `plotSmoothing > 0.02` | `streamline` |
| `color_dynamics` | any hue, saturation, lightness, darkness, brightness or secondary-colour dynamics key not 0 | `color-dynamics` |
| `wet_edges`, `burnt_edges` | `wetEdgesAmount`, `burntEdgesAmount` above 0.02 | `wet-edges`, `burnt-edges` |
| `era`, `family` | from `brush_model.detect_era` | `era-<id in lower case>` |
| `stroke_source` | `preview.stroke_source`: from member presence at `build`, settled by `apply_preview_results` ("Preview-derived fields") | `no-thumbnail` when `none` |
| `shape_coverage` | mean of the normalised shape tile over 255 | none |
| `shape_aspect` | width over height of the bounding box of values above 16 | 0.8 to 1.25 `shape-even`; above `shape-wide`; below `shape-tall` |
| `shape_midtone` | share of values between 16 and 240 among values above 16 | below 0.25 `shape-hard`; below 0.75 `shape-mixed`; else `shape-soft` |
| `shape_edge_touch` | border-ring mean over 0.05 | none |
| `grain_mean` | mean over 255 | none |
| `grain_contrast` | population standard deviation over 255 | below 0.03 `flat`; below 0.10 `subtle`; below 0.25 `medium`; else `strong` (`grain-<class>`) |

Every threshold is a heuristic and every class name is a name guess: a note
shows the raw number beside each class. The six texture facets (the last six
rows) are `null` in the brush record until `previews.py` has run and
`apply_preview_results` has filled them ("Preview-derived fields" above).
Raise `facet_rules_version` when a rule changes.

## F6. Preview files

Folder: `vault/_Previews/`. Written only by `previews.py render --confirm`.
Every file is 8-bit grey with no alpha, written by `png_io.write_png`.

| File | Size | Tracked |
|---|---|---|
| `<home_set_slug>/<brush_id>.stroke.png` | 530x162 | yes |
| `_textures/<texture_id>.<n\|i>.shape.png` (`n` not inverted, `i` inverted) | 256x256 | yes |
| `_textures/<texture_id>.grain.png` | 256x256 | yes |
| `manifest.json` | | yes |
| `_sheets/<set_slug>/sheet-NN.png`, `_sheets/<set_slug>/sheets.json` | 802x1496, 8 rows | no (ignored) |
| `_local/…` | | no (ignored) |

Limits: 128 KB per tracked file, 50 MB for all of them.

- **Stroke.** The ink is the stored thumbnail's alpha (colour types 6 and 4);
  with no alpha, luminance, inverted when the border mean is above 127. Reduce
  by an integer box mean `(sum + n//2)//n` with
  `f = max(1, ceil(max(w/W, h/H)))`, centred. Stretch:
  `hi = max(16, 99.5th percentile (nearest rank) of non-zero ink)`,
  `ink' = min(255, (ink*255 + hi//2)//hi)`. Flatten on dark:
  `v = 26 + (229*ink' + 127)//255`. The stretch `gain` is recorded in
  `catalog/thumbnails.json` and handed to the tagger.
- **No thumbnail, or all-zero alpha.** Use `Reset/QuickLook/Thumbnail.png` when
  present (`stroke_source: "reset-thumbnail"`). Otherwise write a placeholder
  tile (`stroke_source: "none"`). v1 never invents a stroke;
  `rendered-approx` is reserved.
- **Shape tile.** The whole image reduced to fit 256, normalised so that white
  is paint (`255 - v` when `shapeInverted`), on black.
- **Grain tile.** The centre 256x256 at 1:1 (tiled when smaller), not inverted.
- **Bundled-only texture.** No tile file. A sheet draws a labelled stand-in
  cell; a note states the file name in text. A file supplied at
  `library/bundled/<name>` gives a real tile with source `bundled-supplied`.
- **Meaning of approximate.** A stored thumbnail is the drawing app's own
  render, exact even when shape and grain are bundled. A result row's
  `approximate` is true only for `rendered-approx`.
- **No churn.** `manifest.json` maps each output to
  `{source_sha256, preview_version, pixel_sha256}`. A file is rewritten only
  when the source hash or `PREVIEW_VERSION` changes or the file is missing.
- **Sheets.** One column of 8 cells, 802x1496, background 16. A cell is a
  label bar, the 530x162 stroke, and the shape and grain tiles at 128x128.
  `sheets.json` (schema `rosw-brushes-sheets/1`) lists per sheet
  `cells: [{n, id, name, stroke_source, shape_source, grain_source}]`. One or
  two sheets make one tagger call. `render --sheets-only` rebuilds the sheets
  from the committed stroke and tile files with no library.
- A pack with `publish_previews: false` has its previews written under `_local/`.
- A dry run touches neither the vault nor the catalog.

## F7. Notes

One note per brushset that is the home of at least one brush, written by
`notes.py write --confirm` as a pure function of the catalog and a template.
A set row whose `note` is `null` in the catalog (a pseudo-set of loose files
that all repeat brushes of a real set, F1) gets no note, no sidecar and no
line in an `_index.md`; its brushes are found through their home notes. The
number of notes is `counts.notes` (F5).

- **Path:** `<NN_Folder>/<set_slug>.md` under `vault/`; folders
  `01_Procreate_Defaults`, `02_Vendor_Packs`, `03_Loose`, `04_My_Brushes`, each
  with an `_index.md`; `00_INDEX.md` at the top.
- **Which folder.** The first row that fits the set decides:

  | The set | Folder |
  |---|---|
  | `library` is `official` | `01_Procreate_Defaults` |
  | its pack's `pack_kind` is `mine` (a real set or the pack's loose pseudo-set) | `04_My_Brushes` |
  | its `kind` is `loose` | `03_Loose` |
  | anything else (a real set of a `vendor` pack, or of pack `unsorted`) | `02_Vendor_Packs` |

  `ingest.py build` writes the result into `sets[].note`; `notes.py` reads it
  from there and works out no folder of its own.
- **Title and name.** `title` and `set_name` come from the set row. For a
  pseudo-set they are `<product> (loose brushes)` and `<pack_id>-loose` (F1).
- **Frontmatter**, flat (`key: value` or a one-line `[a, b]` list, no commas
  inside items, `"` in a title replaced by `'`), these keys in this order:
  `title, type, set_name, set_slug, set_id, library, pack, pack_kind, vendor,
  redistribute, brush_count, eras, kinds, template, generated_fingerprint, tags`.
- **Body:** `# <title>`; `## Overview`; one `## <display name>[ (n)]` per brush
  whose home is this set, in plist order; optional `## Shared brushes`;
  `## Notes`.
- **Reserved headings:** `Overview`, `Shared brushes`, `Notes`. A brush with one
  of those names gets ` (brush)` appended.
- **A brush chunk** is an H2 section whose first list line matches
  ``^- id: `(b_[0-9a-f]{12})` ``. It has twelve list lines, always present, in
  this order and with these prefixes: `id, kind, shape, grain, size, pressure,
  tilt, speed, taper, render, facets, preview`.
- **Numbers:** `%.3f` for size and spacing, `%.2f` elsewhere. These are for
  reading. An exact value is quoted from `catalog/brushes/<brush_id>.json`,
  joined by the id on the `- id:` line.
- **`## Shared brushes`:** one stub line per member whose home is another set:
  ``- `<brush_id>` <name>: see [[<home note>#<heading>]]``.
- **`## Notes`** and everything after it belongs to the author.
- Line numbers reported for a chunk are 1-based file lines.
  `CHUNKER_VERSION = "b1"`.

Reference render (the values are illustrative; the layout is the contract):

```markdown
---
title: "Demo Set"
type: brushset
set_name: "Demo Set "
set_slug: demo-set
set_id: s_0123456789ab
library: user
pack: demo-pack
pack_kind: vendor
vendor: "Demo Vendor"
redistribute: unknown
brush_count: 2
eras: [E3]
kinds: [stroke]
template: brushset-note/1
generated_fingerprint: "sha256:16:<16 hex>"
tags: [brushset, library/user, era/E3]
---

# Demo Set

## Overview

Two brushes from the pack `demo-pack` (Demo Vendor), read from `Demo_Set.brushset` (517,781 bytes). Both are stroke brushes in format era E3. One carries its own shape image and one uses a shape that ships inside Procreate. Neither embeds a grain image. The pack states no licence, so redistribution is unknown.

Everything above `## Notes` is generated from the catalog. Write only below it.

## Demo Inker

- id: `b_0123456789ab` · 1 of 2 · era E3 · 88 keys
- kind: stroke · spacing tight (0.026)
- shape: embedded 2048x2048, inverted yes · coverage 0.61 · aspect 1.00 · edges hard · scatter 0.18 · rotation 1.00 · randomised yes · azimuth no
- grain: blank (`Brush-Preset-Blank.png`) · scale 16.00 · movement 1.00 · zoom 1.00
- size: 0.003 to 0.198 (fine) · opacity 0.01 to 1.00
- pressure: size high (1.00) · opacity none (0.00)
- tilt: none
- speed: size 0.63 · opacity 0.00
- taper: both · pencil 0.11/0.11 · touch 0.21/0.24
- render: render-type-0 · blend 0 · flow 0.91 · wet mix no
- facets: stroke spacing-tight shape-embedded shape-even shape-hard grain-blank pressure-size-high speed taper-both size-fine scatter shape-rotation randomised jitter-position streamline era-e3
- preview: Procreate's own thumbnail

![[_Previews/demo-set/b_0123456789ab.stroke.png]]

## Demo  Pencil

- id: `b_ba9876543210` · 2 of 2 · era E3 · 88 keys
- kind: stroke · spacing continuous (0.000)
- shape: bundled `Brush-Preset-Hard.png` (inside Procreate, not in this library) · scatter 0.19 · rotation 1.00 · randomised no · azimuth yes
- grain: bundled `Brush-Preset-Stained-Paper-1.jpg` · scale 1.37 · movement 1.00 · zoom 1.00
- size: 0.005 to 0.184 (fine) · opacity 0.00 to 0.92
- pressure: size high (0.82) · opacity medium (0.69)
- tilt: size 1.00 · opacity 0.80
- speed: size 0.00 · opacity 0.20
- taper: both · pencil 1.00/1.00 · touch 0.00/1.00
- render: render-type-0 · blend 0 · flow 1.00 · wet mix no
- facets: stroke spacing-continuous shape-bundled grain-bundled pressure-size-high pressure-opacity-medium tilt speed taper-both size-fine translucent scatter shape-rotation azimuth jitter-opacity streamline era-e3
- preview: Procreate's own thumbnail; shape and grain images are not in the file

![[_Previews/demo-set/b_ba9876543210.stroke.png]]

## Notes

```

**Regeneration**

1. Render the generated part (frontmatter through the blank line before
   `## Notes`). `generated_fingerprint` is the first 16 hex of the sha256 of
   that text with the fingerprint value blanked.
2. In an existing file, split at the last line exactly equal to `## Notes`. The
   tail is kept byte for byte, CRLF included.
3. If the existing generated part's recomputed fingerprint differs from its
   stored one, the note was edited by hand: it is `REFUSED`, nothing is written
   for it, and the run exits 1, unless `--overwrite-generated` is given (which
   shows the lost lines and still needs `--confirm`).
4. Equal text is `unchanged`: no write.

Statuses printed: `new`, `changed (+a -b)`, `unchanged`, `REFUSED`, `orphan`. An
orphan (a note with no set in the catalog) is never deleted. `notes.py check`
exits 1 when anything would change, and needs no library.

`_index.md` (`type: moc`) has one bullet per note; `00_INDEX.md` holds counts,
per-folder lists and a table of facet-word counts. Both keep the same
generated and authored split.

## F8. Tag sidecars and the tagger block

**Sidecar:** `vault/_BrushTags/<note path>.tags.json`, for example
`_BrushTags/02_Vendor_Packs/demo-set.md.tags.json`. Written only by
`vault/tools/brush_tags.py apply --confirm`.

```json
{"schema": 1, "file": "02_Vendor_Packs/demo-set.md", "generator": "brush-tagger v1",
 "vocabulary_fingerprint": "sha256:16:<16 hex>", "updated": "2026-01-01T00:00:00Z",
 "brushes": {
  "b_0123456789ab": {
   "content_sha256": "<64 hex>", "name": "Demo Inker",
   "medium_tags": [], "mark_tags": [], "texture_tags": [],
   "edge_tags": [], "motif_tags": [], "use_tags": [],
   "visual": "One plain sentence about what the stroke looks like.",
   "visual_basis": "described-not-measured",
   "evidence": {"previews": ["sheet"], "stroke_source": "thumbnail"},
   "notes": "One sentence grounding the tags.", "tagged": "2026-01-01T00:00:00Z", "tagger": "brush-tagger v1"}}}
```

- Six axes: `medium`, `mark`, `texture`, `edge`, `motif`, `use`. The stored key
  is `<axis>_tags` in the vocabulary, the sidecar, the index and a result row.
- Caps: medium 2, mark 2, texture 3, edge 2, motif 2, use 3.
- The vocabulary is closed: `vault/_BrushTags/vocabulary.yaml`, the author's
  file, with top-level `<axis>_tags:` keys, two-space `- tag` items and one `#`
  definition per tag on the same line. A word outside it is refused and logged
  as a suggestion.
- `evidence.previews` items are `sheet`, `stroke`, `shape`, `grain`.
- A brush has one note section (in its home note), so its entry lives in that
  note's sidecar. The index still resolves an id across all sidecars, so a
  brush whose home moves keeps its tags; `also_in` comes from the catalog's
  `occurrences`.
- An entry is stale when its `content_sha256` differs from the catalog's.
- Tag sidecars may hold timestamps (`updated`, `tagged`): they record when a
  person-supervised tagging happened and are not regenerated by a build.

**Tagger block.** The tagging agent returns text only, one block per brush, in
the order it was given them:

```
### brush <brush_id> (name: "<name>", chunk <n>, lines <a>-<b>, fp: <content_sha256[:16]>)
medium_tags: <comma-separated tags, or "(none)">
mark_tags: <comma-separated tags, or "(none)">
texture_tags: <comma-separated tags, or "(none)">
edge_tags: <comma-separated tags, or "(none)">
motif_tags: <comma-separated tags, or "(none)">
use_tags: <comma-separated tags, or "(none)">
visual: <one sentence, or "(none)" when no preview was seen>
evidence: <sheet | stroke, shape, grain | none>
notes: <one sentence grounding the tags in this brush's preview, name or facets>
suggestions: <comma-separated "axis:proposed-tag -- why", or "(none)">
```

- The tagger reads contact sheets, sliced from `sheets.json`: one sheet is 8
  brushes, at most two sheets per call. There is no per-brush card.
- Visual tags (`texture`, `edge`) and `visual` are withheld only when
  `stroke_source` is `none`: then the tagger tags from name and facets and
  writes `visual: (none)`. A bundled shape or grain does not withhold them.
- `brush_tags.py apply` rejects a block when: the id is not in the note or not
  in `--ids`; `fp` differs; a tag is outside the vocabulary; an axis is over
  its cap; `visual` is empty while evidence is not `none`.
- Logs, appended by `apply --confirm` only: `_BrushTags/_backfill_log.jsonl`
  and `_BrushTags/_vocabulary_suggestions.jsonl`.

## F9. The search engine

Module: `vault/tools/brush_search.py`, standard library only, no import from
`pipeline/`. Other modules load it with
`importlib.util.spec_from_file_location`.

```
load_index(path) -> index
build_index(vault, catalog, *, write=True) -> index
check_fresh(index, vault, catalog) -> {"state": "fresh"|"stale", "reason"}
search_index(index, query="", *, tags=(), where=(), where_not=(), source_types=None,
             top=5, offset=0, settings=False) -> envelope
similar(index, brush_id=None, *, settings=None, tags=(), where=(), where_not=(),
        top=10, other_sets=False) -> envelope
facet_counts(index, *, tags=(), where=(), where_not=()) -> dict
chunks_for(vault, catalog, note, ...) -> dict
resolve_brush(index, ref) -> chunk
load_vocabulary(vault) -> {axis: [{"tag", "definition"}]}
raises UsageError (exit 2) | NotFound (exit 1); only main() calls sys.exit
```

```
envelope = {"query", "tags", "where", "where_not",
            "ranking": "cosine" | "tag-purity" | "filter-order",
            "total", "offset", "results": [ROW]}
ROW = {"brush_id" | null, "name", "set", "set_title", "library", "pack", "source_type",
       "note", "heading", "start_line", "end_line", "score",
       "medium_tags", "mark_tags", "texture_tags", "edge_tags", "motif_tags", "use_tags",
       "visual", "visual_basis", "tag_state", "facets",
       "preview": {the F5 preview object}, "approximate",
       "also_in": [{"set", "note", "heading"}],
       "record": "brushes/<brush_id>.json",
       "settings" (only when asked)}
```

- This envelope is the wire shape for the command line, MCP and HTTP. A
  service adds only `"index": "fresh" | "stale" | "memory"`.
- `similar` adds `method`, and per result `compared_keys`, `coverage`,
  `differs: [{key, query, other, delta}]`.
- `tag_state` is `tagged`, `stale` or `untagged`.
- The index reads headings and line ranges from the notes, and settings,
  `facets`, `facet_words`, `preview` and `content_sha256` from
  `catalog/brushes/<brush_id>.json`, joined by the id on the note's `- id:`
  line. It derives no facet, and reads none from `catalog.json`,
  `thumbnails.json` or `textures.json`. The texture facets and words are in the
  record once `previews.py render` has run (F5 "Preview-derived fields"); an
  index built before that carries them as `null`, and `inputs_fingerprint`
  makes it stale when they arrive.
- `inputs_fingerprint` covers the notes, the sidecars, `vocabulary.yaml`,
  `catalog/catalog.json` and `catalog/brushes/*.json`.
- The index file (`vault/tools/rag_index/index.json`, ignored) holds no
  absolute path. It embeds the vocabulary with its definitions; there is no
  generated vocabulary file.
- Ranking: TF-IDF cosine over one chunk per brush
  (`idf = ln(N/(1+df)) + 1`). Tags only: `tag-purity`, the mean over the tag
  filters of `1 / len(chunk[axis])`. Filters only: `filter-order`. Results are
  de-duplicated by `brush_id`.
- Tokenizer `t1`: fold typographic apostrophes and accents; keep `b_` ids
  whole; split camelCase; keep digits; `colour` to `color`, `grey` to `gray`;
  light plural stemming; no Porter stemmer.

**Filters**

- `--tag AXIS=V[,V2]`: repeatable and ANDed; a comma list is OR. Pattern
  `^[a-z][a-z_]*=[a-z0-9][a-z0-9,-]*$`. The axis is the short name or the
  `*_tags` key. An unknown axis or value exits 2 with the valid list.
- `--where KEY=V1,V2` and `--where KEY=MIN..MAX` (inclusive, either side may be
  empty), plus `--where-not KEY=V`. A key is a facet name, a raw setting key,
  or one of `id`, `set`, `library`, `tagged`. Booleans accept
  `true/false/yes/no/1/0`. An unknown key exits 2. There are no comparison
  operators: the grammar is safe to type unquoted in a shell.

**Similar** (`method: "gower-v1"`): numeric settings scaled by the 1st and 99th
percentile, booleans and enums equal or not, `shape_ref` weight 4, `grain_ref`
weight 3, every other weight 1 (`spec.yaml` `similar.weights`); missing keys
filled from schema defaults when a schema is present.

## F10. HTTP and MCP

Both servers are thin over one layer, `pipeline/service.py` (`BrushService`:
`status, search, get_brush, similar, list_sets, vocabulary, preview,
settings_schema, validate_patch, decode_upload, open_library_brush,
build_export, write_export`), so the MCP tools, the HTTP routes and
`--json` output return the same shapes. Errors are
`ApiError(code, message, status, hint=None, data=None)`.

Index states: `fresh`; `stale` (served, and flagged in every result); `memory`
(no index file: built in RAM, nothing written); `not_ingested` (no catalog:
data calls fail with a hint that lists the commands in order). A status always
reports one of the four, never `null`: a build that cannot tell `fresh` from
`stale` says `stale`. A server never exits because data is missing.

**The base of a patch.** `validate_patch` (the MCP tool
`validate_settings_patch` and `POST /api/validate-patch`) checks `changes`
against one archive, named in one of three ways:

| Given | The base is |
|---|---|
| `base_id` | the library original of that brush id |
| `base` | `{"members": [{"path", "b64"}]}`, the same form as the export request's base; only `Brush.archive` is read from it |
| neither | the new-brush template of `era` (default: the new-brush era) |

`base_id` and `base` together are `bad_argument`. `base` is never a `to_json`
model and never catalog `settings`: a base is original bytes (F3 "Export").
`era`, when given with a base, must equal the base's own era.

### HTTP: `pipeline/app_server.py`

- Binds `127.0.0.1:8719`. The one origin is `http://localhost:8719`. A busy
  port is exit 2; the server never falls back to another port.
- A token is made per run (`secrets.token_urlsafe(24)`), printed once in the
  first stdout line, `Open http://localhost:<port>/#t=<token>`, and reaches the
  page only in the URL fragment. Every `/api/*` call sends it as
  `X-ROSW-Token`; it is compared with `secrets.compare_digest` on bytes.
- Request gate, in order: method GET or POST (else 405); target starts with
  `/`, at most 2048 characters, no NUL; `Host` is `localhost:<port>` or
  `127.0.0.1:<port>` (else 403 `bad_host`); `Origin`, if present, is
  `http://<allowed host>` (else 403 `bad_origin`); `Sec-Fetch-Site`, if
  present, is `same-origin` or `none` (else 403 `cross_site`); route lookup
  (else 404); token on `/api/*` (else 403 `bad_token`); a POST needs
  `Content-Length` (else 411), within the route's cap (else 413), and
  `application/json`, or `application/octet-stream` for import (else 415).
- Every response: `Content-Length`, `Cache-Control: no-store`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `Cross-Origin-Resource-Policy: same-origin`. Header values are ASCII.
- HTML also gets `Content-Security-Policy: default-src 'self'; img-src 'self'
  blob: data:; style-src 'self'; script-src 'self'; connect-src 'self'
  http://localhost:* http://127.0.0.1:*; worker-src 'self' blob:; object-src
  'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'`.
- Static files, no token: every regular file under `app/` found by walking it
  at start (no dot-files, at most 8 MiB, served by exact match from an explicit
  extension table, never `mimetypes`), plus exactly `/schema/silica_keys.json`,
  `/schema/facets.json`, `/schema/bundled_textures.json` and
  `/schema/preview_calibration.json`. `/` is `/index.html`.
- The server writes nothing. An export is returned to the browser.

| Route | Request | Response |
|---|---|---|
| `GET /api/status` | | the `library_status` payload, plus `caps` and the new-brush era |
| `GET /api/search` | `q`, repeated `tag`, `where`, `where_not`, `top` (1 to 200, default 48), `offset` | the F9 envelope; with no filter, browse in set order |
| `GET /api/facets` | repeated `tag`, `where`, `where_not` | facet and tag counts |
| `GET /api/vocabulary` | | the vocabulary payload |
| `GET /api/sets` | `library` | the `list_sets` payload |
| `GET /api/sets/<set_slug>` | | one set with its rows in order |
| `GET /api/brush/<id>` | `include=a,b` | the `get_brush` payload |
| `GET /api/brush/<id>/similar` | `top` | the similar envelope |
| `GET /api/brush/<id>/open` | `textures=full\|preview\|none` | the import "brush" response, from library originals; 409 `library_missing` without them |
| `GET /api/preview/<id>/<kind>.png` | kind `stroke`, `shape` or `grain` | `image/png` |
| `GET /api/app-source.zip` | | a zip of the allow-listed app files |
| `POST /api/similar` | `{"settings", "tags", "where", "where_not", "top", "other_sets"}` | the similar envelope, for settings that are not a library brush |
| `POST /api/import` | raw bytes; `X-ROSW-Filename` (percent-encoded, display only); query `member=`, `textures=full\|preview\|none` | see below |
| `POST /api/validate-patch` | `{"changes", "base" \| "base_id", "era"}` | the PatchReport, plus `patch_text` |
| `POST /api/export` | see below | bytes, or a JSON report |
| `POST /api/quit` | | `{"ok": true}`, then shutdown |

`<id>` matches the brush id pattern of F1 and is looked up in the catalog; no
path is ever built from it. A preview path taken from the catalog is checked to
lie inside the previews root.

Errors are `{"error": {"code", "message", "hint", "data"}}` with these codes:

| Status | Codes |
|---|---|
| 400 | `bad_request`, `bad_json`, `bad_argument` |
| 403 | `bad_host`, `bad_origin`, `cross_site`, `bad_token`, `export_disabled` |
| 404 | `not_found`, `unknown_id`, `no_preview` |
| 405, 411, 413, 415 | `method_not_allowed`, `length_required`, `too_large`, `unsupported_file` |
| 409 | `library_missing` |
| 422 | `corrupt_file`, `invalid_settings` |
| 500, 503 | `internal`, `not_ingested` |

**Import is stateless.** The page keeps the file and posts it again to pick a
member. The container is sniffed from its bytes and read in memory under the
F3 caps.

- Several brushes and no `member`: a manifest, `{"kind": "brushset", "name",
  "brush_count", "brushes": [{"member", "index", "name", "era", "key_count",
  "shape": {"source", "ref"}, "grain": {...}, "dual", "has_thumbnail",
  "library_id"}], "skipped": [{"entry", "reason"}], "warnings"}`.
- One brush, or a `member`: `{"kind": "brush", "member", "name", "era",
  "settings": {...}, "meta": {"class", "classes", "key_count", "unknown_keys",
  "archive_sha256"}, "textures": {"shape": {"source": "embedded", "width",
  "height", "png_b64"} | {"source": "bundled", "ref", "standin_png_b64"},
  "grain": {...}, "thumbnail": {"png_b64"} | null},
  "sub": {"settings", "textures", "meta"} | null,
  "base": {"members": [{"path", "b64"}]}, "library_id", "warnings"}`.
- `base.members` is every original member verbatim: `Brush.archive`,
  `Shape.png`, `Grain.png`, the thumbnail, `Sub01/`, `Reset/`, author files and
  unknown files. `png_b64` is the original file's bytes, untouched.

**Export request**

```
{"format": "brush" | "brushset" | "gbr" | "kit", "name": "<set name>", "dry_run": false,
 "brushes": [{
   "base": {"library_id": "<brush_id>"} | {"members": [{"path", "b64"}]} | null,
   "changes": {key: value},
   "mode": "strict" | "clamp",
   "textures": {"shape": {"keep": true} | {"png_b64": "..."} | {"bundled": "<name>"}, "grain": ...},
   "thumbnail": {"keep": true} | {"png_b64": "..."} | {"omit": true},
   "sub": {"changes": {...}, "textures": {...}} | null,
   "uuid": "<optional>"}],
 "files": [{"path", "b64"}]}            # kit only
```

- `brush` takes exactly one entry. `base: null` starts from the new-brush
  template. `keep` refers to a base member.
- `strict` (the default) answers 422 `invalid_settings` with the `rejected` list.
- Success is `application/octet-stream` with `Content-Disposition: attachment;
  filename="<ascii-slug>.<ext>"; filename*=UTF-8''<percent-encoded name>` and
  `X-ROSW-Export: <percent-encoded {"filename", "size", "sha256", "brushes",
  "warnings": n}>`.
- `dry_run: true` returns JSON: `{"filename", "size", "sha256",
  "members": [{"path", "size", "state"}], "brushes": [{"name", "uuid", "era",
  "applied", "rejected", "warnings"}], "warnings"}`, where `state` is
  `verbatim`, `re-encoded`, `replaced` or `dropped`.

**The app.** Fourteen tabs, whose ids are the schema's group ids: `ai, stroke,
stabilization, taper, shape, grain, dynamics, pencil, wetmix, color, rendering,
properties, materials, about`; plus the library tab, `library`. A patch from
outside reaches the app by paste only (the envelope in F3); there is no patch
inbox on the server.

### MCP: `pipeline/mcp_server.py`

JSON-RPC over stdio, standard library only, one ASCII JSON object per line, no
`\r`. `sys.stdout` is replaced by `sys.stderr` after the wire handle is taken,
so a stray `print` cannot corrupt the protocol. EOF, a broken pipe and Ctrl-C
exit 0.

| Input | Reply |
|---|---|
| invalid JSON | error `-32700`, id null |
| not an object, wrong `jsonrpc`, no `method` | `-32600` |
| an array | each element handled; an empty array is `-32600` |
| no `id` (a notification) | no reply |
| `initialize` | `protocolVersion` (the client's, if it is `2024-11-05`, `2025-03-26`, `2025-06-18` or `2025-11-25`, else `2025-11-25`), `capabilities.tools`, `serverInfo` (`name: "rosw-brushes"`), `instructions` |
| `ping` | `{}` |
| `tools/list` | `{"tools": [...]}` |
| `tools/call` | a result; `-32602` when `name` is missing, `arguments` is not an object, or the tool is unknown |
| anything else | `-32601` |

A tool failure (a bad argument value, an `ApiError`, an unexpected exception)
is a result with `isError: true` and one text block
`{"error": {code, message, hint}}`, with no traceback. Success is
`{"content": [{"type": "text", "text": <compact JSON>}, ...image blocks],
"isError": false}`.

Tools (`ID` is a string matching the brush id pattern of F1):

| Tool | Arguments | Payload |
|---|---|---|
| `library_status` | none | `{"server", "version", "mode", "root", "index": {"state", "reason"}, "counts", "library_present", "library_files", "vocabulary_axes", "export": {"enabled", "dir"}, "next_steps": [...]}`; a stub build adds one key, `stub` (below) |
| `search_brushes` | `query` (max 500), `tags` (max 12, the tag pattern of F9), `where`, `where_not` (max 12 each), `top` (1 to 25, default 8); at least one of `query`, `tags`, `where` | the F9 envelope |
| `get_brush` | `id: ID`, `include` (of `settings, tags, facets, visual, textures, note`) | the brush: names, sets, `library`, `era`, `family`, facets, tags, `visual`, `visual_basis`, `settings`, textures, `dual: {"name", "era", "blend_code"} \| null`, preview, note location, duplicates |
| `similar_brushes` | `id: ID`, `top` (1 to 25, default 8), `where`, `where_not` | the similar envelope |
| `list_sets` | `library` (`user` or `official`) | `{"sets": [{"set_slug", "set_id", "name", "library", "vendor", "brush_count", "tagged", "note"}]}` |
| `list_vocabulary` | `axis` | `{"axes": {axis: {"description", "tags": [{"tag", "definition"}]}}, "facets": [{"name", "type", "values", "description"}]}` |
| `get_preview` | `id: ID`, `kinds` (1 to 3 of `stroke`, `shape`, `grain`; default `stroke`) | a text block naming the images, then one `image/png` block per kind found; serves stored files only |
| `get_brush_settings_schema` | `group`, `keys` (max 60), `detail` (`compact` or `full`) | the schema rows |
| `validate_settings_patch` | `changes` (required), `base_id: ID` or `base`, `era` | the PatchReport, plus `patch_text` |

**The `library_status` payload**, field by field (`GET /api/status` returns the
same object, plus `caps` and the new-brush era):

| Field | Value |
|---|---|
| `server`, `version` | `"rosw-brushes"` and the server's version |
| `mode` | `mode` is `"project"` for a checkout's own server and `"snapshot"` for the copy an installed plugin starts |
| `root` | the data root, POSIX and relative to the folder that holds it (in a checkout, the repository root) |
| `index` | `{"state", "reason"}`; `state` is one of the four index states above |
| `counts` | the `counts` object of `catalog/catalog.json` (F5), unchanged; `null` when there is no catalog. Never a count of files |
| `library_present` | whether `library/` holds any brush file |
| `library_files` | `{"user": {"files", "brushset", "brush"}, "official": {...}}`: files under each half of the library, counted by name, no file opened |
| `vocabulary_axes` | the tag axes the vocabulary defines, in order; `[]` when there is no vocabulary |
| `export` | `{"enabled", "dir"}` |
| `next_steps` | the commands that would make what is missing, in the order to run them. A command is listed only when its script is on disk **and** its verb is built; never with `--confirm` |

The stub build that exists today returns exactly these keys and one more,
`stub`: `{"stage": "stub", "roots", "exists", "not_read"}`. It opens no file,
so it reports `counts: null` and `vocabulary_axes: []` and lists both under
`stub.not_read`. The key goes when the stub does.

Every tool above is read-only (`readOnlyHint: true`). One more, `export_brush`
(`base_id: ID`, `changes`, `name`, `confirm`), is listed only when the server
is started with `--export-dir DIR`: `confirm: false` is a dry run;
`confirm: true` writes `<ascii-slug>-<id8>.brush` inside `DIR` only, opened so
that it never overwrites. The server writes nothing unless started with
`--export-dir`.

**Registration.** Two entries, one of which exists.

- `repo:.mcp.json` declares the server `brushes` with command `python` and
  arguments `-I` and `brushes/pipeline/mcp_server.py`. `-I` comes first: the
  server opens library originals (section 0).
- `repo:.claude-plugin/plugin.json` is to carry an `mcpServers.brushes` entry
  for the copy an installed plugin starts: command `python`, arguments `-I`,
  then a script path that starts with `${CLAUDE_PLUGIN_ROOT}/`
  (`${CLAUDE_PLUGIN_ROOT}/brushes/pipeline/mcp_server.py`), then
  `--defer-to-project ${CLAUDE_PROJECT_DIR}`. Started that way inside a project
  that has its own copy, the server stands down and lists no tools. **That
  entry is not there yet**: it is a Phase 5 item (`spec.yaml`
  `surfaces.mcp.plugin_entry.state` is `pending`). The stand-down itself is
  built and tested in `mcp_server.py`; what cannot be checked by hand until the
  entry exists is the server's behaviour outside this repository.
- Until that entry exists, `repo:.mcp.json` must not reach the published
  branch or an installed plugin snapshot. The repository root is itself a
  plugin, and a plugin's root `.mcp.json` is loaded as its MCP configuration:
  the plugin would try to start `brushes` in every project, where the relative
  script path does not exist, and would start a second copy inside this
  repository with nothing to make it stand down.

`pipeline/tests/test_mcp_server.py` reads `plugin.json` and holds the word
`pending` or `present` in `spec.yaml`, and this paragraph, to what the file
holds.

## F11. Command lines

| Script | Verbs and flags |
|---|---|
| `pipeline/fetch_base_library.py` | `list` \| `fetch [--only S] [--delay N] [--accept-upstream] [--confirm]` \| `verify` |
| `pipeline/ingest.py` | `where` \| `adopt <src> [--with-docs] [--confirm]` \| `build [--only S] [--strict]` \| `report` \| `census [--json]` |
| `pipeline/previews.py` | `render [--only S] [--force] [--no-sheets] [--sheets-only] [--stdlib] [--confirm]` |
| `pipeline/notes.py` | `write [--only S] [--diff] [--overwrite-generated] [--confirm]` \| `check` |
| `pipeline/brush_file.py` | `inspect <file>` \| `export --from <id\|file> … --out DIR [--confirm]` \| `roundtrip <file\|dir>` |
| `pipeline/device_tests.py` | `build <sitting> [--out DIR] [--known-bad FILE] [--allow-substitutes] [--confirm]` \| `verify <sitting> [--out DIR] [--allow-substitutes]` |
| `pipeline/app_server.py` | `[--port 8719] [--no-browser] [--dev]` |
| `pipeline/mcp_server.py` | `[--export-dir D] [--defer-to-project D] [--selftest]` |
| `vault/tools/brush_search.py` | `index [--check]` \| `search` \| `ask` \| `similar` \| `facets` \| `files` \| `chunks` \| `verify` \| `brush <id>` |
| `vault/tools/brush_tags.py` | `plan` \| `apply --file N [--ids …] [--confirm]` \| `check [--strict]` \| `suggestions` |

Every `pipeline/` script also takes the root flags of F2 that apply to it.
Every file `pipeline/*.py` is either a row of this table or one of the library
modules of `spec.yaml` `cli.library_modules`; a test walks the folder.

This table is the full contract, not what is built. `spec.yaml`
`build.built_verbs` lists the verbs that exist today: of `ingest.py`, `where`
and `adopt` (so `build`, `report` and `census` exit 2 until they land).

- `fetch_base_library.py fetch` is a dry run without `--confirm`. It reads
  `library/sources.json` `official.files`, saves each file as
  `library/official/<pack>/<slug>.brushset` through a `.part` file, checks the
  pinned size and MD5, and skips a file that already matches. When a download
  does not match its pins it is thrown away and the file is reported as
  "upstream changed"; the run continues with the other files and ends with
  exit 1. `--accept-upstream` keeps such a file and reports its size and MD5.
  `verify` re-hashes local files offline. It writes only `library/official/`
  and `library/official/fetch_log.jsonl`, never `sources.json`. It opens a
  connection only to a host in its own `ALLOWED_HOSTS` (section 0).
- `ingest.py adopt <src>` copies each unique container once to
  `library/user/<pack_id>/<name>`: ASCII-fold the name, replace anything
  outside `[A-Za-z0-9._-]` with `_`, and rename `.brushset.zip` to
  `.brushset`. Documents, artwork and images in a pack are not adopted
  (`--with-docs` copies documents to `library/user/<pack_id>/_docs/`, which is
  ignored). `build` needs no `--confirm`, and skips every `_docs/` folder and
  every `*.part` file when it scans the library. `where` prints the resolved
  roots. `census` calls `brush_model.census`, prints, and writes nothing.
- `device_tests.py build <sitting>` chooses the members of a test set from the
  library, builds the sitting's files in memory and, with `--confirm`, writes
  them to `repo:brushes/device-tests/<sitting>/` (or `--out`) and checks them.
  A set in which any slot holds a stand-in, or is empty, is not the control
  set: `build` then prints the plan, exits 1 and writes nothing, dry run or
  not, unless `--allow-substitutes` is given. `verify` reads the built files
  again with `zipfile` alone and compares every member with its library
  source; it exits 1 on any difference, and on a substitute or an empty slot
  unless `--allow-substitutes`. Sittings today: `sitting-1`.
- `brush_file.py roundtrip` exits 1 on any byte difference.
- `brush_search.py index --check` exits 0 when fresh and 1 when stale.

## F12. Who writes what

| Path | Only writer |
|---|---|
| `catalog/**` | `ingest.py build`; and `previews.py render --confirm`, which writes `thumbnails.json` and the tile paths and statistics of `textures.json` itself, and, through `ingest.apply_preview_results`, exactly three fields of each `brushes/<brush_id>.json` (`facets`, `facet_words`, `preview`) and the reassembled `catalog.json` (F5 "Preview-derived fields") |
| `vault/NN_*/*.md`, `_index.md`, `00_INDEX.md`, above `## Notes` | `notes.py write --confirm` |
| `vault/_Previews/**` | `previews.py render --confirm` |
| `vault/_BrushTags/*.tags.json` and the two `.jsonl` logs | `brush_tags.py apply --confirm` |
| `vault/tools/rag_index/**` (ignored) | `brush_search.py index` |
| `library/user/**` | `ingest.py adopt --confirm` |
| `library/official/**`, `library/official/fetch_log.jsonl` | `fetch_base_library.py fetch --confirm` |
| `repo:brushes/device-tests/<sitting>/**`, except `returned/` | `device_tests.py build --confirm` (`--out DIR` names another folder; inside `brushes/` only `device-tests/` may be written). `returned/` is created empty and is filled by hand, with what comes back from the device |
| a file in `--export-dir` or `--out` of `brush_file.py` | `service.write_export` only, reached by MCP `export_brush` with `confirm: true` and by `brush_file.py export --confirm` |
| authored, never generated | `spec.yaml`, `docs/CONTRACTS.md`, `schema/*.json`, `library/sources.json`, `vault/CLAUDE.md`, `vault/_BrushTags/vocabulary.yaml`, each note's `## Notes` |

Agents return text and write no file. Both servers write nothing else. No note
and no sidecar is written with an editor.

`schema/*.json` has no writer: no script writes under `schema/`. F4 says how
`silica_keys.json` is made from census output by hand; a script that wrote it
would first need a row here and in F11.

**What is committed**

| Path | In git |
|---|---|
| `library/user/**/*.brushset`, `*.brush`; `library/official/**/*.brushset` | yes, through Git LFS |
| `library/sources.json`, `library/README.md` | yes |
| `library/official/fetch_log.jsonl` | yes, as plain text (JSON lines; never through LFS) |
| `library/user/<pack_id>/_docs/`, `library/bundled/`, `*.part` | no (`library/.gitignore`: the rules `_docs/`, `bundled/`, `*.part`) |
| `catalog/**`, the notes, the tag sidecars, the tracked previews | yes |
| `vault/tools/rag_index/`, `vault/_Previews/_sheets/`, `vault/_Previews/_local/` | no (`vault/.gitignore`) |
| `repo:brushes/device-tests/<sitting>/manifest.json`, `CHECKLIST.md`, `returned/**` | yes; a `.brush` or `.brushset` in `returned/` through Git LFS |
| everything else in `repo:brushes/device-tests/<sitting>/` (the built set, `singles/`, `known-bad/`) | no (`repo:.gitignore`, the rule `brushes/device-tests/*/*`) |
| any `*.zip` | no (`repo:.gitignore`) |

- The original brush files are committed, for both halves of the library.
  There is no switch that ignores them. `redistribute` in
  `library/sources.json` is recorded information and gates nothing.
- The repository ignores `*.zip`, so a set is stored as `<name>.brushset`,
  never `<name>.brushset.zip`.
- A device-test sitting is not all scratch. Its built brush files are, and are
  ignored. Its `manifest.json` (which brushes went to the device, under which
  freshly drawn folder names), its `CHECKLIST.md` and its `returned/` folder
  cannot be made again by any build, and are committed. `returned/` holds the
  only device evidence there is, and the untouched new brush that becomes the
  new-brush template.
- **`git lfs install`, once per clone, before brush files are committed or
  pushed.** The LFS filter lines in a machine's git configuration are enough
  to store pointers, but the upload happens in the `pre-push` hook that
  `git lfs install` puts in `.git/hooks/`. Without it a push sends pointers
  whose objects the server has never seen, and is refused.
- `repo:.gitattributes` holds, in this order: `brushes/** text=auto eol=lf`
  (never the forced `text`, which would rewrite bytes inside binary files);
  `brushes/app/** -text`, which keeps the earlier designer byte for byte as it
  was received (nine of its files have CRLF line endings) and goes when the
  app is rebuilt; `binary` for `brushes/**/*.png` and `brushes/**/*.archive`;
  then `filter=lfs diff=lfs merge=lfs -text` for
  `brushes/library/**/*.brushset`, `brushes/library/**/*.brush`,
  `brushes/device-tests/**/returned/**/*.brushset` and
  `brushes/device-tests/**/returned/**/*.brush`.
- A tracked file under `brushes/` that is not an LFS pointer may not exceed
  95 MB. `pipeline/tests/test_repo_policy.py` checks the attributes, the
  ignore rules and that limit, and is skipped where git is absent.
- A clone made without Git LFS holds pointer files in `library/`. Readers
  detect one (F3) and say "run git lfs pull". No test needs the real files.

## The library manifest

File: `library/sources.json`, authored, schema `rosw-brushes-sources/1`. No
script writes it.

```json
{"schema": "rosw-brushes-sources/1",
 "packs": [{"id": "demo-pack", "kind": "vendor", "vendor": "Demo Vendor", "product": "Demo Pack",
            "source_url": null, "licence_note": "none in pack; store terms apply",
            "redistribute": "unknown", "publish_previews": true, "evidence": "folder name",
            "match": ["Demo Pack/**", "**/Demo_Pack.zip", "Demo_Pack.zip"],
            "sets": {"Demo Set ": {"slug": "demo-set", "title": "Demo Set"}}}],
 "official": {"host": "download-assets.procreate.art",
              "base": "https://download-assets.procreate.art/Old%20Procreate%20Assets/",
              "index_page": "<the page that lists the downloads>",
              "packs": [{"id": "procreate-5", "kind": "official", "vendor": "...", "product": "...",
                         "licence_note": "...", "redistribute": "unknown", "publish_previews": true}],
              "files": [{"pack": "procreate-5", "slug": "p5-inking", "title": "Inking (Procreate 5)",
                         "path": "Procreate%205/Inking%20Brush%20Set/P5_Inking.brushset",
                         "bytes": 477489, "md5": "2916edbbbdaa83a5de6072ff55b238a3"}]}}
```

- `packs` holds the user packs (`kind` `vendor` or `mine`); `official.packs`
  the official ones. `vendor` is `null` when the pack does not say.
- A pack `id` is a set slug of at most 42 characters (F1 "Loose brushes"), and
  `unsorted` is reserved. `product` gives a loose pseudo-set its title.
- `redistribute` is `yes`, `no` or `unknown`.
- `match` patterns are compared case-insensitively with `fnmatch` against the
  POSIX path relative to the folder being scanned; `*` crosses `/`. Each
  container must match exactly one pack. They are used only for a folder that
  is not yet laid out as `user/<pack_id>/`.
- `sets` maps a set's name, verbatim, to its slug and title. A pack with only
  loose brushes has an empty `sets`.
- `official.files[].path` is appended to `official.base`. `bytes` and `md5` pin
  the download. The file is stored as `official/<pack>/<slug>.brushset`.
- Today: 19 user packs and 40 official files (174,197,966 bytes).

## Device tests

Whether the drawing app opens a file this tool wrote can only be learned on a
device. `spec.yaml` `device_test.results` records one answer per path a file
can take, each `untested`, `passed` or `failed`:

| Path | Question |
|---|---|
| `container` | does it open our zip and plist around untouched members |
| `edit_legacy` | does it open a legacy archive re-encoded with one key changed |
| `edit_modern` | the same for a modern archive |
| `scratch_m220` | does it open a brush built from the M220 template |
| `scratch_e4` | the same from the E4 template |
| `thumbnail_policy` | what it shows for a missing, stale or supplied thumbnail |

Test files are written to `repo:brushes/device-tests/<sitting>/` by
`device_tests.py build --confirm` (F11, F12). The brush files built there are
ignored; the sitting's `manifest.json`, `CHECKLIST.md` and `returned/` are
committed (F12 "What is committed"). No document may claim more than these
results say; while a path is `untested` the wording is
"has not been opened in Procreate".

- **Only the control set goes to the device.** `ROSW-1-control.brushset` is
  eight brushes, one per kind of file; five of the eight kinds exist only in
  the official sets. `build` refuses a set with a stand-in or an empty slot
  (exit 1, nothing written), and `verify` fails one, unless
  `--allow-substitutes` is given; `manifest.json` records `complete` and
  `substitutes`. A sitting spent on an incomplete set answers only part of
  `container` and nothing of `thumbnail_policy`.
- The copy of the old designer's malformed file is written as
  `known-bad/KNOWN-BAD_old-designer.brush`, never under the name it came
  with: the brush that comes back from the device is called "Untitled Brush",
  one character from `Untitled_Brush.brush`. The known-bad file is never put
  in `returned/`.
- The zip of a test set is written by `zip_writer.write_zip` (F3), with fresh
  upper-case version-4 UUIDs as folder names.

## Test fixtures

`pipeline/tests/fixtures.py` builds every test input, standard library only and
independent of the code under test: archives through `plistlib`
(`make_archive`), images through `zlib` (`make_png`), containers through
`zipfile` (`brush_file`, `brushset_file`), a small library on disk
(`write_library`), inputs a reader must refuse (`hostile_files`,
`ratio_bomb`), and `BrushCase`, a test case with a temporary root and no
`ROSW_BRUSHES_*` variables.

- A fixture archive has the shape of a brush archive, not its exact bytes: it
  decodes as `fidelity="table"`. Byte-exact vectors live in the codec's tests.
- The legacy key sets (E0 to E4) are the real ones by name. The modern key set
  is reconstructed; until `fixtures.MODERN_KEYS_VERIFIED` is true, no test may
  assert that a modern fixture is detected as `M220`.
- Fixture writers refuse a target inside the real `brushes/` folder.
