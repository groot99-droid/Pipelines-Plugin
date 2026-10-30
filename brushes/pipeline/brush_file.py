"""The one file-level command of the brushes tool: look into a brush file,
export a brush from one, and prove that a file comes back byte for byte.

    python -I brushes/pipeline/brush_file.py inspect <file> [--json]
    python -I brushes/pipeline/brush_file.py export --from <brush id | file> [--brush SEL]
              [--set NAME] [--change key=value ...] [--out DIR] [--json] [--confirm]
    python -I brushes/pipeline/brush_file.py roundtrip <file | folder> [--allow-table]

Run it with `python -I`: a brush file is data from a stranger (docs/CONTRACTS.md,
section 0), and every file is read in memory under the caps of F3.

inspect    Every set and brush the file holds (nested zips included): each
           brush's members and which view claims them, its era, family, key
           count, fidelity, profile and id, where its shape and grain come from
           (F3 "Texture resolution"; a file in `<library>/bundled/` counts as
           `bundled-supplied`), its Sub01/ and Reset/ archives, and every
           warning. `--json` prints the same as one JSON object.

export     One brush, or one set, written as a new file. The base is always
           original bytes: a library brush named by its id (the first place it
           occurs, in sorted path order), or a file. `--brush` picks one brush
           of a set (its folder name, its 1-based position, or its exact name).
           `--change key=value` changes one archive key, by the rules of
           brush_model.apply_patch in strict mode; the value is read as JSON
           (`0.25`, `true`, `"text"`) and taken as text when it is not JSON.
           `--set NAME` writes a `.brushset` of that name around the export.
           An unchanged brush keeps its archive's source bytes; a changed one
           is re-encoded with its own profile and gets a fresh upper-case UUID
           folder name. Every other member is written back byte for byte; the
           thumbnail is the old one (a `stale_thumbnail` warning) and Reset/ is
           kept verbatim. The plan lists each member as verbatim, re-encoded,
           replaced or dropped. Without --confirm nothing is written; with it
           (and --confirm needs --out) the file goes into --out, never over an
           existing file, and never into the tool's own folders or the data
           roots. `--json` prints the plan as one JSON object on stdout, with
           `dry_run` and `written` (the path, or null); the dry-run line then
           goes to stderr. Until service.py exists, `write_export` here is the
           one writer of --out (F12).

roundtrip  For every container in a file, or under a folder (`.brush`,
           `.brushset` and `.zip` files; `_docs/`, `__MACOSX/` and `*.part`
           skipped): decode every `Brush.archive` (Sub01/ and Reset/ ones
           included) and require that an unchanged export is its source bytes
           and that the archive is re-encoded byte for byte by the rules
           (fidelity "byte"; with --allow-table a "table" archive is listed and
           does not fail); then rebuild the container from its members, read
           the rebuilt zip back with zipfile, and require the same entries, in
           the same order, with the same bytes. Each file gets one line and the
           run a total. Whether the rebuilt zip is the source file byte for
           byte (given the source's dates and forms) is reported, not required:
           it depends on the zlib build. Exit 1 on any mismatch, and on a run
           that found no brush file at all (so that a gate cannot pass on an
           empty folder); exit 2 for a Git LFS pointer.

Exit codes: 0 ok (a clean dry run too), 1 refused or failed (a mismatch, a file
that cannot be read, a rejected change, a file already at the target), 2 usage
or environment (a bad argument, a missing file or folder, a Git LFS pointer:
run git lfs pull).

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import identity  # noqa: E402
import keyed_archive  # noqa: E402
import png_io  # noqa: E402
from bplist import CodecError, ContainerError  # noqa: E402

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."
INSPECT_SCHEMA = "rosw-brushes-inspect/1"
FILE_SUFFIXES = (".brush", ".brushset", ".zip")
SKIPPED_FOLDERS = frozenset({"__macosx", "_docs"})
PART_SUFFIX = ".part"
BUNDLED_DIR = "bundled"
LIBRARY_HALVES = ("user", "official")

VIEW_OF = {container.ARCHIVE: "archive", container.SHAPE: "shape", container.GRAIN: "grain",
           container.THUMBNAIL: "thumbnail", container.AUTHOR_PICTURE: "author picture",
           container.SIGNATURE: "signature"}


class Usage(Exception):
    """A bad argument or a missing file or folder. Exit 2."""

    exit_code = bc.EXIT_USAGE


class Refused(Exception):
    """The command was understood and cannot be done. Exit 1."""

    exit_code = bc.EXIT_REFUSED


def show(text):
    """Text that is safe to print: control characters become `?`."""
    return "".join(ch if ch.isprintable() else "?" for ch in str(text))


def quoted(name):
    """A name in quotes, so that leading and trailing spaces show."""
    return f'"{show(name)}"'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# ── reading a file ───────────────────────────────────────────────────────────

def read_file(path, label):
    """Every set and brush of a file on disk: container.read_any, with the
    errors turned into this command's own."""
    path = Path(path)
    if not path.is_file():
        raise Usage(f"{show(label)} is not a file")
    try:
        data = container.read_path(path)
        return data, container.read_any(data, label)
    except ContainerError as exc:
        if exc.code == "lfs_pointer":
            raise Usage(f"{show(label)} is a Git LFS pointer, not a brush file: run git lfs pull") from None
        raise Refused(f"{show(label)} cannot be read: {show(exc)}") from None
    except OSError as exc:
        raise Usage(f"{show(label)} cannot be read ({type(exc).__name__})") from None


def bundled_folder(paths):
    folder = paths.library / BUNDLED_DIR
    return folder if folder.is_dir() else None


# ── inspect ──────────────────────────────────────────────────────────────────

def _png(data):
    try:
        info = png_io.png_info(data)
        return {"width": info["width"], "height": info["height"], "color_type": info["color_type"]}
    except CodecError:
        return {"width": None, "height": None, "color_type": None}


def view_of(path, named):
    if path in VIEW_OF:
        return VIEW_OF[path]
    top = path.split("/", 1)[0]
    if top == container.SUB:
        return "sub"
    if top == container.RESET:
        return "reset"
    if container.SUB_FOLDER.fullmatch(top) and "/" in path:
        return "secondary beyond Sub01"
    if path.rsplit("/", 1)[-1].lower() == container.EMPTY:
        return "placeholder"
    if path in named:
        return f"{' and '.join(named[path])} (named by the archive)"
    return "unknown"


def describe_archive(data, path):
    """era, family, key count, fidelity, profile and name of one Brush.archive."""
    out = {"path": path, "bytes": len(data), "sha256": sha256(data)}
    try:
        brush = brush_model.decode(data)
    except CodecError as exc:
        out.update({"error": str(exc)})
        return out, None
    out.update({"name": brush.name, "era": brush.era, "family": brush.family,
                "key_count": brush.key_count, "fidelity": brush.fidelity,
                "profile": brush.profile, "rebuild": brush.rebuild})
    return out, brush


def describe_folder(folder, *, uuid=None, bundled=None, position=None):
    """One brush folder, as inspect shows it."""
    warnings = list(folder.warnings)
    archive, brush = describe_archive(folder.archive, container.ARCHIVE)
    if "error" in archive:
        warnings.append(f"Brush.archive cannot be decoded: {archive['error']}")
    params = brush.params if brush is not None else None
    names = (container.texture_names(params) if params is not None
             else container.archive_texture_names(folder.archive))
    named = {}
    for role, name in names.items():
        if name:
            named.setdefault(name, []).append(role)
    try:
        inputs = container.identity_inputs(folder)
        digest = identity.content_sha256(*inputs)
        brush_id = identity.brush_id_from_sha256(digest)
    except (ContainerError, identity.IdentityError) as exc:
        digest, brush_id = None, None
        warnings.append(f"no identity: {exc}")
    textures = {}
    resolved = container.resolve_textures(folder, params, bundled=bundled)
    for role, (data, source) in resolved.items():
        entry = {"source": source, "bundled_name": names[role]}
        if data is not None:
            member = {"shape": container.SHAPE, "grain": container.GRAIN}[role]
            entry["member"] = (member if member in folder else
                               (names[role] if source == "embedded" else None))
            entry.update({"bytes": len(data), "sha256": sha256(data), "texture_id": identity.texture_id(data)})
            entry.update(_png(data))
        textures[role] = entry
    for role, member in (("shape", container.SHAPE), ("grain", container.GRAIN)):
        if folder.get(member) is not None and names[role]:
            warnings.append(f"info: {member} beside a bundled path ({show(names[role])}); "
                            f"the {member} is what the brush uses")
    members = [{"path": m.path, "bytes": len(m.data), "view": view_of(m.path, named),
                "form": m.form or "other", "sha256": sha256(m.data)}
               for m in folder.members]
    archives = []
    for m in folder.members:
        if m.path != container.ARCHIVE and m.path.rsplit("/", 1)[-1] == container.ARCHIVE:
            described, _ = describe_archive(m.data, m.path)
            archives.append(described)
    reset = folder.reset
    out = {"uuid": uuid, "position": position, "name": brush.name if brush else None,
           "id": brush_id, "content_sha256": digest, **{k: archive.get(k) for k in (
               "era", "family", "key_count", "fidelity", "profile", "rebuild")},
           "export_state": brush_model.export_state(brush) if brush is not None else None,
           "textures": textures, "thumbnail": _png(folder.thumbnail) if folder.thumbnail else None,
           "members": members, "other_archives": archives,
           "reset": None if reset is None else {
               "same_as_live": reset.archive == folder.archive if reset.archive else None},
           "warnings": warnings, "skipped": [list(item) for item in folder.skipped]}
    return out


def describe(found, *, bundled=None):
    containers = []
    for item in found:
        if isinstance(item, container.BrushSet):
            containers.append({
                "kind": "brushset", "origin": item.origin, "name": item.name,
                "plist_keys": list(item.plist_order), "plist_extra": sorted(item.plist_extra),
                "brush_count": len(item.brushes),
                "brushes": [describe_folder(folder, uuid=uuid, bundled=bundled, position=n)
                            for n, (uuid, folder) in enumerate(item.brushes, start=1)],
                "warnings": list(item.warnings), "skipped": [list(s) for s in item.skipped]})
        else:
            containers.append({"kind": "brush", "origin": item.origin, "brush_count": 1,
                               "brushes": [describe_folder(item, bundled=bundled, position=1)],
                               "warnings": [], "skipped": []})
    return containers


def print_brush(brush, total):
    head = f"  brush {brush['position']}/{total}  {quoted(brush['name'] or '')}"
    if brush["uuid"]:
        head += f"  {brush['uuid']}"
    print(head + (f"  {brush['id']}" if brush["id"] else ""))
    if brush["era"]:
        print(f"    era {brush['era']} ({brush['family']}, {brush['key_count']} keys)  fidelity "
              f"{brush['fidelity']}  profile {brush['profile']}  rebuild {brush['rebuild']}")
    for role in ("shape", "grain"):
        texture = brush["textures"][role]
        line = f"    {role:<6} {texture['source']}"
        if texture.get("member"):
            line += f"  {show(texture['member'])}"
        elif texture["bundled_name"]:
            line += f"  {show(texture['bundled_name'])}"
        if texture.get("width"):
            line += f"  {texture['width']}x{texture['height']}  {texture['texture_id']}"
        print(line)
    if brush["thumbnail"]:
        print(f"    thumbnail {brush['thumbnail']['width']}x{brush['thumbnail']['height']}")
    print("    members")
    width = max(len(m["path"]) for m in brush["members"])
    for m in brush["members"]:
        print(f"      {show(m['path']):<{width}}  {m['bytes']:>11,}  {m['form']:<6}  {m['view']}")
    for archive in brush["other_archives"]:
        if "error" in archive:
            print(f"    {archive['path']}: cannot be decoded: {show(archive['error'])}")
        else:
            print(f"    {archive['path']}: era {archive['era']}, fidelity {archive['fidelity']}, "
                  f"profile {archive['profile']}, {quoted(archive['name'])}")
    if brush["reset"] is not None:
        print(f"    reset  same archive as the live brush: "
              f"{'yes' if brush['reset']['same_as_live'] else 'no'}")
    for warning in brush["warnings"]:
        print(f"    warning  {show(warning)}")
    for entry, why in brush["skipped"]:
        print(f"    skipped  {show(entry)}: {show(why)}")


def cmd_inspect(args):
    paths = bc.paths_from_args(args)
    label = args.file
    data, found = read_file(args.file, label)
    if not found:
        raise Refused(f"{show(label)} holds no brushset.plist and no Brush.archive"
                      + "".join(f"\n  skipped {show(w)}: {show(r)}" for w, r in found.skipped))
    containers = describe(found, bundled=bundled_folder(paths))
    if args.json:
        print(json.dumps({"schema": INSPECT_SCHEMA, "file": label, "bytes": len(data),
                          "sha256": sha256(data), "containers": containers,
                          "skipped": [list(s) for s in found.skipped]},
                         ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))
        return bc.EXIT_OK
    print(f"file  {show(label)}  {len(data):,} bytes  sha256 {sha256(data)[:16]}")
    for item in containers:
        if item["kind"] == "brushset":
            extra = f"  plist keys: {', '.join(item['plist_keys'])}"
            print(f"brushset {quoted(item['name'])}  {item['brush_count']} brushes{extra}"
                  + (f"  (in {show(item['origin'])})" if item["origin"] != label else ""))
        else:
            print("brush" + (f"  (in {show(item['origin'])})" if item["origin"] != label else ""))
        for warning in item["warnings"]:
            print(f"  warning  {show(warning)}")
        for entry, why in item["skipped"]:
            print(f"  skipped  {show(entry)}: {show(why)}")
        for brush in item["brushes"]:
            print_brush(brush, item["brush_count"])
    for where, why in found.skipped:
        print(f"skipped  {show(where)}: {show(why)}")
    return bc.EXIT_OK


# ── finding a library brush by id ────────────────────────────────────────────

def library_files(library):
    """(POSIX path under the library, path) of every container file, sorted."""
    found = []
    for half in LIBRARY_HALVES:
        root = library / half
        if not root.is_dir():
            continue
        for folder, folders, names in os.walk(root):
            folders[:] = sorted(name for name in folders if name.lower() not in SKIPPED_FOLDERS)
            for name in names:
                if name.lower().endswith((".brush", ".brushset")) and not name.endswith(PART_SUFFIX):
                    path = Path(folder) / name
                    found.append((path.relative_to(library).as_posix(), path))
    return sorted(found, key=lambda item: (item[0].lower(), item[0]))


def find_brush(brush_id, paths):
    """(label, BrushFolder, folder name or None, set or None) of the first
    place the library holds this brush."""
    library = paths.library
    if not library.is_dir():
        raise Usage(f"the library folder {library} is not there (give --library or --root)")
    for relative, path in library_files(library):
        _, found = read_file(path, relative)
        for item in found:
            pairs = (item.brushes if isinstance(item, container.BrushSet) else [(None, item)])
            for uuid, folder in pairs:
                try:
                    digest = identity.content_sha256(*container.identity_inputs(folder))
                except (ContainerError, identity.IdentityError):
                    continue
                if identity.brush_id_from_sha256(digest) == brush_id:
                    where = item.origin + (f" :: {uuid}" if uuid else "")
                    return where, folder, uuid, item if uuid else None
    raise Refused(f"no brush {brush_id} in the library ({library})")


# ── export ───────────────────────────────────────────────────────────────────

def parse_changes(items):
    changes = {}

    def no_constant(name):
        raise ValueError(name)

    for text in items:
        key, sep, raw = text.partition("=")
        key = key.strip()
        if not sep or not key:
            raise Usage(f"--change takes key=value, not {show(text)!r}")
        if key in changes:
            raise Usage(f"--change names {show(key)} twice")
        try:
            changes[key] = json.loads(raw, parse_constant=no_constant)
        except ValueError:
            changes[key] = raw
    return changes


def pick(brush_set, selector):
    """One (uuid, folder) of a set: by folder name, 1-based position or exact name."""
    for uuid, folder in brush_set.brushes:
        if uuid == selector:
            return uuid, folder
    if selector.isdigit() and 1 <= int(selector) <= len(brush_set.brushes):
        return brush_set.brushes[int(selector) - 1]
    named = []
    for uuid, folder in brush_set.brushes:
        try:
            if brush_model.decode(folder.archive).name == selector:
                named.append((uuid, folder))
        except CodecError:
            continue
    if len(named) == 1:
        return named[0]
    if named:
        raise Usage(f"{len(named)} brushes of the set are called {quoted(selector)}: give the "
                    "folder name or the position")
    raise Usage(f"no brush of the set is {quoted(selector)} (a folder name, a position from 1 to "
                f"{len(brush_set.brushes)}, or an exact name)")


def source_of(args, paths):
    """(label, what): what is ("brush", folder, uuid) or ("set", BrushSet)."""
    if identity.is_brush_id(args.source):
        if args.brush:
            raise Usage("--brush picks a brush of a file; a brush id already names one")
        label, folder, uuid, _ = find_brush(args.source, paths)
        return label, ("brush", folder, uuid)
    _, found = read_file(args.source, args.source)
    if len(found) != 1:
        held = ", ".join(show(item.origin) for item in found) or "nothing"
        raise Usage(f"{show(args.source)} holds {len(found)} sets and brushes ({held}); export "
                    "reads a file that is one brush or one set")
    item = found[0]
    if isinstance(item, container.BrushFolder):
        if args.brush:
            raise Usage("--brush picks a brush of a set; this file is one brush")
        return args.source, ("brush", item, None)
    if args.brush:
        uuid, folder = pick(item, args.brush)
        return f"{args.source} :: {uuid}", ("brush", folder, uuid)
    if len(item.brushes) == 1:
        uuid, folder = item.brushes[0]
        return f"{args.source} :: {uuid}", ("brush", folder, uuid)
    return args.source, ("set", item)


def export_brush(folder, changes):
    """(out folder, record, plan, warnings) for one brush and its changes."""
    try:
        base = brush_model.decode(folder.archive)
    except CodecError as exc:
        raise Refused(f"the brush's archive cannot be decoded: {show(exc)}") from None
    record = {"name": base.name, "era": base.era, "applied": {}, "rejected": [], "warnings": []}
    out = folder.copy()
    patched = base
    if changes:
        patched, report = brush_model.apply_patch(base, changes, mode="strict")
        record.update({"applied": report["applied"], "rejected": report["rejected"],
                       "warnings": list(report["warnings"]), "unchanged": report["unchanged"]})
        if not report["ok"]:
            return None, record, None, []
    modified = brush_model.is_modified(patched)
    data = brush_model.encode(patched)
    if not modified and data != folder.archive:
        raise Refused("an unchanged archive did not export as its source bytes")
    record["name"] = patched.name
    record["state"] = brush_model.export_state(patched)
    record["modified"] = modified
    warnings = []
    if modified:
        out.set(container.ARCHIVE, data)
        if folder.thumbnail is not None:
            record["warnings"].append({"key": container.THUMBNAIL, "code": "stale_thumbnail"})
            warnings.append(f"stale_thumbnail: {container.THUMBNAIL} is the one drawn before the change")
    if folder.reset is not None:
        warnings.append("Reset/ is kept verbatim")
    plan = container.member_plan(folder, out, reencoded={container.ARCHIVE})
    return out, record, plan, warnings


def protected(target, paths):
    """The folder an --out inside which is refused, or None."""
    target = target.resolve()
    for name, root in (("the brushes tool", bc.TOOL_ROOT), ("the library", paths.library),
                       ("the catalog", paths.catalog), ("the vault", paths.vault)):
        root = Path(root).resolve()
        if target == root or root in target.parents:
            return name, root
    return None


def write_export(out_dir, filename, data):
    """Put an export on disk: `<out_dir>/<filename>`, never over an existing
    file. Written through `<name>.tmp`, then linked into place (an atomic
    no-clobber), or moved where links are not supported."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / filename
    tmp = out_dir / (filename + ".tmp")
    if target.exists():
        raise Refused(f"{target} is already there; nothing was written")
    try:
        with open(tmp, "xb") as handle:
            handle.write(data)
    except FileExistsError:
        raise Refused(f"{tmp} is in the way; nothing was written") from None
    try:
        try:
            os.link(tmp, target)
        except FileExistsError:
            raise Refused(f"{target} is already there; nothing was written") from None
        except OSError:
            if target.exists():
                raise Refused(f"{target} is already there; nothing was written") from None
            os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def cmd_export(args):
    paths = bc.paths_from_args(args)
    changes = parse_changes(args.change)
    if args.confirm and not args.out:
        raise Usage("--confirm needs --out DIR: the folder the export is written to")
    if args.out:
        guarded = protected(Path(args.out), paths)
        if guarded:
            raise Usage(f"--out may not lie inside {guarded[0]} ({guarded[1]})")
    if args.set is not None and not args.set.strip():
        raise Usage("--set needs a name")
    label, source = source_of(args, paths)
    brushes, members, warnings = [], [], []
    if source[0] == "set":
        if changes:
            raise Usage(f"{show(label)} is a set of {len(source[1].brushes)} brushes: give --brush "
                        "to say which one --change applies to")
        brush_set = source[1]
        out_set = container.BrushSet(
            args.set if args.set is not None else brush_set.name,
            [(uuid, folder.copy()) for uuid, folder in brush_set.brushes], list(brush_set.entry_order),
            brush_set.origin, dict(brush_set.plist_extra), brush_set.plist_order,
            brush_set.plist_source, brush_set.plist_date, brush_set.plist_form,
            plist_read=brush_set.plist_read)
        for uuid, folder in out_set.brushes:
            plan = container.member_plan(folder, folder)
            members += [dict(m, path=f"{uuid}/{m['path']}") for m in plan]
            try:
                described = brush_model.decode(folder.archive)
                brushes.append({"name": described.name, "uuid": uuid, "era": described.era,
                                "applied": {}, "rejected": [], "warnings": [], "state": "source"})
            except CodecError as exc:
                raise Refused(f"{uuid}: the archive cannot be decoded: {show(exc)}") from None
            if folder.reset is not None:
                warnings.append(f"{uuid}: Reset/ is kept verbatim")
        data = container.write_brushset(out_set)
        plist = container.plist_bytes(out_set)
        members.append({"path": container.SET_PLIST, "size": len(plist),
                        "state": "verbatim" if plist == brush_set.plist_source else "re-encoded"})
        filename = container.safe_filename(out_set.name) + ".brushset"
    else:
        _, folder, uuid = source
        out, record, plan, notes = export_brush(folder, changes)
        if out is None:
            for item in record["rejected"]:
                print(f"rejected  {show(item['key'])}: {item['code']}: {show(item['reason'])}")
            raise Refused("the changes were not applied; nothing was written")
        # A folder name exists only inside a set: a `.brush` holds its members at its root.
        new_uuid = None
        if args.set is not None:
            new_uuid = uuid if (uuid and not record["modified"]) else container.new_uuid()
        record["uuid"] = new_uuid
        brushes.append(record)
        warnings += notes
        if args.set is not None:
            out_set = container.BrushSet(args.set, [(new_uuid, out)])
            data = container.write_brushset(out_set)
            members = [dict(m, path=f"{new_uuid}/{m['path']}") for m in plan]
            plist = container.plist_bytes(out_set)
            members.append({"path": container.SET_PLIST, "size": len(plist), "state": "re-encoded"})
            filename = container.safe_filename(args.set) + ".brushset"
        else:
            data = container.write_brush(out)
            members = plan
            filename = container.safe_filename(record["name"]) + ".brush"
    result = {"filename": filename, "size": len(data), "sha256": sha256(data),
              "members": members, "brushes": brushes, "warnings": warnings, "source": label,
              "dry_run": not args.confirm, "written": None}
    if args.json:
        # stdout stays one JSON object: the file is written first, so that the
        # object can say where; the dry-run line goes to stderr.
        if args.confirm:
            result["written"] = str(write_export(args.out, filename, data))
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))
        if not args.confirm:
            print(DRY_RUN_LINE, file=sys.stderr)
        return bc.EXIT_OK
    else:
        print(f"from     {show(label)}")
        print(f"export   {filename}  {len(data):,} bytes  sha256 {result['sha256'][:16]}"
              + (f"  ->  {args.out}" if args.out else ""))
        for brush in brushes:
            folder = f"  {brush['uuid']}" if brush["uuid"] else ""
            print(f"brush    {quoted(brush['name'])}{folder}  era {brush['era']}  "
                  f"archive {brush['state']}")
            for key, value in brush["applied"].items():
                shown = (brush_model.real_text(value) if isinstance(value, float)
                         else json.dumps(value, ensure_ascii=False))
                print(f"  applied  {show(key)} = {show(shown)}")
            for key in brush.get("unchanged", []):
                print(f"  unchanged  {show(key)} (already that value)")
            for warning in brush["warnings"]:
                if warning["code"] != "stale_thumbnail":
                    print(f"  warning  {show(warning['key'])}: {warning['code']}")
        print("members")
        width = max(len(m["path"]) for m in members)
        for m in members:
            print(f"  {m['state']:<10}  {show(m['path']):<{width}}  {m['size']:>11,}")
        for warning in warnings:
            print(f"warning  {show(warning)}")
    if not args.confirm:
        print(DRY_RUN_LINE)
        return bc.EXIT_OK
    target = write_export(args.out, filename, data)
    print(f"wrote    {target}  {len(data):,} bytes")
    return bc.EXIT_OK


# ── roundtrip ────────────────────────────────────────────────────────────────

def discover(target):
    """(label, path) of every file roundtrip reads under a folder, sorted."""
    found = []
    for folder, folders, names in os.walk(target):
        folders[:] = sorted(name for name in folders if name.lower() not in SKIPPED_FOLDERS)
        for name in names:
            low = name.lower()
            if low.endswith(FILE_SUFFIXES) and not low.endswith(PART_SUFFIX):
                path = Path(folder) / name
                found.append((path.relative_to(target).as_posix(), path))
    return sorted(found, key=lambda item: (item[0].lower(), item[0]))


def check_archive(data):
    """(fidelity, problem): problem is None when the archive is as it must be."""
    try:
        brush = brush_model.decode(data)
    except CodecError as exc:
        return None, f"cannot be decoded: {exc}"
    if brush_model.encode(brush) != data:
        return brush.fidelity, "an unchanged export is not the source bytes"
    if brush.fidelity == "byte":
        if keyed_archive.rule_encode(brush.archive, brush.archive.profile) != data:
            return "byte", "decoded as byte, but the rules write other bytes"
        return "byte", None
    why = ("no profile reproduces the file" if brush.archive.fidelity != "byte"
           else f"the schema rebuild is {brush.rebuild}")
    return "table", why


def source_listing(data, prefix):
    """The source's entries as zipfile reads them, independently of container:
    files only, the first of each name, no junk, below `prefix`."""
    out, seen = [], set()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            name = info.orig_filename
            if name.endswith("/") or name in seen or container.is_junk(name):
                continue
            seen.add(name)
            if name.startswith(prefix):
                out.append((name[len(prefix):], archive.read(info)))
    return out


def rebuilt_listing(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.orig_filename, archive.read(info)) for info in archive.infolist()]


def roundtrip_container(item, source, allow_table, tables):
    """(counts, problems) of one set or loose brush. `source` is the
    container's own bytes when it is the file itself, else None."""
    counts = {"brushes": 0, "archives": 0, "byte": 0, "table": 0, "members": 0, "identical": 0}
    problems = []
    pairs = item.brushes if isinstance(item, container.BrushSet) else [(None, item)]
    for uuid, folder in pairs:
        counts["brushes"] += 1
        for member in folder.members:
            if member.path.rsplit("/", 1)[-1] != container.ARCHIVE:
                continue
            where = f"{uuid}/{member.path}" if uuid else member.path
            counts["archives"] += 1
            fidelity, problem = check_archive(member.data)
            if fidelity in ("byte", "table"):
                counts[fidelity] += 1
            if problem and fidelity == "table" and problem.startswith(("no profile", "the schema")):
                tables.append((item.origin, where, problem))
                if not allow_table:
                    problems.append(f"{where}: fidelity table ({problem})")
            elif problem:
                problems.append(f"{where}: {problem}")
    if isinstance(item, container.BrushSet):
        rebuilt = container.write_brushset(item, preserve_order=True, source_dates=True)
        expected = []
        members = {(uuid, m.path): m.data for uuid, folder in item.brushes for m in folder.members}
        for name in item.entry_order:
            if name == container.SET_PLIST:
                expected.append((name, item.plist_source))
            else:
                uuid, _, path = name.partition("/")
                if (uuid, path) in members:
                    expected.append((name, members[(uuid, path)]))
    else:
        rebuilt = container.write_brush(item, preserve_order=True, source_dates=True)
        expected = item.pairs()
    back = rebuilt_listing(rebuilt)
    counts["members"] = len(back)
    if back != expected:
        problems.append("the rebuilt container does not read back as its members")
    if source is not None:
        listing = source_listing(source, getattr(item, "prefix", ""))
        if back != listing:
            lost = len(listing) - len(back)
            problems.append(f"the rebuilt container differs from the source's entries "
                            f"({len(listing)} in the source, {len(back)} rebuilt"
                            + (f"; {lost} not carried" if lost > 0 else "") + ")")
        counts["identical"] = int(rebuilt == source)
    return counts, problems, rebuilt == source if source is not None else None


def roundtrip_file(label, path, allow_table, tables):
    """(status, line, counts) for one file: status ok, FAIL, LFS or none."""
    counts = {"brushes": 0, "archives": 0, "byte": 0, "table": 0, "members": 0, "identical": 0,
              "sets": 0, "loose": 0}
    try:
        data = container.read_path(path)
        found = container.read_any(data, label)
    except ContainerError as exc:
        if exc.code == "lfs_pointer":
            return "LFS", f"{show(label)}: a Git LFS pointer, not a brush file: run git lfs pull", counts
        return "FAIL", f"{show(label)}: cannot be read: {show(exc)}", counts
    except OSError as exc:
        return "FAIL", f"{show(label)}: cannot be read ({type(exc).__name__})", counts
    if not found:
        if label.lower().endswith((".brush", ".brushset")):
            return "FAIL", f"{show(label)}: holds no brushset.plist and no Brush.archive", counts
        return "none", f"{show(label)}: holds no brush file", counts
    problems = [f"{where}: not read: {why}" for where, why in found.skipped]
    zips = []
    for item in found:
        source = data if (len(found) == 1 and item.origin == label) else None
        try:
            got, issues, same = roundtrip_container(item, source, allow_table, tables)
        except CodecError as exc:
            problems.append(f"{show(item.origin)}: {show(exc)}")
            continue
        for key, value in got.items():
            counts[key] += value
        counts["sets" if isinstance(item, container.BrushSet) else "loose"] += 1
        problems += [f"{show(item.origin)}: {issue}" if item.origin != label else issue
                     for issue in issues]
        if same is not None:
            zips.append("zip identical" if same else "zip differs")
        for warning in getattr(item, "warnings", []):
            if "dropped; the first wins" in warning:
                zips.append(show(warning.split(":", 1)[0]))
    kind = (f"{counts['sets']} set{'s' if counts['sets'] != 1 else ''}" if counts["sets"]
            else "") + (", " if counts["sets"] and counts["loose"] else "") + (
        f"{counts['loose']} loose" if counts["loose"] else "")
    summary = (f"{show(label)}  {kind}  {counts['brushes']} brushes  {counts['archives']} archives "
               f"({counts['byte']} byte, {counts['table']} table)  {counts['members']} members"
               + (f"  {'; '.join(zips)}" if zips else ""))
    if problems:
        return "FAIL", summary + "".join(f"\n        {show(problem)}" for problem in problems), counts
    return "ok", summary, counts


def cmd_roundtrip(args):
    target = Path(args.path)
    if target.is_file():
        files = [(args.path, target)]
    elif target.is_dir():
        files = discover(target)
    else:
        raise Usage(f"{show(args.path)} is neither a file nor a folder")
    totals = {"files": 0, "ok": 0, "FAIL": 0, "LFS": 0, "none": 0, "brushes": 0, "archives": 0,
              "byte": 0, "table": 0, "members": 0, "identical": 0, "sets": 0, "loose": 0}
    tables = []
    for label, path in files:
        status, line, counts = roundtrip_file(label, path, args.allow_table, tables)
        print(f"{status:<5} {line}")
        totals["files"] += 1
        totals[status] += 1
        for key, value in counts.items():
            totals[key] += value
    for origin, where, why in tables:
        print(f"table {show(origin)} :: {show(where)}: {show(why)}")
    print(f"total {totals['files']:,} files ({totals['sets']:,} sets, {totals['loose']:,} loose "
          f"brushes): {totals['brushes']:,} brushes, {totals['archives']:,} archives "
          f"({totals['byte']:,} byte, {totals['table']:,} table), {totals['members']:,} members; "
          f"{totals['identical']:,} zips identical to their source; {totals['ok']:,} ok, "
          f"{totals['FAIL']:,} failed" + (f", {totals['LFS']:,} Git LFS pointers" if totals["LFS"] else "")
          + (f", {totals['none']:,} with no brush" if totals["none"] else ""))
    if totals["LFS"]:
        return bc.EXIT_USAGE
    if totals["FAIL"] or not totals["files"]:
        return bc.EXIT_REFUSED
    return bc.EXIT_OK


# ── the command line ─────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="brush_file.py",
        description="Inspect a brush file, export a brush from one, or prove a file comes back "
                    "byte for byte. Run it with `python -I`.")
    verbs = parser.add_subparsers(dest="verb", required=True, metavar="VERB")
    inspect = verbs.add_parser("inspect", help="members, era, fidelity, textures and warnings")
    inspect.add_argument("file", help="a .brush, .brushset or a zip that holds them")
    inspect.add_argument("--json", action="store_true", help="print one JSON object")
    bc.add_path_arguments(inspect, ("root", "library"))
    export = verbs.add_parser("export", help="write a brush or a set as a new file (dry run "
                                             "without --confirm)")
    export.add_argument("--from", dest="source", required=True, metavar="ID|FILE",
                        help="a library brush id (b_ and 12 hex) or a brush file")
    export.add_argument("--brush", metavar="SEL",
                        help="one brush of a set: its folder name, its position from 1, or its name")
    export.add_argument("--set", metavar="NAME", help="write a .brushset of this name")
    export.add_argument("--change", action="append", default=[], metavar="KEY=VALUE",
                        help="change one archive key (repeatable); the value is JSON, or text")
    export.add_argument("--out", metavar="DIR", help="the folder the export is written to")
    export.add_argument("--json", action="store_true", help="print the plan as JSON")
    export.add_argument("--confirm", action="store_true", help="write the file")
    bc.add_path_arguments(export, ("root", "library", "catalog", "vault"))
    roundtrip = verbs.add_parser("roundtrip", help="decode, re-encode and rebuild every "
                                                   "container; exit 1 on any mismatch")
    roundtrip.add_argument("path", help="a brush file, or a folder to search")
    roundtrip.add_argument("--allow-table", action="store_true",
                           help="list archives of fidelity table without failing")
    return parser


VERBS = {"inspect": cmd_inspect, "export": cmd_export, "roundtrip": cmd_roundtrip}


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    try:
        return VERBS[args.verb](args)
    except (Usage, Refused) as exc:
        print(f"brush_file.py {args.verb}: {exc}", file=sys.stderr)
        return exc.exit_code
    except CodecError as exc:
        print(f"brush_file.py {args.verb}: {show(exc)}", file=sys.stderr)
        return bc.EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
