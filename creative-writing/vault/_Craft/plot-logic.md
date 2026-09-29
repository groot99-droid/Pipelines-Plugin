---
title: "Craft note — Plot logic (but / therefore)"
type: craft-note
provenance: "Analysis of the vault's works, written with Claude. Not the author's prose. Quotations from the works are checked against their files."
tags: [craft-note, plot-logic]
---

Back to [[_Craft/_index|Craft notes]]. The rules are in [[CLAUDE.md]] (section "Plot logic"); the machine-readable form is `pipeline/spec.yaml`; the checker is `pipeline/plot_logic.py`. This note explains the rule and shows it working on the vault's own pieces.

# Plot logic: but / therefore, never and-then

## The rule

Between any two plot beats there is either a **but** (this beat defeats what the last one left behind) or a **therefore** (this beat happens because of it). **And then** is the failure: the second beat did not need the first, so the story is a list.

Three tests, one per link:

| Link | Test |
|---|---|
| **T** therefore | Delete the earlier beat. If this beat can still happen the same way, it is not a therefore. |
| **B** but | Without this beat, the earlier beat's outcome would have held. If it would not have, it is not a but. |
| **A** and then | Swap the two beats. If nothing is lost, it is an and-then. |

Each beat carries a **Changes** cell: what is now irreversibly different afterward. The next beat must push on something written there, and its **Because** cell names it: the earlier beat's number plus a phrase copied from that beat's Changes. The checker verifies the phrase is really there, in the same spirit as the vault's rule of verifying quotations. It cannot judge whether a link is *true*; it can make a link that is not anchored to anything impossible to hide.

## What the vault's own engine looks like through this rule

[[CLAUDE.md]] describes the horror engine as "a numbered or listable sequence of discrete, escalating wrongnesses the protagonist notices and mentally shelves before the next one stacks on". Read causally, that is already a but/therefore engine with one link left unspecified: the incident is a **but** (it breaks the current explanation), the shelving is a **therefore** (the protagonist's answer to it), and the next incident should be a **but** against *that* shelf. "Stacks on" does not say the next incident must break the last shelf, only that it comes next. When it does not, the incidents are independent, and the escalation is an and-then in a horror costume.

Two things the ledger makes visible that the annotations only describe:

- **Agency decay.** The annotation of [[03_Stories/08_Following_The_Sheep|Following The Sheep]] notes that the prose degrades Shaun's agency in stages ("motor skills were no longer under his control", then "a mere passenger in his own body"; see [[_Annotations/03_Stories/08_Following_The_Sheep]]). The ledger's **Response** column turns that into a curve you can read down a page: denies, complies, complies, none.
- **The missing inquiry.** Most of the short horror has the protagonist notice and shelve but almost never test. See [[_Craft/cosmic-horror]].

## Worked ledgers

Each ledger below is checked by `pipeline/tests/test_craft_notes.py` against the verdict on its `Expect:` line. The beats are summaries and readings by Claude, marked as such; the quoted words are the works' own.

#### Causal ledger — The Bloody Alarm Clock

Mode: horror-prose
Expect: pass

| # | Link | Because | Beat | Response | Changes |
|---|------|---------|------|----------|---------|
| 1 | open | - | An ordinary person inherits an old bedside clock. It never rings aloud, but every night it plays inside their head. | none | Each night the clock drags them into a vivid nightmare. |
| 2 | T | 1 "vivid nightmare" | The dreams escalate: drowning, losing blood, mysterious internal pain. Every morning carries a real-world echo of what they dreamed. | denies | Their body repeats what the dream did, and their ears begin to bleed when they wake. |
| 3 | T | 2 "ears begin to bleed" | They try to be rid of it: throwing it away, smashing it, leaving it behind. | flees | Every way of getting rid of it has been tried. |
| 4 | B | 3 "every way of getting rid of it" | The clock always returns: on the nightstand, in a dream, in a place they do not remember putting it. | none | The clock is choosing them, not the other way around. |
| 5 | T | 4 "choosing them" | They avoid sleep entirely. Exhaustion brings waking hallucinations as real and as terrifying as the nightmares. | flees | The line between dream and reality dissolves, and the ticking is constant. |
| 6 | B | 5 "the ticking is constant" | The truth arrives: "The clock doesn't measure time. It consumes it." | none | They know what it is, and that it will take the last of their time. |
| 7 | T | 6 "the last of their time" | When it takes the last of theirs, the clock quietly moves on and appears in the home of its next unsuspecting owner. | none | The cycle begins again with someone else. |

Ending: handoff

This is the vault's cleanest but/therefore engine, and it is a pitch, not a story. Every remedy is a therefore ("throwing it away, smashing it, leaving it behind") and every return is a but ("the clock always returns"). Nothing here needed fixing; the ledger only names what the pitch already does. Compare the pieces below, where the same reading finds the seams.

#### Causal ledger — The Nightly Inventory (retrofit of an Idea Library outline)

This is one of the pipeline's own outputs, [[_Idea_Library/2026-09-18_the-nightly-inventory/outline|outline.md]], read back into a ledger. The labelling is Claude's reading of that outline; the author may read a link differently, and that disagreement is exactly what the ledger is for.

Mode: horror-prose
Register: cosmic
Expect: fail

| # | Link | Because | Beat | Response | Knows | Changes |
|---|------|---------|------|----------|-------|---------|
| 1 | open | - | The lamp's beam drops a beat early. He explains it as bulb warm-up and files a maintenance line. | denies | anomaly | He logs it instead of climbing up to look: the first choice to log over look. |
| 2 | A | - | A gull that has landed on the same rail every evening will not land tonight. He blames a weather front. | denies | anomaly | The gull's absence is filed as a weather front, and the rail is empty in a wind too mild to explain it. |
| 3 | A | - | The lamp-room door he double-checked is open again. He blames his own forgetfulness and starts checking it twice, then three times, logging the count. | denies | anomaly | The first entry that indicts him rather than the station: he now logs how often he checks the door. |
| 4 | B | 2 "the gull" | He finds a page about the gull in his own hand, with a wingbeat count he had no reason to count. He blames sleepwalking: "Note to self: sleep more." | denies | pattern | The log holds an entry with no memory attached to it. |
| 5 | T | 3+4 "no memory attached" | He starts counting fixed things (stair treads, lamp panes, the interval between wave-sets) as a private check against the handwriting. The counts disagree with the night before, for things that cannot change. He shelves it as eye strain and logs the counts too. | investigates | pattern | The log is now bigger than the job it serves, and eye strain is the only explanation on file. |
| 6 | B | 5 "eye strain" | In a supply chest he finds a predecessor's logbook, decades old: the same incidents, in the same order, some sentences verbatim. He does not report it. He burns the old log instead of the new one. | complicit | scale | The old log is ashes and nothing has been reported to the mainland. |
| 7 | T | 6 "the old log" | New lines appear in the current log, written in the hours he was asleep or at the lamp, in a hand almost his. He checks the log more than he checks the light. | investigates | scale | He no longer knows which entries are his, and the inventory has become the job. |
| 8 | B | 7 "which entries are his" | He decides to burn this log too, to end the list by ending the object, and finds an entry already there, in the past tense, describing the attempt before he made it. | resists | scale | Shelving fails outright, and the list grows without his permission. |
| 9 | T | 8 "without his permission" | The relief keeper arrives, opens the log and finds the last page occupied by a fresh first entry in the old keeper's hand: the opening line, now the new keeper's own. | none | implicated | The loop closes: the old keeper's hand wrote the trap forward, and the new keeper logs the first item as their own. |

Ending: cyclical

The checker's verdict is two errors, rows 2 and 3, and nothing else. The gull and the door are the outline's two independent incidents: neither depends on anything before it, so they could be swapped without loss. Everything from row 4 on is tightly chained, and row 4 is the best link in the piece because it reaches *back* to the gull. The fix is the outline's to make, not the checker's; one shape it could take is to let the gull matter *because* of row 1's outcome (he chose to log over look, so the first thing he does look at is the rail), and to let the door matter because the gull's absence was filed under weather (he goes to check the doors against the storm). Either repair turns an and-then into a therefore.

#### Causal ledger — The Two Who Woke the Sea (retrofit of an Idea Library outline)

From [[_Idea_Library/2026-09-18_the-two-who-woke-the-sea/outline|outline.md]], same caveat as above. Two threads open separately and a later row joins them, which is what ensemble-convergence looks like in a ledger.

Mode: epic-fantasy
Expect: pass

| # | Link | Because | Beat | Response | Changes |
|---|------|---------|------|----------|---------|
| 1 | open | - | Yrsa, a mourner-for-hire on the western coast, wakes mid-rite weeping for a love that is not hers. | none | She carries a stranger's grief over her own and feels a pull toward the kingdom's centre. |
| 2 | open | - | Corvin, a dock scavenger on the eastern coast, wakes emptying a larder and is still starving. | none | His hunger answers no meal, and he feels the same pull toward the kingdom's centre. |
| 3 | T | 1+2 "a pull toward the kingdom's centre" | A small tide-tremor un-becomes something minor near each of them: a boat, a bell, a half-forgotten name. Each leaves home. | chooses | Both have left home, and neither can go back to what the tremor un-made. |
| 4 | T | 3 "left home" | The crossing, told in images: grief argues with Yrsa to sit down and let the tide take what it wants; hunger argues with Corvin to seize and hoard. Each begins to address the other as the other shore of me. | resists | Each speaks silently to the other as the other shore of me. |
| 5 | T | 4 "the other shore of me" | They meet for the first time at the strait, on the falling tide, before it turns. | none | They stand together at the strait with the tide about to turn. |
| 6 | T | 5 "the tide about to turn" | In the drowned ruin beneath the strait they neither fight nor flee: they finish what Sevrain could not, grief mourning all the way through and hunger setting down what it was reclaiming, in the same moment. | chooses | The rite is complete and the third rising is turned aside. |
| 7 | T | 6 "the rite is complete" | The completed rite draws off the bond that let them find each other: a specific loss, to be decided in the draft. | none | They have lost the bond and part of what they knew of each other. |
| 8 | T | 7 "the bond" | The tide settles instead of rising. Ordinary again, each is later drawn to open water with a faint, wordless familiarity. | none | Two strangers drawn to the same water, with a faint familiarity and no name for it. |

Ending: cost-paid

It passes, with two warnings, and the warnings are the finding: **no but anywhere**, and **six therefores in a row**. Every step works. The outline compresses the crossing into a montage on purpose, which is a sound scope decision, but the consequence is that the climax's solution (they neither fight nor flee; they finish it together) is never preceded by an attempt that failed. It arrives as a revelation, not as the answer to something. Row 4 could be read as a but (grief and hunger argue with them), but even so the opposition is internal and nothing they *try* goes wrong. The vault's own twin-bond structure suggests the repair: let each try the rite alone first, grief mourning without hunger and hunger reclaiming without grief, and let both fail in a way that shows what the other half is for. Then "together" answers a failure.

## How to use it

```
python creative-writing/pipeline/plot_logic.py template --register cosmic     # an empty ledger
python creative-writing/pipeline/plot_logic.py check outline.md --mode horror-prose --register cosmic
python creative-writing/pipeline/plot_logic.py rules --mode horror-prose      # what the outline prompt is told
```

In a pipeline run the outline stage does this for you: it adds the rules to the prompt, checks the ledger it gets back, gives a failing ledger one repair pass, and writes the report beside the outline (`plot_logic_report.md`). A **register** (`liminal`, `psychedelic`, `cosmic`) adds one state column to the ledger and a few shape rules; see [[_Craft/liminality]], [[_Craft/psychedelia]], [[_Craft/cosmic-horror]].

## What it does not do

- It does not judge whether a link is true. A writer can quote a real phrase and still not depend on it.
- It does not apply to essays or poems on their own (their spine is argument and turn, not events). A register switches it on for any mode, because a register is a sequence of states.
- It does not replace the mode. The mode says how the piece sounds; the ledger says why each beat follows.
