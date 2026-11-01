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
import probe as probe_module

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
        if type(self) is not ExecuteNeedsAToken:
            self.skipTest("the local-compute case")
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



class LocalBranch(ExecuteNeedsAToken):
    """A spend pipeline with a local branch: the token is needed on `local` only."""

    def setUp(self):
        super().setUp()
        spec = fixture_spec()
        spec["pipelines"]["scene-3d"]["class"] = "spend"
        spec["pipelines"]["scene-3d"]["local_workload"] = "render_3d_cpu"
        spec["pipelines"]["scene-3d"]["requires_context"] = []
        self.spec_path.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")

    def test_a_run_that_chose_no_branch_cannot_finish_execute(self):
        run_id = self.to_execute()
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("chose none", err)

    def test_cloud_needs_no_token_and_local_needs_one(self):
        cloud = self.to_execute()
        self.assertEqual(self.run_cmd("branch", cloud, "cloud")[0], 0)
        self.assertEqual(self.run_cmd("advance", cloud)[0], 0)
        local = self.to_execute()
        self.assertEqual(self.run_cmd("branch", local, "local")[0], 0)
        code, _, err = self.run_cmd("advance", local)
        self.assertEqual(code, 1)
        self.assertIn("no live compute token", err)
        path = self.root / "probe.json"
        path.write_text(json.dumps(probe()), encoding="utf-8")
        self.assertEqual(self.call(compute_gate, "mint", "render_3d_cpu", "--probe", str(path))[0], 0)
        self.assertEqual(self.call(compute_gate, "consume", local)[0], 0)
        self.assertEqual(self.run_cmd("advance", local)[0], 0)

    def test_a_pipeline_with_no_local_branch_has_none_to_choose(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("branch", run_id, "local")
        self.assertEqual(code, 1)
        self.assertIn("no local branch", err)


class Renewal(GateCase):
    def mint(self):
        self.assertEqual(self.gate("mint", "render_3d_cpu", "--probe", self.probe_file())[0], 0)
        self.assertEqual(self.gate("consume", "scene-000001")[0], 0)

    def age(self, seconds):
        path = compute_gate.token_path(self.env, self.machine)
        token = json.loads(path.read_text(encoding="utf-8"))
        token["ts_epoch"] -= seconds
        token["started_epoch"] -= seconds
        path.write_text(json.dumps(token), encoding="utf-8")

    def test_renew_extends_a_live_token_and_counts_it(self):
        self.mint()
        self.age(1700)
        code, out, _ = self.gate("renew", "scene-000001", "--probe", self.probe_file())
        self.assertEqual(code, 0, out)
        token = compute_gate.load_token(self.env, self.machine)
        self.assertEqual(token["renewals"], 1)
        self.assertEqual(token["consumed_by"], "scene-000001")
        self.assertGreater(token["ttl_seconds"] - compute_gate.token_age(token), 1700)

    def test_an_expired_token_is_not_renewed(self):
        self.mint()
        self.age(1801)
        code, _, err = self.gate("renew", "--probe", self.probe_file())
        self.assertEqual(code, 1)
        self.assertIn("expired", err)

    def test_renew_checks_the_machine_again_and_leaves_the_token_on_a_deny(self):
        self.mint()
        before = compute_gate.token_path(self.env, self.machine).read_text(encoding="utf-8")
        code, out, _ = self.gate("renew", "--probe", self.probe_file(**{"power.source": "battery"}))
        self.assertEqual(code, 1)
        self.assertIn("untouched", out)
        self.assertEqual(compute_gate.token_path(self.env, self.machine).read_text(encoding="utf-8"), before)

    def test_another_run_cannot_renew_it_and_the_total_life_is_capped(self):
        self.mint()
        code, _, err = self.gate("renew", "scene-000002", "--probe", self.probe_file())
        self.assertEqual(code, 1)
        self.assertIn("held by", err)
        path = compute_gate.token_path(self.env, self.machine)
        token = json.loads(path.read_text(encoding="utf-8"))
        token["started_epoch"] -= self.machine["token"]["max_seconds"] - 100  # many renewals ago
        path.write_text(json.dumps(token), encoding="utf-8")
        code, _, err = self.gate("renew", "scene-000001", "--probe", self.probe_file())
        self.assertEqual(code, 1)
        self.assertIn("max_seconds", err)

    def test_a_class_may_set_its_own_ttl(self):
        self.machine["classes"]["render_3d_cpu"]["ttl_seconds"] = 7200
        self.assertEqual(compute_gate.class_ttl(self.machine, "render_3d_cpu"), 7200)
        self.assertEqual(compute_gate.class_ttl(self.machine, "batch_2d"), 1800)
        self.assertEqual(compute_gate.evaluate(self.machine, probe(), "render_3d_cpu")["verdict"], "PASS")


class GpuProbe(unittest.TestCase):
    def block(self, names, smi=()):
        original = probe_module.nvidia_gpus
        probe_module.nvidia_gpus = lambda: list(smi)
        try:
            return probe_module.gpu_block(names)
        finally:
            probe_module.nvidia_gpus = original

    def test_names_are_classified(self):
        cases = {
            "NVIDIA GeForce RTX 4070 Laptop GPU": "discrete",
            "AMD Radeon RX 7800 XT": "discrete",
            "AMD Radeon(TM) Graphics": "integrated",
            "AMD Radeon 780M Graphics": "integrated",
            "Intel(R) Arc(TM) A770 Graphics": "discrete",
            "Intel(R) Arc(TM) Graphics": "integrated",
            "Intel(R) Iris(R) Xe Graphics": "integrated",
            "Intel(R) UHD Graphics 770": "integrated",
            "Microsoft Basic Display Adapter": "virtual",
        }
        for name, want in cases.items():
            with self.subTest(name=name):
                self.assertEqual(probe_module.classify_gpu(name), want)

    def test_every_adapter_counts_not_the_first(self):
        found = self.block(["Intel(R) Arc(TM) Graphics", "AMD Radeon RX 6600"])
        self.assertEqual(found["status"], "discrete")
        self.assertEqual((found["count"], found["discrete_count"]), (2, 1))
        self.assertEqual(found["name"], "AMD Radeon RX 6600")
        self.assertFalse(found["memory_shared_with_system"])

    def test_nvidia_smi_gives_vram_and_adds_an_adapter_the_os_missed(self):
        found = self.block(["Intel(R) UHD Graphics"], smi=[("NVIDIA RTX A2000", 12.0)])
        self.assertEqual(found["status"], "discrete")
        self.assertEqual(found["vram_total_gb"], 12.0)
        self.assertEqual(found["count"], 2)

    def test_integrated_virtual_and_none(self):
        self.assertEqual(self.block(["Intel(R) Arc(TM) Graphics"])["status"], "integrated")
        self.assertEqual(self.block(["Microsoft Basic Display Adapter"])["status"], "none")
        self.assertEqual(self.block([])["status"], "none")


if __name__ == "__main__":
    unittest.main()
