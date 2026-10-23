"""Tests for udgt.py on a small fake game built in a temporary folder."""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(PLUGIN / "engine"))

import udgt  # noqa: E402

GDD = """# Game design

## 3. Game design

### 3.1 Factions

Village against Cabal. See DECISIONS A2 and WORLD 4.1, and Book I.1.

### 3.2 Roles

1. The killer kills.
2. The detective reads clues (A1 to A3).

## 4. Missing

Cites GDD 3.9, which does not exist, and GDD 3.2.2, which falls back to 3.2.
"""

WORLD = """# World

## 4. World bible

### 4.1 Setting

A harbour town, planned to grow in round 8 (V2 later).

| Id | Name |
|---|---|
| `harbour` | The Harbour |
| `chapel` | St Brannock's |
"""

BIBLE = """# Brief

### BOOK I: THE TOWN

#### 1. The train

Arrives daily.

#### 2. The law

Three stages.
"""

DECISIONS = """# Decisions

## Amendments

| # | Item | Decision |
|---|---|---|
| A2 | Factions (open question 1) | **Approved.** Two factions (owner, 2026-10-10). |
| A1 | Traits | Height, scarf, hat. |
| A3 | **Quick mode removed (owner, 2026-10-23; 7J).** It leaves the game. | Open: what replaces it. |
| A4 | Reserved for 7G | |

## Open questions for the owner

1. Engine line? **Resolved 2026-10-10 (A2).**
2. Hosting?
"""

ROLES = {"gddRef": "3.2", "factions": {"village": {"name": "Village"}}, "roles": {
    "killer": {"name": "Killer", "faction": "cabal", "gddRef": "3.1", "cardText": "Strike after dark.",
               "startKit": [{"item": "knife", "qty": 1}], "abilities": ["kill"]},
    "detective": {"name": "Detective", "faction": "village", "cardText": "Read the clues."}}}

STEP = """export function step(room: Room): void {
  room.state.tick++;
  runInputs(room); // M2
  runPhases(room);
}
export const Phase = {
  lobby: 0,
  night: 1,
} as const;
export const Mode = { main: 0, quick: 1 } as const;
"""

TOKENS = """@font-face { font-family: X; src: url('../x.woff2'); }
:root {
  --g-night: #0a0924; /* the sky */
  --g-glass: rgb(37 26 107 / 0.66);
  --g-frame: url("data:image/svg+xml,%3Csvg%3E%3C/svg%3E");
  --g-photo: url('photo.png');
}
"""

COPY = """export const COPY = {
  'menu.start': 'Start game',
  'menu.quit': "Quit",
};
"""

PROFILE = {
    "udgt": 1, "name": "Fake Game", "slug": "fake-game",
    "game": {"paths": []},
    "docs": [
        {"id": "GDD", "path": "docs/GDD.md", "area": "gameplay"},
        {"id": "WORLD", "path": "docs/WORLD.md", "area": "world"},
        {"id": "DECISIONS", "path": "docs/DECISIONS.md", "area": "decisions"},
        {"glob": ["docs/round*/*.md"], "strip": ["docs/"], "area": "rounds"},
    ],
    "era_tags": ["\\((?:[Rr]ound \\d+)\\)"],
    "decisions": {"path": "docs/DECISIONS.md", "row": "^\\|\\s*(A\\d+)\\s*\\|", "number": "A(\\d+)",
                  "layouts": [{"from": 1, "to": 2, "cols": ["topic", "decision"]},
                              {"from": 3, "cols": ["decision", "open"]}],
                  "session": "\\b([5-9][A-Z])\\b(?=[,;)])", "reserved": ["Reserved for"],
                  "open_questions": {"heading": "Open questions", "resolved": "Resolved"}},
    "refs": [
        {"id": "gdd", "pattern": "\\bGDD\\s+(\\d+(?:\\.\\d+)*)", "target": "sec:GDD:{1}", "strict": True},
        {"id": "world", "pattern": "\\bWORLD\\s+(\\d+(?:\\.\\d+)*)", "target": "sec:WORLD:{1}", "strict": True},
        {"id": "decisions", "pattern": "\\bDECISIONS\\s+(A\\d+)", "target": "dec:{1}", "strict": True},
        {"id": "decision-id", "pattern": "(?<![\\w/.#-])(A\\d{1,3})(?:\\s*(?:to|-)\\s*A(?P<to>\\d{1,3}))?(?![\\w.])",
         "target": "dec:{1}", "range": True},
        {"id": "bible", "pattern": "\\bBook\\s+([IVX]+)(?:\\.(\\d+))?\\b", "target": "sec:round1/brief:BOOK {1}.{2}"},
    ],
    "tables": [{"id": "scenes", "path": "docs/WORLD.md", "under": "^4\\.1 ", "kind": "scene", "area": "world",
                "key": 0, "title": 1, "key_pattern": "^([a-z_]+)"}],
    "datasets": {"globs": ["data/*.json"], "strip": ["data/"], "ref_field": "gddRef", "ref_doc": "GDD"},
    "code": {"areas": [{"id": "server", "area": "backend", "globs": ["src/**/*.ts"], "tests": ["src/**/*.test.ts"],
                        "modules": ["src/*.ts"]}],
             "anchors": [
                 {"id": "tick", "file": "src/Step.ts", "kind": "calls", "start": "export function step(", "pattern": "^\\s*(\\w+)\\(room"},
                 {"id": "phases", "file": "src/Step.ts", "kind": "object-keys", "start": "export const Phase = {"},
                 {"id": "modes", "file": "src/Step.ts", "kind": "object-keys", "start": "export const Mode = {"}]},
    "ui": {"token_files": ["src/tokens.css"], "token_prefix": "--g-", "copy": ["src/copy/*.ts"],
           "fonts": [{"family": "Pixel", "file": "fonts/pixel.woff2"}]},
    "future": {"horizons": [{"id": "r8", "label": "Round 8", "pattern": "\\bround 8\\b"},
                            {"id": "v2", "label": "V2", "pattern": "\\bV2\\b"}]},
    "stages": [{"id": "0", "slug": "overview", "title": "Overview", "areas": ["gameplay"], "prompts": ["Why?"]},
               {"id": "1", "slug": "world", "title": "World", "areas": ["world", "future"],
                "keywords": ["quick mode"], "prompts": ["Mood?"]}],
    "explorer": {"title": "Fake", "theme": {"bg": "var(--g-night)"},
                 "views": [{"id": "title", "label": "Title", "special": "title"}]},
}


def git(cwd, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_AUTHOR_DATE="2026-10-10T10:00:00", GIT_COMMITTER_DATE="2026-10-10T10:00:00")
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, env=env)


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = udgt.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


class FakeGame(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp(prefix="udgt-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self.game = root / "game"
        self.home = root / "teardown"
        files = {
            "docs/GDD.md": GDD, "docs/WORLD.md": WORLD, "docs/DECISIONS.md": DECISIONS,
            "docs/round1/brief.md": BIBLE + "\nSee Book I.2 and Book I.\n",
            "data/roles.json": json.dumps(ROLES), "src/Step.ts": STEP, "src/Step.test.ts": "it('a', () => {});\ntest('b', () => {});\n",
            "src/tokens.css": TOKENS, "src/copy/menu.ts": COPY,
        }
        for rel, text in files.items():
            path = self.game / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        (self.game / "fonts").mkdir()
        (self.game / "fonts" / "pixel.woff2").write_bytes(b"wOF2fake")
        git(self.game, "init", "-q")
        git(self.game, "add", "-A")
        git(self.game, "commit", "-q", "-m", "Record the factions (A2)")
        git(self.game, "commit", "-q", "--allow-empty", "-m", "Merge pull request #7 from me/claude/r7-menu")
        self.home.mkdir()
        self.profile = self.home / "profile.json"
        self.profile.write_text(json.dumps(PROFILE), encoding="utf-8")

    def scan(self):
        code, out, err = run("scan", "--profile", self.profile, "--game", self.game)
        self.assertEqual(code, 0, err)
        data = json.loads((self.home / "teardown.json").read_text(encoding="utf-8"))
        return data, {n["id"]: n for n in data["nodes"]}

    def edges(self, data, src):
        return {e["to"] for e in data["edges"] if e["from"] == src}


class Scan(FakeGame):
    def test_decisions_are_keys_not_a_sequence_and_layouts_change_columns(self):
        _, nodes = self.scan()
        self.assertEqual(nodes["dec:A1"]["title"], "A1 Traits")
        self.assertEqual(nodes["dec:A2"]["meta"]["date"], "2026-10-10")
        a3 = nodes["dec:A3"]["meta"]
        self.assertEqual(a3["sessions"], ["7J"])
        self.assertTrue(a3["owner"])
        self.assertEqual(a3["open"], "Open: what replaces it.")
        self.assertIn("open:A3", nodes)
        self.assertEqual(nodes["dec:A4"]["meta"]["status"], "reserved")

    def test_open_questions_know_whether_they_were_resolved(self):
        _, nodes = self.scan()
        self.assertTrue(nodes["oq:1"]["meta"]["resolved"])
        self.assertFalse(nodes["oq:2"]["meta"]["resolved"])

    def test_book_subsections_nest_under_their_book(self):
        _, nodes = self.scan()
        self.assertIn("sec:round1/brief:BOOK I", nodes)
        self.assertIn("sec:round1/brief:BOOK I.2", nodes)

    def test_numbered_list_items_are_citable_sections(self):
        _, nodes = self.scan()
        self.assertTrue(nodes["sec:GDD:3.2"]["meta"]["number"] == "3.2")
        # "3" has items? No: the items sit under 3.2, which is not top-level, so none is made there.
        self.assertNotIn("sec:GDD:3.2.1", nodes)

    def test_citations_link_resolve_ranges_and_report_broken_strict_ones(self):
        data, nodes = self.scan()
        self.assertTrue({"dec:A2", "sec:WORLD:4.1"} <= self.edges(data, "sec:GDD:3.1"))
        self.assertTrue({"dec:A1", "dec:A2", "dec:A3"} <= self.edges(data, "sec:GDD:3.2"))
        self.assertIn("sec:GDD:3.2", self.edges(data, "sec:GDD:4"))  # 3.2.2 falls back to 3.2
        broken = {b["target"] for b in data["broken"]}
        self.assertIn("sec:GDD:3.9", broken)  # and 3.9 never falls back to chapter 3
        self.assertIn("sec:round1/brief:BOOK I.1", self.edges(data, "sec:GDD:3.1"))
        self.assertIn("sec:round1/brief:BOOK I", self.edges(data, "sec:round1/brief:BOOK I.2"))

    def test_tables_become_nodes(self):
        _, nodes = self.scan()
        self.assertEqual(nodes["scene:harbour"]["title"], "The Harbour")
        self.assertIn("scene:chapel", nodes)

    def test_datasets_keep_records_lists_and_their_design_section(self):
        data, nodes = self.scan()
        killer = nodes["rec:roles/roles/killer"]["meta"]
        self.assertEqual(killer["startKit"], ["knife 1"])
        self.assertEqual(killer["abilities"], ["kill"])
        self.assertIn("sec:GDD:3.1", self.edges(data, "rec:roles/roles/killer"))
        self.assertIn("sec:GDD:3.2", self.edges(data, "data:roles"))
        self.assertEqual(nodes["data:roles/roles"]["meta"]["count"], 2)

    def test_anchors_read_ordered_lists_out_of_code(self):
        _, nodes = self.scan()
        names = lambda i: [x["name"] for x in nodes[f"anchor:{i}"]["meta"]["items"]]
        self.assertEqual(names("tick"), ["runInputs", "runPhases"])
        self.assertEqual(names("phases"), ["lobby", "night"])
        self.assertEqual(names("modes"), ["main", "quick"])
        self.assertEqual(nodes["area:server"]["meta"]["test_cases"], 2)

    def test_tokens_keep_inline_uris_and_drop_file_links(self):
        _, nodes = self.scan()
        self.assertEqual(nodes["token:--g-night"]["meta"]["value"], "#0a0924")
        self.assertIn("token:--g-frame", nodes)
        self.assertNotIn("token:--g-photo", nodes)
        self.assertEqual(nodes["copy:menu.quit"]["text"], "Quit")

    def test_history_and_plans(self):
        data, nodes = self.scan()
        self.assertEqual(nodes["pr:7"]["meta"]["round"], 7)
        self.assertEqual(len(data["commits"]), 2)
        self.assertEqual(next(c for c in data["commits"] if "factions" in c["s"])["ids"], ["A2"])
        self.assertIn("plan:r8:WORLD:4.1", nodes)
        self.assertIn("plan:v2:WORLD:4.1", nodes)

    def test_scan_never_writes_the_game(self):
        before = subprocess.run(["git", "-C", str(self.game), "status", "--porcelain"], capture_output=True, text=True).stdout
        self.scan()
        run("build", "--profile", self.profile, "--game", self.game)
        after = subprocess.run(["git", "-C", str(self.game), "status", "--porcelain"], capture_output=True, text=True).stdout
        self.assertEqual(before, after)


class Owner(FakeGame):
    def test_record_appends_verbatim_and_never_rewrites(self):
        self.scan()
        run("record", "1", "--profile", self.profile, "--question", "Mood?", "--answer", "  Damp, quiet, watched.  ")
        run("record", "world", "--profile", self.profile, "--question", "Again?", "--answer", "Yes")
        book = json.loads((self.home / "answers.json").read_text(encoding="utf-8"))
        self.assertEqual([a["answer"] for a in book["answers"]], ["Damp, quiet, watched.", "Yes"])
        self.assertEqual({a["stage"] for a in book["answers"]}, {"1"})
        code, _, err = run("record", "1", "--profile", self.profile, "--question", "Q", "--answer", " ")
        self.assertEqual(code, 2)
        self.assertEqual(len(json.loads((self.home / "answers.json").read_text(encoding="utf-8"))["answers"]), 2)

    def test_brief_lists_prompts_gaps_and_prior_answers(self):
        self.scan()
        run("record", "1", "--profile", self.profile, "--question", "Mood?", "--answer", "Damp")
        code, out, _ = run("brief", "1", "--profile", self.profile, "--json")
        brief = json.loads(out)
        self.assertEqual(brief["prompts"], ["Mood?"])
        self.assertIn("open:A3", [g["id"] for g in brief["gaps"]])
        self.assertEqual(brief["answered"][0]["answer"], "Damp")

    def test_check_flags_chapter_links_that_point_nowhere(self):
        self.scan()
        (self.home / "chapters").mkdir()
        (self.home / "chapters" / "00-overview.md").write_text("# Overview\n\nSee [[dec:A2]] and [[dec:A99]].\n", encoding="utf-8")
        code, out, _ = run("check", "--profile", self.profile, "--game", self.game, "--json", "--strict")
        found = json.loads(out)
        links = [f for f in found if f["kind"] == "chapter-link"]
        self.assertEqual(len(links), 1)
        self.assertIn("dec:A99", links[0]["what"])
        self.assertEqual(code, 1)

    def test_query_and_show(self):
        self.scan()
        code, out, _ = run("query", "quick mode", "--profile", self.profile)
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("dec:A3"))
        code, out, _ = run("show", "dec:A2", "--profile", self.profile, "--json")
        shown = json.loads(out)
        self.assertEqual([c["h"] for c in shown["commits"]].__len__(), 1)
        self.assertIn("sec:GDD:3.1", [e["from"] for e in shown["in"]])
        self.assertEqual(run("query", "zzzz", "--profile", self.profile)[0], 1)


class Build(FakeGame):
    def test_build_themes_the_page_with_the_games_tokens_and_fonts(self):
        self.scan()
        code, _, err = run("build", "--profile", self.profile, "--game", self.game)
        self.assertEqual(code, 0, err)
        out = self.home / "explorer"
        theme = (out / "theme.css").read_text(encoding="utf-8")
        self.assertIn("--g-night: #0a0924;", theme)
        self.assertIn("--x-bg: var(--g-night);", theme)
        self.assertIn("url('fonts/pixel.woff2')", theme)
        self.assertTrue((out / "fonts" / "pixel.woff2").is_file())
        self.assertEqual(json.loads((out / "chapters.json").read_text(encoding="utf-8")), {"chapters": []})

    def test_the_page_reads_only_local_json(self):
        js = (PLUGIN / "explorer" / "explorer.js").read_text(encoding="utf-8")
        fetched = set(re.findall(r"getJSON\('([^']+)'", js))
        self.assertEqual(fetched, {"../teardown.json", "chapters.json", "../answers.json"})
        for name in ("index.html", "explorer.css", "explorer.js"):
            text = (PLUGIN / "explorer" / name).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(src|href)=[\"']https?://", name)
            self.assertNotIn("@import", text, name)


class Plugin(unittest.TestCase):
    def test_nothing_in_the_plugin_names_a_particular_repository(self):
        for path in PLUGIN.rglob("*"):
            if path.is_dir() or path.suffix in (".pyc", ".woff2") or path.name == "plugin.json" or "tests" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for word in ("Who-Did-It", "Who Did It", "Pipelines-Plugin", ".claude/skills"):
                if path.name == "README.md" and word == "Pipelines-Plugin":
                    continue  # the install line names the marketplace
                self.assertNotIn(word, text, f"{path.relative_to(PLUGIN)} names {word}")

    def test_skills_use_the_plugin_root(self):
        for skill in (PLUGIN / "skills").glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            front = text.split("---")[1]
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", front)
            self.assertIn("${CLAUDE_PLUGIN_ROOT}/engine/udgt.py", text)


REAL = PLUGIN.parent.parent / "teardowns" / "who-did-it" / "profile.json"


@unittest.skipUnless(REAL.exists() and any((REAL.parent / p).is_dir() for p in json.loads(REAL.read_text(encoding="utf-8")).get("game", {}).get("paths", [])) if REAL.exists() else False,
                     "the real teardown or its game checkout is not here")
class RealGame(unittest.TestCase):
    def test_the_real_profile_scans_into_the_expected_shape(self):
        prof = udgt.profiles.load(REAL)
        game = udgt.profiles.game_root(prof)
        data = udgt.compose(prof, game)
        counts = data["counts"]
        self.assertGreaterEqual(counts.get("decision", 0), 100)
        self.assertGreaterEqual(counts.get("scene", 0), 25)
        ids = {n["id"] for n in data["nodes"]}
        self.assertIn("anchor:tick-order", ids)
        self.assertIn("sec:round6/owner-brief:BOOK I.3", ids)


if __name__ == "__main__":
    unittest.main()
