"""PreToolUse hook: a `ve publish send --yes` must follow a dry run for that platform.

A dry run is `ve publish send --platform P` without --yes, or `ve publish plan`.
It leaves a marker in the temp folder; a real send for P is refused without a fresh
one, and still asks the user before it goes. `init` and `revoke` always ask.
Stdlib only. It reads the hook JSON on stdin and prints a decision, or nothing.
"""
import json
import re
import shlex
import sys
import tempfile
import time
from pathlib import Path

MARKERS = Path(tempfile.gettempdir()) / "ve-publish-guard"
FRESH_SECONDS = 3600
NAMES = ("youtube", "tiktok", "instagram", "bluesky", "x", "linkedin", "facebook", "threads")


def decide(kind, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": kind,
                                             "permissionDecisionReason": reason}}))


def publish_args(command):
    """The tokens after `publish` when the command runs ve, else None."""
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return None
    for i, tok in enumerate(tokens):
        if tok == "publish" and i > 0 and re.search(r"(^|[\/])ve(\.py)?$", tokens[i - 1]):
            return tokens[i + 1:]
    return None


def platform_of(args):
    for i, tok in enumerate(args):
        if tok == "--platform" and i + 1 < len(args):
            return args[i + 1].lower()
        if tok.startswith("--platform="):
            return tok.split("=", 1)[1].lower()
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return
    if event.get("tool_name") != "Bash":
        return
    args = publish_args((event.get("tool_input") or {}).get("command", ""))
    if not args:
        return
    sub = args[0]
    if sub in ("init", "revoke"):
        decide("ask", f"`ve publish {sub}` changes stored credentials. Confirm you asked for it.")
        return
    MARKERS.mkdir(exist_ok=True)
    if sub == "plan":
        for name in NAMES:
            (MARKERS / name).write_text(str(time.time()))
        return
    if sub != "send":
        return
    platform = platform_of(args)
    if "--yes" not in args:
        if platform:
            (MARKERS / platform).write_text(str(time.time()))
        return
    marker = MARKERS / (platform or "?")
    fresh = marker.exists() and time.time() - float(marker.read_text() or 0) < FRESH_SECONDS
    if not fresh:
        decide("deny", "Run the dry run first (`ve publish send --platform "
                       f"{platform or 'P'}` without --yes, or `ve publish plan`) and show the plan to the user.")
        return
    flags = [f for f in ("--public", "--accept-cost", "--force") if f in args]
    extra = f" with {', '.join(flags)}" if flags else ""
    decide("ask", f"This sends a real post to {platform}{extra}. Confirm the plan above is what the user approved.")


if __name__ == "__main__":
    main()
