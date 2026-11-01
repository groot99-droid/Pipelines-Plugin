#!/usr/bin/env python3
"""Lint an SVG mark or illustration for delivery. Stdlib only; reads the file, never runs it.

    python svg_lint.py mark.svg [--json] [--max-bytes 20000]

Checks: parses as XML; has a viewBox; no script, no external reference, no embedded
raster; text converted to outlines; no hairline strokes; has a title for accessibility;
size. Exit codes: 0 no errors, 1 at least one error, 2 bad input.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}"
STROKE_NUMBER = re.compile(r"^-?\d*\.?\d+")


def local(tag):
    return tag.rsplit("}", 1)[-1]


def finding(level, code, message):
    return {"level": level, "code": code, "message": message}


def lint(text, max_bytes=20000):
    findings = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        return [finding("error", "xml", f"not valid XML: {error}")]
    if local(root.tag) != "svg":
        return [finding("error", "root", "the root element is not <svg>")]

    box = root.get("viewBox")
    if not box:
        findings.append(finding("error", "viewbox", "no viewBox; the mark will not scale"))
    else:
        try:
            parts = [float(p) for p in box.replace(",", " ").split()]
            if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
                raise ValueError
        except ValueError:
            findings.append(finding("error", "viewbox", f"viewBox {box!r} is not four numbers with a positive width and height"))

    height_units = None
    for element in root.iter():
        name = local(element.tag)
        if name == "script":
            findings.append(finding("error", "script", "contains <script>"))
        elif name == "text":
            findings.append(finding("warn", "text", "live <text>: convert type to outlines in the delivered file"))
        elif name == "image":
            findings.append(finding("warn", "raster", "embeds an <image>; a vector mark should be paths and shapes only"))
        elif name == "filter":
            findings.append(finding("warn", "filter", "uses a <filter>; effects often render differently or not at all"))
        for key, value in element.attrib.items():
            if key in ("href", XLINK + "href") and value and not value.startswith("#") and not value.startswith("data:"):
                findings.append(finding("error", "external", f"external reference {value[:60]!r}"))
            if key.startswith("on"):
                findings.append(finding("error", "script", f"event handler attribute {key}"))
        widths = []
        if element.get("stroke-width"):
            widths.append(element.get("stroke-width"))
        style = element.get("style") or ""
        widths += re.findall(r"stroke-width\s*:\s*([^;]+)", style)
        for raw in widths:
            match = STROKE_NUMBER.match(raw.strip())
            if match and 0 < float(match.group()) < 0.25 and root.get("viewBox"):
                findings.append(finding("warn", "hairline", f"stroke-width {raw.strip()} is a hairline in viewBox units"))

    if not any(local(e.tag) == "title" for e in root.iter()):
        findings.append(finding("info", "title", "no <title>; add one if the mark is used inline as an image"))
    size = len(text.encode("utf-8"))
    if size > max_bytes:
        findings.append(finding("warn", "size", f"{size} bytes; over {max_bytes}. Run svgo and check for stray precision"))
    return findings


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    max_bytes = 20000
    paths = []
    skip = False
    for i, arg in enumerate(argv):
        if skip:
            skip = False
        elif arg == "--max-bytes":
            try:
                max_bytes, skip = int(argv[i + 1]), True
            except (IndexError, ValueError):
                print("svg_lint: --max-bytes needs a number", file=sys.stderr)
                return 2
        elif not arg.startswith("--"):
            paths.append(arg)
    if len(paths) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        text = Path(paths[0]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"svg_lint: {error}", file=sys.stderr)
        return 2
    findings = lint(text, max_bytes)
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
