# Backend, netcode and protocol

The server is one authoritative Colyseus process (`apps/server/`, [[area:server]]). Each party is a
`PartyRoom`, and every room steps its simulation at 20 Hz. The client is a static Phaser page on GitHub
Pages. It sends inputs and actions, and it receives only what its seat may know. Railway hosts the server
from `railway.json`, behind a `/health` route ([[sec:ARCHITECTURE:5.10]]).

You chose three things for this layer:
- **one or two matches at a time**, for your friends;
- **full anti-cheat**;
- the auto-mode growing into a **balance lab**.

The second answer asks more of the code than the first. This chapter takes both at their word.

## One step, in a fixed order

**Describe.** `apps/server/src/sim/Step.ts` runs every stage of a tick in a fixed order
([[anchor:tick-order]], [[sec:ARCHITECTURE:5.6]]):
1. the roster and the auto commands;
2. the NPC brains;
3. inputs (one per client, the newest wins, normalised by the server);
4. movement and collision;
5. the queued `act.*` commands, in arrival order;
6. portals;
7. clue decay and mobs;
8. view reconciliation, at 5 Hz, or at once after a crossing;
9. phase timers and the win check.

No message callback changes state. A seat that is `busy` (dying, in transit, hidden, channelling) has its
actions rejected with 426 ([[error:426]]). Kills are decided on the validated tick by a pure function in
`@wdi/shared` (`rules/kill.ts`), with the range slack set to what the target moved in the last 250 ms.

**Compare** (Claude's analysis). Among Us began host-authoritative, with one player's client as the
server. That is why its early years were full of speed and kill-anywhere hacks. Who Did It never trusts a
client for anything that changes state. The design resembles a small competitive-shooter server:
- a fixed tick;
- inputs as intentions, not positions;
- a short history kept for fair hit checks.

**Critique** (Claude's analysis). This is the backend's best decision, made on day one and kept through
seven rounds. The ordered, named tick is also what makes the game testable: 65 server test files drive it
tick by tick. The one risk is that the order is held in place by comments that say "locked call site". A
test that asserts the stage order would protect it as well as the comments do.

## Secrets, by construction

**Describe.** Secrets are kept by several separate mechanisms ([[sec:ARCHITECTURE:5.4]]):
- **Private view.** A role card, an inventory, a notebook and the cooldowns live in a private view that
  only its own client receives.
- **Scene filtering.** Each client gets only the scene it stands in, and nothing about a scene it is not in.
- **Separate random streams.** Randomness comes from named sfc32 streams: deal, traits, npcNames, mobs,
  nodes and more ([[anchor:seed-streams]]). Nothing secret shares a stream with anything public, so watching
  public randomness cannot reveal the deal.
- **Debug handlers off by default.** They register only with `WDI_DEBUG=1`.
- **Tests.** `sight.test.ts`, `visibility.test.ts`, `presence.test.ts`, `seeds.test.ts` and
  `invariants.test.ts` hold these rules in place.

**Compare** (Claude's analysis). Town of Salem sends each client its own role and nothing more, because
it has no space to leak. Among Us sent every player's role to every client for years, which is a known
wallhack source. A spatial hidden-role game has the hardest version of the problem, and few attempt the
per-scene filtering this one does.

**Critique** (Claude's analysis). The *role* secrets are well kept. The *perception* secrets are not, and
under full anti-cheat they are the next thing to fix:
- **Blood is filtered on the client.** The server sets the `bloody` status bit
  (`apps/server/src/sim/Movement.ts:108`) and sends it to every seat in the scene. The client then shows
  it only within 3 tiles (`apps/client/src/view/EntityView.ts:134`-`136`). A modified client can see who
  is bloody anywhere in the scene. That is the killer's identity a minute after every kill.
- **The night radius is server-enforced only in dark scenes.** `Sight.ts` limits sight to
  `vision.nightTiles` (3.5) only when a scene has `"dark": true`, and 6 of the 58 scenes do. On the overworld
  and in the lit houses at night, the server sends every avatar in the scene. The darkness is drawn by the
  client. A modified client sees the whole square at night.

Both fixes use machinery the server already has:
- send `bloody` only to viewers inside `visibleTiles`, which is the same distance test `Sight.ts` does;
- apply `canSee`'s radius in every scene during dusk and night, not only in dark scenes.

## Capacity for friends

**Describe.** You want the first host to carry one or two matches. The server reports `rooms`, `tickP95` and
`patchBytes` on `/health` (`services/Metrics.ts`). On a finished match it writes one JSON line to stdout
(`services/MatchLog.ts`), holding the seats, the duration, the winner, the rounds and the kills. Joining is
rate-limited by `matchmakeGuard.ts`, and messages are capped at 100 per second per client, with a token
bucket per type ([[sec:ARCHITECTURE:5.11]]).

**Compare** (Claude's analysis). One process for one group is how most friends-only games run, Jackbox
included before its scale-out. At 20 Hz with ten seats and NPCs, one small container has plenty of room.

**Critique** (Claude's analysis). Do not build for scale. Do record the one number that says when you
would need to: run `tools/bots/swarm.ts` once with two rooms of ten bots, and write the `tickP95` into
ARCHITECTURE 5.10. If it stays well under the 50 ms tick budget, capacity is settled until open parties
(R7b) bring strangers.

## Full anti-cheat

**Describe.** You chose full anti-cheat: speed hacks, wallhacks and scripted voting all in scope. What is
already in place:

| Threat | Today |
|---|---|
| Speed and teleport | Movement is computed on the server from a normalised input vector and a speed table (`Movement.ts`); a client cannot send a position |
| Kill from afar | Range, line of sight, phase and cooldown are checked on the server tick |
| Role reading | Private views; cover looks are drawn on the server; separate random streams |
| Seeing other scenes | Per-scene views |
| Seeing in the dark | Server-side only in the 6 dark scenes (see above) |
| Message floods | 100 per second cap, per-type buckets, a disconnect after 3 overflows in 10 s |
| Admin abuse | GitHub OAuth gate with an HMAC token, off unless every `WDI_ADMIN_*` variable is set |

**Compare** (Claude's analysis). Friends rarely cheat each other. Strangers in open parties will. Among Us's
anti-cheat arrived after its public lobbies filled with cheaters. Your answer puts anti-cheat in place first,
which is the cheaper order.

**Critique** (Claude's analysis). Your audience answer (friends) and this one (full anti-cheat) pull in
different directions. They meet at open parties (R7b), which bring exactly the strangers anti-cheat is for.
So the work belongs with R7b, in this order:
1. **The two perception leaks above.** Blood and the night radius are wallhacks that need nothing but
   devtools.
2. **A leak test for each message.** Generate a test from `docs/PROTOCOL.md`'s 55 messages
   ([[message:input.move]] and the rest). It asserts that a seat's received patches never hold a field it may
   not see. `invariants.test.ts` is where it belongs.
3. **Scripted voting.** Votes are already server-checked. What a script adds is speed: voting in the first
   tick. A short minimum before votes count, for example 3 s, removes that edge for free.
4. **Chat.** Names are 2 to 16 characters and a profanity list is planned for M7. Mute per seat, at the
   client, costs nothing.
5. **A report trail.** `MatchLog` already writes a line per match. Add the match seed and the build. A
   reported match can then be replayed in the admin room at 10x, because every random value comes from a
   named stream.

## The balance lab

**Describe.** You want the auto-mode to become a balance lab. The pieces exist:
- the `admin` room behind the GitHub gate, which runs an all-NPC match at 1x, 2x, 5x or 10x
  ([[sec:GDD:3.19]]);
- `tools/auto/`, with its `checks/` and a `report/summary.ts` that already computes median match ticks and
  rounds;
- `tools/bots/soak.ts`, `swarm.ts` and `walk.ts`.

**Compare** (Claude's analysis). Card games such as Slay the Spire and Hearthstone balance with millions of
simulated games. Hidden-role games rarely can, because their bots cannot lie. Yours can still measure
everything that does not need lying: match length, how often the Final Night is reached, Cabal win rate as
a function of kill cooldown, and how many clues survive to a meeting.

**Critique** (Claude's analysis). The lab is a command, not a page. Make it headless and repeatable:
- `pnpm --filter tools-auto sweep --seeds 200 --counts 4..10` runs at the highest speed the CPU allows,
  with no client, and writes `tools/auto/report/<date>.md`.
- The report answers the soak's own questions, with your new targets: a median of 20 to 25 minutes
  (chapter 3) and at most one third reaching the Final Night.
- Each report becomes the `basis: auto:<date>` that chapter 2 proposes for the numbers in `balance.json`.
- Know the limit. NPCs do not deceive, so the lab measures pace and pressure, never fun or fairness. The
  M3 playtest still decides those.

## Smaller findings

- [[open:A109]]: `LobbyPlayer` carries no profile, so no live row offers "Add friend". This is a protocol
  gap left between sessions.
- Seven protocol error codes, 422 to 428 ([[error:422]] to [[error:428]]), are well defined. Their
  player-facing copy is worth an audit in the UI chapter's terms.
- `Onub.ts` and `Conductor.ts` are still in the step (chapter 0). Remove them with 7J, together with their
  messages in PROTOCOL.md.

## Owner's word

- 2026-10-23, *How many matches at once should the first public host carry?* "One or two (friends)
  (Recommended)"
- 2026-10-23, *Is cheating a concern for the first audience, or only bugs?* "Full anti-cheat"
- 2026-10-23, *Should the admin auto-mode grow into a balance lab, or stay a bug finder?* "Balance lab
  (Recommended)"

## Open threads

- Send `bloody` only within `visibleTiles`, and enforce the night radius in every scene after dusk. These are
  the two perception leaks.
- A generated leak test for each message in `invariants.test.ts`.
- One swarm run of two rooms of ten bots, with its `tickP95` written into ARCHITECTURE 5.10.
- A headless `sweep` command with dated reports, as the source of `basis: auto`.
- Add the seed and the build to `MatchLog` so a reported match can be replayed.
- Does anti-cheat ship with open parties (R7b), or before the first friends' playtest?
