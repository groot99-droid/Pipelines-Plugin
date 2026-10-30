# -*- coding: utf-8 -*-
"""The reach-connect skill's checker agrees with the engine and with the repo's toolsets."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from agent_reach.channels import get_all_channels

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins" / "reach" / "skills" / "reach-connect" / "scripts" / "check_toolset.py"

pytestmark = pytest.mark.skipif(not SCRIPT.exists(), reason="plugins/reach is not here")


def _load():
    spec = importlib.util.spec_from_file_location("check_toolset", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bundled_channel_list_matches_the_engine():
    assert set(_load().CHANNELS) == {c.name for c in get_all_channels()}


def test_repo_toolsets_pass_the_checker():
    paths = sorted((ROOT / ".claude" / "skills").glob("reach-*/SKILL.md"))
    paths += sorted((ROOT / "plugins").glob("*/skills/*field-research/SKILL.md"))
    assert paths, "no toolsets found"
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), *map(str, paths)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout


def test_checker_names_an_unknown_channel(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "---\nname: x\ndescription: y\nmetadata:\n  reach: [web, tiktok]\n---\n"
        "agent-reach doctor --json; ~/.agent-reach; untrusted\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), str(skill)],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "tiktok" in result.stdout
