"""llm.py: default model, retry with backoff, truncation checks. No network."""
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE))

import llm  # noqa: E402
import run_pipeline  # noqa: E402


class _Resp:
    def __init__(self, body):
        self._b = json.dumps(body).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class DefaultsTest(unittest.TestCase):
    def test_default_model(self):
        self.assertEqual(llm.DEFAULT_ANTHROPIC_MODEL, "claude-sonnet-5-5")

    def test_env_int_rejects_junk(self):
        with mock.patch.dict("os.environ", {"X_T": "abc"}):
            with self.assertRaises(RuntimeError):
                llm._int_env("X_T", 1)


class OllamaTest(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(llm.time, "sleep")
        self.sleep = p.start()
        self.addCleanup(p.stop)

    def test_retries_then_succeeds(self):
        calls = [urllib.error.URLError("down"), _Resp({"response": "ok"})]

        def fake(req, timeout):
            r = calls.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        with mock.patch.object(llm.urllib.request, "urlopen", fake):
            self.assertEqual(llm._generate_ollama("p", system=None, model="m"), "ok")
        self.assertEqual(self.sleep.call_count, 1)

    def test_gives_up_after_retries(self):
        with mock.patch.object(llm.urllib.request, "urlopen",
                               side_effect=urllib.error.URLError("down")) as u:
            with self.assertRaises(llm.LLMError):
                llm._generate_ollama("p", system=None, model="m")
        self.assertEqual(u.call_count, llm.MAX_RETRIES + 1)

    def test_404_is_not_retried(self):
        err = urllib.error.HTTPError("u", 404, "nf", {}, io.BytesIO(b"no model"))
        with mock.patch.object(llm.urllib.request, "urlopen", side_effect=err) as u:
            with self.assertRaises(llm.LLMError):
                llm._generate_ollama("p", system=None, model="m")
        self.assertEqual(u.call_count, 1)

    def test_truncation_raises(self):
        with mock.patch.object(llm.urllib.request, "urlopen",
                               return_value=_Resp({"response": "cut", "done_reason": "length"})):
            with self.assertRaisesRegex(llm.LLMError, "PIPELINE_MAX_TOKENS"):
                llm._generate_ollama("p", system=None, model="m")


class ThemesTest(unittest.TestCase):
    def _vault(self, tmp):
        d = Path(tmp) / "_ChunkTags"
        d.mkdir()
        (d / "vocabulary.yaml").write_text("context_tags:\n  - grief\n  - memory-and-forgetting\n  - loneliness\n",
                                           encoding="utf-8")
        return Path(tmp)

    def test_inline_and_bulleted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            v = self._vault(tmp)
            inline = run_pipeline._extract_idea_themes("Candidate themes: grief, loneliness\n", v)
            self.assertEqual(inline, ["grief", "loneliness"])
            bullets = "## Idea\nCandidate themes:\n- grief\n- loneliness\n\nOther text about memory\n"
            self.assertEqual(run_pipeline._extract_idea_themes(bullets, v), ["grief", "loneliness"])
            bold = "**Candidate themes:**\n1. memory and forgetting\n2. grief\n"
            self.assertEqual(run_pipeline._extract_idea_themes(bold, v), ["grief", "memory-and-forgetting"])


if __name__ == "__main__":
    unittest.main()
