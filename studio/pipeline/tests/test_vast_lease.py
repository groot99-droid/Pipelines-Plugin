"""The remote branch: a GPU rented through the vast plugin, claimed by a run with `lease`.

A fake vast ledger is written into a temporary VAST_STATE_DIR. Nothing here calls Vast or reads a key.
"""

import json
import os
import time
import unittest
from unittest import mock

import yaml

from helpers import fixture_spec
import test_compute_gate

import vast_lease


class RemoteBranch(test_compute_gate.ExecuteNeedsAToken):
    """A local-compute pipeline that also offers a remote branch (`remote_gpu: optional`)."""

    def setUp(self):
        super().setUp()
        spec = fixture_spec()
        spec["pipelines"]["scene-3d"]["class"] = "local-compute"
        spec["pipelines"]["scene-3d"]["workload"] = "render_3d_cpu"
        spec["pipelines"]["scene-3d"]["remote_gpu"] = "optional"
        spec["pipelines"]["scene-3d"]["requires_context"] = []
        self.spec_path.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.vast_dir = self.root / "vast-state"
        self.vast_dir.mkdir()
        patch = mock.patch.dict(os.environ, {"VAST_STATE_DIR": str(self.vast_dir)})
        patch.start()
        self.addCleanup(patch.stop)

    def ledger(self, *rentals):
        (self.vast_dir / "state.json").write_text(json.dumps({"quotes": {}, "rentals": list(rentals), "tunnels": {}}),
                                                  encoding="utf-8")

    def rental(self, instance_id=9001, started=None, ended=None):
        started = time.time() if started is None else started
        return {"instance_id": instance_id, "dph": 0.25, "band": 1.0, "environment": "blender",
                "started": started, "deadline": started + 7200, "ended": ended}

    def test_the_branches_a_pipeline_offers(self):
        run_id = self.new_run(pipeline="scene-3d")
        code, _, err = self.run_cmd("branch", run_id, "cloud")
        self.assertEqual(code, 1)
        self.assertIn("no cloud branch", err)
        self.assertEqual(self.run_cmd("branch", run_id, "remote")[0], 0)
        self.assertEqual(self.run_cmd("branch", run_id, "local")[0], 0)

    def test_remote_needs_a_lease_claimed_after_the_go_ahead(self):
        run_id = self.to_execute()
        self.assertEqual(self.run_cmd("branch", run_id, "remote")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("claimed none", err)
        code, _, err = self.run_cmd("lease", run_id, "9001")
        self.assertEqual(code, 1)
        self.assertIn("no rental 9001", err)
        self.ledger(self.rental(started=time.time() - 3600))
        code, _, err = self.run_cmd("lease", run_id, "9001")
        self.assertEqual(code, 1)
        self.assertIn("before the execute go-ahead", err)
        self.ledger(self.rental(started=time.time(), ended=time.time()))
        code, _, err = self.run_cmd("lease", run_id, "9001")
        self.assertEqual(code, 1)
        self.assertIn("already ended", err)
        self.ledger(self.rental())
        self.assertEqual(self.run_cmd("lease", run_id, "9001")[0], 0)
        self.assertEqual(self.state(run_id)["lease"]["instance_id"], "9001")
        # destroying the instance after the work is fine: the ledger still records the rental
        self.ledger(self.rental(ended=time.time() + 1))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 0, err)

    def test_lease_needs_the_remote_branch_and_execute(self):
        run_id = self.new_run(pipeline="scene-3d")
        self.ledger(self.rental())
        code, _, err = self.run_cmd("lease", run_id, "9001")
        self.assertEqual(code, 1)
        self.assertIn("not on the remote branch", err)
        self.assertEqual(self.run_cmd("branch", run_id, "remote")[0], 0)
        code, _, err = self.run_cmd("lease", run_id, "9001")
        self.assertEqual(code, 1)
        self.assertIn("claimed at execute", err)

    def test_going_back_or_switching_branch_drops_the_lease(self):
        run_id = self.to_execute()
        self.assertEqual(self.run_cmd("branch", run_id, "remote")[0], 0)
        self.ledger(self.rental())
        self.assertEqual(self.run_cmd("lease", run_id, "9001")[0], 0)
        self.assertEqual(self.run_cmd("back", run_id, "--why", "change the layout")[0], 0)
        self.assertIsNone(self.state(run_id)["lease"])

    def test_without_a_branch_a_local_compute_run_still_needs_its_token(self):
        run_id = self.to_execute()
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("no live compute token", err)

    def test_the_reader_tolerates_no_ledger(self):
        self.assertEqual(vast_lease.rentals(), [])
        (self.vast_dir / "state.json").write_text("not json", encoding="utf-8")
        self.assertEqual(vast_lease.rentals(), [])
        self.assertIsNone(vast_lease.rental(1))


class SpecAgreesWithThePlugin(unittest.TestCase):
    def test_every_vast_tool_the_spec_names_is_the_plugins(self):
        import importlib.util
        from pathlib import Path

        repo = Path(__file__).resolve().parents[3]
        server_file = repo / "plugins" / "vast" / "server" / "server.py"
        loader = importlib.util.spec_from_file_location("vast_plugin_server", server_file)
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        spec = yaml.safe_load((repo / "studio" / "pipeline" / "spec.yaml").read_text(encoding="utf-8"))
        seen = 0
        for name, cfg in spec["pipelines"].items():
            tools = [t for t in (cfg.get("connector") or {}).get("tools", []) if t.startswith("mcp__vast__")]
            if cfg.get("remote_gpu"):
                self.assertEqual(cfg["remote_gpu"], "optional", name)
                self.assertTrue(tools, f"{name} has a remote branch and lists no vast tool")
            for tool in tools:
                seen += 1
                with self.subTest(pipeline=name, tool=tool):
                    self.assertIn(tool[len("mcp__vast__"):], module.TOOLS)
                    self.assertNotIn(tool, ("mcp__vast__run_shell", "mcp__vast__reap", "mcp__vast__stop"))
        self.assertGreater(seen, 0)


if __name__ == "__main__":
    unittest.main()
