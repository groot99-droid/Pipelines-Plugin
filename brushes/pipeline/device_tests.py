"""Build the brush files for a sitting with the iPad, and check them afterwards.

    python brushes/pipeline/device_tests.py build sitting-1 [--out DIR] [--known-bad FILE] [--allow-substitutes] [--confirm]
    python brushes/pipeline/device_tests.py verify sitting-1 [--out DIR] [--allow-substitutes]

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

Of these git keeps manifest.json, CHECKLIST.md and whatever is put in returned/
(the record of a sitting, which no build can make again). The set, the loose
copies and the known-bad copy are scratch and are ignored.

Which eight. Each is a kind of brush, not a fixed file: SLOTS below lists them.
The library is scanned in memory and, for each slot, the brush that fits is
taken; among several that fit, the one a fixed rule ranks first, so two runs
choose alike. An era is told here by the number of root keys in Brush.archive,
a stand-in until the file codec exists.

When the library holds no brush of the kind a slot asks for, the result is not
the control set, and `build` REFUSES: it prints the plan, exits 1 and writes
nothing. That is the case until the official sets are in library/official/
(`fetch_base_library.py fetch --confirm`): five of the eight kinds exist only
there. --allow-substitutes builds anyway, with the nearest kind (or, failing
that, any other brush) standing in; the printout, the checklist and the
manifest then say SUBSTITUTE, what each stand-in is and what it no longer
shows. Such a build answers less, and a sitting spent on it is a sitting gone.

`build` is a dry run unless --confirm is given: it scans, chooses, builds
everything in memory, reads the set back, prints the plan, and writes nothing.
With --confirm it writes the files and then checks them as `verify` does. It
refuses to build over a folder whose returned/ holds files: those belong to
the manifest that is there.

`verify` is a second pass that does its own reading, with zipfile alone: it
goes through neither the builder's reader nor zip_writer. It opens the built
set, reads every member again from the library file the manifest names,
compares each file by sha256, parses the plist, lists the header fields of
every zip entry, and checks the folder names. Exit 1 when anything differs,
and also when the manifest lists a substitute or an empty slot, unless
--allow-substitutes is given.

Brush files are data from strangers. Each is opened with zipfile where it lies
and read, entry by entry, into memory, under the size caps of docs/CONTRACTS.md
(F3). No entry is ever extracted to disk and no entry name is used as a path.
Run this as `python -I brushes/pipeline/device_tests.py ...`.

Exit codes: 0 ok, 1 refused or failed, 2 usage or environment.
Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import io
import json
import os
import plistlib
import re
import struct
import sys
import unicodedata
import uuid
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import zip_writer  # noqa: E402

SITTING_1 = "sitting-1"
SITTINGS = (SITTING_1,)
OUT_HOME = "device-tests"                   # under the brushes/ root

SET_FILE = "ROSW-1-control.brushset"
SET_NAME = "ROSW 1 Control"
SINGLES_DIR = "singles"
KNOWN_BAD_DIR = "known-bad"
RETURNED_DIR = "returned"
CHECKLIST_NAME = "CHECKLIST.md"
MANIFEST_NAME = "manifest.json"
MANIFEST_SCHEMA = "rosw-brushes-device-test/1"
KNOWN_BAD_DEFAULT = ("Downloads", "Untitled_Brush.brush")      # under the home folder
# The name the known-bad copy gets here. The app names a brush from its archive,
# not from its file, so the name is ours to choose; and the brush that comes
# back in the return leg is called "Untitled Brush", one character away from
# the file the old designer wrote.
KNOWN_BAD_STEM = "KNOWN-BAD_old-designer"
KNOWN_BAD_SUFFIXES = (".brush", ".brushset")
FETCH_COMMAND = "python brushes/pipeline/fetch_base_library.py fetch --confirm"

LIBRARY_PARTS = ("user", "official")
BRUSH_SUFFIXES = (".brush", ".brushset")
SET_PLIST = "brushset.plist"
BRUSH_ARCHIVE = "Brush.archive"
SHAPE = "Shape.png"
GRAIN = "Grain.png"
THUMBNAIL = "QuickLook/Thumbnail.png"
SUB_ARCHIVE = "Sub01/Brush.archive"
RESET_ARCHIVE = "Reset/Brush.archive"
RESET_SUB_ARCHIVE = "Reset/Sub01/Brush.archive"
AUTHOR_FOLDER = "AuthorPicture/"
SIGNATURE_FOLDER = "Signature/"
EMPTY = ".empty"

MIB = 1024 * 1024
# The reader's caps (docs/CONTRACTS.md F3; spec.yaml format.caps), by the same names.
CAPS = {
    "zip_entries": 5000,                 # entries in one container
    "archive_bytes": MIB,                # one Brush.archive, one brushset.plist
    "entry_bytes": 64 * MIB,             # one inflated entry
    "total_bytes": 2048 * MIB,           # one container, inflated
    "ratio": 200,                        # an entry inflating more than 200:1 ...
    "ratio_min_bytes": 16 * MIB,         # ... and larger than this is refused
    "upload_bytes": 512 * MIB,           # one container file
}

ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
LFS_POINTER_MAX = 1024
# Folders of the library on disk that hold no brush file to scan.
SKIPPED_LIBRARY_FOLDERS = frozenset({"__macosx", "_docs"})
# Junk inside a zip: part of no brush folder (docs/CONTRACTS.md, F3 "Reading";
# ingest.py spells the same two sets). Every other entry of a brush folder is a
# member and is carried, a zero-byte `.empty` and an unknown file among them.
JUNK_FOLDERS = frozenset({"__macosx"})
JUNK_NAMES = frozenset({".ds_store", "thumbs.db", "desktop.ini"})
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# An era by its count of root keys, `$class` included (spec.yaml format.era_keys;
# an M220 archive may carry one to three optional curve keys).
ERA_BY_KEYS = {52: "E0", 61: "E1", 62: "E1b", 63: "E1c", 67: "E2", 88: "E3", 101: "E4",
               172: "M172", 173: "M173", 220: "M220", 221: "M220", 222: "M220", 223: "M220",
               242: "M242"}
LEGACY_MAX_KEYS = 101
STEADY_KEYS = ("plotJitter", "shapeScatter", "shapeRandomise")
STEADY_PREFIX = "dynamicsJitter"

# The form of a folder name in a set: an upper-case version-4 UUID.
UUID_FORM = re.compile(r"[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}")

# What every entry of a zip made here must carry, by zipfile's names for the
# fields (zip_writer.py says why). Written out here, not taken from the writer:
# the second pass checks the writer against them.
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

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."

# What zipfile and zlib raise on a file that is not what it claims to be.
ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, zlib.error, EOFError, OSError,
              RuntimeError, NotImplementedError, ValueError, OverflowError, MemoryError)


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
    return str(uuid.uuid4()).upper()


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


def hostile(name):
    """Why an entry name is refused, or an empty string. The test is made on the
    name as stored (`orig_filename`): on Windows zipfile rewrites a backslash."""
    if not name or "\x00" in name:
        return "an empty or NUL-holding entry name"
    if "\\" in name:
        return "an entry name with a backslash"
    if name.startswith("/") or re.match(r"[A-Za-z]:", name):
        return "an absolute entry name"
    if ".." in name.split("/"):
        return "an entry name with `..`"
    return ""


def _ratio_bomb(info):
    return (info.file_size > CAPS["ratio_min_bytes"]
            and info.file_size > info.compress_size * CAPS["ratio"])


@contextlib.contextmanager
def open_zip(source):
    """`with open_zip(f) as (archive, entries):` for a seekable binary file (an
    open file, or io.BytesIO over bytes). The zip's own directory is checked
    against the caps before anything is inflated. Unreadable otherwise."""
    try:
        archive = zipfile.ZipFile(source)
    except ZIP_ERRORS as exc:
        raise Unreadable(f"it cannot be opened as a zip ({type(exc).__name__})") from None
    with archive:
        infos = archive.infolist()
        if len(infos) > CAPS["zip_entries"]:
            raise Unreadable(f"{len(infos):,} entries; the cap is {CAPS['zip_entries']:,}")
        total = 0
        for info in infos:
            problem = hostile(info.orig_filename)
            if problem:
                raise Unreadable(problem)
            if info.flag_bits & 0x1:
                raise Unreadable("an encrypted entry")
            if info.file_size > CAPS["entry_bytes"]:
                raise Unreadable(f"an entry of {info.file_size:,} bytes; "
                                 f"the cap is {CAPS['entry_bytes']:,}")
            if _ratio_bomb(info):
                raise Unreadable(f"an entry that inflates more than {CAPS['ratio']}:1")
            total += info.file_size
        if total > CAPS["total_bytes"]:
            raise Unreadable(f"{total:,} bytes inflated; the cap is {CAPS['total_bytes']:,}")
        yield archive, infos


@contextlib.contextmanager
def open_library_file(path, stored):
    """`with open_library_file(path, stored) as (archive, entries):` for one
    brush file of the library. Nothing is extracted: zipfile reads the
    directory, and each entry asked for is inflated into memory."""
    check_file(path, stored)
    with open(path, "rb") as handle, open_zip(handle) as opened:
        yield opened


def read_entry(archive, info, cap):
    """One entry's bytes, in memory, or Unreadable. Never more than `cap` bytes."""
    if info.file_size > cap:
        raise Unreadable(f"{show(info.orig_filename)} is {info.file_size:,} bytes inflated; "
                         f"the cap is {cap:,}")
    try:
        with archive.open(info) as handle:
            data = handle.read(cap + 1)
    except ZIP_ERRORS as exc:
        raise Unreadable(f"{show(info.orig_filename)} cannot be read "
                         f"({type(exc).__name__})") from None
    if len(data) > cap:
        raise Unreadable(f"{show(info.orig_filename)} inflates to more than {cap:,} bytes")
    return data


def _junk(name):
    parts = name.lower().split("/")
    return parts[-1] in JUNK_NAMES or any(part in JUNK_FOLDERS for part in parts[:-1])


def folder_members(infos, prefix):
    """The files of one brush folder, in the order the zip stores them:
    ([(path inside the folder, entry)], how many entries were left out).

    The rule of docs/CONTRACTS.md, F3 "Reading". Left out: an entry that is a
    folder, junk (anything under `__MACOSX/`, a `.DS_Store`, `Thumbs.db` or
    `desktop.ini`), and the second and later entries of a repeated name (the
    first wins). Everything else is a member and is kept in source order: a
    zero-byte `.empty` and a file nobody knows among them.
    """
    kept, seen, left_out = [], set(), 0
    for info in infos:
        name = info.orig_filename
        if not name.startswith(prefix) or name == prefix:
            continue
        inside = name[len(prefix):]
        if name.endswith("/") or _junk(inside) or inside in seen:
            left_out += 1
            continue
        seen.add(inside)
        kept.append((inside, info))
    return kept, left_out


def layout(archive, infos):
    """(set name or None, [(folder name, prefix of its entries)]) for an open
    container: a set's folders in the order its plist lists them, or the one
    folder of a loose brush, whose prefix is empty."""
    by_name = {}
    for info in infos:
        name = info.orig_filename
        if not name.endswith("/") and not _junk(name):
            by_name.setdefault(name, info)
    top = ""
    if SET_PLIST not in by_name:
        if BRUSH_ARCHIVE in by_name:
            return None, [("", "")]
        tops = {name.split("/", 1)[0] for name in by_name}
        if len(tops) != 1 or not all("/" in name for name in by_name):
            raise Unreadable(f"it holds no {SET_PLIST} and no {BRUSH_ARCHIVE}")
        top = next(iter(tops)) + "/"            # a set zipped from a file manager
        if top + SET_PLIST not in by_name:
            raise Unreadable(f"it holds no {SET_PLIST} and no {BRUSH_ARCHIVE}")
    raw = read_entry(archive, by_name[top + SET_PLIST], CAPS["archive_bytes"])
    try:
        plist = plistlib.loads(raw)
    except Exception:                           # anything a stranger's plist can raise
        raise Unreadable(f"its {SET_PLIST} cannot be read") from None
    folders = plist.get("brushes") if isinstance(plist, dict) else None
    name = plist.get("name") if isinstance(plist, dict) else None
    if (not isinstance(folders, list) or not isinstance(name, str)
            or not all(isinstance(folder, str) for folder in folders)):
        raise Unreadable(f"its {SET_PLIST} is not the dictionary a set has")
    listed = []
    for folder in folders:
        if folder and "/" not in folder and folder not in (".", "..") and folder not in listed:
            listed.append(folder)
    return name, [(folder, f"{top}{folder}/") for folder in listed]


def archive_facts(data):
    """What choosing needs from one Brush.archive: {"keys", "root", "name",
    "strings"}. Read with plistlib, which is enough to count keys and read plain
    values; it is not the codec. Unreadable says, in plain words, what is wrong.
    """
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
    return {"keys": len(root), "root": root, "name": text("name") or "", "strings": strings}


def _zero(value):
    return isinstance(value, (bool, int, float)) and value == 0


class Candidate:
    """One brush folder found in the library, as plain facts. No image bytes."""

    def __init__(self, container, set_name, position, folder, prefix, members, archive, facts):
        root = facts["root"]
        self.container = container              # library-relative POSIX path of the file
        self.library = container.split("/")[0]  # "user" | "official"
        self.pack = container.split("/")[1] if container.count("/") >= 2 else ""
        self.stem = container.rsplit("/", 1)[-1].rsplit(".", 1)[0]
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
        self.era = ERA_BY_KEYS.get(self.keys, f"X{self.keys}")
        self.family = "legacy" if self.keys <= LEGACY_MAX_KEYS else "modern"
        self.name = facts["name"]
        self.version = root.get("version") if isinstance(root.get("version"), int) else None
        self.bundled_shape = facts["strings"]["bundledShapePath"]
        self.bundled_grain = facts["strings"]["bundledGrainPath"]
        self.author_name = facts["strings"]["authorName"]
        self.stamp = root.get("stamp") is True
        jitters = [value for key, value in root.items()
                   if key in STEADY_KEYS or key.startswith(STEADY_PREFIX)]
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


def _candidate(archive, infos, stored, set_name, position, folder, prefix):
    members, _ = folder_members(infos, prefix)
    by_path = dict(members)
    if BRUSH_ARCHIVE not in by_path:
        raise Unreadable(f"it holds no {BRUSH_ARCHIVE}")
    for path in by_path:
        try:
            zip_writer.check_name(path)
        except zip_writer.ZipWriteError:
            raise Unreadable(f"it holds an entry name this tool does not write: {show(path)!r}") from None
    data = read_entry(archive, by_path[BRUSH_ARCHIVE], CAPS["archive_bytes"])
    return Candidate(stored, set_name, position, folder, prefix, members, data, archive_facts(data))


def scan_library(library):
    """Every brush folder in the library, as a Scan. Of each file only the
    directory, the set's plist and the Brush.archive entries are read."""
    scan = Scan()
    for stored, path in library_files(library):
        part = stored.split("/", 1)[0]
        scan.files[part] += 1
        try:
            with open_library_file(path, stored) as (archive, infos):
                set_name, folders = layout(archive, infos)
                for position, (folder, prefix) in enumerate(folders):
                    try:
                        scan.candidates.append(
                            _candidate(archive, infos, stored, set_name, position, folder, prefix))
                        scan.brushes[part] += 1
                    except Unreadable as exc:
                        where = stored + (f"!/{folder}" if folder else "")
                        scan.skipped.append((show(where), str(exc)))
        except Unreadable as exc:
            scan.skipped.append((show(stored), str(exc)))
    return scan


def load_member(library, candidate):
    """[(path inside the folder, bytes)] of one chosen brush, read again from
    its library file, in the order that file stores them."""
    path = Path(library).joinpath(*candidate.container.split("/"))
    try:
        with open_library_file(path, candidate.container) as (archive, infos):
            members, _ = folder_members(infos, candidate.prefix)
            files = [(inside, read_entry(archive, info, CAPS["entry_bytes"]))
                     for inside, info in members]
    except Unreadable as exc:
        raise DeviceTestError(f"{show(candidate.where)} cannot be read again: {exc}") from None
    if (tuple(inside for inside, _ in files) != candidate.paths
            or sha256(dict(files).get(BRUSH_ARCHIVE, b"")) != candidate.archive_sha256):
        raise DeviceTestError(f"{show(candidate.where)} changed while it was being read")
    return files


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
    """One member of the control set.

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
         'an E0 brush (52 keys), such as "Broken Cont\u00e9" from the Insecto charcoal pack',
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
        with open_zip(io.BytesIO(data)) as (archive, infos):
            info = next((i for i in infos
                         if i.orig_filename.rsplit("/", 1)[-1] == BRUSH_ARCHIVE), None)
            if info is None:
                return True, f"it holds no {BRUSH_ARCHIVE}"
            facts = archive_facts(read_entry(archive, info, CAPS["archive_bytes"]))
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
    stamp = tuple(date_time) if date_time else datetime.datetime.now().timetuple()[:6]
    make = new_uuid or fresh_uuid
    names = {pick.candidate.folder for pick in picks}
    for pick in picks:
        for _ in range(64):
            folder = make()
            if isinstance(folder, str) and UUID_FORM.fullmatch(folder) and folder not in names:
                break
        else:
            raise DeviceTestError("no fresh upper-case version-4 UUID could be made for a folder name")
        names.add(folder)
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
            ">     python brushes/pipeline/device_tests.py build sitting-1 --confirm",
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
        "This folder was made by `python brushes/pipeline/device_tests.py build sitting-1 --confirm`.",
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
        "## Step 1. Get the files onto the iPad",
        "",
        "Any route works, as long as the files arrive unchanged:",
        "",
        "- **iCloud Drive.** On this computer, sign in at icloud.com, open iCloud Drive, and upload",
        f"  `{SET_FILE}`" + (f", the file in `{KNOWN_BAD_DIR}/`" if known else "")
        + f" and the files in `{SINGLES_DIR}/`.",
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
        "**b. One brand-new, untouched brush.** In the Brush Library, tap the **+** at the top",
        "right. Brush Studio opens with a new brush. Change nothing, and tap Done. The new brush",
        "is now in the list (it is usually called \"Untitled Brush\"). Swipe left on it, tap Share,",
        "and save it to Files. It is saved as a `.brush` file. This is what Procreate itself",
        "writes today, and it becomes the starting point for brushes this tool makes.",
        "",
        "Keep the file names Procreate gives them.",
        "",
    ]
    step += 1
    lines += [
        f"## Step {step}. Put the returned files here",
        "",
        "Back on this computer, put both files in:",
        "",
        f"    brushes/{OUT_HOME}/{SITTING_1}/{RETURNED_DIR}/",
        "",
        f"(that is the `{RETURNED_DIR}` folder beside this file). Add your notes there too: a",
        "`notes.txt` with the versions and your answers, or photos of this page filled in.",
        "",
    ]
    if known:
        lines += [
            f"Do not put the known-bad file (`{known_name}`) in `{RETURNED_DIR}/`, nor any brush that",
            "came out of it: that folder is for the two files of the return leg and your notes.",
            "",
        ]
    lines += [
        f"What is in `{RETURNED_DIR}/` is kept in git, together with `{MANIFEST_NAME}` and this page: it",
        "is the only record of what the iPad did, and no build can make it again.",
        "",
        "Do not build this sitting again once files are in that folder: a new build gives the",
        "brushes new folder names, and the returned files are compared with this one.",
        "",
        "Afterwards you can delete the set and the new brush from Procreate (swipe left, Delete).",
        "",
    ]
    return "\n".join(lines)


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


def _source_rows(library, source):
    """[(path inside the folder, sha256, size)] of a member as the library file
    holds it now, read here without the builder's reader."""
    container = source["container"]
    if not _plain_relative(container) or container.split("/")[0] not in LIBRARY_PARTS:
        raise DeviceTestError(f"the manifest names a source outside the library: {show(container)}")
    path = Path(library).joinpath(*container.split("/"))
    if not path.is_file() or path.stat().st_size > CAPS["upload_bytes"]:
        raise DeviceTestError(f"the source {show(container)} is not in the library")
    prefix = source["prefix"]
    rows, seen = [], set()
    with open(path, "rb") as handle, zipfile.ZipFile(handle) as archive:
        for info in archive.infolist():
            name = info.orig_filename
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            inside = name[len(prefix):]
            if inside in seen or _junk(inside) or info.file_size > CAPS["entry_bytes"]:
                continue
            seen.add(inside)
            content = archive.read(info)
            rows.append((inside, sha256(content), len(content)))
    return rows


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


def verify_sitting(library, out, *, allow_substitutes=False):
    """(ok, lines): the built files of sitting 1 checked against the library.

    A build with a substitute or an empty slot is not the control set: it is
    reported, and fails the check unless `allow_substitutes` is true.
    Raises EnvironmentProblem when there is nothing built in `out`.
    """
    out = Path(out)
    try:
        manifest = json.loads(bc.read_text(out / MANIFEST_NAME))
        set_data = (out / SET_FILE).read_bytes()
    except (OSError, UnicodeDecodeError, ValueError):
        raise EnvironmentProblem(f"there is no built sitting in {out} (no readable {MANIFEST_NAME} "
                                 f"and {SET_FILE})") from None
    if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA:
        raise EnvironmentProblem(f"{out / MANIFEST_NAME} is not a {MANIFEST_SCHEMA} manifest")
    try:
        return _verify(Path(library), out, manifest, set_data, allow_substitutes)
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
        date = "%04d-%02d-%02d %02d:%02d:%02d" % info.date_time
        lines.append(f"  {info.compress_type:>6} 0x{info.flag_bits:04x}  {info.create_system:>7},"
                     f"{info.create_version:<7} {info.extract_version:>5} {info.external_attr:>8} "
                     f"{info.internal_attr:>8} {len(info.extra):>5} {len(info.comment):>7}  {date}  {show(name)}")
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
        lines.append(f"  {member.slot.number}  {label}  {show(candidate.name)!r}   {candidate.era}, "
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


def run_build(paths, sitting, *, out=None, known_bad=None, confirm=False, allow_substitutes=False):
    target = resolve_out(paths, out, sitting)
    check_returned(target)                      # a dry run of a build that would be refused is refused too
    build = build_sitting(paths.library, known_bad=known_bad)
    print(render_plan(build, paths.library, target))
    print()
    refused = refusal(build)
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
    ok, lines = verify_sitting(paths.library, target, allow_substitutes=allow_substitutes)
    print("\n".join(lines))
    return bc.EXIT_OK if ok else bc.EXIT_REFUSED


def run_verify(paths, sitting, *, out=None, allow_substitutes=False):
    target = resolve_out(paths, out, sitting)
    ok, lines = verify_sitting(paths.library, target, allow_substitutes=allow_substitutes)
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
                         help="accept a build that is not the control set: one where a slot holds "
                              "a stand-in or is empty because the library lacks the kind of brush "
                              "it asks for. Without this such a build is refused (exit 1)")
        bc.add_path_arguments(sub, names=("root", "library"))
    build.add_argument("--known-bad", metavar="FILE", default=None,
                       help="the malformed brush file to copy into known-bad/ (default: "
                            f"{'/'.join(KNOWN_BAD_DEFAULT)} in the home folder, if it is there)")
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
        if known_bad is None:
            known_bad = Path.home().joinpath(*KNOWN_BAD_DEFAULT)
        elif not known_bad.strip():
            known_bad = None                    # --known-bad "" asks for none
        return run_build(paths, args.sitting, out=args.out, known_bad=known_bad,
                         confirm=args.confirm, allow_substitutes=args.allow_substitutes)
    except DeviceTestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
