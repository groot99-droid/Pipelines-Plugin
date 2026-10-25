# The seven rooms and the story they tell

The game tells its story in three channels: the typed caption over each room video, the log
behind the LOG tab, and a clock stamp that breaks a little more in each room ([[anchor:captions]],
[[anchor:logs]], [[anchor:stamps]]). Seven rooms fall into four phases, from The Departure from
Reality to The Empty Expanse ([[sec:README:the-loop]]). The owner's answers frame this chapter.
The narrator is "The player", the phases should stay "Open-ended: keep adding", and the stamps
"carry it": the breakdown of time is the story. All three hold up in the build, with two gaps.
The voice has more of a person in it than a stand-in for the player usually does. And the stamps
only reach the screen from the third room on, so the clock that breaks is never seen working.

## The voice

**Describe.** Each chapter has a caption, typed on the paper card, and a log entry, both in the
first person and the past or present tense of someone walking (`script.js:22` to `script.js:102`).
The captions set up each room's walk, nearly verb for verb. "I think I have to go up" becomes FIND
THE STAIRS and GO UP. "Found a place to rest" becomes FIND SOMEWHERE TO REST. "The door changed"
becomes GET THROUGH THE ARCH. "I have to keep moving" becomes KEEP MOVING ([[anchor:objectives]],
[[room:dining]], [[room:teal]], [[room:teal2]], [[room:trampoline]]). The walk then makes the
player do it: close your eyes on the couch, and the next room wakes you on the floor beside it
(`walk/scenes/teal2.js:19`).

**Compare** *(Claude's analysis)*. A narrator who is the player but speaks in "I" is close to
found-footage practice: the Backrooms series lets the camera be the viewer's eyes. Right Door
makes the *caption* those eyes. The player reads a line, then walks it, so the "I" is handed over
at NEXT.

**Critique** *(Claude's analysis)*. The handover works best where the voice stays bare: wait,
climb, rest, keep moving. In places the voice knows more than the player does, or is more of a
person. "They painted a sky on the wall to make us forget we're buried" (`script.js:74`) has a
"they" and an "us". "Am I following someone" (`script.js:100`) wonders about another walker. "My
hand tingled" and "I'm so tired" (`script.js:37`) report a body. None of this breaks the owner's
reading, but each line asks the player to agree to be someone with a past here. If "the player"
is the intent, the logs are the place for that past. They sit behind a tab, so they are optional
and written after the fact. The captions could stay as bare as the objectives. Chapter 0 noted
that G's log describes the trampoline park's ending. In a voice that is the player's own diary,
a log one step behind reads as written on arrival, which is coherent, but it should be consistent.
Today A's and G's logs look back, and B's looks ahead ("I just need to find a room to catch my
breath").

## The clock that breaks

**Describe.** The stamps run `14:32`, `18:15`, `27:81`, `SysTime: 88:88`, `ERR_CLOCK_NOT_FOUND`,
`DISTANCE: NaN` and `PING_DETECTED_0x8F` (`script.js:23` to `script.js:101`). They are shown as
the log's tag. From the third room on, the walk's readout puts them on screen and makes them
*behave*:

- **teal.** A WATCH counts *down* from 27:81, with 100-second minutes (`walk/scenes/teal.js:138`).
- **teal2.** It flickers between `SysTime: 88:88`, `SysTime: --:--` and broken digits
  (`walk/scenes/teal2.js:155`).
- **flooded.** It reads `ERR_CLOCK_NOT_FOUND` (`walk/scenes/flooded.js:351`).
- **trampoline.** It counts DISTANCE in metres until the floor wraps, then shows `NaN`
  (`walk/scenes/trampoline.js:191`).
- **grocery.** It shows nothing until you come within 7 m of the cart, then `PING_DETECTED_0x8F`
  with a chime. Shopping List's win turns it into `PING_ACKNOWLEDGED`
  (`walk/scenes/grocery.js:478`, `walk/scenes/grocery.js:434`).

The dining room and the hallway have no readout at all.

**Compare** *(Claude's analysis)*. A HUD that fails is a known horror device. Here it does more,
because the measure itself changes: time, then system time, then no clock, then distance, then a
network ping. The thing the walker counts with dissolves before the answer does.

**Critique** *(Claude's analysis)*. The owner says the stamps carry the story, and from teal on
they do, on screen, without the player opening anything. The weak point is the beginning. The
two stamps that show time *working*, `14:32` and then `18:15` three hours and 43 minutes later
("I've been walking down this hall for what feels like hours"), exist only in the logs of the
first two rooms. The player never sees a clock tick normally before seeing one run backward. A
WATCH readout in the dining room and the hallway, showing 14:32 and 18:15 and ticking forward,
would give the break something to break from. The code costs nothing new, since teal's watch
already shows how.

## Phases, and adding rooms

**Describe.** The phases are labels in the README's table and in no code: The Departure from
Reality (dining, hallway), The Holding Cells (teal, teal2), The System Breakdown (flooded) and The
Empty Expanse (trampoline, grocery) ([[sec:README:the-loop]]). A room is one entry in `CHAPTERS`,
with its id, audio, tilt, name, epithet, loading clip, video, walk id, caption, stamp and log
(`script.js:12`). It also needs a scene module registered in `walk/walk.js` ([[anchor:scene-registry]]),
and four media files named by letter: `X.mp4`, `x.MP4`, `X.mp3` and the scene. The loop to the
title card is tied to "the last chapter", not to the grocery store (`script.js:553`), so a room
added at the end moves the return with it.

**Compare** *(Claude's analysis)*. The Backrooms community wiki catalogs its spaces as numbered
levels with no last level. "Open-ended" fits the genre's own shape better than a closed seven.

**Critique** *(Claude's analysis)*. The data shape can take more rooms easily, and the loop logic
follows the last chapter by itself. Three things grow with each room:

1. **The naming.** Rooms are letters, and the loading clips differ from the room videos only by
   case (`a.MP4`, `A.mp4`). That collides on macOS and Windows checkouts
   ([[sec:README:notes]]). It caps out at 26 rooms, and it gets harder to follow with each pair.
2. **The phases.** They have no home in the data. An open-ended walk needs phase 5 and beyond, and
   a place where a chapter says which phase it is in. Otherwise the arc lives only in the README.
3. **The cost per room.** Each room is a generated room video, a loading clip, a track, a
   hand-written three.js scene (175 to 495 lines today), a caption, a log, a stamp and its test
   checks. Under the stage 2 answers it is also a game and a gate ([[answer:8]], [[answer:9]]).
   The stamps also set a constraint on order: they degrade, so a new room's stamp has to fit
   *between* its neighbours'. Adding a room in the middle is a writing task, not only a build
   task.

## Owner's word

- *The captions and logs follow one first-person voice going deeper: "They said to wait in the
  dining room", "I have to keep moving". Who is the narrator to you?* — "The player" ([[answer:11]])
- *The four phases run Departure from Reality → Holding Cells → System Breakdown → Empty Expanse.
  Is a room missing?* — "Open-ended: keep adding" ([[answer:12]])
- *Do the clock stamps (14:32 → 27:81 → SysTime: 88:88 → ERR_CLOCK_NOT_FOUND → DISTANCE: NaN →
  PING_DETECTED_0x8F) carry the story, or are they texture?* — "They carry it" ([[answer:13]])

## Open threads

- Should the dining room and the hallway show a working clock (14:32, 18:15), so the break has a
  before?
- With the player as the narrator, should the captions lose the "they" and "us", and the logs
  hold the past?
- Should the logs all look back, as if written on arrival in the next room, or all describe their
  own room?
- Phases in the data: should a chapter carry its phase, so an open-ended walk can grow phase 5?
- Naming beyond seven: keep letters and case pairs, or move to numbered folders before adding
  rooms?
