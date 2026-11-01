import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "publish_guard.py"
sys.path.insert(0, str(HOOK.parent))
import publish_guard  # noqa: E402


def run(command):
    out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": command}}),
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else None


class PublishGuard(unittest.TestCase):
    def setUp(self):
        for p in publish_guard.MARKERS.glob("*"):
            p.unlink()

    def test_unrelated_commands_pass(self):
        self.assertIsNone(run("ls -la"))
        self.assertIsNone(run("python ve.py doctor"))

    def test_send_needs_dry_run_first(self):
        send = 'python "$P/bin/ve.py" publish send --platform bluesky --yes'
        self.assertEqual(run(send), "deny")
        self.assertIsNone(run('python "$P/bin/ve.py" publish send --platform bluesky'))
        self.assertEqual(run(send), "ask")

    def test_dry_run_is_per_platform(self):
        run("ve publish send --platform bluesky")
        self.assertEqual(run("ve publish send --platform x --yes"), "deny")

    def test_plan_covers_every_platform(self):
        run("ve publish plan")
        self.assertEqual(run("ve publish send --platform youtube --yes"), "ask")

    def test_init_and_revoke_ask(self):
        self.assertEqual(run("ve publish init bluesky"), "ask")
        self.assertEqual(run("ve publish revoke bluesky"), "ask")


if __name__ == "__main__":
    unittest.main()
