import _paths  # noqa: F401  (puts src/ on sys.path)
import json
import re
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from videoeditor.core import captions, moments


def click_wav(path, seconds=4.0, sr=16000, at=(1.0, 2.0, 3.0)):
    x = np.zeros(int(seconds * sr), dtype=np.float32)
    rng = np.random.default_rng(0)
    for t in at:
        i = int(t * sr)
        x[i:i + 200] = rng.uniform(-0.9, 0.9, 200)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


class Transients(unittest.TestCase):
    def test_finds_clicks_and_builds_shots(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "c.wav"
            click_wav(p)
            peaks = moments.detect_transients(p)
            self.assertEqual(len(peaks), 3)
            for got, want in zip(peaks, (1.0, 2.0, 3.0)):
                self.assertAlmostEqual(got["time"], want, delta=0.08)
            shots = moments.shots_around(peaks, duration=3.2)
            self.assertAlmostEqual(shots[0]["end"] - shots[0]["start"], 0.9, delta=0.1)
            self.assertLessEqual(shots[-1]["end"], 3.2)

    def test_rejects_stereo(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "s.wav"
            with wave.open(str(p), "wb") as w:
                w.setnchannels(2); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\0" * 64000)
            with self.assertRaises(SystemExit):
                moments.detect_transients(p)


class Captions(unittest.TestCase):
    def words(self):
        # second word's start overlaps the previous end by 20ms, like real Whisper output
        return [{"text": "Hello", "start": 0.0, "end": 0.52}, {"text": "big", "start": 0.50, "end": 0.9},
                {"text": "world.", "start": 0.9, "end": 1.3}, {"text": "Again", "start": 1.28, "end": 1.7}]

    def test_ass_events_never_overlap(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "c.ass"
            n = captions.build_ass(self.words(), "opus", out)
            ev = re.findall(r"Dialogue: 0,([\d:.]+),([\d:.]+),", out.read_text(encoding="utf-8"))
            self.assertEqual(len(ev), n)
            to_s = lambda t: sum(float(p) * m for p, m in zip(t.split(":"), (3600, 60, 1)))
            for (a1, b1), (a2, b2) in zip(ev, ev[1:]):
                self.assertLessEqual(to_s(b1), to_s(a2) + 1e-6)

    def test_output_timeline_offsets(self):
        with tempfile.TemporaryDirectory() as td:
            edit = Path(td)
            (edit / "transcripts").mkdir()
            (edit / "transcripts" / "a.json").write_text(json.dumps({"words": [
                {"type": "word", "text": "one", "start": 10.0, "end": 10.4},
                {"type": "word", "text": "two", "start": 20.0, "end": 20.4}]}), encoding="utf-8")
            edl = {"ranges": [{"source": "a", "start": 9.9, "end": 10.5}, {"source": "a", "start": 19.9, "end": 20.5}]}
            got = captions.output_timeline_words(edl, edit)
            self.assertAlmostEqual(got[0]["start"], 0.1, places=3)
            self.assertAlmostEqual(got[1]["start"], 0.6 + 0.1, places=3)

    def test_unknown_style(self):
        with self.assertRaises(SystemExit):
            captions.build_captions({"ranges": []}, Path("."), "neon")


if __name__ == "__main__":
    unittest.main()
