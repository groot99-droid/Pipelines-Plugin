# The building and the canon

The world of Ninety-Nine is one building and eight rules:

- **The building.** A real building in Hallam Row, owned by a fake company, Vellum & Ashe, LLP. It
  is walked from an apartment at dawn down to a store at the bottom of a chute, through rooms
  joined by connectors that only run level or down ([[sec:WORLD:world]], `CLAUDE.md`).
- **The rules.** Canon C1 to C8: the aesthetic law, shadows toward the core, no ascent, never
  "you", nobody blinks, his hands already low-poly, the drone, the clock without hands
  ([[sec:DOC1:3]]).

The owner's answers in this stage reshape both the rules and the one character who comes closest
to a story. The building's mood is "Real, wrong, downward". The rules to defend are C1 and C4,
with C1's company look to be lifted "to a ps2 scale or even a higher quality modern 'low to mid
poly'". Harlowe, the person whose desk he inherits, becomes "the previous 99".

## Real, wrong, downward

**Describe.** The canon already encodes all three words:

- **Real.** C1 makes the building photoreal: floors, walls, concrete, glass, water, fog, light.
  "The company is fake. The building is real."
- **Wrong.** Shadows fall toward the core whatever the light (C2). Every clock is the same clock,
  with no hands (C8).
- **Downward.** C3 forbids windows, sky and ascent after the lobby doors. "Refusing a descent
  results in a descent anyway" ([[sec:DOC1:3]]).

The build enforces downward structurally. The connectors only run level or down, and `check_room()`
fails a build that breaks it (`CLAUDE.md`). Chapter 1 showed how S7 and S8's resist choices end in
the same fall.

**Critique** *(Claude's analysis)*. The owner's three words are the canon's three groups, in the
order a player meets them. That makes them a good test for anything new. Chapter 3's room drift
has to be *real* (the building's own props, not new art), *wrong* (moved, missing, doubled) and
never open a way *up*. Every rule the next scene might break is one of those three.

## C1 lifted: from PS1 to "low to mid poly"

**Describe.** C1 is enforced in four places:

- **The live rooms' company materials** (`lp_*`) are flat-shaded, have "PS1 vertex snapping" (a
  shader that quantises clip-space positions to a coarse grid), and filter blocky "from mip to mip,
  never smoothed (PS1)" (`ninety-nine/src/walk/materials.js:533`, `ninety-nine/src/walk/materials.js:650`).
- **The catalog props in `library.glb`** get the same treatment whatever shading they shipped with:
  "flat shading, PS1 vertex snapping, the model's own flat colours and nothing else", and no photo
  textures (`ninety-nine/src/stage/library.js:8`).
- **The Blender pipeline's `LowPolyProp_*` factory** is flat-shaded, with an N-band toon ramp and
  `apply_vertex_snap()` ([[sec:BLENDER:on-disk-mirrors-of-the-in-blend-pipeline-code]]).
- **C5** gives faces "a static or 4-frame-loop jaw", and C6 makes his hands low-poly from the first
  shot.

**Compare** *(Claude's analysis)*. PS1 rendering is defined by its faults: no perspective-correct
texturing, vertices jittering to a coarse grid, no smooth shading. PS2-era low poly keeps the low
polygon budget, but has smooth (Gouraud) shading, stable vertices and painted textures. A "modern
low to mid poly" look goes further: clean silhouettes, smooth shading, flat or hand-painted colour,
the style of many current stylised games. Both keep C1's contrast, company shapes against a
photoreal building. They swap *broken* for *cheap*.

**Critique** *(Claude's analysis)*. The owner keeps C1's meaning and changes its means. The contrast
stays, and the *wrongness* of the company layer moves from rendering faults to modelling economy.
Four consequences:

1. **The code change is contained.** It lives in two shader paths (`withVertexSnap`, and
   `flatShading` in `materials.js` and `library.js`) and one Blender factory. The catalog models
   are already "stylised low-poly game assets" (`ninety-nine/assets/glb/README.md`). Without the
   PS1 treatment they are already close to the target.
2. **The text must change with it.** C1 says "renders **low-poly PS1**", and so do `CLAUDE.md`
   and the comments that cite it. C5's "4-frame jaw loop" is a PS1-era idea, and may stay as a
   deliberate holdover.
3. **It makes chapter 3's PS1 snap stronger.** Once the company is PS2-or-better, a fracture moment
   that drops the view to PS1 resolution becomes a *regression*: the company's own older, rougher
   self showing through. The screen effect gets its meaning from this decision.
4. **It meets the stage 0 plan for the old sets.** The Blender `LowPolyProp_*` factory has to
   change anyway. The rebuild of the Blender and Higgsfield sets is the natural moment to set the
   new company look once, in one factory, and export it through the GLB route.

## C4, defended

**Describe.** C4 and its test are covered in chapter 0: one "you" per ending card, the manager's
one crack, and a test that counts every "you" in company copy (`ninety-nine/test/cases/canon.text.js:36`).

**Critique** *(Claude's analysis)*. C1 and C4 together are the game's two-layer claim, one for
each sense: what you *see* (the company is fake) and what you *read* (the company never sees you
as a person). Choosing both means every new piece of content has to answer two questions: what
does it look like, and what does it call him?

## Harlowe, the previous 99

**Describe.** Waking the second terminal in S5 C sets `SAW_HARLOWE`. The terminal shows SESSION
USER: S. HARLOWE and an unsaved draft, "I am writing to inform"
(`ninety-nine/text/system.json:23`, [[sec:DOC1:s5-the-desk-the-garage]]). The flag then adds:

- row 019 of S6 C's requisition, in handwriting: "whatever is in the box, do not sign for it"
  (`ninety-nine/text/manifest.json:23`);
- one lowercase line on each ending card, for example "the role was occupied when the offer came
  through." (`ninety-nine/text/endings.json:8`).

Doc 1 says of it: "The role you were promoted into was occupied" (`docs/01_GAME_LOGIC.md:277`).
The ending lines were written under a rule: "no line adds a fact to chase or explains who Harlowe
was", from §9.3's warning that more Harlowe "becomes a mystery to solve"
(`ninety-nine/text/endings.json:3`, [[sec:DOC1:9]]). One prepared string is never used:
"Replacement, one (1). See S. HARLOWE." (`ninety-nine/text/system.json:26`). Numbers run through
the whole game. He is called "Ninety-nine." in S2 C. The speaker calls "One hundred." in PENDING
REVIEW. In ASSIMILATION the empty chair beside him holds a slip reading 100 ([[sec:DOC1:6.4]]).

**Compare** *(Claude's analysis)*. Severance makes the same move with its workers: the person who
held the desk before is a mystery the company keeps. Making Harlowe "the previous 99" answers it
inside the fiction. The number is the role, not the man, and it is reissued.

**Critique** *(Claude's analysis)*. This decision overrides the guardrail written into
`endings.json` and §9.3, so the record should say so. It is a stronger version of the owner's
stage 0 reading of "you". If 99 is a reused label, then calling him "Ninety-nine." is already
calling him by someone else's name. The ladder from Shaun, to 99, to "the candidate", to "you" now
starts lower than it seemed. It can be made legible without a mystery to solve:

- **The session line** reads "SESSION USER: S. HARLOWE · 99" (or the badge on the desk says 99).
  This one fact does the work.
- **The unused requisition string** says it as procurement: "Replacement, one (1). See S. HARLOWE."
  could appear on S6 C's sheet for every run. That would be the company's own, unhandwritten
  admission.
- **The ending lines** change with it. "the role was occupied when the offer came through." becomes
  plainer once the player knows whose role.
- **A limit.** Doc 1 §9.1's "no fourth door" still holds (stage 0, "Yes, both"). Knowing about
  Harlowe must not become a way out, only a clearer view of the trap.

The room drift of chapter 3 offers one more trace that costs nothing. In S6 C, the desk he
inherits, one drifted item could be Harlowe's: a second mug, a coat on the chair. It would be the
previous 99 still in the copy.

## Owner's word

- *The building's mood in three words?* — "Real, wrong, downward" ([[answer:19]])
- *Which canon rule (C1 to C8) would you defend if you had to break all the others? (C7, the
  drone, is already on the table.)* — "C1, C4. i like the low poly look but its more ps1, I'm
  looking to up it to a ps2 scale or even a higher quality modern "low to mid poly"" ([[answer:20]])
- *Doc 1 §9.3 asks whether Harlowe deserves more: today SAW_HARLOWE adds a desktop, a manifest row
  and one extra lowercase line on the ending card, "a haunting instead of an easter egg". What is
  your answer now?* — "Harlowe is the previous 99" ([[answer:21]])

## Open threads

- C1's new wording: "PS2-scale" or "modern low to mid poly"? And does C5's 4-frame jaw stay as a
  holdover?
- The shader change (no vertex snap, smooth shading) and the Blender factory, done together at the
  set rebuild?
- Harlowe as the previous 99: the session line, the requisition row, and rewritten ending lines.
  Amend §9.3 and the `_harloweNote` guardrail to record the change?
- A Harlowe drift item at S6 C's desk?
