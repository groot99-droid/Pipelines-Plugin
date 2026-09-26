#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sRGB hex -> OKLCH conversion.

shadcn/ui v4 and tweakcn express theme variables in `oklch(L C H)`, so emitting
a shadcn theme from hex palettes needs this conversion. Pure stdlib math, per
Bjorn Ottosson's Oklab definition (https://bottosson.github.io/posts/oklab/),
to keep the project's zero-dependency contract.

Pipeline: sRGB -> linear sRGB -> LMS -> cube root -> Oklab -> polar (OKLCH).
"""

import math

# Linear sRGB -> LMS
_LMS_FROM_LRGB = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)

# LMS' (cube-rooted) -> Oklab
_LAB_FROM_LMS = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)


def hex_to_rgb(hex_color: str):
    """#RRGGBB or #RGB -> (r, g, b) floats in 0..1, or None if unparseable."""
    if not hex_color:
        return None
    value = str(hex_color).strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        return None
    try:
        return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None


def _to_linear(channel: float) -> float:
    """Undo the sRGB transfer function."""
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def hex_to_oklch(hex_color: str):
    """#RRGGBB -> (L, C, H) with L in 0..1, C >= 0, H in degrees 0..360.

    Returns None if the input is not a parseable hex color.
    """
    rgb = hex_to_rgb(hex_color)
    if rgb is None:
        return None

    linear = [_to_linear(c) for c in rgb]

    lms = [sum(row[i] * linear[i] for i in range(3)) for row in _LMS_FROM_LRGB]
    # Cube root, sign-preserving: tiny negative values can appear from rounding.
    lms_prime = [math.copysign(abs(v) ** (1 / 3), v) for v in lms]

    lightness, a, b = [
        sum(row[i] * lms_prime[i] for i in range(3)) for row in _LAB_FROM_LMS
    ]

    chroma = math.hypot(a, b)
    hue = math.degrees(math.atan2(b, a))
    if hue < 0:
        hue += 360.0
    # An achromatic color has no meaningful hue; report 0 rather than the
    # arbitrary angle that floating-point noise in a/b would produce.
    if chroma < 1e-6:
        hue = 0.0
    return lightness, chroma, hue


def format_oklch(hex_color: str, precision: int = 4):
    """#RRGGBB -> the CSS string `oklch(L C H)`, or None if unparseable."""
    result = hex_to_oklch(hex_color)
    if result is None:
        return None
    lightness, chroma, hue = result
    return (
        f"oklch({round(lightness, precision):g} "
        f"{round(chroma, precision):g} "
        f"{round(hue, precision):g})"
    )


# ---------------------------------------------------------------------------
# Inverse: Oklab/OKLCH -> sRGB hex.
#
# getComputedStyle() in current Chrome returns oklab() and lab() for any color
# authored in a modern color space -- on tailwindcss.com only 1 of 13 distinct
# background colors came back as rgb(). Harvesting computed styles without
# these is not a partial result, it is a near-empty one.
#
# Constants are Ottosson's published inverse matrices; correctness is pinned by
# round-tripping against hex_to_oklch() in the tests rather than trusted.
# ---------------------------------------------------------------------------

# Oklab -> LMS' (cube-rooted LMS)
_LMS_FROM_LAB = (
    (1.0, 0.3963377774, 0.2158037573),
    (1.0, -0.1055613458, -0.0638541728),
    (1.0, -0.0894841775, -1.2914855480),
)

# LMS -> linear sRGB
_LRGB_FROM_LMS = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _to_srgb(channel: float) -> float:
    """Apply the sRGB transfer function."""
    if channel <= 0.0031308:
        return 12.92 * channel
    return 1.055 * (abs(channel) ** (1 / 2.4)) - 0.055


def oklab_to_hex(lightness: float, a: float, b: float):
    """Oklab -> #RRGGBB, clamped into gamut.

    Out-of-gamut values are clamped per channel. That is not a real gamut
    mapping -- it can shift hue on saturated colors -- so `clipped` is reported
    alongside, letting a caller drop those rather than record a wrong hex.
    Returns (hex, clipped).
    """
    lab = (lightness, a, b)
    lms_prime = [sum(row[i] * lab[i] for i in range(3)) for row in _LMS_FROM_LAB]
    lms = [v ** 3 for v in lms_prime]
    linear = [sum(row[i] * lms[i] for i in range(3)) for row in _LRGB_FROM_LMS]

    clipped = any(c < -1e-4 or c > 1 + 1e-4 for c in linear)
    channels = []
    for value in linear:
        srgb = _to_srgb(max(0.0, min(1.0, value)))
        channels.append(max(0, min(255, round(srgb * 255))))
    return "#" + "".join(f"{c:02X}" for c in channels), clipped


def oklch_to_hex(lightness: float, chroma: float, hue_degrees: float):
    """OKLCH -> (#RRGGBB, clipped)."""
    radians = math.radians(hue_degrees)
    return oklab_to_hex(lightness, chroma * math.cos(radians),
                        chroma * math.sin(radians))
