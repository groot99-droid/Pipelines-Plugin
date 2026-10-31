"""Optional backends: whisperX adapter, speaker turns, Demucs stems, Remotion overlays."""
import _paths  # noqa: F401  (puts src/ on sys.path)

import json
import subprocess
import sys
import tempfile
import types
import unittest
import wave
from pathlib import Path
from unittest import mock

import numpy as np

from videoeditor.core import overlays, pack, reframe, render, stems, transcribe, transcribe_whisperx
from videoeditor.core.platform import probe


# ---------------------------------------------------------------- transcript shape


class WordsToScribe(unittest.TestCase):
    def test_speaker_id_and_spacing(self):
        d = transcribe.words_to_scribe(
            [{"text": "Hi", "start": 0.0, "end": 0.3, "speaker": "SPEAKER_00"},
             {"text": "there", "start": 1.0, "end": 1.4, "speaker": "SPEAKER_01"}], "en", 2.0, backend="whisperx")
        self.assertEqual([w["type"] for w in d["words"]], ["word", "spacing", "word"])
        self.assertEqual(d["words"][0]["speaker_id"], "SPEAKER_00")
        self.assertEqual(d["backend"], "whisperx")
        phrases = pack.group_into_phrases(d["words"], 0.5)  # speaker change + gap both split phrases
        self.assertEqual([p["text"] for p in phrases], ["Hi", "there"])

    def test_untimed_words_are_interpolated_not_dropped(self):
        d = transcribe.words_to_scribe(
            [{"text": "cost", "start": 0.0, "end": 0.4}, {"text": "$13.60", "start": None, "end": None},
             {"text": "total", "start": 1.0, "end": 1.4}], "en", 2.0)
        words = [w for w in d["words"] if w["type"] == "word"]
        self.assertEqual([w["text"] for w in words], ["cost", "$13.60", "total"])
        mid = words[1]
        self.assertGreaterEqual(mid["start"], 0.4)
        self.assertLessEqual(mid["end"], 1.0)
        self.assertLess(mid["start"], mid["end"])

    def test_consecutive_untimed_words_share_the_gap_in_order(self):
        d = transcribe.words_to_scribe(
            [{"text": "a", "start": 0.0, "end": 1.0}, {"text": "$5", "start": None, "end": None},
             {"text": "2014.", "start": None, "end": None}, {"text": "b", "start": 3.0, "end": 4.0}], "en", 4.0)
        w = [x for x in d["words"] if x["type"] == "word"]
        self.assertEqual((w[1]["start"], w[1]["end"]), (1.0, 2.0))
        self.assertEqual((w[2]["start"], w[2]["end"]), (2.0, 3.0))   # not stacked on one instant

    def test_untimed_words_at_edges(self):
        d = transcribe.words_to_scribe(
            [{"text": "2014.", "start": None, "end": None}, {"text": "ok", "start": 1.0, "end": 1.2},
             {"text": "end", "start": None, "end": None}], "en", 3.0)
        w = [x for x in d["words"] if x["type"] == "word"]
        self.assertEqual(w[0]["start"], 0.0)
        self.assertEqual(w[-1]["end"], 3.0)

    def test_blank_words_skipped(self):
        d = transcribe.words_to_scribe([{"text": "  ", "start": 0, "end": 1}, {"text": "a", "start": 1, "end": 2}], "en", 2)
        self.assertEqual([w["text"] for w in d["words"] if w["type"] == "word"], ["a"])


class BackendGuards(unittest.TestCase):
    def test_unknown_backend_and_diarize_need_whisperx(self):
        with tempfile.TemporaryDirectory() as td:
            v = Path(td) / "v.mp4"
            v.write_bytes(b"x")
            with self.assertRaises(SystemExit):
                transcribe.transcribe(v, Path(td) / "e", backend="nope")
            with self.assertRaises(SystemExit) as cm:
                transcribe.transcribe(v, Path(td) / "e", diarize=True)
            self.assertIn("whisperx", str(cm.exception))

    def test_cache_is_per_backend_and_diarization(self):
        with tempfile.TemporaryDirectory() as td:
            v = Path(td) / "v.mp4"
            v.write_bytes(b"x")
            out = Path(td) / "t.json"
            out.write_text(json.dumps({"words": [], "backend": "faster-whisper"}), encoding="utf-8")
            self.assertTrue(transcribe._is_cached(out, v, "faster-whisper", False))
            self.assertFalse(transcribe._is_cached(out, v, "whisperx", False))   # switching backend re-runs
            out.write_text(json.dumps({"words": [], "backend": "whisperx", "diarized": False}), encoding="utf-8")
            self.assertFalse(transcribe._is_cached(out, v, "whisperx", True))    # asked for speakers, have none
            out.write_text(json.dumps({"words": [], "backend": "whisperx", "diarized": True}), encoding="utf-8")
            self.assertTrue(transcribe._is_cached(out, v, "whisperx", True))

    def test_preflight_names_the_extra(self):
        with mock.patch("importlib.util.find_spec", return_value=None):
            with self.assertRaises(SystemExit) as cm:
                transcribe._preflight("whisperx", False)
            self.assertIn("speech-plus", str(cm.exception))
            with self.assertRaises(SystemExit) as cm:
                transcribe._preflight("faster-whisper", True)
            self.assertIn("speech]", str(cm.exception))


# ---------------------------------------------------------------- whisperX adapter


ALIGNED = {"segments": [
    {"start": 0, "end": 2, "text": "Hello 2014.", "speaker": "SPEAKER_00", "words": [
        {"word": "Hello", "start": 0.1, "end": 0.5, "score": 0.9, "speaker": "SPEAKER_00"},
        {"word": "2014."}]},                                  # untimed and unlabeled: seg speaker fills in
    {"start": 3, "end": 4, "text": "Yes", "speaker": "SPEAKER_01", "words": [
        {"word": "Yes", "start": 3.1, "end": 3.4, "score": 0.8, "speaker": "SPEAKER_01"}]}]}


class WhisperXAdapter(unittest.TestCase):
    def test_flatten(self):
        w = transcribe_whisperx.flatten_result(ALIGNED)
        self.assertEqual([x["text"] for x in w], ["Hello", "2014.", "Yes"])
        self.assertIsNone(w[1]["start"])
        self.assertEqual(w[1]["speaker"], "SPEAKER_00")

    def fake_whisperx(self, calls):
        wx = types.ModuleType("whisperx")
        wx.load_audio = lambda p: calls.append("audio") or np.zeros(32000, dtype=np.float32)

        class Asr:
            def transcribe(self, audio, batch_size):
                calls.append("transcribe")
                return {"language": "en", "segments": [{"start": 0, "end": 1, "text": "x"}]}

        wx.load_model = lambda *a, **k: calls.append(("load_model", k.get("use_auth_token"))) or Asr()
        wx.load_align_model = lambda **k: calls.append("load_align") or ("m", {})
        wx.align = lambda segs, *a, **k: calls.append("align") or ALIGNED
        wx.assign_word_speakers = lambda turns, res: calls.append(("assign", turns)) or res
        dz = types.ModuleType("whisperx.diarize")

        class Pipe:
            def __init__(self, token=None, device=None):
                calls.append(("pipe", token))

            def __call__(self, audio, min_speakers=None, max_speakers=None):
                calls.append(("diarize", min_speakers, max_speakers))
                return "TURNS"

        dz.DiarizationPipeline = Pipe
        return {"whisperx": wx, "whisperx.diarize": dz}

    def test_pipeline_order_without_diarization(self):
        calls = []
        with mock.patch.dict(sys.modules, self.fake_whisperx(calls)):
            words, lang, dur = transcribe_whisperx.run_whisperx(Path("a.wav"), model="base.en", language="en")
        self.assertEqual([c if isinstance(c, str) else c[0] for c in calls], ["audio", "load_model", "transcribe", "load_align", "align"])
        self.assertEqual((lang, dur), ("en", 2.0))
        self.assertEqual(len(words), 3)

    def test_diarization_passes_token_and_speaker_bounds(self):
        calls = []
        with mock.patch.dict(sys.modules, self.fake_whisperx(calls)):
            transcribe_whisperx.run_whisperx(Path("a.wav"), model="m", language="en", diarize=True, hf_token="tok",
                                             min_speakers=1, max_speakers=2)
        self.assertIn(("pipe", "tok"), calls)
        self.assertIn(("diarize", 1, 2), calls)
        self.assertIn(("assign", "TURNS"), calls)

    def test_diarization_without_token_fails_before_loading_models(self):
        calls = []
        with mock.patch.dict(sys.modules, self.fake_whisperx(calls)), mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                transcribe_whisperx.run_whisperx(Path("a.wav"), model="m", language="en", diarize=True)
        self.assertIn("HF_TOKEN", str(cm.exception))
        self.assertEqual(calls, [])

    def test_missing_nltk_data_gives_actionable_error(self):
        calls = []
        mods = self.fake_whisperx(calls)

        def boom(*a, **k):
            raise LookupError("Resource punkt_tab not found")

        mods["whisperx"].align = boom
        with mock.patch.dict(sys.modules, mods):
            with self.assertRaises(SystemExit) as cm:
                transcribe_whisperx.run_whisperx(Path("a.wav"), model="m", language="en")
        self.assertIn("nltk.downloader punkt_tab", str(cm.exception))


# ---------------------------------------------------------------- speaker turns


def spoken(text, a, b, spk):
    return {"type": "word", "text": text, "start": a, "end": b, "speaker_id": spk}


class SpeakerTurns(unittest.TestCase):
    MAP = {"SPEAKER_00": "left", "SPEAKER_01": "right"}

    def test_turns_follow_speakers_and_fill_gaps(self):
        words = [spoken("a", 0.5, 2.0, "SPEAKER_00"), spoken("b", 2.0, 2.5, "SPEAKER_00"),
                 spoken("c", 4.0, 6.0, "SPEAKER_01"), spoken("d", 8.0, 10.0, "SPEAKER_00")]
        segs = reframe.speaker_segments_from_words(words, self.MAP)
        self.assertEqual([s["speaker"] for s in segs], ["left", "right", "left"])
        self.assertEqual(segs[0]["start"], 0.0)                      # first turn extends back to the clip start
        self.assertEqual(segs[0]["end"], segs[1]["start"])            # no dead gap between turns

    def test_short_interjection_merges_and_unmapped_ignored(self):
        words = [spoken("a", 0, 3, "SPEAKER_00"), spoken("hm", 3.0, 3.4, "SPEAKER_01"),
                 spoken("b", 3.5, 6, "SPEAKER_00"), spoken("z", 7, 8, "SPEAKER_09")]
        segs = reframe.speaker_segments_from_words(words, self.MAP, min_dur=1.0)
        self.assertEqual([s["speaker"] for s in segs], ["left"])

    def test_no_mapped_speakers_gives_empty(self):
        self.assertEqual(reframe.speaker_segments_from_words([spoken("a", 0, 1, "X")], self.MAP), [])

    def test_pan_render_uses_supplied_turns_not_motion(self):
        with tempfile.TemporaryDirectory() as td:
            clip, out = Path(td) / "c.mp4", Path(td) / "o.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=1280x720:r=25:d=2",
                            "-f", "lavfi", "-i", "sine=d=2", "-shortest", "-pix_fmt", "yuv420p", str(clip)], check=True)
            turns = [{"start": 0.0, "end": 1.0, "speaker": "left"}, {"start": 1.0, "end": 2.0, "speaker": "right"}]
            with mock.patch.object(reframe, "motion_energy", side_effect=AssertionError("motion must not run")):
                res = reframe.reframe(clip, out, "pan", left_roi=(100, 200, 200, 200), right_roi=(900, 200, 200, 200),
                                      segments=turns)
            self.assertEqual(res["segments"], turns)
            self.assertEqual((probe(out)["width"], probe(out)["height"]), (1080, 1920))

    def test_cli_turns_flags_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            clip, out, tr = td / "c.mp4", td / "o.mp4", td / "t.json"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=1280x720:r=25:d=3",
                            "-f", "lavfi", "-i", "sine=d=3", "-shortest", "-pix_fmt", "yuv420p", str(clip)], check=True)
            # transcript of a longer source; the clip starts at 10s in it
            tr.write_text(json.dumps({"words": [spoken("a", 10.0, 11.5, "SPEAKER_00"), spoken("b", 11.5, 13.0, "SPEAKER_01")]}), encoding="utf-8")
            reframe.main([str(clip), "-o", str(out), "--mode", "pan", "--left-roi", "100,200,200,200",
                          "--right-roi", "900,200,200,200", "--turns", str(tr),
                          "--speaker-map", "SPEAKER_00=left,SPEAKER_01=right", "--clip-start", "10"])
            self.assertTrue(out.exists())
            with self.assertRaises(SystemExit):   # --turns without a map is a usage error, not a silent fallback
                reframe.main([str(clip), "-o", str(out), "--mode", "pan", "--left-roi", "1,1,2,2", "--right-roi", "1,1,2,2",
                              "--turns", str(tr)])


# ---------------------------------------------------------------- Demucs stems


def write_wav(path, samples, sr=44100):
    path = Path(path)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype(np.int16).tobytes())


def fake_demucs(calls):
    api = types.ModuleType("demucs.api")
    sr = 44100

    class Separator:
        samplerate = sr

        def __init__(self, model="htdemucs", device="cpu", progress=False):
            calls.append(("init", model, device))

        def separate_audio_file(self, f):
            calls.append(("separate", Path(f).name))
            t = np.arange(sr) / sr
            return None, {"drums": 0.1 * np.sin(2 * np.pi * 100 * t), "bass": 0.1 * np.sin(2 * np.pi * 60 * t),
                          "other": 0.1 * np.sin(2 * np.pi * 440 * t), "vocals": 0.5 * np.sin(2 * np.pi * 220 * t)}

    api.Separator = Separator
    api.save_audio = lambda audio, path, samplerate: write_wav(path, audio, samplerate)
    pkg = types.ModuleType("demucs")
    pkg.api = api
    return {"demucs": pkg, "demucs.api": api}


class Stems(unittest.TestCase):
    def media(self, td):
        m = Path(td) / "m.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=d=1", str(m)], check=True)
        return m

    def test_requested_stems_and_complement(self):
        calls = []
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(sys.modules, fake_demucs(calls)):
            out = stems.separate(self.media(td), Path(td) / "s", ["vocals", "no_vocals"])
            self.assertEqual(set(out), {"vocals", "no_vocals"})
            self.assertTrue(all(p.exists() for p in out.values()))
            with wave.open(str(out["no_vocals"])) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768
            self.assertAlmostEqual(float(np.abs(a).max()), 0.3, delta=0.05)  # drums+bass+other, not vocals
            self.assertEqual([c[0] for c in calls].count("separate"), 1)     # one model run for both

    def test_cached_second_call_skips_the_model(self):
        calls = []
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(sys.modules, fake_demucs(calls)):
            m = self.media(td)
            stems.separate(m, Path(td) / "s", ["drums"])
            stems.separate(m, Path(td) / "s", ["drums"])
            self.assertEqual([c[0] for c in calls].count("init"), 1)

    def test_mono_16k_output_for_detection(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(sys.modules, fake_demucs([])):
            p = stems.separate(self.media(td), Path(td) / "s", ["drums"], mono_16k=True)["drums"]
            with wave.open(str(p)) as w:
                self.assertEqual((w.getnchannels(), w.getframerate()), (1, 16000))

    def test_unknown_stem_and_missing_dependency(self):
        with tempfile.TemporaryDirectory() as td:
            m = self.media(td)
            with mock.patch.dict(sys.modules, fake_demucs([])):
                with self.assertRaises(SystemExit) as cm:
                    stems.separate(m, Path(td) / "s", ["piano"])
                self.assertIn("has no stem 'piano'", str(cm.exception))
            with mock.patch.dict(sys.modules, {"demucs": None, "demucs.api": None}):
                with self.assertRaises(SystemExit) as cm:
                    stems.separate(m, Path(td) / "s2", ["vocals"])
                self.assertIn("videoeditor[stems]", str(cm.exception))


# ---------------------------------------------------------------- Remotion overlays


class RemotionOverlays(unittest.TestCase):
    def test_template_ships_and_has_no_remotion_source(self):
        files = {p.name for p in overlays.TEMPLATE_DIR.rglob("*") if p.is_file()}
        self.assertTrue({"package.json", "Overlay.tsx", "Root.tsx", "index.ts", "types.ts"} <= files)
        pkg = json.loads((overlays.TEMPLATE_DIR / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["dependencies"]["remotion"], pkg["dependencies"]["@remotion/cli"])  # Remotion needs matching versions

    def test_spec_and_pages(self):
        with tempfile.TemporaryDirectory() as td:
            edit = Path(td)
            (edit / "transcripts").mkdir()
            (edit / "transcripts" / "a.json").write_text(json.dumps({"words": [
                {"type": "word", "text": "hello", "start": 1.0, "end": 1.3},
                {"type": "word", "text": "world.", "start": 1.35, "end": 1.8}]}), encoding="utf-8")
            edl = {"ranges": [{"source": "a", "start": 0.9, "end": 2.0}]}
            pages = overlays.caption_pages_from_edl(edl, edit)
            self.assertEqual(pages[0]["text"], "hello world.")
            self.assertAlmostEqual(pages[0]["start"], 0.1, places=2)
            spec = overlays.build_overlay_spec(title="T", pages=pages, duration=2, transparent=True)
            self.assertEqual(spec["background"], "transparent")
            self.assertEqual([i["type"] for i in spec["items"]], ["title", "captions"])
            with self.assertRaises(SystemExit):
                overlays.build_overlay_spec()

    def test_scaffold_skips_build_artifacts_and_writes_props(self):
        with tempfile.TemporaryDirectory() as td:
            slot = Path(td) / "slot_1"
            (slot / "node_modules").mkdir(parents=True)
            spec = overlays.build_overlay_spec(title="T")
            overlays.scaffold_remotion_slot(slot, spec)
            self.assertEqual(json.loads((slot / "overlay.json").read_text(encoding="utf-8"))["items"][0]["text"], "T")
            self.assertTrue((slot / "src" / "Overlay.tsx").exists())

    def test_render_commands(self):
        with tempfile.TemporaryDirectory() as td:
            slot = Path(td)
            (slot / "node_modules").mkdir()
            with mock.patch("subprocess.run") as run:
                overlays.render_remotion(slot, "render.mp4", transparent=True, browser="/b/chrome")
            cmd = run.call_args[0][0]
            self.assertIn("--codec=vp8", cmd)
            self.assertIn("--pixel-format=yuva420p", cmd)
            self.assertIn("render.webm", cmd)                       # alpha needs a WebM container
            self.assertIn("--browser-executable=/b/chrome", cmd)
            with mock.patch("shutil.which", return_value=None):
                with self.assertRaises(SystemExit):
                    overlays.render_remotion(slot)


class WebmAlphaInComposite(unittest.TestCase):
    def test_libvpx_decoder_precedes_the_webm_input(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            base, ov, out = td / "base.mp4", td / "ov.webm", td / "out.mp4"
            for p in (base, ov):
                p.write_bytes(b"x")
            with mock.patch.object(render.subprocess, "run") as run:
                render.build_final_composite(base, [{"file": str(ov), "start_in_output": 0, "duration": 1}], None, out, td)
            cmd = run.call_args[0][0]
            i = cmd.index(str(ov))
            self.assertEqual(cmd[i - 3:i - 1], ["-c:v", "libvpx"])  # ffmpeg's native VP8 decoder would drop alpha
            self.assertEqual(cmd[i - 1], "-i")


if __name__ == "__main__":
    unittest.main()
