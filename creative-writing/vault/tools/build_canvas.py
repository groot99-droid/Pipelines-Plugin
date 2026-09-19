#!/usr/bin/env python3
"""Regenerate Vault_Overview.canvas from each work file's frontmatter.

Stdlib only. Re-run any time frontmatter changes:
    python tools/build_canvas.py

Two-level grouping: one outer group per style-`mode`, and inside it one
sub-group per frontmatter `type` (novel, poem, essay, ...) so heterogeneous
groups -- `unclassified` especially, which spans 9 different types -- get
real internal structure instead of a flat, unsorted grid.

Also draws an edge between any two-or-more files that share a non-empty
frontmatter `project:` value.
"""
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault_search import iter_source_files, split_frontmatter  # noqa: E402

VAULT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = VAULT_ROOT / "Vault_Overview.canvas"

MODE_ORDER = ["horror-prose", "epic-fantasy", "essay-self-help", "confessional-poetry", "unclassified"]
MODE_LABELS = {
    "horror-prose": "Horror-Prose Mode",
    "epic-fantasy": "Epic-Fantasy Mode",
    "essay-self-help": "Essay / Self-Help Mode",
    "confessional-poetry": "Confessional-Poetry Mode",
    "unclassified": "Unclassified / Mixed",
}

# Every group (mode-level and type-subgroup) gets its own individually-generated
# hex color rather than sharing a handful of presets. Colors are handed out in
# creation order using golden-angle hue stepping, which keeps consecutive
# colors well separated even as the number of groups grows or shrinks.
GOLDEN_ANGLE = 137.50776405
_color_counter = {"i": 0}


def next_color(saturation=55, lightness=60):
    hue = (_color_counter["i"] * GOLDEN_ANGLE) % 360
    _color_counter["i"] += 1
    return hsl_to_hex(hue, saturation, lightness)


def hsl_to_hex(h, s, l):
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    r, g, b = (round((v + m) * 255) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

TYPE_LABELS = {
    "book": "Book", "novel": "Novel", "story": "Story", "book-concept": "Book Concept",
    "worldbuilding": "Worldbuilding", "song": "Song", "poem": "Poem", "prose-poem": "Prose Poem",
    "letter": "Letter", "dream-journal": "Dream Journal", "character-profile": "Character Profile",
    "essay": "Essay",
}

NODE_W, NODE_H = 340, 100
NODE_PAD = 16
SUBGROUP_HEADER = 44
SUBGROUP_PAD = 16
SUBGROUP_GAP = 36
MODE_HEADER = 70
MODE_PAD = 30
MODE_MAX_CONTENT_WIDTH = 1900
MODE_GAP_Y = 220
MIN_MODE_WIDTH = 700


def sanitize(s):
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")


def node_id(rel_path):
    return "n_" + sanitize(rel_path)


def mode_group_id(mode):
    return "grp_" + sanitize(mode)


def subgroup_id(mode, typ):
    return "sgrp_" + sanitize(mode) + "_" + sanitize(typ)


def collect_files():
    """mode -> type -> [(rel, title)], plus project -> [rel, ...]"""
    by_mode = {}
    projects = {}
    for path, source_type in iter_source_files(VAULT_ROOT, include_annotations=False):
        if source_type != "work":
            continue
        text = path.read_text(encoding="utf-8")
        fm, _ = split_frontmatter(text)
        rel = path.relative_to(VAULT_ROOT).as_posix()
        mode = fm.get("mode") or "unclassified"
        typ = fm.get("type") or "unknown"
        by_mode.setdefault(mode, {}).setdefault(typ, []).append((rel, fm.get("title") or path.stem))
        if mode not in MODE_ORDER:
            MODE_ORDER.append(mode)
            MODE_LABELS.setdefault(mode, mode.replace("-", " ").title())
            MODE_COLORS.setdefault(mode, "6")
        project = fm.get("project")
        if project:
            projects.setdefault(project, []).append(rel)
    return by_mode, projects


def layout_subgroup(mode, typ, files, origin_x, origin_y):
    """Return (subgroup_node, file_nodes, width, height)."""
    n = len(files)
    cols = max(1, min(4, math.ceil(math.sqrt(n))))
    rows = math.ceil(n / cols)
    width = SUBGROUP_PAD * 2 + cols * NODE_W + (cols - 1) * NODE_PAD
    height = SUBGROUP_HEADER + SUBGROUP_PAD + rows * NODE_H + (rows - 1) * NODE_PAD + SUBGROUP_PAD

    label = f"{TYPE_LABELS.get(typ, typ.replace('-', ' ').title())} ({n})"
    sg_node = {
        "id": subgroup_id(mode, typ), "type": "group",
        "x": origin_x, "y": origin_y, "width": width, "height": height,
        "label": label, "color": next_color(saturation=45, lightness=68),
    }

    file_nodes = []
    for i, (rel, title) in enumerate(sorted(files, key=lambda t: t[1].lower())):
        col, row = i % cols, i // cols
        fx = origin_x + SUBGROUP_PAD + col * (NODE_W + NODE_PAD)
        fy = origin_y + SUBGROUP_HEADER + row * (NODE_H + NODE_PAD)
        file_nodes.append({
            "id": node_id(rel), "type": "file", "file": rel,
            "x": fx, "y": fy, "width": NODE_W, "height": NODE_H,
        })
    return sg_node, file_nodes, width, height


def layout_mode(mode, by_type, origin_y):
    """Shelf-pack this mode's type-subgroups; return (nodes, mode_height)."""
    nodes = []
    type_order = sorted(by_type.keys(), key=lambda t: (-len(by_type[t]), t))

    cursor_x, cursor_y = MODE_PAD, MODE_HEADER
    row_max_h = 0
    content_width = MIN_MODE_WIDTH

    for typ in type_order:
        files = by_type[typ]
        # Pre-measure without placing, to decide wrap, then place at final origin.
        n = len(files)
        cols = max(1, min(4, math.ceil(math.sqrt(n))))
        est_width = SUBGROUP_PAD * 2 + cols * NODE_W + (cols - 1) * NODE_PAD

        if cursor_x > MODE_PAD and cursor_x + est_width > MODE_PAD + MODE_MAX_CONTENT_WIDTH:
            cursor_y += row_max_h + SUBGROUP_GAP
            cursor_x = MODE_PAD
            row_max_h = 0

        sg_node, file_nodes, width, height = layout_subgroup(mode, typ, files, cursor_x, origin_y + cursor_y)
        nodes.append(sg_node)
        nodes.extend(file_nodes)

        cursor_x += width + SUBGROUP_GAP
        row_max_h = max(row_max_h, height)
        content_width = max(content_width, cursor_x - SUBGROUP_GAP + MODE_PAD)

    mode_height = cursor_y + row_max_h + MODE_PAD
    mode_node = {
        "id": mode_group_id(mode), "type": "group",
        "x": 0, "y": origin_y, "width": content_width, "height": mode_height,
        "label": MODE_LABELS.get(mode, mode), "color": next_color(saturation=65, lightness=50),
    }
    return [mode_node] + nodes, mode_height


def build_canvas():
    by_mode, projects = collect_files()
    nodes = []
    edges = []

    cursor_y = 0
    for mode in MODE_ORDER:
        by_type = by_mode.get(mode)
        if not by_type:
            continue
        mode_nodes, mode_height = layout_mode(mode, by_type, cursor_y)
        nodes.extend(mode_nodes)
        cursor_y += mode_height + MODE_GAP_Y

    edge_i = 0
    for project, files in projects.items():
        files = sorted(set(files))
        for a, b in zip(files, files[1:]):
            edge_i += 1
            edges.append({
                "id": f"e_{edge_i}", "fromNode": node_id(a), "toNode": node_id(b),
                "label": project,
            })

    return {"nodes": nodes, "edges": edges}


def main():
    canvas = build_canvas()
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(canvas, f, indent=2)
    n_files = sum(1 for n in canvas["nodes"] if n["type"] == "file")
    n_mode_groups = sum(1 for n in canvas["nodes"] if n["type"] == "group" and n["id"].startswith("grp_"))
    n_subgroups = sum(1 for n in canvas["nodes"] if n["type"] == "group" and n["id"].startswith("sgrp_"))
    print(f"Wrote {OUT_PATH}: {n_files} file nodes, {n_mode_groups} mode groups, "
          f"{n_subgroups} type sub-groups, {len(canvas['edges'])} edges.")


if __name__ == "__main__":
    main()
