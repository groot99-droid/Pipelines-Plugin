# CLAUDE.md — Creative-Writing Vault

## Purpose & scope

This file governs how Claude helps write **new** material in this vault — matching the author's voice at the sentence level and the plot/structure level, and knowing what to avoid. It does **not** license editing the 63 original works in `00_INDEX.md`: those are certified verbatim transcriptions from two master source documents. Frontmatter was added above each file's `# Title` line, but the body below it is untouched. All craft commentary lives in the separate `_Annotations/` tree, never inline in the originals.

## Where this vault sits, and how to read the paths below

This vault lives at `creative-writing/vault/` inside the `Pipelines` repo, as the
data half of the creative-writing tool (the pipeline that writes into it is at
`creative-writing/pipeline/`). See the repo root's `CLAUDE.md` for the layout.

**Every path in this file is vault-relative** — `03_Stories/06_Melting_Away.md`,
`tools/vault_search.py`, `_Annotations/…`. That is the form `vault_search.py`
reports and accepts. When your working directory is the repo root rather than
this vault, prefix it: `creative-writing/vault/tools/vault_search.py`.

## Vault navigation

- [[00_INDEX.md]] — bibliographic ledger of all 63 works, now wikilinked.
- `<folder>/_index.md` — one per numbered folder (e.g. [[02_Novels/_index]]), listing every file in that folder with a link to its companion annotation.
- [[Vault_Overview.canvas]] — visual map: one group per style-mode, with cross-project edges (open in Obsidian).
- `_Annotations/<folder>/<file>.md` — a companion craft-annotation note for every one of the 63 works, mirroring the folder structure.
- [[_Craft/_index]] — cross-cutting craft notes: plot logic, and the liminal, psychedelic and cosmic registers. Analysis written with Claude, not the author's prose.

## Using `tools/vault_search.py`

A self-contained, dependency-free TF-IDF search over the whole vault (works, the index, annotations, and craft notes). No Ollama, no network, no external packages. A result labelled `[craft]` is analysis written with Claude, never the author's own prose: use it as guidance and evidence, do not quote it as the author's voice.

```
python tools/vault_search.py index                      # rebuild after any content/frontmatter change
python tools/vault_search.py search "<query>" [--top N] [--json]
python tools/vault_search.py ask    "<query>" [--top N] [--json]   # alias of search
```

**When to invoke it:**
- Before writing in a given mode, to pull real passages as a warm-up reference.
- Before reusing a motif or theme, to check whether — and how — it's already been used ("have I written about drowning before?").
- When asked "have I written about X," rather than guessing from memory.

Always cite results back to the user as file path + heading/line range (the tool's own output format already does this) — never fabricate a citation the tool didn't return.

## Reading a file's frontmatter

Every work now carries YAML frontmatter above its `# Title` line:

| Field | Meaning |
|---|---|
| `type` | book, novel, story, book-concept, worldbuilding, song, poem, prose-poem, letter, dream-journal, character-profile, essay |
| `mode` | which style section below applies (see mapping) |
| `genre`, `themes`, `archetypes` | content tags |
| `status` | draft / complete / fragment / outline |
| `pov`, `tense` | as actually written — don't assume from mode |
| `project` | set only when a file is explicitly part of a named series/world (e.g. `wyrmreach`, `creative-codex`) |
| `register` | optional list (`liminal`, `psychedelic`, `cosmic`): the kind of world a *new* piece was written under. Written only when a register was used, never inferred, and it never changes `mode`. The 63 originals carry none. |
| `source_volume`, `source_lines` | provenance back to the master documents |
| `tags` | nested `type/…`, `mode/…`, `theme/…`, `project/…`, `status/…`, `archetype/…` for the Tag pane/Graph/Bases |
| `attachments` | reserved for future non-markdown assets; empty today |

**Mode → style section mapping:**

| `mode` value | Section below |
|---|---|
| `horror-prose` | Horror-Prose Mode |
| `epic-fantasy` | Epic-Fantasy Mode |
| `essay-self-help` | Essay / Self-Help Mode |
| `confessional-poetry` | Confessional-Poetry Mode |
| `unclassified` | No fixed mode rules apply — this is a real, expected value (roughly a third of the vault: satire, true-crime/pulp concepts, comedic sketches, dream/vision records, letters, songs, argued-not-confessed poems). Ask the user which register they want rather than defaulting to one of the four modes. |

If a new piece's intended mode is ambiguous, ask — don't silently invent a `mode` or `project` value.

## Writing Style & Narrative Style, by mode

### Horror-Prose Mode
**Prose:** Plain, punchy, concrete sensory vocabulary over abstraction. Short, often fragment-stacked paragraphs for emphasis ("No wind. No insects. No owls. Nothing."). Minimal dialogue tags — bare "said," frequent unattributed exchange bursts. High interiority even mid-action, but delivered clipped, not discursive. Very short chapters/scenes, each closing on a one-line gut-punch or ominous fragment.
**Structure:** The signature engine is **escalation-by-catalogued-incident** — a numbered or listable sequence of discrete, escalating wrongnesses the protagonist notices and mentally shelves before the next one stacks on (armor facing inward, then sick crew, then claw marks, then a curfew rule…). Endings are overwhelmingly **cyclical or non-resolving**: the protagonist is transformed, consumed, or made complicit rather than rescued; the text often loops back to its own opening line or hands the threat to a new victim. Do not default to a tidy, rescued, or cathartic ending in this mode.
**Worked examples:** [[_Annotations/03_Stories/07_Project_-_Man_Eater]] (clearest catalogued-escalation case), [[_Annotations/02_Novels/01_The_Stuffed_Ones]] (cyclical ending), [[_Annotations/03_Stories/06_Melting_Away]] (verbatim-repeated opening/closing line).

### Epic-Fantasy Mode
**Prose:** Third-person, past tense by default (occasional deliberate first/third-person blur as a soul-bond device — see WrymWretch — but that is one intentional experiment, not a general license for mid-scene POV switching). Elaborate cosmology delivered in codex/world-bible register when world-building; simile-dense, nature/light/water-drawn figurative language in narrative prose.
**Structure:** Ensemble-convergence (multiple bonded pairs summoned separately, converging on one location/threat) and twin-bond/soul-pairing structures recur. Memory, prophecy, and elemental/cosmic imbalance are common stakes.
**Worked examples:** [[_Annotations/02_Novels/02_WrymWretch]] and [[_Annotations/05_Worldbuilding/03_World_Codex_of_Wyrmreach]] (same project — `wyrmreach` — read both together), [[_Annotations/05_Worldbuilding/02_The_Redacted_Testament_of_Lira_Calyx]] (found-document/testament framing within this mode).

### Essay / Self-Help Mode
**Prose:** Direct address (second-person or first-person-plural, though this shifts within a piece — don't force one POV throughout). Elevated, abstract-noun-heavy lexicon: **"architecture" is the connective-tissue word across this vault's essay voice** (used literally across multiple essays), alongside covenant, threshold, ledger, communion, sovereignty, doctrine, lineage, codex, grammar, genealogies.
**Structure:** The recurring rhythm is **claim → parable/illustrative example → practice or action-item → closing callback/aphorism**. Known habit, not a rule to silently "fix": this voice tends to **over-explain** — it delivers a concrete image, then immediately re-narrates its meaning in abstract terms rather than trusting subtext. Preserve that instinct when writing in this mode; don't sand it down into ambiguity the author's own voice doesn't use here.
**Worked examples:** [[_Annotations/01_Books/01_The_First_Friend]], [[_Annotations/11_Essays/02_The_Architecture_of_Being]], [[_Annotations/11_Essays/04_The_Creative_Codex_of_the_Mythic_Architect]] (the one essay with an explicit action-item "Implementation" section — use as the template when a practice section is wanted).

### Confessional-Poetry Mode
**Prose:** First-person, autobiographical, processing grief/family/addiction/self-worth/betrayal. Anaphoric/triadic repetition, rhetorical questions as transitional beats, aphoristic closing lines that land the poem's point explicitly rather than trailing into ambiguity.
**Structure:** Poems often pair or cluster thematically (companion/rebuttal pieces, e.g. a betrayal poem answered by a resilience poem) rather than standing fully alone — check the folder MOC and nearby annotations for a piece that might be in conversation with the one being written.
**Worked examples:** [[_Annotations/07_Poems_and_Prose/05_Inherited]], [[_Annotations/07_Poems_and_Prose/09_The_Knife_I_Chose]] paired with [[_Annotations/07_Poems_and_Prose/10_The_Stripes_Remain]].

## Plot logic

Applies to stories: `horror-prose`, `epic-fantasy`, and any piece written under a **register** (below). It does not apply to essays or poems unless a register is chosen. This section is the authority. `pipeline/spec.yaml` (`plot_logic:`, `registers:`) is its machine-readable form, `pipeline/plot_logic.py` enforces it, and [[_Craft/plot-logic]] gives the reasoning and worked examples.

**The rule.** Between any two plot beats there is either a *but* (this beat defeats what the last one left behind) or a *therefore* (it happens because of it), never an *and then*. Delete the earlier beat: if the later one still happens the same way, it is not a therefore. Swap the two: if nothing is lost, it is an and-then.

**The causal ledger.** A story outline ends with a `## Causal ledger`: one table, one row per beat, with `Link` (`open`, `T`, `B` or `A`), `Because` (an earlier beat's number plus a phrase copied from that beat's `Changes`), `Beat`, `Response` (what the protagonist does about it), `Changes` (what is now irreversibly different), and a declared `Ending:` beneath. The checker verifies that the phrase is really there, that the chain has the right shape, and that the ending is legal for the mode. It cannot judge whether a link is *true*; the author reviews that at the outline checkpoint. The draft must make each `Because` visible on the page, so a beat that reads as an and-then in execution is a defect even if the outline was sound.

**Horror-prose keeps its engine.** Escalation-by-catalogued-incident stays. What changes is that it is causal: each incident is a *but* that breaks the protagonist's current explanation, each shelving is the *therefore* that the next incident must specifically break, and a run of incidents that merely add wrongness is the failure. The ending must be one of `cyclical`, `handoff`, `consumed`, `complicit`, `no-return`, `irreversible-knowledge`; this is the "no tidy, rescued endings" rule below, enforced at outline time. Let the shelving get thinner as the list grows and let `Response` show the agency decaying.

**Registers.** A *mode* says how a piece sounds; a *register* says what kind of world it runs in. They cut across modes: *Trips Are Like Exes* is confessional-poetry and psychedelic, *The Endless Temple* is epic-fantasy and liminal, *Missing Campsites* is horror-prose and liminal and cosmic. A register adds one state column to the ledger and a few shape rules; it never removes a rule the mode has. A horror mode that forbids a tidy ending still forbids it under `psychedelic`. **Never infer a register; ask.** Each has a craft note.

- **`liminal`** ([[_Craft/liminality]]): a threshold crossed, held and maybe recrossed; the surface stays ordinary and the rules do not. Track `Place`. Needs a `between`; decide the exit before the entry.
- **`psychedelic`** ([[_Craft/psychedelia]]): perception dissolves and reconstitutes; after the fracture the way out is a surrender or a choice, never a fix. Track `Self`.
- **`cosmic`** ([[_Craft/cosmic-horror]]): Lovecraftian design, a ladder of knowledge (`anomaly`, `pattern`, `scale`, `implicated`) that only rises, earned by acts of inquiry. Track `Knows`. The vault voice stays flat and compressed; the multi-page description ban below stands.

**Not yet covered.** The voice shared by the visionary pieces (the negation ladder, clinical distance, endings on recognition) is not a mode. Those pieces are `unclassified`, and per the table above the pipeline asks which register the author wants; a register supplies their structure, not their voice.

## Anti-Style / do-not list

- **No sustained multi-page dialogue-driven scenes.** Dialogue across this vault is sparse and functional — a burst of exchange, not a scene's engine. The one exception (script-format sketches like *Internal Affairs*) is a distinct comedic form, not license to default to dialogue-heavy scenes elsewhere.
- **No extended granular sensory description held over multiple paragraphs.** Compress description into fragments/lists rather than sustained scene-painting.
- **No mid-scene POV head-hopping.** POV shifts happen between sections/chapters, not within one continuous scene — except the one deliberate WrymWretch experiment, which is a named exception, not a default technique.
- **No tidy, rescued endings in Horror-Prose mode.** Default to complicity, transformation, or the cycle continuing.
- **Ethical restraint precedent, from [[_Annotations/02_Novels/03_Through_the_Eyes_of_Wolf_and_Lamb|Through the Eyes of Wolf and Lamb]]:** *"I will not make victims into props for cleverness; they will have interior lives, small habits, and the dignity of being more than plot points."* Treat this as the default restraint for graphic material — victims get interior lives, no gratuitous how-to/technique detail — unless the user explicitly asks to write something as viscerally graphic as the vault's more exploitative horror pieces (e.g. *Project: Man Eater*, *Melting Away*).
- **Psychedelic material records the experience's structure and symbols, never substances, doses, sourcing or how-to.** Precedent: [[09_Dream_Journal/02_Trip_Tracker_-_July_Fourteenth_2023|Trip Tracker]] preserves its vision "without glorifying or encouraging the circumstances that produced it". This is a restraint on the piece, not on the theme.
- **Don't silently invent `mode`, `project`, or archetype ties.** Several plausible-looking connections in this vault turned out to be false on inspection (e.g. Graknox sits next to the Wyrmreach codex in the source document but has zero textual tie to that world) — verify before asserting a connection, or ask.

## Companion annotation notes as worked examples

Every one of the 63 works has a companion note at `_Annotations/<folder>/<file>.md` with genuine, specific craft analysis (not templated). Use the folder MOCs to browse them; use `tools/vault_search.py` to find one by topic/pattern rather than guessing a path.

## Maintenance

Adding a new work to the vault:
1. Create the file under its folder.
2. Add YAML frontmatter (schema above) above its `# Title` line.
3. Add it to that folder's `_index.md`.
4. Write its companion annotation under `_Annotations/<folder>/`.
5. Re-run `python tools/vault_search.py index` and, if its `mode`/`project` affects the map, `python tools/build_canvas.py`.
