"""Platform registry. Modules are imported lazily so `ve publish plan` never needs a platform's dependencies."""
from __future__ import annotations

import importlib

from videoeditor.publish.base import Publisher

NAMES = ("youtube", "bluesky", "mastodon", "linkedin", "tiktok", "instagram", "x")
_CLASSES = {n: f"videoeditor.publish.platforms.{n}" for n in NAMES}


def get(name: str) -> Publisher:
    if name not in _CLASSES:
        raise SystemExit(f"unknown platform '{name}' (choose from {', '.join(NAMES)})")
    return importlib.import_module(_CLASSES[name]).PUBLISHER()
