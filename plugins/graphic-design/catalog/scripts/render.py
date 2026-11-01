#!/usr/bin/env python3
"""Render an HTML or SVG file to PNG or PDF with headless Chromium (Playwright).

    python render.py poster.html out.png --width 1080 --height 1350 [--scale 2]
    python render.py poster.html out.pdf --paper A4 [--background]
    python render.py mark.svg out.png --width 512 --height 512

Needs `pip install playwright` and `playwright install chromium`; without them it exits 3
with the install line. It opens only the local file you name, over file://, and blocks
every network request, so a page cannot fetch anything or send anything out.
Exit codes: 0 written, 2 bad usage, 3 Playwright or Chromium missing, 4 render failed.
"""
import argparse
import sys
from pathlib import Path

PAPERS = {"A3", "A4", "A5", "Letter", "Legal", "Tabloid"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1350)
    parser.add_argument("--scale", type=float, default=1.0, help="device scale factor for PNG (2 = retina)")
    parser.add_argument("--paper", choices=sorted(PAPERS), help="PDF paper size (default: the page size from --width/--height)")
    parser.add_argument("--background", action="store_true", help="print CSS backgrounds in a PDF")
    args = parser.parse_args(argv)

    suffix = args.output.suffix.lower()
    if suffix not in (".png", ".pdf"):
        print("render: output must end in .png or .pdf", file=sys.stderr)
        return 2
    if not args.source.is_file():
        print(f"render: {args.source} not found", file=sys.stderr)
        return 2
    if args.width < 1 or args.height < 1 or args.scale <= 0:
        print("render: width, height and scale must be positive", file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("render: Playwright is not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        return 3

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport={"width": args.width, "height": args.height}, device_scale_factor=args.scale)
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") else route.abort())
            page.goto(args.source.resolve().as_uri())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            if suffix == ".png":
                page.screenshot(path=str(args.output), full_page=False)
            else:
                options = {"print_background": args.background, "path": str(args.output)}
                if args.paper:
                    options["format"] = args.paper
                else:
                    options["width"], options["height"] = f"{args.width}px", f"{args.height}px"
                page.pdf(**options)
            browser.close()
    except Exception as error:  # Playwright raises its own error types
        message = str(error)
        if "Executable doesn't exist" in message:
            print("render: Chromium is not installed. Run: playwright install chromium", file=sys.stderr)
            return 3
        print(f"render: {message.splitlines()[0] if message else error.__class__.__name__}", file=sys.stderr)
        return 4
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
