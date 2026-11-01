# graphic-design

Graphic design for print and screen, as a Claude Code plugin. It does not draw pictures by itself: it gives a session
the facts, the checks and the routing it needs to make a poster, a logo, a card or a social image properly, and to know
which app or provider to hand the parts it cannot do.

## What is in it

| Piece | What it does |
|---|---|
| `catalog/` | Seven small CSV tables searched with BM25 (stdlib, no network): print specs, print colour rules, social sizes, identity rules, grids, illustration styles, and a tool-routing table |
| `skills/graphic-design-catalog` | Look up sizes, margins, rules and styles before making anything |
| `skills/vector-mark` | Design a logo, icon or pattern as clean SVG, lint it, test it small and in one colour, deliver the set |
| `skills/print-preflight` | Check a described layout against print rules; never says "print-ready" |
| `skills/tool-router` | Which app, provider or command line does which job, and whether it is verified |
| `agents/print-preflight-reviewer` | A written second look at one print layout |
| `agents/brand-consistency-reviewer` | One piece against one brand's own rules |

## Scripts (`catalog/scripts/`, all stdlib except `render.py`)

```
python catalog/scripts/search.py "business card" --domain print
python catalog/scripts/preflight.py layout.json
python catalog/scripts/svg_lint.py mark.svg
python catalog/scripts/render.py poster.html out.png --width 1080 --height 1350
```

`render.py` needs `pip install playwright` and `playwright install chromium`; it opens only the local file you name and
blocks every network request. The CSVs are generated from `catalog/scripts/_build_data.py`: edit a row there, run it, and
commit both.

## Limits, said plainly

- The figures are typical industry values. The printer or the platform decides; confirm anything that costs money.
- `preflight.py` checks a description of the layout, not the artwork or the PDF. A missing key is reported as "not
  checked".
- Claude writes SVG and HTML. Photographic or painterly pictures come from a provider, listed in `tools.csv`.
- Rows marked "Unverified" in `tools.csv` (community MCP servers) are proposals; nothing here installs or enables one.
- The plugin never writes a brand file. Brand colours, type and gates belong to the owner.

## Installing

From the repo's marketplace: `/plugin marketplace add groot99-droid/Pipelines-Plugin`, then
`/plugin install graphic-design@rosw`. Skills and agents are namespaced `graphic-design:`.

Tests: `python -m unittest discover -s catalog/tests`.
