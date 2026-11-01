---
name: vector-mark
description: Design a logo, icon, pattern or simple illustration as clean SVG and check it before delivery. Use when the owner wants a mark, a wordmark, an icon set, a repeating pattern or a diagram drawn as vector, or wants an existing SVG cleaned for delivery. Covers the brief, the construction, the SVG, the lint, the one-colour and small-size tests, and the delivery set.
allowed-tools: Read Grep Glob Bash(python *svg_lint.py *) Bash(python *search.py *)
---
# Vector mark

`lint` below means `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/svg_lint.py"`; `search` means
`python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py"`.

## Steps

1. **Brief.** Ask only what you cannot infer: what it stands for, where it will be used smallest, light or dark
   backgrounds, one colour or more. Read the owner's brand file if one is named; never write one.
2. **Rules.** `search "logo" --domain identity -n 8` and apply them: pick one mark type and say which; build from
   simple filled shapes; no raster, no live text in the final file; no trendy effects.
3. **Construction.** Say the grid or the shapes in one or two lines (for example "a circle, a quarter-circle cut,
   all on a 64-unit grid"). A mark that cannot be explained that simply is usually too complicated.
4. **Write the SVG.** Square `viewBox` (for example `0 0 64 64`), no fixed pixel `width`/`height`, paths and basic
   shapes only, `fill="currentColor"` for the one-colour version, a `<title>`. Keep numbers to two decimals.
5. **Lint.** `lint mark.svg`. Fix every error. Fix warnings or say why they stay. Typical fixes: add the
   `viewBox`, convert `<text>` to paths (Inkscape: Object to Path, or outline the glyphs), remove the embedded image.
6. **Test it.** Render it at 16 px and at 15 mm wide on white, then in black on white and white on black
   (`render.py mark.svg out.png --width 64 --height 64`). If it fails at small size, make a simplified small-size
   version; do not shrink the detailed one.
7. **Shrink.** `svgo mark.svg` if installed (see skill `tool-router`); otherwise leave it, and say so.
8. **Deliver.** The delivery set from the `file-set` identity rule: SVG, vector PDF, PNG at 1x and 2x, in colour and
   one colour, named `<brand>-<variant>-<colour>.<ext>`.

## Limits

- The linter reads the file; it does not judge whether the mark is good. Do the squint test (blur it, or reduce it to
  a silhouette) yourself and report what you saw.
- A mark is not final until the owner has seen it. Show it, name the choices, and list what you would change.
- Do not trace or imitate an existing brand's mark. If the owner shows one as reference, take the principle, not the shape.
