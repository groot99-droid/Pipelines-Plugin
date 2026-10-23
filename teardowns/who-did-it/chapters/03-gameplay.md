# Gameplay and mechanics

A match of Who Did It is a loop of five phases: day, dusk, night, meeting, immunity. It runs between a
grace period at the start and a Final Night at the end ([[sec:GDD:3.3]], [[anchor:phases]]). The Cabal kills
after dark. The Village gathers clues, finishes tasks and votes. A cover role (Killer, Accomplice, Drifter)
walks in another card's character. Since round 6, a second layer of world systems surrounds that core:
resources and crafting, mobs, quests, a Daily Train and vendettas.

Your answers set this chapter's yardstick:
- the game should welcome **every way of playing**: watching, detecting, talking;
- **20 to 25 minutes** is a fine length;
- the ending should be **a short hunt, then a trial**;
- the world is **a second layer**, not just texture.

## Three ways to play, one table

**Describe.** You answered: "a mixture of all of those, so no matter how you choose to play there is a way".
The game already gives each style its own tools.

| Style | What it reads | Systems | Where it pays off |
|---|---|---|---|
| **Watcher** | Who was where, and who wears what | Scenes as rooms, doors that swing, public looks ([[dec:A49]]), the missing-person roll-call | "I saw two Bakers at dusk" |
| **Detective** | Physical evidence | 2 of 3 trait clues per kill, footprints (height), thread (scarf), felt (hat), Blood within 3 tiles, fingerprints, the Doctor's time of death ([[sec:GDD:3.4]]) | Verified entries on the Case Board |
| **Talker** | People | Meetings, Present one Claimed entry, the vote ([[sec:GDD:3.8]]) | The ejection |

The Case Board joins them. It intersects each body's verified traits with every living seat, and shows a
summary row per player instead of raw entries. In keeping with the "vote is the climax" pillar
([[sec:GDD:1]]), it never names anyone.

**Compare** (Claude's analysis). Blood on the Clocktower is the best model for "every style has a way". Each
role there gets a different *kind* of information: a count, a yes or no, a name. Even a quiet player brings
something to the table. Among Us splits its players differently. Taskers mostly ignore the talk, and the
talkers carry the meeting. That is why its meetings are often decided by two people. Your table
already looks more like Clocktower than Among Us, because the Doctor, the Child and the Butler each read a
different clue type.

**Critique** (Claude's analysis). A style survives only if it pays off *in the meeting*. Otherwise it is a
side game. Today two styles do not quite reach the meeting:
- **The watcher has no evidence slot.** A sighting ("two Bakers at dusk") can only be Claimed. A clue
  can be Verified. Give the watcher one verifiable fact: the Butler's Ledger (last house entered per player)
  is already that fact for one role. A shared "door log" for the scene you stood in would make it everyone's.
  It adds no leak, because you only log the doors you could see.
- **The talker has one Claimed entry per meeting.** That is the right limit. But nothing records who claimed
  what *across* meetings, and a lie in meeting 1 that is exposed in meeting 3 is the talker's best moment.
  A one-line history per seat on the Case Board would make that moment visible.

## How long a match runs

**Describe.** GDD §2 and §3.3 both promise "12-18 minutes" ([[sec:GDD:2]], [[sec:GDD:3.3]]). §3.9 names the
soak test's target: a median match of 12 to 18 minutes, and at most one third of matches reaching the
Final Night. The phase table in `balance.json` ([[data:balance]]) gives the following times for a match
that goes the distance:

| Part | Seconds |
|---|---|
| Role reveal and countdown | 23 |
| Grace, plus the map's opening (up to `openingS`) | 30 + up to 120 |
| 4 cycles of day 60, dusk 10, night 100 | 680 |
| 3 meetings: discussion 60 to 90, vote 25, reveal 8, immunity 15 | about 330 to 420 |
| Final Night hunt and forced vote | 90 + about 115 |
| Game over | 20 |

That comes to about 23 to 25 minutes. Every meeting that opens mid-cycle also restarts the cycle at a full
day, which adds more. A match that ends early, with all Cabal gone or parity reached, is shorter.

You said **20 to 25 is fine**.

**Compare** (Claude's analysis). Among Us rounds run 10 to 15 minutes. Town of Salem runs 15 to 30.
Werewolf at a table runs 30 to 60. A Friday-night group plays two or three matches in an evening at 20 to
25 minutes. That is a good rhythm, especially since a match's end puts everyone back in the same lobby.

**Critique** (Claude's analysis).
- **The docs promise a different game.** Two GDD sections and the soak's own target still say 12 to 18.
  Under the project's own rule ("a behaviour change is not done until `GDD.md` changes"), the target is now
  a decision to write down. Amend §2, §3.3 and §3.9 to 20 to 25, and change the soak target with them.
  Otherwise the soak will "fail" a match length you are happy with.
- **The opening cutscene is the cheapest cut.** It plays inside grace, for up to 120 s, every match. Showing
  it in full only on a party's first match on a map is the one change that shortens play without touching
  the game.

## The end: a short hunt, then a trial

**Describe.** If nobody has won when cycle 5 would begin, the Final Night replaces that day
([[sec:GDD:3.8]]):
- night lighting, and wolves in the village;
- every Knife's cooldown drops to 20 s;
- a 90 s hunt while clues still spawn;
- a forced vote with no Skip and the Case Board open. A tie ejects nobody, and the Cabal wins.

You want **both: a short hunt, then a trial**.

**Compare** (Claude's analysis). Among Us has no end phase. It ends on a count. Mafia's last day ("lynch or
lose") is a pure trial. Dread Hunger ends on a race. Your answer is closest to a courtroom drama's last act:
one burst of action, then the long speech. It suits "the vote is the climax" better than a 90 s hunt does.

**Critique** (Claude's analysis). This is a change of two numbers and one rule, and it needs a
decision row and a GDD edit in the same pull request:
- `finalNight.huntS` from 90 to about 45 s. The Knife's 20 s cooldown already makes two strikes likely, so
  a shorter hunt costs the Cabal little.
- A final discussion longer than the table's 60 to 90 s, perhaps 120 s. Give it its own key (for example
  `finalNight.discussionS`), so it is not the `byCount` value.
- Keep "a tie ejects nobody and the Cabal wins". It is what makes the trial tense.

## The world as a second layer

**Describe.** You chose the world as **a second layer**, a real game beside the deduction, not just texture.
Rounds 6 and 7 built it:
- **Resources and crafting** ([[sec:GDD:3.14]]): six resources at nodes in the forests, caves and camp, and six
  recipes.
- **Mobs** ([[sec:GDD:3.15]]): four creatures on leashes and paths, plus the night wolves.
- **Quests and mini-games** ([[sec:GDD:3.16]]): figures at scene spots who give quests (never seats), six
  quests and five mini-games.
- **The Daily Train** ([[dec:A113]]): on Hollowmere, each day the Train stops at the overworld platform.
- **Vendettas** ([[dec:A112]], [[sec:GDD:3.20]]): a secret side goal for a killer role, drawn per match.
- **Hunger**: a Killer who has not struck in two full rounds leaves glowing footprints of their own height
  ([[sec:GDD:3.3]]).

**Compare** (Claude's analysis). Dread Hunger and Project Winter build their hidden-role game on top of a
survival game, and both show the trade-off. The survival layer gives a quiet player something to do. But when
everyone is busy surviving, nobody watches anybody, and the traitor wins by default. Their fix was to
let survival make evidence: Project Winter's traitors are caught sabotaging generators.

**Critique** (Claude's analysis). A second layer works best when it produces evidence for the first.
- **Hunger already does it.** It turns "not killing" into a visible trail. It is the best example in the
  game of a world rule that feeds the deduction.
- **Crafting and quests mostly do not, yet.** A finished quest could stamp a Verified alibi ("Wren was at
  the mill when the giver paid her"). Crafting at a bench could leave a trace that a Detective can Dust. Each
  is a small change, and each turns the second layer into a source for the first.
- **The light tell in [[open:A89]] is that question in miniature.** A lit light says "not Cabal" unless
  it was crafted. Decide whether a light is in every start kit, the Killer's included. That decides whether
  crafting is a disguise.
- **The pillar at risk is "readable in 20 seconds".** A new player now meets roles, clues, the vote,
  resources, recipes, mobs, quests, a train and a vendetta. Teach the second layer later: Hollowmere's Small
  profile could open with quests only, and add crafting from the second match.

## Smaller mechanics

- **The missing-person roll-call** means a Killer who hides every body still faces a meeting. This is good
  design: it closes the "no reports, no game" hole that Among Us leaves to its players.
- **The anti-stall rules** ([[sec:GDD:3.8]]) apply after two meetings with no ejection: Skip is disabled, and
  ejection needs at least ceil(living/3) votes. The snowball guard ([[sec:GDD:3.9]]) changes the kill
  cooldown in the closing turns. Both are good, and both are invisible. Put one line on the board when one
  of them is active.
- **The Drifter** wins alone if it is ejected, and the match goes on. **Last Shot**: an ejected Gamekeeper
  fires at the reveal. Both make the vote matter beyond "find the Cabal". That is right for a mixed-style
  table.
- [[open:A112]]: the Bible's larger arcs (the Skin-Walk, the Dark Positions, Public Unrest, the Train
  robbery) wait for round 8's evolutions and laws (chapter 2).

## Owner's word

- 2026-10-23, *Is cover-spotting and "who was where" the heart of the game now?* "I am for it to be a mixture
  of all of those, so no matter how you choose to play there is a way"
- 2026-10-23, *A full match adds up to about 22 to 25 minutes, against the GDD's 12 to 18. What should
  happen?* "20–25 is fine"
- 2026-10-23, *What should the last two minutes of a match feel like?* "Both, short hunt then trial"
- 2026-10-23, *How much should the world compete with the deduction for attention?* "A second layer"

## Open threads

- Amend GDD §2, §3.3 and §3.9 (and the soak's target) to 20 to 25 minutes.
- Final Night: `huntS` 90 → about 45, and a longer final discussion under its own key. This needs a decision
  row.
- Give the watcher a verifiable fact (a door log for the scene you stood in), and give the talker a
  claim history across meetings.
- Make each world system leave evidence: quests stamp alibis, crafting leaves a trace.
- [[open:A89]]: is a light in every start kit?
- Teach the second layer in steps: quests first, crafting from the second match?
