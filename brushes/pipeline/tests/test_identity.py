"""pipeline/identity.py against the frozen formulas (docs/CONTRACTS.md, F1).

The golden vectors here are the contract's. If one of these tests fails, the
formula changed, and every id in the catalog, the notes, the tag sidecars and
the preview file names would change with it. Fix the code, not the vector.

    python -m unittest discover -s brushes/pipeline/tests
"""

import hashlib
import re
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures  # noqa: E402
import identity  # noqa: E402

A_ONLY = "b_8f525da47bd2"
A_S_G = "b_747322c04223"
A_S_G_SUB = "b_7795500d8ec4"
DEMO_SET = "s_41c10a3b97f2"
PNG_TEXTURE = "t_796120837694"


class GoldenVectors(unittest.TestCase):
    def test_an_archive_alone(self):
        self.assertEqual(identity.brush_id(b"A"), A_ONLY)
        self.assertEqual(identity.brush_id(b"A", None, None), A_ONLY)

    def test_an_archive_with_shape_and_grain(self):
        self.assertEqual(identity.brush_id(b"A", b"S", b"G"), A_S_G)

    def test_a_dual_brush(self):
        self.assertEqual(identity.brush_id(b"A", b"S", b"G", [(b"A2", None, b"G2")]), A_S_G_SUB)

    def test_a_set_of_the_first_two(self):
        self.assertEqual(identity.set_id("Demo Set ", [A_ONLY, A_S_G]), DEMO_SET)

    def test_a_texture(self):
        self.assertEqual(identity.texture_id(b"PNG"), PNG_TEXTURE)


class Formula(unittest.TestCase):
    """The same hash, written out a second time from the contract's text."""

    @staticmethod
    def part(data):
        return b"\x00" if data is None else b"\x01" + len(data).to_bytes(8, "big") + data

    def expected(self, archive, shape, grain, subs=()):
        data = b"rosw-brush-v1\x00" + self.part(archive) + self.part(shape) + self.part(grain)
        for sub in subs:
            data += b"\x02" + b"".join(self.part(piece) for piece in sub)
        return hashlib.sha256(data).hexdigest()

    def test_part_frames_a_value_with_its_length(self):
        self.assertEqual(identity.part(None), b"\x00")
        self.assertEqual(identity.part(b""), b"\x01" + bytes(8))
        self.assertEqual(identity.part(b"abc"), b"\x01\x00\x00\x00\x00\x00\x00\x00\x03abc")

    def test_the_digest_of_a_fixture_brush(self):
        brush = fixtures.make_brush("Formula", "modern", number=21, dual=True)
        digest = identity.content_sha256(brush.archive, brush.shape, brush.grain, brush.subs)
        self.assertEqual(digest, self.expected(brush.archive, brush.shape, brush.grain, brush.subs))
        self.assertEqual(identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs),
                         "b_" + digest[:12])
        self.assertEqual(identity.brush_id_from_sha256(digest), "b_" + digest[:12])

    def test_the_digest_is_64_lower_case_hex_with_no_prefix(self):
        digest = identity.content_sha256(b"A")
        self.assertRegex(digest, r"\A[0-9a-f]{64}\Z")
        self.assertTrue(identity.is_sha256(digest))

    def test_a_texture_is_the_sha256_of_its_bytes(self):
        png = fixtures.make_png(4, 4)
        self.assertEqual(identity.texture_sha256(png), hashlib.sha256(png).hexdigest())
        self.assertEqual(identity.texture_id(png), "t_" + hashlib.sha256(png).hexdigest()[:12])

    def test_a_set_is_its_name_a_nul_and_its_members_joined_by_newlines(self):
        members = [A_ONLY, A_S_G, A_S_G_SUB]
        data = b"rosw-set-v1\x00" + "Démo".encode("utf-8") + b"\x00" + "\n".join(members).encode()
        self.assertEqual(identity.set_sha256("Démo", members), hashlib.sha256(data).hexdigest())
        self.assertEqual(identity.set_id("Démo", members), "s_" + hashlib.sha256(data).hexdigest()[:12])


class WhatChangesAnId(unittest.TestCase):
    def test_each_hashed_field_changes_it(self):
        base = identity.brush_id(b"A", b"S", b"G")
        self.assertNotEqual(identity.brush_id(b"B", b"S", b"G"), base)
        self.assertNotEqual(identity.brush_id(b"A", b"T", b"G"), base)
        self.assertNotEqual(identity.brush_id(b"A", b"S", b"H"), base)
        self.assertNotEqual(identity.brush_id(b"A", b"S", b"G", [(b"A", b"S", b"G")]), base)

    def test_a_missing_image_is_not_an_empty_one(self):
        self.assertNotEqual(identity.brush_id(b"A", None, None), identity.brush_id(b"A", b"", None))
        self.assertNotEqual(identity.brush_id(b"A", None, b""), identity.brush_id(b"A", b"", None))

    def test_bytes_cannot_move_between_fields(self):
        self.assertNotEqual(identity.brush_id(b"AB", None, None), identity.brush_id(b"A", b"B", None))
        self.assertNotEqual(identity.brush_id(b"A", b"SG", None), identity.brush_id(b"A", b"S", b"G"))
        self.assertNotEqual(identity.brush_id(b"A", b"S", None), identity.brush_id(b"A", None, b"S"))

    def test_sub_folders_count_in_order(self):
        one, two = (b"A1", None, None), (b"A2", b"S2", None)
        self.assertNotEqual(identity.brush_id(b"A", subs=[one, two]),
                            identity.brush_id(b"A", subs=[two, one]))
        self.assertNotEqual(identity.brush_id(b"A", subs=[one]), identity.brush_id(b"A", subs=[one, one]))

    def test_any_bytes_like_value_hashes_as_bytes(self):
        self.assertEqual(identity.brush_id(bytearray(b"A"), memoryview(b"S"), b"G"), A_S_G)


class WhatDoesNot(unittest.TestCase):
    """Thumbnail, Reset copy, author files and extra members are not hashed:
    a brush built with and without them carries the same three hashed parts."""

    def ident(self, brush):
        return identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs)

    def test_the_unhashed_members(self):
        plain = fixtures.make_brush("Same", number=7, thumbnail=False)
        dressed = fixtures.make_brush("Same", number=7, thumbnail=True, reset=True, author=True,
                                      empty=("",), extras=[("Extra/unknown.bin", b"x")])
        self.assertGreater(len(dressed.members), len(plain.members))
        self.assertEqual(self.ident(dressed), self.ident(plain))

    def test_a_secondary_brush_is_hashed(self):
        plain = fixtures.make_brush("Same", number=7)
        dual = fixtures.make_brush("Same", number=7, dual=True)
        self.assertEqual(plain.archive, dual.archive)
        self.assertNotEqual(self.ident(dual), self.ident(plain))

    def test_the_synthetic_library(self):
        user = fixtures.standard_user_brushes()
        ids = [self.ident(brush) for brush in user]
        self.assertEqual(len(set(ids)), 4, "four different brushes, two of them with one name")
        self.assertEqual(user[0].name, user[3].name)
        again = fixtures.standard_user_brushes()[0]
        self.assertEqual(self.ident(again), ids[0], "the same brush built twice is the same id")
        for ident in ids:
            self.assertTrue(identity.is_brush_id(ident))


class BadInput(unittest.TestCase):
    def test_an_archive_is_required_and_must_be_bytes(self):
        for bad in (None, "A", 65, ["A"]):
            with self.assertRaises(identity.IdentityError, msg=repr(bad)):
                identity.content_sha256(bad)

    def test_an_image_must_be_bytes_or_none(self):
        with self.assertRaises(identity.IdentityError):
            identity.content_sha256(b"A", "S")
        with self.assertRaises(identity.IdentityError):
            identity.content_sha256(b"A", None, 7)

    def test_a_sub_must_be_a_triple(self):
        for bad in ([b"A2"], [(b"A2", None)], [(b"A2", None, None, None)], [("A2", None, None)], [7]):
            with self.assertRaises(identity.IdentityError, msg=repr(bad)):
                identity.content_sha256(b"A", subs=bad)

    def test_a_texture_must_be_bytes(self):
        for bad in (None, "PNG"):
            with self.assertRaises(identity.IdentityError):
                identity.texture_id(bad)

    def test_a_brush_id_is_cut_only_from_a_full_digest(self):
        for bad in ("abc", "A" * 64, "g" * 64, None, "0" * 63):
            with self.assertRaises(identity.IdentityError, msg=repr(bad)):
                identity.brush_id_from_sha256(bad)

    def test_identity_errors_are_value_errors(self):
        self.assertTrue(issubclass(identity.IdentityError, ValueError))
        self.assertTrue(issubclass(identity.PrefixCollision, identity.IdentityError))


class Sets(unittest.TestCase):
    def test_the_name_is_hashed_verbatim(self):
        members = [A_ONLY, A_S_G]
        self.assertNotEqual(identity.set_id("Demo Set", members), DEMO_SET)
        self.assertNotEqual(identity.set_id("demo set ", members), DEMO_SET)

    def test_membership_and_order_count(self):
        self.assertNotEqual(identity.set_id("Demo Set ", [A_S_G, A_ONLY]), DEMO_SET)
        self.assertNotEqual(identity.set_id("Demo Set ", [A_ONLY]), DEMO_SET)
        self.assertNotEqual(identity.set_id("Demo Set ", [A_ONLY, A_S_G, A_S_G_SUB]), DEMO_SET)

    def test_an_empty_set_and_any_iterable(self):
        self.assertTrue(identity.is_set_id(identity.set_id("", [])))
        self.assertEqual(identity.set_id("Demo Set ", iter((A_ONLY, A_S_G))), DEMO_SET)

    def test_a_member_must_be_a_brush_id(self):
        for bad in ("b111", "b8f525da47bd2", PNG_TEXTURE, "b_8F525DA47BD2", A_ONLY + "\n"):
            with self.assertRaises(identity.IdentityError, msg=repr(bad)):
                identity.set_id("x", [bad])

    def test_the_name_must_be_text(self):
        with self.assertRaises(identity.IdentityError):
            identity.set_id(b"Demo Set ", [A_ONLY])
        with self.assertRaises(identity.IdentityError):
            identity.set_id("lone \ud800 surrogate", [A_ONLY])


class Patterns(unittest.TestCase):
    def test_the_patterns_are_the_contracts(self):
        self.assertEqual(identity.BRUSH_ID_PATTERN, r"^b_[0-9a-f]{12}$")
        self.assertEqual(identity.TEXTURE_ID_PATTERN, r"^t_[0-9a-f]{12}$")
        self.assertEqual(identity.SET_ID_PATTERN, r"^s_[0-9a-f]{12}$")
        self.assertEqual(identity.SET_SLUG_PATTERN, r"^[a-z0-9][a-z0-9-]{0,47}$")
        self.assertEqual(identity.SHA256_PATTERN, r"^[0-9a-f]{64}$")
        self.assertEqual(identity.ID_HEX, 12)

    def test_the_predicates_agree_with_the_patterns(self):
        cases = {
            identity.is_brush_id: (identity.BRUSH_ID_PATTERN, A_ONLY),
            identity.is_texture_id: (identity.TEXTURE_ID_PATTERN, PNG_TEXTURE),
            identity.is_set_id: (identity.SET_ID_PATTERN, DEMO_SET),
            identity.is_set_slug: (identity.SET_SLUG_PATTERN, "demo-set"),
            identity.is_sha256: (identity.SHA256_PATTERN, "0" * 64),
        }
        for predicate, (pattern, good) in cases.items():
            self.assertTrue(predicate(good), good)
            self.assertIsNotNone(re.match(pattern, good))

    def test_what_is_not_an_id(self):
        for bad in ("b8f525da47bd2", "b_8f525da47bd", "b_8f525da47bd22", "b_8F525DA47BD2",
                    "t_8f525da47bd2", " b_8f525da47bd2", "b_8f525da47bd2\n", "", None, 5, b"b_8f525da47bd2"):
            self.assertFalse(identity.is_brush_id(bad), repr(bad))
        self.assertFalse(identity.is_texture_id(A_ONLY))
        self.assertFalse(identity.is_set_id(A_ONLY))
        self.assertFalse(identity.is_sha256("0" * 64 + "\n"))

    def test_what_is_not_a_slug(self):
        for bad in ("", "-a", "A", "a_b", "a b", "a" * 49, "café", "a\n", None):
            self.assertFalse(identity.is_set_slug(bad), repr(bad))
        for good in ("a", "3d", "a" * 48, "p5-inking", "a-", "0-0"):
            self.assertTrue(identity.is_set_slug(good), good)


class Slugs(unittest.TestCase):
    def test_the_contract_vectors(self):
        vectors = {
            "Sargent’s Oils": "sargents-oils",
            "Broken Conté": "broken-conte",
            "3D": "3d",
            "Autumn Stamps ": "autumn-stamps",
        }
        for name, slug in vectors.items():
            self.assertEqual(identity.slugify(name), slug, name)

    def test_a_name_with_no_ascii_form_is_the_fallback(self):
        self.assertEqual(identity.slugify("浓墨淡彩"), identity.SLUG_FALLBACK)
        self.assertEqual(identity.slugify("浓墨淡彩", "chinese-calligraphy"),
                         "chinese-calligraphy")
        self.assertEqual(identity.slugify("   "), identity.SLUG_FALLBACK)
        self.assertEqual(identity.slugify("\U0001f4a7"), identity.SLUG_FALLBACK)

    def test_both_kinds_of_apostrophe_vanish(self):
        self.assertEqual(identity.slugify("Sargent's Oils"), "sargents-oils")
        self.assertEqual(identity.slugify("Dusty’s Grit Liner"), "dustys-grit-liner")

    def test_punctuation_and_case(self):
        self.assertEqual(identity.slugify("FTOON - Canvas X"), "ftoon-canvas-x")
        self.assertEqual(identity.slugify("BrushUp- Paint Pens"), "brushup-paint-pens")
        self.assertEqual(identity.slugify("\U0001f4a7Everything Watercolour"), "everything-watercolour")
        self.assertEqual(identity.slugify("__P5_Inking__"), "p5-inking")
        self.assertEqual(identity.slugify("Tech Pen 0.5"), "tech-pen-0-5")

    def test_it_is_cut_to_48_and_never_ends_in_a_hyphen(self):
        long = identity.slugify("word " * 30)
        self.assertLessEqual(len(long), 48)
        self.assertFalse(long.endswith("-"))
        self.assertTrue(identity.is_set_slug(long))
        self.assertEqual(identity.slugify("a" * 47 + " b"), "a" * 47)

    def test_a_windows_device_name_gets_a_prefix(self):
        for device in ("CON", "nul", "Com1", "LPT9", "aux", "prn"):
            self.assertEqual(identity.slugify(device), "x-" + device.lower())
        self.assertEqual(identity.slugify("console"), "console")
        self.assertEqual(identity.slugify("com10"), "com10")

    def test_every_result_is_a_slug(self):
        for name in ("Demo Set ", "A & <B>", "x" * 200, "Été 2019", "a--b", "..", "CON", ""):
            self.assertTrue(identity.is_set_slug(identity.slugify(name)), name)

    def test_the_fallback_must_itself_be_a_slug(self):
        with self.assertRaises(identity.IdentityError):
            identity.slugify("anything", fallback="Not A Slug")

    def test_the_loose_pseudo_set(self):
        self.assertEqual(identity.loose_set_slug("insecto-charcoal"), "insecto-charcoal-loose")
        with self.assertRaises(identity.IdentityError):
            identity.loose_set_slug("a" * 45)
        with self.assertRaises(identity.IdentityError):
            identity.loose_set_slug("Not A Pack")

    def test_a_pack_id_leaves_room_for_the_loose_suffix(self):
        self.assertEqual(identity.PACK_ID_MAX, 42)
        self.assertEqual(identity.PACK_ID_MAX + len(identity.LOOSE_SUFFIX), identity.SLUG_MAX)
        longest = "p" * identity.PACK_ID_MAX
        self.assertTrue(identity.is_pack_id(longest))
        self.assertTrue(identity.is_set_slug(identity.loose_set_slug(longest)))
        self.assertEqual(len(identity.loose_set_slug(longest)), identity.SLUG_MAX)
        too_long = longest + "p"
        self.assertTrue(identity.is_set_slug(too_long), "a slug, but too long to be a pack id")
        self.assertFalse(identity.is_pack_id(too_long))
        with self.assertRaises(identity.IdentityError):
            identity.loose_set_slug(too_long)
        for bad in ("", "Upper", "-lead", "a b", None, 7, "a" * 49):
            self.assertFalse(identity.is_pack_id(bad), repr(bad))

    def test_the_loose_slug_is_the_name_a_loose_set_is_hashed_under(self):
        """A pseudo-set has no plist, so its `name` is its slug (CONTRACTS F1)."""
        slug = identity.loose_set_slug("demo-pack")
        members = [identity.brush_id(b"A"), identity.brush_id(b"A", b"S", b"G")]
        self.assertEqual(identity.set_id(slug, members), identity.set_id("demo-pack-loose", members))
        self.assertNotEqual(identity.set_id(slug, members), identity.set_id(slug, members[::-1]))


class Collisions(unittest.TestCase):
    def test_the_same_content_gets_the_same_id_back(self):
        registry = identity.Registry()
        self.assertEqual(registry.brush(b"A"), A_ONLY)
        self.assertEqual(registry.brush(b"A"), A_ONLY)
        self.assertEqual(registry.brush(b"A", b"S", b"G"), A_S_G)
        self.assertEqual(registry.texture(b"PNG"), PNG_TEXTURE)
        self.assertEqual(registry.set("Demo Set ", [A_ONLY, A_S_G]), DEMO_SET)
        self.assertEqual(len(registry), 4)
        self.assertIn(A_ONLY, registry)
        self.assertEqual(registry.full_hash(A_ONLY), identity.content_sha256(b"A"))

    def test_two_hashes_under_one_short_id_is_an_error(self):
        registry = identity.Registry()
        first = "8f525da47bd2" + "0" * 52
        second = "8f525da47bd2" + "1" * 52
        self.assertEqual(registry.add(A_ONLY, first), A_ONLY)
        self.assertEqual(registry.add(A_ONLY, first), A_ONLY)
        with self.assertRaises(identity.PrefixCollision) as caught:
            registry.add(A_ONLY, second)
        self.assertEqual(caught.exception.exit_code, 1)
        self.assertEqual(caught.exception.ident, A_ONLY)
        self.assertEqual({caught.exception.known, caught.exception.other}, {first, second})
        self.assertIn(A_ONLY, str(caught.exception))
        self.assertEqual(registry.full_hash(A_ONLY), first, "the first hash is kept")

    def test_a_collision_met_while_hashing_real_content(self):
        registry = identity.Registry()
        registry.add(A_ONLY, "8f525da47bd2" + "f" * 52)      # another brush already holds the id
        with self.assertRaises(identity.PrefixCollision):
            registry.brush(b"A")

    def test_the_kinds_do_not_collide_with_each_other(self):
        registry = identity.Registry()
        digest = "8f525da47bd2" + "0" * 52
        other = "8f525da47bd2" + "1" * 52
        registry.add("b_8f525da47bd2", digest)
        registry.add("t_8f525da47bd2", other)
        registry.add("s_8f525da47bd2", other)
        self.assertEqual(len(registry), 3)

    def test_an_id_must_be_cut_from_the_hash_it_is_given_with(self):
        registry = identity.Registry()
        with self.assertRaises(identity.IdentityError):
            registry.add(A_ONLY, "0" * 64)
        with self.assertRaises(identity.IdentityError):
            registry.add("x_8f525da47bd2", "8f525da47bd2" + "0" * 52)
        with self.assertRaises(identity.IdentityError):
            registry.add(A_ONLY, "8f525da47bd2")
        self.assertEqual(len(registry), 0)


if __name__ == "__main__":
    unittest.main()
