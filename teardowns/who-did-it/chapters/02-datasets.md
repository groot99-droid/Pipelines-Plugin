# Datasets and content

Who Did It keeps its rules as data. `packages/content/data/` holds 25 JSON files plus three folders: 58 scene
files under `scenes/`, the two maps under `maps/` (Hollowmere and Blackpine) and `cutscenes/`. Together they hold 20 roles,
46 abilities, 48 items, 18 clues, 13 looks, 6 tasks, 6 recipes, 6 resources, 4 mobs, 6 quests, 5 minigames and
4 vendettas ([[area:content]]). Every file has a zod schema in `packages/content/src/schemas/`, and most
records carry a `gddRef` back to the GDD section that owns them (246 of them in the data).

The project's own rule makes data and the GDD the only sources of numbers: "No other document restates a
number". This chapter checks how well the data keeps that rule, and reads it against your four answers.

## One source of rules, checked twice

**Describe.** Content is checked in two layers.
- **Per file:** each file's zod schema checks its shape. For example, `roles.ts` requires a non-empty
  `cardText` and `beware`.
- **Across files:** `packages/content/src/validate.ts` checks what one schema cannot. Every id a record
  names must exist, deck rows must add up, and every scene grid must agree with its portals, spawns and
  spots. `validateWorld.ts` and `validateVendettas.ts` add the map graph and the vendetta triggers.

A profession role that `plays` a class copies nine rules fields from it, `beware` among them (`PLAYS_FIELDS`,
`validate.ts:481`). The checks run as tests in `packages/content/test/`.

`balance.json` ([[data:balance]]) is the tuning sheet. It has 31 sections, from `tickHz` to `chat`, and each
section points to its GDD section. The per-player-count table is the heart of it
([[data:balance/byCount]], [[sec:GDD:3.9]]):

| Players | Kill cooldown | Discussion | Tasks each | Cabal wins on |
|---|---|---|---|---|
| 4 to 5 | 60 s | 60 s | 3 | Village at most one |
| 6 to 7 | 35 s | 75 s | 4 | Parity |
| 8 | 30 s | 90 s | 4 | Parity |

The 4-player deck is the practice deck ([[data:roles]], [[sec:GDD:3.1]]).

**Compare** (Claude's analysis). Among Us exposes its tuning as lobby sliders and leaves the host to balance.
Blood on the Clocktower keeps its rules in a fixed script of role tokens. Who Did It sits between the two: one
balance sheet scales with the player count, the host gets no sliders, and every number points to the design
text that justifies it. Data-driven roguelikes such as Slay the Spire work the same way. Few hobby
hidden-role games do.

**Critique** (Claude's analysis). The data layer is in better shape than most of the game. The `gddRef` on
every record is what made this teardown possible: the scan joins 866 records to their sections without
guessing. Two weak spots remain:
- `metrics.json`, `palette.json` and `style.json` carry no `gddRef`, because they belong to the art pipeline
  (stage 6).
- `balance.onub.json` and `roles.onub.json` still ship for a mode that [[dec:A115]] removed. They are 15
  roles and 15 tuning sections of dead weight until 7J's removal lands.

## Every number is a guess, for now

**Describe.** You answered that every number in `balance.json` was set by feel. Nothing in the repo
contradicts that.
- No balance value cites a playtest. `docs/PLAYTESTS/` holds a run sheet, a form, a scorecard and an
  unfilled M2 stub (`2026-xx-xx-m2.md`).
- `tools/auto/` can already run all-NPC matches. It has a `checks/` runner and a `report/` writer. No report
  from it is committed, and no decision cites one.

**Compare** (Claude's analysis). Among Us's defaults came out of many months of live lobbies. Town of Salem
has rebalanced its roles across years of patch notes. A feel-first start is normal. What sets a mature
hidden-role game apart is that each later change to a number names the match that justified it.

**Critique** (Claude's analysis).
- **Mark the guesses.** Add an optional `basis` beside `gddRef` on the numbers that matter most:
  `feel`, `auto:<report>` or `playtest:<date>`. The four `byCount` timers, `vision.nightTiles` (3.5) and
  `clues.traitCluesPerKill` (2) are the ones a first playtest will move. Then the balance sheet shows where
  it is solid and where it is a guess.
- **Use the auto-runner first.** NPC matches cannot tell you whether the game is fun. They can tell you how
  long a match runs at each player count, how often the Cabal wins, and how many clues survive to a meeting.
  The 12-to-18-minute target in [[sec:GDD:2]] is testable today without a single friend in the room.
- The step from 60 s to 35 s at six players is the largest jump in the table. It is also where the win
  condition changes from "Village at most one" to parity. Two rules change on one seat. That is the first
  place a sweep should look.

## The data wins: card text should follow it

**Describe.** You chose: the data wins, and the card is generated from it. Today both are written by hand.
The Killer's row in [[rec:roles/roles/killer]] holds its card text and a `beware` line. The `beware` line
reads: "Clues match your own traits whatever face you wear; your height never changes; Blood shows within 3
tiles; a guarded target voids your kill."

- The "3 tiles" is a copy of `clues.blood.params.visibleTiles` in `clues.json`. The 60 s of Blood is
  `clues.blood.decay.seconds`.
- The `win` line repeats the `byCount` win rule: "living Village at most 1 at 4-5".
- The same text appears a third time in the GDD's role table ([[sec:GDD:3.2]]).

No test ties the sentence to the number. The client mock already reads the 60 s from the data
(`apps/client/src/net/mock/worldMock.ts:45`), so code follows the data where prose does not.

**Compare** (Claude's analysis). Card games with a rules engine, such as Hearthstone or Slay the Spire,
generate card text from data: "Deal {damage}" rendered from the value. Board games cannot, and their errata
pages show the cost. A hidden-role game has more at stake than most, because the card is the only rulebook
most players ever read.

**Critique** (Claude's analysis). Your answer agrees with the project's own "no document restates a number"
rule. The card text is the one place in the data that breaks it. There are two ways to make it hold, in
order of cost:
1. **A drift test.** `packages/content/test/` scans `cardText`, `beware`, `goal` and `win` for numbers. Each
   number must match a value the role's abilities or clues reach. This is cheap and catches the next tuning
   change.
2. **Templated text.** `beware` becomes `"Blood shows within {clues.blood.params.visibleTiles} tiles"`. It is
   rendered once in `@wdi/content`, so the server, the client and the GDD table all read one string. This
   costs more, but you get "card generated" in full.

Start with the test, because it costs least. Move to templates when the round-8 roles arrive.

## Content by you and your friends

**Describe.** You want content written by you and your friends, through pull requests, not by players
through mods. That matches how the data is built today:
- plain JSON in the repo;
- checked when it is built, not when it is loaded;
- frozen ids for scenes, portals, spawns and clues ([[sec:GDD:3.13]]);
- an append-only `SCENE_IDS`.

**Compare** (Claude's analysis). Blood on the Clocktower's script tool lets a group compose a role set
without writing rules. Town of Salem's custom lists do the same within fixed roles. Both stop short of new
mechanics. A friends-by-PR model can go further, because a friend can add an ability and its code in one
pull request. The price is that every friend has to read a schema.

**Critique** (Claude's analysis). The schemas are well commented, but nothing guides a newcomer. Before you
invite a friend, add three things:
- **A how-to page:** `packages/content/README.md`, "Add a role in five files". It covers the `roles.json`
  row, the deck rows, a `looks.json` look, abilities, and the GDD 3.2 row.
- **Validator errors that say what to do.** `role killer: look killer belongs to x` already does. Make every
  message do the same.
- **A deck preview.** `validate.ts` already sums deck rows, so it could print the deck for each player count.

None of this needs runtime mod loading, so the role-secrecy rules stay simple.

## The round-8 seams

**Describe.** Four files were cut as seams in round 6 for the Bible's systems ([[sec:round6/bible-seams:1]]).
- `vendettas.json` is filled: 4 vendettas of kinds conversion, sabotage, heist and contract
  ([[data:vendettas]], [[sec:GDD:3.20]]).
- `evolutions.json`, `laws.json` and `events.json` are empty, though each has a full schema in
  `packages/content/src/schemas/bible.ts` ([[data:evolutions]], [[data:laws]], [[data:events]]):
  - an evolution turns one role into another on a trigger, and may keep its public look;
  - a law stage sets which Tribunal verdicts (release, exile, hang) are allowed;
  - a world event is one row of the propagation matrix: who hears what, how many scenes away.

You want them filled in round 8 ([[plan:r8:ROADMAP:7.1]]).

**Compare** (Claude's analysis). Dread Hunger and Project Winter added their mid-match role changes and
events after launch, once the base loop was known to work. Werewolf variants such as Ultimate Werewolf add
role transformations (the Wild Child, the Doppelgänger) as expansion content, never in the base set.

**Critique** (Claude's analysis). Two things stand out:
- **The schemas are ready, and that is the risk.** Data that already validates is easy to fill. All three
  systems move information or identity:
  - evolutions change who a seat is;
  - events send news across scenes;
  - laws change what a vote can do.

  Chapter 0 asked whether "does this let information cross a door?" should be a review question. `events.json`
  is that question in data form: its `spreadScenes` is the leak. Make 0 the default and justify every row
  above it.
- **Order.** You chose round 8, and the M3 playtest is still open. That is your call. If round 8 has room for
  only one of the three, `laws.json` is the safest to start with. It touches only the meeting, which is
  already the climax pillar, and not space.

## Smaller findings

- [[open:A92]]: cutscenes stay in one pre-seeded `cutscenes.json`, and `phases.openingS` is one number for
  every map. A second map's opening will want its own length.
- [[open:A93]]: transition timings live in `balance.ui.transitionS`. This is presentation data in the rules
  sheet, and the server code never reads it. That is harmless, but `balance.json` is now part rules, part UI.
- Several plans in the scan are marked withdrawn: the round-5 ONUB content schemas
  ([[plan:later:round5/onub-contract:appendix-a-onub-v2-content-schemas-pre-seed-pack]]) and the World
  Bible's V1.5/V2 list in [[plan:v15:DECISIONS:8.1]]. Their data files should go when the code does.

## Owner's word

- 2026-10-23, *Which numbers in balance.json were chosen by feel and which by testing?* "All by feel so far
  (Recommended)"
- 2026-10-23, *Who will author content later: roles, items, scenes, the round-8 evolutions, laws and events?*
  "Me and friends (Recommended)"
- 2026-10-23, *A role exists twice: as card text the player reads, and as data the server runs. When they
  disagree, which wins?* "Data wins, card generated (Recommended)"
- 2026-10-23, *evolutions.json, laws.json and events.json are empty stubs waiting for round 8. What should
  they be?* "Fill them in round 8"

## Open threads

- Add a `basis` field (feel, auto, playtest) to the key balance numbers?
- Which comes first: an auto-runner sweep of `byCount` (match length and Cabal win rate by player count), or
  a friends' playtest?
- A card-text drift test now, templated card text when the round-8 roles land?
- A "how to add a role" page before the first friend's pull request?
- In round 8, which of evolutions, laws and events comes first? And should `events.json` default to
  `spreadScenes: 0` (nothing crosses a door)?
- Remove `balance.onub.json` and `roles.onub.json` with 7J's removal of the quick mode.
