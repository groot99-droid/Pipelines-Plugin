#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DTCG token exporter - turns a generated design system into a W3C Design Tokens
Community Group formatted token file.

    from design_system import generate_design_system
    from tokens import to_dtcg, dumps_dtcg

    result = generate_design_system("SaaS dashboard", "My Project")
    print(dumps_dtcg(result["design_system"]))

Output is consumable by Style Dictionary, Tokens Studio, Supernova, Penpot,
Zeroheight and other DTCG-aware tooling.

SPEC NOTE - value shapes
------------------------
The DTCG draft has been migrating `color` toward an object form
({colorSpace, components, alpha, hex}) and `dimension` toward
({value, unit}). Tooling has not caught up: the string forms ("#2563EB",
"16px") are what shipping importers actually read today. This exporter emits
the string forms and records that choice in
`$extensions["cc.uupm"].valueEncoding`, so an object-form emitter can be added
later without ambiguity about what an existing file contains.
"""

import json
import re

from contrast import evaluate_palette
from design_system import DIAL_TIERS, SEMANTIC_COLOR_ENTRIES

EXTENSION_KEY = "cc.uupm"
VALUE_ENCODING = "string-legacy"

# Radius and shadow are not yet data-driven - these mirror the values
# format_master_md() writes, so a DTCG export and a MASTER.md agree.
RADIUS_SCALE = (
    ("sm", "4px", "Inputs, small chips"),
    ("md", "8px", "Buttons, cards"),
    ("lg", "12px", "Panels, modals"),
    ("xl", "16px", "Hero surfaces"),
    ("full", "9999px", "Pills, avatars"),
)

SHADOW_SCALE = (
    ("sm", "0 1px 2px rgba(0,0,0,0.05)", "Subtle lift"),
    ("md", "0 4px 6px rgba(0,0,0,0.1)", "Cards, buttons"),
    ("lg", "0 10px 15px rgba(0,0,0,0.1)", "Modals, dropdowns"),
    ("xl", "0 20px 25px rgba(0,0,0,0.15)", "Hero images, featured cards"),
)

SPACING_USAGE = {
    "xs": "Tight gaps",
    "sm": "Icon gaps, inline spacing",
    "md": "Standard padding",
    "lg": "Section padding",
    "xl": "Large gaps",
    "2xl": "Section margins",
    "3xl": "Hero padding",
}

# GSAP easing names carry no cubic-bezier definition, so motion.csv rows cannot
# be emitted as DTCG cubicBezier tokens without a mapping. These are the
# standard approximations; anything unmapped is emitted as a plain string token
# rather than being silently wrong.
GSAP_TO_CUBIC_BEZIER = {
    "none": [0.0, 0.0, 1.0, 1.0],
    "linear": [0.0, 0.0, 1.0, 1.0],
    "power1.out": [0.25, 0.46, 0.45, 0.94],
    "power1.in": [0.55, 0.085, 0.68, 0.53],
    "power1.inOut": [0.455, 0.03, 0.515, 0.955],
    "power2.out": [0.215, 0.61, 0.355, 1.0],
    "power2.in": [0.55, 0.055, 0.675, 0.19],
    "power2.inOut": [0.645, 0.045, 0.355, 1.0],
    "power3.out": [0.165, 0.84, 0.44, 1.0],
    "power3.in": [0.895, 0.03, 0.685, 0.22],
    "power3.inOut": [0.77, 0.0, 0.175, 1.0],
    "power4.out": [0.23, 1.0, 0.32, 1.0],
    "expo.out": [0.19, 1.0, 0.22, 1.0],
    "expo.in": [0.95, 0.05, 0.795, 0.035],
    "expo.inOut": [1.0, 0.0, 0.0, 1.0],
    "sine.out": [0.39, 0.575, 0.565, 1.0],
    "sine.in": [0.47, 0.0, 0.745, 0.715],
    "sine.inOut": [0.445, 0.05, 0.55, 0.95],
    "circ.out": [0.075, 0.82, 0.165, 1.0],
    "back.out(1.4)": [0.175, 0.885, 0.32, 1.275],
}


def _token_name(css_var: str) -> str:
    """`--color-on-primary` -> `on-primary`."""
    return css_var.replace("--color-", "", 1)


def _px_to_rem(px_value: str):
    match = re.match(r"^(-?\d+(?:\.\d+)?)px$", str(px_value).strip())
    if not match:
        return None
    return f"{float(match.group(1)) / 16:g}rem"


def _first_duration_ms(duration: str):
    """'150-200ms' -> '150ms'. Returns None for scrub-driven rows.

    motion.csv states durations as ranges. The lower bound is the token value:
    a design token is a single number, and the fast end of a range is the safer
    default to ship.
    """
    text = str(duration or "")
    # Range form first - a bare `\d+ms` search would otherwise match the upper
    # bound in "300-450ms", since that is the number the unit is attached to.
    match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*\d+(?:\.\d+)?\s*ms", text)
    if match:
        return f"{float(match.group(1)):g}ms"
    match = re.search(r"(\d+(?:\.\d+)?)\s*ms", text)
    if match:
        return f"{float(match.group(1)):g}ms"
    match = re.search(r"(\d+(?:\.\d+)?)\s*s\b", text)
    if match:
        return f"{float(match.group(1)) * 1000:g}ms"
    return None


def _color_tokens(colors: dict) -> dict:
    """Semantic color tokens, keyed off the same table MASTER.md renders."""
    group = {}
    for label, key, css_var in SEMANTIC_COLOR_ENTRIES:
        hex_value = (colors.get(key) or "").strip()
        if not hex_value:
            continue
        group[_token_name(css_var)] = {
            "$type": "color",
            "$value": hex_value,
            "$description": label,
        }
    return group


def _contrast_report(colors: dict) -> list:
    """WCAG 2.2 ratios for every applicable pair, as $extensions metadata.

    Delegates to contrast.py so the token file and the --strict-contrast gate
    can never disagree about what passes.
    """
    return evaluate_palette(colors)


def _font_tokens(typography: dict) -> dict:
    group = {}
    heading = (typography.get("heading") or "").strip()
    body = (typography.get("body") or "").strip()
    if heading:
        group["heading"] = {
            "$type": "fontFamily",
            "$value": [heading, "sans-serif"],
            "$description": "Heading typeface",
        }
    if body:
        group["body"] = {
            "$type": "fontFamily",
            "$value": [body, "sans-serif"],
            "$description": "Body typeface",
        }
    return group


def _space_tokens(spacing_scale: dict) -> dict:
    scale = spacing_scale or DIAL_TIERS["density"][1][2]["spacing"]
    group = {}
    for token in ("xs", "sm", "md", "lg", "xl", "2xl", "3xl"):
        px_value = scale.get(token)
        if not px_value:
            continue
        entry = {
            "$type": "dimension",
            "$value": px_value,
            "$description": SPACING_USAGE.get(token, ""),
        }
        rem_value = _px_to_rem(px_value)
        if rem_value:
            entry["$extensions"] = {EXTENSION_KEY: {"rem": rem_value}}
        group[token] = entry
    return group


def _radius_tokens() -> dict:
    return {
        name: {"$type": "dimension", "$value": value, "$description": usage}
        for name, value, usage in RADIUS_SCALE
    }


def _shadow_tokens() -> dict:
    # Emitted as strings rather than DTCG composite `shadow` objects: the source
    # values are CSS shadow shorthand, and splitting them into
    # {offsetX, offsetY, blur, spread, color} would be guesswork on the rgba()
    # alpha handling that importers disagree about anyway.
    return {
        name: {
            "$type": "shadow",
            "$value": value,
            "$description": usage,
            "$extensions": {EXTENSION_KEY: {"encoding": "css-shorthand"}},
        }
        for name, value, usage in SHADOW_SCALE
    }


_SPRING_RE = re.compile(
    r"stiffness:\s*(\d+(?:\.\d+)?).*?damping:\s*(\d+(?:\.\d+)?).*?mass:\s*(\d+(?:\.\d+)?)",
    re.I | re.S,
)


def _spring_params(raw: str):
    """Parse 'stiffness: 280, damping: 18, mass: 1 (...)' into a dict.

    Rows that are not spring-shaped say so in prose ("n/a - scrub-driven",
    "n/a - continuous loop") and yield None, so nothing is emitted for them.
    """
    match = _SPRING_RE.search(str(raw or ""))
    if not match:
        return None
    stiffness, damping, mass = (float(g) for g in match.groups())
    return {"stiffness": stiffness, "damping": damping, "mass": mass}


def _motion_tokens(motion_snippet: dict) -> dict:
    if not motion_snippet:
        return {}
    group = {}

    # DTCG has no spring type. Emitted under $extensions rather than forced
    # into a cubicBezier, which would be a different curve, not a conversion.
    spring = _spring_params(motion_snippet.get("Spring Params"))
    if spring:
        group["spring"] = {
            "default": {
                "$type": "number",
                "$value": spring["stiffness"],
                "$description": (
                    "Spring stiffness. Full model (stiffness/damping/mass) is "
                    "under $extensions - DTCG has no spring token type."
                ),
                "$extensions": {EXTENSION_KEY: {"spring": spring}},
            }
        }

    duration = _first_duration_ms(motion_snippet.get("Duration"))
    if duration:
        group["duration"] = {
            "default": {
                "$type": "duration",
                "$value": duration,
                "$description": motion_snippet.get("Category", "Motion duration"),
            }
        }

    # The reduced-motion fallback is guidance, not a value, so it rides in
    # $extensions. Dropping it would ship a motion token with no opt-out.
    reduced = (motion_snippet.get("Reduced Motion") or "").strip()
    if reduced:
        group["reducedMotion"] = {
            "default": {
                "$type": "string",
                "$value": reduced,
                "$description": "prefers-reduced-motion fallback for this preset",
            }
        }

    easing = (motion_snippet.get("Easing") or "").strip()
    if easing:
        bezier = GSAP_TO_CUBIC_BEZIER.get(easing)
        if bezier:
            group["easing"] = {
                "default": {
                    "$type": "cubicBezier",
                    "$value": bezier,
                    "$description": f"Approximation of GSAP `{easing}`",
                    "$extensions": {EXTENSION_KEY: {"gsapEase": easing}},
                }
            }
        else:
            # No mapping - emit the GSAP name rather than a cubicBezier token
            # that would be a fabrication.
            group["easing"] = {
                "default": {
                    "$type": "string",
                    "$value": easing,
                    "$description": f"GSAP ease `{easing}`; no cubic-bezier equivalent mapped",
                    "$extensions": {
                        EXTENSION_KEY: {"gsapEase": easing, "unmapped": True}
                    },
                }
            }
    return group


def to_dtcg(design_system: dict) -> dict:
    """Build a DTCG token tree from a generate_design_system() result dict."""
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    style = design_system.get("style", {})

    document = {
        "$description": (
            f"Design tokens for {design_system.get('project_name', 'PROJECT')}"
            f" - generated by UI UX Pro Max"
        ),
    }

    color_group = _color_tokens(colors)
    if color_group:
        document["color"] = color_group

    font_group = _font_tokens(typography)
    if font_group:
        document["font"] = {"family": font_group}

    document["space"] = _space_tokens(design_system.get("spacing_scale"))
    document["radius"] = _radius_tokens()
    document["shadow"] = _shadow_tokens()

    motion_group = _motion_tokens(design_system.get("motion_snippet"))
    if motion_group:
        document["motion"] = motion_group

    document["$extensions"] = {
        EXTENSION_KEY: {
            "valueEncoding": VALUE_ENCODING,
            "category": design_system.get("category"),
            "style": style.get("name"),
            "styleId": style.get("id"),
            "pattern": design_system.get("pattern", {}).get("name"),
            "dials": design_system.get("dials", {}),
            "sourceIdentities": design_system.get("source_identities", {}),
            "contrast": _contrast_report(colors),
            "antiPatterns": design_system.get("anti_patterns", ""),
        }
    }
    return document


def dumps_dtcg(design_system: dict, indent: int = 2) -> str:
    return json.dumps(to_dtcg(design_system), indent=indent, ensure_ascii=False)
