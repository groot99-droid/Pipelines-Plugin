"""The hub server: what it serves, what it refuses, and the one thing it writes.

Runs serve.py in a thread on a free port against the temporary studio of
StudioCase. The page's stylesheet is checked against the real tokens.json:
every custom property it uses is a token, and no literal value appears.
"""

import json
import re
import sys
import threading
import unittest
import urllib.error
import urllib.request

from helpers import GOOD_NOTE, NOTE, PIPELINE, StudioCase, precedent

HUB = PIPELINE.parent / "hub"
sys.path.insert(0, str(HUB))
import serve  # noqa: E402

TOKENS = {
    "mutation_policy": "the author commits; an agent proposes",
    "color": {"bg": {"base": "#000000", "panel": "#101010"}, "ink": {"base": "#FFFFFF"},
              "accent": {"cyan": "#00E5FF"}},
    "border": {"hairline": "1px solid {color.ink.base}", "rule": "structure is a line — prose"},
}


class HubCase(StudioCase):
    def setUp(self):
        super().setUp()
        (self.context / "tokens.json").write_text(json.dumps(TOKENS), encoding="utf-8")
        self.place(NOTE, GOOD_NOTE)
        self.place("aurora/design/harbor-dusk.md", precedent("harbor-dusk", kind="design"))
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.index_path = self.root / "index.json"
        self.server = serve.make_server(0, env=self.env, repo=self.repo, index_path=self.index_path, quiet=True)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def get(self, path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data=data, method=method,
                                         headers={"Content-Type": "application/json"} if data else {})
        try:
            with urllib.request.urlopen(request, timeout=5) as reply:
                return reply.status, reply.read(), reply.headers.get("Content-Type", "")
        except urllib.error.HTTPError as err:
            return err.code, err.read(), err.headers.get("Content-Type", "")

    def json(self, path, **kwargs):
        status, body, _ = self.get(path, **kwargs)
        return status, json.loads(body)


class Routes(HubCase):
    def test_the_page_is_served_from_the_hub_folder(self):
        status, body, ctype = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"ROSW", body)
        self.assertIn("text/html", ctype)
        for name in ("app.js", "styles.css"):
            self.assertEqual(self.get(f"/{name}")[0], 200)

    def test_nothing_outside_the_hub_folder_is_served(self):
        for path in ("/../pipeline/spec.yaml", "/%2e%2e/pipeline/spec.yaml", "/..%2f..%2fCLAUDE.md",
                     "/launcher/../../pipeline/studio_run.py", "/../../CLAUDE.md"):
            status, body, _ = self.get(path)
            with self.subTest(path=path):
                self.assertEqual(status, 404, body[:80])
                self.assertNotIn(b"pipelines:", body)

    def test_notes_are_the_vault_rows(self):
        status, rows = self.json("/api/notes")
        self.assertEqual(status, 200)
        self.assertEqual(sorted(r["path"] for r in rows), ["aurora/design/harbor-dusk.md", NOTE])
        self.assertNotIn("body", rows[0])

    def test_search_needs_the_index_and_then_answers(self):
        status, reply = self.json("/api/search?q=console")
        self.assertEqual(status, 400)
        self.assertIn("no index", reply["error"])
        import vault_index
        from studio_common import write_text
        write_text(self.index_path, json.dumps(vault_index.build_index(self.env)))
        status, hits = self.json("/api/search?q=console&top=3")
        self.assertEqual(status, 200)
        self.assertEqual(hits[0]["path"], NOTE)
        self.assertEqual(set(hits[0]), {"score", "path", "title", "heading", "preview"})

    def test_runs_gates_pipelines_and_tokens(self):
        run_id = self.new_run()
        status, runs = self.json("/api/runs")
        self.assertEqual(status, 200)
        self.assertEqual([r["run_id"] for r in runs], [run_id])
        self.assertEqual(runs[0]["next_stage"], "intake")

        status, gates = self.json("/api/gates")
        self.assertEqual(status, 200)
        by_name = {g["gate"]: g for g in gates}
        self.assertEqual(set(by_name), set(self.env.spec["gates"]))
        self.assertTrue(by_name["fixture_look"]["authored"])
        self.assertEqual(by_name["fixture_look"]["unresolved"][0]["topic"], "generated imagery")
        self.assertFalse(by_name["fixture_voice"]["authored"])
        self.assertIn("ui-direction", by_name["fixture_look"]["needed_by"])

        status, pipelines = self.json("/api/pipelines")
        self.assertEqual(status, 200)
        self.assertEqual({p["pipeline"] for p in pipelines}, set(self.env.spec["pipelines"]))

        status, tokens = self.json("/api/tokens")
        self.assertEqual(status, 200)
        self.assertEqual(tokens["color"]["bg"]["base"], "#000000")

    def test_writing_is_titles_only_and_absent_until_built(self):
        status, data = self.json("/api/writing")
        self.assertEqual((status, data["files"]), (200, []))
        index = self.repo / "creative-writing" / "vault" / "tools" / "rag_index" / "index.json"
        index.parent.mkdir(parents=True)
        index.write_text(json.dumps({"built": "2026-09-30", "chunks": [
            {"file": "03_Stories/06_Melting_Away.md", "source_type": "work", "text": "THE PROSE ITSELF"},
            {"file": "03_Stories/06_Melting_Away.md", "source_type": "work", "text": "more prose"},
        ]}), encoding="utf-8")
        status, data = self.json("/api/writing")
        self.assertEqual(status, 200)
        self.assertEqual(data["files"], [{"file": "03_Stories/06_Melting_Away.md", "source_type": "work",
                                          "kind": "03_Stories"}])
        self.assertNotIn("PROSE", json.dumps(data))

    def test_an_unknown_route_is_404(self):
        self.assertEqual(self.json("/api/nothing")[0], 404)


class NewRun(HubCase):
    def test_post_creates_a_run_through_the_bookkeeper(self):
        status, made = self.json("/api/runs", method="POST", body={"pipeline": "ui-direction", "title": "Hub page"})
        self.assertEqual(status, 201, made)
        run_id = made["run"]["run_id"]
        self.assertTrue(run_id.startswith("hub-page-"))
        self.assertIn(run_id, made["command"])
        self.assertTrue((self.runs / run_id / "state.json").is_file())
        self.assertEqual(self.state(run_id)["pipeline"], "ui-direction")

    def test_a_pipeline_that_is_not_implemented_is_refused(self):
        status, reply = self.json("/api/runs", method="POST", body={"pipeline": "still-image", "title": "x"})
        self.assertEqual(status, 400)
        self.assertIn("not_yet_implemented", reply["error"])
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_a_bad_body_is_refused(self):
        for body in ({}, {"pipeline": "ui-direction"}, {"pipeline": "nope", "title": "x"}, ["list"]):
            status, reply = self.json("/api/runs", method="POST", body=body)
            with self.subTest(body=body):
                self.assertEqual(status, 400)
                self.assertIn("error", reply)
        self.assertEqual(self.json("/api/notes", method="POST", body={})[0], 404)

    def test_the_hub_writes_nothing_into_the_vault(self):
        before = sorted(p.as_posix() for p in self.vault.rglob("*"))
        self.json("/api/runs", method="POST", body={"pipeline": "ui-direction", "title": "Hub page"})
        for route in ("/api/notes", "/api/gates", "/api/runs", "/api/tokens", "/api/writing"):
            self.json(route)
        self.assertEqual(sorted(p.as_posix() for p in self.vault.rglob("*")), before)


class Stylesheet(unittest.TestCase):
    """The page is a studio surface: tokens are law."""

    @classmethod
    def setUpClass(cls):
        real = HUB.parent / "vault" / "_Context" / "brand" / "tokens.json"
        cls.tokens = json.loads(real.read_text(encoding="utf-8"))
        cls.css = (HUB / "styles.css").read_text(encoding="utf-8")
        cls.css = re.sub(r"/\*.*?\*/", "", cls.css, flags=re.S)

    @staticmethod
    def flatten(tokens):
        """The same rule app.js applies: a.b.c -> --a-b-c, dots and underscores
        in a key become hyphens, prose values (a dash or an angle bracket) are
        not CSS and are left out."""
        flat = {}

        def walk(value, path):
            if isinstance(value, dict):
                for key, inner in value.items():
                    walk(inner, path + [key])
            elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
                text = str(value)
                if not re.search(r"[—<>]", text):
                    flat["--" + re.sub(r"[._]", "-", "-".join(path))] = text

        walk(tokens, [])
        return flat

    def test_every_custom_property_is_a_token(self):
        flat = self.flatten(self.tokens)
        used = set(re.findall(r"var\((--[a-z0-9-]+)\)", self.css))
        self.assertTrue(used)
        self.assertEqual(sorted(used - set(flat)), [])

    def test_no_literal_colour_size_or_font(self):
        self.assertNotRegex(self.css, r"#[0-9a-fA-F]{3,8}\b")
        self.assertNotRegex(self.css, r"\b(rgb|hsl|oklch)a?\(")
        self.assertNotRegex(self.css, r"\d(px|rem|em|pt)\b")
        for family in re.findall(r"font-family:\s*([^;]+)", self.css):
            self.assertTrue(family.strip().startswith("var("), family)

    def test_the_page_loads_no_remote_resource(self):
        page = (HUB / "index.html").read_text(encoding="utf-8")
        script = (HUB / "app.js").read_text(encoding="utf-8")
        for text in (page, script, self.css):
            self.assertNotRegex(text, r"https?://(?!127\.0\.0\.1)")


if __name__ == "__main__":
    unittest.main()
