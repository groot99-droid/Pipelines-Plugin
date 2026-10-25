# The walk, the exits and the mini games

Each of the seven rooms ends in a first-person walk to an exit. An objective names the exit,
an arrival prompt replaces it near the goal, and stepping onto the exit hands the camera over for
the climb, the approach or the fall ([[sec:README:the-3d-walk]], [[anchor:scene-registry]]). Three
rooms also hold a mini game, and today every one of them is a bonus that never touches the exit
([[sec:README:mini-games]]). The owner's answers turn this around: all three games should gate
their exit ("Yes, all three"), the other four rooms should each get one ("Give each one a game"),
and the dining room is the best walk while the trampoline park is unfinished. This chapter
describes the walk as it is built, then what those answers would change. The "bonus" rule is not
one line of code. It runs through the play module, the scene contract, the README and the test.

## The walk to the exit

**Describe.** A scene module exports `meta` (the objective, the arrival prompt, where you start)
and a `build()` that returns, among other things, a `trigger` box and a `nearGoal` box
([[sec:README:what-moves]], `README.md:179`). Every frame the runtime checks the player's floor
position: inside `nearGoal` the objective changes to the arrival prompt, and inside `trigger` the
exit begins (`walk/walk.js:331`). The exit then follows the scene's `exitPath`, an array or a
function of where the player is, with its own duration, easing, fade and shake. When it finishes,
the walk resolves as `'reached'` (`walk/walk.js:361`). The player walks at 2.2 m/s, "a wary walk,
not a museum stroll" (`walk/controls.js:14`). The objectives are FIND THE STAIRS, WALK TO THE END,
FIND SOMEWHERE TO REST, GET THROUGH THE ARCH, REACH THE RED DOOR, KEEP MOVING and FIND THE EXIT
([[anchor:objectives]], `walk/scenes/*.js`).

**Compare** *(Claude's analysis)*. Each objective is a verb with nothing to defeat, which is the
grammar of a walking game like Pools. The arrival prompt (GO UP, THE END, IT IS HERE) is a small
reward for arriving, closer to a chapter title than a score.

**Critique** *(Claude's analysis)*. The objectives carry the descent well: two exits drop you (the
hallway's stairwell down, the flooded corridor's grate) and one swallows you (teal2's black
arch). Only the dining room's arrival prompt points *up* ("GO UP"), and that room is the anchor. This is consistent with the story,
which goes down from the first room on.

## The dining room, the best walk

**Describe.** At 458 lines, the dining room is the most built room. It has cream plaster, green
shag, the round maple table and four chairs, the sideboard and its green lamp, the wall of
photographs, the china in crooked towers, and the steep dark stairwell in the back wall
([[room:dining]], `walk/scenes/dining.js:1`). Its one movement is taken from its video: the room
is still, then the lamp clicks off. Stretched to the walk, the lamp goes dark every 28 s for
3 s, with a switch click ([[motion:dining]], `walk/scenes/dining.js:30`). Lights Out hangs on
that beat. At a lamp-off one photograph changes (upside down, gone to grey lines, or dark) and
stays changed until it is found. A picture light shows which photo the prompt points at, and a
wrong guess costs nothing ([[minigame:dining]]). Three found keeps the lamp on and holds the room
still.

**Critique** *(Claude's analysis)*. It is the best walk because one beat does three jobs. The lamp
is the room's motion, the game's clock and the scare. Every other room's game borrows a prop
(frames, tins). This one borrows the room's own heartbeat. It is the model the other rooms'
games could follow.

## Gating the exit with every game

**Describe.** Today "a bonus" is enforced in four places. The play module's own header says
"nothing here touches a room's exit" (`walk/play.js:5`). The scene contract gives games no access
to `trigger` or `nearGoal`. The README promises that "rushing through (or SKIP) works as before"
(`README.md:122`). And the walk test visits each room with a game *twice*: first straight to the
exit without playing, then for the game. It checks that "the game leaves the exit's trigger and
colliders as they were" ([[sec:README:testing]]).

**Critique** *(Claude's analysis)*. Gating all three games is a real design change, and it has a
cost in each room:

- **Dining, Lights Out.** A photo changes only at a lamp-off, at 0.87 of each 28 s cycle, and the
  next only at the first lamp-off after the last was found (`walk/scenes/dining.js:30`,
  `walk/scenes/dining.js:353`). Three finds take at least about 24 + 28 + 28 ≈ 80 s, whatever
  the player does. That is my estimate from those constants, not a measurement. A gate there sets a
  floor of over a minute on the first room, waiting on a lamp.
- **Flooded, Fill the Frames.** It is the gentlest to gate: carry three photographs to three
  frames. But the room's exit is a *fall*. The grate gives way under you, so the gate would have to
  hold the grate up, or keep the red door dark, until the frames are hung.
- **Grocery, Shopping List.** The tins are in dead ends of a maze. Gating means walking every dead
  end that has a red tin. That is the most natural gate of the three, since it already ends in
  `PING_ACKNOWLEDGED`, the anomaly answering.

Against the owner's earlier answers ([[answer:1]], [[answer:6]]), gating does two things. It
makes "Trapped" literal: the door is locked until you do what the room asks, and *then* it leads
back to the start. And it makes SKIP the only way past a game that breaks, which is exactly "Only
if something breaks". The cost is the test: its first pass ("straight to the exit without
playing") becomes a check that the exit stays *shut*. Every game also needs a way to tell the
player the exit is shut (an objective change, a sound), or the open-looking door simply refuses
them.

## A game in every room

**Describe.** The four rooms without a game each have a beat taken from their video, stretched to
the walk ([[sec:README:what-moves]]): the hallway's nine tubes stutter one at a time
([[motion:hallway]]). The teal room's black doorway lifts to charcoal every 24 s
([[motion:teal]]). In teal2 the arch keeps growing and snapping back, and the wallpaper patches
shift when you are not looking ([[motion:teal2]], [[room:teal2]]). The trampoline park's floor
repeats, and a scuff mark passes underfoot each lap ([[motion:trampoline]]).

**Critique** *(Claude's analysis)*. Following the dining room's model, a game per room could be
built from the beat each room already has, rather than from new props. These are proposals, not
the owner's plan:

- **hallway.** One tube is wrong (it flickers out of turn); stand under it.
- **teal.** Look into the doorway at the moment it lifts.
- **teal2.** The patches move only when unseen: find the one that does not move. This is the same
  verb as Lights Out, mirrored.
- **trampoline.** Count the scuff mark, or find the one cell where it is missing.

Seven games would also put the README's description, "a walkthrough", under strain
([[answer:2]]). With every exit gated, the player has to play to see the next room.

## The trampoline park, unfinished

**Describe.** The park is one 28.2 m cell of 7 × 10 beds, drawn four times. The player is wrapped
back onto it (`walk/scenes/trampoline.js:24`). The readout counts DISTANCE in metres until the
first wrap, then reads `NaN`. After 110 m (`CHIME_AT`), a chime sounds, the objective becomes HEAD
FOR THE RED, and a red beacon appears 34 m ahead in the direction you are facing
(`walk/scenes/trampoline.js:193`). On a bed the head bobs 2.4 times as much as on a frame.

**Critique** *(Claude's analysis)*. At 2.2 m/s the 110 m is about 50 s of walking, and the beacon
about 15 s more. That makes over a minute in a room whose whole content is that it repeats. The
idea is the strongest in the game (the room *is* the loop), but the walk delivers it as waiting:
nothing changes until the chime. Three things could fix that without new art. The repetition
could become visible sooner, for example by showing the first `NaN` early. The chime could depend
on something the player does, such as turning around or standing still, instead of distance. Or,
as the owner suggests, the room could get a game that makes the loop the puzzle. It is also the
room where the caption ("I have to keep moving") and the log ("I'm trapped in a loop") match the
owner's "Trapped" best, so finishing it pays off the whole game's theme.

## Owner's word

- *The three mini games (Lights Out, Fill the Frames, Shopping List) are bonuses: the exit is open
  from the start. Should any of them ever gate the exit?* — "Yes, all three" ([[answer:8]])
- *Only three of the seven rooms have a mini game. What about the other four (hallway, both teal
  rooms, trampoline park)?* — "Give each one a game" ([[answer:9]])
- *Which room is the best to walk, and which feels unfinished?* — "Best: dining · Unfinished:
  trampoline" ([[answer:10]])

## Open threads

- Gating: how does a shut exit tell the player it is shut? Is it the objective line, a sound, or
  the door itself?
- Dining's gate makes the first room take at least about 80 s. Shorten the lamp cycle in the gated
  version, or accept it?
- The flooded exit is a fall. What holds the grate until the frames are hung?
- Four new games: build them from each room's existing beat (proposals above), or from new props?
- The trampoline park: should the chime come from distance, from something the player does, or
  from the new game?
- When the walk test's "straight to the exit" pass inverts, it becomes the proof that each gate
  holds.
