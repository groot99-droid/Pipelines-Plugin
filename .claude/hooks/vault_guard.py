"""PreToolUse hook: keep Write and Edit away from the vaults' protected notes.

creative-writing/vault: an original work (`origin: original`, or no origin but a `source_volume`) is the author's
  certified text. Edits ask first; the author may allow grammar fixes or a change they request.
studio/vault: notes and brand gates are written only through content_md.py and gate_md.py, so a
  Write or Edit there is refused. The vault's own CLAUDE.md, SCHEMA.md and README.md stay editable.
Stdlib only. It reads the hook JSON on stdin and prints a decision, or nothing.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CW = ROOT / "creative-writing" / "vault"
ST = ROOT / "studio" / "vault"
DOCS = {"CLAUDE.md", "SCHEMA.md", "README.md"}


def decide(kind, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": kind,
                                             "permissionDecisionReason": reason}}))


def inside(path, folder):
    try:
        path.relative_to(folder)
        return True
    except ValueError:
        return False


def is_original(path):
    if not path.is_file() or path.suffix != ".md":
        return False
    head = path.read_text(encoding="utf-8", errors="replace")[:2000]
    if not head.startswith("---"):
        return False
    front = head.split("---", 2)[1] if head.count("---") >= 2 else head
    origin = re.search(r"^origin:\s*(\S+)", front, re.M)
    if origin:
        return origin.group(1) == "original"
    return re.search(r"^source_volume:", front, re.M) is not None  # no origin recorded: a master-volume work counts as original


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    target = (event.get("tool_input") or {}).get("file_path") or (event.get("tool_input") or {}).get("notebook_path")
    if not target:
        return
    path = Path(target)
    path = (path if path.is_absolute() else Path(event.get("cwd") or ROOT) / path).resolve()
    if inside(path, ST) and path.suffix == ".md" and not (path.parent == ST and path.name in DOCS):
        decide("deny", "studio/vault notes and brand gates are written only through content_md.py "
                       "(plan, then apply --confirm) or gate_md.py. Do not use Write or Edit here.")
    elif inside(path, CW) and is_original(path):
        decide("ask", "This is an original work (origin: original). It is certified verbatim: "
                      "edit only what the author asked for, such as grammar fixes or a stated update.")


if __name__ == "__main__":
    main()
