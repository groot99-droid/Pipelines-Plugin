import _paths  # noqa: F401  (puts src/ on sys.path)
import unittest
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"


class NoMacOnlyBits(unittest.TestCase):
    def test_no_macos_strings_in_source(self):
        bad = ("videotoolbox", "/System/Library", "Menlo.ttc")
        offenders = []
        for p in SRC.rglob("*.py"):
            text = p.read_text().lower()
            offenders += [f"{p.name}: {b}" for b in bad if b.lower() in text]
        self.assertEqual(offenders, [])

    def test_no_elevenlabs_dependency_left(self):
        hits = [p.name for p in SRC.rglob("*.py") if "ELEVENLABS_API_KEY" in p.read_text()]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
