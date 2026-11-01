#!/usr/bin/env python3
"""Search the graphic-design catalog: BM25 over the CSVs in ../data. Stdlib only, no network.

    python search.py "business card" --domain print
    python search.py "instagram story" --domain social --json
    python search.py "logo small" --domain identity -n 5

Domains: print, color, social, identity, grid, style, tool. With no --domain the best
domain for the query is guessed and named in the output.
Exit codes: 0 results, 1 no match, 2 bad usage.
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from math import log
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

DOMAINS = {
    "print": ("print-specs.csv", ["Name", "Trim", "Keywords", "Notes"]),
    "color": ("color-print.csv", ["Topic", "Rule", "Keywords", "Notes"]),
    "social": ("social-sizes.csv", ["Platform", "Placement", "Keywords", "Notes"]),
    "identity": ("identity-rules.csv", ["Topic", "Rule", "Keywords", "Notes"]),
    "grid": ("grids.csv", ["Format", "Grid", "Keywords", "Notes"]),
    "style": ("illustration-styles.csv", ["Style", "Traits", "Good for", "Keywords"]),
    "tool": ("tools.csv", ["Job", "Provider", "Route", "How"]),
}

TOKEN = re.compile(r"[a-z0-9]+")
K1, B = 1.5, 0.75


def tokens(text):
    return TOKEN.findall(text.lower())


def load(domain):
    name, _ = DOMAINS[domain]
    with open(DATA / name, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rank(domain, query):
    rows = load(domain)
    _, columns = DOMAINS[domain]
    docs = [tokens(" ".join(row[c] for c in columns)) for row in rows]
    average = sum(len(d) for d in docs) / max(len(docs), 1)
    frequency = defaultdict(int)
    for doc in docs:
        for term in set(doc):
            frequency[term] += 1
    terms = tokens(query)
    scored = []
    for row, doc in zip(rows, docs):
        score = 0.0
        for term in terms:
            if term not in doc:
                continue
            n = len(docs)
            idf = log((n - frequency[term] + 0.5) / (frequency[term] + 0.5) + 1)
            tf = doc.count(term)
            score += idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(doc) / max(average, 1)))
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda pair: -pair[0])
    return scored


def guess_domain(query):
    best, best_score = None, 0.0
    for domain in DOMAINS:
        hits = rank(domain, query)
        if hits and hits[0][0] > best_score:
            best, best_score = domain, hits[0][0]
    return best


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("query")
    parser.add_argument("--domain", choices=sorted(DOMAINS))
    parser.add_argument("-n", "--max-results", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not tokens(args.query):
        print("empty query", file=sys.stderr)
        return 2
    domain = args.domain or guess_domain(args.query)
    if domain is None:
        print("no match", file=sys.stderr)
        return 1
    hits = rank(domain, args.query)[: max(args.max_results, 1)]
    if not hits:
        print("no match", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"domain": domain, "results": [{"score": round(s, 3), **r} for s, r in hits]}, indent=2))
        return 0
    print(f"domain: {domain}" + ("" if args.domain else " (guessed)"))
    for score, row in hits:
        print(f"\n[{row['ID']}] score {score:.2f}")
        for key, value in row.items():
            if key != "ID" and value:
                print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
