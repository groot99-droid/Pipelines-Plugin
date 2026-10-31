"""Build the brush files for a sitting with the iPad, and check them afterwards.

    python -I brushes/pipeline/device_tests.py build sitting-1 [--out DIR] [--known-bad FILE] [--allow-substitutes] [--confirm]
    python -I brushes/pipeline/device_tests.py build sitting-2 [--out DIR] [--allow-substitutes] [--confirm]
    python -I brushes/pipeline/device_tests.py verify sitting-1|sitting-2 [--out DIR] [--allow-substitutes]

Whether the drawing app opens a file this tool wrote can only be learned on a
device (docs/CONTRACTS.md, "Device tests"). A sitting is one visit to the iPad:
a folder of files to take there, and a checklist for the person holding it.

Sitting 1 asks the narrowest question first: does the app open a set whose
container is ours, when everything inside it is not? `build sitting-1` writes,
into brushes/device-tests/sitting-1/ or the folder --out names:

    ROSW-1-control.brushset   the control set, "ROSW 1 Control": eight brushes
                              taken from the library. Every file of every brush
                              is byte for byte the file in the library. Ours
                              are the zip (zip_writer.py), the eight folder
                              names (fresh upper-case version-4 UUIDs) and
                              brushset.plist.
    singles/N-<name>.brush    the same eight, one loose brush file each, to
                              find the brush at fault if the set is refused
    known-bad/KNOWN-BAD_old-designer.brush
                              a copy of a file the old designer wrote, which is
                              malformed: it shows what a refusal looks like.
                              The file is --known-bad, or by default
                              Downloads/Untitled_Brush.brush in the home
                              folder; when there is none, this is left out.
                              The copy gets a name of its own, so that it is
                              never taken for the new "Untitled Brush" that
                              comes back from the iPad
    CHECKLIST.md              the steps for the person holding the iPad
    manifest.json             what was built and from where, with checksums
    returned/                 empty: where the files that come back are put

Sitting 2 asks the next two questions (the design's files F2 and F3): does the
app open an archive our rules wrote, and a brush made from nothing?
`build sitting-2` writes into brushes/device-tests/sitting-2/:

    ROSW-2-edits.brushset     "ROSW 2 Edits": 45 brushes. Each is one of two
                              donors with one setting changed (a few settings
                              are two or three keys that go together), its
                              Brush.archive rule-encoded by brush_model, named
                              "NN key=value". Every other file is the donor's,
                              byte for byte, and only L00 and M00 keep the
                              donor's thumbnail. Donor L is sitting 1's member
                              2 (an E4 brush with its own Shape.png and
                              Grain.png, no jitter, no scatter); donor M is an
                              M220 brush with its own Shape.png and Grain.png.
    ROSW-3-scratch.brushset   "ROSW 3 Scratch & Uni" with its accents and a
                              droplet: six brushes made by
                              brush_model.new_brush, with shapes, grains and
                              a thumbnail written here by png_io
    singles/<code>-<name>.brush   every member of both sets as a loose file
    CHECKLIST.md, manifest.json, returned/   as for sitting 1

Of these git keeps manifest.json, CHECKLIST.md and whatever is put in returned/
(the record of a sitting, which no build can make again). The sets and the
loose copies are scratch and are ignored.

Choosing. Each member that comes from the library is a kind of brush, not a
fixed file: SLOTS (sitting 1) and DONOR_L, DONOR_M and the shape-name slot
(sitting 2) list the kinds. The library is scanned in memory and, for each
slot, the brush that fits is taken; among several that fit, the one a fixed
rule ranks first, so two runs choose alike. A brush's era is
brush_model.detect_era's, from the root key set of its Brush.archive.

When the library holds no brush of the kind a slot asks for, the build is not
complete, and `build` REFUSES: it prints the plan, exits 1 and writes nothing.
--allow-substitutes builds anyway, with the nearest kind (or, for sitting 1,
any other brush) standing in; the printout, the checklist and the manifest
then say SUBSTITUTE, what each stand-in is and what it no longer shows.

`build` is a dry run unless --confirm is given: it scans, chooses, builds
everything in memory, reads the sets back, prints the plan, and writes nothing.
With --confirm it writes the files and then checks them as `verify` does. It
refuses to build over a folder whose returned/ holds files: those belong to
the manifest that is there.

`verify` is a second pass that does its own reading, with zipfile and plistlib:
it goes through neither the builder's reader nor zip_writer. For sitting 1 it
compares every member with the library file the manifest names. For sitting 2
it decodes every archive with brush_model (a scratch archive must decode with
fidelity "byte"), compares each edited archive with its donor's by plistlib
(they may differ only in the brush's name and the keys the member names),
compares every other file with the donor's, byte for byte, and checks the
sha256 of every file against the manifest. Both check the plist, the folder
names and the header fields of every zip entry. Exit 1 when anything differs,
and also when the manifest lists a substitute or an empty slot, unless
--allow-substitutes is given.

Brush files are data from strangers. Each is opened with zipfile where it lies
and read, entry by entry, into memory, under the caps and by the member rules
of container.py (docs/CONTRACTS.md, F3). No entry is ever extracted to disk
and no entry name is used as a path. Run this as
`python -I brushes/pipeline/device_tests.py ...`.

Exit codes: 0 ok, 1 refused or failed, 2 usage or environment.
Standard library only.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import datetime
import hashlib
import io
import json
import math
import os
import plistlib
import re
import struct
import sys
import time
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import png_io  # noqa: E402
import zip_writer  # noqa: E402
from bplist import BrushModelError, CodecError, ContainerError  # noqa: E402

SITTING_1 = "sitting-1"
SITTING_2 = "sitting-2"
SITTINGS = (SITTING_1, SITTING_2)
OUT_HOME = "device-tests"                   # under the brushes/ root

SET_FILE = "ROSW-1-control.brushset"
SET_NAME = "ROSW 1 Control"
EDITS_FILE = "ROSW-2-edits.brushset"
EDITS_NAME = "ROSW 2 Edits"
SCRATCH_FILE = "ROSW-3-scratch.brushset"
SCRATCH_NAME = "ROSW 3 Scratch & Ünï \U0001f4a7"
SINGLES_DIR = "singles"
KNOWN_BAD_DIR = "known-bad"
RETURNED_DIR = "returned"
CHECKLIST_NAME = "CHECKLIST.md"
MANIFEST_NAME = "manifest.json"
MANIFEST_SCHEMA = "rosw-brushes-device-test/1"
MANIFEST_SCHEMA_2 = "rosw-brushes-device-test-2/1"
KNOWN_BAD_DEFAULT = ("Downloads", "Untitled_Brush.brush")      # under the home folder
# The name the known-bad copy gets here. The app names a brush from its archive,
# not from its file, so the name is ours to choose; and the brush that comes
# back in the return leg is called "Untitled Brush", one character away from
# the file the old designer wrote.
KNOWN_BAD_STEM = "KNOWN-BAD_old-designer"
KNOWN_BAD_SUFFIXES = (".brush", ".brushset")
FETCH_COMMAND = "python -I brushes/pipeline/fetch_base_library.py fetch --confirm"

LIBRARY_PARTS = ("user", "official")
BRUSH_SUFFIXES = (".brush", ".brushset")
SET_PLIST = container.SET_PLIST
BRUSH_ARCHIVE = container.ARCHIVE
SHAPE = container.SHAPE
GRAIN = container.GRAIN
THUMBNAIL = container.THUMBNAIL
SUB_ARCHIVE = f"{container.SUB}/{container.ARCHIVE}"
RESET_ARCHIVE = f"{container.RESET}/{container.ARCHIVE}"
RESET_SUB_ARCHIVE = f"{container.RESET}/{container.SUB}/{container.ARCHIVE}"
AUTHOR_FOLDER = container.AUTHOR_FOLDER
SIGNATURE_FOLDER = container.SIGNATURE_FOLDER

# The reader's caps and member rules are container.py's (docs/CONTRACTS.md F3;
# spec.yaml format.caps): the same objects, not copies. Junk is part of no brush
# folder; every other entry of a folder is a member and is carried, a zero-byte
# `.empty` and an unknown file among them.
CAPS = container.CAPS
JUNK_FOLDERS = container.JUNK_FOLDERS
JUNK_NAMES = container.JUNK_NAMES
EMPTY = container.EMPTY
ZIP_MAGIC = container.ZIP_MAGIC
LFS_HEADER = container.LFS_HEADER
ZIP_ERRORS = container.ZIP_ERRORS
LFS_POINTER_MAX = 1024
# Folders of the library on disk that hold no brush file to scan.
SKIPPED_LIBRARY_FOLDERS = frozenset({"__macosx", "_docs"})
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

STEADY_KEYS = ("plotJitter", "shapeScatter", "shapeRandomise")
STEADY_PREFIX = "dynamicsJitter"

# The form of a folder name in a set: an upper-case version-4 UUID.
UUID_FORM = re.compile(r"[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}")

# What every entry of a zip made here must carry, by zipfile's names for the
# fields (zip_writer.py says why). Written out here, not taken from the writer:
# the second pass checks the writer against them. Sitting 1 writes every entry
# in the one form below; sitting 2 writes each donor file in the form its
# source zip used, so there only the fields that every form shares are fixed
# and the method and flags must be one of FORM_FIELDS.
HEADER_FIELDS = (
    ("method", "compress_type", 8),
    ("flags", "flag_bits", 0x0006),
    ("made-by system", "create_system", 0),
    ("made-by version", "create_version", 0),
    ("needs version", "extract_version", 20),
    ("external attr", "external_attr", 0),
    ("extra", "extra", b""),
    ("comment", "comment", b""),
)
COMMON_FIELDS = HEADER_FIELDS[2:]
FORM_FIELDS = {"fast": (8, 0x0006), "normal": (8, 0x0000), "stored": (0, 0x0000)}

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."


class DeviceTestError(Exception):
    """The command cannot go on. Exit 1."""

    exit_code = bc.EXIT_REFUSED


class EnvironmentProblem(DeviceTestError):
    """A missing folder, an empty library, a Git LFS pointer, a bad --out. Exit 2."""

    exit_code = bc.EXIT_USAGE


class Unreadable(Exception):
    """One file or one brush that is passed over, with the reason."""


# ── small helpers ────────────────────────────────────────────────────────────

def show(text):
    """Text that is safe to print: control characters become `?`."""
    return "".join(ch if ch.isprintable() else "?" for ch in str(text))


def fold(text):
    """A name for comparing: accents removed, lower case, outer spaces gone."""
    plain = "".join(ch for ch in unicodedata.normalize("NFKD", str(text))
                    if not unicodedata.combining(ch))
    return plain.lower().strip()


def file_stem(text, limit=40):
    """A brush name as part of a file name: accents folded, and every character
    outside `A-Z a-z 0-9 . _ -` made `_`."""
    plain = "".join(ch for ch in unicodedata.normalize("NFKD", str(text))
                    if not unicodedata.combining(ch))
    stem = re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9._-]", "_", plain)).strip("._")[:limit].strip("._")
    return stem or "brush"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def png_size(data):
    """(width, height) from a PNG's header, or None."""
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR" or len(data) < 24:
        return None
    return struct.unpack(">II", data[16:24])


def _xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def brushset_plist(name, folders):
    """The bytes of a set's brushset.plist, in the exact form the app's own sets
    use: XML, UTF-8, line feeds, tabs, the key `brushes` (the folder names in
    display order) and then the key `name`."""
    if not folders:
        raise DeviceTestError("a set needs at least one brush")
    rows = "".join(f"\t\t<string>{_xml(folder)}</string>\n" for folder in folders)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
            '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            '<plist version="1.0">\n<dict>\n\t<key>brushes</key>\n\t<array>\n'
            + rows +
            "\t</array>\n\t<key>name</key>\n\t<string>" + _xml(name) + "</string>\n"
            "</dict>\n</plist>\n").encode("utf-8")


def fresh_uuid():
    return container.new_uuid()


def _why(exc):
    """The words of a codec error, for a person."""
    return getattr(exc, "detail", "") or getattr(exc, "code", "") or str(exc)


def _folder_names(make, count, taken):
    """`count` fresh folder names from `make`, each an upper-case version-4
    UUID that is not in `taken` (which grows)."""
    names = []
    for _ in range(count):
        for _ in range(64):
            folder = make()
            if isinstance(folder, str) and UUID_FORM.fullmatch(folder) and folder not in taken:
                break
        else:
            raise DeviceTestError("no fresh upper-case version-4 UUID could be made for a folder name")
        taken.add(folder)
        names.append(folder)
    return names


# ── reading the library ──────────────────────────────────────────────────────

def library_files(library):
    """(stored POSIX path, path) of every brush file under user/ and official/,
    in one fixed order. Nothing is opened."""
    found = []
    for part in LIBRARY_PARTS:
        top = Path(library) / part
        if not top.is_dir():
            continue
        for folder, folders, names in os.walk(top):
            folders[:] = [name for name in folders if name.lower() not in SKIPPED_LIBRARY_FOLDERS]
            for name in names:
                if name.lower().endswith(BRUSH_SUFFIXES):
                    path = Path(folder) / name
                    found.append((path.relative_to(library).as_posix(), path))
    return sorted(found, key=lambda item: (item[0].lower(), item[0]))


def check_file(path, stored):
    """Look at one library file before it is opened as a zip. Unreadable when it
    is not a regular file, is over the cap or is not a zip; EnvironmentProblem
    when it is a Git LFS pointer left where the brush file should be."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise Unreadable("not a regular file")
    size = path.stat().st_size
    if size > CAPS["upload_bytes"]:
        raise Unreadable(f"{size:,} bytes; the cap is {CAPS['upload_bytes']:,}")
    with open(path, "rb") as handle:
        head = handle.read(len(LFS_HEADER))
    if size <= LFS_POINTER_MAX and head == LFS_HEADER:
        raise EnvironmentProblem(f"{show(stored)} is a Git LFS pointer, not a brush file. "
                                 "Run `git lfs pull` and try again.")
    if head[:4] not in ZIP_MAGIC:
        raise Unreadable("not a zip file, whatever its name says")


@contextlib.contextmanager
def open_zip(source):
    """`with open_zip(f) as (archive, listing):` for a seekable binary file (an
    open file, or io.BytesIO over bytes). `listing` is container.list_entries':
    the entries that count (files only, the first of a repeated name, no junk).
    Its directory is checked against the caps by container.check_declared
    before anything is inflated. Unreadable otherwise."""
    try:
        archive = zipfile.ZipFile(source)
    except ZIP_ERRORS as exc:
        raise Unreadable(f"it cannot be opened as a zip ({type(exc).__name__})") from None
    with archive:
        try:
            listing = container.list_entries(archive.infolist(), limits=CAPS)
            container.check_declared(listing.kept, limits=CAPS)
        except CodecError as exc:               # LimitExceeded
            raise Unreadable(_why(exc)) from None
        yield archive, listing


@contextlib.contextmanager
def open_library_file(path, stored):
    """`with open_library_file(path, stored) as (archive, listing):` for one
    brush file of the library. Nothing is extracted: zipfile reads the
    directory, and each entry asked for is inflated into memory."""
    check_file(path, stored)
    with open(path, "rb") as handle, open_zip(handle) as opened:
        yield opened


def read_entry(archive, info, cap, budget=None, cap_name="entry_bytes"):
    """One entry's bytes, in memory, by container.read_member, or Unreadable.
    Never more than `cap` bytes."""
    try:
        return container.read_member(archive, info, cap, budget, cap_name=cap_name, limits=CAPS)
    except CodecError as exc:
        raise Unreadable(f"{show(info.orig_filename)}: {_why(exc)}") from None


def folder_members(listing, prefix):
    """The members of one brush folder: ([(path inside the folder, entry)] in
    the order the zip stores them, [(entry name, why)] refused).

    The member rule is container.py's (F3 "Reading"): `listing` has already
    left out folder entries, junk and the later entries of a repeated name;
    every other entry under `prefix` is a member, a zero-byte `.empty` and a
    file nobody knows among them. An entry the reader refuses (an encrypted
    one, or a name that is absolute or holds `..` or a backslash) is listed as
    refused: the folder cannot be carried whole.
    """
    kept, refused = [], []
    for info in listing.kept:
        name = info.orig_filename
        if not name.startswith(prefix) or name == prefix:
            continue
        problem = container.hostile(name) or ("an encrypted entry" if info.flag_bits & 0x1 else "")
        if problem:
            refused.append((name, problem))
            continue
        kept.append((name[len(prefix):], info))
    return kept, refused


def layout(archive, listing, budget=None):
    """(set name or None, [(folder name, prefix of its entries)]) for an open
    container, sniffed by container.sniff: a set's folders in the order its
    plist lists them, or the one folder of a loose brush, whose prefix is empty."""
    names = {info.orig_filename for info in listing.kept}
    kind, top = container.sniff(names)
    if kind == "brush":
        return None, [("", "")]
    if kind != "set":
        raise Unreadable(f"it holds no {SET_PLIST} and no {BRUSH_ARCHIVE}")
    info = next(info for info in listing.kept if info.orig_filename == top + SET_PLIST)
    raw = read_entry(archive, info, CAPS["archive_bytes"], budget, "archive_bytes")
    try:
        name, folders, _, _ = container.parse_plist(raw)
    except ContainerError as exc:
        raise Unreadable(f"its {SET_PLIST} cannot be used: {_why(exc)}") from None
    listed = []
    for folder in folders:
        if folder and "/" not in folder and folder not in (".", "..") and folder not in listed:
            listed.append(folder)
    return name, [(folder, f"{top}{folder}/") for folder in listed]


def archive_facts(data):
    """What choosing needs from one Brush.archive: {"keys", "key_names",
    "root", "name", "strings"}. Read with plistlib, which is enough to name the
    root keys and read plain values; the era is brush_model.detect_era's.
    Unreadable says, in plain words, what is wrong."""
    if not data.startswith(b"bplist00"):
        raise Unreadable("its Brush.archive is not a binary property list")
    try:
        top = plistlib.loads(data, fmt=plistlib.FMT_BINARY)
    except Exception:                           # anything a stranger's plist can raise
        raise Unreadable("its Brush.archive is a property list that cannot be read") from None
    if not isinstance(top, dict):
        found = {str: "a single piece of text", list: "a bare list", bytes: "a run of raw bytes",
                 bool: "a single yes or no", int: "a single number",
                 float: "a single number"}.get(type(top), "something else")
        raise Unreadable(f"its Brush.archive holds {found} where a brush's settings should be, "
                         "not the keyed archive a brush file carries")
    objects = top.get("$objects")
    head = top.get("$top")
    pointer = head.get("root") if isinstance(head, dict) else None
    if (top.get("$archiver") != "NSKeyedArchiver" or not isinstance(objects, list)
            or not isinstance(pointer, plistlib.UID) or not 0 < pointer.data < len(objects)
            or not isinstance(objects[pointer.data], dict)):
        raise Unreadable("its Brush.archive is not the keyed archive a brush holds")
    root = objects[pointer.data]

    def text(key):
        value = root.get(key)
        if isinstance(value, plistlib.UID):
            value = objects[value.data] if 0 < value.data < len(objects) else None
        if isinstance(value, dict):                 # an NSMutableString instance
            value = value.get("NS.string")
        return value if isinstance(value, str) else None

    strings = {key: text(key) for key in ("bundledShapePath", "bundledGrainPath", "authorName")}
    return {"keys": len(root), "key_names": [key for key in root if isinstance(key, str)],
            "root": root, "name": text("name") or "", "strings": strings}


def _zero(value):
    return isinstance(value, (bool, int, float)) and value == 0


class Candidate:
    """One brush folder found in the library, as plain facts. No image bytes."""

    def __init__(self, source, set_name, position, folder, prefix, members, archive, facts):
        root = facts["root"]
        self.container = source                 # library-relative POSIX path of the file
        self.library = source.split("/")[0]     # "user" | "official"
        self.pack = source.split("/")[1] if source.count("/") >= 2 else ""
        self.stem = source.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        self.set_name = set_name                # None for a loose brush
        self.position = position                # place in the set's plist order
        self.folder = folder                    # the folder name in the source zip; "" when loose
        self.prefix = prefix
        self.paths = tuple(path for path, _ in members)
        self.sizes = {path: info.file_size for path, info in members}
        self.total = sum(self.sizes.values())
        self.stored = sum(1 for _, info in members if info.compress_type == zipfile.ZIP_STORED)
        self.archive_sha256 = sha256(archive)
        self.keys = facts["keys"]
        # The era by its exact root key set (F3 "Eras"); X<count> for a set no
        # era has, whose family is its nearest era's.
        self.era, self.era_exact, _, _ = brush_model.detect_era(facts["key_names"])
        self.nearest = self.era if self.era_exact else brush_model.nearest_era(facts["key_names"])
        self.family = brush_model.family_of(self.nearest)
        self.name = facts["name"]
        self.version = root.get("version") if isinstance(root.get("version"), int) else None
        self.bundled_shape = facts["strings"]["bundledShapePath"]
        self.bundled_grain = facts["strings"]["bundledGrainPath"]
        self.author_name = facts["strings"]["authorName"]
        self.stamp = root.get("stamp") is True
        jitters = [value for key, value in root.items()
                   if key in STEADY_KEYS or (isinstance(key, str) and key.startswith(STEADY_PREFIX))]
        # No jitter and no scatter anywhere; and the weaker claim, on the stroke path only.
        self.steady = ("plotJitter" in root and "shapeScatter" in root
                       and all(_zero(value) for value in jitters))
        self.calm = _zero(root.get("plotJitter", 1)) and _zero(root.get("shapeScatter", 1))

    def has(self, path):
        return path in self.sizes

    def has_file_under(self, folder):
        """A real file sits under `folder`: one with bytes in it that is not a
        `.empty` placeholder. Some official sets keep an `AuthorPicture/.empty`
        where a picture would be; that folder carries no picture."""
        return any(path.startswith(folder) and path.rsplit("/", 1)[-1] != EMPTY
                   and self.sizes[path] > 0 for path in self.paths)

    def files_under(self, folder):
        """[(path, size)] of everything under `folder`, placeholders included."""
        return [(path, self.sizes[path]) for path in self.paths if path.startswith(folder)]

    @property
    def has_shape(self):
        return self.has(SHAPE)

    @property
    def has_grain(self):
        return self.has(GRAIN)

    @property
    def has_thumbnail(self):
        return self.has(THUMBNAIL)

    @property
    def dual(self):
        return self.has(SUB_ARCHIVE)

    @property
    def reset(self):
        return self.has(RESET_ARCHIVE)

    @property
    def reset_dual(self):
        return self.has(RESET_SUB_ARCHIVE)

    @property
    def author_picture(self):
        return self.has_file_under(AUTHOR_FOLDER)

    @property
    def signature(self):
        return self.has_file_under(SIGNATURE_FOLDER)

    @property
    def empties(self):
        return sum(1 for path in self.paths if path.rsplit("/", 1)[-1] == EMPTY)

    @property
    def named_textures(self):
        """Textures kept in the folder under their own names, which the archive points at."""
        return [name for name in (self.bundled_shape, self.bundled_grain) if name and self.has(name)]

    @property
    def names_only(self):
        """It carries no shape image and names one that ships inside the app."""
        return bool(self.bundled_shape) and not self.has_shape and not self.named_textures

    @property
    def era_text(self):
        return self.era if self.era_exact else f"{self.era} (nearest {self.nearest})"

    @property
    def where(self):
        return self.container + (f"!/{self.folder}" if self.folder else "")

    @property
    def order(self):
        return (self.container.lower(), self.container, self.position)


class Scan:
    """What a pass over the library found."""

    def __init__(self):
        self.candidates = []
        self.files = dict.fromkeys(LIBRARY_PARTS, 0)
        self.brushes = dict.fromkeys(LIBRARY_PARTS, 0)
        self.skipped = []                       # (where, why)


def _candidate(archive, listing, stored, set_name, position, folder, prefix, budget):
    members, refused = folder_members(listing, prefix)
    if refused:
        name, why = refused[0]
        raise Unreadable(f"{show(name)}: {why}")
    by_path = dict(members)
    if BRUSH_ARCHIVE not in by_path:
        raise Unreadable(f"it holds no {BRUSH_ARCHIVE}")
    for path in by_path:
        try:
            zip_writer.check_name(path)
        except zip_writer.ZipWriteError:
            raise Unreadable(f"it holds an entry name this tool does not write: {show(path)!r}") from None
    data = read_entry(archive, by_path[BRUSH_ARCHIVE], CAPS["archive_bytes"], budget, "archive_bytes")
    return Candidate(stored, set_name, position, folder, prefix, members, data, archive_facts(data))


def scan_library(library):
    """Every brush folder in the library, as a Scan. Of each file only the
    directory, the set's plist and the Brush.archive entries are read."""
    scan = Scan()
    for stored, path in library_files(library):
        part = stored.split("/", 1)[0]
        scan.files[part] += 1
        budget = container.Budget(CAPS["total_bytes"])
        try:
            with open_library_file(path, stored) as (archive, listing):
                set_name, folders = layout(archive, listing, budget)
                for position, (folder, prefix) in enumerate(folders):
                    try:
                        scan.candidates.append(_candidate(archive, listing, stored, set_name,
                                                          position, folder, prefix, budget))
                        scan.brushes[part] += 1
                    except Unreadable as exc:
                        where = stored + (f"!/{folder}" if folder else "")
                        scan.skipped.append((show(where), str(exc)))
        except Unreadable as exc:
            scan.skipped.append((show(stored), str(exc)))
    return scan


def load_folder(library, candidate):
    """The container.BrushFolder of one chosen brush, read again from its
    library file by container.read_brush or read_brushset: its members in the
    order that file stores them, each with the form and date it was stored with."""
    path = Path(library).joinpath(*candidate.container.split("/"))
    try:
        check_file(path, candidate.container)  # a regular file, a zip, under the upload cap
        with open(path, "rb") as handle:
            data = handle.read()
        if len(data) > CAPS["upload_bytes"]:
            raise Unreadable(f"{len(data):,} bytes; the cap is {CAPS['upload_bytes']:,}")
        if candidate.set_name is None:
            folder = container.read_brush(data, hint=candidate.container, limits=CAPS)
        else:
            brush_set = container.read_brushset(data, hint=candidate.container, limits=CAPS)
            folder = dict(brush_set.brushes).get(candidate.folder)
    except (Unreadable, CodecError, OSError) as exc:
        raise DeviceTestError(f"{show(candidate.where)} cannot be read again: {_why(exc)}") from None
    if (folder is None or tuple(folder.paths()) != candidate.paths
            or sha256(folder.archive or b"") != candidate.archive_sha256):
        raise DeviceTestError(f"{show(candidate.where)} changed while it was being read")
    return folder


def load_member(library, candidate):
    """[(path inside the folder, bytes)] of one chosen brush, read again from
    its library file, in the order that file stores them."""
    return load_folder(library, candidate).pairs()


# ── which eight ──────────────────────────────────────────────────────────────

class Tier:
    """One kind of brush a slot accepts. The first tier of a slot is the kind
    the plan asks for; each later one is a substitute, and `lost` says what a
    brush of that kind no longer shows."""

    def __init__(self, what, test, lost=""):
        self.what = what
        self.test = test
        self.lost = lost


class Slot:
    """One member of a test set that is taken from the library.

    wanted   the kind of brush the plan asks for, in words
    shows    what that member is in the set to show
    tiers    the kinds accepted, nearest first; each names a feature a brush has
    rank     among brushes of one kind, the lowest value is taken
    absent   what the set no longer shows when nothing of any kind is found
    fill     when nothing of any kind is found and some other brush fills the
             slot: which one, lowest value first. None for the common rule (an
             era the set lacks, then the fewest keys)
    """

    def __init__(self, number, key, wanted, shows, tiers, rank, absent, fill=None):
        self.number = number
        self.key = key
        self.wanted = wanted
        self.shows = shows
        self.tiers = tiers
        self.rank = rank
        self.absent = absent
        self.fill = fill


def _official(candidate, pack=None, stem=None):
    return (candidate.library == "official" and (pack is None or candidate.pack == pack)
            and (stem is None or candidate.stem == stem))


SLOTS = (
    Slot(1, "e0",
         'an E0 brush (52 keys), such as "Broken Conté" from the Insecto charcoal pack',
         "the oldest format: 52 keys, a name stored as UTF-16, a 440 x 276 thumbnail",
         [Tier("E0 brush (52 keys)", lambda c: c.era == "E0")],
         lambda c: (fold(c.name) != "broken conte", c.pack != "insecto-charcoal",
                    not c.has_thumbnail, c.total),
         "the 52-key format",
         fill=lambda c: (c.family != "legacy", c.keys, not c.has_thumbnail, c.total)),
    Slot(2, "e4",
         "an E4 brush (101 keys) that carries its own Shape.png and Grain.png and has "
         "no jitter and no scatter",
         "the plain legacy brush; the later test sets edit this one",
         [Tier("E4 brush with its own shape and grain and every jitter and scatter setting at zero",
               lambda c: c.era == "E4" and c.has_shape and c.has_grain and c.steady),
          Tier("E4 brush with its own shape and grain whose stroke jitter and scatter are zero",
               lambda c: c.era == "E4" and c.has_shape and c.has_grain and c.calm,
               "Another of its jitter settings is not zero."),
          Tier("E4 brush with its own shape and grain",
               lambda c: c.era == "E4" and c.has_shape and c.has_grain,
               "It has jitter or scatter, so it is a poorer brush to edit later."),
          Tier("legacy brush with its own shape and grain",
               lambda c: c.family == "legacy" and c.has_shape and c.has_grain,
               "It is not the 101-key format.")],
         lambda c: (not c.has_thumbnail, c.stamp, c.total),
         "a legacy brush that carries both of its images"),
    Slot(3, "e3",
         'the E3 brush "IGB 6B Pencil" (88 keys), which carries no image and names two '
         "textures that ship inside the app",
         "whether texture names from older versions of the app still resolve",
         [Tier('E3 brush named "IGB 6B Pencil" that only names its textures',
               lambda c: (c.era == "E3" and fold(c.name) == "igb 6b pencil" and c.names_only
                          and not c.has_grain)),
          Tier("E3 brush that only names its textures",
               lambda c: c.era == "E3" and c.names_only and not c.has_grain,
               "It shows the same thing with other texture names."),
          Tier("legacy brush that only names its shape",
               lambda c: c.family == "legacy" and c.names_only,
               "It is not the 88-key format, or it carries its own grain.")],
         lambda c: (not c.bundled_grain, c.has_grain, not c.has_thumbnail, c.total),
         "texture names that ship inside the app"),
    Slot(4, "dual",
         "a modern dual brush (220 keys), whose second brush is in a Sub01/ folder",
         "whether a Sub01/ folder is carried",
         [Tier("220-key brush with a Sub01/ folder", lambda c: c.era == "M220" and c.dual),
          Tier("modern brush with a Sub01/ folder", lambda c: c.family == "modern" and c.dual,
               "It is not the 220-key format."),
          Tier("brush with a Sub01/ folder", lambda c: c.dual, "It is not a modern brush.")],
         lambda c: (c.reset, not c.has_thumbnail, c.author_picture or c.signature, c.total),
         "dual brushes"),
    Slot(5, "no-thumbnail",
         "a modern brush from the Procreate 5 Inking set that has no thumbnail",
         "whether the app draws a preview of its own when the file has none",
         [Tier("modern brush without a thumbnail in official/procreate-5/p5-inking.brushset",
               lambda c: (_official(c, "procreate-5", "p5-inking") and c.family == "modern"
                          and not c.has_thumbnail)),
          Tier("modern brush without a thumbnail", lambda c: c.family == "modern" and not c.has_thumbnail,
               "It is from another set; it shows the same thing."),
          Tier("brush without a thumbnail", lambda c: not c.has_thumbnail,
               "It is not a modern brush.")],
         lambda c: (c.dual, c.reset, c.total),
         "a missing thumbnail"),
    Slot(6, "author",
         "a brush that carries an author picture and a signature",
         "whether the maker's picture and signature are carried",
         [Tier("brush with AuthorPicture/ and Signature/ files",
               lambda c: c.author_picture and c.signature),
          Tier("brush with one of AuthorPicture/ and Signature/",
               lambda c: c.author_picture or c.signature, "It carries only one of the two.")],
         lambda c: (not c.author_name, c.dual, c.reset, not c.has_thumbnail, c.total),
         "author files"),
    Slot(7, "reset",
         "a Sweet Treats brush that has a reset copy with a second brush in it (Reset/Sub01/)",
         "the deepest folder tree a brush has",
         [Tier("brush with Reset/Sub01/ in official/sweet-treats/",
               lambda c: _official(c, "sweet-treats") and c.reset_dual),
          Tier("brush with Reset/Sub01/", lambda c: c.reset_dual,
               "It is not from Sweet Treats (173 keys)."),
          Tier("brush with a Reset/ folder", lambda c: c.reset,
               "Its Reset/ folder holds no second brush.")],
         lambda c: (not c.has_thumbnail, c.total),
         "Reset/ folders"),
    Slot(8, "earth",
         "a brush from the Earth set (242 keys, `version` 4), with a texture kept under "
         "its own file name and zero-byte `.empty` files",
         "the newest format the library holds",
         [Tier("brush in official/earth/", lambda c: _official(c, "earth")),
          Tier("242-key brush", lambda c: c.era == "M242", "It is not from the Earth set.")],
         lambda c: (not c.named_textures, not c.empties, c.era != "M242", not c.has_thumbnail,
                    c.total),
         "the 242-key format"),
)


class Pick:
    """A slot and the brush chosen for it. `tier` is 0 for the kind the plan
    asks for, 1 and up for a substitute kind, None for a brush that fits no
    kind of the slot at all."""

    def __init__(self, slot, candidate, tier):
        self.slot = slot
        self.candidate = candidate
        self.tier = tier

    @property
    def as_specified(self):
        return self.tier == 0

    @property
    def note(self):
        """Why this brush stands in, and what it no longer shows. Empty when as specified."""
        if self.tier == 0:
            return ""
        missing = f"The library holds no {self.slot.tiers[0].what}."
        if self.tier is None:
            return (f"{missing} Nothing near it was found either, so another brush from the "
                    f"library fills the slot. It shows nothing about {self.slot.absent}.")
        tier = self.slot.tiers[self.tier]
        return f"{missing} This is the nearest kind found: a {tier.what}. {tier.lost}"

    @property
    def shows(self):
        """What this brush shows in the set: the slot's purpose when it is the
        kind asked for; for a stand-in, what it is and what it no longer shows.
        Never the slot's purpose for a brush that does not serve it."""
        if self.tier == 0:
            return self.slot.shows
        if self.tier is None:
            return f"SUBSTITUTE: it shows nothing about {self.slot.absent}"
        tier = self.slot.tiers[self.tier]
        return f"SUBSTITUTE: a {tier.what}. {tier.lost}".rstrip()


def choose(candidates):
    """([Pick] in slot order, [slots left empty]).

    The nearest kinds are served first, across all slots, so that a far
    substitute for one slot never takes the brush another slot asks for: first
    every slot's own kind, then every slot's first substitute kind, then every
    second one, and so on. A slot still empty after that is filled with some
    brush not yet taken. One brush (one Brush.archive) is taken once, however
    many copies of it the library holds.
    """
    picks, taken = {}, set()

    def take(slot, tier, pool, rank):
        best = min(pool, key=lambda c: (rank(c), c.order))
        picks[slot.number] = Pick(slot, best, tier)
        taken.add(best.archive_sha256)

    def free(test):
        return [c for c in candidates if c.archive_sha256 not in taken and test(c)]

    for index in range(max(len(slot.tiers) for slot in SLOTS)):
        for slot in SLOTS:
            if slot.number in picks or index >= len(slot.tiers):
                continue
            pool = free(slot.tiers[index].test)
            if pool:
                take(slot, index, pool, slot.rank)
    for slot in SLOTS:
        pool = free(lambda c: True)
        if slot.number in picks or not pool:
            continue
        present = {pick.candidate.era for pick in picks.values()}
        common = lambda c: (c.era in present, c.keys, not c.has_thumbnail, c.total)  # noqa: E731
        take(slot, None, pool, slot.fill or common)
    return ([picks[slot.number] for slot in SLOTS if slot.number in picks],
            [slot for slot in SLOTS if slot.number not in picks])


# ── building ─────────────────────────────────────────────────────────────────

class Member:
    """A chosen brush with its files and the names it gets in our set."""

    def __init__(self, pick, files, folder):
        self.pick = pick
        self.slot = pick.slot
        self.candidate = pick.candidate
        self.files = files                      # [(path inside the folder, bytes)]
        self.uuid = folder
        self.single = f"{SINGLES_DIR}/{pick.slot.number}-{file_stem(pick.candidate.name)}.brush"

    @property
    def thumbnail_size(self):
        return png_size(dict(self.files).get(THUMBNAIL, b""))


class Build:
    """Everything a sitting's folder will hold, in memory."""

    sitting = SITTING_1

    def __init__(self):
        self.scan = None
        self.members = []
        self.unfilled = []
        self.set_bytes = b""
        self.singles = {}                       # relative path -> bytes
        self.known_bad = None                   # {"file", "data", "broken", "finding"}
        self.known_bad_note = ""
        self.checklist = ""
        self.manifest = {}

    @property
    def substitutes(self):
        return [member for member in self.members if not member.pick.as_specified]

    @property
    def complete(self):
        """Every slot holds the kind of brush the plan asks for: this is the control set."""
        return bool(self.members) and not self.substitutes and not self.unfilled

    def files(self):
        """{relative POSIX path: bytes} of every file to write, the manifest last."""
        out = dict(self.singles)
        if self.known_bad:
            out[self.known_bad["file"]] = self.known_bad["data"]
        out[SET_FILE] = self.set_bytes
        out[CHECKLIST_NAME] = self.checklist.encode("utf-8")
        out[MANIFEST_NAME] = bc.json_text(self.manifest).encode("utf-8")
        return out


def diagnose(data):
    """(looks broken, one sentence) for a file that is said to be a bad brush."""
    if data[:4] not in ZIP_MAGIC:
        return True, "it is not a zip file"
    try:
        with open_zip(io.BytesIO(data)) as (archive, listing):
            for entry in listing.kept:          # what the reader refuses (F3 "Reading")
                problem = (container.hostile(entry.orig_filename)
                           or ("an encrypted entry" if entry.flag_bits & 0x1 else ""))
                if problem:
                    return True, f"it holds {problem}: {show(entry.orig_filename)!r}"
            info = next((i for i in listing.kept
                         if i.orig_filename.rsplit("/", 1)[-1] == BRUSH_ARCHIVE), None)
            if info is None:
                return True, f"it holds no {BRUSH_ARCHIVE}"
            facts = archive_facts(read_entry(archive, info, CAPS["archive_bytes"], None, "archive_bytes"))
    except Unreadable as exc:
        return True, str(exc)
    return False, f"its {BRUSH_ARCHIVE} reads as an ordinary brush archive of {facts['keys']} keys"


def read_known_bad(path):
    """(the known-bad entry or None, a note for the printout)."""
    if path is None:
        return None, "no known-bad file was asked for"
    path = Path(os.path.expanduser(str(path)))
    if not path.is_file():
        return None, f"there is no file at {path}; known-bad/ is left out"
    if path.stat().st_size > CAPS["upload_bytes"]:
        return None, f"{path} is over {CAPS['upload_bytes']:,} bytes; known-bad/ is left out"
    with open(path, "rb") as handle:
        data = handle.read()
    stem, dot, extension = path.name.rpartition(".")
    original = f"{file_stem(stem, 80)}.{file_stem(extension, 12)}" if dot and stem else file_stem(path.name, 80)
    suffix = next((s for s in KNOWN_BAD_SUFFIXES if path.name.lower().endswith(s)), KNOWN_BAD_SUFFIXES[0])
    broken, finding = diagnose(data)
    entry = {"file": f"{KNOWN_BAD_DIR}/{KNOWN_BAD_STEM}{suffix}", "original_name": original,
             "data": data, "broken": broken, "finding": finding}
    note = f"copied from {path} as {entry['file']}: {finding}"
    if not broken:
        note += "  WARNING: nothing wrong was found with it, so it may not be refused"
    return entry, note


def _read_back(data, entries):
    """Open a zip we just made with zipfile and compare it with what went in."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            found = [(info.orig_filename, archive.read(info)) for info in archive.infolist()]
    except ZIP_ERRORS as exc:
        raise DeviceTestError(f"a zip made here cannot be read back ({type(exc).__name__}: {exc})") from None
    if found != [(name, bytes(content)) for name, content in entries]:
        raise DeviceTestError("a zip made here does not read back as what was put into it")


def _stamp(date_time):
    return tuple(date_time) if date_time else datetime.datetime.now().timetuple()[:6]


def build_sitting(library, *, known_bad=None, date_time=None, new_uuid=None):
    """Scan the library, choose the members and build every file of sitting 1 in
    memory. Writes nothing. `date_time` (the date of the zip entries, now by
    default) and `new_uuid` (a callable giving a folder name) exist for the tests.
    """
    library = Path(library)
    if not library.is_dir():
        raise EnvironmentProblem(f"there is no library at {library}")
    build = Build()
    build.scan = scan_library(library)
    if not build.scan.candidates:
        raise EnvironmentProblem(f"no brush file that can be read was found under "
                                 f"{library / LIBRARY_PARTS[0]} or {library / LIBRARY_PARTS[1]}")
    picks, build.unfilled = choose(build.scan.candidates)
    stamp = _stamp(date_time)
    taken = {pick.candidate.folder for pick in picks}
    folders = _folder_names(new_uuid or fresh_uuid, len(picks), taken)
    for pick, folder in zip(picks, folders):
        build.members.append(Member(pick, load_member(library, pick.candidate), folder))

    entries = [(f"{member.uuid}/{inside}", data)
               for member in build.members for inside, data in member.files]
    entries.append((SET_PLIST, brushset_plist(SET_NAME, [member.uuid for member in build.members])))
    try:
        build.set_bytes = zip_writer.write_zip(entries, date_time=stamp)
        _read_back(build.set_bytes, entries)
        for member in build.members:
            build.singles[member.single] = zip_writer.write_zip(member.files, date_time=stamp)
            _read_back(build.singles[member.single], member.files)
    except zip_writer.ZipWriteError as exc:
        raise DeviceTestError(f"the set cannot be written: {exc}") from None

    build.known_bad, build.known_bad_note = read_known_bad(known_bad)
    build.checklist = render_checklist(build)
    build.manifest = make_manifest(build)
    return build


def make_manifest(build):
    """What was built and from where. No absolute path and no date: only names
    inside the library and inside the sitting's folder, sizes and sha256s."""
    members = []
    for member in build.members:
        candidate = member.candidate
        members.append({
            "slot": member.slot.number,
            "slot_kind": member.slot.key,
            "wanted": member.slot.wanted,
            "slot_shows": member.slot.shows,
            "as_specified": member.pick.as_specified,
            "shows": member.pick.shows,
            "note": member.pick.note,
            "name": candidate.name,
            "era": candidate.era,
            "family": candidate.family,
            "keys": candidate.keys,
            "source": {"container": candidate.container, "set": candidate.set_name,
                       "folder": candidate.folder, "prefix": candidate.prefix,
                       "position": candidate.position},
            "uuid": member.uuid,
            "single": member.single,
            "single_sha256": sha256(build.singles[member.single]),
            "files": [{"path": inside, "bytes": len(data), "sha256": sha256(data)}
                      for inside, data in member.files],
        })
    known = build.known_bad
    written = sorted(set(build.singles) | {SET_FILE, CHECKLIST_NAME, MANIFEST_NAME}
                     | ({known["file"]} if known else set()))
    return {
        "schema": MANIFEST_SCHEMA,
        "sitting": SITTING_1,
        # True only for the control set itself: every slot filled as specified.
        "complete": build.complete,
        "substitutes": [member.slot.number for member in build.substitutes],
        "set": {"file": SET_FILE, "name": SET_NAME, "bytes": len(build.set_bytes),
                "sha256": sha256(build.set_bytes)},
        "members": members,
        "unfilled": [{"slot": slot.number, "slot_kind": slot.key, "wanted": slot.wanted}
                     for slot in build.unfilled],
        "known_bad": ({"file": known["file"], "original_name": known["original_name"],
                       "bytes": len(known["data"]), "sha256": sha256(known["data"]),
                       "broken": known["broken"], "finding": known["finding"]} if known else None),
        "written": written,
    }


# ── the checklist ────────────────────────────────────────────────────────────

def _special(member):
    """The one question that belongs to this member alone."""
    candidate = member.candidate
    if not member.pick.as_specified:
        return f"SUBSTITUTE. {member.pick.note} Only the three plain questions apply."
    key = member.slot.key
    if key == "e0":
        size = member.thumbnail_size
        stored = f" ({size[0]} x {size[1]} pixels)" if size else ""
        return ("This is the oldest kind of brush file. Is its name written correctly, accent "
                f"included? Its stored preview picture is an older, smaller size{stored}: does "
                "the preview in the list look right, stretched, or empty?")
    if key == "e4":
        return ("Nothing special: this is the plain case. If this one is missing or does not "
                "draw, say so first, because everything later builds on it.")
    if key == "e3":
        names = " and ".join(f"`{name}`" for name in (candidate.bundled_shape, candidate.bundled_grain)
                             if name)
        return ("This brush carries no pictures of its own. It only names textures that came "
                f"inside older versions of Procreate ({names}). Does it draw with a texture, as "
                "a plain solid line, or not at all?")
    if key == "dual":
        return ("This is a dual brush: two brushes working as one. Tap it a second time to "
                "open Brush Studio. Does Brush Studio show two brushes (a dual brush shows both "
                "of its brushes at the top left)? Does a stroke look like its preview?")
    if key == "no-thumbnail":
        return ("This brush file has no preview picture in it. In the Brush Library list, is "
                "its preview empty, or did Procreate draw one itself?")
    if key == "author":
        return ("In Brush Studio, open \"About this brush\". Is there a maker's name, a "
                "picture and a signature?")
    if key == "reset":
        return ("Another dual brush, and the one with the most inside it: it also carries a "
                "saved reset point. Does Brush Studio show two brushes? In \"About this "
                "brush\", is \"Reset brush\" offered? Look only; do not tap it.")
    names = ", ".join(f"`{name}`" for name in candidate.named_textures)
    kept = f" It keeps its texture in the file under its own name ({names})." if names else ""
    return f"This is the newest kind of brush file in the library.{kept} Does it draw with a texture?"


def _what(member):
    """A few words for the checklist table."""
    candidate = member.candidate
    words = {"e0": "oldest format", "e4": "plain legacy brush", "e3": "names built-in textures",
             "dual": "dual brush", "no-thumbnail": "no preview in the file",
             "author": "maker's picture and signature", "reset": "dual brush with a reset point",
             "earth": "newest format"}[member.slot.key]
    facts = f"{candidate.era}, {candidate.keys} keys"
    if member.pick.as_specified:
        return f"{words} ({facts})"
    # The stand-in's own facts first: the words that follow are the slot's, not this brush's.
    slot = {"e0": "the oldest format", "e4": "the plain legacy brush",
            "e3": "the brush that names built-in textures", "dual": "the dual brush",
            "no-thumbnail": "the brush with no preview in its file",
            "author": "the brush with a maker's picture and signature",
            "reset": "the dual brush with a reset point", "earth": "the newest format"}[member.slot.key]
    nothing = " and shows nothing about it" if member.pick.tier is None else ""
    return f"{facts}. SUBSTITUTE: stands in for {slot}{nothing}"


def _banner(build):
    """The lines that say a build is not the control set. Empty when it is."""
    count = len(build.members)
    substitutes = build.substitutes
    if not substitutes and not build.unfilled:
        return []
    lines = ["> **This build is not the full control set.** It was built with `--allow-substitutes`."]
    if substitutes:
        near = [member for member in substitutes if member.pick.tier is not None]
        lines.append(f"> {len(substitutes)} of its {count} brushes are substitutes: the library did not "
                     "hold the kind of")
        if len(near) == len(substitutes):
            lines.append("> brush the plan asks for, so the nearest kind found stands in.")
        elif not near:
            lines += ["> brush the plan asks for, nor anything near it, so another brush from the library",
                      "> fills the slot."]
        else:
            lines += ["> brush the plan asks for, so the nearest kind found stands in, or, where nothing",
                      "> near was found, another brush from the library fills the slot."]
        lines.append("> Each is marked SUBSTITUTE below, with what it no longer shows.")
    if build.scan.files["official"] == 0:
        lines += [
            "> `brushes/library/official/` holds no official sets, and most of the planned members",
            "> come from them. Fetch them and build again before the sitting:",
            ">",
            f">     {FETCH_COMMAND}",
            ">     python -I brushes/pipeline/device_tests.py build sitting-1 --confirm",
            ">",
            "> A sitting with this build answers less, and there are only two sittings.",
        ]
    for slot in build.unfilled:
        lines.append(f"> Slot {slot.number} is empty: the library had no brush left for it.")
    lines.append("")
    return lines


def render_checklist(build):
    """CHECKLIST.md: the steps for the person holding the iPad, in plain words,
    written from what this build actually holds."""
    members = build.members
    count = len(members)
    known = build.known_bad
    known_name = known["file"].rsplit("/", 1)[-1] if known else ""
    lines = [
        "# Sitting 1: the control set",
        "",
        "This folder was made by `python -I brushes/pipeline/device_tests.py build sitting-1 --confirm`.",
        f"Git keeps three things of it: `{MANIFEST_NAME}`, this checklist, and whatever is put in",
        f"`{RETURNED_DIR}/`. The brush files built here are scratch and are not committed.",
        "",
        "## What this is for",
        "",
        "Nothing this tool has written has been opened in Procreate yet. This sitting asks the",
        "narrowest question first: does Procreate open a brush set that we packed, when every",
        "brush inside it is one that Procreate or a brush maker already made?",
        "",
        f"The set holds {count} brushes taken from the library. Every file inside every brush is,",
        "byte for byte, the original. Only three things are ours: the zip container around them,",
        "the folder name each brush sits in, and the small list (`brushset.plist`) that names the",
        "set and puts the brushes in order. If Procreate opens this set, those three things are",
        "right, and later sittings can test edited and newly made brushes.",
        "",
        "It takes about fifteen minutes. You need the iPad, Procreate, and a way to move files",
        "to the iPad and back.",
        "",
    ]
    lines += _banner(build)
    lines += [
        "## What is in this folder",
        "",
        "| File | What it is |",
        "|---|---|",
        f"| `{SET_FILE}` | the control set, named \"{SET_NAME}\", {count} brushes |",
        f"| `{SINGLES_DIR}/` | the same {count} brushes, one `.brush` file each. "
        "Only needed if the set fails |",
    ]
    if known:
        lines.append(f"| `{known['file']}` | a brush file the old Brush Designer wrote, which is "
                     "malformed. Never a file to bring back |")
    lines += [
        f"| `{RETURNED_DIR}/` | empty. What comes back from the iPad goes here |",
        f"| `{MANIFEST_NAME}` | what was built and from where, with checksums. "
        "For the comparison afterwards |",
        f"| `{CHECKLIST_NAME}` | this file |",
        "",
        "## What to bring back",
        "",
        "1. The Procreate version, the iPadOS version and the iPad model.",
    ]
    if known:
        lines.append("2. What happened when you opened the known-bad file.")
    lines += [
        f"{3 if known else 2}. Your answers to the questions in the table below.",
        f"{4 if known else 3}. Two files: the control set shared back out of Procreate, and one brand-new",
        "   untouched brush.",
        "",
        "Photos of the screen are welcome wherever words are slow.",
        "",
    ]
    lines += _transfer_steps([SET_FILE] + ([f"the file in `{KNOWN_BAD_DIR}/`"] if known else []))
    step = 3
    if known:
        lines += [
            f"## Step {step}. Open the known-bad file first",
            "",
            f"Tap `{known_name}`. The old Brush Designer wrote this file, and it is",
            f"malformed: {known['finding']}.",
            "",
            "We expect Procreate to refuse it, and we want to see what a refusal looks like on your",
            "version, so that we recognise one if a file of ours gets the same treatment. Write down",
            "exactly what happens:",
            "",
            "- the words of any message (a photo of the screen is best), or",
            "- \"nothing happened\", or",
            "- \"a brush appeared\". If one did, say what it is called and whether it draws, then",
            "  delete it straight away (swipe left on the brush, Delete). It may be called",
            "  \"Untitled Brush\", which is also what the new brush of the last step is called, and",
            "  the two must not be mixed up.",
            "",
            "If Procreate closes by itself, open it again and carry on.",
            "",
        ]
        step += 1
    lines += [
        f"## Step {step}. Import the control set",
        "",
        f"Tap `{SET_FILE}`.",
        "",
        "What should happen: Procreate opens and takes the set in. To see it, open any canvas",
        "(the brush icon is only there inside a canvas, not in the Gallery), then tap the brush",
        f"icon at the top right. A new brush set named **{SET_NAME}** is in the Brush Library.",
        f"It holds {count} brushes, in this order:",
        "",
    ]
    for index, member in enumerate(members, 1):
        lines.append(f"{index}. {show(member.candidate.name).strip() or '(a brush with an empty name)'}")
    lines += [
        "",
        "If Procreate shows a message instead, write down its words, then go to \"If the set does",
        "not import\" below.",
        "",
    ]
    step += 1
    lines += [
        f"## Step {step}. Look at each brush",
        "",
        "Stay in that canvas and pick black. For each brush in the set, answer three plain questions:",
        "",
        "- **Listed?** Is it in the set, under the name given here?",
        "- **Preview?** Does its row in the Brush Library show a picture of a stroke?",
        "- **Draws?** Select it and draw one stroke. Does a mark appear?",
        "",
        "| # | Name | What it is | Listed? | Preview? | Draws? |",
        "|---|---|---|---|---|---|",
    ]
    for index, member in enumerate(members, 1):
        name = show(member.candidate.name).strip().replace("|", "/") or "(empty name)"
        lines.append(f"| {index} | {name} | {_what(member)} |  |  |  |")
    lines += [
        "",
        "Then one more question for each brush. To open Brush Studio, tap a brush that is",
        "already selected.",
        "",
    ]
    for index, member in enumerate(members, 1):
        name = show(member.candidate.name).strip() or "(empty name)"
        lines.append(f"{index}. **{name}.** {_special(member)}")
    lines += [
        "",
        "Leave Brush Studio with Cancel each time, so that nothing in the set is changed before",
        "you share it back.",
        "",
        "### If the set does not import, or a brush is missing or will not draw",
        "",
        f"Open the files in `{SINGLES_DIR}/` one at a time, in number order. Each holds one brush of the",
        "set. A single brush lands in the set named \"Imported\". Note for each file whether it",
        "arrives and whether it draws. That tells us which brush is at fault.",
        "",
        "A single file for a dual brush or a brush with a reset point is laid out in a way we",
        "have not yet seen Procreate write, so if one of those fails only as a single file, say",
        "so and do not worry about it.",
        "",
    ]
    step += 1
    lines += [
        f"## Step {step}. The return leg: share two things back",
        "",
        f"**a. The control set.** In the Brush Library, tap the set name **{SET_NAME}** so that it",
        "is selected, then tap it once more. A small menu appears: choose Share. Save the file to",
        "Files (in the same cloud folder is fine). It is saved as a `.brushset` file. This shows",
        "what Procreate kept of each brush and what it rewrote.",
        "",
    ]
    lines += _new_brush_step("b")
    lines += ["Keep the file names Procreate gives them.", ""]
    step += 1
    lines += _returned_steps(step, SITTING_1, "both files")
    if known:
        lines += [
            f"Do not put the known-bad file (`{known_name}`) in `{RETURNED_DIR}/`, nor any brush that",
            "came out of it: that folder is for the two files of the return leg and your notes.",
            "",
        ]
    lines += _closing_lines()
    return "\n".join(lines)


def _transfer_steps(files):
    """Steps 1 and 2 of a checklist: moving the files, and the versions."""
    shown = ", ".join(f"`{name}`" if not name.startswith("the ") else name for name in files)
    return [
        "## Step 1. Get the files onto the iPad",
        "",
        "Any route works, as long as the files arrive unchanged:",
        "",
        "- **iCloud Drive.** On this computer, sign in at icloud.com, open iCloud Drive, and upload",
        f"  {shown} and the files in `{SINGLES_DIR}/`.",
        "  They then appear in the Files app on the iPad, under iCloud Drive.",
        "- **Another cloud drive** that shows up in the Files app (Google Drive, OneDrive,",
        "  Dropbox): the same.",
        "- **Email** the files to yourself and open the message on the iPad.",
        "- **AirDrop**, if the files are on a Mac.",
        "",
        "On the iPad, open the Files app, find the files, and wait until each has finished",
        "downloading (no cloud symbol beside it).",
        "",
        "To open a brush file: tap it in Files. Procreate should open and take it in. If",
        "something else opens instead, press and hold the file, choose Share, then Procreate.",
        "",
        "## Step 2. Write down the versions",
        "",
        "- **Procreate version.** In the iPad's Settings app, find Procreate in the list of apps;",
        "  the version is shown on that page. If you cannot find it there, the App Store page",
        "  for Procreate shows it under Version History.",
        "- **iPadOS version and iPad model.** Settings, General, About.",
        "",
    ]


def _new_brush_step(letter):
    return [
        f"**{letter}. One brand-new, untouched brush.** In the Brush Library, tap the **+** at the top",
        "right. Brush Studio opens with a new brush. Change nothing, and tap Done. The new brush",
        "is now in the list (it is usually called \"Untitled Brush\"). Swipe left on it, tap Share,",
        "and save it to Files. It is saved as a `.brush` file. This is what Procreate itself",
        "writes today, and it becomes the starting point for brushes this tool makes.",
        "",
    ]


def _returned_steps(step, sitting, what):
    return [
        f"## Step {step}. Put the returned files here",
        "",
        f"Back on this computer, put {what} in:",
        "",
        f"    brushes/{OUT_HOME}/{sitting}/{RETURNED_DIR}/",
        "",
        f"(that is the `{RETURNED_DIR}` folder beside this file). Add your notes there too: a",
        "`notes.txt` with the versions and your answers, or photos of this page filled in.",
        "",
    ]


def _closing_lines(sets="the set"):
    return [
        f"What is in `{RETURNED_DIR}/` is kept in git, together with `{MANIFEST_NAME}` and this page: it",
        "is the only record of what the iPad did, and no build can make it again.",
        "",
        "Do not build this sitting again once files are in that folder: a new build gives the",
        "brushes new folder names, and the returned files are compared with this one.",
        "",
        f"Afterwards you can delete {sets} and the new brush from Procreate (swipe left, Delete).",
        "",
    ]


# ── sitting 2: the two donors and what is changed ────────────────────────────

def value_text(value):
    """A requested value as a brush name spells it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, "g")
    if isinstance(value, dict) and isinstance(value.get("points"), list):
        return f"{len(value['points'])} points"
    return str(value)


class Sweep:
    """One member of the edits set: the donor's archive with `changes` applied
    and the name `<code> <label>` (by default `key=value` for each change).
    `thumbnail` keeps the donor's thumbnail; every other member has none, so
    that the preview the app shows is its own."""

    def __init__(self, code, changes, label=None, thumbnail=False):
        self.code = code
        self.changes = dict(changes)
        self.label = label
        self.thumbnail = thumbnail

    @property
    def donor(self):
        return self.code[0]

    @property
    def name(self):
        label = self.label or " ".join(f"{key}={value_text(value)}" for key, value in self.changes.items())
        return f"{self.code} {label}"


def _numbered(prefix, rows):
    return tuple(Sweep(f"{prefix}{number:02d}", changes, label, thumbnail)
                 for number, (changes, label, thumbnail) in enumerate(rows))


# A four-point pressure-to-size curve; apply_patch writes it as the archive's
# point strings, the two end points first.
SIZE_CURVE = [[0.0, 0.0], [0.25, 0.55], [0.6, 0.8], [1.0, 1.0]]
RENDERING_KEYS = ("renderingMaxTransfer", "renderingModulatedTransfer", "renderingRecursiveMixing")
# The six (max, modulated, recursive) combinations the library's M220 brushes
# hold, most common first: 234, 57, 33, 31, 10 and 3 of 368 (counted when this
# was written, with plistlib, over library/official and library/user).
RENDERING_COMBOS = ((False, False, True), (False, False, False), (True, False, False),
                    (True, True, False), (False, True, True), (False, True, False))


def _rendering_label(combo):
    return "rendering max={} mod={} rec={}".format(*(int(value) for value in combo))


# The design's file F2 (critique-fidelity.md section 6). In the library every
# E4 brush holds the same number under blendMode and extendedBlend (246, 32, 21
# and 1 brushes for 0, 1, 8 and 3), so the two change together.
LEGACY_SWEEP = _numbered("L", [
    ({}, "name only", True),
    ({}, "name only, no thumbnail", False),
    ({"plotSpacing": 0.1}, None, False),
    ({"plotSpacing": 0.25}, None, False),
    ({"plotSpacing": 0.5}, None, False),
    ({"plotSpacing": 1.0}, None, False),
    ({"dynamicsRenderType": 0}, None, False),
    ({"dynamicsRenderType": 1}, None, False),
    ({"dynamicsRenderType": 2}, None, False),
    ({"dynamicsRenderType": 3}, None, False),
    ({"blendMode": 1, "extendedBlend": 1}, None, False),
    ({"blendMode": 3, "extendedBlend": 3}, None, False),
    ({"blendMode": 8, "extendedBlend": 8}, None, False),
    ({"textureMovement": 0.0}, None, False),
    ({"textureMovement": 1.0}, None, False),
    ({"textureZoom": 0.0}, None, False),
    ({"textureZoom": 1.0}, None, False),
    ({"shapeRotation": -1.0}, None, False),
    ({"shapeRotation": 0.0}, None, False),
    ({"shapeRotation": 1.0}, None, False),
    ({"stamp": True}, None, False),
    ({"previewSize": 0.1}, None, False),
    ({"previewSize": 0.6}, None, False),
    ({"dynamicsPressureSizeCurve": {"points": SIZE_CURVE}}, None, False),
])
MODERN_SWEEP = _numbered("M", [
    ({}, "name only", True),
    *[(dict(zip(RENDERING_KEYS, combo)), _rendering_label(combo), False) for combo in RENDERING_COMBOS],
    ({"plotSpacing": 0.25, "plotSpacingVersion": 0}, None, False),
    ({"plotSpacing": 0.25, "plotSpacingVersion": 1}, None, False),
    ({"plotSpacing": 1.0, "plotSpacingVersion": 0}, None, False),
    ({"plotSpacing": 1.0, "plotSpacingVersion": 1}, None, False),
    ({"textureApplication": 0}, None, False),
    ({"textureApplication": 1}, None, False),
    ({"grainBlendMode": 7}, None, False),
    ({"grainBlendMode": 10}, None, False),
    ({"grainBlendMode": 27}, None, False),
    ({"shapeCount": 0.0625}, None, False),
    ({"shapeCount": 0.5}, None, False),
    ({"shapeAngle": 1.5708}, None, False),
    ({"wetEdgesAmount": 1.0}, None, False),
    ({"burntEdgesAmount": 1.0}, None, False),
])
SWEEPS = {"L": LEGACY_SWEEP, "M": MODERN_SWEEP}

DONOR_L = Slot(
    "L", "edit-legacy",
    "an E4 brush (101 keys) that carries its own Shape.png and Grain.png and has no jitter "
    "and no scatter: by the same rule, the brush sitting 1 holds as member 2",
    "whether the app opens a legacy archive (one-byte references) that our rules re-encoded "
    "with one setting changed, and what each value of each setting looks like",
    SLOTS[1].tiers, SLOTS[1].rank, "edited legacy brushes")
DONOR_M = Slot(
    "M", "edit-modern",
    "an M220 brush (220 keys) that carries its own Shape.png and Grain.png and has no jitter "
    "and no scatter",
    "whether the app opens a modern archive (two-byte references) that our rules re-encoded "
    "with one setting changed, and what each value of each setting looks like",
    [Tier("M220 brush with its own shape and grain", lambda c: c.era == "M220" and c.has_shape and c.has_grain),
     Tier("modern brush with its own shape and grain",
          lambda c: c.family == "modern" and c.has_shape and c.has_grain,
          "It is not the 220-key format, so a setting the sweep names may be missing."),
     Tier("M220 brush with its own shape", lambda c: c.era == "M220" and c.has_shape,
          "It carries no Grain.png: the grain settings act on a texture inside the app."),
     Tier("M220 brush", lambda c: c.era == "M220",
          "It carries no image of its own: nothing beside the archive is carried verbatim.")],
    lambda c: (not c.steady, not c.calm, not c.has_thumbnail, c.dual, c.reset, c.stamp,
               c.author_picture or c.signature, c.total),
    "edited modern brushes")


def shape_name_slot(candidates):
    """The slot that gives S5 its bundled shape name: a name that a modern brush
    of an official Procreate 5 set gives its shape without carrying the image.
    Among those, the name most such brushes use, then the first by name."""
    p5 = [c for c in candidates if _official(c, "procreate-5") and c.family == "modern" and c.names_only]
    counts = collections.Counter(c.bundled_shape for c in (p5 or [c for c in candidates if c.names_only]))
    return Slot(
        "S5", "bundled-shape",
        "the name of a shape that ships inside the app, as a modern brush of an official "
        "Procreate 5 set names it without carrying the image",
        "whether a brush we made, holding no image at all, finds a shape the app ships by its name",
        [Tier("modern brush of an official Procreate 5 set that names a shape it does not carry",
              lambda c: _official(c, "procreate-5") and c.family == "modern" and c.names_only),
         Tier("brush of an official set that names a shape it does not carry",
              lambda c: c.library == "official" and c.names_only,
              "The name does not come from a Procreate 5 set."),
         Tier("brush that names a shape it does not carry", lambda c: c.names_only,
              "The name does not come from an official set, so it may not ship with the app.")],
        lambda c: (-counts.get(c.bundled_shape, 0), c.bundled_shape or "", c.era != "M220"),
        "a shape that is named and not carried")


def pick_for(slot, candidates, taken=()):
    """The Pick of one slot on its own: its first kind that the library holds,
    and among those the brush its rank puts first. None when no kind fits."""
    for index, tier in enumerate(slot.tiers):
        pool = [c for c in candidates if c.archive_sha256 not in taken and tier.test(c)]
        if pool:
            return Pick(slot, min(pool, key=lambda c: (slot.rank(c), c.order)), index)
    return None


# ── sitting 2: what is made here ─────────────────────────────────────────────

# The images sitting 2 makes, by kind: (what it is, width, height). Shapes and
# grains are 8-bit grey written by png_io.write_png (white is paint; the new
# brush's shapeInverted is the template's), the thumbnail by
# png_io.write_thumbnail. Each is made once per process.
TEXTURES = {
    "disc": ("a soft round dot", 1024, 1024),
    "speckle": ("a fine even speckle", 1024, 1024),
    "oval": ("a soft oval, twice as wide as tall", 600, 300),
    "big-speckle": ("a fine even speckle", 2048, 2048),
    "square": ("a hard square", 512, 512),
}
THUMBNAIL_WHAT = "an S-shaped stroke, 1060 x 324, drawn here"
_MADE = {}

S4_NAME = "S4 Wäßrige Tönung 水彩 "      # 21 characters, a trailing space

# The design's file F3: (code, name, era, shape, grain, thumbnail, sub). A shape
# or grain of None is no image; S5 names its shape instead (shape_name_slot).
SCRATCH = (
    ("S1", "S1 M220 scratch", "M220", "disc", "speckle", True, False),
    ("S2", "S2 M220 no thumbnail", "M220", "disc", "speckle", False, False),
    ("S3", "S3 E4 scratch", "E4", "disc", "speckle", True, False),
    ("S4", S4_NAME, "M220", "oval", "big-speckle", True, False),
    ("S5", "S5 bundled shape", "M220", None, None, False, False),
    ("S6", "S6 dual", "M220", "disc", "speckle", True, True),
)
SUB_NAME = "S6 dual Secondary"


def _smooth(edge):
    """255 inside, 0 outside, a smoothstep between: a table over squared
    distance (0 to 1 in 4096 steps) for a dot whose solid core is `edge` wide."""
    table = []
    for step in range(4097):
        distance = math.sqrt(step / 4096)
        if distance <= edge:
            value = 255
        else:
            t = min(1.0, (distance - edge) / (1.0 - edge))
            value = round(255 * (1.0 - t * t * (3.0 - 2.0 * t)))
        table.append(value)
    return bytes(table)


def soft_dot(width, height):
    """width * height grey bytes: white in the middle with a soft edge, black
    at the border; an oval when the two sides differ."""
    table = _smooth(0.55)
    xs = [((x + 0.5 - width / 2) / (0.47 * width)) ** 2 for x in range(width)]
    rows = []
    for y in range(height):
        dy = ((y + 0.5 - height / 2) / (0.47 * height)) ** 2
        rows.append(bytes(table[min(4096, int((dx + dy) * 4096))] for dx in xs))
    return b"".join(rows)


def speckle(width, height, seed):
    """width * height grey bytes of even noise from 110 to 255: a grain that
    tiles, the same on every machine."""
    raw = hashlib.shake_256(f"rosw sitting-2 grain {seed} {width}x{height}".encode("ascii")).digest(width * height)
    return raw.translate(bytes(110 + (value * 145) // 255 for value in range(256)))


def hard_square(width, height):
    """A white square in the middle half, black around it."""
    left, top = width // 4, height // 4
    row = bytes(left) + b"\xff" * (width - 2 * left) + bytes(width - (width - 2 * left) - left)
    return bytes(width) * top + row * (height - 2 * top) + bytes(width) * (height - (height - 2 * top) - top)


def stroke_alpha(width=png_io.THUMBNAIL_SIZE[0], height=png_io.THUMBNAIL_SIZE[1]):
    """Coverage of one tapered S-shaped stroke across a thumbnail, row by row."""
    plane = bytearray(width * height)
    for x in range(width):
        t = (x + 0.5) / width
        if not 0.04 < t < 0.96:
            continue
        centre = height / 2 + height * 0.22 * math.sin(2 * math.pi * (t - 0.04) / 0.92)
        half = height * 0.11 * math.sin(math.pi * (t - 0.04) / 0.92) ** 0.5
        for y in range(max(0, int(centre - half - 3)), min(height, int(centre + half + 4))):
            inside = half - abs(y + 0.5 - centre)
            if inside > 0:
                plane[y * width + x] = 255 if inside >= 2 else int(255 * inside / 2)
    return bytes(plane)


def texture(kind):
    """The PNG bytes of one image this sitting makes (TEXTURES), made once."""
    if kind not in _MADE:
        _, width, height = TEXTURES[kind]
        if kind in ("disc", "oval"):
            pixels = soft_dot(width, height)
        elif kind == "square":
            pixels = hard_square(width, height)
        else:
            pixels = speckle(width, height, kind)
        _MADE[kind] = png_io.write_png(width, height, "L", pixels)
    return _MADE[kind]


def thumbnail():
    if "thumbnail" not in _MADE:
        _MADE["thumbnail"] = png_io.write_thumbnail(stroke_alpha())
    return _MADE["thumbnail"]


def texture_words(kind):
    what, width, height = TEXTURES[kind]
    return f"{what}, {width} x {height} grey, made here"


# ── sitting 2: building ──────────────────────────────────────────────────────

class Edit:
    """One member of ROSW 2 Edits, in memory."""

    def __init__(self, sweep, folder, plan, brush, report, data, changed):
        self.sweep = sweep
        self.code = sweep.code
        self.name = sweep.name
        self.donor = sweep.donor
        self.folder = folder                    # container.BrushFolder
        self.plan = plan                        # container.member_plan
        self.era = brush.era
        self.state = brush_model.export_state(brush)
        self.applied = {key: value for key, value in report["applied"].items() if key != "name"}
        # By value: the keys whose value differs from the donor's, and the keys
        # the sweep names that hold the donor's own value.
        self.changed = list(changed)
        self.unchanged = [key for key in sweep.changes if key not in changed]
        self.warnings = [dict(item) for item in report["warnings"]]
        self.archive = data
        self.uuid = None
        self.single = f"{SINGLES_DIR}/{sweep.code}-{file_stem(sweep.name[len(sweep.code):])}.brush"


class Scratch:
    """One member of ROSW 3 Scratch, in memory."""

    def __init__(self, code, name, era, folder, made, overrides, sub, polarity):
        self.code = code
        self.name = name
        self.era = era
        self.folder = folder                    # container.BrushFolder
        self.made = made                        # {member path: words}
        self.overrides = overrides
        self.sub = sub
        self.polarity = polarity                # the template's shapeInverted, textureInverted
        self.uuid = None
        self.single = f"{SINGLES_DIR}/{code}-{file_stem(name[len(code):])}.brush"


class Build2:
    """Everything sitting 2's folder will hold, in memory."""

    sitting = SITTING_2

    def __init__(self):
        self.scan = None
        self.donors = {}                        # "L" | "M" -> Pick or None
        self.donor_folders = {}                 # "L" | "M" -> container.BrushFolder
        self.shape_pick = None                  # the Pick that names S5's shape, or None
        self.edits = []
        self.scratch = []
        self.left_out = []                      # (code, name, why)
        self.edits_bytes = b""
        self.scratch_bytes = b""
        self.singles = {}
        self.checklist = ""
        self.manifest = {}

    @property
    def picks(self):
        return {"L": self.donors.get("L"), "M": self.donors.get("M"), "S5": self.shape_pick}

    @property
    def substitutes(self):
        return [role for role, pick in self.picks.items() if pick is not None and not pick.as_specified]

    @property
    def unfilled(self):
        return [role for role, pick in self.picks.items() if pick is None]

    @property
    def complete(self):
        """Every donor as the plan asks, nothing empty, no member left out."""
        return bool(self.edits) and not self.substitutes and not self.unfilled and not self.left_out

    @property
    def shape_name(self):
        return self.shape_pick.candidate.bundled_shape if self.shape_pick else None

    def files(self):
        """{relative POSIX path: bytes} of every file to write, the manifest last."""
        out = dict(self.singles)
        out[EDITS_FILE] = self.edits_bytes
        out[SCRATCH_FILE] = self.scratch_bytes
        out[CHECKLIST_NAME] = self.checklist.encode("utf-8")
        out[MANIFEST_NAME] = bc.json_text(self.manifest).encode("utf-8")
        return out


def make_edit(base, folder, sweep):
    """(Edit, "") for one sweep of a donor, or (None, why) when its changes are
    refused. The archive is rule-encoded by brush_model with the sweep's
    changes and its name; every other member is the donor's, byte for byte,
    and the thumbnail is dropped unless the sweep keeps it."""
    patch = dict(sweep.changes)
    patch["name"] = sweep.name
    try:
        brush, report = brush_model.apply_patch(base, patch, mode="strict")
    except CodecError as exc:
        return None, _why(exc)
    if not report["ok"]:
        first = report["rejected"][0]
        return None, f"{first['key']}: {first['code']}: {first['reason']}"
    try:
        data = brush_model.encode(brush)
    except CodecError as exc:
        return None, f"it cannot be encoded: {_why(exc)}"
    # What changed, by value, as plistlib reads the two archives: the same
    # reading the second pass makes. A value the donor already holds is not a
    # change, whatever width the donor stored it in.
    try:
        before, after = plain_root(folder.archive), plain_root(data)
    except Exception as exc:                    # whatever a broken plist raises
        return None, f"plistlib cannot read it back ({type(exc).__name__})"
    differing = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    if not differing <= set(sweep.changes) | {"name"}:
        raise DeviceTestError(f"{sweep.code}: the encoder changed "
                              f"{', '.join(sorted(differing - set(sweep.changes) - {'name'}))} "
                              "as well as what the sweep names")
    changed = [key for key in sweep.changes if key in differing]
    out = folder.copy()
    out.set(BRUSH_ARCHIVE, data)
    drop = set()
    if not sweep.thumbnail and out.remove(THUMBNAIL):
        drop.add(THUMBNAIL)
    plan = container.member_plan(folder, out, reencoded={BRUSH_ARCHIVE}, drop=drop)
    return Edit(sweep, out, plan, brush, report, data, changed), ""


def _new_brush(library, name, era, now, overrides=None):
    """(Brush, bytes) of a new brush from brush_model's template of `era`."""
    try:
        brush = brush_model.new_brush(name, era=era, overrides=overrides, now=now, library=library)
        return brush, brush_model.encode(brush)
    except BrushModelError as exc:
        if exc.code in ("library_missing", "donor_missing", "donor_mismatch", "lfs_pointer",
                        "bad_container"):
            raise EnvironmentProblem(f"the {era} new-brush template cannot be read: {_why(exc)}") from None
        raise DeviceTestError(f"{show(name)!r} cannot be made: {_why(exc)}") from None
    except CodecError as exc:
        raise DeviceTestError(f"{show(name)!r} cannot be made: {_why(exc)}") from None


def make_scratch(library, now, shape_name):
    """([Scratch], [(code, name, why)] left out): the six brushes of F3, made
    by brush_model.new_brush with the images of TEXTURES."""
    made, left_out = [], []
    for code, name, era, shape, grain, has_thumbnail, sub in SCRATCH:
        overrides = None
        if code == "S5":
            if not shape_name:
                left_out.append((code, name, "the library holds no brush that names a shape it does "
                                             "not carry, so there is no name to give it"))
                continue
            overrides = {"bundledShapePath": shape_name}
        brush, data = _new_brush(library, name, era, now, overrides)
        members, words = [(BRUSH_ARCHIVE, data)], {BRUSH_ARCHIVE: f"new {era} brush, made here"}
        # Our images are white where there is paint: right while these are false.
        polarity = {key: brush.params.get(key) for key in ("shapeInverted", "textureInverted")}
        for path, kind in ((SHAPE, shape), (GRAIN, grain)):
            if kind:
                members.append((path, texture(kind)))
                words[path] = texture_words(kind)
        if has_thumbnail:
            members.append((THUMBNAIL, thumbnail()))
            words[THUMBNAIL] = THUMBNAIL_WHAT
        if sub:
            _, sub_data = _new_brush(library, SUB_NAME, era, now)
            for path, data, what in ((BRUSH_ARCHIVE, sub_data, f"new {era} brush, made here"),
                                     (SHAPE, texture("square"), texture_words("square")),
                                     (GRAIN, texture("speckle"), texture_words("speckle"))):
                members.append((f"{container.SUB}/{path}", data))
                words[f"{container.SUB}/{path}"] = what
        made.append(Scratch(code, name, era, container.BrushFolder(members), words, overrides,
                            SUB_NAME if sub else None, polarity))
    return made, left_out


def _write_set(name, members, stamp):
    """The bytes of a set of (uuid, BrushFolder), read back through the codec's
    reader and compared with what went in."""
    brush_set = container.BrushSet(name, [(member.uuid, member.folder) for member in members])
    try:
        data = container.write_brushset(brush_set, mtime=stamp)
        back = container.read_brushset(data, limits=CAPS)
    except CodecError as exc:
        raise DeviceTestError(f"the set {show(name)!r} cannot be written: {_why(exc)}") from None
    if back.name != name or back.uuids() != brush_set.uuids():
        raise DeviceTestError(f"the set {show(name)!r} does not read back with its name and folders")
    for (_, made), (_, read) in zip(brush_set.brushes, back.brushes):
        if [(m.path, m.data) for m in container.canonical_order(made.members)] != read.pairs():
            raise DeviceTestError(f"the set {show(name)!r} does not read back as what was put into it")
    return data


def _write_single(member, stamp):
    try:
        data = container.write_brush(member.folder, mtime=stamp)
        back = container.read_brush(data, limits=CAPS)
    except CodecError as exc:
        raise DeviceTestError(f"{member.single} cannot be written: {_why(exc)}") from None
    if back.pairs() != [(m.path, m.data) for m in container.canonical_order(member.folder.members)]:
        raise DeviceTestError(f"{member.single} does not read back as what was put into it")
    return data


def build_sitting_2(library, *, date_time=None, new_uuid=None, now=None):
    """Scan the library, choose the donors, and build every file of sitting 2
    in memory. Writes nothing. `date_time` (the date of the zip entries, now by
    default), `new_uuid` (a callable giving a folder name) and `now` (seconds
    since 1970 for the new brushes' creation date, the clock by default) exist
    for the tests."""
    library = Path(library)
    if not library.is_dir():
        raise EnvironmentProblem(f"there is no library at {library}")
    build = Build2()
    build.scan = scan_library(library)
    candidates = build.scan.candidates
    if not candidates:
        raise EnvironmentProblem(f"no brush file that can be read was found under "
                                 f"{library / LIBRARY_PARTS[0]} or {library / LIBRARY_PARTS[1]}")
    for slot in (DONOR_L, DONOR_M):
        build.donors[slot.number] = pick_for(slot, candidates)
    build.shape_pick = pick_for(shape_name_slot(candidates), candidates)

    for role in ("L", "M"):
        pick = build.donors[role]
        if pick is None:
            continue
        folder = load_folder(library, pick.candidate)
        build.donor_folders[role] = folder
        try:
            base = brush_model.decode(folder.archive)
        except CodecError as exc:
            raise DeviceTestError(f"donor {role}, {show(pick.candidate.where)}, cannot be decoded: "
                                  f"{_why(exc)}") from None
        for sweep in SWEEPS[role]:
            edit, why = make_edit(base, folder, sweep)
            if edit is None:
                build.left_out.append((sweep.code, sweep.name, why))
            else:
                build.edits.append(edit)
    if not build.edits:
        raise DeviceTestError("the library holds no donor for either half of the edits set, so "
                              f"{EDITS_FILE} would be empty")
    build.scratch, left = make_scratch(library, time.time() if now is None else now, build.shape_name)
    build.left_out += left

    taken = {pick.candidate.folder for pick in build.donors.values() if pick is not None}
    members = build.edits + build.scratch
    for member, folder in zip(members, _folder_names(new_uuid or fresh_uuid, len(members), taken)):
        member.uuid = folder
    stamp = _stamp(date_time)
    build.edits_bytes = _write_set(EDITS_NAME, build.edits, stamp)
    build.scratch_bytes = _write_set(SCRATCH_NAME, build.scratch, stamp)
    for member in members:
        build.singles[member.single] = _write_single(member, stamp)
    build.checklist = render_checklist_2(build)
    build.manifest = make_manifest_2(build)
    return build


def _donor_record(role, pick, folder):
    if pick is None:
        return {"role": role, "as_specified": False, "note": "nothing of any kind was found",
                "source": None}
    candidate = pick.candidate
    record = {"role": role, "kind": pick.slot.key, "wanted": pick.slot.wanted,
              "shows": pick.slot.shows, "as_specified": pick.as_specified, "note": pick.note,
              "name": candidate.name, "era": candidate.era, "family": candidate.family,
              "keys": candidate.keys,
              "source": {"container": candidate.container, "set": candidate.set_name,
                         "folder": candidate.folder, "prefix": candidate.prefix,
                         "position": candidate.position},
              "archive_sha256": candidate.archive_sha256}
    if folder is not None:
        record["files"] = [{"path": path, "bytes": len(data), "sha256": sha256(data)}
                           for path, data in folder.pairs()]
    else:
        record["bundled_shape"] = candidate.bundled_shape
    return record


def _files_record(folder, extra):
    out = []
    for member in container.canonical_order(folder.members):
        row = {"path": member.path, "bytes": len(member.data), "sha256": sha256(member.data)}
        row.update(extra.get(member.path, {}))
        out.append(row)
    return out


def make_manifest_2(build):
    """What sitting 2 built and from where: every member's donor, the keys it
    changes and their values, and the sha256 of every file written. No
    absolute path and no date."""
    edits = []
    for edit in build.edits:
        states = {row["path"]: {"state": row["state"]} for row in edit.plan}
        edits.append({
            "code": edit.code, "name": edit.name, "donor": edit.donor,
            "changes": edit.sweep.changes, "applied": edit.applied,
            "changed": edit.changed, "unchanged": edit.unchanged, "warnings": edit.warnings,
            "thumbnail": THUMBNAIL in edit.folder,
            "dropped": [row["path"] for row in edit.plan if row["state"] == "dropped"],
            "archive": {"era": edit.era, "export_state": edit.state, "bytes": len(edit.archive),
                        "sha256": sha256(edit.archive)},
            "uuid": edit.uuid, "single": edit.single,
            "single_sha256": sha256(build.singles[edit.single]),
            "files": _files_record(edit.folder, states)})
    scratch = []
    for member in build.scratch:
        scratch.append({
            "code": member.code, "name": member.name, "era": member.era,
            "template": brush_model.NEW_BRUSH_DONORS[member.era]["container"],
            "overrides": member.overrides, "sub": member.sub, "polarity": member.polarity,
            "thumbnail": THUMBNAIL in member.folder,
            "uuid": member.uuid, "single": member.single,
            "single_sha256": sha256(build.singles[member.single]),
            "files": _files_record(member.folder, {path: {"made": words}
                                                   for path, words in member.made.items()})})
    without_manifest = {path: data for path, data in build.files().items() if path != MANIFEST_NAME}
    written =sorted(set(build.singles) | {EDITS_FILE, SCRATCH_FILE, CHECKLIST_NAME, MANIFEST_NAME})
    return {
        "schema": MANIFEST_SCHEMA_2,
        "sitting": SITTING_2,
        "complete": build.complete,
        "substitutes": build.substitutes,
        "unfilled": build.unfilled,
        "left_out": [{"code": code, "name": name, "why": why} for code, name, why in build.left_out],
        "donors": [_donor_record(role, build.donors.get(role), build.donor_folders.get(role))
                   for role in ("L", "M")] + [_donor_record("S5", build.shape_pick, None)],
        "templates": {era: dict(row) for era, row in sorted(brush_model.NEW_BRUSH_DONORS.items())},
        "sets": {
            "edits": {"file": EDITS_FILE, "name": EDITS_NAME, "bytes": len(build.edits_bytes),
                      "sha256": sha256(build.edits_bytes), "members": edits},
            "scratch": {"file": SCRATCH_FILE, "name": SCRATCH_NAME, "bytes": len(build.scratch_bytes),
                        "sha256": sha256(build.scratch_bytes), "members": scratch}},
        "file_sha256": {path: sha256(data) for path, data in sorted(without_manifest.items())},
        "written": written,
    }


# ── sitting 2: the checklist ─────────────────────────────────────────────────

def _where_in_studio(keys):
    """Where the schema guesses a setting lives in Brush Studio: "tab, label"."""
    try:
        schema = brush_model.load_schema()
    except CodecError:
        return ""
    tabs = {group["id"]: group["label"] for group in schema.get("groups", [])}
    rows = {row["key"]: row for row in schema.get("keys", [])}
    places = {}
    for key in keys:
        row = rows.get(key)
        if row is None:
            continue
        labels = places.setdefault(str(tabs.get(row.get("group"), row.get("group"))), [])
        if row.get("label") not in labels:
            labels.append(str(row.get("label")))
    return "; ".join(f"{tab}: {', '.join(labels)}" for tab, labels in places.items())


def _scratch_question(member, build):
    code = member.code
    if code == "S1":
        return ("Made from nothing in the current format (220 keys), with our own shape (a soft "
                "round dot), our own grain (an even speckle) and a preview picture we drew (an "
                "S-shaped stroke). Does it draw a soft round line? Does its preview in the list "
                "show our S-shaped stroke?")
    if code == "S2":
        return ("The same as S1 without a preview picture. In the list, is its preview empty, or "
                "did Procreate draw one itself?")
    if code == "S3":
        return ("The same as S1, made in the older format (101 keys) instead. It starts from another "
                "real brush than S1 does, so its size and spacing may differ; the question is whether "
                "it opens and draws. If only one of S1 and S3 works, that decides which format new "
                "brushes are made in.")
    if code == "S4":
        _, shape_width, shape_height = TEXTURES["oval"]
        _, grain_width, grain_height = TEXTURES["big-speckle"]
        return (f"Its name is `{show(member.name).rstrip()}` and ends in a space, which you will "
                "not see. Is the name shown with every accent and both Chinese characters? Its "
                f"shape is twice as wide as it is tall ({shape_width} x {shape_height}) and its "
                f"grain is large ({grain_width} x {grain_height}). Does it draw?")
    if code == "S5":
        return (f"It carries no picture at all. It names a shape that comes with Procreate, "
                f"`{build.shape_name}`, as a Procreate 5 brush does, and no grain. Does it draw with "
                "that shape, as a plain line, or not at all?")
    return ("A dual brush: two brushes working as one, both made here (the second has a hard "
            "square shape). Tap it a second time to open Brush Studio. Does it show two brushes? "
            "Does it draw?")


def _sitting_2_banner(build):
    if build.complete:
        return []
    lines = ["> **This build is not complete.** It was built with `--allow-substitutes`."]
    for role, pick in build.picks.items():
        if pick is None:
            lines.append(f"> {role}: the library holds nothing of the kind asked for; what depends on it "
                         "is left out.")
        elif not pick.as_specified:
            lines.append(f"> {role}: SUBSTITUTE. {pick.note}")
    for code, name, why in build.left_out:
        lines.append(f"> {code} is left out: {why}.")
    lines.append("")
    return lines


def render_checklist_2(build):
    """CHECKLIST.md of sitting 2, in plain words, from what the build holds."""
    edits, scratch = build.edits, build.scratch
    donors = {role: pick.candidate for role, pick in build.donors.items() if pick is not None}
    counts = collections.Counter(edit.donor for edit in edits)
    lines = [
        "# Sitting 2: edited brushes and brushes made from nothing",
        "",
        "This folder was made by `python -I brushes/pipeline/device_tests.py build sitting-2 --confirm`.",
        f"Git keeps three things of it: `{MANIFEST_NAME}`, this checklist, and whatever is put in",
        f"`{RETURNED_DIR}/`. The brush files built here are scratch and are not committed.",
        "",
        "## Before you start: sitting 1 comes first",
        "",
        "Do sitting 1 (`../sitting-1/CHECKLIST.md`) before this one, in the same session: first its",
        "known-bad file, then the control set, ROSW 1 Control. **If ROSW 1 Control does not open,",
        "stop there** and bring back what sitting 1 asks for; do not go on with this checklist.",
        "Every set here is packed the way ROSW 1 Control is. Until the control set has opened, a set",
        "here that fails cannot tell us whether the brushes we wrote are at fault or the packing.",
        "",
        "## What this is for",
        "",
        "Sitting 1 asks whether Procreate opens a set we packed around brushes it made itself.",
        "This sitting asks the next two questions. Nothing in these two sets has been opened in",
        "Procreate yet.",
        "",
        f"1. **{EDITS_NAME}** ({len(edits)} brushes). Does Procreate open a brush whose settings file",
        "   we wrote ourselves after changing one setting? Each brush is a copy of one of two",
        "   brushes from the library, with one setting changed, and is named after that change:",
        "   `L02 plotSpacing=0.1` is the older brush with its spacing set to 0.1. Its shape and grain",
        "   pictures are the original's, byte for byte. A few settings are two or three numbers that",
        "   go together, so a name may show two or three of them.",
        f"2. **{SCRATCH_NAME}** ({len(scratch)} brushes). Does Procreate open a brush made from",
        "   nothing? Every file in these brushes is ours.",
        "",
        "Your screenshots of Brush Studio also tell us what each number in a settings file means,",
        "which today is only a guess.",
        "",
        "It takes about an hour, most of it the screenshots. You need the iPad, Procreate, and a",
        "way to move files to the iPad and back.",
        "",
    ]
    lines += _sitting_2_banner(build)
    lines += [
        "## What is in this folder",
        "",
        "| File | What it is |",
        "|---|---|",
        f"| `{EDITS_FILE}` | the edited brushes, named \"{EDITS_NAME}\", {len(edits)} brushes |",
        f"| `{SCRATCH_FILE}` | the brushes made from nothing, named \"{SCRATCH_NAME}\", {len(scratch)} brushes |",
        f"| `{SINGLES_DIR}/` | every brush of both sets as a `.brush` file of its own, named by its code. "
        "Needed if a set fails; one of them is worth a tap anyway (Step 5b) |",
        f"| `{RETURNED_DIR}/` | empty. What comes back from the iPad goes here |",
        f"| `{MANIFEST_NAME}` | what was built and from where, with checksums. For the comparison afterwards |",
        f"| `{CHECKLIST_NAME}` | this file |",
        "",
        "## What to bring back",
        "",
        "1. The Procreate version, the iPadOS version and the iPad model.",
        "2. Your answers in the two tables below.",
        f"3. One Brush Studio screenshot for each brush of {EDITS_NAME} ({len(edits)} screenshots),",
        "   taken in the order of the list, so that each can be matched to its brush.",
        "4. Three files: both sets shared back out of Procreate, and one brand-new untouched brush.",
        "",
        "Photos of the screen are welcome wherever words are slow.",
        "",
    ]
    lines += _transfer_steps([EDITS_FILE, SCRATCH_FILE])
    lines += [
        f"## Step 3. Import {EDITS_NAME}",
        "",
        f"Tap `{EDITS_FILE}`. Open any canvas, then tap the brush icon at the top right. A brush set",
        f"named **{EDITS_NAME}** should be in the Brush Library, holding {len(edits)} brushes whose names",
        "start with L00, L01 and so on, then M00, M01 and so on.",
        "",
        "If Procreate shows a message instead, write down its words, then go to \"If a set does not",
        "import\" below.",
        "",
        "## Step 4. Each edited brush: three questions and one screenshot",
        "",
    ]
    for role, words in (("L", "an older brush (the 101-key format), the same brush as member 2 of sitting 1"),
                        ("M", "a current brush (the 220-key format)")):
        if role in donors:
            lines.append(f"- The {counts[role]} **{role}** brushes are copies of "
                         f"**{show(donors[role].name).strip()}**, {words}.")
    lines += [
        "- A brush called \"name only\" changes nothing but its name. L00 and M00 keep the original's",
        "  preview picture. **Every other brush has no preview picture in its file**, so if its row",
        "  in the list shows a stroke, Procreate drew it.",
        "",
        "Pick black. For each brush, in list order:",
        "",
        "1. **Listed?** Is it there, under its name?",
        "2. **Preview?** What does its row in the list show: a stroke, or nothing?",
        "3. **Draws?** Select it and draw one stroke across the canvas. Does a mark appear?",
        "4. **Screenshot.** Tap the selected brush again to open Brush Studio. Open the tab the table",
        "   names (our guess at where the changed setting is) and take a screenshot (top button and",
        "   volume up together). For a \"name only\" brush, the \"About this brush\" tab. Then",
        "   leave with Cancel, so that nothing is changed before you share the set back.",
        "",
        "Anything else you notice goes beside the row: a message, Procreate closing, a stroke that",
        "looks wrong, a setting that is not where the table says.",
        "",
        "| # | Name | Where we think the setting is | Listed? | Preview? | Draws? | Screenshot? |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, edit in enumerate(edits, 1):
        place = _where_in_studio(edit.sweep.changes) if edit.sweep.changes else "About this brush"
        same = " (the original's own value)" if edit.sweep.changes and not edit.changed else ""
        lines.append(f"| {index} | {show(edit.name).replace('|', '/')}{same} | {place or '?'} |  |  |  |  |")
    lines += [
        "",
        "\"The original's own value\" means the copy holds the value the original already had: it",
        "shows what that value is called in Brush Studio.",
        "",
        f"## Step 5. Import {show(SCRATCH_NAME)}",
        "",
        f"Tap `{SCRATCH_FILE}`. The new set's name should read exactly **{SCRATCH_NAME}**: an",
        "ampersand, two accented letters and a water drop. Write down what it shows if it differs.",
        "",
        "For each brush, the same three questions, and its own question:",
        "",
        "| # | Name | Listed? | Preview? | Draws? |",
        "|---|---|---|---|---|",
    ]
    for index, member in enumerate(scratch, 1):
        lines.append(f"| {index} | {show(member.name).strip().replace('|', '/')} |  |  |  |")
    lines.append("")
    for member in scratch:
        lines.append(f"- **{show(member.name).strip()}.** {_scratch_question(member, build)}")
    first = scratch[0] if scratch else None
    lines += [
        "",
        "Leave Brush Studio with Cancel each time.",
        "",
    ]
    if first is not None:
        lines += [
            "## Step 5b (optional, one tap). A loose brush file of ours",
            "",
            f"Even if both sets imported, tap `{first.single}` once. It is the brush",
            f"{show(first.name).strip()} again, as a single `.brush` file, and a loose brush file we wrote",
            "is otherwise never tested. It lands in the set named \"Imported\". Note whether it",
            "arrives and whether it draws, then delete it from \"Imported\".",
            "",
        ]
    lines += [
        "### If a set does not import, or a brush is missing or will not draw",
        "",
        f"Open the files in `{SINGLES_DIR}/` of that set one at a time: their names start with the",
        "brush's code (L00, M03, S2 and so on). A single brush lands in the set named \"Imported\".",
        "Note for each file whether it arrives and whether it draws. Start with L00, M00 and S1,",
        "the plainest of each kind.",
        "",
        "## Step 6. The return leg: share three things back",
        "",
        f"**a. {EDITS_NAME}.** In the Brush Library, tap the set name so that it is selected, then",
        "tap it once more. A small menu appears: choose Share. Save the file to Files. It is saved",
        "as a `.brushset` file. It shows what Procreate kept of each brush, the preview it draws",
        "for each value, and how it writes these settings itself.",
        "",
        f"**b. {SCRATCH_NAME}.** The same.",
        "",
    ]
    lines += _new_brush_step("c")
    lines += ["Keep the file names Procreate gives them.", ""]
    lines += _returned_steps(7, SITTING_2, "the three files and your screenshots")
    lines += _closing_lines("both sets")
    return "\n".join(lines)


# ── sitting 2: the plan ──────────────────────────────────────────────────────

def _changes_text(edit):
    if not edit.sweep.changes:
        return "-"
    if not edit.changed:
        return "the donor's own value"
    if edit.unchanged:
        return f"{', '.join(edit.changed)} (already: {', '.join(edit.unchanged)})"
    return ", ".join(edit.changed)


def render_plan_2(build, library, out):
    scan = build.scan
    lines = ["Sitting 2: edited brushes and brushes made from nothing", "", f"library   {library}"]
    for part in LIBRARY_PARTS:
        lines.append(f"          {part + '/':<10} {scan.files[part]:>4} files, {scan.brushes[part]:>4} brushes")
    if scan.skipped:
        lines.append(f"          passed over: {len(scan.skipped)}")
        lines += [f"            {where}: {why}" for where, why in scan.skipped]
    lines += ["", "donors (an edited brush is its donor with one setting changed and its archive "
                  "rule-encoded; its other files are the donor's)"]
    for role, pick in build.picks.items():
        if pick is None:
            lines.append(f"  {role:<3} EMPTY         the library holds nothing of any kind the slot accepts")
            continue
        candidate = pick.candidate
        label = "as specified" if pick.as_specified else "SUBSTITUTE  "
        lines.append(f"  {role:<3} {label}  {show(candidate.name)!r}   {candidate.era_text}, "
                     f"{candidate.keys} keys")
        lines.append(f"       wanted  {pick.slot.wanted}")
        if pick.note:
            lines.append(f"       NOTE    {pick.note}")
        lines.append(f"       source  {show(candidate.where)}"
                     + (f"   (set {show(candidate.set_name)!r}, place {candidate.position + 1})"
                        if candidate.set_name is not None else "   (a loose brush)"))
        if role == "S5":
            lines.append(f"       name    {show(candidate.bundled_shape)}")
        else:
            lines.append(f"       files   {len(candidate.paths)}, {candidate.total:,} bytes: "
                         f"{', '.join(show(path) for path in candidate.paths)}")
    lines += ["", "new-brush templates (brush_model.NEW_BRUSH_DONORS)"]
    for era, row in sorted(brush_model.NEW_BRUSH_DONORS.items()):
        lines.append(f"  {era:<5} {row['container']} :: {row['entry']}")
    lines += ["", f"{EDITS_FILE}   \"{EDITS_NAME}\"   {len(build.edits)} brushes, "
                  f"{len(build.edits_bytes):,} bytes",
              f"  {'name':<46} {'keys changed':<56} {'archive':<16} thumbnail"]
    for edit in build.edits:
        lines.append(f"  {show(edit.name)[:46]:<46} {_changes_text(edit)[:56]:<56} "
                     f"{edit.era + ' ' + edit.state:<16} {'kept' if THUMBNAIL in edit.folder else '-'}"
                     + (f"   warning {', '.join(w['code'] + ' ' + w['key'] for w in edit.warnings)}"
                        if edit.warnings else ""))
    for code, name, why in build.left_out:
        lines.append(f"  LEFT OUT {code}  {show(name)!r}: {why}")
    lines += ["", f"{SCRATCH_FILE}   \"{show(SCRATCH_NAME)}\"   {len(build.scratch)} brushes, "
                  f"{len(build.scratch_bytes):,} bytes"]
    for member in build.scratch:
        lines.append(f"  {show(member.name)!r}   {member.era}")
        for path in member.folder.paths():
            lines.append(f"       {show(path):<24} {len(member.folder.get(path)):>11,} bytes   {member.made[path]}")
    exact = sum(1 for pick in build.picks.values() if pick is not None and pick.as_specified)
    lines += ["", f"  {exact} of {len(build.picks)} donors are as specified, {len(build.substitutes)} "
                  f"are substitutes, {len(build.unfilled)} are empty; {len(build.left_out)} members "
                  "are left out."]
    if not build.complete:
        lines.append("  NOT COMPLETE   such a build is written only with --allow-substitutes.")
    lines += ["", f"out       {out}"]
    for relative, data in build.files().items():
        lines.append(f"          {relative:<58} {len(data):>12,} bytes")
    lines.append(f"          {RETURNED_DIR + '/':<58} {'(empty)':>18}")
    return "\n".join(lines)


def refusal_2(build):
    if build.complete:
        return ""
    parts = []
    if build.substitutes:
        parts.append(f"{', '.join(build.substitutes)} {'is a substitute' if len(build.substitutes) == 1 else 'are substitutes'}")
    if build.unfilled:
        parts.append(f"nothing was found for {', '.join(build.unfilled)}")
    if build.left_out:
        parts.append(f"{len(build.left_out)} member{'s are' if len(build.left_out) != 1 else ' is'} left out")
    return (f"sitting 2 is not complete: {' and '.join(parts)}. Nothing is written. Pass "
            "--allow-substitutes to build it as it is; a sitting with such a build answers less.")


# ── writing ──────────────────────────────────────────────────────────────────

def default_out(paths, sitting):
    return paths.root / OUT_HOME / sitting


def resolve_out(paths, out, sitting):
    """The folder a sitting is written to. Inside the brushes/ folder only
    device-tests/ may be written; the library is never written, wherever it is."""
    if out is None or not str(out).strip():
        return default_out(paths, sitting)
    target = Path(os.path.expanduser(str(out))).resolve()
    home = (paths.root / OUT_HOME).resolve()
    root = paths.root.resolve()
    library = paths.library.resolve()
    if target == library or library in target.parents:
        raise EnvironmentProblem(f"--out {target} is inside the library, which this command never writes")
    inside_tool = target == root or root in target.parents
    if inside_tool and not (target == home or home in target.parents):
        raise EnvironmentProblem(f"--out {target} is inside {root}; there, only {home} may be written")
    return target


def _own_files(out):
    """The files an earlier build wrote in `out`, by its manifest: only plain
    relative names under singles/ and known-bad/ are believed."""
    try:
        manifest = json.loads(bc.read_text(Path(out) / MANIFEST_NAME))
    except (OSError, UnicodeDecodeError, ValueError):
        return set()
    listed = manifest.get("written") if isinstance(manifest, dict) else None
    own = set()
    for name in listed if isinstance(listed, list) else ():
        parts = name.split("/") if isinstance(name, str) else []
        if (len(parts) == 2 and parts[0] in (SINGLES_DIR, KNOWN_BAD_DIR)
                and parts[1] not in ("", ".", "..") and "\\" not in name and ":" not in name):
            own.add(name)
    return own


def check_returned(out):
    """Refuse a folder whose returned/ holds files: they came back from a sitting
    made with the build that is there, and are compared with its manifest."""
    returned = Path(out) / RETURNED_DIR
    if returned.is_dir() and any(path.is_file() for path in returned.rglob("*")):
        raise DeviceTestError(
            f"{returned} holds files. They came back from a sitting made with the build that is "
            "there now, and a new build would replace the manifest they are compared with. "
            "Build into another folder with --out, or move those files away first.")


def write_build(build, out):
    """Write a build into `out`. Returns the relative paths written and removed."""
    out = Path(out)
    check_returned(out)
    returned = out / RETURNED_DIR
    files = build.files()
    stale = sorted(_own_files(out) - set(files))
    for relative, data in files.items():
        bc.write_bytes(out.joinpath(*relative.split("/")), data)
    removed = []
    for relative in stale:
        path = out.joinpath(*relative.split("/"))
        if path.is_file() and not path.is_symlink():
            path.unlink()
            removed.append(relative)
    returned.mkdir(parents=True, exist_ok=True)
    return sorted(files), removed


# ── the second pass ──────────────────────────────────────────────────────────

def _plain_relative(name):
    parts = name.split("/") if isinstance(name, str) else [""]
    return all(part not in ("", ".", "..") for part in parts) and "\\" not in name and ":" not in name


def _zip_rows(data):
    """[(name, bytes, entry)] of a zip, read with zipfile, in file order; and
    the name of the first entry whose checksum fails, or None."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        broken = archive.testzip()
        return [(info.orig_filename, archive.read(info), info) for info in archive.infolist()], broken


def _source_files(library, source):
    """[(path inside the folder, bytes)] of a member as the library file holds
    it now, read here with zipfile alone, without the builder's reader: the
    first entry of each name under the folder, junk and folder entries left out."""
    container_path = source["container"]
    if not _plain_relative(container_path) or container_path.split("/")[0] not in LIBRARY_PARTS:
        raise DeviceTestError(f"the manifest names a source outside the library: {show(container_path)}")
    path = Path(library).joinpath(*container_path.split("/"))
    if not path.is_file() or path.stat().st_size > CAPS["upload_bytes"]:
        raise DeviceTestError(f"the source {show(container_path)} is not in the library")
    prefix = source["prefix"]
    files, seen = [], set()
    with open(path, "rb") as handle, zipfile.ZipFile(handle) as archive:
        for info in archive.infolist():
            name = info.orig_filename
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            inside = name[len(prefix):]
            if inside in seen or container.is_junk(inside) or info.file_size > CAPS["entry_bytes"]:
                continue
            seen.add(inside)
            files.append((inside, archive.read(info)))
    return files


def _source_rows(library, source):
    """[(path inside the folder, sha256, size)] of a member as the library file
    holds it now, read here without the builder's reader."""
    return [(inside, sha256(content), len(content)) for inside, content in _source_files(library, source)]


def incomplete(manifest):
    """Why a manifest's build is not the control set, in a few words, or "".
    Read from the members and the empty slots themselves, not from the
    manifest's own `complete` flag."""
    members = manifest.get("members", [])
    substitutes = [member["slot"] for member in members if member.get("as_specified") is not True]
    unfilled = [slot["slot"] for slot in manifest.get("unfilled", [])]
    parts = []
    if substitutes:
        parts.append(f"{len(substitutes)} of {len(members)} members are substitutes "
                     f"(slot{'s' if len(substitutes) != 1 else ''} "
                     f"{', '.join(str(number) for number in substitutes)})")
    if unfilled:
        parts.append(f"{len(unfilled)} slot{'s are' if len(unfilled) != 1 else ' is'} empty "
                     f"({', '.join(str(number) for number in unfilled)})")
    if not parts and len(members) != len(SLOTS):
        parts.append(f"it holds {len(members)} members, not {len(SLOTS)}")
    return "; ".join(parts)


def _read_manifest(out, schema, sets):
    try:
        manifest = json.loads(bc.read_text(out / MANIFEST_NAME))
        data = {name: (out / name).read_bytes() for name in sets}
    except (OSError, UnicodeDecodeError, ValueError):
        raise EnvironmentProblem(f"there is no built sitting in {out} (no readable {MANIFEST_NAME} "
                                 f"and {' and '.join(sets)})") from None
    if not isinstance(manifest, dict) or manifest.get("schema") != schema:
        raise EnvironmentProblem(f"{out / MANIFEST_NAME} is not a {schema} manifest")
    return manifest, data


def verify_sitting(library, out, *, allow_substitutes=False):
    """(ok, lines): the built files of sitting 1 checked against the library.

    A build with a substitute or an empty slot is not the control set: it is
    reported, and fails the check unless `allow_substitutes` is true.
    Raises EnvironmentProblem when there is nothing built in `out`.
    """
    out = Path(out)
    manifest, data = _read_manifest(out, MANIFEST_SCHEMA, [SET_FILE])
    try:
        return _verify(Path(library), out, manifest, data[SET_FILE], allow_substitutes)
    except (KeyError, TypeError, AttributeError):
        raise EnvironmentProblem(f"{out / MANIFEST_NAME} is not a complete manifest; "
                                 "build the sitting again") from None


def _verify(library, out, manifest, set_data, allow_substitutes=False):
    lines, problems = [], []

    def check(condition, message):
        if not condition:
            problems.append(message)
        return condition

    try:
        rows, broken = _zip_rows(set_data)
    except ZIP_ERRORS as exc:
        return False, [f"NOT VERIFIED   {SET_FILE} cannot be opened as a zip ({type(exc).__name__}: {exc})"]
    members = manifest.get("members", [])
    uuids = [member["uuid"] for member in members]
    lines.append(f"{SET_FILE}   {len(set_data):,} bytes   sha256 {sha256(set_data)}")
    check(sha256(set_data) == manifest["set"]["sha256"], "the set is not the file the manifest describes")
    check(broken is None, f"the checksum of entry {broken} fails")

    # The plist.
    plist_raw = next((content for name, content, _ in rows if name == SET_PLIST), None)
    lines += ["", SET_PLIST]
    if check(plist_raw is not None, f"the set holds no {SET_PLIST}"):
        check(rows[-1][0] == SET_PLIST, f"{SET_PLIST} is not the last entry")
        try:
            plist = plistlib.loads(plist_raw, fmt=plistlib.FMT_XML)
        except Exception as exc:                # whatever a broken plist raises
            plist = None
            check(False, f"{SET_PLIST} cannot be parsed ({type(exc).__name__})")
        if isinstance(plist, dict):
            lines.append(f"  keys     {', '.join(plist)}")
            lines.append(f"  name     {plist.get('name')!r}")
            lines.append(f"  brushes  {len(plist.get('brushes', []))} folder names")
            check(list(plist) == ["brushes", "name"], f"{SET_PLIST} keys are {list(plist)}")
            check(plist.get("name") == SET_NAME, f"the set name is {plist.get('name')!r}")
            check(plist.get("brushes") == uuids, "the plist's folder names are not the manifest's, in order")
        same_form = plist_raw == brushset_plist(SET_NAME, uuids) if uuids else False
        oracle = plistlib.dumps({"brushes": uuids, "name": SET_NAME}, fmt=plistlib.FMT_XML,
                                sort_keys=False)
        lines.append(f"  form     {'exact' if same_form and plist_raw == oracle else 'DIFFERS'}"
                     "   (the XML form the app's own sets use; also what plistlib writes)")
        check(same_form and plist_raw == oracle, f"{SET_PLIST} is not in the exact XML form")

    # The folder names.
    folders = []
    for name, _, _ in rows:
        top = name.split("/", 1)[0]
        if name != SET_PLIST and top not in folders:
            folders.append(top)
    distinct = len(set(uuids)) == len(uuids)
    formed = all(UUID_FORM.fullmatch(name) for name in uuids)
    lines += ["", f"folder names   {len(uuids)} in the manifest, {len(folders)} in the zip, "
                  f"{'all distinct' if distinct else 'NOT DISTINCT'}, "
                  f"{'all upper-case version-4 UUIDs' if formed else 'NOT ALL UUIDs'}"]
    check(distinct, "two members share a folder name")
    check(formed, "a folder name is not an upper-case version-4 UUID")
    check(folders == uuids, "the folders in the zip are not the manifest's, in order")
    check(all("/" in name or name == SET_PLIST for name, _, _ in rows),
          "the zip holds an entry outside the brush folders")
    check(not any(name.endswith("/") for name, _, _ in rows), "the zip holds a directory entry")

    # Every member file against its source.
    lines += ["", "members, each file against the library file it came from",
              f"  {'#':>2}  {'file':<34} {'bytes':>11}  {'sha256 (set)':<16} {'sha256 (source)':<16} result"]
    for member in members:
        number, folder = member["slot"], member["uuid"]
        label = "as specified" if member["as_specified"] else "SUBSTITUTE"
        lines.append(f"  {number:>2}  {show(member['name'])!r}  {member['era']}, {member['keys']} keys, "
                     f"{label}  <-  {show(member['source']['container'])}"
                     + (f"!/{member['source']['folder']}" if member["source"]["folder"] else ""))
        lines.append(f"      folder {folder}")
        built = [(name[len(folder) + 1:], sha256(content), len(content))
                 for name, content, _ in rows if name.startswith(folder + "/")]
        try:
            source = _source_rows(library, member["source"])
        except (DeviceTestError,) + ZIP_ERRORS as exc:
            source = []
            check(False, f"member {number}: its source cannot be read ({exc})")
        recorded = [(item["path"], item["sha256"], item["bytes"]) for item in member["files"]]
        for index in range(max(len(built), len(source))):
            ours = built[index] if index < len(built) else ("(missing)", "", 0)
            theirs = source[index] if index < len(source) else ("(missing)", "", 0)
            same = ours == theirs
            lines.append(f"      {show(ours[0]):<34} {ours[2]:>11,}  {ours[1][:16]:<16} {theirs[1][:16]:<16} "
                         f"{'identical' if same else 'DIFFERENT'}")
            check(same, f"member {number}: {show(ours[0])} is not its source file {show(theirs[0])}")
        check(built == recorded, f"member {number}: the set does not hold what the manifest lists")
        check(bool(built), f"member {number}: the set holds no file for it")
        # Its loose copy.
        single = member["single"]
        try:
            if not _plain_relative(single):
                raise OSError("not a plain relative name")
            single_rows, single_broken = _zip_rows(out.joinpath(*single.split("/")).read_bytes())
            loose = [(name, sha256(content), len(content)) for name, content, _ in single_rows]
            good = loose == source and single_broken is None
            fields_ok = all(getattr(info, attribute) == wanted
                            for _, _, info in single_rows for _, attribute, wanted in HEADER_FIELDS)
        except ZIP_ERRORS as exc:
            good, fields_ok = False, True
            check(False, f"member {number}: {single} cannot be read ({type(exc).__name__})")
        verdict = "identical to the source, entries at the zip root" if good else "DIFFERENT"
        lines.append(f"      {single}: {verdict}")
        check(good, f"member {number}: {single} does not hold the source files at its root")
        check(fields_ok, f"member {number}: {single} has an entry with other header fields")

    # The header fields of every entry of the set.
    lines += ["", "zip header fields of every entry of the set (zipfile's names)",
              "  method flags  made-by(sys,ver) needs ext-attr int-attr extra comment  "
              "date                 name"]
    for name, content, info in rows:
        lines.append(_header_line(name, info))
        for label, attribute, wanted in HEADER_FIELDS:
            check(getattr(info, attribute) == wanted,
                  f"{show(name)}: {label} is {getattr(info, attribute)!r}, not {wanted!r}")
        # Bit 0 says "text": set for the plist, as in the app's own sets; never more than that bit.
        check(info.internal_attr == 1 if name == SET_PLIST else info.internal_attr in (0, 1),
              f"{show(name)}: the internal attribute is {info.internal_attr}")
    with zipfile.ZipFile(io.BytesIO(set_data)) as archive:
        check(archive.comment == b"", "the zip carries a comment")
    lines.append(f"  {len(rows)} entries; wanted: method 8, flags 0x0006, made by 0,0, needs 20, "
                 "external attribute 0, no extra, no comment, no directory entry")

    # The known-bad copy.
    known = manifest.get("known_bad")
    if known:
        try:
            if not _plain_relative(known["file"]):
                raise OSError("not a plain relative name")
            copy = out.joinpath(*known["file"].split("/")).read_bytes()
            same = sha256(copy) == known["sha256"]
        except OSError:
            same = False
        lines += ["", f"{known['file']}   {'as copied' if same else 'DIFFERENT'}   ({known['finding']})"]
        check(same, f"{known['file']} is not the file that was copied")

    # Is it the control set at all?
    short = incomplete(manifest)
    check(manifest.get("complete") is (not short), "the manifest's `complete` flag does not match its members")
    if short:
        lines += ["", f"INCOMPLETE   this is not the control set: {short}."]
        if allow_substitutes:
            lines.append("             Allowed by --allow-substitutes. A sitting with it answers less.")
        else:
            check(False, f"this is not the control set: {short}. Fetch the official sets "
                         f"(`{FETCH_COMMAND}`) and build again, or pass --allow-substitutes")

    lines.append("")
    if problems:
        lines += [f"  problem: {problem}" for problem in problems]
        lines.append(f"NOT VERIFIED   {len(problems)} problem{'s' if len(problems) != 1 else ''}")
    else:
        files = sum(len(member["files"]) for member in members)
        lines.append(f"VERIFIED   {len(members)} members, {files} files, each identical to its source; "
                     f"{len(rows)} zip entries with the intended header fields"
                     + ("" if not short else "; NOT the control set (substitutes allowed)"))
    return not problems, lines


def _header_line(name, info):
    date = "%04d-%02d-%02d %02d:%02d:%02d" % info.date_time
    return (f"  {info.compress_type:>6} 0x{info.flag_bits:04x}  {info.create_system:>7},"
            f"{info.create_version:<7} {info.extract_version:>5} {info.external_attr:>8} "
            f"{info.internal_attr:>8} {len(info.extra):>5} {len(info.comment):>7}  {date}  {show(name)}")


# ── sitting 2: the second pass ───────────────────────────────────────────────

def _plain_value(objects, value, depth=0, path=()):
    """A value of a keyed archive read by plistlib, with every reference
    followed: a tuple that compares equal exactly when the two values are the
    same, type for type, whatever the objects' numbering."""
    if depth > 48:
        return ("deep",)
    if isinstance(value, plistlib.UID):
        number = value.data
        if number in path or not 0 <= number < len(objects):
            return ("uid", number)
        return _plain_value(objects, objects[number], depth + 1, path + (number,))
    if isinstance(value, dict):
        return ("dict", tuple(sorted((str(key), _plain_value(objects, item, depth + 1, path))
                                     for key, item in value.items())))
    if isinstance(value, list):
        return ("list", tuple(_plain_value(objects, item, depth + 1, path) for item in value))
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        return ("real", struct.pack(">d", value))
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, bytes):
        return ("data", value)
    return (type(value).__name__, repr(value))


def plain_root(data):
    """{root key: plain value} of a Brush.archive, read by plistlib alone."""
    top = plistlib.loads(data, fmt=plistlib.FMT_BINARY)
    objects = top["$objects"]
    root = objects[top["$top"]["root"].data]
    return {str(key): _plain_value(objects, value) for key, value in root.items()}


def _field(plain, name):
    """The plain value under `name` in a plain dict value, or None."""
    if not plain or plain[0] != "dict":
        return None
    return dict(plain[1]).get(name)


def plain_text(plain):
    """The text of a plain string value, wrapped in an NSMutableString or not."""
    if plain and plain[0] == "str":
        return plain[1]
    inner = _field(plain, "NS.string")
    return inner[1] if inner and inner[0] == "str" else None


def _curve_strings(points):
    """The point strings a curve patch of numeric pairs becomes: "{x, y}" with
    six decimals, the two end points first and the points between by x."""
    pairs = sorted((float(x), float(y)) for x, y in points)
    ordered = [pairs[0], pairs[-1]] + pairs[1:-1]
    return ["{%.6f, %.6f}" % (x + 0.0, y + 0.0) for x, y in ordered]


def holds(plain, wanted):
    """Whether a plain value is the value a sweep asked for: a real by its
    32-bit pattern, an int or a bool by type and value, a curve by its points."""
    if isinstance(wanted, bool):
        return plain == ("bool", wanted)
    if isinstance(wanted, int):
        return plain == ("int", wanted)
    if isinstance(wanted, float):
        if not plain or plain[0] != "real":
            return False
        found = struct.unpack(">d", plain[1])[0]
        return struct.pack(">f", found) == struct.pack(">f", wanted)
    if isinstance(wanted, dict) and "points" in wanted:
        points = _field(plain, "points")
        objects = _field(points, "NS.objects")
        if not objects or objects[0] != "list":
            return False
        return [item[1] if item[0] == "str" else None for item in objects[1]] == _curve_strings(wanted["points"])
    return False


def _member_rows(rows, folder):
    return [(name[len(folder) + 1:], content) for name, content, _ in rows if name.startswith(folder + "/")]


def _check_set_2(record, data, lines, check):
    """The checks every set of sitting 2 shares: its bytes, its plist, its
    folder names and the header fields of its entries. Returns the zip rows."""
    name, label = record["name"], record["file"]
    rows, broken = _zip_rows(data)
    uuids = [member["uuid"] for member in record["members"]]
    lines.append(f"{label}   {len(data):,} bytes   sha256 {sha256(data)}")
    check(sha256(data) == record["sha256"], f"{label} is not the file the manifest describes")
    check(broken is None, f"{label}: the checksum of entry {broken} fails")
    plist_raw = next((content for entry, content, _ in rows if entry == SET_PLIST), None)
    if check(plist_raw is not None, f"{label} holds no {SET_PLIST}"):
        check(rows[-1][0] == SET_PLIST, f"{label}: {SET_PLIST} is not the last entry")
        try:
            plist = plistlib.loads(plist_raw, fmt=plistlib.FMT_XML)
        except Exception as exc:                # whatever a broken plist raises
            plist = None
            check(False, f"{label}: {SET_PLIST} cannot be parsed ({type(exc).__name__})")
        if isinstance(plist, dict):
            check(list(plist) == ["brushes", "name"], f"{label}: {SET_PLIST} keys are {list(plist)}")
            check(plist.get("name") == name, f"{label}: the set name is {plist.get('name')!r}")
            check(plist.get("brushes") == uuids, f"{label}: the plist's folder names are not the manifest's")
        oracle = plistlib.dumps({"brushes": uuids, "name": name}, fmt=plistlib.FMT_XML, sort_keys=False)
        check(plist_raw == oracle, f"{label}: {SET_PLIST} is not what plistlib writes for its keys")
        lines.append(f"  {SET_PLIST}   keys brushes, name   name {name!r}   "
                     f"{'the exact XML plistlib writes' if plist_raw == oracle else 'DIFFERS'}")
    folders = []
    for entry, _, _ in rows:
        top = entry.split("/", 1)[0]
        if entry != SET_PLIST and top not in folders:
            folders.append(top)
    distinct = len(set(uuids)) == len(uuids)
    formed = all(UUID_FORM.fullmatch(folder) for folder in uuids)
    check(distinct and formed, f"{label}: folder names are not distinct upper-case version-4 UUIDs")
    check(folders == uuids, f"{label}: the folders in the zip are not the manifest's, in order")
    check(not any(entry.endswith("/") for entry, _, _ in rows), f"{label}: a directory entry")
    forms = collections.Counter()
    for entry, _, info in rows:
        form = next((key for key, pair in FORM_FIELDS.items()
                     if pair == (info.compress_type, info.flag_bits)), None)
        forms[form or "OTHER"] += 1
        check(form is not None, f"{label}: {show(entry)} is stored in no known form")
        for field_label, attribute, wanted in COMMON_FIELDS:
            check(getattr(info, attribute) == wanted,
                  f"{label}: {show(entry)}: {field_label} is {getattr(info, attribute)!r}")
        check(info.internal_attr == 1 if entry == SET_PLIST else info.internal_attr in (0, 1),
              f"{label}: {show(entry)}: the internal attribute is {info.internal_attr}")
    lines.append(f"  folder names   {len(uuids)}, {'distinct' if distinct else 'NOT DISTINCT'}, "
                 f"{'upper-case version-4 UUIDs' if formed else 'NOT ALL UUIDs'}, in plist order"
                 f"   entries {len(rows)} ({', '.join(f'{count} {form}' for form, count in sorted(forms.items()))})")
    return rows


def _check_single(out, member, built, check):
    single = member["single"]
    try:
        if not _plain_relative(single):
            raise OSError("not a plain relative name")
        data = out.joinpath(*single.split("/")).read_bytes()
        rows, broken = _zip_rows(data)
    except ZIP_ERRORS as exc:
        check(False, f"{member['code']}: {single} cannot be read ({type(exc).__name__})")
        return False
    good = ([(name, content) for name, content, _ in rows] == built and broken is None
            and sha256(data) == member["single_sha256"])
    check(good, f"{member['code']}: {single} does not hold the member's files at its root")
    fields = all((info.compress_type, info.flag_bits) in FORM_FIELDS.values()
                 and all(getattr(info, attribute) == wanted for _, attribute, wanted in COMMON_FIELDS)
                 for _, _, info in rows)
    check(fields, f"{member['code']}: {single} has an entry with other header fields")
    return good and fields


def _decode(data):
    """(era, fidelity, error) of an archive by brush_model.decode."""
    try:
        brush = brush_model.decode(data)
    except CodecError as exc:
        return None, None, _why(exc)
    return brush.era, brush.fidelity, ""


def verify_sitting_2(library, out, *, allow_substitutes=False):
    """(ok, lines): the built files of sitting 2 checked against the library
    and the manifest. Raises EnvironmentProblem when nothing is built in `out`."""
    out = Path(out)
    manifest, data = _read_manifest(out, MANIFEST_SCHEMA_2, [EDITS_FILE, SCRATCH_FILE])
    try:
        return _verify_2(Path(library), out, manifest, data, allow_substitutes)
    except (KeyError, TypeError, AttributeError, IndexError):
        raise EnvironmentProblem(f"{out / MANIFEST_NAME} is not a complete manifest; "
                                 "build the sitting again") from None


def _verify_2(library, out, manifest, data, allow_substitutes):
    lines, problems = [], []

    def check(condition, message):
        if not condition:
            problems.append(message)
        return condition

    edits, scratch = manifest["sets"]["edits"], manifest["sets"]["scratch"]

    # The donors, read again from the library with zipfile alone.
    donors = {}
    for donor in manifest["donors"]:
        if donor["role"] not in ("L", "M") or not donor.get("source"):
            continue
        try:
            files = _source_files(library, donor["source"])
        except (DeviceTestError,) + ZIP_ERRORS as exc:
            check(False, f"donor {donor['role']}: its source cannot be read ({exc})")
            continue
        recorded = [(item["path"], item["sha256"]) for item in donor.get("files", [])]
        check([(path, sha256(content)) for path, content in files] == recorded,
              f"donor {donor['role']}: the library file is no longer what the build read")
        donors[donor["role"]] = dict(files)

    # ROSW 2 Edits.
    try:
        rows = _check_set_2(edits, data[EDITS_FILE], lines, check)
    except ZIP_ERRORS as exc:
        return False, [f"NOT VERIFIED   {EDITS_FILE} cannot be opened as a zip ({type(exc).__name__}: {exc})"]
    lines += ["", f"  {'name':<44} {'keys that differ from the donor (plistlib), name aside':<76} "
                  f"{'values':<7} {'textures':<9} {'thumbnail':<9} {'decodes':<12} single  result"]
    for member in edits["members"]:
        built = _member_rows(rows, member["uuid"])
        mine = []

        def own(condition, message):
            if not condition:
                mine.append(message)
            return check(condition, f"{member['code']}: {message}")

        own([(path, sha256(content), len(content)) for path, content in built]
            == [(item["path"], item["sha256"], item["bytes"]) for item in member["files"]],
            "the set does not hold the files the manifest lists")
        built_files = dict(built)
        archive = built_files.get(BRUSH_ARCHIVE, b"")
        era, fidelity, error = _decode(archive)
        own(not error, f"the archive does not decode ({error})")
        own(era == member["archive"]["era"], f"the archive decodes as {era}, not {member['archive']['era']}")
        donor_files = donors.get(member["donor"])
        diff, values_ok, textures, thumb = ["?"], False, "?", "?"
        if own(donor_files is not None, f"donor {member['donor']} could not be read"):
            try:
                theirs, ours = plain_root(donor_files[BRUSH_ARCHIVE]), plain_root(archive)
            except Exception as exc:            # whatever a broken plist raises
                own(False, f"plistlib cannot read the archives ({type(exc).__name__})")
                theirs = ours = {}
            differing = sorted(key for key in set(theirs) | set(ours) if theirs.get(key) != ours.get(key))
            diff = [key for key in differing if key != "name"]
            own(set(differing) == set(member["changed"]) | {"name"},
                f"plistlib finds {', '.join(differing) or 'nothing'} changed, not "
                f"{', '.join(member['changed'] + ['name'])}")
            own(plain_text(ours.get("name")) == member["name"], "the archive does not hold the member's name")
            values_ok = all(holds(ours.get(key), value) for key, value in member["changes"].items())
            own(values_ok, "a key does not hold the value the member's name says")
            others = {path: content for path, content in donor_files.items()
                      if path not in (BRUSH_ARCHIVE, THUMBNAIL)}
            same = all(built_files.get(path) == content for path, content in others.items())
            extra = sorted(set(built_files) - set(others) - {BRUSH_ARCHIVE, THUMBNAIL})
            own(same and not extra, "its files beside the archive are not the donor's, byte for byte")
            textures = f"{len(others)} same" if same and not extra else "DIFFERENT"
            if member["thumbnail"]:
                kept = (donor_files.get(THUMBNAIL) is not None
                        and built_files.get(THUMBNAIL) == donor_files.get(THUMBNAIL))
                own(kept, "the thumbnail is not the donor's")
                thumb = "donor's" if kept else "DIFFERENT"
            else:
                own(THUMBNAIL not in built_files, "it holds a thumbnail")
                thumb = "none" if THUMBNAIL not in built_files else "PRESENT"
        single = _check_single(out, member, built, check)
        if not member["changes"]:
            shown = "- (name only)"
        elif not diff:
            shown = "- (the donor's own value)"
        else:
            shown = ", ".join(diff)
        lines.append(f"  {show(member['name'])[:44]:<44} {shown[:76]:<76} {'ok' if values_ok else 'WRONG':<7} "
                     f"{textures:<9} {thumb:<9} {(era or '-') + ' ' + (fidelity or error[:6]):<12} "
                     f"{'ok' if single else 'BAD':<7} {'ok' if not mine else 'FAILED'}")

    # ROSW 3 Scratch.
    lines.append("")
    try:
        rows = _check_set_2(scratch, data[SCRATCH_FILE], lines, check)
    except ZIP_ERRORS as exc:
        return False, lines + [f"NOT VERIFIED   {SCRATCH_FILE} cannot be opened as a zip "
                               f"({type(exc).__name__}: {exc})"]
    lines += ["", f"  {'name':<26} {'archives (brush_model.decode)':<34} {'files':<44} single  result"]
    for member in scratch["members"]:
        built = _member_rows(rows, member["uuid"])
        mine = []

        def own(condition, message):
            if not condition:
                mine.append(message)
            return check(condition, f"{member['code']}: {message}")

        own([(path, sha256(content), len(content)) for path, content in built]
            == [(item["path"], item["sha256"], item["bytes"]) for item in member["files"]],
            "the set does not hold the files the manifest lists")
        decoded = []
        for path, content in built:
            if path.rsplit("/", 1)[-1] != BRUSH_ARCHIVE:
                continue
            era, fidelity, error = _decode(content)
            own(not error, f"{path} does not decode ({error})")
            own(fidelity == "byte", f"{path} decodes with fidelity {fidelity}, not byte")
            decoded.append(f"{path.split('/')[0] if '/' in path else 'main'} {era} {fidelity or 'ERROR'}")
        try:
            name = plain_text(plain_root(dict(built).get(BRUSH_ARCHIVE, b"")).get("name"))
        except Exception:                       # whatever a broken plist raises
            name = None
        own(name == member["name"], "the archive does not hold the member's name")
        single = _check_single(out, member, built, check)
        files = ", ".join(path.replace("QuickLook/", "") for path, _ in built if path.rsplit("/", 1)[-1] != BRUSH_ARCHIVE)
        lines.append(f"  {show(member['name']).rstrip()[:26]:<26} {'; '.join(decoded)[:34]:<34} "
                     f"{(files or '(archive only)')[:44]:<44} {'ok' if single else 'BAD':<7} "
                     f"{'ok' if not mine else 'FAILED'}")

    # Every file the manifest lists, by its sha256.
    lines.append("")
    hashed = manifest.get("file_sha256", {})
    for relative, digest in sorted(hashed.items()):
        try:
            if not _plain_relative(relative):
                raise OSError("not a plain relative name")
            same = sha256(out.joinpath(*relative.split("/")).read_bytes()) == digest
        except OSError:
            same = False
        check(same, f"{relative} is not the file the manifest describes")
    lines.append(f"files   {len(hashed)} listed in the manifest with their sha256, "
                 f"{sum(1 for p in problems if 'is not the file the manifest describes' in p)} differ")

    short = incomplete_2(manifest)
    check(manifest.get("complete") is (not short), "the manifest's `complete` flag does not match it")
    if short:
        lines += ["", f"INCOMPLETE   {short}."]
        if allow_substitutes:
            lines.append("             Allowed by --allow-substitutes. A sitting with it answers less.")
        else:
            check(False, f"sitting 2 is not complete: {short}. Pass --allow-substitutes to accept it")
    lines.append("")
    if problems:
        lines += [f"  problem: {problem}" for problem in problems]
        lines.append(f"NOT VERIFIED   {len(problems)} problem{'s' if len(problems) != 1 else ''}")
    else:
        lines.append(f"VERIFIED   {len(edits['members'])} edited brushes, each its donor with only the "
                     f"named keys and the name changed and every other file the donor's; "
                     f"{len(scratch['members'])} scratch brushes, every archive decoding byte for byte"
                     + ("" if not short else "; NOT complete (substitutes allowed)"))
    return not problems, lines


def incomplete_2(manifest):
    """Why sitting 2's build is not complete, in a few words, or ""."""
    parts = []
    substitutes = [donor["role"] for donor in manifest.get("donors", [])
                   if donor.get("source") and donor.get("as_specified") is not True]
    unfilled = [donor["role"] for donor in manifest.get("donors", []) if not donor.get("source")]
    if substitutes:
        parts.append(f"{', '.join(substitutes)} {'is a substitute' if len(substitutes) == 1 else 'are substitutes'}")
    if unfilled:
        parts.append(f"nothing was found for {', '.join(unfilled)}")
    left = manifest.get("left_out", [])
    if left:
        parts.append(f"{len(left)} member{'s are' if len(left) != 1 else ' is'} left out "
                     f"({', '.join(item['code'] for item in left)})")
    return "; ".join(parts)


# ── the verbs ────────────────────────────────────────────────────────────────

def render_plan(build, library, out):
    """The printout of a build: what was scanned, which brush fills each slot
    and where it came from, and what is written."""
    scan = build.scan
    lines = [f"Sitting 1: the control set \"{SET_NAME}\"", "",
             f"library   {library}"]
    for part in LIBRARY_PARTS:
        lines.append(f"          {part + '/':<10} {scan.files[part]:>4} files, "
                     f"{scan.brushes[part]:>4} brushes")
    if scan.skipped:
        lines.append(f"          passed over: {len(scan.skipped)}")
        lines += [f"            {where}: {why}" for where, why in scan.skipped]
    lines += ["", "members (every file is byte for byte the source's; the zip, the folder names "
                  "and brushset.plist are ours)"]
    for member in build.members:
        candidate = member.candidate
        label = "as specified" if member.pick.as_specified else "SUBSTITUTE  "
        lines.append(f"  {member.slot.number}  {label}  {show(candidate.name)!r}   {candidate.era_text}, "
                     f"{candidate.keys} keys")
        lines.append(f"       wanted  {member.slot.wanted}")
        lines.append(f"       to show {member.slot.shows}")
        if member.pick.note:
            lines.append(f"       NOTE    {member.pick.note}")
        lines.append(f"       source  {show(candidate.where)}"
                     + (f"   (set {show(candidate.set_name)!r}, place {candidate.position + 1})"
                        if candidate.set_name is not None else "   (a loose brush)"))
        size = member.thumbnail_size
        extras = [f"thumbnail {size[0]} x {size[1]}" if size else "no thumbnail"]
        if candidate.stored:
            extras.append(f"{candidate.stored} stored without compression in the source "
                          "(written here as deflate)")
        author = candidate.files_under(AUTHOR_FOLDER) + candidate.files_under(SIGNATURE_FOLDER)
        if author:
            extras.append("author files: " + ", ".join(f"{show(path)} {size:,} bytes"
                                                       for path, size in author))
        lines.append(f"       files   {len(member.files)}, {candidate.total:,} bytes: "
                     f"{', '.join(show(path) for path in candidate.paths)}   ({'; '.join(extras)})")
        lines.append(f"       single  {member.single}   {len(build.singles[member.single]):,} bytes")
    for slot in build.unfilled:
        lines.append(f"  {slot.number}  EMPTY         the library had no brush left for: {slot.wanted}")
    exact = sum(1 for member in build.members if member.pick.as_specified)
    lines += ["", f"  {exact} of {len(SLOTS)} members are as specified, "
                  f"{len(build.members) - exact} are substitutes, {len(build.unfilled)} slots are empty."]
    if scan.files["official"] == 0:
        lines.append("  WARNING   library/official/ holds no file. The members that come from the "
                     "official sets cannot be")
        lines.append("            chosen until `fetch_base_library.py fetch --confirm` has run; "
                     "build again after it.")
    if not build.complete:
        lines.append("  NOT THE CONTROL SET   a build with a substitute or an empty slot is written "
                     "only with --allow-substitutes.")
    lines += ["", f"known-bad {build.known_bad_note}", "", f"out       {out}"]
    for relative, data in build.files().items():
        lines.append(f"          {relative:<44} {len(data):>12,} bytes")
    lines.append(f"          {RETURNED_DIR + '/':<44} {'(empty)':>18}")
    return "\n".join(lines)


def refusal(build):
    """Why a build is refused without --allow-substitutes, or ""."""
    if build.complete:
        return ""
    parts = []
    if build.substitutes:
        parts.append(f"{len(build.substitutes)} of {len(build.members)} members are substitutes")
    if build.unfilled:
        parts.append(f"{len(build.unfilled)} slot{'s are' if len(build.unfilled) != 1 else ' is'} empty")
    return (f"this is not the control set: {' and '.join(parts)}. Nothing is written. Fetch the "
            f"official sets (`{FETCH_COMMAND}`) and build again, or pass --allow-substitutes to "
            "build it as it is; a sitting with such a build answers less.")


def run_build(paths, sitting, *, out=None, known_bad=None, confirm=False, allow_substitutes=False,
              now=None):
    target = resolve_out(paths, out, sitting)
    check_returned(target)                      # a dry run of a build that would be refused is refused too
    if sitting == SITTING_2:
        build = build_sitting_2(paths.library, now=now)
        print(render_plan_2(build, paths.library, target))
        refused = refusal_2(build)
        verify = verify_sitting_2
    else:
        build = build_sitting(paths.library, known_bad=known_bad)
        print(render_plan(build, paths.library, target))
        refused = refusal(build)
        verify = verify_sitting
    print()
    if refused and not allow_substitutes:       # dry run or not: the plan is shown, nothing is built
        raise DeviceTestError(refused)
    if not confirm:
        print(DRY_RUN_LINE)
        return bc.EXIT_OK
    try:
        written, removed = write_build(build, target)
    except OSError as exc:
        raise DeviceTestError(f"{target} cannot be written: {exc}") from None
    for relative in removed:
        print(f"removed   {relative}   (left by an earlier build)")
    print(f"WRITTEN   {len(written)} files in {target}")
    print()
    ok, lines = verify(paths.library, target, allow_substitutes=allow_substitutes)
    print("\n".join(lines))
    return bc.EXIT_OK if ok else bc.EXIT_REFUSED


def run_verify(paths, sitting, *, out=None, allow_substitutes=False):
    target = resolve_out(paths, out, sitting)
    verify = verify_sitting_2 if sitting == SITTING_2 else verify_sitting
    ok, lines = verify(paths.library, target, allow_substitutes=allow_substitutes)
    print("\n".join(lines))
    return bc.EXIT_OK if ok else bc.EXIT_REFUSED


# ── the command line ─────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="device_tests.py",
        description="Build the brush files for a sitting with the iPad, and check them. "
                    "`build` is a dry run without --confirm.")
    verbs = parser.add_subparsers(dest="verb", metavar="{build,verify}", required=True)
    build = verbs.add_parser("build", help="choose the members from the library and build the "
                                           "sitting's files (a dry run without --confirm)")
    verify = verbs.add_parser("verify", help="check a built sitting against the library")
    for sub in (build, verify):
        sub.add_argument("sitting", choices=SITTINGS, metavar="SITTING",
                         help="which sitting: " + ", ".join(SITTINGS))
        sub.add_argument("--out", metavar="DIR", default=None,
                         help=f"the sitting's folder (default: <root>/{OUT_HOME}/<sitting>)")
        sub.add_argument("--allow-substitutes", action="store_true",
                         help="accept a build that is not complete: one where a slot or a donor "
                              "holds a stand-in or is empty because the library lacks the kind of "
                              "brush it asks for. Without this such a build is refused (exit 1)")
        bc.add_path_arguments(sub, names=("root", "library"))
    build.add_argument("--known-bad", metavar="FILE", default=None,
                       help="sitting 1 only: the malformed brush file to copy into known-bad/ "
                            f"(default: {'/'.join(KNOWN_BAD_DEFAULT)} in the home folder, if it is there)")
    build.add_argument("--confirm", action="store_true", help="really write the files")
    return parser


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    paths = bc.paths_from_args(args)
    try:
        if args.verb == "verify":
            return run_verify(paths, args.sitting, out=args.out,
                              allow_substitutes=args.allow_substitutes)
        known_bad = args.known_bad
        if args.sitting == SITTING_2:
            if known_bad is not None:
                print("error: --known-bad belongs to sitting-1; sitting 2 has no known-bad file",
                      file=sys.stderr)
                return bc.EXIT_USAGE
        elif known_bad is None:
            known_bad = Path.home().joinpath(*KNOWN_BAD_DEFAULT)
        elif not known_bad.strip():
            known_bad = None                    # --known-bad "" asks for none
        return run_build(paths, args.sitting, out=args.out, known_bad=known_bad,
                         confirm=args.confirm, allow_substitutes=args.allow_substitutes)
    except DeviceTestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except BrushModelError as exc:
        # The key schema is a code asset beside this script (F2): without it no era is known.
        print(f"error: {_why(exc)}", file=sys.stderr)
        return bc.EXIT_USAGE if exc.code in ("no_schema", "bad_schema") else bc.EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
