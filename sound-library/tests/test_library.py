"""Tests for sound-library/library.py. They run on temporary folders with
generated WAVs, never touch the network, and read the real catalog only to
check its shape."""

import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
import wave
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import library  # noqa: E402

LIB = Path(library.__file__).resolve().parent


def make_wav(seconds=0.5, rate=8000, channels=1, width=2, fill=0x11):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(width)
        handle.setframerate(rate)
        handle.writeframes(bytes([fill]) * int(seconds * rate) * channels * width)
    return buf.getvalue()


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as archive:
        for name, blob in members.items():
            archive.writestr(name, blob)
    return path


class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.catalog = self.tmp / "catalog.json"
        self.files = self.tmp / "files"
        self.bell = make_wav(0.25, fill=1)
        self.ride = make_wav(1.0, rate=16000, channels=2, fill=2)
        self.zip = make_zip(self.tmp / "b32e13f5-Test_Sounds_Pt1.zip", {
            "Archive/": b"",
            "Archive/Bike Bell.wav": self.bell,
            "Archive/Riding Bike (loopable).wav": self.ride,
            "__MACOSX/Archive/._Bike Bell.wav": b"\x00" * 207,
            "Archive/notes.txt": b"not audio",
        })

    def ingest(self, *sources, **kw):
        kw.setdefault("today", date(2026, 10, 21))
        return library.ingest(list(sources), catalog=self.catalog, files=self.files, **kw)

    def test_ingest_reads_the_zip_and_skips_the_junk(self):
        self.assertEqual(self.ingest(self.zip, release="sfx-test"), (2, 0, 0, 0))
        data = library.load(self.catalog)
        self.assertEqual([e["id"] for e in data["items"]],
                         ["test-sounds/bike-bell", "test-sounds/riding-bike-loopable"])
        bell = library.by_id(data)["test-sounds/bike-bell"]
        self.assertEqual(bell["name"], "Bike Bell")
        self.assertEqual(bell["category"], "test-sounds")
        self.assertEqual(bell["file"], "test-sounds/bike-bell.wav")
        self.assertEqual(bell["sha256"], hashlib.sha256(self.bell).hexdigest())
        self.assertEqual((bell["duration_s"], bell["sample_rate"], bell["channels"], bell["bit_depth"]),
                         (0.25, 8000, 1, 16))
        self.assertEqual(bell["tags"], ["bike", "bell"])
        self.assertFalse(bell["loopable"])
        self.assertEqual(bell["source"], {"release": "sfx-test", "asset": "Test_Sounds_Pt1.zip",
                                          "member": "Archive/Bike Bell.wav"})
        self.assertEqual(bell["added"], "2026-10-21")
        ride = library.by_id(data)["test-sounds/riding-bike-loopable"]
        self.assertTrue(ride["loopable"])
        self.assertEqual((ride["duration_s"], ride["channels"]), (1.0, 2))
        self.assertEqual((self.files / "test-sounds" / "bike-bell.wav").read_bytes(), self.bell)
        self.assertFalse(list(self.files.rglob("*.part")))

    def test_ingest_is_idempotent_and_refuses_a_different_file_for_an_id(self):
        self.ingest(self.zip)
        self.assertEqual(self.ingest(self.zip), (0, 2, 0, 0))
        other = make_zip(self.tmp / "Test_Sounds_Pt2.zip", {"Bike Bell.wav": make_wav(0.1, fill=9)})
        self.assertEqual(self.ingest(other), (0, 0, 0, 1))
        self.assertEqual(library.by_id(library.load(self.catalog))["test-sounds/bike-bell"]["sha256"],
                         hashlib.sha256(self.bell).hexdigest())
        self.assertEqual(self.ingest(other, replace=True), (0, 0, 1, 0))
        entry = library.by_id(library.load(self.catalog))["test-sounds/bike-bell"]
        self.assertEqual(entry["sha256"], hashlib.sha256(make_wav(0.1, fill=9)).hexdigest())
        self.assertEqual(entry["added"], "2026-10-21", "a replacement keeps the first date")

    def test_ingest_takes_a_folder_and_an_explicit_category(self):
        folder = self.tmp / "Boats"
        (folder / "deep").mkdir(parents=True)
        (folder / "deep" / "Ship Horn.wav").write_bytes(self.bell)
        (folder / "deep" / "._Ship Horn.wav").write_bytes(b"\x00")
        self.assertEqual(self.ingest(folder, category="Sea Craft"), (1, 0, 0, 0))
        entry = library.load(self.catalog)["items"][0]
        self.assertEqual(entry["id"], "sea-craft/ship-horn")
        self.assertEqual(entry["source"], {"release": None, "asset": "Boats", "member": "deep/Ship Horn.wav"})

    def test_ingest_refuses_what_is_neither_zip_nor_folder(self):
        bad = self.tmp / "x.zip"
        bad.write_bytes(b"nope")
        with self.assertRaises(library.Usage):
            self.ingest(bad)

    def test_category_from_zip_name(self):
        for name, want in [("Motor_Bikes_Pt3.zip", "motor-bikes"), ("b32e13f5-Bicycle_Pt1.zip", "bicycle"),
                           ("Boats Part 2.zip", "boats"), ("Rain-pt12.zip", "rain"), ("Doors.zip", "doors")]:
            self.assertEqual(library.category_from(name), want, name)

    def test_wav_info_rejects_what_is_not_a_wav(self):
        self.assertIsNone(library.wav_info(b"ID3" + b"\x00" * 40))
        self.assertIsNone(library.wav_info(b""))
        info = library.wav_info(make_wav(2.0, rate=44100, channels=2, width=3))
        self.assertEqual(info, {"channels": 2, "sample_rate": 44100, "bit_depth": 24, "duration_s": 2.0})

    def test_search_ranks_and_filters(self):
        self.ingest(self.zip)
        hits = library.search("bell", catalog=self.catalog, files=self.files)
        self.assertEqual([h["id"] for h in hits], ["test-sounds/bike-bell"])
        self.assertTrue(hits[0]["present"])
        hits = library.search("bike", catalog=self.catalog, files=self.files)
        self.assertEqual(len(hits), 2)
        hits = library.search("bike riding", catalog=self.catalog, files=self.files)
        self.assertEqual(hits[0]["id"], "test-sounds/riding-bike-loopable")
        self.assertEqual([h["id"] for h in library.search("", loopable=True, catalog=self.catalog, files=self.files)],
                         ["test-sounds/riding-bike-loopable"])
        self.assertEqual([h["id"] for h in library.search("", max_seconds=0.5, catalog=self.catalog, files=self.files)],
                         ["test-sounds/bike-bell"])
        self.assertEqual(library.search("", category="other", catalog=self.catalog, files=self.files), [])
        self.assertEqual(library.search("xylophone", catalog=self.catalog, files=self.files), [])

    def test_fetch_from_local_places_by_content_hash(self):
        self.ingest(self.zip)
        data = library.load(self.catalog)
        for entry in data["items"]:
            library.local_path(entry, self.files).unlink()
        renamed = make_zip(self.tmp / "whatever.zip", {"x/renamed.wav": self.bell})
        placed = library.fetch_from_local([renamed], data["items"], files=self.files)
        self.assertEqual(placed, ["test-sounds/bike-bell"])
        self.assertEqual((self.files / "test-sounds" / "bike-bell.wav").read_bytes(), self.bell)
        self.assertFalse((self.files / "test-sounds" / "riding-bike-loopable.wav").exists())

    def test_fetch_from_release_downloads_the_asset_and_checks_the_hash(self):
        self.ingest(self.zip, release="sfx-test")
        data = library.load(self.catalog)
        for entry in data["items"]:
            library.local_path(entry, self.files).unlink()
        zip_bytes = self.zip.read_bytes()
        calls = []

        def opener(request, timeout=None):
            calls.append(request.full_url)
            if request.full_url.endswith("/releases/tags/sfx-test"):
                body = {"assets": [{"name": "Test_Sounds_Pt1.zip",
                                    "browser_download_url": "https://dl.example/Test_Sounds_Pt1.zip"}]}
                return io.BytesIO(json.dumps(body).encode("utf-8"))
            if request.full_url == "https://dl.example/Test_Sounds_Pt1.zip":
                return io.BytesIO(zip_bytes)
            raise AssertionError(request.full_url)

        placed, failed = library.fetch_from_release(data["items"], files=self.files, opener=opener,
                                                    cache=self.tmp / "cache", repo="o/r")
        self.assertEqual(failed, [])
        self.assertEqual(sorted(placed), ["test-sounds/bike-bell", "test-sounds/riding-bike-loopable"])
        self.assertEqual(calls, ["https://api.github.com/repos/o/r/releases/tags/sfx-test",
                                 "https://dl.example/Test_Sounds_Pt1.zip"], "one download serves both members")
        self.assertEqual((self.files / "test-sounds" / "riding-bike-loopable.wav").read_bytes(), self.ride)
        # A member whose content changed is refused, not placed.
        data["items"][0]["sha256"] = "0" * 64
        library.local_path(data["items"][0], self.files).unlink()
        placed, failed = library.fetch_from_release(data["items"][:1], files=self.files, opener=opener,
                                                    cache=self.tmp / "cache", repo="o/r")
        self.assertEqual(placed, [])
        self.assertEqual(len(failed), 1)
        self.assertIn("sha256", failed[0][1])
        self.assertFalse(library.local_path(data["items"][0], self.files).exists())

    def test_download_release_takes_every_zip_once(self):
        zip_bytes = self.zip.read_bytes()
        calls = []

        def opener(request, timeout=None):
            calls.append(request.full_url)
            if request.full_url.endswith("/releases/tags/sfx-test"):
                body = {"assets": [{"name": "Test_Sounds_Pt1.zip", "browser_download_url": "https://dl.example/a.zip"},
                                   {"name": "README.txt", "browser_download_url": "https://dl.example/r.txt"}]}
                return io.BytesIO(json.dumps(body).encode("utf-8"))
            return io.BytesIO(zip_bytes)

        paths = library.download_release("sfx-test", self.tmp / "dl", repo="o/r", opener=opener)
        self.assertEqual([p.name for p in paths], ["Test_Sounds_Pt1.zip"])
        self.assertEqual(calls, ["https://api.github.com/repos/o/r/releases/tags/sfx-test", "https://dl.example/a.zip"])
        self.assertEqual(self.ingest(*paths, release="sfx-test"), (2, 0, 0, 0))
        with self.assertRaises(library.Usage):
            library.download_release("sfx-test", self.tmp / "dl2", repo="o/r",
                                     opener=lambda r, timeout=None: io.BytesIO(b'{"assets": []}'))

    def test_fetch_from_release_needs_a_tag(self):
        self.ingest(self.zip)
        data = library.load(self.catalog)
        for entry in data["items"]:
            library.local_path(entry, self.files).unlink()
        placed, failed = library.fetch_from_release(data["items"][:1], files=self.files,
                                                    opener=lambda *a, **k: self.fail("no network without a tag"))
        self.assertEqual(placed, [])
        self.assertIn("no release recorded", failed[0][1])

    def test_verify_finds_a_changed_file_and_a_bad_id(self):
        self.ingest(self.zip)
        self.assertEqual(library.verify(self.catalog, self.files), [])
        (self.files / "test-sounds" / "bike-bell.wav").write_bytes(b"RIFF" + b"\x00" * 40)
        problems = library.verify(self.catalog, self.files)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not match", problems[0])
        data = library.load(self.catalog)
        data["items"][0]["id"] = "elsewhere/bike-bell"
        library.save(data, self.catalog)
        self.assertTrue(any("does not match category" in p for p in library.verify(self.catalog, self.files)))

    def test_status_counts_by_category(self):
        self.ingest(self.zip)
        rows = library.status(self.catalog, self.files)
        self.assertEqual(rows["test-sounds"]["items"], 2)
        self.assertEqual(rows["test-sounds"]["here"], 2)
        self.assertAlmostEqual(rows["test-sounds"]["seconds"], 1.25)

    def test_main_exit_codes(self):
        self.assertEqual(library.main(["show", "nothing/here"]), library.EXIT_USAGE)


class RealCatalogTest(unittest.TestCase):
    """The committed catalog: well formed, and nothing in it is a link or a path
    off this machine. The files need not be on disk."""

    def setUp(self):
        self.data = library.load(LIB / "catalog.json")

    def test_catalog_verifies(self):
        self.assertEqual(library.verify(LIB / "catalog.json", LIB / "files"), [])

    def test_every_entry_names_its_release_and_holds_no_link(self):
        text = json.dumps(self.data)
        self.assertNotIn("http", text)
        self.assertNotIn("/home/", text)
        self.assertNotIn("C:\\", text)
        for entry in self.data["items"]:
            self.assertTrue(entry["source"]["release"], entry["id"])
            self.assertTrue(entry["source"]["asset"].endswith(".zip"), entry["id"])
            self.assertIsNotNone(entry["duration_s"], entry["id"])
            self.assertEqual(entry["format"], "wav", entry["id"])

    def test_files_folder_is_ignored_by_git(self):
        ignore = (LIB.parent / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("sound-library/files/", ignore)


if __name__ == "__main__":
    unittest.main()
