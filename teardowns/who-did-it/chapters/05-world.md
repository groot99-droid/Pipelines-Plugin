# World and the Bible

Who Did It has three written worlds, and they do not yet agree:

1. **The game's world bible**, `docs/WORLD.md` §4 ([[doc:WORLD]], [[sec:WORLD:4.1]]): Hollowmere, "a fog-bound
   harbour hamlet on a northern coast, autumn 1931". It has a shuttered tin mine, the will of Lord Aldous Vane,
   and mere-rot in the marsh. The tone is toon-noir.
2. **The owner's Bible**, `docs/round6/owner-brief.md` §2, Books I to VI ([[sec:round6/owner-brief:BOOK I]]):
   Hollowmere as a frontier company town of the Railroad Barons, with a Daily Train, four asymmetric killers,
   a three-stage law, townsfolk who evolve, and an NPC engine that sees everything.
3. **The new lore**: fifteen works in this repo's creative-writing vault marked `project: who-did-it`. These
   are a ledger, a codex, the Company's bylaws, the Train's timetable, a lamplighter's round, a Gazette, a tab
   book, stories, a ballad and two poems. They are set in **1893**, the year of the Panic, in Coldwater
   Territory, on the Thorne & Expanse Line. You named them the game's upcoming lore.

You answered: **the Bible's version for now; the new lore is where it is going**. You also said: Books I, IV
and V matter, and Book V most of all ("the killer dilemmas and state aware NPCs and Environmental effects and
mobs"); the era is all of costume, history and folk horror; and each map should **play differently**.

> The lore works are on the branch `claude/sharp-mccarthy-pqi3ws` and are not merged yet. The scan reads them
> through the profile's `lore` source once they reach `main` (`lore:vault/...` nodes). Until then this chapter
> cites them as `<work>:<line>`, under `creative-writing/vault/`.

## Three Hollowmeres

**Describe.**

| | WORLD 4.1 and the game data | The Bible, Book I | The new lore |
|---|---|---|---|
| Year | autumn 1931 | not dated | 1893 (`05_Worldbuilding/04_The_Canon_and_Trope_Ledger_of_Who_Did_It.md:42`) |
| Place | harbour hamlet; "the fog hides the sea" | company town, a week's walk from anywhere | "HollowMere has no sea"; "no harbour… a marsh dock" (Ledger:260, :291) |
| Owner | Lord Vane's will, "whoever remains" | the Railroad Barons | Cornelius Thorne and the Thorne & Expanse Line; Vane is a tin magnate from Port-au-Levain, three nights dead |
| The Beast | in the sea cave ([[creature:the-beast]]) | not named | in the Tin Gallery, woken by mere-rot (`05_Codex_of_the_End_of_the_Line.md:277`) |
| The Iron Beast | not present | not present | the Train itself (`06_Songs/06_Ballad_of_the_Iron_Beast.md:31`) |

The game data still holds the first column:
- `maps/hollowmere.json` has the blurb "Fog-bound harbour hamlet" and `theme: "harbour"` ([[data:maps/hollowmere]]);
- the quest giver is "Harbourmaster Pell", whose quest is "caulk the skiff" ([[rec:quests/npcs/harbourmaster]]);
- the Thief's goal is "escape by the cave sea exit" ([[rec:roles/roles/thief]]);
- the bakery rooms of [[dec:A116]] have a compressor fridge and a hanging bulb, which is 1931 kit.

But the game's own opening cutscene already tells the Bible's story: "HOLLOWMERE — EST. BY THE RAILROAD
EXPANSE… laid down, tie by tie and spike by spike, by the Railroad Barons"
(`apps/client/src/ui/copy/cutscenes.ts:9`-`13`). So the game contradicts itself between its first screen and
its first quest.

**Compare** (Claude's analysis). Long-running worlds handle this with an explicit canon order. Blood on the
Clocktower's wiki outranks old scripts. Hollow Knight's lore is ranked by the in-game text. The new
lore already does this for itself: the Ledger is written as a clerk's rulings between "what the paint says"
and "what the town says". It is the only one of the three documents that settles a conflict.

**Critique** (Claude's analysis). Your answer gives an order: the Bible now, the lore next. Make it a rule
before the next art or copy round, so no session builds a harbour again:
- **One canon line in WORLD.md 4.1.** For example: "Canon order: the lore in the ROSW vault, then the
  Bible, then this section. Where they differ, this section is out of date." Then mark §4.1's harbour
  sentences as superseded, rather than deleting them.
- **A small data pass.** It is mostly renames, not new systems:
  - `maps/hollowmere.json` blurb and theme;
  - Pell moves to the marsh dock (the lore keeps him there, Ledger:291-293);
  - the Thief's "sea exit" becomes the lore's way out: the Train, or the marsh;
  - the 1931 kit in the bakery rooms is replaced to fit 1893: ice from the mere, a dough trough, a clay oven
    (`05_Worldbuilding/09_A_Lamplighter_s_Round_of_HollowMere.md:182`-`206`).

  Frozen ids stay frozen ([[sec:GDD:3.13]]), so only names and text change.
- **1893 or 1931?** The art prompts in `docs/round5/art-plan.md` all end in "1931". The year changes the
  silhouettes: trench coats and wool caps in 1931, frock coats and bowlers in 1893. If the lore wins, the
  next art round needs the date first.

## Book V: killer dilemmas, state-aware NPCs, the environment

### Killer dilemmas

**Describe.** Round 7 built the four vendettas as rules ([[dec:A112]], [[sec:GDD:3.20]], [[data:vendettas]]):
- conversion (the Zealot);
- sabotage;
- a heist (the Bandit);
- a contract (the Hitman).

Each has one consequence, at most once per match. The lore turns each into a moral choice:
- **The Hitman.** The Baron's black-wax letter says "Burn the Letter… OR Accept the Baron's Contract". In
  `07_The_Daily_Train_Timetable_Manifest_and_Rules_of_Carriage.md:213`-`265`, the conductor takes a third
  road: neither burning the letter nor answering it.
- **The Bandit.** The gold-coin tip forces the Baker to choose, and she sweeps away his bootprint
  (`07_Poems_and_Prose/22_The_Daybook_of_Crumb_s_Ovens.md:58`-`64`).
- **The Zealot.** He kills the Vicar and Skin-Walks while the body is unreported (Codex:126).

**Compare** (Claude's analysis). A hidden-role game rarely gives a killer a *dilemma*. Its killers have goals.
The nearest are Blood on the Clocktower's Evil Twin, or Secret Hitler's fascist who must pass a liberal
policy to stay hidden. Your vendettas are closer to Dishonored's chaos choices: the same objective, reached by
a clean or a bloody road, with the world remembering which.

**Critique** (Claude's analysis).
- **The code has goals; the lore has choices.** Today a vendetta is a trigger, an emission and one
  consequence. To make it a dilemma, give each vendetta two `fires`, a clean road and a bloody one, and let
  the world state remember which was taken. The `vendettas.json` schema (`Vendetta.fires`, one `EventKind`)
  would need a second field. That is a small schema change for round 8.
- **The lore disagrees with the data in three places**, and each needs a decision:

  | Vendetta | The game today | The lore and the Bible |
  |---|---|---|
  | Hitman | drawn on a Killer card | "Nobody starts as the Hitman" (Codex:149) |
  | Bandit | a strongbox in `manor_hall` | the bakery, the chapel plate, the bank vault, the express safe |
  | Zealot | 45 s near the Vicar voids his vote | kills him and Skin-Walks |

### State-aware NPCs

**Describe.** Book V's "omniscient NPC engine" (BOOK V.3) has every ambient NPC scan a cone of 90° and 8
tiles. It adds to a `gossipValue` for what it sees: +5 for loitering, +25 for lockpicking, +100 for a
murder. Above 50, it carries the observation to the Post Office as a letter. The lore's version is quieter:
- the Gazette prints the town's mood by district: "Square: Calm… Pump Row: Panicked… Mill Row: Entranced"
  (`10_The_HollowMere_Gazette_Morning_Edition.md:181`);
- the Bylaws record the town's temper daily in the same four states (`06_Articles….md:267`);
- slips harden into indictments after a day (Articles:242-243).

The game has the bones of this:
- `routines.json` gives NPCs phase classes and work, social and rest activities;
- `sim/npc/memory.ts` and the `npcTells` tests give NPCs memory;
- the events schema already names the four moods (`mood: calm | panicked | entranced | rioting` in
  `bible.ts`);
- `events.json` is empty ([[data:events]]).

**Compare** (Claude's analysis). Dwarf Fortress and RimWorld show that NPC state is most legible when it
reaches the player as *news*: a mood line, a letter, a headline. The Gazette is that channel, and the lore
has already written its voice.

**Critique** (Claude's analysis). This is where your favourite Book meets your favourite pillar, and they
pull against each other.
- **Book V moves information across doors.** An NPC who sees a murder in the tavern and posts a letter tells
  the whole town what happened inside a scene. Chapter 0 asked whether "does this let information cross a
  door?" should be a review question. Book V's answer is "yes, on purpose, with delay". That can be good. A
  leak that costs a day and arrives as a *rumour* keeps space meaningful.
- **Keep the leak delayed, partial and wrong-able.**
  - Delayed: the letter lands at the next Day, when the Train comes, never at once.
  - Partial: it names a trait, never a seat. That is the lore's own rule: the Gazette "prints no unverified
    name" (Articles:180-182), and its trait notice points at an innocent (Gazette:135-151).
  - Wrong-able: the gossip weights can be fooled by a disguise, like a witness.

  Written into `events.json` as `spreadScenes` with a delay, this is a mechanic only Who Did It has.
- **Moods first, letters second.** A district mood (Calm, Panicked, Entranced, Rioting) is one value per
  scene group. It is visible on the HUD and cheap to compute, and it already has a name in the schema. Build
  moods in round 8. The letter pipeline can follow when the Post Office scene exists, and today it does not.

### Environment and mobs

**Describe.** Four creature types are in the data (wolf, boar, bat, rat), plus the night wolves. The world
bible names the Mere-wolf, the Bog-wisp (V1.5), the Beast (V2), and crows, rats and gulls ([[creature:Mere-wolf]],
[[creature:Bog-wisp]], [[sec:WORLD:4.6]]). The lore agrees on the mechanics and gives them causes:
- mere-wolves never cross the light (Codex:269-271), which is the data's `fleeLightTiles: 4`;
- mere-rot makes wolves bold, puts false footsteps in the dark, and brings a cough (Codex:281-286), which is
  the Bible's miasma (BOOK I.4);
- the tide that has no sea decides whether the Fenwood path holds (Lamplighter:58), which is a portal
  `window: lowTide` ([[sec:WORLD:4.5]]);
- "Fourteen Things Left Lying Around" walks WORLD 4.8's fourteen props one by one ([[sec:WORLD:4.8]]).

**Critique** (Claude's analysis). The lore is a design document for clues and is not yet read as one. Each
item it adds is a clue or a red herring with rules already implied:
- **False footsteps and the mere-rot cough** are noise rings that are not a killer. Book V's "Lung-Rot false
  positive" is the same idea at Blackpine. These are cheap, and they serve the detective style from chapter 3.
- **Wet Fenwood mud in a bootprint** (`12_Fourteen_Things_Left_Lying_Around.md:447`) is a location trait on a
  footprint. It is the watcher's verifiable fact that chapter 3 asked for.
- **"The goat that did not bleat"** (Lamplighter:296) against `barn.json`'s `entryNoise: goat` is the best
  clue in the lore. A *missing* noise is evidence. It needs only a log line, "the goat was quiet".

## Each map plays differently

**Describe.** You want maps that play differently. Today:
- **Hollowmere** has 21 scenes and the Daily Train ([[dec:A113]]).
- **Blackpine** ([[sec:WORLD:4.10]], [[sec:round6/owner-brief:BOOK III]]) has 8 scenes, with no train and no
  exclusive rule yet.
- **Port-au-Levain** moved to round 8 with its map ([[dec:A105]]).

The lore's Codex gives each settlement its own clock, verdict, predator and identity prop (Codex:58-88). But
the Ledger also says the three towns "keep three sets of books, and they come to the same column totals"
(Ledger:301-317). They mirror each other on purpose.

**Compare** (Claude's analysis). Among Us's maps share rules and differ in sabotage and layout. The Polus
seismic stabilisers and the Airship's ladders are each one exclusive mechanic. That is "feel different".
Dread Hunger's two maps and Project Winter's seasons change resources, threats and win routes. That is "play
differently", and it costs a separate balance pass per map.

**Critique** (Claude's analysis). "Play differently" multiplies the balance work from chapters 2 and 4 by the
number of maps. The lore suggests a way to keep that cost bounded. Mirror the *structure*, and vary the four
things the Codex names:

| | Hollowmere | Blackpine | Port-au-Levain |
|---|---|---|---|
| Clock | the Daily Train, Day to Dusk | the Payroll Train, the Shift-Whistle, the Midnight Roll Call | the Morning Ferry |
| Law | Detective → Police Officer → Judge | Camp Investigator → Mine Warden → Circuit Judge | Inquisitor → Guild Bailiff → High Chancellor |
| Predator (Book V.2) | mere-wolves, forest stalkers | Timber-wolves, tunnel crawlers | tide-ghouls, salt-flat drowners |
| Identity prop | the role card | the branded tally log (`bp.tally_0..9`) | the Wake Loaf on its platter |

(Clock, law and identity prop: Codex:60-88.)

The same `balance.json` sections then take one override block per map. The balance lab from chapter 4 sweeps
each map separately. This is the lore's "same column totals" made into a rule.

## Owner's word

- 2026-10-23, *Which is Hollowmere?* "The bibles version for now but the new upcoming lore is all in “Who did it
  Narrative Worldbuilding” in pipelines"
- 2026-10-23, *Which Book of the Bible matters most to you?* "Book1, BookV, and Book 1v but if I had to choose
  one it would be book V the killer dilemmas and state aware NPCs and Environmental effects and mobs."
- 2026-10-23, *Is the 1931 setting a costume, or should history carry the theme?* "It’s a combination of all of
  those that make the game"
- 2026-10-23, *Should each map play differently, or feel different around the same rules?* "Play differently"

## Open threads

- Write a canon order into WORLD.md 4.1 (lore, then Bible, then WORLD), and mark the harbour text superseded.
- 1893 or 1931? It decides the next art round's silhouettes and the bakery kit.
- The data pass: Hollowmere's blurb and theme, Pell's dock, the Thief's exit. Names only; ids stay frozen.
- Vendettas as dilemmas: two `fires` per vendetta (clean and bloody). Settle the three lore/data disagreements
  (who draws the Hitman, where the Bandit robs, what the Zealot does).
- Round 8: district moods first, the gossip-to-letter pipeline when the Post Office exists. Every letter is
  delayed, names a trait, and can be wrong.
- Turn the lore's tells into clues: the false footsteps, the cough, Fenwood mud, the goat that did not bleat.
- Per-map overrides of one `balance.json`: clock, law, predator and identity prop.
- Merge the lore branch, so the scan picks the works up as `lore:` nodes.
