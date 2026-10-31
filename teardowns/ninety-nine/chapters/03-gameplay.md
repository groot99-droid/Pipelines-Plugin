# Spine, render and the walked choice

Ninety-Nine's rules fit in one file. Each choice adds +1 or −1 to `conformance`. A change of
direction adds 1 to `dissonance`. The score picks the next room's render. After S8 the score
picks the ending ([[sec:DOC1:2]], `ninety-nine/src/state.js:34`). Everything else the player
does (how long they hesitate, whether they double back) is `friction`. Friction feeds only
`fracture`, the "weather" of the building ([[sec:DOC1:2.3]]). The owner's answers in this stage
are the most concrete so far:

- The mini-games went because they "felt more like chores… a Band-Aid for the lack of game
  play".
- Friction should be told to the player "Once, obliquely".
- The two screen overlays that show fracture today should go, and three effects replace them: PS1
  snap, tracking tear and missed blink.
- The duplicate rooms should become corrupted copies of their originals, using all four drift
  options, without removing any existing scene.

Together those answers rebuild the thing Doc 1 says the player actually controls: "Not the route.
The **weather**" ([[sec:DOC1:7.3]]).

## The spine and the render

**Describe.** Render resolution is three lines. At +2 or above the room is compliant. At −2 or
below it is hostile. In between, the last render holds: "The tie at zero resolving to the *last*
render is what makes wavering feel like drifting instead of teleporting. Do not 'fix' it"
(`ninety-nine/src/state.js:42`). S0's application form sets only the starting render: two or more
NOT WILLING answers put him in the hostile waiting room, and the score stays at 0
(`ninety-nine/src/state.js:62`). The endings resolve in this order:

1. an early exit, or dissonance of 4 or more, goes to PENDING REVIEW;
2. +4 with the box opened goes to RETAINED;
3. +4 goes to ASSIMILATION;
4. −4 goes to EXPULSION;
5. everything else goes to PENDING REVIEW (`ninety-nine/src/state.js:97`).

Over all 256 paths, 202 end in PENDING REVIEW: "**Commitment is rare.** … wavering is the most
common way to end up filed and forgotten" ([[sec:DOC1:7.1]]).

**Compare** *(Claude's analysis)*. Papers, Please scores compliance too, but it shows the score
(the money, the family). Ninety-Nine hides it completely. The only feedback is which room appears
next, and since the tie holds the last render, a single defiant step changes nothing visible. That
is the design: "Resistance does not get you different geography. It gets you the same geography,
angrier" ([[sec:DOC1:1.3]]).

**Critique** *(Claude's analysis)*. The spine is sound, and the owner's stage 0 answer ("Yes,
both") holds it. The cost shows in §7.3. It names two sources of "weather": Doc 3's mini-games and
`dwell` timing. The mini-games are gone. That leaves friction from walking, and the only thing
friction drives that a player can *see* is the fracture overlay, which the owner now wants
removed. Without the changes this chapter records, two runs with the same choices would look
almost identical. That is why the drift and the screen effects below are not decoration. They
are the only replay variety the design has left.

## The mini-games, and what replaced them

**Describe.** Doc 3 specified seven mini-games in eleven modes. Each scene had one, from MG-01
THE INTAKE FORM to MG-07 THE HANDOFF / THE BREATH ([[minigame:MG-01]] to [[minigame:MG-07]]).
They were retired on 2026-10-03 "at the author's request", and each choice became a threshold
zone in the room ([[sec:DOC3:1]], `docs/03_MINIGAME_UX.md:7`). Friction now
comes from movement. Hesitation counts active choosing time, eased from 20 s to 90 s. Doubling back
counts walks into one threshold's ring and then the other's, after a 1.5 s debounce; three count as
full. Each scene yields `0.6 × hesitation + 0.4 × doubling`, from 0 to 1
(`ninety-nine/src/friction.js:1`, `ninety-nine/src/friction.js:17`).

**Critique** *(Claude's analysis)*. The owner's verdict is harsh, and the record agrees with it:
Doc 3's own §1 says mini-games output only friction, never the choice. They were a second game
bolted on to make the first one feel like a game. Walking is better because it *is* the choice.
The lesson in "none of it felt themed" is the test for everything this chapter adds: drift and
screen effects must come from the building's theme (copying, company resolution, a man who blinks
in a building where nobody does, C5), and never become something to solve. The Right Door
teardown recorded the opposite call for that game, gated mini-games in every room, made on the
same day this game retired its own. There, the one game that works (Lights Out) is the one built
from its room's own beat. The two decisions agree on that point.

## Duplicate rooms as corrupted copies

**Describe.** Six room keys are exact copies of another room, by rule: an alias may change only
its spawn, name and shots, or the build fails (`ninety-nine/tools/build_rooms.py:2349`):

| Alias | Copy of | When |
|---|---|---|
| S2 C / S2 H | S1 C / S1 H, the waiting room | the call comes in the room he is already in |
| S6 C | S5 C, the desk | the terminal wakes on the same desk |
| S7 H | S6 H, the edge | the same edge, one step closer |
| SE_RETAINED | SE_ASSIM, the boardroom | the second boardroom ending |
| SE_EXPUL | S8 H, the store | the ending where he landed |

The tools for change already exist: `unseen` changes a room behind his back (used once, in S4 C),
`show`/`hide` and `env` beats change it in view, and fracture already takes the score into account
([[anchor:beats]]).

**Critique** *(Claude's analysis)*. The owner chose all four drift options, but option 4 only for
the duplicates. No scene is removed, and no existing hostile room is redesigned. One fact shapes
how they combine: in a continuous walk, he never *leaves* an aliased room. S2 happens in S1's
room while he is still in it. So "a corrupted copy" cannot be a second room built beside the first
one. It has to happen *in place*, while he is there. The four options then fit together as one
system:

1. **The content** (option 2): each alias carries a short drift list against its original, for
   example a chair fewer, a stapler moved, the rail shorter, a seat added at the boardroom table.
   `check_room()` accepts drift but refuses it on a threshold zone, a doorway or anything that
   opens a way up (C3, and chapter 1's truthful labels).
2. **The moment** (option 1): the drift is applied as an `unseen` change when the alias's scene
   begins, out of his view, so he finds it when he turns.
3. **The amount** (option 3): fracture decides how much of the list applies. A committed run sees
   one item; a waverer sees all of them.
4. **The look** (option 4): the drifted items are the original's own props, moved, duplicated or
   missing, never new art. That is what makes it a *copy*, and the backrooms effect, rather than
   a different room.

The missed blink (below) is the natural moment for a drift that happens in view. The removed "99"
slip can come back here as an object: Doc 1 §9.2's "slip on the floor", placed in the room as a
drift item, rather than drawn on the screen.

## Screen effects instead of the overlays

**Describe.** Today `fracture` is applied once, when each scene starts
(`ninety-nine/src/director.js:682`). Two overlays show it ([[sec:DOC4:5.2]],
`ninety-nine/src/fracture.js:1`):

- a soft-light wash in the *opposite* render's fog and ambient colours, capped at 0.22 opacity;
- a "99" paper slip fixed at the same screen position in both renders, with a slight chroma
  drift.

Fracture also drives the drone's detune depth and the voice pitch drift ([[sec:DOC1:2.3]]).

**Critique** *(Claude's analysis)*. The owner's three picks each come from the game's own canon.
They should fire rarely and more often as fracture rises, never during a carried moment or inside
a threshold ring, and always respect `prefers-reduced-motion`:

- **PS1 snap.** For a few frames the whole view drops to company resolution, which is C1's low-poly
  rule briefly claiming the photoreal building. It is the most on-theme of the three. It is also a
  deliberate, momentary break of C1, so C1's text should say that fracture may do it.
- **Tracking tear.** A band of the image slides sideways and snaps back. It is the most legible of
  the three, and the least tied to *this* building, since it reads as "old tape".
- **Missed blink.** The edges close and open, like an eyelid, and a drift item has moved. This
  fits C5 (no NPC blinks) as a contrast: he is the only one who blinks. It also gives option 3 its
  in-view moment, so the blink and the drift should be built together.

Removing the overlays also removes the old "texture bleed" from the opposite render. That bleed
was the only thing on screen hinting that the two buildings are one. The duplicated rooms take over
that job, by putting the same objects in the wrong places.

## Telling the player, once

**Describe.** Friction is never shown. It sums across scenes, up to 8, and reaches the player only
through fracture (`ninety-nine/src/friction.js:1`).

**Critique** *(Claude's analysis)*. "Once, obliquely" fits a company that keeps a file on him. The
line must obey C4 (no "you"), and it reads best where the company already reports on him: a
caption in S4 or S6, or a row in S6 C's requisition manifest, worded like "THE CANDIDATE'S DELAY
HAS BEEN NOTED". Better still, it could show only on a run where friction is already high, so the
player who hesitates is the one who hears that hesitation counts.

## Owner's word

- *Should duplicate rooms change a little, like the backrooms' duplication effect? (asked in
  conversation, after the options for room drift were laid out)* — "yes, ask chapter 3 questions, i
  like all four options you mentioned and id also like get rid of the two screenoverlays. a cool
  random screen effect would be cool but id have to see options." ([[answer:11]])
- *Room drift (the backrooms copy effect): which should Ninety-Nine use?* — "i dont want to get rid
  of any scenes that already exists only change the duplicate rooms for option 4.,1. Aliases drift
  via `unseen`,2. Alias drift lists,3. Drift tied to fracture,4. H as a corrupted copy of C"
  ([[answer:12]])
- *With the two fracture overlays gone (the opposite render's colour bleed and the fixed '99'
  slip), which random screen effect should replace them? Each fires rarely, more often as fracture
  rises, and never on a threshold.* — "PS1 snap,Tracking tear,Missed blink" ([[answer:13]])
- *Retiring the mini-games (2026-10-03) for walked thresholds was the largest change. What made you
  decide it?* — "the designs sucked and felt more like chores. Worst design ideas I've had to date.
  none of it felt themed either it was like a Band-Aid for the lack of game play" ([[answer:14]])
- *Friction now comes from how he moves (hesitating, doubling back between thresholds) and feeds
  only fracture. Should the player ever be told that it counts?* — "Once, obliquely"
  ([[answer:15]])

## Open threads

- The drift lists per alias: which props move, go missing or double, in S2, S6 C, S7 H and the two
  endings?
- Fracture as the amount: one drift item at low fracture, all of them at high?
- The screen effects: their frequency curve against fracture, and C1's text amended to allow the PS1
  snap?
- The "99" slip back as an object, a drift item on the floor, per Doc 1 §9.2?
- The oblique line: where it appears (a caption, or a manifest row), and whether it shows only on a
  high-friction run?
- Doc 1 §7.3 and Doc 4 §5.2 to be amended once the overlays go, so the specs describe the new
  weather.
