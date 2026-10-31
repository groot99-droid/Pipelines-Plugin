"""The Meshy client against a fake Meshy on this machine: the dry run, the
go-ahead, resume, downloads, and that the key never shows. No real request is
made, and the key is a made-up value in a temporary key file."""

import ast
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

from glb_fixture import box_glb, png
from helpers import REPO, StudioCase

import glb_inspect
import meshy_client

FAKE_KEY = "fake-meshy-key-for-tests-0123456789"
MODEL = box_glb()


class FakeMeshy(BaseHTTPRequestHandler):
    """Tasks finish on their second poll. Files are served from /files/."""

    def log_message(self, *args):
        pass

    def reply(self, code, payload=None, raw=None, length=None):
        body = raw if raw is not None else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Length", str(length if length is not None else len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorised(self):
        world = self.server.world
        world["auth"].append(self.headers.get("Authorization"))
        if self.headers.get("Authorization") != f"Bearer {FAKE_KEY}":
            self.reply(401, {"message": "Invalid API key"})
            return False
        return True

    def do_GET(self):
        world = self.server.world
        if self.path.startswith("/files/"):
            world["file_auth"].append(self.headers.get("Authorization"))
            name = self.path.rsplit("/", 1)[1]
            if name.startswith("short"):
                return self.reply(200, raw=MODEL[:100], length=len(MODEL))
            return self.reply(200, raw=png(4, 4) if name.endswith(".png") else MODEL)
        if not self.authorised():
            return
        if self.path == "/openapi/v1/balance":
            return self.reply(200, {"balance": 640, "monthly_credits": 600, "permanent_credits": 40})
        if self.path.startswith("/openapi/v1/animations/library"):
            return self.reply(200, [{"action_id": 1, "name": "Walk", "category": "WalkAndRun"}])
        task_id = self.path.rsplit("/", 1)[1]
        task = world["tasks"].get(task_id)
        if task is None:
            return self.reply(404, {"message": "Task not found"})
        task["polls"] += 1
        base = f"http://127.0.0.1:{self.server.server_port}/files"
        stem = "short" if world.get("short") else task_id
        found = {"id": task_id, "status": "IN_PROGRESS" if task["polls"] < 2 else task["final"],
                 "progress": 50 if task["polls"] < 2 else 100}
        if found["status"] == "SUCCEEDED":
            found["consumed_credits"] = 20
            found["thumbnail_url"] = f"{base}/{task_id}.png?Signature=abc"
            if task["kind"] == "rig":
                found["result"] = {"rigged_character_glb_url": f"{base}/{stem}.glb?Signature=abc",
                                   "basic_animations": {"walking_glb_url": f"{base}/{stem}-walk.glb?Signature=abc"}}
            else:
                found["model_urls"] = {"glb": f"{base}/{stem}.glb?Signature=abc", "fbx": f"{base}/{stem}.fbx"}
        if found["status"] == "FAILED":
            found["task_error"] = {"message": "The prompt was moderated"}
        self.reply(200, found)

    def do_POST(self):
        world = self.server.world
        if not self.authorised():
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        world["posts"].append((self.path, body))
        task_id = f"task-{len(world['posts'])}"
        world["tasks"][task_id] = {"polls": 0, "final": world.get("final", "SUCCEEDED"),
                                   "kind": "rig" if self.path.endswith("rigging") else "model"}
        self.reply(202, {"result": task_id})


class MeshyCase(StudioCase):
    def setUp(self):
        super().setUp()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeMeshy)
        self.server.world = {"posts": [], "tasks": {}, "auth": [], "file_auth": []}
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        keys = self.root / "keys.env"
        keys.write_text(f"# test keys\nMESHY_API_KEY={FAKE_KEY}\n", encoding="utf-8")
        patch = mock.patch.dict(os.environ, {
            "ROSW_KEYS_FILE": str(keys),
            "MESHY_BASE_URL": f"http://127.0.0.1:{self.server.server_port}",
        })
        patch.start()
        self.addCleanup(patch.stop)
        self.outputs = []

    @property
    def world(self):
        return self.server.world

    def meshy(self, *arguments):
        code, out, err = self.call(meshy_client, *arguments)
        self.outputs.append(out + err)
        return code, out, err

    def tearDown(self):
        for text in self.outputs:
            self.assertNotIn(FAKE_KEY, text, "the key's value was printed")
        super().tearDown()

    def at_execute(self, confirmed=True):
        run_id = self.new_run(pipeline="asset-3d")
        self.through(run_id, "recipe", note="props/3d/lantern.md")
        if confirmed:
            self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "make them")[0], 0)
        return run_id

    def ledger(self, run_id):
        return json.loads((self.runs / run_id / meshy_client.LEDGER).read_text(encoding="utf-8"))


class DryRun(MeshyCase):
    def test_a_dry_run_posts_nothing_and_writes_nothing(self):
        run_id = self.at_execute(confirmed=False)
        code, out, err = self.meshy("create", "preview", run_id, "--name", "lantern",
                                    "--prompt", "a brass lantern", "--set", "target_polycount=8000")
        self.assertEqual(code, 0, err)
        self.assertIn('"prompt": "a brass lantern"', out)
        self.assertIn('"target_polycount": 8000', out)
        self.assertIn("estimate  20 credits", out)
        self.assertIn("balance   640 credits", out)
        self.assertIn("DRY RUN", out)
        self.assertEqual(self.world["posts"], [])
        self.assertFalse((self.runs / run_id / meshy_client.LEDGER).exists())

    def test_confirm_needs_the_execute_go_ahead(self):
        run_id = self.at_execute(confirmed=False)
        code, _, err = self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lantern",
                                  "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("no execute go-ahead", err)
        self.assertEqual(self.world["posts"], [])

    def test_confirm_needs_the_run_at_execute(self):
        run_id = self.new_run(pipeline="asset-3d")
        code, _, err = self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lantern",
                                  "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("is at `intake`", err)

    def test_a_pipeline_that_does_not_spend_cannot_call_meshy(self):
        run_id = self.new_run(pipeline="assemble-3d")
        self.through(run_id, "recipe", note="props/3d/table.md")
        self.run_cmd("confirm", run_id, "execute", "--words", "go")
        code, _, err = self.meshy("create", "preview", run_id, "--name", "x", "--prompt", "x", "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("does not spend", err)


class Requests(MeshyCase):
    def test_a_field_the_op_does_not_take_is_refused(self):
        run_id = self.at_execute()
        code, _, err = self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "x",
                                  "--set", "art_style=realistic")
        self.assertEqual(code, 2)
        self.assertIn("has no field `art_style`", err)

    def test_an_op_says_what_it_needs(self):
        run_id = self.at_execute()
        self.assertEqual(self.meshy("create", "preview", run_id, "--name", "a")[0], 2)
        code, _, err = self.meshy("create", "retexture", run_id, "--name", "a", "--model", "https://x/m.glb")
        self.assertIn("needs --prompt or --image", err)
        code, _, err = self.meshy("create", "animate", run_id, "--name", "a", "--from", "a:rig")
        self.assertEqual(code, 1)
        self.assertIn("made no `rig`", err)

    def test_a_long_prompt_is_refused(self):
        run_id = self.at_execute()
        code, _, err = self.meshy("create", "preview", run_id, "--name", "a", "--prompt", "x" * 801)
        self.assertEqual(code, 2)
        self.assertIn("800", err)

    def test_a_local_image_goes_as_a_data_uri_and_is_logged_as_a_hash(self):
        run_id = self.at_execute()
        image = self.runs / run_id / "ref.png"
        image.write_bytes(png(16, 16))
        code, out, err = self.meshy("create", "image", run_id, "--name", "statue", "--image", str(image),
                                    "--set", "should_texture=false", "--confirm")
        self.assertEqual(code, 0, err)
        path, body = self.world["posts"][0]
        self.assertEqual(path, "/openapi/v1/image-to-3d")
        self.assertTrue(body["image_url"].startswith("data:image/png;base64,"))
        self.assertIs(body["should_texture"], False)
        logged = self.ledger(run_id)["tasks"][0]["request"]["image_url"]
        self.assertRegex(logged, r"^data:image/png;base64,<\d+ bytes, sha256 [0-9a-f]{12}>$")
        self.assertNotIn("base64,iVBOR", out)

    def test_the_base_url_must_be_https_or_this_machine(self):
        with mock.patch.dict(os.environ, {"MESHY_BASE_URL": "http://api.example.com"}):
            code, _, err = self.meshy("balance")
        self.assertEqual(code, 2)
        self.assertIn("https", err)

    def test_no_key_is_refused_by_name(self):
        (self.root / "keys.env").write_text("MESHY_API_KEY=your-key-here\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"MESHY_API_KEY": ""}):
            code, _, err = self.meshy("balance")
        self.assertEqual(code, 1)
        self.assertIn("MESHY_API_KEY is not set", err)
        self.assertEqual(self.world["auth"], [])

    def test_the_service_saying_no_is_a_refusal(self):
        (self.root / "keys.env").write_text("MESHY_API_KEY=wrong-key\n", encoding="utf-8")
        code, _, err = self.meshy("balance")
        self.assertEqual(code, 1)
        self.assertIn("Meshy said 401", err)
        self.assertIn("Invalid API key", err)

    def test_the_animation_library(self):
        code, out, _ = self.meshy("animations", "--search", "walk")
        self.assertEqual(code, 0)
        self.assertIn("Walk", out)


class Flow(MeshyCase):
    def test_preview_refine_download(self):
        run_id = self.at_execute()
        preview = ("create", "preview", run_id, "--name", "lantern", "--prompt", "a brass lantern")
        self.assertEqual(self.meshy(*preview, "--confirm")[0], 0)
        code, out, _ = self.meshy(*preview, "--confirm")
        self.assertEqual(code, 0)
        self.assertIn("reused", out)
        self.assertEqual(len(self.world["posts"]), 1, "a matching create posted again")

        code, out, err = self.meshy("create", "refine", run_id, "--name", "lantern", "--from", "lantern:preview",
                                    "--confirm")
        self.assertEqual(code, 1, "refine before the preview finished")
        self.assertIn("not SUCCEEDED", err)

        code, out, err = self.meshy("wait", run_id, "--interval", "0")
        self.assertEqual(code, 0, err)
        self.assertIn("SUCCEEDED", out)
        self.assertIn("spent 20", out)

        code, _, err = self.meshy("create", "refine", run_id, "--name", "lantern", "--from", "lantern:preview",
                                  "--set", "enable_pbr=true", "--confirm")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.world["posts"][1], ("/openapi/v2/text-to-3d",
                                                  {"mode": "refine", "preview_task_id": "task-1", "enable_pbr": True}))
        self.meshy("wait", run_id, "--interval", "0")
        code, out, err = self.meshy("download", run_id, "--name", "lantern", "--op", "refine", "--thumbnail")
        self.assertEqual(code, 0, err)
        model = self.runs / run_id / "meshy" / "lantern-refine.glb"
        self.assertEqual(model.read_bytes(), MODEL)
        self.assertTrue((self.runs / run_id / "meshy" / "lantern-refine-thumb.png").is_file())
        self.assertEqual(glb_inspect.inspect(model.read_bytes())["triangles"], 12)
        self.assertEqual(self.world["file_auth"], [None, None], "the key went to the file host")

        ledger = (self.runs / run_id / meshy_client.LEDGER).read_text(encoding="utf-8")
        self.assertNotIn("Signature", ledger, "a signed link was stored")
        self.assertNotIn("/files/", ledger)
        task = self.ledger(run_id)["tasks"][1]
        self.assertEqual(task["downloads"][0]["file"], "lantern-refine.glb")
        self.assertEqual(task["formats"], ["fbx", "glb"])

        code, out, _ = self.meshy("status", run_id, "--offline")
        self.assertIn("lantern:preview", out)
        self.assertIn("lantern:refine", out)

    def test_a_changed_request_needs_again(self):
        run_id = self.at_execute()
        self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lantern", "--confirm")
        code, _, err = self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lamp",
                                  "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("--again", err)
        self.assertEqual(len(self.world["posts"]), 1)
        code, _, err = self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lamp",
                                  "--again", "--confirm")
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.world["posts"]), 2)

    def test_a_failed_task_is_logged_and_may_be_made_again(self):
        self.world["final"] = "FAILED"
        run_id = self.at_execute()
        create = ("create", "preview", run_id, "--name", "lantern", "--prompt", "a lantern", "--confirm")
        self.meshy(*create)
        code, out, _ = self.meshy("wait", run_id, "--interval", "0")
        self.assertEqual(code, 1)
        self.assertIn("FAILED", out)
        self.assertIn("moderated", out)
        self.meshy(*create)
        self.assertEqual(len(self.world["posts"]), 2, "a failed task is not reused")

    def test_a_short_download_keeps_nothing(self):
        run_id = self.at_execute()
        self.meshy("create", "preview", run_id, "--name", "lantern", "--prompt", "a lantern", "--confirm")
        self.meshy("wait", run_id, "--interval", "0")
        self.world["short"] = True
        code, _, err = self.meshy("download", run_id, "--name", "lantern", "--op", "preview")
        self.assertEqual(code, 1)
        self.assertIn("Nothing was kept", err)
        folder = self.runs / run_id / "meshy"
        self.assertEqual(list(folder.iterdir()) if folder.exists() else [], [])

    def test_a_rig_and_its_walk(self):
        run_id = self.at_execute()
        self.meshy("create", "preview", run_id, "--name", "hero", "--prompt", "a knight", "--confirm")
        self.meshy("wait", run_id, "--interval", "0")
        self.meshy("create", "refine", run_id, "--name", "hero", "--from", "hero:preview", "--confirm")
        self.meshy("wait", run_id, "--interval", "0")
        code, out, err = self.meshy("create", "rig", run_id, "--name", "hero", "--from", "hero:refine",
                                    "--set", "height_meters=1.8")
        self.assertIn("estimate  5 credits", out)
        self.meshy("create", "rig", run_id, "--name", "hero", "--from", "hero:refine", "--set",
                   "height_meters=1.8", "--confirm")
        self.assertEqual(self.world["posts"][-1], ("/openapi/v1/rigging",
                                                   {"input_task_id": "task-2", "height_meters": 1.8}))
        self.meshy("wait", run_id, "--interval", "0")
        self.assertEqual(self.meshy("download", run_id, "--name", "hero", "--op", "rig")[0], 0)
        code, _, err = self.meshy("download", run_id, "--name", "hero", "--op", "rig", "--part", "walking")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.runs / run_id / "meshy" / "hero-rig-walking.glb").is_file())
        code, _, err = self.meshy("download", run_id, "--name", "hero", "--op", "rig", "--part", "running")
        self.assertEqual(code, 1, "the fake has no running clip")


class Estimates(unittest.TestCase):
    def test_the_pricing_table(self):
        e = meshy_client.estimate_credits
        self.assertEqual(e("preview", {}), 20)
        self.assertEqual(e("preview", {"ai_model": "meshy-t2.5", "geometry_resolution": "4k"}), 10)
        self.assertEqual(e("refine", {"texture_resolution": "8k"}), 15)
        self.assertEqual(e("image", {}), 30)
        self.assertEqual(e("image", {"should_texture": False}), 20)
        self.assertEqual(e("image", {"texture_resolution": "8k", "ai_model": "meshy-6-lite"}), 20)
        self.assertEqual(e("animate", {"action_ids": [1, 2, 3]}), 9)
        self.assertEqual(e("rig", {}), 5)


class KeyReader(unittest.TestCase):
    """The client reads the key file the way creative-writing/pipeline/llm.py
    does. llm.py is read as text, never imported: importing it loads the real
    key file into the environment."""

    def test_it_reads_keys_as_llm_py_does(self):
        llm = (REPO / "creative-writing" / "pipeline" / "llm.py").read_text(encoding="utf-8")
        mine = (REPO / "studio" / "pipeline" / "meshy_client.py").read_text(encoding="utf-8")
        for line in ('os.environ.get("ROSW_KEYS_FILE") or os.path.join(',
                     'os.path.expanduser("~"), ".rosw", "keys.env")',
                     'if not line or line.startswith("#") or "=" not in line:',
                     "value = value.strip().strip('\"').strip(\"'\")",
                     "if value and value not in PLACEHOLDERS:"):
            with self.subTest(line=line):
                self.assertIn(line, llm)
                self.assertIn(line, mine)

        def placeholders(source):
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "PLACEHOLDERS":
                    return ast.literal_eval(node.value)
        self.assertEqual(placeholders(llm), placeholders(mine))

    def test_the_setup_page_knows_the_key(self):
        setup = (REPO / "docs" / "setup_keys.py").read_text(encoding="utf-8")
        self.assertIn(f'"{meshy_client.KEY_NAME}"', setup)


if __name__ == "__main__":
    unittest.main()
