# How it was made, and what is next

Right Door, Wrong Exit has 40 commits over seven working days, from 2026-08-22 to 2026-10-09, and
eleven merged pull requests ([[history:summary]]). It was built in two bursts five weeks apart: the
shell in three days of August, and the walk in four days around the start of October. The owner's
answers frame this chapter. The walk was not the plan ("No, it grew"). Ninety-Nine took four
things from it: "The descent, Liminal rooms, The workflow, The trap". And it is never finished:
"Never: it keeps growing". Its history also lines up with Ninety-Nine's, day for day.

## The shell, 22 to 25 August

**Describe.** The first upload (2026-08-22) was a scroll reel, "Backrooms Reel (Mobile)". The same
day brought fixed asset paths, a README, a pass on reduced motion and off-screen video pausing
([[pr:1]], [[pr:2]]), and the reel's own file was deleted. On 2026-08-24 the reel became the
click-through loop: "Replace scroll reel with a click-through home → loading → room loop" (commit
987395f). The home screen was cut down to the artwork and START, and the room counter dropped. The
eight section tracks arrived, each section got its own, and the click-anywhere veil came in so the
home track could play ([[pr:3]]). The next five pull requests, over two days, are almost all about
the loading screen. The clips were muted and played in full ([[pr:4]]). The loading screens stopped
being cut off and lost their overlay ([[pr:5]]). They became bare, with a 5.0 s trim and a caption
that clears itself ([[pr:6]]). Finally the hang was fixed and the white SKIP tab added ([[pr:7]]).
Every one of these came from one branch, `interactive-loading-screens`.

**Critique** *(Claude's analysis)*. Five pull requests in two days on one screen shows where the
owner's attention was: the loading screen as "A room of its own" ([[answer:5]]) was earned by
iteration, not designed up front. The cost is visible in chapter 1. The fixes stacked guard on
guard (start, stall, cap), which is robust, but it is also the one part the walk test cannot see.

## The walk, 30 September to 9 October

**Describe.** After five quiet weeks, the walk came in four steps. On 2026-09-30 came the dining
room and the hallway, with three.js vendored in the same commit ([[pr:8]]). Later that day the
other five rooms followed, with a stairwell down at THE END ([[pr:9]]). On 2026-10-01 rooms B to G
were refined, and every room was animated to its video's movement ([[pr:10]]). On 2026-10-03 the
mini games and the piles arrived, and on 2026-10-09 the piles were settled cleanly and "Never step
the walk backward after a long build" ([[pr:11]]). The pile work alone changed about 1,900 lines
(commit eeed3b2).

**Compare** *(Claude's analysis)*. The dates match Ninety-Nine's own history closely
(`groot99-droid/The-Intern`). Ninety-Nine's game landed on 2026-09-30 with "walkable 3D rooms",
the same day this game got its first walk. On 2026-10-01 Ninety-Nine replaced its AI video and
still pipeline with live 3D sets, the same day this game refined its rooms to *match* its videos.
On 2026-10-03 Ninety-Nine became one continuous walk and retired its mini-games, the same day this
game *added* its mini games. The two games were built side by side, from the same starting point
(video, then a walk), and on those three days they made opposite choices. Ninety-Nine dropped the
video and the games. Right Door kept the video and gained games.

**Critique** *(Claude's analysis)*. "No, it grew" is what the history shows: the shell was
finished, and the walk was added on top without changing it. The state machine still treats the
walk as an optional step between a room and the next loader. The last room's button still says
BEGIN AGAIN from before the walk existed (chapter 1). That is the cost of growth by addition:
each layer is clean, and the joins between them carry leftovers.

## What Ninety-Nine carried over

**Describe.** The owner names four things carried into Ninety-Nine:

- **The descent.** Ninety-Nine's canon C3 is "No windows. No sky. No ascent", with stairs and
  elevators that only go down.
- **The liminal rooms.**
- **The workflow.** A static site with no bundler, chosen in Ninety-Nine's spec to match "the
  existing *Right Door Wrong Exit* workflow" (`The-Intern/docs/04_TECHNICAL_BUILD.md:16`), the same
  three.js, and built through Claude session branches.
- **The trap.** All three of Ninety-Nine's endings are losses (`The-Intern/docs/01_GAME_LOGIC.md`
  §9.1).

**Critique** *(Claude's analysis)*. Of the four, the trap carried over in the most changed form.
Here the trap is structural: the exit leads back to the start ([[answer:1]]). In Ninety-Nine it is
narrative: there are choices, and each ending is a different loss. Only PENDING REVIEW, which
sends the candidate back to a waiting room, keeps this game's loop. If the two games merge in some
fashion ([[answer:4]]), PENDING REVIEW is where the two traps already meet.

## Never finished

**Describe.** The owner sees the game as open-ended: "Never: it keeps growing", consistent with
"Open-ended: keep adding" in chapter 3 ([[answer:12]]). The answers to the earlier briefs add up
to a growth plan:

- gate every game and give every room one (chapter 2);
- give the dining room and the hallway a working clock (chapter 3);
- settle the sound beds (chapter 4);
- add CI and rename the media (chapter 5);
- decide on merging with Ninety-Nine (chapter 0).

**Critique** *(Claude's analysis)*. A game that never finishes still needs an order of work. From
the chapters, the cheapest and most enabling steps come first:

1. **CI for the walk test, then the rename** (chapter 5). Every later step depends on the test
   running, and every new room depends on the new names.
2. **The two small leftovers.** BEGIN AGAIN, and the missing working clock in the first two rooms
   (chapters 1 and 3).
3. **The trampoline park**, the room the owner calls unfinished (chapter 2), and the room that is
   the loop.
4. **Games and gates, one room at a time**, with the walk test's "straight to the exit" pass turned
   into proof that each gate holds.
5. **New rooms**, each with its stamp placed between its neighbours'.

The merge question sits across all of these. If it means a shared engine, steps 1 and 3 are the
place to start. If it means a shared fiction, it touches only the title card and Ninety-Nine's
PENDING REVIEW, and can come at any time.

## Owner's word

- *It began on 2026-08-22 as a scroll reel of videos, became a click-through loop two days later,
  and grew a 3D walk five weeks after that. Was the 3D walk always the plan?* — "No, it grew"
  ([[answer:20]])
- *Ninety-Nine names this game as its structural reference. What did you carry over into it?* —
  "The descent,Liminal rooms,The workflow,The trap" ([[answer:21]])
- *What would make Right Door, Wrong Exit finished?* — "Never: it keeps growing" ([[answer:22]])

## Open threads

- The order of work above: does it match the owner's priorities, or should a new room come first?
- On 2026-10-03 the two games made opposite choices about mini-games. Is that difference part of
  what each game is, or something to resolve if they merge?
- PENDING REVIEW and the title card as the place where the two traps meet: worth pursuing as the
  first, cheapest form of the merge?
