"""Tests for studio/library/library.py. They run on temporary folders and never
touch the network or the real catalog."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import library  # noqa: E402

LIB = Path(library.__file__).resolve().parent
UPLOAD_HOST = "d2ol7oe51mr4n9.cloudfront.net"


def item(ident, kind="image", ts=1791000000.0, **params):
    ext = {"image": "png", "video": "mp4", "audio": "wav", "3d": "glb"}[kind]
    results = {"rawUrl": f"https://cdn.example/hf_{ident}.{ext}"}
    if kind == "image":
        results["minUrl"] = f"https://cdn.example/hf_{ident}_min.webp"
    if kind == "audio":
        results["durationSec"] = 6
    return {"id": ident, "type": kind, "model": "m1", "status": "completed", "liked": False,
            "createdAt": ts, "params": {"prompt": "a prompt", **params}, "results": results}


class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.catalog = self.tmp / "catalog.json"

    def page(self, name, items):
        path = self.tmp / name
        path.write_text(json.dumps({"items": items, "next_cursor": None}), encoding="utf-8")
        return path

    def test_ingest_is_idempotent_and_sorted_newest_first(self):
        p = self.page("p1.json", [item("a", ts=1), item("b", ts=3), item("c", "video", ts=2)])
        self.assertEqual(library.ingest([p], self.catalog), (3, 0, 0))
        self.assertEqual(library.ingest([p], self.catalog), (0, 0, 0))
        cat = json.loads(self.catalog.read_text(encoding="utf-8"))
        self.assertEqual([e["id"] for e in cat["items"]], ["b", "c", "a"])
        self.assertEqual(cat["counts"], {"image": 2, "video": 1, "audio": 0, "3d": 0})

    def test_incomplete_jobs_are_skipped(self):
        pending = item("p")
        pending["status"] = "in_progress"
        pending["results"] = {}
        self.assertEqual(library.ingest([self.page("p.json", [pending, item("ok")])], self.catalog), (1, 0, 1))

    def test_upload_urls_are_never_kept(self):
        upload = f"https://{UPLOAD_HOST}/user_x/u1.png"
        p = self.page("p.json", [item("m", "3d", medias=[
            {"role": "image", "data": {"id": "u1", "type": "media_input", "url": upload}},
            {"role": "image", "data": {"id": "a", "type": "image_job", "url": "https://cdn.example/a.png"}},
        ], input_image={"id": "u1", "type": "media_input", "url": upload})])
        library.ingest([p], self.catalog)
        text = self.catalog.read_text(encoding="utf-8")
        self.assertNotIn(UPLOAD_HOST, text)
        entry = json.loads(text)["items"][0]
        self.assertEqual([i["id"] for i in entry["inputs"]], ["u1", "a"])

    def test_normalize_keeps_settings_and_audio_duration(self):
        e = library.normalize(item("s", "audio", seed=7, aspect_ratio="16:9", reference_elements=[1], batch_size=4))
        self.assertEqual(e["settings"], {"seed": 7, "aspect_ratio": "16:9"})
        self.assertEqual((e["ext"], e["duration_sec"]), ("wav", 6))

    def test_a_3d_model_borrows_its_source_image_thumb(self):
        img = library.normalize(item("img"))
        mesh = library.normalize(item("mesh", "3d", medias=[{"role": "image", "data": {"id": "img", "type": "image_job"}}]))
        self.assertEqual(library._thumb_source(mesh, {"img": img}), (img["preview_url"], False))
        self.assertEqual(library._thumb_source(library.normalize(item("v", "video")), {})[1], True)
        self.assertEqual(library._thumb_source(library.normalize(item("au", "audio")), {}), (None, False))

    def test_select_filters(self):
        items = [library.normalize(item("a", ts=1)), library.normalize(item("b", "video", ts=1800000000))]
        self.assertEqual([e["id"] for e in library.select(items, types=["video"])], ["b"])
        self.assertEqual([e["id"] for e in library.select(items, since="2027-01-01")], ["b"])
        self.assertEqual(len(library.select(items, limit=1)), 1)

    def test_bad_page_is_a_usage_error(self):
        bad = self.tmp / "bad.json"
        bad.write_text('{"nope": 1}', encoding="utf-8")
        with self.assertRaises(library.Usage):
            library.ingest([bad], self.catalog)


class RealCatalogTest(unittest.TestCase):
    """The versioned catalog: well-formed, and holding no upload link."""

    def test_catalog_is_well_formed(self):
        path = LIB / "catalog.json"
        if not path.exists():
            self.skipTest("no catalog yet")
        text = path.read_text(encoding="utf-8")
        self.assertNotIn(UPLOAD_HOST, text)
        cat = json.loads(text)
        ids = [e["id"] for e in cat["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(cat["count"], len(ids))
        for e in cat["items"]:
            self.assertIn(e["type"], library.TYPES)
            self.assertTrue(e["url"].startswith("https://"))

    def test_originals_are_not_versioned(self):
        ignore = (LIB.parent.parent / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("studio/library/files/", ignore)


if __name__ == "__main__":
    unittest.main()
