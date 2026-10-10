"""What git will do with the files under brushes/ (docs/CONTRACTS.md, F12).

The original brush files are committed through Git LFS. One of them is larger
than a plain blob may be, so a file that slipped past the LFS rule would make
the repository impossible to push. These tests ask git itself: which attributes
a path gets, which paths it ignores, and how large every tracked blob is.

Two halves:

  - the real repository: skipped where brushes/ is not at the root of a git
    repository (a copy of the folder, an unpacked archive). It reads the index
    and the attribute and ignore rules. It never reads a file from
    brushes/library/, and it changes nothing.
  - the checks themselves, run on a small repository made in a temporary
    folder with a zip, an oversized file and an original added without LFS
    planted in it, so that a check which could never fail is noticed.

Everything is skipped where git is not installed.

    python -m unittest discover -s brushes/pipeline/tests
"""

import os
import shutil
import stat
import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures  # noqa: E402

BRUSHES = PIPELINE.parent
REPO = BRUSHES.parent

PLAIN_BLOB_LIMIT = 95 * 1000 * 1000          # bytes; GitHub refuses a plain blob over 100 MB
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
POINTER_MAX = 1024                           # a pointer file is about 130 bytes
ORIGINAL_SUFFIXES = (".brushset", ".brush")
SUBMODULE = "160000"


def setUpModule():
    if shutil.which("git") is None:
        raise unittest.SkipTest("git is not installed")


# ── asking git ───────────────────────────────────────────────────────────────

def git(repo, *args, stdin=None):
    return subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=str(repo), input=stdin,
                          capture_output=True, timeout=300)


def make_writable(folder):
    """Git marks its object files read-only, and Windows will not delete those."""
    for path in Path(folder).rglob("*"):
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass


def checked(done):
    if done.returncode != 0:
        raise AssertionError(done.stderr.decode("utf-8", "replace"))
    return done.stdout


def why_not_the_real_repository():
    """A reason to skip the real-repository checks, or None."""
    try:
        top = git(REPO, "rev-parse", "--show-toplevel")
    except (OSError, subprocess.SubprocessError) as exc:
        return f"git cannot be run: {exc}"
    if top.returncode != 0:
        return "this folder is not inside a git repository"
    try:
        if Path(top.stdout.decode("utf-8", "replace").strip()).resolve() != REPO.resolve():
            return "brushes/ is not at the root of this git repository"
    except OSError as exc:
        return f"the repository root cannot be resolved: {exc}"
    return None


def attributes(repo, names, paths):
    """{path: {attribute: value}} as git resolves them. A path need not exist."""
    fields = checked(git(repo, "check-attr", "-z", *names, "--", *paths)).decode("utf-8").split("\0")
    found = {path: {} for path in paths}
    for index in range(0, len(fields) - 2, 3):
        found[fields[index]][fields[index + 1]] = fields[index + 2]
    return found


def ignored(repo, path):
    """Whether git's ignore rules cover a path, tracked or not, existing or not."""
    done = git(repo, "check-ignore", "--no-index", "-q", "--", path)
    if done.returncode not in (0, 1):
        raise AssertionError(done.stderr.decode("utf-8", "replace"))
    return done.returncode == 0


def tracked(repo, under="brushes"):
    """[(blob sha, path)] for every file in the index under a folder."""
    entries = []
    for record in checked(git(repo, "ls-files", "-s", "-z", "--", under)).decode("utf-8").split("\0"):
        if record:
            meta, path = record.split("\t", 1)
            mode, sha, _stage = meta.split()
            if mode != SUBMODULE:
                entries.append((sha, path))
    return entries


def blob_sizes(repo, entries):
    """{sha: size in bytes} from one `git cat-file --batch-check` run."""
    shas = sorted({sha for sha, _ in entries})
    if not shas:
        return {}
    listing = checked(git(repo, "cat-file", "--batch-check", stdin=("\n".join(shas) + "\n").encode("ascii")))
    sizes = {}
    for line in listing.decode("ascii").splitlines():
        sha, kind, size = line.split()
        if kind == "blob":
            sizes[sha] = int(size)
    return sizes


# ── the checks ───────────────────────────────────────────────────────────────

def zips(entries):
    return sorted(path for _, path in entries if path.lower().endswith(".zip"))


def large_blobs(entries, sizes, limit=PLAIN_BLOB_LIMIT):
    """Tracked blobs over the limit. An LFS pointer is a small blob, so a file
    that reaches this list is in git itself, whatever its attributes say."""
    return sorted(path for sha, path in entries if sizes.get(sha, 0) > limit)


def goes_through_lfs(path):
    """A brush file that must be an LFS pointer in git: an original of the
    library, or a file that came back from a device test sitting."""
    if not path.endswith(ORIGINAL_SUFFIXES):
        return False
    return path.startswith("brushes/library/") or (
        path.startswith("brushes/device-tests/") and "/returned/" in path)


def originals(entries):
    return [(sha, path) for sha, path in entries if goes_through_lfs(path)]


def not_pointers(repo, entries, sizes):
    """Tracked originals whose blob is the file itself and not an LFS pointer."""
    plain = []
    for sha, path in originals(entries):
        if sizes.get(sha, POINTER_MAX + 1) > POINTER_MAX:
            plain.append(path)
        elif not checked(git(repo, "cat-file", "blob", sha)).startswith(LFS_HEADER):
            plain.append(path)
    return sorted(plain)


def without_the_attribute(repo, entries):
    paths = [path for _, path in originals(entries)]
    if not paths:
        return []
    found = attributes(repo, ["filter"], paths)
    return sorted(path for path in paths if found[path]["filter"] != "lfs")


# ── the real repository ──────────────────────────────────────────────────────

class RealRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reason = why_not_the_real_repository()
        if reason:
            raise unittest.SkipTest(reason)


ORIGINALS = [
    "brushes/library/user/x/y.brushset",
    "brushes/library/official/x/y.brushset",
    "brushes/library/user/x/z.brush",
    "brushes/library/official/procreate-5/p5-inking.brushset",
    "brushes/library/user/sargents-oils/Sargent’s_Oils.brushset",
    "brushes/library/user/a pack/with space/Deep_er.brush",
    "brushes/library/top-level.brushset",
    # What comes back from a device: the only copy there is.
    "brushes/device-tests/sitting-1/returned/ROSW 1 Control.brushset",
    "brushes/device-tests/sitting-1/returned/Untitled Brush.brush",
    "brushes/device-tests/sitting-2/returned/shared/Edited.brush",
]
NOT_ORIGINALS = [
    "brushes/pipeline/tests/x.brushset", "brushes/app/assets/y.brush",
    "brushes/device-tests/ROSW-1-control.brushset", "brushes/library/sources.json",
    "brushes/library/README.md", "brushes/library/official/fetch_log.jsonl",
    "brushes/library/user/x/y.brushset.txt", "studio/x.brushset",
    # Built for a sitting: scratch, ignored, and not LFS's business.
    "brushes/device-tests/sitting-1/ROSW-1-control.brushset",
    "brushes/device-tests/sitting-1/singles/1-Broken_Conte.brush",
    "brushes/device-tests/sitting-1/known-bad/KNOWN-BAD_old-designer.brush",
    "brushes/device-tests/sitting-1/manifest.json",
    "brushes/device-tests/sitting-1/returned/notes.txt",
]
TEXT = [
    "brushes/README.md", "brushes/spec.yaml", "brushes/pipeline/identity.py",
    "brushes/library/sources.json", "brushes/catalog/brushes/b_0123456789ab.json",
    "brushes/vault/02_Vendor_Packs/demo-set.md", "brushes/library/official/fetch_log.jsonl",
    "brushes/device-tests/sitting-1/manifest.json", "brushes/device-tests/sitting-1/CHECKLIST.md",
]
# The earlier designer, as received: no line-ending conversion at all, so that
# the nine files that came with CRLF are stored with CRLF.
AS_RECEIVED = [
    "brushes/app/index.html", "brushes/app/app.js", "brushes/app/editor/BrushState.js",
    "brushes/app/export/PlistEncoder.js", "brushes/app/styles.css",
]
BINARY = [
    "brushes/x.png", "brushes/vault/_Previews/demo-set/b_0123456789ab.stroke.png",
    "brushes/vault/_Previews/_textures/t_0123456789ab.n.shape.png",
    "brushes/a/b/Brush.archive", "brushes/app/assets/icon.png",
]


class Attributes(RealRepository):
    def test_the_original_brush_files_go_through_lfs(self):
        found = attributes(REPO, ["filter", "diff", "merge", "text"], ORIGINALS)
        for path in ORIGINALS:
            self.assertEqual(found[path], {"filter": "lfs", "diff": "lfs", "merge": "lfs", "text": "unset"},
                             path)

    def test_only_the_library_does(self):
        found = attributes(REPO, ["filter"], NOT_ORIGINALS)
        for path in NOT_ORIGINALS:
            self.assertEqual(found[path]["filter"], "unspecified", path)

    def test_text_is_detected_not_forced_and_stored_with_lf(self):
        found = attributes(REPO, ["text", "eol"], TEXT)
        for path in TEXT:
            self.assertEqual(found[path], {"text": "auto", "eol": "lf"}, path)

    def test_images_and_archives_are_binary(self):
        found = attributes(REPO, ["text", "diff", "merge"], BINARY)
        for path in BINARY:
            self.assertEqual(found[path], {"text": "unset", "diff": "unset", "merge": "unset"}, path)

    def test_the_designer_as_received_is_stored_byte_for_byte(self):
        """`text` unset: git converts no line ending in either direction, so a
        file received with CRLF is committed and checked out with CRLF."""
        found = attributes(REPO, ["text", "filter", "diff"], AS_RECEIVED)
        for path in AS_RECEIVED:
            self.assertEqual(found[path], {"text": "unset", "filter": "unspecified", "diff": "unspecified"},
                             path)

    def test_the_files_received_with_crlf_still_have_it(self):
        """Nine files of the old designer came with CRLF. Nothing may have
        rewritten them in the working tree."""
        app = BRUSHES / "app"
        if not app.is_dir():
            self.skipTest("no brushes/app here")
        crlf = sorted(path.relative_to(app).as_posix() for path in app.rglob("*.js")
                      if b"\r\n" in path.read_bytes())
        self.assertEqual(crlf, [
            "editor/BrushState.js", "editor/HistoryManager.js", "editor/PresetLibrary.js",
            "export/BrushArchive.js", "export/BrushExporter.js", "export/PlistEncoder.js",
            "generators/GrainGenerator.js", "generators/ShapeGenerator.js", "ui/Slider.js"])

    def test_nothing_outside_brushes_changed(self):
        found = attributes(REPO, ["filter", "text"], ["creative-writing/README.md",
                                                     "studio/pipeline/spec.yaml", "docs/index.html",
                                                     "README.md"])
        for path, values in found.items():
            self.assertEqual(values, {"filter": "unspecified", "text": "unspecified"}, path)


class Ignored(RealRepository):
    def test_what_is_never_committed(self):
        for path in (
                "brushes/device-tests/sitting-1/ROSW-1-control.brushset",
                "brushes/device-tests/sitting-1/singles/1-Broken_Conte.brush",
                "brushes/device-tests/sitting-1/known-bad/KNOWN-BAD_old-designer.brush",
                "brushes/device-tests/sitting-1/manifest.json.tmp",
                "brushes/device-tests/trial/ROSW-1-control.brushset",
                "brushes/device-tests/trial/singles/2-Steady.brush",
                "brushes/device-tests/sitting-1/returned/Archive.zip",
                "brushes/library/user/demo-pack/_docs/Guide.pdf",
                "brushes/library/bundled/Brush-Preset-Hard.png",
                "brushes/library/official/procreate-5/p5-inking.brushset.part",
                "brushes/library/user/demo-pack/Name.brushset.zip",
                "brushes/library/user/demo-pack/Vendor_Pack.zip",
                "brushes/vault/tools/rag_index/index.json",
                "brushes/vault/_Previews/_sheets/demo-set/sheet-01.png",
                "brushes/vault/_Previews/_sheets/demo-set/sheets.json",
                "brushes/vault/_Previews/_local/demo-set/b_0123456789ab.stroke.png",
                "brushes/pipeline/__pycache__/identity.cpython-313.pyc",
                "brushes/pipeline/runs/scratch.json"):
            self.assertTrue(ignored(REPO, path), path)

    def test_the_record_of_a_device_sitting_is_committed(self):
        """A sitting's built brush files are scratch. Its manifest (a new build
        draws new folder names), its checklist and what came back are not."""
        for path in (
                "brushes/device-tests/sitting-1/manifest.json",
                "brushes/device-tests/sitting-1/CHECKLIST.md",
                "brushes/device-tests/sitting-1/returned/ROSW 1 Control.brushset",
                "brushes/device-tests/sitting-1/returned/Untitled Brush.brush",
                "brushes/device-tests/sitting-1/returned/notes.txt",
                "brushes/device-tests/sitting-1/returned/photos/page-1.jpg",
                "brushes/device-tests/sitting-2/manifest.json",
                "brushes/device-tests/sitting-2/returned/ROSW 2 Edits.brushset"):
            self.assertFalse(ignored(REPO, path), path)

    def test_what_is_committed(self):
        for path in (
                "brushes/library/official/fetch_log.jsonl",
                "brushes/library/user/demo-pack/Name.brushset",
                "brushes/library/user/demo-pack/Loose.brush",
                "brushes/library/official/procreate-5/p5-inking.brushset",
                "brushes/library/sources.json",
                "brushes/library/README.md",
                "brushes/catalog/catalog.json",
                "brushes/catalog/brushes/b_0123456789ab.json",
                "brushes/vault/02_Vendor_Packs/demo-set.md",
                "brushes/vault/_BrushTags/02_Vendor_Packs/demo-set.md.tags.json",
                "brushes/vault/_BrushTags/vocabulary.yaml",
                "brushes/vault/_Previews/manifest.json",
                "brushes/vault/_Previews/demo-set/b_0123456789ab.stroke.png",
                "brushes/vault/_Previews/_textures/t_0123456789ab.grain.png",
                "brushes/vault/tools/brush_search.py",
                "brushes/schema/silica_keys.json",
                "brushes/spec.yaml",
                "brushes/docs/CONTRACTS.md",
                "brushes/pipeline/tests/fixtures.py",
                "brushes/app/index.html"):
            self.assertFalse(ignored(REPO, path), path)


class Tracked(RealRepository):
    """What is in the index now. With nothing under brushes/ staged yet these
    pass on an empty list; TheChecksThemselves shows they can fail."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.entries = tracked(REPO)
        cls.sizes = blob_sizes(REPO, cls.entries)

    def test_nothing_tracked_under_brushes_is_a_zip(self):
        self.assertEqual(zips(self.entries), [],
                         "a set is stored as Name.brushset; the repository ignores *.zip")

    def test_no_plain_blob_is_over_the_limit(self):
        self.assertEqual(large_blobs(self.entries, self.sizes), [],
                         "a file this large must be tracked through Git LFS")

    def test_every_tracked_original_is_an_lfs_pointer(self):
        self.assertEqual(not_pointers(REPO, self.entries, self.sizes), [],
                         "added without the LFS filter: run `git lfs install`, then add it again")

    def test_every_tracked_original_has_the_lfs_attribute(self):
        self.assertEqual(without_the_attribute(REPO, self.entries), [])

    def test_the_limit_is_the_declared_one(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml is not installed")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec["commit_policy"]["limits"]["plain_blob_mb"] * 1000 * 1000, PLAIN_BLOB_LIMIT)
        self.assertLess(PLAIN_BLOB_LIMIT, 100 * 1024 * 1024)


# ── the checks, on a repository with the mistakes planted ────────────────────

class TheChecksThemselves(unittest.TestCase):
    """A scratch repository in a temporary folder. The planted files are staged
    before any attribute file exists, which is exactly how an original ends up
    in git without LFS: added on a machine where the rule had not arrived."""

    @classmethod
    def setUpClass(cls):
        if not (REPO / ".gitattributes").is_file():
            raise unittest.SkipTest("brushes/ is not inside its repository: no attribute file to try")
        cls.case = unittest.TestCase()
        cls.repo = fixtures.temp_dir(cls.case, prefix="brushes-policy-")
        cls.case.addCleanup(make_writable, cls.repo)
        checked(git(cls.repo, "init", "-q"))
        checked(git(cls.repo, "config", "core.autocrlf", "false"))
        brush = fixtures.brush_file(fixtures.make_brush("Planted", number=31))
        cls.planted = {
            "brushes/library/user/p/Plain.brushset": brush + bytes(16384),
            "brushes/library/user/p/Small_Plain.brush": b"PK\x03\x04 short, but not a pointer",
            "brushes/library/user/p/Pointer.brushset": fixtures.LFS_POINTER,
            "brushes/library/user/p/Old.brushset.zip": brush,
            "brushes/device-tests/sitting-1/returned/Came Back.brushset": brush,
            "brushes/device-tests/sitting-1/returned/Pointer.brush": fixtures.LFS_POINTER,
            "brushes/device-tests/sitting-1/singles/1-Scratch.brush": brush,
            "brushes/catalog/big.json": b"{" + b" " * 20000 + b"}",
            "brushes/catalog/small.json": b"{}\n",
            "elsewhere/outside.zip": brush,
        }
        for relative, data in cls.planted.items():
            target = cls.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        checked(git(cls.repo, "add", "-f", "--", *cls.planted))
        shutil.copyfile(REPO / ".gitattributes", cls.repo / ".gitattributes")
        cls.entries = tracked(cls.repo)
        cls.sizes = blob_sizes(cls.repo, cls.entries)

    @classmethod
    def tearDownClass(cls):
        cls.case.doCleanups()

    def test_the_scratch_repository_is_not_the_real_one(self):
        self.assertNotIn(REPO.resolve(), [self.repo, *self.repo.parents])
        top = Path(checked(git(self.repo, "rev-parse", "--show-toplevel")).decode("utf-8").strip())
        self.assertEqual(top.resolve(), self.repo)

    def test_only_what_is_under_brushes_is_looked_at(self):
        self.assertEqual(sorted(path for _, path in self.entries),
                         sorted(path for path in self.planted if path.startswith("brushes/")))

    def test_a_tracked_zip_is_found(self):
        self.assertEqual(zips(self.entries), ["brushes/library/user/p/Old.brushset.zip"])

    def test_a_large_blob_is_found(self):
        self.assertEqual(large_blobs(self.entries, self.sizes), [])
        self.assertEqual(large_blobs(self.entries, self.sizes, limit=10000),
                         ["brushes/catalog/big.json", "brushes/library/user/p/Plain.brushset"])
        sha_of = {path: sha for sha, path in self.entries}
        self.assertEqual(self.sizes[sha_of["brushes/catalog/big.json"]], 20002)
        self.assertLess(self.sizes[sha_of["brushes/library/user/p/Old.brushset.zip"]], 10000)

    def test_an_original_added_without_lfs_is_found(self):
        self.assertEqual(not_pointers(self.repo, self.entries, self.sizes),
                         ["brushes/device-tests/sitting-1/returned/Came Back.brushset",
                          "brushes/library/user/p/Plain.brushset", "brushes/library/user/p/Small_Plain.brush"])

    def test_which_brush_files_must_be_pointers(self):
        for path in ORIGINALS:
            self.assertTrue(goes_through_lfs(path), path)
        for path in NOT_ORIGINALS:
            self.assertFalse(goes_through_lfs(path), path)
        self.assertNotIn("brushes/device-tests/sitting-1/singles/1-Scratch.brush",
                         [path for _, path in originals(self.entries)],
                         "a built file, force-added, is not LFS's to track")

    def test_a_pointer_is_not_mistaken_for_one(self):
        self.assertNotIn("brushes/library/user/p/Pointer.brushset",
                         not_pointers(self.repo, self.entries, self.sizes))
        self.assertNotIn("brushes/library/user/p/Pointer.brushset",
                         large_blobs(self.entries, self.sizes, limit=POINTER_MAX))

    def test_the_real_attribute_file_gives_the_same_answers_here(self):
        found = attributes(self.repo, ["filter", "text"], ORIGINALS + NOT_ORIGINALS + BINARY)
        for path in ORIGINALS:
            self.assertEqual(found[path], {"filter": "lfs", "text": "unset"}, path)
        for path in NOT_ORIGINALS:
            self.assertEqual(found[path]["filter"], "unspecified", path)
        for path in BINARY:
            self.assertEqual(found[path]["text"], "unset", path)
        self.assertEqual(without_the_attribute(self.repo, self.entries), [])

    def test_an_original_outside_the_rule_is_found(self):
        (self.repo / ".gitattributes").write_bytes(b"brushes/library/user/**/*.brushset filter=lfs\n")
        self.addCleanup(shutil.copyfile, REPO / ".gitattributes", self.repo / ".gitattributes")
        self.assertEqual(without_the_attribute(self.repo, self.entries),
                         ["brushes/device-tests/sitting-1/returned/Came Back.brushset",
                          "brushes/device-tests/sitting-1/returned/Pointer.brush",
                          "brushes/library/user/p/Small_Plain.brush"])


if __name__ == "__main__":
    unittest.main()
