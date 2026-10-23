# The future: rounds 8 and 9, and after

The roadmap stages two more rounds ([[doc:ROADMAP]]):
- **R8, evolutions, law, economy, Port-au-Levain** ([[milestone:R8]]). It covers conditional role evolutions,
  the three-stage law pipeline and the Tribunal, the four macro resources and the tax loops, HQ tiers, and the
  Port-au-Levain campaign map (Bible Books I.4 to I.5, III.4, IV).
- **R9, world events, propagation, Blackpine industry, story mode** ([[milestone:R9]]). It covers the NPC
  propagation matrix from `events.json`, Blackpine's soot, steam and roll call, the single-player story mode on
  the auto-mode harness, and an admin inspector (Books III, V, VI).

The scan holds 117 stated plans: 26 for R8, 4 for R9, 43 for V1.5, 35 for V2 and 9 for "later". It also holds
10 seams cut for them in round 6 ([[sec:round6/bible-seams:1]], [[sec:round6/bible-seams:2]]), 27 open cells
in the decision log and 12 open questions.

Your four answers reframe all of it:
- R8 and R9's systems are **all equally** the game;
- the game **has been played five times** by friends and family, and grew by watching them;
- **V2 is not this game**: first person belongs to a remake, "Who Did It Too?";
- you will stop **when something else has your attention**, and probably keep building after that.

## All equally

**Describe.** You chose none of evolutions, the law, the economy, the maps or story mode over the others.
They are one design. The Bible already treats them that way. Book VI's "Unified Systemic Matrix" and the
propagation table in Book V.3 tie each killer action to a role's evolution, a town mood and an enforcer
([[sec:round6/owner-brief:BOOK V]]).

**Compare** (Claude's analysis). Immersive-sim designers say the same: in Deus Ex or Dishonored no single
system is the game; the *interactions* are. They still build in a fixed order. They lay a foundation that
everything reads first (the AI's perception, the stealth model), then the systems that write to it.

**Critique** (Claude's analysis). "All equally" is a fair answer about *value*. It is not yet an answer about
*order*, and rounds 8 and 9 need one. The risk is the round-6 pattern you named in chapter 7: everything at
once. A sequencing rule keeps your answer and still gives an order. **Build first what the next playtest can
see as a story beat.**
1. **Town moods** (Calm, Panicked, Entranced, Rioting), because every other system reads them and the
   players can see them (chapter 5).
2. **The law** (Tribunal stages and verdicts), because it changes the meeting, which every match has
   (chapters 3 and 5).
3. **Evolutions and the vendetta dilemmas**, because they are the plot twists.
4. **The economy and HQ tiers**, because they matter only once the town has a mood to tax and a law to
   break.
5. **Port-au-Levain**, built from the start as a map (chapter 7). **Story mode** comes last, because it runs
   on all of the above.

That is not a ranking. It is the order in which each system has something to talk to.

## Five playtests, and the curve from idea to story

**Describe.** You answered:
- friends played the first launch, and there have been **five playtests** in total;
- "everyone has loved the designs, the thoughts, the story";
- the game "went from an among us rip off to what it is now" by "watching people struggle, get board, find
  bugs, and make suggestions";
- the biggest flaw you saw is the curve from "I have a cool idea" to "how do I create a world narrative, how
  does that narrative present itself in the game play … plot twists, anticipation".

The repo has a full playtest kit: tiers by milestone in ROADMAP 7.5, a run sheet, a Google Forms feedback
form, the M3 "fun or stop" scorecard and a template in `docs/PLAYTESTS/`. It has no filled-in session. The
earlier chapters of this teardown read that gap as "never played". Your answer corrects them, and they now say
the playtests happened but were not written down.

**Compare** (Claude's analysis). Your method is the one most designers swear by: watch people play, don't ask
them. Valve's playtesting and the "watch, don't explain" rule of tabletop design both start there. What
studios add is a *trail*. They write down each session in a few lines, so the next person changing the game
can see why the last change was made.

**Critique** (Claude's analysis).
- **The learning lives only in you.** You saw players struggle and get bored, and you changed the game.
  The sessions that build it saw only your instructions, not what you saw. Chapter 7's quick mode is what
  happens when a picture does not travel. Five lines per playtest in `docs/PLAYTESTS/` are enough: what
  bored them, what confused them, what they did that you didn't expect, what you changed because of it.
  Then the next round's brief can cite them.
- **The flaw you named is the one the lore is solving.** "How the narrative presents itself in the gameplay"
  is the question chapter 5 answered from your own vault works. The goat that did not bleat, the Gazette's
  trait notice that points at an innocent, and the vendettas as dilemmas are all narrative made into
  mechanics. The answer to the flaw is already being written. It needs to reach the briefs.
- **Anticipation is a timing problem, and the game already has the clock.** The Daily Train, dusk and the
  Final Night are scheduled beats. A plot twist needs a promise first: the Train is late, the Gazette
  hints at a name, a vendetta letter arrives. Each of those is a line of `events.json` timed to a phase.

## V2 is a sequel, not a version

**Describe.** You answered that Who Did It "will never become a FPO". The game works and you and your friends
like the look. First person may come in a remake, "Who Did It Too?". The game still plans V2 as its own future:
- ARCHITECTURE 5.13, "V2 migration path": a Three.js or Babylon.js renderer, a `yaw` input, a capsule
  collider, a vision cone ([[sec:ARCHITECTURE:5.13]]);
- ROADMAP 7.8, the V2 outline;
- 35 V2 plans in the scan, and the frozen-id rule that exists partly "because V2 reads the same graph"
  ([[sec:GDD:3.13]]);
- CLAUDE.md's description of V1 and V2, and the Writing Museum as "the candidate seed for the V2 renderer".

**Compare** (Claude's analysis). Studios usually split a game into a sequel when its core changes. Among Us
VR is a separate product, not an Among Us update. Your answer does the same, and it frees the current game
from a constraint it has carried since day one.

**Critique** (Claude's analysis).
- **Relabel V2 as "Who Did It Too?"** in ARCHITECTURE 5.13, ROADMAP 7.8 and CLAUDE.md, rather than deleting
  it. The work is still useful to a sequel.
- **Keep the frozen ids.** They protect save data, replays, the lore's references and any sequel that wants
  the same town. They cost nothing.
- **Drop the V2 constraints that cost something.** The reserved `yaw` field, the `zoneId` versus `sceneId`
  split and the "content frozen behind `schemaVersion`" gate are there only for V2. They can stay as notes and
  stop being rules.
- **The 35 V2 plans** in the decision log and the master plan can be moved to a "Who Did It Too?" list, so
  the 43 V1.5 plans stop sharing a horizon with them.

## When it ends

**Describe.** You answered: "It’s not to prove anything, I’ll be done when something else has my attention".
After that you will probably keep building "new maps, mobs, and play styles forever".

**Compare** (Claude's analysis). This is the profile of a long-lived hobby world, like Dwarf Fortress's
decades or a tabletop group's home campaign, more than a product with a ship date. Those last because their
structure lets the next addition be small: a new creature is a data row, not a refactor.

**Critique** (Claude's analysis). For a world you may build on "forever", the speed of the last two weeks
matters less than the cost of the next addition. The teardown's findings point the same way:
- **Content as data** (chapter 2): card text generated from the numbers, a "how to add a role" page, readable
  validator errors. A new role is then a pull request a friend can make.
- **Per-map overrides** (chapter 5): a new map is a block of overrides and a scene set, not a new ruleset.
- **One canon** (chapter 5): the lore first, then the Bible, then WORLD.md. A new map's story has one place
  to start.
- **A record of intent** (chapter 7) and **a record of play** (above): the next session, or you in a year,
  can see why things are as they are. This teardown is a first version of that record. `udgt-consult` reads
  it from any Who Did It session, and a new `scan` after each round keeps it current.

## Owner's word

- 2026-10-23, *Rounds 8 and 9 stage evolutions, the law, an economy, Port-au-Levain and story mode. Which one is the
  game, and which are features?* "All equally"
- 2026-10-23, *When should friends first play a full match?* "I’ve had friends playing its first launch, in total
  I’ve had 5 play tests. Everyone has loved the designs, the thoughts, the story, and everything as it has
  progressed. The biggest flaw I saw was the actual curve from “I have a cool idea I want to build” to “How to I
  create a world narrative, how does that narrative present itself in the game play, how can you make this
  interesting like you would a story with plot twists, anticipation, and more while factoring in actual
  gameplay” that’s how this went from an among us rip off to what it is now. Through watching people struggle,
  get board, find bugs, and make suggestions (even if they didn’t intend it as a suggestion). This is what I’ve
  learned from doing it testing it and responding accordingly. Overall my close friends and family are very
  impressed and proud while strangers look at me with shock that I did this mostly from my phone and laptop in
  only a few days, I actually think it’s around week 2 or something."
- 2026-10-23, *Is V2 still the goal, or has the isometric game become the game?* "I don’t believe Who did it will
  ever become a FPO, the game works now, I like the look, and my friends like the look. However that doesn’t
  mean FPOV won’t be featured in a remake “Who Did It Too?”"
- 2026-10-23, *What would make you stop working on it?* "It’s not to prove anything, I’ll be done when something
  else has my attention, even then I’ll probably still use this first creation as a reference and who knows
  probably continue to build out new maps, mobs, and play styles forever."

## Open threads

- Adopt the sequencing rule for rounds 8 and 9: moods, law, evolutions and dilemmas, economy, then
  Port-au-Levain (as a map), then story mode?
- Write the five playtests into `docs/PLAYTESTS/`, five lines each, and cite them in round 8's brief.
- Relabel V2 as "Who Did It Too?" in ARCHITECTURE 5.13, ROADMAP 7.8 and CLAUDE.md. Keep the frozen ids, and
  turn the V2-only constraints into notes.
- Move the 35 V2 plans to a sequel list.
- Rescan this teardown after each round (`udgt.py diff`, then `scan`), and answer a short brief when a stage's
  findings move.
