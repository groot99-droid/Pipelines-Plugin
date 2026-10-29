"""Small helpers shared by platform modules."""
from __future__ import annotations

import mimetypes
import time
from collections.abc import Iterator
from pathlib import Path


def read_chunks(path: str | Path, size: int) -> Iterator[tuple[int, bytes]]:
    """Yield (offset, bytes) for consecutive chunks of at most `size` bytes."""
    with open(path, "rb") as f:
        offset = 0
        while True:
            block = f.read(size)
            if not block:
                return
            yield offset, block
            offset += len(block)


def mime_for(path: str | Path, default: str = "video/mp4") -> str:
    return mimetypes.guess_type(str(path))[0] or default


def utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())


def first_line(text: str, limit: int) -> str:
    line = (text.strip().splitlines() or [""])[0].strip()
    return line[:limit].rstrip()


def poll(fn, done, *, interval: float, timeout: float, sleep=time.sleep, now=time.monotonic):
    """Call fn() until done(result) is truthy or `timeout` seconds pass. Returns the last result."""
    deadline = now() + timeout
    while True:
        res = fn()
        if done(res):
            return res
        if now() >= deadline:
            return res
        sleep(interval)
