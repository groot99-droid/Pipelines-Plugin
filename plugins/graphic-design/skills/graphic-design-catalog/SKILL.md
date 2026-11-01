---
name: graphic-design-catalog
description: Look up graphic-design facts before making a poster, flyer, card, social image, logo or layout - print sizes with bleed and safe margins, print colour rules (ink limits, rich black, hairlines, fonts), platform image sizes, logo and identity rules, grids and hierarchy, illustration styles. Use at the start of any print or social design task, and whenever a size, a margin or a print rule is about to be guessed.
allowed-tools: Read Grep Glob Bash(python *search.py *)
---
# Graphic-design catalog

`search` below means `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py"`. It reads seven small CSV tables
in `${CLAUDE_PLUGIN_ROOT}/catalog/data/`, ranks rows with BM25, never touches the network and never writes a file.

```
search "business card" --domain print
search "instagram story" --domain social
search "small text black" --domain color
search "logo small size" --domain identity
search "poster swiss" --domain grid
search "risograph" --domain style
```

Without `--domain` it guesses and says which domain it picked. Add `--json` for machine-readable rows and
`-n 5` for more rows. Exit 1 means no row matched: say so, do not invent a figure.

## How to use it

1. Name the deliverable and where it ends up (print, screen, both). Ask the owner if you cannot tell.
2. Look up its size, bleed and safe margin (`print`) or its pixel size (`social`), then its colour rules (`color`).
3. Pick a grid (`grid`) and, for illustration, a style (`style`). Say why in a line.
4. Make the piece: SVG by hand (skill `vector-mark`), or HTML and CSS rendered with
   `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/render.py" in.html out.png --width W --height H`
   (PNG) or `... out.pdf --paper A4 --background` (PDF). Raster images come from a provider; see skill `tool-router`.
5. Before anything goes to a printer, run skill `print-preflight`.

## Honest limits

- The figures are typical industry values. The printer or the platform has the final say, and platform sizes change.
  Tell the owner which figures to confirm before money is spent.
- Claude writes SVG and HTML; it does not output a raster picture directly. A photographic or painterly image needs
  a provider.
- Brand colours, type and gates belong to the owner. Propose changes; never write over a brand file.
