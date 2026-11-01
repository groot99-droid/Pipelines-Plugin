#!/usr/bin/env python3
"""Print preflight: check a JSON description of a layout against print rules. Stdlib only.

    python preflight.py layout.json [--json]

The file describes the layout; this script never opens the artwork itself:

    {
      "target": "print",                      // print | large-format
      "trim_mm": [210, 297],
      "bleed_mm": 3,
      "safe_mm": 5,                           // distance of live content from the trim, as built
      "colour_mode": "CMYK",                  // CMYK | RGB
      "total_ink_pct": 280,                   // highest C+M+Y+K in the artwork, if known
      "min_text_pt": 8,
      "min_stroke_pt": 0.5,
      "fonts": [{"name": "Inter", "embedded": true}],
      "images": [{"name": "hero.jpg", "px": [3000, 2000], "placed_mm": [210, 140]}],
      "pdf_standard": "PDF/X-4"               // optional
    }

Every key is optional; a missing key is reported as "not checked", never as a pass.
Exit codes: 0 no errors, 1 at least one error, 2 bad input.
"""
import json
import sys
from pathlib import Path

MM_PER_INCH = 25.4
RULES = {
    "print": {"min_ppi_error": 150, "min_ppi_warn": 250, "bleed_mm": 3.0, "safe_mm": 3.0},
    "large-format": {"min_ppi_error": 72, "min_ppi_warn": 100, "bleed_mm": 3.0, "safe_mm": 10.0},
}
INK_LIMIT = 300
MIN_TEXT_PT = 6
MIN_STROKE_PT = 0.25


def finding(level, code, message):
    return {"level": level, "code": code, "message": message}


def check(spec):
    findings = []
    target = spec.get("target", "print")
    if target not in RULES:
        raise ValueError(f"target must be one of {sorted(RULES)}")
    rule = RULES[target]

    if "bleed_mm" in spec:
        if spec["bleed_mm"] < rule["bleed_mm"]:
            findings.append(finding("error", "bleed", f"bleed is {spec['bleed_mm']} mm; at least {rule['bleed_mm']} mm is needed"))
    else:
        findings.append(finding("info", "bleed", "bleed not checked: bleed_mm missing"))

    if "safe_mm" in spec:
        if spec["safe_mm"] < rule["safe_mm"]:
            findings.append(finding("warn", "safe-zone", f"live content sits {spec['safe_mm']} mm from the trim; keep it at least {rule['safe_mm']} mm in"))
    else:
        findings.append(finding("info", "safe-zone", "safe zone not checked: safe_mm missing"))

    mode = spec.get("colour_mode")
    if mode is None:
        findings.append(finding("info", "colour-mode", "colour mode not checked: colour_mode missing"))
    elif mode.upper() == "RGB":
        findings.append(finding("warn", "colour-mode", "artwork is RGB; convert to the printer's CMYK profile and proof the result"))

    if "total_ink_pct" in spec and spec["total_ink_pct"] > INK_LIMIT:
        findings.append(finding("warn", "ink-limit", f"total ink {spec['total_ink_pct']}% is over {INK_LIMIT}%; check the printer's limit"))
    elif "total_ink_pct" not in spec:
        findings.append(finding("info", "ink-limit", "ink limit not checked: total_ink_pct missing"))

    if "min_text_pt" in spec and spec["min_text_pt"] < MIN_TEXT_PT:
        findings.append(finding("warn", "text-size", f"smallest text is {spec['min_text_pt']} pt; under {MIN_TEXT_PT} pt may not read"))
    if "min_stroke_pt" in spec and spec["min_stroke_pt"] < MIN_STROKE_PT:
        findings.append(finding("error", "hairline", f"thinnest stroke is {spec['min_stroke_pt']} pt; under {MIN_STROKE_PT} pt may not print"))

    fonts = spec.get("fonts")
    if fonts is None:
        findings.append(finding("info", "fonts", "fonts not checked: fonts missing"))
    else:
        for font in fonts:
            if not font.get("embedded"):
                findings.append(finding("error", "fonts", f"font {font.get('name', '?')} is not embedded or outlined"))

    images = spec.get("images")
    if images is None:
        findings.append(finding("info", "images", "images not checked: images missing"))
    else:
        for image in images:
            try:
                (px_w, px_h), (mm_w, mm_h) = image["px"], image["placed_mm"]
                ppi = min(px_w / (mm_w / MM_PER_INCH), px_h / (mm_h / MM_PER_INCH))
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                findings.append(finding("warn", "images", f"image {image.get('name', '?')}: needs px and placed_mm"))
                continue
            name = image.get("name", "?")
            if ppi < rule["min_ppi_error"]:
                findings.append(finding("error", "image-resolution", f"{name} is {ppi:.0f} ppi at its placed size; under {rule['min_ppi_error']} ppi will look soft"))
            elif ppi < rule["min_ppi_warn"]:
                findings.append(finding("warn", "image-resolution", f"{name} is {ppi:.0f} ppi at its placed size; {rule['min_ppi_warn']}+ is safer"))

    standard = spec.get("pdf_standard")
    if standard is not None and not str(standard).upper().replace(" ", "").startswith("PDF/X"):
        findings.append(finding("warn", "pdf-standard", f"{standard} is not a PDF/X standard; ask the printer what they accept"))
    return findings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if len(paths) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        spec = json.loads(Path(paths[0]).read_text(encoding="utf-8"))
        findings = check(spec)
    except (OSError, ValueError) as error:
        print(f"preflight: {error}", file=sys.stderr)
        return 2
    errors = sum(f["level"] == "error" for f in findings)
    if as_json:
        print(json.dumps({"errors": errors, "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['level'].upper():5} {f['code']}: {f['message']}")
        print(f"\n{errors} error(s), {sum(f['level'] == 'warn' for f in findings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
