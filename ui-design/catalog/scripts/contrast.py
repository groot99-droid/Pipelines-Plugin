#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WCAG 2.2 contrast evaluation for generated palettes.

The design system generator picks a palette from colors.csv and hands it on.
Nothing previously checked whether the foreground/background pairs it emitted
actually met a contrast minimum -- the pre-delivery checklist said "4.5:1
minimum" but no code enforced it. This module is that check.

    from contrast import evaluate_palette, failures

    report = evaluate_palette(design_system["colors"])
    if failures(report):
        ...  # a pair fell short

Two thresholds, per WCAG 2.2:
  * 4.5:1 for normal-size text (1.4.3 Contrast (Minimum))
  * 3.0:1 for UI component boundaries and focus indicators
    (1.4.11 Non-text Contrast) -- borders and focus rings are not text

Text pairs are *enforceable*: a palette that fails one is wrong, full stop.
Non-text pairs are *advisory*, because 1.4.11 only applies when the boundary is
the sole means of identifying a component -- which this generator cannot know.
An audit of all 192 palettes in colors.csv bears that distinction out: every
text pair passes in every palette, while border-on-background falls under 3:1
in 173 of them, because a deliberately subtle border is a normal design choice
and not in itself a defect. Gating on it would fail 90% of the catalog and
train everyone to pass --no-strict-contrast.

Note: validate_data.py carries its own luminance helper. That one *raises* on
malformed input because it is a strict CSV validator; these return None so a
single bad cell cannot crash generation. The duplication is deliberate.
"""

TEXT_MINIMUM = 4.5
NON_TEXT_MINIMUM = 3.0

# (pair name, foreground key, background key, minimum, label, advisory)
CONTRAST_PAIRS = (
    ("foreground-on-background", "foreground", "background", TEXT_MINIMUM, "Body text", False),
    ("on-primary-on-primary", "on_primary", "primary", TEXT_MINIMUM, "Text on primary", False),
    ("on-secondary-on-secondary", "on_secondary", "secondary", TEXT_MINIMUM, "Text on secondary", False),
    ("on-accent-on-accent", "on_accent", "accent", TEXT_MINIMUM, "Text on accent/CTA", False),
    ("on-destructive-on-destructive", "on_destructive", "destructive", TEXT_MINIMUM, "Text on destructive", False),
    ("card-foreground-on-card", "card_foreground", "card", TEXT_MINIMUM, "Text on card", False),
    ("muted-foreground-on-muted", "muted_foreground", "muted", TEXT_MINIMUM, "Muted text", False),
    # Non-text: component boundaries, not labels. Advisory - see module docstring.
    ("border-on-background", "border", "background", NON_TEXT_MINIMUM, "Border against background", True),
    ("ring-on-background", "ring", "background", NON_TEXT_MINIMUM, "Focus ring against background", True),
)


def relative_luminance(hex_color: str):
    """WCAG relative luminance of a #RRGGBB string, or None if unparseable."""
    if not hex_color:
        return None
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        return None
    try:
        channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    except ValueError:
        return None
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str):
    """WCAG contrast ratio for two hex colors, or None if either is invalid."""
    first_luminance = relative_luminance(first)
    second_luminance = relative_luminance(second)
    if first_luminance is None or second_luminance is None:
        return None
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def evaluate_palette(colors: dict) -> list:
    """Evaluate every applicable pair in a design system `colors` dict.

    Pairs whose colors are absent or unparseable are skipped rather than
    reported as failures: a palette that simply does not define `destructive`
    has not failed a contrast check, it just has nothing to check.
    """
    report = []
    colors = colors or {}
    for name, fg_key, bg_key, minimum, label, advisory in CONTRAST_PAIRS:
        foreground = (colors.get(fg_key) or "").strip()
        background = (colors.get(bg_key) or "").strip()
        if not foreground or not background:
            continue
        ratio = contrast_ratio(foreground, background)
        if ratio is None:
            continue
        report.append({
            "pair": name,
            "label": label,
            "foreground": foreground,
            "background": background,
            "ratio": round(ratio, 2),
            "wcag22Minimum": minimum,
            "nonText": minimum == NON_TEXT_MINIMUM,
            "advisory": advisory,
            "passes": ratio >= minimum,
        })
    return report


def failures(report: list) -> list:
    """Enforceable failures: text pairs below their minimum.

    Advisory (non-text) shortfalls are excluded -- use advisories() for those.
    This is what a --strict-contrast gate should act on.
    """
    return [entry for entry in report or []
            if not entry["passes"] and not entry["advisory"]]


def advisories(report: list) -> list:
    """Non-text pairs below their minimum. Worth surfacing, not worth failing on."""
    return [entry for entry in report or []
            if not entry["passes"] and entry["advisory"]]


def format_report(report: list, indent: str = "") -> str:
    """Human-readable lines for a contrast report. Empty string if nothing checked."""
    if not report:
        return ""
    lines = []
    for entry in report:
        mark = "PASS" if entry["passes"] else ("WARN" if entry["advisory"] else "FAIL")
        scope = "non-text" if entry["nonText"] else "text"
        lines.append(
            f"{indent}[{mark}] {entry['label']}: {entry['foreground']} on "
            f"{entry['background']} = {entry['ratio']}:1 "
            f"(needs {entry['wcag22Minimum']}:1, {scope})"
        )
    return "\n".join(lines)
