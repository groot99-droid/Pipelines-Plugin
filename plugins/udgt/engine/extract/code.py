"""Source code: per-area inventory, test counts, and named anchors.

An area is a set of globs (client, server, shared...). The inventory counts files and lines, and
test cases in files matching the area's `tests` globs. An anchor pulls an ordered list out of one
file without running it:

- `object-keys`: the keys of the object literal that starts at the `start` line (e.g. an enum).
- `calls`: the calls matching `pattern` inside the block that starts at `start`, in order
  (e.g. a fixed tick order), with each line's trailing `//` comment kept.
- `matches`: every match of `pattern` in the file (first group), in order.
"""

import re

from .common import Part, glob, read, rel

KEY = re.compile(r"^\s*(?:/\*\*.*\*/\s*)?['\"]?([A-Za-z_$][\w$]*)['\"]?\s*:")
TEST = re.compile(r"^\s*(?:it|test)(?:\.each\([^)]*\))?\(\s*['\"`]", re.MULTILINE)


def block(lines, start):
    """Lines from the first line containing `start` up to the brace that closes it."""
    for i, line in enumerate(lines):
        if start in line:
            depth = 0
            out = []
            for j in range(i, len(lines)):
                out.append((j + 1, lines[j]))
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0 and j > i:
                    return i + 1, out
                if depth <= 0 and "{" in lines[j] and "}" in lines[j]:
                    return i + 1, out
            return i + 1, out
    return None, []


def anchor(game, spec):
    path = game / spec["file"]
    if not path.exists():
        return None, [], f"anchor {spec['id']}: {spec['file']} not found"
    lines = read(path).splitlines()
    kind = spec["kind"]
    items = []
    line0 = 1
    if kind == "matches":
        rx = re.compile(spec["pattern"])
        for i, line in enumerate(lines, 1):
            for m in rx.finditer(line):
                items.append({"name": m.group(1) if m.groups() else m.group(0), "line": i})
    else:
        line0, body = block(lines, spec["start"])
        if line0 is None:
            return None, [], f"anchor {spec['id']}: start {spec['start']!r} not found in {spec['file']}"
        if kind == "object-keys" and len(body) == 1:
            inner = body[0][1].split("{", 1)[1].rsplit("}", 1)[0]
            items = [{"name": k, "line": line0} for k in re.findall(r"([A-Za-z_$][\w$]*)\s*:", inner)]
        elif kind == "object-keys":
            for i, line in body[1:]:
                stripped = line.strip()
                if stripped.startswith(("//", "*", "/*")):
                    continue
                m = KEY.match(line)
                if m:
                    items.append({"name": m.group(1), "line": i})
        elif kind == "calls":
            rx = re.compile(spec["pattern"])
            for i, line in body[1:]:
                m = rx.match(line)
                if m:
                    note = line.split("//", 1)[1].strip() if "//" in line else ""
                    items.append({"name": m.group(1), "line": i, "note": note})
    return line0, items, None


def extract(game, profile):
    spec = profile.get("code")
    part = Part()
    if not spec:
        return part
    for area in spec.get("areas", []):
        files = glob(game, area["globs"], area.get("exclude", ()))
        tests = glob(game, area.get("tests", []))
        test_set = set(tests)
        lines = 0
        by_dir = {}
        for path in files:
            n = read(path).count("\n")
            lines += n
            d = rel(game, path.parent)
            by_dir[d] = by_dir.get(d, 0) + n
        cases = sum(len(TEST.findall(read(p))) for p in tests)
        top = sorted(by_dir.items(), key=lambda kv: -kv[1])[:12]
        aid = f"area:{area['id']}"
        part.node(aid, "codearea", area.get("area", "code"), area.get("title", area["id"]),
                  text=area.get("about", ""),
                  meta={"files": len([f for f in files if f not in test_set]), "lines": lines,
                        "test_files": len(tests), "test_cases": cases,
                        "largest_dirs": [{"dir": d, "lines": n} for d, n in top]})
        for path in files:
            if path in test_set:
                continue
            relpath = rel(game, path)
            if area.get("modules") and any(path.match(g) for g in area["modules"]):
                text = read(path)
                first = next((l.strip(" /*") for l in text.splitlines() if l.strip().startswith(("//", "/**", " *"))), "")
                part.node(f"mod:{relpath}", "module", area.get("area", "code"), path.stem,
                          text=first, source={"path": relpath, "line": 1},
                          meta={"lines": text.count("\n"), "area": area["id"]})
                part.edge(f"mod:{relpath}", aid, "in")
    for a in spec.get("anchors", []):
        line0, items, err = anchor(game, a)
        if err:
            part.notes.append(err)
            continue
        part.node(f"anchor:{a['id']}", "anchor", a.get("area", "code"), a.get("title", a["id"]),
                  text=a.get("about", ""), source={"path": a["file"], "line": line0},
                  meta={"items": items, "count": len(items)})
    return part
