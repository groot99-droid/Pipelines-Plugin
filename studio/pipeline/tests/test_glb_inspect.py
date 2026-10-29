"""The GLB inspector, on boxes built in the test."""

import contextlib
import io
import json
import shutil
import struct
import tempfile
import unittest
from pathlib import Path

from glb_fixture import box_glb
import helpers  # noqa: F401  (puts studio/pipeline on the path)

import glb_inspect


class Inspect(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="glb-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def write(self, name, data):
        path = self.root / name
        path.write_bytes(data)
        return path

    def run_cli(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = glb_inspect.main([str(a) for a in arguments])
        return code, out.getvalue(), err.getvalue()

    def test_a_box(self):
        report = glb_inspect.inspect(box_glb((1.0, 2.0, 0.5), texture=(64, 32)))
        self.assertEqual(report["triangles"], 12)
        self.assertEqual(report["meshes"][0]["vertices"], 8)
        self.assertEqual(report["materials"], ["grey"])
        self.assertEqual(report["textures"], 1)
        self.assertEqual(report["images"][0]["size"], [64, 32])
        self.assertEqual(report["bbox"]["size"], [1.0, 2.0, 0.5])
        self.assertEqual(report["height_m"], 2.0)
        self.assertEqual(report["skins"], 0)

    def test_node_transforms_move_and_scale_the_box(self):
        report = glb_inspect.inspect(box_glb((1.0, 2.0, 0.5), translation=(3, 1, 0), scale=(2, 2, 2)))
        self.assertEqual(report["bbox"]["size"], [2.0, 4.0, 1.0])
        self.assertEqual(report["bbox"]["min"], [2.0, 1.0, -0.5])

    def test_a_rotation(self):
        doc_bytes = box_glb((1.0, 2.0, 0.5))
        doc, binary = glb_inspect.read_glb(doc_bytes)
        doc["nodes"][0]["rotation"] = [0, 0, 0.7071068, 0.7071068]  # 90 degrees about z: lying down
        text = json.dumps(doc).encode()
        text += b" " * (-len(text) % 4)
        body = struct.pack("<II", len(text), glb_inspect.JSON_CHUNK) + text + struct.pack(
            "<II", len(binary), glb_inspect.BIN_CHUNK) + binary
        rotated = struct.pack("<III", glb_inspect.MAGIC, 2, 12 + len(body)) + body
        report = glb_inspect.inspect(rotated)
        self.assertAlmostEqual(report["height_m"], 1.0, places=4)
        self.assertAlmostEqual(report["bbox"]["size"][0], 2.0, places=4)

    def test_budgets(self):
        path = self.write("box.glb", box_glb(texture=(4096, 2048)))
        code, out, _ = self.run_cli(path, "--budget", "tris=12,tex=4096,height=1.5-2.5,mb=1")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("pass"), 4)
        code, out, _ = self.run_cli(path, "--budget", "tris=10,tex=2048,height=3-4")
        self.assertEqual(code, 1)
        self.assertEqual(out.count("OVER"), 3)

    def test_json(self):
        path = self.write("box.glb", box_glb())
        code, out, _ = self.run_cli(path, "--json", "--budget", "tris=5")
        self.assertEqual(code, 1)
        found = json.loads(out)
        self.assertEqual(found["findings"], [{"limit": "tris", "pass": False, "found": "12 triangles, budget 5"}])

    def test_what_is_not_a_glb(self):
        for name, data in (("text.glb", b"not a model at all, just text"),
                           ("cut.glb", box_glb()[:40]),
                           ("v1.glb", b"glTF" + (1).to_bytes(4, "little") + bytes(40))):
            with self.subTest(name=name):
                code, _, err = self.run_cli(self.write(name, data))
                self.assertEqual(code, 2)
                self.assertIn("error", err)
        code, _, err = self.run_cli(self.write("ok.glb", box_glb()), "--budget", "polys=3")
        self.assertEqual(code, 2)

    def test_image_sizes(self):
        jpeg = (b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
                b"\xff\xc0\x00\x11\x08\x01\x00\x02\x00\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01")
        self.assertEqual(glb_inspect.image_size(jpeg), (512, 256))
        webp = b"RIFF\x00\x00\x00\x00WEBPVP8X" + bytes(8) + (99).to_bytes(3, "little") + (49).to_bytes(3, "little")
        self.assertEqual(glb_inspect.image_size(webp), (100, 50))
        self.assertIsNone(glb_inspect.image_size(b"nothing"))


if __name__ == "__main__":
    unittest.main()
