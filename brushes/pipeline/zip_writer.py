"""Write a zip the way the drawing app writes its own brush files.

    data = zip_writer.write_zip([("Brush.archive", archive), ("Shape.png", shape)])

`write_zip` takes the entries in the order they are to be stored, each a
(name, bytes) pair, and returns the bytes of a finished zip. It writes no file.
`check_name` says, before anything is built, whether a name can be stored, and
`is_text` is the rule behind one header bit. That is the whole module.

This is the one zip writer of the tool (docs/CONTRACTS.md, F3 "Writing"): the
file codec's `container.py` calls `write_zip` and writes no zip of its own.

Why not `zipfile`: every entry of every brush file in library/user/ carries the
same header values, and `zipfile` cannot write two of them (it stores flag bits
0 and an external attribute of its own). This writer stores what was observed
there, so that a container made here from such a file differs from the app's
own in the entry dates and nothing else:

    field                    value    in the header as
    compression method       8        deflate, a raw stream (no zlib wrapper)
    general purpose flags    0x0006   the "fastest" hint; no data descriptor,
                                      no encryption, no UTF-8 name flag
    version needed           20       extract_version
    version made by          0        create_version 0, create_system 0
    external attributes      0
    internal attributes      0 or 1   1 when the entry is text (see below)
    extra field              none     in the local header and the directory
    entry comment            none
    zip comment              none
    directory entries        none     a folder exists only as part of a name
    zip64                    never    a zip too large for the plain format is refused

The deflate stream is made at level 1 with zlib's default window and memory
level. The files in library/user/ are made the same way: given the entries of
one of them and their dates, this writer returned that file byte for byte, for
all 72 of them (zlib 1.3.1). Another zlib build may give other compressed bytes
for the same data, so never compare compressed bytes across machines; compare
what is read back.

What that proof does not cover. It was run on library/user/ only; the official
sets were not on disk. Two of them (Earth, Chinese Calligraphy) are reported to
hold entries stored without compression (method 0). This writer has no stored
mode: it writes every entry as deflate, so a container made from such a source
differs from it in the method of those entries as well as in the dates. What is
read back is the same bytes either way. A stored mode, and any entry name that
is not ASCII, are added only once their header values (the method, the flag
bits, the name encoding) have been read from a real file: nothing here is
guessed. Until then a name that is not ASCII is refused, not written.

Internal attribute. The app's writer copies zlib's guess about the data into
bit 0: its `brushset.plist` entries, which are XML text, carry 1, and every
archive and image carries 0. zlib guesses from the byte values it meets: any of
0 to 6, 14 to 25 or 28 to 31 means binary; otherwise a tab, a line feed, a
carriage return or any byte from 32 up means text; data with neither (empty
data, for one) is binary. zlib looks at the first block it writes; this writer
applies the same rule to the whole entry.

Dates. An entry's date is `date_time`, a (year, month, day, hour, minute,
second) tuple, unless the entry gives its own as a third item. The default is a
fixed date, so the same input gives the same bytes. The format keeps two-second
steps: an odd second is stored as the even one before it.

What is refused, with ZipWriteError: a name that is empty, not ASCII, holds a
control character or a backslash, starts with `/` or a drive letter, ends with
`/`, or has an empty, `.` or `..` part; the same name twice; data that is not
bytes; a date outside 1980 to 2107; more entries or bytes than the plain zip
format holds.

Standard library only. Not a command.
"""

from __future__ import annotations

import re
import struct
import zlib

METHOD_DEFLATE = 8
FLAG_BITS = 0x0006
EXTRACT_VERSION = 20
CREATE_VERSION = 0
CREATE_SYSTEM = 0
EXTERNAL_ATTR = 0
DEFLATE_LEVEL = 1

# The date an entry gets when none is given: fixed, so output is repeatable.
DEFAULT_DATE_TIME = (2020, 1, 1, 0, 0, 0)

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
    if not (1980 <= year <= 2107 and 1 <= month <= 12 and 1 <= day <= 31
            and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
        raise ZipWriteError(f"a zip cannot hold the date {date_time!r}")
    return (hour << 11) | (minute << 5) | (second // 2), ((year - 1980) << 9) | (month << 5) | day


def _deflate(data):
    """A raw deflate stream of `data`, as the app's writer makes it."""
    compressor = zlib.compressobj(DEFLATE_LEVEL, zlib.DEFLATED, -zlib.MAX_WBITS)
    return compressor.compress(data) + compressor.flush()


def write_zip(entries, *, date_time=DEFAULT_DATE_TIME):
    """The bytes of a zip holding `entries`, in the order given.

    entries     an iterable of (name, data) or (name, data, date_time). `name`
                is the full entry name with `/` between folders; `data` is
                bytes, a bytearray or a memoryview.
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
        if not isinstance(entry, (tuple, list)) or len(entry) not in (2, 3):
            raise ZipWriteError("an entry is (name, data) or (name, data, date_time)")
        name = check_name(entry[0])
        if name in seen:
            raise ZipWriteError(f"the entry name {entry[0]!r} is given twice")
        seen.add(name)
        if not isinstance(entry[1], (bytes, bytearray, memoryview)):
            raise ZipWriteError(f"the data of {entry[0]!r} must be bytes, "
                                f"not {type(entry[1]).__name__}")
        data = bytes(entry[1])
        time_field, date_field = default_stamp if len(entry) == 2 else _dos_date_time(entry[2])
        packed = _deflate(data)
        crc = zlib.crc32(data) & 0xFFFFFFFF
        if len(data) > MAX_BYTES or len(packed) > MAX_BYTES or offset > MAX_BYTES:
            raise ZipWriteError(f"{entry[0]!r} does not fit a zip without zip64")
        if len(directory) >= MAX_ENTRIES:
            raise ZipWriteError(f"more than {MAX_ENTRIES:,} entries do not fit a zip without zip64")
        local = _LOCAL.pack(LOCAL_SIGNATURE, EXTRACT_VERSION, FLAG_BITS, METHOD_DEFLATE,
                            time_field, date_field, crc, len(packed), len(data), len(name), 0)
        directory.append(_CENTRAL.pack(
            CENTRAL_SIGNATURE, CREATE_VERSION, CREATE_SYSTEM, EXTRACT_VERSION, FLAG_BITS,
            METHOD_DEFLATE, time_field, date_field, crc, len(packed), len(data), len(name),
            0, 0, 0, 1 if is_text(data) else 0, EXTERNAL_ATTR, offset) + name)
        body += [local, name, packed]
        offset += len(local) + len(name) + len(packed)
    central = b"".join(directory)
    if offset > MAX_BYTES or len(central) > MAX_BYTES:
        raise ZipWriteError("the zip does not fit the format without zip64")
    end = _END.pack(END_SIGNATURE, 0, 0, len(directory), len(directory), len(central), offset, 0)
    return b"".join(body) + central + end
