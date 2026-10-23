"""Design documents: one node per document and per numbered (or titled) section.

A section's id is `sec:<DOC>:<number>` when the heading is numbered (`3.11`, `BOOK I`), else
`sec:<DOC>:<slug>`. Era tags the profile declares (e.g. "(round 7)", "(M5a)") are kept on the
section so the history view can place it.
"""

import re

from .common import Part, glob, read, rel, sections, slug

ITEM = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)


def doc_entries(game, profile):
    """(doc id, path, area, role) for every document the profile names, in order."""
    seen = set()
    for spec in profile["docs"]:
        if "path" in spec:
            paths = glob(game, [spec["path"]])
            ids = [spec["id"]] * len(paths)
        else:
            paths = glob(game, spec["glob"], spec.get("exclude", ()))
            ids = [doc_id_for(rel(game, p), spec) for p in paths]
        for doc_id, path in zip(ids, paths):
            if path in seen:
                continue
            seen.add(path)
            yield doc_id, path, spec.get("area", "design"), spec.get("role", "")


def doc_id_for(path, spec):
    stem = path
    for prefix in spec.get("strip", []):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    if stem.endswith(".md"):
        stem = stem[:-3]
    return spec.get("prefix", "") + stem


def extract(game, profile):
    part = Part()
    era = [re.compile(p) for p in profile.get("era_tags", [])]
    for doc_id, path, area, role in doc_entries(game, profile):
        text = read(path)
        relpath = rel(game, path)
        doc_node = f"doc:{doc_id}"
        part.node(doc_node, "doc", area, doc_id, source={"path": relpath, "line": 1},
                  meta={"lines": text.count("\n") + 1, "role": role})
        used = {}
        stack = []  # (level, number) of the enclosing numbered headings
        items = []
        for sec in sections(text):
            while stack and stack[-1][0] >= sec["level"]:
                stack.pop()
            number = sec["number"]
            if number and number.isdigit() and stack and not stack[-1][1][0].isdigit():
                number = f"{stack[-1][1]}.{number}"  # BOOK I > "3." is BOOK I.3
            if number:
                stack.append((sec["level"], number))
            sec["number"] = number
            key = number or slug(sec["title"])
            if key in used:
                used[key] += 1
                key = f"{key}~{used[key]}"
            else:
                used[key] = 1
            sid = f"sec:{doc_id}:{key}"
            eras = sorted({m.group(0).strip("() ") for rx in era for m in rx.finditer(sec["raw"] + " " + sec["body"][:400])})
            words = len(sec["body"].split())
            part.node(sid, "section", area, f"{doc_id} {sec['number'] + ' ' if sec['number'] else ''}{sec['title']}",
                      text=sec["body"], source={"path": relpath, "line": sec["line"]},
                      meta={"doc": doc_id, "number": sec["number"], "level": sec["level"],
                            "words": words, "eras": eras})
            part.edge(sid, doc_node, "in")
            if number and number.isdigit():
                for m in ITEM.finditer(sec["body"]):
                    items.append((f"{number}.{m.group(1)}", m, sec, sid))
        # A numbered list item in a top-level section is citable as "<section>.<n>" (UI 1.6 is
        # the sixth principle of section 1) unless a real subsection already has that number.
        for key, m, sec, parent in items:
            if key in used:
                continue
            used[key] = 1
            line = sec["line"] + sec["body"][: m.start()].count("\n") + 1
            iid = f"sec:{doc_id}:{key}"
            part.node(iid, "section", area, f"{doc_id} {key} {m.group(2)[:80]}", text=m.group(2),
                      source={"path": relpath, "line": line},
                      meta={"doc": doc_id, "number": key, "level": sec["level"] + 1,
                            "words": len(m.group(2).split()), "eras": [], "item": True})
            part.edge(iid, parent, "in")
    return part
