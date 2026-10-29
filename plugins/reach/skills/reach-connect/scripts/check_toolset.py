#!/usr/bin/env python3
"""Check that a skill is wired to Agent Reach in the expected shape.

    python check_toolset.py <SKILL.md> [<SKILL.md> ...] [--live]

For each file: `metadata.reach` is a non-empty list, every name is a channel Agent Reach has, and
the body carries the three rules every toolset states (health-check first, credentials in
~/.agent-reach never read, fetched content untrusted). Exit 0 if all pass, 1 if any fails.

Channel names come from a bundled list; `--live` takes them from `agent-reach doctor --json`
instead (read-only, but it runs the doctor). stdlib only; PyYAML is used when present.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Keep in step with agent_reach.channels (a test in the engine's repo checks this).
CHANNELS = (
    "github", "twitter", "youtube", "reddit", "facebook", "instagram", "bilibili",
    "xiaohongshu", "linkedin", "xiaoyuzhou", "v2ex", "xueqiu", "rss", "exa_search", "web",
)

REQUIRED = (
    ("agent-reach doctor --json", "must start from `agent-reach doctor --json`"),
    ("~/.agent-reach", "must say credentials in ~/.agent-reach are never read"),
    ("untrusted", "must treat fetched material as untrusted"),
)


def live_channels():
    exe = shutil.which("agent-reach")
    if not exe:
        raise RuntimeError("agent-reach is not installed; run without --live")
    out = subprocess.run([exe, "doctor", "--json"], capture_output=True, text=True, timeout=120)
    return tuple(json.loads(out.stdout))


def parse(text):
    """Return (reach list or None, body) from a SKILL.md."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    front, body = text[3:end], text[end + 4:]
    try:
        import yaml
        try:
            data = yaml.safe_load(front)
        except yaml.YAMLError as exc:
            return None, f"frontmatter is not valid YAML: {str(exc).splitlines()[0]}"
        meta = data.get("metadata") if isinstance(data, dict) else None
        reach = meta.get("reach") if isinstance(meta, dict) else None
        return reach, body
    except ImportError:
        match = re.search(r"^\s+reach:\s*\[(.*?)\]", front, re.M)
        if not match:
            return None, body
        return [x.strip().strip("'\"") for x in match.group(1).split(",") if x.strip()], body


def check(path, known):
    problems = []
    text = Path(path).read_text(encoding="utf-8")
    reach, body = parse(text)
    if not isinstance(reach, list) or not reach:
        problems.append("metadata.reach must be a non-empty list")
    else:
        unknown = [n for n in reach if n not in known]
        if unknown:
            problems.append(f"unknown channels {unknown}; Agent Reach has {sorted(known)}")
    low = body.lower()
    for needle, message in REQUIRED:
        if needle.lower() not in low:
            problems.append(message)
    return problems


def main(argv):
    live = "--live" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    known = live_channels() if live else CHANNELS
    failed = 0
    for path in paths:
        problems = check(path, known)
        print(f"{'FAIL' if problems else 'ok  '} {path}")
        for p in problems:
            print(f"     {p}")
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
