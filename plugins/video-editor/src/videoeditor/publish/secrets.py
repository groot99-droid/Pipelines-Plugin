"""Credential storage: OS keyring, or environment variables. This module never writes a secret to a file.

Environment variables are the fallback (and the right choice in CI / containers): VE_<PLATFORM>_<NAME>,
for example VE_MASTODON_TOKEN or VE_YOUTUBE_CLIENT_SECRET. `ve publish init` stores into the keyring
when one is available and otherwise tells you which variables to set.
"""
from __future__ import annotations

import json
import os

SERVICE = "videoeditor-publish"


def env_name(platform: str, name: str) -> str:
    return f"VE_{platform}_{name}".upper().replace("-", "_")


def _keyring():
    try:
        import keyring
        from keyring.backends import fail
    except ImportError:
        return None
    try:
        backend = keyring.get_keyring()
    except Exception:
        return None
    cls = type(backend)
    # no backend, the null backend, or a file-based/plaintext one (keyrings.alt) is NOT a secret store
    if isinstance(backend, fail.Keyring) or cls.__module__.startswith(("keyring.backends.null", "keyrings.alt")) \
            or "plaintext" in cls.__name__.lower():
        return None
    return keyring


def keyring_available() -> bool:
    return _keyring() is not None


def get(platform: str, name: str) -> str | None:
    v = os.environ.get(env_name(platform, name))
    if v:
        return v
    kr = _keyring()
    if kr is None:
        return None
    try:
        return kr.get_password(SERVICE, f"{platform}:{name}")
    except Exception:
        return None


def set(platform: str, name: str, value: str) -> None:  # noqa: A001 - mirrors keyring's API
    kr = _keyring()
    if kr is None:
        raise RuntimeError(
            f"no OS keyring available, so {name} was not saved (this tool never writes secrets to files). "
            f"Set the environment variable {env_name(platform, name)} instead.")
    kr.set_password(SERVICE, f"{platform}:{name}", value)


def delete(platform: str, name: str) -> bool:
    kr = _keyring()
    if kr is None:
        return False
    try:
        kr.delete_password(SERVICE, f"{platform}:{name}")
        return True
    except Exception:
        return False


def get_json(platform: str, name: str) -> dict | None:
    raw = get(platform, name)
    return json.loads(raw) if raw else None


def set_json(platform: str, name: str, value: dict) -> None:
    set(platform, name, json.dumps(value))
