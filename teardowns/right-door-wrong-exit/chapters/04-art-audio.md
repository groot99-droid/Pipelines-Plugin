# Video, procedural rooms and sound

Right Door, Wrong Exit is made from two kinds of material that never mix in a file. One kind is
media: seven room videos, seven loading clips, eight section tracks and the title card, made in a
"Mixed" way, in the owner's word. The other kind is code: seven rooms built in three.js with no
model and no texture downloaded, and ten sounds synthesized in the browser
([[sec:README:built-for-phones]], [[anchor:sounds]], [[anchor:piles]]). The owner's answers frame
this chapter. The real room is "Neither alone": it is the pair, the video you see and the place you
enter. And a room at rest should sound like "The track alone". The pairing is the most carefully
kept rule in the game. The sound is where the build and the answer part ways.

## The pair: clip and room

**Describe.** Each room video is a fixed-camera, five-second loop with one thing happening in it.
The 3D room plays the same beat, stretched to a 20 to 40 s cycle so that it comes round whether
the player rushes or dawdles ([[sec:README:what-moves]]). The lamp clicks off. The tubes go grey
one at a time. The black doorway lifts. The arch grows. The red door lights, goes dark and
stutters on. The LEDs pulse. The store dips ([[motion:dining]], [[motion:hallway]],
[[motion:teal]], [[motion:teal2]], [[motion:flooded]], [[motion:trampoline]],
[[motion:grocery]]). `cycle()` and a hash-driven `stutter()` keep each beat deterministic
(`walk/build.js:201`, `walk/build.js:207`). The rooms were then refined to their videos in one pull
request ("Refine rooms B–G and animate every room to its video's movement", [[pr:10]]). The hallway
was rebuilt "to its room video", down to two wide low treads and then five steps
([[room:hallway]]).

**Compare** *(Claude's analysis)*. Pairing a flat image with a walkable version is the move of the
Chronicle Museum walkthrough this walk was modelled on (`README.md:53`). Most liminal games pick
one medium. Here the video does what a render cannot do cheaply (a camera-perfect, uncanny still),
and the room does what a video cannot (let you stand in it).

**Critique** *(Claude's analysis)*. "Neither alone" is exactly how the build treats the two. No
room is built without its clip, and no clip lacks a matching beat in the room, so the rule is
already enforced by habit. It is not enforced by a test, though. The walk test checks that each
room's animation *plays*, but not that it matches its clip. Since the video comes first, a
regenerated clip can drift from its room without anything failing. The "What moves" table is the
contract. It lives in the README, and it is the first thing to keep in step whenever a clip is
replaced.

## The rooms built from code

**Describe.** Every texture is generated on the device from seeded noise: about two dozen
generators, among them carpet, plaster, wood grain, curtain pleats, plaid and diamond wallpaper,
moss block, leather, tiles, the sky mural, the faded photographs, caution tape and the EXIT sign
(`walk/textures.js`). Each has normal and roughness maps, at 512 px on a phone and 1024 px on a
desktop. Generation runs in idle callbacks while the room video plays (`walk/textures.js:1`). The
clutter comes from three seeded generators, `pyramid`, `stack` and `heap`, plus a sagging box
(`walk/piles.js:142`, `walk/piles.js:262`, `walk/piles.js:523`). A heap settles one piece at a time
under rules on what a piece can bear, and how far it may stand out over a drop
([[sec:README:piles]]).

**Critique** *(Claude's analysis)*. The procedural approach is what makes "phone first" honest. The
rooms cost nothing to download beyond three.js. The physical rules for piles (a lid pressed flat
under what lies on it, a wet sheet that may jut out 2 cm) are far beyond what a five-second clip
asks for. The care is visible: piles that never clip are what keeps a photoreal clip and a
procedural room reading as one place. The cost is that `piles.js` (986 lines) is now the largest
file in the walk, larger than any room.

## The media

**Describe.** The media adds up to about 26 MB of room video, 9 MB of loading clips, 36 MB of
section tracks, and a 5.9 MB title card (`0.PNG`, 1520 × 2688). That is about 76 MB for a full
run. The videos are muted in the markup and in code, so the section track is the only media sound
([[sec:README:notes]]). The next loading clip is prefetched while you read the current room, and
the room video waits until its loading clip is playing.

**Critique** *(Claude's analysis)*. For an owner who plays on a phone, the title card is the
heaviest first impression: 5.9 MB of PNG before START, at 1520 × 2688, larger than any room video. A compressed copy at screen size would look the same on a phone, and cost a fraction of
that. The section tracks (36 MB) weigh more than all the video together. They loop, and the room
tracks run 3.7 to 7.3 MB each, so a lighter encoding there would save more than anywhere else.
Neither change touches the look or the sound design. How the media was made ("Mixed") matters for
one thing only: whether a regenerated or re-edited clip can be made again to match its room. That
is worth noting beside each clip.

## The sound of a room at rest

**Describe.** Each section's track starts with its loading clip and keeps playing through the room
and the walk ([[sec:README:notes]]). The synthesized sounds sit on their own master gain, which
follows the SOUND toggle (`walk/sound.js:1`). Some are events: the chime, the drip, the groan,
the click, the ping, and pickup, wrong and win for the games. Two are *continuous beds*. The
hallway's fluorescent `buzz` is a 120 Hz sawtooth that rises the further you walk
(`walk/scenes/hallway.js:195`). Teal2's `hum` is a detuned pair of 55 Hz sawtooths that grows
with time and with nearness to the arch (`walk/scenes/teal2.js:179`, `walk/sound.js:113`). The
flooded corridor groans every 7 to 16 seconds (`walk/scenes/flooded.js:380`).

**Critique** *(Claude's analysis)*. The owner wants a room at rest to sound like "The track alone".
The events fit that: they mark something happening and then stop. The two beds do not. In the
hallway and in teal2, the room at rest is the track *plus* a rising synthesized tone, which is the
room's own hum, exactly the option the owner did not pick. The flooded groan, every 7 to 16
seconds, also never lets that room rest. There are two ways to read it. The beds may be the point
of those two rooms (the caption says "The hum of the lights is getting louder", and the log "The
humming is getting louder"), in which case they are story events that last, and they should stay.
Or the track should carry the rise. Ninety-Nine went the other way: one continuous 48 Hz drone
under everything, never restarted (its canon C7). If the two games meet, this is the clearest
place where their sound designs disagree.

## Owner's word

- *The room videos came first, and the 3D rooms were built afterwards to match them, beat for
  beat. Which is the real room to you?* — "Neither alone" ([[answer:14]])
- *How were the room videos, loading clips and section tracks made?* — "Mixed" ([[answer:15]])
- *Each room's track plays on under the walk, and the walk adds small synthesized sounds (hum,
  buzz, drip, groan, chime). What should a room sound like when nothing is happening?* — "The
  track alone" ([[answer:16]])

## Open threads

- The hallway buzz and the teal2 hum: story events that rise, or beds to remove so the track stands
  alone?
- The flooded corridor's groan every 7 to 16 seconds: keep it, or space it out?
- A compressed, screen-sized title card, and lighter section tracks, for the phone?
- Should the "What moves" pairing become a check, so a replaced clip cannot drift from its room?
- Note beside each clip how it was made, so it can be remade to match its room.
