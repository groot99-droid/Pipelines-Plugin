import _paths  # noqa: F401  (puts src/ on sys.path)
import unittest
from types import SimpleNamespace as NS

from videoeditor.core import pack, render
from videoeditor.core.transcribe import to_scribe_shape


def seg(*words):
    return NS(words=[NS(word=w, start=s, end=e) for w, s, e in words])


class ScribeShape(unittest.TestCase):
    def setUp(self):
        self.data = to_scribe_shape(
            [seg((" Hello", 0.0, 0.4), (" world.", 0.45, 0.9)), seg((" Next", 2.0, 2.3))], "en", 3.0)

    def test_types_and_spacing(self):
        types = [w["type"] for w in self.data["words"]]
        self.assertEqual(types, ["word", "spacing", "word", "spacing", "word"])
        self.assertEqual(self.data["words"][0]["text"], "Hello")
        gap = self.data["words"][3]
        self.assertEqual((gap["start"], gap["end"]), (0.9, 2.0))

    def test_pack_reads_it_unchanged(self):
        phrases = pack.group_into_phrases(self.data["words"], 0.5)
        self.assertEqual([p["text"] for p in phrases], ["Hello world.", "Next"])

    def test_render_reads_it_unchanged(self):
        words = render._words_in_range(self.data, 0.0, 1.0)
        self.assertEqual([w["text"] for w in words], ["Hello", "world."])

    def test_empty_words_skipped(self):
        d = to_scribe_shape([seg((" ", 0, 1), ("ok", 1, 2))], "en", 2)
        self.assertEqual([w["text"] for w in d["words"] if w["type"] == "word"], ["ok"])


if __name__ == "__main__":
    unittest.main()


class MissingExtra(unittest.TestCase):
    def test_friendly_error_without_faster_whisper(self):
        import sys, tempfile
        from pathlib import Path
        from unittest import mock
        from videoeditor.core.transcribe import transcribe

        with tempfile.TemporaryDirectory() as td:
            video = Path(td) / "v.mp4"
            video.write_bytes(b"x")
            with mock.patch.dict(sys.modules, {"faster_whisper": None}):  # None => ImportError on import
                with self.assertRaises(SystemExit) as cm:
                    transcribe(video, Path(td) / "edit")
            self.assertIn("videoeditor[speech]", str(cm.exception))
