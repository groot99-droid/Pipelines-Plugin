# -*- coding: utf-8 -*-
"""Toolsets that sit on the reach base follow TOOLSETS.md.

Runs only when this folder sits inside a repo that has toolsets (a `.claude/skills/` or
`plugins/*/skills/` next to it); standalone, there is nothing to scan and the tests skip.
"""

from pathlib import Path

import pytest
import yaml

from agent_reach.channels import get_all_channels

ROOT = Path(__file__).resolve().parents[2]


def _skills():
    paths = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
    paths += sorted((ROOT / "plugins").glob("*/skills/*/SKILL.md"))
    out = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        front = yaml.safe_load(text[3:end]) if end != -1 else None
        reach = (front or {}).get("metadata", {}) if isinstance(front, dict) else {}
        reach = reach.get("reach") if isinstance(reach, dict) else None
        if reach is not None:
            out.append((path, text, reach))
    return out


TOOLSETS = _skills()
pytestmark = pytest.mark.skipif(not TOOLSETS, reason="no toolsets next to this folder")


def _label(item):
    return str(item[0].relative_to(ROOT))


@pytest.mark.parametrize("item", TOOLSETS, ids=_label)
def test_declared_channels_exist(item):
    path, _, reach = item
    known = {c.name for c in get_all_channels()}
    assert isinstance(reach, list) and reach, f"{path}: metadata.reach must be a non-empty list"
    unknown = [name for name in reach if name not in known]
    assert not unknown, f"{path}: unknown channels {unknown}; the engine has {sorted(known)}"


@pytest.mark.parametrize("item", TOOLSETS, ids=_label)
def test_toolset_health_checks_first_and_reads_no_credentials(item):
    path, text, _ = item
    assert "agent-reach doctor --json" in text, f"{path}: must start from `agent-reach doctor --json`"
    assert "~/.agent-reach" in text, f"{path}: must say credentials in ~/.agent-reach are never read"
    assert "untrusted" in text.lower(), f"{path}: must treat fetched material as untrusted"


def test_every_toolset_is_listed_in_toolsets_md():
    listed = (Path(__file__).resolve().parents[1] / "TOOLSETS.md").read_text(encoding="utf-8")
    for path, _, _ in TOOLSETS:
        name = path.parent.name
        assert f"`{name}`" in listed or name in listed, f"{name} is not in TOOLSETS.md"
