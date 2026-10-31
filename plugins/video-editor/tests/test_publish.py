"""`ve publish`: safety rules, credential handling, OAuth, and every platform against a faked network."""
import _paths  # noqa: F401  (puts src/ on sys.path)

import base64
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from unittest import mock

from videoeditor.publish import handoff, ledger, net, oauth, package, secrets, service
from videoeditor.publish.base import Publisher, Result, Spec
from videoeditor.publish.errors import ApiError, AuthError, NotAllowed, PublishError, ValidationFailed
from videoeditor.publish.platforms import NAMES, get
from videoeditor.publish.platforms import bluesky, instagram, linkedin, mastodon, tiktok, x, youtube

TOKEN = json.dumps({"access_token": "ACCESS", "refresh_token": None, "expires_at": None, "scope": None, "extra": {}})


# ------------------------------------------------------------------ helpers


class Resp:
    def __init__(self, status=200, body=None, headers=None, text=None):
        self.status_code, self._body, self.headers = status, body, headers or {}
        self.text = text if text is not None else json.dumps(body)

    def json(self):
        return self._body


class FakeNet:
    """Replaces net.request. Routes are (METHOD, url-substring) -> Resp or a callable(kwargs) -> Resp, or a list
    consumed in order. Records every call."""

    def __init__(self, routes):
        # accept (METHOD, fragment, response) or ((METHOD, fragment), response)
        self.routes = [(r[0], r[1], r[2]) if len(r) == 3 else (r[0][0], r[0][1], r[1]) for r in routes]
        self.calls = []

    def __call__(self, platform, method, url, **kw):
        # read file-like bodies now, as the real client would, so tests can inspect what was sent
        body = kw.get("data")
        if hasattr(body, "read"):
            kw = dict(kw, data=body.read())
        self.calls.append({"method": method, "url": url, **kw})
        for m, frag, res in self.routes:
            if m == method and frag in url:
                if isinstance(res, list):
                    r = res.pop(0) if len(res) > 1 else res[0]
                else:
                    r = res(kw) if callable(res) else res
                ok = kw.get("ok", (200, 201, 202, 204, 206))
                if r.status_code not in ok:
                    raise ApiError(platform, r.status_code, (r.text or "")[:200])
                return r
        raise AssertionError(f"unrouted request: {method} {url}")

    def find(self, method, frag):
        return [c for c in self.calls if c["method"] == method and frag in c["url"]]


_VIDEO_CACHE: dict = {}


def make_video(td, name="v.mp4", seconds=2, size="1080x1920", extra=()):
    p = Path(td) / name
    key = (Path(name).suffix, seconds, size, tuple(extra))
    if key in _VIDEO_CACHE:                      # encoding is the slow part; reuse the same bytes
        p.write_bytes(_VIDEO_CACHE[key])
        return p
    _make_video(p, seconds, size, extra)
    _VIDEO_CACHE[key] = p.read_bytes()
    return p


def _make_video(p, seconds, size, extra):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc=s={size}:r=25:d={seconds}",
                    "-f", "lavfi", "-i", "sine=d=%d" % seconds, "-shortest", "-pix_fmt", "yuv420p", *extra, str(p)], check=True)


def make_pkg(td, **kw):
    video = make_video(td)
    args = dict(caption="Hello world", tags=["editing"], platforms=["youtube"], made_for_kids=False)
    args.update(kw)
    return package.build(video, **args)


class Env(unittest.TestCase):
    """Each test gets a clean credential environment (no real keyring, no real network)."""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.dir = Path(self.td.name)
        clean = {k: v for k, v in os.environ.items() if not k.startswith("VE_")}
        self.env = mock.patch.dict(os.environ, clean, clear=True)
        self.env.start()
        self.nokeyring = mock.patch.object(secrets, "_keyring", return_value=None)
        self.nokeyring.start()
        self.sleep = mock.patch("time.sleep")
        self.sleep.start()

    def tearDown(self):
        self.sleep.stop(); self.nokeyring.stop(); self.env.stop(); self.td.cleanup()

    def fake(self, routes):
        f = FakeNet(routes)
        p = mock.patch.object(net, "request", f)
        p.start()
        self.addCleanup(p.stop)
        return f


# ------------------------------------------------------------------ package, ledger, secrets, net


class PackageAndLedger(Env):
    def test_roundtrip_and_text(self):
        pkg = make_pkg(self.dir, overrides={"x": {"caption": "short"}})
        package.save(pkg, self.dir / "edit")
        loaded = package.load(self.dir / "edit")
        self.assertEqual(loaded.full_text("youtube"), "Hello world\n\n#editing")
        self.assertEqual(loaded.full_text("x"), "short\n\n#editing")          # override wins; never one identical blast
        self.assertEqual(loaded.info["orientation"], "vertical")
        with self.assertRaises(FileNotFoundError):
            package.load(self.dir / "nope")

    def test_fingerprint_follows_content_not_name(self):
        a = make_pkg(self.dir)
        copy = self.dir / "renamed.mp4"
        copy.write_bytes(Path(a.video).read_bytes())
        b = package.build(copy, "x")
        self.assertEqual(a.fingerprint(), b.fingerprint())

    def test_ledger_key_and_lookup_and_no_secrets(self):
        k1 = ledger.idempotency_key("fp", "x", "public", "text")
        self.assertEqual(k1, ledger.idempotency_key("fp", "x", "public", "text"))
        self.assertNotEqual(k1, ledger.idempotency_key("fp", "x", "draft", "text"))
        ledger.record(self.dir, key=k1, platform="x", mode="public", status="failed", note="boom")
        self.assertIsNone(ledger.find_success(self.dir, k1))                  # a failure never blocks a retry
        ledger.record(self.dir, key=k1, platform="x", mode="public", status="ok", url="https://x/1")
        self.assertEqual(ledger.find_success(self.dir, k1)["url"], "https://x/1")
        raw = (self.dir / ledger.FILE_NAME).read_text(encoding="utf-8")
        self.assertNotIn("text", [json.loads(l).get("caption") for l in raw.splitlines()])


class Secrets(Env):
    def test_env_vars_and_no_file_fallback(self):
        os.environ["VE_MASTODON_TOKEN"] = "abc"
        self.assertEqual(secrets.get("mastodon", "token"), "abc")
        before = set(os.listdir(self.dir))
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            with self.assertRaises(RuntimeError) as cm:
                secrets.set("mastodon", "token", "zzz")
        finally:
            os.chdir(cwd)
        self.assertIn("VE_MASTODON_TOKEN", str(cm.exception))
        self.assertEqual(set(os.listdir(self.dir)), before)                  # nothing written anywhere
        self.assertFalse(secrets.delete("mastodon", "token"))

    def test_keyring_used_when_available(self):
        store = {}
        kr = mock.Mock()
        kr.set_password.side_effect = lambda s, k, v: store.__setitem__((s, k), v)
        kr.get_password.side_effect = lambda s, k: store.get((s, k))
        with mock.patch.object(secrets, "_keyring", return_value=kr):
            secrets.set_json("youtube", "token", {"a": 1})
            self.assertEqual(secrets.get_json("youtube", "token"), {"a": 1})
        self.assertEqual(list(store)[0][0], secrets.SERVICE)

    def test_plaintext_and_null_keyring_backends_are_refused(self):
        import sys
        import types

        for mod, name in (("keyrings.alt.file", "PlaintextKeyring"), ("keyring.backends.null", "Keyring"), ("some.pkg", "EncryptedFileKeyring")):
            cls = type(name, (), {})
            cls.__module__ = mod
            fake_kr = types.ModuleType("keyring")
            fake_kr.get_keyring = lambda c=cls: c()
            fail_mod = types.ModuleType("keyring.backends.fail")
            fail_mod.Keyring = type("FailKeyring", (), {})
            backends = types.ModuleType("keyring.backends")
            backends.fail = fail_mod
            with self.nokeyring_off(), mock.patch.dict(sys.modules, {"keyring": fake_kr, "keyring.backends": backends,
                                                                      "keyring.backends.fail": fail_mod}):
                expected_none = mod != "some.pkg"
                self.assertEqual(secrets._keyring() is None, expected_none, (mod, name))

    def nokeyring_off(self):
        class Ctx:
            def __enter__(s):
                self.nokeyring.stop()

            def __exit__(s, *a):
                self.nokeyring.start()

        return Ctx()

    def test_no_source_file_writes_secrets(self):
        """Only package.py and ledger.py may write files in the publish package, and neither handles credentials."""
        root = Path(__file__).parents[1] / "src" / "videoeditor" / "publish"
        writers = set()
        for p in root.rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            if re.search(r"write_text|write_bytes|open\([^)]*[\"'][wax]b?[\"']", text):
                writers.add(p.name)
        self.assertEqual(writers, {"package.py", "ledger.py"})


class NetRetry(unittest.TestCase):
    def rq(self, statuses):
        calls = iter(statuses)

        def fake(method, url, timeout=None, **kw):
            s = next(calls)
            return Resp(s[0], {}, s[1] if len(s) > 1 else {}, text="body")

        return mock.patch("requests.request", side_effect=fake)

    def test_retries_429_with_retry_after_then_succeeds(self):
        sleeps = []
        with self.rq([(429, {"Retry-After": "7"}), (200,)]) as m:
            r = net.request("p", "GET", "http://x", sleep=sleeps.append)
        self.assertEqual((r.status_code, m.call_count, sleeps), (200, 2, [7.0]))

    def test_gives_up_with_redacted_api_error(self):
        sleeps = []
        with self.rq([(500,), (500,), (500,)]):
            with self.assertRaises(ApiError) as cm:
                net.request("p", "GET", "http://x", retries=2, sleep=sleeps.append)
        self.assertEqual((cm.exception.status, len(sleeps)), (500, 2))

    def test_client_errors_are_not_retried(self):
        with self.rq([(403,)]) as m:
            with self.assertRaises(ApiError):
                net.request("p", "GET", "http://x", sleep=lambda s: None)
        self.assertEqual(m.call_count, 1)

    def test_connection_errors_never_leak_the_url_query(self):
        import requests

        boom = requests.ConnectionError("HTTPSConnectionPool: /media?access_token=SECRETTOKEN&x=1")
        with mock.patch("requests.request", side_effect=boom):
            with self.assertRaises(PublishError) as cm:
                net.request("instagram", "GET", "https://graph.example.com/v26.0/C1?access_token=SECRETTOKEN", retries=1,
                            sleep=lambda s: None)
        self.assertNotIn("SECRETTOKEN", str(cm.exception))
        self.assertIn("graph.example.com", str(cm.exception))

    def test_redact(self):
        self.assertEqual(net.redact("token=SECRET1 and SECRET2", ["SECRET1", "SECRET2", ""]), "token=*** and ***")


# ------------------------------------------------------------------ the safety rules (service.py)


class FakePublisher(Publisher):
    def __init__(self, modes=("draft", "public"), cost=None, issues=None):
        self.spec = Spec(name="fake", title="Fake", modes=modes, cost_note=cost)
        self.sent, self._issues = [], issues or []

    def validate(self, pkg):
        return list(self._issues)

    def plan(self, pkg, mode):
        return [f"would send as {mode}"]

    def send(self, pkg, mode, *, idempotency_key=None):
        self.sent.append((mode, idempotency_key))
        return Result("fake", mode, "ok" if mode == "public" else "draft", id="1")


class SafetyRules(Env):
    def setUp(self):
        super().setUp()
        self.pkg = make_pkg(self.dir)
        self.edit = self.dir / "edit"

    def go(self, pub, **kw):
        kw.setdefault("confirm", True)
        return service.send(self.pkg, "fake", edit_dir=self.edit, publisher=pub, **kw)

    def test_no_confirmation_means_no_network(self):
        pub = FakePublisher()
        with self.assertRaises(NotAllowed):
            self.go(pub, confirm=False)
        self.assertEqual(pub.sent, [])

    def test_default_is_draft_never_public(self):
        pub = FakePublisher()
        self.assertEqual(self.go(pub).mode, "draft")
        self.assertEqual(pub.sent[0][0], "draft")

    def test_public_needs_explicit_opt_in(self):
        pub = FakePublisher()
        self.assertEqual(self.go(pub, public=True).mode, "public")

    def test_platform_without_draft_refuses_unless_public(self):
        pub = FakePublisher(modes=("public",))
        with self.assertRaises(NotAllowed) as cm:
            self.go(pub)
        self.assertIn("--public", str(cm.exception))
        self.assertEqual(pub.sent, [])
        self.assertEqual(self.go(pub, public=True).mode, "public")

    def test_cost_needs_acknowledgement(self):
        pub = FakePublisher(modes=("public",), cost="$$")
        with self.assertRaises(NotAllowed):
            self.go(pub, public=True)
        self.assertEqual(pub.sent, [])
        self.go(pub, public=True, accept_cost=True)

    def test_validation_errors_block_but_warnings_do_not(self):
        from videoeditor.publish.base import Issue

        with self.assertRaises(ValidationFailed):
            self.go(FakePublisher(issues=[Issue("error", "too long")]))
        self.go(FakePublisher(issues=[Issue("warn", "meh")]))

    def test_duplicate_blocked_until_forced_and_failures_do_not_count(self):
        pub = FakePublisher()
        self.go(pub)
        with self.assertRaises(NotAllowed) as cm:
            self.go(pub)
        self.assertIn("already sent", str(cm.exception))
        self.go(pub, force=True)
        self.assertEqual(len(pub.sent), 2)
        self.assertEqual(pub.sent[0][1], pub.sent[1][1])                      # same idempotency key both times

        flaky = FakePublisher(modes=("public",))
        flaky.send = mock.Mock(side_effect=[PublishError("network down"), Result("fake", "public", "ok")])
        with self.assertRaises(PublishError):
            self.go(flaky, public=True)
        self.go(flaky, public=True)                                           # retry after a failure is allowed
        self.assertEqual([e["status"] for e in ledger.read(self.edit)][-2:], ["failed", "ok"])

    def test_no_real_platform_defaults_to_public(self):
        for name in NAMES:
            pub = get(name)
            try:
                mode = service.resolve_mode(pub, public=False)
            except NotAllowed:
                continue
            self.assertEqual(mode, "draft", name)

    def test_x_and_bluesky_are_public_only_and_x_costs_money(self):
        self.assertEqual(get("x").spec.modes, ("public",))
        self.assertEqual(get("bluesky").spec.modes, ("public",))
        self.assertIsNotNone(get("x").spec.cost_note)
        for n in ("x", "bluesky"):
            with self.assertRaises(NotAllowed):
                service.send(self.pkg, n, edit_dir=self.edit, confirm=True)


class Handoff(Env):
    def test_checklist_has_file_caption_and_disclosures(self):
        pkg = make_pkg(self.dir, ai_generated=True, branded_content=True, title="My title")
        text = handoff.checklist(pkg, "tiktok")
        for needle in (pkg.video, "Hello world", "#editing", "AI-generated", "branded", "tiktok.com"):
            self.assertIn(needle, text)
        self.assertIn("mastodon.example", handoff.checklist(pkg, "mastodon", instance="https://mastodon.example"))


class GenericValidation(Env):
    def test_soft_limits_warn_hard_limits_block(self):
        long = make_pkg(self.dir, caption="a" * 400)
        issues = {i.severity for i in get("bluesky").validate(long)}
        self.assertEqual(issues, {"warn"})                                    # 300 graphemes is not on the official page
        self.assertIn("error", {i.severity for i in get("tiktok").validate(make_pkg(self.dir, caption="a" * 2500))})

    def test_orientation_extension_and_duration(self):
        wide = package.build(make_video(self.dir, "wide.mp4", size="1280x720"), "x")
        msgs = [i.message for i in get("tiktok").validate(wide)]
        self.assertTrue(any("vertical" in m for m in msgs))
        short = package.build(make_video(self.dir, "short.mp4", seconds=1), "x")
        self.assertTrue(any("at least 3s" in i.message for i in get("instagram").validate(short)))
        mov = package.build(make_video(self.dir, "c.mov"), "x")
        self.assertTrue(any("accepts" in i.message for i in get("bluesky").validate(mov)))


# ------------------------------------------------------------------ OAuth


class OAuth(Env):
    def cfg(self, **kw):
        base = dict(platform="p", auth_url="https://auth.example/authorize", token_url="https://auth.example/token",
                    client_id="CID", scopes=["a", "b"])
        base.update(kw)
        return oauth.OAuthConfig(**base)

    def test_pkce_pair_is_s256(self):
        v, c = oauth.pkce_pair()
        self.assertEqual(c, base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode())
        self.assertGreaterEqual(len(v), 43)

    def test_auth_url_variants(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(oauth.build_auth_url(self.cfg(), "http://127.0.0.1:1/cb", "S", "CH")).query)
        self.assertEqual((q["client_id"], q["scope"], q["code_challenge_method"]), (["CID"], ["a b"], ["S256"]))
        t = tiktok.oauth_config("KEY", "SEC")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(oauth.build_auth_url(t, "http://x/", "S", None)).query)
        self.assertEqual((q["client_key"], q["scope"]), (["KEY"], ["user.info.basic,video.upload"]))
        self.assertNotIn("code_challenge", q)                                 # TikTok documents PKCE for mobile/desktop only
        self.assertFalse(linkedin.oauth_config("a", "b").pkce)

    def test_token_exchange_client_auth_placement(self):
        f = self.fake([("POST", "token", Resp(200, {"access_token": "T", "refresh_token": "R", "expires_in": 3600}))])
        tok = oauth.exchange_code(self.cfg(client_secret="SEC"), "CODE", "http://r/", "VER")
        self.assertEqual((tok.access_token, tok.refresh_token), ("T", "R"))
        body = f.calls[0]["data"]
        self.assertEqual((body["code_verifier"], body["client_secret"], body["client_id"]), ("VER", "SEC", "CID"))
        f2 = self.fake([("POST", "token", Resp(200, {"access_token": "T"}))])
        oauth.exchange_code(self.cfg(client_secret="SEC", token_auth="basic"), "C", "http://r/", None)
        self.assertEqual(f2.calls[0]["auth"], ("CID", "SEC"))
        self.assertNotIn("client_secret", f2.calls[0]["data"])

    def test_refresh_keeps_old_refresh_token_and_autorefreshes(self):
        self.fake([("POST", "token", Resp(200, {"access_token": "NEW", "expires_in": 60}))])
        old = oauth.TokenSet("OLD", "REFRESH", time.time() - 10)
        new = oauth.refresh(self.cfg(), old)
        self.assertEqual((new.access_token, new.refresh_token), ("NEW", "REFRESH"))
        os.environ["VE_P_TOKEN"] = json.dumps({"access_token": "OLD", "refresh_token": "REFRESH", "expires_at": time.time() - 10,
                                               "scope": None, "extra": {}})
        self.assertEqual(oauth.access_token(self.cfg()), "NEW")               # env creds cannot be re-saved: still works
        os.environ["VE_P_TOKEN"] = json.dumps({"access_token": "OLD", "refresh_token": None, "expires_at": time.time() - 10,
                                               "scope": None, "extra": {}})
        with self.assertRaises(AuthError):
            oauth.access_token(self.cfg())
        del os.environ["VE_P_TOKEN"]
        with self.assertRaises(AuthError):
            oauth.access_token(self.cfg())

    def test_loopback_flow_checks_state_and_exchanges_code(self):
        printed = []
        self.fake([("POST", "token", Resp(200, {"access_token": "T"}))])
        result = {}

        def run():
            result["tok"] = oauth.loopback_authorize(self.cfg(), timeout=10, say=printed.append)

        th = threading.Thread(target=run)
        th.start()
        for _ in range(400):
            if printed:
                break
            time.sleep(0) if False else threading.Event().wait(0.05)
        url = re.search(r"https://auth\.example/authorize\?\S+", printed[0]).group(0)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        cb = q["redirect_uri"][0] + "?" + urllib.parse.urlencode({"code": "CODE", "state": q["state"][0]})
        urllib.request.urlopen(cb, timeout=5).read()
        th.join(10)
        self.assertEqual(result["tok"].access_token, "T")
        self.assertTrue(q["redirect_uri"][0].startswith("http://127.0.0.1:"))  # loopback only

    def test_loopback_ignores_stray_requests_before_the_callback(self):
        printed, result = [], {}
        self.fake([("POST", "token", Resp(200, {"access_token": "T"}))])
        th = threading.Thread(target=lambda: result.update(tok=oauth.loopback_authorize(self.cfg(), timeout=10, say=printed.append)))
        th.start()
        for _ in range(400):
            if printed:
                break
            threading.Event().wait(0.05)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(re.search(r"https://auth\.example/authorize\?\S+", printed[0]).group(0)).query)
        base = q["redirect_uri"][0].rsplit("/callback", 1)[0]
        for stray in ("/favicon.ico", "/callback", "/other?code=evil"):    # none of these may end the flow
            try:
                urllib.request.urlopen(base + stray, timeout=5)
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)
        self.assertTrue(th.is_alive())
        urllib.request.urlopen(q["redirect_uri"][0] + "?" + urllib.parse.urlencode({"code": "C", "state": q["state"][0]}), timeout=5).read()
        th.join(10)
        self.assertEqual(result["tok"].access_token, "T")

    def test_loopback_rejects_wrong_state(self):
        printed, err = [], {}

        def run():
            try:
                oauth.loopback_authorize(self.cfg(), timeout=10, say=printed.append)
            except AuthError as e:
                err["e"] = e

        th = threading.Thread(target=run)
        th.start()
        for _ in range(400):
            if printed:
                break
            threading.Event().wait(0.05)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(re.search(r"https://\S+", printed[0]).group(0)).query)
        urllib.request.urlopen(q["redirect_uri"][0] + "?code=X&state=WRONG", timeout=5).read()
        th.join(10)
        self.assertIn("state mismatch", str(err["e"]))

    def test_manual_flow(self):
        self.fake([("POST", "token", Resp(200, {"access_token": "T"}))])
        seen = {}

        def ask(prompt):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(re.search(r"https://auth\S+", seen["say"]).group(0)).query)
            return f"https://app.example/cb?code=C1&state={q['state'][0]}"

        tok = oauth.manual_authorize(self.cfg(), "https://app.example/cb", ask=ask, say=lambda s: seen.update(say=s))
        self.assertEqual(tok.access_token, "T")
        with self.assertRaises(AuthError):
            oauth.manual_authorize(self.cfg(), "https://app.example/cb", ask=lambda p: "https://app.example/cb?code=C&state=BAD",
                                   say=lambda s: None)
        tok = oauth.manual_authorize(self.cfg(), "https://app.example/cb", ask=lambda p: "JUSTACODE", say=lambda s: None)
        self.assertEqual(tok.access_token, "T")

    def test_init_without_keyring_does_not_store_and_prints_only_on_request(self):
        self.fake([("POST", "token", Resp(200, {"access_token": "T", "refresh_token": "R"}))])
        said = []
        answers = iter(["CID", "n"])          # client id, then decline to print the token
        with mock.patch.object(oauth, "loopback_authorize", return_value=oauth.TokenSet("T", "R")):
            msg = oauth.run_init("p", lambda c, s: self.cfg(client_id=c), ask=lambda p: next(answers),
                                 ask_secret=lambda p: "", say=said.append)
        self.assertIn("not stored", msg)
        self.assertFalse(any("export" in s for s in said))


# ------------------------------------------------------------------ platforms


class Mastodon(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_MASTODON_INSTANCE="https://masto.example", VE_MASTODON_TOKEN="TOK")
        self.pkg = make_pkg(self.dir)

    def routes(self, **over):
        inst = {"configuration": {"statuses": {"max_characters": 500}, "media_attachments": {"video_size_limit": 10**9}}}
        r = [("GET", "/api/v2/instance", Resp(200, inst)),
             ("POST", "/api/v2/media", Resp(202, {"id": "M1", "url": None})),
             ("GET", "/api/v1/media/M1", [Resp(206, {}), Resp(200, {"id": "M1", "url": "u"})]),
             ("POST", "/api/v1/statuses", Resp(200, {"id": "S1", "url": "https://masto.example/@me/1"}))]
        return [(k, v) for k, v in {(m, f): res for m, f, res in r}.items()] if not over else over["routes"]

    def test_draft_is_followers_only_with_idempotency_key(self):
        f = self.fake(self.routes())
        res = service.send(self.pkg, "mastodon", edit_dir=self.dir / "e", confirm=True)
        st = f.find("POST", "/api/v1/statuses")[0]
        self.assertEqual((st["json"]["visibility"], st["json"]["media_ids"], res.status), ("private", ["M1"], "draft"))
        self.assertIn("Idempotency-Key", st["headers"])
        self.assertEqual(len(f.find("GET", "/api/v1/media/M1")), 2)           # polled 206 then 200
        self.assertEqual(f.find("POST", "/api/v2/media")[0]["headers"]["Authorization"], "Bearer TOK")

    def test_public_and_instance_limits(self):
        f = self.fake(self.routes())
        service.send(self.pkg, "mastodon", edit_dir=self.dir / "e", confirm=True, public=True)
        self.assertEqual(f.find("POST", "/api/v1/statuses")[0]["json"]["visibility"], "public")
        long = make_pkg(self.dir, caption="a" * 600)
        self.fake(self.routes())
        with self.assertRaises(PublishError) as cm:
            mastodon.PUBLISHER().send(long, "draft")
        self.assertIn("this instance allows 500", str(cm.exception))

    def test_unconfigured(self):
        del os.environ["VE_MASTODON_TOKEN"]
        with self.assertRaises(AuthError):
            service.send(self.pkg, "mastodon", edit_dir=self.dir / "e", confirm=True)


class Bluesky(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_BLUESKY_IDENTIFIER="me.bsky.social", VE_BLUESKY_APP_PASSWORD="APP")
        self.pkg = make_pkg(self.dir, caption="Hello #editing", tags=[])

    def routes(self, job_states):
        sess = {"did": "did:plc:abc", "accessJwt": "JWT", "handle": "me.bsky.social",
                "didDoc": {"service": [{"id": "#atproto_pds", "serviceEndpoint": "https://pds.example.com"}]}}
        blob = {"$type": "blob", "ref": {"$link": "bafy"}, "mimeType": "video/mp4", "size": 1}
        return [("POST", "createSession", Resp(200, sess)),
                ("GET", "getServiceAuth", Resp(200, {"token": "SVC"})),
                ("GET", "getUploadLimits", Resp(200, {"canUpload": True})),
                ("POST", "uploadVideo", Resp(200, {"jobStatus": {"jobId": "J1", "did": "did:plc:abc", "state": "JOB_STATE_CREATED"}})),
                ("GET", "getJobStatus", job_states),
                ("POST", "createRecord", Resp(200, {"uri": "at://did:plc:abc/app.bsky.feed.post/3kabc", "cid": "c"}))], blob

    def test_full_flow(self):
        blob = {"$type": "blob", "ref": {"$link": "bafy"}, "mimeType": "video/mp4", "size": 1}
        routes, _ = self.routes([Resp(200, {"jobStatus": {"jobId": "J1", "did": "d", "state": "JOB_STATE_ENCODING"}}),
                                 Resp(200, {"jobStatus": {"jobId": "J1", "did": "d", "state": "JOB_STATE_COMPLETED", "blob": blob}})])
        f = self.fake(routes)
        res = service.send(self.pkg, "bluesky", edit_dir=self.dir / "e", confirm=True, public=True)
        self.assertEqual(res.url, "https://bsky.app/profile/did:plc:abc/post/3kabc")
        auth = [c["url"] for c in f.find("GET", "getServiceAuth")]
        self.assertTrue(any("aud=did%3Aweb%3Apds.example.com" in u and "lxm=com.atproto.repo.uploadBlob" in u for u in auth))
        self.assertTrue(any("aud=did%3Aweb%3Avideo.bsky.app" in u and "getUploadLimits" in u for u in auth))
        up = f.find("POST", "uploadVideo")[0]
        self.assertEqual((up["headers"]["Content-Type"], up["headers"]["Authorization"], up["params"]["did"]),
                         ("video/mp4", "Bearer SVC", "did:plc:abc"))
        rec = f.find("POST", "createRecord")[0]["json"]
        self.assertTrue(f.find("POST", "createRecord")[0]["url"].startswith("https://pds.example.com/"))
        self.assertEqual(rec["record"]["embed"]["$type"], "app.bsky.embed.video")
        self.assertEqual(rec["record"]["embed"]["video"], blob)
        self.assertEqual(rec["record"]["embed"]["aspectRatio"], {"width": 1080, "height": 1920})
        self.assertEqual(rec["record"]["facets"][0]["features"][0]["tag"], "editing")
        self.assertEqual(rec["collection"], "app.bsky.feed.post")

    def test_hashtag_facets_use_utf8_byte_offsets(self):
        facets = bluesky.hashtag_facets("héllo #tag and #two")
        self.assertEqual([f["features"][0]["tag"] for f in facets], ["tag", "two"])
        text = "héllo #tag and #two".encode()
        self.assertEqual(text[facets[0]["index"]["byteStart"]:facets[0]["index"]["byteEnd"]], b"#tag")

    def test_failed_processing_is_reported_and_nothing_is_posted(self):
        routes, _ = self.routes([Resp(200, {"jobStatus": {"jobId": "J1", "did": "d", "state": "JOB_STATE_FAILED",
                                                          "error": "bad", "failureCode": "validation_failure"}})])
        f = self.fake(routes)
        with self.assertRaises(PublishError) as cm:
            service.send(self.pkg, "bluesky", edit_dir=self.dir / "e", confirm=True, public=True)
        self.assertIn("validation_failure", str(cm.exception))
        self.assertEqual(f.find("POST", "createRecord"), [])

    def test_upload_limit_blocks(self):
        routes, _ = self.routes([Resp(200, {})])
        routes[2] = ("GET", "getUploadLimits", Resp(200, {"canUpload": False, "message": "daily limit"}))
        self.fake(routes)
        with self.assertRaises(PublishError) as cm:
            service.send(self.pkg, "bluesky", edit_dir=self.dir / "e", confirm=True, public=True)
        self.assertIn("daily limit", str(cm.exception))

    def test_pds_fallback(self):
        self.assertEqual(bluesky.pds_from_session({}, "https://bsky.social/"), "https://bsky.social")


class YouTube(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_YOUTUBE_CLIENT_ID="CID", VE_YOUTUBE_TOKEN=TOKEN)

    def test_declaration_is_required_not_defaulted(self):
        pkg = make_pkg(self.dir, made_for_kids=None)
        with self.assertRaises(ValidationFailed) as cm:
            service.send(pkg, "youtube", edit_dir=self.dir / "e", confirm=True)
        self.assertIn("made for kids", str(cm.exception))

    def test_draft_upload_private_single_chunk(self):
        pkg = make_pkg(self.dir, ai_generated=True)
        f = self.fake([("POST", "upload/youtube/v3/videos", Resp(200, {}, {"Location": "https://up.example/session"})),
                       ("PUT", "up.example", Resp(201, {"id": "VID1"}))])
        res = service.send(pkg, "youtube", edit_dir=self.dir / "e", confirm=True)
        init = f.find("POST", "upload/youtube")[0]
        md = init["json"]
        self.assertEqual((md["status"]["privacyStatus"], md["status"]["selfDeclaredMadeForKids"], md["status"]["containsSyntheticMedia"]),
                         ("private", False, True))
        self.assertEqual(init["params"], {"uploadType": "resumable", "part": "snippet,status"})
        self.assertEqual(init["headers"]["X-Upload-Content-Length"], str(pkg.info["bytes"]))
        self.assertIn("#Shorts", md["snippet"]["description"])                # vertical and short
        self.assertEqual((res.status, res.id), ("draft", "VID1"))
        put = f.find("PUT", "up.example")[0]
        self.assertEqual(put["headers"]["Content-Range"], f"bytes 0-{pkg.info['bytes'] - 1}/{pkg.info['bytes']}")

    def test_public_and_multi_chunk_ranges(self):
        pkg = make_pkg(self.dir)
        with open(pkg.video, "ab") as fh:           # pad past a few chunks; trailing bytes do not matter to the fake network
            fh.write(os.urandom(700_000))
        pkg.info["bytes"] = total = Path(pkg.video).stat().st_size
        chunk = 262144
        self.assertGreater(total, chunk * 2)
        puts = [Resp(308, {}) for _ in range(-(-total // chunk) - 1)] + [Resp(200, {"id": "VID2"})]
        f = self.fake([("POST", "upload/youtube/v3/videos", Resp(200, {}, {"Location": "https://up.example/s"})),
                       ("PUT", "up.example", puts)])
        with mock.patch.object(youtube, "CHUNK", chunk):
            res = service.send(pkg, "youtube", edit_dir=self.dir / "e", confirm=True, public=True)
        ranges = [c["headers"]["Content-Range"] for c in f.find("PUT", "up.example")]
        self.assertEqual(ranges[0], f"bytes 0-{chunk - 1}/{total}")
        self.assertEqual(ranges[-1].split("/")[0].split("-")[1], str(total - 1))
        self.assertEqual(f.find("POST", "upload/youtube")[0]["json"]["status"]["privacyStatus"], "public")
        self.assertEqual(res.status, "ok")

    def test_long_horizontal_video_warns_about_shorts(self):
        wide = package.build(make_video(self.dir, "w.mp4", size="1280x720"), "x", made_for_kids=False)
        self.assertTrue(any("Short" in i.message for i in get("youtube").validate(wide)))
        self.assertNotIn("#Shorts", youtube.YouTube().metadata(wide, "draft")["snippet"]["description"])


class LinkedIn(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_LINKEDIN_CLIENT_ID="CID", VE_LINKEDIN_TOKEN=TOKEN)
        self.pkg = make_pkg(self.dir, caption="Use *this* #tag (now)", tags=[])

    def routes(self, etag=True):
        total = self.pkg.info["bytes"]
        init = {"value": {"video": "urn:li:video:V1", "uploadToken": "UT",
                          "uploadInstructions": [{"uploadUrl": "https://up.li/1", "firstByte": 0, "lastByte": total - 1}]}}
        return [("GET", "/v2/userinfo", Resp(200, {"sub": "abc123"})),
                ("POST", "initializeUpload", Resp(200, init)),
                ("PUT", "up.li", Resp(200, {}, {"ETag": '"etag-1"'} if etag else {})),
                ("POST", "finalizeUpload", Resp(200, {})),
                ("GET", "/rest/videos/", Resp(200, {"status": "AVAILABLE"})),
                ("POST", "/rest/posts", Resp(201, {}, {"x-restli-id": "urn:li:share:99"}))]

    def test_connections_by_default_and_headers(self):
        f = self.fake(self.routes())
        res = service.send(self.pkg, "linkedin", edit_dir=self.dir / "e", confirm=True)
        post = f.find("POST", "/rest/posts")[0]
        b = post["json"]
        self.assertEqual((b["visibility"], b["lifecycleState"], b["author"]), ("CONNECTIONS", "PUBLISHED", "urn:li:person:abc123"))
        self.assertEqual(b["content"]["media"]["id"], "urn:li:video:V1")
        self.assertEqual(post["headers"]["Linkedin-Version"], linkedin.VERSION)
        self.assertEqual(post["headers"]["X-Restli-Protocol-Version"], "2.0.0")
        self.assertEqual(res.id, "urn:li:share:99")
        fin = f.find("POST", "finalizeUpload")[0]["json"]["finalizeUploadRequest"]
        self.assertEqual((fin["uploadToken"], fin["uploadedPartIds"]), ("UT", ['"etag-1"']))
        init = f.find("POST", "initializeUpload")[0]["json"]["initializeUploadRequest"]
        self.assertEqual((init["owner"], init["fileSizeBytes"]), ("urn:li:person:abc123", self.pkg.info["bytes"]))

    def test_public_and_little_format_escaping(self):
        f = self.fake(self.routes())
        service.send(self.pkg, "linkedin", edit_dir=self.dir / "e", confirm=True, public=True)
        b = f.find("POST", "/rest/posts")[0]["json"]
        self.assertEqual(b["visibility"], "PUBLIC")
        self.assertEqual(b["commentary"], r"Use \*this\* \#tag \(now\)")
        self.assertEqual(linkedin.little_escape("a|b{c}"), r"a\|b\{c\}")

    def test_missing_etag_stops_before_finalize_and_post(self):
        f = self.fake(self.routes(etag=False))
        with self.assertRaises(PublishError):
            service.send(self.pkg, "linkedin", edit_dir=self.dir / "e", confirm=True)
        self.assertEqual(f.find("POST", "finalizeUpload") + f.find("POST", "/rest/posts"), [])

    def test_person_id_override(self):
        os.environ["VE_LINKEDIN_PERSON_ID"] = "override"
        f = self.fake([r for r in self.routes() if "/v2/userinfo" not in r[1]])
        service.send(self.pkg, "linkedin", edit_dir=self.dir / "e", confirm=True)
        self.assertEqual(f.find("POST", "/rest/posts")[0]["json"]["author"], "urn:li:person:override")


class TikTok(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_TIKTOK_CLIENT_ID="KEY", VE_TIKTOK_TOKEN=TOKEN)
        self.pkg = make_pkg(self.dir, caption="Hello tiktok", tags=["fun"])

    def test_chunk_plan_rules(self):
        self.assertEqual(tiktok.chunk_plan(3_000_000), (3_000_000, 1))
        self.assertEqual(tiktok.chunk_plan(50_000_000), (50_000_000, 1))
        size, n = tiktok.chunk_plan(100 * 1024 * 1024 + 123)
        self.assertEqual((size, n), (tiktok.CHUNK, 10))                       # floor; trailing bytes join the last chunk
        self.assertGreaterEqual(size, tiktok.MIN_CHUNK)

    def test_draft_goes_to_inbox_without_a_caption_field(self):
        total = self.pkg.info["bytes"]
        f = self.fake([("POST", "inbox/video/init", Resp(200, {"data": {"publish_id": "P1", "upload_url": "https://up.tt/u"}})),
                       ("PUT", "up.tt", Resp(201, {})),
                       ("POST", "status/fetch", Resp(200, {"data": {"status": "SEND_TO_USER_INBOX"}}))])
        res = service.send(self.pkg, "tiktok", edit_dir=self.dir / "e", confirm=True)
        init = f.find("POST", "inbox/video/init")[0]["json"]
        self.assertEqual(init["source_info"], {"source": "FILE_UPLOAD", "video_size": total, "chunk_size": total, "total_chunk_count": 1})
        self.assertNotIn("post_info", init)
        put = f.find("PUT", "up.tt")[0]["headers"]
        self.assertEqual((put["Content-Range"], put["Content-Type"]), (f"bytes 0-{total - 1}/{total}", "video/mp4"))
        self.assertEqual(res.status, "draft")
        self.assertIn("Hello tiktok", res.note)                               # caption is shown for pasting
        self.assertEqual(f.calls[0]["headers"]["Authorization"], "Bearer ACCESS")

    def test_public_needs_creator_to_allow_it(self):
        self.fake([("POST", "creator_info", Resp(200, {"data": {"privacy_level_options": ["SELF_ONLY"]}}))])
        with self.assertRaises(PublishError) as cm:
            service.send(self.pkg, "tiktok", edit_dir=self.dir / "e", confirm=True, public=True)
        self.assertIn("cannot post publicly", str(cm.exception))

    def test_public_direct_post_body(self):
        self.pkg.ai_generated, self.pkg.branded_content = True, True
        f = self.fake([("POST", "creator_info", Resp(200, {"data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"],
                                                                      "max_video_post_duration_sec": 600}})),
                       ("POST", "/video/init/", Resp(200, {"data": {"publish_id": "P2", "upload_url": "https://up.tt/u"}})),
                       ("PUT", "up.tt", Resp(201, {})),
                       ("POST", "status/fetch", [Resp(200, {"data": {"status": "PROCESSING_UPLOAD"}}),
                                                  Resp(200, {"data": {"status": "PUBLISH_COMPLETE"}})])])
        res = service.send(self.pkg, "tiktok", edit_dir=self.dir / "e", confirm=True, public=True)
        pi = f.find("POST", "/video/init/")[0]["json"]["post_info"]
        self.assertEqual((pi["privacy_level"], pi["is_aigc"], pi["brand_content_toggle"], pi["title"].startswith("Hello tiktok")),
                         ("PUBLIC_TO_EVERYONE", True, True, True))
        self.assertEqual(res.status, "ok")

    def test_failed_status_raises(self):
        self.fake([("POST", "inbox/video/init", Resp(200, {"data": {"publish_id": "P1", "upload_url": "https://up.tt/u"}})),
                   ("PUT", "up.tt", Resp(201, {})),
                   ("POST", "status/fetch", Resp(200, {"data": {"status": "FAILED", "fail_reason": "duration_check_failed"}}))])
        with self.assertRaises(PublishError) as cm:
            service.send(self.pkg, "tiktok", edit_dir=self.dir / "e", confirm=True)
        self.assertIn("duration_check_failed", str(cm.exception))


class Instagram(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_INSTAGRAM_TOKEN="IGTOKEN", VE_INSTAGRAM_USER_ID="1789")
        self.pkg = make_pkg(self.dir, caption="Reel caption", tags=[])

    def routes(self, statuses):
        return [("POST", "/1789/media_publish", Resp(200, {"id": "MEDIA1"})),
                ("POST", "/1789/media", Resp(200, {"id": "C1", "uri": "https://rupload.facebook.com/ig-api-upload/v26.0/C1"})),
                ("POST", "rupload.facebook.com", Resp(200, {"success": True})),
                ("GET", "/C1", statuses)]

    def test_draft_stops_before_publish(self):
        f = self.fake(self.routes([Resp(200, {"status_code": "IN_PROGRESS"}), Resp(200, {"status_code": "FINISHED"})]))
        res = instagram.Instagram().send(self.pkg, "draft", interval=0)
        self.assertEqual((res.status, res.id), ("draft", "C1"))
        self.assertEqual(f.find("POST", "media_publish"), [])
        c = f.find("POST", "/1789/media")[0]["data"]
        self.assertEqual((c["media_type"], c["upload_type"], c["caption"]), ("REELS", "resumable", "Reel caption"))
        up = f.find("POST", "rupload.facebook.com")[0]
        self.assertEqual((up["headers"]["offset"], up["headers"]["file_size"], up["headers"]["Authorization"]),
                         ("0", str(self.pkg.info["bytes"]), "OAuth IGTOKEN"))
        for call in f.calls:                                                  # the token never rides in a URL
            self.assertNotIn("IGTOKEN", call["url"])

    def test_public_publishes_the_container(self):
        f = self.fake(self.routes([Resp(200, {"status_code": "FINISHED"})]))
        res = instagram.Instagram().send(self.pkg, "public", interval=0)
        self.assertEqual((res.status, res.id), ("ok", "MEDIA1"))
        self.assertEqual(f.find("POST", "media_publish")[0]["data"]["creation_id"], "C1")

    def test_error_and_timeout_publish_nothing(self):
        for st, word in (("ERROR", "ERROR"), ("IN_PROGRESS", "still")):
            f = self.fake(self.routes([Resp(200, {"status_code": st})]))
            with self.assertRaises(PublishError) as cm:
                instagram.Instagram().send(self.pkg, "public", interval=0, max_polls=2)
            self.assertIn(word, str(cm.exception))
            self.assertEqual(f.find("POST", "media_publish"), [])

    def test_ai_flag_and_hosted_url_variant(self):
        os.environ["VE_INSTAGRAM_VIDEO_URL"] = "https://cdn.example/v.mp4"
        self.pkg.ai_generated = True
        f = self.fake(self.routes([Resp(200, {"status_code": "FINISHED"})]))
        instagram.Instagram().send(self.pkg, "draft", interval=0)
        c = f.find("POST", "/1789/media")[0]["data"]
        self.assertEqual((c["video_url"], c["is_ai_generated"]), ("https://cdn.example/v.mp4", "true"))
        self.assertNotIn("upload_type", c)
        self.assertEqual(f.find("POST", "rupload.facebook.com"), [])


class XPlatform(Env):
    def setUp(self):
        super().setUp()
        os.environ.update(VE_X_CLIENT_ID="CID", VE_X_TOKEN=TOKEN)
        self.pkg = make_pkg(self.dir, caption="Hello X", tags=[])

    def routes(self, finalize):
        return [("POST", "/2/media/upload/initialize", Resp(200, {"data": {"id": "MID"}})),
                ("POST", "/append", Resp(204, None, text="")),
                ("POST", "/finalize", finalize),
                ("GET", "/2/media/upload", Resp(200, {"data": {"processing_info": {"state": "succeeded"}}})),
                ("POST", "/2/tweets", Resp(201, {"data": {"id": "T1", "text": "Hello X"}}))]

    def test_both_flags_are_required(self):
        for kw in ({"public": True}, {"accept_cost": True}):
            with self.assertRaises(NotAllowed):
                service.send(self.pkg, "x", edit_dir=self.dir / "e", confirm=True, **kw)

    def test_chunked_upload_then_post(self):
        self.pkg.ai_generated = True
        f = self.fake(self.routes(Resp(200, {"data": {"id": "MID", "processing_info": {"state": "pending", "check_after_secs": 1}}})))
        res = service.send(self.pkg, "x", edit_dir=self.dir / "e", confirm=True, public=True, accept_cost=True)
        init = f.find("POST", "/initialize")[0]["json"]
        self.assertEqual((init["media_type"], init["media_category"], init["total_bytes"]), ("video/mp4", "tweet_video", self.pkg.info["bytes"]))
        appends = f.find("POST", "/append")
        self.assertEqual([a["data"]["segment_index"] for a in appends], [str(i) for i in range(len(appends))])
        self.assertTrue(all(len(a["files"]["media"][1]) <= x.SEGMENT for a in appends))
        self.assertEqual(sum(len(a["files"]["media"][1]) for a in appends), self.pkg.info["bytes"])
        self.assertEqual(f.find("GET", "/2/media/upload")[0]["params"], {"command": "STATUS", "media_id": "MID"})
        tw = f.find("POST", "/2/tweets")[0]["json"]
        self.assertEqual((tw["media"], tw["made_with_ai"]), ({"media_ids": ["MID"]}, True))
        self.assertEqual(res.url, "https://x.com/i/status/T1")

    def test_processing_failure_posts_nothing(self):
        routes = self.routes(Resp(200, {"data": {"id": "MID", "processing_info": {"state": "in_progress"}}}))
        routes[3] = ("GET", "/2/media/upload", Resp(200, {"data": {"processing_info": {"state": "failed", "error": {"x": 1}}}}))
        f = self.fake(routes)
        with self.assertRaises(PublishError):
            service.send(self.pkg, "x", edit_dir=self.dir / "e", confirm=True, public=True, accept_cost=True)
        self.assertEqual(f.find("POST", "/2/tweets"), [])


# ------------------------------------------------------------------ CLI


class Cli(Env):
    def run_cli(self, *args):
        from videoeditor.publish import cli

        out, err = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
            try:
                cli.main(list(args))
                rc = 0
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue(), err.getvalue()

    def test_prepare_plan_and_refusals(self):
        video = make_video(self.dir)
        edit = str(self.dir / "edit")
        rc, out, _ = self.run_cli("prepare", "--video", str(video), "--caption", "hi", "--platforms", "youtube,bluesky,x",
                                  "--not-made-for-kids", "--edit-dir", edit)
        self.assertEqual(rc, 0)
        self.assertIn("Nothing was sent", out)
        self.assertIn("mode: draft", out)
        self.assertIn("blocked: Bluesky has no private/draft mode", out)
        self.assertIn("COST:", out)
        rc, _, err = self.run_cli("send", "--platform", "bluesky", "--yes", "--edit-dir", edit)
        self.assertEqual(rc, 1)
        self.assertIn("--public", err)
        rc, _, err = self.run_cli("send", "--platform", "youtube", "--edit-dir", edit)
        self.assertIn("dry run", err)

    def test_init_without_a_terminal_fails_cleanly(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            rc, _, err = self.run_cli("init", "mastodon")
        self.assertEqual(rc, 1)
        self.assertIn("interactive input", err)

    def test_prepare_needs_caption_and_known_platforms(self):
        video = make_video(self.dir)
        rc, _, err = self.run_cli("prepare", "--video", str(video), "--edit-dir", str(self.dir / "e"))
        self.assertEqual(rc, 1)
        rc, _, err = self.run_cli("prepare", "--video", str(video), "--caption", "x", "--platforms", "myspace", "--edit-dir", str(self.dir / "e"))
        self.assertIn("unknown platform", err)

    def test_per_platform_caption_override_and_status(self):
        video = make_video(self.dir)
        edit = str(self.dir / "edit")
        self.run_cli("prepare", "--video", str(video), "--caption", "long caption", "--caption-for", "x=short", "--platforms", "x", "--edit-dir", edit)
        self.assertEqual(package.load(Path(edit)).for_platform("x")["caption"], "short")
        rc, out, _ = self.run_cli("status", "--edit-dir", edit)
        self.assertIn("NOT available", out)
        rc, out, _ = self.run_cli("handoff", "--platform", "x", "--edit-dir", edit)
        self.assertIn("x.com/compose/post", out)

    def test_end_to_end_send_records_ledger_and_blocks_repeat(self):
        os.environ.update(VE_MASTODON_INSTANCE="https://m.example", VE_MASTODON_TOKEN="T")
        video = make_video(self.dir)
        edit = str(self.dir / "edit")
        self.run_cli("prepare", "--video", str(video), "--caption", "hi", "--platforms", "mastodon", "--edit-dir", edit)
        inst = {"configuration": {"statuses": {"max_characters": 500}, "media_attachments": {}}}
        self.fake([("GET", "/api/v2/instance", Resp(200, inst)), ("POST", "/api/v2/media", Resp(200, {"id": "M", "url": "u"})),
                   ("POST", "/api/v1/statuses", Resp(200, {"id": "S", "url": "https://m.example/1"}))])
        rc, out, _ = self.run_cli("send", "--platform", "mastodon", "--yes", "--edit-dir", edit)
        self.assertEqual(rc, 0)
        self.assertIn("draft", out)
        rc, _, err = self.run_cli("send", "--platform", "mastodon", "--yes", "--edit-dir", edit)
        self.assertEqual(rc, 1)
        self.assertIn("already sent", err)
        self.assertEqual(len(ledger.read(Path(edit))), 1)


if __name__ == "__main__":
    unittest.main()
