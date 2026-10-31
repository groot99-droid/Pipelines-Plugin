"""One way to fetch a file: into `<target>.part`, checked, then moved into place.

Standard library only, so the generations library can use it too. A short
read, an error, or an interrupt leaves no `.part` behind and no target.
"""

import hashlib
import http.client
import os
import urllib.error
import urllib.request
from pathlib import Path


class DownloadError(Exception):
    """The file was not kept. The message says why, without the link."""


def download(url, target, headers=None, timeout=120, chunk=1 << 16):
    """Fetch url to target. Returns {"file", "bytes", "sha256"}."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    digest, size = hashlib.sha256(), 0
    try:
        request = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(request, timeout=timeout) as response, part.open("wb") as out:
            expected = response.headers.get("Content-Length")
            while True:
                block = response.read(chunk)
                if not block:
                    break
                out.write(block)
                digest.update(block)
                size += len(block)
        if expected is not None and int(expected) != size:
            raise DownloadError(f"{target.name}: got {size} bytes of {expected}")
        os.replace(part, target)
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as err:
        raise DownloadError(f"{target.name}: the download failed "
                            f"({getattr(err, 'reason', None) or type(err).__name__})") from None
    finally:
        if part.exists():
            part.unlink()
    return {"file": target.name, "bytes": size, "sha256": digest.hexdigest()}
