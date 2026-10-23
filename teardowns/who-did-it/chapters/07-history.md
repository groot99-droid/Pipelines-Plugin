# How it was made: history and reversals

Who Did It was built in 13 days, from 2026-10-10 to 2026-10-23, by parallel AI sessions working to a plan
([[doc:SESSIONS]]). The game repository holds 522 commits and 167 merges, and every decision is a row in
[[doc:DECISIONS]]: 105 rows numbered A1 to A118, with A66 to A78 never used. This chapter reads the history
for one question: what got lost between what you asked for and what was built?

You answered two of the three questions:
- the quick mode was removed because **the directions were misunderstood**;
- the decision you would make differently is **A105, the round-6 scope**.

You did not answer the third question, on whether parallel sessions were worth it. This chapter does not
answer it for you.

## Seven rounds

**Describe.** Round sizes are counted from the session logs in `docs/SESSIONS.md`; commit counts come from
`git log` in the game repository.

| Round | Dates | Sessions | What it built |
|---|---|---|---|
| 1 | 10-10 | 4 (A to D) | scaffold: server, client, content, art pipeline ([[sec:SESSIONS:integration-log-2026-10-10]]) |
| 2 | 10-10 to 10-15 | about 1 | M1 finish ([[sec:SESSIONS:round-2-started-2026-10-10-after-prs-1-to-6-merg]]) |
| 3 | 10-16 | 7 | the match flow, world actions, bots and soak, art ([[milestone:M3]]) |
| 4 | 10-16 to 10-17 | 8 | the first quick mode (wake-loaf, M3b), NPC fill ([[milestone:M3b]]) |
| 5 | 10-17 to 10-18 | 14 | public looks (A49), isometric everywhere, ONUB v2, Blackpine, art styles (A79) |
| 6 | 10-22 | 16 | resources, crafting, mobs, quests (M5b), cutscenes and music, admin auto-mode, the Bible's seams ([[milestone:M5b]]) |
| 7 | 10-23 | 12 | the night-glass re-skin, parties, vendettas, the Daily Train; quick mode removed ([[milestone:R7]]) |

Commits per day show the same shape: 50 on day one, then 109 on 10-18, 114 on 10-22 and 147 on 10-23. Each
round was larger than the one before. Merges climbed from 4 a day to 74 on the last day.

**Compare** (Claude's analysis). This is how a studio scales a team: more people per milestone, a
coordination document, and an integrator. What is unusual is the clock. A studio's milestone is weeks; yours
is a day. The overhead a studio pays in meetings, you pay in `SESSIONS.md`, which is now over 3,300 lines,
in seams files per round (`docs/round6/seams.md`, `docs/round7/...`), and in contract decisions
([[dec:A105]] is one).

**Critique** (Claude's analysis). The process scaled well in one respect: the code holds. Tests, frozen ids
and the queued-actions rule survived seven rounds of parallel edits. It scaled badly in another. The size of
each round grew faster than its playtests could be written down. You ran five playtests and learned from
watching them (chapter 8), but none of them is in the repo (chapter 0). So each round's sessions built
without seeing what the last playtest showed. Rounds 6 and 7 were the largest and came after
the longest pause (10-18 to 10-22). That is the point where your answer below starts.

## The quick mode: directions misunderstood

**Describe.** The quick mode's life in the decision log:
- **10-10:** a friend framed the whole game as "One Night Ultimate Baguette", "a wrapper around the one-night
  hidden-role card game" ([[sec:GDD:3.11]]). The first plan took it in as a *mode*, and the owner decision
  that day accepted its length.
- **10-16, round 4:** the wake-loaf quick mode: a deal, a night script, acts, a dawn vote, played around
  Crumb's Wake Table ([[milestone:M3b]]).
- **10-17, round 5:** you supplied "the full mode (two cards per player, four prep stations, night roles, a
  5-minute Morning Rush, one vote) and its art". Round 5 rebuilt it as ONUB v2: 15 roles, 18 tuning sections,
  Onub.ts and Conductor.ts ([[sec:SESSIONS:round-5-log-5e-onub-v2-bots-npc-brains-e2e-and-s]]).
- **10-22, the Bible:** Book II describes *two* formats. Format A is "Crumb's Ovens Quick Mode", marked as
  shipped in round 5. Format B is "Port-au-Levain — The Full Island Campaign (mode: main)", a whole map
  ([[sec:round6/owner-brief:BOOK II]]).
- **10-23, round 7:** removed ([[dec:A115]]): "Remove the quick mode entirely", "Now, in round 7".
  Port-au-Levain stays as a main-mode map for round 8.

You answered: "I wanted ONUB to become a map and game mode like 'HollowMere' and 'BlackPine'. Instead … a flat
tile and card based deduction game, super boring and not at all how I saw it going … some context gets lost I
guess."

**Compare** (Claude's analysis). This is the classic spec failure: the *mechanics* were written down and the
*picture* was not. What reached round 5 was a list of rules, "two cards per player, four prep stations, night
roles, a 5-minute Morning Rush, one vote". Those rules fit a card game exactly. Your picture of a walkable map
existed, but it appears in the documents only after the build, as Book II's Format B. Game studios guard against
this with a "target experience" statement or a mood reel, which comes before any feature list.

**Critique** (Claude's analysis).
- **The rules were followed. The intent was lost.** Every session built what its brief said. No brief said
  "it should feel like walking Hollowmere". The orchestrator wrote briefs from rule lists, so a rule list was
  what got built.
- **Six days, two server modules (`Onub.ts` and `Conductor.ts`, about 390 lines), 15 roles and their art** were built and then removed.
  The cost was not in the code. It was in a round of attention that the main mode did not get.
- **The fix is the one this teardown uses.** Ask about feel and intent before building. Record the answer
  verbatim. Quote it in the work. A brief per feature ("what should this feel like? what is it like?
  what must it never become?") at the top of each round's contract would have caught "card game" against
  "a map". Put that brief at the top of `docs/round8/` before the Port-au-Levain map is specified.

## A105 and the round-6 scope

**Describe.** You named A105 and the round-6 scope as the decision you would change. Round 6 was the largest
round, with 16 sessions. It took on most of the Bible at once:
- resources and crafting ([[sec:GDD:3.14]]);
- mobs ([[sec:GDD:3.15]]);
- quests and mini-games ([[sec:GDD:3.16]]);
- cutscenes and music ([[sec:GDD:3.18]]);
- the admin auto-mode ([[sec:GDD:3.19]]);
- the round-8 seams (`vendettas`, `evolutions`, `laws`, `events`, [[sec:round6/bible-seams:1]]).

[[dec:A105]] is the round-7 contract that round 6's orchestrator (6Z) wrote. Round 7 opened before round 6's
last pull requests had landed, "on the owner's instruction to continue without them for the day". It
restaged the Bible's seams across round 7, then 8, then 9.

**Compare** (Claude's analysis). Scope creep in a game with friends is usually features that each sound small.
Here it was a whole world document arriving at once. The Bible landed on 10-22 and was turned into 16 parallel
briefs the same day. A studio would have taken a Bible like that through a pre-production pass first: what is
the core, what is later, what is never.

**Critique** (Claude's analysis). Your answer matches what chapters 0, 2 and 3 found from the code:
- the second layer arrived before the first was played;
- the round-8 stubs were built because the schemas were ready, not because play asked for them;
- the match grew from the GDD's 12 to 18 minutes to 20 to 25 minutes, and no recorded playtest shows it.

Doing it differently would look like this:
- **Round 6 as pre-production.** One session reads the Bible, sorts it into *core / round 8 / later*, and asks
  you the brief questions. Then a small round builds the core.
- **A playtest record between rounds.** The M3 gate is called "fun or stop" ([[milestone:M3]]). You already
  play between rounds. Make the gate the *write-up*: no round of new systems starts until the last playtest's
  form is in `docs/PLAYTESTS/`, so the sessions read what you saw.

## The decision log as a record

**Describe.** [[doc:DECISIONS]] is the project's memory. Each row has the decision, its owner, what changed in
review, and what stays open. Its layout changed at A86. 70 of the 522 commits name a decision id in their
subject. The `A66` to `A78` gap is real: those numbers have no rows. Several rows are still placeholders
reserved for a session or an integration ([[dec:A82]], [[dec:A94]], [[dec:A97]], [[dec:A114]]).

**Critique** (Claude's analysis). The log is what made this teardown possible. Almost every finding here is a
citation, not a guess. It records *what* was decided, by whom, with what open. What it does not record is
*what you wanted it to feel like*. The quick mode is the proof. Add one column for intent, filled in from
your own words, to rows that create a feature.

## Owner's word

- 2026-10-23, *What made you decide to remove the quick mode?* "The directions were misunderstood, I wanted ONUB
  to become a map and game mode like “HollowMere” and “BlackPine” instead it made what ONUB became in round 5 a
  flat tile and card based deduction game, super boring and not at all how I saw it going or specified but some
  context gets lost I guess"
- 2026-10-23, *Which decision would you make differently with what you know now?* "A105/round-6 scope"
- *Was parallel building worth its coordination cost?* Not answered.

## Open threads

- An intent brief ("feel, like, never") at the top of each round's contract, starting with `docs/round8/` and
  Port-au-Levain.
- Make the M3 gate a write-up gate: the last playtest's form is in `docs/PLAYTESTS/` before a round starts.
- An intent column in DECISIONS for rows that create a feature.
- Round 8 opens with a pre-production pass over the Bible: core, round 8, later, never.
- Parallel sessions: keep, shrink, or pause? This is still open.
