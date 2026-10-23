# Overview and pillars

Who Did It is a hidden-role murder mystery for 4 to 10 friends, played from a link. It takes the body
and the emergency meeting from Among Us, hidden factions and a climactic vote from Mafia, and physical
clues with hidden attributes from the whodunit. It is set in a storm-cut harbour hamlet in autumn 1931
([[sec:GDD:1]]). The game was built in seven rounds of parallel AI sessions, from 2026-10-10 to
2026-10-23 (482 commits). In that time it grew from a frozen v0.1 plan ([[doc:MASTER_PLAN]]) into two
maps, twenty roles, crafting, mobs, quests, cutscenes, an admin auto-mode, parties and vendettas.
Rounds 8 and 9 are already staged ([[milestone:R8]], [[milestone:R9]]).

You named **space is information** as the pillar you would defend above all. You want a body to land
as **dread, then suspicion**. The audience is **your friends, on a Friday night**. This chapter reads
the whole game against those three answers.

## The four pillars

**Describe.** GDD §1 sets four pillars, each with a design rule ([[sec:GDD:1]]):

| Pillar | Rule |
|---|---|
| Every kill tells a story | A knife kill always leaves 2 of 3 trait clues, a print and Blood |
| The vote is the climax | Phases funnel into short meetings; the Case Board never names anyone |
| Space is information | Entering a house, forest or cave removes you from sight; nothing in a scene leaks out of it |
| Readable in 20 seconds | One card, three abilities, canned chat outside meetings |

**Space is information** is the most deeply built of the four. It has its own stages in the server's
tick: `runPortals`, then `reconcileViews` ([[anchor:tick-order]]). Two server modules serve it,
`apps/server/src/sim/Visibility.ts` and `Sight.ts`. The architecture rule behind it is that a client
receives nothing about a scene it is not in ([[sec:ARCHITECTURE:5.4]]). The first-ten-minutes walkthrough
teaches it before anything else: you step into The Drowned Lantern and leave the street's sight
([[sec:GDD:2]]).

**Compare** (Claude's analysis). Among Us makes space informative through vision radius and line of
sight inside one connected map. Who Did It makes it *topological*: a building is a separate scene, so
"where were you" has a discrete, checkable answer. That is closer to Clue's rooms than to Among Us's
corridors. Mafia and Town of Salem have no space at all; their alibis are purely verbal. Here, an alibi
is a claim the world can contradict.

**Critique** (Claude's analysis).
- The pillar you chose is the one that costs the most network and rules code. It is also the one most
  exposed to later rounds. Every new system that moves people or information across scene borders weakens
  "nothing leaks": NPC gossip and letters in round 9, the Daily Train, and the propagation matrix
  ([[sec:round6/bible-seams:2.3]]). Make "does this let information cross a door?" an explicit review
  question for rounds 8 and 9.
- **A49 changed what space is *for*.** Since round 5, every seat walks as its card's character, so roles
  are public by sight. The only exceptions are the cover roles, Killer, Accomplice and Drifter, who wear
  another card's look ([[dec:A49]]). You chose this over the recommended private-looks option, knowing
  roles stop being secret. The deduction no longer asks *who is what*. It asks *which of the people who
  look like X is really X*, and *who was where*. That puts even more weight on space, which agrees with
  your answer, but GDD §1's wording predates the change. The pillar table still describes the older,
  fully hidden game.

## Dread, then suspicion

**Describe.** The body beat is staged in GDD §2, step 7 ([[sec:GDD:2]]). Night falls with a vignette. A
scream pulses at the screen edge with a direction arrow. The Killer carries Blood for 60 s and walks to
the well to wash. Reporting the body teleports everyone to the square, and the body stays where it fell.
Round 6 added death cutscenes and music (M5c, [[milestone:M5c]]). Round 7 added the Vicar's memorial
([[milestone:R7]]).

**Compare** (Claude's analysis). Among Us cuts straight to a meeting splash, so the dread is a single
frame and suspicion takes over at once. Werewolf-at-a-table gets its dread from the narrator's morning
announcement. Your scream-arrow-then-search sequence sits between the two: dread lasts as long as the
walk to the body. That is long enough to feel, and it is spatial, which agrees with your pillar.

**Critique** (Claude's analysis). A cutscene or a memorial on *every* death would turn dread into a
routine. Keep the long version for the first death of a match, and make later ones short. The teleport
to the square is efficient, but it skips the moment when people find the body *together*, and that is
where suspicion is born ("you were already here?"). Consider letting the reporter's arrival position be
seen at the meeting. It is spatial evidence, it costs nothing, and it fits your pillar.

## For friends on a Friday night

**Describe.** The design leans this way in several places:
- canned chat outside meetings;
- a 5-character join code and a share link;
- NPCs that fill the seats below four ([[sec:GDD:3.12]]);
- a target match of 12 to 18 minutes ([[sec:GDD:2]]);
- a quick mode that was cut on 2026-10-23 because the main mode is the game ([[dec:A115]]).

Round 7 also added open parties, profiles and friends lists ([[milestone:R7b]]), which serve strangers
online more than a known group.

**Compare** (Claude's analysis). The closest model for "friends on voice" is Among Us's private-lobby
play, where social reading outweighs the systems. Dread Hunger and Project Winter show the risk on the
other side: survival systems that eat the attention deduction needs.

**Critique** (Claude's analysis).
- **No playtest is on record yet.** `docs/PLAYTESTS/` holds a run sheet, a form, a scorecard and one
  unfilled M2 stub. The roadmap's M3 gate is called "fun or stop" ([[milestone:M3]]), but there is no
  entry saying it was passed. Seven rounds of systems now rest on an untested core. For a Friday-night
  game this is the single largest risk.
- Rounds 5 to 7 added resources, crafting, mobs, quests, hunger, a train, vendettas and an economy
  plan. Each is defensible on its own. Together they compete with the 20-second readability pillar and
  with the deduction. The Bible's later Books (I to VI) stage even more ([[sec:round6/owner-brief:BOOK I]]).
- Public parties and profiles (R7b) are a different audience's features. They are not harmful, but
  they are not Friday-night features, and they carry an ongoing cost in moderation and abuse handling.

## What the teardown will help decide

You asked for all four: what to cut, what to build in round 8, where docs and code disagree, and how
to pitch the game. Each later chapter ends with its own open threads. The scan's first findings:

- **Drift.** Two citations point at sections that do not exist. UI 14.28 is cited by the round-7 log.
  WORLD 4.11 (Port-au-Levain) is planned but not yet written. GDD §1's pillar text predates A49.
- **Withdrawn plans.** The quick mode is removed by A115, but `apps/server/src/sim/Onub.ts` (216 lines)
  and `Conductor.ts` (170) still stand while 7J's removal lands. GDD 3.11 still describes the mode until
  then.

## Owner's word

- 2026-10-23, *If everything else had to be cut, which pillar would you defend?* "Space is information"
- 2026-10-23, *What should the table feel the moment a body is found?* "Dread, then suspicion"
- 2026-10-23, *Who is the game for first?* "My friends, Friday night"
- 2026-10-23, *What should this teardown help you decide next?* "All of those" (what to cut, what to
  build in round 8, where docs and code disagree, how to pitch it)
- 2026-10-23, *Descriptive only, or also critical?* "Describe, Compare, Critique"

## Open threads

- Should GDD §1's pillar table be rewritten for public looks (A49), with deduction as "who is really who,
  and who was where"?
- When will the first friends' playtest (the M3 "fun or stop") happen, and does round 8 wait for it?
- Do open parties and profiles stay, or does the game narrow back to private links for friends?
- Should "does this let information cross a door?" become a review question for every round-8/9 system?
