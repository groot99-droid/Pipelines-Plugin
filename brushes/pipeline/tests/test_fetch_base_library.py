"""pipeline/fetch_base_library.py: list, fetch and verify (docs/CONTRACTS.md, F11).

No test here opens a connection. The script takes the object it sends requests
through as an argument, and every test hands it one that answers from a table;
on top of that, setUp makes any attempt to connect a socket fail the test. The
library is a temporary folder with a manifest in the real schema that names
the host `downloads.invalid`, which the script itself would refuse to open:
only a test's own opener ever sees that name.

    python -m unittest discover -s brushes/pipeline/tests
"""

import contextlib
import hashlib
import io
import json
import os
import socket
import subprocess
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fetch_base_library as fb  # noqa: E402
import fixtures  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "fetch_base_library.py"
HOST = "downloads.invalid"
BASE = f"https://{HOST}/fixtures/"
PACK = fixtures.OFFICIAL_PACK


def md5(data):
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


class Headers(dict):
    """Response headers: looked up without regard to case, as the real ones are."""

    def get(self, name, default=None):
        for key, value in self.items():
            if key.lower() == name.lower():
                return value
        return default


class FakeResponse:
    def __init__(self, body, url, *, status=200, headers=None, length="body", etag="md5"):
        self.body = io.BytesIO(body)
        self.url = url
        self.status = status
        self.headers = Headers(headers or {})
        if length == "body":
            length = len(body)
        if length is not None:
            self.headers.setdefault("Content-Length", str(length))
        if etag == "md5":
            etag = f'"{md5(body)}"'
        if etag is not None:
            self.headers.setdefault("ETag", etag)
        self.headers.setdefault("Last-Modified", "Tue, 04 Aug 2026 10:00:00 GMT")
        self.reads = 0
        self.closed = False

    def geturl(self):
        return self.url

    def read(self, amount=-1):
        self.reads += 1
        return self.body.read(amount)

    def close(self):
        self.closed = True


class FakeOpener:
    """Stands where the network would be. `answers` maps an address to a list
    of answers, used in turn (the last one repeats): bytes for a plain 200, a
    FakeResponse, or an exception to raise."""

    def __init__(self, answers=None):
        self.answers = {url: list(items) for url, items in (answers or {}).items()}
        self.requests = []
        self.timeouts = []
        self.responses = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        self.timeouts.append(timeout)
        url = request.full_url
        if url not in self.answers:
            raise AssertionError(f"an unexpected request: {url}")
        queue = self.answers[url]
        answer = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(answer, BaseException):
            raise answer
        if isinstance(answer, bytes):
            answer = FakeResponse(answer, url)
        self.responses.append(answer)
        return answer

    @property
    def urls(self):
        return [request.full_url for request in self.requests]


def http_error(url, code):
    return urllib.error.HTTPError(url, code, "fixture", Headers(), io.BytesIO(b""))


class FetchCase(fixtures.BrushCase):
    """A temporary library whose manifest names two small official sets."""

    SLUGS = ("demo-one", "demo-two")

    def setUp(self):
        super().setUp()
        for target in ("socket.socket.connect", "socket.create_connection"):
            patcher = mock.patch(target, side_effect=AssertionError("a test opened a connection"))
            patcher.start()
            self.addCleanup(patcher.stop)
        self.library = self.tmp / "library"
        self.library.mkdir()
        self.bodies = {
            slug: fixtures.brushset_file(f"Official {number}", [
                fixtures.make_brush(f"Official Brush {number}", "modern", number=40 + number)])
            for number, slug in enumerate(self.SLUGS, start=1)}
        self.sources = fixtures.standard_sources()
        self.sources["official"]["files"] = [self.entry(slug) for slug in self.SLUGS]
        self.write_sources()
        self.sleeps = []

    def entry(self, slug, **changes):
        body = self.bodies[slug]
        entry = {"pack": PACK, "slug": slug, "title": slug.replace("-", " ").title(),
                 "path": f"Demo%20Sets/{slug}.brushset", "bytes": len(body), "md5": md5(body)}
        entry.update(changes)
        return entry

    def write_sources(self):
        with open(self.library / "sources.json", "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(self.sources, ensure_ascii=False, indent=2) + "\n")

    def use_the_allowed_host(self):
        """Make the manifest name the one host the script may open. Only for a
        test of a path that builds no opener; setUp fails any connection."""
        host = fb.ALLOWED_HOSTS[0]
        self.sources["official"]["host"] = host
        self.sources["official"]["base"] = f"https://{host}/fixtures/"
        self.write_sources()

    def url(self, slug):
        return f"{BASE}Demo%20Sets/{slug}.brushset"

    def dest(self, slug):
        return self.library / "official" / PACK / f"{slug}.brushset"

    def log(self):
        path = self.library / "official" / "fetch_log.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def good(self):
        return FakeOpener({self.url(slug): [self.bodies[slug]] for slug in self.SLUGS})

    def run_main(self, *argv, opener=None, free=10 ** 12):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fb.main([*argv, "--library", str(self.library)],
                           opener=opener if opener is not None else FakeOpener(),
                           sleep=self.sleeps.append, disk_free=lambda folder: free)
        return code, out.getvalue(), err.getvalue()

    def files(self):
        return sorted(p.relative_to(self.library).as_posix() for p in self.library.rglob("*") if p.is_file())


# ── the manifest ─────────────────────────────────────────────────────────────

class TheManifest(FetchCase):
    def test_the_official_block_is_read(self):
        official = fb.load_official(self.library)
        self.assertEqual((official.host, official.base), (HOST, BASE))
        self.assertEqual([item.key for item in official.files], [f"{PACK}/{slug}" for slug in self.SLUGS])
        first = official.files[0]
        self.assertEqual(first.url, self.url("demo-one"))
        self.assertEqual(first.stored, f"official/{PACK}/demo-one.brushset")
        self.assertEqual((first.bytes, first.md5), (len(self.bodies["demo-one"]), md5(self.bodies["demo-one"])))

    def test_a_missing_manifest_is_exit_2(self):
        (self.library / "sources.json").unlink()
        code, out, err = self.run_main("list")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("sources.json", err)
        code, _, _ = self.run_main("fetch", "--confirm")
        self.assertEqual(code, bc.EXIT_USAGE)

    def test_a_manifest_that_is_not_json_or_not_this_schema_is_exit_2(self):
        (self.library / "sources.json").write_text("{ not json", encoding="utf-8")
        self.assertEqual(self.run_main("verify")[0], bc.EXIT_USAGE)
        self.sources["schema"] = "something-else/9"
        self.write_sources()
        self.assertEqual(self.run_main("verify")[0], bc.EXIT_USAGE)

    def test_an_address_that_could_leave_the_host_is_refused_before_any_request(self):
        bad = {
            "http, not https": {"base": f"http://{HOST}/fixtures/"},
            "a base on another host": {"base": "https://elsewhere.invalid/fixtures/"},
            "a base with user info": {"base": f"https://user@{HOST}/fixtures/"},
            "a base with a port": {"base": f"https://{HOST}:8443/fixtures/"},
            "a base without its slash": {"base": f"https://{HOST}/fixtures"},
            "a base with a query": {"base": f"https://{HOST}/fixtures/?x=1/"},
            "a host with a slash": {"host": f"{HOST}/x"},
            "an upper-case host": {"host": HOST.upper()},
        }
        paths = {
            "an absolute path": "/Demo/x.brushset",
            "a path that climbs": "Demo/../../x.brushset",
            "a full address": "https://elsewhere.invalid/x.brushset",
            "a host-relative path": "//elsewhere.invalid/x.brushset",
            "a path with a space": "Demo Sets/x.brushset",
            "a path with a backslash": "Demo\\x.brushset",
            "a path with a query": "Demo/x.brushset?redirect=1",
            "a path with a fragment": "Demo/x.brushset#f",
            "a path that is not ASCII": "Demo/浓.brushset",
            "an empty path": "",
        }
        opener = FakeOpener()
        for what, change in bad.items():
            self.sources = fixtures.standard_sources()
            self.sources["official"]["files"] = [self.entry("demo-one")]
            self.sources["official"].update(change)
            self.write_sources()
            code, _, err = self.run_main("fetch", "--confirm", opener=opener)
            self.assertEqual(code, bc.EXIT_USAGE, what)
            self.assertIn("error:", err, what)
        for what, path in paths.items():
            self.sources = fixtures.standard_sources()
            self.sources["official"]["files"] = [self.entry("demo-one", path=path)]
            self.write_sources()
            code, _, err = self.run_main("fetch", "--confirm", opener=opener)
            self.assertEqual(code, bc.EXIT_USAGE, what)
        self.assertEqual(opener.requests, [])
        self.assertEqual(self.files(), ["sources.json"])

    def test_pins_and_destinations_are_checked(self):
        bad = {
            "an md5 that is not 32 hex": {"md5": "XYZ"},
            "an upper-case md5": {"md5": "A" * 32},
            "a negative size": {"bytes": -1},
            "a size that is text": {"bytes": "12"},
            "a size over the download cap": {"bytes": fb.MAX_DOWNLOAD_BYTES + 1},
            "a pack that is a path": {"pack": "../user"},
            "a pack id too long for its loose set": {"pack": "p" * (fb.identity.PACK_ID_MAX + 1)},
            "a slug with a slash": {"slug": "a/b"},
            "a slug in upper case": {"slug": "Demo"},
        }
        for what, change in bad.items():
            entry = self.entry("demo-one")
            entry.update(change)
            self.sources["official"]["files"] = [entry]
            self.write_sources()
            with self.assertRaises(fb.ManifestError, msg=what):
                fb.load_official(self.library)
        self.sources["official"]["files"] = [self.entry("demo-one"), self.entry("demo-one")]
        self.write_sources()
        with self.assertRaises(fb.ManifestError):
            fb.load_official(self.library)

    def test_check_url(self):
        self.assertEqual(fb.check_url(self.url("demo-one"), HOST), self.url("demo-one"))
        for url in (f"http://{HOST}/x", "https://elsewhere.invalid/x", f"https://{HOST}:443/x",
                    f"https://user:pw@{HOST}/x", f"https://{HOST}.elsewhere.invalid/x",
                    f"https://{HOST.upper()}/x", f"ftp://{HOST}/x", "file:///etc/passwd",
                    f"https://{HOST}:port/x", "/x", ""):
            with self.assertRaises(fb.Refused, msg=url):
                fb.check_url(url, HOST)

    def test_the_real_manifest_loads_and_stays_on_its_host(self):
        official = fb.load_official(BRUSHES / "library")
        self.assertEqual(official.host, "download-assets.procreate.art")
        self.assertEqual(len(official.files), 40)
        self.assertEqual(len({item.stored for item in official.files}), 40)
        for item in official.files:
            self.assertTrue(item.url.startswith("https://download-assets.procreate.art/Old%20Procreate%20Assets/"))
            self.assertTrue(item.stored.isascii())
            self.assertRegex(item.stored, r"^official/[a-z0-9-]+/[a-z0-9-]+\.brushset$")


# ── list and the dry run ─────────────────────────────────────────────────────

class ListAndDryRun(FetchCase):
    def test_list_names_every_file_and_opens_nothing(self):
        opener = FakeOpener()
        code, out, err = self.run_main("list", opener=opener)
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        for slug in self.SLUGS:
            self.assertIn(f"{PACK}/{slug}", out)
            self.assertIn(md5(self.bodies[slug]), out)
        self.assertIn("2 missing", out)
        self.assertIn(HOST, out)
        self.assertEqual(opener.requests, [])
        self.assertEqual(self.files(), ["sources.json"])

    def test_list_sees_what_is_here(self):
        self.dest("demo-one").parent.mkdir(parents=True)
        self.dest("demo-one").write_bytes(self.bodies["demo-one"])
        self.dest("demo-two").write_bytes(self.bodies["demo-two"] + b"more")
        code, out, _ = self.run_main("list")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("1 differs, 1 present", out)

    def test_fetch_without_confirm_is_a_dry_run(self):
        before = fixtures.tree_digest(self.tmp)
        opener = FakeOpener()
        code, out, err = self.run_main("fetch", opener=opener)
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertEqual(out.rstrip("\n").splitlines()[-1], "DRY RUN   nothing is written without --confirm.")
        self.assertEqual(fb.DRY_RUN_LINE, "DRY RUN   nothing is written without --confirm.")
        for slug in self.SLUGS:
            self.assertIn(self.url(slug), out)
            self.assertIn(f"official/{PACK}/{slug}.brushset", out)
        self.assertIn("2 to download", out)
        self.assertEqual(opener.requests, [], "a dry run opens no connection")
        self.assertEqual(self.sleeps, [])
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse((self.library / "official").exists())

    def test_the_dry_run_does_not_build_an_opener(self):
        self.use_the_allowed_host()
        with mock.patch.object(fb, "make_opener", side_effect=AssertionError("built")):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = fb.main(["--library", str(self.library), "fetch"])
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn(fb.DRY_RUN_LINE, out.getvalue())


# ── the one host ─────────────────────────────────────────────────────────────

class TheOneHost(FetchCase):
    """The manifest names its host, and --library or ROSW_BRUSHES_LIBRARY can
    point at any manifest. Only a host in ALLOWED_HOSTS is ever opened."""

    def run_real(self, *argv):
        """main() as the command line runs it: no opener handed in."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fb.main([*argv, "--library", str(self.library)], sleep=self.sleeps.append,
                           disk_free=lambda folder: 10 ** 12)
        return code, out.getvalue(), err.getvalue()

    def test_the_allow_list_is_the_one_documented_host(self):
        self.assertEqual(fb.ALLOWED_HOSTS, ("download-assets.procreate.art",))
        self.assertIn(fb.load_official(BRUSHES / "library").host, fb.ALLOWED_HOSTS)
        self.assertNotIn(HOST, fb.ALLOWED_HOSTS, "the fixtures' host is never one that is opened")

    def test_fetch_refuses_a_manifest_that_names_another_host(self):
        before = fixtures.tree_digest(self.tmp)
        with mock.patch.object(urllib.request.OpenerDirector, "open",
                               side_effect=AssertionError("a request was made")):
            for argv in (["fetch"], ["fetch", "--confirm"], ["fetch", "--confirm", "--accept-upstream"],
                         ["fetch", "--only", "demo-one", "--confirm"]):
                code, out, err = self.run_real(*argv)
                self.assertEqual(code, bc.EXIT_USAGE, argv)
                self.assertIn(f"official.host is '{HOST}'", err, argv)
                self.assertIn(fb.ALLOWED_HOSTS[0], err, argv)
                self.assertNotIn(fb.DRY_RUN_LINE, out, "a dry run of a fetch that would be refused is refused")
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertEqual(self.sleeps, [])

    def test_the_environment_cannot_point_it_at_another_host_either(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {bc.ENV_LIBRARY: str(self.library)}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fb.main(["fetch", "--confirm"])
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("official.host", err.getvalue())
        self.assertEqual(self.files(), ["sources.json"])

    def test_no_opener_is_built_for_another_host(self):
        for host in (HOST, "elsewhere.invalid", fb.ALLOWED_HOSTS[0] + ".elsewhere.invalid",
                     fb.ALLOWED_HOSTS[0].upper(), "procreate.art", ""):
            with self.assertRaises(fb.ManifestError, msg=host):
                fb.make_opener(host)
            with self.assertRaises(fb.ManifestError, msg=host):
                fb.check_host(host)
        self.assertEqual(fb.check_host(fb.ALLOWED_HOSTS[0]), fb.ALLOWED_HOSTS[0])

    def test_list_and_verify_still_read_such_a_manifest_and_say_so(self):
        code, out, err = self.run_real("list")
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertIn("NOT A HOST THIS SCRIPT MAY OPEN", out)
        self.use_the_allowed_host()
        code, out, err = self.run_real("list")
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertNotIn("NOT A HOST", out)


# ── a confirmed fetch ────────────────────────────────────────────────────────

class Confirmed(FetchCase):
    def test_it_downloads_checks_and_stores_every_file(self):
        opener = self.good()
        code, out, err = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        for slug in self.SLUGS:
            self.assertEqual(self.dest(slug).read_bytes(), self.bodies[slug])
        self.assertEqual(self.files(), [f"official/{PACK}/demo-one.brushset",
                                        f"official/{PACK}/demo-two.brushset",
                                        "official/fetch_log.jsonl", "sources.json"])
        self.assertEqual(opener.urls, [self.url(slug) for slug in self.SLUGS])
        self.assertIn("2 downloaded", out)
        self.assertNotIn("DRY RUN", out)

    def test_every_request_is_a_get_over_https_with_a_name_and_a_timeout(self):
        opener = self.good()
        self.run_main("fetch", "--confirm", opener=opener)
        for request in opener.requests:
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual((request.type, request.host), ("https", HOST))
            self.assertIsNone(request.data)
            agent = request.get_header("User-agent")
            self.assertEqual(agent, fb.USER_AGENT)
            self.assertRegex(agent, r"^rosw-brushes/\S+ \(\+https://github\.com/\S+\)$")
        self.assertEqual(opener.timeouts, [fb.TIMEOUT_SECONDS] * 2)
        self.assertEqual(fb.TIMEOUT_SECONDS, 60)
        self.assertTrue(all(response.closed for response in opener.responses))

    def test_it_waits_between_requests_and_not_after_the_last(self):
        self.run_main("fetch", "--confirm", opener=self.good())
        self.assertEqual(self.sleeps, [fb.DEFAULT_DELAY])
        self.assertEqual(fb.DEFAULT_DELAY, 1.0)

    def test_the_delay_can_be_set(self):
        self.run_main("fetch", "--delay", "0.25", "--confirm", opener=self.good())
        self.assertEqual(self.sleeps, [0.25])

    def test_the_log_has_one_line_per_file_and_no_clock_and_no_machine_path(self):
        self.run_main("fetch", "--confirm", opener=self.good())
        records = self.log()
        self.assertEqual([record["slug"] for record in records], list(self.SLUGS))
        for record, slug in zip(records, self.SLUGS):
            body = self.bodies[slug]
            self.assertEqual(set(record), {"schema", "pack", "slug", "file", "url", "bytes", "md5",
                                           "sha256", "etag", "last_modified", "pins"})
            self.assertEqual(record["schema"], "rosw-brushes-fetch/1")
            self.assertEqual(record["file"], f"official/{PACK}/{slug}.brushset")
            self.assertEqual(record["url"], self.url(slug))
            self.assertEqual(record["bytes"], len(body))
            self.assertEqual(record["md5"], md5(body))
            self.assertEqual(record["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual(record["etag"], f'"{md5(body)}"')
            self.assertEqual(record["last_modified"], "Tue, 04 Aug 2026 10:00:00 GMT")
            self.assertEqual(record["pins"], "match")
        raw = (self.library / "official" / "fetch_log.jsonl").read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(str(self.tmp).encode("utf-8"), raw)
        self.assertNotIn(self.tmp.name.encode("utf-8"), raw)
        for word in (b"fetched_at", b"timestamp", b"date"):
            self.assertNotIn(word, raw.lower())

    def test_a_file_already_here_and_correct_is_skipped_without_a_request(self):
        self.run_main("fetch", "--confirm", opener=self.good())
        log = (self.library / "official" / "fetch_log.jsonl").read_bytes()
        before = fixtures.tree_digest(self.library)
        self.sleeps.clear()
        opener = FakeOpener()
        code, out, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(opener.requests, [])
        self.assertEqual(self.sleeps, [])
        self.assertIn("0 to download", out)
        self.assertEqual((self.library / "official" / "fetch_log.jsonl").read_bytes(), log)
        self.assertEqual(fixtures.tree_digest(self.library), before)

    def test_only_the_missing_file_is_asked_for(self):
        self.dest("demo-one").parent.mkdir(parents=True)
        self.dest("demo-one").write_bytes(self.bodies["demo-one"])
        opener = self.good()
        code, _, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(opener.urls, [self.url("demo-two")])
        self.assertEqual(self.sleeps, [])
        self.assertEqual(len(self.log()), 1)

    def test_a_local_file_that_differs_is_replaced(self):
        self.dest("demo-one").parent.mkdir(parents=True)
        self.dest("demo-one").write_bytes(b"an older download")
        self.dest("demo-two").write_bytes(self.bodies["demo-two"])
        opener = self.good()
        code, out, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("replace", out)
        self.assertEqual(opener.urls, [self.url("demo-one")])
        self.assertEqual(self.dest("demo-one").read_bytes(), self.bodies["demo-one"])

    def test_only_selects_by_pack_and_slug(self):
        opener = self.good()
        code, _, _ = self.run_main("fetch", "--only", "two", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(opener.urls, [self.url("demo-two")])
        self.assertFalse(self.dest("demo-one").exists())
        code, _, err = self.run_main("fetch", "--only", "no-such-set", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("--only", err)

    def test_a_leftover_part_file_is_not_kept(self):
        part = self.dest("demo-one").with_name("demo-one.brushset.part")
        part.parent.mkdir(parents=True)
        part.write_bytes(b"half of an older attempt")
        code, _, _ = self.run_main("fetch", "--confirm", opener=self.good())
        self.assertEqual(code, bc.EXIT_OK)
        self.assertFalse(part.exists())
        self.assertEqual(self.dest("demo-one").read_bytes(), self.bodies["demo-one"])

    def test_the_manifest_is_never_written(self):
        before = (self.library / "sources.json").read_bytes()
        stamp = (self.library / "sources.json").stat().st_mtime_ns
        self.run_main("fetch", "--confirm", opener=self.good())
        self.run_main("verify")
        self.run_main("list")
        self.assertEqual((self.library / "sources.json").read_bytes(), before)
        self.assertEqual((self.library / "sources.json").stat().st_mtime_ns, stamp)

    def test_nothing_is_written_outside_official(self):
        outside = fixtures.temp_dir(self)
        with contextlib.ExitStack() as stack:
            stack.callback(os.chdir, os.getcwd())
            os.chdir(outside)
            self.run_main("fetch", "--confirm", opener=self.good())
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual({path.split("/")[0] for path in self.files()}, {"official", "sources.json"})

    def test_a_file_with_no_pins_is_fetched_and_its_real_values_reported(self):
        self.sources["official"]["files"] = [self.entry("demo-one", bytes=None, md5=None)]
        self.write_sources()
        code, out, _ = self.run_main("fetch", "--confirm", opener=self.good())
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.log()[0]["pins"], "none")
        self.assertIn(md5(self.bodies["demo-one"]), out)
        self.assertIn("sources.json", out)
        opener = FakeOpener()
        self.assertEqual(self.run_main("fetch", "--confirm", opener=opener)[0], bc.EXIT_OK)
        self.assertEqual(opener.requests, [], "a file that cannot be checked is not fetched again")
        self.assertEqual(self.run_main("verify")[0], bc.EXIT_REFUSED, "and verify does not vouch for it")

    def test_too_little_disk_space_is_exit_2_before_any_request(self):
        opener = self.good()
        code, _, err = self.run_main("fetch", "--confirm", opener=opener, free=1000)
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("free", err)
        self.assertEqual(opener.requests, [])
        self.assertEqual(self.files(), ["sources.json"])


# ── when the server's file is not the pinned one ─────────────────────────────

class UpstreamChanged(FetchCase):
    def changed(self, slug="demo-one", **response):
        body = bytes(reversed(self.bodies[slug]))
        answers = {self.url(s): [self.bodies[s]] for s in self.SLUGS}
        answers[self.url(slug)] = [FakeResponse(body, self.url(slug), **response)]
        return FakeOpener(answers), body

    def test_another_md5_is_refused_and_nothing_is_kept(self):
        opener, _ = self.changed(etag=None)
        code, out, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("upstream changed", out)
        self.assertIn("review and update sources.json", out)
        self.assertFalse(self.dest("demo-one").exists())
        self.assertEqual(self.files(), [f"official/{PACK}/demo-two.brushset", "official/fetch_log.jsonl",
                                        "sources.json"])
        self.assertEqual([record["slug"] for record in self.log()], ["demo-two"],
                         "the run went on with the other file")
        self.assertEqual(len(opener.requests), 2, "a changed file is not asked for again")

    def test_an_etag_that_is_not_the_pinned_md5_stops_before_the_body_is_read(self):
        opener, _ = self.changed()
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(opener.responses[0].reads, 0)
        self.assertTrue(opener.responses[0].closed)
        self.assertEqual(self.files(), ["sources.json"])

    def test_another_size_stops_before_the_body_is_read(self):
        body = self.bodies["demo-one"] + b"longer"
        opener = FakeOpener({self.url("demo-one"): [FakeResponse(body, self.url("demo-one"), etag=None)]})
        code, out, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("pinned", out)
        self.assertEqual(opener.responses[0].reads, 0)
        self.assertEqual(self.files(), ["sources.json"])

    def test_a_multipart_etag_is_not_taken_for_an_md5(self):
        body = self.bodies["demo-one"]
        opener = FakeOpener({self.url("demo-one"): [
            FakeResponse(body, self.url("demo-one"), etag=f'"{"0" * 32}-3"')]})
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.dest("demo-one").read_bytes(), body)

    def test_a_local_copy_survives_a_changed_upstream(self):
        self.dest("demo-one").parent.mkdir(parents=True)
        self.dest("demo-one").write_bytes(b"an older download")
        opener, _ = self.changed(etag=None)
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(self.dest("demo-one").read_bytes(), b"an older download")

    def test_accept_upstream_keeps_the_new_file_and_says_what_it_is(self):
        opener, body = self.changed()
        code, out, _ = self.run_main("fetch", "--accept-upstream", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.dest("demo-one").read_bytes(), body)
        record = self.log()[0]
        self.assertEqual((record["pins"], record["md5"], record["bytes"]), ("differ", md5(body), len(body)))
        self.assertEqual(self.log()[1]["pins"], "match")
        self.assertIn("update sources.json by hand", out)
        self.assertIn(md5(body), out)
        code, out, _ = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_REFUSED, "the pins are still the old ones until the author changes them")
        self.assertIn(md5(body), out)


# ── failures ─────────────────────────────────────────────────────────────────

class Failures(FetchCase):
    def one(self, *answers):
        return FakeOpener({self.url("demo-one"): list(answers), self.url("demo-two"): [self.bodies["demo-two"]]})

    def test_a_404_is_not_retried_and_the_run_goes_on(self):
        opener = self.one(http_error(self.url("demo-one"), 404))
        code, out, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(opener.urls, [self.url("demo-one"), self.url("demo-two")])
        self.assertIn("404", out)
        self.assertEqual(self.sleeps, [fb.DEFAULT_DELAY], "only the polite wait, no retry wait")
        self.assertTrue(self.dest("demo-two").exists())
        self.assertFalse(self.dest("demo-one").exists())

    def test_a_403_is_not_retried_either(self):
        opener = self.one(http_error(self.url("demo-one"), 403))
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(len(opener.requests), 1)

    def test_a_server_error_is_retried_with_longer_waits(self):
        url = self.url("demo-one")
        opener = self.one(http_error(url, 503), http_error(url, 500), self.bodies["demo-one"])
        code, out, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(len(opener.requests), 3)
        self.assertEqual(self.sleeps, [2, 4])
        self.assertEqual(self.dest("demo-one").read_bytes(), self.bodies["demo-one"])
        self.assertIn("trying again", out)

    def test_it_gives_up_after_three_retries(self):
        opener = self.one(http_error(self.url("demo-one"), 503))
        code, out, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(len(opener.requests), 4)
        self.assertEqual(self.sleeps, list(fb.RETRY_WAITS))
        self.assertEqual(fb.RETRY_WAITS, (2, 4, 8))
        self.assertIn("gave up after 4 attempts", out)
        self.assertEqual(self.files(), ["sources.json"])

    def test_a_connection_that_cannot_be_made_is_retried(self):
        opener = self.one(urllib.error.URLError("no route"), TimeoutError("slow"), self.bodies["demo-one"])
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.sleeps, [2, 4])

    def test_a_body_that_stops_short_is_retried_and_never_stored(self):
        url, body = self.url("demo-one"), self.bodies["demo-one"]
        short = FakeResponse(body[:100], url, length=len(body), etag=None)
        opener = self.one(short, body)
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(len(opener.requests), 2)
        self.assertEqual(self.dest("demo-one").read_bytes(), body)
        self.assertEqual(self.files(), [f"official/{PACK}/demo-one.brushset", "official/fetch_log.jsonl",
                                        "sources.json"])

    def test_a_connection_that_breaks_while_reading_is_retried(self):
        url, body = self.url("demo-one"), self.bodies["demo-one"]
        broken = FakeResponse(body, url)
        broken.read = mock.Mock(side_effect=ConnectionResetError("reset"))
        opener = self.one(broken, body)
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertTrue(broken.closed)
        self.assertEqual(self.dest("demo-one").read_bytes(), body)

    def test_an_announced_size_over_the_cap_is_refused_unread(self):
        url = self.url("demo-one")
        self.sources["official"]["files"] = [self.entry("demo-one", bytes=None, md5=None)]
        self.write_sources()
        huge = FakeResponse(b"x", url, length=fb.MAX_DOWNLOAD_BYTES + 1, etag=None)
        opener = FakeOpener({url: [huge]})
        code, out, _ = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(huge.reads, 0)
        self.assertEqual(len(opener.requests), 1, "a refusal is not retried")
        self.assertEqual(fb.MAX_DOWNLOAD_BYTES, 200 * 1000 * 1000)
        self.assertEqual(self.files(), ["sources.json"])

    def test_a_body_that_outgrows_the_cap_is_cut_off(self):
        url = self.url("demo-one")
        self.sources["official"]["files"] = [self.entry("demo-one", bytes=None, md5=None)]
        self.write_sources()
        endless = FakeResponse(b"x" * 5000, url, length=None, etag=None)
        with mock.patch.object(fb, "MAX_DOWNLOAD_BYTES", 1000), mock.patch.object(fb, "CHUNK", 400):
            code, _, _ = self.run_main("fetch", "--confirm", opener=FakeOpener({url: [endless]}))
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertLessEqual(endless.reads, 4)
        self.assertEqual(self.files(), ["sources.json"])

    def test_an_answer_that_came_from_somewhere_else_is_refused(self):
        url = self.url("demo-one")
        elsewhere = FakeResponse(self.bodies["demo-one"], "https://elsewhere.invalid/demo-one.brushset")
        opener = FakeOpener({url: [elsewhere]})
        code, out, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(elsewhere.reads, 0)
        self.assertTrue(elsewhere.closed)
        self.assertEqual(self.files(), ["sources.json"])

    def test_an_answer_that_is_not_200_is_a_failure(self):
        url = self.url("demo-one")
        partial = FakeResponse(self.bodies["demo-one"], url, status=206)
        code, _, _ = self.run_main("fetch", "--only", "demo-one", "--confirm", opener=FakeOpener({url: [partial]}))
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(self.files(), ["sources.json"])

    def test_an_empty_answer_is_a_failure(self):
        url = self.url("demo-one")
        self.sources["official"]["files"] = [self.entry("demo-one", bytes=None, md5=None)]
        self.write_sources()
        code, _, _ = self.run_main("fetch", "--confirm", opener=FakeOpener({url: [b""]}))
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(self.files(), ["sources.json"])


class TheOpener(unittest.TestCase):
    """The real opener, looked at but never used."""

    def test_it_speaks_https_only_and_uses_no_proxy(self):
        opener = fb.make_opener(fb.ALLOWED_HOSTS[0])
        kinds = [type(handler) for handler in opener.handlers]
        self.assertIn(urllib.request.HTTPSHandler, kinds)
        self.assertIn(fb.SameHostRedirect, kinds)
        for unwanted in (urllib.request.HTTPHandler, urllib.request.FTPHandler, urllib.request.FileHandler,
                         urllib.request.DataHandler, urllib.request.ProxyHandler):
            self.assertFalse(any(issubclass(kind, unwanted) for kind in kinds), unwanted.__name__)
        plain = [kind for kind in kinds if kind is urllib.request.HTTPRedirectHandler]
        self.assertEqual(plain, [], "the only redirect handler is the one that checks the host")

    def test_an_address_it_has_no_handler_for_is_an_error_not_a_request(self):
        opener = fb.make_opener(fb.ALLOWED_HOSTS[0])
        for url in ("http://downloads.invalid/x", "ftp://downloads.invalid/x", "file:///nothing"):
            with self.assertRaises(urllib.error.URLError, msg=url):
                opener.open(urllib.request.Request(url), timeout=1)

    def test_a_redirect_to_another_host_or_scheme_is_refused(self):
        handler = fb.SameHostRedirect(HOST)
        request = urllib.request.Request(f"https://{HOST}/a.brushset", headers={"User-Agent": "t"})
        for target in ("https://elsewhere.invalid/a.brushset", f"http://{HOST}/a.brushset",
                       f"https://{HOST}:8443/a.brushset", f"https://{HOST}@elsewhere.invalid/a",
                       "ftp://elsewhere.invalid/a"):
            with self.assertRaises(fb.Refused, msg=target):
                handler.redirect_request(request, io.BytesIO(), 302, "Found", Headers(), target)

    def test_a_redirect_that_stays_on_the_host_is_followed(self):
        handler = fb.SameHostRedirect(HOST)
        request = urllib.request.Request(f"https://{HOST}/a.brushset", headers={"User-Agent": "t"})
        target = f"https://{HOST}/moved/a.brushset"
        followed = handler.redirect_request(request, io.BytesIO(), 302, "Found", Headers(), target)
        self.assertEqual(followed.full_url, target)

    def test_a_refused_redirect_is_not_retried(self):
        self.assertTrue(issubclass(fb.UpstreamChanged, fb.Refused))
        self.assertFalse(issubclass(fb.Refused, (OSError, urllib.error.URLError)))


# ── verify, and pointer files ────────────────────────────────────────────────

class Verify(FetchCase):
    def fetched(self):
        self.run_main("fetch", "--confirm", opener=self.good())

    def test_everything_here_and_correct_is_exit_0_and_opens_nothing(self):
        self.fetched()
        before = fixtures.tree_digest(self.library)
        opener = FakeOpener()
        code, out, err = self.run_main("verify", opener=opener)
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertIn("2 of 2 files are present and match their pins", out)
        self.assertIn(f"{sum(len(body) for body in self.bodies.values()):,} bytes on disk", out)
        self.assertEqual(opener.requests, [])
        self.assertEqual(fixtures.tree_digest(self.library), before)

    def test_a_missing_file_is_exit_1(self):
        self.fetched()
        self.dest("demo-two").unlink()
        code, out, _ = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("MISSING", out)
        self.assertIn("1 of 2", out)

    def test_a_changed_byte_is_exit_1_and_its_md5_is_shown(self):
        self.fetched()
        body = bytearray(self.bodies["demo-one"])
        body[len(body) // 2] ^= 0xFF
        self.dest("demo-one").write_bytes(bytes(body))
        code, out, _ = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("DIFFERS", out)
        self.assertIn(md5(bytes(body)), out)

    def test_nothing_fetched_yet_is_exit_1(self):
        code, out, _ = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("0 of 2", out)

    def test_a_file_the_manifest_does_not_name_is_pointed_out(self):
        self.fetched()
        (self.library / "official" / PACK / "stray.brushset").write_bytes(b"stray")
        (self.library / "official" / PACK / "demo-one.brushset.part").write_bytes(b"half")
        code, out, _ = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn(f"official/{PACK}/stray.brushset", out)
        self.assertIn(f"official/{PACK}/demo-one.brushset.part", out)
        self.assertNotIn("unexpected  official/fetch_log.jsonl", out)

    def test_a_git_lfs_pointer_is_exit_2_with_what_to_run(self):
        self.fetched()
        self.dest("demo-one").write_bytes(fixtures.LFS_POINTER)
        code, out, err = self.run_main("verify")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("git lfs pull", err)

    def test_fetch_never_overwrites_a_pointer(self):
        self.dest("demo-one").parent.mkdir(parents=True)
        self.dest("demo-one").write_bytes(fixtures.LFS_POINTER)
        opener = self.good()
        code, _, err = self.run_main("fetch", "--confirm", opener=opener)
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("git lfs pull", err)
        self.assertEqual(opener.requests, [])
        self.assertEqual(self.dest("demo-one").read_bytes(), fixtures.LFS_POINTER)

    def test_a_file_over_the_plain_blob_limit_is_named(self):
        self.fetched()
        with mock.patch.object(fb, "PLAIN_BLOB_LIMIT", 10):
            _, out, _ = self.run_main("verify")
        self.assertIn("Git LFS only", out)
        self.assertEqual(fb.PLAIN_BLOB_LIMIT, 95 * 1000 * 1000)


# ── the command line ─────────────────────────────────────────────────────────

class CommandLine(FetchCase):
    def test_the_verbs_and_flags_are_the_contracts(self):
        parser = fb.build_parser()
        fetch = parser.parse_args(["fetch", "--only", "p5", "--delay", "3", "--accept-upstream", "--confirm"])
        self.assertEqual((fetch.verb, fetch.only, fetch.delay, fetch.accept_upstream, fetch.confirm),
                         ("fetch", "p5", 3.0, True, True))
        plain = parser.parse_args(["fetch"])
        self.assertEqual((plain.only, plain.delay, plain.accept_upstream, plain.confirm),
                         (None, fb.DEFAULT_DELAY, False, False))
        self.assertEqual(parser.parse_args(["list"]).verb, "list")
        self.assertEqual(parser.parse_args(["verify"]).verb, "verify")

    def test_usage_errors_are_exit_2(self):
        for argv in ([], ["download"], ["fetch", "--delay", "-1"], ["fetch", "--delay", "soon"],
                     ["fetch", "--dry-run"], ["list", "extra"]):
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                fb.main(argv + ["--library", str(self.library)])
            self.assertEqual(raised.exception.code, bc.EXIT_USAGE, argv)

    def test_the_root_flags_work_before_and_after_the_verb(self):
        root = self.tmp / "data"
        (root / "library").mkdir(parents=True)
        (root / "library" / "sources.json").write_bytes((self.library / "sources.json").read_bytes())
        for argv in (["--root", str(root), "list"], ["list", "--root", str(root)],
                     ["--library", str(root / "library"), "list"], ["list", "--library", str(root / "library")]):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = fb.main(argv)
            self.assertEqual(code, bc.EXIT_OK, argv)
            self.assertIn(str(root / "library" / "official"), out.getvalue(), argv)

    def test_the_environment_names_the_library_too(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {bc.ENV_LIBRARY: str(self.library)}), contextlib.redirect_stdout(out):
            code = fb.main(["list"])
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn(str(self.library / "official"), out.getvalue())

    def test_it_runs_isolated_from_any_directory(self):
        elsewhere = fixtures.temp_dir(self)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "list", "--library", str(self.library)],
                              cwd=str(elsewhere), env=env, capture_output=True, timeout=120)
        self.assertEqual(done.returncode, bc.EXIT_OK, done.stderr.decode("utf-8", "replace"))
        text = done.stdout.decode("utf-8")
        self.assertIn(f"{PACK}/demo-one", text)
        self.assertIn("2 missing", text)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_the_module_says_what_the_spec_says(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml is not installed")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        declared = spec["cli"]["scripts"]["pipeline/fetch_base_library.py"]
        parser = fb.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), declared["verbs"])
        fetch_flags = {flag for action in verbs.choices["fetch"]._actions for flag in action.option_strings}
        self.assertTrue(set(declared["flags"]["fetch"]) <= fetch_flags)
        self.assertEqual(spec["runtime"]["network"]["script"], "pipeline/fetch_base_library.py")
        self.assertEqual(spec["runtime"]["network"]["scheme"], "https")
        self.assertEqual(spec["commit_policy"]["limits"]["plain_blob_mb"] * 1000 * 1000, fb.PLAIN_BLOB_LIMIT)
        self.assertEqual(fb.SOURCES_SCHEMA, spec["library"]["sources_schema"])
        self.assertEqual(f"library/{fb.OFFICIAL_DIR}", spec["layout"]["library_official"])


if __name__ == "__main__":
    unittest.main()
