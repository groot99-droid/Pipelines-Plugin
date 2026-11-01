import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".claude" / "hooks" / "vault_guard.py"


def run(path):
    out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(path)}}),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None


class VaultGuard(unittest.TestCase):
    def test_original_asks(self):
        self.assertEqual(run(ROOT / "creative-writing/vault/01_Books/01_The_First_Friend.md"), "ask")

    def test_derived_and_auto_authored_do_not_ask(self):
        self.assertIsNone(run(ROOT / "creative-writing/vault/10_Characters/02_The_Bottonian_Philosopher.md"))
        self.assertIsNone(run(ROOT / "creative-writing/vault/11_Essays/04_The_Creative_Codex_of_the_Mythic_Architect.md"))

    def test_new_file_and_other_folders_pass(self):
        self.assertIsNone(run(ROOT / "creative-writing/vault/03_Stories/not-yet-written.md"))
        self.assertIsNone(run(ROOT / "studio/pipeline/studio_run.py"))

    def test_studio_notes_denied_docs_allowed(self):
        self.assertEqual(run(ROOT / "studio/vault/aurora/ui/console.md"), "deny")
        self.assertIsNone(run(ROOT / "studio/vault/CLAUDE.md"))


if __name__ == "__main__":
    unittest.main()
