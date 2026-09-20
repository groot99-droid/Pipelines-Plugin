#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Route a product brief to the right catalog rows before searching.

A literal BM25 query matches the words a brief happens to use, not the words
the catalog uses: "freelancer invoicing SaaS fintech trustworthy" ranks the
*Freelancer Platform* product row above *Invoice & Billing Tool*, and search.py
prints the wrong row with the same confidence as a right one. This script
cross-checks the product domain three ways and warns when they disagree:

  raw      the brief, searched as written
  variant  the brief plus the catalog's own forms of each word (invoicing ->
           invoice, freelancer -> freelance), searched again
  keyword  stem overlap between the brief and each row's Product Type/Keywords

It then prints the candidate rows, ready-to-run commands, and a manifest of the
supplemental searches (UX, charts, motion, stack) a wide brief needs. The
manifest is what the ui-design-multipart skill fans out to
ui-design-search-part agents; the router says whether that is worth doing. A
stack part is probed first and dropped into `not_covered` when that stack's data
has no usable rows for it, so no agent is sent to a search that cannot answer.

Usage:
    python route.py "<brief>" [--stack <stack>] [--top N] [--json]

Standard library only; reads catalog/data through core.py and never writes.
"""

import argparse
import csv
import io
import json
import math
import sys
from collections import defaultdict

import core

# Fan-out only pays off for wide briefs: one search is milliseconds, one agent
# is not. Below this many manifest parts the router says to run them inline.
FAN_OUT_MIN_PARTS = 4
CLOSE_RATIO = 0.85      # runner-up fused score / top fused score at or above this is ambiguous
LOW_COVERAGE = 0.5      # raw token coverage below this is low confidence
SEARCH_DEPTH = 10
RRF_K = 3               # small corpus, small constant: rank 1 counts clearly more than rank 4
PART_N = 3

# Each entry adds a supplemental part when the brief mentions any trigger. The
# design-system command already covers product/style/color/landing/typography,
# so the manifest holds only what it does not.
CONCERNS = (
    ("forms", {"form", "forms", "checkout", "invoice", "invoicing", "signup", "payment",
               "billing", "login", "onboarding", "booking", "input"},
     "ux", "form validation error feedback", "form validation input"),
    ("charts", {"dashboard", "analytics", "chart", "charts", "report", "reports", "metrics",
                "revenue", "reporting", "graph"},
     "chart", "dashboard trend comparison", "chart data table"),
    ("motion", {"animation", "animated", "motion", "transition", "transitions", "interactive",
                "parallax", "scroll"},
     "gsap", "scroll reveal stagger", "animation transition"),
    ("nav", {"navigation", "menu", "sidebar", "tabs", "navbar", "nav"},
     "ux", "navigation hierarchy back", "navigation routing"),
    ("icons", {"icon", "icons", "iconography"},
     "icons", "decorative icon aria hidden", "icon accessible label"),
)
# Accessibility is priority 1 in the guide, so it is always in the manifest.
BASELINE = ("a11y", "ux", "keyboard focus contrast accessible", "accessibility focus label")


def stem_key(word):
    """Collapse inflections to one key: invoicing/invoice -> invoic."""
    w = word.lower()
    for suffix in ("ing", "ers", "er", "ed", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 4:
            w = w[: -len(suffix)]
            if suffix in ("ing", "ed", "er") and len(w) > 4 and w[-1] == w[-2] and w[-1] not in "lszf":
                w = w[:-1]
            break
    if len(w) > 4 and w.endswith("e"):
        w = w[:-1]
    return w


def load_products():
    with (core.DATA_DIR / "products.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def tokens_of(text):
    return core.BM25().tokenize(text)


def build_vocabulary(rows):
    """stem key -> the catalog's own surface forms for it."""
    by_key = defaultdict(set)
    for row in rows:
        for token in tokens_of(row["Product Type"] + " " + row["Keywords"]):
            by_key[stem_key(token)].add(token)
    return by_key


def variant_query(brief_tokens, vocabulary):
    """The brief plus the catalog's spelling of each word, order kept, no repeats."""
    seen, out = set(), []
    for token in brief_tokens:
        for form in [token, *sorted(vocabulary.get(stem_key(token), ()))]:
            if form not in seen:
                seen.add(form)
                out.append(form)
    return " ".join(out)


def keyword_scores(brief_tokens, rows):
    """IDF-weighted stem overlap with each row's Product Type and Keywords."""
    row_keys = []
    df = defaultdict(int)
    for row in rows:
        type_keys = {stem_key(t) for t in tokens_of(row["Product Type"])}
        keyword_keys = {stem_key(t) for t in tokens_of(row["Keywords"])}
        row_keys.append((type_keys, keyword_keys))
        for key in type_keys | keyword_keys:
            df[key] += 1
    brief_keys = {stem_key(t) for t in brief_tokens}
    scores = {}
    for row, (type_keys, keyword_keys) in zip(rows, row_keys):
        score = 0.0
        for key in brief_keys & (type_keys | keyword_keys):
            weight = math.log(1 + len(rows) / df[key])
            score += weight * (2.0 if key in type_keys else 1.0)   # a name hit is identity
        if score > 0:
            scores[row["Product Type"]] = score
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def ranked_names(result):
    return [row["Product Type"] for row in result.get("results", [])]


def fuse(sources):
    """Reciprocal-rank fusion over {source: [names in rank order]}."""
    fused = defaultdict(float)
    for names in sources.values():
        for rank, name in enumerate(names, 1):
            fused[name] += 1.0 / (RRF_K + rank)
    return sorted(fused.items(), key=lambda item: item[1], reverse=True)


def rank_of(names, name):
    return names.index(name) + 1 if name in names else None


def find_warnings(candidates, sources, raw_diagnostic):
    warnings = []
    if not candidates:
        return [{"code": "no-match",
                 "message": "No product row matched any source. Retry with words from ui-design/INDEX.md."}]
    top = candidates[0]["product_type"]
    disagree = {src: names[0] for src, names in sources.items() if names and names[0] != top}
    if disagree:
        detail = "; ".join(f'{src} ranks "{name}" first' for src, name in disagree.items())
        warnings.append({
            "code": "ambiguous",
            "message": (f'Sources disagree: the combined ranking picks "{top}", but {detail}. '
                        "Read both rows before choosing; a literal search alone would have "
                        "printed the wrong one with full confidence."),
        })
    if len(candidates) > 1 and candidates[1]["fused"] >= CLOSE_RATIO * candidates[0]["fused"]:
        warnings.append({
            "code": "close-call",
            "message": (f'"{top}" and "{candidates[1]["product_type"]}" score within '
                        f"{round((1 - CLOSE_RATIO) * 100)}% of each other."),
        })
    coverage = raw_diagnostic.get("token_coverage")
    if raw_diagnostic.get("abstained") or (coverage is not None and coverage < LOW_COVERAGE):
        warnings.append({
            "code": "low-confidence",
            "message": (f"The literal brief search is low confidence (reason="
                        f"{raw_diagnostic.get('reason')}, token_coverage={coverage}). Rephrase "
                        "in the catalog's own words (ui-design/INDEX.md)."),
        })
    return warnings


def build_manifest(brief_tokens, stack):
    parts = []
    concerns = [(BASELINE[0], BASELINE[1], BASELINE[2], BASELINE[3])]
    concerns += [(name, domain, dq, sq) for name, triggers, domain, dq, sq in CONCERNS
                 if triggers & set(brief_tokens)]
    for name, domain, domain_query, stack_query in concerns:
        parts.append({"part_id": f"{domain}-{name}", "kind": "domain", "target": domain,
                      "query": domain_query, "n": PART_N})
        if stack:
            parts.append({"part_id": f"stack-{stack}-{name}", "kind": "stack", "target": stack,
                          "query": stack_query, "n": PART_N})
    return parts


def probe_stack_parts(manifest):
    """Split the manifest into parts the catalog can answer and parts it cannot.

    A stack part costs an agent, so it is dispatched only if its own query finds
    rows in that stack's CSV at usable coverage. The stack queries are one set
    for every stack; most stacks lack rows for some concern (nextjs has none for
    accessibility), and an agent sent there can only come back empty, or with a
    row that matched a single stem. Domain parts are not probed: the domain
    files are the catalog's core and every concern has rows there.
    """
    kept, not_covered = [], []
    for part in manifest:
        if part["kind"] != "stack":
            kept.append(part)
            continue
        probe = core.search_stack(part["query"], part["target"], part["n"], diagnostics=True)
        coverage = probe.get("diagnostics", {}).get("token_coverage")
        if probe.get("error"):
            reason = probe["error"]
        elif not probe.get("results"):
            reason = f"no rows (token_coverage={coverage})"
        elif coverage is not None and coverage < LOW_COVERAGE:
            reason = f"token_coverage {coverage:.2f} is under {LOW_COVERAGE}"
        else:
            kept.append(part)
            continue
        not_covered.append({"part_id": part["part_id"], "target": part["target"],
                            "query": part["query"], "reason": reason})
    return kept, not_covered


def part_command(part):
    flag = "--domain" if part["kind"] == "domain" else "--stack"
    return (f'python ui-design/catalog/scripts/search.py "{part["query"]}" '
            f'{flag} {part["target"]} -n {part["n"]} --json --diagnostics')


def route(brief, stack=None, top=5):
    rows = load_products()
    ids = {row["Product Type"]: row["No"] for row in rows}
    by_name = {row["Product Type"]: row for row in rows}
    brief_tokens = tokens_of(brief)
    vocabulary = build_vocabulary(rows)

    raw = core.search(brief, "product", SEARCH_DEPTH, diagnostics=True)
    sources = {"raw": ranked_names(raw)}
    variant_text = variant_query(brief_tokens, vocabulary)
    if variant_text != " ".join(brief_tokens):
        variant = core.search(variant_text, "product", SEARCH_DEPTH, diagnostics=True)
        sources["variant"] = ranked_names(variant)
    keyword = keyword_scores(brief_tokens, rows)
    if keyword:
        sources["keyword"] = [name for name, _ in keyword[:SEARCH_DEPTH]]

    candidates = []
    # The variant query is the raw query plus the catalog's spellings, so it
    # supersedes raw in the fusion; counting both would double-weight the
    # literal search. Raw still takes part in the disagreement warning.
    fused_sources = {src: names for src, names in sources.items()
                     if src != "raw" or "variant" not in sources}
    for name, score in fuse(fused_sources)[:top]:
        candidates.append({
            "id": int(ids[name]) if ids[name].isdigit() else ids[name],
            "product_type": name,
            "keywords": by_name[name]["Keywords"],
            "fused": round(score, 4),
            "ranks": {src: rank_of(names, name) for src, names in sources.items()},
        })
    warnings = find_warnings(candidates, sources, raw.get("diagnostics", {}))

    commands = []
    if candidates:
        chosen = candidates[0]["product_type"]
        extra = [t for t in brief_tokens if stem_key(t) not in {stem_key(x) for x in tokens_of(chosen)}]
        query = " ".join([chosen, *extra])
        commands.append(f'python ui-design/catalog/scripts/search.py "{query}" --design-system '
                        f'-p "{chosen}"')
    manifest, not_covered = probe_stack_parts(build_manifest(brief_tokens, stack))
    return {
        "brief": brief,
        "stack": stack,
        "variant_query": variant_text,
        "candidates": candidates,
        "warnings": warnings,
        "commands": commands,
        "manifest": manifest,
        "not_covered": not_covered,
        "fan_out": {"recommended": len(manifest) >= FAN_OUT_MIN_PARTS,
                    "parts": len(manifest), "threshold": FAN_OUT_MIN_PARTS},
    }


def format_report(result):
    out = [f"## Route: {result['brief']}", ""]
    out.append("### Product candidates")
    if not result["candidates"]:
        out.append("(none)")
    for i, cand in enumerate(result["candidates"], 1):
        ranks = " ".join(f"{src}#{rank}" for src, rank in cand["ranks"].items() if rank)
        out.append(f"{i}. **{cand['product_type']}** (id {cand['id']})  fused={cand['fused']}  [{ranks}]")
        out.append(f"   keywords: {cand['keywords']}")
    out.append("")
    if result["warnings"]:
        out.append("### Warnings")
        for warning in result["warnings"]:
            out.append(f"- **{warning['code'].upper()}**: {warning['message']}")
        out.append("")
    out.append("### Commands (run inline)")
    for command in result["commands"]:
        out.append(f"    {command}")
    out.append("")
    fan = result["fan_out"]
    verdict = "fan out" if fan["recommended"] else "run inline"
    out.append(f"### Supplemental parts: {fan['parts']} (threshold {fan['threshold']}) -> {verdict}")
    for part in result["manifest"]:
        out.append(f"- `{part['part_id']}`: {part_command(part)}")
    if result["not_covered"]:
        out.append("")
        out.append("### Not covered (no agent dispatched)")
        for part in result["not_covered"]:
            out.append(f"- `{part['part_id']}`: stack {part['target']} cannot answer "
                       f"\"{part['query']}\" ({part['reason']}); the domain part for the same "
                       "concern still runs")
    return "\n".join(out)


def main():
    for stream in (sys.stdout, sys.stderr):
        if stream.encoding and stream.encoding.lower() != "utf-8":
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, io.UnsupportedOperation):
                pass
    parser = argparse.ArgumentParser(description="Route a product brief to catalog rows, warn on ambiguity, emit a search manifest")
    parser.add_argument("brief", help="The product brief, in the user's own words")
    parser.add_argument("--stack", "-s", choices=core.AVAILABLE_STACKS, help="Also emit stack-search parts for this stack")
    parser.add_argument("--top", type=int, default=5, choices=range(1, 11), metavar="1-10", help="Candidate rows to show (default 5)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output, including the manifest")
    args = parser.parse_args()
    result = route(args.brief, args.stack, args.top)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
