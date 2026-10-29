"""Pack a brush bundle into a Procreate .brush or .brushset. Standard library only.

    python studio/pipeline/brush_pack.py pack    <bundle> [--out DIR]
    python studio/pipeline/brush_pack.py set     <bundle>... --name <set name> [--out DIR]
    python studio/pipeline/brush_pack.py inspect <file.brush | file.brushset | bundle>
    python studio/pipeline/brush_pack.py compare <a.brush> <b.brush>

A bundle is what the brush designer exports: a zip, or a folder, holding

    brush.json       the brush: name, author, notes, identifier, version, the
                     43 tunables, the generator names, and the two pressure
                     curves as base64 (see BUNDLE_SCHEMA)
    Shape.png        the tip, 512 x 512 greyscale
    Grain.png        the grain, 1024 x 1024 greyscale
    Thumbnail.png    optional, 256 x 256; Shape.png stands in when missing

`pack` writes <name>.brush: a zip of Brush.archive (an NSKeyedArchiver
binary plist of an MCBrush, written with plistlib so its object table and
UIDs are right), Shape.png, Grain.png and QuickLook/Thumbnail.png. `set`
writes a .brushset holding one folder per brush plus brushset.plist.

Whether Procreate accepts the result is settled only by importing one. The
archive's shape follows what the Creative-Headquarters designer built, whose
own bplist encoder was wrong by construction and was never confirmed to
import. `inspect` decodes a file so it can be compared with a brush Procreate
itself wrote; `compare` lists the keys and types that differ.

Exit codes: 0 done, 1 refused, 2 usage error.
"""

import argparse
import base64
import io
import json
import plistlib
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

BUNDLE_SCHEMA = "rosw/brush-bundle/v1"

# The 43 tunables Brush.archive carries, and the type each is written as.
# From the designer's BrushState (33 numeric, 9 boolean, one blend-mode enum).
FLOATS = (
    "brushSpacing", "brushSpacingJitter", "brushStreamline", "brushStreamlinePressure",
    "brushStabilization", "brushMotionFiltering", "brushJitterX", "brushJitterY", "brushFallOff",
    "brushShapeScatter", "brushShapeRotation", "brushShapeCountJitter",
    "brushGrainScale", "brushGrainRotation", "brushGrainDepth", "brushGrainDepthMin",
    "brushGrainDepthJitter", "brushGrainOffsetJitter",
    "brushSizeMaximum", "brushSizeMinimum", "brushOpacityMaximum", "brushOpacityMinimum",
    "brushBleedAmount",
    "brushTaperSizeStart", "brushTaperSizeEnd", "brushTaperTip", "brushTaperOpacity",
    "brushWetDilution", "brushWetCharge", "brushWetPull", "brushWetAttack", "brushWetBleed",
)
INTS = ("brushShapeCount", "brushBlendingMode")
BOOLS = (
    "brushShapeRandomized", "brushAzimuth", "brushFlipX", "brushFlipY",
    "brushGrainMoving", "brushGrainZoom", "brushTaperLinked", "brushWetEdge", "brushWetBurn",
)
TUNABLES = FLOATS + INTS + BOOLS
CURVES = ("brushPressureSizeResponse", "brushPressureOpacityResponse")
TEXT = {"name": "brushName", "authorName": "brushAuthorName", "notes": "brushNotes"}
BLENDING_MODES = 16
IMAGES = ("Shape.png", "Grain.png")
THUMBNAIL = "Thumbnail.png"


class Refused(Exception):
    pass


class Usage(Exception):
    pass


# ── reading a bundle ─────────────────────────────────────────────────────────

def read_bundle(path):
    """{"brush": dict, "files": {name: bytes}} from a zip or a folder."""
    path = Path(path)
    files = {}
    if path.is_dir():
        for name in IMAGES + (THUMBNAIL, "brush.json"):
            if (path / name).is_file():
                files[name] = (path / name).read_bytes()
    elif path.is_file():
        try:
            with zipfile.ZipFile(path) as bundle:
                for info in bundle.infolist():
                    name = Path(info.filename).name
                    if name in IMAGES + (THUMBNAIL, "brush.json"):
                        files[name] = bundle.read(info)
        except zipfile.BadZipFile:
            raise Usage(f"{path} is neither a folder nor a zip")
    else:
        raise Usage(f"no bundle at {path}")
    if "brush.json" not in files:
        raise Refused(f"{path} has no brush.json")
    for name in IMAGES:
        if name not in files:
            raise Refused(f"{path} has no {name}")
        if files[name][:8] != b"\x89PNG\r\n\x1a\n":
            raise Refused(f"{name} in {path} is not a PNG")
    try:
        brush = json.loads(files.pop("brush.json").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise Refused(f"brush.json in {path} does not parse: {err}")
    if not isinstance(brush, dict):
        raise Refused("brush.json is a JSON object")
    return {"brush": brush, "files": files}


def typed_brush(brush):
    """The brush as the archive writes it: every tunable present and typed,
    the text fields as strings, the curves as bytes or absent. A value with
    the wrong type is refused rather than coerced silently."""
    source = dict(brush.get("parameters") or {})
    for key in TUNABLES + CURVES:
        if key in brush and key not in source:
            source[key] = brush[key]
    out = {}
    missing = [key for key in TUNABLES if key not in source]
    if missing:
        raise Refused(f"brush.json lacks {len(missing)} tunable(s): {', '.join(missing[:6])}"
                      + (" …" if len(missing) > 6 else ""))
    for key in FLOATS:
        value = source[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Refused(f"{key} is a number, not {value!r}")
        out[key] = float(value)
    for key in INTS:
        value = source[key]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Refused(f"{key} is an integer, not {value!r}")
        out[key] = value
    if not 0 <= out["brushBlendingMode"] < BLENDING_MODES:
        raise Refused(f"brushBlendingMode is 0 to {BLENDING_MODES - 1}, not {out['brushBlendingMode']}")
    if out["brushShapeCount"] < 1:
        raise Refused("brushShapeCount is at least 1")
    for key in BOOLS:
        value = source[key]
        if not isinstance(value, bool):
            raise Refused(f"{key} is true or false, not {value!r}")
        out[key] = value
    for field, archived in TEXT.items():
        value = brush.get(field, "")
        if value is not None and not isinstance(value, str):
            raise Refused(f"{field} is text")
        out[archived] = value or ""
    if not out["brushName"].strip():
        raise Refused("the brush has no name")
    identifier = str(brush.get("identifier") or "").strip()
    out["brushIdentifier"] = identifier if UUID_RE.fullmatch(identifier) else str(uuid.uuid4()).upper()
    version = brush.get("version", 1)
    if isinstance(version, bool) or not isinstance(version, int):
        raise Refused("version is an integer")
    out["brushVersion"] = version
    curves = brush.get("curves") or {}
    for key in CURVES:
        value = curves.get(key, source.get(key))
        if value in (None, ""):
            continue
        try:
            out[key] = base64.b64decode(value, validate=True) if isinstance(value, str) else bytes(value)
        except (ValueError, TypeError):
            raise Refused(f"{key} is base64")
    return out


UUID_RE = re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")


# ── the archive ──────────────────────────────────────────────────────────────

def keyed_archive(brush):
    """The NSKeyedArchiver form of an MCBrush: $objects[0] is $null, [1] the
    brush, [2] its class. Strings and data are their own objects, referenced
    by UID, as NSKeyedArchiver writes them; numbers and booleans sit inline."""
    objects = ["$null"]
    entry = {}
    objects.append(entry)
    class_uid = plistlib.UID(len(objects))
    objects.append({"$classname": "MCBrush", "$classes": ["MCBrush", "NSObject"]})
    entry["$class"] = class_uid
    for key in sorted(brush):
        value = brush[key]
        if isinstance(value, (str, bytes)):
            objects.append(value)
            entry[key] = plistlib.UID(len(objects) - 1)
        else:
            entry[key] = value
    return {"$version": 100000, "$archiver": "NSKeyedArchiver",
            "$top": {"root": plistlib.UID(1)}, "$objects": objects}


def archive_bytes(brush):
    return plistlib.dumps(keyed_archive(brush), fmt=plistlib.FMT_BINARY)


def unarchive(data):
    """The brush dict back out of a keyed archive, UIDs resolved. Used by
    inspect and the tests."""
    plist = plistlib.loads(data)
    objects = plist["$objects"]

    def resolve(value):
        if isinstance(value, plistlib.UID):
            return resolve(objects[value.data])
        if isinstance(value, dict):
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        return value

    root = resolve(plist["$top"]["root"])
    return root


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "brush"


# ── writing files ────────────────────────────────────────────────────────────

def write_brush_entries(zf, brush, files, prefix=""):
    zf.writestr(zipfile.ZipInfo(prefix + "Brush.archive"), archive_bytes(brush), zipfile.ZIP_DEFLATED)
    for name in IMAGES:
        zf.writestr(zipfile.ZipInfo(prefix + name), files[name], zipfile.ZIP_STORED)
    thumbnail = files.get(THUMBNAIL) or files["Shape.png"]
    zf.writestr(zipfile.ZipInfo(prefix + "QuickLook/Thumbnail.png"), thumbnail, zipfile.ZIP_STORED)


def pack(bundle_path, out_dir):
    bundle = read_bundle(bundle_path)
    brush = typed_brush(bundle["brush"])
    out = Path(out_dir) / f"{safe_name(brush['brushName'])}.brush"
    out.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        write_brush_entries(zf, brush, bundle["files"])
    out.write_bytes(buffer.getvalue())
    return out, brush


def pack_set(bundle_paths, set_name, out_dir):
    set_name = " ".join(set_name.split())
    if not set_name:
        raise Usage("--name is empty")
    brushes = []
    for path in bundle_paths:
        bundle = read_bundle(path)
        brushes.append((typed_brush(bundle["brush"]), bundle["files"]))
    identifiers = [brush["brushIdentifier"] for brush, _ in brushes]
    if len(set(identifiers)) != len(identifiers):
        raise Refused("two brushes in the set share an identifier. Give each its own.")
    out = Path(out_dir) / f"{safe_name(set_name)}.brushset"
    out.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for brush, files in brushes:
            write_brush_entries(zf, brush, files, prefix=brush["brushIdentifier"] + "/")
        manifest = {"name": set_name, "brushes": identifiers}
        zf.writestr(zipfile.ZipInfo("brushset.plist"),
                    plistlib.dumps(manifest, fmt=plistlib.FMT_BINARY), zipfile.ZIP_DEFLATED)
    out.write_bytes(buffer.getvalue())
    return out, brushes


# ── reading files back ───────────────────────────────────────────────────────

def inspect(path):
    """What a .brush, a .brushset or a bundle holds, as a JSON-able dict."""
    path = Path(path)
    if path.is_dir() or path.suffix == ".zip":
        bundle = read_bundle(path)
        return {"kind": "bundle", "brush": describe(typed_brush(bundle["brush"])),
                "files": sorted(bundle["files"])}
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError):
        raise Usage(f"{path} is not a zip")
    with zf:
        names = sorted(zf.namelist())
        archives = [n for n in names if n.endswith("Brush.archive")]
        found = {"kind": "brushset" if "brushset.plist" in names else "brush", "files": names, "brushes": {}}
        if "brushset.plist" in names:
            found["manifest"] = plistlib.loads(zf.read("brushset.plist"))
        for name in archives:
            found["brushes"][name] = describe(unarchive(zf.read(name)))
        return found


def describe(brush):
    """A brush with bytes shown as their length, for printing."""
    return {key: (f"<{len(value)} bytes>" if isinstance(value, bytes) else value)
            for key, value in brush.items()}


def compare(a, b):
    """Keys and types that differ between the first archive of two files."""
    def first(path):
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith("Brush.archive")]
            if not names:
                raise Refused(f"{path} holds no Brush.archive")
            return unarchive(zf.read(names[0]))
    left, right = first(a), first(b)
    lines = []
    for key in sorted(set(left) | set(right)):
        if key not in left:
            lines.append(f"only in {Path(b).name}: {key} ({type(right[key]).__name__})")
        elif key not in right:
            lines.append(f"only in {Path(a).name}: {key} ({type(left[key]).__name__})")
        elif type(left[key]) is not type(right[key]):
            lines.append(f"{key}: {type(left[key]).__name__} in {Path(a).name}, "
                         f"{type(right[key]).__name__} in {Path(b).name}")
    return lines


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_pack(args):
    out, brush = pack(args.bundle, args.out)
    print(f"wrote     {out}")
    print(f"brush     {brush['brushName']} · {brush['brushIdentifier']}")
    return 0


def cmd_set(args):
    out, brushes = pack_set(args.bundles, args.name, args.out)
    print(f"wrote     {out}")
    for brush, _ in brushes:
        print(f"brush     {brush['brushName']} · {brush['brushIdentifier']}")
    return 0


def cmd_inspect(args):
    print(json.dumps(inspect(args.path), indent=2, ensure_ascii=False, default=str))
    return 0


def cmd_compare(args):
    lines = compare(args.a, args.b)
    print("\n".join(lines) if lines else "same keys, same types")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="brush_pack.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("pack", help="a bundle -> <name>.brush")
    p.add_argument("bundle")
    p.add_argument("--out", default=".")
    p = sub.add_parser("set", help="bundles -> <name>.brushset")
    p.add_argument("bundles", nargs="+")
    p.add_argument("--name", required=True)
    p.add_argument("--out", default=".")
    p = sub.add_parser("inspect", help="decode a .brush, .brushset or bundle")
    p.add_argument("path")
    p = sub.add_parser("compare", help="keys and types that differ between two .brush files")
    p.add_argument("a")
    p.add_argument("b")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return {"pack": cmd_pack, "set": cmd_set, "inspect": cmd_inspect, "compare": cmd_compare}[args.command](args)
    except Refused as problem:
        print(f"refused   {problem}", file=sys.stderr)
        return 1
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
