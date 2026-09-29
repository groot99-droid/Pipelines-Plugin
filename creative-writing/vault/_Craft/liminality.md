---
title: "Craft note — Liminality"
type: craft-note
provenance: "Analysis of the vault's works, written with Claude. Not the author's prose. Quotations from the works are checked against their files."
register: liminal
tags: [craft-note, register/liminal]
---

Back to [[_Craft/_index|Craft notes]]. Register config: `registers.liminal` in `pipeline/spec.yaml`. Plot-logic background: [[_Craft/plot-logic]].

# Liminality

## What the register means here

A story of **thresholds**: a boundary is crossed, held, and maybe recrossed, and the *surface stays ordinary while the rules do not*. The register's state column is `Place`:

`outside → crossing → between → inside`, and `back`

It may begin `outside` or already `between` (The Yellow Drop does). It must contain a `between`: a crossing with no in-between is a teleport, not a threshold. The exit is decided before the entry: `back` earns **return-with-residue**, `inside` earns **no-return** or **handoff**.

## What the vault does

The vault writes liminality constantly and names it almost never. The word "liminal" occurs in three works, once each: "For a moment, he simply stood in that liminal space, neither fully arrived nor fully departed." ([[02_Novels/02_WrymWretch|WrymWretch]], on a tide line, "a narrow, shimmering boundary between sea and land"); "There was something liminal about it, something that made me feel suspended between versions of myself." ([[09_Dream_Journal/01_Dream_Journal|Dream Journal]]); and "the liminal hour of 2:22" ([[09_Dream_Journal/02_Trip_Tracker_-_July_Fourteenth_2023|Trip Tracker]]). Everything else is done with devices, and the devices are consistent enough to list.

| Device | Where | The vault's own words |
|---|---|---|
| **A clock keeps the door** | [[03_Stories/07_Project_-_Man_Eater\|Man Eater]]; Trip Tracker; [[03_Stories/03_The_Yellow_Drop_and_The_Plain_Before_Sound\|The Yellow Drop]]; [[04_Book_Concepts/04_The_Bloody_Alarm_Clock\|The Bloody Alarm Clock]]; [[04_Book_Concepts/02_Missing_Campsites\|Missing Campsites]] | "Do not, under any circumstances, leave this room after 10:00 precisely."; "the liminal hour of 2:22"; "The alarm is buzzing."; the phones "show no signal, no time, no date" |
| **Ordinary surface, wrong rules** | Missing Campsites; Man Eater; [[04_Book_Concepts/08_The_Show_Must_Go_On\|The Show Must Go On]] | "Not dangerous. Not dramatic. Just wrong."; hallways "each about 4 feet wide but a whopping 15 feet high"; "before long it just becomes normal for him" |
| **Crossing by reading, unmarked** | [[02_Novels/05_The_Endless_Temple_-_Elaris_Sel_Marden\|The Endless Temple]] | a tea that makes scholars "more vividly imagine, if not envision, the book they were reading so clearly it was as if they were the narrator"; the text then slides into "My hand shot up almost by instinct" with no scene break |
| **Point of view is the threshold** | The Yellow Drop | "The point of view slid outward, smooth as breath — from the ear's inner creation to the dim room beyond the eyelids." |
| **A cut with no transition** | [[03_Stories/09_Low_In_The_Water\|Low In The Water]] | a boat in a marsh becomes a Waffle House mid-sentence: "as the boat shot through  The Waffle House sign flickered" |
| **Descent** | [[03_Stories/01_A_Journey_Into_the_Soul\|A Journey Into the Soul]] | "The pupil is not an opening. It is a geological event."; "Gravity weakens. Pebbles drift upward." |
| **Worlds inside worlds** | The Endless Temple; A Journey Into the Soul; [[05_Worldbuilding/01_People_of_the_Bark\|People of the Bark]] | "every book was alive, and inside of it, an entire universe"; "Every eye contains a universe."; "Even the smallest world is a universe to the ones who live in it." |
| **Return with residue** | Dream Journal; Trip Tracker; The Yellow Drop | "Even when I opened my eyes, the dream didn't end. It hovered. It waited. It asked for a vow."; "the echo of that sound-born world lingers" |

Two of these are worth naming as techniques rather than images. **The clock-keyed door** is the vault's most consistent liminal signature and appears in the horror, the visions and the hypnagogic pieces alike. And **the unmarked frame slip** (The Endless Temple's tea; The Yellow Drop's point-of-view slide) is done twice, deliberately, and the annotation of the former calls it "the chapter's central craft risk": nothing marks the crossing except a setup two paragraphs earlier.

## What the vault lacks

**No comparable description.** The annotations describe each crossing well and then coin a name for it that no other annotation uses: `closed-loop-waking-frame` (Yellow Drop), `frame-narrative-within-narrative` (Endless Temple), `reality-genre-bleed` and `unreliable-perception-onset` (Show Must Go On), `dream-bleed-into-waking` (Alarm Clock). Across all 63 annotations, 163 of 175 pattern names are used exactly once, so no query can gather the liminal works.

**A tag that means two things.** The chunk vocabulary's only liminal word is the motif `threshold`, applied to 37 chunks in 21 works. It is applied to the tide line in WrymWretch and also to an essay chapter preview ("we will step across the threshold of the second pillar", [[01_Books/01_The_First_Friend|The First Friend]]) and a poem ("standing at the threshold of becoming what you were", [[07_Poems_and_Prose/05_Inherited|Inherited]]). One tag covers the image and the event, so a search for a crossing returns a metaphor. The tagger even filed the WrymWretch tide-line chunk under `plot=denouement`, the nearest available tag, though the passage sits near the opening of Chapter One. The vocabulary changes in this batch split it: `threshold-crossing` and `liminal-hold` for the event, `threshold` left for the image.

**No home for the voice.** Six of the works above are `unclassified` in their frontmatter (The Yellow Drop, A Journey Into the Soul, The Show Must Go On, Dream Journal, Trip Tracker, People of the Bark), and the pipeline treats `unclassified` as deliberately not implemented ([[CLAUDE.md]]: ask which register the author wants). Structure can now come from a register, but the *voice* of these pieces still has no mode. See [[_Craft/psychedelia]] for the pattern the voice shares, and the open question about a fifth mode.

## Worked ledger

#### Causal ledger — The Yellow Drop and The Plain Before Sound

Mode: unclassified
Register: liminal
Expect: pass

| # | Link | Because | Beat | Response | Place | Changes |
|---|------|---------|------|----------|-------|---------|
| 1 | open | - | In the first morning the ear holds only a pale, waiting surface: a blank stretch that feels more like potential than space. | none | between | There is a blank plain of potential and nothing else. |
| 2 | T | 1 "blank plain" | A yellow drop of sound falls and ripples outward in warm rings. A feather-light note follows, then a deep weighted tone, then a bright chime that breaks open the horizon. | none | between | The plain has ripples, depth and direction. |
| 3 | T | 2 "depth and direction" | Sounds fall at irregular intervals: silver ticks, red thuds, blue hums. Where they cross, new patterns form. "This was not light painting a scene. This was sound building one." | none | between | Sound has built architecture: pillars, arches, corridors of pressure and rhythm. |
| 4 | T | 3 "corridors of pressure and rhythm" | The rhythm quickens, not frantic but inevitable, like a tide rising toward shore. The whole sound-world leans forward at the edge of revelation. | none | between | The world is poised on a final drop. |
| 5 | B | 4 "a final drop" | The final drop falls, bright and impossibly clear, and the body opens its eyes. The sound-architecture collapses in an instant. | none | crossing | The world that the drops built is undone by the drop that completes it. |
| 6 | T | 5 "the drop that completes it" | The point of view slides outward to the dim room beyond the eyelids. The alarm is buzzing and the morning has begun; for a heartbeat the echo of that world lingers. | none | back | The world is gone and only its echo remains. |

Ending: return-with-residue

Two things this ledger shows. First, **causality does not need a protagonist**: no one acts in this piece (every Response is `none`), and it still chains, because each layer of sound is the ground the next layer stands on. The only **but** is the ending, and it is the right one: what the world leaned toward is exactly what ends it. Second, its annotation calls the ending "tidy rather than haunting" ([[_Annotations/03_Stories/03_The_Yellow_Drop_and_The_Plain_Before_Sound]]), which is true and is the point: in this register the closed loop with residue is the native ending, not a soft one. The horror mode's rule against tidy endings must not be carried over. (The ledger for [[_Craft/cosmic-horror|Missing Campsites]] shows the same story shape ending the other way, in no-return.)

## Guidance for writing in this register

- **Name what opens the door**, in the `Changes` of the `crossing` row. Sleep, reading, a rule broken at a set hour, a cut. Use a clock or a count unless you have a better door; this vault has used a clock every time.
- **Keep the surface ordinary.** The `between` rows are where the register lives. The wrongness is that nothing looks wrong.
- **Decide the exit first.** Return with residue (something carried back, most of it lost) or no return. A return that loses nothing is a rescue, and in a horror mode it is forbidden.
- **Do not confuse the image with the event.** A character who stands at a threshold in a figure of speech has not crossed one.
