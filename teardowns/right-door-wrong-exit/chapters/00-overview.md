# Overview and the loop

Right Door, Wrong Exit is a seven-room liminal walkthrough. In each room a five-second loading clip
glitches into a looping room video and a typewritten caption, and then a first-person three.js walk
to the room's exit. The exit of the last room, a lit EXIT sign in a stripped grocery store, leads
back to the title card. The owner calls it a walkthrough, made first for themself. What the return
should leave behind is: "Trapped: there was never a way out". This chapter reads the whole game
against that line. The loop is the game's argument and not a restart. The owner wants the teardown
to settle whether to grow it and merge it with Ninety-Nine (their second game, in
`groot99-droid/The-Intern`). This chapter starts that question, and the open threads end on it.

## The loop is the ending

**Describe.** The README draws the loop as a cycle: gate, title card, START, then for each room the
loading clip, the room, NEXT and the walk, and after the last walk, the title card again
([[sec:README:the-loop]], `README.md:16`). In code, the last chapter's walk ends in `goHome()`
rather than a next loader (`script.js:553`). So does a walk that fails (`script.js:560`), so a
broken room still closes the loop. `goHome()` glitches back to the home phase and clears the log
(`script.js:626`). There is no end card, no credits and no "you escaped". The last thing before
the title is the grocery store's EXIT door, reached through a maze, past entrance doors that are
locked black glass ([[room:grocery]], `README.md:110`).

The loop also shows up inside the game. The first log entry says of the stairwell "It just loops"
(`script.js:24`). In the trampoline park the floor is one 28 m cell drawn four times. The player
is wrapped back onto it, the same scuff mark passes underfoot, and DISTANCE reads NaN
([[room:trampoline]], `README.md:104`). That room's log ends "I'm trapped in a loop"
(`script.js:89`). So the whole run repeats on a small scale what the room does on a large one.

**Compare** *(Claude's analysis)*. In The Exit 8 the loop is the mechanic, and noticing what
changed is how you leave. Right Door, Wrong Exit gives no such way out: following the objective
puts you back at the start. That is closer to the found-footage Backrooms, where no-clipping out of
reality has no return route. The game's name already states the thesis: the door is the right
one, and the exit is still wrong.

**Critique** *(Claude's analysis)*. The trap holds only if the player can tell the return from a
reset. Today the return looks exactly like the page's own start: the same `glitchTo`, the same
title card, the same `0.mp3` (`script.js:626`). A player who arrives there may read it as "the
demo is over". If "Trapped: there was never a way out" is the feeling, the title card could know
it has been here before (a changed stamp, a worn START, a log line). The cost is small, because
`goHome()` already runs only on this path or on cancel.

## A walkthrough, with games inside it

**Describe.** The README's first line calls it "a single-page, click-through liminal-space
walkthrough" (`README.md:3`), the owner's word too. It began even thinner: a scroll reel ("Backrooms
Reel (Mobile)", deleted on 2026-08-22). The reel was replaced by the click-through
home → loading → room loop two days later (commit 987395f, [[pr:3]]). The 3D walks came five weeks
after that ([[pr:8]], [[pr:9]], [[pr:10]]). The three mini games came last ([[pr:11]]): Lights Out,
Fill the Frames and Shopping List ([[minigame:dining]], [[minigame:flooded]],
[[minigame:grocery]]). Each is "a bonus: the exit is open from the start and the game never
touches it" (`README.md:122`).

**Compare** *(Claude's analysis)*. Lights Out is anomaly-spotting, the same verb as The Exit 8.
The walks without a game sit closer to Pools: a space to cross, with nothing to beat.

**Critique** *(Claude's analysis)*. The bonus rule fits "walkthrough" exactly. Nothing stops the
walk, and SKIP is there during every walk and every loading clip, so no room is a dead end
([[sec:README:notes]]). But the score line under the readout, the tally and the win sounds pull
toward "game" (`README.md:124`). Each win also *calms* the room: the lamp stays on, the corridor
stops groaning, the anomaly holds steady. That works against a run whose feeling is being trapped.
Taken together, a win is a small reprieve inside the trap. That is coherent, but the README never
says it is the intent.

## Seven rooms, one descent, one voice

**Describe.** The rooms fall into four phases: The Departure from Reality, The Holding Cells, The
System Breakdown and The Empty Expanse ([[sec:README:the-loop]]). Each chapter has an epithet,
from The Anchor to The Anomaly ([[anchor:epithets]]). The clock stamps decay from `14:32` to
`27:81`, `SysTime: 88:88`, `ERR_CLOCK_NOT_FOUND`, `DISTANCE: NaN` and `PING_DETECTED_0x8F`
([[anchor:stamps]]). One first-person voice runs through the captions and logs
([[anchor:captions]], [[anchor:logs]]). The way through mostly goes down: the hallway ends at a
stairwell going **down**, the grate in front of the red door gives way, and the caption says "I
fell through a vent" ([[room:hallway]], [[room:flooded]], `script.js:87`).

**Critique** *(Claude's analysis)*. One log looks out of place. Chapter G's log, behind the LOG tab
in the grocery store, describes the chime and "a single, bright red glow on the horizon"
(`script.js:102`). In the walk, that happens at the end of the *trampoline park*
(`walk/scenes/trampoline.js:8`, `README.md:108`). The other logs mostly describe their own room,
although A's and B's lean toward the room ahead. So G's log reads as F's ending, and the grocery
store, the room that closes the loop, has no log of its own. It may be deliberate (the voice is
always one step behind). If not, it is the one place where the story's last word is missing.

## Made for one person

**Describe.** The owner names themself as the first audience. The build still carries a lot of
care that only a player sees: textures generated on the device, one draw call per material,
adaptive resolution, a phone layout ([[sec:README:built-for-phones]]). Behind it is a 1,114-line
browser test that walks every room, plays every game with each key, and measures every pile for
overlaps (`tools/walk_test.mjs`, [[sec:README:testing]]).

**Critique** *(Claude's analysis)*. For a piece made for oneself, that is a lot of
engineering. It reads less as product polish and more as the place where the craft was learned.
The same practices (seeded generators, a headless walk test, the clip-to-room motion tables) went
on to Ninety-Nine. One cost of "for me" is acceptable as long as it stays that way: the
loading clips and room videos differ only by case (`a.MP4`, `A.mp4`). They collide on default
macOS and Windows checkouts (`README.md:283`). That only matters once someone else clones it.

## Toward Ninety-Nine

**Describe.** Ninety-Nine's own design docs name this game as their structural reference
(`The-Intern/docs/01_GAME_LOGIC.md:7`). Its technical spec chose "no bundler" to match "the
existing *Right Door Wrong Exit* workflow" (`The-Intern/docs/04_TECHNICAL_BUILD.md:16`). Both ship
the same three.js, r160.

**Compare** *(Claude's analysis)*. The two games already share a back half. Ninety-Nine's hostile
path runs to a concrete edge over a pool. From there it goes into the water, down to a rusted
grate, through a chute, and out into a convenience store where one tube flickers
(`The-Intern/ninety-nine/assets/Scene Flow.md:186`). Right Door's runs from a flooded corridor to
a grate that gives way, a shaft, and a stripped grocery store whose left tube row flickers. Both
games only descend. Both put a lone light at the end of a fall: Ninety-Nine's pool lamp, and the
red glow here. There are also real differences. Ninety-Nine is one continuous walk with choices
and four endings, where one, PENDING REVIEW, also sends him back to a waiting room. Right Door
has cuts (loading clips, glitches), no choices, and one ending that is a loop.

**Critique** *(Claude's analysis)*. "Merge" can mean at least three different things, with very
different costs:

1. **Right Door as a place inside Ninety-Nine's building.** It could be a hidden layer under the
   hostile path, reached through the grate. This costs the most: Ninety-Nine's rooms are data
   (`build_rooms.py`, `scenes.json`), while these seven are hand-written three.js modules. They
   would have to be ported, and Ninety-Nine's canon would govern them: low-poly company things,
   photoreal building. The trampoline park and the painted sky would have to be judged under C1.
2. **A shared engine.** Same three.js version, both walk-first. The walk runtime, piles, procedural
   textures and test harness could become one library both games use. This changes nothing a
   player sees, and it removes the duplicated effort.
3. **A shared fiction, separate games.** For example, Ninety-Nine's PENDING REVIEW (a loop back to
   a waiting room) and this game's title card could be the same place, seen from two sides.
   This costs the least and keeps each game whole.

Growing Right Door on its own (more rooms, more games) is a separate question from merging. The
loop answer suggests rooms can be added without changing the ending, since the ending is the
return.

## Owner's word

- *When the loop drops the player back on the title card after the Grocery Store, what should they
  feel, in one line?* — "Trapped: there was never a way out" ([[answer:1]])
- *What word do you use for it?* — "A walkthrough" ([[answer:2]])
- *Who is it for first?* — "Me" ([[answer:3]])
- *What should this teardown help you decide next?* — "whether to grow it and make merge it with
  the intern in some fashion" ([[answer:4]])

## Open threads

- Should the return to the title card show that it is a return, so the trap reads as a trap and
  not as a reset?
- Is G's log meant to describe the trampoline park's glow, or should the grocery store get its own
  last entry?
- Should a mini-game win calm the room, which is a reprieve that softens the trap, or should it
  stay as small as it is?
- Merge with Ninety-Nine: a place inside its building, a shared engine, or a shared fiction?
  Later chapters (the walk, the rooms, the engine) will gather what each option would cost.
