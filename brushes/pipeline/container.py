"""Brush files as containers: `.brush` and `.brushset` zips, read and written in memory.

    found = container.read_any(data, "Pack.zip")      # every set and brush in it, nested or not
    brush_set = container.read_brushset(data)         # BrushSet(name, brushes, ...)
    folder = container.read_brush(data)               # BrushFolder: members and their views
    textures = container.resolve_textures(folder, params)
    data = container.write_brushset(brush_set)        # through zip_writer.write_zip

This is the container layer of the file codec (docs/CONTRACTS.md, F3
"Containers"). It knows zips, folders and the set's plist; the archive inside a
folder is keyed_archive's and brush_model's.

A brush folder is its members. `BrushFolder.members` is the ordered list of
everything the folder held, as `Member(path, data, date_time, form)`: the path
inside the folder, the bytes, and how the source zip stored it (its date and
its zip_writer form), so that a member written back unchanged is written back
the way it came. Typed views read that list and never hold a copy of their own:

    archive          Brush.archive
    shape, grain     Shape.png, Grain.png
    thumbnail        QuickLook/Thumbnail.png
    author_picture   AuthorPicture/AuthorPicture.png
    signature        Signature/SignaturePicture.png
    sub              the folder Sub01/, as a BrushFolder (None without one)
    reset            the folder Reset/, as a BrushFolder (its own Sub01/ inside)
    extras           [(path, bytes)] of every member no view above claims: a
                     zero-byte `.empty`, a texture kept under its own name, a
                     Sub02/, a file nobody knows

A set is `BrushSet`: its name, its brushes as [(folder name, BrushFolder)] in
the order of the plist's `brushes` array, the entry order of the zip it was
read from, where it was found, and the plist's other keys (`plist_extra`, such
as `iconName`), kept in the order the plist held them (`plist_order`).

Reading (F3 "Reading"):

  - A zip is opened over the bytes in memory. Nothing is extracted, and no
    entry name is ever used as a path.
  - It is sniffed by content: a root `brushset.plist` is a set, a root
    `Brush.archive` a brush, one shared top folder holding `brushset.plist` a
    set. `read_any` searches anything else for entries ending `.brush`,
    `.brushset`, `.brushset.zip` or `.zip`, to a nesting depth of 3.
  - Junk is part of no folder: an entry under `__MACOSX/`, one named
    `.DS_Store`, `Thumbs.db` or `desktop.ini` (any case), and a folder entry.
    A name met a second time is dropped with a warning: the first wins.
  - Inside a brush folder every other entry is a member, kept in source order
    and written back. A member no view claims raises an unknown-member warning,
    unless it is a `.empty` or the texture the folder's archive names.
  - Refused, and reported as skipped, the container read on: an encrypted
    entry; a name that is absolute or holds `..` or a backslash (tested on the
    name as stored, `orig_filename`, which zipfile does not rewrite).
  - A file at the root of a set that is not `brushset.plist` belongs to no
    folder: it is reported as skipped and not written back. So is a folder that
    holds no `Brush.archive`.
  - The plist's `brushes` array is the only brush order; a folder it does not
    list is kept, after the listed ones, with a warning.
  - A Git LFS pointer is ContainerError("lfs_pointer"): run git lfs pull.

Caps (F3; spec.yaml `format.caps`): CAPS below, by the same names. Exceeding one
raises LimitExceeded, whose `code` is the cap's name. The archive cap also
covers `brushset.plist`, which is read before anything is known about it.

Texture resolution (F3), the one place it is done: `resolve_textures(folder,
params)` gives each of shape and grain as (bytes or None, source): the folder's
`Shape.png` (`Grain.png`); else the member named exactly by `bundledShapePath`
(`bundledGrainPath`), a name with no `/` in it; else, for a grain, the name
`Brush-Preset-Blank.png` is `blank`; else the file of that exact name in the
library's `bundled/` folder, when the caller gives one (`bundled-supplied`);
else the name only, for an image inside the drawing app (`bundled`). No name
and no image is `none`. Without `params`, the names are read from the folder's
own archive.

Identity is identity.py's, and this module has no id function. It gives the
inputs F1 hashes, `identity_inputs(folder)`: the archive; the shape and grain
the folder itself carries (the first two steps above, never a bundled file);
and the same three for every `SubNN/` holding a `Brush.archive`, in ascending
order of folder name, Sub02/ and beyond included.

Writing (F3 "Writing"): `write_brush` and `write_brushset` give the bytes of a
zip made by zip_writer.write_zip, the one writer. Every member is written back
byte for byte, in the zip_writer form it was read in, with the date given
(`mtime`, a fixed constant by default) or, with `source_dates`, the date it was
read with. A member made here is written in zip_writer's default form. The
entry order is the canonical one (`Brush.archive`, `Shape.png`, `Grain.png`,
`QuickLook/Thumbnail.png`, `AuthorPicture/...`, `Signature/...`, `Sub01/...`,
`Reset/...`, then other members sorted; a set's plist last), or with
`preserve_order` the order the source zip held. A set whose name, brushes and
plist keys are what was read writes its plist's source bytes; any other set
gets a plist written by plistlib (XML, UTF-8, tabs, keys in the order read).
`member_plan` says what an export did to each member: `verbatim`,
`re-encoded`, `replaced` or `dropped`, and a drop nobody asked for is an error.

What stands behind it. Each of the 112 files of the library was read here and
written again with `preserve_order` and `source_dates` (zlib 1.3.1): 111 came
back byte for byte. The other, Chinese Calligraphy, holds every `.empty` twice,
first stored and then deflated; the reader keeps the first, so the rebuilt file
lacks the 84 later copies, and each of its 193 other entries has the source's
local and central record byte for byte. The 61 plists are what plistlib writes
for their keys. Nothing written here has been opened in the drawing app.

Errors: ContainerError(code, detail) and LimitExceeded(code, detail), both
from bplist.py. Codes of ContainerError: lfs_pointer, not_a_zip, not_a_brush,
not_a_brushset, bad_plist, encrypted, hostile_name, unreadable, bad_member,
bad_folder, no_archive, unrequested_drop, write. The code of LimitExceeded is
the cap's name (a zip nested past the depth cap is `nesting_depth`).

Standard library only. Not a command.
"""

from __future__ import annotations

import copy
import io
import os
import plistlib
import re
import uuid as _uuid
import zipfile
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import bplist
import identity
import keyed_archive
import zip_writer
from bplist import CodecError, ContainerError, LimitExceeded

__all__ = ["ARCHIVE", "AUTHOR_PICTURE", "BLANK_GRAIN", "Budget", "BrushFolder", "BrushSet",
           "CAPS", "ContainerError", "DEFAULT_LIMITS", "EMPTY", "Found", "GRAIN", "JUNK_FOLDERS",
           "JUNK_NAMES", "LFS_HEADER", "LimitExceeded", "Listing", "Member", "NESTED_SUFFIXES",
           "RESET", "SET_PLIST", "SHAPE", "SIGNATURE", "STATES", "SUB", "SUB_FOLDER", "THUMBNAIL",
           "ZIP_EPOCH", "ZIP_ERRORS", "ZIP_MAGIC", "archive_texture_names", "canonical_order",
           "check_declared", "hostile", "identity_inputs", "is_junk", "is_lfs_pointer",
           "list_entries", "member_plan", "new_uuid", "parse_plist", "plist_bytes", "ratio_bomb",
           "read_any", "read_brush", "read_brushset", "read_member", "read_path", "render_plist",
           "resolve_textures", "safe_filename", "shown_name", "sniff", "texture_names",
           "write_brush", "write_brushset"]

MIB = 1024 * 1024
# The reader's caps (docs/CONTRACTS.md F3; spec.yaml format.caps), by the same names.
CAPS = {
    "zip_entries": 5000,                 # entries in one container
    "archive_bytes": MIB,                # one Brush.archive (and one brushset.plist)
    "entry_bytes": 64 * MIB,             # one inflated entry
    "total_bytes": 2048 * MIB,           # one container, inflated
    "ratio": 200,                        # an entry inflating more than 200:1 ...
    "ratio_min_bytes": 16 * MIB,         # ... and larger than this is refused
    "nesting_depth": 3,
    "upload_bytes": 512 * MIB,           # one container file, on disk or nested
}
DEFAULT_LIMITS = CAPS

# The date a zip made here gives its entries unless told otherwise.
ZIP_EPOCH = zip_writer.DEFAULT_DATE_TIME

SET_PLIST = "brushset.plist"
ARCHIVE = "Brush.archive"
SHAPE = "Shape.png"
GRAIN = "Grain.png"
THUMBNAIL = "QuickLook/Thumbnail.png"
AUTHOR_PICTURE = "AuthorPicture/AuthorPicture.png"
SIGNATURE = "Signature/SignaturePicture.png"
SUB = "Sub01"
RESET = "Reset"
AUTHOR_FOLDER = "AuthorPicture/"
SIGNATURE_FOLDER = "Signature/"
BLANK_GRAIN = "Brush-Preset-Blank.png"
SHAPE_KEY = "bundledShapePath"
GRAIN_KEY = "bundledGrainPath"

# Junk: part of no brush folder, wherever it sits (F3 "Reading"). ingest.py
# takes these from here; device_tests.py spells the same two sets.
JUNK_FOLDERS = frozenset({"__macosx"})
JUNK_NAMES = frozenset({".ds_store", "thumbs.db", "desktop.ini"})
# A zero-byte placeholder some official sets carry: a member like any other,
# except that it raises no unknown-member warning, never enters identity, and
# never decides what a container is.
EMPTY = ".empty"

NESTED_SUFFIXES = (".brush", ".brushset", ".zip")          # `.brushset.zip` ends in `.zip`
ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
SUB_FOLDER = re.compile(r"Sub[0-9]+")
STATES = ("verbatim", "re-encoded", "replaced", "dropped")
PLIST_KEYS = ("brushes", "name")

# What zipfile and zlib raise on a file that is not what it claims to be.
ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, zlib.error, EOFError, OSError,
              RuntimeError, NotImplementedError, ValueError, OverflowError, MemoryError)


# ── small rules ──────────────────────────────────────────────────────────────

def is_lfs_pointer(data):
    """True for the text Git LFS leaves where a file should be."""
    return bytes(data[:len(LFS_HEADER)]) == LFS_HEADER


def is_junk(name):
    """True for an entry that is part of no folder: under `__MACOSX/`, or named
    `.DS_Store`, `Thumbs.db` or `desktop.ini`, compared without regard to case."""
    parts = name.lower().split("/")
    return parts[-1] in JUNK_NAMES or any(part in JUNK_FOLDERS for part in parts[:-1])


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


def _last(name):
    return name.rsplit("/", 1)[-1]


def sniff(names):
    """("set" | "brush" | "other", prefix) from a zip's entry names alone. A
    `.empty` placeholder never decides: it is left out of the one-top-folder test."""
    if SET_PLIST in names:
        return "set", ""
    if ARCHIVE in names:
        return "brush", ""
    real = [name for name in names if _last(name).lower() != EMPTY]
    tops = {name.split("/", 1)[0] for name in real}
    if len(tops) == 1 and all("/" in name for name in real):
        prefix = next(iter(tops)) + "/"
        if prefix + SET_PLIST in names:
            return "set", prefix
    return "other", ""


def new_uuid():
    """A fresh folder name: an upper-case version-4 UUID."""
    return str(_uuid.uuid4()).upper()


def safe_filename(name):
    """The ASCII slug a file made from `name` is called by (F10: `<ascii-slug>.<ext>`):
    identity.slugify, with `untitled` for a name that leaves nothing."""
    return identity.slugify(name if isinstance(name, str) else "", identity.SLUG_FALLBACK)


# ── caps ─────────────────────────────────────────────────────────────────────

@dataclass
class Listing:
    """The entries of a zip that count, and what was left out of them."""

    kept: list                       # ZipInfo, first of each name, in zip order
    duplicates: list                 # names met again and dropped
    junk: list                       # names of junk entries
    folders: list                    # names of folder entries


def list_entries(infos, *, limits=None):
    """Split a zip's infolist into what counts and what does not: files only,
    the first of a repeated name, and no junk. Raises LimitExceeded when the
    zip holds more entries than the cap."""
    limits = CAPS if limits is None else limits
    infos = list(infos)
    if len(infos) > limits["zip_entries"]:
        raise LimitExceeded("zip_entries", f"{len(infos):,} entries; the cap is "
                                           f"{limits['zip_entries']:,}")
    listing = Listing([], [], [], [])
    seen = set()
    for info in infos:
        name = info.orig_filename
        if name.endswith("/"):
            listing.folders.append(name)
        elif is_junk(name):
            listing.junk.append(name)
        elif name in seen:
            listing.duplicates.append(name)
        else:
            seen.add(name)
            listing.kept.append(info)
    return listing


def ratio_bomb(info, *, limits=None):
    """True for an entry whose directory says it inflates more than the ratio
    cap and is larger than the size above which that counts."""
    limits = CAPS if limits is None else limits
    return (info.file_size > limits["ratio_min_bytes"]
            and info.file_size > info.compress_size * limits["ratio"])


def check_declared(infos, *, limits=None):
    """Refuse a container whose own directory already breaks the caps."""
    limits = CAPS if limits is None else limits
    total = 0
    for info in infos:
        size = info.file_size
        if _last(info.orig_filename) == ARCHIVE and size > limits["archive_bytes"]:
            raise LimitExceeded("archive_bytes", f"a Brush.archive of {size:,} bytes; "
                                                 f"the cap is {limits['archive_bytes']:,}")
        if size > limits["entry_bytes"]:
            raise LimitExceeded("entry_bytes", f"an entry of {size:,} bytes; the cap is "
                                               f"{limits['entry_bytes']:,}")
        if ratio_bomb(info, limits=limits):
            raise LimitExceeded("ratio", f"an entry that inflates more than {limits['ratio']}:1")
        total += size
    if total > limits["total_bytes"]:
        raise LimitExceeded("total_bytes", f"{total:,} bytes inflated; the cap is "
                                           f"{limits['total_bytes']:,}")


class Budget:
    """How many bytes may still be inflated out of one file on disk."""

    def __init__(self, limit=None):
        self.cap = CAPS["total_bytes"] if limit is None else limit
        self.left = self.cap

    def spend(self, size):
        if size > self.left:
            raise LimitExceeded("total_bytes", f"more than {self.cap:,} bytes would be inflated "
                                               "from one file")
        self.left -= size


def read_member(archive, info, cap, budget=None, *, cap_name="entry_bytes", limits=None):
    """One entry's bytes, in memory. Never more than `cap` bytes: the size the
    directory gives is checked first, and the stream is cut one byte past it."""
    limits = CAPS if limits is None else limits
    if info.flag_bits & 0x1:
        raise ContainerError("encrypted", "an encrypted entry")
    if info.file_size > cap:
        raise LimitExceeded(cap_name, f"{info.file_size:,} bytes inflated; the cap is {cap:,}")
    if ratio_bomb(info, limits=limits):
        raise LimitExceeded("ratio", f"it inflates more than {limits['ratio']}:1")
    if budget is not None:
        budget.spend(info.file_size)
    try:
        with archive.open(info) as handle:
            data = handle.read(cap + 1)
    except ZIP_ERRORS as exc:
        raise ContainerError("unreadable", f"it cannot be read ({type(exc).__name__}: {exc})") from None
    if len(data) > cap:
        raise LimitExceeded(cap_name, f"more than {cap:,} bytes inflated")
    return data


# ── members and folders ──────────────────────────────────────────────────────

@dataclass(eq=False)
class Member:
    """One member of a brush folder.

    path        its path inside the folder, `/` between parts, exactly as stored
    data        its bytes
    date_time   the date the source zip gave it, or None for a member made here
    form        the zip_writer form it was stored in, or None (the default form)
    """

    path: str
    data: bytes
    date_time: tuple | None = None
    form: str | None = None


def _member(item):
    if isinstance(item, Member):
        return item
    try:
        path, data = item[0], item[1]
    except (TypeError, IndexError, KeyError):
        raise ContainerError("bad_member", "a member is (path, bytes)") from None
    if not isinstance(path, str) or not path:
        raise ContainerError("bad_member", f"a member's path is text, not {path!r}")
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise ContainerError("bad_member", f"the data of {path!r} must be bytes")
    return Member(path, bytes(data), *item[2:4])


def _rank(path):
    """The canonical write order of a member path (F3 "Writing")."""
    if path == ARCHIVE:
        return (0,)
    if path == SHAPE:
        return (1,)
    if path == GRAIN:
        return (2,)
    if path == THUMBNAIL:
        return (3,)
    if path.startswith(AUTHOR_FOLDER):
        return (4, 0 if path == AUTHOR_PICTURE else 1, path)
    if path.startswith(SIGNATURE_FOLDER):
        return (5, 0 if path == SIGNATURE else 1, path)
    if path.startswith(SUB + "/"):
        return (6,) + _rank(path[len(SUB) + 1:])
    if path.startswith(RESET + "/"):
        return (7,) + _rank(path[len(RESET) + 1:])
    return (8, path)


def canonical_order(members):
    """Members in the canonical write order; their own order breaks no tie."""
    return sorted(members, key=lambda member: _rank(member.path))


_TYPED = (ARCHIVE, SHAPE, GRAIN, THUMBNAIL, AUTHOR_PICTURE, SIGNATURE)


class BrushFolder:
    """A brush folder: its members, in order, and typed views over them.

    members      [Member]; (path, bytes) pairs are taken too
    source_uuid  the folder's name in the set it was read from, or None
    origin       where it was found ("" when unknown)
    warnings     what reading it noticed; skipped [(entry, why)] what it refused
    """

    def __init__(self, members=(), *, source_uuid=None, origin="", warnings=None, skipped=None):
        self.members = [_member(item) for item in members]
        paths = [member.path for member in self.members]
        if len(set(paths)) != len(paths):
            raise ContainerError("bad_member", "a folder holds each path once")
        self.source_uuid = source_uuid
        self.origin = origin
        self.warnings = list(warnings or [])
        self.skipped = list(skipped or [])

    def __repr__(self):
        return f"<BrushFolder {len(self.members)} members{' ' + self.origin if self.origin else ''}>"

    @classmethod
    def from_parts(cls, archive, shape=None, grain=None, thumbnail=None, author_picture=None,
                   signature=None, sub=None, reset=None, extras=()):
        """A folder made from its parts, in canonical order: the signature F3
        gives a BrushFolder. `sub` and `reset` are BrushFolders; `extras` are
        (path, bytes) pairs."""
        members = [(path, data) for path, data in ((ARCHIVE, archive), (SHAPE, shape),
                                                   (GRAIN, grain), (THUMBNAIL, thumbnail),
                                                   (AUTHOR_PICTURE, author_picture),
                                                   (SIGNATURE, signature)) if data is not None]
        for name, inner in ((SUB, sub), (RESET, reset)):
            if inner is not None:
                members += [Member(f"{name}/{m.path}", m.data, m.date_time, m.form)
                            for m in inner.members]
        members += [(path, data) for path, data in extras]
        return cls(members)

    # ── reading members ──
    def paths(self):
        return [member.path for member in self.members]

    def pairs(self):
        """[(path, bytes)] in member order."""
        return [(member.path, member.data) for member in self.members]

    def member(self, path):
        return next((member for member in self.members if member.path == path), None)

    def get(self, path):
        """The bytes of the member at `path`, or None."""
        member = self.member(path)
        return member.data if member is not None else None

    def __contains__(self, path):
        return self.member(path) is not None

    # ── typed views ──
    @property
    def archive(self):
        return self.get(ARCHIVE)

    @property
    def shape(self):
        return self.get(SHAPE)

    @property
    def grain(self):
        return self.get(GRAIN)

    @property
    def thumbnail(self):
        return self.get(THUMBNAIL)

    @property
    def author_picture(self):
        return self.get(AUTHOR_PICTURE)

    @property
    def signature(self):
        return self.get(SIGNATURE)

    def view(self, folder):
        """The members under `folder/` as a BrushFolder of their own (paths
        relative to it), or None when there are none. It is a view: changing
        it changes nothing here."""
        prefix = folder + "/"
        inside = [Member(m.path[len(prefix):], m.data, m.date_time, m.form)
                  for m in self.members if m.path.startswith(prefix)]
        if not inside:
            return None
        return BrushFolder(inside, origin=f"{self.origin}/{folder}" if self.origin else folder)

    @property
    def sub(self):
        return self.view(SUB)

    @property
    def reset(self):
        return self.view(RESET)

    @property
    def extras(self):
        """[(path, bytes)] of every member no typed view claims."""
        return [(m.path, m.data) for m in self.members
                if m.path not in _TYPED and not m.path.startswith((SUB + "/", RESET + "/"))]

    def secondaries(self):
        """[(folder name, BrushFolder)] for every `SubNN/` that holds a
        Brush.archive, in ascending order of name: Sub01/ and any beyond it."""
        names = sorted({m.path.split("/", 1)[0] for m in self.members
                        if "/" in m.path and SUB_FOLDER.fullmatch(m.path.split("/", 1)[0])
                        and m.path.split("/", 1)[1] == ARCHIVE})
        return [(name, self.view(name)) for name in names]

    # ── changing members ──
    def copy(self):
        """A copy whose member list can be changed without touching this one."""
        made = BrushFolder([], source_uuid=self.source_uuid, origin=self.origin,
                           warnings=self.warnings, skipped=self.skipped)
        made.members = [Member(m.path, m.data, m.date_time, m.form) for m in self.members]
        return made

    def set(self, path, data):
        """Give the member at `path` these bytes. A member that was there keeps
        its place and its zip form and loses its source date; a new one is
        added at the end, in the default form."""
        if not isinstance(path, str) or not path:
            raise ContainerError("bad_member", f"a member's path is text, not {path!r}")
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise ContainerError("bad_member", f"the data of {path!r} must be bytes")
        member = self.member(path)
        if member is None:
            self.members.append(Member(path, bytes(data)))
        else:
            member.data, member.date_time = bytes(data), None

    def remove(self, path):
        """Remove the member at `path`; True when there was one."""
        before = len(self.members)
        self.members = [m for m in self.members if m.path != path]
        return len(self.members) != before

    def unknown_members(self):
        """The members that raise an unknown-member warning: extras that are
        not a `.empty` and not the texture the folder's archive names, and the
        same inside Sub01/ and Reset/ (as paths of this folder). A secondary
        folder beyond Sub01 counts once, by its folder name."""
        candidates, beyond = [], []
        for path, _ in self.extras:
            top = path.split("/", 1)[0]
            if "/" in path and SUB_FOLDER.fullmatch(top):
                if top not in beyond:
                    beyond.append(top)
            elif _last(path).lower() != EMPTY:
                candidates.append(path)
        unknown = []
        if candidates:                       # the archive is read only when it can matter
            named = {name for name in archive_texture_names(self.archive).values() if name}
            unknown = [path for path in candidates if path not in named]
        for folder in (SUB, RESET):
            inner = self.view(folder)
            if inner is not None:
                unknown += [f"{folder}/{path}" for path in inner.unknown_members()]
        return unknown + [f"{name}/" for name in beyond]

    def member_warnings(self):
        """Warnings about the members, for a person: unknown members and
        secondary folders beyond Sub01."""
        out = []
        for path in self.unknown_members():
            if path.endswith("/"):
                out.append(f"a secondary folder beyond {SUB}: {path} is kept as extra members")
            else:
                out.append(f"an unknown member, kept as it is: {path}")
        return out


# ── texture names, resolution and identity inputs ────────────────────────────

def _text(form):
    """The text of a string value: a str, brush_model's {"string": s} form, or
    keyed_archive's NSMutableString dict; None for anything else."""
    if isinstance(form, str):
        return form
    if isinstance(form, bplist.PDict):
        value = form.get("NS.string")
        return value if isinstance(value, str) else None
    if isinstance(form, dict):
        value = form.get("string")
        return value if isinstance(value, str) else None
    return None


def texture_names(params):
    """{"shape": name or None, "grain": name or None} from a brush's parameters
    (brush_model's `params`, or any mapping of the two keys)."""
    params = params or {}
    return {"shape": _text(params.get(SHAPE_KEY)) or None,
            "grain": _text(params.get(GRAIN_KEY)) or None}


def archive_texture_names(archive_bytes):
    """texture_names read straight from Brush.archive bytes, through
    keyed_archive without the profile check. An archive that does not read
    names nothing."""
    if not archive_bytes:
        return {"shape": None, "grain": None}
    try:
        archive = keyed_archive.decode(archive_bytes, verify=False)
        root = keyed_archive.root(archive)
        if not isinstance(root, bplist.PDict):
            return {"shape": None, "grain": None}
        return {"shape": _text(keyed_archive.deref(archive, root.get(SHAPE_KEY))) or None,
                "grain": _text(keyed_archive.deref(archive, root.get(GRAIN_KEY))) or None}
    except (CodecError, RecursionError, TypeError, AttributeError):
        return {"shape": None, "grain": None}


def _bundled_file(bundled, name, limits):
    """The bytes of the file called exactly `name` in the bundled folder, or
    None. The name comes from an archive, so it is never joined into a path:
    the folder is listed and its entries are compared with it."""
    if bundled is None:
        return None
    if isinstance(bundled, dict):
        data = bundled.get(name)
        return bytes(data) if isinstance(data, (bytes, bytearray)) else None
    try:
        with os.scandir(bundled) as listing:
            match = next((entry for entry in listing if entry.name == name), None)
        if match is None or not match.is_file(follow_symlinks=False):
            return None
        if match.stat(follow_symlinks=False).st_size > limits["entry_bytes"]:
            return None
        with open(match.path, "rb") as handle:
            return handle.read(limits["entry_bytes"] + 1)[:limits["entry_bytes"]]
    except OSError:
        return None


def resolve_textures(folder, params=None, *, bundled=None, limits=None):
    """{"shape": (bytes or None, source), "grain": (bytes or None, source)}, by
    the one resolution rule of F3. `params` gives the bundled names (None: read
    them from the folder's archive); `bundled` is the library's `bundled/`
    folder, or a {name: bytes} mapping, or None."""
    limits = CAPS if limits is None else limits
    names = texture_names(params) if params is not None else None
    out = {}
    for role, member_path in (("shape", SHAPE), ("grain", GRAIN)):
        data = folder.get(member_path)
        if data is not None:
            out[role] = (data, "embedded")
            continue
        if names is None:                    # the archive is read only when it can matter
            names = archive_texture_names(folder.archive)
        name = names[role]
        if not name:
            out[role] = (None, "none")
            continue
        data = folder.get(name) if "/" not in name else None
        if data is not None:
            out[role] = (data, "embedded")
        elif role == "grain" and name == BLANK_GRAIN:
            out[role] = (None, "blank")
        else:
            supplied = _bundled_file(bundled, name, limits)
            out[role] = (supplied, "bundled-supplied") if supplied is not None else (None, "bundled")
    return out


def _carried(folder):
    textures = resolve_textures(folder)
    return tuple(textures[role][0] if textures[role][1] == "embedded" else None
                 for role in ("shape", "grain"))


def identity_inputs(folder):
    """(archive, shape, grain, subs): what identity.content_sha256 hashes for
    this folder (F1). Shape and grain are what the folder itself carries;
    `subs` holds one (archive, shape, grain) per SubNN/ with a Brush.archive,
    ascending by folder name, each resolved inside its own folder."""
    if folder.archive is None:
        raise ContainerError("no_archive", "a brush folder without Brush.archive has no identity")
    shape, grain = _carried(folder)
    subs = []
    for _, inner in folder.secondaries():
        sub_shape, sub_grain = _carried(inner)
        subs.append((inner.archive, sub_shape, sub_grain))
    return folder.archive, shape, grain, subs


# ── the set's plist ──────────────────────────────────────────────────────────

def _plain(value, depth=0):
    """A value of a binary plist (bplist's logical form) as plistlib's."""
    if depth > bplist.MAX_DEPTH:
        raise ContainerError("bad_plist", "brushset.plist nests too deep")
    if isinstance(value, bplist.PDict):
        out = {}
        for key, item in value:
            if not isinstance(key, str) or key in out:
                raise ContainerError("bad_plist", "brushset.plist repeats a key or has one that "
                                                  "is not text")
            out[key] = _plain(item, depth + 1)
        return out
    if isinstance(value, list):
        return [_plain(item, depth + 1) for item in value]
    if isinstance(value, bplist.Real):
        return value.value
    if isinstance(value, bplist.Date):
        return datetime(2001, 1, 1) + timedelta(seconds=value.value)
    if isinstance(value, (str, int, bool, bytes)):
        return value
    raise ContainerError("bad_plist", f"brushset.plist holds a {type(value).__name__}")


def parse_plist(data):
    """(name, folder names, extra keys, key order) of a brushset.plist, XML or
    binary. Raises ContainerError("bad_plist")."""
    try:
        if data.startswith(b"bplist00"):
            value = _plain(bplist.loads(data))
        else:
            value = plistlib.loads(data, fmt=plistlib.FMT_XML)
    except ContainerError:
        raise
    except Exception as exc:    # anything a stranger's plist can raise
        raise ContainerError("bad_plist", f"brushset.plist cannot be read ({type(exc).__name__})") from None
    if not isinstance(value, dict):
        raise ContainerError("bad_plist", "brushset.plist is not a dict")
    name, brushes = value.get("name"), value.get("brushes")
    if not isinstance(name, str):
        raise ContainerError("bad_plist", "brushset.plist has no `name` text")
    if not isinstance(brushes, list) or not all(isinstance(item, str) for item in brushes):
        raise ContainerError("bad_plist", "brushset.plist has no `brushes` list of folder names")
    extra = {key: item for key, item in value.items() if key not in PLIST_KEYS}
    return name, list(brushes), extra, tuple(value)


def render_plist(name, uuids, extra=None, order=PLIST_KEYS):
    """A brushset.plist as the app writes one: XML, UTF-8, tab-indented, LF,
    keys in `order` (extra keys it does not name follow it), `&`, `<`, `>`
    escaped. Written by plistlib, which gives the 61 plists of the library
    byte for byte."""
    extra = dict(extra or {})
    content = {}
    for key in list(order) + [key for key in PLIST_KEYS if key not in order] + list(extra):
        if key in content:
            continue
        if key == "brushes":
            content[key] = list(uuids)
        elif key == "name":
            content[key] = name
        elif key in extra:
            content[key] = extra[key]
    try:
        return plistlib.dumps(content, fmt=plistlib.FMT_XML, sort_keys=False)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ContainerError("write", f"brushset.plist cannot be written: {exc}") from None


# ── sets ─────────────────────────────────────────────────────────────────────

@dataclass(eq=False)
class BrushSet:
    """A brushset.

    name          the set's name, exactly as the plist holds it
    brushes       [(folder name, BrushFolder)] in plist order; folders the
                  plist does not list follow, with a warning
    entry_order   the source zip's entry names (below `prefix`), in zip order
    origin        where it was found
    plist_extra   the plist's other keys, in the order read
    plist_order   every key of the plist in the order read
    plist_source  the plist's bytes as read, written back while nothing it
                  says has changed
    plist_date, plist_form   how the source zip stored the plist
    prefix        the one top folder the set sat in, or ""
    warnings, skipped        what reading it noticed and refused
    """

    name: str
    brushes: list
    entry_order: list = field(default_factory=list)
    origin: str = ""
    plist_extra: dict = field(default_factory=dict)
    plist_order: tuple = PLIST_KEYS
    plist_source: bytes | None = None
    plist_date: tuple | None = None
    plist_form: str | None = None
    prefix: str = ""
    warnings: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    plist_read: tuple | None = field(default=None, repr=False)

    def __post_init__(self):
        self.brushes = [(uuid, folder) for uuid, folder in self.brushes]

    def uuids(self):
        return [uuid for uuid, _ in self.brushes]

    def _plist_state(self):
        return (self.name, self.uuids(), copy.deepcopy(self.plist_extra), tuple(self.plist_order))


def plist_bytes(brush_set):
    """The bytes of the set's plist: the source bytes while the name, the
    folder names and the plist keys are what was read; otherwise written new."""
    if (brush_set.plist_source is not None and brush_set.plist_read is not None
            and brush_set._plist_state() == brush_set.plist_read):
        return brush_set.plist_source
    return render_plist(brush_set.name, brush_set.uuids(), brush_set.plist_extra,
                        brush_set.plist_order)


# ── reading ──────────────────────────────────────────────────────────────────

class Found(list):
    """What read_any found: BrushSet and BrushFolder objects in the order met.
    `skipped` lists [(where, why)] for every container or entry not read."""

    def __init__(self):
        super().__init__()
        self.skipped = []


def _open(data, where):
    try:
        return zipfile.ZipFile(io.BytesIO(data))
    except ZIP_ERRORS as exc:
        raise ContainerError("not_a_zip", f"{where or 'the file'} cannot be opened as a zip "
                                          f"({type(exc).__name__})") from None


def _check_bytes(data, where, limits):
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise ContainerError("not_a_zip", "a container is bytes")
    if is_lfs_pointer(data):
        raise ContainerError("lfs_pointer", f"{where or 'the file'} is a Git LFS pointer, not a "
                                            "brush file: run git lfs pull")
    if len(data) > limits["upload_bytes"]:
        raise LimitExceeded("upload_bytes", f"{len(data):,} bytes; the cap is "
                                            f"{limits['upload_bytes']:,}")
    return bytes(data)


def _structural(listing):
    out = []
    if listing.duplicates:
        shown = ", ".join(listing.duplicates[:3]) + (" ..." if len(listing.duplicates) > 3 else "")
        out.append(f"{len(listing.duplicates)} later entr{'y' if len(listing.duplicates) == 1 else 'ies'} "
                   f"with a name already met {'was' if len(listing.duplicates) == 1 else 'were'} "
                   f"dropped; the first wins: {shown}")
    return out


def _read_members(archive, items, budget, limits, skipped, where):
    """Members from [(path in folder, ZipInfo)], or skip what is refused."""
    members = []
    for path, info in items:
        problem = hostile(info.orig_filename)
        if problem:
            skipped.append((info.orig_filename, problem))
            continue
        if info.flag_bits & 0x1:
            skipped.append((info.orig_filename, "an encrypted entry"))
            continue
        is_archive = _last(path) == ARCHIVE
        cap = limits["archive_bytes"] if is_archive else limits["entry_bytes"]
        data = read_member(archive, info, cap, budget, limits=limits,
                           cap_name="archive_bytes" if is_archive else "entry_bytes")
        members.append(Member(path, data, tuple(info.date_time),
                              zip_writer.form_of(info.compress_type, info.flag_bits)))
    return members


def _brush_from(archive, listing, where, budget, limits):
    check_declared(listing.kept, limits=limits)
    skipped = []
    members = _read_members(archive, [(info.orig_filename, info) for info in listing.kept],
                            budget, limits, skipped, where)
    folder = BrushFolder(members, origin=where, warnings=_structural(listing),
                         skipped=skipped)
    if folder.archive is None:
        raise ContainerError("not_a_brush", f"{where or 'the file'} holds no readable Brush.archive")
    folder.warnings += folder.member_warnings()
    return folder


def _set_from(archive, listing, prefix, where, budget, limits):
    check_declared(listing.kept, limits=limits)
    warnings = _structural(listing)
    skipped = []
    plist_info = next(info for info in listing.kept if info.orig_filename == prefix + SET_PLIST)
    raw = read_member(archive, plist_info, limits["archive_bytes"], budget, limits=limits,
                      cap_name="archive_bytes")
    name, listed, extra, order = parse_plist(raw)
    groups, entry_order = {}, []
    for info in listing.kept:
        full = info.orig_filename
        problem = hostile(full)
        if problem:
            skipped.append((full, problem))
            continue
        if not full.startswith(prefix):
            skipped.append((full, "a file outside the set's folder; not written back"))
            continue
        relative = full[len(prefix):]
        if relative == SET_PLIST:
            entry_order.append(relative)
            continue
        if "/" not in relative:
            skipped.append((full, "a file outside every brush folder; not written back"))
            continue
        top, path = relative.split("/", 1)
        groups.setdefault(top, []).append((path, info))
        entry_order.append(relative)
    folders = {}
    for top, items in groups.items():
        members = _read_members(archive, items, budget, limits, skipped, where)
        if not any(member.path == ARCHIVE for member in members):
            skipped.append((prefix + top + "/", "a folder that holds no Brush.archive; not "
                                                "written back"))
            entry_order = [entry for entry in entry_order if not entry.startswith(top + "/")]
            continue
        folders[top] = BrushFolder(members, source_uuid=top, origin=f"{where}/{top}" if where else top)
    brushes, placed = [], set()
    for uuid in listed:
        if uuid in placed:
            warnings.append(f"brushset.plist lists {uuid} twice; the second is ignored")
            continue
        if uuid not in folders:
            warnings.append(f"brushset.plist lists {uuid}, which the set does not hold")
            continue
        placed.add(uuid)
        brushes.append((uuid, folders[uuid]))
    for top, folder in folders.items():
        if top not in placed:
            warnings.append(f"the folder {top} is not listed in brushset.plist; it is kept after "
                            "the listed ones")
            brushes.append((top, folder))
    for _, folder in brushes:
        folder.warnings += folder.member_warnings()
    brush_set = BrushSet(name, brushes, entry_order, where, extra, order, raw,
                         tuple(plist_info.date_time),
                         zip_writer.form_of(plist_info.compress_type, plist_info.flag_bits),
                         prefix, warnings, skipped)
    brush_set.plist_read = brush_set._plist_state()
    return brush_set


def _read_zip(data, where, limits, budget, want):
    with _open(data, where) as archive:
        listing = list_entries(archive.infolist(), limits=limits)
        kind, prefix = sniff({info.orig_filename for info in listing.kept})
        if want == "brush" and kind != "brush":
            raise ContainerError("not_a_brush", f"{where or 'the file'} is not a brush "
                                                "(no Brush.archive at its root)")
        if want == "set" and kind != "set":
            raise ContainerError("not_a_brushset", f"{where or 'the file'} is not a brushset "
                                                   "(no brushset.plist at its root)")
        if kind == "brush":
            return _brush_from(archive, listing, where, budget, limits)
        if kind == "set":
            return _set_from(archive, listing, prefix, where, budget, limits)
        return None


def read_brush(data, *, hint="", limits=None):
    """The BrushFolder of a `.brush`: a zip with Brush.archive at its root."""
    limits = CAPS if limits is None else limits
    data = _check_bytes(data, hint, limits)
    return _read_zip(data, hint, limits, Budget(limits["total_bytes"]), "brush")


def read_brushset(data, *, hint="", limits=None):
    """The BrushSet of a `.brushset`: a zip with brushset.plist at its root, or
    in its one top folder."""
    limits = CAPS if limits is None else limits
    data = _check_bytes(data, hint, limits)
    return _read_zip(data, hint, limits, Budget(limits["total_bytes"]), "set")


def read_any(data, hint="", *, limits=DEFAULT_LIMITS):
    """Every set and brush in a file, nested to the depth cap: a Found list of
    BrushSet and BrushFolder objects, each with its `origin` (`hint`, then `!/`
    and the entry names inward). A nested container that cannot be read is
    listed in `skipped`; the file itself raises."""
    data = _check_bytes(data, hint, limits)
    found = Found()
    _search(data, hint, 0, Budget(limits["total_bytes"]), limits, found)
    return found


def _search(data, where, depth, budget, limits, found):
    result = _read_zip(data, where, limits, budget, None)
    if result is not None:
        found.append(result)
        return
    with _open(data, where) as archive:
        listing = list_entries(archive.infolist(), limits=limits)
        for info in listing.kept:
            if not info.orig_filename.lower().endswith(NESTED_SUFFIXES):
                continue
            inner = f"{where}!/{shown_name(info)}" if where else shown_name(info)
            try:
                if depth + 1 > limits["nesting_depth"]:
                    raise LimitExceeded("nesting_depth", f"nested more than "
                                                         f"{limits['nesting_depth']} zips deep; "
                                                         "not opened")
                problem = hostile(info.orig_filename)
                if problem:
                    raise ContainerError("hostile_name", problem)
                nested = read_member(archive, info, limits["upload_bytes"], budget, limits=limits,
                                     cap_name="upload_bytes")
                if is_lfs_pointer(nested):
                    raise ContainerError("lfs_pointer", "a Git LFS pointer, not a brush file")
                if nested[:4] not in ZIP_MAGIC:
                    raise ContainerError("not_a_zip", "not a zip file, whatever its name says")
                before = len(found)
                _search(nested, inner, depth + 1, budget, limits, found)
                if len(found) == before and info.orig_filename.lower().endswith((".brush", ".brushset")):
                    found.skipped.append((inner, "it holds no brushset.plist and no Brush.archive"))
            except ContainerError as exc:            # LimitExceeded among them
                found.skipped.append((inner, exc.detail or exc.code))


# ── writing ──────────────────────────────────────────────────────────────────

def _entry(name, member, mtime, source_dates):
    date = member.date_time if (source_dates and member.date_time is not None) else mtime
    return (name, member.data, date, member.form)


def _zip(entries, mtime):
    try:
        return zip_writer.write_zip(entries, date_time=mtime)
    except zip_writer.ZipWriteError as exc:
        raise ContainerError("write", str(exc)) from None


def write_brush(folder, *, mtime=ZIP_EPOCH, preserve_order=False, source_dates=False):
    """The bytes of a `.brush`: the folder's members at the root of a zip, in
    canonical order (or the folder's own, with `preserve_order`)."""
    if folder.archive is None:
        raise ContainerError("no_archive", "a brush folder without Brush.archive is not a brush")
    members = folder.members if preserve_order else canonical_order(folder.members)
    return _zip([_entry(member.path, member, mtime, source_dates) for member in members], mtime)


def _folder_name(uuid):
    if not isinstance(uuid, str) or not uuid or "/" in uuid:
        raise ContainerError("bad_folder", f"a brush folder's name is one path part, not {uuid!r}")
    try:
        zip_writer.check_name(uuid)
    except zip_writer.ZipWriteError as exc:
        raise ContainerError("bad_folder", str(exc)) from None
    return uuid


def write_brushset(brush_set, *, mtime=ZIP_EPOCH, preserve_order=False, source_dates=False):
    """The bytes of a `.brushset`: one folder per brush, then brushset.plist.

    preserve_order   replay the source zip's entry order (`entry_order`); a
                     member or folder it does not know follows in canonical
                     order: a new member after the last one of its folder, a
                     new folder at the end, before the plist if that came last
    source_dates     give each member read from a file the date it had
    """
    if not isinstance(brush_set.name, str):
        raise ContainerError("bad_plist", "a set's name is text")
    seen = set()
    for uuid, folder in brush_set.brushes:
        _folder_name(uuid)
        if uuid in seen:
            raise ContainerError("bad_folder", f"two brushes of the set are called {uuid}")
        seen.add(uuid)
        if folder.archive is None:
            raise ContainerError("no_archive", f"{uuid} holds no Brush.archive")
    plist = Member(SET_PLIST, plist_bytes(brush_set), brush_set.plist_date, brush_set.plist_form)
    entries = []
    if not preserve_order or not brush_set.entry_order:
        for uuid, folder in brush_set.brushes:
            entries += [_entry(f"{uuid}/{m.path}", m, mtime, source_dates)
                        for m in canonical_order(folder.members)]
        entries.append(_entry(SET_PLIST, plist, mtime, source_dates))
        return _zip(entries, mtime)
    by_source = {}
    for uuid, folder in brush_set.brushes:
        key = folder.source_uuid if folder.source_uuid is not None else uuid
        by_source.setdefault(key, (uuid, folder))
    last_of = {}
    for position, name in enumerate(brush_set.entry_order):
        last_of[name.split("/", 1)[0]] = position
    done, plist_done = set(), False

    def rest_of(uuid, folder):
        out = []
        for member in canonical_order(folder.members):
            if (uuid, member.path) not in done:
                done.add((uuid, member.path))
                out.append(_entry(f"{uuid}/{member.path}", member, mtime, source_dates))
        return out

    for position, name in enumerate(brush_set.entry_order):
        if name == SET_PLIST:
            if not plist_done:
                entries.append(_entry(SET_PLIST, plist, mtime, source_dates))
                plist_done = True
            continue
        source, _, path = name.partition("/")
        target = by_source.get(source)
        if target is None:
            continue
        uuid, folder = target
        member = folder.member(path)
        if member is not None and (uuid, path) not in done:
            done.add((uuid, path))
            entries.append(_entry(f"{uuid}/{path}", member, mtime, source_dates))
        if last_of.get(source) == position:
            entries += rest_of(uuid, folder)
    tail = []
    for uuid, folder in brush_set.brushes:
        tail += rest_of(uuid, folder)
    if plist_done:
        entries += tail
    else:
        entries += tail + [_entry(SET_PLIST, plist, mtime, source_dates)]
    return _zip(entries, mtime)


# ── what an export did ───────────────────────────────────────────────────────

def member_plan(before, after, *, reencoded=(), drop=()):
    """[{"path", "size", "state"}]: each member of `after` (a BrushFolder) as
    `verbatim` (the bytes of `before`'s member at that path), `re-encoded` (a
    path in `reencoded` whose bytes changed), or `replaced` (any other change,
    or a member `before` did not have); then each member of `before` missing
    from `after` as `dropped`. A drop of a path not in `drop` raises
    ContainerError("unrequested_drop")."""
    plan = []
    for member in after.members:
        old = before.get(member.path) if before is not None else None
        if old is not None and old == member.data:
            state = "verbatim"
        elif old is not None and member.path in reencoded:
            state = "re-encoded"
        else:
            state = "replaced"
        plan.append({"path": member.path, "size": len(member.data), "state": state})
    missing = [m for m in (before.members if before is not None else []) if m.path not in after]
    unasked = [m.path for m in missing if m.path not in drop]
    if unasked:
        raise ContainerError("unrequested_drop", "members would be dropped that nobody asked to "
                                                 f"drop: {', '.join(unasked)}")
    plan += [{"path": m.path, "size": len(m.data), "state": "dropped"} for m in missing]
    return plan


def read_path(path, *, limits=None):
    """The bytes of a container on disk, refused before reading when the file
    is over the upload cap. A Git LFS pointer is read (it is small) and is
    refused by the reader."""
    limits = CAPS if limits is None else limits
    path = Path(path)
    size = path.stat().st_size
    if size > limits["upload_bytes"]:
        raise LimitExceeded("upload_bytes", f"{size:,} bytes; the cap is {limits['upload_bytes']:,}")
    with open(path, "rb") as handle:
        # Read what is there, sized by the file, not a buffer of the whole cap
        # (512 MiB allocated on every call). A file that grew past the cap
        # since the stat is refused all the same.
        data = handle.read()
    if len(data) > limits["upload_bytes"]:
        raise LimitExceeded("upload_bytes", f"{len(data):,} bytes; the cap is "
                                            f"{limits['upload_bytes']:,}")
    return data
