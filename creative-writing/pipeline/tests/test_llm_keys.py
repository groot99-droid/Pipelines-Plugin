"""Tests for where llm.py finds its keys. stdlib unittest; run from the repo root:

    python -m unittest discover -s creative-writing/pipeline/tests -v

These tests never read the real key files: both locations are pointed at a
temporary folder, and assertions compare key names, never values.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parent.parent
REPO = PIPELINE.parent.parent
sys.path.insert(0, str(PIPELINE))

import llm  # noqa: E402

NAMES = ("GEMINI_API_KEY", "GEMINI_MODEL", "ANTHROPIC_API_KEY", "ROSW_KEYS_FILE")


def base_env():
    """The current environment without any key the tests look at."""
    return {k: v for k, v in os.environ.items() if k not in NAMES}


class UserKeyFileTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.keys = Path(tmp.name) / "keys.env"
        self.legacy = Path(tmp.name) / "legacy.env"
        patcher = mock.patch.object(llm, "LEGACY_ENV", str(self.legacy))
        patcher.start()
        self.addCleanup(patcher.stop)

    def load(self, **extra):
        env = base_env()
        env["ROSW_KEYS_FILE"] = str(self.keys)
        env.update(extra)
        with mock.patch.dict(os.environ, env, clear=True):
            llm._load_dotenv()
            return {k: os.environ.get(k) for k in NAMES if k in os.environ}

    def test_default_location_is_outside_the_repo(self):
        with mock.patch.dict(os.environ, base_env(), clear=True):
            path = Path(llm.user_keys_file())
        self.assertTrue(path.is_absolute())
        self.assertEqual(path.parent.name, ".rosw")
        self.assertNotIn(REPO.resolve(), path.resolve().parents)

    def test_override_location(self):
        self.assertEqual(self.load()["ROSW_KEYS_FILE"], str(self.keys))
        with mock.patch.dict(os.environ, {"ROSW_KEYS_FILE": str(self.keys)}):
            self.assertEqual(llm.user_keys_file(), str(self.keys))

    def test_user_file_is_loaded_and_overrides_the_shell(self):
        self.keys.write_text('GEMINI_API_KEY="from-file"\n# comment\n', encoding="utf-8")
        env = self.load(GEMINI_API_KEY="from-shell")
        self.assertTrue(env["GEMINI_API_KEY"] == "from-file", "file value did not win")

    def test_placeholder_and_missing_file_are_ignored(self):
        for placeholder in ("your-key-here", "Add_Key"):
            self.keys.write_text(f"GEMINI_API_KEY={placeholder}\n", encoding="utf-8")
            self.assertNotIn("GEMINI_API_KEY", list(self.load()))
        self.keys.unlink()
        self.assertNotIn("GEMINI_API_KEY", list(self.load()))

    def test_user_file_wins_over_legacy_repo_env(self):
        self.keys.write_text("GEMINI_API_KEY=user\n", encoding="utf-8")
        self.legacy.write_text("GEMINI_API_KEY=legacy\nGEMINI_MODEL=m\n", encoding="utf-8")
        env = self.load()
        self.assertTrue(env["GEMINI_API_KEY"] == "user", "user file did not win")
        self.assertTrue(env.get("GEMINI_MODEL") == "m", "legacy file was not read")


if __name__ == "__main__":
    unittest.main()
