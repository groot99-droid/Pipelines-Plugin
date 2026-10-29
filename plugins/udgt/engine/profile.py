"""A game profile: what UDGT reads in one game's repo, and how.

The profile is a JSON file kept in the teardown folder, beside the teardown it produces. Its
keys are described in profiles/schema.json; this module checks the parts the engine depends on,
compiles the patterns, and resolves the game checkout.
"""

import json
import os
import re
from pathlib import Path

REQUIRED = ("udgt", "name", "slug", "docs", "stages")
SCHEMA_VERSION = 1


class ProfileError(Exception):
    """A profile the engine cannot use."""


def load(path):
    path = Path(path)
    if not path.is_file():
        raise ProfileError(f"no profile at {path}")
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as err:
        raise ProfileError(f"{path}: not JSON ({err})") from None
    missing = [k for k in REQUIRED if k not in profile]
    if missing:
        raise ProfileError(f"{path}: missing {', '.join(missing)}")
    if profile["udgt"] != SCHEMA_VERSION:
        raise ProfileError(f"{path}: profile version {profile['udgt']}, engine expects {SCHEMA_VERSION}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", profile["slug"]):
        raise ProfileError(f"{path}: slug must be lowercase letters, digits and dashes")
    for ref in profile.get("refs", []):
        try:
            ref["rx"] = re.compile(ref["pattern"])
        except (KeyError, re.error) as err:
            raise ProfileError(f"{path}: ref {ref.get('id')}: {err}") from None
        if "target" not in ref or "id" not in ref:
            raise ProfileError(f"{path}: every ref needs an id and a target")
    stage_ids = [s["id"] for s in profile["stages"]]
    if len(set(stage_ids)) != len(stage_ids):
        raise ProfileError(f"{path}: stage ids repeat")
    for stage in profile["stages"]:
        for key in ("id", "slug", "title", "areas", "prompts"):
            if key not in stage:
                raise ProfileError(f"{path}: stage {stage.get('id')} has no {key}")
    profile["_home"] = path.parent.resolve()
    profile["_path"] = path.resolve()
    return profile


def game_root(profile, given=None):
    """The game checkout: --game, then UDGT_GAME, then the profile's `game.path` (relative to it)."""
    candidates = []
    if given:
        candidates.append(Path(given))
    if os.environ.get("UDGT_GAME"):
        candidates.append(Path(os.environ["UDGT_GAME"]))
    for p in profile.get("game", {}).get("paths", []):
        candidates.append((profile["_home"] / p))
    for c in candidates:
        if c.is_dir():
            return c.resolve()
    tried = ", ".join(str(c) for c in candidates) or "nothing"
    raise ProfileError(f"no game checkout found (tried {tried}); pass --game <path>")


def stage(profile, stage_id):
    for s in profile["stages"]:
        if s["id"] == stage_id or s["slug"] == stage_id:
            return s
    raise ProfileError(f"no stage {stage_id!r}; stages are " + ", ".join(f"{s['id']} {s['slug']}" for s in profile["stages"]))
