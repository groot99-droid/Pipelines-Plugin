"""Work types: a run given --type files under that type's folder; without one a
work keeps its mode's folder; an unknown type is refused, and every type's
folder exists in the vault."""
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE))

import run_pipeline as rp  # noqa: E402

VAULT = PIPELINE.parent / "vault"


class WorkTypes(unittest.TestCase):
    def setUp(self):
        self.spec = rp.load_spec()

    def test_mode_default_without_a_type(self):
        self.assertEqual(rp._target(self.spec, "epic-fantasy"), ("03_Stories", "story"))

    def test_type_overrides_folder_and_type(self):
        self.assertEqual(rp._target(self.spec, "epic-fantasy", "worldbuilding"),
                         ("05_Worldbuilding", "worldbuilding"))
        self.assertEqual(rp._target(self.spec, "confessional-poetry", "song"), ("06_Songs", "song"))

    def test_unknown_type_is_refused(self):
        with self.assertRaises(SystemExit):
            rp._target(self.spec, "epic-fantasy", "codex")

    def test_types_match_schema_and_vault(self):
        allowed = {t.strip() for t in self.spec["frontmatter_schema"]["type"].split("|")}
        for work_type, folder in self.spec["work_types"].items():
            self.assertIn(work_type, allowed)
            self.assertTrue((VAULT / folder / "_index.md").exists(), folder)


if __name__ == "__main__":
    unittest.main()
