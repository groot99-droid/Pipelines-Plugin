#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harvest design tokens from real websites -- MAINTAINER TOOLING, NOT catalog/.

WHY THIS LIVES IN maintenance/ AND NOT catalog/scripts/
-------------------------------------------------------
The ui-design-catalog skill promises its users, verbatim in
skills/ui-design-catalog/SKILL.md (in the plugin root):

    "the scripts need Python 3 and use only the standard library
     -- no third-party packages, no network access"

catalog/scripts/ is the half of this tool that keeps that promise. The skill
runs only what is in catalog/; maintenance/ holds the tools that need
dependencies, the network, or a secret, so anything here stays a maintainer
tool and that promise stays true. Harvested results reach users only as
reviewed rows in the CSVs -- never as a live fetch at skill runtime.

HOW CAPTURE WORKS
-----------------
This script does not crawl. It normalizes a JSON capture produced by running
EXTRACTOR_JS (below) in a real browser against a loaded page.

Computed styles are the whole point: a design token is what the browser
*resolved*, not what a stylesheet declared. Static HTML+CSS fetching misses the
cascade, JS-applied themes, and @layer/@theme blocks entirely.

THREE FAILURE MODES THIS GUARDS AGAINST
---------------------------------------
Each was hit while building this, and each returns data that looks plausible:

1. Storybook/iframe shells. primer.style redirects into a Storybook whose
   tokens live in an iframe. The outer document yields 0 custom properties but
   still yields a full type scale -- of Storybook's own chrome. Guard: reject a
   capture with iframes and near-zero color variety.

2. Tokens outside :root. Tailwind v4 declares in @theme/@layer, and
   cross-origin stylesheets throw on .cssRules. Reading stylesheets found 2
   variables on a page with hundreds. Guard: the extractor reads rendered
   elements, never stylesheets.

3. Modern color spaces. getComputedStyle returns oklab()/lab() for any color
   authored that way -- on tailwindcss.com only 1 of 13 distinct backgrounds
   came back as rgb(). An rgb-only parser silently drops ~90% and reports
   success. Guard: the extractor canonicalizes through a 1x1 canvas, which uses
   the browser's own color engine and handles every present and future color
   function exactly.

USAGE
-----
    # 1. In a browser, on the target page, run EXTRACTOR_JS and save the JSON.
    python maintenance/harvest-site-tokens.py show-extractor > extract.js

    # 2. Normalize one or more captures into a review report.
    python maintenance/harvest-site-tokens.py report captures/*.json

Output is a proposal for human review, never a direct CSV write. Harvested
values describe one page of one site at one moment; promoting them into the
catalog is an editorial decision with a licensing dimension (see
SOURCE-RESEARCH.md at the plugin root).
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# A CSS pill radius (9999px, or calc(infinity)) resolves to an enormous used
# value. Anything past this is a pill, not a measured corner.
PILL_RADIUS_THRESHOLD_PX = 1000

# Below this many sampled elements the page probably had not finished
# rendering, or we captured a shell rather than the real document.
MIN_ELEMENTS = 150

# A real page renders more than a couple of distinct surface colors. Fewer
# means the color pipeline dropped them (failure mode 3) or we got a shell.
MIN_DISTINCT_BACKGROUNDS = 3

EXTRACTOR_JS = r"""
/* Run on a fully loaded page; returns a JSON string to save as a capture.
   Reads RENDERED ELEMENTS, not stylesheets, and canonicalizes every color
   through a 1x1 canvas so oklab()/lab()/color() resolve exactly. */
(() => {
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const ctx = cv.getContext('2d', { willReadFrequently: true });
  const hex = (css) => {
    if (!css || css === 'transparent') return null;
    try {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = '#000';
      ctx.fillStyle = css;
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      if (d[3] < 240) return null;            // translucent: an overlay, not a token
      return '#' + [d[0], d[1], d[2]].map(v => v.toString(16).padStart(2, '0'))
        .join('').toUpperCase();
    } catch (e) { return null; }
  };

  const bg = {}, fg = {}, bd = {}, type = {}, space = {}, fam = {}, radius = {};
  let n = 0, skipped = 0;

  document.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) { skipped++; return; }
    n++;
    const s = getComputedStyle(el);

    // Backgrounds weighted by painted area: a page's real surface color is the
    // one covering the most pixels, not the one on the most elements.
    const b = hex(s.backgroundColor);
    if (b) bg[b] = (bg[b] || 0) + r.width * r.height;

    if (parseFloat(s.borderTopWidth) > 0) {
      const c = hex(s.borderTopColor);
      if (c) bd[c] = (bd[c] || 0) + 1;
    }
    if (parseFloat(s.borderTopLeftRadius) > 0) {
      radius[s.borderTopLeftRadius] = (radius[s.borderTopLeftRadius] || 0) + 1;
    }

    // Leaf nodes only: a wrapper inherits color but paints no glyphs.
    const text = el.children.length === 0 && el.textContent && el.textContent.trim();
    if (text && text.length > 1) {
      // Text colors weighted by glyph count: body copy should outrank a label.
      const c = hex(s.color);
      if (c) fg[c] = (fg[c] || 0) + text.length;
      const k = `${s.fontSize}|${s.fontWeight}|${s.lineHeight}`;
      type[k] = (type[k] || 0) + 1;
      const f = s.fontFamily.split(',')[0].replace(/["']/g, '').trim();
      if (f) fam[f] = (fam[f] || 0) + text.length;
    }

    [s.gap, s.rowGap, s.paddingTop, s.paddingLeft, s.marginBottom].forEach(v => {
      if (v && /^\d+(\.\d+)?px$/.test(v) && v !== '0px') space[v] = (space[v] || 0) + 1;
    });
  });

  const top = (o, k) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, k)
    .map(([value, weight]) => ({ value, weight: Math.round(weight) }));

  return JSON.stringify({
    url: location.href, title: document.title,
    capturedAt: new Date().toISOString(),
    viewport: { w: innerWidth, h: innerHeight },
    elementsSampled: n, elementsSkipped: skipped,
    iframes: document.querySelectorAll('iframe').length,
    backgroundsByArea: top(bg, 16), textColorsByGlyphs: top(fg, 10),
    borderColors: top(bd, 8), typeSteps: top(type, 14),
    spacing: top(space, 16), radii: top(radius, 8), families: top(fam, 6),
  });
})()
"""


def _px(value):
    try:
        return float(str(value).rstrip("px"))
    except ValueError:
        return None


def validate(capture: dict) -> list:
    """Reasons this capture should not be trusted. Empty list means usable."""
    problems = []
    sampled = capture.get("elementsSampled", 0)
    backgrounds = capture.get("backgroundsByArea", [])

    if sampled < MIN_ELEMENTS:
        problems.append(
            f"only {sampled} elements sampled (< {MIN_ELEMENTS}) -- page may not "
            "have finished rendering")
    if len(backgrounds) < MIN_DISTINCT_BACKGROUNDS:
        problems.append(
            f"only {len(backgrounds)} distinct background(s) -- colors were "
            "probably dropped, or this is a shell page")
    if capture.get("iframes", 0) > 0 and len(backgrounds) < 5:
        problems.append(
            f"{capture['iframes']} iframe(s) present and few colors found -- this "
            "looks like a Storybook/embed shell; the real tokens are inside the "
            "frame, so any type scale here belongs to the shell's chrome")
    if not capture.get("typeSteps"):
        problems.append("no type steps captured")

    viewport = capture.get("viewport") or {}
    if not viewport.get("w"):
        problems.append(
            "viewport width reported as 0 -- responsive values in this capture "
            "cannot be attributed to a known breakpoint (advisory)")
    return problems


def normalize_radii(radii: list) -> dict:
    """Split measured corner radii from pill radii."""
    measured, pills = [], 0
    for entry in radii or []:
        value = _px(entry["value"])
        if value is None:
            continue
        if value >= PILL_RADIUS_THRESHOLD_PX:
            pills += entry["weight"]
        else:
            measured.append((value, entry["weight"]))
    measured.sort()
    return {"measured": measured, "pillUses": pills}


def infer_spacing_base(spacing: list):
    """Find the base unit a spacing scale is built on.

    Reports how much of the observed spacing is an exact multiple, because a
    site mixing 4px steps with em-derived values (11.2px, 8.4px) does not have
    a 4px scale, and recording one would be wrong.
    """
    values = [(_px(e["value"]), e["weight"]) for e in spacing or []]
    values = [(v, w) for v, w in values if v]
    if not values:
        return None
    total = sum(w for _, w in values)
    scored = []
    for base in (2, 4, 8):
        hit = sum(w for v, w in values if abs(v / base - round(v / base)) < 1e-6)
        scored.append({"base": base, "share": round(hit / total, 3)})

    # Every multiple of 8 is also a multiple of 4 and 2, so a clean 8px scale
    # scores 1.0 on all three. Ties must resolve to the LARGEST base: calling
    # an 8px scale "2px" is not a smaller claim, it is a wrong one.
    top_share = max(entry["share"] for entry in scored)
    best = max((e for e in scored if e["share"] == top_share),
               key=lambda e: e["base"])
    off = sorted({v for v, _ in values
                  if abs(v / best["base"] - round(v / best["base"])) > 1e-6})
    best["offScale"] = off
    return best


def summarize_type(type_steps: list) -> list:
    """Collapse raw fontSize|weight|lineHeight triples into a readable scale."""
    rows = []
    for entry in type_steps or []:
        size, weight, line_height = entry["value"].split("|")
        size_px, lh_px = _px(size), _px(line_height)
        ratio = round(lh_px / size_px, 2) if size_px and lh_px else None
        rows.append({"size": size, "weight": weight, "lineHeight": line_height,
                     "ratio": ratio, "uses": entry["weight"]})
    rows.sort(key=lambda r: (-r["uses"]))
    return rows


def looks_like_css_var(family: str) -> bool:
    """Heuristic: 'plexMono'/'inter' are custom-property names, not families.

    Real CSS family names are title-cased words ("Inter", "Geist", "IBM Plex
    Mono"). A bare camelCase or lowercase token is what a var indirection
    leaves behind, and recording it as a font family would be wrong.
    """
    return bool(family) and " " not in family and family[:1].islower()


def report(capture: dict) -> str:
    lines = []
    url = capture.get("url", "?")
    lines.append(f"## {capture.get('title', url)}")
    lines.append(f"   {url}")
    lines.append(f"   sampled {capture.get('elementsSampled', 0)} elements "
                 f"({capture.get('elementsSkipped', 0)} too small to matter)")

    problems = validate(capture)
    if problems:
        lines.append("")
        lines.append("   !! CAPTURE NOT TRUSTED:")
        for problem in problems:
            lines.append(f"      - {problem}")

    lines.append("")
    lines.append("   Surfaces (by painted area):")
    for entry in (capture.get("backgroundsByArea") or [])[:6]:
        lines.append(f"      {entry['value']}  area={entry['weight']:,}")

    lines.append("   Text colors (by glyph count):")
    for entry in (capture.get("textColorsByGlyphs") or [])[:5]:
        lines.append(f"      {entry['value']}  glyphs={entry['weight']:,}")

    lines.append("")
    lines.append("   Type scale:")
    for row in summarize_type(capture.get("typeSteps"))[:8]:
        lines.append(f"      {row['size']:>9} / {row['weight']:<4} "
                     f"lh {row['lineHeight']:>9} (x{row['ratio']})  uses={row['uses']}")

    spacing = infer_spacing_base(capture.get("spacing"))
    if spacing:
        lines.append("")
        lines.append(f"   Spacing: {int(spacing['share'] * 100)}% of observed values "
                     f"are multiples of {spacing['base']}px")
        if spacing["offScale"]:
            shown = ", ".join(f"{v:g}px" for v in spacing["offScale"][:6])
            lines.append(f"      off-scale (likely em-derived): {shown}")

    radii = normalize_radii(capture.get("radii"))
    if radii["measured"] or radii["pillUses"]:
        shown = ", ".join(f"{v:g}px(x{w})" for v, w in radii["measured"][:5])
        lines.append(f"   Radii: {shown or 'none'}"
                     + (f" + {radii['pillUses']} pill uses" if radii["pillUses"] else ""))

    families = capture.get("families") or []
    real = [f for f in families if not looks_like_css_var(f["value"])]
    masked = [f for f in families if looks_like_css_var(f["value"])]
    lines.append(f"   Fonts: {', '.join(f['value'] for f in real) or 'none resolved'}")
    if masked:
        lines.append(f"      unresolved var indirection (NOT font names): "
                     f"{', '.join(f['value'] for f in masked)}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show-extractor", help="print the browser extraction snippet")
    report_cmd = sub.add_parser("report", help="normalize capture JSON into a review report")
    report_cmd.add_argument("captures", nargs="+", type=Path)

    args = parser.parse_args(argv)

    if args.command == "show-extractor":
        print(EXTRACTOR_JS.strip())
        return 0

    untrusted = 0
    for path in args.captures:
        if not path.exists():
            print(f"missing: {path}", file=sys.stderr)
            continue
        capture = json.loads(path.read_text(encoding="utf-8"))
        print(report(capture))
        print()
        if validate(capture):
            untrusted += 1

    if untrusted:
        print(f"{untrusted} capture(s) flagged as untrusted -- do not promote "
              f"these into the catalog without re-capturing.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
