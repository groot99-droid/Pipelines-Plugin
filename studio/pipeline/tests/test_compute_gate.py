"""The compute gate: verdicts pinned against machine.yaml, the token's life,
and the execute check a local-compute pipeline must pass.

The ten verdict cases are the ones Creative-Headquarters' test_gate.py pinned,
re-stated against a probe of this shape. The three defects that gate had are
each pinned by a test here: a denial never overwrites a live token, a re-mint
keeps who holds it, and no test touches a real token (the token lives under
the temporary run folder).
"""

import copy
import json
import time
import unittest

import yaml

from helpers import StudioCase, fixture_spec

import compute_gate

HEALTHY = {
    "host": {"name": "YOGA", "kind": "windows", "machine": "Yoga Book 9 14IMU9"},
    "gpu": {"status": "integrated", "name": "Intel Arc Graphics", "vram_total_gb": None, "memory_shared_with_system": True},
    "memory": {"total_gb": 16, "available_gb": 11, "free_pct": 68, "swap_used_mb": 1800, "dynamic_claim_limit_gb": 6},
    "power": {"source": "ac", "battery_pct": 88},
    "thermal": {"cpu_temp_c": None, "cpu_perf_pct": 94},
    "disk": {"free_gb": 180, "system_free_gb": 180},
}


def probe(**changes):
    found = copy.deepcopy(HEALTHY)
    for dotted, value in changes.items():
        block, key = dotted.split(".")
        found[block][key] = value
    found["ts_epoch"] = int(time.time())
    return found


class GateCase(StudioCase):
    def setUp(self):
        super().setUp()
        self.machine = compute_gate.load_machine()

    def gate(self, *arguments):
        return self.call(compute_gate, *arguments)

    def probe_file(self, name="probe.json", **changes):
        path = self.root / name
        path.write_text(json.dumps(probe(**changes)), encoding="utf-8")
        return path

    def verdict(self, workload, **changes):
        return compute_gate.evaluate(self.machine, probe(**changes), workload)["verdict"]


class Verdicts(GateCase):
    def test_the_ten_pinned_cases(self):
        cases = [
            ("healthy", "llm_local_sm", {}, "PASS"),
            ("one readable thermal reading", "render_3d_cpu", {}, "PASS"),
            ("both thermal readings null", "llm_local_sm", {"thermal.cpu_perf_pct": None}, "DENY"),
            ("battery", "render_3d_cpu", {"power.source": "battery"}, "DENY"),
            ("battery is fine for the small model", "llm_local_sm", {"power.source": "battery"}, "PASS"),
            ("throttling", "render_3d_cpu", {"thermal.cpu_temp_c": 91, "thermal.cpu_perf_pct": 58}, "DENY"),
            ("low memory", "llm_local_md", {"memory.available_gb": 4, "memory.free_pct": 25, "memory.swap_used_mb": 7000}, "DENY"),
            ("discrete GPU", "render_3d_cpu", {"gpu.status": "discrete", "gpu.name": "RTX 4070"}, "DENY"),
            ("macOS", "llm_local_sm", {"host.kind": "macos"}, "DENY"),
        ]
        for label, workload, changes, want in cases:
            with self.subTest(case=label):
                self.assertEqual(self.verdict(workload, **changes), want)
        # the tenth: a live token for another class blocks a mint
        self.assertEqual(self.gate("mint", "llm_local_sm", "--probe", self.probe_file())[0], 0)
        code, out, _ = self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())
        self.assertEqual(code, 1)
        self.assertIn("a live llm_local_sm token", out)

    def test_an_unreadable_metric_closes_the_gate_with_its_remedy(self):
        found = compute_gate.evaluate(self.machine, probe(**{"power.source": None}), "render_3d_cpu")
        self.assertEqual(found["verdict"], "DENY")
        self.assertIn("power.source is unreadable", found["reasons"][0])
        self.assertIn(self.machine["remedies"]["power.source"], found["remedies"])

    def test_evaluate_writes_nothing_and_all_surveys_every_class(self):
        code, out, _ = self.gate("evaluate", "--all", "--probe", self.probe_file(**{"power.source": "battery"}))
        self.assertEqual(code, 1)
        for name in self.machine["classes"]:
            self.assertIn(name, out)
        self.assertFalse(compute_gate.token_path(self.env, self.machine).exists())

    def test_an_unknown_class_is_a_usage_error(self):
        code, _, err = self.gate("evaluate", "render_gpu", "--probe", self.probe_file())
        self.assertEqual(code, 2)
        self.assertIn("no class", err)


class Token(GateCase):
    def test_a_denial_never_overwrites_a_live_token(self):
        self.assertEqual(self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())[0], 0)
        before = compute_gate.token_path(self.env, self.machine).read_text(encoding="utf-8")
        code, out, _ = self.gate("mint", "render_3d_cpu", "--probe", self.probe_file(**{"power.source": "battery"}))
        self.assertEqual(code, 1)
        self.assertIn("untouched", out)
        self.assertEqual(compute_gate.token_path(self.env, self.machine).read_text(encoding="utf-8"), before)
        code, _, _ = self.gate("mint", "llm_local_md", "--probe", self.probe_file())
        self.assertEqual(code, 1)  # single flight
        self.assertEqual(compute_gate.token_path(self.env, self.machine).read_text(encoding="utf-8"), before)

    def test_a_re_mint_refreshes_the_ttl_and_keeps_the_holder(self):
        self.assertEqual(self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())[0], 0)
        self.assertEqual(self.gate("consume", "scene-000001")[0], 0)
        first = compute_gate.load_token(self.env, self.machine)
        time.sleep(0.01)
        code, out, _ = self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())
        self.assertEqual(code, 0)
        self.assertIn("held by scene-000001", out)
        again = compute_gate.load_token(self.env, self.machine)
        self.assertEqual(again["consumed_by"], "scene-000001")
        self.assertGreater(again["ts_epoch"], first["ts_epoch"])

    def test_consume_is_one_run_at_a_time(self):
        code, _, err = self.gate("consume", "scene-000001")
        self.assertEqual(code, 1)
        self.assertIn("no live PASS token", err)
        self.assertEqual(self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())[0], 0)
        self.assertEqual(self.gate("consume", "scene-000001")[0], 0)
        self.assertEqual(self.gate("consume", "scene-000001")[0], 0)
        code, _, err = self.gate("consume", "scene-000002")
        self.assertEqual(code, 1)
        self.assertIn("held by run `scene-000001`", err)

    def test_an_expired_token_is_no_token(self):
        self.assertEqual(self.gate("mint", "llm_local_sm", "--probe", self.probe_file())[0], 0)
        path = compute_gate.token_path(self.env, self.machine)
        token = json.loads(path.read_text(encoding="utf-8"))
        token["ts_epoch"] -= token["ttl_seconds"] + 1
        path.write_text(json.dumps(token), encoding="utf-8")
        code, out, _ = self.gate("status")
        self.assertIn("expired", out)
        self.assertEqual(self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())[0], 0)
        self.assertEqual(self.gate("release")[0], 0)
        self.assertFalse(path.exists())

    def test_force_overrides_with_a_warning(self):
        self.assertEqual(self.gate("mint", "llm_local_sm", "--probe", self.probe_file())[0], 0)
        code, _, err = self.gate("mint", "render_3d_cpu", "--probe", self.probe_file(), "--force")
        self.assertEqual(code, 0)
        self.assertIn("overrides a live token", err)

    def test_the_token_lives_under_the_run_folder_and_nowhere_else(self):
        self.assertEqual(compute_gate.token_path(self.env, self.machine).parent, self.runs.resolve())
        self.assertNotEqual(self.runs, compute_gate.HERE / "runs")


class ExecuteNeedsAToken(StudioCase):
    """A local-compute pipeline in the fixture spec."""

    def setUp(self):
        super().setUp()
        spec = fixture_spec()
        spec["pipelines"]["scene-3d"]["class"] = "local-compute"
        spec["pipelines"]["scene-3d"]["workload"] = "render_3d_cpu"
        spec["pipelines"]["scene-3d"]["requires_context"] = []
        self.spec_path.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.env = self.env.__class__(self.spec_path, runs_dir=self.runs, vault_dir=self.vault,
                                      context_dir=self.context, assets_dir=self.assets)
        self.machine = compute_gate.load_machine()

    def to_execute(self):
        run_id = self.new_run(pipeline="scene-3d")
        self.put(run_id, "brief.md", "A camera path.\n")
        self.assertEqual(self.run_cmd("note", run_id, "one-offs/3d/camera-path.md")[0], 0)
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.put(run_id, "attestation.md", "# Attestation\n\nThis pipeline needs no brand context.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.put(run_id, "recipe.md", "One render.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "render it")[0], 0)
        self.put(run_id, "execute_log.md", "Rendered.\n")
        return run_id

    def test_execute_is_not_done_without_a_consumed_token(self):
        run_id = self.to_execute()
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("no live compute token", err)
        path = self.root / "probe.json"
        path.write_text(json.dumps(probe()), encoding="utf-8")
        self.assertEqual(self.call(compute_gate, "mint", "llm_local_sm", "--probe", str(path))[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("is for `llm_local_sm`", err)
        self.assertEqual(self.call(compute_gate, "release")[0], 0)
        self.assertEqual(self.call(compute_gate, "mint", "render_3d_cpu", "--probe", str(path))[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("not consumed by this run", err)
        self.assertEqual(self.call(compute_gate, "consume", run_id)[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 0, err)

    def test_a_pipeline_of_another_class_needs_none(self):
        run_id = self.new_run()
        self.through(run_id, "execute")
        self.assertEqual(self.state(run_id)["completed_stages"][-1], "execute")


if __name__ == "__main__":
    unittest.main()
