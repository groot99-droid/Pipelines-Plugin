# Revision notes — "The Two Who Woke the Sea"

## 1. Wyrmreach-tie verification (highest-stakes check)

Ran, from the vault root (`C:\Users\utopi\Creative-Writing`):

```
python tools/vault_search.py search "Sevrain drowned god twin soul grief hunger tide" --top 5 --json
```

Result: top hits were `05_Worldbuilding/03_World_Codex_of_Wyrmreach.md` (score 0.135, frontmatter match on shared genre/theme tags: high-fantasy, memory-and-oblivion, twin-souls, elemental-balance), `04_Book_Concepts/07_Narrative_Voice.md` (0.129, unrelated mode/theme), `02_Novels/04_The_Cycle_of_Us.md` (0.125, unrelated), a second Narrative_Voice.md chunk (0.114), and `02_Novels/02_WrymWretch.md` (0.112). All scores are low-to-moderate and driven entirely by shared *mode-level* vocabulary (drowned/hungry/twin/tide/elemental-balance as genre furniture), not by any shared name, place, or specific cosmological mechanism. No hit contains Sevrain, Yrsa, Corvin, or the "un-becoming tide" mechanic.

Then ran targeted proper-noun searches:

```
python tools/vault_search.py search "Sevrain" --top 5 --json
python tools/vault_search.py search "Yrsa" --top 5 --json
python tools/vault_search.py search "Corvin" --top 5 --json
```

Result: all three returned **empty result sets** — none of this draft's three named entities appear anywhere in the vault's indexed content. This confirms the names are original to this piece and do not collide with any existing vault character, place, or god name, including within the Wyrmreach material.

**Conclusion:** the thematic overlap with WrymWretch/Wyrmreach (twin-bond souls, elemental/memory imbalance, hungry-vs-grieving elemental forces) is exactly the kind of shared *mode convention* CLAUDE.md's Graknox/Wyrmreach precedent warns against over-reading as a project tie. The search results support only a mode-level echo, not a textual or naming connection. No project tie is asserted in the draft, and none should be added.

## 2. Proper-noun / cosmology-term cross-check against references.md's do-not-reuse list

Grepped `draft.md` directly for every term on the explicit list: Thalen (of Cedarheart), Sylvan, Aeris Galewing, Aetherius, Rhyla Mosswhisper, Gaia, Lunessa Tidecaller, Aquatica, Kael Duskbane, Umbra, Seraphyne, Astraia, Shallock Izladar, First Light, Sun's Roaring Anger, Moon's Silent Tear, the Luminary Priory, the Astral Expanse, Remnants of Izladar, Wyrmguard, Circle of Seasons, Tidecallers, Stonekeepers, Galechanters, and "Wyrmreach" itself (case-insensitive).

Result: **zero matches**. The draft's own vocabulary (Sevrain, Yrsa, Corvin, "the widow's tongue" bell, "un-becoming," the drowned court/strait) is fully original and distinct from the Wyrmreach lexicon.

## 3. Voice/structure and restraint check

- **Third-person past tense:** confirmed throughout.
- **Simile-dense nature/light/water language:** confirmed and consistent with the mode's voice notes.
- **POV / section-break discipline — issue found and fixed:** the outline's craft rule ("No mid-scene POV head-hopping — alternate by section break, not within one continuous scene") was violated in three places in the original draft, where Yrsa's and Corvin's interior states were both narrated within a single unbroken paragraph/scene once they converged (the strait meeting, the climax in the drowned court, and the aftermath). **Fix:** inserted a section break between each character's interiority beat in all three locations, so the alternation now happens by section break everywhere in the piece. Neutral, externally-observed lines describing both of them together ("Grief finished mourning. Hunger finished wanting...") were left un-split, since those are the narrator stepping back to describe the shared, external event, not head-hopping. The epilogue's alternating paragraphs were left as-is — separate times and places, not one continuous scene, so ordinary braided-epilogue structure rather than a violation.
- **Ethical-restraint / gratuitous-content check:** confirmed no gratuitous violence, sexual content, or exploitative material.

## Summary

One substantive fix made (POV/section-break discipline in three locations); the Wyrmreach-tie and forbidden-vocabulary checks both passed cleanly and are documented above with the specific searches run and their results, not just a pass/fail flag.
