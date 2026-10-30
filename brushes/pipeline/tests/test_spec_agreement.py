"""The contract is stated in three places. They must agree.

spec.yaml declares it, the code implements it, docs/CONTRACTS.md explains it.
These tests read the real files and write nothing. They cover what exists
today: a block of the spec whose module is not built yet is checked for its
own shape and against the document, and gets bound to its code when that lands.

    python -m unittest discover -s brushes/pipeline/tests
"""

import ast
import io
import json
import re
import sys
import tokenize
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:          # an isolated interpreter (-I) hides a pyyaml in the user's site-packages
    yaml = None

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import brush_file  # noqa: E402
import container  # noqa: E402
import device_tests  # noqa: E402
import fetch_base_library  # noqa: E402
import fixtures  # noqa: E402
import identity  # noqa: E402
import ingest  # noqa: E402
import mcp_server  # noqa: E402
import notes  # noqa: E402
import previews  # noqa: E402

BRUSHES = PIPELINE.parent
REPO = BRUSHES.parent
SPEC_PATH = BRUSHES / "spec.yaml"
CONTRACTS_PATH = BRUSHES / "docs" / "CONTRACTS.md"
SOURCES_PATH = BRUSHES / "library" / "sources.json"

MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|Windows|Program)|/Users/|/home/")


def read(path):
    return Path(path).read_text(encoding="utf-8")


class Loaded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if yaml is None:
            raise unittest.SkipTest("pyyaml cannot be imported here (an isolated interpreter hides "
                                    "the user's site); run without -I to check the spec")
        cls.spec_text = read(SPEC_PATH)
        cls.spec = yaml.safe_load(cls.spec_text)
        cls.contracts = read(CONTRACTS_PATH)
        cls.sources = json.loads(read(SOURCES_PATH))

    def section(self, heading):
        """The text of one `## ` section of CONTRACTS.md."""
        start = self.contracts.index(f"\n## {heading}")
        end = self.contracts.find("\n## F", start + 4)
        for other in ("\n## The library manifest", "\n## Device tests", "\n## Test fixtures"):
            at = self.contracts.find(other, start + 4)
            if at != -1 and (end == -1 or at < end):
                end = at
        return self.contracts[start:end if end != -1 else None]


class TheFile(Loaded):
    def test_it_loads_and_is_version_1(self):
        self.assertIsInstance(self.spec, dict)
        self.assertEqual(self.spec["version"], 1)
        self.assertEqual(self.spec["tool_root"], BRUSHES.name)

    def test_the_header_says_what_is_declared_and_what_is_implemented(self):
        header = self.spec_text.split("\nversion:", 1)[0]
        self.assertTrue(header.startswith("# brushes spec"))
        self.assertTrue(all(line.startswith("#") or not line for line in header.splitlines()))
        for phrase in ("DECLARES", "IMPLEMENTS", "pipeline/identity.py", "pipeline/brush_common.py",
                       "test_spec_agreement.py", "under construction", "does NOT own"):
            self.assertIn(phrase, header)

    def test_it_points_at_the_contract_document(self):
        self.assertEqual(BRUSHES / self.spec["contract"], CONTRACTS_PATH)
        self.assertTrue(CONTRACTS_PATH.is_file())
        self.assertIn("spec.yaml", self.contracts)

    def test_what_it_says_exists_does(self):
        self.assertEqual(self.spec["build"]["state"], "under_construction")
        for relative in self.spec["build"]["exists"]:
            self.assertTrue((BRUSHES / relative).is_file(), relative)

    def test_every_module_on_disk_is_listed_as_existing(self):
        """`build.exists` is what a reader takes for the state of the tool: a
        script that is there and not listed is as wrong as one listed and not there."""
        exists = set(self.spec["build"]["exists"])
        on_disk = {f"pipeline/{path.name}" for path in PIPELINE.glob("*.py")}
        self.assertEqual(on_disk - exists, set())
        self.assertEqual({item for item in exists if item.startswith("pipeline/") and "/tests/" not in item},
                         on_disk)
        readme = read(BRUSHES / "README.md")
        for script in sorted(on_disk):
            self.assertIn(f"| `{script}` |", readme, "the README's table of what is here now")

    def test_the_built_verbs_are_what_each_parser_accepts(self):
        """`cli.scripts` is the full contract; `build.built_verbs` is what runs today."""
        built = self.spec["build"]["built_verbs"]
        parsers = {"pipeline/fetch_base_library.py": fetch_base_library.build_parser(),
                   "pipeline/ingest.py": ingest.build_parser(),
                   "pipeline/previews.py": previews.build_parser(),
                   "pipeline/notes.py": notes.build_parser(),
                   "pipeline/device_tests.py": device_tests.build_parser(),
                   "pipeline/brush_file.py": brush_file.build_parser()}
        self.assertEqual(set(built), set(parsers))
        for script, parser in parsers.items():
            verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
            self.assertEqual(list(verbs.choices), built[script], script)
            declared = self.spec["cli"]["scripts"][script]["verbs"]
            self.assertTrue(set(built[script]) <= set(declared), script)
            self.assertIn(script, self.spec["build"]["exists"])
        missing = set(self.spec["cli"]["scripts"]["pipeline/ingest.py"]["verbs"]) - set(built["pipeline/ingest.py"])
        self.assertEqual(missing, set(),
                         "when a verb lands, add it here and switch on its row of mcp_server.NEXT_STEPS")
        for what, script, verb, is_built in mcp_server.NEXT_STEPS:
            if script in built:
                self.assertEqual(is_built, verb in built[script], (script, verb))
            else:
                self.assertEqual(is_built, (BRUSHES / script).is_file(), (script, verb))

    def test_files_are_lf_and_name_no_machine_path(self):
        for path in (SPEC_PATH, CONTRACTS_PATH, SOURCES_PATH, BRUSHES / "README.md",
                     BRUSHES / "library" / "README.md", BRUSHES / "library" / ".gitignore",
                     BRUSHES / "vault" / ".gitignore", PIPELINE / "identity.py",
                     PIPELINE / "brush_common.py", PIPELINE / "zip_writer.py",
                     PIPELINE / "fetch_base_library.py", PIPELINE / "ingest.py",
                     PIPELINE / "device_tests.py", PIPELINE / "tests" / "fixtures.py"):
            raw = path.read_bytes()
            self.assertNotIn(b"\r", raw, path.name)
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path.name)
            self.assertIsNone(MACHINE_PATH.search(raw.decode("utf-8")), path.name)


class ExitCodesRootsAndPort(Loaded):
    def test_exit_codes(self):
        self.assertEqual(self.spec["exit_codes"],
                         {"ok": bc.EXIT_OK, "refused": bc.EXIT_REFUSED, "usage": bc.EXIT_USAGE})
        for code, constant in ((0, "ok"), (1, "refused"), (2, "usage")):
            self.assertEqual(self.spec["exit_codes"][constant], code)

    def test_environment_names_and_flags(self):
        roots = self.spec["roots"]
        self.assertEqual(roots["order"], ["flag", "env", "default"])
        self.assertEqual({name: roots[name]["env"] for name in bc.ENV_NAMES}, bc.ENV_NAMES)
        self.assertEqual({name: roots[name]["flag"] for name in bc.FLAGS}, bc.FLAGS)
        self.assertIsNone(roots["index"]["flag"])
        self.assertEqual(roots["index"]["vault_tools_flag"], "--index",
                         "only the vault tools take --index; it is declared, not left to prose")
        self.assertEqual(roots["module"], "pipeline/brush_common.py")
        self.assertTrue((BRUSHES / roots["module"]).is_file())

    def test_the_vault_tools_read_all_five_names(self):
        """With only ROSW_BRUSHES_ROOT set, a vault tool must land on the same
        vault and catalog as the pipeline scripts and the servers."""
        tools = self.spec["roots"]["vault_tools"]
        self.assertEqual(tools["flags"], ["--vault", "--catalog", "--index"])
        self.assertEqual(tools["env"], [bc.ENV_VAULT, bc.ENV_CATALOG, bc.ENV_INDEX, bc.ENV_ROOT])
        self.assertLess(tools["env"].index(bc.ENV_VAULT), tools["env"].index(bc.ENV_ROOT),
                        "a folder's own variable beats the root")
        section = " ".join(self.section("F2.").split())
        self.assertIn("then `ROSW_BRUSHES_ROOT`, as `<ROOT>/vault` and `<ROOT>/catalog`", section)
        self.assertIn("A test keeps all five names equal to `ENV_NAMES`", section)
        self.assertIn("`--index` exists only there", section)
        for path in sorted((BRUSHES / "vault" / "tools").glob("*.py")):
            source = read(path)
            named = set(re.findall(r"ROSW_BRUSHES_[A-Z_]+", source))
            self.assertTrue(named <= set(bc.ENV_NAMES.values()), path.name)
            self.assertTrue({bc.ENV_VAULT, bc.ENV_CATALOG, bc.ENV_ROOT} <= named, path.name)

    def test_the_paths_tuple(self):
        self.assertEqual(tuple(self.spec["roots"]["paths"]), bc.Paths._fields)
        derived = self.spec["roots"]["derived"]
        self.assertEqual(set(derived) | set(bc.ENV_NAMES), set(bc.Paths._fields))

    def test_the_declared_defaults_are_what_the_code_resolves(self):
        fixtures.clean_env(self)
        root = fixtures.temp_dir(self)
        paths = bc.resolve_paths(root=root)
        layout = {"<root>": paths.root, "<vault>": paths.vault, "<code>": bc.TOOL_ROOT}

        def expand(text):
            token, _, rest = text.partition("/")
            return layout[token] / rest if rest else layout[token]

        self.assertEqual(self.spec["roots"]["root"]["default"], "<code>")
        self.assertEqual(bc.resolve_paths().root, expand("<code>"))
        for name in ("library", "catalog", "vault", "index"):
            self.assertEqual(getattr(paths, name), expand(self.spec["roots"][name]["default"]), name)
        for name, text in self.spec["roots"]["derived"].items():
            self.assertEqual(getattr(paths, name), expand(text), name)

    def test_the_schema_and_the_app_are_code_not_data(self):
        """F2, F3 and F10 once disagreed on where schema/ lives under a moved
        root. One answer, in the code, the spec and the document."""
        derived = self.spec["roots"]["derived"]
        self.assertEqual((derived["schema"], derived["app"]), ("<code>/schema", "<code>/app"))
        moved = bc.resolve_paths(root=fixtures.temp_dir(self))
        self.assertEqual((moved.schema, moved.app), (BRUSHES / "schema", BRUSHES / "app"))
        self.assertNotEqual(moved.root, BRUSHES)
        section = self.section("F2.")
        self.assertIn("| `schema` | none | none | `TOOL_ROOT/schema`, always |", section)
        self.assertIn("| `app` | none | none | `TOOL_ROOT/app`, always |", section)
        self.assertNotIn("`<root>/schema`", self.contracts)
        self.assertNotIn("`<root>/app`", self.contracts)
        self.assertIn("TOOL_ROOT/schema/silica_keys.json", self.section("F3."))

    def test_the_port(self):
        app = self.spec["surfaces"]["app"]
        self.assertEqual(app["port"], bc.APP_PORT)
        self.assertEqual(app["origin"], f"http://localhost:{bc.APP_PORT}")
        self.assertEqual(app["bind"], "127.0.0.1")
        self.assertIn(f"127.0.0.1:{bc.APP_PORT}", self.contracts)
        self.assertIn(f"APP_PORT = {bc.APP_PORT}", self.contracts)

    def test_the_document_names_them_too(self):
        for name in bc.ENV_NAMES.values():
            self.assertIn(f"`{name}`", self.contracts)
        for flag in bc.FLAGS.values():
            self.assertIn(f"`{flag}`", self.contracts)
        self.assertIn("EXIT_OK, EXIT_REFUSED, EXIT_USAGE = 0, 1, 2", self.contracts)
        self.assertIn(", ".join(bc.Paths._fields), self.contracts)


class Identity(Loaded):
    def test_the_patterns(self):
        declared = self.spec["identity"]
        self.assertEqual(declared["brush_id"], identity.BRUSH_ID_PATTERN)
        self.assertEqual(declared["texture_id"], identity.TEXTURE_ID_PATTERN)
        self.assertEqual(declared["set_id"], identity.SET_ID_PATTERN)
        self.assertEqual(declared["set_slug"], identity.SET_SLUG_PATTERN)
        self.assertEqual(declared["content_sha256"], identity.SHA256_PATTERN)
        self.assertEqual(declared["hex_chars"], identity.ID_HEX)
        self.assertEqual(declared["module"], "pipeline/identity.py")
        for key in ("brush_id", "texture_id", "set_id", "set_slug"):
            self.assertIn(declared[key], self.contracts, key)

    def test_the_domains(self):
        declared = self.spec["identity"]["domains"]
        self.assertEqual(declared["brush"].encode() + b"\x00", identity.BRUSH_DOMAIN)
        self.assertEqual(declared["set"].encode() + b"\x00", identity.SET_DOMAIN)

    def test_the_golden_vectors_are_what_the_code_computes(self):
        golden = self.spec["identity"]["golden"]

        def data(value):
            return None if value is None else value.encode("ascii")

        one = golden["brush_archive_only"]
        self.assertEqual(identity.brush_id(data(one["archive"])), one["id"])
        two = golden["brush_with_textures"]
        self.assertEqual(identity.brush_id(data(two["archive"]), data(two["shape"]), data(two["grain"])),
                         two["id"])
        three = golden["brush_with_sub"]
        sub = three["sub"]
        self.assertEqual(identity.brush_id(
            data(three["archive"]), data(three["shape"]), data(three["grain"]),
            [(data(sub["archive"]), data(sub["shape"]), data(sub["grain"]))]), three["id"])
        group = golden["set"]
        self.assertEqual(group["members"], [one["id"], two["id"]])
        self.assertEqual(identity.set_id(group["name"], group["members"]), group["id"])
        self.assertTrue(group["name"].endswith(" "), "the trailing space is part of the vector")
        texture = golden["texture"]
        self.assertEqual(identity.texture_id(data(texture["bytes"])), texture["id"])
        for entry in golden.values():
            self.assertIn(f"`{entry['id']}`", self.contracts)

    def test_the_loose_rule(self):
        self.assertEqual(self.spec["identity"]["loose_set_slug"], "<pack_id>" + identity.LOOSE_SUFFIX)

    def test_a_pack_id_leaves_room_for_the_loose_suffix(self):
        declared = self.spec["identity"]
        self.assertEqual(declared["pack_id_max"], identity.PACK_ID_MAX)
        self.assertEqual(declared["pack_id_max"], 42)
        section = " ".join(self.section("F1.").split())
        self.assertIn("A pack id is a set slug of at most 42 characters", section)
        for pack in self.sources["packs"] + self.sources["official"]["packs"]:
            self.assertTrue(identity.is_pack_id(pack["id"]), pack["id"])

    def test_a_loose_pseudo_set_is_fully_specified(self):
        """Its order, its hashed name and its title feed the frozen set_id and
        the notes; none of them may be left to the builder."""
        loose = self.spec["identity"]["loose_set"]
        self.assertEqual(set(loose), {"kind", "member_order", "name", "title", "without_a_home_brush"})
        self.assertEqual(loose["kind"], "loose")
        section = " ".join(self.section("F1.").split())
        for words in ("**Loose brushes.**", "`(file name lower-cased, file name)`",
                      "the slug itself, `<pack_id>-loose`", "`<product> (loose brushes)`",
                      '`"note": null`', "It gets no note and no sidecar"):
            self.assertIn(words, section)
        self.assertIn("(file name lower-cased, file name)", loose["member_order"])
        self.assertIn("<product> (loose brushes)", loose["title"])
        self.assertIn("note null", loose["without_a_home_brush"])
        # The name a pseudo-set is hashed under is its slug: one function gives both.
        slug = identity.loose_set_slug("demo-pack")
        members = [identity.brush_id(b"A")]
        self.assertEqual(identity.set_id(slug, members), identity.set_id("demo-pack-loose", members))

    def test_every_secondary_is_hashed(self):
        section = " ".join(self.section("F1.").split())
        self.assertIn("Every `SubNN/` folder that holds a `Brush.archive` is hashed", section)
        self.assertIn("a `Sub02/` that F3 files under `extras` still enters the hash", section)
        self.assertIn("resolved inside its own folder", section)
        self.assertIn("ascending", self.spec["identity"]["subs"])
        two = identity.brush_id(b"A", None, None, [(b"S1", None, None), (b"S2", b"s", None)])
        self.assertNotEqual(two, identity.brush_id(b"A", None, None, [(b"S1", None, None)]))
        self.assertNotEqual(two, identity.brush_id(b"A", None, None, [(b"S2", b"s", None), (b"S1", None, None)]))


class Format(Loaded):
    ERAS = ["E0", "E1", "E1b", "E1c", "E2", "E3", "E4", "M172", "M173", "M220", "M242"]

    def test_the_eras(self):
        declared = self.spec["format"]
        self.assertEqual(declared["eras"], self.ERAS)
        self.assertEqual(list(declared["era_keys"]), self.ERAS)
        self.assertEqual(list(declared["era_family"]), self.ERAS)
        self.assertEqual(declared["families"], ["legacy", "modern"])
        for era in self.ERAS:
            self.assertEqual(declared["era_family"][era], "legacy" if era.startswith("E") else "modern")
            if era.startswith("M"):
                self.assertEqual(declared["era_keys"][era], int(era[1:]))
            self.assertIn(f"| `{era}` | {declared['era_keys'][era]}", self.contracts, era)

    def test_the_legacy_key_counts_are_the_fixtures(self):
        for era, count in fixtures.LEGACY_KEY_COUNTS.items():
            self.assertEqual(self.spec["format"]["era_keys"][era], count, era)
        self.assertEqual(self.spec["format"]["era_keys"][fixtures.MODERN_ERA], fixtures.MODERN_KEY_COUNT)

    def test_an_unknown_era_is_named_by_its_key_count(self):
        unknown = self.spec["format"]["unknown_era"]
        self.assertEqual(unknown["id"], "X<count>")
        self.assertIsNotNone(re.match(unknown["pattern"], "X97"))
        for era in self.ERAS:
            self.assertIsNone(re.match(unknown["pattern"], era))
        self.assertIn("`X<count>`", self.contracts)

    def test_an_era_matches_on_its_exact_key_set_only(self):
        section = " ".join(self.section("F3.").split())
        for words in ("**An era matches only on an exact root key set.**",
                      "88 keys that are not E3's 88 keys are `X88`, not `E3`",
                      "the smallest symmetric difference", "the earlier row of the table on a tie",
                      "The family of an `X<count>` archive is its nearest era's",
                      "brush_model.nearest_era(keys) -> era_id"):
            self.assertIn(words, section)
        self.assertNotIn("| legacy or modern |", self.contracts)
        self.assertIn("exact root key set only", self.spec["format"]["era_match"])
        self.assertIn("smallest symmetric difference", self.spec["format"]["era_match"])

    def test_one_rule_for_what_a_member_is(self):
        """F3 once listed `.empty` as ignored under Reading and as written back
        under Writing. One rule now, and both early readers follow it."""
        section = " ".join(self.section("F3.").split())
        self.assertNotIn("a zero-byte `.empty`, files that are not brush data", section)
        for words in ("**Junk is part of no folder.**", "**Inside a brush folder every other entry is a member.**",
                      "it raises no such warning, and it never enters identity",
                      "the first wins, with a warning", "including `.empty` members and unknown files"):
            self.assertIn(words, section)
        for name in sorted(ingest.JUNK_NAMES):
            self.assertIn(name, section.lower())
        for reader in (ingest, device_tests):        # both take the one reader's rules
            self.assertEqual(reader.JUNK_NAMES, container.JUNK_NAMES, reader.__name__)
            self.assertEqual(reader.JUNK_FOLDERS, container.JUNK_FOLDERS, reader.__name__)
            self.assertEqual(reader.EMPTY, container.EMPTY, reader.__name__)
        self.assertEqual(container.EMPTY, ".empty")
        self.assertNotIn(".empty", ingest.JUNK_NAMES | device_tests.JUNK_NAMES)

    def test_the_one_zip_writer_is_named_with_what_it_writes(self):
        import zip_writer
        section = " ".join(self.section("F3.").split())
        self.assertIn("`zip_writer.write_zip(entries, *, date_time=DEFAULT_DATE_TIME) -> bytes`", section)
        self.assertIn("write no zip of their own", section)
        self.assertIn(f"**zlib level {zip_writer.DEFLATE_LEVEL}**", section)
        self.assertIn("internal attribute bit 0 set to 1 when the entry's data is text", section)
        self.assertIn(f"flag bits `0x{zip_writer.FLAG_BITS:04x}`", section)
        self.assertIn(f"`extract_version` {zip_writer.EXTRACT_VERSION}", section)
        # The three forms read off the library: code, spec and document agree.
        declared = self.spec["format"]["zip_forms"]
        self.assertEqual(list(declared), list(zip_writer.FORMS))
        for name, (method, flags, level) in zip_writer.FORMS.items():
            self.assertEqual(declared[name], {"method": method, "flag_bits": flags, "level": level}, name)
            row = re.search(rf"\| `{name}` \| ([^|]*) \| ([^|]*) \| ([^|]*) \|", section)
            self.assertIsNotNone(row, f"the forms table has a row for {name}")
            self.assertEqual((row.group(1), row.group(2)), (str(method), f"`0x{flags:04x}`"), name)
            if level is not None:
                self.assertIn(f"zlib level {level}", row.group(3), name)
        self.assertEqual(self.spec["format"]["zip_default_form"], zip_writer.DEFAULT_FORM)
        self.assertEqual(tuple(self.spec["format"]["zip_zero_date"]), zip_writer.ZERO_DATE)
        self.assertIn("`zip_writer.ZERO_DATE`", section)
        self.assertIn("form_of(method, flag_bits)", section)
        self.assertIn("pipeline/zip_writer.py", self.spec["cli"]["library_modules"])
        self.assertTrue(zip_writer.is_text(b"<plist>\n") and not zip_writer.is_text(b"\x00PNG"))

    def test_profiles_and_the_new_brush_era(self):
        declared = self.spec["format"]
        self.assertEqual(declared["profiles"], ["ios_legacy", "ios_modern"])
        self.assertEqual(declared["new_brush_era"], "M220")
        self.assertEqual(declared["new_brush_eras"], ["M220", "E4"])
        for word in ("`ios_legacy`", "`ios_modern`", 'era="M220"'):
            self.assertIn(word, self.contracts)

    def test_the_caps(self):
        caps = self.spec["format"]["caps"]
        mib = 1024 * 1024
        self.assertEqual(caps, {
            "zip_entries": 5000, "archive_bytes": mib, "entry_bytes": 64 * mib,
            "total_bytes": 2048 * mib, "ratio": 200, "ratio_min_bytes": 16 * mib,
            "nesting_depth": 3, "upload_bytes": 512 * mib, "plist_objects": 100000,
            "plist_depth": 64, "png_pixels": 8192 * 8192})

    def test_the_device_test_block_claims_nothing(self):
        device = self.spec["device_test"]
        self.assertEqual(list(device["results"]), ["container", "edit_legacy", "edit_modern",
                                                   "scratch_m220", "scratch_e4", "thumbnail_policy"])
        self.assertEqual(set(device["results"].values()), {"untested"})
        self.assertEqual(device["values"], ["untested", "passed", "failed"])
        self.assertEqual(set(device["wording"]), set(device["values"]))
        self.assertIsNone(device["procreate_version"])
        self.assertIsNone(device["date"])
        for paths in device["files"].values():
            self.assertTrue(set(paths) <= set(device["results"]))
        self.assertEqual({p for paths in device["files"].values() for p in paths}, set(device["results"]))
        section = self.section("Device tests")
        for path in device["results"]:
            self.assertIn(f"`{path}`", section)
        self.assertIn(device["wording"]["untested"], section)
        self.assertIn("`untested`", read(BRUSHES / "README.md"))


class TagsFacetsPreviews(Loaded):
    def test_six_axes_and_their_caps(self):
        tags = self.spec["tags"]
        self.assertEqual(tags["axes"], ["medium", "mark", "texture", "edge", "motif", "use"])
        self.assertEqual(tags["caps"], {"medium": 2, "mark": 2, "texture": 3, "edge": 2, "motif": 2, "use": 3})
        self.assertEqual(tags["stored_keys"], [f"{axis}_tags" for axis in tags["axes"]])
        self.assertIs(tags["closed"], True)
        self.assertEqual(tags["visual_basis"], "described-not-measured")
        section = self.section("F8.")
        self.assertIn("medium 2, mark 2, texture 3, edge 2, motif 2, use 3", section)
        for key in tags["stored_keys"]:
            self.assertIn(f"{key}:", section)
        self.assertIn(tags["visual_basis"], section)

    def test_the_facet_names(self):
        facets = self.spec["facets"]
        self.assertIsInstance(facets, list)
        self.assertEqual(len(facets), len(set(facets)))
        for name in facets:
            self.assertRegex(name, r"^[a-z][a-z0-9_]*$")
        for needed in ("stroke_source", "shape_source", "grain_source", "family", "era"):
            self.assertIn(needed, facets)
        self.assertNotIn("approximate", facets)
        self.assertNotIn("approx", facets)
        section = self.section("F5.")
        for name in facets:
            self.assertIn(f"`{name}`", section, name)
        self.assertEqual(self.spec["facet_owner"], {"code": "pipeline/ingest.py", "rules": "schema/facets.json"})

    def test_the_preview_words(self):
        words = self.spec["preview_sources"]
        self.assertEqual(words["stroke_source"], ["thumbnail", "reset-thumbnail", "none", "rendered-approx"])
        self.assertEqual(words["shape_source"], ["embedded", "bundled", "bundled-supplied", "none"])
        self.assertEqual(set(words["grain_source"]), set(words["shape_source"]) | {"blank"})
        self.assertEqual(self.spec["previews"]["kinds"], ["stroke", "shape", "grain"])
        for word in words["stroke_source"] + words["grain_source"]:
            self.assertIn(f"`{word}`", self.contracts, word)

    def test_the_preview_limits(self):
        self.assertEqual(self.spec["previews"]["preview_kb"], 128)
        self.assertEqual(self.spec["previews"]["previews_total_mb"], 50)
        limits = self.spec["commit_policy"]["limits"]
        self.assertEqual((limits["preview_kb"], limits["previews_total_mb"], limits["plain_blob_mb"]),
                         (128, 50, 95))
        section = self.section("F6.")
        self.assertIn("128 KB per tracked file, 50 MB", section)
        self.assertEqual(self.spec["previews"]["stroke"]["size"], [530, 162])
        self.assertEqual(self.spec["previews"]["shape"]["size"], [256, 256])
        self.assertEqual(self.spec["previews"]["sheet"]["size"], [802, 1496])
        for size in ("530x162", "256x256", "802x1496"):
            self.assertIn(size, section)

    def test_similar_weights_are_a_declared_placeholder(self):
        similar = self.spec["similar"]
        self.assertEqual(similar["status"], "placeholder")
        self.assertEqual(similar["weights"], {"default": 1, "shape_ref": 4, "grain_ref": 3})


class Surfaces(Loaded):
    def test_every_mcp_tool_is_in_the_document(self):
        mcp = self.spec["surfaces"]["mcp"]
        self.assertEqual(mcp["tools"], [
            "library_status", "search_brushes", "get_brush", "similar_brushes", "list_sets",
            "list_vocabulary", "get_preview", "get_brush_settings_schema", "validate_settings_patch"])
        self.assertEqual(mcp["gated_tools"], {"export_brush": "--export-dir"})
        section = self.section("F10.")
        for tool in list(mcp["tools"]) + list(mcp["gated_tools"]):
            self.assertIn(f"`{tool}`", section, tool)
        table = section.split("\nTools (", 1)[1].split("\n\n", 2)[1]      # the table that follows, and no later one
        rows = re.findall(r"^\| `([a-z_]+)` \|", table, re.M)
        self.assertEqual(rows, mcp["tools"], "the tool table lists the same tools in the same order")
        self.assertIn(mcp["gated_tools"]["export_brush"], section)
        self.assertEqual(mcp["script"], "pipeline/mcp_server.py")

    def test_the_status_payload(self):
        status = self.spec["surfaces"]["mcp"]["status"]
        self.assertEqual(tuple(status["modes"]), mcp_server.MODES)
        self.assertEqual(tuple(status["index_states"]), mcp_server.INDEX_STATES)
        self.assertEqual(status["stub_key"], "stub")
        context = mcp_server.make_context(bc.resolve_paths(root=fixtures.temp_dir(self) / "brushes"))
        payload = mcp_server.library_status({}, context)
        self.assertEqual(list(payload), status["keys"] + [status["stub_key"]])
        self.assertIn(payload["index"]["state"], status["index_states"])
        self.assertIn(payload["mode"], status["modes"])
        section = self.section("F10.")
        fields = section.split("**The `library_status` payload**", 1)[1].split("\n\n", 2)[1]
        listed = [name for row in re.findall(r"^\| ([^|]+) \|", fields, re.M)
                  for name in re.findall(r"`([a-z_]+)`", row)]
        self.assertEqual(listed, status["keys"], "the field table names every key, in order")
        self.assertIn("Never a count of files", section)

    def test_the_base_of_a_patch_is_defined(self):
        section = " ".join(self.section("F10.").split())
        self.assertIn("**The base of a patch.**", section)
        self.assertIn('`{"members": [{"path", "b64"}]}`, the same form as the export request\'s base', section)
        self.assertIn("`base_id` and `base` together are `bad_argument`", section)
        self.assertIn("never a `to_json` model", section)

    def test_the_registration(self):
        mcp = self.spec["surfaces"]["mcp"]
        self.assertEqual(mcp["registration"], {"command": "python", "args": ["-I", "brushes/pipeline/mcp_server.py"]})
        self.assertEqual(mcp["declared_in"], ["repo:.mcp.json"] + (
            ["repo:.claude-plugin/plugin.json"] if mcp["plugin_entry"]["state"] == "present" else []))
        if (REPO / ".mcp.json").is_file():
            declared = json.loads(read(REPO / ".mcp.json"))["mcpServers"][mcp["server"]]
            self.assertEqual(declared, mcp["registration"])
        self.assertIn("passes -I", self.spec["runtime"]["isolation"])
        self.assertIn("their registrations pass `-I`", " ".join(self.section("0.").split()))

    def test_every_route_is_in_the_document(self):
        routes = self.spec["surfaces"]["app"]["routes"]
        self.assertEqual(len(routes), 16)
        self.assertEqual(len(set(routes)), 16)
        section = self.section("F10.")
        for route in routes:
            self.assertRegex(route, r"^(GET|POST) /api/[a-z<>_./-]+$")
            self.assertIn(f"| `{route}` |", section, route)
        listed = re.findall(r"^\| `((?:GET|POST) /api/[^`]+)` \|", section, re.M)
        self.assertEqual(listed, routes, "the route table lists the same routes in the same order")

    def test_static_files_tabs_and_formats(self):
        app = self.spec["surfaces"]["app"]
        section = self.section("F10.")
        self.assertEqual(len(app["static"]["schema"]), 4)
        for path in app["static"]["schema"]:
            self.assertIn(path, section)
        tabs = app["tabs"]
        self.assertEqual(tabs, ["ai", "stroke", "stabilization", "taper", "shape", "grain", "dynamics",
                                "pencil", "wetmix", "color", "rendering", "properties", "materials", "about"])
        self.assertEqual(len(tabs), 14)
        flat = " ".join(section.split())
        self.assertIn(", ".join(tabs), flat)
        self.assertEqual(app["export_formats"], ["brush", "brushset", "gbr", "kit"])
        self.assertIn('"brush" | "brushset" | "gbr" | "kit"', section)
        self.assertEqual(app["token"]["header"], "X-ROSW-Token")
        self.assertIn("X-ROSW-Token", section)
        self.assertIn(app["patch_schema"], self.contracts)


class CommandLines(Loaded):
    def rows(self):
        section = self.section("F11.")
        found = {}
        for line in section.splitlines():
            match = re.match(r"^\| `([a-z_/]+\.py)` \| (.*) \|$", line)
            if match:
                found[match.group(1)] = match.group(2)
        return found

    def test_the_command_is_python(self):
        self.assertEqual(self.spec["cli"]["command"], "python")
        self.assertEqual(self.spec["runtime"]["command"], "python")
        self.assertNotIn("python3", self.contracts.replace("never `python3`", ""))

    def test_every_script_and_verb_is_in_the_document(self):
        scripts = self.spec["cli"]["scripts"]
        rows = self.rows()
        self.assertEqual(list(rows), list(scripts), "the table lists the same scripts in the same order")
        for script, declared in scripts.items():
            self.assertIn(f"`{script}`", self.contracts)
            row = rows[script]
            verbs = re.findall(r"`([a-z]+)[ `]", row)
            self.assertEqual(verbs, declared["verbs"], script)
            self.assertTrue(set(declared["confirm"]) <= set(declared["verbs"]), script)
            for verb, flags in declared.get("flags", {}).items():
                self.assertTrue(verb == "" or verb in declared["verbs"], (script, verb))
                for flag in flags:
                    self.assertIn(flag, row, (script, flag))

    def test_a_confirm_verb_is_shown_with_its_flag(self):
        rows = self.rows()
        for script, declared in self.spec["cli"]["scripts"].items():
            for verb in declared["confirm"]:
                self.assertIn("--confirm", declared["flags"][verb], (script, verb))
                shown = re.search(rf"`{verb}\b[^`]*`", rows[script])
                self.assertIsNotNone(shown, (script, verb))
                self.assertIn("--confirm", shown.group(0), (script, verb))

    def test_which_verbs_are_writers(self):
        confirm = {script: declared["confirm"] for script, declared in self.spec["cli"]["scripts"].items()}
        self.assertEqual(confirm["pipeline/fetch_base_library.py"], ["fetch"])
        self.assertEqual(confirm["pipeline/ingest.py"], ["adopt"])
        self.assertEqual(confirm["pipeline/previews.py"], ["render"])
        self.assertEqual(confirm["pipeline/notes.py"], ["write"])
        self.assertEqual(confirm["pipeline/brush_file.py"], ["export"])
        self.assertEqual(confirm["vault/tools/brush_tags.py"], ["apply"])
        self.assertEqual(confirm["vault/tools/brush_search.py"], [])
        self.assertIn("DRY RUN   nothing is written without --confirm.", self.contracts)

    def test_library_modules_have_no_command_line(self):
        modules = self.spec["cli"]["library_modules"]
        self.assertEqual(set(modules) & set(self.spec["cli"]["scripts"]), set())
        for module in ("pipeline/identity.py", "pipeline/brush_common.py"):
            self.assertIn(module, modules)
            tree = ast.parse(read(BRUSHES / module))
            names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
            self.assertNotIn("main", names, module)

    def test_writers(self):
        writers = self.spec["persistence"]["writers"]
        section = self.section("F12.")
        scripts = self.spec["cli"]["scripts"]
        for path, commands in writers.items():
            for command in commands:
                if not command.startswith(("pipeline/", "vault/tools/")):
                    continue
                script, verb = command.split()[:2]
                self.assertIn(verb, scripts[script]["verbs"], command)
                needs_confirm = verb in scripts[script]["confirm"]
                self.assertEqual("--confirm" in command, needs_confirm, command)
                shown = command.split("/")[-1]
                self.assertIn(f"`{shown}`", section, command)
        self.assertEqual(set(self.spec["persistence"]["no_confirm"]),
                         {"pipeline/ingest.py build", "vault/tools/brush_search.py index"})
        self.assertEqual(writers[f"repo:brushes/{device_tests.OUT_HOME}/**"],
                         ["pipeline/device_tests.py build --confirm"])
        self.assertIn("`library/official/fetch_log.jsonl`", section)
        self.assertIn("library/official/** and library/official/fetch_log.jsonl", writers)
        for authored in ("spec.yaml", "library/sources.json", "vault/CLAUDE.md",
                         "vault/_BrushTags/vocabulary.yaml"):
            self.assertIn(authored, self.spec["persistence"]["authored"])
            self.assertIn(f"`{authored}`", section)

    def test_every_writer_of_a_script_is_declared(self):
        """F12 lists every writer. A script that takes --confirm and has no row
        under `persistence.writers` writes somewhere nobody declared."""
        commands = [command for listed in self.spec["persistence"]["writers"].values() for command in listed]
        for script, declared in self.spec["cli"]["scripts"].items():
            for verb in declared["confirm"]:
                # `brush_file.py export` writes through service.write_export, and its row says so.
                named = f"{script.rsplit('/', 1)[-1]} {verb} --confirm"
                self.assertTrue(any(named in command for command in commands),
                                f"`{script} {verb}` takes --confirm and no writer row names it")

    def test_every_pipeline_module_on_disk_is_declared(self):
        """Disk against spec: a file under pipeline/ is a script of F11 or a
        library module. Two were once neither, and nothing noticed."""
        scripts = set(self.spec["cli"]["scripts"])
        modules = set(self.spec["cli"]["library_modules"])
        on_disk = sorted(f"pipeline/{path.name}" for path in PIPELINE.glob("*.py"))
        self.assertGreaterEqual(len(on_disk), 7)
        for relative in on_disk:
            self.assertTrue(relative in scripts or relative in modules,
                            f"{relative} is in neither cli.scripts nor cli.library_modules")
            names = {node.name for node in ast.parse(read(BRUSHES / relative)).body
                     if isinstance(node, ast.FunctionDef)}
            self.assertEqual("main" in names, relative in scripts,
                             f"{relative}: a script has a main(), a library module has none")
        for relative in sorted(f"vault/tools/{path.name}" for path in (BRUSHES / "vault" / "tools").glob("*.py")):
            self.assertIn(relative, scripts)
        rows = self.rows()
        for relative in on_disk:
            if relative in scripts:
                self.assertIn(relative, rows, "a script on disk has a row in the F11 table")

    def test_the_fields_previews_changes_and_who_reads_them(self):
        """Four Phase 2 owners (ingest, previews, notes, search) meet at these
        three fields. One function writes them; everyone reads the brush record."""
        declared = self.spec["persistence"]["preview_fields"]
        self.assertEqual(declared["fields"], ["facets", "facet_words", "preview"])
        self.assertEqual(declared["record"], "catalog/brushes/<brush_id>.json")
        self.assertEqual(declared["applied_by"], "ingest.apply_preview_results")
        self.assertEqual(declared["called_by"], ["pipeline/ingest.py build", "pipeline/previews.py render --confirm"])
        self.assertEqual(declared["inputs"], ["catalog/thumbnails.json", "catalog/textures.json"])
        self.assertTrue(set(declared["measured_facets"]) <= set(self.spec["facets"]))
        self.assertEqual(declared["measured_facets"][2:], self.spec["facets"][-6:],
                         "the six texture facets, as the facet list ends")
        f5 = " ".join(self.section("F5.").split())
        for words in ("**Preview-derived fields.**", "**One function writes them:** `ingest.apply_preview_results(paths)`",
                      "It changes no other field", "`previews.py` writes no brush record itself",
                      "**Before previews has run for a brush**", "**Everyone reads the brush record.**",
                      "are copies made by `assemble_index`"):
            self.assertIn(words, f5)
        for name in declared["measured_facets"]:
            self.assertIn(f"`{name}`", f5)
        f12 = " ".join(self.section("F12.").split())
        self.assertIn("exactly three fields of each `brushes/<brush_id>.json` (`facets`, `facet_words`, `preview`)", f12)
        f9 = " ".join(self.section("F9.").split())
        self.assertIn("`facets`, `facet_words`, `preview` and `content_sha256` from "
                      "`catalog/brushes/<brush_id>.json`", f9)
        self.assertIn("reads none from `catalog.json`", f9)

    def test_the_run_order(self):
        order = self.spec["persistence"]["run_order"]
        self.assertEqual([step.split()[0].rsplit("/", 1)[-1] + " " + step.split()[1] for step in order],
                         ["fetch_base_library.py fetch", "ingest.py adopt", "ingest.py build",
                          "previews.py render", "notes.py write", "brush_search.py index"])
        scripts = self.spec["cli"]["scripts"]
        for step in order:
            script, verb = step.split()[:2]
            self.assertIn(verb, scripts[script]["verbs"], step)
            self.assertEqual("--confirm" in step, verb in scripts[script]["confirm"], step)
        block = self.section("F5.").split("**The run order.**", 1)[1].split("```", 2)[1]
        listed = [" ".join(line.split()[:2]) for line in block.strip().splitlines()]
        self.assertEqual(listed, ["fetch_base_library.py fetch", "ingest.py adopt", "ingest.py build",
                                  "previews.py render", "notes.py write", "brush_search.py index"])

    def test_how_the_schema_file_is_made(self):
        self.assertIn("schema/*.json", self.spec["persistence"]["authored"])
        self.assertIn("No script writes under schema/", self.spec["persistence"]["schema_files"])
        f4 = " ".join(self.section("F4.").split())
        self.assertIn("**How the file is made.** It is authored: no script writes under `schema/`", f4)
        self.assertIn("`python -I brushes/pipeline/ingest.py census --json`", f4)
        self.assertIn("it needs a row in F11 and in F12", f4)
        self.assertIn("`schema/*.json` has no writer", " ".join(self.section("F12.").split()))
        self.assertFalse([path for path in self.spec["persistence"]["writers"] if "schema" in path])

    def test_which_folder_a_note_goes_to(self):
        rule = self.spec["layout"]["note_folder_rule"]
        self.assertEqual([row["folder"] for row in rule],
                         ["01_Procreate_Defaults", "04_My_Brushes", "03_Loose", "02_Vendor_Packs"])
        self.assertEqual(sorted(row["folder"] for row in rule), self.spec["layout"]["note_folders"])
        f7 = self.section("F7.")
        table = f7.split("**Which folder.**", 1)[1]
        self.assertEqual(re.findall(r"\| `(\d\d_[A-Za-z_]+)` \|", table)[:4], [row["folder"] for row in rule])
        flat = " ".join(f7.split())
        self.assertIn("One note per brushset that is the home of at least one brush", flat)
        self.assertIn("gets no note, no sidecar", flat)
        f5 = " ".join(self.section("F5.").split())
        self.assertIn("`counts.notes` counts the rows whose `note` is not `null`", f5)
        self.assertIn('"sets": 0, "notes": 0,', f5)


class TheLibraryManifest(Loaded):
    def test_schema_and_counts(self):
        declared = self.spec["library"]
        self.assertEqual(self.sources["schema"], declared["sources_schema"])
        self.assertEqual(len(self.sources["packs"]), declared["user_packs"])
        self.assertEqual(declared["user_packs"], 19)
        files = self.sources["official"]["files"]
        self.assertEqual(len(files), declared["official_sets"])
        self.assertEqual(declared["official_sets"], 40)
        self.assertEqual(sum(entry["bytes"] for entry in files), declared["official_bytes"])
        self.assertEqual(declared["official_bytes"], 174197966)
        section = self.section("The library manifest")
        self.assertIn("19 user packs and 40 official files (174,197,966 bytes)", section)

    def test_every_user_pack(self):
        fields = {"id", "kind", "vendor", "product", "source_url", "licence_note", "redistribute",
                  "publish_previews", "evidence", "match", "sets"}
        ids = [pack["id"] for pack in self.sources["packs"]]
        self.assertEqual(len(set(ids)), len(ids))
        for pack in self.sources["packs"]:
            self.assertEqual(set(pack), fields, pack["id"])
            self.assertTrue(identity.is_set_slug(pack["id"]), pack["id"])
            self.assertTrue(identity.is_set_slug(identity.loose_set_slug(pack["id"])))
            self.assertIn(pack["kind"], ("vendor", "mine"))
            self.assertIn(pack["redistribute"], self.spec["library"]["redistribute"])
            self.assertTrue(pack["vendor"] is None or pack["vendor"].strip(), pack["id"])
            self.assertTrue(pack["evidence"].strip(), pack["id"])
            self.assertTrue(pack["licence_note"].strip(), pack["id"])
            self.assertIsInstance(pack["publish_previews"], bool)
            self.assertTrue(pack["match"], pack["id"])
            for pattern in pack["match"]:
                self.assertFalse(pattern.startswith("/") or "\\" in pattern or ":" in pattern, pattern)
            for name, entry in pack["sets"].items():
                self.assertEqual(set(entry), {"slug", "title"}, name)
                self.assertTrue(identity.is_set_slug(entry["slug"]), entry["slug"])
                self.assertTrue(entry["title"].strip())
                self.assertNotIn('"', entry["title"])

    def test_set_slugs_are_unique_across_the_whole_library(self):
        slugs = [entry["slug"] for pack in self.sources["packs"] for entry in pack["sets"].values()]
        slugs += [identity.loose_set_slug(pack["id"]) for pack in self.sources["packs"]]
        slugs += [entry["slug"] for entry in self.sources["official"]["files"]]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertEqual(len([s for pack in self.sources["packs"] for s in pack["sets"]]), 21)

    def test_each_user_set_slug_is_what_slugify_makes_of_its_name(self):
        """So the manifest and a bare `slugify(name)` cannot disagree by accident."""
        for pack in self.sources["packs"]:
            for name, entry in pack["sets"].items():
                self.assertEqual(identity.slugify(name), entry["slug"], name)

    def test_every_official_file(self):
        official = self.sources["official"]
        self.assertEqual(official["host"], "download-assets.procreate.art")
        self.assertEqual(self.spec["runtime"]["network"]["hosts"], [official["host"]])
        self.assertTrue(official["base"].startswith(f"https://{official['host']}/"))
        self.assertTrue(official["base"].endswith("/"))
        self.assertEqual(list(fetch_base_library.ALLOWED_HOSTS), self.spec["runtime"]["network"]["hosts"],
                         "the script's own allow-list, not whatever a manifest names")
        self.assertIn("`ALLOWED_HOSTS`", self.section("0."))
        self.assertIn("continues with the other files and ends with exit 1", " ".join(self.section("F11.").split()))
        self.assertNotIn("stops with exit 1", " ".join(self.section("F11.").split()))
        packs = {pack["id"]: pack for pack in official["packs"]}
        self.assertEqual(len(packs), 8)
        for pack in packs.values():
            self.assertEqual(pack["kind"], "official")
            self.assertIn(pack["redistribute"], self.spec["library"]["redistribute"])
        targets = set()
        for entry in official["files"]:
            self.assertEqual(set(entry), {"pack", "slug", "title", "path", "bytes", "md5"})
            self.assertIn(entry["pack"], packs)
            self.assertTrue(identity.is_set_slug(entry["slug"]))
            self.assertRegex(entry["md5"], r"^[0-9a-f]{32}$")
            self.assertIs(type(entry["bytes"]), int)
            self.assertGreater(entry["bytes"], 0)
            self.assertLess(entry["bytes"], 200 * 1000 * 1000)
            self.assertTrue(entry["path"].isascii() and entry["path"].endswith(".brushset"))
            self.assertFalse(entry["path"].startswith("/") or ".." in entry["path"] or " " in entry["path"])
            self.assertTrue(entry["title"].strip())
            targets.add(f"official/{entry['pack']}/{entry['slug']}.brushset")
        self.assertEqual(len(targets), 40, "every file has its own place in the library")
        self.assertEqual(len({entry["md5"] for entry in official["files"]}), 40)
        self.assertEqual(set(packs), {entry["pack"] for entry in official["files"]})
        count = {pack: sum(1 for e in official["files"] if e["pack"] == pack) for pack in packs}
        self.assertEqual((count["procreate-5"], count["procreate-2"]), (18, 16))
        self.assertEqual(sum(count.values()) - 34, 6)

    def test_the_manifest_is_plain_lf_json_with_real_characters(self):
        raw = SOURCES_PATH.read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"}\n"))
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertIn("\U0001f4a7Everything Watercolour".encode("utf-8"), raw)
        self.assertIn("Autumn Stamps ", self.sources["packs"][0]["sets"])

    def test_the_fixture_manifest_has_the_same_shape(self):
        synthetic = fixtures.standard_sources()
        self.assertEqual(synthetic["schema"], self.sources["schema"])
        self.assertEqual(set(synthetic["packs"][0]), set(self.sources["packs"][0]))
        self.assertEqual(set(synthetic["official"]) - {"files"}, set(self.sources["official"]) - {"files"})
        self.assertEqual(set(synthetic["official"]["packs"][0]), set(self.sources["official"]["packs"][0]))


class RepositoryFiles(Loaded):
    """What the commit policy says, read from the files themselves. The checks
    that need git are in test_repo_policy.py. Skipped for a copy of brushes/
    taken out of its repository, where the root files are not there to read."""

    @classmethod
    def setUpClass(cls):
        missing = [name for name in (".gitattributes", ".gitignore", "INDEX.md")
                   if not (REPO / name).is_file()]
        if missing:
            raise unittest.SkipTest(f"brushes/ is not inside its repository: no {', '.join(missing)}")
        super().setUpClass()

    def test_the_attribute_lines_and_their_order(self):
        policy = self.spec["commit_policy"]
        lines = [line.strip() for line in read(REPO / ".gitattributes").splitlines()
                 if line.strip() and not line.startswith("#")]
        wanted = ([policy["text"], policy["as_received"]]
                  + [f"{pattern} binary" for pattern in policy["binary"]]
                  + [f"{pattern} {policy['lfs']['attributes']}" for pattern in policy["lfs"]["patterns"]])
        self.assertEqual(wanted, [
            "brushes/** text=auto eol=lf",
            "brushes/app/** -text",
            "brushes/**/*.png binary",
            "brushes/**/*.archive binary",
            "brushes/library/**/*.brushset filter=lfs diff=lfs merge=lfs -text",
            "brushes/library/**/*.brush filter=lfs diff=lfs merge=lfs -text",
            "brushes/device-tests/**/returned/**/*.brushset filter=lfs diff=lfs merge=lfs -text",
            "brushes/device-tests/**/returned/**/*.brush filter=lfs diff=lfs merge=lfs -text"])
        brush_lines = [line for line in lines if line.startswith("brushes/")]
        self.assertEqual(brush_lines, wanted)
        self.assertEqual(lines.count("plugins/ui-design/** text eol=lf"), 1, "the plugin's rule is untouched")
        self.assertNotIn("brushes/** text eol=lf", lines)
        for line in wanted:
            self.assertIn(line.split()[0], self.section("F12."))

    def test_the_root_ignore_file(self):
        root = read(REPO / ".gitignore")
        rules = [line.strip() for line in root.splitlines()
                 if line.strip().lstrip("!").startswith("brushes/")]
        kept = self.spec["device_test"]["kept"]
        self.assertEqual(kept, ["manifest.json", "CHECKLIST.md", "returned/"])
        self.assertEqual(rules, ["brushes/device-tests/*/*"] + [f"!brushes/device-tests/*/{name}" for name in kept],
                         "a sitting's built files are ignored; its record is kept")
        self.assertNotIn("\nbrushes/device-tests/\n", root, "the folder is no longer ignored whole")
        self.assertIn("repo:brushes/device-tests/*/*", self.spec["commit_policy"]["never_tracked"])
        self.assertEqual((device_tests.MANIFEST_NAME, device_tests.CHECKLIST_NAME, device_tests.RETURNED_DIR + "/"),
                         tuple(kept))
        self.assertIn("brushes/", root.split("\n# ──", 1)[0], "the header names the tool")
        self.assertNotIn("\nbrushes/library", root, "the originals are not ignored")
        self.assertIn("\n*.zip\n", root)
        section = " ".join(self.section("Device tests").split())
        self.assertIn("`manifest.json`, `CHECKLIST.md` and `returned/` are committed", section)
        self.assertIn("`known-bad/KNOWN-BAD_old-designer.brush`", section)
        self.assertEqual(f"{device_tests.KNOWN_BAD_DIR}/{device_tests.KNOWN_BAD_STEM}.brush",
                         "known-bad/KNOWN-BAD_old-designer.brush")

    def test_git_lfs_has_to_be_installed_before_a_push(self):
        """The filter lines of a machine's git config store pointers; only the
        pre-push hook of `git lfs install` uploads the files. Every document a
        person follows to commit brush files says so."""
        self.assertIn("git lfs install", self.spec["commit_policy"]["lfs"]["setup"])
        for path in (BRUSHES / "README.md", BRUSHES / "library" / "README.md", CONTRACTS_PATH):
            self.assertIn("git lfs install", read(path), path.name)
        self.assertIn("pre-push", " ".join(self.section("F12.").split()))

    def test_the_root_index_lists_the_tool(self):
        self.assertIn("| `brushes/` |", read(REPO / "INDEX.md"))


class IgnoreFilesInsideTheTool(Loaded):
    def test_the_library_ignores_exactly_three_things(self):
        rules = [line.strip() for line in read(BRUSHES / "library" / ".gitignore").splitlines()
                 if line.strip() and not line.startswith("#")]
        self.assertEqual(rules, ["_docs/", "bundled/", "*.part"])
        # Where each rule bites. `_docs/` is written by `adopt --with-docs`
        # inside a pack's own folder, never at the top of library/.
        declared = {"_docs/": f"library/{ingest.USER_DIR}/<pack_id>/{ingest.DOCS_DIR}/",
                    "bundled/": "library/bundled/", "*.part": "*.part"}
        for rule in rules:
            self.assertIn(declared[rule], self.spec["commit_policy"]["never_tracked"])
        self.assertNotIn("library/_docs/", self.spec["commit_policy"]["never_tracked"])
        self.assertNotIn("`library/_docs/`", self.contracts)
        self.assertIn("`library/user/<pack_id>/_docs/`", self.section("F12."))
        self.assertIn("skips every `_docs/` folder", " ".join(self.section("F11.").split()))
        self.assertIn("official/fetch_log.jsonl", read(BRUSHES / "library" / "README.md"))
        self.assertNotIn("exists yet", read(BRUSHES / "library" / "README.md"))

    def test_the_vault_ignores_what_is_rebuilt(self):
        vault = [line.strip() for line in read(BRUSHES / "vault" / ".gitignore").splitlines()]
        for rule in ("tools/rag_index/", "_Previews/_sheets/", "_Previews/_local/"):
            self.assertIn(rule, vault)
            self.assertIn(f"vault/{rule}", self.spec["commit_policy"]["never_tracked"])
        self.assertNotIn("_Previews/", vault, "the previews themselves are committed")

    def test_the_originals_are_committed_and_nothing_gates_them(self):
        policy = self.spec["commit_policy"]
        self.assertIn("Git LFS", policy["originals"])
        self.assertNotIn("switch", policy)
        self.assertEqual(self.spec["library"]["adoption_rename"], {".brushset.zip": ".brushset"})
        section = self.section("F12.")
        self.assertIn("There is no switch that ignores them", " ".join(section.split()))
        self.assertIn("gates nothing", " ".join(section.split()))


# ── Python 3.10 ──────────────────────────────────────────────────────────────
# No interpreter older than the one running these tests may be at hand, so the
# rules are checked on the source: a syntax parse at the 3.10 grammar, a walk
# for the names and statements the house rules keep out, and, on 3.12 and
# later, a token scan for the f-string forms that only 3.12 accepts.

FORBIDDEN_MODULES = {"tomllib"}
FORBIDDEN_MEMBERS = {("typing", "Self"), ("typing", "override"), ("datetime", "UTC"),
                     ("enum", "StrEnum"), ("itertools", "batched"), ("hashlib", "file_digest")}
FORBIDDEN_NAMES = {"ExceptionGroup", "BaseExceptionGroup"}
STRING_PREFIX = "rRbBfFuU"


def _annotations(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = node.args
            for arg in (arguments.posonlyargs + arguments.args + arguments.kwonlyargs
                        + [a for a in (arguments.vararg, arguments.kwarg) if a]):
                if arg.annotation is not None:
                    yield arg.annotation
            if node.returns is not None:
                yield node.returns
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation


def _quote(token_text):
    text = token_text.lstrip(STRING_PREFIX)
    return text[:3] if text[:3] in ('"""', "'''") else text[:1]


def _clashes(enclosing, nested):
    return nested[:1] == enclosing[:1] and (len(enclosing) == 1 or nested == enclosing)


def new_fstring_syntax(source):
    """Uses of the f-string grammar that Python 3.12 widened: inside a
    replacement field, a quote of the enclosing kind, a backslash, a comment,
    or a line break in a one-line string. Python 3.10 rejects all four."""
    if sys.version_info < (3, 12):
        return []
    problems, stack = [], []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        line = token.start[0]
        if token.type == tokenize.FSTRING_START:
            quote = _quote(token.string)
            if stack and _clashes(stack[-1], quote):
                problems.append(f"line {line}: an f-string nested in one with the same quotes")
            stack.append(quote)
        elif token.type == tokenize.FSTRING_END:
            stack.pop()
        elif not stack:
            continue
        elif token.type == tokenize.STRING:
            if _clashes(stack[-1], _quote(token.string)):
                problems.append(f"line {line}: a string inside an f-string reuses its quotes")
            if "\\" in token.string:
                problems.append(f"line {line}: a backslash inside an f-string's braces")
        elif token.type == tokenize.FSTRING_MIDDLE and len(stack) > 1 and "\\" in token.string:
            problems.append(f"line {line}: a backslash inside an f-string's braces")
        elif token.type == tokenize.COMMENT:
            problems.append(f"line {line}: a comment inside an f-string's braces")
        elif token.type in (tokenize.NL, tokenize.NEWLINE) and len(stack[-1]) == 1:
            problems.append(f"line {line}: a line break inside a one-line f-string's braces")
    return problems


def newer_than_3_10(source, filename="<source>"):
    """Why a module breaks the Python 3.10 rules, as a list of reasons."""
    try:
        tree = ast.parse(source, filename=filename, feature_version=(3, 10))
    except SyntaxError as exc:
        return [f"line {exc.lineno}: {exc.msg}"]
    problems = []
    future = any(isinstance(node, ast.ImportFrom) and node.module == "__future__"
                 and any(alias.name == "annotations" for alias in node.names) for node in tree.body)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, getattr(ast, "Match", ())):
            problems.append(f"line {line}: a match statement")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_MODULES:
                    problems.append(f"line {line}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
            if module in FORBIDDEN_MODULES:
                problems.append(f"line {line}: from {node.module} import ...")
            for alias in node.names:
                if (module, alias.name) in FORBIDDEN_MEMBERS:
                    problems.append(f"line {line}: {module}.{alias.name}")
        elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
              and (node.value.id, node.attr) in FORBIDDEN_MEMBERS):
            problems.append(f"line {line}: {node.value.id}.{node.attr}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            problems.append(f"line {line}: {node.id}")
    if not future:
        for annotation in _annotations(tree):
            if any(isinstance(part, ast.BinOp) and isinstance(part.op, ast.BitOr)
                   for part in ast.walk(annotation)):
                problems.append(f"line {annotation.lineno}: an `X | Y` annotation without "
                                "`from __future__ import annotations`")
    return problems + new_fstring_syntax(source)


class PythonRules(unittest.TestCase):
    """Runtime code is Python 3.10 and standard library only. This reads every
    module the tool has today, and every one a later change adds."""

    RUNTIME = [BRUSHES / "pipeline", BRUSHES / "vault" / "tools"]
    OPTIONAL = {"png_io.py": {"PIL"}, "previews.py": {"PIL"}}

    def modules(self, with_tests):
        for folder in self.RUNTIME:
            if not folder.is_dir():
                continue
            for path in sorted(folder.rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                if not with_tests and "tests" in path.relative_to(folder).parts:
                    continue
                yield path

    def test_every_module_keeps_the_python_3_10_rules(self):
        seen = 0
        for path in self.modules(with_tests=True):
            self.assertEqual(newer_than_3_10(read(path), str(path)), [],
                             path.relative_to(BRUSHES).as_posix())
            seen += 1
        self.assertGreaterEqual(seen, 7)

    def test_the_checker_passes_what_3_10_runs(self):
        fine = (
            "from __future__ import annotations\nimport json\n\n"
            "def f(x: int | None, *rest: str) -> dict[str, int] | None:\n"
            "    with open('a', encoding='utf-8') as a, open('b', encoding='utf-8') as b:\n"
            "        return {f\"{x!r:>4} {json.dumps({'k': 1})}\": len(rest)}\n",
            "from typing import Optional\n\ndef f(x: Optional[int] = None) -> str:\n"
            "    return f'{x}' f\"{x}\" + f'''{\n        x\n    }'''\n",
            "x = {'a': 1}\ny = f\"\"\"{x[\"a\"]}\"\"\" + f\"a\\n{x['a']:\\t>3}\"\nz = 1 | 2\n",
        )
        for source in fine:
            compile(source, "<fine>", "exec")
            self.assertEqual(newer_than_3_10(source), [], source)

    def test_the_checker_catches_what_the_rules_keep_out(self):
        caught = {
            "a match statement": "def f(x):\n    match x:\n        case 1:\n            return 2\n",
            "tomllib": "import tomllib\n",
            "tomllib, from": "from tomllib import loads\n",
            "typing.Self": "from typing import Self\n",
            "typing.Self, as an attribute": "import typing\n\nclass A:\n    g = typing.Self\n",
            "datetime.UTC": "import datetime\nnow = datetime.datetime.now(datetime.UTC)\n",
            "datetime.UTC, from": "from datetime import UTC\n",
            "ExceptionGroup": "raise ExceptionGroup('several', [ValueError()])\n",
            "except*": "try:\n    pass\nexcept* ValueError:\n    pass\n",
            "a type statement": "type Pair = tuple[int, int]\n",
            "type parameters": "def first[T](items: list[T]) -> T:\n    return items[0]\n",
            "a union annotation evaluated at run time": "def f(x: int | None) -> None:\n    pass\n",
        }
        for what, source in caught.items():
            self.assertNotEqual(newer_than_3_10(source), [], what)

    @unittest.skipIf(sys.version_info < (3, 12), "these forms do not tokenize before Python 3.12")
    def test_the_checker_catches_the_f_strings_only_3_12_accepts(self):
        caught = {
            "the enclosing quote reused": "d = {'k': 1}\nx = f\"{d[\"k\"]}\"\n",
            "a backslash in the braces": "a = ['x']\nx = f\"{'\\n'.join(a)}\"\n",
            "an f-string nested with the same quotes": "x = 1\ny = f\"{f\"{x}\"}\"\n",
            "a comment in the braces": "x = 1\ny = f'''{\n    x  # why\n}'''\n",
            "a line break in a one-line string": "x = 1\ny = f'{\n    x\n}'\n",
        }
        for what, source in caught.items():
            compile(source, "<new>", "exec")
            self.assertNotEqual(newer_than_3_10(source), [], what)

    def test_runtime_modules_import_the_standard_library_and_their_siblings_only(self):
        for path in self.modules(with_tests=False):
            siblings = {p.stem for p in path.parent.glob("*.py")}
            allowed = set(sys.stdlib_module_names) | siblings | self.OPTIONAL.get(path.name, set())
            tree = ast.parse(read(path), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    imported.add((node.module or "").split(".")[0])
            self.assertEqual(imported - allowed, set(), path.relative_to(BRUSHES).as_posix())

    @unittest.skipIf(yaml is None, "pyyaml cannot be imported here")
    def test_the_spec_says_the_same(self):
        runtime = yaml.safe_load(read(SPEC_PATH))["runtime"]
        self.assertEqual(runtime["python"], "3.10")
        self.assertEqual(runtime["stdlib_only"]["roots"], ["pipeline", "vault/tools"])
        self.assertEqual(runtime["stdlib_only"]["except"], ["pipeline/tests"])
        self.assertEqual({Path(p).name: {"PIL"} for p in runtime["stdlib_only"]["optional"]["PIL"]},
                         self.OPTIONAL)
        self.assertEqual(runtime["network"]["script"], "pipeline/fetch_base_library.py")


if __name__ == "__main__":
    unittest.main()
