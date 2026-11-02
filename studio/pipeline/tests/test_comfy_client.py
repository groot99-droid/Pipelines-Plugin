"""The ComfyUI client against a fake ComfyUI on this machine: the dry run, the audit of nodes and model files,
the patched workflow, the upload, the wait, the download, reuse, and that a server on another machine is refused.
No real request leaves this machine."""

import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from glb_fixture import box_glb, png
from helpers import PIPELINE  # noqa: F401  (puts the pipeline folder on sys.path)

import comfy_client

MODEL = box_glb()


def full_object_info(flow, skip_class=None, skip_file=None):
    """What a server that has everything the workflow names would answer."""
    info = {}
    for node in flow.values():
        info.setdefault(node["class_type"], {"input": {"required": {}}})
    for node in flow.values():
        field = comfy_client.LOADERS.get(node["class_type"])
        if field:
            options = info[node["class_type"]]["input"]["required"].setdefault(field, [[]])[0]
            if node["inputs"][field] != skip_file:
                options.append(node["inputs"][field])
    if skip_class:
        info.pop(skip_class, None)
    return info


class FakeComfy(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, code, payload=None, raw=None):
        body = raw if raw is not None else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        world = self.server.world
        path = self.path.split("?")[0]
        world["gets"].append(path)
        if path == "/system_stats":
            return self.reply(200, {"devices": [{"name": "Fake GPU", "vram_total": 24 << 30}]})
        if path == "/object_info":
            return self.reply(200, world["info"])
        if path.startswith("/history/"):
            world["polls"] += 1
            pid = path.rsplit("/", 1)[1]
            if world["polls"] < 2:
                return self.reply(200, {})
            if world.get("fail"):
                return self.reply(200, {pid: {"status": {"status_str": "error", "messages": [["execution_error", {"node_type": "Trellis2ShapeStage", "exception_message": "CUDA out of memory"}]]}, "outputs": {}}})
            outputs = {} if world.get("no_file") else {"322": {"3d": [{"filename": "ComfyUI_00001_.glb", "subfolder": "3d", "type": "output"}]}}
            return self.reply(200, {pid: {"status": {"status_str": "success", "completed": True}, "outputs": outputs}})
        if path == "/view":
            if world.get("short"):
                self.send_response(200)
                self.send_header("Content-Length", str(len(MODEL)))
                self.end_headers()
                self.wfile.write(MODEL[:50])
                return
            return self.reply(200, raw=MODEL)
        self.reply(404, {"error": "no such route"})

    def do_POST(self):
        world = self.server.world
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        world["posts"].append(self.path)
        if self.path == "/upload/image":
            world["uploaded"] = body
            return self.reply(200, {"name": "rosw_upload.png", "subfolder": "", "type": "input"})
        if self.path == "/prompt":
            world["prompt"] = json.loads(body)["prompt"]
            if world.get("reject"):
                return self.reply(400, {"error": {"message": "invalid prompt"}, "node_errors": {"91": {"errors": ["bad"]}}})
            return self.reply(200, {"prompt_id": "pid-1", "number": 1, "node_errors": {}})
        self.reply(404, {"error": "no such route"})


class ComfyCase(unittest.TestCase):
    def setUp(self):
        self.flow = comfy_client.load_workflow()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfy)
        self.server.world = {"gets": [], "posts": [], "polls": 0, "info": full_object_info(self.flow)}
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.image = self.dir / "axe.png"
        self.image.write_bytes(png(8, 8))
        self.out = self.dir / "out"
        patcher = mock.patch.dict(os.environ, {"COMFY_URL": f"http://127.0.0.1:{self.server.server_address[1]}"})
        patcher.start()
        self.addCleanup(patcher.stop)

    @property
    def world(self):
        return self.server.world

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = comfy_client.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def run_args(self, *extra):
        return ("run", "--image", str(self.image), "--out", str(self.out), "--interval", "0.01", *extra)


class Workflow(unittest.TestCase):
    def test_every_binding_matches_the_shipped_workflow(self):
        flow = comfy_client.load_workflow()
        self.assertEqual(len(comfy_client.seeds_of(flow)), 4)

    def test_a_reexported_workflow_with_shifted_ids_is_refused(self):
        flow = json.loads(comfy_client.WORKFLOW.read_text(encoding="utf-8"))
        flow["122"]["class_type"] = "SomethingElse"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "w.json")
            path.write_text(json.dumps(flow), encoding="utf-8")
            with mock.patch.object(comfy_client, "WORKFLOW", path):
                with self.assertRaises(comfy_client.Usage):
                    comfy_client.load_workflow()

    def test_patching_sets_image_engine_background_and_seeds_and_leaves_the_original(self):
        flow = comfy_client.load_workflow()
        before = json.dumps(flow, sort_keys=True)
        out = comfy_client.patched(flow, "up.png", "pixal3d", 100, False)
        self.assertEqual(out["122"]["inputs"]["image"], "up.png")
        self.assertIs(out["316"]["inputs"]["value"], False)
        self.assertIs(out["248"]["inputs"]["switch"], False)
        self.assertEqual(comfy_client.seeds_of(out), [100, 101, 102, 103])
        self.assertEqual(json.dumps(flow, sort_keys=True), before)
        self.assertIs(comfy_client.patched(flow, "up.png", "trellis2", None, True)["316"]["inputs"]["value"], True)

    def test_the_other_engines_unet_is_not_required(self):
        flow = comfy_client.load_workflow()
        names = {f[2] for f in comfy_client.pick("trellis2", flow)[1]}
        self.assertIn("trellis_2_int8_convrot.safetensors", names)
        self.assertNotIn("pixal3d_int8_convrot.safetensors", names)
        names = {f[2] for f in comfy_client.pick("pixal3d", flow)[1]}
        self.assertIn("pixal3d_int8_convrot.safetensors", names)
        self.assertNotIn("trellis_2_int8_convrot.safetensors", names)

    def test_the_workflow_holds_no_local_path_or_link(self):
        text = comfy_client.WORKFLOW.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"https?://|[A-Za-z]:\\\\|/Users/|/home/")


class Run(ComfyCase):
    def test_check_reports_a_complete_server(self):
        code, out, err = self.run_cli("check")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Fake GPU, 24 GB VRAM", out)

    def test_check_names_a_missing_class_and_a_missing_model(self):
        self.world["info"] = full_object_info(self.flow, skip_class="Trellis2ShapeStage", skip_file="birefnet.safetensors")
        code, out, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("missing   node class Trellis2ShapeStage", out)
        self.assertIn("missing   model file birefnet.safetensors", out)

    def test_plan_sends_nothing(self):
        code, out, _ = self.run_cli("plan", "--image", str(self.image), "--engine", "pixal3d", "--seed", "7")
        self.assertEqual(code, 0)
        self.assertIn("seeds       [7, 8, 9, 10]", out)
        self.assertEqual((self.world["gets"], self.world["posts"]), ([], []))

    def test_dry_run_checks_but_uploads_and_queues_nothing(self):
        code, out, _ = self.run_cli(*self.run_args())
        self.assertEqual(code, 0)
        self.assertIn("dry run", out)
        self.assertEqual(self.world["posts"], [])
        self.assertFalse(self.out.exists())

    def test_confirmed_run_uploads_patches_waits_downloads_and_records(self):
        code, out, err = self.run_cli(*self.run_args("--confirm", "--engine", "pixal3d", "--seed", "5"))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.world["posts"], ["/upload/image", "/prompt"])
        sent = self.world["prompt"]
        self.assertEqual(sent["122"]["inputs"]["image"], "rosw_upload.png")
        self.assertIs(sent["316"]["inputs"]["value"], False)
        self.assertEqual(comfy_client.seeds_of(sent), [5, 6, 7, 8])
        self.assertEqual((self.out / "ComfyUI_00001_.glb").read_bytes(), MODEL)
        self.assertFalse(list(self.out.glob("*.part")))
        task = json.loads((self.out / "comfy_tasks.json").read_text(encoding="utf-8"))["tasks"][0]
        self.assertEqual((task["status"], task["engine"], task["prompt_id"]), ("done", "pixal3d", "pid-1"))
        self.assertEqual(len(task["image_sha256"]), 64)
        self.assertEqual(len(task["files"][0]["sha256"]), 64)
        ledger_text = (self.out / "comfy_tasks.json").read_text(encoding="utf-8")
        self.assertNotIn(str(self.image), ledger_text)
        self.assertNotIn("127.0.0.1", ledger_text)

    def test_the_same_request_is_reused_and_posts_nothing(self):
        self.run_cli(*self.run_args("--confirm"))
        self.world["posts"].clear()
        code, out, _ = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 0)
        self.assertIn("reuse", out)
        self.assertEqual(self.world["posts"], [])

    def test_a_different_engine_is_a_new_request(self):
        self.run_cli(*self.run_args("--confirm"))
        self.world["posts"].clear()
        self.world["polls"] = 0
        self.run_cli(*self.run_args("--confirm", "--engine", "pixal3d"))
        self.assertEqual(self.world["posts"], ["/upload/image", "/prompt"])

    def test_a_server_missing_a_model_is_refused_before_anything_is_uploaded(self):
        self.world["info"] = full_object_info(self.flow, skip_file="birefnet.safetensors")
        code, _, err = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 1)
        self.assertIn("nothing was sent", err)
        self.assertEqual(self.world["posts"], [])

    def test_a_rejected_workflow_is_reported(self):
        self.world["reject"] = True
        code, _, err = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 1)
        self.assertIn("invalid prompt", err)

    def test_a_failed_job_says_why(self):
        self.world["fail"] = True
        code, _, err = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 1)
        self.assertIn("CUDA out of memory", err)

    def test_no_output_file_is_a_failure_not_a_pass(self):
        self.world["no_file"] = True
        code, _, err = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 1)
        self.assertIn("no file", err)
        task = json.loads((self.out / "comfy_tasks.json").read_text(encoding="utf-8"))["tasks"][0]
        self.assertEqual(task["status"], "failed")

    def test_a_short_download_keeps_nothing(self):
        self.world["short"] = True
        code, _, err = self.run_cli(*self.run_args("--confirm"))
        self.assertEqual(code, 1)
        self.assertIn("status pid-1", err)
        self.assertEqual(list(self.out.glob("*.glb")) + list(self.out.glob("*.part")), [])

    def test_timeout_does_not_cancel_and_names_the_prompt(self):
        self.world["polls"] = -10_000
        code, _, err = self.run_cli(*self.run_args("--confirm", "--timeout", "0"))
        self.assertEqual(code, 1)
        self.assertIn("not cancelled", err)
        self.assertIn("pid-1", err)

    def test_status_of_a_finished_prompt_lists_its_file(self):
        self.world["polls"] = 5
        code, out, _ = self.run_cli("status", "pid-1")
        self.assertEqual(code, 0)
        self.assertIn("ComfyUI_00001_.glb", out)


class Safety(ComfyCase):
    def test_a_bad_image_is_a_usage_error(self):
        bad = self.dir / "a.gif"
        bad.write_bytes(b"GIF89a")
        code, _, err = self.run_cli("plan", "--image", str(bad))
        self.assertEqual(code, 2)
        empty = self.dir / "e.png"
        empty.write_bytes(b"")
        self.assertEqual(self.run_cli("plan", "--image", str(empty))[0], 2)

    def test_a_server_on_another_machine_is_refused_without_the_flag_and_without_https(self):
        with mock.patch.dict(os.environ, {"COMFY_URL": "http://gpu.example.com:8188"}):
            code, _, err = self.run_cli("check")
            self.assertEqual(code, 1)
            self.assertIn("--allow-remote", err)
            code, _, err = self.run_cli("--allow-remote", "check")
            self.assertEqual(code, 1)
            self.assertIn("https", err)
        self.assertEqual(self.world["gets"], [])

    def test_an_unreachable_server_is_a_refusal_not_a_traceback(self):
        with mock.patch.dict(os.environ, {"COMFY_URL": "http://127.0.0.1:9"}):
            code, _, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("cannot reach", err)

    def test_no_environment_value_is_ever_printed(self):
        with mock.patch.dict(os.environ, {"COMFY_URL": os.environ["COMFY_URL"], "SOME_SECRET_FOR_TEST": "sekrit-value-123"}):
            _, out, err = self.run_cli(*self.run_args("--confirm"))
        self.assertNotIn("sekrit-value-123", out + err)


if __name__ == "__main__":
    unittest.main()
