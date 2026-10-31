"""vault/tools/brush_search.py: the tokenizer, the vocabulary, the index, the
search and `similar`, the filters and the command line (docs/CONTRACTS.md F9
and F11).

Every test builds a small synthetic catalog and vault in a temporary folder
(`make_world`). The one exception is `RealCatalog`, which is skipped unless the
repository's catalog exists, reads it without writing anything, and asserts
only relevance sanity, never exact ids.

    python -m unittest discover -s brushes/pipeline/tests -p "test_brush_*.py"
"""

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402

BRUSHES = PIPELINE.parent
TOOLS = BRUSHES / "vault" / "tools"
SEARCH = TOOLS / "brush_search.py"
REAL_VOCABULARY = BRUSHES / "vault" / "_BrushTags" / "vocabulary.yaml"
REAL_CATALOG = BRUSHES / "catalog"


def load_tool(name):
    """Load a vault tool the way the servers do: by path, no package."""
    spec = importlib.util.spec_from_file_location(f"_test_{name}", TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(TOOLS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(TOOLS))
    return module


bs = load_tool("brush_search")

try:
    import yaml
except ImportError:
    yaml = None


# ── a synthetic catalog and vault ────────────────────────────────────────────

VOCABULARY = """\
# a small closed vocabulary for the tests
medium_tags:
  - nib-pen        # a hard nib [also: fountain pen, dip pen, quill]
  - charcoal       # coarse crumbly black [also: conte, vine]
  - watercolor     # a transparent wash [also: watercolour, aquarelle]
mark_tags:
  - line           # a continuous stroke
  - stipple        # fine dots [also: stippling, dots]
  - picture-stamp  # one picture per tap [also: stamp, stamps]
texture_tags:
  - paper-tooth    # fine speckle [also: grainy, tooth]
  - smooth         # no variation
  - gritty         # coarse specks
edge_tags:
  - crisp          # a clean boundary
  - soft           # fades out
motif_tags:
  - fruit-vegetable  # produce [also: pumpkin, berries, food]
  - flower           # blooms
use_tags:
  - line-art       # final linework [also: inking, inker, ink]
  - shading        # building tone [also: shader, shade]
  - decorating     # placing pictures
"""

NOTE_FIXTURE_LINES = ("kind", "shape", "grain", "size")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def facets_for(kind="stroke", spacing=0.01, taper="none", size="fine", era="E3", **more):
    stamp = kind == "stamp"
    spacing_class = "continuous" if spacing <= 0.02 else "tight" if spacing <= 0.1 else "visible" if spacing <= 0.5 \
        else "dotted"
    facets = {"kind": kind, "is_stamp": stamp, "spacing": spacing, "spacing_class": spacing_class,
              "taper": taper, "size_class": size, "era": era, "family": "legacy", "has_grain": True,
              "translucent": False, "grain_contrast": None, "shape_coverage": None, "dual": False}
    facets.update(more)
    words = [kind, f"spacing-{spacing_class}", f"size-{size}", f"era-{era.lower()}"]
    if taper != "none":
        words.append(f"taper-{taper}")
    return facets, words


# name, set, spacing, kind, taper, size, extra settings
SPECS = [
    # the "inks" set (user, vendor pack)
    {"name": "Dry Ink Pen", "set": "inks", "spacing": 0.010, "taper": "both", "size": "fine",
     "settings": {"maxSize": 0.20, "dynamicsPressureSize": 0.9, "shapeScatter": 0.0, "blendMode": 0}},
    {"name": "Wet Ink Brush", "set": "inks", "spacing": 0.012, "taper": "both", "size": "fine",
     "settings": {"maxSize": 0.22, "dynamicsPressureSize": 0.9, "shapeScatter": 0.0, "blendMode": 0}},
    {"name": "Technical Liner 0.5", "set": "inks", "spacing": 0.011, "taper": "none", "size": "fine",
     "settings": {"maxSize": 0.05, "dynamicsPressureSize": 0.0, "shapeScatter": 0.0, "blendMode": 0}},
    # the "paints" set (user)
    {"name": "Watercolour Wash", "set": "paints", "spacing": 0.05, "taper": "none", "size": "broad",
     "settings": {"maxSize": 0.8, "dynamicsPressureSize": 0.2, "shapeScatter": 0.0, "blendMode": 2}},
    {"name": "Charcoal Stick", "set": "paints", "spacing": 0.02, "taper": "end", "size": "medium",
     "settings": {"maxSize": 0.4, "dynamicsPressureSize": 0.6, "shapeScatter": 0.1, "blendMode": 0}},
    {"name": "Grainy Charcoal Dust", "set": "paints", "spacing": 0.03, "taper": "none", "size": "broad",
     "settings": {"maxSize": 0.9, "dynamicsPressureSize": 0.5, "shapeScatter": 0.3, "blendMode": 0}},
    {"name": "Broken Cont\u00e9 Stick", "set": "paints", "spacing": 0.02, "taper": "end", "size": "medium",
     "settings": {"maxSize": 0.45, "dynamicsPressureSize": 0.55, "shapeScatter": 0.1, "blendMode": 0}},
    # the "stamps" set (official)
    {"name": "Pumpkin 1", "set": "stamps", "kind": "stamp", "spacing": 1.0, "size": "broad",
     "settings": {"maxSize": 1.0, "dynamicsPressureSize": 0.0, "shapeScatter": 0.0, "blendMode": 0, "stamp": True}},
    {"name": "Pumpkin 2", "set": "stamps", "kind": "stamp", "spacing": 1.0, "size": "broad",
     "settings": {"maxSize": 1.0, "dynamicsPressureSize": 0.0, "shapeScatter": 0.0, "blendMode": 0, "stamp": True}},
    {"name": "Floral Stamp 3", "set": "stamps", "kind": "stamp", "spacing": 0.8, "size": "max",
     "settings": {"maxSize": 1.5, "dynamicsPressureSize": 0.0, "shapeScatter": 0.5, "blendMode": 0, "stamp": True}},
    # two brushes with one name in two sets, to test tie-breaks
    {"name": "Twin", "set": "inks", "spacing": 0.3, "settings": {"maxSize": 0.3, "blendMode": 0}},
    {"name": "Twin", "set": "inks", "variant": "b", "spacing": 0.3, "settings": {"maxSize": 0.3, "blendMode": 0}},
    # a real tag in a real key (the library has one): dynamicsTiltAngle = -0.0
    {"name": "Tagged Real", "set": "stamps", "spacing": 0.2,
     "settings": {"maxSize": 0.3, "blendMode": 0, "dynamicsTiltAngle": {"$real32": "80000000"}}},
]

SETS = {
    "inks": {"title": "Inks", "library": "user", "pack": "ink-pack", "pack_kind": "vendor",
             "note": "02_Vendor_Packs/inks.md"},
    "paints": {"title": "Paints", "library": "user", "pack": "paint-pack", "pack_kind": "vendor",
               "note": "02_Vendor_Packs/paints.md"},
    "stamps": {"title": "Stamps", "library": "official", "pack": "official-pack", "pack_kind": "official",
               "note": "01_Procreate_Defaults/stamps.md"},
    "ink-pack-loose": {"title": "Ink Pack (loose brushes)", "library": "user", "pack": "ink-pack",
                       "pack_kind": "vendor", "note": None, "kind": "loose"},
}


def brush_id(spec):
    return "b_" + sha(spec["name"] + "|" + spec["set"] + "|" + spec.get("variant", ""))[:12]


class World:
    """Paths and ids of one synthetic vault and catalog."""

    def __init__(self, root):
        self.root = Path(root)
        self.vault = self.root / "vault"
        self.catalog = self.root / "catalog"
        self.ids = {}                 # (name, set) -> id
        self.records = {}             # id -> record

    def id(self, name, set_slug=None):
        found = [i for (n, s), i in self.ids.items() if n == name and (set_slug is None or s == set_slug)]
        assert len(found) == 1, (name, set_slug, found)
        return found[0]

    def note(self, slug):
        return SETS[slug]["note"]

    def note_path(self, slug):
        return self.vault / self.note(slug)

    def args(self):
        return ["--vault", str(self.vault), "--catalog", str(self.catalog)]

    def sidecar(self, slug):
        return self.vault / "_BrushTags" / (self.note(slug) + ".tags.json")


def render_note(world, slug, specs, shared, crlf=False):
    set_row = SETS[slug]
    lines = ["---", f'title: "{set_row["title"]}"', "type: brushset", f"set_slug: {slug}",
             f"library: {set_row['library']}", f"pack: {set_row['pack']}", "---", "",
             f"# {set_row['title']}", "", "## Overview", "",
             f"{len(specs)} brushes of the fixture set {set_row['title']}.", ""]
    for n, spec in enumerate(specs, start=1):
        rec = world.records[brush_id(spec)]
        lines += [f"## {rec['display_name']}", "", f"- id: `{rec['id']}` · {n} of {len(specs)} · era E3 · 88 keys",
                  f"- kind: {rec['facets']['kind']} · spacing {rec['facets']['spacing_class']} "
                  f"({rec['facets']['spacing']:.3f})", "- shape: embedded", "- grain: blank", "",
                  f"![[_Previews/{slug}/{rec['id']}.stroke.png]]", ""]
    if shared:
        lines += ["## Shared brushes", ""]
        lines += [f"- `{i}` {name}: see [[{note}#{name}]]" for i, name, note in shared]
        lines += [""]
    lines += ["## Notes", "", "Author's remarks: the grainy comic inks live here.", ""]
    # a fenced block with a '## ' in it must not start a section
    lines += ["```", "## not a heading", "```", ""]
    text = "\n".join(lines)
    return text.replace("\n", "\r\n") if crlf else text


def make_world(root, *, notes=True, vocabulary=True, brushes=None, reverse_write=False):
    """Write a synthetic catalog (catalog.json and one record per brush) and a
    vault (notes, an index, a moc, the vocabulary) under `root`."""
    world = World(root)
    brushes = SPECS if brushes is None else brushes
    by_set = {}
    for spec in brushes:
        by_set.setdefault(spec["set"], []).append(spec)
    for slug, specs in by_set.items():
        for position, spec in enumerate(specs, start=1):
            bid = brush_id(spec)
            facets, words = facets_for(kind=spec.get("kind", "stroke"), spacing=spec["spacing"],
                                       taper=spec.get("taper", "none"), size=spec.get("size", "fine"))
            settings = {"plotSpacing": spec["spacing"], **spec["settings"]}
            record = {
                "schema": "rosw-brushes-brush/1", "id": bid, "content_sha256": sha(spec["name"] + str(settings)),
                "name": spec["name"], "display_name": spec["name"].strip() or "Untitled",
                "library": SETS[slug]["library"], "pack": SETS[slug]["pack"], "family": "legacy", "era": "E3",
                "home": {"set_slug": slug, "position": position},
                "occurrences": [{"set_slug": slug, "pack": SETS[slug]["pack"], "position": position}],
                "shape": {"source": "bundled", "bundled_name": "Brush-Preset-Hard.png", "texture_id": None,
                          "inverted": False},
                "grain": {"source": "embedded", "bundled_name": None, "texture_id": "t_" + sha(slug)[:12],
                          "inverted": False},
                "settings": settings, "facets": facets, "facet_words": words,
                "preview": {"stroke": None, "stroke_source": "thumbnail", "shape": None, "shape_source": "bundled",
                            "grain": None, "grain_source": "embedded"},
                "warnings": []}
            world.ids[(spec["name"] + spec.get("variant", ""), slug)] = bid
            world.records[bid] = record
    # Dry Ink Pen is also a member of the "ink-pack-loose" pseudo-set and of "stamps"
    dry = world.records.get(world.ids.get(("Dry Ink Pen", "inks")), {"id": None, "occurrences": []})
    dry["occurrences"].append({"set_slug": "stamps", "pack": "official-pack", "position": 9})
    dry["occurrences"].append({"set_slug": "ink-pack-loose", "pack": "ink-pack", "position": 1})
    (world.catalog / "brushes").mkdir(parents=True)
    for bid, record in (reversed(list(world.records.items())) if reverse_write else world.records.items()):
        (world.catalog / "brushes" / f"{bid}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    sets = []
    for slug, row in SETS.items():
        members = [brush_id(s) for s in by_set.get(slug, [])]
        if slug == "stamps" and dry["id"]:
            members.append(dry["id"])
        if slug == "ink-pack-loose":
            members = [dry["id"]] if dry["id"] else []
        sets.append({"set_slug": slug, "set_id": "s_" + sha(slug)[:12], "name": row["title"], "title": row["title"],
                     "kind": row.get("kind", "set"), "library": row["library"], "pack": row["pack"],
                     "pack_kind": row["pack_kind"], "brush_count": len(members), "note": row["note"],
                     "brushes": members})
    catalog = {"schema": "rosw-brushes-catalog/1", "counts": {"brushes": len(world.records)}, "sets": sets,
               "brushes": [{"id": i} for i in sorted(world.records)]}
    (world.catalog / "catalog.json").write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n",
                                                encoding="utf-8", newline="\n")
    vault = world.vault
    (vault / "_BrushTags").mkdir(parents=True)
    if vocabulary:
        (vault / "_BrushTags" / "vocabulary.yaml").write_text(VOCABULARY, encoding="utf-8", newline="\n")
    if notes:
        for slug, specs in by_set.items():
            note = world.note_path(slug)
            note.parent.mkdir(parents=True, exist_ok=True)
            shared = []
            if slug == "stamps" and dry["id"]:
                shared = [(dry["id"], "Dry Ink Pen", SETS["inks"]["note"])]
            note.write_text(render_note(world, slug, specs, shared), encoding="utf-8", newline="")
        (vault / "00_INDEX.md").write_text("# Brush vault\n\n## Counts\n\nThirteen fixture brushes.\n",
                                           encoding="utf-8", newline="\n")
        moc = vault / "02_Vendor_Packs" / "_index.md"
        moc.parent.mkdir(parents=True, exist_ok=True)
        moc.write_text("---\ntitle: Vendor packs\ntype: moc\n---\n\n# Vendor packs\n\n- inks\n- paints\n",
                       encoding="utf-8", newline="\n")
        (vault / "CLAUDE.md").write_text("# rules\n\n## Never indexed\n\nsecret words\n", encoding="utf-8", newline="\n")
    return world


def write_sidecar(world, slug, entries, *, stamp="2026-03-04T05:06:07Z", file=None):
    """Write a sidecar by hand. entries: {brush id: {axis_tags: [...], visual: str, sha: str}}."""
    brushes = {}
    for bid, entry in entries.items():
        record = world.records.get(bid)
        brushes[bid] = {
            "content_sha256": entry.get("sha") or record["content_sha256"], "name": record["name"] if record else "x",
            "medium_tags": entry.get("medium_tags", []), "mark_tags": entry.get("mark_tags", []),
            "texture_tags": entry.get("texture_tags", []), "edge_tags": entry.get("edge_tags", []),
            "motif_tags": entry.get("motif_tags", []), "use_tags": entry.get("use_tags", []),
            "visual": entry.get("visual", "A plain stroke."), "visual_basis": "described-not-measured",
            "evidence": {"previews": ["sheet"], "stroke_source": "thumbnail"}, "notes": "fixture",
            "tagged": stamp, "tagger": "brush-tagger v1"}
    path = world.sidecar(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema": 1, "file": file or world.note(slug), "generator": "brush-tagger v1",
            "vocabulary_fingerprint": "sha256:16:0000000000000000", "updated": stamp, "brushes": brushes}
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


class WorldCase(fixtures.BrushCase):
    def setUp(self):
        super().setUp()
        self.world = make_world(self.tmp / "data")
        self.vault, self.catalog = self.world.vault, self.world.catalog

    def build(self, **kw):
        return bs.build_index(self.vault, self.catalog, write=False, **kw)

    def ids(self, envelope):
        return [r["brush_id"] for r in envelope["results"]]

    def names(self, envelope):
        return [r["name"] for r in envelope["results"]]

    def cli(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if stdin is not None:
                with mock.patch.object(sys, "stdin", io.StringIO(stdin)):
                    code = self._run(argv)
            else:
                code = self._run(argv)
        return code, out.getvalue(), err.getvalue()

    def _run(self, argv):
        try:
            return bs.main(list(argv))
        except SystemExit as stop:
            return stop.code

    def cli_world(self, *argv, **kw):
        return self.cli(*argv, *self.world.args(), **kw)


# ── the tokenizer ────────────────────────────────────────────────────────────

class Tokenizer(unittest.TestCase):
    CASES = [
        ("Pencil 6B", ["pencil", "6b"]),
        ("3D", ["3d"]),
        ("FT Cez\u00e1nne", ["ft", "cezanne"]),
        ("Bubbles1", ["bubble", "1"]),
        ("GrainShader 1 Fixed", ["grain", "shader", "grainshader", "1", "fixed"]),
        ("Frankentoon - Tech Pen 0.5", ["frankentoon", "tech", "pen", "0.5"]),
        ("AN Wet On Wet 8", ["an", "wet", "wet", "8"]),
        ("an inker", ["inker"]),
        ("Sargent\u2019s Oils", ["sargent", "oil"]),
        ("P5_Inking HB Pencil 2H", ["p5", "inking", "hb", "pencil", "2h"]),
        ("dynamicsPressureSize", ["dynamic", "pressure", "size", "dynamicspressuresize"]),
        ("Everything Watercolour", ["everything", "watercolor"]),
        ("paper-tooth", ["paper", "tooth"]),
        ("E4 sha256:16:abc b_3f9a1c2e7d10", ["b_3f9a1c2e7d10", "e4"]),
    ]

    def test_the_confirmed_cases(self):
        for text, expected in self.CASES:
            with self.subTest(text=text):
                self.assertEqual(bs.tokenize(text), expected)

    def test_accents_fold_and_apostrophes_go(self):
        self.assertEqual(bs.tokenize("Cont\u00e9"), ["conte"])
        self.assertEqual(bs.tokenize("Butcher\u2019s Paper"), ["butcher", "paper"])
        self.assertEqual(bs.tokenize("D'Entrecasteaux"), ["d", "entrecasteaux", "dentrecasteaux"][1:])

    def test_digits_are_kept(self):
        self.assertEqual(bs.tokenize("Stroke 57"), ["stroke", "57"])
        self.assertEqual(bs.tokenize("6B 2H HB"), ["6b", "2h", "hb"])
        self.assertEqual(bs.tokenize("No.2"), ["no", "2"])

    def test_british_spellings(self):
        self.assertEqual(bs.tokenize("colour grey"), ["color", "gray"])
        self.assertEqual(bs.tokenize("Watercolours"), ["watercolor"])

    def test_stopwords_go_unless_the_word_is_all_caps(self):
        self.assertEqual(bs.tokenize("the pen of a master"), ["pen", "master"])
        self.assertEqual(bs.tokenize("AN Big"), ["an", "big"])
        self.assertEqual(bs.tokenize("up down out off over no"), ["up", "down", "out", "off", "over", "no"])

    def test_light_plural_stemming_with_guards(self):
        for word, expected in (("Splatters", "splatter"), ("Hatches", "hatch"), ("Berries", "berry"),
                               ("Drops", "drop"), ("boxes", "box"), ("brushes", "brush"), ("oils", "oil"),
                               ("canvas", "canvas"), ("glass", "glass"), ("gloss", "gloss"), ("chaos", "chaos"),
                               ("bus", "bus")):
            with self.subTest(word=word):
                self.assertEqual(bs.tokenize(word), [expected])

    def test_no_porter_stemming(self):
        self.assertEqual(bs.tokenize("stippling shader blender"), ["stippling", "shader", "blender"])

    def test_ids_stay_whole_and_hashes_go(self):
        self.assertEqual(bs.tokenize("see b_0123456789ab sha256:16:deadbeef"), ["b_0123456789ab", "see"])

    def test_camel_case_splits_and_emits_the_joined_word(self):
        self.assertEqual(bs.tokenize("GrainShader"), ["grain", "shader", "grainshader"])
        self.assertEqual(bs.tokenize("XMLHttp"), ["xml", "http", "xmlhttp"])

    def test_single_letters_go_single_digits_stay(self):
        self.assertEqual(bs.tokenize("x 5 y"), ["5"])

    def test_non_latin_text_is_kept_as_it_is(self):
        self.assertEqual(bs.tokenize("\u6c34\u5f69-\u538b\u611f"), ["\u6c34\u5f69", "\u538b\u611f"])

    def test_emoji_are_ignored(self):
        self.assertEqual(bs.tokenize("\U0001f4a7Everything"), ["everything"])

    def test_empty_and_none(self):
        self.assertEqual(bs.tokenize(""), [])
        self.assertEqual(bs.tokenize(None), [])
        self.assertEqual(bs.tokenize("the of a"), [])

    def test_the_query_and_the_index_use_one_function(self):
        self.assertEqual(bs.tokenize("Wet-Ink"), bs.tokenize("wet ink"))


# ── the vocabulary ───────────────────────────────────────────────────────────

class Vocabulary(unittest.TestCase):
    def test_the_axes_are_the_six_of_the_spec(self):
        self.assertEqual(bs.AXES, ("medium", "mark", "texture", "edge", "motif", "use"))
        self.assertEqual(bs.TAG_FIELDS, tuple(f"{a}_tags" for a in bs.AXES))
        self.assertEqual(bs.TAG_CAPS, {"medium": 2, "mark": 2, "texture": 3, "edge": 2, "motif": 2, "use": 3})

    def test_parse_reads_tags_definitions_and_synonyms(self):
        parsed = bs.parse_vocabulary_text(VOCABULARY)
        self.assertEqual(list(parsed), list(bs.TAG_FIELDS))
        nib = parsed["medium_tags"][0]
        self.assertEqual(nib["tag"], "nib-pen")
        self.assertEqual(nib["definition"], "a hard nib")
        self.assertEqual(nib["synonyms"], ["fountain pen", "dip pen", "quill"])
        self.assertEqual(parsed["texture_tags"][1], {"tag": "smooth", "definition": "no variation", "synonyms": []})

    def test_a_line_it_cannot_read_names_its_number(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.parse_vocabulary_text("medium_tags:\n  - ok  # fine\n  - Bad Tag  # nope\n")
        self.assertIn("line 3", str(caught.exception))

    def test_an_unknown_axis_key_is_refused(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.parse_vocabulary_text("shape_tags:\n  - round\n")
        self.assertIn("shape_tags", str(caught.exception))

    def test_a_repeated_tag_or_axis_is_refused(self):
        with self.assertRaises(bs.UsageError):
            bs.parse_vocabulary_text("medium_tags:\n  - a\n  - a\n")
        with self.assertRaises(bs.UsageError):
            bs.parse_vocabulary_text("medium_tags:\n  - a\nmedium_tags:\n  - b\n")

    def test_a_list_item_before_any_axis_is_refused(self):
        with self.assertRaises(bs.UsageError):
            bs.parse_vocabulary_text("  - orphan\n")

    def test_load_vocabulary_has_the_f9_shape_and_both_spellings(self):
        with fixtures_temp() as tmp:
            world = make_world(tmp)
            vocab = bs.load_vocabulary(world.vault)
        self.assertEqual(list(vocab), list(bs.AXES))
        self.assertEqual(vocab["medium"][0], {"tag": "nib-pen", "definition": "a hard nib"})
        self.assertEqual(vocab["medium_tags"], vocab["medium"])
        self.assertIn("medium_tags", vocab)
        self.assertNotIn("shape", vocab)

    def test_a_missing_vocabulary_is_a_usage_error(self):
        with fixtures_temp() as tmp:
            with self.assertRaises(bs.UsageError):
                bs.load_vocabulary(Path(tmp))

    def test_the_fingerprint_ignores_order_and_definitions(self):
        one = bs.parse_vocabulary_text("medium_tags:\n  - a  # x\n  - b  # y\n")
        two = bs.parse_vocabulary_text("medium_tags:\n  - b  # other\n  - a\n")
        self.assertEqual(bs.vocabulary_fingerprint(one), bs.vocabulary_fingerprint(two))
        three = bs.parse_vocabulary_text("medium_tags:\n  - a\n  - c\n")
        self.assertNotEqual(bs.vocabulary_fingerprint(one), bs.vocabulary_fingerprint(three))
        self.assertRegex(bs.vocabulary_fingerprint(one), r"^sha256:16:[0-9a-f]{16}$")


def tempfile_dir():
    import atexit
    import shutil
    import tempfile
    path = tempfile.mkdtemp(prefix="brushes-test-")
    atexit.register(shutil.rmtree, path, True)
    return path


@contextlib.contextmanager
def fixtures_temp():
    import shutil
    import tempfile
    path = Path(tempfile.mkdtemp(prefix="brushes-test-")).resolve()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


class RealVocabulary(unittest.TestCase):
    """The author's vocabulary.yaml, as shipped."""

    @classmethod
    def setUpClass(cls):
        cls.text = REAL_VOCABULARY.read_text(encoding="utf-8")
        cls.parsed = bs.parse_vocabulary_text(cls.text, "vocabulary.yaml")

    def test_all_six_axes_in_order(self):
        self.assertEqual(list(self.parsed), list(bs.TAG_FIELDS))

    def test_each_axis_is_a_usable_size(self):
        for key, entries in self.parsed.items():
            with self.subTest(axis=key):
                self.assertGreaterEqual(len(entries), 20)
                self.assertLessEqual(len(entries), 45)

    def test_tags_are_lowercase_hyphenated_and_unique_with_a_definition(self):
        for key, entries in self.parsed.items():
            tags = [e["tag"] for e in entries]
            self.assertEqual(len(tags), len(set(tags)), key)
            for entry in entries:
                self.assertRegex(entry["tag"], r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
                self.assertGreater(len(entry["definition"]), 10, entry["tag"])
                self.assertLess(len(entry["definition"]), 400, entry["tag"])

    def test_every_tag_has_a_few_synonyms(self):
        for key, entries in self.parsed.items():
            for entry in entries:
                self.assertGreaterEqual(len(entry["synonyms"]), 1, f"{key} {entry['tag']}")
                self.assertTrue(all(s == s.lower() and "," not in s for s in entry["synonyms"]))

    def test_a_tag_belongs_to_one_axis(self):
        seen = {}
        for key, entries in self.parsed.items():
            for entry in entries:
                self.assertNotIn(entry["tag"], seen, f"{entry['tag']} in {key} and {seen.get(entry['tag'])}")
                seen[entry["tag"]] = key

    def test_nothing_in_the_file_is_nested_or_quoted(self):
        for line in self.text.splitlines():
            if line.startswith("  - "):
                self.assertNotIn('"', line.split("#", 1)[0])
            elif line.strip() and not line.startswith("#"):
                self.assertRegex(line, r"^[a-z]+_tags:\s*(#.*)?$")

    @unittest.skipIf(yaml is None, "pyyaml is not installed")
    def test_it_is_also_plain_yaml_with_the_same_tags(self):
        loaded = yaml.safe_load(self.text)
        self.assertEqual({k: v for k, v in loaded.items()},
                         {k: [e["tag"] for e in entries] for k, entries in self.parsed.items()})

    def test_the_motifs_cover_the_library_it_was_written_from(self):
        tags = {e["tag"] for e in self.parsed["motif_tags"]}
        for needed in ("food-sweets", "earth-sediment", "fruit-vegetable", "leaf-foliage", "metal-rust", "flower"):
            self.assertIn(needed, tags)
        media = {e["tag"] for e in self.parsed["medium_tags"]}
        for needed in ("technical-pen", "charcoal", "watercolor", "graphite-pencil", "nib-pen", "printmaking"):
            self.assertIn(needed, media)


# ── folders and names ────────────────────────────────────────────────────────

class Roots(unittest.TestCase):
    def setUp(self):
        self.env = {}

    def resolve(self, **flags):
        return bs.resolve_roots(environ=self.env, **flags)

    def test_the_tools_own_vault_and_the_catalog_beside_it_by_default(self):
        vault, catalog, index = self.resolve()
        self.assertEqual(vault, (BRUSHES / "vault").resolve())
        self.assertEqual(catalog, (BRUSHES / "catalog").resolve())
        self.assertEqual(index, (BRUSHES / "vault" / "tools" / "rag_index" / "index.json").resolve())

    def test_the_root_moves_the_vault_and_the_catalog(self):
        self.env = {"ROSW_BRUSHES_ROOT": str(Path.cwd() / "elsewhere")}
        vault, catalog, index = self.resolve()
        self.assertEqual(vault, (Path.cwd() / "elsewhere" / "vault").resolve())
        self.assertEqual(catalog, (Path.cwd() / "elsewhere" / "catalog").resolve())
        self.assertEqual(index, vault / "tools" / "rag_index" / "index.json")

    def test_a_folders_own_variable_beats_the_root_and_a_flag_beats_both(self):
        here = Path.cwd()
        self.env = {"ROSW_BRUSHES_ROOT": str(here / "root"), "ROSW_BRUSHES_VAULT": str(here / "v"),
                    "ROSW_BRUSHES_CATALOG": str(here / "c"), "ROSW_BRUSHES_INDEX": str(here / "i.json")}
        vault, catalog, index = self.resolve()
        self.assertEqual((vault, catalog, index), ((here / "v").resolve(), (here / "c").resolve(),
                                                    (here / "i.json").resolve()))
        vault, catalog, index = self.resolve(vault=str(here / "fv"), catalog=str(here / "fc"), index=str(here / "fi"))
        self.assertEqual((vault, catalog, index), ((here / "fv").resolve(), (here / "fc").resolve(),
                                                    (here / "fi").resolve()))

    def test_an_empty_value_counts_as_absent(self):
        self.env = {"ROSW_BRUSHES_ROOT": "  ", "ROSW_BRUSHES_VAULT": ""}
        self.assertEqual(self.resolve()[0], (BRUSHES / "vault").resolve())

    def test_the_five_names_are_the_pipelines(self):
        self.assertEqual(bs.ENV_NAMES, bc.ENV_NAMES)
        self.assertEqual((bs.ENV_ROOT, bs.ENV_LIBRARY, bs.ENV_CATALOG, bs.ENV_VAULT, bs.ENV_INDEX),
                         (bc.ENV_ROOT, bc.ENV_LIBRARY, bc.ENV_CATALOG, bc.ENV_VAULT, bc.ENV_INDEX))

    def test_the_default_root_is_the_pipelines_default(self):
        self.assertEqual(bs.TOOL_ROOT, bc.TOOL_ROOT)


# ── notes ────────────────────────────────────────────────────────────────────

class NoteParsing(unittest.TestCase):
    NOTE = ("---\ntitle: \"T\"\nlibrary: user\ntags: [a, b]\n---\n\n# T\n\n## Overview\n\nWords.\n\n"
            "## Brush One\n\n- id: `b_0123456789ab` · 1 of 2\n- kind: stroke\n\n![[x]]\n\n"
            "## Plain\n\n- not an id\n\n```\n## inside a fence\n```\n\n## Empty\n\n## Last\n\n"
            "- id: `b_ba9876543210`\n")

    def test_line_numbers_are_file_lines_with_frontmatter_counted(self):
        parsed = bs.parse_note(self.NOTE)
        lines = self.NOTE.split("\n")
        sections = {s["heading"]: s for s in parsed["sections"]}
        brush = sections["Brush One"]
        self.assertEqual(lines[brush["start_line"] - 1], "## Brush One")
        self.assertEqual(lines[brush["end_line"] - 1], "![[x]]")
        self.assertEqual(brush["brush_id"], "b_0123456789ab")
        self.assertEqual(sections["Last"]["brush_id"], "b_ba9876543210")
        self.assertEqual(lines[sections["Last"]["end_line"] - 1], "- id: `b_ba9876543210`")

    def test_a_heading_inside_a_fence_does_not_split(self):
        parsed = bs.parse_note(self.NOTE)
        headings = [s["heading"] for s in parsed["sections"]]
        self.assertNotIn("inside a fence", headings)
        plain = next(s for s in parsed["sections"] if s["heading"] == "Plain")
        self.assertIn("## inside a fence", plain["text"])
        self.assertIsNone(plain["brush_id"])

    def test_an_empty_section_is_skipped_and_the_preamble_is_chunk_zero(self):
        parsed = bs.parse_note(self.NOTE)
        self.assertNotIn("Empty", [s["heading"] for s in parsed["sections"]])
        self.assertEqual(parsed["sections"][0]["chunk_index"], 0)
        self.assertIsNone(parsed["sections"][0]["heading"])
        self.assertEqual(parsed["frontmatter"]["tags"], ["a", "b"])

    def test_crlf_input_read_through_read_text_gives_the_same_locations(self):
        path = Path(tempfile_dir()) / "crlf.md"
        path.write_bytes(self.NOTE.replace("\n", "\r\n").encode("utf-8"))
        lf = bs.parse_note(self.NOTE)
        crlf = bs.parse_note(bs.read_text(path))
        self.assertEqual([(s["heading"], s["start_line"], s["end_line"]) for s in lf["sections"]],
                         [(s["heading"], s["start_line"], s["end_line"]) for s in crlf["sections"]])

    def test_a_heading_with_three_hashes_is_not_a_section(self):
        parsed = bs.parse_note("## A\n\ntext\n\n### Sub\n\nmore\n")
        self.assertEqual([s["heading"] for s in parsed["sections"]], ["A"])

    def test_a_note_with_no_frontmatter(self):
        parsed = bs.parse_note("# Title\n\n## Only\n\nbody\n")
        self.assertEqual(parsed["frontmatter"], {})
        self.assertEqual([s["heading"] for s in parsed["sections"]], [None, "Only"])

    def test_the_shared_brushes_stub_ids_are_read(self):
        parsed = bs.parse_note("## Shared brushes\n\n- `b_0123456789ab` Name: see [[x#Name]]\n")
        self.assertEqual(parsed["sections"][0]["shared"], ["b_0123456789ab"])


class NoteFiles(WorldCase):
    def test_discovery_types_and_exclusions(self):
        found = dict(bs.iter_notes(self.vault))
        self.assertEqual(found["00_INDEX.md"], "index")
        self.assertEqual(found["02_Vendor_Packs/_index.md"], "moc")
        self.assertEqual(found["02_Vendor_Packs/inks.md"], "set")
        self.assertNotIn("CLAUDE.md", found)
        (self.vault / "_Guides").mkdir()
        (self.vault / "_Guides" / "g.md").write_text("# g\n", encoding="utf-8")
        (self.vault / "_Previews").mkdir()
        (self.vault / "_Previews" / "p.md").write_text("# p\n", encoding="utf-8")
        found = dict(bs.iter_notes(self.vault))
        self.assertEqual(found["_Guides/g.md"], "guide")
        self.assertNotIn("_Previews/p.md", found)
        paths = [p for p, _ in bs.iter_notes(self.vault)]
        self.assertEqual(paths[0], "00_INDEX.md")
        self.assertEqual(paths, paths and sorted(paths, key=lambda r: (r[:2] != "00", r[:1] == "_", r.casefold())))


# ── building the index ───────────────────────────────────────────────────────

class Index(WorldCase):
    def test_one_chunk_per_brush_and_the_note_chunks(self):
        index = self.build()
        brushes = [c for c in index["chunks"] if c["source_type"] == "brush"]
        self.assertEqual(len(brushes), len(SPECS))
        self.assertEqual(index["brush_chunk_count"], len(SPECS))
        self.assertEqual(len({c["brush_id"] for c in brushes}), len(SPECS))
        kinds = {c["source_type"] for c in index["chunks"]}
        self.assertEqual(kinds, {"brush", "set", "index", "moc"})
        self.assertEqual(index["chunk_count"], len(index["chunks"]))

    def test_a_brush_chunk_has_its_note_heading_and_lines(self):
        index = self.build()
        chunk = bs.resolve_brush(index, "Dry Ink Pen")
        self.assertEqual(chunk["note"], "02_Vendor_Packs/inks.md")
        self.assertEqual(chunk["heading"], "Dry Ink Pen")
        lines = (self.vault / chunk["note"]).read_text(encoding="utf-8").split("\n")
        self.assertEqual(lines[chunk["start_line"] - 1], "## Dry Ink Pen")
        self.assertIn(f"`{chunk['brush_id']}`", lines[chunk["start_line"] + 1])
        self.assertGreater(chunk["end_line"], chunk["start_line"])

    def test_facets_settings_and_preview_come_from_the_record(self):
        index = self.build()
        chunk = bs.resolve_brush(index, "Pumpkin 1")
        record = self.world.records[chunk["brush_id"]]
        self.assertEqual(chunk["facets"], record["facets"])
        self.assertEqual(chunk["settings"], record["settings"])
        self.assertEqual(chunk["preview"], record["preview"])
        self.assertEqual(chunk["content_sha256"], record["content_sha256"])
        self.assertEqual(chunk["facet_words"], record["facet_words"])

    def test_also_in_comes_from_the_occurrences(self):
        index = self.build()
        chunk = bs.resolve_brush(index, "Dry Ink Pen")
        self.assertEqual(sorted(a["set"] for a in chunk["also_in"]), ["ink-pack-loose", "stamps"])
        stamps = next(a for a in chunk["also_in"] if a["set"] == "stamps")
        self.assertEqual(stamps["note"], "01_Procreate_Defaults/stamps.md")
        self.assertEqual(stamps["heading"], "Shared brushes")
        loose = next(a for a in chunk["also_in"] if a["set"] == "ink-pack-loose")
        self.assertIsNone(loose["note"])

    def test_no_notes_means_no_locations_and_a_note(self):
        with fixtures_temp() as tmp:
            world = make_world(tmp, notes=False)
            index = bs.build_index(world.vault, world.catalog, write=False)
        chunk = bs.resolve_brush(index, "Dry Ink Pen")
        self.assertEqual((chunk["note"], chunk["heading"], chunk["start_line"], chunk["end_line"]),
                         (None, None, None, None))
        self.assertTrue(any("not on disk" in w for w in index["warnings"]))
        self.assertTrue(all(c["source_type"] == "brush" for c in index["chunks"]))

    def test_the_index_holds_no_timestamp_no_absolute_path_no_vault_key(self):
        index = self.build()
        text = json.dumps(index, ensure_ascii=False)
        self.assertNotIn(str(self.tmp), text)
        self.assertNotIn(str(self.tmp).replace("\\", "/"), text)
        self.assertNotIn(str(self.tmp).replace("\\", "\\\\"), text)
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]", text))
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text))
        for key in ("built", "vault", "catalog", "timestamp", "created", "updated"):
            self.assertNotIn(key, index)
        self.assertEqual(index["schema"], 1)

    def test_two_builds_are_the_same_bytes(self):
        a, b = self.tmp / "a.json", self.tmp / "b.json"
        bs.build_index(self.vault, self.catalog, index_path=a)
        bs.build_index(self.vault, self.catalog, index_path=b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertFalse(b"\r" in a.read_bytes())
        self.assertFalse(a.with_name("a.json.tmp").exists())

    def test_the_default_index_path_is_under_the_vault(self):
        bs.build_index(self.vault, self.catalog)
        self.assertTrue((self.vault / "tools" / "rag_index" / "index.json").is_file())

    def test_the_index_path_variable_is_obeyed(self):
        target = self.tmp / "elsewhere" / "idx.json"
        with mock.patch.dict(os.environ, {"ROSW_BRUSHES_INDEX": str(target)}):
            bs.build_index(self.vault, self.catalog)
        self.assertTrue(target.is_file())

    def test_the_same_bytes_whatever_order_the_files_were_made_in(self):
        other = make_world(self.tmp / "other", reverse_write=True)
        a, b = self.tmp / "a.json", self.tmp / "b.json"
        bs.build_index(self.vault, self.catalog, index_path=a)
        bs.build_index(other.vault, other.catalog, index_path=b)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_load_index_round_trips(self):
        path = self.tmp / "i.json"
        built = bs.build_index(self.vault, self.catalog, index_path=path)
        loaded = bs.load_index(path)
        self.assertEqual(json.loads(json.dumps(built)), loaded)

    def test_load_index_errors_are_usage_errors(self):
        with self.assertRaises(bs.UsageError):
            bs.load_index(self.tmp / "missing.json")
        bad = self.tmp / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with self.assertRaises(bs.UsageError):
            bs.load_index(bad)
        other = self.tmp / "other.json"
        other.write_text('{"schema": 99, "chunks": []}', encoding="utf-8")
        with self.assertRaises(bs.UsageError):
            bs.load_index(other)

    def test_a_missing_catalog_is_a_usage_error(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.build_index(self.vault, self.tmp / "nowhere", write=False)
        self.assertIn("ingest.py build", str(caught.exception))

    def test_an_empty_catalog_builds_an_empty_index(self):
        with fixtures_temp() as tmp:
            world = make_world(tmp, brushes=[])
            index = bs.build_index(world.vault, world.catalog, write=False)
            self.assertEqual(index["brush_chunk_count"], 0)
            envelope = bs.search_index(index, "ink", source_types=["brush"])
            self.assertEqual((envelope["total"], envelope["results"]), (0, []))
            envelope = bs.search_index(index, tags=["medium=nib-pen"])
            self.assertEqual(envelope["total"], 0)
            self.assertEqual(bs.similar(index, settings={"plotSpacing": 0.1})["total"], 0)
            self.assertEqual(bs.facet_counts(index)["brushes"], 0)
            with self.assertRaises(bs.NotFound):
                bs.resolve_brush(index, "anything")

    def test_a_missing_vocabulary_is_a_warning_not_a_failure(self):
        with fixtures_temp() as tmp:
            world = make_world(tmp, vocabulary=False)
            index = bs.build_index(world.vault, world.catalog, write=False)
        self.assertTrue(any("vocabulary" in w for w in index["warnings"]))
        with self.assertRaises(bs.UsageError):
            bs.search_index(index, tags=["medium=nib-pen"])

    def test_the_vocabulary_is_embedded_with_definitions(self):
        index = self.build()
        self.assertEqual(index["vocabulary"]["medium_tags"][0], {"tag": "nib-pen", "definition": "a hard nib"})
        self.assertEqual(list(index["vocabulary"]), list(bs.TAG_FIELDS))

    def test_a_non_brush_file_in_the_records_folder_is_ignored(self):
        (self.catalog / "brushes" / "notes.txt").write_text("x", encoding="utf-8")
        (self.catalog / "brushes" / "readme.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.build()["brush_chunk_count"], len(SPECS))

    def test_a_note_chunk_for_the_overview_and_the_authors_notes(self):
        index = self.build()
        headings = [(c["note"], c["heading"]) for c in index["chunks"] if c["source_type"] == "set"]
        self.assertIn(("02_Vendor_Packs/inks.md", "Overview"), headings)
        self.assertIn(("02_Vendor_Packs/inks.md", "Notes"), headings)
        self.assertNotIn(("02_Vendor_Packs/inks.md", "not a heading"), headings)

    def test_claude_md_is_never_indexed(self):
        index = self.build()
        self.assertFalse(any("secret" in c.get("snippet", "") for c in index["chunks"]))


class Freshness(WorldCase):
    def setUp(self):
        super().setUp()
        self.path = self.tmp / "idx.json"
        self.index = bs.build_index(self.vault, self.catalog, index_path=self.path)

    def state(self):
        return bs.check_fresh(bs.load_index(self.path), self.vault, self.catalog)

    def test_fresh_after_a_build(self):
        result = self.state()
        self.assertEqual(result["state"], "fresh")
        self.assertIsInstance(result["reason"], str)

    def test_a_sidecar_note_vocabulary_or_record_edit_makes_it_stale(self):
        victims = {
            "sidecars": lambda: write_sidecar(self.world, "inks", {self.world.id("Dry Ink Pen"): {}}),
            "notes": lambda: self.world.note_path("inks").write_text(
                self.world.note_path("inks").read_text(encoding="utf-8") + "\nmore\n", encoding="utf-8"),
            "vocabulary": lambda: (self.vault / "_BrushTags" / "vocabulary.yaml").write_text(
                VOCABULARY + "  - extra-use\n".replace("  - extra-use", ""), encoding="utf-8") or
            (self.vault / "_BrushTags" / "vocabulary.yaml").write_text(
                VOCABULARY.replace("decorating ", "decorating2"), encoding="utf-8"),
            "catalog": lambda: self._touch_record(),
        }
        for name, edit in victims.items():
            with self.subTest(changed=name):
                bs.build_index(self.vault, self.catalog, index_path=self.path)
                self.assertEqual(self.state()["state"], "fresh")
                edit()
                result = self.state()
                self.assertEqual(result["state"], "stale", name)
                self.assertIn(name, result["reason"])
                bs.build_index(self.vault, self.catalog, index_path=self.path)
                self.assertEqual(self.state()["state"], "fresh")

    def _touch_record(self):
        path = self.catalog / "brushes" / f"{self.world.id('Pumpkin 1')}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["facets"]["grain_contrast"] = 0.2           # previews.py arriving
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_a_new_note_makes_it_stale(self):
        (self.vault / "02_Vendor_Packs" / "new.md").write_text("# new\n\n## A\n\nx\n", encoding="utf-8")
        self.assertEqual(self.state()["state"], "stale")

    def test_the_engine_version_is_part_of_it(self):
        index = bs.load_index(self.path)
        index["engine"] = "brush_search/0"
        self.assertEqual(bs.check_fresh(index, self.vault, self.catalog)["state"], "stale")

    def test_crlf_in_a_note_does_not_change_the_fingerprint(self):
        path = self.world.note_path("inks")
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(self.state()["state"], "fresh")


# ── search ───────────────────────────────────────────────────────────────────

class Search(WorldCase):
    def setUp(self):
        super().setUp()
        self.index = self.build()

    def test_the_envelope_has_the_f9_keys(self):
        envelope = bs.search_index(self.index, "ink")
        self.assertEqual(list(envelope), ["query", "tags", "where", "where_not", "ranking", "total", "offset", "results"])
        self.assertEqual(envelope["ranking"], "cosine")
        self.assertEqual(envelope["offset"], 0)

    def test_the_row_has_the_f9_keys(self):
        row = bs.search_index(self.index, "ink", source_types=["brush"])["results"][0]
        expected = ["brush_id", "name", "set", "set_title", "library", "pack", "source_type", "note", "heading",
                    "start_line", "end_line", "score", "medium_tags", "mark_tags", "texture_tags", "edge_tags",
                    "motif_tags", "use_tags", "visual", "visual_basis", "tag_state", "facets", "preview", "approximate",
                    "also_in", "record"]
        self.assertEqual(list(row), expected)
        self.assertEqual(row["record"], f"brushes/{row['brush_id']}.json")
        self.assertEqual(row["tag_state"], "untagged")
        self.assertIsNone(row["visual_basis"])
        self.assertIs(row["approximate"], False)

    def test_settings_only_when_asked(self):
        self.assertNotIn("settings", bs.search_index(self.index, "ink")["results"][0])
        row = bs.search_index(self.index, "ink", settings=True, source_types=["brush"])["results"][0]
        self.assertEqual(row["settings"], self.world.records[row["brush_id"]]["settings"])

    def test_a_name_match_comes_first(self):
        self.assertEqual(self.names(bs.search_index(self.index, "pumpkin"))[:2], ["Pumpkin 1", "Pumpkin 2"])
        self.assertEqual(self.names(bs.search_index(self.index, "charcoal", top=3))[0], "Charcoal Stick")

    def test_a_set_title_and_digits_are_searchable(self):
        self.assertEqual(self.names(bs.search_index(self.index, "0.5"))[0], "Technical Liner 0.5")
        # "Stamps" is only in the set title and a one-word synonym of picture-stamp
        names = self.names(bs.search_index(self.index, "stamps", top=20, source_types=["brush"]))
        self.assertIn("Floral Stamp 3", names)
        self.assertIn("Pumpkin 1", names)

    def test_accents_and_plurals_and_spellings_fold(self):
        self.assertIn("Broken Cont\u00e9 Stick", self.names(bs.search_index(self.index, "conte")))
        self.assertIn("Broken Cont\u00e9 Stick", self.names(bs.search_index(self.index, "CONT\u00c9")))
        self.assertEqual(self.names(bs.search_index(self.index, "watercolor"))[0], "Watercolour Wash")
        self.assertEqual(self.names(bs.search_index(self.index, "watercolours"))[0], "Watercolour Wash")

    def test_the_same_query_gives_the_same_answer_every_time(self):
        first = bs.search_index(self.index, "grainy charcoal ink", top=10)
        for _ in range(3):
            self.assertEqual(bs.search_index(self.index, "grainy charcoal ink", top=10), first)
        again = self.build()
        self.assertEqual(bs.search_index(again, "grainy charcoal ink", top=10), first)

    def test_equal_scores_break_by_name_then_id(self):
        envelope = bs.search_index(self.index, "twin", source_types=["brush"])
        twins = [r for r in envelope["results"] if r["name"] == "Twin"]
        self.assertEqual(len(twins), 2)
        self.assertEqual(twins[0]["score"], twins[1]["score"])
        self.assertEqual([t["brush_id"] for t in twins], sorted(t["brush_id"] for t in twins))

    def test_scores_are_rounded_to_four_places_and_sorted_down(self):
        scores = [r["score"] for r in bs.search_index(self.index, "ink pen brush", top=10)["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for score in scores:
            self.assertEqual(score, round(score, 4))
            self.assertGreater(score, 0)

    def test_top_and_offset_page_through_the_total(self):
        full = bs.search_index(self.index, "ink brush pen stick", top=50)
        self.assertGreater(full["total"], 3)
        page = bs.search_index(self.index, "ink brush pen stick", top=2, offset=1)
        self.assertEqual(page["total"], full["total"])
        self.assertEqual(page["offset"], 1)
        self.assertEqual(page["results"], full["results"][1:3])

    def test_a_bad_window_is_a_usage_error(self):
        for kw in ({"top": -1}, {"offset": -1}, {"top": "5"}):
            with self.assertRaises(bs.UsageError):
                bs.search_index(self.index, "ink", **kw)

    def test_a_query_with_no_usable_word_finds_nothing(self):
        for query in ("the of a", "zzzzqx", "!!!"):
            envelope = bs.search_index(self.index, query)
            self.assertEqual((envelope["total"], envelope["results"]), (0, []), query)

    def test_no_query_and_no_filter_browses_in_set_order(self):
        envelope = bs.search_index(self.index, "", top=50, source_types=["brush"])
        self.assertEqual(envelope["ranking"], "filter-order")
        self.assertEqual(envelope["total"], len(SPECS))
        sets = [r["set"] for r in envelope["results"]]
        self.assertEqual(sets, sorted(sets))

    def test_source_types_narrow_the_search(self):
        everything = bs.search_index(self.index, "comic", top=10)
        self.assertEqual({r["source_type"] for r in everything["results"]}, {"set"})
        self.assertEqual(bs.search_index(self.index, "comic", source_types=["brush"])["total"], 0)
        row = everything["results"][0]
        self.assertIsNone(row["brush_id"])
        self.assertEqual(row["heading"], "Notes")
        self.assertIn("comic", row["snippet"])
        self.assertEqual(row["tag_state"], None)
        self.assertEqual(row["facets"], {})
        with self.assertRaises(bs.UsageError):
            bs.search_index(self.index, "ink", source_types=["picture"])

    def test_a_filter_with_a_query_narrows_to_brushes(self):
        envelope = bs.search_index(self.index, "comic", where=["library=user"])
        self.assertEqual(envelope["total"], 0)

    def test_results_are_one_per_brush(self):
        ids = self.ids(bs.search_index(self.index, "ink pen stick pumpkin", top=50, source_types=["brush"]))
        self.assertEqual(len(ids), len(set(ids)))

    def test_the_vocabulary_expands_a_query_to_the_tags_own_words(self):
        # "inking" is a synonym of the use tag line-art; "ink" is another; "inker" a third.
        expanded = bs.search_index(self.index, "inker", top=10)
        names = self.names(expanded)
        self.assertIn("Dry Ink Pen", names)
        plain = [t for t in bs.tokenize("inker")]
        self.assertEqual(plain, ["inker"])

    def test_a_multi_word_synonym_triggers_but_adds_only_one_word_terms(self):
        group = next(g for g in self.index["expansions"] if g["tag"] == "medium:nib-pen")
        self.assertIn(["fountain", "pen"], group["phrases"])
        self.assertEqual(group["terms"], ["nib", "pen", "quill"])
        found = self.names(bs.search_index(self.index, "fountain pen", top=10))
        self.assertIn("Dry Ink Pen", found)

    def test_a_synonym_reaches_a_name_the_query_never_used(self):
        # "food" is a synonym of motif food-sweets / fruit-vegetable; pumpkin is a one-word synonym of the latter.
        names = self.names(bs.search_index(self.index, "food", top=10))
        self.assertTrue({"Pumpkin 1", "Pumpkin 2"} <= set(names))

    def test_expansion_never_buries_an_exact_name(self):
        self.assertEqual(self.names(bs.search_index(self.index, "stipple", top=1)), [])        # no such brush
        self.assertEqual(self.names(bs.search_index(self.index, "pumpkin 1", top=1)), ["Pumpkin 1"])


# ── filters ──────────────────────────────────────────────────────────────────

class Filters(WorldCase):
    def setUp(self):
        super().setUp()
        self.index = self.build()

    def found(self, **kw):
        return sorted(self.names(bs.search_index(self.index, top=100, **kw)))

    def test_where_equality_on_a_facet(self):
        self.assertEqual(self.found(where=["kind=stamp"]), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2"])
        self.assertEqual(self.found(where=["taper=both"]), ["Dry Ink Pen", "Wet Ink Brush"])

    def test_one_filter_may_be_a_bare_string(self):
        self.assertEqual(self.found(where="kind=stamp"), self.found(where=["kind=stamp"]))
        self.assertEqual(self.found(where_not="kind=stamp"), self.found(where_not=["kind=stamp"]))
        self.assertEqual(bs.search_index(self.index, tags="medium=nib-pen")["tags"], [["medium", ["nib-pen"]]])

    def test_where_with_a_list_is_or_and_flags_are_and(self):
        self.assertEqual(self.found(where=["taper=both,end"]),
                         ["Broken Cont\u00e9 Stick", "Charcoal Stick", "Dry Ink Pen", "Wet Ink Brush"])
        self.assertEqual(self.found(where=["taper=both,end", "set=inks"]), ["Dry Ink Pen", "Wet Ink Brush"])

    def test_where_booleans_accept_every_spelling(self):
        for word in ("true", "yes", "1", "TRUE", "Yes"):
            self.assertEqual(self.found(where=[f"is_stamp={word}"]), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2"], word)
        for word in ("false", "no", "0"):
            self.assertEqual(len(self.found(where=[f"is_stamp={word}"])), len(SPECS) - 3, word)

    def test_where_ranges_are_inclusive_and_either_side_may_be_open(self):
        self.assertEqual(self.found(where=["spacing=0.01..0.012"]),
                         ["Dry Ink Pen", "Technical Liner 0.5", "Wet Ink Brush"])
        self.assertEqual(self.found(where=["spacing=0.8.."]), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2"])
        self.assertEqual(self.found(where=["spacing=..0.0101"]), ["Dry Ink Pen"])
        self.assertEqual(self.found(where=["spacing=0.012..0.012"]), ["Wet Ink Brush"])

    def test_where_on_a_raw_setting_key(self):
        self.assertEqual(self.found(where=["shapeScatter=0.3.."]), ["Floral Stamp 3", "Grainy Charcoal Dust"])
        self.assertEqual(self.found(where=["stamp=true"]), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2"])
        self.assertEqual(self.found(where=["blendMode=2"]), ["Watercolour Wash"])

    def test_a_real_tag_is_opened_as_a_number(self):
        self.assertEqual(self.found(where=["dynamicsTiltAngle=0"]), ["Tagged Real"])
        self.assertEqual(self.found(where=["dynamicsTiltAngle=-1..1"]), ["Tagged Real"])

    def test_where_not_excludes(self):
        names = self.found(where=["set=stamps"], where_not=["kind=stamp"])
        self.assertEqual(names, ["Dry Ink Pen", "Tagged Real"])           # Dry Ink Pen is shared into stamps
        self.assertEqual(self.found(where_not=["is_stamp=true", "library=user"]), ["Tagged Real"])

    def test_a_missing_value_matches_no_where_and_passes_every_where_not(self):
        # grain_contrast is null in every record: the previews have not run
        self.assertEqual(self.found(where=["grain_contrast=0..1"]), [])
        self.assertEqual(len(self.found(where_not=["grain_contrast=0..1"])), len(SPECS))

    def test_the_builtin_keys(self):
        stick = self.world.id("Charcoal Stick")
        self.assertEqual(self.found(where=[f"id={stick}"]), ["Charcoal Stick"])
        self.assertEqual(self.found(where=["library=official"]), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2", "Tagged Real"])
        self.assertEqual(self.found(where=["pack=paint-pack"]),
                         sorted(["Watercolour Wash", "Charcoal Stick", "Grainy Charcoal Dust",
                                 "Broken Cont\u00e9 Stick"]))
        self.assertEqual(self.found(where=["tagged=false"]), sorted(n["name"] for n in SPECS))

    def test_set_also_matches_the_sets_a_brush_is_shared_into(self):
        self.assertIn("Dry Ink Pen", self.found(where=["set=stamps"]))
        self.assertIn("Dry Ink Pen", self.found(where=["set=ink-pack-loose"]))
        self.assertNotIn("Dry Ink Pen", self.found(where=["set=paints"]))

    def test_an_unknown_key_is_a_usage_error_that_suggests_one(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.search_index(self.index, where=["spaceing=0.1"])
        self.assertIn("spacing", str(caught.exception))
        with self.assertRaises(bs.UsageError):
            bs.search_index(self.index, where_not=["nonsense=1"])

    def test_comparison_operators_are_refused(self):
        for spec in ("spacing>0.1", "spacing<0.1", "spacing>=1", "spacing=0.1 and x"):
            with self.subTest(spec=spec):
                with self.assertRaises(bs.UsageError):
                    bs.search_index(self.index, where=[spec])

    def test_a_bad_range_is_a_usage_error(self):
        with self.assertRaises(bs.UsageError):
            bs.search_index(self.index, where=["spacing=a..b"])

    def test_the_envelope_echoes_the_filters(self):
        envelope = bs.search_index(self.index, where=["kind=stamp"], where_not=["set=stamps"])
        self.assertEqual(envelope["where"], ["kind=stamp"])
        self.assertEqual(envelope["where_not"], ["set=stamps"])
        self.assertEqual(envelope["ranking"], "filter-order")


class TagFilters(WorldCase):
    def setUp(self):
        super().setUp()
        w = self.world
        write_sidecar(w, "inks", {
            w.id("Dry Ink Pen"): {"medium_tags": ["nib-pen"], "mark_tags": ["line"], "use_tags": ["line-art"],
                                  "texture_tags": ["paper-tooth", "gritty"], "visual": "A dry grainy hairline."},
            w.id("Wet Ink Brush"): {"medium_tags": ["nib-pen", "watercolor"], "mark_tags": ["line"],
                                    "use_tags": ["line-art", "shading"], "visual": "A smooth wet line."},
            w.id("Technical Liner 0.5"): {"medium_tags": ["nib-pen"], "use_tags": ["line-art"]},
        })
        write_sidecar(w, "stamps", {w.id("Pumpkin 1"): {"mark_tags": ["picture-stamp"], "motif_tags": ["fruit-vegetable"],
                                                        "use_tags": ["decorating"]}})
        self.index = self.build()

    def found(self, **kw):
        return self.names(bs.search_index(self.index, top=100, **kw))

    def test_tags_attach_and_the_state_says_so(self):
        row = bs.search_index(self.index, "dry", source_types=["brush"])["results"][0]
        self.assertEqual(row["name"], "Dry Ink Pen")
        self.assertEqual(row["tag_state"], "tagged")
        self.assertEqual(row["medium_tags"], ["nib-pen"])
        self.assertEqual(row["visual"], "A dry grainy hairline.")
        self.assertEqual(row["visual_basis"], "described-not-measured")

    def test_a_tag_only_search_ranks_by_purity(self):
        envelope = bs.search_index(self.index, tags=["medium=nib-pen"], top=10)
        self.assertEqual(envelope["ranking"], "tag-purity")
        names = self.names(envelope)
        self.assertEqual(set(names), {"Dry Ink Pen", "Wet Ink Brush", "Technical Liner 0.5"})
        # one medium tag outranks two; ties by name
        self.assertEqual(names, ["Dry Ink Pen", "Technical Liner 0.5", "Wet Ink Brush"])
        scores = [r["score"] for r in envelope["results"]]
        self.assertEqual(scores, [1.0, 1.0, 0.5])

    def test_purity_is_the_mean_over_the_tag_filters(self):
        envelope = bs.search_index(self.index, tags=["medium=nib-pen", "use=line-art,shading"], top=10)
        by_name = {r["name"]: r["score"] for r in envelope["results"]}
        self.assertEqual(by_name["Dry Ink Pen"], 1.0)                 # (1/1 + 1/1) / 2
        self.assertEqual(by_name["Wet Ink Brush"], 0.5)               # (1/2 + 1/2) / 2

    def test_two_tag_flags_are_anded_a_comma_list_is_or(self):
        self.assertEqual(sorted(self.found(tags=["medium=nib-pen", "texture=gritty"])), ["Dry Ink Pen"])
        self.assertEqual(sorted(self.found(tags=["medium=charcoal,watercolor"])), ["Wet Ink Brush"])
        self.assertEqual(sorted(self.found(tags=["medium=nib-pen,watercolor", "use=shading"])), ["Wet Ink Brush"])

    def test_the_axis_can_be_the_stored_key(self):
        self.assertEqual(self.found(tags=["medium_tags=watercolor"]), ["Wet Ink Brush"])
        self.assertEqual(self.found(tags=[("medium", ["watercolor"])]), ["Wet Ink Brush"])

    def test_a_query_with_tags_ranks_by_cosine_inside_the_filter(self):
        envelope = bs.search_index(self.index, "dry", tags=["medium=nib-pen"], top=10)
        self.assertEqual(envelope["ranking"], "cosine")
        self.assertEqual(self.names(envelope)[0], "Dry Ink Pen")
        self.assertTrue(set(self.names(envelope)) <= {"Dry Ink Pen", "Wet Ink Brush", "Technical Liner 0.5"})

    def test_tags_are_searchable_as_words(self):
        # nothing in the name says watercolor, the tag does
        names = self.names(bs.search_index(self.index, "watercolor", top=5))
        self.assertIn("Wet Ink Brush", names)

    def test_the_visual_sentence_is_searchable(self):
        names = self.names(bs.search_index(self.index, "hairline", top=5))
        self.assertEqual(names[0], "Dry Ink Pen")

    def test_an_unknown_axis_is_a_usage_error_that_lists_the_axes(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.search_index(self.index, tags=["colour=red"])
        for axis in bs.AXES:
            self.assertIn(axis, str(caught.exception))

    def test_an_unknown_value_is_a_usage_error_with_a_close_match_and_the_list(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.search_index(self.index, tags=["medium=nib-pens"])
        self.assertIn("nib-pen", str(caught.exception))
        self.assertIn("charcoal", str(caught.exception))

    def test_a_malformed_tag_spec_is_a_usage_error(self):
        for spec in ("medium", "medium=", "=nib-pen", "Medium=Nib-Pen", "medium=a b", "medium=a;b"):
            with self.subTest(spec=spec):
                with self.assertRaises(bs.UsageError):
                    bs.search_index(self.index, tags=[spec])

    def test_where_tagged(self):
        self.assertEqual(sorted(self.found(where=["tagged=true"])), ["Dry Ink Pen", "Pumpkin 1", "Technical Liner 0.5",
                                                                     "Wet Ink Brush"])

    def test_a_tag_filter_never_returns_a_note_chunk(self):
        envelope = bs.search_index(self.index, tags=["use=decorating"], source_types=["brush", "set"])
        self.assertEqual({r["source_type"] for r in envelope["results"]}, {"brush"})


class SidecarResolution(WorldCase):
    def test_a_changed_hash_drops_the_tags_and_says_stale(self):
        w = self.world
        write_sidecar(w, "inks", {w.id("Dry Ink Pen"): {"medium_tags": ["nib-pen"], "sha": "0" * 64}})
        index = self.build()
        chunk = bs.resolve_brush(index, "Dry Ink Pen")
        self.assertEqual(chunk["tag_state"], "stale")
        self.assertEqual(chunk["medium_tags"], [])
        self.assertEqual(chunk["visual"], "")
        self.assertTrue(any("mismatch" in warning for warning in index["warnings"]))
        self.assertEqual(bs.search_index(index, tags=["medium=nib-pen"])["total"], 0)

    def test_a_tag_outside_the_vocabulary_is_dropped_with_a_warning(self):
        w = self.world
        write_sidecar(w, "inks", {w.id("Dry Ink Pen"): {"medium_tags": ["nib-pen", "mystery"]}})
        index = self.build()
        self.assertEqual(bs.resolve_brush(index, "Dry Ink Pen")["medium_tags"], ["nib-pen"])
        self.assertTrue(any("mystery" in warning for warning in index["warnings"]))

    def test_an_orphan_entry_warns(self):
        w = self.world
        write_sidecar(w, "inks", {w.id("Dry Ink Pen"): {}})
        path = w.sidecar("inks")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["brushes"]["b_ffffffffffff"] = dict(next(iter(data["brushes"].values())))
        path.write_text(json.dumps(data), encoding="utf-8")
        index = self.build()
        self.assertTrue(any("no catalog record" in warning for warning in index["warnings"]))

    def test_the_entry_follows_the_id_across_sidecars(self):
        w = self.world
        dry = w.id("Dry Ink Pen")
        write_sidecar(w, "stamps", {dry: {"medium_tags": ["nib-pen"]}})           # not its home note
        index = self.build()
        self.assertEqual(bs.resolve_brush(index, dry)["medium_tags"], ["nib-pen"])

    def test_two_current_entries_with_different_tags_warn_and_the_later_wins(self):
        w = self.world
        dry = w.id("Dry Ink Pen")
        write_sidecar(w, "inks", {dry: {"medium_tags": ["nib-pen"]}}, stamp="2026-01-01T00:00:00Z")
        write_sidecar(w, "stamps", {dry: {"medium_tags": ["charcoal"]}}, stamp="2026-02-01T00:00:00Z")
        index = self.build()
        self.assertEqual(bs.resolve_brush(index, dry)["medium_tags"], ["charcoal"])
        self.assertTrue(any("different tags" in warning for warning in index["warnings"]))

    def test_a_current_entry_beats_a_stale_one(self):
        w = self.world
        dry = w.id("Dry Ink Pen")
        write_sidecar(w, "inks", {dry: {"medium_tags": ["nib-pen"]}}, stamp="2026-01-01T00:00:00Z")
        write_sidecar(w, "stamps", {dry: {"medium_tags": ["charcoal"], "sha": "1" * 64}}, stamp="2026-09-01T00:00:00Z")
        index = self.build()
        chunk = bs.resolve_brush(index, dry)
        self.assertEqual((chunk["tag_state"], chunk["medium_tags"]), ("tagged", ["nib-pen"]))

    def test_a_sidecar_that_is_not_json_is_ignored_with_a_warning(self):
        path = self.world.sidecar("inks")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{broken", encoding="utf-8")
        index = self.build()
        self.assertTrue(any("not valid JSON" in warning for warning in index["warnings"]))
        self.assertEqual(index["tagged_count"], 0)


# ── similar ──────────────────────────────────────────────────────────────────

class Similar(WorldCase):
    def setUp(self):
        super().setUp()
        self.index = self.build()

    def test_the_envelope_and_rows(self):
        envelope = bs.similar(self.index, "Dry Ink Pen", top=5)
        self.assertEqual(envelope["method"], "gower-v1")
        self.assertEqual(envelope["query"]["name"], "Dry Ink Pen")
        self.assertEqual(envelope["offset"], 0)
        row = envelope["results"][0]
        self.assertIn("compared_keys", row)
        self.assertIn("coverage", row)
        self.assertIsInstance(row["differs"], list)
        for item in row["differs"]:
            self.assertEqual(set(item), {"key", "query", "other", "delta"})
        self.assertLessEqual(len(row["differs"]), 3)

    def test_the_nearest_brush_differs_in_one_key_not_ten(self):
        envelope = bs.similar(self.index, "Dry Ink Pen", top=20)
        self.assertEqual(envelope["results"][0]["name"], "Wet Ink Brush")
        order = self.names(envelope)
        self.assertLess(order.index("Wet Ink Brush"), order.index("Pumpkin 1"))
        self.assertLess(order.index("Wet Ink Brush"), order.index("Floral Stamp 3"))

    def test_scores_fall_and_the_brush_itself_is_never_listed(self):
        envelope = bs.similar(self.index, "Dry Ink Pen", top=50)
        scores = [r["score"] for r in envelope["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertNotIn(self.world.id("Dry Ink Pen"), self.ids(envelope))
        self.assertEqual(envelope["total"], len(SPECS) - 1)
        self.assertTrue(all(0 <= s <= 1 for s in scores))

    def test_two_identical_brushes_score_one(self):
        envelope = bs.similar(self.index, self.world.id("Pumpkin 1"), top=3)
        self.assertEqual(envelope["results"][0]["name"], "Pumpkin 2")
        self.assertEqual(envelope["results"][0]["score"], 1.0)

    def test_other_sets_leaves_out_the_brushs_own_set(self):
        own = bs.similar(self.index, "Dry Ink Pen", top=50)
        other = bs.similar(self.index, "Dry Ink Pen", top=50, other_sets=True)
        self.assertIn("Wet Ink Brush", self.names(own))
        self.assertNotIn("Wet Ink Brush", self.names(other))
        self.assertTrue(all(r["set"] != "inks" for r in other["results"]))

    def test_filters_apply(self):
        envelope = bs.similar(self.index, "Dry Ink Pen", where=["kind=stamp"], top=20)
        self.assertEqual(sorted(self.names(envelope)), ["Floral Stamp 3", "Pumpkin 1", "Pumpkin 2"])
        envelope = bs.similar(self.index, "Dry Ink Pen", where_not=["library=user"], top=20)
        self.assertTrue(all(r["library"] == "official" for r in envelope["results"]))
        envelope = bs.similar(self.index, "Dry Ink Pen", tags=[], where=["set=paints"], top=20)
        self.assertTrue(envelope["total"] > 0)

    def test_a_tag_filter_applies(self):
        write_sidecar(self.world, "paints", {self.world.id("Charcoal Stick"): {"medium_tags": ["charcoal"]}})
        index = self.build()
        envelope = bs.similar(index, "Dry Ink Pen", tags=["medium=charcoal"])
        self.assertEqual(self.names(envelope), ["Charcoal Stick"])

    def test_by_settings_not_a_library_brush(self):
        probe = dict(self.world.records[self.world.id("Dry Ink Pen")]["settings"])
        envelope = bs.similar(self.index, settings=probe, top=3)
        self.assertEqual(envelope["query"], {"brush_id": None, "settings_keys": len(probe)})
        self.assertEqual(envelope["results"][0]["name"], "Dry Ink Pen")
        self.assertEqual(envelope["results"][0]["score"], 1.0)
        self.assertEqual(envelope["total"], len(SPECS))

    def test_by_a_partial_settings_object_fills_defaults(self):
        envelope = bs.similar(self.index, settings={"plotSpacing": 1.0, "stamp": True}, top=3)
        self.assertEqual(set(self.names(envelope)[:2]), {"Pumpkin 1", "Pumpkin 2"})

    def test_a_name_an_id_and_a_prefix_all_work(self):
        dry = self.world.id("Dry Ink Pen")
        by_id = bs.similar(self.index, dry, top=3)
        self.assertEqual(bs.similar(self.index, "Dry Ink Pen", top=3), by_id)
        self.assertEqual(bs.similar(self.index, dry[:8], top=3), by_id)
        self.assertEqual(bs.similar(self.index, dry[2:8], top=3), by_id)

    def test_an_ambiguous_name_is_a_usage_error_listing_ids(self):
        with self.assertRaises(bs.UsageError) as caught:
            bs.similar(self.index, "Twin")
        for brush in SPECS:
            if brush["name"] == "Twin":
                self.assertIn(brush_id(brush), str(caught.exception))

    def test_an_unknown_brush_is_not_found(self):
        with self.assertRaises(bs.NotFound):
            bs.similar(self.index, "b_000000000000")
        with self.assertRaises(bs.NotFound):
            bs.similar(self.index, "No Such Brush")

    def test_one_of_brush_or_settings(self):
        with self.assertRaises(bs.UsageError):
            bs.similar(self.index)
        with self.assertRaises(bs.UsageError):
            bs.similar(self.index, "Pumpkin 1", settings={"plotSpacing": 1})
        with self.assertRaises(bs.UsageError):
            bs.similar(self.index, settings=[1, 2])

    def test_the_order_is_the_same_every_time(self):
        first = bs.similar(self.index, "Charcoal Stick", top=20)
        self.assertEqual(bs.similar(self.build(), "Charcoal Stick", top=20), first)

    def test_a_real_key_holding_a_tag_does_not_break_it(self):
        envelope = bs.similar(self.index, "Tagged Real", top=3)
        self.assertEqual(len(envelope["results"]), 3)
        envelope = bs.similar(self.index, "Dry Ink Pen", top=50)
        self.assertIn("Tagged Real", self.names(envelope))

    def test_the_shape_and_grain_references_weigh_in(self):
        stats = self.index["param_stats"]
        self.assertIn("plotSpacing", stats)
        self.assertEqual(self.index["similar"]["weights"], {"default": 1, "shape_ref": 4, "grain_ref": 3})
        envelope = bs.similar(self.index, "Dry Ink Pen", top=1)
        keys = {d["key"] for r in envelope["results"] for d in r["differs"]}
        self.assertTrue(keys)

    def test_the_numbers_are_scaled_by_the_percentile_range(self):
        stat = self.index["param_stats"]["plotSpacing"]
        self.assertEqual(stat["kind"], "num")
        values = sorted(self.world.records[i]["settings"]["plotSpacing"] for i in self.world.records)
        self.assertEqual(stat["lo"], values[int(round(0.01 * (len(values) - 1)))])
        self.assertEqual(stat["hi"], values[int(round(0.99 * (len(values) - 1)))])
        self.assertEqual(self.index["param_stats"]["blendMode"]["kind"], "enum")
        self.assertEqual(self.index["param_stats"]["stamp"]["kind"], "bool")

    def test_the_excluded_keys_never_take_part(self):
        for key in self.index["param_stats"]:
            self.assertFalse(key.endswith("Version") or key.startswith("saved") or key in
                             {"paintSize", "color", "name", "version", "creationDate"})


# ── facets, brush lookup, chunks, verify ─────────────────────────────────────

class FacetCounts(WorldCase):
    def setUp(self):
        super().setUp()
        write_sidecar(self.world, "inks", {self.world.id("Dry Ink Pen"): {"medium_tags": ["nib-pen"]}})
        self.index = self.build()

    def test_counts_are_over_the_brushes(self):
        result = bs.facet_counts(self.index)
        self.assertEqual(result["brushes"], len(SPECS))
        self.assertEqual(result["facets"]["kind"]["values"], {"stamp": 3, "stroke": len(SPECS) - 3})
        self.assertEqual(result["facets"]["is_stamp"]["kind"], "bool")
        self.assertEqual(result["facets"]["is_stamp"]["values"]["true"], 3)
        self.assertEqual(result["tag_state"], {"tagged": 1, "stale": 0, "untagged": len(SPECS) - 1})

    def test_filters_narrow_the_counts(self):
        result = bs.facet_counts(self.index, where=["library=official"])
        self.assertEqual(result["brushes"], 4)

    def test_every_vocabulary_tag_is_listed_with_its_count_and_definition(self):
        result = bs.facet_counts(self.index)
        self.assertEqual(list(result["tags"]), list(bs.AXES))
        medium = result["tags"]["medium"]
        self.assertEqual(medium["values"], {"nib-pen": 1, "charcoal": 0, "watercolor": 0})
        self.assertEqual(medium["definitions"]["charcoal"], "coarse crumbly black")
        self.assertEqual(medium["tagged"], 1)

    def test_numbers_have_a_range(self):
        index = self.index
        result = bs.facet_counts(index, settings=True)
        self.assertEqual(result["numeric"]["plotSpacing"]["max"], 1.0)
        self.assertIn("plotSpacing", result["where_keys"]["settings"])
        self.assertEqual(result["where_keys"]["builtin"], list(bs.BUILTIN_KEYS))


class ResolveBrush(WorldCase):
    def setUp(self):
        super().setUp()
        self.index = self.build()

    def test_every_form(self):
        pumpkin = self.world.id("Pumpkin 1")
        for ref in (pumpkin, pumpkin[2:], pumpkin[:8], "Pumpkin 1", "pumpkin 1", " Pumpkin 1 "):
            with self.subTest(ref=ref):
                self.assertEqual(bs.resolve_brush(self.index, ref)["brush_id"], pumpkin)

    def test_a_short_prefix_is_not_enough(self):
        with self.assertRaises(bs.NotFound):
            bs.resolve_brush(self.index, self.world.id("Pumpkin 1")[:6])    # b_ and 4 hex

    def test_an_ambiguous_prefix_lists_the_ids(self):
        ids = sorted(self.world.records)
        shared = os.path.commonprefix([ids[0], ids[1]])
        if len(shared) >= 8:                       # only if two ids happen to share 6 hex characters
            with self.assertRaises(bs.UsageError):
                bs.resolve_brush(self.index, shared)

    def test_not_found(self):
        with self.assertRaises(bs.NotFound):
            bs.resolve_brush(self.index, "Nothing Like This")


class ChunksFor(WorldCase):
    def test_the_chunks_of_a_note(self):
        result = bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md")
        self.assertEqual(result["file"], "02_Vendor_Packs/inks.md")
        self.assertEqual(result["set"], "inks")
        self.assertEqual(result["library"], "user")
        self.assertEqual(result["chunker_version"], "b1")
        self.assertEqual(result["brush_count"], 5)
        self.assertRegex(result["body_fingerprint"], r"^sha256:16:[0-9a-f]{16}$")
        brushes = [c for c in result["chunks"] if c["brush_id"]]
        self.assertEqual([c["name"] for c in brushes],
                         ["Dry Ink Pen", "Wet Ink Brush", "Technical Liner 0.5", "Twin", "Twin"])
        dry = brushes[0]
        self.assertEqual(dry["content_fp"], self.world.records[dry["brush_id"]]["content_sha256"][:16])
        self.assertEqual(dry["tag_state"], "untagged")
        self.assertIn("text", dry)
        lines = self.world.note_path("inks").read_text(encoding="utf-8").split("\n")
        self.assertEqual(lines[dry["start_line"] - 1], "## Dry Ink Pen")

    def test_ids_range_untagged_and_brief(self):
        dry, wet = self.world.id("Dry Ink Pen"), self.world.id("Wet Ink Brush")
        result = bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md", ids=[dry, wet], brief=True)
        self.assertEqual([c["brush_id"] for c in result["chunks"]], [dry, wet])
        self.assertTrue(all("text" not in c for c in result["chunks"]))
        self.assertEqual(len(bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md", ids=f"{dry},{wet}")["chunks"]), 2)
        write_sidecar(self.world, "inks", {dry: {}})
        result = bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md", untagged=True)
        self.assertNotIn(dry, [c["brush_id"] for c in result["chunks"]])
        self.assertEqual(len(result["chunks"]), 4)
        first = bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md", ids=[dry])["chunks"][0]
        window = bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md",
                               line_range=f"{first['start_line']}-{first['start_line']}")
        self.assertEqual([c["brush_id"] for c in window["chunks"]], [dry])

    def test_a_note_that_is_not_there_is_not_found(self):
        with self.assertRaises(bs.NotFound):
            bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/nope.md")

    def test_a_path_that_leaves_the_vault_is_a_usage_error(self):
        for bad in ("../x.md", "/etc/passwd", "C:/x.md", ""):
            with self.subTest(note=bad):
                with self.assertRaises(bs.UsageError):
                    bs.chunks_for(self.vault, self.catalog, bad)

    def test_a_bad_line_range_is_a_usage_error(self):
        with self.assertRaises(bs.UsageError):
            bs.chunks_for(self.vault, self.catalog, "02_Vendor_Packs/inks.md", line_range="five")


class Verify(WorldCase):
    def digest(self, *values, cite=True):
        dry = self.world.id("Dry Ink Pen")
        record = self.world.records[dry]
        index = self.build()
        chunk = bs.resolve_brush(index, dry)
        head = f"### {dry} -- Dry Ink Pen ({chunk['note']}, lines {chunk['start_line']}-{chunk['end_line']})" if cite \
            else f"### {dry} -- Dry Ink Pen (02_Vendor_Packs/inks.md, lines 1-2)"
        return "\n".join([head, "", "- a bullet", "", "Exact values:", *values, ""]), record

    def test_an_exact_value_passes_a_rounded_one_is_marked(self):
        text, record = self.digest("- `plotSpacing` = `0.01`", "- `maxSize` = `0.2`", '- name: "Dry Ink Pen"',
                                   "- `maxSize` = `0.25`", '- name: "Dry Ink"', "- `noSuchKey` = `1`")
        out, marked = bs.verify_digest(self.vault, self.catalog, text)
        lines = out.split("\n")
        self.assertEqual(marked, 3)
        for line in lines:
            if "0.25" in line or '"Dry Ink"' in line or "noSuchKey" in line:
                self.assertTrue(line.endswith(bs.UNVERIFIED_MARKER), line)
            elif line.startswith("- `") or line.startswith("- name"):
                self.assertNotIn("UNVERIFIED", line)

    def test_a_wrong_citation_marks_the_heading(self):
        text, _ = self.digest("- `plotSpacing` = `0.01`", cite=False)
        out, marked = bs.verify_digest(self.vault, self.catalog, text)
        self.assertGreaterEqual(marked, 1)
        self.assertTrue(out.split("\n")[0].endswith(bs.UNVERIFIED_MARKER))

    def test_an_unknown_brush_is_marked_and_none_is_left_alone(self):
        text = "### b_ffffffffffff -- X (a.md, lines 1-2)\n\nExact values:\n- (none)\n- `plotSpacing` = `1`\n"
        out, marked = bs.verify_digest(self.vault, self.catalog, text)
        self.assertEqual(marked, 2)
        self.assertNotIn("(none)  " + bs.UNVERIFIED_MARKER, out)

    def test_the_marker_is_the_creative_writing_one(self):
        self.assertEqual(bs.UNVERIFIED_MARKER, "[UNVERIFIED -- not found in source text, do not cite as exact]")
        agent = BRUSHES.parent / ".claude" / "agents" / "creative-writing-librarian-native.md"
        if agent.is_file():
            self.assertIn(bs.UNVERIFIED_MARKER, agent.read_text(encoding="utf-8"))


# ── the command line ─────────────────────────────────────────────────────────

class CommandLine(WorldCase):
    def setUp(self):
        super().setUp()
        write_sidecar(self.world, "inks", {self.world.id("Dry Ink Pen"): {
            "medium_tags": ["nib-pen"], "use_tags": ["line-art"], "visual": "A dry grainy hairline."}})

    def index(self):
        code, out, err = self.cli_world("index")
        self.assertEqual(code, 0, out + err)
        return out

    def test_the_verbs_are_the_contracts(self):
        parser = bs.build_parser()
        verbs = next(a for a in parser._actions if isinstance(a.choices, dict))
        self.assertEqual(list(verbs.choices), ["index", "search", "ask", "similar", "facets", "files", "chunks",
                                               "verify", "brush"])

    def test_no_index_is_exit_2(self):
        code, out, err = self.cli_world("search", "ink")
        self.assertEqual(code, 2)
        self.assertIn("index", err)

    def test_index_with_no_vault_folder_is_exit_2(self):
        code, out, err = self.cli("index", "--vault", str(self.tmp / "nowhere"), "--catalog", str(self.catalog))
        self.assertEqual(code, 2)
        self.assertIn("vault", err)
        self.assertFalse((self.tmp / "nowhere").exists())

    def test_index_prints_a_summary_and_exit_0(self):
        out = self.index()
        self.assertRegex(out, r"Indexed \d+ notes -> \d+ chunks \(13 brushes, 1 tagged\)")
        self.assertTrue((self.vault / "tools" / "rag_index" / "index.json").is_file())

    def test_index_check_exits_0_fresh_1_stale(self):
        code, out, _ = self.cli_world("index", "--check")
        self.assertEqual(code, 1)                     # no index yet
        self.assertIn("stale", out)
        self.index()
        code, out, _ = self.cli_world("index", "--check")
        self.assertEqual((code, out.split(":")[0]), (0, "fresh"))
        write_sidecar(self.world, "inks", {self.world.id("Wet Ink Brush"): {}})
        code, out, _ = self.cli_world("index", "--check")
        self.assertEqual(code, 1)
        self.assertIn("sidecars", out)
        self.index()
        self.assertEqual(self.cli_world("index", "--check")[0], 0)

    def test_search_text_and_json(self):
        self.index()
        code, out, _ = self.cli_world("search", "dry ink", "--top", "2")
        self.assertEqual(code, 0)
        self.assertIn("Dry Ink Pen", out)
        self.assertIn("tags: medium=nib-pen", out)
        self.assertIn("visual (described, not measured): A dry grainy hairline.", out)
        self.assertRegex(out, r"2 of \d+ matches shown\.  ranking: cosine")
        code, out, _ = self.cli_world("search", "dry ink", "--top", "2", "--json")
        data = json.loads(out)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["name"], "Dry Ink Pen")
        self.assertEqual(data["ranking"], "cosine")

    def test_ask_is_search(self):
        self.index()
        self.assertEqual(self.cli_world("ask", "dry ink", "--json"), self.cli_world("search", "dry ink", "--json"))

    def test_no_results_is_exit_0(self):
        self.index()
        code, out, _ = self.cli_world("search", "zzzzqx")
        self.assertEqual((code, out), (0, "No results found.\n"))
        code, out, _ = self.cli_world("search", "zzzzqx", "--json")
        self.assertEqual((code, json.loads(out)["total"]), (0, 0))

    def test_filters_without_a_query(self):
        self.index()
        code, out, _ = self.cli_world("search", "--tag", "medium=nib-pen", "--json")
        self.assertEqual(code, 0)
        self.assertEqual([r["name"] for r in json.loads(out)["results"]], ["Dry Ink Pen"])
        code, out, _ = self.cli_world("search", "--where", "kind=stamp", "--where-not", "set=stamps", "--json")
        self.assertEqual(json.loads(out)["total"], 0)
        code, out, _ = self.cli_world("search", "--where", "spacing=0.9..", "--source", "brush", "--json")
        self.assertEqual(code, 0)

    def test_nothing_to_search_for_is_exit_2(self):
        self.index()
        self.assertEqual(self.cli_world("search")[0], 2)

    def test_bad_arguments_are_exit_2(self):
        self.index()
        for argv in (("search", "x", "--tag", "colour=red"), ("search", "x", "--tag", "medium=zzz"),
                     ("search", "x", "--where", "nope=1"), ("search", "x", "--where", "spacing>1"),
                     ("search", "x", "--source", "picture"), ("search", "x", "--top", "-1"),
                     ("similar", "Twin"), ("facets", "--axis", "nope")):
            with self.subTest(argv=argv):
                self.assertEqual(self.cli_world(*argv)[0], 2)
        self.assertEqual(self.cli("search", "x", "--bogus")[0], 2)
        self.assertEqual(self.cli()[0], 2)

    def test_error_messages_list_the_valid_choices(self):
        self.index()
        _, _, err = self.cli_world("search", "x", "--tag", "medium=zzz")
        self.assertIn("nib-pen", err)
        _, _, err = self.cli_world("search", "x", "--tag", "colour=red")
        self.assertIn("medium, mark, texture", err)

    def test_similar_and_not_found(self):
        self.index()
        code, out, _ = self.cli_world("similar", "Dry Ink Pen", "--top", "2")
        self.assertEqual(code, 0)
        self.assertIn("gower-v1", out)
        self.assertIn("compared", out)
        code, out, _ = self.cli_world("similar", "Dry Ink Pen", "--json", "--other-sets")
        self.assertEqual(json.loads(out)["method"], "gower-v1")
        self.assertEqual(self.cli_world("similar", "No Such Brush")[0], 1)

    def test_facets_text_and_json(self):
        self.index()
        code, out, _ = self.cli_world("facets")
        self.assertEqual(code, 0)
        self.assertIn("13 brushes", out)
        self.assertIn("nib-pen (1)", out)
        code, out, _ = self.cli_world("facets", "--axis", "use", "--json")
        data = json.loads(out)
        self.assertEqual(list(data["tags"]), ["use"])
        self.assertEqual(data["tags"]["use"]["values"]["line-art"], 1)
        code, out, _ = self.cli_world("facets", "--settings", "--json", "--where", "library=official")
        self.assertEqual(json.loads(out)["brushes"], 4)

    def test_files(self):
        code, out, _ = self.cli_world("files")
        self.assertEqual(code, 0)
        self.assertIn("02_Vendor_Packs/inks.md  [set]", out)
        code, out, _ = self.cli_world("files", "--type", "moc", "--json")
        self.assertEqual(json.loads(out), [{"file": "02_Vendor_Packs/_index.md", "source_type": "moc"}])

    def test_chunks(self):
        code, out, _ = self.cli_world("chunks", "02_Vendor_Packs/inks.md", "--json", "--brief")
        data = json.loads(out)
        self.assertEqual(data["brush_count"], 5)
        code, out, _ = self.cli_world("chunks", "02_Vendor_Packs/inks.md", "--untagged")
        self.assertEqual(code, 0)
        self.assertNotIn(self.world.id("Dry Ink Pen"), out)
        self.assertEqual(self.cli_world("chunks", "02_Vendor_Packs/nope.md")[0], 1)
        self.assertEqual(self.cli_world("chunks", "../x.md")[0], 2)

    def test_brush(self):
        self.index()
        code, out, _ = self.cli_world("brush", "Dry Ink Pen", "--settings")
        self.assertEqual(code, 0)
        self.assertIn("tags (tagged): medium=nib-pen", out)
        self.assertIn("plotSpacing = 0.01", out)
        code, out, _ = self.cli_world("brush", self.world.id("Pumpkin 1"), "--json")
        self.assertEqual(json.loads(out)["name"], "Pumpkin 1")
        self.assertEqual(self.cli_world("brush", "Nothing")[0], 1)
        self.assertEqual(self.cli_world("brush", "Twin")[0], 2)

    def test_verify_from_stdin_and_strict(self):
        self.index()
        dry = self.world.id("Dry Ink Pen")
        digest = f"### {dry} -- x (02_Vendor_Packs/inks.md, lines 1-1)\n\nExact values:\n- `plotSpacing` = `0.5`\n"
        code, out, err = self.cli_world("verify", stdin=digest)
        self.assertEqual(code, 0)
        self.assertIn("UNVERIFIED", out)
        self.assertEqual(self.cli_world("verify", "--strict", stdin=digest)[0], 1)
        self.assertEqual(self.cli_world("verify", "--strict", stdin="nothing here\n")[0], 0)

    def test_the_environment_variables_are_honoured(self):
        env = {"ROSW_BRUSHES_VAULT": str(self.vault), "ROSW_BRUSHES_CATALOG": str(self.catalog)}
        with mock.patch.dict(os.environ, env):
            code, out, err = self.cli("index")
        self.assertEqual(code, 0, err)
        with mock.patch.dict(os.environ, {"ROSW_BRUSHES_ROOT": str(self.world.root)}):
            code, out, _ = self.cli("search", "ink", "--json")
        self.assertEqual(code, 0)
        self.assertGreater(json.loads(out)["total"], 0)

    def test_a_script_run_under_python_dash_I_from_another_folder(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("ROSW_BRUSHES_")}
        elsewhere = self.tmp / "cwd"
        elsewhere.mkdir()
        run = lambda *a: subprocess.run([sys.executable, "-I", str(SEARCH), *a, *self.world.args()],
                                        capture_output=True, text=True, encoding="utf-8", cwd=elsewhere, env=env)
        built = run("index")
        self.assertEqual(built.returncode, 0, built.stderr)
        found = run("search", "pumpkin", "--json")
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertEqual(json.loads(found.stdout)["results"][0]["name"], "Pumpkin 1")
        self.assertEqual(run("search", "ink", "--tag", "medium=zzz").returncode, 2)
        self.assertEqual(run("brush", "Nothing").returncode, 1)


class Offline(WorldCase):
    def test_the_script_imports_no_network_module(self):
        tree = ast.parse(SEARCH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        banned = {"socket", "ssl", "urllib", "http", "ftplib", "smtplib", "requests", "asyncio", "subprocess",
                  "yaml", "numpy", "pipeline", "brush_common"}
        self.assertEqual(imported & banned, set())

    def test_everything_runs_with_every_socket_refused(self):
        import socket

        def refuse(*a, **k):
            raise AssertionError("a network call was made")
        with mock.patch.object(socket, "socket", refuse), mock.patch.object(socket, "create_connection", refuse), \
                mock.patch.object(socket, "getaddrinfo", refuse):
            index = bs.build_index(self.vault, self.catalog, write=False)
            bs.search_index(index, "ink")
            bs.similar(index, "Dry Ink Pen")
            bs.facet_counts(index)

    def test_every_text_open_names_utf8_and_every_write_is_lf(self):
        source = SEARCH.read_text(encoding="utf-8")
        for match in re.finditer(r"\bopen\(([^)]*)\)", source):
            self.assertIn("encoding=", match.group(1), match.group(0))
        for match in re.finditer(r"\.(read_text|write_text)\(([^)]*)\)", source):
            self.assertIn("encoding=", match.group(2), match.group(0))
        self.assertNotIn(b"\r", SEARCH.read_bytes())

    def test_the_tool_does_not_import_the_pipeline(self):
        self.assertNotIn("import brush_common", SEARCH.read_text(encoding="utf-8"))


# ── a catalog that ingest.py built from the fixture library ──────────────────

class FromIngest(fixtures.BrushCase):
    """The real shape of a record, from the real builder, over the synthetic library."""

    def setUp(self):
        super().setUp()
        import ingest
        self.root = self.tmp / "brushes"
        fixtures.write_library(self.root / "library")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ingest.main(["build", "--root", str(self.root)])
        self.assertEqual(code, 0, out.getvalue() + err.getvalue())
        self.vault, self.catalog = self.root / "vault", self.root / "catalog"
        self.vault.mkdir(parents=True, exist_ok=True)

    def test_an_index_builds_and_searches_over_ingests_records(self):
        index = bs.build_index(self.vault, self.catalog, write=False)
        catalog = json.loads((self.catalog / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(index["brush_chunk_count"], catalog["counts"]["brushes"])
        envelope = bs.search_index(index, "inker")
        self.assertEqual(envelope["results"][0]["name"], "Demo Inker")
        self.assertEqual(bs.search_index(index, "conte")["results"][0]["name"], "Broken Cont\u00e9")
        row = envelope["results"][0]
        self.assertEqual(row["pack"], "demo-pack")
        self.assertEqual(row["library"], "user")
        self.assertIsNone(row["note"])
        self.assertEqual(bs.search_index(index, where=["kind=stamp"], top=10)["total"], 1)
        self.assertEqual(bs.facet_counts(index)["brushes"], catalog["counts"]["brushes"])
        similar = bs.similar(index, "Modern Plain")
        self.assertGreater(similar["total"], 0)

    def test_every_facet_ingest_wrote_is_a_where_key(self):
        index = bs.build_index(self.vault, self.catalog, write=False)
        spec = (BRUSHES / "spec.yaml").read_text(encoding="utf-8")
        names = re.findall(r"^  - ([a-z_]+)$", spec.split("\nfacets:\n", 1)[1].split("\nfacet_owner", 1)[0], re.M)
        self.assertEqual(sorted(names), sorted(index["where_keys"]["facets"]))


# ── the real catalog, read-only ──────────────────────────────────────────────

@unittest.skipUnless((REAL_CATALOG / "catalog.json").is_file() and (REAL_CATALOG / "brushes").is_dir()
                     and REAL_VOCABULARY.is_file(), "the real catalog is not built")
class RealCatalog(unittest.TestCase):
    """Relevance sanity over the 990 real brushes (names, sets and facets; most
    are untagged). Reads catalog/ and vault/ and writes nothing. It prints the
    top results of its queries so a person can read them; it never asserts an
    exact id."""

    @classmethod
    def setUpClass(cls):
        cls.index = bs.build_index(BRUSHES / "vault", REAL_CATALOG, write=False)
        cls.verbose = os.environ.get("ROSW_BRUSHES_VERBOSE")

    def top(self, query, n=5, **kw):
        rows = bs.search_index(self.index, query, top=n, **kw)["results"]
        if self.verbose:
            print(f"\n  {query!r}")
            for r in rows:
                print(f"    {r['score']:.3f}  {r['name'].strip()}  [{r['set_title']}]")
        return rows

    def blob(self, row):
        words = row["name"] + " " + " ".join(row["facets"].get(k) or "" for k in ("kind", "taper", "size_class"))
        return (words + " " + (row["set_title"] or "") + " " + (row["pack"] or "")).lower()

    def test_the_index_covers_the_catalog(self):
        catalog = json.loads((REAL_CATALOG / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(self.index["brush_chunk_count"], catalog["counts"]["brushes"])
        self.assertGreater(self.index["vocab_size"], 200)

    def test_dry_grainy_ink_for_comic_shading(self):
        rows = self.top("dry grainy ink for comic shading")
        self.assertEqual(len(rows), 5)
        plausible = ("ink", "dry", "grain", "shad", "pen", "hatch", "graphite", "rake", "pencil", "toner", "tone",
                     "comic", "grit")
        hits = [r for r in rows if any(word in self.blob(r) for word in plausible)]
        self.assertGreaterEqual(len(hits), 4, [r["name"] for r in rows])

    def test_ink_finds_inks(self):
        rows = self.top("ink")
        self.assertTrue(all("ink" in self.blob(r) for r in rows), [r["name"] for r in rows])

    def test_charcoal_finds_charcoals(self):
        rows = self.top("charcoal", 6)
        self.assertGreaterEqual(sum("charcoal" in self.blob(r) or "coal" in self.blob(r) for r in rows), 5)

    def test_watercolour_wash_finds_watercolour_washes(self):
        rows = self.top("watercolour wash")
        self.assertTrue(all("wash" in self.blob(r) or "watercolo" in self.blob(r) for r in rows))

    def test_stipple(self):
        rows = self.top("stipple", 3)
        self.assertTrue("stipple" in self.blob(rows[0]))

    def test_calligraphy(self):
        rows = self.top("calligraphy", 3)
        self.assertTrue(any("calligraph" in self.blob(r) for r in rows))

    def test_food_stamps_reach_the_sweet_treats(self):
        rows = self.top("food", 8)
        self.assertTrue(any(r["set"] == "sweet-treats" for r in rows), [r["name"] for r in rows])

    def test_halftone_and_grain_queries_return_something_sensible(self):
        self.assertIn("halftone", self.blob(self.top("halftone", 1)[0]))
        self.assertTrue(any("grain" in self.blob(r) for r in self.top("grain", 5)))

    def test_similar_runs_on_real_settings(self):
        envelope = bs.similar(self.index, "Technical Pen", other_sets=True, top=5) \
            if self._unique("Technical Pen") else bs.similar(self.index, self._first("Technical Pen"), top=5)
        self.assertEqual(len(envelope["results"]), 5)
        self.assertTrue(all(0 <= r["score"] <= 1 for r in envelope["results"]))

    def _first(self, name):
        return next(c["brush_id"] for c in self.index["chunks"] if c.get("name") == name)

    def _unique(self, name):
        return sum(1 for c in self.index["chunks"] if c.get("name") == name) == 1

    def test_the_real_index_has_no_absolute_path(self):
        text = json.dumps(self.index, ensure_ascii=False)
        self.assertNotIn(str(BRUSHES), text)
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]", text))


if __name__ == "__main__":
    unittest.main()
