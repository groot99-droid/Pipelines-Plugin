"""Bring brush files into the library.

    python brushes/pipeline/ingest.py where
    python brushes/pipeline/ingest.py adopt <src> [--with-docs] [--confirm]

`where` prints the folders every brushes script works on, and whether each
exists. `adopt` copies the brush files found in a folder (or in one file) into
library/user/<pack_id>/, one copy of each (docs/CONTRACTS.md, F11 and F12). The
catalog verbs (`build`, `report`, `census`) are not part of this module yet.

How `adopt` decides what a file is:

  - By content, never by extension. A zip with `brushset.plist` at its root (or
    inside its one top folder) is a set; a zip with `Brush.archive` at its root
    is a brush. Any other zip is searched for entries named `*.brush`,
    `*.brushset` or `*.zip`, through at most three zips nested in each other.
  - Nothing is ever extracted to disk and no entry name is ever used as a path:
    a nested file is read into memory and hashed there. A stored file name is
    made from the original's last path part by the name rule below.
  - One container is one sha256. A second sighting, on disk or inside a zip, is
    recorded as another place the same file was found, and is not copied.
  - The pack is the one whose `match` patterns in library/sources.json fit the
    path of the file on disk (for a nested file, the zip it was found in). A
    path under `user/<pack_id>/` is that pack. No fit is the pack `unsorted`,
    with a warning. A path that fits two packs is an error in the manifest and
    stops the run.
  - The name rule: fold accents, replace every character outside
    `A-Z a-z 0-9 . _ -` with `_`, and end the name `.brushset` for a set and
    `.brush` for a brush (so `Name.brushset.zip` is stored as `Name.brushset`:
    the repository ignores `*.zip`).
  - Documents, images and `.procreate` artwork are never adopted. With
    --with-docs the ones on disk are copied to `user/<pack_id>/_docs/`, which
    git ignores.

Without --confirm the plan is printed and nothing is written. With it, each
file is copied through `<name>.part`, hashed again, and moved into place. A
file already in the library is left alone; a different file under the same
name stops the run before anything is written.

Brush files are data from strangers. The size caps of docs/CONTRACTS.md (F3)
apply to everything read here, and CAPS below repeats them until the file
codec owns them. Run this as `python -I brushes/pipeline/ingest.py ...`.

Exit codes: 0 ok, 1 refused or failed, 2 usage or environment.
Standard library only.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import os
import plistlib
import re
import shutil
import sys
import unicodedata
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import identity  # noqa: E402

SOURCES_NAME = "sources.json"
SOURCES_SCHEMA = "rosw-brushes-sources/1"
USER_DIR = "user"
DOCS_DIR = "_docs"
UNSORTED = "unsorted"
PART_SUFFIX = ".part"
SET_SUFFIX = ".brushset"
BRUSH_SUFFIX = ".brush"
SET_PLIST = "brushset.plist"
BRUSH_ARCHIVE = "Brush.archive"

MIB = 1024 * 1024
# The reader's caps (docs/CONTRACTS.md F3; spec.yaml format.caps), by the same names.
CAPS = {
    "zip_entries": 5000,                 # entries in one container
    "archive_bytes": MIB,                # one Brush.archive
    "entry_bytes": 64 * MIB,             # one inflated entry
    "total_bytes": 2048 * MIB,           # one container, inflated
    "ratio": 200,                        # an entry inflating more than 200:1 ...
    "ratio_min_bytes": 16 * MIB,         # ... and larger than this is refused
    "nesting_depth": 3,
    "upload_bytes": 512 * MIB,           # one container file, on disk or nested
}

NESTED_SUFFIXES = (".brush", ".brushset", ".zip")          # `.brushset.zip` ends in `.zip`
STRIPPED_SUFFIXES = (".brushset.zip", ".brush.zip", ".brushset", ".brush", ".zip")
ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
LFS_POINTER_MAX = 1024
# Junk: part of no brush folder, in a zip or on disk (docs/CONTRACTS.md, F3
# "Reading"). device_tests.py spells the same two sets.
JUNK_FOLDERS = frozenset({"__macosx"})
JUNK_NAMES = frozenset({".ds_store", "thumbs.db", "desktop.ini"})
# A zero-byte placeholder some official sets carry. Inside a zip it is a member
# of the brush folder it sits in, and is listed like any other entry: only the
# file codec decides what a member is, and it keeps this one. It never decides
# what a container is (`sniff`), and a loose one on disk is not a brush file or
# a document.
EMPTY = ".empty"
ARTWORK_SUFFIXES = (".procreate",)
DOCUMENT_KINDS = (
    ("artwork", ARTWORK_SUFFIXES + (".psd", ".swatches")),
    ("document", (".pdf", ".txt", ".rtf", ".md", ".doc", ".docx", ".htm", ".html", ".url", ".webloc")),
    ("image", (".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".heic", ".bmp", ".svg")),
)
NAME_MAX = 120
CHUNK = MIB
SPACE_MARGIN = 64 * MIB
# GitHub refuses a plain blob over 100 MB; the repository's own limit is 95.
PLAIN_BLOB_LIMIT = 95 * 1000 * 1000

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."

# What zipfile and zlib raise on a file that is not what it claims to be.
ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, zlib.error, EOFError, OSError,
              RuntimeError, NotImplementedError, ValueError, OverflowError, MemoryError)


class IngestError(Exception):
    """The command cannot go on. Exit 1."""

    exit_code = bc.EXIT_REFUSED


class EnvironmentProblem(IngestError):
    """A missing folder or manifest, or a Git LFS pointer where a file should be. Exit 2."""

    exit_code = bc.EXIT_USAGE


class Skip(Exception):
    """One file or entry that is not read: over a cap, hostile, or not a zip."""


# ── the manifest ─────────────────────────────────────────────────────────────

def load_sources(library):
    """<library>/sources.json, checked for the parts adoption reads. Reads only."""
    path = Path(library) / SOURCES_NAME
    try:
        sources = json.loads(bc.read_text(path))
    except FileNotFoundError:
        raise EnvironmentProblem(f"there is no manifest at {path} (point --library at the folder "
                                 "that holds sources.json)") from None
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise EnvironmentProblem(f"{path} cannot be read as JSON: {exc}") from None
    if not isinstance(sources, dict) or sources.get("schema") != SOURCES_SCHEMA:
        raise EnvironmentProblem(f"{path} is not a {SOURCES_SCHEMA} manifest")
    packs = sources.get("packs")
    if not isinstance(packs, list):
        raise EnvironmentProblem(f"{path}: `packs` must be a list")
    seen = set()
    for pack in packs:
        ident = pack.get("id") if isinstance(pack, dict) else None
        if not identity.is_pack_id(ident) or ident in seen or ident == UNSORTED:
            raise EnvironmentProblem(
                f"{path}: every pack needs its own lower-case id of at most "
                f"{identity.PACK_ID_MAX} characters (so that `<id>{identity.LOOSE_SUFFIX}` is a "
                f"set slug), not {ident!r}")
        seen.add(ident)
        match = pack.get("match", [])
        if not isinstance(match, list) or not all(isinstance(p, str) and p for p in match):
            raise EnvironmentProblem(f"{path}: `match` of pack {ident} must be a list of patterns")
        if not isinstance(pack.get("sets", {}), dict):
            raise EnvironmentProblem(f"{path}: `sets` of pack {ident} must be an object")
    return sources


def packs_for(rel, sources):
    """The ids of the packs a path belongs to: none, one, or (a manifest error) several.

    `rel` is a POSIX path relative to the folder being scanned. A path already
    laid out as `user/<pack_id>/...` is that pack. Otherwise each pack's
    `match` patterns are tried with fnmatch, ignoring case; `*` crosses `/`.
    """
    parts = rel.split("/")
    ids = [pack["id"] for pack in sources["packs"]]
    if len(parts) >= 3 and parts[0] == USER_DIR and parts[1] in ids:
        return [parts[1]]
    low = rel.lower()
    return [pack["id"] for pack in sources["packs"]
            if any(fnmatch.fnmatchcase(low, pattern.lower()) for pattern in pack.get("match", ()))]


# ── names ────────────────────────────────────────────────────────────────────

def show(text):
    """Text that is safe to print: control characters become `?`."""
    return "".join(ch if ch.isprintable() else "?" for ch in str(text))


def safe_name(text):
    """Accents folded, and every character outside `A-Z a-z 0-9 . _ -` made `_`."""
    folded = "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))
    return re.sub(r"[^A-Za-z0-9._-]", "_", folded)


def _guard(stem):
    """A stem that is a legal file name everywhere: not empty, not hidden, not a
    Windows device, not too long."""
    stem = stem.strip(".")[:NAME_MAX].strip(".") or "untitled"
    if stem.split(".")[0].lower() in identity.WINDOWS_DEVICES:
        stem = "x-" + stem
    return stem


def adopted_name(original, kind):
    """The file name a container is stored under. `kind` is "set" or "brush"."""
    base = original.replace("\\", "/").rsplit("/", 1)[-1]
    low = base.lower()
    for suffix in STRIPPED_SUFFIXES:
        if low.endswith(suffix):
            base = base[:len(base) - len(suffix)]
            break
    return _guard(safe_name(base)) + (SET_SUFFIX if kind == "set" else BRUSH_SUFFIX)


def document_name(original):
    """The file name a document is stored under in `_docs/`."""
    base = safe_name(original.replace("\\", "/").rsplit("/", 1)[-1])
    stem, dot, extension = base.rpartition(".")
    if not dot or not stem or len(extension) > 12:
        return _guard(base)
    return _guard(stem) + "." + extension


def with_hash(name, sha256):
    """`name` made unique by eight characters of the content hash before its extension."""
    stem, dot, extension = name.rpartition(".")
    return f"{stem}_{sha256[:8]}.{extension}" if dot and stem else f"{name}_{sha256[:8]}"


def document_kind(name):
    low = name.lower()
    for kind, suffixes in DOCUMENT_KINDS:
        if low.endswith(suffixes):
            return kind
    return "other"


# ── reading zips ─────────────────────────────────────────────────────────────

def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def shown_name(info):
    """An entry's name for people. A zip made on a Mac may hold UTF-8 names
    without saying so; zipfile then reads them as code page 437."""
    name = info.orig_filename
    if not info.flag_bits & 0x800:
        try:
            return name.encode("cp437").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return name


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


def list_entries(archive):
    """The entries of an open zip that count: files only, the first of a
    repeated name, and no junk (nothing from `__MACOSX/`, no `.DS_Store`,
    `Thumbs.db` or `desktop.ini`). A `.empty` placeholder is an entry like any
    other: inside a brush folder it is a member (docs/CONTRACTS.md, F3)."""
    infos = archive.infolist()
    if len(infos) > CAPS["zip_entries"]:
        raise Skip(f"{len(infos):,} entries; the cap is {CAPS['zip_entries']:,}")
    kept, seen = [], set()
    for info in infos:
        name = info.orig_filename
        if name.endswith("/") or name in seen:
            continue
        parts = name.lower().split("/")
        if parts[-1] in JUNK_NAMES or any(part in JUNK_FOLDERS for part in parts[:-1]):
            continue
        seen.add(name)
        kept.append(info)
    return kept


def sniff(names):
    """("set" | "brush" | "other", prefix) from a zip's entry names alone. A
    `.empty` placeholder never decides: it is left out of the one-top-folder test."""
    if SET_PLIST in names:
        return "set", ""
    if BRUSH_ARCHIVE in names:
        return "brush", ""
    real = [name for name in names if name.rsplit("/", 1)[-1].lower() != EMPTY]
    tops = {name.split("/", 1)[0] for name in real}
    if len(tops) == 1 and all("/" in name for name in real):
        prefix = next(iter(tops)) + "/"
        if prefix + SET_PLIST in names:
            return "set", prefix
    return "other", ""


def _ratio_bomb(info):
    return (info.file_size > CAPS["ratio_min_bytes"]
            and info.file_size > info.compress_size * CAPS["ratio"])


def check_declared(infos):
    """Refuse a container whose own directory already breaks the reader's caps."""
    total = 0
    for info in infos:
        size = info.file_size
        if info.orig_filename.rsplit("/", 1)[-1] == BRUSH_ARCHIVE and size > CAPS["archive_bytes"]:
            raise Skip(f"a Brush.archive of {size:,} bytes; the cap is {CAPS['archive_bytes']:,}")
        if size > CAPS["entry_bytes"]:
            raise Skip(f"an entry of {size:,} bytes; the cap is {CAPS['entry_bytes']:,}")
        if _ratio_bomb(info):
            raise Skip(f"an entry that inflates more than {CAPS['ratio']}:1")
        total += size
    if total > CAPS["total_bytes"]:
        raise Skip(f"{total:,} bytes inflated; the cap is {CAPS['total_bytes']:,}")


def _too_deep():
    return f"nested more than {CAPS['nesting_depth']} zips deep; not opened"


class Budget:
    """How many bytes may still be inflated out of one file on disk."""

    def __init__(self, limit=None):
        self.left = CAPS["total_bytes"] if limit is None else limit

    def spend(self, size):
        if size > self.left:
            raise Skip(f"more than {CAPS['total_bytes']:,} bytes would be inflated from one file")
        self.left -= size


def read_entry(archive, info, cap, budget=None):
    """One entry's bytes, in memory, or Skip. Never more than `cap` bytes."""
    if info.flag_bits & 0x1:
        raise Skip("an encrypted entry")
    if info.file_size > cap:
        raise Skip(f"{info.file_size:,} bytes inflated; the cap is {cap:,}")
    if _ratio_bomb(info):
        raise Skip(f"it inflates more than {CAPS['ratio']}:1")
    if budget is not None:
        budget.spend(info.file_size)
    try:
        with archive.open(info) as handle:
            data = handle.read(cap + 1)
    except ZIP_ERRORS as exc:
        raise Skip(f"it cannot be read ({type(exc).__name__}: {exc})") from None
    if len(data) > cap:
        raise Skip(f"more than {cap:,} bytes inflated")
    return data


def plist_set_name(data):
    """The `name` of an XML brushset.plist, or None. A binary plist is left to
    the file codec, which caps what it parses."""
    if not data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith((b"<?xml", b"<!DOCTYPE", b"<plist")):
        return None
    try:
        value = plistlib.loads(data, fmt=plistlib.FMT_XML)
    except Exception:           # anything a stranger's XML can raise: the name is only for display
        return None
    name = value.get("name") if isinstance(value, dict) else None
    return name if isinstance(name, str) else None


# ── what a scan finds ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Location:
    """One place a file was found: a file on disk, or an entry inside zips."""

    top: str                    # POSIX path of the file on disk, relative to the scanned folder
    path: Path                  # that file
    chain: tuple = ()           # entry names as stored, from the outermost zip inward
    shown: tuple = ()           # the same names for people

    @property
    def depth(self):
        return len(self.chain)

    @property
    def display(self):
        return show(self.top + "".join("!/" + name for name in self.shown))

    @property
    def basename(self):
        last = self.shown[-1] if self.shown else self.top
        return last.replace("\\", "/").rsplit("/", 1)[-1]

    def inside(self, info):
        return Location(self.top, self.path, self.chain + (info.orig_filename,),
                        self.shown + (shown_name(info),))


@dataclass
class Container:
    sha256: str
    size: int
    kind: str                   # "set" | "brush"
    set_name: str | None = None
    brush_count: int | None = None
    locations: list = field(default_factory=list)


@dataclass
class Document:
    rel: str
    path: Path
    size: int
    kind: str                   # "document" | "image" | "artwork" | "other"


class Scanner:
    """Walks a folder and records every brush container in it, once per sha256."""

    def __init__(self, src):
        self.src = Path(src)
        self.containers = {}            # sha256 -> Container
        # sha256 of a zip that is not a container -> what was found in it, as
        # (container sha256, entry names from that zip inward, the same for people)
        self.searched = {}
        self.documents = []
        self.skipped = []               # (where, why)
        self.zips_searched = 0

    def files(self):
        """(relative POSIX path, path) of every file, in one fixed order."""
        if self.src.is_file():
            return [(self.src.name, self.src)]
        found = []
        for folder, folders, names in os.walk(self.src):
            folders[:] = [name for name in folders if name.lower() not in JUNK_FOLDERS]
            for name in names:
                path = Path(folder) / name
                found.append((path.relative_to(self.src).as_posix(), path))
        return sorted(found, key=lambda item: (item[0].lower(), item[0]))

    def run(self):
        for rel, path in self.files():
            self.file(rel, path)
        return self

    def file(self, rel, path):
        low = path.name.lower()
        if low in JUNK_NAMES or low == EMPTY:
            return
        if path.is_symlink() or not path.is_file():
            self.skipped.append((show(rel), "not a regular file"))
            return
        size = path.stat().st_size
        with open(path, "rb") as handle:
            head = handle.read(len(LFS_HEADER))
        brushy = low.endswith(NESTED_SUFFIXES)
        if brushy and size <= LFS_POINTER_MAX and head == LFS_HEADER:
            raise EnvironmentProblem(f"{show(rel)} is a Git LFS pointer, not a brush file. "
                                     "Run `git lfs pull` and try again.")
        if low.endswith(ARTWORK_SUFFIXES) or head[:4] not in ZIP_MAGIC:
            if brushy:
                self.skipped.append((show(rel), "not a zip file, whatever its name says"))
            else:
                self.documents.append(Document(rel, path, size, document_kind(low)))
            return
        if size > CAPS["upload_bytes"]:
            self.skipped.append((show(rel), f"{size:,} bytes; the cap is {CAPS['upload_bytes']:,}"))
            return
        sha256 = file_sha256(path)
        location = Location(rel, path)
        if sha256 in self.containers:
            self.containers[sha256].locations.append(location)
            return
        if sha256 in self.searched:
            self.again(sha256, location)
            return
        try:
            with open(path, "rb") as handle, zipfile.ZipFile(handle) as archive:
                found = self.examine(archive, sha256, size, location, Budget())
        except Skip as exc:
            self.skipped.append((location.display, str(exc)))
            return
        except ZIP_ERRORS as exc:
            self.skipped.append((location.display, f"it cannot be opened as a zip ({type(exc).__name__})"))
            return
        if not found:
            if low.endswith((SET_SUFFIX, BRUSH_SUFFIX, ".brushset.zip", ".brush.zip")):
                self.skipped.append((location.display, f"it holds no {SET_PLIST} and no {BRUSH_ARCHIVE}"))
            else:
                self.documents.append(Document(rel, path, size, document_kind(low)))

    def again(self, sha256, location):
        """A zip that was searched before, met in another place: everything
        found in it is in that place too, as far down as the depth cap reaches."""
        within = []
        for found, chain, shown in self.searched[sha256]:
            place = Location(location.top, location.path, location.chain + chain, location.shown + shown)
            if place.depth > CAPS["nesting_depth"]:
                self.skipped.append((place.display, _too_deep()))
                continue
            self.containers[found].locations.append(place)
            within.append((found, chain, shown))
        return within

    def examine(self, archive, sha256, size, location, budget):
        """Record what an open zip is. Returns the containers it is or holds, each
        as (sha256, entry names from this zip inward, the same names for people)."""
        infos = list_entries(archive)
        names = {info.orig_filename for info in infos}
        kind, prefix = sniff(names)
        if kind != "other":
            check_declared(infos)
            container = Container(sha256, size, kind, locations=[location])
            if kind == "set":
                member = re.compile(re.escape(prefix) + "[^/]+/" + re.escape(BRUSH_ARCHIVE))
                container.brush_count = sum(1 for name in names if member.fullmatch(name))
                plist = next(info for info in infos if info.orig_filename == prefix + SET_PLIST)
                try:
                    container.set_name = plist_set_name(read_entry(archive, plist, CAPS["archive_bytes"]))
                except Skip:
                    pass
            self.containers[sha256] = container
            return [(sha256, (), ())]
        self.searched[sha256] = []              # set first: a zip that holds itself ends here
        self.zips_searched += 1
        found = []
        for info in infos:
            if not info.orig_filename.lower().endswith(NESTED_SUFFIXES):
                continue
            inner = location.inside(info)
            try:
                below = self.nested(archive, info, inner, budget)
            except Skip as exc:
                self.skipped.append((inner.display, str(exc)))
                continue
            found += [(held, inner.chain[-1:] + chain, inner.shown[-1:] + shown)
                      for held, chain, shown in below]
        self.searched[sha256] = found
        return found

    def nested(self, archive, info, location, budget):
        if location.depth > CAPS["nesting_depth"]:
            raise Skip(_too_deep())
        problem = hostile(info.orig_filename)
        if problem:
            raise Skip(problem)
        data = read_entry(archive, info, CAPS["upload_bytes"], budget)
        if data.startswith(LFS_HEADER):
            raise Skip("a Git LFS pointer, not a brush file")
        if data[:4] not in ZIP_MAGIC:
            raise Skip("not a zip file, whatever its name says")
        sha256 = hashlib.sha256(data).hexdigest()
        if sha256 in self.containers:
            self.containers[sha256].locations.append(location)
            return [(sha256, (), ())]
        if sha256 in self.searched:
            return self.again(sha256, location)
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as inner:
                found = self.examine(inner, sha256, len(data), location, budget)
        except ZIP_ERRORS as exc:
            raise Skip(f"it cannot be opened as a zip ({type(exc).__name__})") from None
        low = info.orig_filename.lower()
        if not found and low.endswith((SET_SUFFIX, BRUSH_SUFFIX, ".brushset.zip", ".brush.zip")):
            raise Skip(f"it holds no {SET_PLIST} and no {BRUSH_ARCHIVE}")
        return found


def read_location(location):
    """The bytes of a nested file, read again from the zip on disk."""
    budget = Budget()

    def dig(archive, chain):
        info = next((i for i in archive.infolist() if i.orig_filename == chain[0]), None)
        if info is None:
            raise IngestError(f"{location.display} is no longer where it was found")
        data = read_entry(archive, info, CAPS["upload_bytes"], budget)
        if len(chain) == 1:
            return data
        with zipfile.ZipFile(io.BytesIO(data)) as inner:
            return dig(inner, chain[1:])

    try:
        with open(location.path, "rb") as handle, zipfile.ZipFile(handle) as archive:
            return dig(archive, location.chain)
    except (Skip,) + ZIP_ERRORS as exc:
        raise IngestError(f"{location.display} cannot be read again: {exc}") from None


# ── the plan ─────────────────────────────────────────────────────────────────

@dataclass
class Item:
    """One container and what adoption does with it."""

    container: Container
    pack: str
    name: str
    named_after: Location
    source: Location
    status: str = "copy"        # copy | present | conflict
    held_at: str = ""           # for `present`: where the library already holds it

    @property
    def target(self):
        return f"{USER_DIR}/{self.pack}/{self.name}"


@dataclass
class DocumentItem:
    document: Document
    sha256: str
    pack: str
    name: str
    status: str = "copy"        # copy | present

    @property
    def target(self):
        return f"{USER_DIR}/{self.pack}/{DOCS_DIR}/{self.name}"


@dataclass
class Plan:
    src: Path
    library: Path
    scan: Scanner
    with_docs: bool
    items: list = field(default_factory=list)
    documents: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)

    def to_copy(self):
        return ([item for item in self.items if item.status == "copy"]
                + [item for item in self.documents if item.status == "copy"])

    def bytes_to_copy(self):
        return (sum(item.container.size for item in self.items if item.status == "copy")
                + sum(item.document.size for item in self.documents if item.status == "copy"))


def index_library(library):
    """{stored path: sha256} of every brush file already under library/user/."""
    folder = Path(library) / USER_DIR
    held = {}
    if not folder.is_dir():
        return held
    for path in sorted(folder.rglob("*")):
        if (not path.is_file() or path.name.endswith(PART_SUFFIX)
                or DOCS_DIR in path.relative_to(folder).parts):
            continue
        stored = bc.stored_path(path, library)
        if path.stat().st_size <= LFS_POINTER_MAX:
            with open(path, "rb") as handle:
                if handle.read(len(LFS_HEADER)) == LFS_HEADER:
                    raise EnvironmentProblem(f"{stored} is a Git LFS pointer, not the file. "
                                             "Run `git lfs pull` and try again.")
        held[stored] = file_sha256(path)
    return held


def _choose(container, sources, blockers):
    """(pack, the location that names the file, the location to copy from, other packs)."""
    ranked = []
    for location in container.locations:
        packs = packs_for(location.top, sources)
        if len(packs) > 1:
            blockers.append(f"{show(location.top)} fits more than one pack ({', '.join(packs)}). "
                            f"Each file must fit exactly one: fix the `match` patterns in {SOURCES_NAME}.")
        ranked.append(((not packs, location.depth > 0, location.top.lower(), location.top,
                        location.chain), location, packs[0] if packs else None))
    ranked.sort(key=lambda entry: entry[0])
    _, named_after, pack = ranked[0]
    on_disk = [location for _, location, _ in ranked if location.depth == 0]
    others = sorted({other for _, _, other in ranked if other and other != pack})
    return pack or UNSORTED, named_after, (on_disk[0] if on_disk else named_after), others


def build_plan(scan, sources, library, *, with_docs=False):
    plan = Plan(scan.src, Path(library), scan, with_docs)
    declared = {pack["id"]: pack for pack in sources["packs"]}
    for container in scan.containers.values():
        pack, named_after, source, others = _choose(container, sources, plan.blockers)
        item = Item(container, pack, adopted_name(named_after.basename, container.kind),
                    named_after, source)
        plan.items.append(item)
        if pack == UNSORTED:
            plan.warnings.append(f"{named_after.display} fits no pack in {SOURCES_NAME}; "
                                 f"it would be stored under {USER_DIR}/{UNSORTED}/")
        if others:
            plan.notes.append(f"{item.name} was also found in the files of {', '.join(others)}; "
                              f"it is stored once, under {pack}")
        if (pack in declared and container.kind == "set" and container.set_name is not None
                and container.set_name not in declared[pack].get("sets", {})):
            plan.notes.append(f"the set name {show(container.set_name)!r} ({item.name}) is not in the "
                              f"`sets` of pack {pack} in {SOURCES_NAME}")
    plan.items.sort(key=lambda item: (item.pack == UNSORTED, item.pack, item.name.lower(), item.name,
                                      item.container.sha256))

    _settle_names(plan, index_library(library))
    if with_docs:
        _plan_documents(plan, sources)
    return plan


def _settle_names(plan, held):
    """Mark what the library already holds, and give every other file a name
    nothing else has. `held` is {stored path: sha256} of the library's files.

    A name can be taken in two ways. By a file of this same scan (two files,
    one name): the later one carries eight characters of its hash, and a file
    that reached the library in an earlier run keeps the name it was given. By
    a library file this scan did not find: that is a conflict, and it stops the
    run, because it may be another version of the same pack, and replacing a
    file is the author's decision.
    """
    where = {}
    for stored, sha256 in held.items():
        where.setdefault(sha256, stored)
    owner = {stored.lower(): sha256 for stored, sha256 in held.items()}
    scanned = {item.container.sha256 for item in plan.items}
    for item in plan.items:
        if item.container.sha256 in where:
            item.status, item.held_at = "present", where[item.container.sha256]
    for item in plan.items:
        if item.status == "present":
            continue
        sha256 = item.container.sha256
        holder = owner.get(item.target.lower())
        if holder is not None and holder in scanned:
            renamed = with_hash(item.name, sha256)
            plan.notes.append(f"{item.named_after.display} would also be named {item.name}; "
                              f"it is stored as {renamed}")
            item.name = renamed
            holder = owner.get(item.target.lower())
        if holder is not None or (plan.library / item.target).exists():
            item.status = "conflict"
            plan.blockers.append(f"{item.target} already exists and is a different file. "
                                 "Nothing in the library is overwritten: move it away first.")
            continue
        owner[item.target.lower()] = sha256


def _plan_documents(plan, sources):
    """Give every document on disk a place in its pack's `_docs/`. A name that
    another file holds, in the plan or in the library, is tried once more with
    the content hash in it; the same bytes under the same name are one file."""
    taken = {}                  # (pack, lower-case name) -> sha256 of the file that has the name
    for document in plan.scan.documents:
        packs = packs_for(document.rel, sources)
        if len(packs) > 1:
            plan.blockers.append(f"{show(document.rel)} fits more than one pack ({', '.join(packs)}). "
                                 f"Fix the `match` patterns in {SOURCES_NAME}.")
            continue
        pack = packs[0] if packs else UNSORTED
        sha256 = file_sha256(document.path)
        name = document_name(document.path.name)
        for candidate in (name, with_hash(name, sha256)):
            key = (pack, candidate.lower())
            if key in taken:
                if taken[key] == sha256:
                    break                                   # already planned: the same file again
                continue
            target = plan.library / USER_DIR / pack / DOCS_DIR / candidate
            if target.exists():
                taken[key] = file_sha256(target) if target.is_file() else ""
                if taken[key] == sha256:
                    plan.documents.append(DocumentItem(document, sha256, pack, candidate, "present"))
                    break
                continue
            taken[key] = sha256
            plan.documents.append(DocumentItem(document, sha256, pack, candidate))
            break
        else:
            plan.warnings.append(f"{show(document.rel)} is not copied: both names it could take in "
                                 f"{USER_DIR}/{pack}/{DOCS_DIR}/ belong to other files")
    plan.documents.sort(key=lambda item: (item.pack, item.name.lower(), item.name))


def render(plan, free=None):
    """The plan as text. The same input gives the same text."""
    scan, items = plan.scan, plan.items
    sets = sum(1 for item in items if item.container.kind == "set")
    total = sum(item.container.size for item in items)
    copies = sum(len(item.container.locations) - 1 for item in items)
    lines = [
        f"ADOPT     {plan.src}",
        f"INTO      {plan.library / USER_DIR}",
        f"FOUND     {len(items)} brush files ({sets} sets, {len(items) - sets} brushes), {total:,} bytes",
        f"          {copies} more copies of them recognised by sha256 (not copied twice)",
        f"          {scan.zips_searched} other zip files searched; "
        f"{len(scan.documents)} other files on disk not adopted",
    ]
    by_pack = {}
    for item in items:
        by_pack.setdefault(item.pack, []).append(item)
    for pack, members in by_pack.items():
        size = sum(item.container.size for item in members)
        lines += ["", f"{pack}   {len(members)} files, {size:,} bytes"]
        for item in members:
            container = item.container
            about = ""
            if container.kind == "set":
                named = "name unread" if container.set_name is None else repr(show(container.set_name))
                about = f"   {named}, {container.brush_count} brushes"
            word = {"copy": "copy", "present": "present", "conflict": "CONFLICT"}[item.status]
            lines.append(f"  {word:<8} {container.kind:<5} {container.size:>12,}  {item.name}{about}")
            extra = len(container.locations) - 1
            more = f"   (+{extra} identical)" if extra else ""
            lines.append(f"           from  {item.named_after.display}{more}")
            if item.status == "present" and item.held_at != item.target:
                lines.append(f"           held  {item.held_at}")
    if plan.documents:
        lines += ["", f"DOCUMENTS   copied to <pack>/{DOCS_DIR}/, which git ignores"]
        for item in plan.documents:
            lines.append(f"  {item.status:<8} {item.document.size:>12,}  {item.target}"
                         f"   from  {show(item.document.rel)}")
    elif scan.documents:
        kinds = {}
        for document in scan.documents:
            count, size = kinds.get(document.kind, (0, 0))
            kinds[document.kind] = (count + 1, size + document.size)
        lines += ["", "NOT ADOPTED   documents, images and artwork stay where they are "
                      "(--with-docs copies them to an ignored _docs/)"]
        for kind in sorted(kinds):
            lines.append(f"  {kinds[kind][0]:>4} {kind:<9} {kinds[kind][1]:>14,} bytes")
    for title, entries in (("NOTES", plan.notes), ("WARNINGS", plan.warnings)):
        if entries:
            lines += ["", title] + [f"  {entry}" for entry in entries]
    if scan.skipped:
        lines += ["", "SKIPPED   read as far as it was safe, and left out"]
        lines += [f"  {where}: {show(why)}" for where, why in scan.skipped]
    large = [item for item in items if item.container.size > PLAIN_BLOB_LIMIT]
    if large:
        lines += ["", f"OVER {PLAIN_BLOB_LIMIT // 1_000_000} MB   too large for a plain git blob; "
                      "these must go through Git LFS"]
        lines += [f"  {item.container.size:>12,}  {item.held_at or item.target}" for item in large]
    if plan.blockers:
        lines += ["", "REFUSED"] + [f"  {entry}" for entry in plan.blockers]
    waiting = plan.to_copy()
    present = sum(1 for item in items + plan.documents if item.status == "present")
    lines += ["", f"TOTAL     {len(waiting)} files to copy, {plan.bytes_to_copy():,} bytes; "
                  f"{present} already in the library"]
    if free is not None:
        lines.append(f"          {free:,} bytes free on the library's disk")
    return "\n".join(lines)


# ── writing ──────────────────────────────────────────────────────────────────

def _pieces(location):
    if location.depth:
        yield read_location(location)
        return
    with open(location.path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                return
            yield chunk


def copy_checked(location, sha256, dest):
    """Copy one file through `<dest>.part`; move it into place only if the bytes
    written have the hash the plan was made with. Never replaces a file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + PART_SUFFIX)
    digest = hashlib.sha256()
    try:
        with open(part, "wb") as out:
            for chunk in _pieces(location):
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != sha256:
            raise IngestError(f"{location.display} changed while it was being copied; "
                              f"{dest.name} was not written")
        if dest.exists():
            raise IngestError(f"{dest.name} appeared while the copy ran; it was not replaced")
        os.replace(part, dest)
    except OSError as exc:
        raise IngestError(f"{dest.name} could not be written: {exc}") from None
    finally:
        if part.exists():
            part.unlink()


def apply_plan(plan):
    """Do every `copy` of a plan. Returns (files written, bytes written)."""
    count = size = 0
    for item in plan.items:
        if item.status == "copy":
            copy_checked(item.source, item.container.sha256, plan.library / item.target)
            count, size = count + 1, size + item.container.size
    for item in plan.documents:
        if item.status == "copy":
            copy_checked(Location(item.document.rel, item.document.path), item.sha256,
                         plan.library / item.target)
            count, size = count + 1, size + item.document.size
    return count, size


def _disk_free(folder):
    folder = Path(folder)
    while not folder.exists() and folder.parent != folder:
        folder = folder.parent
    return shutil.disk_usage(folder).free


# ── the verbs ────────────────────────────────────────────────────────────────

def run_where(paths):
    """Print every resolved folder and file, and whether it is there."""
    width = max(len(name) for name in paths._fields)
    for name in paths._fields:
        path = getattr(paths, name)
        print(f"{name:<{width}}  {'present' if path.exists() else 'missing':<8} {path}")
    manifest = paths.library / SOURCES_NAME
    if manifest.is_file():
        try:
            sources = load_sources(paths.library)
        except IngestError as exc:
            print(f"{'manifest':<{width}}  {'unusable':<8} {exc}")
        else:
            official = sources.get("official")
            files = official.get("files") if isinstance(official, dict) else None
            print(f"{'manifest':<{width}}  {'present':<8} {len(sources['packs'])} user packs, "
                  f"{len(files) if isinstance(files, list) else 0} official files")
    else:
        print(f"{'manifest':<{width}}  {'missing':<8} {manifest}")
    return bc.EXIT_OK


def run_adopt(paths, src, *, with_docs=False, confirm=False, disk_free=None):
    library = paths.library
    source = Path(os.path.expanduser(str(src))).resolve()
    if not source.exists():
        raise EnvironmentProblem(f"there is nothing at {source}")
    sources = load_sources(library)
    if source == library or library in source.parents or source in library.parents:
        raise EnvironmentProblem(f"{source} and the library {library} overlap; adopt from outside it")
    scan = Scanner(source).run()
    plan = build_plan(scan, sources, library, with_docs=with_docs)
    free = (disk_free or _disk_free)(library)
    print(render(plan, free))
    print()
    if plan.blockers:
        print("REFUSED   nothing was written." if confirm else DRY_RUN_LINE)
        return bc.EXIT_REFUSED
    if not confirm:
        print(DRY_RUN_LINE)
        return bc.EXIT_OK
    if not plan.to_copy():
        print("DONE      nothing to copy: everything found is already in the library.")
        return bc.EXIT_OK
    if free < plan.bytes_to_copy() + SPACE_MARGIN:
        raise EnvironmentProblem(f"{plan.bytes_to_copy():,} bytes are needed and only {free:,} are "
                                 f"free under {library}")
    count, size = apply_plan(plan)
    print(f"DONE      {count} files copied, {size:,} bytes, each checked against its sha256.")
    return bc.EXIT_OK


# ── the command line ─────────────────────────────────────────────────────────

def _add_roots(parser, default):
    for name in ("root", "library", "catalog", "vault"):
        parser.add_argument(bc.FLAGS[name], metavar="DIR", default=default, help=bc.FLAG_HELP[name])


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ingest.py",
        description="Bring brush files into the library. `adopt` is a dry run without --confirm.")
    _add_roots(parser, None)
    verbs = parser.add_subparsers(dest="verb", metavar="{where,adopt}", required=True)
    where = verbs.add_parser("where", help="print the folders the brushes scripts work on")
    adopt = verbs.add_parser("adopt", help="copy the brush files under SRC into library/user/ "
                                           "(a dry run without --confirm)")
    adopt.add_argument("src", metavar="SRC", help="a folder, or one file, to look for brush files in")
    adopt.add_argument("--with-docs", action="store_true",
                       help="also copy documents, images and artwork into an ignored _docs/ folder")
    adopt.add_argument("--confirm", action="store_true", help="really copy")
    for sub in (where, adopt):
        _add_roots(sub, argparse.SUPPRESS)
    return parser


def main(argv=None, *, disk_free=None):
    """`disk_free` exists for the tests."""
    bc.open_console()
    args = build_parser().parse_args(argv)
    paths = bc.paths_from_args(args)
    try:
        if args.verb == "where":
            return run_where(paths)
        return run_adopt(paths, args.src, with_docs=args.with_docs, confirm=args.confirm,
                         disk_free=disk_free)
    except IngestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
