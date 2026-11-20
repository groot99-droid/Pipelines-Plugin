"""Read the vast plugin's spend ledger, read-only, for a run's `remote` branch.

The vast MCP server (plugins/vast/) rents GPUs and records each rental in
<VAST_STATE_DIR>/state.json (default ~/.vast-mcp/). A run on a `remote` branch
claims one rental with `studio_run.py lease <run-id> <instance-id>`, and its
execute stage is not marked done without that claim. This file only reads that
ledger. It never calls Vast, never reads a key, and never writes the ledger.

What it cannot do: see what ran on the instance. The run's execute_log.md says
that; the bookkeeper checks the rental, not the work.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def state_dir(environ=None):
    environ = os.environ if environ is None else environ
    folder = environ.get("VAST_STATE_DIR") or str(Path(environ.get("HOME") or Path.home()) / ".vast-mcp")
    return Path(folder).expanduser()


def rentals(environ=None):
    """Every rental the ledger records, or [] when there is no ledger."""
    path = state_dir(environ) / "state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    found = state.get("rentals") if isinstance(state, dict) else None
    return [r for r in found if isinstance(r, dict)] if isinstance(found, list) else []


def rental(instance_id, environ=None):
    for item in rentals(environ):
        if str(item.get("instance_id")) == str(instance_id):
            return item
    return None
