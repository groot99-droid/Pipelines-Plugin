"""Append-only publish log. Its main job: a retry (or a second `send`) can never post the same thing twice."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

FILE_NAME = "publish_ledger.jsonl"
OK_STATES = ("ok", "draft")


def idempotency_key(fingerprint: str, platform: str, mode: str, text: str) -> str:
    return hashlib.sha256(f"{fingerprint}|{platform}|{mode}|{text}".encode()).hexdigest()[:24]


def read(edit_dir: Path) -> list[dict]:
    p = edit_dir / FILE_NAME
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def find_success(edit_dir: Path, key: str) -> dict | None:
    for entry in reversed(read(edit_dir)):
        if entry.get("key") == key and entry.get("status") in OK_STATES:
            return entry
    return None


def record(edit_dir: Path, *, key: str, platform: str, mode: str, status: str, remote_id: str | None = None,
           url: str | None = None, note: str | None = None) -> dict:
    """Append one line. No tokens or captions are stored, only what is needed to recognise a repeat."""
    edit_dir.mkdir(parents=True, exist_ok=True)
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "key": key, "platform": platform, "mode": mode,
             "status": status, "id": remote_id, "url": url, "note": note}
    with open(edit_dir / FILE_NAME, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry
