"""One place for network calls: timeouts, retries with backoff on 429/5xx, and secret-safe error text."""
from __future__ import annotations

import time

from videoeditor.publish.errors import ApiError, PublishError

RETRY_STATUSES = (429, 500, 502, 503, 504)
_SENSITIVE = ("authorization", "access_token", "refresh_token", "client_secret", "code_verifier", "password")


def _requests():
    try:
        import requests
    except ImportError:
        raise SystemExit("publishing needs requests: pip install 'videoeditor[publish]'") from None
    return requests


def redact(text: str, secrets: list[str] | None = None) -> str:
    for s in secrets or []:
        if s:
            text = text.replace(s, "***")
    return text


def request(platform: str, method: str, url: str, *, retries: int = 3, backoff: float = 1.0, timeout: float = 60,
            ok: tuple[int, ...] = (200, 201, 202, 204, 206), sleep=time.sleep, **kw):
    """Perform a request, retrying 429/5xx (honouring Retry-After). Raises ApiError on a final non-ok status."""
    rq = _requests()
    last = None
    for attempt in range(retries + 1):
        try:
            resp = rq.request(method, url, timeout=timeout, **kw)
        except rq.RequestException as e:
            # the exception text contains the full URL, which can carry a token in its query string: never echo it
            if attempt < retries:
                sleep(backoff * (2 ** attempt))
                continue
            raise PublishError(f"{platform}: network error ({type(e).__name__}) talking to "
                               f"{url.split('?')[0].split('://')[-1].split('/')[0]}") from None
        if resp.status_code in ok:
            return resp
        last = resp
        if resp.status_code in RETRY_STATUSES and attempt < retries:
            wait = resp.headers.get("Retry-After")
            sleep(float(wait) if wait and wait.replace(".", "", 1).isdigit() else backoff * (2 ** attempt))
            continue
        break
    body = (last.text or "")[:500] if last is not None else ""
    raise ApiError(platform, last.status_code if last is not None else 0, redact(body))
