"""A keyed archive (`Brush.archive`) as a graph that can be written back byte for byte.

    archive = keyed_archive.decode(data)
    root = keyed_archive.root(archive)               # the brush: an ordered PDict
    root.set("plotSpacing", Real.f32(0.25))
    data = keyed_archive.encode(archive)

A keyed archive is a property list of four entries: `$version`, `$archiver`,
`$top` (which names the root) and `$objects`, a numbered list. Entry 0 of
`$objects` is the text `$null`; a `UID(n)` anywhere in the list means entry n,
and `UID(0)` means nil. An instance is a dict whose `$class` names a class
entry; a class entry is a dict of `$classname` and `$classes`.

`decode` keeps all of it, known or not: every key in the order it was stored,
every class, every width (docs/CONTRACTS.md, F3). The values are the logical
values of bplist.py: bool, int, str, bytes for data, `Real` (4 or 8 bytes, kept
apart), `UID`, `PDict` for a dict and list for an array.

Byte identity. `encode` writes the graph through bplist.flatten, the app's own
layout rules, with one of two rules for which value strings share an object
(`PROFILES`). `decode` proves the result on the spot: it encodes what it just
read with each profile and compares with the input.

    a match     archive.profile is that profile, archive.fidelity is "byte"
    no match    archive.profile is None, archive.fidelity is "table": the graph
                is right but these rules do not give the file's layout

Either way the input is kept in `archive.source`, and `encode` returns it for
an archive nobody changed. A changed archive is written by the rules with its
own profile; a changed "table" archive needs a profile from the caller (its
family's default), else DEFAULT_PROFILE is used. `rule_encode` always writes
by the rules.

Editing. Every place in the graph holds a value of its own, so setting one key
never changes another: the 0.0 that one object served for dozens of keys in
the file is shared again, or not, when the graph is flattened. Sharing between
`$objects` entries is explicit (two keys holding the same UID) and is the
caller's to keep or break. The library has two cases of it: the six `saved...`
keys of a modern brush hold one empty array, and three archives hold one
string entry under both `bundledShapePath` and `bundledGrainPath`. Four others
hold one text under two of the `bundled...Path` keys as two entries (one of
them under those same two keys), so equal text does not say which it is.

Numbering. `encode` writes `$objects` in list order and changes no UID.
`renumber` gives a graph the app's numbering: depth first from the root, each
instance before what it holds, its class entry after its contents the first
time the class is used. On every archive of the library it changes nothing.
The order of the root's own children is the app's encode order, which this
module does not know: the caller passes it, and without it the present
numbers decide.

Errors. A property list that is not a keyed archive, or a graph that cannot be
written as one, raises `ArchiveError` with one of the codes `envelope`,
`null_object`, `no_root`, `dangling_uid`, `bad_value` and `profile`. Bytes
that are not a property list raise bplist's own errors.

Standard library only. Not a command.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from typing import Callable

import bplist
from bplist import ArchiveError, CodecError, Date, PDict, Real, UID

__all__ = ["A6", "Archive", "ArchiveError", "CodecError", "DEFAULT_PROFILE", "ENVELOPE_KEYS",
           "FIDELITY_BYTE", "FIDELITY_TABLE", "LEGACY_SHARED", "NULL", "PDict", "PROFILES",
           "Real", "UID", "class_chain", "class_name", "clone", "decode", "deref", "encode",
           "is_modified", "legacy_shared", "matching_profiles", "renumber", "root",
           "rule_encode", "tagged_pointer_eligible", "uids_in"]

ENVELOPE_KEYS = ("$version", "$archiver", "$top", "$objects")
NULL = "$null"
ROOT = "root"
CLASS = "$class"
CLASS_NAME = "$classname"
CLASS_CHAIN = "$classes"

FIDELITY_BYTE = "byte"
FIDELITY_TABLE = "table"

# ── the two string-sharing rules ─────────────────────────────────────────────
# The app's writer seems to share an object between equal value strings only
# when both are the very same string in memory, and which strings that is true
# of changed with the system the app ran on. That is a model. What the library
# decides (1,040 distinct archives when this was written):
#
#   ios_legacy   619 archives. `NSObject` and `NSMutableArray` are shared in
#                the 512 that hold a curve and `NSDate` in the 22 that hold a
#                date; no other value string is. `NSArray` is in the set by
#                analogy: no legacy archive uses it twice, so none decides it.
#   ios_modern   421 archives. `NSObject`, `NSArray` and `NSDate` are shared
#                and `NSMutableArray` is not, nor any other repeated string.
#                The pointer rule below explains that, but so would "those
#                three names": no other string short enough is used twice in
#                any archive, so the alphabet is untested beyond `NSObject`.
#
# The 107 legacy archives without a curve repeat no value string that either
# rule shares, so both rules give their bytes; `decode` records the first.

LEGACY_SHARED = frozenset({"NSObject", "NSArray", "NSMutableArray", "NSDate"})

# The characters a short string may be packed from, most frequent first.
A6 = "eilotrm.apdnsIc ufkMShjTRxgC4013bDNvwyUL2O856P-B79AFKEWV_zGJ/HYX"
_A6 = frozenset(A6)
_A5 = frozenset(A6[:32])


def legacy_shared(text):
    """`ios_legacy`: four class names share an object; nothing else does."""
    return text in LEGACY_SHARED


def tagged_pointer_eligible(text):
    """`ios_modern`: an ASCII string short enough to be held in a pointer.

    Up to 7 characters of any ASCII; up to 9 from the 64-character alphabet
    A6; up to 11 from its first 32.
    """
    if not text.isascii():
        return False
    length = len(text)
    if length <= 7:
        return True
    if length <= 9:
        return _A6.issuperset(text)
    if length <= 11:
        return _A5.issuperset(text)
    return False


PROFILES: dict[str, Callable[[str], bool]] = {
    "ios_legacy": legacy_shared,
    "ios_modern": tagged_pointer_eligible,
}
# What a changed archive is written with when neither it nor the caller names
# a profile. brush_model passes the family's default instead.
DEFAULT_PROFILE = "ios_modern"


def _default_top():
    return PDict([(ROOT, UID(1))])


@dataclass
class Archive:
    """A decoded keyed archive.

    top_order   the four envelope keys in the order the file holds them
    version     `$version` (100000 in every file seen)
    archiver    `$archiver` ("NSKeyedArchiver")
    objects     `$objects`: entry 0 is "$null", entry `top["root"]` the root
    profile     the profile that reproduces `source`, or None
    fidelity    "byte" when a profile does, else "table"
    source      the bytes this was decoded from, or None for a built archive
    top         `$top`: {"root": UID(1)} in every file seen
    """

    top_order: tuple
    version: int
    archiver: str
    objects: list
    profile: str | None = None
    fidelity: str = FIDELITY_TABLE
    source: bytes | None = None
    top: PDict = field(default_factory=_default_top)
    _digest: str | None = field(default=None, repr=False, compare=False)

    def __repr__(self):
        held = "no source" if self.source is None else f"{len(self.source)} source bytes"
        return (f"<Archive {self.fidelity} {self.profile} {len(self.objects)} entries, {held}>")


# ── walking a graph ──────────────────────────────────────────────────────────

def _too_deep():
    return bplist.LimitExceeded("plist_depth",
                                f"containers nested deeper than {bplist.MAX_DEPTH}")


def uids_in(value):
    """Every UID inside a value, in order, the value itself included."""
    found = []

    def walk(item, depth):
        if isinstance(item, UID):
            found.append(item)
            return
        if isinstance(item, PDict):
            held = [v for _, v in item]
        elif isinstance(item, (list, tuple)):
            held = item
        else:
            return
        if depth > bplist.MAX_DEPTH:            # also ends a value that holds itself
            raise _too_deep()
        for child in held:
            walk(child, depth + 1)

    walk(value, 0)
    return found


def _copy(value, rename=None, depth=0):
    """A deep copy of a logical value; `rename` maps each UID number to a new one."""
    if isinstance(value, UID):
        return value if rename is None else UID(rename[value.value])
    if isinstance(value, (PDict, list, tuple)):
        if depth > bplist.MAX_DEPTH:
            raise _too_deep()
        if isinstance(value, PDict):
            return PDict((key, _copy(item, rename, depth + 1)) for key, item in value)
        return [_copy(item, rename, depth + 1) for item in value]
    if isinstance(value, bytearray):
        return bytes(value)
    return value


def _feed(digest, value, depth=0):
    """Feed one logical value to a hash, so that two graphs give one hash
    exactly when they would be written as the same bytes."""
    if depth > bplist.MAX_DEPTH:
        raise _too_deep()
    if isinstance(value, bool):
        digest.update(b"T" if value else b"F")
    elif isinstance(value, int):
        text = str(value).encode("ascii")
        digest.update(b"i%d:" % len(text) + text)
    elif isinstance(value, Real):
        digest.update(b"r%d:" % len(value.bits) + value.bits)
    elif isinstance(value, str):
        raw = value.encode("utf-16-be", "surrogatepass")
        digest.update(b"s%d:" % len(raw) + raw)
    elif isinstance(value, UID):
        digest.update(b"u%d;" % value.value)
    elif isinstance(value, (bytes, bytearray)):
        digest.update(b"b%d:" % len(value) + bytes(value))
    elif isinstance(value, Date):
        digest.update(b"d" + value.bits)
    elif isinstance(value, (PDict, dict)):
        pairs = list(value.items()) if isinstance(value, dict) else list(value)
        digest.update(b"{%d:" % len(pairs))
        for key, item in pairs:
            _feed(digest, key, depth + 1)
            _feed(digest, item, depth + 1)
    elif isinstance(value, (list, tuple)):
        digest.update(b"[%d:" % len(value))
        for item in value:
            _feed(digest, item, depth + 1)
    else:
        digest.update(b"?" + repr(value).encode("utf-8", "replace"))


def _tree_digest(archive):
    digest = hashlib.sha256()
    for part in (list(archive.top_order), archive.version, archive.archiver, archive.top,
                 archive.objects):
        _feed(digest, part)
    return digest.hexdigest()


def clone(archive):
    """A copy that shares no container with the original. A copy of an
    unchanged archive is unchanged too, and still returns the source bytes."""
    return replace(archive, top_order=tuple(archive.top_order), objects=_copy(archive.objects),
                   top=_copy(archive.top))


def is_modified(archive):
    """True when the graph is no longer what `decode` read (or when the
    archive was never decoded from bytes)."""
    if archive.source is None or archive._digest is None:
        return True
    try:
        return _tree_digest(archive) != archive._digest
    except (CodecError, TypeError, ValueError, AttributeError, RecursionError):
        return True


# ── looking things up ────────────────────────────────────────────────────────

def deref(archive, value):
    """The entry a UID names (None for nil); any other value is returned as it is."""
    if not isinstance(value, UID):
        return value
    if value.value == 0:
        return None
    if not 0 < value.value < len(archive.objects):
        raise ArchiveError("dangling_uid", f"UID {value.value} of {len(archive.objects)} entries")
    return archive.objects[value.value]


def root(archive):
    """The root instance: the brush itself, as an ordered PDict."""
    return deref(archive, archive.top.get(ROOT))


def _class_entry(archive, uid):
    holder = deref(archive, uid)
    if not isinstance(holder, PDict):
        return None
    entry = deref(archive, holder.get(CLASS))
    return entry if isinstance(entry, PDict) else None


def class_name(archive, uid):
    """The class name of the instance a UID names, or None when it is not an instance."""
    entry = _class_entry(archive, uid)
    name = entry.get(CLASS_NAME) if entry is not None else None
    return name if isinstance(name, str) else None


def class_chain(archive, uid):
    """The `$classes` list of the instance a UID names, or None."""
    entry = _class_entry(archive, uid)
    chain = entry.get(CLASS_CHAIN) if entry is not None else None
    return list(chain) if bplist.is_array(chain) else None


# ── checking ─────────────────────────────────────────────────────────────────

def _check(archive):
    """Raise ArchiveError unless the archive can be written as a keyed archive."""
    order = tuple(archive.top_order)
    if sorted(order) != sorted(ENVELOPE_KEYS):
        raise ArchiveError("envelope", f"the top order {order!r} is not the four envelope keys")
    if isinstance(archive.version, bool) or not isinstance(archive.version, int):
        raise ArchiveError("envelope", "`$version` is not an int")
    if not isinstance(archive.archiver, str):
        raise ArchiveError("envelope", "`$archiver` is not text")
    objects = archive.objects
    if not bplist.is_array(objects):
        raise ArchiveError("envelope", "`$objects` is not an array")
    if not objects or objects[0] != NULL:
        raise ArchiveError("null_object", "entry 0 of `$objects` is not the text `$null`")
    top = archive.top
    try:
        if not isinstance(top, PDict) or any(not isinstance(k, str) or not isinstance(v, UID)
                                             for k, v in top):
            raise ArchiveError("envelope", "`$top` is not a dict of UIDs")
        uids = uids_in([top, objects])
    except CodecError:
        raise
    except (TypeError, ValueError):
        raise ArchiveError("bad_value", "a PDict holds (key, value) pairs") from None
    start = top.get(ROOT)
    if start is None:
        raise ArchiveError("no_root", "`$top` names no root")
    count = len(objects)
    for uid in uids:
        if isinstance(uid.value, bool) or not isinstance(uid.value, int) \
                or not 0 <= uid.value < count:
            raise ArchiveError("dangling_uid", f"UID {uid.value!r} of {count} entries")
    if start.value == 0 or not isinstance(objects[start.value], PDict):
        raise ArchiveError("no_root", "the root is not an instance")


# ── decoding and encoding ────────────────────────────────────────────────────

def rule_encode(archive, profile):
    """The archive written by the app's layout rules with the named profile,
    whether or not it was changed. `$objects` is written in list order."""
    if profile not in PROFILES:
        raise ArchiveError("profile", f"{profile!r} is not one of {', '.join(PROFILES)}")
    _check(archive)
    values = {"$version": archive.version, "$archiver": archive.archiver,
              "$top": archive.top, "$objects": archive.objects}
    envelope = PDict((key, values[key]) for key in archive.top_order)
    return bplist.dumps(envelope, shared=PROFILES[profile])


def _rule_bytes(archive, profile):
    """rule_encode, or None for a graph the rules cannot write: one that was
    read from a file but holds a value no writer of the app's makes, such as
    a 16-byte int beyond 2**64. Such a file can still be replayed."""
    try:
        return rule_encode(archive, profile)
    except bplist.BplistError:
        return None


def matching_profiles(archive, data):
    """The profiles, in PROFILES order, whose rule encoding of `archive` is `data`."""
    return [name for name in PROFILES if _rule_bytes(archive, name) == data]


def decode(data, *, verify=True):
    """Read a keyed archive.

    With `verify` (the default) the graph is written back with each profile
    and compared with `data`: the first profile that gives the same bytes is
    recorded and the fidelity is "byte". Without it, or with no match, the
    fidelity is "table"; so is a graph that holds a value the rules cannot
    write at all (bplist raises for it again if the archive is changed and
    encoded). The input is kept as `source` in every case.

    Raises bplist.BplistError for bytes that are not a property list,
    bplist.LimitExceeded for one over a cap, and ArchiveError for a property
    list that is not a keyed archive.
    """
    table = bplist.parse_table(data)
    tree = bplist.resolve(table)
    if not isinstance(tree, PDict):
        raise ArchiveError("envelope", "the top object is not a dict")
    order = tuple(tree.keys())
    if sorted(order) != sorted(ENVELOPE_KEYS):
        raise ArchiveError("envelope", f"the top keys are {list(order)!r}, not the four "
                                       "of a keyed archive")
    archive = Archive(order, tree.get("$version"), tree.get("$archiver"), tree.get("$objects"),
                      None, FIDELITY_TABLE, bytes(data), tree.get("$top"))
    _check(archive)
    if verify:
        for name in PROFILES:
            if _rule_bytes(archive, name) == archive.source:
                archive.profile, archive.fidelity = name, FIDELITY_BYTE
                break
    archive._digest = _tree_digest(archive)
    return archive


def encode(archive, *, profile=None):
    """The bytes of an archive.

    An archive that is still what `decode` read is returned as its source
    bytes, whatever its fidelity. A changed or built one is written by the
    rules, with `profile` if given, else its own, else DEFAULT_PROFILE.
    """
    if not is_modified(archive):
        return archive.source
    return rule_encode(archive, profile or archive.profile or DEFAULT_PROFILE)


# ── canonical numbering ──────────────────────────────────────────────────────

def renumber(archive, root_child_order=None):
    """A copy of the archive with `$objects` numbered the way the app numbers them.

    Depth first from the root. An instance takes the next number, then
    everything it refers to, field by field in its own key order, then its
    class entry, the first time that class is used. `root_child_order` lists
    root keys in the order the app archives them; root keys it does not list
    follow in the order of their present numbers, which is also the whole
    order when it is None. Entries nothing refers to are dropped.

    When nothing moves, the copy still counts as unmodified and keeps the
    source bytes. Otherwise it has none and is written by the rules. The
    profile and the fidelity are carried over either way: they describe the
    file the graph was read from.
    """
    _check(archive)
    objects = archive.objects
    start = archive.top.get(ROOT).value
    listed = {key: rank for rank, key in enumerate(root_child_order or ())}

    def rank(pair):
        refs = [uid.value for uid in uids_in(pair[1]) if uid.value]
        return (listed.get(pair[0], len(listed)), min(refs) if refs else 0)

    def refers_to(number):
        """The entries an entry refers to, in the order they are numbered:
        what it holds first, its class last."""
        entry = objects[number]
        if not isinstance(entry, PDict):
            return [uid.value for uid in uids_in(entry)]
        fields = sorted(entry, key=rank) if number == start else list(entry)
        held, classes = [], []
        for key, value in fields:
            (classes if key == CLASS else held).extend(uid.value for uid in uids_in(value))
        return held + classes

    new_number = {0: 0}
    order = [0]
    # The root first, then anything else `$top` names. The stack is last in,
    # first out, so pushing a list reversed visits it in order, depth first.
    stack = [uid.value for _, uid in reversed(archive.top)] + [start]
    while stack:
        number = stack.pop()
        if number in new_number:
            continue
        new_number[number] = len(order)
        order.append(number)
        stack.extend(reversed(refers_to(number)))

    result = replace(archive, top_order=tuple(archive.top_order),
                     objects=[_copy(objects[number], new_number) for number in order],
                     top=_copy(archive.top, new_number))
    if result.objects != objects or result.top != archive.top:
        result.source = None
        result._digest = None
    return result
