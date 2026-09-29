# Vault and its indexers

Subsystem `vault-rag` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 13 entries · 23 corrections made to the first reading.

## Summary

The vault-rag subsystem has three parts. (1) An Obsidian vault at vault/ that follows the Content MD spec in vault/SCHEMA.md. It also holds a template, a worked example and a migration gap analysis. (2) Two stdlib-only Python indexers that can read any vault directory. tools/vault_rag.py has the subcommands status, index, ask and evict, plus a global --endpoint flag that must come before the subcommand. It chunks notes (800 tokens with 120 overlap, at chars/4), embeds them through local Ollama into a single JSON index at state/rag_index/index.json, and answers using only the retrieved chunks, citing [c_NNNN] ids. tools/vault_manifest.py (flags --vault and --out) writes state/vault_manifest.json, a one-row-per-note index with no embeddings that includes each note's full body. The hub Library tab reads it, and the hub's separate browser-side Ask index is built from it. (3) OBSIDIAN.md describes two connections. A is an Obsidian community plugin talking to Ollama: Copilot, Smart Connections or Text Generator are listed and none is chosen, and it needs OLLAMA_ORIGINS=app://obsidian.md. B is vault_rag.py. WHICH VAULT THE STATE FILES CAME FROM: neither generated state file was built from this repo's vault/. Both headers record vault C:\Users\utopi\Creative-Writing, the sibling 'Living Archive'. The manifest (built 2026-09-01T04:30:49Z, 413,578 bytes) has count 64: 63 works plus Creative-Writing's own root OBSIDIAN.md with kind 'other'. It is large because every row embeds the full note body. The RAG index (built 2026-09-01T00:22:35Z, 1,183,899 bytes, one JSON line) has embed_model nomic-embed-text, partial=false, 173 chunks (c_0000..c_0172) from 65 files including 00_INDEX.md, and dims 768. Its chunk paths use Windows backslashes, so it was built by Windows-native Python. NEW FINDINGS: C:\Users\utopi\Creative-Writing no longer exists on disk. Both state files are therefore orphaned and cannot be rebuilt from their source, and `vault_rag.py status` would print 'vault path no longer exists'. The only .obsidian/ folder is at the REPO ROOT; vault/ has none. So Obsidian has been pointed at Creative-Headquarters/, not vault/ as the docs instruct, and the .gitignore Obsidian rules, which are scoped to vault/.obsidian/, do not cover it. By both tools' file rules, this repo's vault/ holds exactly one corpus note: vault/studio-os/ui/ui-ux-intelligence-integration.md. The Creative-Writing to Content MD migration exists only as an assessment (GAP-ANALYSIS.md, now partly stale). There is no migration script and no files have been migrated. vault/README.md says 'the archive indexes these files', but no code under archive/ references the vault.

## Tools

### vault_rag.py

`cli` · status `runs-today`

Paths: `tools/vault_rag.py`

Local RAG over an Obsidian vault using Ollama. It chunks and embeds every eligible note into a stdlib JSON vector index, then answers questions using only the retrieved chunks, with chunk-id citations. It is the executable form of skills/local_rag_orchestration.skill.md (OBSIDIAN.md 'connection B') and the 'local implementation the archive has been missing' per DECISIONS.md D1.

**Entry points**

- `python3 tools/vault_rag.py status`
  - does: Resolves the endpoint and prints '<endpoint> ok' plus the served models. For each tier in dashboard.json hardware.local_llm.tiers it prints 'ok (<served tag>)' or 'MISSING -- ollama pull <tag>', and the same for embed_model. With no index it prints 'index none -- run: python3 tools/vault_rag.py index' and returns 0. Otherwise it prints '<N> chunks from <vault>', 'built <iso>' and '(PARTIAL)' if partial. If the indexed vault dir exists, it lists notes whose mtime is newer than built ('N note(s) changed since -- reindex: <first 3>...') or prints 'fresh'. If the dir is missing it prints 'vault path no longer exists', which is what the current index would produce because C:\Users\utopi\Creative-Writing is gone.
  - changes: nothing
- `python3 tools/vault_rag.py index [--vault <dir>] [--embed-model <tag>]`
  - does: Chunks and embeds every eligible .md note into state/rag_index/index.json. --vault defaults to <repo>/vault; --embed-model defaults to dashboard.json hardware.local_llm.embed_model. The vault-dir check runs before any endpoint call (exit 1 'no vault at <path>'). Then it resolves the endpoint, runs require_model on the embed model, and exits 1 if there are no eligible files. A file whose sha256[:16] is unchanged reuses its old vectors, but only when the old index has the identical str(resolved vault) and the same embed_model. It saves a partial checkpoint every 20 newly embedded chunks and on any embedding failure. It evicts the embed model after a successful run; the failure path returns 1 without evicting. It prints vault/endpoint/embed/files, then 'indexed N chunks (E embedded, R reused) in Xs', 'written state/rag_index/index.json (X MB)' and 'evicted <model>'.
  - changes: writes state/rag_index/index.json via state/rag_index/index.json.tmp and an atomic replace; creates state/rag_index/ if needed; overwrites any index built from another vault (the first checkpoint save already replaces it)
- `python3 tools/vault_rag.py ask "<question>" [--tier sm|md] [--model <tag>] [--top-k 8] [--rerank-to 4] [--max-words 250] [--json] [--write-dashboard]`
  - does: Loads the index; exits 1 if it is missing or empty; warns if partial. Resolves the endpoint and runs require_model on the index's embed_model and on the tier model (--model overrides the model but TIER_LIMITS still come from --tier). Embeds the question (60 s timeout) and evicts the embed model. Dot-product scores every chunk and takes the top-k, then keeps up to --rerank-to chunks that fit the tier payload cap. Generates with the tier model and evicts it in finally. Prints the answer, a sources list and a window footer, or JSON with --json. There is no --vault flag: it always answers from whichever vault the current index was built from.
  - changes: state/rag_traces/<YYYYMMDDTHHMMSSZ>.txt only when the model output contains <think> blocks; dashboard.json hardware.local_llm.context_used_pct and loaded_tier only with --write-dashboard (the whole file is rewritten with indent=2)
- `python3 tools/vault_rag.py evict`
  - does: Resolves the endpoint (exits 2 if unreachable), then POSTs {model, keep_alive: 0} to /api/generate for every tier model and the embed_model listed in dashboard.json, printing 'released <tag>' for each. Errors are ignored as best effort.
  - changes: Ollama resident memory only
- `python3 tools/vault_rag.py --endpoint <url> {status|index|ask|evict} ...`
  - does: Global option defined on the top-level parser only, so it must come before the subcommand. It overrides dashboard.json hardware.local_llm.endpoint. When given, the WSL gateway fallback is skipped. dashboard.json is still read and must parse.
  - changes: nothing extra
- `python3 tools/vault_rag.py --help`
  - does: argparse help, using the module docstring as the description (RawDescriptionHelpFormatter). CI runs it with -W error::EncodingWarning.
  - changes: nothing

**Inputs**

- vault directory (index --vault; default <repo>/vault)
- question string (ask positional)
- dashboard.json hardware.local_llm: endpoint (http://localhost:11434), embed_model (nomic-embed-text), tiers.sm.model (llama3.1:8b), tiers.md.model (mistral-nemo:12b); _tiers_note marks these tags PROVISIONAL
- CLI overrides: --endpoint, --embed-model, --tier, --model, --top-k, --rerank-to, --max-words, --json, --write-dashboard

**Outputs**

- state/rag_index/index.json: {vault (str of resolved path), embed_model, built (UTC ISO), partial (bool), chunks:[{id 'c_NNNN', file (vault-relative, OS separator, so backslashes on Windows), title, kind, file_hash (sha256[:16] of raw text), text, vec (base64 float32 of the L2-normalized vector)}], dims (final save only)}. Written as a single JSON line with ensure_ascii=False.
- ask stdout: answer, 'sources' lines '[c_id] <score .3f>  <file>', footer '<model> | tier <t> | window <pct>% of <num_ctx>' plus ' | think trace archived' when applicable; if pct >= 60 a 'window past 60%' warning line (non-JSON mode only)
- ask --json: {question, answer, model, tier, sources:[{id, file, title, score (4 dp)}], context_used_pct}
- state/rag_traces/<stamp>.txt (archived <think> text, never shown or re-fed)
- exit codes (docstring and code): 0 ok | 1 index/answer/model problem | 2 Ollama endpoint unreachable

**Reads**

- dashboard.json
- <vault>/**/*.md (default vault/, or the --vault target)
- state/rag_index/index.json
- /proc/version (WSL detection)
- file mtimes of the indexed vault (status)

**Writes**

- state/rag_index/index.json
- state/rag_index/index.json.tmp (transient)
- state/rag_traces/<YYYYMMDDTHHMMSSZ>.txt
- dashboard.json (only ask --write-dashboard)

**Depends on**

- Python 3 stdlib only (argparse, base64, hashlib, json, re, subprocess, time, urllib, array, datetime, pathlib)
- Ollama HTTP API: GET /api/tags, POST /api/embeddings, POST /api/generate
- embedding model served by Ollama (nomic-embed-text; the existing index shows 768 dims)
- tier generation models served by Ollama (llama3.1:8b sm, mistral-nemo:12b md per dashboard; provisional)
- `ip route show default` (subprocess, only under WSL for the gateway fallback)

**Environment and secret names (names only)**

- none read by the script
- OLLAMA_HOST (named in the unreachable-endpoint error text as a Windows-side requirement for WSL2 access; BOOT.md section 2)

**Gates and checkpoints**

- resolve_endpoint: exits 2 with guidance if GET /api/tags (6 s timeout) does not answer. Without --endpoint under WSL, it retries with the default-gateway IP substituted into the host.
- require_model: the tag family (text before ':') must appear in /api/tags, otherwise exit 1 printing 'ollama pull <tag>' and 'python3 tools/reconcile_models.py --write'. No silent substitution.
- CHECKPOINT-F1: partial index (partial=true) saved every 20 newly embedded chunks and on any embedding failure ('partial index saved (N chunks) -- re-run to resume', exit 1)
- ask: exit 1 'no index yet' if the index is missing or has no chunks; warning if partial=true
- eviction contract: embed model evicted before generation; generation model evicted in a finally block; every embed/generate call uses keep_alive '5m'
- window ceiling: context_used_pct >= 60 prints a warning in non-JSON mode only; it never stops the run
- index: exit 1 if the vault dir is missing (checked before the endpoint) or has no eligible notes

**Invoked by**

- operator by hand (BOOT.md section 2 lines 74-76, OBSIDIAN.md section B, README.md)
- skills/local_rag_orchestration.skill.md P5 preflight: `python3 tools/vault_rag.py status | grep -qE "index +[0-9]+ chunks"`, then greps for 'changed since'
- CI .github/workflows/verify.yml (--help, plus an importlib core-logic test)

**Invokes**

- Ollama /api/tags, /api/embeddings, /api/generate (including keep_alive 0 eviction)
- ip route show default (subprocess, WSL only)

**Notes**

FILE SELECTION: sorted rglob('*.md'). A file is skipped if any parent directory component starts with '_' or '.', or if it is named SCHEMA.md or README.md at any depth. 00_INDEX.md IS indexed. FRONTMATTER: parsed only when the text starts with '---' and a closing '\n---' is found. Regex '^(\w[\w_]*):\s*(.+?)\s*$' needs a non-empty value; only title/kind/project/status/id are kept, and only title and kind are stored per chunk. The title falls back to the file stem with a leading '<digits>_' removed and '_' turned into spaces (e.g. 00_INDEX gives 'INDEX'). CHUNKING: tokens are chars/4. The body is split on blank lines and paragraphs are packed up to 800 tokens (3,200 chars). A new chunk begins with the last 480 chars (120 tokens) of the previous one. While a buffer exceeds 4,800 chars (1.5x), 3,200-char slices are cut off with 480-char overlap. EMBEDDING: POST /api/embeddings {model, prompt, keep_alive '5m'}; timeout 120 s at index and 60 s for the ask question. Vectors are L2-normalized and packed as float32 base64. RETRIEVAL: brute-force dot product over all chunks, sorted, top-k (default 8). Then greedily keep up to rerank-to (default 4) chunks whose text fits the remaining budget of payload_tokens x 4 chars, skipping oversized ones. If none fit, the best chunk is truncated to the cap. This is similarity order, not a cross-encoder. Tier limits: sm num_ctx 8192 / payload 3000 tok (12,000 chars) / num_predict 800; md 4096 / 1200 tok (4,800 chars) / 600. ANSWER PROMPT (QUERY_SUBPROMPT, sent as the user prompt with no system field): answer from the studio's private corpus using ONLY the retrieval block; if it does not contain the answer, say so plainly and do not fill gaps from general knowledge; cite chunk ids in square brackets like [c_0412] after each claim; 'Question: {question}' followed by <RETRIEVAL>...</RETRIEVAL>; answer in at most {max_words} words after the line 'ANSWER:'. Retrieval entries are '[id] (title -- file)\ntext'. Generate options: stream false, keep_alive 5m, temperature 0.6, top_p 0.95, tier num_ctx/num_predict, 600 s timeout. POST-PROCESSING: all <think>...</think> blocks are removed and archived. re.sub('^ANSWER:\s*', flags=re.M) strips 'ANSWER:' at the start of EVERY line, not only the first. context_used_pct = round(100 x (prompt_eval_count or len(prompt)//4) / num_ctx). OTHER VAULTS: index --vault can target any directory; only one index exists at a time. The current index was built from C:\Users\utopi\Creative-Writing, and that directory no longer exists (verified 2026-09-28). OBSERVATIONS FROM SOURCE: (a) chunk ids are renumbered sequentially on every index run, so a [c_NNNN] citation is not stable across re-indexes. (b) Reuse is keyed on the whole-file hash. A file partly embedded when a checkpoint or failure save happened is stored under its hash with only those chunks; on resume it is 'reused' as-is and never completed. (c) status staleness compares mtime to the build time only; it cannot detect deleted notes. (d) status never checks that the index's embed_model is served. (e) Because status prints no 'changed since' line when the vault path is missing, the skill's P5 preflight would report OK:P5 for the current orphaned index. (f) Not implemented here, though the skill specifies them: SYNTHESIS mode (MAP/REDUCE to state/rag_notes/), ROUTER_SUBPROMPT mode classification, CHECKPOINT-F2 (answer to the dashboard event_log) and chunk-title generation. EVIDENCE OF USE: index.json exists (partial=false, 173 chunks, 768 dims, file paths with backslashes, so it was run by Windows-native Python). dashboard.json has context_used_pct 0 and loaded_tier null, and there is no state/rag_traces/, so nothing on disk shows ask was ever run with --write-dashboard or with a think-emitting model.

### vault_manifest.py

`cli` · status `runs-today`

Paths: `tools/vault_manifest.py`

Writes state/vault_manifest.json, a small one-row-per-note index of a vault with no embeddings, for the static hub UI (hub/index.html Library tab; the Ask tab's browser-side index is built from it). Each row carries the note's full body so the browser never has to read the vault directly.

**Entry points**

- `python3 tools/vault_manifest.py`
  - does: Builds the manifest from <repo>/vault into state/vault_manifest.json
  - changes: writes state/vault_manifest.json
- `python3 tools/vault_manifest.py [--vault <dir>] [--out <file>]`
  - does: Builds the manifest from any vault directory (the docstring example is --vault ../Creative-Writing). --out overrides the output path (default <repo>/state/vault_manifest.json). Prints ' vault <path>', ' notes <n>' and ' wrote <path relative to repo if inside it>'.
  - changes: writes the --out file (creates parent directories)
- `python3 tools/vault_manifest.py --help`
  - does: argparse help (the module docstring)
  - changes: nothing

**Inputs**

- vault directory (--vault, default <repo>/vault)
- --out path (default <repo>/state/vault_manifest.json)

**Outputs**

- manifest JSON: top level {vault (absolute resolved path), built (UTC ISO), count, notes:[...]}. Each note: {path (vault-relative, forward slashes), id, title, kind, status, project, tags (list), created, updated, body (full body minus frontmatter, stripped), overview, next_steps_open (int), content_hash (sha256[:16] of the raw file), word_count}. Notes are sorted by updated (else created) descending; the file is written with indent=2 and ensure_ascii=False.
- exit 0 ok; exit 1 with 'no vault at <path>' if --vault is not a directory

**Reads**

- <vault>/**/*.md (default vault/, or the --vault target)
- file mtimes (plain-markdown notes)

**Writes**

- state/vault_manifest.json (or the --out path)

**Depends on**

- Python 3 stdlib only (argparse, hashlib, json, re, datetime, pathlib); uses Path.is_relative_to

**Gates and checkpoints**

- exits 1 'no vault at <path>' if --vault is not a directory
- no validation of Content MD required fields, type: content-md, section order, or kind/status vocabulary

**Invoked by**

- operator by hand after editing notes (README.md line 63; error text in hub/app.js lines 120-121 and 164 and hub/index.html line 85: 'python3 tools/vault_manifest.py --vault <path> ... then Refresh')

**Notes**

FILE SELECTION: the same rule as vault_rag.py (skip any parent directory starting with '_' or '.'), but EXCLUDED_NAMES = SCHEMA.md, README.md and 00_INDEX.md. Excluding 00_INDEX.md is manifest-only, per the docstring ('keep the two in sync'). TWO NOTE SHAPES: (1) Content MD branch, used when the frontmatter yields at least one of id/title/kind/project/status/created/updated/tags; type: content-md is never checked. The regex '^(\w[\w_]*):\s*(.*)$' accepts EMPTY values, so a template-style 'kind: ' gives kind '' rather than 'other'. tags '[a, b]' becomes a list; other values have their quotes stripped. Multi-line YAML (artifacts:) and skills/context_brand/context_domain/type are dropped. The title falls back to the stem with [_-] turned into spaces. overview is the text of '## Overview'. next_steps_open counts lines starting '- [ ]' inside '## Next Steps'. created/updated come from the frontmatter. (2) Plain markdown (no frontmatter): title is the first '# ' heading, else the stem. kind comes from the top-level folder with leading digits and an optional '_'/'-' removed and '_' turned into spaces (e.g. 01_Books becomes Books); files at the vault root get 'other'. overview joins the **Type:** and **Note:** values with ' — ' from the block before the first '\n---'; otherwise it is the first paragraph over 20 chars after that marker (headings dropped), truncated to 400 chars plus '…'. created and updated are both the file's mtime date in UTC; next_steps_open is 0. There is no CI coverage: verify.yml does not reference vault_manifest.py.

### state/rag_index/index.json (RAG vector index)

`data` · status `generated`

Paths: `state/rag_index/index.json`

The single on-disk vector index that vault_rag.py index writes and ask/status read. It holds one vault at a time.

**Inputs**

- vault_rag.py index

**Outputs**

- retrieval corpus for vault_rag.py ask; source-vault and freshness info for status

**Depends on**

- vault_rag.py

**Gates and checkpoints**

- partial flag set by CHECKPOINT-F1 saves
- gitignored by .gitignore line 17 'state/' (line 39 is a comment restating this)

**Invoked by**

- vault_rag.py index (writer)
- vault_rag.py ask and status (readers)

**Notes**

Observed header: vault 'C:\\Users\\utopi\\Creative-Writing', embed_model 'nomic-embed-text', built '2026-09-01T00:22:35.909751+00:00', partial false; the trailing key is dims 768. There are 173 chunks (c_0000..c_0172) from 65 distinct files: 63 works, 00_INDEX.md (chunk c_0000, title 'INDEX') and Creative-Writing's root OBSIDIAN.md. All 173 chunks have kind '' because the source has no frontmatter. File paths use backslashes (e.g. '01_Books\\01_The_First_Friend.md'), showing it was built by Windows-native Python. Size is 1,183,899 bytes as one JSON line; file mtime Aug 31 20:22 local. ORPHANED: its source vault C:\Users\utopi\Creative-Writing does not exist on disk now, so status reports 'vault path no longer exists' and ask still answers from this stale Creative-Writing corpus. It was not built from this repo's vault/.

### state/vault_manifest.json (hub note manifest)

`data` · status `generated`

Paths: `state/vault_manifest.json`

Browser-loadable note index that hub/app.js fetches for the Library tab. The hub Ask tab chunks and embeds the notes' bodies from it into its own browser-side index.

**Inputs**

- vault_manifest.py

**Outputs**

- hub Library cards; corpus for the hub Ask tab's in-browser index

**Depends on**

- vault_manifest.py

**Gates and checkpoints**

- gitignored by .gitignore line 17 'state/'

**Invoked by**

- vault_manifest.py (writer)
- hub/app.js fetch('../state/vault_manifest.json') (reader, line 111)

**Notes**

Observed: vault 'C:\\Users\\utopi\\Creative-Writing', built '2026-09-01T04:30:49.101105+00:00', count 64, 413,578 bytes. Paths run from 01_Books/01_The_First_Friend.md through 11_Essays/07_Shoot_for_the_Moon.md (11_Essays starts at 02_), then a root-level 'OBSIDIAN.md' (kind 'other', title 'This repo is an Obsidian vault', Creative-Writing's own guide, distinct from this repo's OBSIDIAN.md). Frontmatter-derived fields are empty ('id': '', 'status': '', 'project': '', 'tags': []). kind values are folder-derived (Books, Novels, Stories, Book Concepts, Worldbuilding, Songs, Poems and Prose, Letters, Dream Journal, Characters, Essays, other), not the SCHEMA vocabulary. Dates are file-mtime dates: ONLY the first note (The First Friend) has created/updated 2026-08-31; the other 63, OBSIDIAN.md included, are 2026-08-30. The first note's word_count is 10,784. The size comes from the embedded full 'body' of every note. README.md describes the Library as 'one card per Content MD in vault/', but the manifest holds Creative-Writing works. Its source directory no longer exists, so it cannot be regenerated from that source.

### state/rag_traces/ (think-trace archive)

`data` · status `never-exercised`

Paths: `state/rag_traces/`

Audit archive for <think> blocks stripped from ask answers: one timestamped .txt per answer that contained a trace.

**Inputs**

- vault_rag.py ask (only when the model output contains <think>...</think>)

**Outputs**

- state/rag_traces/<YYYYMMDDTHHMMSSZ>.txt

**Depends on**

- vault_rag.py

**Gates and checkpoints**

- gitignored via 'state/'

**Invoked by**

- vault_rag.py ask

**Notes**

The directory does not exist: state/ holds only rag_index/ and vault_manifest.json. A model that emits no <think> would never create it, so its absence does not prove ask never ran.

### Obsidian vault (vault/)

`data` · status `partial`

Paths: `vault/`, `vault/README.md`, `vault/studio-os/ui/ui-ux-intelligence-integration.md`

The studio's source of truth for creative work: plain-markdown Content MDs meant to be edited in Obsidian. The indexers only read it.

**Entry points**

- `Obsidian -> Open folder as vault -> Creative-Headquarters/vault/`
  - does: Documented setup (vault/README.md step 1, OBSIDIAN.md A1). On disk vault/ has NO .obsidian/ folder, while the repo root does, so the folder actually opened in Obsidian was Creative-Headquarters/.
  - changes: Obsidian writes .obsidian/ state in whichever folder is opened
- `Obsidian Settings -> Files and links -> template folder = _templates`
  - does: Enables the Content MD template for core Templates or Templater
  - changes: Obsidian settings
- ````dataview\nTABLE kind, project, updated\nFROM "vault"\nWHERE type = "content-md" AND status = "in-progress"\nSORT updated DESC\n````
  - does: Optional Dataview query from vault/README.md listing in-progress Content MDs. FROM "vault" only resolves when the Obsidian vault is the repo root, which matches the on-disk .obsidian/ location but contradicts README step 1.
  - changes: nothing

**Inputs**

- Content MDs authored by a person or agent per vault/SCHEMA.md

**Outputs**

- corpus for vault_rag.py index and vault_manifest.py (both default --vault)
- note count for the tools/verify_system.py L3-consistency check

**Depends on**

- Obsidian (optional: Templater, Dataview community plugins)

**Gates and checkpoints**

- 'Directories prefixed _ are ignored by ingest' (vault/README.md); the tools also skip '.'-prefixed dirs and README.md/SCHEMA.md
- verify_system.py counts notes with a slightly different rule: it excludes any path part starting with '_' (filename included) and README.md/SCHEMA.md, and does not check '.' dirs. It fails if gates are unauthored, there are no notes, and state != BLOCKED.

**Invoked by**

- operator in Obsidian
- vault_rag.py index (default --vault)
- vault_manifest.py (default --vault)
- tools/verify_system.py (counts notes)

**Notes**

Contents on disk: README.md, SCHEMA.md, _templates/content-md.md, _examples/example-stipple-brush.md, _migration/GAP-ANALYSIS.md and studio-os/ui/ui-ux-intelligence-integration.md. After the exclusion rules only ONE corpus note remains: studio-os/ui/ui-ux-intelligence-integration.md (id cmd_20260831_ui-ux-intelligence-integration, kind ui, status in-progress, project [[Studio Headless OS]], created 2026-08-31, updated 2026-09-01, skills [ui_ux_intelligence, css_html_ui]). Its Timeline says writing it satisfied verify_system.py's L3-consistency check, which DEGRADED state needs while gates are unauthored. Its folder 'studio-os/ui' follows <project>/<kind>/ loosely. Neither state file was built from this directory. vault/README.md says 'the archive indexes these files', but no file under archive/ references the vault or Content MDs; vault_rag.py and vault_manifest.py are the only implemented readers.

### Content MD schema

`protocol` · status `partial`

Paths: `vault/SCHEMA.md`

The Content MD spec: the durable, cold-readable record of one made thing (character, design, audio piece, shot, brush...). It is the unit of memory; resuming work means reading it cold.

**Outputs**

- contract consumed by vault_manifest.py (Overview/Next Steps extraction, frontmatter keys), vault_rag.py (title/kind), the Obsidian template, GAP-ANALYSIS, and agents writing notes

**Gates and checkpoints**

- THE ONE RULE: the first screenful must answer 'what is this, and what do I do next'. ## Overview and ## Next Steps come first, always, so that a person in Obsidian or an agent reading the first 40 lines gets a usable answer
- Required frontmatter: id, type, kind, title, status, created, updated
- Sections appear in fixed order; omit one only when it is genuinely empty; never pad or reorder
- One Content MD per made thing, not per session: resuming updates the file (append to Timeline, rewrite Next Steps) and never creates a second file
- Agent rules: never fabricate a Timeline entry; rewrite ## Next Steps in full each session; append to ## Timeline and never edit past entries (correct with a new dated entry); bump updated (the hub sorts by it); move answered Open Questions into Decisions in Force; ## Method must be sufficient to reproduce
- If status: blocked, the first Next Steps item names the blocker and what would unblock it

**Invoked by**

- agents and operator writing notes
- vault/_migration/GAP-ANALYSIS.md (assesses Creative-Writing against it)

**Notes**

FILE PLACEMENT: vault/<project>/<kind>/<slug>.md (e.g. aurora/character/aurora-lead.md); _templates/ and _examples/ sit alongside. FRONTMATTER (YAML, Obsidian-native, 'queryable by Dataview, indexed by the archive'): id (cmd_<YYYYMMDD>_<slug>, stable forever) | type (always the literal content-md; marks the file for ingest) | kind | title (human title shown in the hub) | project (wikilink to the project note, e.g. "[[Project Aurora]]"; optional so one-offs need no invented project) | status | created (date) | updated (date) | skills (skill ids that touched it) | context_brand (e.g. [visual_identity, color_science]) | context_domain (e.g. [classical_illustration]) | artifacts (list of {path, role}; role is one of concept-frame, final, variant, reference, export) | tags. REQUIRED: id, type, kind, title, status, created, updated. OPTIONAL: project, skills, context_brand, context_domain, artifacts, tags. KINDS (flat on purpose): character, design, audio, video, 3d, brush, copy, ui, world, other. STATUS: seed (intent captured, nothing made) | in-progress (active, has artifacts) | blocked (needs something; say what in Next Steps) | complete (done; may be referenced as precedent) | archived (superseded or abandoned; excluded from active views). BODY SECTIONS IN ORDER: ## Overview (2-4 sentences, no preamble) | ## Next Steps (markdown checkboxes, most important first, concrete enough to start without asking) | ## Timeline (append-only, newest last, one entry per session headed '### YYYY-MM-DD · <skill>'; the exact-steps record, not a transcript) | ## Method (reproducible recipe: prompts, parameters, settings, versions; prefer a code block) | ## Decisions in Force (binding rules for later sessions, not history) | ## Open Questions (deleted when answered) | ## Contradictions (conflicts naming the other file; empty is normal) | ## Links (wikilinks; they build Obsidian's graph). ENFORCEMENT: neither indexer validates required fields, type: content-md, section order or the kind/status vocabulary. vault_manifest treats any recognized frontmatter key as a Content MD. Status is partial because the spec exists but is enforced only by convention.

### Content MD Obsidian template

`data` · status `runs-today`

Paths: `vault/_templates/content-md.md`

Skeleton for a new Content MD, for Obsidian core Templates or Templater. It pre-fills the frontmatter and all eight sections in schema order.

**Inputs**

- Obsidian date tokens {{date:YYYYMMDD}}, {{date:YYYY-MM-DD}}

**Outputs**

- new note with id 'cmd_<date>_' (slug left blank), type content-md, status seed, created/updated set to today, empty lists for skills/context_brand/context_domain/artifacts/tags, blank kind/title/project, and the 8 sections with HTML-comment guidance (Timeline heading '### <date> · ', empty Method code block)

**Depends on**

- Obsidian core Templates or Templater plugin

**Gates and checkpoints**

- the template folder must be set to _templates in Obsidian settings

**Invoked by**

- operator in Obsidian

**Notes**

Excluded from both indexers because it sits under a '_' directory. If a note made from it kept the blank 'kind: ' line, vault_manifest would record kind '' while vault_rag would drop the key. Whether the template has ever been used cannot be determined; 'runs-today' only means it is present and well-formed.

### Worked example Content MD (dry stipple brush)

`doc` · status `runs-today`

Paths: `vault/_examples/example-stipple-brush.md`

Reference example of a fully filled Content MD (kind brush, status in-progress, project [[Brush Kit v1]], skills [brush_designer]) showing every section, including a Method block of Procreate brush parameters.

**Invoked by**

- humans or agents learning the schema

**Notes**

vault/README.md calls it safe to delete once real notes exist. It lives under '_examples', so ingest ignores it. Its Method reproduces from tools/brush-designer/ defaults (that directory exists). Its artifacts, assets/brushes/dry-stipple-v3.brush (final) and dry-stipple-v1.brush (variant), do NOT exist: there is no assets/ directory at the repo root. Its wikilinks [[Brush Kit v1]], [[wet-stipple-brush]] and [[visual_identity]] do not resolve inside vault/. An empty 0-byte wet-stipple-brush.md exists at the repo root (see the repo-root Obsidian entry). 'runs-today' only means the file is present and valid as an example.

### Creative-Writing -> Vault migration (GAP-ANALYSIS)

`doc` · status `specified-not-implemented`

Paths: `vault/_migration/GAP-ANALYSIS.md`

Assessment of what separates the 63 works in groot99-droid/Creative-Writing from routable Content MDs, and which decisions the author must make before migrating.

**Inputs**

- Creative-Writing repo (counted as 65 md files: 63 works + 00_INDEX.md + README.md across 11 numbered folders 01_Books..11_Essays)
- vault/SCHEMA.md
- Router.md §3 routing table and §5 resolution ladder
- dashboard.json state

**Outputs**

- gap tables, kind-mapping proposal, 7 decisions required before migration

**Gates and checkpoints**

- 'Assessment only — no files have been migrated'
- Decisions required BEFORE migration (author-only): (1) kind vocabulary (blocks everything else) (2) project grouping (3) created dates (4) status per work (5) granularity (Dream Journal holds 6 entries; The First Friend is a book plus appendix) (6) Next Steps policy for finished work (recommends omission) (7) which brand gates to author first
- 'Never fabricate a Timeline entry': the only honest Timeline entry for a migrated work is the migration itself, dated, with source volume and line range

**Invoked by**

- operator / planning

**Notes**

SOURCE: Creative-Writing, the 'Living Archive'. Per-folder counts: Books 1, Novels 5, Stories 9, Book Concepts 8, Worldbuilding 3, Songs 2, Poems and Prose 21, Letters 1, Dream Journal 2, Characters 5, Essays 6. WHAT IS RIGHT: a uniform header block on 63/63 files (# Title, **Type:**, **Source:**, **Text:**, optional **Note:**, then ---); provenance (e.g. Master_Volume_1 line ranges); 00_INDEX.md consistent (63 links, 0 broken); unique title slugs; verbatim text. MISSING: frontmatter on 0/63, Content MD sections on 0/63, 0 wikilinks, no project layer (the numbered folders are kinds, not projects), no usable chronology (all 5 commits dated 2026-08-27). DERIVABILITY: mechanical fields are id, type, title, updated and tags, plus the section skeleton ('roughly 6 of 13 frontmatter fields'). Partial: kind, status (folder proxy: 04_Book_Concepts gives seed, finished works give complete), context_domain. Not derivable: created, project, context_brand. N/A: skills, artifacts. Body: Overview is partial; Next Steps, Timeline, Method, Decisions in Force and Links are not derivable. KIND MISMATCH: 52 works map to copy (83%), 6 to character, 3 to world, 2 to audio (below the L2 floor of 3). It recommends option 1: extend the vocabulary with poem, story, novel, essay, concept and journal (a SCHEMA amendment plus a DECISIONS entry). HEADLINE: a perfect migration unblocks 0 of 8 skill routes. The corpus can serve 2 of 10 brand gates (brand_voice, narrative_continuity), and memory_discipline only weakly. The cheapest path out of BLOCKED is authoring 2-3 context/brand/*.context.md files, independent of migration. No migration script exists under tools/ (tools/ holds bootstrap.sh, brush-designer/, hw/, launcher/, reconcile_models.py, ui-ux-pro-max/, vault_manifest.py, vault_rag.py, verify_system.py). STALENESS: the document assumes all 10 gates are unauthored, the vault is empty, the state is BLOCKED and there are 8 skills. dashboard.json now shows state DEGRADED with 3 gates authored:true, and the ui-ux note describes ui_ux_intelligence as the ninth routed skill. Creative-Writing also had at least one more .md (a root OBSIDIAN.md) when the index and manifest were built than the 65 counted here. SCHEMA.md still lists the original 10 kinds, so decision (1) is unresolved.

### Obsidian -> Ollama plugin connection (connection A)

`protocol` · status `specified-not-implemented`

Paths: `OBSIDIAN.md`

In-app writing assistance: an Obsidian community plugin calls the local Ollama server to chat in the sidebar, rewrite a selection or continue a paragraph, and it sees the open note. OBSIDIAN.md says to set it up first.

**Entry points**

- `ollama list`
  - does: Lists installed models (OBSIDIAN.md section 0)
  - changes: nothing
- `curl http://localhost:11434/api/tags`
  - does: Confirms the Ollama server is serving; if ollama list works but curl does not, start the tray app or `ollama serve`
  - changes: nothing
- `ollama pull llama3.1:8b`
  - does: Pulls the sm-tier everyday model
  - changes: Ollama model store
- `ollama pull nomic-embed-text`
  - does: Pulls the embedding model that connection B needs
  - changes: Ollama model store
- `python3 tools/reconcile_models.py [--write]`
  - does: Reports drift between dashboard.json model tags and what Ollama serves; --write applies it (reconcile_models.py exit codes: 0 match, 1 drift, 2 endpoint unreachable)
  - changes: dashboard.json with --write
- `setx OLLAMA_ORIGINS "app://obsidian.md"`
  - does: Windows, run once: lets Obsidian's renderer origin through Ollama's cross-origin check. Afterwards fully quit Ollama from the tray and reopen it (setx affects new processes only).
  - changes: user environment variable
- `export OLLAMA_ORIGINS="app://obsidian.md"`
  - does: macOS/Linux equivalent
  - changes: shell environment

**Inputs**

- an Obsidian vault: Creative-Headquarters/vault/ or Creative-Writing/ per OBSIDIAN.md A1 (both can be open as separate vaults)

**Outputs**

- in-editor generations from the local model

**Writes**

- plugin embedding caches such as .smart-env/ and plugin vectors/ folders, if the plugin indexes the vault (OBSIDIAN.md: several hundred MB)

**Depends on**

- Obsidian
- one community plugin: Copilot, Smart Connections or Text Generator (all three listed; none chosen)
- Ollama at http://localhost:11434

**Environment and secret names (names only)**

- OLLAMA_ORIGINS
- OLLAMA_HOST

**Gates and checkpoints**

- OLLAMA_ORIGINS must include app://obsidian.md. Without it the plugin reports 'failed to fetch' or 'cannot connect' while curl from a terminal works. Ollama must be fully restarted after setting it.
- From WSL2: Windows needs OLLAMA_HOST=0.0.0.0 and an inbound rule for port 11434 (BOOT.md section 2)
- Plugin settings: Provider = Ollama (or custom / OpenAI-compatible); Base URL = http://localhost:11434; Model = llama3.1:8b or whatever `ollama list` shows; API key blank or a placeholder
- Git hygiene as claimed by OBSIDIAN.md: plugins/*/data.json (where plugin API keys live), workspace.json, cache, .trash/, .smart-env/, state/rag_index/, *.faiss and .env are gitignored. In this repo's actual .gitignore the Obsidian patterns are scoped to vault/: vault/.obsidian/plugins/*/data.json, workspace.json, workspace-mobile.json, cache, graph.json; vault/.trash/; vault/.smart-env/; vault/.smart-connections/. Global patterns are *.faiss, *.embeddings.json, .env, .env.* and state/. The real .obsidian/ is at the repo root, which these vault/-scoped patterns do NOT match.

**Invoked by**

- operator (manual setup)

**Invokes**

- Ollama HTTP API from Obsidian's renderer (origin app://obsidian.md)

**Notes**

PLUGIN CHOICE: OBSIDIAN.md picks none. It lists Copilot (chat sidebar over the current note or the whole vault; first-class Ollama provider), Smart Connections (surfaces related notes; local embeddings) and Text Generator (templated generation; custom endpoint), and warns that plugin UI labels change between versions ('the three values are what matter'). Nothing in the repo implements this connection; it is a manual configuration guide. ON DISK: a .obsidian/ folder exists at the repo root (created Aug 31 local, touched Sep 17), and vault/ has none. A top-level directory listing (file contents not read) shows no plugins/ subfolder, so there is no on-disk evidence that a community plugin is installed. Whether OLLAMA_ORIGINS is set cannot be determined from files. README.md adds that the hub Ask tab needs 'one more origin to allow'. The hub is served by tools/launcher/Start-Hub.ps1 at http://localhost:<port>/hub/ (default 8765, scanning 10 ports, bound to 127.0.0.1), but no document names that origin explicitly. SIZING: an 8B Q4 model is about 6 GB resident and a 12-14B about 10 GB on a 16 GB machine; md needs AC power and a quiet desktop; sm is the default; raising num_ctx costs memory because Ollama allocates the KV cache when the model loads.

### Repo-root Obsidian vault state (.obsidian/ and stray note)

`data` · status `generated`

Paths: `.obsidian/`, `wet-stipple-brush.md`

On-disk evidence of how Obsidian is actually being used: the repo root, not vault/, holds the Obsidian vault configuration, plus an empty note named after an unresolved wikilink.

**Inputs**

- Obsidian opening Creative-Headquarters/ as a vault

**Depends on**

- Obsidian

**Gates and checkpoints**

- not covered by .gitignore's vault/.obsidian/* patterns (tracked status not checked; .git/ not read)

**Invoked by**

- operator in Obsidian

**Notes**

Per the hard rules, .obsidian/ contents were not read; only its existence and top-level names were observed (no plugins/ subfolder). wet-stipple-brush.md at the repo root is a 0-byte file (mtime 2026-09-17 15:36 local). Its name matches the unresolved [[wet-stipple-brush]] wikilink in vault/_examples/example-stipple-brush.md; its origin is not recorded. Neither indexer sees it, because both default to <repo>/vault. With the repo root as the Obsidian vault, the Dataview example's FROM "vault" targets the vault/ subfolder correctly, while vault/README.md step 1 ('Open this directory as a vault') is not what was done.

### CI: vault_rag smoke and core-logic test

`ci` · status `partial`

Paths: `.github/workflows/verify.yml`

Checks that vault_rag.py parses --help with UTF-8-explicit I/O, and unit-checks chunking, the vector pack/unpack round trip and frontmatter stripping without an Ollama server.

**Entry points**

- `python3 -W error::EncodingWarning tools/vault_rag.py --help > /dev/null`
  - does: Step 'Tools declare their encodings' (with PYTHONWARNDEFAULTENCODING=1): fails on any implicit-encoding file call (PEP 597). The same step runs verify_system.py --quiet and reconcile_models.py --help.
  - changes: nothing
- `python3 -W error::EncodingWarning - <<'EOF' ... EOF (step 'vault_rag core logic')`
  - does: Imports tools/vault_rag.py via importlib. Asserts that chunk() on 12 x ~1 KB paragraphs is non-empty and every chunk is <= CHUNK_TOKENS*CHARS_PER_TOKEN*1.5. Asserts that normalize -> pack -> unpack keeps unit length within 1e-5. Asserts that strip_frontmatter('---\ntitle: A -- B\nkind: copy\n---\nprose here') gives title 'A -- B' and body 'prose here', and that a note with no frontmatter is all body. Prints 'vault_rag core logic ok'.
  - changes: nothing

**Inputs**

- tools/vault_rag.py

**Outputs**

- 'vault_rag core logic ok' or a failing assertion

**Reads**

- tools/vault_rag.py

**Depends on**

- GitHub Actions ubuntu-latest, actions/checkout@v4, actions/setup-python@v5 with Python 3.11

**Environment and secret names (names only)**

- PYTHONWARNDEFAULTENCODING (set to "1"; not a secret)

**Gates and checkpoints**

- -W error::EncodingWarning makes implicit-encoding calls fatal
- triggers: push to main, pull_request, workflow_dispatch

**Invoked by**

- GitHub Actions (workflow 'verify')

**Invokes**

- tools/vault_rag.py (import and --help only; nothing runs against Ollama)

**Notes**

Covers vault_rag.py only; verify.yml never references vault_manifest.py. 'partial' refers to coverage: index/ask/evict/status against Ollama, retrieval, payload trimming and the reuse/resume logic are untested. Run history was not inspected.

## Usage flows

### First-time setup and query of this repo's vault

1. ollama list; curl http://localhost:11434/api/tags (confirm Ollama is serving; otherwise start the tray app or run `ollama serve`)
2. ollama pull llama3.1:8b; ollama pull nomic-embed-text
3. python3 tools/reconcile_models.py then python3 tools/reconcile_models.py --write (make dashboard.json model tags match reality)
4. python3 tools/vault_rag.py status (endpoint ok, tier/embed models ok or MISSING; today the index line reads '173 chunks from C:\Users\utopi\Creative-Writing' plus 'vault path no longer exists')
5. python3 tools/vault_rag.py index (default --vault <repo>/vault; only 1 eligible note today, studio-os/ui/ui-ux-intelligence-integration.md; replaces the orphaned Creative-Writing index; no reuse because the vault path differs)
6. python3 tools/vault_rag.py ask "what did I decide about X" [--json] [--tier sm|md] [--write-dashboard]
7. python3 tools/vault_manifest.py (so the hub Library shows vault/ instead of the stale Creative-Writing manifest)
8. python3 tools/vault_rag.py evict (optional; each command already evicts on exit)

### Index and browse the Creative-Writing archive (reconstructs what state/ reflects; the source dir is now missing)

1. python3 tools/vault_rag.py index --vault ../Creative-Writing (produced the current index.json: 173 chunks, nomic-embed-text, 768 dims, built 2026-09-01T00:22Z by Windows-native Python. Re-running today fails with 'no vault at C:\Users\utopi\Creative-Writing', exit 1.)
2. python3 tools/vault_manifest.py --vault ../Creative-Writing (produced the current state/vault_manifest.json: 64 notes with full bodies, built 2026-09-01T04:30Z; would also fail today)
3. tools/launcher/Start-Hub.ps1 [-Port 8765] [-PortSearch 10] [-NoBrowser] [-Stop] (loopback http.server on the repo root; opens http://localhost:<port>/hub/)
4. hub/app.js fetches ../state/vault_manifest.json for the Library tab. The Ask tab builds its own localStorage index ('hub:index:v1') from the manifest bodies via /api/embeddings.
5. python3 tools/vault_rag.py ask "which stories share the drowning motif" --json (ask takes no --vault; it answers from the stale Creative-Writing index while that is the indexed vault)

### vault_rag ask internal pipeline

1. Load state/rag_index/index.json; exit 1 if it is missing or has no chunks; warn if partial
2. Resolve the endpoint (--endpoint, else dashboard.json hardware.local_llm.endpoint; WSL gateway fallback only without --endpoint); exit 2 if unreachable
3. Pick the tier model (--model, else dashboard tiers[--tier].model) and the embed model (index.embed_model); require_model on both (family match) or exit 1
4. POST /api/embeddings for the question (60 s); L2-normalize; evict the embed model
5. Dot product against every chunk vector; sort; take --top-k (default 8)
6. Greedily keep up to --rerank-to (default 4) chunks that fit payload_tokens*4 chars (sm 12,000 / md 4,800); if none fit, truncate the best chunk to the cap
7. Build QUERY_SUBPROMPT (ONLY the retrieval block; say so if the answer is absent; cite [c_id]; at most --max-words, default 250; after 'ANSWER:')
8. POST /api/generate (stream false, temperature 0.6, top_p 0.95, tier num_ctx/num_predict, keep_alive 5m, 600 s); evict the model in finally
9. Strip every <think> block (archive to state/rag_traces/<stamp>.txt) and line-initial 'ANSWER:'; compute context_used_pct
10. Print the answer, sources and window footer with the >= 60% warning, or JSON without the warning; with --write-dashboard, write context_used_pct and loaded_tier to dashboard.json

### Incremental refresh after editing notes

1. Edit or add notes in Obsidian
2. python3 tools/vault_rag.py status (shows the count and first 3 notes with mtime newer than 'built'; deleted notes are not detected)
3. python3 tools/vault_rag.py index [--vault <same dir>] (unchanged file hashes reuse their vectors only if the resolved vault path string and embed model match the old index; changed files are re-embedded; checkpoint every 20 new chunks; chunk ids are renumbered)
4. python3 tools/vault_manifest.py [--vault <same dir>] (the hub does not read the vault directly)
5. Refresh in the hub; rebuild the Ask tab index (it re-embeds only notes whose content_hash changed)

### Resume an interrupted index

1. An embedding failure, or a kill after a checkpoint, leaves index.json with partial=true (a failure exits 1 without evicting)
2. Re-run python3 tools/vault_rag.py index with the same --vault and embed model
3. Files whose hash is present are reused and the rest are embedded. Caveat from source: a file that was only partly embedded is reused with its partial chunk list and never completed; delete index.json to force a clean rebuild.

### Author or resume a Content MD (per SCHEMA.md)

1. Open the vault in Obsidian (documented: vault/; on disk: the repo root was opened) and set the template folder to _templates
2. Create vault/<project>/<kind>/<slug>.md from _templates/content-md.md; fill id cmd_<YYYYMMDD>_<slug>, kind, title, status (seed) and created/updated
3. Write ## Overview (2-4 sentences) and ## Next Steps (checkboxes) first, then Timeline, Method, Decisions in Force, Open Questions, Contradictions and Links in that order
4. In later sessions: append a dated '### YYYY-MM-DD · <skill>' Timeline entry (never edit or fabricate past ones), rewrite Next Steps in full, move answered Open Questions to Decisions in Force, bump updated
5. Re-run tools/vault_manifest.py and tools/vault_rag.py index so the hub and RAG see the change

### Connect Obsidian to Ollama (connection A)

1. Windows: setx OLLAMA_ORIGINS "app://obsidian.md" (macOS/Linux: export OLLAMA_ORIGINS="app://obsidian.md"); fully quit and reopen Ollama
2. Obsidian -> Open folder as vault (Creative-Headquarters/vault/ and/or Creative-Writing/)
3. Settings -> Community plugins -> Browse -> install one of Copilot, Smart Connections or Text Generator
4. Set Provider = Ollama (or custom/OpenAI-compatible), Base URL http://localhost:11434, Model llama3.1:8b (whatever `ollama list` shows), API key blank or a placeholder
5. If the plugin reports 'failed to fetch' while curl works: revisit OLLAMA_ORIGINS and restart Ollama fully; for the hub Ask tab, the hub's own origin must also be allowed

### Creative-Writing migration (planned, not implemented)

1. The author decides the kind vocabulary (recommended: extend SCHEMA with poem/story/novel/essay/concept/journal plus a DECISIONS entry)
2. The author decides project groupings, created dates, status per work, granularity and the Next Steps policy (omit for complete works)
3. Mechanically generate id/type/title/updated/tags and the section skeleton for 63 works
4. Per-file human pass: kind, status, project, context_brand, Overview, Links, and next steps for seeds
5. One honest Timeline entry per work: the migration itself, with source volume and line range
6. No script exists for any of these steps; GAP-ANALYSIS states no files have been migrated, and the Creative-Writing source directory is not present on this machine now

## Relationships

| From | Relation | To |
|---|---|---|
| vault_rag.py | implements (executable form). It deviates on purpose: a JSON index instead of FAISS, and similarity-order 're… | skills/local_rag_orchestration.skill.md |
| skills/local_rag_orchestration.skill.md | P5 preflight runs `vault_rag.py status` and greps for 'index +N chunks' and 'changed since' | vault_rag.py |
| vault_rag.py | docstring: the local equivalent of the archive's graph_store.py/vector_store.py that D1 calls for | DECISIONS.md D1 |
| vault_rag.py | reads hardware.local_llm.endpoint, embed_model and tiers.*.model; writes context_used_pct and loaded_tier wit… | dashboard.json |
| vault_rag.py | calls /api/tags, /api/embeddings and /api/generate (including keep_alive 0 eviction) | Ollama HTTP API (localhost:11434) |
| vault_rag.py | writes (index) / reads (ask, status) | state/rag_index/index.json |
| vault_rag.py | writes archived <think> traces from ask | state/rag_traces/ |
| vault_rag.py | suggested fix in the require_model error text ('--write') | tools/reconcile_models.py |
| vault_rag.py | referenced in the endpoint-unreachable error text (OLLAMA_HOST=0.0.0.0 and the 11434 inbound rule for WSL2) | BOOT.md section 2 |
| vault_rag.py | default --vault target for index; read-only | Obsidian vault (vault/) |
| vault_rag.py | the current index.json was built from this sibling vault via --vault; the directory no longer exists | Creative-Writing (C:\Users\utopi\Creative-Writing, now absent) |
| vault_manifest.py | writes | state/vault_manifest.json |
| vault_manifest.py | shares the vault_files exclusion rule ('keep the two in sync'); the manifest also excludes 00_INDEX.md | vault_rag.py |
| vault_manifest.py | parses frontmatter fields id/title/kind/project/status/created/updated/tags and extracts the ## Overview and… | Content MD schema |
| vault_manifest.py | the current manifest (64 notes, 413,578 bytes) was built from this sibling vault via --vault; that is why the… | Creative-Writing (C:\Users\utopi\Creative-Writing, now absent) |
| hub/app.js | fetch('../state/vault_manifest.json') for the Library tab; the Ask tab chunks and embeds manifest bodies into… | state/vault_manifest.json |
| hub/ollama.js | mirrors the chunk constants (800/120), tier limits, nomic-embed-text, the QUERY prompt text and the retrieval… | vault_rag.py |
| tools/launcher/Start-Hub.ps1 | serves the repo root over 127.0.0.1 http.server (default port 8765) so the hub's fetch() of the manifest works | state/vault_manifest.json |
| tools/verify_system.py | counts vault notes (excluding '_' path parts and README.md/SCHEMA.md) for the L3-consistency gate check | Obsidian vault (vault/) |
| CI: vault_rag smoke and core-logic test | imports it and tests chunk, pack/unpack, normalize, dot and strip_frontmatter, plus --help under -W error::En… | vault_rag.py |
| Content MD Obsidian template | implements the frontmatter and section order | Content MD schema |
| Worked example Content MD (dry stipple brush) | example instance | Content MD schema |
| Worked example Content MD (dry stipple brush) | its Method reproduces from brush-designer defaults | tools/brush-designer/ |
| Creative-Writing -> Vault migration (GAP-ANALYSIS) | assesses the Creative-Writing corpus against the required fields and sections; proposes a kind-vocabulary ame… | Content MD schema |
| Creative-Writing -> Vault migration (GAP-ANALYSIS) | finds that migration serves 2 of 10 gates and unblocks 0 of 8 skill routes (stale: dashboard now DEGRADED wit… | Router.md / dashboard.json brand gates |
| Obsidian -> Ollama plugin connection (connection A) | OBSIDIAN.md pairs them: A (plugin, sees the open note) for writing; B (vault_rag.py, the whole vault) for rem… | vault_rag.py |
| Obsidian -> Ollama plugin connection (connection A) | same OLLAMA_ORIGINS requirement; the hub needs its own origin allowed too (README.md), served by Start-Hub.ps… | hub Ask tab |
| Repo-root Obsidian vault state (.obsidian/ and stray note) | the Obsidian vault root is Creative-Headquarters/, so vault/ is a subfolder inside it; this makes the Datavie… | Obsidian vault (vault/) |
| vault/studio-os/ui/ui-ux-intelligence-integration.md | its existence satisfies the L3-consistency check that DEGRADED state needs at least one vault note while gate… | tools/verify_system.py |
| archive/ | claimed by vault/README.md and README.md ('the archive indexes these files'), but no code under archive/ refe… | Obsidian vault (vault/) |

**Open questions the files could not settle**

- Where did C:\Users\utopi\Creative-Writing go? It is absent now, yet both state files point at it. Was it moved, renamed or deleted, and should the index and manifest be rebuilt from vault/ or from Creative-Writing's new location?
- Has `vault_rag.py ask` ever run? Nothing on disk shows it: there is no state/rag_traces/, and dashboard.json has context_used_pct 0 and loaded_tier null. Because llama3.1:8b would not emit <think>, this is inconclusive.
- Are the dashboard tier tags (llama3.1:8b, mistral-nemo:12b) actually installed? They are marked PROVISIONAL. Only nomic-embed-text is shown to work, because the index was built with it.
- Is the repo root meant to be the Obsidian vault? That is where .obsidian/ is on disk, and it makes Dataview FROM "vault" work. Or should vault/ itself be the vault, as vault/README.md and OBSIDIAN.md instruct? If the root stays the vault, the vault/-scoped .gitignore rules leave .obsidian/workspace.json, graph.json, plugins/*/data.json and any root .smart-env/ unignored. Whether they are tracked was not checked (.git/ not read).
- Which Obsidian community plugin, if any, is in use, and is OLLAMA_ORIGINS set? OBSIDIAN.md lists three and picks none. A top-level listing of the root .obsidian/ shows no plugins/ folder; environment variables cannot be read from files.
- What exact origin must be added to OLLAMA_ORIGINS for the hub Ask tab? README.md says 'one more origin'. Start-Hub.ps1 serves http://localhost:8765 by default (scanning up to +9 ports), but no document names the value.
- Is the hub meant to show vault/ Content MDs (as README.md says) or the Creative-Writing archive (what state/vault_manifest.json currently contains)? The same question applies to the RAG index.
- What created the 0-byte wet-stipple-brush.md at the repo root (2026-09-17)? Its name matches an unresolved wikilink in the example note.
- The author's kind-vocabulary decision (GAP-ANALYSIS section 4) is unresolved; SCHEMA.md still lists the original 10 kinds.
- verify_system.py uses a slightly different exclusion rule than the two indexers: it checks '_' on every path part including the filename, and does not check '.' dirs. Is the divergence intentional?
- vault/README.md and README.md say 'the archive indexes these files', but archive/ has no vault-reading code. Is an archive-side ingest still planned, or is vault_rag.py its replacement (DECISIONS.md D1)?
- The CI workflow's run history and pass/fail state were not inspected.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: state/vault_manifest.json: created/updated = 2026-08-31 (file mtime)
  - evidence: state/vault_manifest.json: only the first note (01_Books/01_The_First_Friend.md, line 15) has updated 2026-08-31. The other 63 entries, OBSIDIAN.md included (lines 31..1023), have 2026-08-30. A Grep count for '"updated": "2026-08-31"' returns 1.
- **added**: The state files were built from C:\Users\utopi\Creative-Writing (implied still present; flows show re-running index --vault ../Creative-Writing)
  - evidence: PowerShell Test-Path 'C:\Users\utopi\Creative-Writing' returns False, and no *Creative* directory other than Creative-Headquarters exists under C:\Users\utopi. Both state files are orphaned. vault_rag.py cmd_status (lines 527-537) would print 'vault path no longer exists'. index/manifest runs with --vault ../Creative-Writing would exit 1 'no vault at ...' (vault_rag.py lines 276-278, vault_manifest.py lines 185-187).
- **added**: Obsidian vault entry point: open Creative-Headquarters/vault/ as the vault; open question about Dataview FROM "vault"
  - evidence: `ls -a vault/` shows no .obsidian/; `ls -a` at the repo root shows .obsidian/. The folder actually opened in Obsidian is the repo root, which is what the Dataview FROM "vault" in vault/README.md line 44 assumes, but not what README step 1 and OBSIDIAN.md A1 say.
- **corrected**: Git hygiene: .obsidian/plugins/*/data.json, workspace.json, cache, .trash/, .smart-env/ are gitignored in this repo
  - evidence: .gitignore lines 31-42 scope these to vault/ (vault/.obsidian/plugins/*/data.json, vault/.obsidian/workspace.json, workspace-mobile.json, cache, graph.json, vault/.trash/, vault/.smart-env/, vault/.smart-connections/). Only *.faiss, *.embeddings.json, .env/.env.* and state/ are unscoped. The real .obsidian/ at the repo root is not matched by these patterns.
- **corrected**: index.json is gitignored per .gitignore line 39
  - evidence: .gitignore line 17 is 'state/', which does the ignoring; line 39 is only a comment ('state/ already covers state/rag_index/ and state/rag_traces/').
- **added**: Content of the repo root relevant to the vault (not in inventory)
  - evidence: The repo root holds wet-stipple-brush.md, a 0-byte file (mtime Sep 17 15:36) whose name matches the unresolved wikilink [[wet-stipple-brush]] in vault/_examples/example-stipple-brush.md lines 33 and 94.
- **corrected**: index.json chunk schema: file (vault-relative)
  - evidence: vault_rag.py line 305 uses str(f.relative_to(vault)) with no separator normalization. The index stores backslash paths such as '01_Books\\01_The_First_Friend.md', while vault_manifest.py line 133 converts to forward slashes. All 173 chunks have kind '' (grep count).
- **corrected**: window ceiling: prints a warning when context_used_pct >= 60
  - evidence: vault_rag.py lines 471-487: the >= 60 warning is inside the else branch of `if args.json`, so --json output never includes it.
- **corrected**: Post-processing strips <think>...</think> and a leading 'ANSWER:'
  - evidence: vault_rag.py line 462: re.sub(r'^ANSWER:\s*', '', answer, flags=re.M) replaces every line-initial 'ANSWER:', not only a leading one.
- **corrected**: EMBEDDING: 120 s timeout
  - evidence: vault_rag.py line 326: 120 s applies to index embeddings. Line 408: the ask question embedding uses timeout=60.
- **added**: --endpoint override: nothing extra
  - evidence: vault_rag.py resolve_endpoint line 119 reads and parses dashboard.json before applying the override, so dashboard.json must exist and parse for every subcommand, even with --endpoint.
- **corrected**: index: evicts the embed model at the end
  - evidence: vault_rag.py lines 328-335: the embedding-failure path saves a partial index and returns 1 without calling evict. Eviction (line 360) happens only on success.
- **added**: skills/local_rag_orchestration.skill.md P5 preflight greps status for index freshness
  - evidence: skill lines 102-106 grep 'index +[0-9]+ chunks' and 'changed since'. With the current orphaned index, status prints 'vault path no longer exists' and no 'changed since' line (vault_rag.py lines 527-537), so P5 would print OK:P5.
- **corrected**: hub/ollama.js mirrors vault_rag.py's constants and QUERY prompt
  - evidence: hub/ollama.js does mirror the chunk sizes, tier limits, the prompt text and the retrieval logic. Defaults differ: hub/index.html lines 118-120 set top-k 12 and max words 220 (CLI: 8 and 250); hub/app.js line 298 uses chunk ids 'c_<path>_<i>' (CLI: c_NNNN); the hub index lives in localStorage 'hub:index:v1' (app.js line 312) and never reads state/rag_index/index.json.
- **added**: vault/README.md / README.md: 'the archive indexes these files for search and the graph view'
  - evidence: A Grep for vault|content-md|SCHEMA.md under archive/ finds no matches. vault_rag.py's docstring (lines 5-7) calls itself 'the local implementation the archive has been missing (DECISIONS.md D1)'. The only implemented vault readers are vault_rag.py and vault_manifest.py.
- **added**: GAP-ANALYSIS headline (0 of 8 routes; system BLOCKED; all 10 gates unauthored; vault empty)
  - evidence: GAP-ANALYSIS.md section 6 states this, but dashboard.json line 10 shows state DEGRADED and lines 237/247/256 show three gates with authored: true. vault/studio-os/ui/ui-ux-intelligence-integration.md calls ui_ux_intelligence 'the ninth routed skill'. The document is stale relative to the current state.
- **added**: Worked example: whether the referenced artifacts exist was not checked
  - evidence: `ls -a` at the repo root shows no assets/ directory, so assets/brushes/dry-stipple-v3.brush and dry-stipple-v1.brush do not exist. tools/brush-designer/ does exist.
- **corrected**: CI: vault_manifest.py has no CI coverage 'in the lines read'
  - evidence: A Grep of the whole repo for vault_manifest finds no hit in .github/workflows/verify.yml, so there is definitively no CI coverage. verify.yml runs on ubuntu-latest with Python 3.11, triggered by push to main, pull_request and workflow_dispatch (lines 9-23).
- **corrected**: Connection A entry points 'ollama list && curl ...' and 'ollama pull llama3.1:8b && ollama pull nomic-embed-text'
  - evidence: OBSIDIAN.md lines 22-36 list these as separate one-line commands, not &&-chained. Split into individual entry points.
- **corrected**: vault_manifest Content MD detection: title and kind come from frontmatter
  - evidence: vault_manifest.py line 73 regex '^(\w[\w_]*):\s*(.*)$' accepts empty values, so a template-style 'kind: ' produces kind '' (meta.get('kind','other') returns ''), not 'other'. vault_rag.py line 225 uses '(.+?)', which drops empty values.
- **corrected**: Creative-Writing root OBSIDIAN.md: contents and relation not verified (open question)
  - evidence: state/vault_manifest.json lines 1015-1029: title 'This repo is an Obsidian vault'; the body describes Creative-Writing as an Obsidian vault of 63 works; the overview is 'Ollama runs the model on this laptop. Two ways to use it here...'. It is Creative-Writing's own guide, distinct from this repo's OBSIDIAN.md ('Connecting Obsidian to Ollama').
- **corrected**: All vault_rag.py subcommands/flags (status, index --vault --embed-model, ask question --tier --model --top-k --rerank-to --max-words --json --write-dashboard, evict, global --endpoint)
  - evidence: Confirmed against tools/vault_rag.py main() lines 551-584; no other subcommands or flags exist. Exit codes 0/1/2 confirmed in the docstring line 29 and in code.
- **corrected**: Index header values, 173 chunks, 65 files, 768 dims, 1,183,899 bytes; manifest count 64, 413,578 bytes
  - evidence: Confirmed as stated: head/tail of state/rag_index/index.json, grep counts (173 ids, last c_0172, 65 unique files) and ls -la sizes. No change needed; recorded as verified.
