"""Named tables inside documents: protocol messages, milestones, scene lists, seams.

Each profile entry names a file, a heading pattern the table sits under, the node kind, the
column that holds the key, and optionally the column that holds the title. Every row becomes
one node `<kind>:<key>`, with the row's cells kept by header name.
"""

import re

from .common import Part, read, rel, sections, slug, strip_md, tables


def extract(game, profile):
    part = Part()
    for spec in profile.get("tables", []):
        path = game / spec["path"]
        if not path.exists():
            part.notes.append(f"table source {spec['path']} not found")
            continue
        text = read(path)
        relpath = rel(game, path)
        under = re.compile(spec["under"], re.IGNORECASE)
        key_col = spec.get("key", 0)
        title_col = spec.get("title")
        key_rx = re.compile(spec["key_pattern"]) if spec.get("key_pattern") else None
        found = 0
        for sec in sections(text):
            if not under.search(sec["raw"]):
                continue
            for start, header, rows in tables(sec["body"]):
                names = [strip_md(h) or f"c{k}" for k, h in enumerate(header)]
                for line, cells in rows:
                    if key_col >= len(cells):
                        continue
                    raw_key = strip_md(cells[key_col])
                    if key_rx:
                        m = key_rx.search(raw_key)
                        if not m:
                            continue
                        raw_key = m.group(1) if m.groups() else m.group(0)
                    if not raw_key or set(raw_key) <= set("-—– "):
                        continue
                    key = raw_key if re.fullmatch(r"[\w.:/-]+", raw_key) else slug(raw_key)
                    nid = f"{spec['kind']}:{key}"
                    title = strip_md(cells[title_col]) if title_col is not None and title_col < len(cells) else raw_key
                    meta = {names[k] if k < len(names) else f"c{k}": strip_md(c) for k, c in enumerate(cells)}
                    meta["table"] = spec["id"]
                    meta["under"] = strip_md(sec["raw"])
                    part.node(nid, spec["kind"], spec.get("area", "design"), title,
                              text=" · ".join(strip_md(c) for c in cells[1:] if c),
                              source={"path": relpath, "line": sec["line"] + line},
                              meta=meta)
                    found += 1
        if not found:
            part.notes.append(f"table {spec['id']}: no rows under /{spec['under']}/ in {spec['path']}")
    return dedupe(part)


def dedupe(part):
    seen = {}
    for node in part.nodes:
        base = node["id"]
        if base in seen:
            seen[base] += 1
            node["id"] = f"{base}~{seen[base]}"
        else:
            seen[base] = 1
    return part
