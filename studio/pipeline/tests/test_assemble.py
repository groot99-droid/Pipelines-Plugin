"""The assembly plan without Blender, and the headless assembler with it.

The plan's tests always run. The Blender test runs only where there is a
Blender: `blender` on PATH, or ROSW_BPY_PYTHON naming a Python that can import
bpy (the `bpy` module from PyPI). Elsewhere it is skipped and says so."""

import ast
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from glb_fixture import box_glb
from helpers import PIPELINE

import glb_inspect

sys.path.insert(0, str(PIPELINE / "bpy"))
import assemble_plan as plan_module  # noqa: E402

ASSEMBLER = PIPELINE / "bpy" / "assemble.py"
ALLOWED_IMPORTS = {"json", "math", "bpy", "mathutils"}
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "__import__", "getattr", "setattr", "globals", "locals"}


class PlanCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="assemble-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "meshy").mkdir()
        (self.root / "meshy" / "box.glb").write_bytes(box_glb((1.0, 2.0, 0.5)))
        (self.root / "meshy" / "pole.glb").write_bytes(box_glb((0.2, 4.0, 0.2), translation=(2, 1, 0)))

    def layout(self, **changes):
        layout = {"assets": [
            {"name": "box", "glb": "meshy/box.glb", "target_height_m": 0.9, "rotation_deg": [0, 0, 30],
             "lods": [0.5]},
            {"name": "pole", "glb": "meshy/pole.glb", "target_height_m": 1.8, "location": [1.5, 0, 0]},
        ], "render": {"resolution": [160, 90], "samples": 2}}
        layout.update(changes)
        path = self.root / "assembly.json"
        path.write_text(json.dumps(layout), encoding="utf-8")
        return path

    def resolve(self, layout):
        return plan_module.resolve(layout, self.root, self.root / "blender")


class Layout(PlanCase):
    def test_a_good_layout_is_filled_in(self):
        plan = plan_module.load(self.layout(), self.root / "blender")
        self.assertEqual(plan["assets"][0]["glb"], str((self.root / "meshy" / "box.glb").resolve()))
        self.assertTrue(plan["assets"][0]["ground"])
        self.assertEqual(plan["assets"][1]["location"], [1.5, 0.0, 0.0])
        self.assertEqual(plan["render"]["engine"], "cycles")
        self.assertEqual(plan["export"], {"blend": "scene.blend", "glb": "scene.glb", "include_floor": False})
        self.assertEqual(plan_module.missing_models(plan), [])

    def test_what_a_layout_may_not_say(self):
        good = json.loads(self.layout().read_text(encoding="utf-8"))
        cases = {
            "outside": {"name": "x", "glb": "../elsewhere.glb"},
            "not a model": {"name": "x", "glb": "meshy/box.png"},
            "bad name": {"name": "Big Box", "glb": "meshy/box.glb"},
            "both sizes": {"name": "x", "glb": "meshy/box.glb", "target_height_m": 1, "scale": 2},
            "lods upward": {"name": "x", "glb": "meshy/box.glb", "lods": [0.25, 0.5]},
            "decimate zero": {"name": "x", "glb": "meshy/box.glb", "decimate": 0},
            "unknown key": {"name": "x", "glb": "meshy/box.glb", "colour": "red"},
            "short location": {"name": "x", "glb": "meshy/box.glb", "location": [0, 0]},
        }
        for label, asset in cases.items():
            with self.subTest(case=label), self.assertRaises(plan_module.Invalid):
                self.resolve({"assets": [asset]})
        for label, change in {"twice": {"assets": good["assets"] + [good["assets"][0]]},
                              "no assets": {"assets": []},
                              "engine": {"render": {"engine": "octane"}},
                              "a path as a file": {"export": {"glb": "../out.glb"}},
                              "top-level typo": {"camrea": "auto"},
                              "a light with no type": {"lights": [{"location": [0, 0, 1]}]}}.items():
            with self.subTest(case=label), self.assertRaises(plan_module.Invalid):
                self.resolve({**good, **change})

    def test_check_says_what_is_missing(self):
        (self.root / "meshy" / "pole.glb").unlink()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = plan_module.main(["check", str(self.layout())])
        self.assertEqual(code, 1)
        self.assertIn("missing", err.getvalue())
        self.assertIn("box: box.glb, to 0.9 m tall", out.getvalue())


class Math(unittest.TestCase):
    def test_fit_scale(self):
        self.assertEqual(plan_module.fit_scale(2.0, 0.9), 0.45)
        self.assertEqual(plan_module.fit_scale(2.0, None), 1.0)
        with self.assertRaises(ValueError):
            plan_module.fit_scale(0.0, 1.0)

    def test_placement(self):
        lo, hi = (1.0, 2.0, 0.5), (3.0, 4.0, 2.5)
        self.assertEqual(plan_module.placement(lo, hi, (0, 0, 0), True), (-2.0, -3.0, -0.5))
        self.assertEqual(plan_module.placement(lo, hi, (0, 0, 1), False), (-2.0, -3.0, -0.5))

    def test_the_camera_sees_the_whole_box(self):
        import math
        lo, hi = (-1.0, -1.0, 0.0), (1.0, 1.0, 2.0)
        for aspect in (16 / 9, 1.0, 9 / 16):
            eye, centre = plan_module.auto_camera(lo, hi, 50.0, aspect)
            distance = math.dist(eye, centre)
            radius = math.dist(lo, hi) / 2
            narrow = math.atan(18.0 / 50.0 / aspect if aspect >= 1 else 18.0 / 50.0 * aspect)
            with self.subTest(aspect=aspect):
                self.assertGreater(math.asin(min(radius / distance, 1)), 0)
                self.assertLess(math.asin(radius / distance), narrow)
                self.assertGreater(eye[2], centre[2], "the camera looks down a little")

    def test_studio_lights_scale_with_the_box(self):
        small = plan_module.studio_lights((0, 0, 0), (1, 1, 1))
        large = plan_module.studio_lights((0, 0, 0), (10, 10, 10))
        self.assertEqual([l["name"] for l in small], ["key", "fill", "rim"])
        self.assertGreater(large[0]["energy"], small[0]["energy"])


class Steps(PlanCase):
    """Every step is code the live branch sends through execute_blender_code,
    where the server's safe mode allows bpy, mathutils and plain stdlib only."""

    def test_every_step_is_self_contained_code(self):
        plan = plan_module.load(self.layout(), self.root / "blender")
        for step in plan_module.STEPS:
            with self.subTest(step=step):
                code = plan_module.step_code(plan, step)
                tree = ast.parse(code)
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported |= {a.name.split(".")[0] for a in node.names}
                    elif isinstance(node, ast.ImportFrom):
                        imported.add(node.module.split(".")[0])
                    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, FORBIDDEN_CALLS)
                    elif isinstance(node, ast.Attribute):
                        self.assertFalse(node.attr.startswith("__"), node.attr)
                self.assertLessEqual(imported, ALLOWED_IMPORTS)
                self.assertIn('print("ROSW "', code)
                # The plan rides in as a JSON string literal; read it back
                # rather than search the text, which escapes a Windows path twice.
                literal = next(node.value.args[0] for node in tree.body
                               if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PLAN")
                carried = json.loads(ast.literal_eval(literal))
                self.assertEqual(carried["assets"][0]["glb"], str((self.root / "meshy" / "box.glb").resolve()))
                self.assertEqual(carried, plan)

    def test_the_shared_math_goes_into_the_steps_that_use_it(self):
        plan = plan_module.load(self.layout(), self.root / "blender")
        self.assertIn("def placement(", plan_module.step_code(plan, "normalize"))
        self.assertIn("def auto_camera(", plan_module.step_code(plan, "stage"))
        self.assertNotIn("def placement(", plan_module.step_code(plan, "import"))

    def test_emit_prints_one_step(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = plan_module.main(["emit", str(self.layout()), "--step", "import"])
        self.assertEqual(code, 0)
        self.assertTrue(out.getvalue().startswith("# ROSW assemble step `import`"))


def bpy_command():
    """How to run assemble.py here, or None."""
    python = os.environ.get("ROSW_BPY_PYTHON")
    if python:
        return [python, str(ASSEMBLER)]
    blender = shutil.which("blender")
    if blender:
        return [blender, "-b", "--factory-startup", "--python", str(ASSEMBLER), "--"]
    return None


@unittest.skipIf(bpy_command() is None, "no Blender here: put blender on PATH or set ROSW_BPY_PYTHON")
class Headless(PlanCase):
    def test_the_whole_assembly(self):
        out = self.root / "blender"
        result = subprocess.run(bpy_command() + ["--layout", str(self.layout()), "--out", str(out)],
                                capture_output=True, text=True, timeout=600)
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])
        for name in ("scene.blend", "scene.glb", "preview.png", "assemble_report.json"):
            self.assertTrue((out / name).is_file(), name)
        self.assertEqual(sorted(p.stem for p in (out / "steps").iterdir()), sorted(plan_module.STEPS))
        report = json.loads((out / "assemble_report.json").read_text(encoding="utf-8"))
        by_step = {entry["step"]: entry for entry in report["steps"]}
        sizes = {a["name"]: a for a in by_step["normalize"]["assets"]}
        self.assertAlmostEqual(sizes["box"]["size"][2], 0.9, places=3)
        self.assertAlmostEqual(sizes["pole"]["size"][2], 1.8, places=3)
        self.assertAlmostEqual(sizes["box"]["base_z"], 0.0, places=4)
        lods = by_step["lods"]["assets"][0]["lods"]
        self.assertEqual(lods[0]["lod"], "rosw_box_LOD1")
        self.assertLess(lods[0]["triangles"], 12)
        scene = glb_inspect.inspect((out / "scene.glb").read_bytes())
        self.assertEqual(scene["triangles"], 24, "the LOD and the floor stay out of the export")
        self.assertAlmostEqual(scene["height_m"], 1.8, places=3)
        self.assertAlmostEqual(scene["bbox"]["min"][1], 0.0, places=3)


if __name__ == "__main__":
    unittest.main()
