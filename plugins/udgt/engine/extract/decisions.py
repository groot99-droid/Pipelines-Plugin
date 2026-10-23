"""The decision log: one node per decision row and per numbered open question.

The profile gives the file, the row pattern (its first group is the id), and `layouts`: which
column holds what for a range of ids, because a log's columns can change meaning partway through.
Ids are keys, not a sequence: rows may be out of order and numbers may be skipped. A row whose
text matches a `reserved` marker is kept with status "reserved".
"""

import re

from .common import Part, read, rel, sections, split_row, strip_md

DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
BOLD = re.compile(r"\*\*(.+?)\*\*")
LIST_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")


def layout_for(num, layouts):
    for spec in layouts:
        lo = spec.get("from", 0)
        hi = spec.get("to", 10 ** 9)
        if lo <= num <= hi:
            return spec["cols"]
    return ["topic", "decision"]


def extract(game, profile):
    spec = profile.get("decisions")
    part = Part()
    if not spec:
        return part
    path = game / spec["path"]
    if not path.exists():
        part.notes.append(f"decision log {spec['path']} not found")
        return part
    text = read(path)
    relpath = rel(game, path)
    row = re.compile(spec["row"])
    num_of = re.compile(spec.get("number", r"(\d+)"))
    session = re.compile(spec["session"]) if spec.get("session") else None
    reserved = spec.get("reserved", [])
    open_marker = spec.get("open_marker", "Open:")
    owner_words = spec.get("owner_words", ["owner"])
    heading = ""
    lines = text.splitlines()
    seen = {}
    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            heading = strip_md(line.lstrip("#").strip())
            continue
        m = row.match(line)
        if not m:
            continue
        did = m.group(1)
        cells = split_row(line)[1:]
        num = int(num_of.search(did).group(1))
        cols = layout_for(num, spec.get("layouts", []))
        fields = {name: (cells[k] if k < len(cells) else "") for k, name in enumerate(cols)}
        whole = " ".join(cells)
        decision = fields.get("decision", "")
        topic = fields.get("topic", "")
        bold = BOLD.search(decision)
        title = strip_md(topic)[:120] if topic else (strip_md(bold.group(1)) if bold else strip_md(decision)[:120])
        first = strip_md(cells[0]) if cells else ""
        status = "reserved" if any(first.startswith(r) for r in reserved) else "decided"
        open_text = ""
        if fields.get("open"):
            open_text = strip_md(fields["open"])
        elif open_marker in whole:
            open_text = strip_md(whole.split(open_marker, 1)[1])
            open_text = open_marker + " " + open_text
        if open_text and re.match(re.escape(open_marker) + r"\s*none\b", open_text, re.IGNORECASE):
            open_text = ""
        dates = DATE.findall(whole)
        sessions = sorted(set(session.findall(title + " " + topic))) if session else []
        node_id = f"dec:{did}"
        if node_id in seen:
            seen[node_id] += 1
            node_id = f"{node_id}~{seen[node_id]}"
            part.notes.append(f"decision {did} appears more than once (line {i})")
        else:
            seen[node_id] = 1
        part.node(node_id, "decision", spec.get("area", "decisions"), f"{did} {title}",
                  text=strip_md(topic + " " + decision if topic else decision),
                  source={"path": relpath, "line": i},
                  meta={"number": num, "status": status, "date": dates[0] if dates else None,
                        "owner": any(re.search(rf"\b{re.escape(w)}\b", whole, re.IGNORECASE) for w in owner_words),
                        "sessions": sessions, "open": open_text or None, "group": heading,
                        "changed_in_review": bool(re.search(r"[Cc]hange[ds]? (made|in review)", whole))})
        if open_text:
            part.node(f"open:{did}", "open", "future", f"Open after {did}", text=open_text,
                      source={"path": relpath, "line": i}, meta={"decision": did})
            part.edge(f"open:{did}", node_id, "raised-by")
    # numbered open questions, under any heading matching the profile's pattern
    oq = spec.get("open_questions")
    if oq:
        rx = re.compile(oq["heading"], re.IGNORECASE)
        resolved = re.compile(oq.get("resolved", r"Resolved"), re.IGNORECASE)
        for sec in sections(text):
            if not rx.search(sec["raw"]):
                continue
            item, start = [], 0
            body_lines = sec["body"].splitlines()

            def flush():
                if not item:
                    return
                n = item[0][0]
                body = " ".join(t for _, t in item)
                done = bool(resolved.search(body))
                part.node(f"oq:{n}", "question", "future", f"Open question {n}: {strip_md(body)[:90]}",
                          text=strip_md(body), source={"path": relpath, "line": start},
                          meta={"resolved": done, "date": (DATE.findall(body) or [None])[0]})

            for k, line in enumerate(body_lines):
                m = LIST_ITEM.match(line)
                if m:
                    flush()
                    item = [(m.group(1), m.group(2))]
                    start = sec["line"] + k + 1
                elif item and line.strip() and (line.startswith(" ") or line.startswith("\t")):
                    item.append((item[0][0], line.strip()))
                elif item and not line.strip():
                    continue
                elif item:
                    flush()
                    item = []
            flush()
    return part
