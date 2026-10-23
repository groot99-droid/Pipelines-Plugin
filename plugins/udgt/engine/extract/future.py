"""Future planning: every section that speaks of later work, by horizon.

The profile lists horizons, each a label and a pattern (e.g. "round 8", "V2", "planned"). A
section whose text matches gets one `plan` node per horizon with the matching sentences, so
the future view can list what is promised where, and the check can flag promises that a later
document already withdrew (a sentence with a `withdrawn` word).
"""

import re

from .common import Part, excerpt

SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*(\[])")


def extract(section_nodes, bodies, profile):
    spec = profile.get("future")
    part = Part()
    if not spec:
        return part
    horizons = [(h["id"], h["label"], re.compile(h["pattern"])) for h in spec["horizons"]]
    withdrawn = re.compile(spec.get("withdrawn", r"\b(removed|dropped|cut|withdrawn|superseded)\b"), re.IGNORECASE)
    for node in section_nodes:
        body = bodies.get(node["id"], "")
        if not body:
            continue
        sentences = [s for s in SENTENCE.split(re.sub(r"\s+", " ", body)) if s.strip()]
        for hid, label, rx in horizons:
            hits = [s for s in sentences if rx.search(s)]
            if not hits:
                continue
            pid = f"plan:{hid}:{node['id'][4:]}"
            part.node(pid, "plan", "future", f"{label} · {node['title']}",
                      text=" ".join(hits[:4]), source=node.get("source"),
                      meta={"horizon": hid, "label": label, "count": len(hits),
                            "withdrawn": sum(bool(withdrawn.search(s)) for s in hits),
                            "sentences": [excerpt(s, 300) for s in hits[:8]]})
            part.edge(pid, node["id"], "stated-in")
    return part
