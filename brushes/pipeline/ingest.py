"""Bring brush files into the library.

    python -I brushes/pipeline/ingest.py where
    python -I brushes/pipeline/ingest.py adopt <src> [--with-docs] [--confirm]
    python -I brushes/pipeline/ingest.py census [--json]

`where` prints the folders every brushes script works on, and whether each
exists. `adopt` copies the brush files found in a folder (or in one file) into
library/user/<pack_id>/, one copy of each (docs/CONTRACTS.md, F11 and F12).
`census` counts what the library's archives hold (brush_model.census) and
prints it, a summary or with --json the whole census and its schema columns
(brush_model.census_columns), which is what the census columns of
schema/silica_keys.json are merged from by hand (F4). It writes nothing. The
catalog verbs (`build`, `report`) are not part of this module yet.

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
apply to everything read here. The caps, the sniffing and the rules of what is
a member and what is junk are the file codec's (container.py): this module
takes them from there and keeps no copy of its own. Run this as
`python -I brushes/pipeline/ingest.py ...`.

Exit codes: 0 ok, 1 refused or failed, 2 usage or environment.
Standard library only.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import math
import os
import plistlib
import re
import shutil
import sys
import unicodedata
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import identity  # noqa: E402
import png_io  # noqa: E402
from bplist import BrushModelError, CodecError, ContainerError, LimitExceeded  # noqa: E402

SOURCES_NAME = "sources.json"
SOURCES_SCHEMA = "rosw-brushes-sources/1"
USER_DIR = "user"
DOCS_DIR = "_docs"
UNSORTED = "unsorted"
PART_SUFFIX = ".part"
SET_SUFFIX = ".brushset"
BRUSH_SUFFIX = ".brush"
SET_PLIST = container.SET_PLIST
BRUSH_ARCHIVE = container.ARCHIVE

MIB = 1024 * 1024
# The reader's caps (docs/CONTRACTS.md F3; spec.yaml format.caps): the codec's
# own dict, so that the reader and ingest cannot drift apart.
CAPS = container.CAPS

NESTED_SUFFIXES = container.NESTED_SUFFIXES        # `.brushset.zip` ends in `.zip`
STRIPPED_SUFFIXES = (".brushset.zip", ".brush.zip", ".brushset", ".brush", ".zip")
ZIP_MAGIC = container.ZIP_MAGIC
LFS_HEADER = container.LFS_HEADER
LFS_POINTER_MAX = 1024
# Junk: part of no brush folder, in a zip or on disk (docs/CONTRACTS.md, F3
# "Reading"). The codec's sets; device_tests.py spells the same two.
JUNK_FOLDERS = container.JUNK_FOLDERS
JUNK_NAMES = container.JUNK_NAMES
# A zero-byte placeholder some official sets carry. Inside a zip it is a member
# of the brush folder it sits in, and is listed like any other entry: only the
# file codec decides what a member is, and it keeps this one. It never decides
# what a container is (`sniff`), and a loose one on disk is not a brush file or
# a document.
EMPTY = container.EMPTY
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
ZIP_ERRORS = container.ZIP_ERRORS


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


# The reading rules are container.py's. What they raise is turned into Skip
# here: one file or entry that is not read, with the codec's sentence as why.

shown_name = container.shown_name
hostile = container.hostile
sniff = container.sniff


def _skip(exc):
    return Skip(exc.detail or exc.code)


def list_entries(archive):
    """The entries of an open zip that count: files only, the first of a
    repeated name, and no junk (nothing from `__MACOSX/`, no `.DS_Store`,
    `Thumbs.db` or `desktop.ini`). A `.empty` placeholder is an entry like any
    other: inside a brush folder it is a member (docs/CONTRACTS.md, F3)."""
    try:
        return container.list_entries(archive.infolist()).kept
    except ContainerError as exc:
        raise _skip(exc) from None


def check_declared(infos):
    """Refuse a container whose own directory already breaks the reader's caps."""
    try:
        container.check_declared(infos)
    except ContainerError as exc:
        raise _skip(exc) from None


def _too_deep():
    return f"nested more than {CAPS['nesting_depth']} zips deep; not opened"


class Budget(container.Budget):
    """How many bytes may still be inflated out of one file on disk."""

    def spend(self, size):
        try:
            super().spend(size)
        except ContainerError as exc:
            raise _skip(exc) from None


def read_entry(archive, info, cap, budget=None):
    """One entry's bytes, in memory, or Skip. Never more than `cap` bytes."""
    try:
        return container.read_member(archive, info, cap, budget)
    except ContainerError as exc:
        raise _skip(exc) from None


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


def run_census(paths, *, as_json=False):
    """Count what every archive of the library holds and print it. Reads the
    library in memory through container.py; writes nothing."""
    library = paths.library
    if not library.is_dir():
        raise EnvironmentProblem(f"there is no library folder at {library}")
    try:
        result = brush_model.census(library)
    except BrushModelError as exc:
        if exc.code in ("lfs_pointer", "library_missing"):
            raise EnvironmentProblem(str(exc)) from None
        raise IngestError(str(exc)) from None
    except CodecError as exc:                  # a cap of F3 (LimitExceeded) among them
        raise IngestError(str(exc)) from None
    result["columns"] = brush_model.census_columns(result)
    if as_json:
        sys.stdout.write(bc.json_text(result))
        return bc.EXIT_OK
    print(f"census   {result['archives']:,} archives, {result['distinct']:,} distinct, "
          f"{len(result['unreadable']):,} unreadable, {len(result['keys']):,} root keys")
    print(f"{'era':<7} {'family':<7} {'count':>6} {'keys':>5}  profiles; fidelity; rebuild")
    for row in result["eras"]:
        counted = "; ".join(", ".join(f"{name} {count}" for name, count in row[part].items())
                            for part in ("profiles", "fidelity", "rebuild"))
        print(f"{show(row['id']):<7} {row['family']:<7} {row['count']:>6} {row['key_count']:>5}  {counted}")
    for item in result["unreadable"]:
        print(f"unreadable  {show(item['label'])}: {show(item['error'])}")
    return bc.EXIT_OK


# ── the catalog: constants and small readers ─────────────────────────────────

INGEST_VERSION = 1
BRUSH_SCHEMA = "rosw-brushes-brush/1"
CATALOG_SCHEMA = "rosw-brushes-catalog/1"
REPORT_SCHEMA = "rosw-brushes-ingest-report/1"
FACETS_SCHEMA = "rosw-brushes-facets/1"
# A code asset, like silica_keys.json: the folder beside pipeline/, whatever
# --root says (docs/CONTRACTS.md F2).
FACETS_PATH = bc.TOOL_ROOT / "schema" / "facets.json"

OFFICIAL_DIR = "official"
BUNDLED_DIR = "bundled"
BRUSHES_DIR = "brushes"
SETS_DIR = "sets"
CATALOG_NAME = "catalog.json"
TEXTURES_NAME = "textures.json"
THUMBNAILS_NAME = "thumbnails.json"
CONTAINERS_NAME = "containers.json"
REPORT_NAME = "ingest_report.json"
CONTAINER_FILE_SUFFIXES = (".brush", ".brushset", ".zip")
LIBRARIES = ("user", "official")
STROKE_SOURCES = ("thumbnail", "reset-thumbnail", "none", "rendered-approx")
NOTE_FOLDER = {"official": "01_Procreate_Defaults", "mine": "04_My_Brushes",
               "loose": "03_Loose", "other": "02_Vendor_Packs"}
RESET_THUMBNAIL = f"{container.RESET}/{container.THUMBNAIL}"
SUB_ARCHIVE = f"{container.SUB}/{container.ARCHIVE}"
DIFFERING_KEYS_MAX = 20
NS_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
PACK_FIELDS = ("id", "kind", "vendor", "product", "source_url", "licence_note", "redistribute",
               "publish_previews", "evidence")
_ABSENT = object()


def _read_json(path, default=None):
    """A generated JSON file of the catalog, or `default` when it is not there."""
    try:
        return json.loads(bc.read_text(path))
    except FileNotFoundError:
        return default
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise IngestError(f"{Path(path).name} in the catalog cannot be read as JSON: "
                          f"{type(exc).__name__}") from None


def _read_map(path):
    value = _read_json(path, {})
    return value if isinstance(value, dict) else {}


def _write_if_changed(path, value):
    """Write `value` in the one JSON spelling unless the file already holds
    exactly that text. True when the file was written."""
    text = bc.json_text(value)
    path = Path(path)
    try:
        if bc.read_text(path) == text:
            return False
    except FileNotFoundError:
        pass
    except (OSError, UnicodeDecodeError):
        pass
    bc.write_text(path, text)
    return True


def _sha(data):
    return hashlib.sha256(data).hexdigest()


# ── facets (docs/CONTRACTS.md F5 "Facets"; thresholds in schema/facets.json) ─

def load_facet_rules(path=None):
    """schema/facets.json, checked against the facet functions of this module.
    A missing or unusable file is exit 2: it is part of the code."""
    path = Path(path) if path is not None else FACETS_PATH
    try:
        rules = json.loads(bc.read_text(path))
    except FileNotFoundError:
        raise EnvironmentProblem(f"the facet rules are not at {path}") from None
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise EnvironmentProblem(f"{path.name} cannot be read as JSON: {exc}") from None
    if (not isinstance(rules, dict) or rules.get("schema") != FACETS_SCHEMA
            or not isinstance(rules.get("facets"), dict)):
        raise EnvironmentProblem(f"{path.name} is not a {FACETS_SCHEMA} file")
    named, coded = list(rules["facets"]), list(FACET_FUNCTIONS)
    if set(named) != set(coded):
        raise EnvironmentProblem(
            f"{path.name} and ingest.py name different facets: only in the file "
            f"{sorted(set(named) - set(coded))}, only in the code {sorted(set(coded) - set(named))}")
    unknown = [name for name in rules.get("word_order", []) if name not in rules["facets"]]
    if unknown or not isinstance(rules.get("round"), int):
        raise EnvironmentProblem(f"{path.name}: `word_order` names {unknown}, or `round` is not a number")
    return rules


def _number(params, key):
    """S(key) as a finite number (a tag opened), else None. A bool is not a number."""
    value = brush_model.scalar(brush_model.setting(params, key))
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) else None


def _code(params, key):
    """S(key) as a whole number, else None."""
    value = _number(params, key)
    if value is None or value != int(value):
        return None
    return int(value)


def _truthy(params, key):
    value = brush_model.scalar(brush_model.setting(params, key))
    return bool(value) if isinstance(value, (bool, int, float)) else False


def _flag(params, key):
    """A bool setting, or None when the archive does not hold the key."""
    if not params or brush_model.setting(params, key) is None:
        return None
    return _truthy(params, key)


def _round(value, places):
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value):
        return None
    rounded = round(float(value), places)
    return 0.0 if rounded == 0 else rounded


def class_of(value, classes):
    """The class of a number under a `classes` list of schema/facets.json."""
    if value is None or isinstance(value, bool):
        return None
    for row in classes:
        if "upto" in row:
            if value <= row["upto"]:
                return row["class"]
        elif "below" in row:
            if value < row["below"]:
                return row["class"]
        else:
            return row["class"]
    return None


@dataclass
class FacetInput:
    """What the facets of one brush are computed from: the brush record's own
    fields, and the measured statistics once previews.py has run."""

    params: dict
    era: str | None
    family: str | None
    shape_source: str
    grain_source: str
    dual: bool
    stroke_source: str
    shape_stats: dict | None = None     # {coverage, aspect, midtone, edge_touch}
    grain_stats: dict | None = None     # {mean, contrast}


def _f_kind(inp, rule, get, places):
    return rule["when_true"] if _truthy(inp.params, rule["keys"][0]) else rule["when_false"]


def _f_true(inp, rule, get, places):
    return _truthy(inp.params, rule["keys"][0])


def _f_value(inp, rule, get, places):
    return _round(_number(inp.params, rule["keys"][0]), places)


def _f_code(inp, rule, get, places):
    return _code(inp.params, rule["keys"][0])


def _f_class(inp, rule, get, places):
    return class_of(get(rule["of"]), rule["classes"])


def _f_shape_source(inp, rule, get, places):
    return inp.shape_source


def _f_grain_source(inp, rule, get, places):
    return inp.grain_source


def _f_shape_bundled(inp, rule, get, places):
    return inp.shape_source in rule["sources"]


def _f_grain_bundled(inp, rule, get, places):
    return inp.grain_source in rule["sources"]


def _f_has_grain(inp, rule, get, places):
    if inp.grain_source in rule["embedded"]:
        contrast = get("grain_contrast")
        return contrast is None or contrast >= rule["embedded_min_contrast"]
    return inp.grain_source in rule["sources"]


def _f_grain_movement(inp, rule, get, places):
    value = _round(_number(inp.params, rule["keys"][0]), places)
    if value is None:
        return None
    if value <= rule["static_at"]:
        return "static"
    return "rolling" if value >= rule["rolling_from"] else "partial"


def _f_wet_mix(inp, rule, get, places):
    if brush_model.setting(inp.params, rule["render_key"]) is not None:
        return _code(inp.params, rule["render_key"]) == rule["render_value"]
    mix = _number(inp.params, rule["mix_key"])
    return mix is not None and mix > rule["mix_above"]


def _f_render_code(inp, rule, get, places):
    params = inp.params
    for key, template in ((rule["render_key"], rule["render_template"]),
                          (rule["glaze_key"], rule["glaze_template"])):
        if brush_model.setting(params, key) is not None:
            code = _code(params, key)
            return template.format(n=code) if code is not None else None
    switches = rule["transfer_keys"]
    if all(brush_model.setting(params, key) is not None for key, _, _ in switches):
        return rule["transfer_template"].format(
            *[on if _truthy(params, key) else off for key, on, off in switches])
    return None


def _f_largest_above(inp, rule, get, places):
    values = [_number(inp.params, key) for key in rule["keys"]]
    values = [value for value in values if value is not None]
    return bool(values) and max(values) > rule["above"]


def _f_taper(inp, rule, get, places):
    start, end = get("taper_start"), get("taper_end")
    return "both" if start and end else "start" if start else "end" if end else "none"


def _f_any_above(inp, rule, get, places):
    for key in rule["keys"]:
        value = _number(inp.params, key)
        if value is not None and (abs(value) if rule.get("absolute") else value) > rule["above"]:
            return True
    return False


def _f_any_not_equal(inp, rule, get, places):
    for key in rule["keys"]:
        value = _number(inp.params, key)
        if value is not None and value != rule["not_equal"]:
            return True
    return False


def _f_below(inp, rule, get, places):
    value = get(rule["of"])
    return value is not None and value < rule["below"]


def _f_dual(inp, rule, get, places):
    return bool(inp.dual)


def _f_era(inp, rule, get, places):
    return inp.era


def _f_family(inp, rule, get, places):
    return inp.family


def _f_stroke_source(inp, rule, get, places):
    return inp.stroke_source


def _f_measured(inp, rule, get, places):
    role, field_name = rule["measured"]
    stats = inp.shape_stats if role == "shape" else inp.grain_stats
    return _round(stats.get(field_name), places) if isinstance(stats, dict) else None


# One function per facet name: the names equal spec.yaml `facets` and the keys
# of schema/facets.json (pipeline/tests/test_ingest_build.py holds all three).
FACET_FUNCTIONS = {
    "kind": _f_kind,
    "is_stamp": _f_true,
    "spacing": _f_value,
    "spacing_class": _f_class,
    "shape_source": _f_shape_source,
    "uses_bundled_shape": _f_shape_bundled,
    "grain_source": _f_grain_source,
    "has_grain": _f_has_grain,
    "uses_bundled_grain": _f_grain_bundled,
    "grain_movement": _f_grain_movement,
    "grain_application_code": _f_code,
    "wet_mix": _f_wet_mix,
    "render_code": _f_render_code,
    "taper": _f_taper,
    "taper_start": _f_largest_above,
    "taper_end": _f_largest_above,
    "pressure_size": _f_value,
    "pressure_size_class": _f_class,
    "pressure_opacity": _f_value,
    "pressure_opacity_class": _f_class,
    "tilt": _f_any_above,
    "speed": _f_any_above,
    "size_min": _f_value,
    "size_max": _f_value,
    "size_class": _f_class,
    "opacity_min": _f_value,
    "opacity_max": _f_value,
    "translucent": _f_below,
    "dual": _f_dual,
    "dual_blend_code": _f_code,
    "blend_code": _f_code,
    "blend_extended_code": _f_code,
    "scatter": _f_any_above,
    "shape_rotation": _f_any_not_equal,
    "randomised": _f_true,
    "azimuth": _f_true,
    "jitter_size": _f_any_above,
    "jitter_opacity": _f_any_above,
    "jitter_position": _f_any_above,
    "streamline": _f_any_above,
    "color_dynamics": _f_any_not_equal,
    "wet_edges": _f_any_above,
    "burnt_edges": _f_any_above,
    "era": _f_era,
    "family": _f_family,
    "stroke_source": _f_stroke_source,
    "shape_coverage": _f_measured,
    "shape_aspect": _f_measured,
    "shape_midtone": _f_measured,
    "shape_edge_touch": _f_measured,
    "grain_mean": _f_measured,
    "grain_contrast": _f_measured,
}


def compute_facets(inp, rules):
    """Every facet of one brush, by the rules of schema/facets.json."""
    rows, places, done = rules["facets"], rules["round"], {}

    def get(name):
        if name not in done:
            done[name] = FACET_FUNCTIONS[name](inp, rows[name], get, places)
        return done[name]

    return {name: get(name) for name in FACET_FUNCTIONS}


def facet_words(facets, rules):
    """The facet words of a facet dict, in the rules' `word_order`."""
    words = []
    for name in rules.get("word_order", []):
        rule = rules["facets"][name]
        spec = rule.get("word")
        value = facets.get(name)
        word = None
        if not spec:
            continue
        if "if_true" in spec:
            word = spec["if_true"] if value is True else None
        elif "map" in spec:
            word = spec["map"].get(value) if isinstance(value, str) else None
        elif "template" in spec:
            template = spec["template"]
            if "{class}" in template:
                found = class_of(value, rule.get("classes", []))
                word = template.format(**{"class": found}) if found else None
            elif value is not None and not any(value == skip and type(value) is type(skip)
                                               or (skip is None and value is None)
                                               for skip in spec.get("skip", [])):
                text = str(value)
                word = template.format(value=text.lower() if spec.get("lower") else text)
        if word and word not in words:
            words.append(word)
    return words


def finish_record(record, thumbnails, textures, rules):
    """A brush record with its three preview-derived fields (`facets`,
    `facet_words`, `preview`) worked out from the record itself, the entries of
    thumbnails.json and textures.json, and the facet rules. Pure: nothing else
    of the record changes (docs/CONTRACTS.md F5 "Preview-derived fields")."""
    thumbnail = record.get("thumbnail") or {}
    reset = record.get("reset") or {}
    own = thumbnail.get("sha256") if thumbnail.get("present") else None
    current = [sha for sha in (own, reset.get("thumbnail_sha256")) if sha]
    provisional = ("thumbnail" if own else "reset-thumbnail" if reset.get("thumbnail_sha256")
                   else "none")
    entry = thumbnails.get(record["id"]) if isinstance(thumbnails, dict) else None
    valid = (isinstance(entry, dict) and entry.get("stroke_source") in STROKE_SOURCES
             and (entry.get("source_sha256") in current if current
                  else entry.get("source_sha256") is None))
    shape, grain = record["shape"], record["grain"]
    shape_tile = grain_tile = shape_stats = grain_stats = None
    if valid:
        held = textures.get(shape.get("texture_id")) if shape.get("texture_id") else None
        if isinstance(held, dict):
            side = "i" if shape.get("inverted") else "n"
            shape_tile = (held.get("shape_tiles") or {}).get(side)
            shape_stats = ((held.get("stats") or {}).get("shape") or {}).get(side)
        held = textures.get(grain.get("texture_id")) if grain.get("texture_id") else None
        if isinstance(held, dict):
            grain_tile = held.get("grain_tile")
            grain_stats = (held.get("stats") or {}).get("grain")
    preview = {
        "stroke": entry.get("stroke") if valid and isinstance(entry.get("stroke"), str) else None,
        "stroke_source": entry["stroke_source"] if valid else provisional,
        "shape": shape_tile if isinstance(shape_tile, str) else None,
        "shape_source": shape["source"],
        "grain": grain_tile if isinstance(grain_tile, str) else None,
        "grain_source": grain["source"],
    }
    inp = FacetInput(params=record.get("settings") or {}, era=record.get("era"),
                     family=record.get("family"), shape_source=shape["source"],
                     grain_source=grain["source"], dual=record.get("secondary") is not None,
                     stroke_source=preview["stroke_source"],
                     shape_stats=shape_stats if isinstance(shape_stats, dict) else None,
                     grain_stats=grain_stats if isinstance(grain_stats, dict) else None)
    facets = compute_facets(inp, rules)
    out = dict(record)
    out["facets"] = facets
    out["facet_words"] = facet_words(facets, rules)
    out["preview"] = preview
    return out


# ── assembling catalog.json, and the preview step's way back in ──────────────

def library_fingerprint(containers):
    """`sha256:16:<16 hex>` over every container's library path and sha256."""
    lines = sorted(f"{path}\t{sha}" for sha, entry in containers.items()
                   for path in (entry.get("paths") or []))
    return "sha256:16:" + _sha("\n".join(lines).encode("utf-8"))[:16]


def _catalog_paths(paths):
    catalog = Path(paths.catalog)
    return catalog, catalog / BRUSHES_DIR, catalog / SETS_DIR


def _load_records(folder, pattern):
    records = []
    if folder.is_dir():
        for path in sorted(folder.glob(pattern)):
            value = _read_json(path)
            if isinstance(value, dict):
                records.append(value)
    return records


def assemble_index(paths, packs=None):
    """Write catalog.json from the brush records, the set records, textures.json
    and containers.json; a pure function of them. `packs` are the manifest rows
    of the packs (build passes them; otherwise those of the catalog.json on
    disk are kept). Returns the catalog."""
    catalog, brushes_dir, sets_dir = _catalog_paths(paths)
    records = _load_records(brushes_dir, "b_*.json")
    sets = sorted(_load_records(sets_dir, "*.json"), key=lambda row: row.get("set_slug", ""))
    textures = _read_map(catalog / TEXTURES_NAME)
    containers = _read_map(catalog / CONTAINERS_NAME)
    rules = load_facet_rules()
    if packs is None:
        held = _read_map(catalog / CATALOG_NAME).get("packs") or []
        packs = [{key: value for key, value in pack.items() if key != "counts"}
                 for pack in held if isinstance(pack, dict)]
    rows = []
    by_library = dict.fromkeys(LIBRARIES, 0)
    for record in sorted(records, key=lambda r: r["id"]):
        rows.append({"id": record["id"], "name": record["name"], "display_name": record["display_name"],
                     "home_set": record["home"]["set_slug"], "position": record["home"]["position"],
                     "library": record["library"], "family": record["family"], "era": record["era"],
                     "key_count": record["format"]["key_count"], "facets": record["facets"],
                     "facet_words": record["facet_words"], "preview": record["preview"],
                     "occurrence_count": len(record["occurrences"])})
        if record["library"] in by_library:
            by_library[record["library"]] += 1
    pack_rows = []
    for pack in sorted(packs, key=lambda p: p["id"]):
        ident = pack["id"]
        counts = {
            "containers": sum(1 for entry in containers.values() if entry.get("pack") == ident),
            "sets": sum(1 for row in sets if row.get("pack") == ident),
            "brushes": sum(1 for record in records if record["pack"] == ident),
            "occurrences": sum(1 for record in records for place in record["occurrences"]
                               if place["pack"] == ident),
        }
        pack_rows.append({**pack, "counts": counts})
    value = {
        "schema": CATALOG_SCHEMA,
        "ingest_version": INGEST_VERSION,
        "facet_rules_version": rules["facet_rules_version"],
        "library_fingerprint": library_fingerprint(containers),
        "counts": {"brushes": len(records),
                   "occurrences": sum(len(record["occurrences"]) for record in records),
                   "sets": len(sets), "notes": sum(1 for row in sets if row.get("note")),
                   "packs": len(pack_rows), "textures": len(textures), "by_library": by_library},
        "packs": pack_rows,
        "sets": sets,
        "brushes": rows,
    }
    catalog.mkdir(parents=True, exist_ok=True)
    _write_if_changed(catalog / CATALOG_NAME, value)
    return value


def apply_preview_results(paths, packs=None):
    """Set the three preview-derived fields of every brush record from
    thumbnails.json and textures.json, rewrite a record only when its text
    changes, then reassemble catalog.json (docs/CONTRACTS.md F5). The one code
    that derives a facet word from a measurement. Returns the number of brush
    records rewritten."""
    catalog, brushes_dir, _ = _catalog_paths(paths)
    rules = load_facet_rules()
    thumbnails = _read_map(catalog / THUMBNAILS_NAME)
    textures = _read_map(catalog / TEXTURES_NAME)
    changed = 0
    if brushes_dir.is_dir():
        for path in sorted(brushes_dir.glob("b_*.json")):
            record = _read_json(path)
            if not isinstance(record, dict):
                continue
            if _write_if_changed(path, finish_record(record, thumbnails, textures, rules)):
                changed += 1
    assemble_index(paths, packs)
    return changed


# ── the catalog: reading the library ─────────────────────────────────────────

def _png_header(data):
    try:
        info = png_io.png_info(data)
    except (CodecError, ValueError):
        return None
    return info


def _date_text(form):
    """An NSDate form as `YYYY-MM-DDTHH:MM:SSZ` (UTC), or None."""
    seconds = form.get("time") if isinstance(form, dict) else None
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds):
        return None
    try:
        return (NS_EPOCH + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return None


def _ref_size(archive):
    """The object reference size in a binary property list's trailer."""
    if len(archive) >= 40 and archive.startswith(b"bplist00"):
        return archive[-25]
    return None


@dataclass
class SetRow:
    """A brushset or a pack's loose pseudo-set, before ids and homes are known."""

    kind: str                   # "set" | "loose"
    name: str
    slug: str
    title: str
    pack: str
    library: str
    members: list = field(default_factory=list)   # [Place]
    set_id: str = ""
    note: str | None = None


@dataclass
class Place:
    """One occurrence of a brush: a member of a set row."""

    facts: dict
    container: str              # library path of the file
    container_sha256: str
    entry_prefix: str
    file: str = ""              # a loose member's file name, for its order
    row: SetRow | None = None
    position: int = 0


class CatalogBuild:
    """Reads every container of the library once (docs/CONTRACTS.md F5) and
    turns what it holds into the brush records, set rows and side files."""

    def __init__(self, paths, sources, rules):
        self.paths = paths
        self.library = Path(paths.library)
        self.sources = sources
        self.rules = rules
        self.registry = identity.Registry()
        bundled = self.library / BUNDLED_DIR
        self.bundled = bundled if bundled.is_dir() else None
        self.schema_keys = {row["key"] for row in brush_model.load_schema()["keys"]}
        self.user_packs = {pack["id"]: pack for pack in sources["packs"]}
        official = sources.get("official") if isinstance(sources.get("official"), dict) else {}
        self.official_packs = {pack["id"]: pack for pack in official.get("packs", [])
                               if isinstance(pack, dict) and identity.is_pack_id(pack.get("id"))}
        self.official_files = {}
        for entry in official.get("files", []):
            if isinstance(entry, dict) and identity.is_set_slug(entry.get("slug")):
                self.official_files[(entry.get("pack"), entry["slug"] + SET_SUFFIX)] = entry
        self.containers = {}        # sha256 -> summary (paths, bytes, pack, library, found, ...)
        self.parsed = {}            # sha256 -> [("set", SetRow) | ("brush", facts, prefix, file)]
        self.set_rows = []
        self.loose = {}             # pack -> [Place]
        self.textures = {}          # texture id -> {sha256, width, height, used_as}
        self.skipped = []           # (where, why)
        self.warnings = []          # (where, message)
        self.blockers = []
        self.other_files = []
        self.unknown_keys = {}      # key -> {brush ids}, eras
        self.files_read = 0

    # ── what goes wrong ──
    def skip(self, where, why):
        self.skipped.append((show(where), show(why)))

    def warn(self, where, message):
        self.warnings.append((show(where), show(message)))

    # ── packs and names ──
    def pack_of(self, rel):
        parts = rel.split("/")
        if len(parts) >= 3 and parts[0] == USER_DIR and parts[1] in self.user_packs:
            return parts[1]
        if len(parts) >= 3 and parts[0] == OFFICIAL_DIR and parts[1] in self.official_packs:
            return parts[1]
        matches = packs_for(rel, self.sources)
        if len(matches) > 1:
            self.blockers.append(f"{show(rel)} fits more than one pack ({', '.join(matches)}). Each "
                                 f"file must fit exactly one: fix the `match` patterns in {SOURCES_NAME}.")
        if matches:
            return matches[0]
        self.warn(rel, f"fits no pack in {SOURCES_NAME}; it is catalogued under the pack {UNSORTED}")
        return UNSORTED

    def library_of(self, pack):
        return OFFICIAL_DIR if pack in self.official_packs else USER_DIR

    def pack_kind(self, pack):
        if pack in self.official_packs:
            return "official"
        kind = self.user_packs.get(pack, {}).get("kind")
        return kind if kind in ("vendor", "mine") else "vendor"

    def product(self, pack):
        held = self.user_packs.get(pack) or self.official_packs.get(pack) or {}
        product = held.get("product")
        return product if isinstance(product, str) and product.strip() else pack

    def set_names(self, pack, name, rel):
        """(slug, title) of a real set: the manifest's, else made from its name."""
        if pack in self.official_packs:
            entry = self.official_files.get((pack, rel.rsplit("/", 1)[-1]))
            if entry is not None:
                title = entry.get("title")
                return entry["slug"], title if isinstance(title, str) and title else entry["slug"]
            self.warn(rel, f"is not among the official files of {SOURCES_NAME}; its slug is made "
                           "from its name")
        else:
            declared = self.user_packs.get(pack, {}).get("sets", {}).get(name)
            if isinstance(declared, dict) and identity.is_set_slug(declared.get("slug")):
                title = declared.get("title")
                return declared["slug"], (title if isinstance(title, str) and title
                                          else name.strip() or declared["slug"])
            if pack != UNSORTED:
                self.warn(rel, f"the set name {name!r} is not in the `sets` of pack {pack} in "
                               f"{SOURCES_NAME}; its slug is made from its name")
        slug = identity.slugify(name)
        return slug, name.strip() or slug

    # ── the walk ──
    def files(self):
        """(library path, path) of every file a build may read, in one order:
        `_docs/`, `bundled/`, junk, `*.part` and `.tmp` files left out."""
        found = []
        for folder, folders, names in os.walk(self.library):
            here = Path(folder)
            top = here == self.library
            folders[:] = sorted(name for name in folders
                                if name.lower() not in JUNK_FOLDERS and name != DOCS_DIR
                                and not (top and name == BUNDLED_DIR))
            for name in names:
                low = name.lower()
                if low in JUNK_NAMES or low == EMPTY or low.endswith((PART_SUFFIX, ".tmp")):
                    continue
                path = here / name
                found.append((path.relative_to(self.library).as_posix(), path))
        return sorted(found, key=lambda item: (item[0].lower(), item[0]))

    def run(self):
        for rel, path in self.files():
            if not rel.lower().endswith(CONTAINER_FILE_SUFFIXES):
                if rel.count("/") >= 2 and rel.split("/")[0] in LIBRARIES:
                    self.other_files.append(show(rel))
                continue
            if path.is_symlink() or not path.is_file():
                self.skip(rel, "not a regular file")
                continue
            self.read_file(rel, path)
        return self

    def read_file(self, rel, path):
        try:
            data = container.read_path(path)
        except LimitExceeded as exc:
            self.skip(rel, exc.detail or exc.code)
            return
        except OSError as exc:
            self.skip(rel, f"it cannot be read ({type(exc).__name__})")
            return
        if container.is_lfs_pointer(data):
            raise EnvironmentProblem(f"{show(rel)} is a Git LFS pointer, not the file. "
                                     "Run `git lfs pull` and try again.")
        self.files_read += 1
        sha = _sha(data)
        pack = self.pack_of(rel)
        if sha in self.containers:
            summary = self.containers[sha]
            summary["paths"].append(rel)
            for item in self.parsed.get(sha, []):
                if item[0] == "set":
                    self.warn(rel, f"is the same file as {summary['paths'][0]}; its set is "
                                   "catalogued once, from there")
                else:
                    _, facts, prefix, name = item
                    self.add_loose(pack, Place(facts, rel, sha, prefix, name))
            return
        summary = {"paths": [rel], "bytes": len(data), "pack": pack, "library": self.library_of(pack),
                   "found": [], "skipped": [], "warnings": []}
        self.containers[sha] = summary
        self.parsed[sha] = []
        try:
            found = container.read_any(data, rel)
        except ContainerError as exc:           # LimitExceeded among them
            if exc.code == "lfs_pointer":
                raise EnvironmentProblem(f"{show(rel)} is a Git LFS pointer. Run `git lfs pull`.") from None
            self.skip(rel, exc.detail or exc.code)
            summary["skipped"].append([show(rel), show(exc.detail or exc.code)])
            return
        for where, why in found.skipped:
            self.skip(where, why)
            summary["skipped"].append([show(where), show(why)])
        for item in found:
            nested = item.origin[len(rel) + 2:] + "!/" if item.origin.startswith(rel + "!/") else ""
            if isinstance(item, container.BrushSet):
                self.read_set(item, rel, sha, pack, nested, summary)
            else:
                facts = self.describe(item, item.origin)
                if facts is None:
                    continue
                name = item.origin.rsplit("!/", 1)[-1].rsplit("/", 1)[-1]
                self.parsed[sha].append(("brush", facts, nested, name))
                summary["found"].append({"kind": "brush", "entry_prefix": nested, "id": facts["id"]})
                self.add_loose(pack, Place(facts, rel, sha, nested, name))

    def read_set(self, item, rel, sha, pack, nested, summary):
        for message in item.warnings:
            self.warn(item.origin, message)
            summary["warnings"].append(show(message))
        for entry, why in item.skipped:
            self.skip(f"{item.origin} :: {entry}", why)
            summary["skipped"].append([show(f"{item.origin} :: {entry}"), show(why)])
        slug, title = self.set_names(pack, item.name, rel)
        row = SetRow("set", item.name, slug, title, pack, self.library_of(pack))
        for uuid, folder in item.brushes:
            prefix = f"{nested}{item.prefix}{uuid}/"
            facts = self.describe(folder, f"{item.origin}/{uuid}")
            if facts is None:
                continue
            row.members.append(Place(facts, rel, sha, prefix))
        self.set_rows.append(row)
        self.parsed[sha].append(("set", row))
        summary["found"].append({"kind": "set", "name": item.name, "set_slug": slug,
                                 "entry_prefix": nested + item.prefix,
                                 "brushes": [place.facts["id"] for place in row.members]})

    def add_loose(self, pack, place):
        self.loose.setdefault(pack, []).append(place)

    # ── one brush folder ──
    def texture(self, role, resolved, name, params, inverted_key):
        data, source = resolved
        texture_id = None
        if data is not None:
            texture_id = self.registry.texture(data)
            held = self.textures.get(texture_id)
            if held is None:
                header = _png_header(data)
                held = self.textures[texture_id] = {
                    "sha256": identity.texture_sha256(data),
                    "width": header["width"] if header else None,
                    "height": header["height"] if header else None,
                    "used_as": set()}
            held["used_as"].add(role)
        return {"source": source, "bundled_name": name, "texture_id": texture_id,
                "inverted": _flag(params, inverted_key)}

    def describe(self, folder, where):
        """The facts of one brush folder that its record is made of, or None
        (with a skip) when it cannot be catalogued. Holds no image bytes."""
        try:
            archive, shape, grain, subs = container.identity_inputs(folder)
        except ContainerError as exc:
            self.skip(where, exc.detail or exc.code)
            return None
        digest = identity.content_sha256(archive, shape, grain, subs)
        brush_id = self.registry.add(identity.brush_id_from_sha256(digest), digest)
        try:
            brush = brush_model.decode(archive)
        except (CodecError, RecursionError) as exc:
            code = getattr(exc, "code", type(exc).__name__)
            self.skip(where, f"its Brush.archive cannot be decoded ({code})")
            return None
        params = brush.params
        settings = brush_model.to_json(brush)["params"]
        warnings = [show(message) for message in folder.warnings]
        for entry, why in folder.skipped:
            self.skip(f"{where} :: {entry}", why)
        names = container.texture_names(params)
        resolved = container.resolve_textures(folder, params, bundled=self.bundled)
        shape_obj = self.texture("shape", resolved["shape"], names["shape"], params, "shapeInverted")
        grain_obj = self.texture("grain", resolved["grain"], names["grain"], params, "textureInverted")
        if folder.shape is not None and names["shape"] and resolved["shape"][1] == "embedded":
            warnings.append(f"Shape.png and bundledShapePath {names['shape']!r} are both present; "
                            "Shape.png is used")
        if folder.grain is not None and names["grain"] and resolved["grain"][1] == "embedded":
            warnings.append(f"Grain.png and bundledGrainPath {names['grain']!r} are both present; "
                            "Grain.png is used")
        era, exact, missing, extra = brush_model.detect_era(params)
        if not exact:
            warnings.append(f"the root keys match no era: {brush.era}, nearest "
                            f"{brush_model.nearest_era(params)} ({len(missing)} missing, {len(extra)} extra)")
        unknown = sorted(key for key in params if key not in self.schema_keys)
        for key in unknown:
            held = self.unknown_keys.setdefault(key, {"brushes": set(), "eras": set()})
            held["brushes"].add(brush_id)
            held["eras"].add(brush.era)
        if unknown:
            warnings.append(f"keys the schema lacks: {', '.join(unknown)}")
        thumbnail = folder.thumbnail
        if thumbnail is None:
            thumb = {"present": False, "sha256": None, "width": None, "height": None, "color_type": None}
        else:
            header = _png_header(thumbnail)
            if header is None:
                warnings.append("QuickLook/Thumbnail.png is not a readable PNG")
            thumb = {"present": True, "sha256": _sha(thumbnail),
                     "width": header["width"] if header else None,
                     "height": header["height"] if header else None,
                     "color_type": header["color_type"] if header else None}
        return {
            "id": brush_id, "content_sha256": digest, "where": where,
            "name": brush.name, "era": brush.era, "family": brush.family,
            "format": {"key_count": brush.key_count, "version": _code(params, "version"),
                       "ref_size": _ref_size(archive), "archive_bytes": len(archive),
                       "archive_sha256": _sha(archive), "classes": list(brush.root_class)},
            "shape": shape_obj, "grain": grain_obj, "thumbnail": thumb,
            "secondary": self.secondary(folder, where, warnings),
            "reset": self.reset(folder, archive, settings, where, warnings),
            "author": {"name": brush_model.text(params.get("authorName")),
                       "has_picture": folder.author_picture is not None,
                       "has_signature": folder.signature is not None,
                       "creation_date": _date_text(params.get("creationDate"))},
            "settings": settings,
            "warnings": warnings,
        }

    def secondary(self, folder, where, warnings):
        """The Sub01/ brush of a dual brush (never a brush of its own), or None."""
        sub = folder.sub
        if sub is None or sub.archive is None:
            return None
        sub_archive, sub_shape, sub_grain, _ = container.identity_inputs(sub)
        params = None
        out = {"name": None, "component_sha256": identity.content_sha256(sub_archive, sub_shape, sub_grain),
               "era": None, "settings": None}
        try:
            brush = brush_model.decode(sub_archive)
        except (CodecError, RecursionError) as exc:
            warnings.append(f"Sub01/Brush.archive cannot be decoded ({getattr(exc, 'code', type(exc).__name__)})")
        else:
            params = brush.params
            out.update(name=brush.name, era=brush.era, settings=brush_model.to_json(brush)["params"])
        names = (container.texture_names(params) if params is not None
                 else container.archive_texture_names(sub_archive))
        resolved = container.resolve_textures(sub, params, bundled=self.bundled)
        out["shape"] = self.texture("shape", resolved["shape"], names["shape"], params or {}, "shapeInverted")
        out["grain"] = self.texture("grain", resolved["grain"], names["grain"], params or {}, "textureInverted")
        return out

    def reset(self, folder, archive, settings, where, warnings):
        """What the Reset/ copy holds, compared with the live brush, or None."""
        reset = folder.reset
        if reset is None:
            return None
        held = reset.archive
        differing, same = [], None
        if held is not None:
            if held == archive:
                same = True
            else:
                try:
                    other = brush_model.to_json(brush_model.decode(held))["params"]
                except (CodecError, RecursionError) as exc:
                    warnings.append(f"Reset/Brush.archive cannot be decoded "
                                    f"({getattr(exc, 'code', type(exc).__name__)})")
                else:
                    differing = sorted(key for key in set(settings) | set(other)
                                       if settings.get(key, _ABSENT) != other.get(key, _ABSENT))
                    same = not differing
        thumbnail = reset.thumbnail
        return {"archive_sha256": _sha(held) if held is not None else None, "same_as_live": same,
                "differing_keys": differing[:DIFFERING_KEYS_MAX], "differing_count": len(differing),
                "has_secondary": SUB_ARCHIVE in reset,
                "thumbnail_sha256": _sha(thumbnail) if thumbnail is not None else None}

    # ── sets, homes and records ──
    def loose_rows(self):
        for pack in sorted(self.loose):
            places = sorted(self.loose[pack], key=lambda place: (place.file.lower(), place.file,
                                                                place.container, place.entry_prefix))
            slug = identity.loose_set_slug(pack)
            row = SetRow("loose", slug, slug, f"{self.product(pack)} (loose brushes)", pack,
                         self.library_of(pack), places)
            self.set_rows.append(row)

    def note_path(self, row):
        if row.library == OFFICIAL_DIR:
            folder = NOTE_FOLDER["official"]
        elif self.pack_kind(row.pack) == "mine":
            folder = NOTE_FOLDER["mine"]
        elif row.kind == "loose":
            folder = NOTE_FOLDER["loose"]
        else:
            folder = NOTE_FOLDER["other"]
        return f"{folder}/{row.slug}.md"

    def assemble(self, thumbnails, textures_held):
        """(records by id, set rows, texture records): the catalog in memory."""
        self.loose_rows()
        by_slug = {}
        for row in self.set_rows:
            if row.slug in by_slug:
                self.blockers.append(
                    f"two sets have the slug {row.slug!r} ({by_slug[row.slug].pack}: "
                    f"{show(by_slug[row.slug].name)!r} and {row.pack}: {show(row.name)!r}). Give one of "
                    f"them its own slug under `sets` in {SOURCES_NAME}.")
                continue
            by_slug[row.slug] = row
        if self.blockers:
            return None
        rows = sorted(by_slug.values(), key=lambda row: row.slug)
        places = {}
        for row in rows:
            for position, place in enumerate(row.members, start=1):
                place.row, place.position = row, position
                places.setdefault(place.facts["id"], []).append(place)
            row.set_id = self.registry.set(row.name, [place.facts["id"] for place in row.members])

        def home_key(place):
            return (place.row.kind != "set", place.row.pack, place.row.slug, place.position,
                    place.container, place.entry_prefix)

        records = {}
        for brush_id in sorted(places):
            occurring = sorted(places[brush_id], key=home_key)
            home, facts = occurring[0], occurring[0].facts
            warnings = list(facts["warnings"])
            for place in occurring[1:]:
                if place.facts["thumbnail"]["sha256"] != facts["thumbnail"]["sha256"]:
                    warnings.append(f"the copy in {place.row.slug} #{place.position} carries another "
                                    "thumbnail; the record describes the home copy")
                if place.facts["reset"] != facts["reset"]:
                    warnings.append(f"the copy in {place.row.slug} #{place.position} carries another "
                                    "Reset/ folder; the record describes the home copy")
            display = facts["name"].strip() or "Untitled"
            record = {
                "schema": BRUSH_SCHEMA, "id": brush_id, "content_sha256": facts["content_sha256"],
                "name": facts["name"], "display_name": display, "slug": identity.slugify(display),
                "library": home.row.library, "pack": home.row.pack,
                "family": facts["family"], "era": facts["era"], "format": facts["format"],
                "home": {"set_slug": home.row.slug, "position": home.position},
                "occurrences": [{"set_slug": place.row.slug, "set_id": place.row.set_id,
                                 "position": place.position, "pack": place.row.pack,
                                 "container": place.container,
                                 "container_sha256": place.container_sha256,
                                 "entry_prefix": place.entry_prefix} for place in occurring],
                "shape": facts["shape"], "grain": facts["grain"], "thumbnail": facts["thumbnail"],
                "secondary": facts["secondary"], "reset": facts["reset"], "author": facts["author"],
                "settings": facts["settings"],
                "facets": {}, "facet_words": [], "preview": {},
                "warnings": sorted(set(warnings)),
            }
            records[brush_id] = finish_record(record, thumbnails, textures_held, self.rules)
        homes = {record["home"]["set_slug"] for record in records.values()}
        set_records = []
        for row in rows:
            row.note = self.note_path(row) if row.slug in homes else None
            set_records.append({
                "set_slug": row.slug, "set_id": row.set_id, "name": row.name, "title": row.title,
                "kind": row.kind, "library": row.library, "pack": row.pack,
                "pack_kind": self.pack_kind(row.pack), "brush_count": len(row.members),
                "note": row.note, "brushes": [place.facts["id"] for place in row.members]})
        texture_records = {}
        for texture_id in sorted(self.textures):
            held = self.textures[texture_id]
            before = textures_held.get(texture_id) if isinstance(textures_held.get(texture_id), dict) else {}
            tiles = before.get("shape_tiles")
            texture_records[texture_id] = {
                "sha256": held["sha256"], "width": held["width"], "height": held["height"],
                "used_as": sorted(held["used_as"]),
                "shape_tiles": tiles if isinstance(tiles, dict) else {"n": None, "i": None},
                "grain_tile": before.get("grain_tile"),
                "stats": before.get("stats")}
        return records, set_records, texture_records

    def pack_rows(self, used):
        """The manifest fields of every pack (and `unsorted` when it is used)."""
        rows = []
        for pack, library in ([(pack, USER_DIR) for pack in self.user_packs.values()]
                              + [(pack, OFFICIAL_DIR) for pack in self.official_packs.values()]):
            row = {name: pack.get(name) for name in PACK_FIELDS}
            row["library"] = library
            rows.append(row)
        if UNSORTED in used:
            rows.append({**dict.fromkeys(PACK_FIELDS), "id": UNSORTED, "kind": "vendor",
                         "redistribute": "unknown", "library": USER_DIR})
        return rows

    def report(self, records, set_records, texture_records):
        """ingest_report.json: counts, duplicates, skipped files, warnings, keys
        the schema lacks (docs/CONTRACTS.md F5)."""
        duplicates = []
        for record in records.values():
            if len(record["occurrences"]) > 1:
                duplicates.append({"id": record["id"], "name": record["name"],
                                   "home": record["home"]["set_slug"],
                                   "occurrences": [f"{place['set_slug']}#{place['position']}"
                                                   for place in record["occurrences"]]})
        collisions = []
        for row in set_records:
            named = {}
            for brush_id in row["brushes"]:
                named.setdefault(records[brush_id]["name"], [])
                if brush_id not in named[records[brush_id]["name"]]:
                    named[records[brush_id]["name"]].append(brush_id)
            collisions += [{"set_slug": row["set_slug"], "name": name, "ids": ids}
                           for name, ids in sorted(named.items()) if len(ids) > 1]
        bundled = {"shape": {}, "grain": {}}
        for record in records.values():
            for role in ("shape", "grain"):
                texture = record[role]
                if texture["source"] in ("bundled", "blank") and texture["bundled_name"]:
                    counts = bundled[role]
                    counts[texture["bundled_name"]] = counts.get(texture["bundled_name"], 0) + 1
        unknown_eras = [{"id": record["id"], "name": record["name"], "era": record["era"],
                         "nearest": brush_model.nearest_era(record["settings"])}
                        for record in records.values() if record["era"].startswith("X")]
        counted = lambda key, value: sum(1 for r in records.values() if r[key] == value)  # noqa: E731
        return {
            "schema": REPORT_SCHEMA,
            "ingest_version": INGEST_VERSION,
            "facet_rules_version": self.rules["facet_rules_version"],
            "counts": {
                "files_read": self.files_read,
                "containers": len(self.containers),
                "container_copies": sum(len(entry["paths"]) - 1 for entry in self.containers.values()),
                "occurrences": sum(len(r["occurrences"]) for r in records.values()),
                "brushes": len(records),
                "by_library": {library: counted("library", library) for library in LIBRARIES},
                "sets": len(set_records),
                "loose_sets": sum(1 for row in set_records if row["kind"] == "loose"),
                "notes": sum(1 for row in set_records if row["note"]),
                "textures": len(texture_records),
                "duplicates": len(duplicates),
                "dual": sum(1 for r in records.values() if r["secondary"] is not None),
                "with_reset": sum(1 for r in records.values() if r["reset"] is not None),
                "no_thumbnail": sum(1 for r in records.values() if not r["thumbnail"]["present"]),
                "bundled_only": {role: sum(bundled[role].values()) for role in bundled},
                "skipped": len(self.skipped),
                "warnings": len(self.warnings) + sum(len(r["warnings"]) for r in records.values()),
            },
            "duplicates": sorted(duplicates, key=lambda row: row["id"]),
            "name_collisions": collisions,
            "skipped": [{"where": where, "why": why} for where, why in sorted(set(self.skipped))],
            "warnings": ([{"where": where, "message": message}
                          for where, message in sorted(set(self.warnings))]
                         + [{"where": record["id"], "message": message}
                            for record in sorted(records.values(), key=lambda r: r["id"])
                            for message in record["warnings"]]),
            "unknown_keys": {key: {"brushes": len(held["brushes"]), "eras": sorted(held["eras"])}
                             for key, held in sorted(self.unknown_keys.items())},
            "unknown_eras": sorted(unknown_eras, key=lambda row: row["id"]),
            "bundled_textures": {role: dict(sorted(names.items())) for role, names in bundled.items()},
            "other_files": sorted(self.other_files),
        }

    def container_records(self):
        out = {}
        for sha, summary in sorted(self.containers.items()):
            out[sha] = {"paths": sorted(summary["paths"], key=lambda p: (p.lower(), p)),
                        "bytes": summary["bytes"], "pack": summary["pack"],
                        "library": summary["library"], "found": summary["found"],
                        "skipped": sorted(summary["skipped"]),
                        "warnings": sorted(set(summary["warnings"]))}
        return out


# ── build and report ─────────────────────────────────────────────────────────

def _selected(records, set_records, only):
    """The brush ids and set slugs that `--only S` writes: S is a set slug or a pack id."""
    sets = {row["set_slug"] for row in set_records if only in (row["set_slug"], row["pack"])}
    if not sets:
        raise EnvironmentProblem(f"--only {only}: no set slug or pack id of the library is {only!r}")
    ids = {record["id"] for record in records.values()
           if any(place["set_slug"] in sets for place in record["occurrences"])}
    return ids, sets


def run_build(paths, *, only=None, strict=False):
    """Read the library and write the catalog (docs/CONTRACTS.md F5). Needs no
    --confirm: the catalog is generated and rebuildable. The same library gives
    the same bytes."""
    library = Path(paths.library)
    if not library.is_dir():
        raise EnvironmentProblem(f"there is no library folder at {library}")
    sources = load_sources(library)
    rules = load_facet_rules()
    catalog, brushes_dir, sets_dir = _catalog_paths(paths)
    try:
        catalog.resolve().relative_to(library.resolve())
    except ValueError:
        pass
    else:
        raise EnvironmentProblem(f"the catalog {catalog} lies inside the library {library}")
    build = CatalogBuild(paths, sources, rules)
    try:
        build.run()
        thumbnails = _read_json(catalog / THUMBNAILS_NAME, None)
        textures_held = _read_map(catalog / TEXTURES_NAME)
        assembled = build.assemble(thumbnails if isinstance(thumbnails, dict) else {}, textures_held)
    except identity.PrefixCollision as exc:
        raise IngestError(str(exc)) from None
    if build.blockers or assembled is None:
        print("REFUSED   nothing was written.")
        for entry in build.blockers:
            print(f"  {entry}")
        return bc.EXIT_REFUSED
    records, set_records, texture_records = assembled
    report = build.report(records, set_records, texture_records)
    counts = report["counts"]
    print(f"BUILD     {library}  ->  {catalog}")
    print(f"READ      {counts['files_read']} files, {counts['containers']} containers "
          f"({counts['container_copies']} copies), {counts['skipped']} skipped")
    print(f"FOUND     {counts['brushes']:,} brushes in {counts['occurrences']:,} places "
          f"(user {counts['by_library']['user']}, official {counts['by_library']['official']}); "
          f"{counts['sets']} sets ({counts['loose_sets']} loose), {counts['notes']} notes; "
          f"{counts['textures']} textures")
    if build.skipped:
        print("SKIPPED   read as far as it was safe, and left out")
        for where, why in sorted(set(build.skipped)):
            print(f"  {where}: {why}")
    if strict and build.skipped:
        print("REFUSED   --strict: something was skipped, so nothing was written.")
        return bc.EXIT_REFUSED

    wanted_ids = wanted_sets = None
    if only is not None:
        wanted_ids, wanted_sets = _selected(records, set_records, only)
    written = removed = 0
    brushes_dir.mkdir(parents=True, exist_ok=True)
    sets_dir.mkdir(parents=True, exist_ok=True)
    for brush_id, record in records.items():
        if wanted_ids is None or brush_id in wanted_ids:
            written += _write_if_changed(brushes_dir / f"{brush_id}.json", record)
    for row in set_records:
        if wanted_sets is None or row["set_slug"] in wanted_sets:
            written += _write_if_changed(sets_dir / f"{row['set_slug']}.json", row)
    if only is None:
        keep = {f"{brush_id}.json" for brush_id in records}
        for path in sorted(brushes_dir.glob("*.json")):
            if path.name not in keep:
                path.unlink()
                removed += 1
        keep = {f"{row['set_slug']}.json" for row in set_records}
        for path in sorted(sets_dir.glob("*.json")):
            if path.name not in keep:
                path.unlink()
                removed += 1
    written += _write_if_changed(catalog / TEXTURES_NAME, texture_records)
    written += _write_if_changed(catalog / CONTAINERS_NAME, build.container_records())
    written += _write_if_changed(catalog / REPORT_NAME, report)
    if not isinstance(thumbnails, dict):
        written += _write_if_changed(catalog / THUMBNAILS_NAME, {})
    before = bc.read_text(catalog / CATALOG_NAME) if (catalog / CATALOG_NAME).is_file() else None
    written += apply_preview_results(paths, build.pack_rows({row["pack"] for row in set_records}))
    written += bc.read_text(catalog / CATALOG_NAME) != before
    print(f"WROTE     {written} files changed, {removed} removed"
          + (f" (--only {only}: {len(wanted_ids)} brush records, {len(wanted_sets)} sets)"
             if only is not None else ""))
    if counts["warnings"]:
        print(f"WARNINGS  {counts['warnings']}; `ingest.py report` lists them")
    return bc.EXIT_OK


def _distribution(values):
    counts = {}
    for value in values:
        key = "null" if value is None else str(value).lower() if isinstance(value, bool) else str(value)
        counts[key] = counts.get(key, 0) + 1
    return ", ".join(f"{key} {count}" for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def run_report(paths):
    """Print what the catalog holds and what the last build met. Writes nothing."""
    catalog = Path(paths.catalog)
    index = _read_json(catalog / CATALOG_NAME)
    report = _read_json(catalog / REPORT_NAME)
    if not isinstance(index, dict) or not isinstance(report, dict):
        raise EnvironmentProblem(f"there is no catalog at {catalog}; run `ingest.py build` first")
    counts = index["counts"]
    rows = index["brushes"]
    sets = index["sets"]
    print(f"CATALOG   {catalog}   {index['library_fingerprint']}   ingest {index['ingest_version']}, "
          f"facet rules {index['facet_rules_version']}")
    print(f"brushes   {counts['brushes']:,} (user {counts['by_library']['user']:,}, official "
          f"{counts['by_library']['official']:,}) in {counts['occurrences']:,} places; "
          f"{counts['textures']:,} textures")
    print(f"sets      {counts['sets']} ({sum(1 for s in sets if s['kind'] == 'set')} brushsets, "
          f"{sum(1 for s in sets if s['kind'] == 'loose')} loose); {counts['notes']} notes; "
          f"{counts['packs']} packs")
    print(f"eras      {_distribution(row['era'] for row in rows)}")
    print(f"families  {_distribution(row['family'] for row in rows)}")
    rules = load_facet_rules()
    print("facets")
    for name in rules["facets"]:
        values = [row["facets"].get(name) for row in rows]
        if all(value is None or isinstance(value, (str, bool)) for value in values):
            print(f"  {name:<24} {_distribution(values)}")
        else:
            numbers = [value for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
            nulls = sum(1 for value in values if value is None)
            span = f"{min(numbers)} to {max(numbers)}" if numbers else "none"
            print(f"  {name:<24} {len(numbers)} values, {span}; null {nulls}")
    built = report["counts"]
    print(f"build     {built['files_read']} files, {built['containers']} containers, "
          f"{built['duplicates']} brush ids in more than one place, {built['dual']} dual, "
          f"{built['with_reset']} with Reset/, {built['no_thumbnail']} without a thumbnail")
    print(f"bundled   shape {built['bundled_only']['shape']}, grain {built['bundled_only']['grain']} "
          "brushes name an image that ships inside the app")
    for title, entries in (("SKIPPED", [f"{e['where']}: {e['why']}" for e in report["skipped"]]),
                           ("UNKNOWN KEYS", [f"{k}: {v['brushes']} brushes, {', '.join(v['eras'])}"
                                             for k, v in report["unknown_keys"].items()]),
                           ("UNKNOWN ERAS", [f"{e['id']} {e['name']!r}: {e['era']}, nearest {e['nearest']}"
                                             for e in report["unknown_eras"]]),
                           ("NAME COLLISIONS", [f"{e['set_slug']}: {e['name']!r} x{len(e['ids'])}"
                                                for e in report["name_collisions"]]),
                           ("WARNINGS", [f"{e['where']}: {e['message']}" for e in report["warnings"]])):
        if entries:
            print(f"{title} ({len(entries)})")
            for entry in entries:
                print(f"  {show(entry)}")
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
    verbs = parser.add_subparsers(dest="verb", metavar="{where,adopt,build,report,census}", required=True)
    where = verbs.add_parser("where", help="print the folders the brushes scripts work on")
    adopt = verbs.add_parser("adopt", help="copy the brush files under SRC into library/user/ "
                                           "(a dry run without --confirm)")
    adopt.add_argument("src", metavar="SRC", help="a folder, or one file, to look for brush files in")
    adopt.add_argument("--with-docs", action="store_true",
                       help="also copy documents, images and artwork into an ignored _docs/ folder")
    adopt.add_argument("--confirm", action="store_true", help="really copy")
    build = verbs.add_parser("build", help="read the library and write the catalog (generated and "
                                           "rebuildable: no --confirm)")
    build.add_argument("--only", metavar="S", help="write the brush and set records of one set slug "
                                                   "or pack id; the whole library is still read")
    build.add_argument("--strict", action="store_true",
                       help="exit 1 and write nothing when anything had to be skipped")
    report = verbs.add_parser("report", help="print what the catalog holds and what the last build "
                                             "met; writes nothing")
    census = verbs.add_parser("census", help="count what the library's archives hold; writes nothing")
    census.add_argument("--json", action="store_true",
                        help="print the whole census and its schema columns as JSON")
    for sub in (where, adopt, build, report, census):
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
        if args.verb == "census":
            return run_census(paths, as_json=args.json)
        if args.verb == "build":
            return run_build(paths, only=args.only, strict=args.strict)
        if args.verb == "report":
            return run_report(paths)
        return run_adopt(paths, args.src, with_docs=args.with_docs, confirm=args.confirm,
                         disk_free=disk_free)
    except IngestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
