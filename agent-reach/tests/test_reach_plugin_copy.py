# -*- coding: utf-8 -*-
"""plugins/reach carries a verbatim copy of this engine's skill; it must not drift."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_reach_plugin.py"
spec = importlib.util.spec_from_file_location("sync_reach_plugin", SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

pytestmark = pytest.mark.skipif(not sync.TARGET.parent.is_dir(), reason="plugins/reach is not here")


def test_plugin_copy_matches_the_engine_skill():
    bad = [str(p) for p in sync.drift()]
    assert not bad, f"run python agent-reach/scripts/sync_reach_plugin.py; drifted: {bad}"
