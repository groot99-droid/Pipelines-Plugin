"""The Writing Museum builder: adapter, mapping, layout and lint.

Runs against a temporary vault and temporary scene specs; the real vault is read
once, read-only, to check that the ten-work path works on real data. Nothing is
written under writing-museum/data/ or creative-writing/vault/.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUILD))

import build_museum  # noqa: E402
import layout  # noqa: E402
import library  # noqa: E402
import works  # noqa: E402

REPO = BUILD.parent.parent
REAL_VAULT = REPO / "creative-writing" / "vault"

WORK = """---
title: "The Lantern Room"
type: story
mode: horror-prose
genre: [horror]
status: complete
themes: [isolation, threshold]
tags: [type/story, mode/horror-prose]
---
# The Lantern Room
**Type:** Short story  
**Source:** `Master_Volume_9`, lines 1–3  
**Text:** complete and verbatim.

---
The house had one room nobody used. """ + " ".join(["The lantern burned in it all night, and nobody had lit it."] * 20) + """

She counted the doors again. """ + " ".join(["There were six, and there had been five."] * 25) + """

No wind. No insects. Nothing.
"""

POEM = """---
title: "Small Hours"
type: poem
mode: confessional-poetry
themes: [grief]
---
# Small Hours

I kept the clock you stopped.
I kept the coat, the key, the cup.
""" + "\n".join(["I kept the words you never said, and said them for you."] * 40) + "\n"

STORIES_INDEX = """---
title: "Stories — Index"
type: moc
folder: 03_Stories
tags: [moc]
---

Short and flash fiction — mostly horror.

- [[03_Stories/01_The_Lantern_Room|The Lantern Room]] — a house with one room nobody used, and a lantern nobody lit; see [[02_Novels/01_Other|the other one]] → annotation: [[_Annotations/03_Stories/01_The_Lantern_Room|notes]]
"""


def sidecar_for(vault, rel):
    """A sidecar in the tagger's shape for a work in the temp vault, tagging every chunk dread/threshold."""
    w = works.read_work(rel, vault)
    chunks = []
    for ch in w["chunks"]:
        chunks.append({"chunk_index": ch["index"], "heading": ch["heading"], "start_line": ch["start_line"],
                       "end_line": ch["end_line"], "content_fingerprint": ch["fingerprint"],
                       "plot_tags": ["opening-hook"], "context_tags": ["isolation"],
                       "mood_tags": ["dread", "unease"], "motif_tags": ["threshold"], "notes": "a test chunk"})
    path = vault / "_ChunkTags" / (rel + ".tags.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"file": rel, "chunks": chunks}), encoding="utf-8")


class TempVault(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="writing-museum-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.vault = self.root / "vault"
        (self.vault / "03_Stories").mkdir(parents=True)
        (self.vault / "07_Poems_and_Prose").mkdir(parents=True)
        (self.vault / "tools").mkdir()
        shutil.copy(REAL_VAULT / "tools" / "vault_search.py", self.vault / "tools" / "vault_search.py")
        (self.vault / "03_Stories" / "01_The_Lantern_Room.md").write_text(WORK, encoding="utf-8")
        (self.vault / "07_Poems_and_Prose" / "01_Small_Hours.md").write_text(POEM, encoding="utf-8")
        sidecar_for(self.vault, "03_Stories/01_The_Lantern_Room.md")
        (self.vault / "03_Stories" / "_index.md").write_text(STORIES_INDEX, encoding="utf-8")
        self.scenes = self.root / "scenes"
        self.scenes.mkdir()
        self.out = self.root / "out"

    def spec(self, sid="the-lantern-room", rel="03_Stories/01_The_Lantern_Room.md", order=1, **extra):
        spec = {"id": sid, "order": order, "work": rel, "hub_side": "S" if order % 2 else "N", "panels": "all"}
        spec.update(extra)
        (self.scenes / f"{sid}.json").write_text(json.dumps(spec), encoding="utf-8")
        return spec


class Adapter(TempVault):
    def test_a_work_becomes_verbatim_panels(self):
        w = works.read_work("03_Stories/01_The_Lantern_Room.md", self.vault)
        self.assertEqual(w["title"], "The Lantern Room")
        self.assertGreaterEqual(len(w["chunks"]), 2)
        self.assertTrue(all(ch["tagged"] for ch in w["chunks"]))
        e = works.entry_for({"id": "lantern", "work": "03_Stories/01_The_Lantern_Room.md"}, w, self.vault)
        body = WORK.split("---\n", 2)[2]
        for p in e["works"]:
            self.assertIn(" ".join(p["text"].split()), " ".join(body.split()))
            self.assertEqual(p["tags"]["mood_tags"], ["dread", "unease"])
            a, b = p["credit"]["lines"]
            self.assertLessEqual(a, b)
            self.assertIn("lines", p["location"])
        self.assertEqual(e["room"], "lantern")
        self.assertEqual(e["wing"], "writing")

    def test_the_transcription_header_is_left_off_the_panel(self):
        w = works.read_work("03_Stories/01_The_Lantern_Room.md", self.vault)
        first = w["chunks"][0]["text"]
        self.assertTrue(first.startswith("The house had one room"), first[:60])
        self.assertNotIn("**Source:**", first)
        self.assertEqual(works.strip_header("# T\n**Type:** x\n---\nProse here.\n\nMore."), "Prose here.\n\nMore.")
        self.assertEqual(works.strip_header("**Type:** x\n**Note:** Chapter One: The Dunes.\n\n---\nIntroduction\n\nProse."), "Introduction\n\nProse.")
        self.assertFalse(works.is_header_line("**Bold** words inside prose are not a label."))

    def test_file_lines_point_into_the_file(self):
        w = works.read_work("03_Stories/01_The_Lantern_Room.md", self.vault)
        lines = WORK.splitlines()
        for ch in w["chunks"]:
            a, b = ch["file_lines"]
            self.assertEqual(lines[a - 1].strip(), ch["text"].split("\n")[0].strip())
            self.assertEqual(lines[b - 1].strip(), ch["text"].split("\n")[-1].strip())

    def test_a_long_chunk_is_split_without_changing_a_word(self):
        w = works.read_work("07_Poems_and_Prose/01_Small_Hours.md", self.vault)
        text = w["chunks"][0]["text"]
        parts = works.split_long(text, 60)
        self.assertGreater(len(parts), 1)
        self.assertEqual(" ".join(" ".join(parts).split()), " ".join(text.split()))
        e = works.entry_for({"id": "small-hours", "work": "07_Poems_and_Prose/01_Small_Hours.md"}, w, self.vault)
        self.assertTrue(all(p["dims"]["type"] == "poem" for p in e["works"]))
        self.assertTrue(all(p["dims"]["w_m"] == works.WIDTHS["verse"] for p in e["works"]))

    def test_panel_height_follows_the_text(self):
        short = works.panel_dims("Nothing.", False)
        long = works.panel_dims(" ".join(["word"] * 250), False)
        self.assertEqual(short["type"], "panel-short")
        self.assertLess(short["h_m"], long["h_m"])
        self.assertLessEqual(long["h_m"], works.MAX_H)

    def test_selecting_a_chunk_that_does_not_exist_is_refused(self):
        with self.assertRaises(ValueError):
            works.entry_for({"id": "x", "work": "03_Stories/01_The_Lantern_Room.md", "panels": [99]}, vault=self.vault)

    def test_the_slug_drops_the_number_prefix(self):
        self.assertEqual(works.slug_of("03_Stories/06_Melting_Away.md"), "melting-away")
        self.assertEqual(works.slug_of("02_Novels/05_The_Endless_Temple_-_Elaris_Sel_Marden.md"), "the-endless-temple-elaris-sel-marden")


class Proposal(TempVault):
    def test_every_value_names_its_source(self):
        p = build_museum.propose("03_Stories/01_The_Lantern_Room.md", "lantern", 3, self.vault)
        s = p["spec"]
        self.assertEqual(s["hub_side"], "S")
        self.assertEqual(set(s["style"]), set(s["sources"]))
        self.assertEqual(s["style"]["theme"], "cast-iron-glass")
        self.assertIn("mode.horror-prose", s["sources"]["theme"])
        self.assertIn("mood.dread", s["sources"]["wall"])
        self.assertIn("motif.threshold", s["sources"]["floor"])
        self.assertEqual(layout.style_errors(layout.style_of(s), "lantern"), [])

    def test_an_untagged_work_falls_back_to_defaults_and_says_so(self):
        p = build_museum.propose("07_Poems_and_Prose/01_Small_Hours.md", "small-hours", 2, self.vault)
        self.assertEqual(p["work"]["untagged_chunks"], [1])
        self.assertIn("DEFAULT_STYLE", p["spec"]["sources"]["wall"])
        self.assertEqual(p["spec"]["hub_side"], "N")

    def test_the_mapping_names_only_things_the_viewer_has(self):
        m = build_museum.load_mapping()
        for row in m["mode"].values():
            self.assertIn(row["theme"], layout.THEMES)
            self.assertIn(row["frame"], layout.FRAME)
            self.assertIn(row["frame_small"], layout.FRAME)
        for row in m["motif"].values():
            self.assertIn(row["floor"], layout.FLOORS)
            self.assertIn(row["trim"], layout.TRIMS)
        for mood, row in m["mood"].items():
            self.assertEqual(layout.style_errors(layout.style_of({"style": row}), mood), [])
        vocab = (REAL_VAULT / "_ChunkTags" / "vocabulary.yaml").read_text(encoding="utf-8")
        for tag in list(m["mood"]) + list(m["motif"]):
            self.assertIn(f"- {tag}", vocab, f"{tag} is not in the closed vocabulary")


class Build(TempVault):
    def test_no_scenes_builds_the_hall_alone(self):
        code = build_museum.build(self.scenes, self.out, lint_only=False, vault=self.vault)
        self.assertEqual(code, 0)
        manifest = json.loads((self.out / "museum-manifest.json").read_text(encoding="utf-8"))
        lay = json.loads((self.out / "museum-layout.json").read_text(encoding="utf-8"))
        self.assertEqual([r["id"] for r in manifest["rooms"]], ["hub"])
        self.assertEqual(list(lay["scenes"]), ["hub"])
        self.assertEqual(lay["scenes"]["hub"]["doors"], [])

    def test_two_scenes_lay_out_and_lint(self):
        self.spec("the-lantern-room", order=1, style={"theme": "cast-iron-glass", "wall": "#2f2224"})
        self.spec("small-hours", "07_Poems_and_Prose/01_Small_Hours.md", order=2)
        code = build_museum.build(self.scenes, self.out, lint_only=False, vault=self.vault)
        self.assertEqual(code, 0)
        manifest = json.loads((self.out / "museum-manifest.json").read_text(encoding="utf-8"))
        lay = json.loads((self.out / "museum-layout.json").read_text(encoding="utf-8"))
        self.assertEqual(lay["order"], ["the-lantern-room", "small-hours"])
        self.assertEqual({d["target"] for d in lay["scenes"]["hub"]["doors"]}, {"the-lantern-room", "small-hours"})
        self.assertEqual({d["hub_side"] for d in lay["scenes"]["hub"]["doors"]}, {"S", "N"})
        room = lay["scenes"]["the-lantern-room"]
        panels = [w for a in manifest["artists"] if a["room"] == "the-lantern-room" for w in a["works"]]
        self.assertEqual(set(room["hangs"]), {p["id"] for p in panels})
        self.assertEqual(room["style"]["theme"], "cast-iron-glass")
        self.assertEqual(room["style"]["wall"], "#2f2224")
        self.assertEqual([d["target"] for d in room["doors"]], ["hub", "small-hours"])
        self.assertTrue(all(not f.get("model") for f in room["fx"]))
        self.assertEqual(room["props"], [])
        self.assertEqual(manifest["wings"][0]["rooms"], ["the-lantern-room", "small-hours"])
        self.assertTrue(all(w["text"] and w["image"] is None for a in manifest["artists"] for w in a["works"]))

    def test_a_bad_style_fails_the_lint_and_writes_nothing(self):
        self.spec("the-lantern-room", style={"theme": "glass-cathedral"})
        code = build_museum.build(self.scenes, self.out, lint_only=False, vault=self.vault)
        self.assertEqual(code, 1)
        self.assertFalse(self.out.exists())

    def test_a_spec_whose_file_name_is_not_its_id_is_refused(self):
        (self.scenes / "other.json").write_text(json.dumps({"id": "lantern", "work": "03_Stories/01_The_Lantern_Room.md"}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            build_museum.load_specs(self.scenes)

    def test_check_reports_a_missing_work(self):
        spec = self.spec("ghost", rel="03_Stories/99_Nothing.md")
        errors = build_museum.spec_errors(spec, self.vault)
        self.assertTrue(any("not in the vault" in e for e in errors))

    def test_the_lint_catches_overlaps(self):
        self.spec("the-lantern-room")
        out = build_museum.compose(build_museum.load_specs(self.scenes), self.vault)
        room = out["layout_result"]["layout"]["scenes"]["the-lantern-room"]
        hangs = list(room["hangs"].values())
        if len(hangs) > 1:
            hangs[1]["along"] = hangs[0]["along"]
            hangs[1]["pos"][2] = hangs[0]["pos"][2]
            hangs[1]["wall"] = hangs[0]["wall"]
        errors = layout.lint(out["layout_result"], out["entries"], out["room_specs"])
        self.assertTrue(any("overlap" in e for e in errors))


class Library(TempVault):
    """data/library.json: every work of the vault, with a room or without, and every scene."""

    def test_every_work_is_in_the_library_whether_or_not_it_has_a_room(self):
        self.spec("the-lantern-room", order=1)
        lib = library.compose(build_museum.load_specs(self.scenes), self.vault)
        self.assertEqual([w["path"] for w in lib["works"]],
                         ["03_Stories/01_The_Lantern_Room.md", "07_Poems_and_Prose/01_Small_Hours.md"])
        self.assertEqual([f["folder"] for f in lib["folders"]], ["03_Stories", "07_Poems_and_Prose"])
        lantern, hours = lib["works"]
        self.assertEqual(lantern["scene"], "the-lantern-room")
        self.assertIsNone(hours["scene"])
        self.assertEqual(lantern["slug"], "the-lantern-room")
        self.assertEqual((lantern["type"], lantern["mode"], lantern["themes"]), ("story", "horror-prose", ["isolation", "threshold"]))
        self.assertEqual(hours["type"], "poem")
        self.assertNotIn("tags", lantern)   # the frontmatter's Obsidian tags are not carried

    def test_the_folder_index_gives_the_name_the_description_and_the_blurbs(self):
        lib = library.compose([], self.vault)
        stories, poems = lib["folders"]
        self.assertEqual((stories["name"], stories["about"]), ("Stories", "Short and flash fiction — mostly horror."))
        self.assertEqual(lib["works"][0]["blurb"], "a house with one room nobody used, and a lantern nobody lit; see the other one.")
        self.assertEqual((poems["name"], poems["about"]), ("Poems and Prose", ""))   # no _index.md: named from the folder
        self.assertEqual(lib["works"][1]["blurb"], "")
        self.assertEqual(library.folder_name("09_Dream_Journal", {"title": "09_Dream_Journal — Index"}), "Dream Journal")

    def test_passages_are_the_vault_chunks_verbatim_without_the_header(self):
        lib = library.compose([], self.vault)
        lantern = lib["works"][0]
        w = works.read_work("03_Stories/01_The_Lantern_Room.md", self.vault)
        self.assertEqual([p["text"] for p in lantern["passages"]], [ch["text"] for ch in w["chunks"]])
        self.assertEqual([p["lines"] for p in lantern["passages"]], [ch["file_lines"] for ch in w["chunks"]])
        body = WORK.split("---\n", 2)[2]
        for p in lantern["passages"]:
            self.assertIn(" ".join(p["text"].split()), " ".join(body.split()))
            self.assertNotIn("**Source:**", p["text"])
            self.assertEqual(p["tags"]["mood_tags"], ["dread", "unease"])
            self.assertTrue(p["tagged"])
        self.assertFalse(lib["works"][1]["passages"][0]["tagged"])

    def test_scenes_carry_the_spec_the_panel_count_the_room_size_and_the_note(self):
        self.spec("small-hours", "07_Poems_and_Prose/01_Small_Hours.md", order=2)
        self.spec("the-lantern-room", order=1, style={"theme": "cast-iron-glass", "wall": "#2f2224"}, sources={"wall": "a test"})
        specs = build_museum.load_specs(self.scenes)
        composed = build_museum.compose(specs, self.vault)
        lib = library.compose(specs, self.vault, composed)
        self.assertEqual([s["id"] for s in lib["scenes"]], ["the-lantern-room", "small-hours"])
        lantern = lib["scenes"][0]
        self.assertEqual(lantern["style"]["wall"], "#2f2224")
        self.assertEqual(lantern["sources"], {"wall": "a test"})
        self.assertEqual(lantern["passages"], len(next(e for e in composed["entries"] if e["slug"] == "the-lantern-room")["works"]))
        self.assertEqual(lantern["size"], composed["layout_result"]["layout"]["scenes"]["the-lantern-room"]["size"])
        self.assertEqual(lantern["note"], "studio/vault/writing-museum/3d/the-lantern-room.md")
        self.assertEqual(lantern["slug"], "the-lantern-room")
        self.assertTrue(lantern["intro"]["summary"])
        without = library.compose(specs, self.vault)   # no composed result: counted here, size unknown
        self.assertEqual(without["scenes"][0]["passages"], lantern["passages"])
        self.assertEqual(without["scenes"][0]["size"], [])

    def test_build_writes_the_library_and_lint_does_not(self):
        self.spec("the-lantern-room")
        self.assertEqual(build_museum.build(self.scenes, self.out, lint_only=True, vault=self.vault), 0)
        self.assertFalse(self.out.exists())
        self.assertEqual(build_museum.build(self.scenes, self.out, lint_only=False, vault=self.vault), 0)
        lib = json.loads((self.out / "library.json").read_text(encoding="utf-8"))
        self.assertEqual(len(lib["works"]), 2)
        self.assertEqual([s["id"] for s in lib["scenes"]], ["the-lantern-room"])
        self.assertEqual(lib["scenes"][0]["size"], [10.0, 8.0])
        self.assertEqual(lib["source"], "creative-writing/vault")

    def test_the_page_reads_only_the_library(self):
        web = BUILD.parent / "web"
        page = (web / "explore.html").read_text(encoding="utf-8")
        script = (web / "js" / "explore.js").read_text(encoding="utf-8")
        css = (web / "css" / "explore.css").read_text(encoding="utf-8")
        self.assertIn("../data/library.json", script)
        self.assertNotIn("museum-manifest", script)
        for text in (page, script, css):
            self.assertNotRegex(text, r"https?://")
        self.assertIn('href="explore.html"', (web / "index.html").read_text(encoding="utf-8"))


@unittest.skipUnless((REAL_VAULT / "tools" / "vault_search.py").is_file(), "the creative-writing vault is not beside this tool")
class RealVault(unittest.TestCase):
    """Read-only: the proposal path on the real vault, for one work of each mode."""

    def test_the_library_lists_the_63_works_and_every_scene_is_one_of_them(self):
        rels = library.list_works(REAL_VAULT)
        self.assertEqual(len(rels), 63)
        self.assertTrue(all(rel.endswith(".md") and not rel.endswith("_index.md") for rel in rels))
        scenes = build_museum.SCENES
        if scenes.is_dir():
            for spec in build_museum.load_specs(scenes):
                self.assertIn(spec["work"], rels)

    def test_a_real_work_proposes_a_valid_style(self):
        for rel in ("03_Stories/06_Melting_Away.md", "11_Essays/02_The_Architecture_of_Being.md",
                    "07_Poems_and_Prose/05_Inherited.md", "02_Novels/02_WrymWretch.md"):
            with self.subTest(work=rel):
                p = build_museum.propose(rel, None, 1)
                self.assertEqual(layout.style_errors(layout.style_of(p["spec"]), rel), [])
                self.assertEqual(p["work"]["untagged_chunks"], [])
                self.assertTrue(p["panels"])


if __name__ == "__main__":
    unittest.main()
