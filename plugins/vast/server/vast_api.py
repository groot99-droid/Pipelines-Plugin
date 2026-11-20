"""A small stdlib client for the Vast.ai REST API (https://console.vast.ai/api/v0).

Every call sends `Authorization: Bearer <key>`. The key is read once by `api_key()` and never
returned, logged or written anywhere. The endpoint shapes are those of docs.vast.ai/api as read on
2026-11-19, corrected by the first live run that day (UNVERIFIED.md says which were called).

VAST_BASE_URL overrides the base for tests. It must be https, or http on 127.0.0.1 / localhost.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://console.vast.ai/api/v0"
LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")
PLACEHOLDERS = {"", "your-key-here", "add_key", "changeme", "xxx"}
TIMEOUT = 60


class VastError(Exception):
    """A refusal or failure, reported to the caller as a tool error."""

    def __init__(self, code, message, hint=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


# ── the key ──────────────────────────────────────────────────────────────────

def home(environ):
    return Path(environ.get("HOME") or environ.get("USERPROFILE") or Path.home())


def expand(path, environ):
    """A path with a leading ~ resolved against the given environment's home."""
    text = str(path)
    if text == "~" or text.startswith(("~/", "~\\")):
        return home(environ) / text[2:]
    return Path(text)


def read_key_file(path):
    """NAME=value lines of a keys file, as a dict. Comments and blanks are skipped."""
    values = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        if name.startswith("export "):
            name = name[len("export "):].strip()
        values[name] = value.strip().strip('"').strip("'")
    return values


def _usable(value):
    return isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS


def api_key(environ=None):
    """VAST_API_KEY from the environment, else the keys file named by VAST_KEYS_FILE, else the
    Vast CLI's own key file. Raises VastError naming the places it looked, never a value."""
    environ = os.environ if environ is None else environ
    value = environ.get("VAST_API_KEY")
    if _usable(value):
        return value.strip()
    keys_file = environ.get("VAST_KEYS_FILE")
    if keys_file:
        value = read_key_file(expand(keys_file, environ)).get("VAST_API_KEY")
        if _usable(value):
            return value.strip()
    for cli_file in (home(environ) / ".config" / "vastai" / "vast_api_key", home(environ) / ".vast_api_key"):
        try:
            value = cli_file.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if _usable(value):
            return value
    raise VastError("no_key", "VAST_API_KEY is not set",
                    "set VAST_API_KEY in the environment, or name a keys file holding it with "
                    "VAST_KEYS_FILE, or run `vastai set api-key` once; the value is never shown here")


def has_key(environ=None):
    try:
        api_key(environ)
        return True
    except VastError:
        return False


def base_url(environ=None):
    environ = os.environ if environ is None else environ
    url = (environ.get("VAST_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme == "https":
        return url
    if parts.scheme == "http" and parts.hostname in LOCAL_HOSTS:
        return url
    raise VastError("bad_base_url", "VAST_BASE_URL must be https (or http on localhost)")


# ── the client ───────────────────────────────────────────────────────────────

class VastAPI:
    def __init__(self, environ=None, opener=None):
        self.environ = os.environ if environ is None else environ
        self.base = base_url(self.environ)
        self.opener = opener or urllib.request.build_opener()

    def call(self, method, path, body=None, query=None, base=None):
        url = (base or self.base) + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Accept", "application/json")
        request.add_header("Authorization", "Bearer " + api_key(self.environ))
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with self.opener.open(request, timeout=TIMEOUT) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = json.loads(exc.read() or b"{}").get("msg") or ""
            except (ValueError, AttributeError):
                pass
            hint = "check VAST_API_KEY" if exc.code in (401, 403) else None
            raise VastError("http_%d" % exc.code,
                            f"Vast answered {exc.code} to {method} {path}"
                            + (f": {str(detail)[:200]}" if detail else ""), hint) from None
        except urllib.error.URLError as exc:
            raise VastError("unreachable", f"Vast could not be reached: {exc.reason}",
                            "check the network, or VAST_BASE_URL") from None
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except ValueError:
            raise VastError("bad_reply", f"Vast's reply to {method} {path} was not JSON") from None

    # account
    def user(self):
        return self.call("GET", "/users/current/")

    # offers
    def search(self, query):
        reply = self.call("PUT", "/search/asks/", {"q": query})
        offers = reply.get("offers") if isinstance(reply, dict) else reply
        return offers if isinstance(offers, list) else []

    def offer(self, offer_id):
        # Vast's search returns nothing for an `id` filter (live run, 2026-11-19); the same number is
        # filterable as `ask_contract_id`.
        offers = self.search({"ask_contract_id": {"eq": int(offer_id)}, "rentable": {"eq": True},
                              "type": "on-demand", "limit": 1})
        for offer in offers:
            if int(offer.get("id", -1)) == int(offer_id):
                return offer
        return None

    # instances
    def create(self, offer_id, body):
        return self.call("PUT", f"/asks/{int(offer_id)}/", body)

    def instances(self):
        # The v0 list answers 410 "deprecated, use /api/v1/instances/" (live run, 2026-11-19). v1 keeps
        # the list under the same `instances` key. Only this one call moves; a base that is not Vast's
        # v0 (the tests' fake) is used as it is.
        base = self.base[:-len("/api/v0")] + "/api/v1" if self.base.endswith("/api/v0") else self.base
        reply = self.call("GET", "/instances/", base=base)
        items = reply.get("instances") if isinstance(reply, dict) else reply
        return items if isinstance(items, list) else []

    def instance(self, instance_id):
        reply = self.call("GET", f"/instances/{int(instance_id)}/")
        item = reply.get("instances") if isinstance(reply, dict) else None
        if isinstance(item, list):
            item = item[0] if item else None
        return item if isinstance(item, dict) else None

    def attach_ssh(self, instance_id, public_key):
        return self.call("POST", f"/instances/{int(instance_id)}/ssh/", {"ssh_key": public_key})

    def stop(self, instance_id):
        return self.call("PUT", f"/instances/{int(instance_id)}/", {"state": "stopped"})

    def destroy(self, instance_id):
        return self.call("DELETE", f"/instances/{int(instance_id)}/")
