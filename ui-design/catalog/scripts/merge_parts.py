#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge and cross-check the blocks returned by a multipart subagent fan-out.

A script splits the work (route.py for search, the four review areas for a page
review), one agent handles one part, and this script merges the answers and
checks them, because an agent's report of its own completeness is not evidence.
It fails when a part is missing, duplicated, unknown or malformed, and it
flags parts that came back empty or low-confidence.

  --mode search   blocks are PART / QUERY / RETRIED / VERDICT / ROWS, one per
                  manifest part from route.py --json
  --mode review   blocks are AREA / FINDINGS / NOT-CHECKED, one per review
                  area; every cited rule-id must exist in
                  references/quick-reference.md, so a reviewer cannot invent
                  a rule to win an argument

Usage:
    python merge_parts.py --mode search --manifest route.json --results a.txt b.txt [--json]
    python merge_parts.py --mode review --results reviews.txt [--areas layout,motion] [--json]
    (a results file of - reads stdin)

Exit codes:
    0 -- every expected part came back exactly once and is well formed
         (warnings may still be listed)
    1 -- a part is missing, duplicated, unknown or malformed, or a finding
         cites a rule that does not exist

Standard library only; writes nothing.
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path

QUICK_REFERENCE = Path(__file__).resolve().parents[2] / "references" / "quick-reference.md"

# Review areas and the quick-reference sections each one is allowed to cite.
AREA_SECTIONS = {
    "a11y+touch": (1, 2),
    "layout": (5,),
    "type-color-style": (4, 6),
    "motion": (7,),
}
SEVERITIES = ("critical", "high", "medium", "low")
VERDICTS = ("match", "low-confidence", "empty")

SEARCH_KEYS = ("PART", "QUERY", "RETRIED", "VERDICT", "ROWS")
REVIEW_KEYS = ("AREA", "FINDINGS", "NOT-CHECKED")
KEY_LINE = re.compile(r"^(PART|QUERY|RETRIED|VERDICT|ROWS|AREA|FINDINGS|NOT-CHECKED):[ \t]*(.*)$")


def load_rule_ids(path=QUICK_REFERENCE):
    """rule-id -> quick-reference section number."""
    rules, section = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        heading = re.match(r"### (\d+)\.", line)
        if heading:
            section = int(heading.group(1))
            continue
        rule = re.match(r"- `([a-z0-9-]+)`", line)
        if rule and section is not None:
            rules[rule.group(1)] = section
    return rules


def parse_blocks(text, start_key):
    """Split agent output into blocks, each a dict of key -> list of lines.

    A block starts at a `start_key:` line. Stray prose and code fences before,
    between or after blocks are ignored; anything after a key line and before
    the next key line belongs to that key.
    """
    blocks, block, key = [], None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            continue
        match = KEY_LINE.match(line.strip())
        if match and match.group(1) == start_key:
            block = {}
            blocks.append(block)
        if match and block is not None:
            key = match.group(1)
            block.setdefault(key, [])
            if match.group(2):
                block[key].append(match.group(2))
        elif block is not None and key and line.strip():
            block[key].append(line.strip())
    return blocks


def single(block, key):
    values = block.get(key) or []
    return " ".join(values).strip()


def bullets(lines):
    """The `- item` lines of a multi-line key; `(none)` means an empty list."""
    items = []
    for line in lines:
        if line.strip().lower() in ("(none)", "none"):
            continue
        items.append(line[1:].strip() if line.startswith("-") else line)
    return items


def read_results(paths):
    chunks = []
    for path in paths:
        chunks.append(sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8"))
    return "\n".join(chunks)


def merge_search(manifest, text):
    errors, warnings = [], []
    expected = {part["part_id"]: part for part in manifest}
    blocks = parse_blocks(text, "PART")
    seen, parts = {}, []
    for block in blocks:
        part_id = single(block, "PART")
        if part_id not in expected:
            errors.append(f"unknown part {part_id!r}: not in the manifest")
            continue
        if part_id in seen:
            errors.append(f"part {part_id!r} returned more than once")
            continue
        seen[part_id] = block
        verdict = single(block, "VERDICT").lower()
        query = single(block, "QUERY")
        retried = single(block, "RETRIED").lower() == "yes"
        rows = bullets(block.get("ROWS", []))
        if verdict not in VERDICTS:
            errors.append(f"part {part_id!r}: VERDICT must be one of {list(VERDICTS)}, got {verdict!r}")
        if not query:
            errors.append(f"part {part_id!r}: QUERY is missing")
        elif query != expected[part_id]["query"] and not retried:
            errors.append(f"part {part_id!r}: ran {query!r} instead of the manifest query "
                          f"{expected[part_id]['query']!r} without declaring RETRIED: yes")
        if verdict == "match" and not rows:
            errors.append(f"part {part_id!r}: VERDICT match but ROWS is empty")
        if verdict == "empty":
            warnings.append(f"part {part_id!r} is empty: say that no database match was found "
                            "for it; do not present general guidance as a match")
        elif verdict == "low-confidence" and retried:
            warnings.append(f"part {part_id!r} is low-confidence after a retry: the retry did not "
                            "recover, so treat the part as not searched and do not cite its rows")
        elif verdict == "low-confidence":
            warnings.append(f"part {part_id!r} is low-confidence: verify the top row before using it")
        parts.append({"part_id": part_id, "verdict": verdict, "retried": retried,
                      "query": query, "rows": rows})
    for part_id in expected:
        if part_id not in seen:
            errors.append(f"part {part_id!r} is missing: no block came back for it")
    counts = {verdict: sum(1 for p in parts if p["verdict"] == verdict) for verdict in VERDICTS}
    return {"mode": "search", "expected": len(expected), "returned": len(seen),
            "verdicts": counts, "parts": parts, "errors": errors, "warnings": warnings}


def merge_review(areas, text, rules):
    errors, warnings = [], []
    blocks = parse_blocks(text, "AREA")
    seen, reviewed, findings = set(), [], []
    for block in blocks:
        area = single(block, "AREA")
        if area not in areas:
            errors.append(f"unknown area {area!r}: expected one of {sorted(areas)}")
            continue
        if area in seen:
            errors.append(f"area {area!r} returned more than once")
            continue
        seen.add(area)
        if "FINDINGS" not in block:
            errors.append(f"area {area!r}: FINDINGS is missing (write '(none)' if there are none)")
        for item in bullets(block.get("FINDINGS", [])):
            fields = [f.strip() for f in item.split("|", 3)]
            if len(fields) != 4 or not all(fields):
                errors.append(f"area {area!r}: finding is not 'rule-id | severity | evidence | fix': {item!r}")
                continue
            rule_id, severity, evidence, fix = fields
            severity = severity.lower()
            if rule_id not in rules:
                errors.append(f"area {area!r}: cites rule-id {rule_id!r}, which is not in "
                              "references/quick-reference.md")
                continue
            if severity not in SEVERITIES:
                errors.append(f"area {area!r}: severity {severity!r} is not one of {list(SEVERITIES)}")
                continue
            if not re.search(r"\d", evidence):
                warnings.append(f"area {area!r}: {rule_id} cites no line number in its evidence")
            if rules[rule_id] not in areas[area]:
                warnings.append(f"area {area!r}: {rule_id} belongs to quick-reference section "
                                f"{rules[rule_id]}, outside this area's sections {list(areas[area])}")
            findings.append({"area": area, "rule_id": rule_id, "severity": severity,
                             "evidence": evidence, "fix": fix})
        not_checked = single(block, "NOT-CHECKED")
        if not not_checked:
            warnings.append(f"area {area!r}: NOT-CHECKED is empty; a reviewer must say what it could not check")
        reviewed.append({"area": area, "not_checked": not_checked})
    for area in areas:
        if area not in seen:
            errors.append(f"area {area!r} is missing: no block came back for it")
    findings.sort(key=lambda f: SEVERITIES.index(f["severity"]))
    return {"mode": "review", "expected": len(areas), "returned": len(seen),
            "areas": reviewed, "findings": findings, "errors": errors, "warnings": warnings}


def format_report(merged):
    out = [f"## Merge ({merged['mode']}): {merged['returned']}/{merged['expected']} parts returned"]
    if merged["mode"] == "search":
        counts = merged["verdicts"]
        out.append("Verdicts: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
        for part in merged["parts"]:
            retry = " (retried)" if part["retried"] else ""
            out.append(f"- `{part['part_id']}`: {part['verdict']}{retry}, {len(part['rows'])} row(s)")
    else:
        out.append(f"Findings: {len(merged['findings'])}")
        for finding in merged["findings"]:
            out.append(f"- [{finding['severity']}] {finding['area']} / {finding['rule_id']}: "
                       f"{finding['evidence']} -> {finding['fix']}")
        for area in merged["areas"]:
            out.append(f"- not checked in {area['area']}: {area['not_checked'] or '(unstated)'}")
    for label, key in (("Errors", "errors"), ("Warnings", "warnings")):
        if merged[key]:
            out.append(f"\n{label}:")
            out.extend(f"- {message}" for message in merged[key])
    out.append("\nRESULT: " + ("FAIL" if merged["errors"] else "OK"))
    return "\n".join(out)


def load_manifest(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["manifest"] if isinstance(data, dict) else data


def main():
    for stream in (sys.stdout, sys.stderr):
        if stream.encoding and stream.encoding.lower() != "utf-8":
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, io.UnsupportedOperation):
                pass
    parser = argparse.ArgumentParser(description="Merge and cross-check multipart subagent output")
    parser.add_argument("--mode", required=True, choices=("search", "review"))
    parser.add_argument("--manifest", help="search mode: the JSON from route.py --json, or its manifest list")
    parser.add_argument("--areas", help="review mode: comma-separated subset of areas (default: all four)")
    parser.add_argument("--results", required=True, nargs="+", help="files of agent blocks; - reads stdin")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    text = read_results(args.results)
    if args.mode == "search":
        if not args.manifest:
            parser.error("--mode search needs --manifest")
        merged = merge_search(load_manifest(args.manifest), text)
    else:
        chosen = [a.strip() for a in args.areas.split(",")] if args.areas else list(AREA_SECTIONS)
        unknown = [a for a in chosen if a not in AREA_SECTIONS]
        if unknown:
            parser.error(f"unknown area(s) {unknown}; choose from {list(AREA_SECTIONS)}")
        merged = merge_review({a: AREA_SECTIONS[a] for a in chosen}, text, load_rule_ids())

    print(json.dumps(merged, indent=2, ensure_ascii=False) if args.json else format_report(merged))
    sys.exit(1 if merged["errors"] else 0)


if __name__ == "__main__":
    main()
