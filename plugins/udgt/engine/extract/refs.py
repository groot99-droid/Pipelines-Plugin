"""Cross-references: the citations that tie documents, decisions, data and commits together.

Each profile ref has a pattern and a `target` template. `{1}` is the pattern's first group (`{2}`... the next, empty when unmatched, and a trailing
dot is dropped);
`{doc}` comes from the ref's `doc`. A `range` group (named `to`) expands `A52 to A64`. A section
target that does not exist is retried without its last component (`3.11.2` -> `3.11`), so a
citation lands on the nearest section that does, but never on a whole numbered chapter. `strict` refs report a miss as broken.
"""

import re


def resolve(target, ids):
    if target in ids:
        return target
    head, _, num = target.rpartition(":")
    while "." in num:
        num = num.rsplit(".", 1)[0]
        if num.isdigit():
            return None  # "3.99" does not fall back to the whole of chapter 3
        if f"{head}:{num}" in ids:
            return f"{head}:{num}"
    return None


def scan(text, refs):
    for ref in refs:
        for m in ref["rx"].finditer(text):
            first = m.group(1)
            targets = [first]
            if ref.get("range") and m.groupdict().get("to"):
                a, b = int(re.sub(r"\D", "", first)), int(m.group("to"))
                prefix = re.sub(r"\d+$", "", first)
                if 0 < b - a <= 60:
                    targets = [f"{prefix}{n}" for n in range(a, b + 1)]
            for t in targets:
                out = ref["target"].replace("{1}", t).replace("{doc}", ref.get("doc", ""))
                for k in range(2, (ref["rx"].groups or 1) + 1):
                    g = m.group(k)
                    out = out.replace(f"{{{k}}}", g or "")
                yield ref, out.rstrip(".")


def link(sources, refs, ids):
    """Edges from each (node id, text) to what its text cites, plus the broken strict ones."""
    edges, broken = [], []
    for nid, text in sources:
        seen = set()
        for ref, target in scan(text, refs):
            hit = resolve(target, ids)
            if hit and hit != nid and hit not in seen:
                seen.add(hit)
                edges.append({"from": nid, "to": hit, "kind": "cites"})
            elif not hit and ref.get("strict"):
                broken.append({"from": nid, "target": target, "ref": ref["id"]})
    return edges, broken
