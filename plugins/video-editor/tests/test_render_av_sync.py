"""Segments must end video and audio together, so a concat of many cuts does not drift.

Regression: a millisecond-rounded `-t` (5.041667 -> "5.042") landed just past a frame
boundary, the video kept an extra frame the audio never got, and over 17 segments the
audio ran ~150 ms ahead of the picture.
"""
import _paths  # noqa: F401  (puts src/ on sys.path)
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "src" / "videoeditor" / "core" / "render.py"
SPEC = importlib.util.spec_from_file_location("video_use_render_sync", MODULE_PATH)
assert SPEC and SPEC.loader
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)

HAVE_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def _durations(path: Path) -> dict[str, float]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.split()
    return {kind: float(value) for kind, value in (line.split(",") for line in out)}


class FrameExactDurationTests(unittest.TestCase):
    def test_rounds_to_whole_frames(self):
        self.assertEqual(render.frame_exact_duration(5.041667, "24"), (121, 121 / 24))
        self.assertEqual(render.frame_exact_duration(5.2, "24/1"), (125, 125 / 24))
        n, exact = render.frame_exact_duration(2.0, "30000/1001")
        self.assertEqual(n, 60)
        self.assertAlmostEqual(exact, 60 * 1001 / 30000)

    def test_never_zero_frames(self):
        self.assertEqual(render.frame_exact_duration(0.001, "24")[0], 1)


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg and ffprobe on PATH")
class SegmentSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.source = cls.dir / "src.mp4"
        # 24 fps video with 44.1 kHz audio, so the extractor also has to resample
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y",
             "-f", "lavfi", "-i", "testsrc2=rate=24:size=320x240:duration=8",
             "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=8",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.source)],
            check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_segment_streams_match_and_concat_does_not_drift(self):
        # lengths that used to round past a frame boundary, or were not whole frames
        ranges = [(0.0, 5.041667), (0.416667, 1.2), (1.0, 2.833333), (0.5, 1.0)]
        segs = []
        for i, (start, length) in enumerate(ranges):
            out = self.dir / f"seg_{i}.mp4"
            render.extract_segment(self.source, start, length, "", out, draft=True, rate="24")
            d = _durations(out)
            n, exact = render.frame_exact_duration(length, "24")
            with self.subTest(segment=i):
                self.assertAlmostEqual(d["video"], exact, delta=0.001)
                self.assertAlmostEqual(d["audio"], exact, delta=0.025)  # within one AAC frame
            segs.append(out)

        base = self.dir / "base.mp4"
        render.concat_segments(segs, base, self.dir)
        d = _durations(base)
        self.assertLess(abs(d["video"] - d["audio"]), 1 / 24, "audio drifted from video by a frame or more")


if __name__ == "__main__":
    unittest.main()
