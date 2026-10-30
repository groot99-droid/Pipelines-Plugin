"""Write a zip the way the drawing app writes its own brush files.

    data = zip_writer.write_zip([("Brush.archive", archive), ("Shape.png", shape)])

`write_zip` takes the entries in the order they are to be stored, each a
(name, bytes) pair, and returns the bytes of a finished zip. It writes no file.
`check_name` says, before anything is built, whether a name can be stored,
`is_text` is the rule behind one header bit, and `form_of` names the form of an
entry read from a file. That is the whole module.

This is the one zip writer of the tool (docs/CONTRACTS.md, F3 "Writing"): the
file codec's `container.py` calls `write_zip` and writes no zip of its own.

Why not `zipfile`: every entry of every brush file in the library carries
header values that `zipfile` cannot write (it stores flag bits of its own and an
external attribute of its own). This writer stores what was observed in the
library's 112 files, so that a container made here from such a file differs
from the app's own in nothing but what was changed.

Every entry, whatever its form:

    field                    value    in the header as
    version needed           20       extract_version
    version made by          0        create_version 0, create_system 0
    external attributes      0
    internal attributes      0 or 1   1 when the entry is text (see below)
    extra field              none     in the local header and the directory
    entry comment            none
    zip comment              none
    directory entries        none     a folder exists only as part of a name
    data descriptor          none     sizes and CRC are in the local header
    zip64                    never    a zip too large for the plain format is refused

Forms. An entry is stored in one of three forms, each read off real files
(FORMS; 3,319 entries in the 112 files of the library):

    form      method   flag bits  data                          seen in
    fast      8        0x0006     raw deflate, zlib level 1     110 files, 3,003 entries: every
                                                                user file and 38 official sets
    normal    8        0x0000     raw deflate, zlib level 6     Earth and Chinese Calligraphy,
                                                                216 entries
    stored    0        0x0000     the bytes themselves          the same two sets, 100 entries,
                                                                every one a zero-byte `.empty`

`fast` is the default and is what a member made here is written in. The flag
bits are the deflate "speed" hint (0x0006 "super fast", 0x0000 "normal"), and
in the library they agree with the level the stream was made at: given each
entry's data and date, level 1 rebuilds every `fast` entry byte for byte and
level 6 every `normal` one, with zlib's default window and memory level (zlib
1.3.1). Another zlib build may give other compressed bytes for the same data,
so never compare compressed bytes across machines; compare what is read back.
`stored` was only ever seen on empty data; this writer stores any data that
way when asked, because the header of a stored entry has no field left to
choose (its sizes are equal and its method is 0).

`form_of(method, flag_bits)` names the form of an entry as it was read, or
gives None for one no file has shown (deflate with another speed hint, a
method other than 0 and 8). A caller writes such an entry in the default form.

Internal attribute. The app's writer copies zlib's guess about the data into
bit 0: its `brushset.plist` entries, which are XML text, carry 1, and every
archive and image carries 0 (in all three forms). zlib guesses from the byte
values it meets: any of 0 to 6, 14 to 25 or 28 to 31 means binary; otherwise a
tab, a line feed, a carriage return or any byte from 32 up means text; data
with neither (empty data, for one) is binary. zlib looks at the first block it
writes; this writer applies the same rule to the whole entry.

Dates. An entry's date is `date_time`, a (year, month, day, hour, minute,
second) tuple, unless the entry gives its own as a third item (None there means
`date_time`). The default is a fixed date, so the same input gives the same
bytes. The format keeps two-second steps: an odd second is stored as the even
one before it. One date that is not a calendar date is accepted, because the
app writes it: every stored `.empty` of Earth and Chinese Calligraphy carries
the date field 32 and the time field 0, which zipfile reads back as
`ZERO_DATE`, (1980, 1, 0, 0, 0, 0). Every other impossible date is refused.

Names. Every entry name in the library is ASCII, and no entry carries the
UTF-8 name flag (0x0800), so a name that is not ASCII is refused, not written:
how the app spells one has not been read off a real file.

What is refused, with ZipWriteError: a name that is empty, not ASCII, holds a
control character or a backslash, starts with `/` or a drive letter, ends with
`/`, or has an empty, `.` or `..` part; the same name twice; data that is not
bytes; a form that is not one of FORMS; a date outside 1980 to 2107; more
entries or bytes than the plain zip format holds.

Standard library only. Not a command.
"""

from __future__ import annotations

import re
import struct
import zlib

METHOD_DEFLATE = 8
METHOD_STORED = 0
FLAG_BITS = 0x0006
EXTRACT_VERSION = 20
CREATE_VERSION = 0
CREATE_SYSTEM = 0
EXTERNAL_ATTR = 0
DEFLATE_LEVEL = 1

# The three forms an entry is stored in: (method, flag bits, zlib level).
FORMS = {
    "fast": (METHOD_DEFLATE, FLAG_BITS, DEFLATE_LEVEL),
    "normal": (METHOD_DEFLATE, 0x0000, 6),
    "stored": (METHOD_STORED, 0x0000, None),
}
DEFAULT_FORM = "fast"

# The date an entry gets when none is given: fixed, so output is repeatable.
DEFAULT_DATE_TIME = (2020, 1, 1, 0, 0, 0)
# The one date that is not a calendar date and is written all the same: what
# zipfile reads from the date field 32 and the time field 0.
ZERO_DATE = (1980, 1, 0, 0, 0, 0)

# The plain format's ceilings. Each field's all-ones value means "see the zip64
# record", which this writer never writes.
MAX_ENTRIES = 0xFFFF - 1
MAX_BYTES = 0xFFFFFFFF - 1
MAX_NAME = 0xFFFF

LOCAL_SIGNATURE = b"PK\x03\x04"
CENTRAL_SIGNATURE = b"PK\x01\x02"
END_SIGNATURE = b"PK\x05\x06"

_LOCAL = struct.Struct("<4sHHHHHIIIHH")
_CENTRAL = struct.Struct("<4sBBHHHHHIIIHHHHHII")
_END = struct.Struct("<4sHHHHIIH")

# zlib's rule for telling text from binary (trees.c, detect_data_type).
_BINARY_BYTES = bytes(range(0, 7)) + bytes(range(14, 26)) + bytes(range(28, 32))
_TEXT_BYTES = bytes((9, 10, 13)) + bytes(range(32, 256))
_NOT_BINARY = bytes(sorted(set(range(256)) - set(_BINARY_BYTES)))
_NOT_TEXT = bytes(sorted(set(range(256)) - set(_TEXT_BYTES)))

_DRIVE = re.compile(r"[A-Za-z]:")


class ZipWriteError(ValueError):
    """An entry this writer will not store, or a zip too large for the format."""


def is_text(data):
    """True when zlib would call these bytes text. Decides the internal attribute."""
    if data.translate(None, _NOT_BINARY):
        return False
    return bool(data.translate(None, _NOT_TEXT))


def form_of(method, flag_bits):
    """The name of the form an entry was read in (its compression method and
    flag bits, as zipfile's `compress_type` and `flag_bits` give them), or None
    for a form no library file has shown. Bits other than the speed hint (bit 0
    encryption, bit 3 data descriptor, bit 11 UTF-8 name) are not part of a
    form: an entry that carries them is None."""
    for name, (form_method, form_flags, _) in FORMS.items():
        if method == form_method and flag_bits == form_flags:
            return name
    return None


def check_name(name):
    """The entry name as ASCII bytes, or ZipWriteError saying what is wrong with it."""
    if not isinstance(name, str) or not name:
        raise ZipWriteError(f"an entry name must be a non-empty string, not {name!r}")
    if not name.isascii() or any(ord(ch) < 32 or ord(ch) == 127 for ch in name):
        raise ZipWriteError(f"an entry name must be printable ASCII: {name!r}")
    if "\\" in name:
        raise ZipWriteError(f"an entry name may not hold a backslash: {name!r}")
    if name.startswith("/") or _DRIVE.match(name):
        raise ZipWriteError(f"an entry name may not be absolute: {name!r}")
    if name.endswith("/"):
        raise ZipWriteError(f"a folder is never an entry of its own: {name!r}")
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise ZipWriteError(f"an entry name may not hold an empty, `.` or `..` part: {name!r}")
    if len(name) > MAX_NAME:
        raise ZipWriteError(f"an entry name of {len(name)} characters is too long")
    return name.encode("ascii")


def _dos_date_time(date_time):
    """(time, date) as the two 16-bit header fields."""
    try:
        year, month, day, hour, minute, second = (int(part) for part in date_time)
    except (TypeError, ValueError):
        raise ZipWriteError(f"a date is (year, month, day, hour, minute, second), "
                            f"not {date_time!r}") from None
    if (year, month, day, hour, minute, second) == ZERO_DATE:
        return 0, 32
    if not (1980 <= year <= 2107 and 1 <= month <= 12 and 1 <= day <= 31
            and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
        raise ZipWriteError(f"a zip cannot hold the date {date_time!r}")
    return (hour << 11) | (minute << 5) | (second // 2), ((year - 1980) << 9) | (month << 5) | day


def _pack(data, level):
    """The stored form of `data`: a raw deflate stream at `level`, as the app's
    writer makes it, or the bytes themselves for level None."""
    if level is None:
        return data
    compressor = zlib.compressobj(level, zlib.DEFLATED, -zlib.MAX_WBITS)
    return compressor.compress(data) + compressor.flush()


def write_zip(entries, *, date_time=DEFAULT_DATE_TIME):
    """The bytes of a zip holding `entries`, in the order given.

    entries     an iterable of (name, data), (name, data, date_time) or
                (name, data, date_time, form). `name` is the full entry name
                with `/` between folders; `data` is bytes, a bytearray or a
                memoryview; a date_time of None is `date_time` below; `form`
                is a key of FORMS, None meaning DEFAULT_FORM.
    date_time   the date of every entry that does not give its own.

    Raises ZipWriteError and returns nothing partial. An empty list gives a
    valid zip with no entries.
    """
    default_stamp = _dos_date_time(date_time)
    seen = set()
    body = []
    directory = []
    offset = 0
    for entry in entries:
        if not isinstance(entry, (tuple, list)) or len(entry) not in (2, 3, 4):
            raise ZipWriteError("an entry is (name, data), (name, data, date_time) or "
                                "(name, data, date_time, form)")
        name = check_name(entry[0])
        if name in seen:
            raise ZipWriteError(f"the entry name {entry[0]!r} is given twice")
        seen.add(name)
        if not isinstance(entry[1], (bytes, bytearray, memoryview)):
            raise ZipWriteError(f"the data of {entry[0]!r} must be bytes, "
                                f"not {type(entry[1]).__name__}")
        data = bytes(entry[1])
        own_date = entry[2] if len(entry) > 2 else None
        time_field, date_field = default_stamp if own_date is None else _dos_date_time(own_date)
        form = entry[3] if len(entry) > 3 and entry[3] is not None else DEFAULT_FORM
        if not isinstance(form, str) or form not in FORMS:
            raise ZipWriteError(f"the form of {entry[0]!r} is one of {', '.join(FORMS)}, "
                                f"not {form!r}")
        method, flag_bits, level = FORMS[form]
        packed = _pack(data, level)
        crc = zlib.crc32(data) & 0xFFFFFFFF
        if len(data) > MAX_BYTES or len(packed) > MAX_BYTES or offset > MAX_BYTES:
            raise ZipWriteError(f"{entry[0]!r} does not fit a zip without zip64")
        if len(directory) >= MAX_ENTRIES:
            raise ZipWriteError(f"more than {MAX_ENTRIES:,} entries do not fit a zip without zip64")
        local = _LOCAL.pack(LOCAL_SIGNATURE, EXTRACT_VERSION, flag_bits, method,
                            time_field, date_field, crc, len(packed), len(data), len(name), 0)
        directory.append(_CENTRAL.pack(
            CENTRAL_SIGNATURE, CREATE_VERSION, CREATE_SYSTEM, EXTRACT_VERSION, flag_bits,
            method, time_field, date_field, crc, len(packed), len(data), len(name),
            0, 0, 0, 1 if is_text(data) else 0, EXTERNAL_ATTR, offset) + name)
        body += [local, name, packed]
        offset += len(local) + len(name) + len(packed)
    central = b"".join(directory)
    if offset > MAX_BYTES or len(central) > MAX_BYTES:
        raise ZipWriteError("the zip does not fit the format without zip64")
    end = _END.pack(END_SIGNATURE, 0, 0, len(directory), len(directory), len(central), offset, 0)
    return b"".join(body) + central + end
