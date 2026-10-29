"""Write hub.ico from tokens.json. Standard library only.

    python studio/hub/launcher/make_icon.py [OUT]

A 32x32 icon: the ground colour with one accent square, the studio's own
mark reduced to its two colours. The colours come from tokens.json
(`color.bg.base` and the first accent), so a retheme changes the icon by
re-running this. Install-Shortcut.ps1 runs it when hub.ico is missing.
"""

import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = HERE.parent.parent / "vault" / "_Context" / "brand" / "tokens.json"
SIZE = 32


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def colours(tokens_path=TOKENS):
    tokens = json.loads(Path(tokens_path).read_text(encoding="utf-8"))
    color = tokens["color"]
    ground = hex_rgb(color["bg"]["base"])
    accent = hex_rgb(next(iter(color["accent"].values())))
    return ground, accent


def ico_bytes(ground, accent, size=SIZE):
    """One 32-bit BGRA image in a BMP container, as .ico expects."""
    rows = []
    inset, span = size // 4, size // 2
    for y in range(size - 1, -1, -1):  # BMP rows run bottom-up
        row = bytearray()
        for x in range(size):
            inside = inset <= x < inset + span and inset <= y < inset + span
            r, g, b = accent if inside else ground
            row += bytes((b, g, r, 255))
        rows.append(bytes(row))
    pixels = b"".join(rows)
    mask = b"\x00" * (size * size // 8)  # every pixel opaque
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, len(pixels) + len(mask), 0, 0, 0, 0)
    image = header + pixels + mask
    directory = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(image), 6 + 16)
    return directory + entry + image


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = Path(argv[0]) if argv else HERE / "hub.ico"
    ground, accent = colours()
    out.write_bytes(ico_bytes(ground, accent))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
