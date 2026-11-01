# Changelog

## 0.1.0

- Catalog (stdlib, no network) of print specs, print colour rules, social sizes, identity rules, grids,
  illustration styles and a tool-routing table, with a BM25 `search.py`.
- `preflight.py` checks a JSON description of a layout against print rules; `svg_lint.py` checks an SVG
  mark for delivery; `render.py` renders HTML or SVG to PNG or PDF with headless Chromium.
- Skills `graphic-design-catalog`, `vector-mark`, `print-preflight`, `tool-router`; agents
  `print-preflight-reviewer` and `brand-consistency-reviewer`.
