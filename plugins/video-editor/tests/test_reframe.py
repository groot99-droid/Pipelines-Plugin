import _paths  # noqa: F401  (puts src/ on sys.path)
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from videoeditor.core import reframe
from videoeditor.core.platform import probe


class SpeakerSegments(unittest.TestCase):
    def curves(self, left_first=3.0, total=6.0, fps=30.0):
        n = int(total * fps)
        left, right = np.full(n, 1.0), np.full(n, 1.0)
        k = int(left_first * fps)
        left[:k] = 10.0
        right[k:] = 10.0
        return left, right

    def test_switch_found(self):
        left, right = self.curves()
        segs = reframe.speaker_segments(left, right, 30.0)
        self.assertEqual([s["speaker"] for s in segs], ["left", "right"])
        self.assertAlmostEqual(segs[0]["end"], 3.0, delta=0.4)

    def test_short_interjection_merges(self):
        left, right = self.curves(total=6.0)
        right[:] = 1.0
        left[:] = 10.0
        right[60:75] = 40.0   # 0.5s blip from the other side
        segs = reframe.speaker_segments(left, right, 30.0, min_dur=1.0)
        self.assertEqual([s["speaker"] for s in segs], ["left"])

    def test_empty(self):
        self.assertEqual(reframe.speaker_segments(np.array([]), np.array([])), [])


class Geometry(unittest.TestCase):
    def test_pan_expr_hard_cuts(self):
        segs = [{"start": 0, "end": 2.5, "speaker": "left"}, {"start": 2.5, "end": 5, "speaker": "right"}]
        self.assertEqual(reframe.pan_expr(segs, 100, 900), "if(lt(t\\,2.5000)\\,100\\,900)")

    def test_pan_positions_clamped(self):
        self.assertEqual(reframe.pan_positions(50, 1900, 1920, 608), (0, 1920 - 608))

    def test_strip_width_is_even(self):
        self.assertEqual(reframe.strip_width(1080), 606)  # 1080*9/16 = 607.5 -> even

    def test_split_enable_expression(self):
        segs = [{"start": 0, "end": 2, "speaker": "left"}, {"start": 2, "end": 4, "speaker": "right"}]
        f = reframe.split_filter(segs, (400, 500), (1400, 500), 1920, 1080)
        self.assertIn("between(t,2.000,4.000)", f)
        self.assertTrue(f.endswith("[v]"))


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg required")
class CenterCropRender(unittest.TestCase):
    def test_output_has_video_and_audio_at_1080x1920(self):
        with tempfile.TemporaryDirectory() as td:
            src, out = Path(td) / "in.mp4", Path(td) / "out.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=640x360:r=25:d=1",
                            "-f", "lavfi", "-i", "sine=d=1", "-shortest", "-pix_fmt", "yuv420p", str(src)], check=True)
            reframe.reframe(src, out, "center")
            info = probe(out)
            self.assertEqual((info["width"], info["height"]), (1080, 1920))  # regression: -map once dropped video
            self.assertTrue(info["has_audio"])


if __name__ == "__main__":
    unittest.main()
