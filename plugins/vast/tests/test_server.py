"""Tests for the vast MCP server: a fake Vast API on 127.0.0.1, fake ssh/scp, an injected clock.

Nothing here reaches the network or a real account, and no real key is used.
"""

from __future__ import annotations

import json
import os
import socket
import stat
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "server"))
sys.path.insert(0, str(HERE))

import ledger as ledger_mod  # noqa: E402
import remote as remote_mod  # noqa: E402
import server  # noqa: E402
import vast_api  # noqa: E402
from fake_vast import FAKE_KEY, FakeVast  # noqa: E402

DAY = 86400.0
HOUR = 3600.0


class Clock:
    def __init__(self, now=1_800_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


class FakeRun:
    """Stands in for subprocess.run: records argv and answers like a shell would."""

    def __init__(self):
        self.calls = []
        self.answer = (0, "ok\n", "")

    def __call__(self, argv, capture_output=True, text=True, timeout=None):
        self.calls.append(argv)
        code, out, err = self.answer
        if argv and Path(argv[0]).stem.lower() == "scp" and not str(argv[-1]).startswith("root@"):
            Path(argv[-1]).write_bytes(b"rendered bytes")   # a download lands a file
        return type("Done", (), {"returncode": code, "stdout": out, "stderr": err})()


class FakePopen:
    pid = 424242

    def __init__(self, argv, **kwargs):
        FakePopen.last = argv


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.fake = FakeVast()
        url = self.fake.start()
        self.addCleanup(self.fake.stop)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        for name in ("ssh", "scp"):  # found on PATH; FakeRun answers in their place
            if os.name == "nt":
                (bin_dir / (name + ".bat")).write_text("@exit /b 0\r\n")
            else:
                shim = bin_dir / name
                shim.write_text("#!/bin/sh\nexit 0\n")
                shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
        (root / "home" / ".ssh").mkdir(parents=True)
        (root / "home" / ".ssh" / "id_ed25519").write_text("PRIVATE KEY MATERIAL\n")
        (root / "home" / ".ssh" / "id_ed25519.pub").write_text("ssh-ed25519 AAAAC3fakefakefake test\n")
        (root / "work").mkdir()
        self.environ = {
            "HOME": str(root / "home"), "PATH": str(bin_dir), "VAST_API_KEY": FAKE_KEY, "VAST_BASE_URL": url,
            "VAST_STATE_DIR": str(root / "state"), "VAST_WORK_DIR": str(root / "work"),
        }
        self.root = root
        self.clock = Clock()
        self.run = FakeRun()
        self.context = server.make_context(self.environ, clock=self.clock, sleep=lambda s: None,
                                           runner=self.run, popen=FakePopen)

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, name, arguments=None):
        reply = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                 "params": {"name": name, "arguments": arguments or {}}}, self.context)
        result = reply["result"]
        payload = json.loads(result["content"][0]["text"])
        return result["isError"], payload

    def ok(self, name, arguments=None):
        is_error, payload = self.call(name, arguments)
        self.assertFalse(is_error, payload)
        return payload

    def refused(self, name, arguments, code):
        is_error, payload = self.call(name, arguments)
        self.assertTrue(is_error, payload)
        self.assertEqual(payload["error"]["code"], code, payload)
        return payload

    def rent(self, offer_id=101, hours=2, environment="blender"):
        quote = self.ok("quote", {"offer_id": offer_id, "environment": environment, "hours": hours})
        rented = self.ok("rent", {"quote_id": quote["quote_id"], "confirm": True})
        return quote, rented


class ProtocolTests(Base):
    def test_handshake_and_list(self):
        hello = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                 "params": {"protocolVersion": "2025-06-18"}}, self.context)
        self.assertEqual(hello["result"]["protocolVersion"], "2025-06-18")
        listed = server.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, self.context)
        names = {tool["name"] for tool in listed["result"]["tools"]}
        self.assertTrue({"quote", "rent", "destroy", "run_recipe", "run_shell", "tunnel"} <= names)
        rent = next(t for t in listed["result"]["tools"] if t["name"] == "rent")
        self.assertTrue(rent["annotations"]["destructiveHint"])

    def test_bad_arguments_and_unknown_tool(self):
        self.refused("quote", {"offer_id": "x", "environment": "base", "hours": 1}, "bad_argument")
        reply = server.dispatch({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                 "params": {"name": "nope"}}, self.context)
        self.assertEqual(reply["error"]["code"], server.INVALID_PARAMS)
        self.assertIn(b"-32700", server.handle_line(b"{not json", self.context))

    def test_notification_gets_no_reply(self):
        self.assertIsNone(server.dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}, self.context))


class BudgetTests(Base):
    def test_bands(self):
        ledger = self.context.ledger
        self.assertEqual(ledger.band_for(0.25)["max_dph"], 1.0)
        self.assertEqual(ledger.band_for(1.0)["max_dph"], 1.0)
        self.assertEqual(ledger.band_for(1.2)["hours"], 50)
        self.assertEqual(ledger.band_for(9.99)["hours"], 4)
        self.assertIsNone(ledger.band_for(12.0))

    def test_over_ceiling_refused(self):
        self.refused("quote", {"offer_id": 303, "environment": "base", "hours": 1}, "over_ceiling")

    def test_quote_caps_to_band_and_reserves(self):
        quote = self.ok("quote", {"offer_id": 202, "environment": "base", "hours": 80})
        self.assertEqual(quote["cap_hours"], 50)
        self.assertTrue(quote["capped"])
        self.ok("rent", {"quote_id": quote["quote_id"], "confirm": True})
        # the whole 50 h are reserved while it lives
        self.refused("quote", {"offer_id": 202, "environment": "base", "hours": 1}, "band_spent")
        # the cheaper band is untouched
        self.ok("quote", {"offer_id": 101, "environment": "base", "hours": 1})

    def test_rolling_window_frees_hours(self):
        _, rented = self.rent(offer_id=202, hours=50)
        self.clock.now += 10 * HOUR
        self.ok("destroy", {"instance_id": rented["instance_id"], "confirm": True})
        usage = {row["max_dph"]: row for row in self.context.ledger.band_usage()}
        self.assertAlmostEqual(usage[1.5]["counted_hours"], 10, places=1)
        self.assertAlmostEqual(usage[1.5]["remaining_hours"], 40, places=1)
        self.clock.now += 14 * DAY + HOUR
        usage = {row["max_dph"]: row for row in self.context.ledger.band_usage()}
        self.assertEqual(usage[1.5]["remaining_hours"], 50)

    def test_spend_block_on_every_result(self):
        self.rent()
        payload = self.ok("instances")
        self.assertEqual(len(payload["spend"]["live"]), 1)
        self.assertEqual(len(payload["spend"]["bands"]), 5)


class RentTests(Base):
    def test_rent_without_confirm_is_a_dry_run(self):
        quote = self.ok("quote", {"offer_id": 101, "environment": "base", "hours": 1})
        dry = self.ok("rent", {"quote_id": quote["quote_id"]})
        self.assertTrue(dry["dry_run"])
        self.assertFalse(any(r["path"].startswith("/api/v0/asks/") for r in self.fake.requests))

    def test_rent_records_and_sends_watchdog(self):
        quote, rented = self.rent(hours=2)
        instance = self.fake.instances[rented["instance_id"]]
        self.assertIn("sleep 7200;", instance["onstart"])
        self.assertIn("$CONTAINER_ID", instance["onstart"])
        self.assertIn("blender-4.2.3-linux-x64.tar.xz", instance["onstart"])
        self.assertEqual(instance["label"], "claude-vast-" + quote["quote_id"])
        rental = self.context.ledger.rental(rented["instance_id"])
        self.assertEqual(rental["deadline"] - rental["started"], 2 * HOUR)

    def test_quote_used_once(self):
        quote, _ = self.rent()
        self.refused("rent", {"quote_id": quote["quote_id"], "confirm": True}, "bad_quote")

    def test_stale_quote_refused(self):
        quote = self.ok("quote", {"offer_id": 101, "environment": "base", "hours": 1})
        self.clock.now += 16 * 60
        self.refused("rent", {"quote_id": quote["quote_id"], "confirm": True}, "bad_quote")

    def test_price_rise_refused(self):
        quote = self.ok("quote", {"offer_id": 101, "environment": "base", "hours": 1})
        self.fake.offers[0]["dph_total"] = 0.40
        self.refused("rent", {"quote_id": quote["quote_id"], "confirm": True}, "price_changed")

    def test_destroy_needs_confirm(self):
        _, rented = self.rent()
        dry = self.ok("destroy", {"instance_id": rented["instance_id"]})
        self.assertTrue(dry["dry_run"])
        self.assertIn(rented["instance_id"], self.fake.instances)
        self.ok("destroy", {"instance_id": rented["instance_id"], "confirm": True})
        self.assertNotIn(rented["instance_id"], self.fake.instances)
        self.assertIsNotNone(self.context.ledger.rental(rented["instance_id"])["ended"])

    def test_instances_settles_stopped_and_gone(self):
        _, first = self.rent()
        _, second = self.rent()
        self.fake.instances[first["instance_id"]]["actual_status"] = "stopped"
        del self.fake.instances[second["instance_id"]]
        self.ok("instances")
        self.assertEqual(self.context.ledger.rental(first["instance_id"])["ended_how"], "observed_stopped")
        self.assertEqual(self.context.ledger.rental(second["instance_id"])["ended_how"], "gone")

    def test_reap(self):
        _, rented = self.rent(hours=1)
        self.assertEqual(self.ok("reap")["would_destroy"], [])
        self.clock.now += 2 * HOUR
        self.assertEqual(self.ok("reap")["would_destroy"], [rented["instance_id"]])
        self.assertEqual(self.ok("reap", {"confirm": True})["destroyed"], [rented["instance_id"]])


class KeyTests(Base):
    def test_key_never_leaves_in_output_or_state(self):
        _, rented = self.rent()
        texts = [json.dumps(self.ok(name)) for name in ("account", "instances", "list_recipes")]
        texts.append(json.dumps(self.ok("search_offers")))
        for path in Path(self.environ["VAST_STATE_DIR"]).iterdir():
            texts.append(path.read_text(encoding="utf-8"))
        joined = "\n".join(texts)
        self.assertNotIn(FAKE_KEY, joined)
        self.assertNotIn("PRIVATE KEY MATERIAL", joined)
        self.assertNotIn("someone@example.com", joined)
        self.assertTrue(all(r["auth"] == "Bearer " + FAKE_KEY for r in self.fake.requests))

    def test_no_key(self):
        environ = {k: v for k, v in self.environ.items() if k != "VAST_API_KEY"}
        context = server.make_context(environ, clock=self.clock)
        self.context = context
        self.assertEqual(self.ok("account")["key"], "not set")
        self.refused("search_offers", {}, "no_key")

    def test_key_sources(self):
        keys = self.root / "keys.env"
        keys.write_text("OTHER=1\nVAST_API_KEY=from-file-value\n")
        self.assertEqual(vast_api.api_key({"VAST_KEYS_FILE": str(keys), "HOME": str(self.root)}), "from-file-value")
        self.assertEqual(vast_api.api_key({"VAST_KEYS_FILE": "~/keys.env", "HOME": str(self.root)}), "from-file-value")
        cli = self.root / "home" / ".config" / "vastai"
        cli.mkdir(parents=True)
        (cli / "vast_api_key").write_text("from-cli\n")
        self.assertEqual(vast_api.api_key({"HOME": str(self.root / "home")}), "from-cli")
        self.assertEqual(vast_api.api_key({"VAST_API_KEY": "your-key-here", "HOME": str(self.root / "home")}), "from-cli")

    def test_base_url_must_be_https_or_local(self):
        with self.assertRaises(vast_api.VastError):
            vast_api.base_url({"VAST_BASE_URL": "http://example.com/api"})
        self.assertEqual(vast_api.base_url({}), vast_api.DEFAULT_BASE_URL)


class RecipeTests(Base):
    def test_injection_stays_literal(self):
        recipes = self.context.recipes
        command, background = remote_mod.render(
            "blender_script", {"script": "assemble.py", "args": ["--layout", "x; rm -rf /", "{script}"]}, recipes)
        self.assertTrue(background)
        self.assertIn("'x; rm -rf /'", command)
        self.assertIn("'{script}'", command)
        self.assertIn("/workspace/job/assemble.py", command)

    def test_paths_cannot_climb(self):
        for bad in ("../etc/passwd", "/etc/passwd", "a/../../b", "a b"):
            with self.assertRaises(vast_api.VastError):
                remote_mod.render("blender_render", {"blend": bad, "output": "out/f_####"}, self.context.recipes)

    def test_unknown_and_missing_params(self):
        with self.assertRaises(vast_api.VastError):
            remote_mod.render("gpu_info", {"x": 1}, self.context.recipes)
        with self.assertRaises(vast_api.VastError):
            remote_mod.render("comfy_install_node", {"repo": "https://github.com/a/b"}, self.context.recipes)
        with self.assertRaises(vast_api.VastError):
            remote_mod.render("comfy_install_node", {"repo": "https://evil.example/a/b", "name": "n", "ref": "main"},
                              self.context.recipes)

    def test_every_recipe_names_a_known_environment(self):
        recipes = self.context.recipes
        for name, recipe in recipes["recipes"].items():
            self.assertIn(recipe.get("environment", "base"), recipes["environments"], name)

    def test_run_recipe_foreground_and_background(self):
        _, rented = self.rent()
        result = self.ok("run_recipe", {"instance_id": rented["instance_id"], "recipe": "gpu_info"})
        self.assertEqual(result["exit_code"], 0)
        argv = self.run.calls[-1]
        self.assertIn("BatchMode=yes", argv)
        self.assertIn("StrictHostKeyChecking=accept-new", argv)
        self.assertTrue(any(a.startswith("UserKnownHostsFile=") for a in argv))
        started = self.ok("run_recipe", {"instance_id": rented["instance_id"], "recipe": "blender_render",
                                         "arguments": {"blend": "scene.blend", "output": "render/f_####"}})
        self.assertRegex(started["job_id"], r"^j_[0-9a-f]{8}$")
        self.assertIn("nohup bash -c", self.run.calls[-1][-1])
        self.run.answer = (0, "STATE done 0\nSaved: render/f_0001.png\n", "")
        status = self.ok("job_status", {"instance_id": rented["instance_id"], "job_id": started["job_id"]})
        self.assertEqual(status["state"], "done")
        self.assertEqual(status["exit_code"], 0)

    def test_wrong_environment_refused(self):
        _, rented = self.rent(environment="base")
        self.refused("run_recipe", {"instance_id": rented["instance_id"], "recipe": "comfy_start"}, "wrong_environment")

    def test_run_shell_needs_confirm(self):
        _, rented = self.rent()
        before = len(self.run.calls)
        dry = self.ok("run_shell", {"instance_id": rented["instance_id"], "command": "ls"})
        self.assertTrue(dry["dry_run"])
        self.assertEqual(len(self.run.calls), before)
        self.ok("run_shell", {"instance_id": rented["instance_id"], "command": "ls", "confirm": True})
        events = (Path(self.environ["VAST_STATE_DIR"]) / "events.jsonl").read_text()
        self.assertIn('"command": "ls"', events)


class FileAndTunnelTests(Base):
    def test_upload_download_stay_in_work_dir(self):
        _, rented = self.rent()
        (self.root / "work" / "scene.blend").write_bytes(b"blend")
        up = self.ok("upload", {"instance_id": rented["instance_id"], "local": "scene.blend", "remote": "scene.blend"})
        self.assertEqual(len(up["sha256"]), 64)
        self.refused("upload", {"instance_id": rented["instance_id"], "local": "../home/.ssh/id_ed25519",
                                "remote": "k"}, "outside_work_dir")
        self.refused("download", {"instance_id": rented["instance_id"], "remote": "../../root/x", "local": "x"},
                     "bad_path")
        down = self.ok("download", {"instance_id": rented["instance_id"], "remote": "render/f_0001.png",
                                    "local": "out/f_0001.png"})
        self.assertEqual(down["bytes"], len(b"rendered bytes"))

    def test_tunnel_open_close(self):
        _, rented = self.rent(environment="comfy")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            free_port = probe.getsockname()[1]
        opened = self.ok("tunnel", {"action": "open", "instance_id": rented["instance_id"], "local_port": free_port})
        self.assertEqual(opened["local"], f"http://127.0.0.1:{free_port}")
        self.assertIn(f"127.0.0.1:{free_port}:127.0.0.1:8188", FakePopen.last)
        self.refused("tunnel", {"action": "open", "instance_id": rented["instance_id"], "local_port": free_port},
                     "port_taken")
        self.assertIn(str(free_port), self.ok("tunnel", {"action": "list"})["tunnels"])
        self.assertTrue(self.ok("tunnel", {"action": "close", "local_port": free_port})["closed"])
        self.assertEqual(self.ok("tunnel", {"action": "list"})["tunnels"], {})


class LimitsFileTests(unittest.TestCase):
    def test_limits_are_the_authors(self):
        limits = ledger_mod.load_limits()
        self.assertEqual(limits["window_days"], 14)
        self.assertEqual([(b["max_dph"], b["hours"]) for b in limits["bands"]],
                         [(1.0, 100), (1.5, 50), (2.5, 30), (5.0, 10), (10.0, 4)])


if __name__ == "__main__":
    unittest.main()
