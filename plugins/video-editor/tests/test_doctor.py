"""`ve doctor` and the plugin launcher."""
import _paths  # noqa: F401  (puts src/ on sys.path)

import io
import json
import os
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path
from unittest import mock

from videoeditor import doctor

ROOT = Path(__file__).resolve().parents[1]


class Doctor(unittest.TestCase):
    def test_report_shape_and_required_tools(self):
        rep = doctor.report()
        self.assertEqual(set(rep["tools"]) >= {"ffmpeg", "ffprobe", "node", "npm"}, True)
        self.assertIn("numpy", rep["required_python"])
        self.assertEqual(set(rep["optional_python"]), {"faster_whisper", "whisperx", "demucs", "requests", "keyring"})
        for o in rep["optional_python"].values():
            self.assertTrue(o["extra"].startswith("videoeditor["))     # names the pip extra that adds it
            self.assertTrue(o["pip"])                                  # and the package to install directly
        self.assertEqual(rep["ok"], not rep["problems"])

    def test_missing_ffmpeg_is_a_problem(self):
        with mock.patch("shutil.which", return_value=None):
            rep = doctor.report()
        self.assertFalse(rep["ok"])
        self.assertTrue(any("ffmpeg and ffprobe" in p for p in rep["problems"]))

    def test_no_subtitles_filter_is_flagged(self):
        with mock.patch.object(doctor, "_ffmpeg_has_filter", return_value=False):
            rep = doctor.report()
        if rep["tools"]["ffmpeg"]["found"]:
            self.assertTrue(any("subtitles" in p for p in rep["problems"]))

    def test_never_prints_credential_values(self):
        env = {"VE_MASTODON_INSTANCE": "https://m.example", "VE_MASTODON_TOKEN": "SUPERSECRETVALUE",
               "VE_BLUESKY_APP_PASSWORD": "ANOTHERSECRET", "VE_BLUESKY_IDENTIFIER": "me.example"}
        with mock.patch.dict(os.environ, env):
            rep = doctor.report()
            text = doctor.render(rep) + json.dumps(rep)
        self.assertNotIn("SUPERSECRETVALUE", text)
        self.assertNotIn("ANOTHERSECRET", text)
        self.assertNotIn("m.example", text)
        self.assertTrue(rep["publish_configured"]["mastodon"])             # presence, by name only
        self.assertTrue(rep["publish_configured"]["bluesky"])

    def test_main_exit_code_and_json(self):
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            code = doctor.main(as_json=True)
        self.assertEqual(code, 0 if json.loads(out.getvalue())["ok"] else 1)


class Launcher(unittest.TestCase):
    def run_ve(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "bin" / "ve.py"), *args], capture_output=True, text=True, encoding="utf-8", cwd=Path(tempfile.gettempdir()))

    def test_runs_from_any_directory_without_install(self):
        r = self.run_ve("--help")
        self.assertEqual(r.returncode, 0)
        for cmd in ("ask", "doctor", "publish", "separate", "transcribe"):
            self.assertIn(cmd, r.stdout)

    def test_doctor_json_through_the_launcher(self):
        r = self.run_ve("doctor", "--json")
        self.assertIn(r.returncode, (0, 1))
        self.assertIn("required_python", json.loads(r.stdout))

    def test_publish_is_reachable_through_the_launcher(self):
        with tempfile.TemporaryDirectory() as edit_dir:
            r = self.run_ve("publish", "status", "--edit-dir", edit_dir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("configured:", r.stdout)


if __name__ == "__main__":
    unittest.main()
