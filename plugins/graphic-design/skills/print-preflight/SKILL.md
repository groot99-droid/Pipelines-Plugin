---
name: print-preflight
description: Check a layout against print rules before it is sent to a printer or exported as a final PDF - bleed, safe margin, image resolution at placed size, colour mode, ink limit, hairlines, minimum text size, font embedding, PDF/X. Use before delivering any print file, and whenever the owner asks whether a design is print-ready.
allowed-tools: Read Grep Glob Bash(python *preflight.py *) Bash(python *search.py *)
---
# Print preflight

`preflight` below means `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/preflight.py"`. It does not open the artwork or the
PDF. It checks a small JSON description of the layout, so the result is only as true as that description. Say that
when you report.

## Steps

1. **Find the spec.** `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<product>" --domain print` for the trim,
   bleed and safe margin. If the printer gave their own figures, use theirs and say so.
2. **Describe the layout.** Write a JSON file in the scratch folder (never in the owner's project folder) with the keys in
   the docstring of `preflight.py`: `target`, `trim_mm`, `bleed_mm`, `safe_mm`, `colour_mode`, `total_ink_pct`,
   `min_text_pt`, `min_stroke_pt`, `fonts`, `images` (pixel size and placed size in mm), `pdf_standard`. Fill a key only
   from something you measured or were told; leave the others out. A missing key is reported as "not checked".
3. **Run it.** `preflight layout.json`. Exit 1 means at least one error.
4. **Report.** Errors first, then warnings, then what was not checked. For each error give the fix:
   - bleed or safe margin: extend background and images to the bleed edge; pull live text inward.
   - image resolution: replace the image or place it smaller; upscaling adds no detail.
   - RGB: convert to the printer's profile and proof the colours that shifted.
   - fonts: embed or outline them.
5. **Never say "print-ready".** Say "no errors in the checks that ran", list the checks that did not run, and tell the
   owner to ask the printer for a proof.

## Limits

- Ink limits and PDF standards vary by printer and paper; the catalog gives typical values (`--domain color`).
- Overprint, spot colours, varnish layers and die lines need a person looking at a preview in the layout app.
