"""Lore kept outside the game: Markdown works whose frontmatter marks them as the game's.

A profile's `lore` lists roots, each relative to the profile, with a frontmatter filter:
`{"id": "vault", "root": "../vault", "match": {"project": "my-game"}}`. Every matching work becomes
a `lore` node (`lore:<root id>/<path without .md>`) and every `##` heading in it a `lore-section`
(`lore:<root id>/<path>#<slug>`). Folders whose name starts with `_` or `.` are skipped. Source
paths read `<root id>:<path>`, since the work is not in the game checkout. A root that does not
exist, or holds no match yet, leaves a note and no nodes.
"""

import re
from pathlib import Path

from .common import Part, read, sections, slug

FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LIST = re.compile(r"^\[(.*)\]$")


def frontmatter(text):
    """(fields, body, body's first line) for the simple `key: value` and `key: [a, b]` subset."""
    m = FRONT.match(text)
    if not m:
        return {}, text, 1
    fields = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t", "#")):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        listed = LIST.match(value)
        if listed:
            value = [v.strip().strip("'\"") for v in listed.group(1).split(",") if v.strip()]
        else:
            value = value.strip("'\"")
        fields[key.strip()] = value
    return fields, text[m.end():], m.group(0).count("\n") + 1


def matches(fields, want):
    for key, value in want.items():
        have = fields.get(key)
        if isinstance(have, list):
            if value not in have:
                return False
        elif have != value:
            return False
    return True


def works(root):
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(p.startswith(("_", ".")) for p in parts):
            continue
        yield path


def extract(profile):
    part = Part()
    for spec in profile.get("lore", []):
        root = (profile["_home"] / spec["root"]).resolve()
        rid = spec["id"]
        if not root.is_dir():
            part.notes.append(f"lore {rid}: no folder at {spec['root']}")
            continue
        found = 0
        for path in works(root):
            text = read(path)
            fields, body, first = frontmatter(text)
            if not matches(fields, spec.get("match", {})):
                continue
            found += 1
            relpath = path.relative_to(root).as_posix()
            nid = f"lore:{rid}/{relpath[:-3]}"
            meta = {k: fields[k] for k in ("type", "status", "genre", "themes", "tags") if k in fields}
            part.node(nid, "lore", spec.get("area", "world"), fields.get("title") or path.stem,
                      text=body, source={"path": f"{rid}:{relpath}", "line": 1},
                      meta=dict(meta, lines=text.count("\n") + 1))
            used = set()
            for sec in sections(body):
                if sec["level"] != 2:
                    continue
                base = sid = f"{nid}#{slug(sec['raw'])}"
                n = 2
                while sid in used:
                    sid, n = f"{base}-{n}", n + 1
                used.add(sid)
                part.node(sid, "lore-section", spec.get("area", "world"), sec["raw"],
                          text=sec["body"], source={"path": f"{rid}:{relpath}", "line": first + sec["line"] - 1})
                part.edge(sid, nid, "in")
        if not found:
            part.notes.append(f"lore {rid}: no work matches {spec.get('match', {})} yet")
    return part
