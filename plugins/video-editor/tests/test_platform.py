import _paths  # noqa: F401  (puts src/ on sys.path)
import re
import unittest
from pathlib import Path
from unittest import mock

from videoeditor.core import captions, platform

SRC = Path(__file__).parents[1] / "src"


class NoMacOnlyBits(unittest.TestCase):
    def test_no_macos_strings_in_source(self):
        bad = ("videotoolbox", "/System/Library", "Menlo.ttc")
        offenders = []
        for p in SRC.rglob("*.py"):
            text = p.read_text(encoding="utf-8").lower()
            offenders += [f"{p.name}: {b}" for b in bad if b.lower() in text]
        self.assertEqual(offenders, [])

    def test_no_elevenlabs_dependency_left(self):
        hits = [p.name for p in SRC.rglob("*.py") if "ELEVENLABS_API_KEY" in p.read_text(encoding="utf-8")]
        self.assertEqual(hits, [])


class WithoutFontconfig(unittest.TestCase):
    """Windows and stock macOS have no fc-match: fonts must degrade, not crash."""

    def test_find_font_returns_none_or_an_existing_file(self):
        with mock.patch("shutil.which", return_value=None):
            found = platform.find_font("No Such Family")
        self.assertTrue(found is None or Path(found).exists())

    def test_installed_family_passes_the_preferred_family_through(self):
        with mock.patch("shutil.which", return_value=None):
            self.assertEqual(captions.installed_family("Arial Black"), "Arial Black")

    def test_a_failing_fc_match_falls_back(self):
        with mock.patch("shutil.which", return_value="fc-match"), \
             mock.patch("subprocess.run", side_effect=OSError("boom")):
            self.assertIsNone(platform.fc_match("%{file}", "x"))
            self.assertEqual(captions.installed_family("Arial Black"), "DejaVu Sans")


class Utf8Everywhere(unittest.TestCase):
    def test_text_reads_and_writes_name_their_encoding(self):
        bare = re.compile(r"\.(?:read_text|write_text)\((?:[^()]|\([^()]*\))*\)")
        offenders = []
        for p in SRC.rglob("*.py"):
            for m in bare.finditer(p.read_text(encoding="utf-8")):
                if "encoding=" not in m.group(0):
                    offenders.append(f"{p.name}: {m.group(0)[:60]}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
