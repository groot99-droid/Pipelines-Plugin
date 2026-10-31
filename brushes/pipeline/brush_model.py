"""The brush model: a `Brush.archive` as plain parameters, and back.

    brush = brush_model.decode(data)                 # bytes -> Brush
    brush.params["plotSpacing"]                      # one JSON value per root key
    patched, report = brush_model.apply_patch(brush, {"plotSpacing": 0.25})
    data = brush_model.encode(patched)               # unchanged -> the source bytes

This is the top of the file codec (docs/CONTRACTS.md, F3 and F4). bplist.py
reads and writes the property list, keyed_archive.py the numbered graph inside
it, and this module the brush: which keys a brush holds, of what type, in
which of the app's generations (its era), and how a change to one of them is
checked and written.

The schema. Everything this module knows about a key, an era or a class comes
from `schema/silica_keys.json`, the folder beside this code (never under a data
root): each key's type and limits, each era's exact key list and key order,
each class's chain and field order, and the order in which the app archives
the root's children. `load_schema()` reads it once.

Parameters. `Brush.params` maps every root key but `$class` to a JSON value,
in root key order. The forms are the ones of F3:

    real                a number (the 32-bit float, widened)
    int, bool           a number, true / false
    string              text, or None for nil; {"string", "wrapper"} when the
                        file wraps it in an NSMutableString
    data                {"$data": hex}
    curve               {"points": ["{0.000000, 0.000000}", ...]} and, in a
                        legacy archive, "resolution": 1024
    roll parameters     {"mode", "activationFalloff", "activationOrigin",
                         "activationRange"}
    array               a list of numbers
    date                {"time": seconds since 2001-01-01, 64-bit}
    another class       {"$class", "$classes", "$fields": [[key, value], ...]}

and three typed tags for a number whose plain form would not say what it is:

    {"$real32": x}   {"$real64": x}   {"$int": n}

A tag is used for a scalar under a key the schema does not know, for a scalar
that is not of its key's schema type, and for a real no JSON number carries:
negative zero and the non-finite values, whose `x` is then the stored bytes in
hex ("80000000" is the 32-bit negative zero). Inside `$fields`, text held in
place is {"$inline": text}, a list held in place {"$list": [...]}, and a
reference to a bare number {"$ref": tag}. A value with no form at all is
{"$opaque": why}: it cannot be built from JSON, and is written back from the
decoded archive.

Two ways to write an archive, and which is used when:

    unchanged      `encode` returns the source bytes.
    changed        the decoded graph is kept; only the root keys whose values
                   changed get new entries, and the graph is numbered again in
                   the app's order. Whatever this module does not understand
                   is written back as it was read.
    no archive     a brush made by `from_json` is built from its parameters
                   and the schema alone: classes, field orders, the encode
                   order, the key order and the types.

`from_archive` runs the third way on every archive it reads and compares the
result with the graph it read. `Brush.rebuild` says how that went ("exact",
"renumbered" or "kept"), and `Brush.fidelity` is "byte" only when the build
from parameters gives the file's own bytes. Anything less is "table": the
source bytes are kept and returned for an unchanged brush, and a changed one
is written into the graph that was read, never rebuilt from parameters that
do not say everything. A changed archive is written with its own profile; one
no profile reproduced takes its era's profile from the schema, and one of no
known era (X<count>) its family's (FAMILY_PROFILE).

Patches (`apply_patch`) change only the keys named, check each value against
its key's schema row and report what happened in the PatchReport of F3. A
value is held to a row's `limits` only when the row says `limits_hard`, and no
row of the schema says so today. New brushes (`new_brush`) are one real donor
archive of their era, named in NEW_BRUSH_DONORS and read from the library when
the brush is made, with the name, the creation date and the texture names
replaced. `census` counts what the library holds; `census_columns` gives the
schema's census columns from it.

Evidence. When this was written, every `Brush.archive` of the library (1,071
entries, 1,040 distinct, eleven eras) was rebuilt from its JSON parameters and
the schema to the same bytes; the opt-in test in tests/test_brush_model.py
repeats the walk. That proves the forms, the class tables, the encode order
and the stored key orders against those files. It proves nothing about what
the drawing app opens: no file written here has been opened on a device.

Untrusted input. An archive comes from a stranger. Forms are built under a
depth cap and one budget for the whole archive (MAX_FORM_VALUES, the cap
`plist_objects` of F3): a graph that names one entry along many paths raises
LimitExceeded("plist_objects") instead of unfolding without end, and an entry
that holds itself becomes `$opaque`. The library is read through container.py,
the one reader: in memory, never extracting an entry, never using an entry
name as a path, under the caps of F3.

Errors are `BrushModelError(code, detail)`, with one of the codes not_a_brush,
duplicate_key, no_schema, bad_schema, bad_json, bad_value, opaque, bad_mode,
bad_patch, bad_era, bad_override, library_missing, lfs_pointer, bad_container,
donor_missing, donor_mismatch, curve_invalid; the codec below raises its own.

Standard library only. Not a command.
"""

from __future__ import annotations

import collections
import copy
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field, replace
from pathlib import Path

import bplist
import brush_common
import container
import keyed_archive
from bplist import BrushModelError, CodecError, ContainerError, LimitExceeded, PDict, Real, UID
from keyed_archive import Archive

__all__ = ["Brush", "BrushModelError", "CENSUS_SCHEMA", "FAMILY_PROFILE", "FREE_TEXT_KEYS", "Issue",
           "MODEL_SCHEMA", "NEW_BRUSH_DONORS", "NEW_BRUSH_ERA", "NEW_BRUSH_ERAS", "OBSERVED_FIELDS",
           "PATCH_SCHEMA", "REJECT_CODES", "SCHEMA_PATH", "WARNING_CODES", "aliases_of",
           "apply_patch", "canonical_curve", "case_base", "census", "census_columns",
           "curve_points", "decode", "detect_era", "encode", "export_state", "family_of",
           "from_archive", "from_json", "is_modified", "library_archives", "load_donor",
           "load_schema", "merge_orders", "nearest_era", "new_brush", "point_text",
           "read_library_archive", "real_text", "same_real", "scalar", "set_curve", "setting",
           "text", "to_archive", "to_json", "validate"]

MODEL_SCHEMA = "rosw-brushes-model/1"
PATCH_SCHEMA = "rosw-brushes-patch/1"
SCHEMA_PATH = brush_common.TOOL_ROOT / "schema" / "silica_keys.json"

CLASS = "$class"
FAMILIES = ("legacy", "modern")
# What a changed archive is written with when its own profile is not known.
FAMILY_PROFILE = {"legacy": "ios_legacy", "modern": "ios_modern"}
TYPES = ("real", "int", "bool", "string_ref", "data_ref", "curve_ref", "roll_ref", "array_ref",
         "date_ref")
ENVELOPE_VERSION = 100000
ENVELOPE_ARCHIVER = "NSKeyedArchiver"

# ── new brushes ──────────────────────────────────────────────────────────────
# A new brush is one real archive of its era with the name, the date and the
# texture names replaced (F3 "New brushes"). The donor is read from the library
# when the brush is made; nothing of it is stored here but where it is and the
# sha256 that says it is still the same file.
NEW_BRUSH_ERA = "M220"
NEW_BRUSH_ERAS = ("M220", "E4")
NEW_BRUSH_DONORS = {
    # P2 Airbrushing "Hard Brush": a plain hard round brush, 220 keys, written
    # by the app in 2025; read byte for byte by the rules and the schema.
    "M220": {"container": "official/procreate-2/p2-airbrushing.brushset",
             "entry": "E0719D60-EE29-46C8-9DC1-D7A4323E6A3B/Brush.archive",
             "archive_sha256": "310d22e6896e917c5e185cfbc89e9c1cc7ce32a4c2908275a1e6a924ba27835e"},
    # Everything Watercolour "AN Big Ass Filler & Eraser": a plain round
    # filler, 101 keys, no jitter, no scatter, render type 0.
    "E4": {"container": "user/everything-watercolour/Everything_Watercolour.brushset",
           "entry": "ACFC6405-6E03-44AD-907F-32495FD0EE4D/Brush.archive",
           "archive_sha256": "daf0b587dce135a078580112822332f61cb31680f2dbd5836f73d4c00a22b193"},
}
TEXTURE_KEYS = ("bundledShapePath", "bundledGrainPath", "bundledMetallicPath",
                "bundledRoughnessPath", "bundledHeightPath")
NS_EPOCH = 978307200                    # seconds from 1970-01-01 to 2001-01-01

# ── patches ──────────────────────────────────────────────────────────────────
REJECT_CODES = ("unknown_key", "wrong_type", "not_in_enum", "non_finite", "read_only",
                "not_in_era", "curve_invalid", "out_of_range")
WARNING_CODES = ("outside_observed", "stale_thumbnail")
MODES = ("strict", "clamp")
MAX_CURVE_POINTS = 64
MAX_FORM_DEPTH = 16
# What one archive's forms may unfold to: the property-list cap of F3
# (spec.yaml format.caps.plist_objects), which bplist.resolve also applies.
MAX_FORM_VALUES = bplist.MAX_OBJECTS

# ── reading the library ──────────────────────────────────────────────────────
# The library is read through container.py, the one reader, under its caps.
ARCHIVE_NAME = container.ARCHIVE
CONTAINER_SUFFIXES = (".brush", ".brushset")
SKIPPED_FOLDERS = frozenset({"__macosx", "_docs"})      # folders on disk the walk passes over
LFS_HEADER = container.LFS_HEADER
MAX_ZIP_ENTRIES = container.CAPS["zip_entries"]
MAX_CONTAINER_BYTES = container.CAPS["upload_bytes"]

_POINT = re.compile(r"^\{(-?\d+\.\d{6}), (-?\d+\.\d{6})\}$")
_SCALAR_TAGS = ("$real32", "$real64", "$int")
_ROLL_FIELDS = ("mode", "activationFalloff", "activationOrigin", "activationRange")
_NO = object()


class _Opaque(Exception):
    """A value the forms do not express."""


class _Reject(Exception):
    """One change of a patch that is not applied."""

    def __init__(self, code, reason):
        super().__init__(code, reason)
        self.code = code
        self.reason = reason


@dataclass
class Issue:
    """One finding of `validate`: level is "error", "warning" or "info"."""

    level: str
    code: str
    key: str | None
    message: str


@dataclass
class Brush:
    """One brush archive as parameters.

    params          root key -> JSON value, in root key order, `$class` left out
    era             an era id of the schema, or X<count> for a key set no era has
    family          "legacy" or "modern": the era's, or the nearest era's
    profile         the string-sharing rule the archive is written with
    top_order       the four envelope keys in file order
    root_class      the root's class chain
    class_position  where `$class` stands among the root keys
    shared          groups of root keys that hold one and the same entry, beyond
                    what the schema's own rules share (two texture names that
                    are one string, in three library files)
    fidelity        "byte": a build from these parameters gives the file's bytes;
                    "table": it does not, and the source bytes are kept;
                    "built": there is no file (from_json)
    rebuild         how the build from parameters compared with the graph read:
                    "exact", "renumbered", "kept" (the parameters do not say
                    everything; the decoded graph is what gets written), or None
    archive         the decoded archive, or None
    """

    params: dict
    era: str
    family: str
    profile: str
    top_order: tuple
    root_class: tuple
    class_position: int = 0
    shared: list = field(default_factory=list)
    fidelity: str = "built"
    rebuild: str | None = None
    archive: Archive | None = field(default=None, repr=False, compare=False)
    base: dict | None = field(default=None, repr=False, compare=False)
    base_mark: str | None = field(default=None, repr=False, compare=False)

    @property
    def key_order(self):
        """Every root key in order, `$class` included."""
        keys = list(self.params)
        keys.insert(max(0, min(self.class_position, len(keys))), CLASS)
        return keys

    @property
    def key_count(self):
        return len(self.params) + 1

    @property
    def name(self):
        """The brush's name as text ("" for nil)."""
        return text(self.params.get("name")) or ""

    def __repr__(self):
        return (f"<Brush {self.name!r} {self.era} {self.key_count} keys, {self.fidelity}, "
                f"{self.profile}>")


# ── the schema ───────────────────────────────────────────────────────────────

_LOADED = None
_INDEXES = {}


class _Index:
    """The schema, looked up the ways this module needs."""

    def __init__(self, schema):
        try:
            self._load(schema)
        except BrushModelError:
            raise
        except (KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
            raise BrushModelError("bad_schema", f"{type(exc).__name__}: {exc}") from None

    def _load(self, schema):
        self.schema = schema
        self.rows = {}
        for row in schema["keys"]:
            if row["key"] in self.rows:
                raise BrushModelError("bad_schema", f"the key {row['key']} has two rows")
            if row["type"] not in TYPES:
                raise BrushModelError("bad_schema", f"{row['key']}: type {row['type']!r}")
            self.rows[row["key"]] = row
        self.eras = []
        self.era = {}
        self.exact = {}
        self.base = {}
        self.optional = {}
        for row in schema["eras"]:
            era = row["id"]
            if row["family"] not in FAMILIES or row["profile"] not in keyed_archive.PROFILES:
                raise BrushModelError("bad_schema", f"era {era}: family or profile")
            self.eras.append(era)
            self.era[era] = row
            self.base[era] = frozenset(row["key_order"])
            self.optional[era] = frozenset(row.get("optional_keys", ()))
            orders = [row["key_order"]] + [v["key_order"] for v in row.get("variants", ())]
            for order in orders:
                keys = frozenset(order)
                if len(keys) != len(order) or CLASS not in keys or keys in self.exact:
                    raise BrushModelError("bad_schema", f"era {era}: a key order repeats a key, "
                                                        "lacks $class or is another era's")
                self.exact[keys] = (era, tuple(order))
        self.classes = {name: spec for name, spec in schema["classes"].items()
                        if not name.startswith("$")}
        self.form_class = {spec["form"]: (name, spec) for name, spec in self.classes.items()}
        self.class_entry = tuple(schema["classes"]["$class_entry"]["fields"])
        self.encode_order = {family: list(schema["encode_order"][family]) for family in FAMILIES}
        guessed = schema["encode_order"].get("guessed") or {}
        self.guessed = {family: frozenset(guessed.get(family, ())) for family in FAMILIES}
        for name, spec in self.classes.items():
            if spec["chain"][0] != name or CLASS not in spec["fields"]:
                raise BrushModelError("bad_schema", f"class {name}: chain or fields")

    def family(self, era, keys=None):
        if era in self.era:
            return self.era[era]["family"]
        return self.era[_nearest(self, frozenset(keys or ()) | {CLASS})[0]]["family"]


def load_schema():
    """The key schema, read once from the schema/ folder beside this code.

    It is the folder of the running code whatever data root is in use (F2).
    The dict is shared: do not change it.
    """
    global _LOADED
    if _LOADED is None:
        try:
            content = brush_common.read_text(SCHEMA_PATH)
        except OSError as exc:
            raise BrushModelError("no_schema", f"schema/{SCHEMA_PATH.name} cannot be read "
                                               f"({type(exc).__name__})") from None
        try:
            schema = json.loads(content)
        except ValueError as exc:
            raise BrushModelError("bad_schema", f"schema/{SCHEMA_PATH.name}: {exc}") from None
        _LOADED = (schema, _Index(schema))
    return _LOADED[0]


def _index(schema=None):
    if schema is None:
        load_schema()
        return _LOADED[1]
    if _LOADED is not None and schema is _LOADED[0]:
        return _LOADED[1]
    held = _INDEXES.get(id(schema))
    if held is None or held[0] is not schema:
        if len(_INDEXES) >= 16:
            _INDEXES.clear()
        held = _INDEXES[id(schema)] = (schema, _Index(schema))
    return held[1]


def aliases_of(key, *, schema=None):
    """The other keys that name the same setting in another era."""
    row = _index(schema).rows.get(key)
    return list(row.get("aliases", ())) if row else []


def setting(params, key, default=None, *, schema=None):
    """`params[key]`, or the value under the first alias of `key` that the
    brush holds and that has the same type (the facet code's `S(k)`)."""
    if key in params:
        return params[key]
    index = _index(schema)
    row = index.rows.get(key)
    for alias in (row.get("aliases", ()) if row else ()):
        other = index.rows.get(alias)
        if alias in params and other is not None and other["type"] == row["type"]:
            return params[alias]
    return default


# ── eras ─────────────────────────────────────────────────────────────────────

def _nearest(index, keys):
    """(era, missing, extra): the era whose key set is nearest to `keys`, the
    earlier row on a tie. An era's optional keys count as its own."""
    best = None
    for era in index.eras:
        wanted = index.base[era] | (keys & index.optional[era])
        distance = len(wanted ^ keys)
        if best is None or distance < best[0]:
            best = (distance, era, wanted)
    if best is None:
        raise BrushModelError("bad_schema", "the schema lists no era")
    return best[1], sorted(best[2] - keys), sorted(keys - best[2])


def detect_era(keys, *, schema=None):
    """(era_id, exact, missing, extra) for a root key set.

    An era matches only on its exact key set (M220: its 220 keys plus any of
    its optional keys). Anything else is X<count>, and `missing` and `extra`
    are measured against the nearest era. `$class` is counted whether or not
    `keys` names it: every root has one.
    """
    index = _index(schema)
    keys = frozenset(keys) | {CLASS}
    hit = index.exact.get(keys)
    if hit is not None:
        return hit[0], True, [], []
    for era in index.eras:
        optional = index.optional[era]
        if optional and index.base[era] <= keys and keys - index.base[era] <= optional:
            return era, True, [], []
    _, missing, extra = _nearest(index, keys)
    return f"X{len(keys)}", False, missing, extra


def nearest_era(keys, *, schema=None):
    """The era a key set is nearest to: the era itself on an exact match."""
    index = _index(schema)
    era, exact, _, _ = detect_era(keys, schema=schema)
    return era if exact else _nearest(index, frozenset(keys) | {CLASS})[0]


def family_of(era_or_keys, *, schema=None):
    """"legacy" or "modern" for an era id or a root key set."""
    index = _index(schema)
    if isinstance(era_or_keys, str):
        if era_or_keys not in index.era:
            raise BrushModelError("bad_era", f"{era_or_keys!r} is not an era of the schema")
        return index.era[era_or_keys]["family"]
    return index.era[nearest_era(era_or_keys, schema=schema)]["family"]


# ── scalars ──────────────────────────────────────────────────────────────────

def _plain_number(value):
    """True for a float a JSON number carries exactly: finite, not negative zero."""
    return math.isfinite(value) and not (value == 0.0 and math.copysign(1.0, value) < 0.0)


def _real_form(real, plain_width):
    """A stored real as JSON: a number when its key's type says its width and
    the value survives JSON, else a tag."""
    value = real.value
    plain = _plain_number(value)
    if plain and real.width == plain_width:
        return value
    return {"$real32" if real.width == 4 else "$real64": value if plain else real.bits.hex()}


def _scalar_form(value, kind):
    """A stored bool, int or real as JSON. `kind` is the schema type of the
    key it stands under ("real", "int", "real64") or None."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value if kind == "int" else {"$int": value}
    return _real_form(value, 4 if kind == "real" else 8 if kind == "real64" else 0)


def _bad(detail):
    return BrushModelError("bad_value", detail)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _real_of(payload, width):
    """The Real a number, or a hex string of the stored bytes, stands for."""
    if isinstance(payload, str):
        if not re.fullmatch("[0-9a-fA-F]{%d}" % (2 * width), payload):
            raise _bad(f"a {8 * width}-bit real given as text is {2 * width} hex digits")
        return Real(bytes.fromhex(payload))
    if not _is_number(payload):
        raise _bad(f"a real is a number, not {type(payload).__name__}")
    try:
        return Real.f32(payload) if width == 4 else Real.f64(payload)
    except CodecError:
        raise _bad(f"{payload!r} does not fit a {8 * width}-bit real") from None


def _tag(form):
    """(tag, payload) when `form` is a typed-scalar tag, else None."""
    if isinstance(form, dict) and len(form) == 1:
        (tag, payload), = form.items()
        if tag in _SCALAR_TAGS:
            return tag, payload
    return None


def _tag_value(tag, payload):
    """The stored value a tag stands for."""
    if tag == "$int":
        if isinstance(payload, bool) or not isinstance(payload, int):
            raise _bad("`$int` holds a whole number")
        if not -(1 << 63) <= payload < (1 << 64):
            raise _bad(f"{payload} does not fit a property list")
        return payload
    return _real_of(payload, 4 if tag == "$real32" else 8)


def _f32(value):
    """A number rounded to 32 bits and widened again."""
    return _real_of(value, 4).value


def scalar(form, default=None):
    """The Python value of a scalar form: a tag is opened, hex is turned back
    into its float. Anything that is not a scalar gives `default`."""
    if isinstance(form, (bool, int, float)):
        return form
    opened = _tag(form)
    if opened is None:
        return default
    try:
        value = _tag_value(*opened)
    except BrushModelError:
        return default
    return value.value if isinstance(value, Real) else value


def text(form, default=None):
    """The text of a string form (plain or wrapped); `default` for nil or
    anything else."""
    if isinstance(form, str):
        return form
    if isinstance(form, dict) and isinstance(form.get("string"), str) and "wrapper" in form:
        return form["string"]
    return default


def real_text(value):
    """The shortest decimal that reads back as the same 32-bit float: the
    canonical text of a real (F3)."""
    real = Real.f32(scalar(value, value))
    number = real.value
    if not math.isfinite(number):
        return repr(number)
    for digits in range(1, 10):
        candidate = "%.*g" % (digits, number)
        if Real.f32(float(candidate)).bits == real.bits:
            break
    shown = repr(float(candidate))
    return shown[:-2] if shown.endswith(".0") else shown


def same_real(one, two):
    """Whether two numbers are the same 32-bit pattern."""
    return Real.f32(scalar(one, one)).bits == Real.f32(scalar(two, two)).bits


# ── curves ───────────────────────────────────────────────────────────────────

def point_text(x, y):
    """One curve point as the archive spells it."""
    return "{%.6f, %.6f}" % (x + 0.0, y + 0.0)          # + 0.0 turns -0.0 into 0.0


def _parse_point(point):
    match = _POINT.match(point) if isinstance(point, str) else None
    return (float(match.group(1)), float(match.group(2))) if match else None


def canonical_curve(points):
    """Curve points as the strings an archive holds.

    Strings that already have the archive's form are kept as they are, in the
    order given. Numeric pairs are written "{%.6f, %.6f}", the two end points
    (lowest and highest x) first and the points between them after, by x.
    A curve has 2 to 64 points, every coordinate a finite number from 0 to 1.
    """
    if not isinstance(points, (list, tuple)):
        raise BrushModelError("curve_invalid", "the points of a curve are a list")
    if not 2 <= len(points) <= MAX_CURVE_POINTS:
        raise BrushModelError("curve_invalid", f"a curve has 2 to {MAX_CURVE_POINTS} points, "
                                               f"not {len(points)}")
    pairs = []
    verbatim = True
    for point in points:
        if isinstance(point, str):
            pair = _parse_point(point)
            if pair is None:
                raise BrushModelError("curve_invalid", f"{point!r} is not a point: "
                                                       "\"{0.250000, 0.330000}\" is")
        elif isinstance(point, (list, tuple)) and len(point) == 2 and all(map(_is_number, point)):
            verbatim = False
            pair = (float(point[0]), float(point[1]))
        else:
            raise BrushModelError("curve_invalid", "a point is a pair of numbers [x, y] or "
                                                   "the text \"{x, y}\"")
        if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in pair):
            raise BrushModelError("curve_invalid", "a coordinate is a number from 0 to 1")
        pairs.append(pair)
    if verbatim:
        return list(points)
    ordered = sorted(pairs, key=lambda pair: pair[0])
    return [point_text(*pair) for pair in [ordered[0], ordered[-1]] + ordered[1:-1]]


def curve_points(brush, key, *, file_order=False):
    """The points of a curve as (x, y) numbers, by x unless `file_order`."""
    form = brush.params.get(key)
    if not isinstance(form, dict) or not isinstance(form.get("points"), list):
        raise BrushModelError("curve_invalid", f"{key} is not a curve of this brush")
    pairs = [_parse_point(point) for point in form["points"]]
    if any(pair is None for pair in pairs):
        raise BrushModelError("curve_invalid", f"{key} holds a point that is not \"{{x, y}}\"")
    return pairs if file_order else sorted(pairs, key=lambda pair: pair[0])


def set_curve(brush, key, points, *, schema=None):
    """Give a curve of this brush new points, in place. The key must be a curve
    the brush holds, or one the schema lists as optional for its era."""
    patched, report = apply_patch(brush, {key: {"points": list(points)}}, schema=schema)
    if report["rejected"]:
        first = report["rejected"][0]
        raise BrushModelError("curve_invalid", f"{key}: {first['code']}: {first['reason']}")
    brush.params = patched.params
    brush.class_position = patched.class_position
    brush.shared = patched.shared
    brush.era = patched.era


# ── reading an archive into forms ────────────────────────────────────────────

class _Reader:
    """Turns the entries of one decoded archive into JSON value forms.

    One reader serves one archive, and it has one budget for everything it
    unfolds (`MAX_FORM_VALUES`, the property-list cap `plist_objects` of F3):
    every reference followed, every field and list item, every curve point
    and array item costs one. A graph that names one entry along many paths
    (each level of instances naming the next one several times) unfolds into
    exponentially many values from a few hundred bytes; the budget stops it
    with LimitExceeded("plist_objects") in time linear in the cap. It is never
    turned into `$opaque`, which is caught per root key and would give each
    key a fresh budget.
    """

    def __init__(self, index, archive, budget=None):
        self.index = index
        self.objects = archive.objects
        self.left = MAX_FORM_VALUES if budget is None else budget

    def spend(self, count=1):
        self.left -= count
        if self.left < 0:
            raise LimitExceeded("plist_objects", f"the archive's values unfold to more than "
                                                 f"{MAX_FORM_VALUES:,} values (one entry named "
                                                 "along many paths); it is not read")

    def root_form(self, key, value):
        row = self.index.rows.get(key)
        try:
            if isinstance(value, (bool, int, Real)):
                return _scalar_form(value, row["type"] if row else None)
            if isinstance(value, UID):
                return self.ref(value, (), 0)
            raise _Opaque("held in place")
        except _Opaque as why:
            return {"$opaque": str(why)}

    def entry(self, uid):
        if not isinstance(uid, UID) or not 0 < uid.value < len(self.objects):
            raise _Opaque("a reference to nothing")
        return self.objects[uid.value]

    def chain(self, holder):
        """The class chain of an instance, when its class entry is the plain kind."""
        entry = self.entry(holder.get(CLASS))
        fields = self.index.class_entry
        if not isinstance(entry, PDict) or (
                tuple(entry.keys()) != fields if fields is not None
                else sorted(entry.keys()) != ["$classes", "$classname"]):
            raise _Opaque("a class entry of another shape")
        name, chain = entry.get("$classname"), entry.get("$classes")
        if (not isinstance(name, str) or not bplist.is_array(chain) or not chain
                or any(not isinstance(item, str) for item in chain) or chain[0] != name):
            raise _Opaque("a class entry of another shape")
        return list(chain)

    def ref(self, uid, path, depth):
        if uid.value == 0:
            return None
        self.spend()
        if uid.value in path:
            raise _Opaque("an entry that holds itself")
        if depth > MAX_FORM_DEPTH:
            raise _Opaque("nested too deep")
        entry = self.entry(uid)
        if isinstance(entry, str):
            return entry
        if isinstance(entry, (bytes, bytearray)):
            return {"$data": bytes(entry).hex()}
        if isinstance(entry, (bool, int, Real)):
            return {"$ref": _scalar_form(entry, None)}
        if isinstance(entry, PDict) and entry.has(CLASS):
            return self.instance(entry, path + (uid.value,), depth + 1)
        raise _Opaque("an entry that is no instance")

    def instance(self, entry, path, depth):
        chain = self.chain(entry)
        spec = self.index.classes.get(chain[0])
        if spec is not None and chain == spec["chain"]:
            short = self.SHORT.get(spec["form"])
            form = short(self, spec, entry) if short else _NO
            if form is not _NO:
                return form
        fields = [[key, None if key == CLASS else self.field(value, path, depth)]
                  for key, value in entry]
        return {"$class": chain[0], "$classes": chain, "$fields": fields}

    def field(self, value, path, depth):
        self.spend()
        if isinstance(value, (bool, int, Real)):
            return _scalar_form(value, None)
        if isinstance(value, str):
            return {"$inline": value}
        if isinstance(value, UID):
            return self.ref(value, path, depth)
        if bplist.is_array(value):
            if depth > MAX_FORM_DEPTH:
                raise _Opaque("nested too deep")
            return {"$list": [self.field(item, path, depth + 1) for item in value]}
        raise _Opaque("a value with no form")

    def at(self, uid):
        """The entry a UID names, or None for nil, for no UID and for one out of range."""
        if isinstance(uid, UID) and 0 < uid.value < len(self.objects):
            return self.objects[uid.value]
        return None

    def _curve(self, spec, entry):
        optional = spec.get("optional", ())
        if entry.keys() not in (spec["fields"], [f for f in spec["fields"] if f not in optional]) \
                or "points" not in self.index.form_class:
            return _NO
        points_spec = self.index.form_class["points"][1]
        holder = self.at(entry.get("points"))
        if (not isinstance(holder, PDict) or holder.keys() != points_spec["fields"]
                or self.chain(holder) != points_spec["chain"]):
            return _NO
        items = holder.get("NS.objects")
        if not bplist.is_array(items):
            return _NO
        self.spend(len(items))
        points = [self.at(item) for item in items]
        if any(not isinstance(point, str) for point in points):
            return _NO
        form = {"points": points}
        if entry.has("resolution"):
            resolution = entry.get("resolution")
            if isinstance(resolution, bool) or not isinstance(resolution, int):
                return _NO
            form["resolution"] = resolution
        return form

    def _roll(self, spec, entry):
        if entry.keys() != spec["fields"]:
            return _NO
        form = {}
        for name in _ROLL_FIELDS:
            value = entry.get(name)
            if name == "mode":
                if isinstance(value, bool) or not isinstance(value, int):
                    return _NO
                form[name] = value
            elif isinstance(value, Real) and value.width == 4 and _plain_number(value.value):
                form[name] = value.value
            else:
                return _NO
        return form

    def _array(self, spec, entry):
        items = entry.get("NS.objects")
        if entry.keys() != spec["fields"] or not bplist.is_array(items):
            return _NO
        self.spend(len(items))
        held = [self.at(item) for item in items]
        if any(not isinstance(item, (bool, int, Real)) for item in held):
            return _NO
        return [_scalar_form(item, "real") for item in held]

    def _date(self, spec, entry):
        value = entry.get("NS.time")
        if entry.keys() != spec["fields"] or not isinstance(value, Real) or value.width != 8:
            return _NO
        return {"time": _scalar_form(value, "real64")}

    def _string(self, spec, entry):
        value = entry.get("NS.string")
        if entry.keys() != spec["fields"] or not isinstance(value, str):
            return _NO
        return {"string": value, "wrapper": spec["chain"][0]}

    SHORT = {"curve": _curve, "roll": _roll, "array": _array, "date": _date, "string": _string}

    def is_shared_empty(self, number):
        """Whether an entry is the one empty array every empty array is."""
        entry = self.objects[number]
        if not isinstance(entry, PDict) or not entry.has(CLASS):
            return False
        try:
            spec = self.index.classes.get(self.chain(entry)[0])
        except _Opaque:
            return False
        return bool(spec and spec.get("share_empty") and entry.keys() == spec["fields"]
                    and entry.get("NS.objects") == [])


# ── building an archive from forms ───────────────────────────────────────────

class _Builder:
    """Appends the entries of JSON value forms to an `$objects` list, numbered
    the way the app numbers them: an instance, then what it holds field by
    field, then its class entry the first time the class is used."""

    def __init__(self, index, objects):
        self.index = index
        self.objects = objects
        self.class_uid = {}
        self.empty = {}
        self.group_uid = {}
        self.group_of = {}
        for number, entry in enumerate(objects):
            if isinstance(entry, PDict) and tuple(entry.keys()) == index.class_entry \
                    and bplist.is_array(entry.get("$classes")):
                self.class_uid.setdefault(tuple(entry.get("$classes")), UID(number))
        reader = _Reader(index, Archive((), 0, "", objects))
        for number in range(1, len(objects)):
            if reader.is_shared_empty(number):
                name = reader.chain(objects[number])[0]
                self.empty.setdefault(name, UID(number))

    def add(self, value):
        self.objects.append(value)
        return UID(len(self.objects) - 1)

    def class_ref(self, chain):
        chain = tuple(chain)
        if chain not in self.class_uid:
            values = {"$classname": chain[0], "$classes": list(chain)}
            self.class_uid[chain] = self.add(PDict((name, values[name])
                                                   for name in self.index.class_entry))
        return self.class_uid[chain]

    def instance(self, chain, fields, make):
        """An instance whose fields are made in order; its class comes last."""
        holder = PDict()
        uid = self.add(holder)
        values = {name: make(name) for name in fields if name != CLASS}
        values[CLASS] = self.class_ref(chain)
        holder.extend((name, values[name]) for name in fields)
        return uid

    def share(self, groups):
        """Root keys that are to hold one entry: the first made is used by all."""
        for group in groups:
            for key in group:
                self.group_of[key] = tuple(group)

    def root_value(self, key, form):
        row = self.index.rows.get(key)
        kind = row["type"] if row else None
        if form is None:
            return UID(0)
        if isinstance(form, bool):
            return form
        if _is_number(form):
            if kind == "real":
                return _real_of(form, 4)
            if kind == "int" and isinstance(form, int):
                return _tag_value("$int", form)
            raise _bad(f"{key}: a number here must say what it is ($real32, $real64 or $int)")
        opened = _tag(form)
        if opened is not None:
            return _tag_value(*opened)
        group = self.group_of.get(key)
        if group in self.group_uid:
            return self.group_uid[group]
        uid = self.ref(form, 0)
        if group is not None:
            self.group_uid[group] = uid
        return uid

    def ref(self, form, depth):
        if form is None:
            return UID(0)
        if depth > MAX_FORM_DEPTH:
            raise _bad("a value nested too deep")
        if isinstance(form, str):
            return self.add(form)
        if isinstance(form, list):
            return self.array(form)
        if not isinstance(form, dict):
            raise _bad(f"a {type(form).__name__} is not a value of a brush")
        if "$opaque" in form:
            raise BrushModelError("opaque", "a value this module could not read cannot be built")
        if "$data" in form:
            return self.add(_data_of(form))
        if "$ref" in form:
            inner = form["$ref"]
            return self.add(inner if isinstance(inner, bool) else _tag_value(*_need_tag(inner)))
        if "$class" in form:
            return self.generic(form, depth)
        if "points" in form:
            return self.curve(form)
        if "time" in form:
            return self.date(form)
        if "mode" in form:
            return self.roll(form)
        if "wrapper" in form:
            return self.string(form)
        raise _bad(f"an object with the keys {sorted(form)} is not a value of a brush")

    def spec(self, form_name):
        if form_name not in self.index.form_class:
            raise BrushModelError("bad_schema", f"the schema has no class for a {form_name}")
        return self.index.form_class[form_name][1]

    def curve(self, form):
        spec = self.spec("curve")
        points_spec = self.spec("points")
        fields = [name for name in spec["fields"]
                  if name in form or name not in spec.get("optional", ())]

        def points():
            return self.instance(points_spec["chain"], points_spec["fields"],
                                 lambda _: [self.add(point) for point in form["points"]])

        return self.instance(spec["chain"], fields,
                             lambda name: points() if name == "points" else form[name])

    def roll(self, form):
        spec = self.spec("roll")
        return self.instance(spec["chain"], spec["fields"],
                             lambda name: form[name] if name == "mode" else _real_of(form[name], 4))

    def array(self, form):
        spec = self.spec("array")
        name = spec["chain"][0]
        if not form and spec.get("share_empty") and name in self.empty:
            return self.empty[name]

        def element(item):
            if isinstance(item, bool):
                return self.add(item)
            opened = _tag(item)
            return self.add(_tag_value(*opened) if opened else _real_of(item, 4))

        uid = self.instance(spec["chain"], spec["fields"], lambda _: [element(item) for item in form])
        if not form and spec.get("share_empty"):
            self.empty[name] = uid
        return uid

    def date(self, form):
        spec = self.spec("date")
        opened = _tag(form["time"])
        value = _tag_value(*opened) if opened else _real_of(form["time"], 8)
        return self.instance(spec["chain"], spec["fields"], lambda _: value)

    def string(self, form):
        spec = self.index.classes.get(form["wrapper"])
        if spec is None or spec["form"] != "string":
            raise _bad(f"{form['wrapper']!r} is not a class that wraps a string")
        return self.instance(spec["chain"], spec["fields"], lambda _: form["string"])

    def generic(self, form, depth):
        fields = [key for key, _ in form["$fields"]]
        values = dict((key, value) for key, value in form["$fields"])
        return self.instance(form["$classes"], fields,
                             lambda name: self.field(values[name], depth + 1))

    def field(self, form, depth):
        if form is None or isinstance(form, bool):
            return UID(0) if form is None else form
        opened = _tag(form)
        if opened is not None:
            return _tag_value(*opened)
        if isinstance(form, dict) and len(form) == 1 and "$inline" in form:
            return form["$inline"]
        if isinstance(form, dict) and len(form) == 1 and "$list" in form:
            if depth > MAX_FORM_DEPTH:
                raise _bad("a value nested too deep")
            return [self.field(item, depth + 1) for item in form["$list"]]
        return self.ref(form, depth)


def _need_tag(form):
    opened = _tag(form)
    if opened is None:
        raise _bad("a number here must say what it is ($real32, $real64 or $int)")
    return opened


def _data_of(form):
    value = form.get("$data")
    if len(form) != 1 or not isinstance(value, str) or not re.fullmatch("(?:[0-9a-fA-F]{2})*", value):
        raise _bad("data is {\"$data\": hex}")
    return bytes.fromhex(value)


def _encode_keys(index, brush, keys):
    """`keys` in the order the app archives them: the schema's encode order,
    then any key it does not list, in root order."""
    listed = {key: rank for rank, key in enumerate(index.encode_order[brush.family])}
    position = {key: rank for rank, key in enumerate(brush.params)}
    return sorted(keys, key=lambda key: (listed.get(key, len(listed)), position[key]))


def _build(index, brush):
    """An archive made of the brush's parameters and the schema alone."""
    root = PDict()
    objects = [keyed_archive.NULL, root]
    builder = _Builder(index, objects)
    builder.share(brush.shared)
    values = {}
    for key in _encode_keys(index, brush, list(brush.params)):
        values[key] = builder.root_value(key, brush.params[key])
    values[CLASS] = builder.class_ref(brush.root_class)
    root.extend((key, values[key]) for key in brush.key_order)
    return Archive(tuple(brush.top_order), ENVELOPE_VERSION, ENVELOPE_ARCHIVER, objects,
                   brush.profile, keyed_archive.FIDELITY_TABLE, None)


def _patched(index, brush):
    """The decoded archive with new entries for the root keys that changed,
    numbered again. Everything else is the graph that was read."""
    archive = keyed_archive.clone(brush.archive)
    root = keyed_archive.root(archive)
    held = {key: value for key, value in root}      # a PDict has keys() but is no mapping
    changed =[key for key in brush.params
               if key not in brush.base or not _same(brush.params[key], brush.base[key])]
    was_shared = {tuple(group) for group in _decoded_shared(brush)}
    regrouped = [group for group in brush.shared if tuple(group) not in was_shared]
    for group in regrouped:
        changed.extend(key for key in group if key not in changed and key in brush.params)
    builder = _Builder(index, archive.objects)
    builder.share(group for group in regrouped)
    for key in _encode_keys(index, brush, changed):
        held[key] = builder.root_value(key, brush.params[key])
    if tuple(brush.root_class) != tuple(keyed_archive.class_chain(archive, archive.top.get("root"))):
        held[CLASS] = builder.class_ref(brush.root_class)
    root[:] = [(key, held[key]) for key in brush.key_order]
    archive.top_order = tuple(brush.top_order)
    result = keyed_archive.renumber(archive, index.encode_order[brush.family])
    result.profile = brush.profile
    return result


def _decoded_shared(brush):
    return json.loads(brush.base_mark)[1] if brush.base_mark else []


# ── identity of parameters ───────────────────────────────────────────────────

def _same(one, two):
    """Whether two forms are the same value, type for type."""
    try:
        return (json.dumps(one, sort_keys=True, allow_nan=False)
                == json.dumps(two, sort_keys=True, allow_nan=False))
    except (TypeError, ValueError):
        return False


def _mark(brush):
    try:
        return json.dumps([list(brush.params.items()), [list(group) for group in brush.shared],
                           brush.class_position, list(brush.root_class), list(brush.top_order)],
                          sort_keys=True, allow_nan=False)
    except (TypeError, ValueError):
        return None


def is_modified(brush):
    """True when the brush is no longer what was decoded, or never was."""
    return brush.archive is None or brush.base_mark is None or _mark(brush) != brush.base_mark


def _identical(one, two):
    """Graph equality that keeps a bool apart from an int and a dict from a list."""
    if type(one) is not type(two):
        return False
    if isinstance(one, (list, tuple)):
        return len(one) == len(two) and all(_identical(a, b) for a, b in zip(one, two))
    return one == two


def _same_graph(one, two):
    return (tuple(one.top_order) == tuple(two.top_order) and one.version == two.version
            and one.archiver == two.archiver and _identical(one.top, two.top)
            and _identical(one.objects, two.objects))


# ── decode, encode ───────────────────────────────────────────────────────────

def from_archive(archive, *, schema=None):
    """A decoded keyed archive as a Brush.

    Raises BrushModelError("not_a_brush") when the root is not a SilicaBrush
    instance, and "duplicate_key" when the root names a key twice.
    """
    index = _index(schema)
    try:
        root = keyed_archive.root(archive)
        chain = keyed_archive.class_chain(archive, archive.top.get("root"))
    except CodecError as exc:
        raise BrushModelError("not_a_brush", str(exc)) from None
    if (not isinstance(root, PDict) or not chain or any(not isinstance(c, str) for c in chain)
            or "SilicaBrush" not in chain):
        raise BrushModelError("not_a_brush", "the root of the archive is not a SilicaBrush")
    reader = _Reader(index, archive)
    params, class_position, holders = {}, 0, {}
    for position, (key, value) in enumerate(root):
        if key == CLASS:
            class_position = position
            continue
        if key in params:
            raise BrushModelError("duplicate_key", f"the root holds {key} twice")
        params[key] = reader.root_form(key, value)
        if isinstance(value, UID) and 0 < value.value < len(archive.objects):
            holders.setdefault(value.value, []).append(key)
    if root.keys().count(CLASS) != 1:
        raise BrushModelError("not_a_brush", "the root holds `$class` more than once")
    shared = [keys for number, keys in holders.items()
              if len(keys) > 1 and not reader.is_shared_empty(number)]
    era, exact, _, _ = detect_era(root.keys(), schema=schema)
    family = index.family(era, root.keys())
    profile = archive.profile or (index.era[era]["profile"] if exact else FAMILY_PROFILE[family])
    brush = Brush(params, era, family, profile, tuple(archive.top_order), tuple(chain),
                  class_position, shared, "table", None, archive)
    brush.base = copy.deepcopy(params)
    brush.base_mark = _mark(brush)
    brush.rebuild = _compare(index, brush, archive)
    if archive.fidelity == keyed_archive.FIDELITY_BYTE and brush.rebuild == "exact":
        brush.fidelity = "byte"
    return brush


def _compare(index, brush, archive):
    """How an archive built from the parameters compares with the one read."""
    try:
        built = _build(index, brush)
        if _same_graph(built, archive):
            return "exact"
        if _same_graph(built, keyed_archive.renumber(archive, index.encode_order[brush.family])):
            return "renumbered"
    except (CodecError, RecursionError, TypeError, KeyError, ValueError, AttributeError):
        pass
    return "kept"


def decode(data, *, schema=None):
    """The Brush of a `Brush.archive`. Raises the codec's errors for bytes that
    are not a keyed archive and BrushModelError for an archive that is not a brush."""
    return from_archive(keyed_archive.decode(data), schema=schema)


def to_archive(brush, *, schema=None):
    """The keyed archive of a brush: the one it was decoded from while nothing
    changed; that graph with the changed keys rebuilt when something did; and,
    for a brush that never had one, an archive built from its parameters."""
    index = _index(schema)
    if brush.archive is not None and not is_modified(brush):
        return keyed_archive.clone(brush.archive)
    try:
        if brush.archive is not None and brush.base is not None:
            return _patched(index, brush)
        return _build(index, brush)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        raise _bad(f"the parameters are not in the forms of the model "
                   f"({type(exc).__name__}: {exc})") from None


def encode(brush, *, schema=None):
    """The bytes of a brush. An unchanged brush is its source bytes; a changed
    one is written by the layout rules with the brush's profile."""
    return keyed_archive.encode(to_archive(brush, schema=schema), profile=brush.profile)


def export_state(brush, *, schema=None):
    """What `encode` gives for this brush:

        "source"     nothing changed: the bytes that were read
        "canonical"  written by the rules that reproduce the app's own files:
                     a known era, a key order that was read from a real file
                     for exactly this key set, and a base that those rules
                     reproduced (or no base at all)
        "valid"      a well-formed archive whose layout is not claimed to be
                     the app's: an unknown era, a key set whose order was
                     never seen, a base the rules do not reproduce, or a
                     changed key that now holds an entry of its own at a
                     place in the encode order that is only guessed
                     (`encode_order.guessed` of the schema)
    """
    index = _index(schema)
    if not is_modified(brush):
        return "source"
    stored = index.exact.get(frozenset(brush.key_order))
    known = stored is not None and list(stored[1]) == brush.key_order
    decoded_well = brush.archive is None or (brush.fidelity == "byte" and brush.rebuild == "exact")
    return "canonical" if known and decoded_well and not _guessed_changes(index, brush) else "valid"


def _guessed_changes(index, brush):
    """The keys whose place in the encode order is a guess and that hold an
    entry of their own (not nil) that the base did not have: the numbering of
    such an archive is not known to be the app's."""
    guessed = index.guessed.get(brush.family, frozenset())
    base = brush.base if brush.base is not None else {}
    return sorted(key for key in guessed if brush.params.get(key) is not None
                  and (key not in base or not _same(base[key], brush.params[key])))


# ── JSON ─────────────────────────────────────────────────────────────────────

def to_json(brush):
    """The frozen JSON form of a brush (F3). `key_order` is the root key order,
    `$class` included; JSON written with sorted keys loses the order of
    `params`, so it is said twice."""
    return {"schema": MODEL_SCHEMA, "era": brush.era, "family": brush.family,
            "profile": brush.profile, "top_order": list(brush.top_order),
            "root_class": list(brush.root_class), "key_order": brush.key_order,
            "params": copy.deepcopy(brush.params),
            "shared": [list(group) for group in brush.shared]}


def _canonical_scalar(form, kind):
    """A scalar form in its one spelling for a key of schema type `kind`."""
    if isinstance(form, bool):
        return form
    if _is_number(form):
        if kind == "real":
            return _real_form(_real_of(form, 4), 4)
        if kind == "real64":
            return _real_form(_real_of(form, 8), 8)
        if kind == "int" and isinstance(form, int):
            return _scalar_form(_tag_value("$int", form), "int")
        raise _bad("a number here must say what it is ($real32, $real64 or $int)")
    return _scalar_form(_tag_value(*_need_tag(form)), kind)


def _canonical(index, key, form):
    """One parameter in its one spelling, or BrushModelError("bad_value")."""
    row = index.rows.get(key)
    kind = row["type"] if row else None
    if form is None or isinstance(form, (bool, str)):
        return form
    if _is_number(form) or _tag(form) is not None:
        return _canonical_scalar(form, kind)
    return _canonical_ref(index, form, 0)


def _canonical_ref(index, form, depth):
    if depth > MAX_FORM_DEPTH:
        raise _bad("a value nested too deep")
    if form is None or isinstance(form, str):
        return form
    if isinstance(form, list):
        return [_canonical_scalar(item, "real") for item in form]
    if not isinstance(form, dict):
        raise _bad(f"a {type(form).__name__} is not a value of a brush")
    keys = set(form)
    if "$opaque" in form:
        return copy.deepcopy(form)
    if "$data" in form:
        return {"$data": _data_of(form).hex()}
    if keys == {"$ref"}:
        inner = form["$ref"]
        return {"$ref": inner if isinstance(inner, bool) else _canonical_scalar(inner, None)}
    if keys == {"$class", "$classes", "$fields"}:
        chain, fields = form["$classes"], form["$fields"]
        if (not isinstance(chain, list) or not chain or any(not isinstance(c, str) for c in chain)
                or form["$class"] != chain[0] or not isinstance(fields, list)
                or any(not isinstance(pair, (list, tuple)) or len(pair) != 2
                       or not isinstance(pair[0], str) for pair in fields)
                or [pair[0] for pair in fields].count(CLASS) != 1
                or len({pair[0] for pair in fields}) != len(fields)):
            raise _bad("an instance is {\"$class\", \"$classes\", \"$fields\": [[key, value]]} "
                       "with one `$class` field")
        return {"$class": chain[0], "$classes": list(chain),
                "$fields": [[name, None if name == CLASS else _canonical_field(index, value, depth + 1)]
                            for name, value in fields]}
    if "points" in form:
        points = form["points"]
        resolution = form.get("resolution")
        if (not keys <= {"points", "resolution"} or not isinstance(points, list)
                or any(not isinstance(point, str) for point in points)
                or ("resolution" in form and (isinstance(resolution, bool)
                                              or not isinstance(resolution, int)))):
            raise _bad("a curve is {\"points\": [text, ...]} with an optional whole `resolution`")
        return dict(form, points=list(points))
    if keys == {"time"}:
        return {"time": _canonical_scalar(form["time"], "real64")}
    if keys == set(_ROLL_FIELDS):
        mode = form["mode"]
        if isinstance(mode, bool) or not isinstance(mode, int):
            raise _bad("the mode of roll parameters is a whole number")
        out = {"mode": mode}
        for name in _ROLL_FIELDS[1:]:
            out[name] = _canonical_scalar(form[name], "real")
            if not isinstance(out[name], float):
                raise _bad("roll parameters hold plain 32-bit reals")
        return out
    if keys == {"string", "wrapper"}:
        spec = index.classes.get(form["wrapper"]) if isinstance(form["wrapper"], str) else None
        if not isinstance(form["string"], str) or spec is None or spec["form"] != "string":
            raise _bad("a wrapped string is {\"string\": text, \"wrapper\": a string class}")
        return {"string": form["string"], "wrapper": form["wrapper"]}
    raise _bad(f"an object with the keys {sorted(keys)} is not a value of a brush")


def _canonical_field(index, form, depth):
    if form is None or isinstance(form, bool):
        return form
    if _tag(form) is not None:
        return _canonical_scalar(form, None)
    if isinstance(form, dict) and set(form) == {"$inline"} and isinstance(form["$inline"], str):
        return {"$inline": form["$inline"]}
    if isinstance(form, dict) and set(form) == {"$list"} and isinstance(form["$list"], list):
        return {"$list": [_canonical_field(index, item, depth + 1) for item in form["$list"]]}
    if _is_number(form) or isinstance(form, list):
        raise _bad("inside `$fields` a number is tagged and a list is {\"$list\": [...]}")
    return _canonical_ref(index, form, depth)


def from_json(obj, *, schema=None):
    """A Brush from the JSON form `to_json` gives. It has no archive behind it:
    `encode` builds one from the parameters and the schema.

    Raises BrushModelError("bad_json") for another shape and "bad_value" for a
    parameter that is not in one of the forms.
    """
    index = _index(schema)
    if not isinstance(obj, dict) or obj.get("schema") != MODEL_SCHEMA:
        raise BrushModelError("bad_json", f"not a {MODEL_SCHEMA} object")
    params, order = obj.get("params"), obj.get("key_order")
    top_order, root_class = obj.get("top_order"), obj.get("root_class")
    if not isinstance(params, dict) or any(not isinstance(key, str) for key in params):
        raise BrushModelError("bad_json", "`params` is an object of key: value")
    if (not isinstance(order, list) or any(not isinstance(key, str) for key in order)
            or len(set(order)) != len(order) or set(order) != set(params) | {CLASS}
            or CLASS in params):
        raise BrushModelError("bad_json", "`key_order` lists every key of `params` once, and `$class`")
    if (not isinstance(top_order, list) or any(not isinstance(key, str) for key in top_order)
            or sorted(top_order) != sorted(keyed_archive.ENVELOPE_KEYS)):
        raise BrushModelError("bad_json", "`top_order` is the four envelope keys")
    if (not isinstance(root_class, list) or not root_class
            or any(not isinstance(name, str) for name in root_class)):
        raise BrushModelError("bad_json", "`root_class` is a class chain")
    era, exact, _, _ = detect_era(order, schema=schema)
    if obj.get("era") not in (None, era):
        raise BrushModelError("bad_json", f"`era` says {obj.get('era')!r}; the keys are {era}")
    family = index.family(era, order)
    if obj.get("family") not in (None, family):
        raise BrushModelError("bad_json", f"`family` says {obj.get('family')!r}; the keys are {family}")
    profile = obj.get("profile")
    if profile is None:
        profile = index.era[era]["profile"] if exact else FAMILY_PROFILE[family]
    if profile not in keyed_archive.PROFILES:
        raise BrushModelError("bad_json", f"`profile` {profile!r} is not a profile")
    shared = obj.get("shared", [])
    if (not isinstance(shared, list)
            or any(not isinstance(group, list) or len(group) < 2 or len(set(group)) != len(group)
                   or any(key not in params for key in group) for group in shared)
            or len({key for group in shared for key in group}) != sum(map(len, shared))):
        raise BrushModelError("bad_json", "`shared` is a list of groups of keys of `params`")
    canonical = {}
    for key in order:
        if key == CLASS:
            continue
        try:
            canonical[key] = _canonical(index, key, params[key])
        except BrushModelError as exc:
            raise BrushModelError(exc.code, f"{key}: {exc.detail}") from None
        except (KeyError, TypeError, AttributeError) as exc:
            raise _bad(f"{key}: {type(exc).__name__}") from None
    return Brush(canonical, era, family, profile, tuple(top_order), tuple(root_class),
                 order.index(CLASS), [list(group) for group in shared], "built", None)


# ── patches ──────────────────────────────────────────────────────────────────

def _echo(value, depth=0):
    """A value as it was sent, made safe to put in a JSON report."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else repr(value)
    if depth < 8 and isinstance(value, (list, tuple)):
        return [_echo(item, depth + 1) for item in value[:64]]
    if depth < 8 and isinstance(value, dict):
        return {str(key): _echo(item, depth + 1) for key, item in list(value.items())[:64]}
    return repr(value)[:200]


def _finite(value, what="the value"):
    if not math.isfinite(value):
        raise _Reject("non_finite", f"{what} is not a finite number")
    return value


def _patch_real32(value, what="a real"):
    """A patch value as a 32-bit real form."""
    opened = _tag(value)
    if opened is not None:
        if opened[0] != "$real32":
            raise _Reject("wrong_type", f"{what} is a 32-bit real, not {opened[0]}")
        try:
            real = _real_of(opened[1], 4)
        except BrushModelError as exc:
            raise _Reject("wrong_type", exc.detail) from None
    elif _is_number(value):
        _finite(value)
        try:
            real = Real.f32(value)
        except CodecError:
            raise _Reject("non_finite", f"{value!r} does not fit a 32-bit real") from None
    else:
        raise _Reject("wrong_type", f"{what} is a number, not {_kind_name(value)}")
    _finite(real.value)
    return _real_form(real, 4)


def _patch_whole(value, what="an int"):
    opened = _tag(value)
    if opened is not None:
        if opened[0] != "$int":
            raise _Reject("wrong_type", f"{what} is a whole number, not {opened[0]}")
        value = opened[1]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _Reject("wrong_type", f"{what} is a whole number, not {_kind_name(value)}")
    if isinstance(value, float):
        if _finite(value) != math.trunc(value):
            raise _Reject("wrong_type", f"{what} is a whole number, not {value!r}")
        value = int(value)
    if not -(1 << 63) <= value < (1 << 63):
        raise _Reject("wrong_type", f"{value} does not fit a 64-bit int")
    return value


def _kind_name(value):
    if value is None:
        return "null"
    return {bool: "a boolean", int: "a number", float: "a number", str: "text", list: "a list",
            dict: "an object"}.get(type(value), type(value).__name__)


def _patch_real(index, brush, row, current, value):
    return _patch_real32(value)


def _patch_int(index, brush, row, current, value):
    whole = _patch_whole(value)
    enum = row.get("enum")
    if enum and str(whole) not in enum:
        raise _Reject("not_in_enum", f"{whole} is not one of {', '.join(sorted(enum, key=_by_number))}")
    return whole


def _by_number(text_value):
    try:
        return (0, int(text_value))
    except ValueError:
        return (1, 0)


def _patch_bool(index, brush, row, current, value):
    if not isinstance(value, bool):
        raise _Reject("wrong_type", f"a switch is true or false, not {_kind_name(value)}")
    return value


def _patch_string(index, brush, row, current, value):
    wrapped = isinstance(current, dict) and "wrapper" in current
    if value is None:
        return None
    if isinstance(value, str):
        return {"string": value, "wrapper": current["wrapper"]} if wrapped else value
    if isinstance(value, dict) and set(value) == {"string", "wrapper"}:
        try:
            return _canonical_ref(index, value, 0)
        except BrushModelError as exc:
            raise _Reject("wrong_type", exc.detail) from None
    raise _Reject("wrong_type", f"a string is text or null, not {_kind_name(value)}")


def _patch_data(index, brush, row, current, value):
    if value is None:
        return None
    try:
        if not isinstance(value, dict):
            raise _bad("data is {\"$data\": hex}")
        return {"$data": _data_of(value).hex()}
    except BrushModelError as exc:
        raise _Reject("wrong_type", exc.detail) from None


def _patch_curve(index, brush, row, current, value):
    spec = index.form_class["curve"][1]
    held = current if isinstance(current, dict) and "points" in current else None
    if held is not None:
        resolution = held.get("resolution")
    else:
        resolution = (spec.get("resolution") or {}).get(brush.family)
    points = value
    if isinstance(value, dict):
        if not set(value) <= {"points", "resolution"} or "points" not in value:
            raise _Reject("curve_invalid", "a curve is {\"points\": [...]}")
        if "resolution" in value and value["resolution"] != resolution:
            raise _Reject("curve_invalid", "the resolution of a curve is not a setting: "
                                           f"this one has {resolution!r}")
        points = value["points"]
    try:
        strings = canonical_curve(points)
    except BrushModelError as exc:
        raise _Reject("curve_invalid", exc.detail) from None
    if held is not None and sorted(strings) == sorted(held["points"]):
        strings = list(held["points"])          # the same points: the file's order is kept
    form = {"points": strings}
    if resolution is not None:
        form["resolution"] = resolution
    return form


def _patch_roll(index, brush, row, current, value):
    if not isinstance(value, dict) or set(value) != set(_ROLL_FIELDS):
        raise _Reject("wrong_type", "roll parameters are {" + ", ".join(_ROLL_FIELDS) + "}")
    form = {"mode": _patch_whole(value["mode"], "the mode")}
    for name in _ROLL_FIELDS[1:]:
        form[name] = _patch_real32(value[name], name)
        if not isinstance(form[name], float):
            raise _Reject("wrong_type", f"{name} is a plain number")
    return form


def _patch_array(index, brush, row, current, value):
    if not isinstance(value, (list, tuple)):
        raise _Reject("wrong_type", f"an array is a list of numbers, not {_kind_name(value)}")
    if len(value) > 4096:
        raise _Reject("wrong_type", "an array of more than 4096 numbers")
    return [_patch_real32(item, "an array item") for item in value]


def _patch_date(index, brush, row, current, value):
    if not isinstance(value, dict) or set(value) != {"time"} or not _is_number(value["time"]):
        raise _Reject("wrong_type", "a date is {\"time\": seconds since 2001-01-01}")
    return {"time": _real_form(Real.f64(_finite(value["time"], "the time")), 8)}


_PATCHERS = {"real": _patch_real, "int": _patch_int, "bool": _patch_bool,
             "string_ref": _patch_string, "data_ref": _patch_data, "curve_ref": _patch_curve,
             "roll_ref": _patch_roll, "array_ref": _patch_array, "date_ref": _patch_date}


def _patch_unknown(current, value):
    """A change to a key the schema does not list: the new value takes the type
    of the one the brush holds."""
    if isinstance(current, bool):
        if isinstance(value, bool):
            return value
        raise _Reject("wrong_type", f"this key holds a boolean, not {_kind_name(value)}")
    opened = _tag(current)
    if opened is not None:
        if opened[0] == "$int":
            return {"$int": _patch_whole(value)}
        if opened[0] == "$real32":
            if _tag(value) is None and not _is_number(value):
                raise _Reject("wrong_type", f"this key holds a real, not {_kind_name(value)}")
            plain = _patch_real32(value)
            return plain if isinstance(plain, dict) else {"$real32": plain}
        if _tag(value) is not None and _tag(value)[0] == "$real64":
            value = _tag(value)[1]
        if not _is_number(value):
            raise _Reject("wrong_type", f"this key holds a real, not {_kind_name(value)}")
        return _real_form(Real.f64(_finite(value)), 0)
    if current is None or isinstance(current, str):
        if value is None or isinstance(value, str):
            return value
        raise _Reject("wrong_type", f"this key holds text, not {_kind_name(value)}")
    if _same(current, value):
        return current                  # sent back as it holds it: unchanged
    raise _Reject("read_only", "a value of this kind is written back as it was read")


def _limits(row, key, form, mode, report):
    """Clamp or reject against `limits` only when the row says they are hard;
    otherwise warn when the value lies outside what was observed."""
    limits = row.get("limits")
    if limits and row.get("limits_hard"):
        low, high = limits
        if low <= form <= high:
            return form
        if mode == "strict":
            raise _Reject("out_of_range", f"{form!r} is outside {low!r} to {high!r}")
        inside = min(max(form, low), high)
        inside = int(inside) if row["type"] == "int" else _f32(inside)
        report["clamped"].append({"key": key, "from": form, "to": inside, "min": low, "max": high})
        return inside
    observed = row.get("observed") or {}
    low, high = observed.get("min"), observed.get("max")
    if (_is_number(low) and form < low) or (_is_number(high) and form > high):
        report["warnings"].append({"key": key, "code": "outside_observed"})
    return form


def _patch_form(index, brush, key, value, mode, allow_unknown, report):
    if key == CLASS:
        raise _Reject("read_only", "the class of a brush is not a setting")
    row = index.rows.get(key)
    held = key in brush.params
    if row is None:
        if not held:
            raise _Reject("unknown_key", "no archive key of this name is known")
        if not allow_unknown:
            raise _Reject("unknown_key", "the schema does not list this key; "
                                         "it is written back as it was read")
        return _patch_unknown(brush.params[key], value)
    if not held and key not in index.optional.get(brush.era, ()):
        others = [alias for alias in row.get("aliases", ()) if alias in brush.params]
        hint = f"; this brush holds {', '.join(others)}" if others else ""
        raise _Reject("not_in_era", f"a brush of era {brush.era} has no {key}{hint}")
    current = brush.params.get(key)
    if row.get("ui") == "readonly":
        # A read-only key sent back with the value it holds changes nothing:
        # it is listed as unchanged (F3 "Patches"). Only a different value is
        # read_only.
        try:
            form = _PATCHERS[row["type"]](index, brush, row, current, value)
        except _Reject:
            form = _NO
        if held and form is not _NO and _same(current, form):
            return form
        if held and _same(current, value):
            return current
        raise _Reject("read_only", f"{key} is read-only")
    form = _PATCHERS[row["type"]](index, brush, row, current, value)
    if row["type"] == "real" and _same_at_32_bits(current, form):
        return current          # equal at the 32-bit level: unchanged, its stored width kept
    if row["type"] in ("real", "int") and _is_number(form):
        form = _limits(row, key, form, mode, report)
    return form


def _same_at_32_bits(current, form):
    """Whether a real key's present value, stored as a 64-bit real, is the
    32-bit real a patch gives. (A 32-bit one compares by `_same`.)"""
    opened = _tag(current)
    if opened is None or opened[0] != "$real64" or not _is_number(opened[1]) or not _is_number(form):
        return False
    try:
        return Real.f32(opened[1]).bits == Real.f32(form).bits
    except CodecError:
        return False


def _unshare(brush, key):
    """A key that got a value of its own no longer holds an entry with others."""
    brush.shared = [group for group in ([k for k in g if k != key] for g in brush.shared)
                    if len(group) > 1]


def _reorder(index, brush):
    """After a key was added: the stored order of the new key set when one was
    read from a real file, else the present order with the new keys last."""
    stored = index.exact.get(frozenset(brush.key_order))
    if stored is None:
        return
    order = list(stored[1])
    brush.params = {key: brush.params[key] for key in order if key != CLASS}
    brush.class_position = order.index(CLASS)


def apply_patch(brush, changes, *, mode="strict", allow_unknown=False, schema=None):
    """Apply the keys of `changes` to a copy of `brush`: (Brush, PatchReport).

    A key absent from `changes` is never touched. Each value is read by its
    key's schema type (1 on a real key is 1.0) and a real is rounded to 32
    bits. A change equal to the present value, bit for bit, is listed under
    `unchanged`. A value is held to `limits` only where the schema row says
    `limits_hard`: then `mode="strict"` rejects it and `mode="clamp"` moves it
    to the limit. Otherwise it is applied and, when it lies outside what the
    library holds, the report warns `outside_observed`.

    The report is `ok` when nothing was rejected. The returned brush carries
    every change that was not rejected: check `ok` before writing it.
    """
    if mode not in MODES:
        raise BrushModelError("bad_mode", f"mode is one of {', '.join(MODES)}, not {mode!r}")
    if not isinstance(changes, dict):
        raise BrushModelError("bad_patch", "`changes` is an object of key: value")
    index = _index(schema)
    result = replace(brush, params=copy.deepcopy(brush.params),
                     shared=[list(group) for group in brush.shared])
    report = {"ok": True, "era": brush.era, "applied": {}, "clamped": [], "rejected": [],
              "unchanged": [], "warnings": []}
    added = False
    for key, value in changes.items():
        marks = (len(report["clamped"]), len(report["warnings"]))
        try:
            if not isinstance(key, str):
                raise _Reject("unknown_key", "a key is text")
            form = _patch_form(index, result, key, value, mode, allow_unknown, report)
        except _Reject as no:
            del report["clamped"][marks[0]:], report["warnings"][marks[1]:]
            report["rejected"].append({"key": key if isinstance(key, str) else repr(key),
                                       "value": _echo(value), "code": no.code, "reason": no.reason})
            continue
        if key in result.params and _same(result.params[key], form):
            report["unchanged"].append(key)
            continue
        added = added or key not in result.params
        result.params[key] = form
        report["applied"][key] = copy.deepcopy(form)
        _unshare(result, key)
    if added:
        _reorder(index, result)
        result.era = detect_era(result.key_order, schema=schema)[0]
    report["ok"] = not report["rejected"]
    return result, report


# ── new brushes ──────────────────────────────────────────────────────────────

def _archives_of(found, where):
    """(entry name, bytes) for every `Brush.archive` member of what
    container.read_any found, in the order the source zip held them. A name is
    the entry's name in its zip; one in a nested zip is prefixed with the path
    to that zip and `!/`."""
    out = []
    for item in found:
        nested = item.origin[len(where) + 2:] + "!/" if item.origin.startswith(where + "!/") else ""
        if isinstance(item, container.BrushSet):
            position = {name: number for number, name in enumerate(item.entry_order)}
            held = sorted(((position.get(f"{uuid}/{member.path}", len(position)), uuid, member)
                           for uuid, folder in item.brushes for member in folder.members
                           if member.path.rsplit("/", 1)[-1] == ARCHIVE_NAME),
                          key=lambda row: row[0])
            out += [(f"{nested}{item.prefix}{uuid}/{member.path}", member.data)
                    for _, uuid, member in held]
        else:
            out += [(nested + member.path, member.data) for member in item.members
                    if member.path.rsplit("/", 1)[-1] == ARCHIVE_NAME]
    return out


def _container_archives(data, where):
    """(entry name, bytes) for each `Brush.archive` of a container held in
    memory, read by container.read_any under the caps of F3: nothing is
    extracted, no entry name is used as a path, junk and refused entries are
    passed over, and the first of a repeated name wins."""
    try:
        found = container.read_any(data, where)
    except LimitExceeded:
        raise
    except ContainerError as exc:
        if exc.code == "lfs_pointer":
            raise BrushModelError("lfs_pointer", f"{where} is a Git LFS pointer, not a brush file: "
                                                 "run git lfs pull") from None
        raise BrushModelError("bad_container", f"{where}: {exc}") from None
    return _archives_of(found, where)


def _read_container(path, where):
    try:
        return container.read_path(path)
    except OSError as exc:
        raise BrushModelError("library_missing", f"{where} cannot be read "
                                                 f"({type(exc).__name__})") from None


def library_archives(library):
    """(label, bytes) for every `Brush.archive` of every `.brush` and
    `.brushset` under a library folder, in a fixed order, read in memory by
    container.py. A label is `<path under the library> :: <entry name>`."""
    root = Path(library)
    if not root.is_dir():
        raise BrushModelError("library_missing", "the library folder is not there")
    found = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if (path.suffix.lower() in CONTAINER_SUFFIXES and path.is_file()
                and not any(part.lower() in SKIPPED_FOLDERS for part in relative.parts)):
            found.append((relative.as_posix(), path))
    for where, path in sorted(found):
        for entry, data in _container_archives(_read_container(path, where), where):
            yield f"{where} :: {entry}", data


def read_library_archive(library, where, entry):
    """The bytes of one `Brush.archive`: `where` is a container's path under
    the library, `entry` the entry's exact name inside it."""
    parts = str(where).split("/")
    if (not isinstance(where, str) or not where or "\\" in where or ":" in where
            or where.startswith("/") or ".." in parts or "" in parts):
        raise BrushModelError("library_missing", "a container is named by its POSIX path under "
                                                 "the library")
    path = Path(library) / where
    if not path.is_file():
        raise BrushModelError("library_missing", f"{where} is not in the library")
    for name, data in _container_archives(_read_container(path, where), where):
        if name == entry:
            return data
    raise BrushModelError("donor_missing", f"{where} holds no {entry}")


def load_donor(era=NEW_BRUSH_ERA, *, library=None, schema=None):
    """The real archive a new brush of `era` is made from, as a Brush.

    Read from the library (`library`, else the resolved library root) every
    time. Raises BrushModelError: "bad_era" for an era no donor is named for,
    "library_missing" when the file is not there, "lfs_pointer" for a clone
    without Git LFS, "donor_mismatch" when the file is not the one named.
    """
    if era not in NEW_BRUSH_DONORS:
        raise BrushModelError("bad_era", f"a new brush is made in one of "
                                         f"{', '.join(NEW_BRUSH_ERAS)}, not {era!r}")
    donor = NEW_BRUSH_DONORS[era]
    root = Path(library) if library is not None else brush_common.resolve_paths().library
    if not root.is_dir():
        raise BrushModelError("library_missing",
                              "a new brush is made from a real brush of the library, and the "
                              f"library folder is not there (it needs {donor['container']})")
    data = read_library_archive(root, donor["container"], donor["entry"])
    if hashlib.sha256(data).hexdigest() != donor["archive_sha256"]:
        raise BrushModelError("donor_mismatch", f"{donor['container']} :: {donor['entry']} is not "
                                                "the archive the new-brush template names")
    brush = decode(data, schema=schema)
    if brush.era != era or brush.fidelity != "byte":
        raise BrushModelError("donor_mismatch", f"the donor reads as {brush.era}, {brush.fidelity}; "
                                                f"a template is {era}, byte")
    return brush


def new_brush(name, *, era=NEW_BRUSH_ERA, overrides=None, now=None, library=None, schema=None):
    """A new brush: the donor archive of `era` with its name, its creation date
    and its texture names replaced, and nothing else (F3 "New brushes").

    name        the brush's name
    overrides   changes applied on top, by the rules of `apply_patch` in strict
                mode; one that is rejected raises BrushModelError("bad_override")
    now         seconds since 1970-01-01 for the creation date (default: the clock)
    library     the library folder (default: the resolved library root)

    The five `bundled...Path` keys are set to nil: the textures of a new brush
    are the files put beside its archive, or the bundled names `overrides` gives.
    """
    if not isinstance(name, str):
        raise _bad("the name of a brush is text")
    brush = load_donor(era, library=library, schema=schema)
    result = replace(brush, params=copy.deepcopy(brush.params),
                     shared=[list(group) for group in brush.shared])
    result.params["name"] = name
    _unshare(result, "name")
    if "creationDate" in result.params:
        if now is not None and not _is_number(now):
            raise _bad("`now` is a number of seconds since 1970-01-01")
        seconds = time.time() if now is None else float(now)
        if not math.isfinite(seconds):
            raise _bad("`now` is a finite number of seconds")
        result.params["creationDate"] = {"time": _real_form(Real.f64(seconds - NS_EPOCH), 8)}
    for key in TEXTURE_KEYS:
        if key in result.params:
            result.params[key] = None
            _unshare(result, key)
    if overrides:
        result, report = apply_patch(result, overrides, schema=schema)
        if not report["ok"]:
            first = report["rejected"][0]
            raise BrushModelError("bad_override", f"{first['key']}: {first['code']}: {first['reason']}")
    return result


def case_base(era, assign=None, *, schema=None):
    """The brush the cases of schema/patch_cases.json are run against: every
    key of `era` with its schema default, in the era's key order, and then the
    values of `assign` put in as they are.

    It is made of defaults, so it is not a brush any app wrote. It exists to
    check patches where there is no library. It is never the template of a new
    brush: `new_brush` is.
    """
    index = _index(schema)
    if era not in index.era:
        raise BrushModelError("bad_era", f"{era!r} is not an era of the schema")
    row = index.era[era]
    resolution = (index.form_class["curve"][1].get("resolution") or {}).get(row["family"])
    params = {}
    for key in row["key_order"]:
        if key == CLASS:
            continue
        default = copy.deepcopy(index.rows[key]["default"])
        if isinstance(default, dict) and "points" in default and resolution is not None:
            default["resolution"] = resolution
        params[key] = default
    params.update(copy.deepcopy(assign or {}))
    return from_json({"schema": MODEL_SCHEMA, "era": None, "family": row["family"],
                      "profile": row["profile"], "top_order": row["top_order"],
                      "root_class": row["root_class"],
                      "key_order": row["key_order"] + [k for k in params if k not in row["key_order"]],
                      "params": params}, schema=schema)


# ── validate ─────────────────────────────────────────────────────────────────

def _fits(kind, form):
    """Whether a form is of its key's schema type."""
    if kind == "bool":
        return isinstance(form, bool)
    if kind == "int":
        return isinstance(form, int) and not isinstance(form, bool)
    if kind == "real":
        return isinstance(form, float) or (isinstance(form, dict) and "$real32" in form)
    if form is None:
        return True
    if kind == "string_ref":
        return isinstance(form, str) or (isinstance(form, dict) and set(form) == {"string", "wrapper"})
    if kind == "array_ref":
        return isinstance(form, list)
    marker = {"data_ref": "$data", "curve_ref": "points", "roll_ref": "mode", "date_ref": "time"}
    return isinstance(form, dict) and marker[kind] in form


def validate(brush, *, schema=None):
    """What is unusual about a brush, as a list of Issue. Nothing here stops
    an export; a warning says what the export will be."""
    index = _index(schema)
    issues = []

    def add(level, code, key, message):
        issues.append(Issue(level, code, key, message))

    era, exact, missing, extra = detect_era(brush.key_order, schema=schema)
    if not exact:
        add("warning", "unknown_era", None,
            f"the {brush.key_count} root keys are no era's; the nearest is "
            f"{nearest_era(brush.key_order, schema=schema)} ({len(missing)} missing, "
            f"{len(extra)} extra)")
    elif list(index.exact.get(frozenset(brush.key_order), (None, ()))[1]) != brush.key_order:
        add("info", "key_order_unseen", None,
            "no real file was read with exactly this key set in this order")
    for key, form in brush.params.items():
        row = index.rows.get(key)
        if isinstance(form, dict) and "$opaque" in form:
            add("warning", "opaque_value", key, f"not read ({form['$opaque']}); written back as it was")
        elif row is None:
            add("info", "unknown_key", key, "not in the schema; written back as it was read")
        elif not _fits(row["type"], form):
            add("warning", "type_mismatch", key, f"the schema types this key {row['type']}")
        elif row["type"] == "real" and isinstance(form, dict):
            value = scalar(form)
            if not math.isfinite(value):
                add("warning", "non_finite", key, "holds a value that is not a finite number")
        elif row["type"] == "int" and row.get("enum") and str(form) not in row["enum"]:
            add("info", "not_in_enum", key, f"{form} is not a value the library holds for this key")
        elif row["type"] == "curve_ref" and form is not None:
            if any(_parse_point(point) is None for point in form["points"]) or len(form["points"]) < 2:
                add("warning", "curve_invalid", key, "holds a point that is not \"{x, y}\"")
    if brush.params.get("name") in (None, ""):
        add("info", "no_name", "name", "the brush has no name")
    if brush.archive is not None and brush.fidelity == "table":
        add("warning", "fidelity_table", None,
            "the layout rules do not give this file's own bytes; unchanged, it is exported as "
            "its source bytes")
    if brush.rebuild == "kept":
        add("warning", "graph_kept", None,
            "the parameters do not say everything the archive holds; a change is written into "
            "the graph that was read")
    if is_modified(brush) and export_state(brush, schema=schema) == "valid":
        guessed = _guessed_changes(index, brush)
        add("warning", "fidelity_valid", guessed[0] if len(guessed) == 1 else None,
            "written as a valid archive, not in a layout known to be the app's own"
            + (f" (where {', '.join(guessed)} is numbered is a guess)" if guessed else ""))
    return issues


# ── census ───────────────────────────────────────────────────────────────────

CENSUS_SCHEMA = "rosw-brushes-census/1"
CENSUS_TOP = 6
# Keys whose values are text a person typed. The census counts them and lists
# no value of theirs but nil and "", so a brush's name or its author's never
# reaches the schema.
FREE_TEXT_KEYS = frozenset({"name", "authorName"})
# What a stored instance's class says its schema type is.
_CLASS_TYPES = {"ValkyrieMagnitudinalCurve": "curve_ref", "ValkyrieBrushRollParameters": "roll_ref",
                "NSArray": "array_ref", "NSMutableArray": "array_ref", "NSDate": "date_ref",
                "NSMutableString": "string_ref", "NSString": "string_ref"}
# The fields of a census key row that the schema copies into `observed`.
OBSERVED_FIELDS = ("count", "nil", "min", "max", "distinct", "common", "nested")


class _BareIndex:
    """What the reader needs when there is no schema: no rows and no classes,
    so every instance comes out in the generic `$class` form."""

    rows = {}
    classes = {}
    form_class = {}
    class_entry = None


def merge_orders(sequences):
    """One order that agrees with every sequence, when there is one.

    A sequence is a list of items or of groups of items (a group is a list of
    items whose order among themselves is not known). Returns {"order",
    "conflicts": [[a, b]] seen both ways round, "unproven": [[a, b]] next to
    each other in the order without ever being seen one after the other}.
    Items that are free to go next are taken in sorted order, so the result
    does not depend on the order the sequences come in.
    """
    after = collections.OrderedDict()
    for sequence in sequences:
        groups = [list(item) if isinstance(item, (list, tuple)) else [item] for item in sequence]
        for position, group in enumerate(groups):
            for item in group:
                after.setdefault(item, set())
            for later in groups[position + 1:]:
                for item in group:
                    after[item].update(later)
    conflicts = sorted([a, b] for a in after for b in after[a] if a in after[b] and a < b)
    waiting = {item: 0 for item in after}
    for item in after:
        for later in after[item]:
            waiting[later] += 1
    order = []
    ready = sorted(item for item in after if waiting[item] == 0)
    while ready:
        item = ready.pop(0)
        order.append(item)
        freed = []
        for later in after[item]:
            waiting[later] -= 1
            if waiting[later] == 0:
                freed.append(later)
        ready = sorted(ready + freed)
    unproven = [[a, b] for a, b in zip(order, order[1:]) if b not in after[a]]
    return {"order": order, "conflicts": conflicts, "unproven": unproven}


def _census_form(reader, value):
    """A stored root value as a JSON form, each scalar in the plain form of
    its stored kind: an int is a number, a 4-byte real a number (or a tag when
    JSON cannot carry it), an 8-byte real a `$real64` tag."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, Real):
        return _real_form(value, value.width)
    if isinstance(value, UID):
        try:
            return reader.ref(value, (), 0)
        except _Opaque as why:
            return {"$opaque": str(why)}
    return {"$opaque": "held in place"}


def _census_type(stored, form):
    """The schema type of a stored root value, told by its shape alone."""
    if isinstance(stored, bool):
        return "bool"
    if isinstance(stored, int):
        return "int"
    if isinstance(stored, Real):
        return "real" if stored.width == 4 else "real64"
    if form is None:
        return "nil"
    if isinstance(form, str):
        return "string_ref"
    if isinstance(form, list):
        return "array_ref"
    if not isinstance(form, dict):
        return "other"
    if "$class" in form:
        return _CLASS_TYPES.get(form["$class"], "instance:" + str(form["$class"]))
    for marker, kind in (("$data", "data_ref"), ("points", "curve_ref"), ("mode", "roll_ref"),
                         ("time", "date_ref"), ("wrapper", "string_ref"), ("$opaque", "opaque"),
                         ("$ref", "ref")):
        if marker in form:
            return kind
    return "other"


def _number_of(form):
    """The number a scalar form stands for, for min and max (None for none)."""
    value = scalar(form)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value if isinstance(value, int) else value + 0.0     # -0.0 counts as 0.0


def _sources(source):
    if isinstance(source, (str, Path)):
        yield from library_archives(source)
        return
    for number, item in enumerate(source):
        if isinstance(item, (bytes, bytearray)):
            yield f"#{number}", bytes(item)
        else:
            label, data = item
            yield str(label), bytes(data)


def _counted(counter, top):
    """[[value, count]] for the most common JSON texts of a counter."""
    rows = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    return [[json.loads(encoded), count] for encoded, count in rows[:top]]


def _most(counter):
    """The most common item of a counter, the first in sorted order on a tie."""
    if not counter:
        return None
    return sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]


def _era_rank(index):
    """A sort key that puts the schema's eras in their order, then the rest."""
    known = {era: rank for rank, era in enumerate(index.eras)} if index else {}
    return lambda era: (known.get(era, len(known)), len(era), era)


def census(source, *, schema=None, top=CENSUS_TOP):
    """What a set of archives holds, counted once per distinct archive.

    `source` is a library folder (walked in memory) or an iterable of archive
    bytes or of (label, bytes). With the schema at hand (the default, when
    schema/silica_keys.json exists) each key set is named by `detect_era` and
    curves, rolls, arrays, dates and wrapped strings come out in their forms;
    without it a key set is named K<count> and every instance is generic.
    The result is plain data with no path outside the library, no date and no
    free text (FREE_TEXT_KEYS). Nothing is written.

        schema, archives, distinct, unreadable: [{"label", "error"}]
        eras       one row per era: id, family, count, key_count, key_order
                   (of its smallest key set), top_order, root_class, profiles,
                   fidelity, rebuild, versions, optional_keys, variants. A key
                   set no era has is a row of its own
        key_sets   one row per distinct root key set
        classes    per class name, each (chain, fields) seen, with counts per
                   family; the root's own class is in `eras`
        encode     per family, the order in which root children are numbered:
                   {"order", "conflicts", "unproven"} from `merge_orders`
        shared     root keys seen holding one entry, with counts
        keys       per root key: type, types, eras {era: n}, count, nil, min,
                   max, distinct, common [[value, n]], default (the most
                   common value), nested (the shape inside a curve, an array,
                   a wrapped string, data, free text)

    A curve is counted by its points; its `resolution` is counted under
    `nested`, so one default serves both families. `census_columns` turns the
    result into the census columns of the schema.
    """
    index = None
    try:
        index = _index(schema)
    except BrushModelError:
        if schema is not None:
            raise
    bare = index if index is not None else _BareIndex()
    result = {"schema": CENSUS_SCHEMA, "archives": 0, "distinct": 0, "unreadable": []}
    seen = set()
    key_sets = collections.OrderedDict()
    classes = collections.defaultdict(collections.Counter)
    sequences = collections.defaultdict(set)
    shared = collections.Counter()
    keys = {}
    for label, data in _sources(source):
        result["archives"] += 1
        digest = hashlib.sha256(data).digest()
        if digest in seen:
            continue
        seen.add(digest)
        try:
            archive = keyed_archive.decode(data)
            root = keyed_archive.root(archive)
            start = archive.top.get("root")
            chain = keyed_archive.class_chain(archive, start)
            if not isinstance(root, PDict) or not chain:
                raise BrushModelError("not_a_brush", "the root is not an instance")
            order = tuple(root.keys())
            if len(set(order)) != len(order):
                raise BrushModelError("duplicate_key", "the root holds a key twice")
            reader = _Reader(bare, archive)
            forms = [(key, value, _census_form(reader, value)) for key, value in root
                     if key != CLASS]
        except CodecError as exc:              # LimitExceeded among them
            result["unreadable"].append({"label": label, "error": str(exc)})
            continue
        result["distinct"] += 1
        brush = None
        if index is not None:
            era, exact, _, _ = detect_era(order, schema=schema)
            family = index.family(era, order)
            group = era if exact else order
            try:
                brush = from_archive(archive, schema=schema)
            except CodecError:
                brush = None
        else:
            era, family, group = f"K{len(order)}", "unknown", order
        row = key_sets.setdefault(order, {
            "key_count": len(order), "count": 0, "era": era, "group": group, "family": family,
            "key_order": list(order), "top_order": collections.Counter(),
            "root_class": collections.Counter(), "profiles": collections.Counter(),
            "fidelity": collections.Counter(), "rebuild": collections.Counter(),
            "versions": collections.Counter(), "example": label})
        row["count"] += 1
        row["top_order"][json.dumps(list(archive.top_order))] += 1
        row["root_class"][json.dumps(list(chain))] += 1
        row["profiles"][str(archive.profile)] += 1
        row["fidelity"][brush.fidelity if brush else archive.fidelity] += 1
        if brush is not None:
            row["rebuild"][str(brush.rebuild)] += 1
        version = root.get("version")
        row["versions"][json.dumps(version if isinstance(version, int)
                                   and not isinstance(version, bool) else None)] += 1
        for number, entry in enumerate(archive.objects):
            if number == start.value or not isinstance(entry, PDict):
                continue
            if entry.has(CLASS):
                pointer = entry.get(CLASS)
                held = keyed_archive.deref(archive, pointer) if isinstance(pointer, UID) else None
                if isinstance(held, PDict) and bplist.is_array(held.get("$classes")):
                    classes[str(held.get("$classname"))][json.dumps(
                        {"chain": list(held.get("$classes")), "fields": entry.keys(),
                         "family": family})] += 1
            elif entry.has("$classname"):
                classes["$class_entry"][json.dumps({"fields": entry.keys(), "family": family})] += 1
        numbered = collections.OrderedDict()
        for key, value in root:
            if key != CLASS and isinstance(value, UID) and value.value:
                numbered.setdefault(value.value, []).append(key)
        sequences[family].add(tuple(tuple(numbered[number]) for number in sorted(numbered)))
        for number, holders in numbered.items():
            if len(holders) > 1:
                shared[json.dumps(sorted(holders))] += 1
        for key, value, form in forms:
            stats = keys.setdefault(key, {"count": 0, "nil": 0, "types": collections.Counter(),
                                          "eras": collections.Counter(), "min": None, "max": None,
                                          "values": collections.Counter(), "texts": set(),
                                          "nested": collections.defaultdict(collections.Counter)})
            kind = _census_type(value, form)
            stats["count"] += 1
            stats["eras"][era] += 1
            if kind == "nil":
                stats["nil"] += 1
            else:
                stats["types"][kind] += 1
            nested = stats["nested"]
            number = _number_of(form) if kind in ("real", "real64", "int") else None
            if kind == "date_ref" and isinstance(form, dict) and "time" in form:
                number = _number_of(form["time"])
            if number is not None:
                stats["min"] = number if stats["min"] is None else min(stats["min"], number)
                stats["max"] = number if stats["max"] is None else max(stats["max"], number)
            shown = form
            if kind == "int":
                nested["values"][str(form)] += 1
            elif kind == "curve_ref" and isinstance(form, dict) and "points" in form:
                shown = {"points": form["points"]}
                nested["points"][str(len(form["points"]))] += 1
                nested["resolution"][json.dumps(form.get("resolution"))] += 1
            elif kind == "array_ref":
                held = keyed_archive.class_chain(archive, value)
                nested["class"][held[0] if held else "?"] += 1
                nested["length"][str(len(form)) if isinstance(form, list) else "?"] += 1
            elif kind == "string_ref" and isinstance(form, dict) and "wrapper" in form:
                nested["wrapper"][str(form["wrapper"])] += 1
            elif kind == "data_ref" and isinstance(form, dict) and isinstance(form.get("$data"), str):
                nested["bytes"][str(len(form["$data"]) // 2)] += 1
            if key in FREE_TEXT_KEYS:
                spelled = text(form)
                nested["text"]["nil" if form is None else "empty" if spelled == ""
                               else "text" if spelled is not None else "other"] += 1
                if form is not None and spelled != "":
                    stats["texts"].add(json.dumps(form, sort_keys=True))
                    continue
            stats["values"][json.dumps(shown, sort_keys=True, allow_nan=False)] += 1

    rank = _era_rank(index)
    result["key_sets"] = []
    eras = collections.OrderedDict()
    for row in sorted(key_sets.values(),
                      key=lambda r: (rank(r["era"]), r["key_count"], r["key_order"])):
        row = dict(row)
        for name in ("top_order", "root_class"):
            row[name] = json.loads(_most(row[name]))
        for name in ("profiles", "fidelity", "rebuild", "versions"):
            row[name] = dict(sorted(row[name].items()))
        group = row.pop("group")
        eras.setdefault(group if isinstance(group, str) else tuple(group), []).append(row)
        result["key_sets"].append(row)
    result["eras"] = []
    for rows in eras.values():
        base = min(rows, key=lambda r: (r["key_count"], -r["count"], r["key_order"]))
        totals = {name: collections.Counter()
                  for name in ("profiles", "fidelity", "rebuild", "versions")}
        for row in rows:
            for name, counter in totals.items():
                counter.update(row[name])
        variants = [r for r in rows if r is not base]
        optional = sorted({key for r in variants for key in r["key_order"]}
                          - set(base["key_order"]))
        era_row = {"id": base["era"], "family": base["family"],
                   "count": sum(r["count"] for r in rows), "key_count": base["key_count"],
                   "key_order": base["key_order"], "top_order": base["top_order"],
                   "root_class": base["root_class"]}
        era_row.update({name: dict(sorted(counter.items())) for name, counter in totals.items()})
        era_row["optional_keys"] = optional
        era_row["variants"] = [{"key_count": r["key_count"], "count": r["count"],
                                "key_order": r["key_order"]} for r in variants]
        result["eras"].append(era_row)
    result["classes"] = {}
    for name, counter in sorted(classes.items()):
        shapes = collections.OrderedDict()
        for encoded, count in sorted(counter.items()):
            shape = json.loads(encoded)
            family = shape.pop("family")
            held = shapes.setdefault(json.dumps(shape, sort_keys=True),
                                     dict(shape, count=0, families={}))
            held["count"] += count
            held["families"][family] = held["families"].get(family, 0) + count
        result["classes"][name] = list(shapes.values())
    result["encode"] = {family: merge_orders(sorted(found))
                        for family, found in sorted(sequences.items())}
    result["shared"] = [{"keys": json.loads(group), "count": count}
                        for group, count in sorted(shared.items())]
    result["keys"] = {}
    for key in sorted(keys):
        stats = keys[key]
        types = dict(sorted(stats["types"].items()))
        common = _counted(stats["values"], top)
        result["keys"][key] = {
            "type": (next(iter(types)) if len(types) == 1 else "mixed" if types else "nil"),
            "types": types,
            "eras": {era: stats["eras"][era] for era in sorted(stats["eras"], key=rank)},
            "count": stats["count"], "nil": stats["nil"],
            "min": stats["min"], "max": stats["max"],
            "distinct": len(stats["values"]) + len(stats["texts"]),
            "common": common,
            "default": common[0][0] if common else None,
            "nested": {name: dict(sorted(counter.items()))
                       for name, counter in sorted(stats["nested"].items())}}
    return result


def census_columns(result):
    """The census columns of schema/silica_keys.json, as a census gives them.

        {"eras": [era rows], "classes": {name: {"chain", "fields_by_family"}},
         "encode_order": {family: [key, ...]},
         "keys": {key: {"type", "eras", "default", "observed"}}}

    `type` is None for a key that was nil in every archive: its type is then
    the schema author's to give. The schema holds more than this: its written
    columns, and keys of `encode_order` that no archive numbers (a texture
    path that is always nil). F4: the file is merged from this by hand, and
    the opt-in corpus test compares the two.
    """
    columns = {"eras": [], "classes": {}, "encode_order": {}, "keys": {}}
    for row in result["eras"]:
        columns["eras"].append({
            "id": row["id"], "family": row["family"], "encode_family": row["family"],
            "profile": _most(collections.Counter(row["profiles"])), "count": row["count"],
            "key_count": row["key_count"], "key_order": row["key_order"],
            "top_order": row["top_order"], "root_class": row["root_class"],
            "versions": row["versions"], "optional_keys": row["optional_keys"],
            "variants": row["variants"]})
    for name, shapes in result["classes"].items():
        by_family = {}
        for shape in shapes:
            for family in sorted(shape["families"]):
                by_family.setdefault(family, shape["fields"])
        chains = {json.dumps(shape.get("chain")) for shape in shapes}
        held = {"fields_by_family": dict(sorted(by_family.items()))}
        if len(chains) == 1 and shapes[0].get("chain") is not None:
            held["chain"] = shapes[0]["chain"]
        columns["classes"][name] = held
    columns["encode_order"] = {family: merged["order"]
                               for family, merged in result["encode"].items()}
    for key, stats in result["keys"].items():
        kind = stats["type"]
        columns["keys"][key] = {
            "type": None if kind == "nil" else kind,
            "eras": list(stats["eras"]),
            "default": stats["default"],
            "observed": {name: stats[name] for name in OBSERVED_FIELDS}}
    return columns
