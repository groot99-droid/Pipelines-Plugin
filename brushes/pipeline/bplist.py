"""Binary property lists, read and written byte for byte.

    table = bplist.parse_table(data)        # the object table, kept verbatim
    data  = bplist.serialize_table(table)   # ... and replayed
    value = bplist.loads(data)              # the logical tree
    data  = bplist.dumps(value, shared=rule)

This is the bottom of the file codec (docs/CONTRACTS.md, F3). A `Brush.archive`
is a binary property list ("bplist00") written by the drawing app's keyed
archiver, and the same value can be laid out in many ways: which equal values
share one object, how wide a number is stored, where an unused object is left
behind. The standard library's plistlib reads such a file but writes its own
layout, so a brush read and written through it is never the same bytes. This
module keeps two views:

  the object table   `parse_table` returns every object as a small tuple, in
                     file order, with the widths and reference lists it was
                     stored with. `serialize_table` writes a table back; for a
                     file laid out the plain way (`table.contiguous`) the result
                     is the file itself.
  the logical tree   `resolve` (and `loads`) turn a table into plain values;
                     `flatten` (and `dumps`) turn plain values into a table by
                     the rules the app's writer follows, given below.

Logical values:

    bool, int, str     themselves
    bytes              a data object
    Real               a real with its width kept: 4 bytes or 8. A plain Python
                       float is refused, because it does not say which
    UID                a keyed-archiver reference
    Date               a date object (never seen in a brush archive)
    PDict              a dict as an ordered list of (key, value) pairs
    list               an array

The writer's rules (`flatten`), in the order objects are numbered:

    dict      takes the next number; then every key, then every value in order
    array     takes the next number; then every element in order
    key       one object per distinct key text in the whole file. Keys and
              value strings never share an object
    bool      a new object every time, but every reference names the first one
              made for that value: the later ones are left unreferenced
    UID       the same pattern as bool, per value; as wide as its value needs
    int       one object per distinct value; 1, 2, 4 or 8 bytes by size, and 8
              for a negative one
    real      a 4-byte real with a whole-number value is one object per bit
              pattern; any other real is a new object every time
    string    one object per text when `shared(text)` says so, otherwise a new
              object every time. ASCII text is stored as bytes, anything else
              as UTF-16 big-endian
    data      a new object every time

    trailer   six zero bytes; the offset size, as wide as the offset of the
              offset table needs; the reference size, as wide as the number of
              objects needs; the number of objects; the top object, 0; the
              offset of the offset table

`shared` is the only thing that differs between the two generations of the
app's writer; keyed_archive.PROFILES holds both rules.

What stands behind the rules. Written by them, every `Brush.archive` of the
library came back byte for byte when this was written (1,071 archives, 1,040
of them distinct; the opt-in test in tests/test_keyed_archive.py repeats the
walk). That decides what those files exercise, and nothing more:

    decided     the numbering order; one object per key; the bool and UID
                pattern; one object per int value (1, 2 and 4 bytes); a whole
                4-byte real shared (0.0 and 1.0 in every file, 4.0 in five);
                a fractional one never shared; -0.0 kept apart from 0.0;
                ASCII and UTF-16 strings; counts under 15 and counts that take
                one more byte; reference size 1 up to 218 objects and 2 from
                393; offset size 2
    undecided   no file has it, so the rule here is a choice: an int of 8
                bytes or a negative one; a UID over 255; a count of 256 or
                more; where exactly the reference size and the offset size
                change (taken as 256 objects, and a table at 256 or 65,536
                bytes); a whole real other than 0, 1 and 4 used twice; -0.0
                used twice; a whole 8-byte real used twice (no archive holds
                more than one 8-byte real); a key and a value string of the
                same text; a date object

Untrusted input. A brush file comes from a stranger. `parse_table` checks the
size, the trailer, every offset, every count and every reference before it
reads what they point at, never allocates from a count it has not checked
against the bytes that remain, and refuses a file whose objects overlap.
`resolve` refuses a container that holds itself, nesting deeper than 64, and a
tree larger than the cap on a table. A file that is not a property list this
module reads raises `BplistError`; one over a cap of F3 raises `LimitExceeded`.
Nothing here opens a file or a connection.

Errors. The error classes of the whole codec live here, because every other
codec module can import this one. Each carries a `code`:

    BplistError     not_bytes  bad_magic  truncated  bad_trailer  offset_range
                    ref_range  overlap  bad_count  bad_marker  bad_string
                    unsupported  malformed  cycle  bad_key  bad_node  bad_table
                    bad_value  untyped_real  int_range  uid_range  bad_real
                    real_range  bad_date
    LimitExceeded   archive_bytes  plist_objects  plist_depth  (the cap's name
                    in spec.yaml `format.caps`)

Standard library only. Not a command.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from typing import Callable

MAGIC = b"bplist00"
HEADER_SIZE = len(MAGIC)
TRAILER_SIZE = 32

# The caps of F3 (spec.yaml `format.caps`: archive_bytes, plist_objects, plist_depth).
MAX_BYTES = 1 << 20
MAX_OBJECTS = 100_000
MAX_DEPTH = 64

INT_WIDTHS = (1, 2, 4, 8, 16)
REAL_WIDTHS = (4, 8)
MAX_UID_WIDTH = 8


# ── errors ───────────────────────────────────────────────────────────────────

class CodecError(ValueError):
    """The base of every error the file codec raises. `code` is a short fixed
    word a caller can test; `detail` is a sentence for a person.

    A ValueError, because what is wrong is always the data handed in."""

    def __init__(self, code, detail=""):
        super().__init__(code, detail)
        self.code = code
        self.detail = detail

    def __str__(self):
        return f"{self.code}: {self.detail}" if self.detail else str(self.code)


class BplistError(CodecError):
    """Bytes that are not a binary property list this module reads, or a value
    it cannot write."""


class ArchiveError(CodecError):
    """A property list that is not a keyed archive (raised by keyed_archive)."""


class BrushModelError(CodecError):
    """An archive that is not a brush, or a change a brush cannot take."""


class ContainerError(CodecError):
    """A `.brush` or `.brushset` file that cannot be read or written."""


class LimitExceeded(ContainerError):
    """Input over one of the caps of F3. `code` is the cap's name in spec.yaml."""


class PngError(CodecError):
    """An image that cannot be read or written."""


class PngUnsupported(PngError):
    """A valid image of a kind the standard-library reader does not decode."""


# ── logical values ───────────────────────────────────────────────────────────

def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BplistError("bad_real", f"a real is made from a number, not {type(value).__name__}")
    try:
        return float(value)
    except OverflowError:
        raise BplistError("real_range", f"{value!r} is too large for a real") from None


@dataclass(frozen=True)
class UID:
    """A keyed-archiver reference: the number of an entry of `$objects`."""

    value: int


@dataclass(frozen=True)
class Real:
    """A real number with its stored width: `bits` is 4 or 8 big-endian bytes.

    Two reals are equal when their bits are, so 0.0 and -0.0 differ and a
    4-byte 1.0 is not an 8-byte 1.0.
    """

    bits: bytes

    def __post_init__(self):
        if not isinstance(self.bits, bytes) or len(self.bits) not in REAL_WIDTHS:
            raise BplistError("bad_real", "a real is 4 or 8 bytes")

    @property
    def width(self):
        return len(self.bits)

    @property
    def value(self):
        return struct.unpack(">f" if len(self.bits) == 4 else ">d", self.bits)[0]

    @classmethod
    def f32(cls, value):
        """The 4-byte real nearest to `value`."""
        number = _number(value)
        try:
            return cls(struct.pack(">f", number))
        except (OverflowError, struct.error):
            raise BplistError("real_range", f"{value!r} does not fit a 4-byte real") from None

    @classmethod
    def f64(cls, value):
        """The 8-byte real of `value`."""
        return cls(struct.pack(">d", _number(value)))

    def __repr__(self):
        return f"Real.f{len(self.bits) * 8}({self.value!r})"


@dataclass(frozen=True)
class Date:
    """A date object: 8 bytes, a big-endian double of seconds since 2001-01-01."""

    bits: bytes

    def __post_init__(self):
        if not isinstance(self.bits, bytes) or len(self.bits) != 8:
            raise BplistError("bad_date", "a date is 8 bytes")

    @property
    def value(self):
        return struct.unpack(">d", self.bits)[0]


class PDict(list):
    """A dict as an ordered list of (key, value) pairs.

    The order is the order in the file and is written back. A hostile file may
    repeat a key; `get` and `set` then act on the first.

    A PDict is a list, so `isinstance(value, list)` is true of a dict as well
    as of an array, and `in` looks for a pair, not a key. Test for a PDict
    first, or ask `is_array`; ask `has` for a key.
    """

    def keys(self):
        return [key for key, _ in self]

    def values(self):
        return [value for _, value in self]

    def items(self):
        return list(self)

    def has(self, key):
        return any(k == key for k, _ in self)

    def get(self, key, default=None):
        for k, value in self:
            if k == key:
                return value
        return default

    def set(self, key, value):
        """Replace the value of `key` where it stands, or add the pair at the end."""
        for position, (k, _) in enumerate(self):
            if k == key:
                self[position] = (key, value)
                return
        self.append((key, value))

    def drop(self, key):
        """Remove the first pair with that key. True when there was one."""
        for position, (k, _) in enumerate(self):
            if k == key:
                del self[position]
                return True
        return False

    def __repr__(self):
        return f"PDict({list.__repr__(self)})"


def is_array(value):
    """True for the logical form of an array: a list that is not a PDict."""
    return isinstance(value, list) and not isinstance(value, PDict)


@dataclass
class ObjectTable:
    """A binary property list as its numbered objects.

    objects      one tuple per object, in number order:
                     ("bool", value)            ("int", width, value)
                     ("real", width, bits)      ("date", bits)
                     ("data", bytes)            ("ascii", text)
                     ("utf16", text)            ("uid", width, value)
                     ("array", refs)            ("dict", key_refs, value_refs)
    top          the number of the top object
    offset_size  bytes per entry of the offset table
    ref_size     bytes per object reference
    contiguous   set by parse_table: True when the file is laid out the plain
                 way (objects in number order with nothing between them, counts
                 written in their shortest form, an unused trailer of zeros),
                 which is exactly when serialize_table gives the file back
    """

    objects: list
    top: int = 0
    offset_size: int = 1
    ref_size: int = 1
    contiguous: bool = True


def byte_count(n):
    """The width the app's writer uses for a count, an offset or a reference."""
    if n < 1 << 8:
        return 1
    if n < 1 << 16:
        return 2
    if n < 1 << 32:
        return 4
    return 8


# ── reading ──────────────────────────────────────────────────────────────────

_FORMATS = {2: "H", 4: "I", 8: "Q"}


def _truncated(what):
    return BplistError("truncated", f"{what} runs past the end of the object area")


def _read_ints(data, start, count, width):
    """`count` big-endian unsigned ints of `width` bytes. The caller has
    already checked that they lie inside the data."""
    end = start + count * width
    if width == 1:
        return tuple(data[start:end])
    if width in _FORMATS:
        return struct.unpack(f">{count}{_FORMATS[width]}", data[start:end])
    return tuple(int.from_bytes(data[at:at + width], "big") for at in range(start, end, width))


def _read_count(data, position, limit, low):
    """The count in a marker's low half, or in the int that follows it."""
    if low != 0x0F:
        return low, position
    if position >= limit:
        raise _truncated("a count")
    marker = data[position]
    if marker >> 4 != 0x1 or (marker & 0x0F) > 3:
        raise BplistError("bad_count", f"a count is not an int (marker 0x{marker:02x})")
    width = 1 << (marker & 0x0F)
    end = position + 1 + width
    if end > limit:
        raise _truncated("a count")
    return int.from_bytes(data[position + 1:end], "big"), end


def _read_refs(data, position, count, ref_size, limit, n_objects):
    end = position + count * ref_size
    if end > limit:
        raise _truncated(f"a list of {count:,} references")
    refs = _read_ints(data, position, count, ref_size)
    if count and max(refs) >= n_objects:
        raise BplistError("ref_range", f"a reference to object {max(refs):,} of {n_objects:,}")
    return refs, end


def _parse_object(data, start, limit, ref_size, n_objects):
    """(node, end) for the object whose marker byte is at `start` < `limit`."""
    marker = data[start]
    high, low = marker >> 4, marker & 0x0F
    position = start + 1
    if high == 0x0:
        if low == 0x08:
            return ("bool", False), position
        if low == 0x09:
            return ("bool", True), position
        if low in (0x00, 0x0F):
            raise BplistError("unsupported", "a null or fill object")
        raise BplistError("bad_marker", f"marker 0x{marker:02x}")
    if high == 0x1:
        if low > 4:
            raise BplistError("bad_marker", f"an int of 2**{low} bytes")
        end = position + (1 << low)
        if end > limit:
            raise _truncated("an int")
        # 1, 2 and 4 bytes are unsigned; 8 and 16 are two's complement.
        return ("int", 1 << low, int.from_bytes(data[position:end], "big", signed=low >= 3)), end
    if high == 0x2:
        if low not in (2, 3):
            raise BplistError("bad_marker", f"a real of 2**{low} bytes")
        end = position + (1 << low)
        if end > limit:
            raise _truncated("a real")
        return ("real", 1 << low, data[position:end]), end
    if high == 0x3:
        if low != 3:
            raise BplistError("bad_marker", f"marker 0x{marker:02x}")
        end = position + 8
        if end > limit:
            raise _truncated("a date")
        return ("date", data[position:end]), end
    if high == 0x4:
        count, position = _read_count(data, position, limit, low)
        end = position + count
        if end > limit:
            raise _truncated(f"data of {count:,} bytes")
        return ("data", data[position:end]), end
    if high == 0x5:
        count, position = _read_count(data, position, limit, low)
        end = position + count
        if end > limit:
            raise _truncated(f"a string of {count:,} bytes")
        raw = data[position:end]
        if not raw.isascii():
            raise BplistError("bad_string", "an ASCII string holds a byte above 0x7f")
        return ("ascii", raw.decode("ascii")), end
    if high == 0x6:
        count, position = _read_count(data, position, limit, low)
        end = position + 2 * count
        if end > limit:
            raise _truncated(f"a string of {count:,} UTF-16 units")
        # surrogatepass keeps an unpaired surrogate, so the units are written back as read.
        return ("utf16", data[position:end].decode("utf-16-be", "surrogatepass")), end
    if high == 0x8:
        width = low + 1
        if width > MAX_UID_WIDTH:
            raise BplistError("bad_marker", f"a UID of {width} bytes")
        end = position + width
        if end > limit:
            raise _truncated("a UID")
        return ("uid", width, int.from_bytes(data[position:end], "big")), end
    if high == 0xA:
        count, position = _read_count(data, position, limit, low)
        refs, end = _read_refs(data, position, count, ref_size, limit, n_objects)
        return ("array", refs), end
    if high == 0xD:
        count, position = _read_count(data, position, limit, low)
        key_refs, position = _read_refs(data, position, count, ref_size, limit, n_objects)
        value_refs, end = _read_refs(data, position, count, ref_size, limit, n_objects)
        return ("dict", key_refs, value_refs), end
    if high in (0x7, 0xB, 0xC):
        raise BplistError("unsupported", "a set, an ordered set or a UTF-8 string")
    raise BplistError("bad_marker", f"marker 0x{marker:02x}")


def parse_table(data, *, max_objects=MAX_OBJECTS, max_bytes=MAX_BYTES):
    """The object table of a binary property list, exactly as stored.

    Raises BplistError for bytes that are not one, and LimitExceeded for a
    file larger than `max_bytes` or holding more than `max_objects` objects.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise BplistError("not_bytes", f"a property list is bytes, not {type(data).__name__}")
    data = bytes(data)
    size = len(data)
    if size > max_bytes:
        raise LimitExceeded("archive_bytes", f"{size:,} bytes; the cap is {max_bytes:,}")
    if data[:HEADER_SIZE] != MAGIC:
        raise BplistError("bad_magic", "the file does not begin `bplist00`")
    if size < HEADER_SIZE + 2 + TRAILER_SIZE:
        raise BplistError("truncated", f"{size} bytes cannot hold an object, a table and a trailer")
    trailer = size - TRAILER_SIZE
    offset_size, ref_size = data[trailer + 6], data[trailer + 7]
    n_objects, top, table_offset = struct.unpack(">QQQ", data[trailer + 8:])
    if not 1 <= offset_size <= 8 or not 1 <= ref_size <= 8:
        raise BplistError("bad_trailer", f"offset size {offset_size}, reference size {ref_size}")
    if n_objects < 1:
        raise BplistError("bad_trailer", "no objects")
    # Is the claimed table inside the file? Asked before anything is sized by
    # the claim, so a count of 2**60 costs nothing.
    if table_offset <= HEADER_SIZE or table_offset + n_objects * offset_size > trailer:
        raise BplistError("offset_range", f"an offset table for {n_objects:,} objects at "
                                          f"{table_offset:,} does not fit {size:,} bytes")
    if n_objects > max_objects:
        raise LimitExceeded("plist_objects", f"{n_objects:,} objects; the cap is {max_objects:,}")
    if top >= n_objects:
        raise BplistError("ref_range", f"the top object is {top:,} of {n_objects:,}")
    if n_objects - 1 >= 1 << (8 * ref_size):
        raise BplistError("bad_trailer", f"{n_objects:,} objects cannot be named in "
                                         f"{ref_size} byte(s)")
    offsets = _read_ints(data, table_offset, n_objects, offset_size)
    if min(offsets) < HEADER_SIZE or max(offsets) >= table_offset:
        raise BplistError("offset_range", "an object offset lies outside the object area")

    # Objects of an honest file do not overlap, so together they are no larger
    # than the object area. Holding a hostile one to that bounds the work: it
    # cannot point 100,000 offsets at one large array.
    budget = table_offset - HEADER_SIZE
    objects = []
    try:
        for start in offsets:
            node, end = _parse_object(data, start, table_offset, ref_size, n_objects)
            budget -= end - start
            if budget < 0:
                raise BplistError("overlap", "objects overlap one another")
            objects.append(node)
    except (struct.error, IndexError, UnicodeError, OverflowError) as exc:
        raise BplistError("malformed", f"{type(exc).__name__}: {exc}") from None
    table = ObjectTable(objects, top, offset_size, ref_size, False)
    try:
        table.contiguous = serialize_table(table) == data
    except BplistError:
        table.contiguous = False
    return table


def resolve(table, *, max_depth=MAX_DEPTH, max_objects=MAX_OBJECTS):
    """The logical tree of a table: plain values, PDict for a dict, list for an array.

    Every reference gets a value of its own, so changing one place in the tree
    never changes another. A container that holds itself raises BplistError.
    Containers nested deeper than `max_depth` raise LimitExceeded, and so does
    a tree of more than `max_objects` values and keys: the cap on a table is
    also the cap on what it unfolds to, which stops a small table of arrays
    that each name the next one twice from unfolding without end.
    """
    objects = table.objects
    count = len(objects)
    if not isinstance(table.top, int) or not 0 <= table.top < count:
        raise BplistError("ref_range", "the top object is not in the table")
    budget = [max_objects]
    on_path = set()

    def ref(number):
        if not isinstance(number, int) or not 0 <= number < count:
            raise BplistError("ref_range", f"a reference to object {number!r} of {count:,}")
        return number

    def build(number, depth):
        budget[0] -= 1
        if budget[0] < 0:
            raise LimitExceeded("plist_objects", f"the tree holds more than {max_objects:,} "
                                                 "values and keys")
        node = objects[number]
        kind = node[0]
        if kind in ("ascii", "utf16", "data", "bool"):
            return node[1]
        if kind in ("int", "uid"):
            return node[2] if kind == "int" else UID(node[2])
        if kind == "real":
            return Real(node[2])
        if kind == "date":
            return Date(node[1])
        if kind not in ("array", "dict"):
            raise BplistError("bad_node", f"an object of kind {kind!r}")
        if depth >= max_depth:
            raise LimitExceeded("plist_depth", f"containers nested deeper than {max_depth}")
        if number in on_path:
            raise BplistError("cycle", f"object {number:,} contains itself")
        on_path.add(number)
        if kind == "array":
            value = [build(ref(child), depth + 1) for child in node[1]]
        else:
            if len(node[1]) != len(node[2]):
                raise BplistError("bad_node", "a dict with unequal key and value lists")
            value = PDict()
            for key_ref, value_ref in zip(node[1], node[2]):
                key_node = objects[ref(key_ref)]
                if key_node[0] not in ("ascii", "utf16"):
                    raise BplistError("bad_key", f"a dict key of kind {key_node[0]!r}")
                budget[0] -= 1
                value.append((key_node[1], build(ref(value_ref), depth + 1)))
        on_path.discard(number)
        return value

    return build(table.top, 0)


def loads(data):
    """The logical tree of a binary property list."""
    return resolve(parse_table(data))


# ── writing ──────────────────────────────────────────────────────────────────

def _count_bytes(marker, count):
    """A marker byte with a count: in its low half when under 15, else as an int."""
    if count < 15:
        return bytes((marker | count,))
    if count < 1 << 8:
        return bytes((marker | 0x0F, 0x10, count))
    if count < 1 << 16:
        return bytes((marker | 0x0F, 0x11)) + count.to_bytes(2, "big")
    if count < 1 << 32:
        return bytes((marker | 0x0F, 0x12)) + count.to_bytes(4, "big")
    return bytes((marker | 0x0F, 0x13)) + count.to_bytes(8, "big")


def _pack_ints(values, width):
    if width == 1:
        return bytes(values)
    if width in _FORMATS:
        return struct.pack(f">{len(values)}{_FORMATS[width]}", *values)
    return b"".join(value.to_bytes(width, "big") for value in values)


def _encode_node(node, ref_size, n_objects):
    kind = node[0]
    if kind == "bool":
        return b"\x09" if node[1] else b"\x08"
    if kind == "int":
        _, width, value = node
        if width not in INT_WIDTHS:
            raise BplistError("bad_node", f"an int of {width} bytes")
        return bytes((0x10 | INT_WIDTHS.index(width),)) + value.to_bytes(width, "big", signed=width >= 8)
    if kind == "real":
        _, width, bits = node
        if width not in REAL_WIDTHS or len(bits) != width:
            raise BplistError("bad_node", f"a real of {width} bytes")
        return (b"\x22" if width == 4 else b"\x23") + bits
    if kind == "date":
        if len(node[1]) != 8:
            raise BplistError("bad_node", "a date that is not 8 bytes")
        return b"\x33" + node[1]
    if kind == "data":
        return _count_bytes(0x40, len(node[1])) + node[1]
    if kind == "ascii":
        raw = node[1].encode("ascii")
        return _count_bytes(0x50, len(raw)) + raw
    if kind == "utf16":
        raw = node[1].encode("utf-16-be", "surrogatepass")
        return _count_bytes(0x60, len(raw) // 2) + raw
    if kind == "uid":
        _, width, value = node
        if not 1 <= width <= MAX_UID_WIDTH:
            raise BplistError("bad_node", f"a UID of {width} bytes")
        return bytes((0x80 | (width - 1),)) + value.to_bytes(width, "big")
    if kind == "array":
        refs = node[1]
        if refs and not 0 <= min(refs) <= max(refs) < n_objects:
            raise BplistError("ref_range", "an array names an object that is not in the table")
        return _count_bytes(0xA0, len(refs)) + _pack_ints(refs, ref_size)
    if kind == "dict":
        _, key_refs, value_refs = node
        if len(key_refs) != len(value_refs):
            raise BplistError("bad_node", "a dict with unequal key and value lists")
        refs = tuple(key_refs) + tuple(value_refs)
        if refs and not 0 <= min(refs) <= max(refs) < n_objects:
            raise BplistError("ref_range", "a dict names an object that is not in the table")
        return _count_bytes(0xD0, len(key_refs)) + _pack_ints(refs, ref_size)
    raise BplistError("bad_node", f"an object of kind {kind!r}")


def _serialize(objects, top, offset_size, ref_size):
    """The file for a list of nodes. `offset_size` None means "by the writer's rule"."""
    count = len(objects)
    if count < 1:
        raise BplistError("bad_table", "a property list holds at least one object")
    if not isinstance(top, int) or not 0 <= top < count:
        raise BplistError("ref_range", "the top object is not in the table")
    if not isinstance(ref_size, int) or not 1 <= ref_size <= 8 or count - 1 >= 1 << (8 * ref_size):
        raise BplistError("bad_table", f"{count:,} objects cannot be named in {ref_size!r} byte(s)")
    try:
        chunks = [_encode_node(node, ref_size, count) for node in objects]
    except CodecError:
        raise
    except (TypeError, ValueError, IndexError, OverflowError, AttributeError, struct.error) as exc:
        raise BplistError("bad_node", f"{type(exc).__name__}: {exc}") from None
    offsets = []
    position = HEADER_SIZE
    for chunk in chunks:
        offsets.append(position)
        position += len(chunk)
    if offset_size is None:
        offset_size = byte_count(position)
    if not isinstance(offset_size, int) or not 1 <= offset_size <= 8 \
            or offsets[-1] >= 1 << (8 * offset_size):
        raise BplistError("bad_table", f"an offset of {offsets[-1]:,} does not fit "
                                       f"{offset_size!r} byte(s)")
    trailer = bytes(6) + bytes((offset_size, ref_size)) + struct.pack(">QQQ", count, top, position)
    return b"".join([MAGIC] + chunks + [_pack_ints(offsets, offset_size), trailer])


def serialize_table(table):
    """The bytes of a table: objects in number order from offset 8, the offset
    table, then the trailer. The table's own offset and reference sizes are kept."""
    return _serialize(table.objects, table.top, table.offset_size, table.ref_size)


def _int_width(value):
    if value < 0:
        if value < -(1 << 63):
            raise BplistError("int_range", f"{value} does not fit 8 bytes")
        return 8
    if value < 1 << 8:
        return 1
    if value < 1 << 16:
        return 2
    if value < 1 << 32:
        return 4
    if value < 1 << 63:
        return 8
    if value < 1 << 64:
        return 16           # as the standard library writes it; never seen in a brush
    raise BplistError("int_range", f"{value} does not fit a property list")


def _is_whole(real):
    value = real.value
    return math.isfinite(value) and value == math.trunc(value)


def _flatten(value, shared, max_depth, max_objects):
    """The numbered objects the app's writer makes of a logical value; the top is object 0."""
    objects = []
    key_index, string_index, int_index, real_index = {}, {}, {}, {}
    first_bool, first_uid = {}, {}
    budget = [max_objects]

    def spend():
        """The same cap `resolve` puts on a tree: its values and keys, counted
        where they stand. So whatever is written here can be read back."""
        budget[0] -= 1
        if budget[0] < 0:
            raise LimitExceeded("plist_objects", f"more than {max_objects:,} values and keys")

    def add(node):
        objects.append(node)
        return len(objects) - 1

    def string_node(text):
        return ("ascii", text) if text.isascii() else ("utf16", text)

    def key(text):
        spend()
        if not isinstance(text, str):
            raise BplistError("bad_key", f"a dict key must be text, not {type(text).__name__}")
        number = key_index.get(text)
        if number is None:
            number = key_index[text] = add(string_node(text))
        return number

    def walk(item, depth):
        spend()
        if isinstance(item, bool):
            return first_bool.setdefault(item, add(("bool", item)))
        if isinstance(item, int):
            number = int_index.get(item)
            if number is None:
                number = int_index[item] = add(("int", _int_width(item), item))
            return number
        if isinstance(item, Real):
            if item.width != 4 or not _is_whole(item):
                return add(("real", item.width, item.bits))
            number = real_index.get(item.bits)
            if number is None:
                number = real_index[item.bits] = add(("real", 4, item.bits))
            return number
        if isinstance(item, str):
            if not shared(item):
                return add(string_node(item))
            number = string_index.get(item)
            if number is None:
                number = string_index[item] = add(string_node(item))
            return number
        if isinstance(item, UID):
            if not isinstance(item.value, int) or isinstance(item.value, bool) \
                    or not 0 <= item.value < 1 << 64:
                raise BplistError("uid_range", f"{item.value!r} is not a UID value")
            number = add(("uid", byte_count(item.value), item.value))
            return first_uid.setdefault(item.value, number)
        if isinstance(item, (bytes, bytearray)):
            return add(("data", bytes(item)))
        if isinstance(item, Date):
            return add(("date", item.bits))
        if isinstance(item, (PDict, dict, list, tuple)):
            if depth >= max_depth:
                raise LimitExceeded("plist_depth", f"containers nested deeper than {max_depth}")
            number = add(None)
            if isinstance(item, (PDict, dict)):
                pairs = list(item.items()) if isinstance(item, dict) else list(item)
                if any(not isinstance(pair, (tuple, list)) or len(pair) != 2 for pair in pairs):
                    raise BplistError("bad_value", "a PDict holds (key, value) pairs")
                key_refs = tuple(key(k) for k, _ in pairs)
                value_refs = tuple(walk(v, depth + 1) for _, v in pairs)
                objects[number] = ("dict", key_refs, value_refs)
            else:
                objects[number] = ("array", tuple(walk(v, depth + 1) for v in item))
            return number
        if isinstance(item, float):
            raise BplistError("untyped_real", "wrap a float in Real.f32 or Real.f64: "
                                              "the width is part of the file")
        raise BplistError("unsupported", f"a {type(item).__name__} has no property-list form")

    walk(value, 0)
    return objects


def flatten(value, *, shared: Callable[[str], bool], max_depth=MAX_DEPTH,
            max_objects=MAX_OBJECTS):
    """The object table the app's writer makes of a logical value.

    `shared(text)` says whether equal value strings share one object. The top
    value is object 0, a reference is as wide as the number of objects needs
    and an offset as wide as the offset of the table needs. See the module
    text for the rules.
    """
    objects = _flatten(value, shared, max_depth, max_objects)
    ref_size = byte_count(len(objects))
    size = HEADER_SIZE + sum(len(_encode_node(node, ref_size, len(objects))) for node in objects)
    return ObjectTable(objects, 0, byte_count(size), ref_size, True)


def dumps(value, *, shared: Callable[[str], bool]):
    """The bytes the app's writer makes of a logical value."""
    objects = _flatten(value, shared, MAX_DEPTH, MAX_OBJECTS)
    return _serialize(objects, 0, None, byte_count(len(objects)))
