---
title: "Craft note — Cosmic (Lovecraftian) design"
type: craft-note
provenance: "Analysis of the vault's works, written with Claude. Not the author's prose. Quotations from the works are checked against their files."
register: cosmic
tags: [craft-note, register/cosmic]
---

Back to [[_Craft/_index|Craft notes]]. Register config: `registers.cosmic` in `pipeline/spec.yaml`. Plot-logic background: [[_Craft/plot-logic]].

# Cosmic (Lovecraftian) design

## What the register means here

Lovecraftian design is not tentacles. Its engine is **a ladder of knowledge that costs**: an investigator meets an anomaly, tests it, learns that the thing is larger than the frame they were using, and cannot un-learn it. The threat is indifferent rather than malicious. The register's state column is `Knows`, and it can only rise:

`unaware < anomaly < pattern < scale < implicated`

Each rung should be earned by an act (**T**: look, test, ask, count) that lands as a **B** (what is found breaks the current shelf). `implicated` is the vault's own top rung, and it is not standard Lovecraft: the protagonist is the entry, the hand, the thing.

## What the vault does

The vault never uses the vocabulary. "Lovecraft" returns no results, and "unknowable", "eldritch" and "madness" occur in no work. What it has, it has under other names, and almost all of it is one rung of the ladder rather than the whole ladder.

| Rung | Where it lives | The vault's own words |
|---|---|---|
| anomaly, shelved | The catalogued-incident engine of the horror-prose mode | "he had been in worse places" ([[03_Stories/07_Project_-_Man_Eater\|Man Eater]]); "It's just a crazy coincidence" ([[03_Stories/08_Following_The_Sheep\|Following The Sheep]]) |
| pattern | Keys and rules | "Do not, under any circumstances, leave this room after 10:00 precisely" (Man Eater); 66 floors, 666 offices (Following The Sheep) |
| scale, as erosion | [[04_Book_Concepts/02_Missing_Campsites\|Missing Campsites]] | "They just don't exist." / "No one even remembers they were there." |
| scale, as conspiracy | [[05_Worldbuilding/02_The_Redacted_Testament_of_Lira_Calyx\|The Redacted Testament of Lira Calyx]] | "The model is brilliant; the data are compromised." |
| scale, as object | [[04_Book_Concepts/04_The_Bloody_Alarm_Clock\|The Bloody Alarm Clock]] | "The clock doesn't measure time. It consumes it." |
| implicated | Man Eater, Following The Sheep, and the found-document frame | "Follow in my footsteps, and you will become me." (Man Eater); "You are one of us now." (Testament) |

Three findings that shape the register:

**1. The best inquiry engine in the vault is not in the horror mode.** [[05_Worldbuilding/02_The_Redacted_Testament_of_Lira_Calyx|The Redacted Testament of Lira Calyx]] is classified epic-fantasy. It has the whole ladder: a first anomaly (a waveform "she cannot explain"), a hypothesis, forensic archive work, a conspiracy, and then the Lovecraftian turn: the investigator's own method is the trap ("The model is brilliant; the data are compromised."). It has a **found-document frame with tampering as a beat** (marginal notes in a second hand, overwritten pages, redaction bars; the chunk tagger had suggested `textual-tampering` and `marginal-annotation` for exactly these, and the suggestions sat unadopted in its log). And it ends by implicating the *reader*: "If you understand even a fraction of what she wrote, you are infected with the truth." Its annotation names the patterns `found-document-testament`, `unreliable-marginalia` and `incomplete-victory-ending`, and its type is worldbuilding. It is the template for this register and nothing in the vault knows it.

**2. The short horror mostly has no inquiry.** In [[03_Stories/07_Project_-_Man_Eater|Man Eater]] the protagonist investigates exactly once, at the end, when he and Jax follow the call past "the point of no return". In Following The Sheep he never tests anything; each anomaly is "noted, flinched at, then rationalized away" (see [[_Annotations/03_Stories/08_Following_The_Sheep]]) and then he is compelled. The Missing Campsites pitch has the campers observe, never test. This is not a flaw in those pieces; it is what `escalation-by-catalogued-incident` is. It does mean the vault's horror knows the *top* of the ladder (you are the thing) far better than the middle rungs, and the register exists to supply the middle.

**3. The vault's cosmic scale is humane.** [[05_Worldbuilding/01_People_of_the_Bark|People of the Bark]] is cosmic indifference told as comedy: a squirrel landing on the trunk is a cataclysm ("Meanwhile, the squirrel is just scratching an itch"), and a human hand is "the arrival of a god" to them and "someone checking for termites" to us. Its moral is the opposite of Lovecraft's: "Even the smallest world is a universe to the ones who live in it." The device is the same (a frame so large that the thing acting on you does not notice you); the verdict is not. A cosmic piece written in this vault inherits that ethic through [[CLAUDE.md]]'s restraint precedent: the victims keep their interior lives. Scale takes away the protagonist's importance, not their dignity.

## How the two layers of the vault describe this

The vault has two ways of describing a work's structure and they fail in opposite directions. **Annotations** are rich and specific: [[_Annotations/04_Book_Concepts/02_Missing_Campsites]] names `erosion-of-consensus-reality` and `cosmic-horror-reveal`; [[_Annotations/05_Worldbuilding/02_The_Redacted_Testament_of_Lira_Calyx]] names `unreliable-marginalia`. But 163 of the annotations' 175 pattern names are used exactly once, so no pattern connects two works and nothing can be compared. **Chunk tags** are a closed vocabulary and so are comparable, but it contains no word for any rung above `anomaly`: the nearest tags are `existential-dread`, `paranoia` and `unreliable-reality`. The vocabulary changes in this batch add the rungs (see `_ChunkTags/vocabulary.yaml`).

## Worked ledgers

Each ledger is checked by `pipeline/tests/test_craft_notes.py` against its `Expect:` line. Beats and Changes are Claude's summaries; quoted words are the works' own.

#### Causal ledger — Project: Man Eater

Mode: horror-prose
Register: cosmic
Expect: pass

| # | Link | Because | Beat | Response | Knows | Changes |
|---|------|---------|------|----------|-------|---------|
| 1 | open | - | Fisk, a new recruit, arrives at a base in the North Dakota woods. It is armored to keep things in, the crew look sick and slightly anorexic, there are claw marks on the walls, and it is colder inside than out. | denies | anomaly | He shelves all of it: "he had been in worse places". |
| 2 | T | 1 "worse places" | Sam, the head of the project, gives him three rules: a strict diet, never leave the room after 10:00 precisely, never leave the base. | complies | anomaly | Three rules bind him: the cafeteria diet, in his room at 10:00 precisely, never leave the base. |
| 3 | T | 2 "10:00 precisely" | At 10:00 a low, flute-like call sounds. Fisk feels scared and comforted. His skeletal bunkmate gets up and walks out. Fisk does not stop him. | complies | pattern | The bunkmate is gone, Fisk let him go, and he feels drained. |
| 4 | T | 2 "the cafeteria diet" | The cafeteria meal makes him hungrier the more he eats. By afternoon his ribs and knuckles show. He files it as a body reacting to a new climate. | denies | pattern | He is hungrier and visibly thinner, and he has filed it as climate. |
| 5 | B | 3 "let him go" | Sam says the bunkmate was transferred after a conversation around 10:00, a conversation Fisk knows never happened. | denies | pattern | Sam's account is a lie, and Fisk knows it. |
| 6 | T | 5 "a lie" | The call comes again and this time it calls him. With his new bunkmate Jax he follows it down the hall as the air freezes, past the point of return. | investigates | pattern | They are following the sound together, and frostbite has begun. |
| 7 | B | 6 "following the sound" | Around the corner a pale man stands near the ceiling, playing a flute: "Beware the Windigo, for I am he." He vanishes. Fisk's skin tightens on his bones. | none | scale | The thing has told him what he is becoming, and his body agrees. |
| 8 | B | 7 "what he is becoming" | Gassed and tied to a stalagmite, Fisk hears Sam explain: the base sits on the first recorded birthplace of a Windigo, and the crew are fed flesh and chemicals to speed the curse for his superiors. | resists | scale | The curse is a harvested programme, and Fisk is the next test subject in a line of them. |
| 9 | T | 8 "the next test subject" | He wakes transformed, a tube in his arm, his amputated parts on a table. His thoughts go blank and animal. He knows it will spread and that he will never take revenge. | none | implicated | He is the thing, kept like "an animal in a zoo", and it will spread. |

Ending: consumed

Two findings. The **Response** column reads denies, complies, complies, denies, denies, then one `investigates`, then none, none, none: an agency curve that thins to nothing, which is the mode's "transformed, consumed, or made complicit" written as data. And row 4 is a **callback** (it answers rule one from row 2, two beats earlier), the only place the story pays off something it set up. The `Knows` column shows why the ending works: it climbs one rung at a time, and the last rung is the protagonist.

#### Causal ledger — The Redacted Testament of Lira Calyx

Mode: epic-fantasy
Register: cosmic
Expect: pass

| # | Link | Because | Beat | Response | Knows | Changes |
|---|------|---------|------|----------|-------|---------|
| 1 | open | - | Book I. Lira Calyx, a field scientist, trusts method. On the third night she records the Spore-Weavers pulsing like a single organism, with a waveform no known driver explains. | investigates | anomaly | She has an unexplained waveform and has named it Pattern alpha. |
| 2 | B | 1 "unexplained waveform" | A marginal note appears in a different hand: "Phase offset miscalculated." She writes, "Who wrote this?" and gets no answer. | investigates | anomaly | Someone else is in her notebooks, correcting her. |
| 3 | T | 1 "unexplained waveform" | Anomalies accumulate. She formalises Hypothesis 1, that aetheric gradients bias evolution upward, and publishes a cautious note. A patron threatens her, a redaction appears in the official logs, and she leaves with a crystalline fragment. | investigates | pattern | Publishing drew a threat and a redaction, and she carries the fragment. |
| 4 | T | 3 "the fragment" | Book II. She follows the fragment into archives and labs: a consortium that stopped operating months before the Convergence, isotope ratios that are not natural, a note behind a console reading "She's close. Move the logs." Her brief on engineered catalysts is redacted and she is branded a saboteur. | investigates | scale | The world was engineered, and the truth is being redacted as fast as she finds it. |
| 5 | B | 4 "being redacted" | Book III. She infiltrates the Continuum's outposts. The engineer she trusted betrays her, and the logs she stole turn out to be overwritten with false timestamps and fabricated readings. | investigates | scale | Her own data streams are being sabotaged, and someone she trusted sold her out. |
| 6 | T | 5 "her own data streams" | Her journals are tampered with. A page she thought she wrote reappears in the archive with a second set of annotations in another hand, nudging her away from a fatal assumption. | none | scale | A second hand is shadowing her pages and warning her off a fatal assumption. |
| 7 | B | 6 "a fatal assumption" | Book IV. She builds a coalition and fires the pulses her model prescribes. "The model is brilliant; the data are compromised." The result is a pause and a partial catastrophe, and she is taken. | chooses | scale | The method itself was the trap: the world is worse off and she is gone. |
| 8 | T | 7 "the method itself was the trap" | The final chapter is a found document. The archivist confesses to the marginal notes: they followed Lira, arrived too late, and stole the books out of guilt. | none | implicated | The archivist is implicated, having watched her taken and kept her work. |
| 9 | T | 8 "kept her work" | The archivist turns to the reader: "If you understand even a fraction of what she wrote, you are infected with the truth." "You are one of us now." | none | implicated | The reader has read it and cannot un-read it, and is now a target. |

Ending: irreversible-knowledge

The whole ladder, one rung at a time, with an act of inquiry on almost every row. Row 7 is the piece the short horror lacks: a competent test that *can fail*, and fails because of something the investigator could not have known. Row 9 moves the top rung from the protagonist to the reader. When this ledger was first checked, epic-fantasy's allowed endings did not include `irreversible-knowledge`, so the mode's own worked example would have been flagged by its own rule; the mode's list was widened.

#### Causal ledger — Missing Campsites, as pitched

The pitch is the author's and is unchanged. This ledger reads it as written. Row 3 and row 4 have no antecedent in the pitch: each morning simply removes more.

Mode: horror-prose
Register: liminal, cosmic
Expect: fail

| # | Link | Because | Beat | Response | Place | Knows | Changes |
|---|------|---------|------|----------|-------|-------|---------|
| 1 | open | - | Campers pull into a remote national-forest campground for a quiet weekend. The first campsites, the ones at the entrance, simply are not there, although the map shows them and the signs point to them. | none | outside | anomaly | The map and the land disagree, and the land is empty. |
| 2 | B | 1 "the land is empty" | The campers are unsettled, but rangers, families and hikers act as if nothing is missing. | none | crossing | anomaly | Nobody else sees the loss, and the campers know it. |
| 3 | A | - | The next morning more campsites have vanished. No one notices, no one cares, no one remembers they were there. Except the campers. | none | between | pattern | More of the campground is gone and only the campers remember it. |
| 4 | A | - | By the end of the second day the whole campground has been erased except the last five sites, where the campers are staying: the only fixed points in a landscape quietly unravelling. | none | between | scale | Only the campers' five sites are left, as the only fixed points. |
| 5 | B | 4 "the only fixed points" | The final morning: the sky is wrong, the air heavy, the trees in patterns that should not exist, and the phones show no signal, no time, no date. They have slipped into a different dimension that has been pulling them in since they arrived. | none | inside | implicated | They did not lose the campsites: they were being drawn in, piece by piece, from the start. |

Ending: no-return

The checker gives two errors (rows 3 and 4 are and-thens), one warning (`no-investigates`), and one note (no callbacks). The vault's own annotation already says why: "each day removes a fixed point from the world ... instead of introducing a threat, so dread accumulates through subtraction" ([[_Annotations/04_Book_Concepts/02_Missing_Campsites]]). That is a countdown, and a countdown is an and-then by construction: the schedule does the work, not the campers. Rows 1, 2 and 5 are good. Row 5 is a real **but**: it reinterprets "the only fixed points" as the last things to be drawn in.

#### Causal ledger — Missing Campsites, an illustrative repair

This is not a proposal for the book. It is Claude's demonstration of what the mechanism does to a countdown: it keeps every image in the pitch and replaces the schedule with the campers' own attempts, each of which fails in a specific way.

Mode: horror-prose
Register: liminal, cosmic
Expect: pass

| # | Link | Because | Beat | Response | Place | Knows | Changes |
|---|------|---------|------|----------|-------|-------|---------|
| 1 | open | - | Campers arrive at a remote campground for a quiet weekend. The first campsites, the ones at the entrance, are not there, though the map shows them and the signs point to them. They walk to where the sites should be. | investigates | outside | anomaly | The map and the ground disagree, and only the ground can be walked. |
| 2 | B | 1 "the map and the ground disagree" | They ask a ranger. The ranger reads the same map and sees nothing missing, and so do the families and hikers. | investigates | crossing | anomaly | Their memory is the only record that the sites ever existed. |
| 3 | T | 2 "only record" | To hold on to evidence they photograph the next sites and tie a marker to the last one on the loop. | investigates | between | pattern | There is a marker on site 12 and a photograph of it. |
| 4 | B | 3 "a photograph of it" | The next morning site 12, the marker and the photograph's clearing are gone: the photo shows a clearing that has never been anything else. | denies | between | scale | The world rewrites its own evidence, and only the campers are left over. |
| 5 | T | 4 "left over" | They stop trusting proof and trust each other: they stay together on the last five sites and agree to drive out at first light. | flees | between | scale | The five sites are all that is left, and they are planning to leave. |
| 6 | B | 5 "planning to leave" | At first light there is no road to the entrance and no entrance. The sky is wrong, the trees stand in patterns that should not exist, and the phones show no signal, no time, no date. | none | inside | implicated | They did not lose the campsites: they were being drawn in, piece by piece, from the moment they arrived. |

Ending: no-return

Row 4 is the row the pitch was missing: the test that could fail, and fails by rewriting the evidence. It is Lovecraft's move (the record cannot be kept), and it turns the escalation from "more disappears" into everything they try being undone. The ending's beat is unchanged.

## Guidance for writing in this register

- **Earn the rungs.** A rung with no act of inquiry under it is exposure, not knowledge. Do not skip a rung; the checker warns when the ladder jumps.
- **Vault voice, not baroque voice.** [[CLAUDE.md]] bans multi-paragraph description, and this vault's cosmic dread is by subtraction and flat register ("Not dangerous. Not dramatic. Just wrong."). Render the unnameable by the failure of the catalogue, not by extended description.
- **The frame can be a beat.** A log, a testament or a manuscript is the natural frame. If it is tampered with (marginal notes, overwritten entries), the tampering is a beat and belongs in the ledger.
- **Keep the victim.** The restraint precedent applies at any scale: the protagonist is more than a device for the reveal.
- **Choose the horror's verdict.** The vault has both: indifference that erases (Missing Campsites) and indifference that is a squirrel scratching an itch (People of the Bark). Decide which one the piece is.
