#!/usr/bin/env python3
"""Writes the catalog CSVs under ../data from the tables below.

The tables are the source; the CSVs are generated and committed. Edit a row here,
run this script, commit both. Stdlib only. Values are typical industry figures:
confirm anything that costs money (print specs, ink limits, platform sizes) with
the printer or the platform before delivery.
"""
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def write(name, header, rows):
    for row in rows:
        if len(row) != len(header):
            raise SystemExit(f"{name}: row has {len(row)} cells, header has {len(header)}: {row[0]}")
    with open(DATA / name, "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle, lineterminator="\n")
        out.writerow(header)
        out.writerows(rows)


PRINT = [
    ["a0", "A0 poster", "841 x 1189 mm", "3 mm (5 mm large format)", "10 mm", "100-150 ppi at final size", "CMYK or RGB per printer", "poster large format wall plan architectural", "Large-format printers usually take lower ppi; ask the printer."],
    ["a1", "A1 poster", "594 x 841 mm", "3 mm", "10 mm", "150 ppi at final size", "CMYK", "poster event wall", "Typical event poster."],
    ["a2", "A2 poster", "420 x 594 mm", "3 mm", "8 mm", "200-300 ppi at final size", "CMYK", "poster print wall", "Common for posters and prints."],
    ["a3", "A3 flyer or poster", "297 x 420 mm", "3 mm", "6 mm", "300 ppi at final size", "CMYK", "flyer poster print magazine spread", "Also the trim of an A4 spread."],
    ["a4", "A4 document or flyer", "210 x 297 mm", "3 mm", "5 mm", "300 ppi at final size", "CMYK", "flyer letter brochure document print", "Default office and flyer size outside North America."],
    ["a5", "A5 flyer or leaflet", "148 x 210 mm", "3 mm", "5 mm", "300 ppi at final size", "CMYK", "flyer leaflet postcard handout", "Half of A4."],
    ["a6", "A6 postcard", "105 x 148 mm", "3 mm", "4 mm", "300 ppi at final size", "CMYK", "postcard invitation card", "Quarter of A4."],
    ["dl", "DL flyer or rack card", "99 x 210 mm", "3 mm", "5 mm", "300 ppi at final size", "CMYK", "dl flyer leaflet rack card tri-fold", "One third of an A4 sheet; common tri-fold panel."],
    ["us-letter", "US Letter", "8.5 x 11 in", "0.125 in", "0.25 in", "300 ppi at final size", "CMYK", "letter flyer document print us", "Default office size in North America."],
    ["us-legal", "US Legal", "8.5 x 14 in", "0.125 in", "0.25 in", "300 ppi at final size", "CMYK", "legal document print us", "Legal documents."],
    ["us-tabloid", "US Tabloid or Ledger", "11 x 17 in", "0.125 in", "0.25 in", "300 ppi at final size", "CMYK", "tabloid ledger poster spread us", "Two US Letter pages side by side."],
    ["us-poster-18x24", "US poster 18 x 24 in", "18 x 24 in", "0.125 in", "0.5 in", "200-300 ppi at final size", "CMYK", "poster us print wall", "Common US poster size."],
    ["us-poster-24x36", "US poster 24 x 36 in", "24 x 36 in", "0.125 in", "0.5 in", "150-200 ppi at final size", "CMYK", "poster us print wall movie", "Common US one-sheet and wall poster size."],
    ["business-card-us", "Business card (US)", "3.5 x 2 in", "0.125 in", "0.125 in", "300-600 ppi at final size", "CMYK", "business card us small", "Keep text 0.125 in inside the trim."],
    ["business-card-eu", "Business card (EU)", "85 x 55 mm", "3 mm", "3 mm", "300-600 ppi at final size", "CMYK", "business card eu small", "Common European size."],
    ["postcard-us", "Postcard (US)", "6 x 4 in", "0.125 in", "0.25 in", "300 ppi at final size", "CMYK", "postcard mail us", "Leave the address area clear if it will be mailed."],
    ["book-trade", "Trade paperback cover", "5.5 x 8.5 in", "0.125 in", "0.25 in", "300 ppi at final size", "CMYK", "book cover paperback spine", "Spine width depends on page count and paper; get it from the printer."],
    ["brochure-trifold", "Tri-fold brochure (letter)", "11 x 8.5 in flat", "0.125 in", "0.25 in per panel", "300 ppi at final size", "CMYK", "brochure trifold folded panel", "The folded-in panel is usually 1/16 in narrower."],
    ["banner-rollup", "Roll-up banner", "850 x 2000 mm", "10 mm", "50 mm", "100-150 ppi at final size", "CMYK", "banner rollup stand event", "Keep key content well above the floor end."],
    ["sticker-die", "Die-cut sticker", "per shape", "1.5-3 mm", "3 mm inside the cut line", "300 ppi at final size", "CMYK", "sticker die cut vinyl", "Supply a separate cut path as a named spot colour or its own layer."],
]

COLOR = [
    ["rgb-cmyk", "Colour mode", "Convert to CMYK for offset and most digital print; keep RGB only if the printer asks for it", "CMYK", "rgb cmyk convert mode profile", "Bright RGB blues, greens and oranges shift when converted. Proof them."],
    ["ink-coated", "Total ink limit, coated", "Sum of C+M+Y+K at any pixel", "300% (FOGRA39 about 330%, SWOP v2 300%)", "ink limit tac coated sheetfed", "Typical values; the printer's profile decides."],
    ["ink-uncoated", "Total ink limit, uncoated", "Sum of C+M+Y+K at any pixel", "260-280%", "ink limit tac uncoated paper", "Uncoated paper absorbs more; lower the limit."],
    ["ink-news", "Total ink limit, newsprint", "Sum of C+M+Y+K at any pixel", "240%", "ink limit tac newsprint", "Newsprint prints dull and spreads."],
    ["rich-black", "Rich black", "Use rich black for large black areas, plain K for small text", "about C60 M40 Y40 K100 for large areas", "rich black k text registration", "Never use four-colour black for body text; misregistration blurs it."],
    ["small-text-k", "Small text colour", "Set text under about 12 pt in a single ink, not a CMYK mix", "K100 or one spot", "small text black registration", "Mixed inks misregister and make thin strokes fuzzy."],
    ["hairline", "Minimum stroke", "Strokes thinner than this may not print", "0.25 pt (0.1 mm) at least; 0.5 pt safer; reversed out 1 pt", "hairline stroke line weight", "Reversed-out (white on colour) strokes need more."],
    ["min-text", "Minimum text size", "Smallest readable size", "6 pt on white; 8 pt reversed or on texture", "text size small print legible", "Thin serif faces need more."],
    ["bleed", "Bleed", "Extend artwork past the trim", "3 mm (0.125 in)", "bleed trim edge crop", "Background colour and images must reach the bleed edge."],
    ["safe-zone", "Safe zone", "Keep text and logos inside the trim by", "3-5 mm (0.125-0.25 in)", "safe margin trim cut", "Cutting moves up to about 1 mm."],
    ["image-res", "Image resolution", "Effective ppi of a placed raster at its final size", "300 ppi for print up to A3; 150 or lower for large format viewed from a distance", "image resolution ppi dpi raster upscale", "Effective ppi = pixels / placed inches. Upscaling does not add detail."],
    ["fonts", "Fonts", "Embed or outline every font", "All fonts embedded in the PDF", "font embed outline pdf", "A missing font is substituted silently."],
    ["pdf-x", "Delivery format", "Press-ready PDF", "PDF/X-1a or PDF/X-4", "pdf x1a x4 delivery press", "Ask the printer which one; X-4 keeps transparency."],
    ["spot", "Spot colours", "Name spot colours exactly and use them on purpose", "Pantone or custom spots, named", "spot pantone varnish foil cut", "Varnish, foil and die lines each go on their own named spot layer."],
    ["overprint", "Overprint", "Overprint black text over colour; knock out everything else", "Overprint K text only", "overprint knockout trap", "Check with an overprint preview."],
    ["delta-e", "Colour difference", "How far a printed colour may drift from the proof", "Delta E 2000 under about 2-3 for brand colours, under 5 for general work", "delta e colour match proof brand", "Supply brand colours as Pantone or CMYK values, not RGB."],
    ["grey-neutral", "Neutral greys", "Build neutral greys from K alone", "K only", "grey gray neutral cast", "CMY greys drift to a colour cast."],
    ["profile", "ICC profile", "Embed or convert to the printer's profile", "Printer's profile, else FOGRA39/FOGRA51 (Europe) or GRACoL/SWOP (US)", "icc profile fogra gracol swop", "Do not guess; ask."],
]

SOCIAL = [
    ["ig-portrait", "Instagram", "Feed post, portrait", "1080 x 1350", "4:5", "instagram feed post portrait", "Largest feed footprint."],
    ["ig-square", "Instagram", "Feed post, square", "1080 x 1080", "1:1", "instagram feed post square", ""],
    ["ig-story", "Instagram", "Story or Reel", "1080 x 1920", "9:16", "instagram story reel vertical", "Keep key content out of the top and bottom ~250 px."],
    ["tt-video", "TikTok", "Video or cover", "1080 x 1920", "9:16", "tiktok video vertical cover", "Keep key content clear of the caption and button area."],
    ["yt-short", "YouTube", "Short", "1080 x 1920", "9:16", "youtube short vertical", ""],
    ["yt-thumb", "YouTube", "Video thumbnail", "1280 x 720", "16:9", "youtube thumbnail", "Under 2 MB; text must read at small size."],
    ["yt-banner", "YouTube", "Channel banner", "2560 x 1440", "16:9", "youtube banner channel art", "The safe area for all devices is about 1546 x 423 px at the centre."],
    ["fb-link", "Facebook", "Link or shared image", "1200 x 630", "1.91:1", "facebook link share post", ""],
    ["fb-cover", "Facebook", "Page cover", "820 x 312", "about 2.6:1", "facebook cover page", "Shows differently on mobile; keep the middle clear."],
    ["li-post", "LinkedIn", "Feed image", "1200 x 627", "1.91:1", "linkedin post feed", ""],
    ["li-banner", "LinkedIn", "Profile banner", "1584 x 396", "4:1", "linkedin banner profile cover", "The profile photo covers part of the lower left."],
    ["x-post", "X", "Post image", "1600 x 900", "16:9", "x twitter post image", ""],
    ["x-header", "X", "Profile header", "1500 x 500", "3:1", "x twitter header banner", ""],
    ["pin-pin", "Pinterest", "Pin", "1000 x 1500", "2:3", "pinterest pin vertical", ""],
    ["bsky-post", "Bluesky", "Post image", "1200 x 675", "16:9", "bluesky post image", "Images are re-encoded; keep files small."],
    ["og-image", "Any site", "Open Graph share image", "1200 x 630", "1.91:1", "open graph og share preview link", "Keep text in the central ~80%."],
    ["favicon", "Any site", "Favicon", "32 x 32, 180 x 180 (touch), 512 x 512 (PWA)", "1:1", "favicon icon app touch", "Provide an SVG as well; test at 16 px."],
    ["email-header", "Email", "Header image", "600 wide", "about 3:1", "email header newsletter", "Design at 1200 wide for high-density screens; always set alt text."],
]

IDENTITY = [
    ["mark-types", "Mark types", "Pick one: wordmark, lettermark, pictorial mark, abstract mark, combination mark, emblem, mascot", "Name which type it is and why", "logo wordmark lettermark pictorial abstract emblem mascot", "A combination mark needs the symbol and the wordmark to work alone too."],
    ["small-size", "Minimum size", "The mark must read at its smallest use", "Test at 16 px (screen) and 15 mm wide (print)", "logo small size favicon minimum legibility", "If it fails, make a simplified small-size version."],
    ["one-colour", "One-colour version", "Provide a single-colour version that works on light and on dark", "Render it in black and in white on a flat background", "logo one colour mono black white reversed", "Gradients and effects are not part of the mark."],
    ["clear-space", "Clear space", "Keep a margin around the mark free of other elements", "At least a defined unit (for example the height of the symbol's cap) on every side", "logo clear space margin exclusion", "Define the unit in the guidelines and show it."],
    ["scalable", "Scalable construction", "Build from simple filled shapes", "No raster images, no tiny gaps, no strokes thinner than 1/20 of the mark's height", "logo vector scalable construction stroke", "Outline strokes for the final file."],
    ["text-outlined", "Type in the mark", "Convert text to outlines in the delivered file", "No live text element in the final SVG or PDF", "logo font outline text convert", "Keep an editable source file."],
    ["distinct", "Distinctiveness", "Squint test and silhouette test", "Blur it or reduce it to a silhouette: is it still itself?", "logo distinct silhouette squint memorable", "Compare against five competitors before keeping it."],
    ["no-trend", "Longevity", "Avoid effects that date quickly", "No drop shadows, bevels or stock gradients", "logo trend timeless effect", "Effects belong to applications of the mark, not the mark."],
    ["lockups", "Lockups", "Provide horizontal, stacked and icon-only lockups", "Each has its own minimum size", "logo lockup horizontal stacked icon", "Name each variant in the file name."],
    ["contrast", "Contrast on backgrounds", "Mark and background should differ clearly", "Text-sized elements at least 4.5:1; large or graphic parts at least 3:1", "logo contrast background wcag accessibility", "Provide a version for each background in the palette."],
    ["file-set", "Delivery set", "Deliver SVG, PDF (vector) and PNG at 1x and 2x, in colour and one colour", "SVG optimised, PNG with a transparent background", "logo files deliver svg png pdf set", "Name files <brand>-<variant>-<colour>.<ext>."],
    ["palette", "Palette", "Define primary and secondary colours with values for screen and print", "HEX, RGB, CMYK and a Pantone reference for each", "brand palette colour hex cmyk pantone", "Print values come from a proof, not a formula, for brand colours."],
    ["typography", "Typography", "One display face, one text face, a fallback for each", "Licences cover the use (web, print, app)", "brand typography font licence fallback", "Check the licence before delivering a font to a client."],
    ["consistency", "Consistency", "Every piece uses the same palette, type scale and mark rules", "Compare each new piece with the brand's tokens", "brand consistency tokens guidelines review", "Brand gates belong to the author: propose changes, never write them."],
]

GRIDS = [
    ["poster-swiss", "Poster", "12-column grid, strong left alignment, wide left margin", "One dominant element (about 60% of the weight), one secondary, small details", "poster swiss grid typographic modernist", "Works with one type family in two or three sizes."],
    ["poster-centered", "Poster", "Centred axis with symmetrical margins", "Title, image, date and place read top to bottom", "poster centered symmetrical event concert", "Good for formal events; avoid centring long text."],
    ["poster-fullbleed", "Poster", "Full-bleed image with a text block on a calm area", "The image carries the mood; text sits where the image is quiet", "poster photo fullbleed overlay", "Check contrast of text on the image where the text sits, not on the average."],
    ["editorial-2col", "Editorial page", "Two columns, 5-8 mm gutter, 12-16 mm outer margin on A4", "Headline, standfirst, body, caption", "editorial magazine page columns gutter", "Body 9-11 pt on 12-14 pt leading; 45-75 characters per line."],
    ["editorial-modular", "Editorial spread", "Modular grid of 6 x 4 or 12 x 8 cells", "Image sizes come in whole numbers of modules", "editorial modular grid spread magazine", "Align baselines across columns."],
    ["book-single", "Book page", "Single text block; inner margin smaller than outer, bottom margin largest", "Running head, folio, text", "book page margins text block", "Pick the proportions once and reuse them."],
    ["social-carousel", "Carousel", "Same grid on every slide, the headline in the same place", "One idea per slide; the last slide asks for the action", "social carousel slides instagram linkedin", "Keep the edge clear; the next slide peeks in on some apps."],
    ["flyer-info", "Flyer", "Single column with a clear F or Z reading path", "What, when, where, how to act, in that order", "flyer info event leaflet", "Put the call to action where the eye ends."],
    ["slide-title", "Presentation slide", "8 or 12-column grid, 5% outer margin", "One message per slide as the title; support below", "slide deck presentation grid", "Body text no smaller than 18 pt when projected."],
    ["packaging-panel", "Packaging", "Panels from the dieline, each panel its own mini-layout", "The front panel carries brand and product; the back carries detail and legal", "packaging dieline panel box label", "Get the dieline from the manufacturer; never redraw it."],
    ["card-small", "Business card", "Left-aligned stack with 3-4 lines of information", "Name, role, contact", "business card small layout contact", "Do not go under 7 pt."],
    ["type-scale", "Type scale", "Ratio scale: 1.25 for text, 1.5 or more for display", "Three to five sizes in total", "type scale ratio hierarchy size", "Round to whole points."],
]

STYLES = [
    ["flat-vector", "Flat vector", "Solid shapes, limited palette, no gradients", "Icons, explainers, UI illustration", "flat vector shapes minimal explainer", "Easy to keep consistent across a set."],
    ["geometric", "Geometric", "Circles, triangles, grids; built from a construction", "Logos, patterns, posters", "geometric shapes grid construction pattern", "Show the construction in the brief."],
    ["line-art", "Line art", "Single stroke weight, no fill or sparse fill", "Editorial, icons, colouring pages", "line art stroke outline monoline", "Keep one stroke width and one corner style."],
    ["isometric", "Isometric", "30-degree axes, no perspective", "Diagrams, product illustration, game assets", "isometric diagram 3d game", "Use a fixed light direction."],
    ["risograph", "Risograph", "Two or three spot inks, overprint, grain", "Posters, zines, covers", "risograph riso grain overprint spot zine", "Overprint is the effect: set multiply, not opacity."],
    ["halftone", "Halftone", "Dots of varying size in one or two inks", "Retro, newspaper, pop art", "halftone dots retro pop print", "Pick the dot angle and frequency deliberately."],
    ["pixel", "Pixel art", "Fixed grid, limited palette, no anti-aliasing", "Games, retro, avatars", "pixel art sprite game retro", "Export at integer scale only; no smoothing."],
    ["painterly", "Painterly", "Visible brush marks, colour blending", "Covers, concept art, mood", "painterly brush concept art cover", "Raster work: go through an image provider or Krita."],
    ["collage", "Collage", "Cut-out photos and paper textures, uneven edges", "Editorial, music, zines", "collage cutout paper texture editorial", "Mind photo licences."],
    ["grain-gradient", "Grain gradient", "Soft colour fields with noise", "Backgrounds, covers, social posts", "grain gradient noise soft background", "Add noise at final size so it does not blur."],
    ["3d-render", "3D render", "Lit 3D objects, soft materials", "Product, hero images, icons", "3d render blender product lit hero", "A fixed camera and light rig repeats well."],
    ["type-only", "Type-only", "The lettering is the picture", "Posters, covers, social", "typography poster lettering type only", "One idea, one typeface, a large contrast in scale."],
]

TOOLS = [
    ["svg-author", "Write a logo, icon or pattern as SVG", "Claude-native", "Claude", "Write the SVG, check it with svg_lint.py, shrink it with svgo", "Nothing external", "Ready"],
    ["html-poster", "Poster or layout from HTML and CSS to PNG or PDF", "Claude-native", "Headless Chromium", "render.py", "Python playwright and Chromium", "Ready if installed"],
    ["raster-generate", "New raster image from a prompt", "Provider", "Higgsfield, Adobe Firefly, Canva generate-image, Figma generate_image", "The studio's still-image pipeline or the provider's tool", "Provider account", "Ready where connected"],
    ["bg-remove", "Remove a background", "Provider or local", "Adobe image_remove_background, Canva remove-background, rembg", "Provider tool or CLI", "Provider account or rembg", "Ready where connected"],
    ["vectorize", "Raster to vector", "Provider or local", "Adobe image_vectorize, vtracer, potrace", "Provider tool or CLI", "Provider account or the CLI", "Ready where connected"],
    ["upscale", "Upscale an image", "Provider or local", "Higgsfield upscale_image, Upscayl, Real-ESRGAN", "Provider tool or CLI", "Provider account or a GPU", "Gate by compute class"],
    ["batch-resize", "Resize or convert many files", "Local", "ImageMagick, vips", "CLI", "The tool installed", "Ready if installed"],
    ["svg-optimise", "Shrink an SVG", "Local", "svgo", "CLI", "Node", "Ready if installed"],
    ["font-subset", "Subset or inspect a font", "Local", "fonttools (pyftsubset)", "CLI", "Python package", "Ready if installed"],
    ["adobe-cloud", "Edit, resize or lay out through Adobe Express", "Provider", "Adobe for Creativity MCP and its adobe-* skills", "The provider's skills", "Adobe sign-in", "Ready where connected"],
    ["adobe-desktop", "Photoshop, Illustrator, InDesign or Premiere on the desktop", "Community MCP", "adb-mcp, adobe-mcp, illustrator-mcp-server", "Draft a setup; the author enables it", "The app and the server", "Unverified"],
    ["idml", "Round-trip a layout to InDesign", "Provider", "Adobe export_idml and convert_pdf_to_indd", "The provider's tools", "Adobe sign-in", "Ready where connected"],
    ["affinity", "Vector, raster and layout in Affinity", "Local MCP", "Affinity MCP execute_script and render_spread", "Direct", "Affinity installed and the server connected", "Ready where connected"],
    ["inkscape", "SVG cleanup, text to path, PDF or EPS export", "Local", "Inkscape command line", "CLI", "Inkscape installed", "Ready if installed"],
    ["gimp", "Raster batch edits", "Local", "GIMP 3 Script-Fu or a community MCP", "CLI", "GIMP installed", "Unverified for MCP"],
    ["krita", "Painting and brushes", "Local", "Krita and a community MCP", "Direct", "Krita installed", "Unverified"],
    ["penpot", "Open-source interface and graphic design", "MCP", "Penpot MCP", "Direct", "A Penpot account or install", "Unverified"],
    ["figma", "Design files and diagrams in Figma", "MCP", "Figma MCP", "The figma skills", "Figma sign-in", "Ready where connected"],
    ["canva", "Design from templates, resize, brand check", "MCP", "Canva MCP and its skills", "The canva skills", "Canva sign-in", "Ready where connected"],
    ["scribus", "Print-ready desktop publishing, PDF/X", "Local", "Scribus Python scripter, headless", "CLI", "Scribus installed", "Ready if installed"],
    ["blender-3d", "3D render for a hero image", "Local MCP", "Blender MCP", "The blender plugin", "Blender running", "Ready where connected"],
    ["lottie", "Light web motion", "Local", "Lottie JSON or Rive", "Author in code or an editor", "Nothing", "Ready"],
    ["print-check", "Check a layout before it goes to print", "Local", "preflight.py in this plugin", "Skill print-preflight", "A JSON description of the file", "Ready"],
]

if __name__ == "__main__":
    write("print-specs.csv", ["ID", "Name", "Trim", "Bleed", "Safe margin", "Resolution", "Colour", "Keywords", "Notes"], PRINT)
    write("color-print.csv", ["ID", "Topic", "Rule", "Value", "Keywords", "Notes"], COLOR)
    write("social-sizes.csv", ["ID", "Platform", "Placement", "Size px", "Ratio", "Keywords", "Notes"], SOCIAL)
    write("identity-rules.csv", ["ID", "Topic", "Rule", "Check", "Keywords", "Notes"], IDENTITY)
    write("grids.csv", ["ID", "Format", "Grid", "Hierarchy", "Keywords", "Notes"], GRIDS)
    write("illustration-styles.csv", ["ID", "Style", "Traits", "Good for", "Keywords", "Notes"], STYLES)
    write("tools.csv", ["ID", "Job", "Route", "Provider", "How", "Needs", "Status"], TOOLS)
    print("wrote", len(list(DATA.glob("*.csv"))), "files")
