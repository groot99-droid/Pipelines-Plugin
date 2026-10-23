"""The interface: design tokens, palettes, UI copy, screens and reference screenshots.

Tokens are CSS custom properties with the profile's prefix, read from the token files (only the
values are kept; a value that links to a file is skipped, an inline data: URI is kept). A palette file is a JSON object whose string values
are colours. Copy is every `'key': 'text'` pair in the copy files. Screens are files matched by
the screen globs; screenshots are images, with PNG size read from the header.
"""

import json
import re
import struct

from .common import Part, glob, read, rel

DECL = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);(?:\s*/\*(.*?)\*/)?")
HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")
COPY = re.compile(r"""^\s*['"]([\w.\-]+)['"]\s*:\s*(['"`])((?:\\.|(?!\2).)*)\2""", re.MULTILINE)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return [w, h]


def colours(data, prefix=""):
    if isinstance(data, dict):
        for k, v in data.items():
            yield from colours(v, f"{prefix}{k}." if not prefix else f"{prefix}{k}.")
    elif isinstance(data, str) and HEX.match(data):
        yield prefix.rstrip("."), data


def css_tokens(text, prefix):
    out = {}
    body = re.sub(r"@font-face\s*{[^}]*}", "", text)
    for m in DECL.finditer(body):
        name, value, note = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        # Inline data: URIs (an SVG frame, a grain) are the game's own values; links to files are not.
        if not name.startswith(prefix) or re.search(r"url\(\s*(?!['\"]?data:)", value):
            continue
        out.setdefault(name, {"value": value, "note": note})
    return out


def extract(game, profile):
    spec = profile.get("ui")
    part = Part()
    if not spec:
        return part
    prefix = spec.get("token_prefix", "--")
    for path in glob(game, spec.get("token_files", [])):
        relpath = rel(game, path)
        text = read(path)
        for name, tok in css_tokens(text, prefix).items():
            line = text[: text.find(name + ":")].count("\n") + 1
            part.node(f"token:{name}", "token", "ui", name, text=tok["note"],
                      source={"path": relpath, "line": line},
                      meta={"value": tok["value"], "group": token_group(name, prefix)})
    for path in glob(game, spec.get("palettes", [])):
        relpath = rel(game, path)
        try:
            data = json.loads(read(path))
        except ValueError:
            part.notes.append(f"{relpath}: palette is not JSON")
            continue
        for name, value in colours(data):
            part.node(f"colour:{name}", "colour", "ui", name, source={"path": relpath, "line": 1},
                      meta={"value": value})
    copy_total = 0
    for path in glob(game, spec.get("copy", []), spec.get("copy_exclude", ())):
        relpath = rel(game, path)
        text = read(path)
        for m in COPY.finditer(text):
            key, value = m.group(1), m.group(3)
            line = text[: m.start()].count("\n") + 1
            part.node(f"copy:{key}", "copy", "ui", key, text=value,
                      source={"path": relpath, "line": line}, meta={"file": path.stem})
            copy_total += 1
    for group in spec.get("screens", []):
        for path in glob(game, group["globs"], group.get("exclude", ())):
            relpath = rel(game, path)
            text = read(path)
            first = next((l.strip(" /*") for l in text.splitlines() if l.strip().startswith(("//", "/**", " *"))), "")
            part.node(f"screen:{group['id']}/{path.stem}", "screen", "ui", path.stem,
                      text=first, source={"path": relpath, "line": 1},
                      meta={"layer": group["id"], "lines": text.count("\n")})
    for path in glob(game, spec.get("screenshots", [])):
        relpath = rel(game, path)
        part.node(f"shot:{path.stem}", "screenshot", "ui", path.stem, source={"path": relpath, "line": 1},
                  meta={"size": png_size(path) if path.suffix.lower() == ".png" else None})
    if copy_total:
        part.notes.append(f"{copy_total} copy strings")
    return part


def token_group(name, prefix):
    rest = name[len(prefix):]
    for group in ("font", "text", "display", "space", "radius", "shadow", "dur", "ease", "z", "glass",
                  "night", "faction", "frame", "on", "glow", "weight", "tracking", "leading"):
        if rest == group or rest.startswith(group + "-"):
            return group
    return "colour" if rest.endswith("-rgb") or "-" not in rest else rest.split("-")[0]
