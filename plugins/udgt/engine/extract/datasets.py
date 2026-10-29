"""Data files: one node per file, per collection inside it, and per record.

A collection is any key whose value is an object of objects (keyed by id) or a list of objects.
A record keeps its scalar fields (strings shortened), the length of its lists, and the list of
its field names. A `ref_field` (e.g. `gddRef`) on a file or a record links it to a section of the
document the profile names as `ref_doc`.
"""

import json

from .common import Part, glob, rel

SCALAR_CAP = 240


def small(value):
    return isinstance(value, dict) and 0 < len(value) <= 3 and all(
        isinstance(x, (str, int, float, bool)) for x in value.values())


def summarize(record):
    meta = {}
    for key, value in record.items():
        if isinstance(value, (bool, int, float)) or value is None:
            meta[key] = value
        elif isinstance(value, str):
            meta[key] = value if len(value) <= SCALAR_CAP else value[: SCALAR_CAP - 1] + "…"
        elif isinstance(value, list):
            if value and all(isinstance(v, str) for v in value) and len(value) <= 12:
                meta[key] = value
            elif value and len(value) <= 12 and all(small(v) for v in value):
                meta[key] = [" ".join(str(x) for x in v.values()) for v in value]  # {"item": "knife", "qty": 1}
            else:
                meta[key] = f"[{len(value)}]"
        elif isinstance(value, dict):
            meta[key] = f"{{{len(value)}}}"
    return meta


def collections(data):
    """(name, [(record id, record)]) for every collection-shaped value of a JSON object."""
    if isinstance(data, list) and data and all(isinstance(v, dict) for v in data):
        yield "", [(str(v.get("id", k)), v) for k, v in enumerate(data)]
        return
    if not isinstance(data, dict):
        return
    for key, value in data.items():
        if isinstance(value, dict) and value and all(isinstance(v, dict) for v in value.values()):
            yield key, [(str(k), v) for k, v in value.items()]
        elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            yield key, [(str(v.get("id", k)), v) for k, v in enumerate(value)]


def extract(game, profile):
    spec = profile.get("datasets")
    part = Part()
    if not spec:
        return part
    ref_field = spec.get("ref_field")
    ref_doc = spec.get("ref_doc")
    record_cap = spec.get("record_cap", 400)
    for path in glob(game, spec["globs"], spec.get("exclude", ())):
        relpath = rel(game, path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as err:
            part.notes.append(f"{relpath}: not JSON ({err})")
            continue
        ds = relpath[: -len(".json")] if relpath.endswith(".json") else relpath
        for prefix in spec.get("strip", []):
            if ds.startswith(prefix):
                ds = ds[len(prefix):]
        file_id = f"data:{ds}"
        top_keys = list(data) if isinstance(data, dict) else []
        cols = list(collections(data))
        part.node(file_id, "dataset", spec.get("area", "data"), ds,
                  source={"path": relpath, "line": 1},
                  meta={"keys": top_keys, "bytes": path.stat().st_size,
                        "collections": {name or "(root)": len(recs) for name, recs in cols},
                        "scalars": summarize(data) if isinstance(data, dict) else {}})
        if ref_field and isinstance(data, dict) and isinstance(data.get(ref_field), str):
            part.edge(file_id, f"sec:{ref_doc}:{data[ref_field]}", "documented-in")
        emitted = 0
        for name, recs in cols:
            coll_id = f"{file_id}/{name}" if name else file_id
            fields = sorted({k for _, r in recs for k in r})
            if name:
                part.node(coll_id, "collection", spec.get("area", "data"), f"{ds} · {name}",
                          meta={"count": len(recs), "fields": fields})
                part.edge(coll_id, file_id, "in")
            for rid, rec in recs:
                if emitted >= record_cap:
                    break
                emitted += 1
                nid = f"rec:{ds}/{name}/{rid}" if name else f"rec:{ds}/{rid}"
                title = str(rec.get("name") or rec.get("title") or rid)
                part.node(nid, "record", spec.get("area", "data"), title,
                          meta=dict(summarize(rec), _collection=coll_id))
                part.edge(nid, coll_id, "in")
                if ref_field and isinstance(rec.get(ref_field), str):
                    part.edge(nid, f"sec:{ref_doc}:{rec[ref_field]}", "documented-in")
            if emitted >= record_cap:
                part.notes.append(f"{relpath}: record cap {record_cap} reached")
                break
    return part
