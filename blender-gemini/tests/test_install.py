"""Tests for blender-gemini/install.py. They run on temporary folders, never touch the real
~/.gemini, start no server and open no socket to Blender."""

import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import install  # noqa: E402

TOOL = Path(install.__file__).resolve().parent
REPO = TOOL.parent
FAKE_KEY = "test-key-value-123"  # not a real key, and not shaped like one
OTHER_KEY = "other-test-value-456"


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.settings = self.tmp / ".gemini" / "settings.json"

    def read(self):
        return json.loads(self.settings.read_text(encoding="utf-8"))

    def seed(self, data):
        self.settings.parent.mkdir(parents=True)
        self.settings.write_text(json.dumps(data), encoding="utf-8")

    def test_creates_the_file_with_only_the_blender_server(self):
        status, previous = install.install(self.settings, install.server_entry())
        self.assertEqual((status, previous), ("added", None))
        self.assertEqual(list(self.read()), ["mcpServers"])
        self.assertEqual(list(self.read()["mcpServers"]), ["blender"])

    def test_merge_keeps_everything_else(self):
        self.seed({"theme": "dark", "mcpServers": {"other": {"command": "x"}}})
        install.install(self.settings, install.server_entry())
        data = self.read()
        self.assertEqual(data["theme"], "dark")
        self.assertEqual(data["mcpServers"]["other"], {"command": "x"})
        self.assertIn("blender", data["mcpServers"])

    def test_second_install_is_a_no_op_and_writes_no_second_backup(self):
        self.seed({"theme": "dark"})
        install.install(self.settings, install.server_entry())
        before = self.settings.read_text(encoding="utf-8")
        status, _ = install.install(self.settings, install.server_entry())
        self.assertEqual(status, "unchanged")
        self.assertEqual(self.settings.read_text(encoding="utf-8"), before)

    def test_first_backup_is_the_pre_install_file_and_is_never_overwritten(self):
        self.seed({"theme": "dark"})
        install.install(self.settings, install.server_entry("readonly"))
        install.install(self.settings, install.server_entry("full"))
        backup = self.settings.with_name("settings.json.rosw-bak")
        self.assertEqual(json.loads(backup.read_text(encoding="utf-8")), {"theme": "dark"})

    def test_a_different_existing_entry_is_reported_and_replaced(self):
        self.seed({"mcpServers": {"blender": {"command": "something-else"}}})
        status, previous = install.install(self.settings, install.server_entry())
        self.assertEqual(status, "updated")
        self.assertEqual(previous, {"command": "something-else"})
        self.assertEqual(self.read()["mcpServers"]["blender"]["command"], "uvx")

    def test_dry_run_writes_nothing(self):
        status, _ = install.install(self.settings, install.server_entry(), dry_run=True)
        self.assertEqual(status, "added")
        self.assertFalse(self.settings.exists())
        self.seed({"theme": "dark"})
        install.install(self.settings, install.server_entry(), dry_run=True)
        self.assertEqual(self.read(), {"theme": "dark"})
        self.assertFalse(self.settings.with_name("settings.json.rosw-bak").exists())

    def test_refuses_a_file_it_cannot_parse_and_leaves_it_alone(self):
        self.settings.parent.mkdir(parents=True)
        text = '{\n  // my notes\n  "theme": "dark"\n}\n'
        self.settings.write_text(text, encoding="utf-8")
        with self.assertRaises(install.SettingsError):
            install.install(self.settings, install.server_entry())
        self.assertEqual(self.settings.read_text(encoding="utf-8"), text)
        self.assertEqual(sorted(p.name for p in self.settings.parent.iterdir()), ["settings.json"])

    def test_refuses_the_wrong_shapes(self):
        for body in ('[1, 2]', '{"mcpServers": []}'):
            self.settings.parent.mkdir(parents=True, exist_ok=True)
            self.settings.write_text(body, encoding="utf-8")
            with self.assertRaises(install.SettingsError):
                install.install(self.settings, install.server_entry())
            self.assertEqual(self.settings.read_text(encoding="utf-8"), body)

    def test_a_utf8_bom_is_tolerated(self):
        self.settings.parent.mkdir(parents=True)
        self.settings.write_bytes(b"\xef\xbb\xbf" + json.dumps({"theme": "dark"}).encode())
        install.install(self.settings, install.server_entry())
        self.assertEqual(self.read()["theme"], "dark")

    def test_uninstall_removes_only_the_blender_server(self):
        self.seed({"theme": "dark", "mcpServers": {"other": {"command": "x"}}})
        install.install(self.settings, install.server_entry())
        self.assertEqual(install.uninstall(self.settings), "removed")
        self.assertEqual(self.read(), {"theme": "dark", "mcpServers": {"other": {"command": "x"}}})
        self.assertEqual(install.uninstall(self.settings), "absent")

    def test_uninstall_does_not_create_a_missing_file(self):
        self.assertEqual(install.uninstall(self.settings), "absent")
        self.assertFalse(self.settings.exists())

    def test_uninstall_dry_run_keeps_the_entry(self):
        install.install(self.settings, install.server_entry())
        self.assertEqual(install.uninstall(self.settings, dry_run=True), "removed")
        self.assertIn("blender", self.read()["mcpServers"])

    def test_settings_path(self):
        self.assertEqual(install.settings_path("user").parts[-2:], (".gemini", "settings.json"))
        self.assertEqual(install.settings_path("project"), Path.cwd() / ".gemini" / "settings.json")
        self.assertEqual(install.settings_path("user", override=str(self.settings)), self.settings)


class ProfileTest(unittest.TestCase):
    def test_readonly_exposes_only_the_read_tools_and_never_the_code_tool(self):
        entry = install.server_entry("readonly")
        self.assertEqual(entry["includeTools"], install.READ_ONLY_TOOLS)
        self.assertNotIn("execute_blender_code", entry["includeTools"])
        self.assertTrue(entry["trust"])
        self.assertNotIn("excludeTools", entry)

    def test_full_asks_unless_trust_is_given(self):
        self.assertFalse(install.server_entry("full")["trust"])
        self.assertTrue(install.server_entry("full", trust=True)["trust"])
        self.assertNotIn("includeTools", install.server_entry("full"))

    def test_the_feedback_tool_is_never_exposed(self):
        self.assertIn("record_trajectory_feedback", install.server_entry("full")["excludeTools"])
        self.assertNotIn("record_trajectory_feedback", install.server_entry("readonly")["includeTools"])

    def test_safe_mode_and_telemetry_settings(self):
        env = install.server_entry("full")["env"]
        self.assertEqual(env["BLENDER_MCP_SAFE_MODE"], "1")
        self.assertEqual(env["BLENDER_MCP_DISABLE_TELEMETRY"], "1")
        off = install.server_entry("full", safe_mode=False)["env"]
        self.assertNotIn("BLENDER_MCP_SAFE_MODE", off)
        self.assertEqual(off["BLENDER_MCP_DISABLE_TELEMETRY"], "1")

    def test_the_server_is_the_current_package_run_by_uvx(self):
        entry = install.server_entry()
        self.assertEqual((entry["command"], entry["args"]), ("uvx", ["mcp-for-blender"]))

    def test_unknown_profile_is_an_error(self):
        with self.assertRaises(ValueError):
            install.server_entry("everything")

    def test_trust_with_the_readonly_profile_is_refused_by_the_cli(self):
        self.assertEqual(install.main(["install", "--trust", "--dry-run", "--settings", "x.json"]), 2)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.settings = self.tmp / "settings.json"

    def test_install_check_uninstall_round_trip(self):
        argv = ["--settings", str(self.settings)]
        self.assertEqual(install.main(["install", *argv]), 0)
        self.assertIn("blender", json.loads(self.settings.read_text(encoding="utf-8"))["mcpServers"])
        self.assertEqual(install.main(["uninstall", *argv]), 0)
        self.assertEqual(json.loads(self.settings.read_text(encoding="utf-8")), {"mcpServers": {}})

    def test_a_refused_file_exits_2(self):
        self.settings.write_text("{not json", encoding="utf-8")
        self.assertEqual(install.main(["install", "--settings", str(self.settings)]), 2)
        self.assertEqual(self.settings.read_text(encoding="utf-8"), "{not json")


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.settings = self.tmp / "settings.json"
        install.install(self.settings, install.server_entry())

    def run_checks(self, **overrides):
        kwargs = dict(which=lambda name: f"/bin/{name}", probe=lambda host, port: True,
                      platform="linux", repo_root=REPO,
                      env={install.KEY_NAME: FAKE_KEY},
                      keys_file=self.tmp / "no-keys.env", gemini_env=self.tmp / "no-gemini.env")
        kwargs.update(overrides)
        return {label: (status, detail) for status, label, detail in
                install.run_checks(self.settings, **kwargs)}

    def test_everything_in_place_is_ready(self):
        rows = self.run_checks()
        self.assertEqual({s for s, _ in rows.values()}, {"ok"}, rows)

    def test_missing_config_names_the_fix(self):
        install.uninstall(self.settings)
        status, detail = self.run_checks()["gemini config"]
        self.assertEqual(status, "fail")
        self.assertIn("install.py install", detail)

    def test_an_unparsable_settings_file_fails_instead_of_raising(self):
        self.settings.write_text("{nope", encoding="utf-8")
        self.assertEqual(self.run_checks()["gemini config"][0], "fail")

    def test_a_missing_binary_fails(self):
        rows = self.run_checks(which=lambda name: None if name == "uvx" else f"/bin/{name}")
        self.assertEqual(rows["uvx"][0], "fail")
        self.assertEqual(rows["gemini"][0], "ok")

    def test_blender_not_listening_fails_and_says_how_to_start_it(self):
        status, detail = self.run_checks(probe=lambda host, port: False)["blender"]
        self.assertEqual(status, "fail")
        self.assertIn("Start MCP Server", detail)

    def test_the_probe_dials_the_servers_own_host_and_port(self):
        entry = install.server_entry()
        entry["env"]["BLENDER_PORT"] = "9999"
        install.install(self.settings, entry)
        seen = []
        self.run_checks(probe=lambda host, port: seen.append((host, port)) or True)
        self.assertEqual(seen, [("localhost", 9999)])

    def test_a_claude_config_without_the_backend_pin_fails(self):
        repo = self.tmp / "repo"
        repo.mkdir()
        (repo / ".mcp.json").write_text(json.dumps(
            {"mcpServers": {"gemini": {"command": "npx", "args": ["-y", "gemini-mcp-tool"]}}}), encoding="utf-8")
        status, detail = self.run_checks(repo_root=repo)["claude config"]
        self.assertEqual(status, "fail")
        self.assertIn("GEMINI_MCP_BACKEND", detail)

    def test_bare_npx_on_windows_is_a_warning_not_a_failure(self):
        self.assertEqual(self.run_checks(platform="win32")["claude config"][0], "warn")

    def test_check_command_reads_only(self):
        before = self.settings.read_text(encoding="utf-8")
        install.run_checks(self.settings, which=lambda n: None, probe=lambda h, p: False, repo_root=REPO,
                           env={}, keys_file=self.tmp / "a", gemini_env=self.tmp / "b")
        self.assertEqual(self.settings.read_text(encoding="utf-8"), before)
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["settings.json"])

    def test_key_row_by_where_the_key_is(self):
        gemini_env = self.tmp / "gemini.env"
        keys_file = self.tmp / "keys.env"
        none = {}
        self.assertEqual(self.run_checks(env=none)["gemini key"][0], "fail")
        keys_file.write_text(f"{install.KEY_NAME}={FAKE_KEY}\n", encoding="utf-8")
        status, detail = self.run_checks(env=none, keys_file=keys_file, gemini_env=gemini_env)["gemini key"]
        self.assertEqual(status, "fail")
        self.assertIn("sync-key", detail)  # the fix is named
        gemini_env.write_text(f"{install.KEY_NAME}={FAKE_KEY}\n", encoding="utf-8")
        self.assertEqual(self.run_checks(env=none, keys_file=keys_file, gemini_env=gemini_env)["gemini key"][0], "ok")
        self.assertEqual(self.run_checks()["gemini key"][0], "ok")  # the environment alone is enough

    def test_a_placeholder_key_does_not_count(self):
        keys_file = self.tmp / "keys.env"
        keys_file.write_text(f"{install.KEY_NAME}=your-key-here\n", encoding="utf-8")
        status, detail = self.run_checks(env={}, keys_file=keys_file)["gemini key"]
        self.assertEqual(status, "fail")
        self.assertIn("not set", detail)

    def test_the_key_value_never_appears_in_any_row(self):
        keys_file = self.tmp / "keys.env"
        gemini_env = self.tmp / "gemini.env"
        for path in (keys_file, gemini_env):
            path.write_text(f"{install.KEY_NAME}={FAKE_KEY}\n", encoding="utf-8")
        for env in ({}, {install.KEY_NAME: FAKE_KEY}):
            rows = install.run_checks(self.settings, which=lambda n: f"/bin/{n}", probe=lambda h, p: True,
                                      repo_root=REPO, env=env, keys_file=keys_file, gemini_env=gemini_env)
            self.assertNotIn(FAKE_KEY, json.dumps(rows))


def run_main(argv):
    """(exit code, stdout, stderr) of install.main(argv)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = install.main(argv)
    return code, out.getvalue(), err.getvalue()


class SyncKeyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.source = self.tmp / "keys.env"
        self.target = self.tmp / "home" / ".gemini" / ".env"
        self.source.write_text(f"# ROSW keys\nANTHROPIC_API_KEY=unrelated-test-value\n"
                               f"{install.KEY_NAME}={FAKE_KEY}\n", encoding="utf-8")

    def argv(self, *extra):
        return ["sync-key", "--keys-file", str(self.source), "--env-file", str(self.target), *extra]

    def text(self):
        return self.target.read_text(encoding="utf-8")

    def test_copies_only_the_gemini_key_and_creates_the_folder(self):
        code, out, err = run_main(self.argv())
        self.assertEqual(code, 0, err)
        self.assertEqual(self.text(), f"{install.KEY_NAME}={FAKE_KEY}\n")
        self.assertNotIn("unrelated-test-value", self.text())  # no other key travels with it

    def test_nothing_printed_holds_the_value(self):
        for argv in (self.argv(), self.argv(), self.argv("--dry-run"), self.argv("--remove")):
            _, out, err = run_main(argv)
            self.assertNotIn(FAKE_KEY, out + err)
        self.assertIn(install.KEY_NAME, out)  # it names the key, which is fine

    def test_every_other_line_is_kept_and_the_key_line_keeps_its_place(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text(f"FIRST=1\n{install.KEY_NAME}=old-value\nLAST=2\n", encoding="utf-8")
        run_main(self.argv())
        self.assertEqual(self.text(), f"FIRST=1\n{install.KEY_NAME}={FAKE_KEY}\nLAST=2\n")

    def test_status_added_updated_unchanged(self):
        self.assertEqual(install.sync_key(self.source, self.target), "added")
        self.assertEqual(install.sync_key(self.source, self.target), "unchanged")
        self.target.write_text(f"{install.KEY_NAME}={OTHER_KEY}\n", encoding="utf-8")
        self.assertEqual(install.sync_key(self.source, self.target), "updated")
        self.assertEqual(install.read_key(self.target), FAKE_KEY)

    def test_an_export_line_and_duplicates_are_replaced_by_one_line(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text(f"export {install.KEY_NAME}=a1\nX=1\n{install.KEY_NAME}=a2\n", encoding="utf-8")
        install.sync_key(self.source, self.target)
        self.assertEqual(self.text(), f"{install.KEY_NAME}={FAKE_KEY}\nX=1\n")

    def test_no_backup_is_left_because_it_would_be_a_second_copy(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text(f"{install.KEY_NAME}={OTHER_KEY}\n", encoding="utf-8")
        install.sync_key(self.source, self.target)
        self.assertEqual([p.name for p in self.target.parent.iterdir()], [".env"])

    @unittest.skipIf(os.name == "nt", "POSIX modes")
    def test_the_file_is_mode_600_even_if_it_was_wider(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("X=1\n", encoding="utf-8")
        os.chmod(self.target, 0o644)
        install.sync_key(self.source, self.target)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)

    def test_refuses_when_the_source_has_no_key_and_writes_nothing(self):
        self.source.write_text("ANTHROPIC_API_KEY=unrelated-test-value\n", encoding="utf-8")
        code, _, err = run_main(self.argv())
        self.assertEqual(code, 2)
        self.assertIn("setup_keys.py", err)
        self.assertFalse(self.target.exists())

    def test_refuses_a_missing_source_and_a_placeholder(self):
        for body in (None, f"{install.KEY_NAME}=your-key-here\n", f"{install.KEY_NAME}=\n"):
            if body is None:
                self.source.unlink()
            else:
                self.source.write_text(body, encoding="utf-8")
            self.assertEqual(run_main(self.argv())[0], 2)
        self.assertFalse(self.target.exists())

    def test_refuses_a_value_a_dotenv_parser_could_misread_without_echoing_it(self):
        for bad in ("has space", "quote\"d", "hash#tag", "dollar$sign", "back\\slash"):
            self.source.write_text(f'{install.KEY_NAME}="{bad}"\n', encoding="utf-8")
            code, out, err = run_main(self.argv())
            self.assertEqual(code, 2, bad)
            self.assertNotIn(bad, out + err)
        self.assertFalse(self.target.exists())

    def test_dry_run_writes_nothing(self):
        code, out, _ = run_main(self.argv("--dry-run"))
        self.assertEqual(code, 0)
        self.assertIn("added", out)
        self.assertFalse(self.target.exists())

    def test_remove_takes_out_only_the_key_line(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text(f"A=1\n{install.KEY_NAME}={FAKE_KEY}\nB=2\n", encoding="utf-8")
        self.assertEqual(install.sync_key(self.source, self.target, remove=True), "removed")
        self.assertEqual(self.text(), "A=1\nB=2\n")
        self.assertEqual(install.sync_key(self.source, self.target, remove=True), "absent")

    def test_remove_does_not_need_the_source_and_does_not_create_a_file(self):
        self.source.unlink()
        self.assertEqual(install.sync_key(self.source, self.target, remove=True), "absent")
        self.assertFalse(self.target.exists())

    def test_the_default_paths(self):
        self.assertEqual(install.gemini_env_file().parts[-2:], (".gemini", ".env"))
        self.assertEqual(install.rosw_keys_file().parts[-2:], (".rosw", "keys.env"))


class RepoAgreementTest(unittest.TestCase):
    """The pieces that live outside install.py have to agree with it."""

    def test_mcp_json_registers_the_gemini_server_on_the_gemini_backend(self):
        config = json.loads((REPO / ".mcp.json").read_text(encoding="utf-8"))
        gemini = config["mcpServers"]["gemini"]
        self.assertEqual(gemini["args"], ["-y", "gemini-mcp-tool"])
        self.assertEqual(gemini["env"]["GEMINI_MCP_BACKEND"], "gemini")
        self.assertEqual(list(config["mcpServers"]), ["gemini"])

    def test_the_skill_names_the_tool_the_mcp_json_server_exposes(self):
        text = (REPO / ".claude" / "skills" / "blender-gemini" / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S).group(1)
        self.assertIn("name: blender-gemini", front)
        self.assertIn("description:", front)
        self.assertIn("mcp__gemini__ask-gemini", text)
        self.assertIn("blender-gemini/install.py check", text)
        self.assertIn("sync-key", text)
        flat = " ".join(text.lower().split())  # the prose is hard-wrapped
        self.assertIn("never read, print or ask for a key value", flat)  # Claude does not handle keys

    def test_the_readme_lists_every_read_only_tool_and_the_package(self):
        text = (TOOL / "README.md").read_text(encoding="utf-8")
        for name in install.READ_ONLY_TOOLS + [install.PACKAGE, "sync-key", install.KEY_NAME, "~/.gemini/.env"]:
            self.assertIn(name, text)

    def test_key_handling_agrees_with_the_keys_page_helper(self):
        spec = importlib.util.spec_from_file_location("rosw_setup_keys", REPO / "docs" / "setup_keys.py")
        setup_keys = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup_keys)
        self.assertIn(install.KEY_NAME, setup_keys.KEYS)  # the keys page can set it
        self.assertEqual(install.KEY_PLACEHOLDERS, setup_keys.PLACEHOLDERS)
        with mock.patch.dict(os.environ):
            os.environ.pop("ROSW_KEYS_FILE", None)
            self.assertEqual(install.rosw_keys_file(), setup_keys.keys_file())
            os.environ["ROSW_KEYS_FILE"] = str(Path(tempfile.gettempdir()) / "elsewhere.env")
            self.assertEqual(install.rosw_keys_file(), setup_keys.keys_file())
        tmp = Path(tempfile.mkdtemp())
        samples = {
            "plain": [f"{install.KEY_NAME}={FAKE_KEY}"],
            "quoted": [f'{install.KEY_NAME}="{FAKE_KEY}"', "OTHER=1"],
            "last wins": [f"{install.KEY_NAME}={OTHER_KEY}", f"{install.KEY_NAME}={FAKE_KEY}"],
            "placeholder": [f"{install.KEY_NAME}=your-key-here"],
            "empty": [f"{install.KEY_NAME}="],
            "commented": [f"# {install.KEY_NAME}={FAKE_KEY}"],
            "absent": ["OTHER=1"],
        }
        for label, lines in samples.items():
            path = tmp / f"{label.replace(' ', '-')}.env"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(install.read_key(path), setup_keys.parse(lines).get(install.KEY_NAME), label)

    def test_no_secret_shaped_values_in_what_install_writes(self):
        blob = json.dumps([install.server_entry(p, trust=True) for p in install.PROFILES])
        self.assertIsNone(re.search(r"(?i)api[_-]?key|token|secret|password", blob))


if __name__ == "__main__":
    unittest.main()
