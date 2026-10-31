"""Identity for the brush library: the one place an id is computed.

A brush, a texture and a brushset are each named by a short id taken from a
sha256. Every other module asks this one; none hashes for itself. The formulas
are frozen (brushes/docs/CONTRACTS.md, F1), because an id is written into the
catalog, the notes, the tag sidecars and the preview file names: changing a
formula renames everything at once.

    part(x)        = b"\\x00" if x is None else b"\\x01" + len(x) as 8 bytes big-endian + x
    content_sha256 = sha256(b"rosw-brush-v1\\x00" + part(archive) + part(shape) + part(grain)
                            + for each SubNN ascending: b"\\x02" + part(a) + part(s) + part(g))
    brush_id       = "b_" + content_sha256[:12]
    texture_id     = "t_" + sha256(png_bytes)[:12]
    set_id         = "s_" + sha256(b"rosw-set-v1\\x00" + name as UTF-8 + b"\\x00"
                                   + "\\n".join(brush_ids) as UTF-8)[:12]

What goes in: the Brush.archive bytes, the shape and grain image bytes that the
brush file itself carries (None when the brush only names an image that ships
inside the drawing app), and the same three for each secondary brush folder:
every `SubNN/` that holds a Brush.archive, in ascending order of its folder
name, with its shape and grain found inside that folder by the same rule as the
primary's. A second secondary counts even though the typed view of a brush
folder shows only `Sub01/`.
What stays out: the thumbnail, the Reset copy, the author picture, the
signature, unknown extra members, and any image supplied from outside the file.

Twelve hex characters are 48 bits. Two different hashes that share those twelve
are not expected, and are never papered over: Registry raises PrefixCollision,
and a command that meets one exits 1.

Standard library only. Not a command.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

BRUSH_DOMAIN = b"rosw-brush-v1\x00"
SET_DOMAIN = b"rosw-set-v1\x00"
SUB_MARK = b"\x02"
ID_HEX = 12
SLUG_MAX = 48
SLUG_FALLBACK = "untitled"
LOOSE_SUFFIX = "-loose"
# A pack id must leave room for the suffix: `<pack_id>-loose` is a set slug.
PACK_ID_MAX = SLUG_MAX - len(LOOSE_SUFFIX)

BRUSH_ID_PATTERN = r"^b_[0-9a-f]{12}$"
TEXTURE_ID_PATTERN = r"^t_[0-9a-f]{12}$"
SET_ID_PATTERN = r"^s_[0-9a-f]{12}$"
SET_SLUG_PATTERN = r"^[a-z0-9][a-z0-9-]{0,47}$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"

# Compiled without the anchors' newline loophole: use fullmatch, never match.
_BRUSH_ID = re.compile(r"b_[0-9a-f]{12}")
_TEXTURE_ID = re.compile(r"t_[0-9a-f]{12}")
_SET_ID = re.compile(r"s_[0-9a-f]{12}")
_SET_SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,47}")
_SHA256 = re.compile(r"[0-9a-f]{64}")

# Names Windows will not let a file have, whatever the extension.
WINDOWS_DEVICES = frozenset(
    {"con", "prn", "aux", "nul"} | {f"{name}{n}" for name in ("com", "lpt") for n in range(1, 10)})

# Apostrophes are dropped, not turned into a hyphen: "Sargent's" is "sargents",
# whether the file wrote a straight quote or a typographic one.
_APOSTROPHES = dict.fromkeys(map(ord, "'‘’ʼ"))


class IdentityError(ValueError):
    """A value an id cannot be made from, or a string that is not an id."""


class PrefixCollision(IdentityError):
    """Two different full hashes share one short id. A command exits 1."""

    exit_code = 1

    def __init__(self, ident, known, other):
        super().__init__(
            f"{ident} stands for two different hashes ({known} and {other}). "
            "The short id is ambiguous; nothing was changed.")
        self.ident = ident
        self.known = known
        self.other = other


# ── predicates ───────────────────────────────────────────────────────────────

def is_brush_id(text):
    return isinstance(text, str) and _BRUSH_ID.fullmatch(text) is not None


def is_texture_id(text):
    return isinstance(text, str) and _TEXTURE_ID.fullmatch(text) is not None


def is_set_id(text):
    return isinstance(text, str) and _SET_ID.fullmatch(text) is not None


def is_set_slug(text):
    return isinstance(text, str) and _SET_SLUG.fullmatch(text) is not None


def is_pack_id(text):
    """A pack id: a slug short enough that its loose pseudo-set has a slug too."""
    return is_set_slug(text) and len(text) <= PACK_ID_MAX


def is_sha256(text):
    return isinstance(text, str) and _SHA256.fullmatch(text) is not None


# ── the hash ─────────────────────────────────────────────────────────────────

def _bytes_or_none(value, what):
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    raise IdentityError(f"{what} must be bytes or None, not {type(value).__name__}")


def part(data):
    """One framed field: a missing value and an empty one hash differently."""
    if data is None:
        return b"\x00"
    return b"\x01" + len(data).to_bytes(8, "big") + data


def content_sha256(archive, shape=None, grain=None, subs=()):
    """The 64-hex digest a brush is known by.

    archive  the Brush.archive bytes
    shape    the shape image bytes carried in the brush file, or None
    grain    the grain image bytes carried in the brush file, or None
    subs     one (archive, shape, grain) triple per secondary brush folder,
             in ascending SubNN order
    """
    archive = _bytes_or_none(archive, "archive")
    if archive is None:
        raise IdentityError("a brush has no identity without its archive bytes")
    digest = hashlib.sha256(BRUSH_DOMAIN)
    for name, value in (("archive", archive), ("shape", shape), ("grain", grain)):
        digest.update(part(_bytes_or_none(value, name)))
    for position, sub in enumerate(subs, start=1):
        try:
            sub_archive, sub_shape, sub_grain = sub
        except (TypeError, ValueError):
            raise IdentityError(
                f"sub {position} must be an (archive, shape, grain) triple") from None
        digest.update(SUB_MARK)
        for name, value in (("archive", sub_archive), ("shape", sub_shape), ("grain", sub_grain)):
            digest.update(part(_bytes_or_none(value, f"sub {position} {name}")))
    return digest.hexdigest()


def brush_id_from_sha256(digest):
    """The short id for a digest content_sha256 returned."""
    if not is_sha256(digest):
        raise IdentityError("a brush id is cut from 64 lower-case hex characters")
    return "b_" + digest[:ID_HEX]


def brush_id(archive, shape=None, grain=None, subs=()):
    return brush_id_from_sha256(content_sha256(archive, shape, grain, subs))


def texture_sha256(png_bytes):
    """The digest of a texture: the image file's bytes, exactly as stored."""
    data = _bytes_or_none(png_bytes, "a texture")
    if data is None:
        raise IdentityError("a texture has no identity without its bytes")
    return hashlib.sha256(data).hexdigest()


def texture_id(png_bytes):
    return "t_" + texture_sha256(png_bytes)[:ID_HEX]


def set_sha256(name, brush_ids):
    """The digest of a brushset: its name as written, and its members in order.

    The name is hashed verbatim, so a trailing space counts. A set that gains,
    loses or reorders a brush gets another id; set_id is a fingerprint, and the
    set's slug is the handle.
    """
    if not isinstance(name, str):
        raise IdentityError("a set name must be text")
    members = list(brush_ids)
    for member in members:
        if not is_brush_id(member):
            raise IdentityError(f"{member!r} is not a brush id, so it cannot be a set member")
    try:
        encoded = name.encode("utf-8")
    except UnicodeEncodeError:
        raise IdentityError("a set name must be encodable as UTF-8") from None
    return hashlib.sha256(SET_DOMAIN + encoded + b"\x00" + "\n".join(members).encode("utf-8")).hexdigest()


def set_id(name, brush_ids):
    return "s_" + set_sha256(name, brush_ids)[:ID_HEX]


# ── slugs ────────────────────────────────────────────────────────────────────

def slugify(text, fallback=SLUG_FALLBACK):
    """A lower-case ASCII handle of at most 48 characters, or the fallback.

    Accents fold to their base letter, apostrophes vanish, anything else that is
    not a letter or a digit becomes one hyphen. A name with nothing left (one
    written in a script with no ASCII form) returns the fallback, and a name
    Windows reserves for a device gets an `x-` in front.
    """
    if not is_set_slug(fallback):
        raise IdentityError(f"the fallback {fallback!r} is not itself a slug")
    folded = unicodedata.normalize("NFKD", str(text).translate(_APOSTROPHES))
    ascii_only = "".join(ch for ch in folded if not unicodedata.combining(ch) and ord(ch) < 128)
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    if not slug:
        return fallback
    if slug in WINDOWS_DEVICES:
        slug = "x-" + slug
    return slug[:SLUG_MAX].strip("-")


def loose_set_slug(pack_id):
    """The slug of the pseudo-set that holds a pack's loose .brush files.

    It is also that pseudo-set's name: it has no plist, so `set_id` hashes the
    slug itself (docs/CONTRACTS.md, F1 "Loose brushes").
    """
    if not is_pack_id(pack_id):
        raise IdentityError(f"{pack_id!r} cannot name a loose set: a pack id is a slug of at most "
                            f"{PACK_ID_MAX} characters")
    return f"{pack_id}{LOOSE_SUFFIX}"


# ── collisions ───────────────────────────────────────────────────────────────

class Registry:
    """Hands out ids and remembers which full hash each one stands for.

    Use one per catalog build. The same content always gets the same id back;
    different content that lands on an id already given raises PrefixCollision.
    """

    def __init__(self):
        self._full = {}

    def __len__(self):
        return len(self._full)

    def __contains__(self, ident):
        return ident in self._full

    def full_hash(self, ident):
        return self._full[ident]

    def add(self, ident, full_hash):
        """Record that `ident` stands for `full_hash`. Returns the id."""
        if not is_sha256(full_hash):
            raise IdentityError("a full hash is 64 lower-case hex characters")
        if not (is_brush_id(ident) or is_texture_id(ident) or is_set_id(ident)):
            raise IdentityError(f"{ident!r} is not a brush, texture or set id")
        if ident[2:] != full_hash[:ID_HEX]:
            raise IdentityError(f"{ident} is not cut from {full_hash}")
        known = self._full.setdefault(ident, full_hash)
        if known != full_hash:
            raise PrefixCollision(ident, known, full_hash)
        return ident

    def brush(self, archive, shape=None, grain=None, subs=()):
        digest = content_sha256(archive, shape, grain, subs)
        return self.add(brush_id_from_sha256(digest), digest)

    def texture(self, png_bytes):
        digest = texture_sha256(png_bytes)
        return self.add("t_" + digest[:ID_HEX], digest)

    def set(self, name, brush_ids):
        digest = set_sha256(name, brush_ids)
        return self.add("s_" + digest[:ID_HEX], digest)
