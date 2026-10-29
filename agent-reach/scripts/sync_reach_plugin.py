#!/usr/bin/env python3
"""Refresh plugins/reach/skills/agent-reach/ from this engine's agent_reach/skill/.

The reach plugin cannot read outside its own folder once installed, so it carries a copy of the
engine's English skill and its references. Run this after changing either, from anywhere:

    python agent-reach/scripts/sync_reach_plugin.py          # copy
    python agent-reach/scripts/sync_reach_plugin.py --check  # exit 1 if the copy has drifted

stdlib only. A no-op when the plugin folder is not next to this engine.
"""

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
SOURCE = ENGINE / "agent_reach" / "skill"
TARGET = ENGINE.parent / "plugins" / "reach" / "skills" / "agent-reach"


def pairs():
    yield SOURCE / "SKILL_en.md", TARGET / "SKILL.md"
    for ref in sorted((SOURCE / "references").glob("*.md")):
        yield ref, TARGET / "references" / ref.name


def drift():
    """Files whose copy is missing or differs, plus copies with no source."""
    out = [dst for src, dst in pairs() if not dst.exists() or dst.read_bytes() != src.read_bytes()]
    wanted = {dst for _, dst in pairs()}
    if (TARGET / "references").is_dir():
        out += [p for p in sorted((TARGET / "references").glob("*.md")) if p not in wanted]
    return out


def main(argv):
    if not TARGET.parent.is_dir():
        print("plugins/reach is not next to this engine; nothing to do")
        return 0
    if "--check" in argv:
        bad = drift()
        for path in bad:
            print(f"drifted: {path.relative_to(ENGINE.parent)}")
        return 1 if bad else 0
    for src, dst in pairs():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
    for path in drift():
        path.unlink()
    print("synced plugins/reach/skills/agent-reach from agent_reach/skill")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
