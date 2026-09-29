# Hub and launcher

Subsystem `hub-launcher` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 11 entries · 24 corrections made to the first reading.

## Summary

THE HUB (hub/index.html, title 'THE HUB — Studio Headless OS') is a static browser app with no build step and five tabs: Library, Ask, Designer Pro, Brushes and Pipeline. It needs an HTTP origin because it fetch()es '../dashboard.json', '../state/vault_manifest.json' and '../tools/ui-ux-pro-max/data/<file>.csv'.

It calls a local Ollama server directly (default http://localhost:11434) through hub/ollama.js (HubOllama), using:
- GET /api/tags (6 s timeout)
- POST /api/embeddings {model, prompt, keep_alive:'5m'}
- POST /api/generate {stream:false, keep_alive:'5m', options}
- POST /api/generate {model, keep_alive:0} to evict a model

The hub's only persisted state is browser localStorage: hub:tab, hub:endpoint, hub:tier, hub:overview:<content_hash> and hub:index:v1. It writes no files and starts no routed tasks.

Tabs:
- **Library** renders cards from the manifest. It writes an AI overview only when the user clicks.
- **Ask** is RAG done in the browser: chunk, embed, cosine top-k, fit to a budget, generate with chunk citations. It mirrors the constants in tools/vault_rag.py.
- **Designer Pro** does CSV search and conflict checks without a model. Its optional Ollama 'blend' always uses the sm tier. It fetches styles.csv at page load, whichever tab is showing.
- **Brushes** only shows tools/brush-designer/index.html in an iframe.
- **Pipeline** is a hard-coded preview of five stations. It does not fetch, poll or act. The live rail is control_room.html + router.js, which polls dashboard.json every 5000 ms. Nothing writes dashboard.json.pipeline. tools/verify_system.py (run in CI) sets the constraints any writer of that block must meet.

Launchers:
- **tools/launcher/Start-Hub.ps1** serves the whole repo root. It probes 127.0.0.1:8765-8774 by default, reuses a running hub (found by 'Studio Headless OS' in /hub/index.html), and otherwise spawns `python.exe -m http.server <port> --bind 127.0.0.1 --directory <root>`. Params: -Port, -PortSearch, -Stop, -NoBrowser.
- **tools/launcher/Install-Shortcut.ps1** writes tools/launcher/hub.ico and 'Studio Hub.lnk' to the Desktop folder and to Start Menu\Programs. Only the Programs copy gets the CTRL+ALT+H hotkey. Params: -Name, -Hotkey, -NoHotkey. Both .lnk files exist on this machine: C:/Users/utopi/OneDrive/Desktop and %APPDATA%/Microsoft/Windows/Start Menu/Programs.

Port disagreement:
- Start-Hub.ps1 and tools/launcher/README.md use 8765 (range 8765-8774).
- .claude/launch.json and the root README.md use 8347.
- The file:// note in hub/index.html says http://localhost:8000/hub/.

These are three separate browser origins, each with its own localStorage.

## Tools

### THE HUB (hub web app)

`web-app` · status `runs-today`

Paths: `hub/index.html`, `hub/app.js`, `hub/ollama.js`, `hub/designer-pro.js`, `hub/styles.css`

Static browser front-end over the studio repo: five tabs (Library, Ask, Designer Pro, Brushes, Pipeline), plus a header chip and a <dialog> for the local Ollama connection.

**Entry points**

- `http://localhost:<port>/hub/ (Start-Hub.ps1 default: http://localhost:8765/hub/)`
  - does: URL opened by tools/launcher/Start-Hub.ps1: the first port in 8765..(8765+PortSearch-1) that already serves the hub, otherwise the first free port.
  - changes: browser localStorage only
- `http://localhost:8347/hub/`
  - does: Where the hub is reachable when served by the .claude/launch.json 'hub-static-server' config (python3 -m http.server 8347).
  - changes: browser localStorage only
- `python3 -m http.server (from repo root), then http://localhost:8000/hub/`
  - does: Manual serve instruction shown in #offlineNote. The note is displayed only when location.protocol is 'file:'.
  - changes: nothing
- `Header chip #settingsBtn -> <dialog id=settingsDialog>`
  - does: Fills #endpointInput from HubOllama.getEndpoint() and #tierSelect from hub:tier (default 'sm'), then calls showModal(). - #endpointInput change: setEndpoint(trimmed value, or DEFAULT_ENDPOINT if empty), then refreshConnDot(). - #testConnBtn: GET {endpoint}/api/tags. Prints 'reachable — <models>', 'reachable — no models pulled' or 'unreachable — <err>', then refreshConnDot(). - #tierSelect change: writes hub:tier. It does not refresh the chip. - #evictBtn: HubOllama.evict for the current tier model and the embed model, then shows 'evicted'. There is no /api/tags check first.
  - changes: localStorage hub:endpoint and hub:tier; unloads models from Ollama memory (evict)

**Inputs**

- dashboard.json -> hardware.local_llm.{endpoint, tiers.sm.model, tiers.sm.context_window_tokens, tiers.md.model, tiers.md.context_window_tokens, embed_model}. Optional overrides, read once at boot in app.js.
- localStorage hub:tab, hub:endpoint, hub:tier
- user clicks and typed text

**Outputs**

- Rendered UI
- Connection chip text. Initial 'Ollama —', then 'Ollama — <tier model>', 'Ollama — <tier model> not pulled' or 'Ollama — unreachable'. The dot gets class 'on' or 'off'.

**Reads**

- ../dashboard.json (app.js boot; designer-pro.js resolveTier() fetches it a second time)
- ../state/vault_manifest.json (Library and Ask)
- ../tools/ui-ux-pro-max/data/{styles,colors,typography,ux-guidelines,charts,landing,products,icons,motion}.csv (Designer Pro)
- ../tools/brush-designer/index.html (Brushes iframe and link)
- styles.css, ollama.js, app.js, designer-pro.js (same directory)
- https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;800&display=swap (preconnect also to fonts.gstatic.com)
- localStorage hub:tab, hub:endpoint, hub:tier, hub:overview:<content_hash>, hub:index:v1

**Writes**

- browser localStorage: hub:tab, hub:endpoint, hub:tier, hub:overview:<content_hash>, hub:index:v1

**Depends on**

- A static HTTP server rooted at the repo root (Start-Hub.ps1, .claude/launch.json, or a manual python http.server)
- Ollama REST server, default http://localhost:11434
- Google Fonts CDN (fonts.googleapis.com, fonts.gstatic.com) for JetBrains Mono
- Browser APIs: dialog.showModal, AbortSignal.timeout, AbortController, localStorage, fetch

**Environment and secret names (names only)**

- OLLAMA_ORIGINS. Set on the Ollama side, not read by the hub. The settings hint says 'setx OLLAMA_ORIGINS needs this origin added, then a full restart of Ollama' and links ../OBSIDIAN.md § A2.

**Gates and checkpoints**

- file:// check: if location.protocol is 'file:', body gets class 'offline' and #offlineNote is shown. The fetches then fail.
- Model check: before generate/embed calls, Library, Ask and Designer Pro call GET /api/tags and HubOllama.familyMatches(model, served). They throw if the family is missing.
  - Only the text before ':' is compared, so any tag of the same family passes.
  - The settings Evict button does not check.
- The md tier option label 'md — mistral-nemo:12b (AC + quiet desktop only)' is text only. No power, thermal or compute-gate check exists in hub code. dashboard.json says every workload class except llm_local_sm requires AC.
- Endpoint precedence: dashboard.json endpoint is applied only when localStorage hub:endpoint is unset. It is then persisted with setEndpoint, so later edits to dashboard.json's endpoint are ignored for that origin.

**Invoked by**

- tools/launcher/Start-Hub.ps1 (Start-Process <url>)
- Studio Hub.lnk shortcuts (run Start-Hub.ps1)
- .claude/launch.json hub-static-server (serves the origin; does not open the hub itself)
- user opening the URL manually

**Invokes**

- HubOllama (hub/ollama.js)
- Library tab
- Ask tab
- Designer Pro tab
- Brushes tab
- Pipeline tab
- Ollama GET /api/tags, POST /api/embeddings, POST /api/generate

**Notes**

LOAD ORDER
- Scripts load in this order: ollama.js, app.js, designer-pro.js.
- app.js runs synchronously at load, in this order:
  1. file:// check
  2. fire the dashboard.json fetch (async; refreshConnDot runs again in its finally)
  3. showTab(localStorage hub:tab || 'library')
  4. wire the dialog
  5. refreshConnDot()
  6. render the Pipeline preview
- The last tab is therefore restored before the dashboard overrides arrive, and /api/tags is called twice at boot.
- designer-pro.js mounts on DOMContentLoaded whatever tab is active. It immediately fetches ../tools/ui-ux-pro-max/data/styles.csv.

TABS
- data-tab ids: library, ask, designer, brushes, pipeline.
- Views: #view-library, #view-ask, #view-designer, #view-brushes, #view-pipeline.

TIERS AND MODELS
- app.js takes only model and num_ctx (from context_window_tokens) per tier from dashboard.json. payload_tokens and num_predict always come from HubOllama.DEFAULT_TIERS.
- The tier <select> labels hard-code llama3.1:8b and mistral-nemo:12b.

DOC DISCREPANCIES
- ollama.js's header says 'Nothing leaves the machine', but index.html loads Google Fonts from an external CDN.
- The root README.md says 'Four tabs:' and then lists five bullets. index.html has five tabs.

STYLES
- styles.css is the token file:
  - HARD MONO palette: --bg #000000, --bg-raise #0B0B0B, --bg-panel #141414, --line #383838, --ink #FFFFFF, --ink-dim #9E9E9E, --amber #FFC400, --cyan #00E5FF, --alert #FF3B30, --queued #8A8AFF
  - all radii 0, JetBrains Mono
- Its header says it consumes the same token dictionary as control_room.html (skills/css_html_ui.skill.md ARTIFACT A, HARD MONO 2026-09-01).

EVIDENCE AND CI
- DECISIONS.md records it 'Rendered at 375 / 1000 / 1440px on all five Hub tabs'.
- CI (.github/workflows/verify.yml) does not check hub/*.js; it runs node --check only on router.js.
- Per vault/studio-os/ui/ui-ux-intelligence-integration.md, check_palette_parity reads only control_room.html, not hub/styles.css.

### HubOllama (hub/ollama.js)

`library` · status `runs-today`

Paths: `hub/ollama.js`

Ollama client and RAG helpers that run in the browser, shared by the hub tabs. It mirrors tools/vault_rag.py's constants, tier limits and 'answer only from the retrieval block' prompt.

**Entry points**

- `HubOllama.fetchTags(endpoint) -> GET {endpoint}/api/tags (AbortSignal.timeout(6000))`
  - does: Returns data.models[].name. Throws 'HTTP <status>' when the response is not ok.
  - changes: nothing
- `HubOllama.embed(endpoint, model, prompt) -> POST {endpoint}/api/embeddings {model, prompt, keep_alive:'5m'}`
  - does: Returns data.embedding. Throws 'embeddings HTTP <status>'. No timeout.
  - changes: loads the embed model into Ollama memory for 5m
- `HubOllama.generate(endpoint, {model, prompt, options, signal}) -> POST {endpoint}/api/generate {model, prompt, stream:false, keep_alive:'5m', options}`
  - does: Returns data.response or ''. The optional AbortSignal allows cancelling. No timeout.
  - changes: loads the model into Ollama memory for 5m
- `HubOllama.evict(endpoint, model) -> POST {endpoint}/api/generate {model, keep_alive:0}`
  - does: Best-effort unload. Errors are swallowed.
  - changes: unloads the model from Ollama memory
- `HubOllama.getEndpoint() / setEndpoint(v)`
  - does: Reads or writes localStorage 'hub:endpoint'. Defaults to DEFAULT_ENDPOINT 'http://localhost:11434'.
  - changes: localStorage hub:endpoint (setEndpoint)
- `HubOllama.familyMatches / stripThink / stripFrontmatter / chunkText / normalize / dot / retrieve / buildPrompt`
  - does: Pure helpers. No network, no model.
  - changes: nothing

**Inputs**

- endpoint URL
- model tag
- prompt text
- note bodies (chunkText)
- query vector and chunk list (retrieve)

**Outputs**

- served model names
- embedding vectors
- generated text
- ranked chunks [{score, c}]
- assembled RAG prompt

**Reads**

- localStorage hub:endpoint

**Writes**

- localStorage hub:endpoint (via setEndpoint)

**Depends on**

- Ollama REST API at the configured endpoint

**Gates and checkpoints**

- familyMatches(tag, served) compares only the family prefix before ':'.
- retrieve(): scores all chunks by dot product and keeps topK (default 12). It then adds chunks greedily, up to rerankTo (default 4), while each fits the remaining budget of payloadTokens*4 chars. If none fits, it falls back to the single best chunk truncated to payloadTokens*4 chars.

**Invoked by**

- app.js (settings dialog, Library tab, Ask tab)
- designer-pro.js (Designer Pro tab)

**Invokes**

- Ollama GET /api/tags
- Ollama POST /api/embeddings
- Ollama POST /api/generate

**Notes**

CONSTANTS
- CHARS_PER_TOKEN=4, CHUNK_TOKENS=800 (3200 chars), OVERLAP_TOKENS=120 (480 chars).
- These match tools/vault_rag.py lines 64-66.

DEFAULT_TIERS
- sm = {model 'llama3.1:8b', num_ctx 8192, payload_tokens 3000, num_predict 800}
- md = {model 'mistral-nemo:12b', num_ctx 4096, payload_tokens 1200, num_predict 600}
- The limits match vault_rag.py TIER_LIMITS.
- DEFAULT_EMBED_MODEL is 'nomic-embed-text'.

PROMPT
- QUERY_TEMPLATE says:
  - use ONLY the retrieval block
  - say so plainly if the answer is not there
  - cite chunk ids like [c_0412]
  - answer in at most N words
  - put the final answer after 'ANSWER:'
- stripThink() removes every <think>…</think>. It then removes the first 'ANSWER:' found at the start of a line (regex /^ANSWER:\s*/m, not global) and trims. Text before that line is kept.

CHUNKING
- chunkText packs paragraphs (split on blank lines) up to 3200 chars and carries the last 480 chars into the next chunk.
- While the current chunk is over 4800 chars, it hard-splits off 3200 chars.

FRONTMATTER
- stripFrontmatter is exported but never called in hub code.
- It does not need to be: tools/vault_manifest.py parse_frontmatter() already splits frontmatter off, and note.body holds only body.strip().

DEFAULTS VS vault_rag.py
- The retrieve() comment says the logic is identical to vault_rag.py cmd_ask.
- Defaults differ. The hub Ask UI uses top-k 12, rerank-to 4, max-words 220. vault_rag.py ask uses --top-k 8, --rerank-to 4, --max-words 250.

EMBEDDINGS ROUTE
- Uses the /api/embeddings route with field 'prompt' and reads 'embedding', the same route vault_rag.py uses.

### Library tab

`web-app` · status `runs-today`

Paths: `hub/index.html`, `hub/app.js`

One card per note in the last-indexed vault, built from state/vault_manifest.json. Each card shows the authored overview, plus an AI overview the local model writes only when the user clicks.

**Entry points**

- `Tab button data-tab="library" (default tab; view #view-library)`
  - does: showTab('library') calls loadManifest() if manifestNotes is empty. loadManifest() is fetch('../state/vault_manifest.json').
  - changes: localStorage hub:tab
- `#libraryRefresh 'Refresh manifest'`
  - does: Re-fetches ../state/vault_manifest.json, rebuilds the kind and status filters and re-renders.
  - changes: nothing
- `#librarySearch (input) / #libraryKind / #libraryStatus / #librarySort (change)`
  - does: Filtering and sorting in the browser. - Search: lowercase substring over title + project + tags. - Kind and status options: distinct manifest values, sorted. - Sort: 'updated' (descending string compare) or 'title' (localeCompare).
  - changes: nothing
- `Card button .ai-overview-btn ('Generate AI overview' / 'Regenerate AI overview')`
  - does: 1. Resolves the tier model from hub:tier (default sm). 2. GET /api/tags family check. 3. POST /api/generate with prompt 'Summarize this note for a library card. Two to three sentences, plain language, no preamble, no restating the title. Note titled "<title>":' followed by note.body.slice(0,6000). options are {temperature:0.4, num_predict:200}. No num_ctx is passed, so the tier's num_ctx is not applied. No evict.
  - changes: localStorage hub:overview:<content_hash> = JSON {text, model}; the model stays resident in Ollama for 5m
- `python3 tools/vault_manifest.py --vault <path>`
  - does: Command shown in the tab hint and error text to regenerate the manifest. The hub does not run it.
  - changes: writes state/vault_manifest.json (vault_manifest.py --out default: <repo>/state/vault_manifest.json; --vault default: <repo>/vault)

**Inputs**

- state/vault_manifest.json: top level {vault, built, count, notes[]}. Each note is {path, id, title, kind, status, project, tags[], created, updated, body (frontmatter already stripped), overview, next_steps_open, content_hash (sha256 of raw file, first 16 hex), word_count}.
- localStorage hub:tier and hub:endpoint (model and endpoint for the AI overview)

**Outputs**

- Card grid (#libraryGrid). Each card shows title, kind pill, status pill, 'updated <date>', '<n> open step(s)', 'Overview (authored)', a cached AI overview with model name, and #tags.
- #libraryVaultName: the last path segment of manifest.vault
- #libraryEmpty messages: load error with the vault_manifest.py instruction, 'No notes match this filter.', or empty-vault text

**Reads**

- ../state/vault_manifest.json
- localStorage hub:overview:<content_hash>, hub:tier, hub:endpoint

**Writes**

- localStorage hub:overview:<content_hash>

**Depends on**

- tools/vault_manifest.py (produces the manifest)
- Ollama tier model (AI overview only)

**Gates and checkpoints**

- The AI overview runs only when the user clicks.
- The tier model family must appear in /api/tags. Otherwise it throws "'<model>' is not served — installed: …" and the card shows 'Generation failed: …'.
- If the manifest is missing or invalid, the tab tells the user to run tools/vault_manifest.py --vault <path> and then Refresh.

**Invoked by**

- THE HUB tab strip
- Ask tab (the Build index button calls loadManifest when manifestNotes is empty)

**Invokes**

- HubOllama.getEndpoint, fetchTags, familyMatches, generate, stripThink

**Notes**

WHAT NEEDS A MODEL
- No model is needed for the card list, filters, sort, authored overview, pills or tags.
- A model is needed only for the AI overview.

CACHING
- The AI overview is cached by content_hash. content_hash covers the raw file including frontmatter, so any edit orphans the cached overview.

WHICH VAULT
- state/vault_manifest.json currently records:
  - vault 'C:\Users\utopi\Creative-Writing'
  - count 64
  - built '2026-09-01T04:30:49.101105+00:00'
- That vault is outside this repo. The root README.md says the Library shows 'one card per Content MD in vault/', and vault_manifest.py's default --vault is <repo>/vault.
- vault_manifest.py handles both Content MDs (frontmatter) and plain-markdown archives. For plain markdown: title from H1, kind from the top-level folder, dates from mtime.

### Ask tab

`web-app` · status `runs-today`

Paths: `hub/index.html`, `hub/app.js`, `hub/ollama.js`

Retrieval-augmented Q&A over the manifest's notes, run in the browser. It keeps an embedding index in localStorage, retrieves chunks by cosine similarity, and has the tier model answer only from those chunks with chunk-id citations.

**Entry points**

- `Tab button data-tab="ask" (view #view-ask)`
  - does: initAsk() runs once. It loads localStorage hub:index:v1 if saved.embedModel equals the current embedModel, then shows Status, Chunks and Notes.
  - changes: localStorage hub:tab
- `#buildIndexBtn 'Build / refresh index'`
  - does: 1. Loads the manifest if it is empty. Alerts if there are no notes. 2. GET /api/tags and checks the embed model family. Alerts 'Cannot build index' if it is not served. 3. Drops cached chunks whose hash is no longer in the manifest. 4. For each note whose content_hash is not yet indexed: chunkText(note.body), then one POST /api/embeddings per chunk. Each vector is normalized and gets id 'c_<path>_<i>'. A progress bar shows notes done. 5. HubOllama.evict(embed model).
  - changes: localStorage hub:index:v1 = {embedModel, chunks:[{id,file,title,hash,text,vec}]}. If the quota is exceeded it is kept in memory only, with a console.warn. The embed model is loaded and then unloaded in Ollama.
- `#askForm submit (textarea #askInput, button #askSubmit)`
  - does: 1. Alerts if no index exists. 2. GET /api/tags and checks both the embed and tier model families. 3. Embeds the question (POST /api/embeddings) and normalizes it. 4. retrieve(qvec, chunks, {topK, rerankTo, payloadTokens: tier.payload_tokens}), then buildPrompt(question, kept, maxWords). 5. POST /api/generate with options {temperature:0.6, top_p:0.95, num_ctx: tier.num_ctx, num_predict: tier.num_predict}. 6. evict(tier model) and stripThink. 7. Renders the answer and one source row per chunk: '[id] title — file · score 0.000'.
  - changes: Ollama: the tier model is loaded and then evicted. The embed model stays resident 5m (it is not evicted after the question). Chat log DOM only.
- `Advanced: #optTopK (default 12, HTML min 1 max 50), #optRerankTo (default 4, 1-12), #optMaxWords (default 220, 40-800)`
  - does: Retrieval and answer-length knobs. JS does not clamp them; it uses Number(value) || default.
  - changes: nothing

**Inputs**

- state/vault_manifest.json notes[].{path, title, content_hash, body}
- question text
- tier from hub:tier (sm or md)
- embed model: dashboard.json hardware.local_llm.embed_model, else 'nomic-embed-text'

**Outputs**

- Answer text with [chunk-id] citations
- Sources list with cosine scores
- Index stats: Status built/not built, Chunks, Notes covered

**Reads**

- ../state/vault_manifest.json (via the shared loadManifest)
- localStorage hub:index:v1, hub:tier, hub:endpoint

**Writes**

- localStorage hub:index:v1

**Depends on**

- Ollama embed model (default nomic-embed-text)
- Ollama tier model (default sm llama3.1:8b; md mistral-nemo:12b)

**Gates and checkpoints**

- Asking is blocked with an alert until an index exists.
- Building is blocked with an alert if the manifest has no notes.
- Both model families must be served, or the call throws. Errors show as 'Could not answer: <msg>'.
- The prompt tells the model to use ONLY the retrieval block and to say so plainly when the answer is not there.
- A cached index is discarded if its embedModel differs from the current one.

**Invoked by**

- THE HUB tab strip

**Invokes**

- Library tab loadManifest (shared manifestNotes)
- HubOllama.getEndpoint, fetchTags, familyMatches, chunkText, embed, normalize, retrieve, buildPrompt, generate, evict, stripThink

**Notes**

WHAT NEEDS A MODEL
- No model is needed for chunking, normalization, cosine scoring, the budget fill or prompt assembly.
- Models are needed for the embeddings (index and question) and for answer generation.

INDEXING BEHAVIOUR
- The index is incremental by content_hash.
- If a note fails part-way through, the error is logged to the console. The chunks already embedded for that note stay in the index under its hash, so later builds treat the note as done and do not retry it until its content changes.
- initAsk can run at boot, before dashboard.json has set embedModel. This has no effect today because dashboard embed_model equals the default.

RELATION TO vault_rag.py
- This re-implements 'tools/vault_rag.py ask' in the browser. It does not read state/rag_index/.

PERSISTENCE AND EVIDENCE
- The chat log is not persisted.
- No file in the repo records whether the Ask index has ever been built.

### Designer Pro tab

`web-app` · status `runs-today`

Paths: `hub/index.html`, `hub/designer-pro.js`

Style generation and mixing over the vendored ui-ux-pro-max CSV corpus. Search and conflict checks run without a model and pick 'ingredients'. An optional local-model blend then proposes one design direction from those rows only.

**Entry points**

- `Tab button data-tab="designer" (view #view-designer)`
  - does: Shows the tab. designer-pro.js has already mounted on DOMContentLoaded, whatever tab is active. At mount it renders the domain buttons, renderMix(), and run() on the default domain 'style', which fetches styles.csv at page load.
  - changes: localStorage hub:tab
- `Domain buttons #dpDomains: style|color|typography|ux|chart|landing|product|icons|motion`
  - does: Fetches '../tools/ui-ux-pro-max/data/<file>' the first time a domain is used, then caches it in memory by file. Files: styles.csv, colors.csv, typography.csv, ux-guidelines.csv, charts.csv, landing.csv, products.csv, icons.csv, motion.csv. Parses as RFC-4180-ish CSV (strips BOM, handles quoted commas and newlines) and re-runs the search.
  - changes: nothing
- `#dpQuery search (input: 180 ms debounce; Enter: immediate)`
  - does: Token-overlap scoring over the domain's title columns and all non-NOISE columns. - Phrase in title +30, phrase in body +12. - Each term of 2+ chars: +6 if in title, +2 if in body. - An empty query scores every row 1. - Keeps rows with score > 0 and shows the top 40. Each row shows up to 10 non-title, non-NOISE fields shorter than 900 chars. - On zero hits it prints: python3 tools/ui-ux-pro-max/scripts/search.py "<q>" --domain <id>.
  - changes: nothing
- `'+ mix' on a row / 'remove' in the mix list / #dpClear 'Clear mix'`
  - does: Adds or removes an ingredient {key, domain, title, row}. The corpus checks are recomputed and the results re-run.
  - changes: in-memory mix only
- `#dpGenerate 'Blend into a direction' (label becomes 'Cancel' while running)`
  - does: 1. resolveTier(): fetch ../dashboard.json once and override only sm.model and sm.num_ctx. Always uses tiers.sm. 2. GET /api/tags family check. 3. POST /api/generate with prompt buildPrompt(brief, checks), options {temperature:0.5, num_predict:420, num_ctx: tier.num_ctx} and an AbortController signal. An elapsed-seconds ticker is shown. 4. Renders the output labelled 'a proposal, not a corpus match … Nothing here is written to any token file.' Clicking the button again aborts the request.
  - changes: Ollama: the sm model stays loaded (keep_alive 5m, no evict). DOM only.

**Inputs**

- #dpBrief text ('What is being designed')
- #dpQuery search text
- active domain
- selected mix rows
- dashboard.json hardware.local_llm.tiers.sm.{model, context_window_tokens}

**Outputs**

- #dpResults: scored corpus row cards; #dpCount row count
- #dpChecks: corpus checks, each blocked, warn or ok
- #dpOut: generated text with four sections (DIRECTION, CONTRIBUTIONS, TENSIONS, AVOID) citing [ing_n], plus an ingredients footer

**Reads**

- ../tools/ui-ux-pro-max/data/styles.csv
- ../tools/ui-ux-pro-max/data/colors.csv
- ../tools/ui-ux-pro-max/data/typography.csv
- ../tools/ui-ux-pro-max/data/ux-guidelines.csv
- ../tools/ui-ux-pro-max/data/charts.csv
- ../tools/ui-ux-pro-max/data/landing.csv
- ../tools/ui-ux-pro-max/data/products.csv
- ../tools/ui-ux-pro-max/data/icons.csv
- ../tools/ui-ux-pro-max/data/motion.csv
- ../dashboard.json
- localStorage hub:endpoint

**Depends on**

- tools/ui-ux-pro-max/data CSV corpus
- Ollama sm tier model (default llama3.1:8b), for the blend only

**Gates and checkpoints**

- The corpus checks need no model and are read from row fields. For every mix row, any domain:
  - Status == deprecated is 'blocked' and names Replacement Domain / Replacement ID.
  - Accessibility tag 'risk:high' is 'blocked'; 'risk:conditional' is 'warn'.
  - Performance tag 'cost:high' is 'warn'.
- The corpus checks for style-domain rows only:
  - Mode clash is 'blocked' when some style has Preferred Mode 'dark' and some style has 'Dark Mode ✓' = not-recommended. The code does not require these to be different rows.
  - No mode left is 'blocked' when some style has Dark not-recommended and some style has Light not-recommended.
  - Two or more Complexity 'high' styles is 'warn'.
  - Three or more styles is 'warn'.
- The checks go into the prompt as a <CHECKS> block. HARD RULES tell the model to:
  - address every CHECK in TENSIONS and never answer 'none' while one is listed
  - use only the <INGREDIENTS> block
  - never introduce a colour, typeface or library that is not in it
  - cite [ing_n]
- The Generate button is disabled while the mix is empty.
- The banner says nothing is written to ARTIFACT A: studio tokens stay operator-approval only, and the output never becomes a token.
- The CLI search.py (BM25) is declared authoritative when it disagrees with this tab.

**Invoked by**

- THE HUB (mounted at page load; shown via the tab strip)

**Invokes**

- HubOllama.getEndpoint, fetchTags, familyMatches, generate (with signal), stripThink
- suggests (does not run) tools/ui-ux-pro-max/scripts/search.py

**Notes**

WHAT NEEDS A MODEL
- No model is needed for CSV parsing, scoring, row display, the mix and every conflict check.
- A model is needed only for the 'Blend into a direction' text.
- The blend always uses the sm tier and ignores hub:tier.

FILTERING
- NOISE columns, excluded from scoring, display and prompt: No, Google Fonts URL, CSS Import, Tailwind Config, Import Code, GSAP Snippet, Implementation Checklist, Design System Variables, Code Example Good, Code Example Bad.
- Ingredient fields of 600 chars or more are dropped from the prompt.

PERSISTENCE
- Neither the output nor the mix is persisted (no localStorage, no file).

DOMAIN MISMATCH WITH THE CLI
- The hub id 'motion' maps to motion.csv. tools/ui-ux-pro-max/scripts/core.py CSV_CONFIG names that file 'gsap' and has no 'motion' key.
- search.py's --domain choices come from CSV_CONFIG.keys(), so the suggested fallback '--domain motion' would be rejected by argparse. The other eight ids match CSV_CONFIG keys.
- The hub omits three CLI domains: react (react-performance.csv), web (app-interface.csv) and google-fonts (google-fonts.csv). data/ also has ui-reasoning.csv, which the hub does not use.

CORPUS COUNTS
- The tab hint says 79 styles, 192 palettes, 74 font pairings, 119 UX guidelines.
- Counting rows that start with a number in the data files: styles.csv 88 rows, 9 of them deprecated (79 remain); colors.csv 192; typography.csv 74; ux-guidelines.csv 119.
- The tab loads all 88 style rows and flags the deprecated ones.
- The check columns exist in styles.csv with live values: 11 risk:high, 25 risk:conditional, 7 cost:high.

EVIDENCE OF USE
- vault/studio-os/ui/ui-ux-intelligence-integration.md records one measured run: 137 s for a 3-ingredient blend with llama3.1:8b on CPU.
- It also records the earlier 'TENSIONS: none' failure that led to feeding checks into the prompt, and num_predict being lowered from 700 to 420.

### Brushes tab

`web-app` · status `runs-today`

Paths: `hub/index.html`, `tools/brush-designer/index.html`

Shows the standalone Procreate brush designer in an iframe. The designer itself has shape and grain generators, stroke preview and .brush/.brushset export.

**Entry points**

- `Tab button data-tab="brushes" (view #view-brushes)`
  - does: Shows <iframe id=brushFrame class=brush-frame title='Procreate Brush Designer' src='../tools/brush-designer/index.html' loading='lazy'>.
  - changes: localStorage hub:tab
- `<a href='../tools/brush-designer/index.html' target=_blank rel=noopener> 'Open in a new tab ↗'`
  - does: Opens the brush designer on its own.
  - changes: nothing from the hub side

**Outputs**

- Brush designer UI inside the iframe

**Reads**

- ../tools/brush-designer/index.html

**Depends on**

- tools/brush-designer/ (separate subsystem; the root README says it has one CDN dependency, fflate)

**Invoked by**

- THE HUB tab strip

**Invokes**

- tools/brush-designer/index.html (iframe)

**Notes**

The hint says 'nothing here talks to it besides embedding the page'. Hub code has no postMessage and no data exchange with it.

tools/brush-designer/ai/OllamaAssist.js reads and writes the same localStorage keys 'hub:endpoint' and 'hub:tier' (lines 74-83). Its comment says both tools are served from one origin, so the endpoint and tier settings are shared through storage, not through hub code.

The brush designer also uses the localStorage key 'brushPresets' and IndexedDB, and Section.js has its own STORE_KEY. Those belong to the brush-designer subsystem, as do brush export and generation, and are not inventoried here.

### Pipeline tab

`web-app` · status `stub`

Paths: `hub/index.html`, `hub/app.js`, `hub/styles.css`

A static preview of the pipeline 'transit rail' layout that is not wired to anything. It is the placeholder for a live pipeline view and the natural place to connect an external Pipelines tool.

**Entry points**

- `Tab button data-tab="pipeline" (view #view-pipeline)`
  - does: Shows a warning banner and a hard-coded rail. The rail is rendered once when app.js runs at page load.
  - changes: localStorage hub:tab
- `<a href='../control_room.html' target=_blank rel=noopener> (banner link)`
  - does: Opens the live view, which router.js fills by polling dashboard.json. Start-Hub.ps1's server serves the repo root, so control_room.html is reachable on the same origin.
  - changes: nothing

**Inputs**

- None at runtime. The data is the PREVIEW_STATIONS constant in hub/app.js.

**Outputs**

- Banner: 'Not connected. This tab is a static preview of the pipeline layout — it does not read dashboard.json and nothing here starts a routed task … wiring this tab to it is future work (see README.md → "What does not run yet")'
- Panel heading 'Pipeline Rail' with the static tick 'example data, not live'
- #previewRail containing 5 station divs

**Gates and checkpoints**

- There is no execution path: no click handlers, no fetch, no polling and no dispatch.

**Invoked by**

- THE HUB tab strip

**Notes**

WHAT IT RENDERS TODAY

At load, app.js sets #previewRail.innerHTML from PREVIEW_STATIONS. Each station becomes:
<div class="station s-{status}"><div class="node"></div><div class="name">{name}</div><div class="meta">{meta}</div></div>

The five stations:
- Ideation (complete, 'seed captured')
- Context Resolution (complete, 'L1 recalled')
- Generation (in_progress, 'sm tier · llama3.1:8b', hard-coded rather than taken from the tiers)
- Review (awaiting_render, 'queued')
- Export (queued, '—')

The tab has none of the following: progress bar, status word, phase count, project name, node tooltip or event log.

hub/styles.css:
- The rail is a column-flow grid (grid-auto-columns minmax(112px,1fr)) that scrolls horizontally inside itself. It is focusable (tabindex=0, role=group) and has a 2px connecting rule.
- The default node is a 14px square with a 2px --queued violet border.
- Node states: s-complete (cyan fill), s-in_progress (cyan outline), s-awaiting_render (amber outline), s-blocked (alert fill).
- s-queued, s-compositing and s-review fall back to the default violet outline.
- .station .meta.c-{cyan,amber,alert,queued,dim} are defined, but app.js never applies them.
- The station names do not match the phase labels in dashboard.json.

WHAT IT WOULD NEED TO BECOME LIVE

1. A data source.
   - Either fetch '../dashboard.json' (app.js already fetches it once at boot but reads only hardware.local_llm) or an equivalent endpoint with the same shape.
   - Current shape of dashboard.json.pipeline: {project, current_phase_id, phases:[{id, label, skill, status, progress_pct}], status_enum:[queued, in_progress, awaiting_render, compositing, review, blocked, complete], _note}.
   - Current content is authored example data: project PROJECT_AURORA, current_phase_id ph_03, and six phases:
     - ph_01 Concept & Style Frames / adobe_firefly / complete 100
     - ph_02 Score & Stems / suno_audio / complete 100
     - ph_03 Shot Generation / higgsfield_api / blocked 62
     - ph_04 3D Insert Shots / blender_python / queued 0
     - ph_05 Compositing / adobe_suite_uxp / compositing 18
     - ph_06 Delivery UI Page / css_html_ui / queued 0

2. A renderer like router.js renderPipeline(p).
   - It reads phases[].{id,label,skill,status,progress_pct} and uses: class 'station s-<status>', node title = id, name = label, meta = skill.
   - It adds a 'status-word' meta with the underscores replaced.
   - statusColor maps complete/in_progress/compositing to c-cyan, awaiting_render/review to c-amber, blocked to c-alert, queued to c-queued, and anything else to c-dim.
   - It fills '.bar > i' to progress_pct% and writes '#phase-count' as '<n complete>/<total> complete'.
   - The project name comes from renderHeader (#sys-project = pipeline.project).
   - router.js reads neither pipeline.current_phase_id nor status_enum.
   - The hub's station markup already matches router.js's (station, node, name, meta), so the same component would carry over.

3. Polling.
   - router.js CONFIG.POLL_MS = 5000, using fetch('dashboard.json?t='+Date.now(), {cache:'no-store'}).
   - It stops on document.hidden and fetches immediately on return.
   - On a failed fetch it adds body.offline and keeps the last STATE on screen.
   - From hub/ the URL would be '../dashboard.json'.

4. CSS.
   - hub/styles.css lacks .station .bar, s-compositing and s-review. control_room.html's inline CSS has them (lines 154-170).

5. Optional extra feeds from dashboard.json.
   - system_status {state, mode, active_skill, last_heartbeat}. blocked_reason is in the file but router.js does not render it.
   - event_log[] {ts, actor, event, detail}
   - active_variables

6. Constraints any writer must satisfy.
   - tools/verify_system.py check_pipeline(), run in CI by .github/workflows/verify.yml, requires:
     - unique phase ids
     - current_phase_id to be one of the ids
     - each phase.skill to be registered in registries.skills (file skills/<skill>.skill.md). Registered today: higgsfield_api, suno_audio, adobe_firefly, adobe_suite_uxp, blender_python, css_html_ui, local_rag_orchestration, hardware_compute, ui_ux_intelligence.
     - status to be in status_enum
     - 0 <= progress_pct <= 100
     - complete to mean 100, and queued to mean 0

7. A writer. Nothing in code writes dashboard.json.pipeline.
   - router.js writeDashboard() is a stub. Its TODO would call dispatchAPICall('agent', '/dashboard/patch'), and the agent is registered as 'http://localhost:8787' (stub).
   - tools/vault_rag.py ask --write-dashboard writes only hardware.local_llm.context_used_pct and loaded_tier.
   - tools/reconcile_models.py --write writes only hardware.local_llm.tiers[*].model and _tiers_note.
   - The root README.md 'What does not run yet' says no routed task executes: router.js dispatch is stubs, and Router.md is a contract with no implementing code.
   - An external Pipelines tool would have to either produce phase state in the dashboard.json.pipeline schema (and pass check_pipeline), or be read directly by a rewritten tab.

### Start-Hub.ps1

`launcher` · status `runs-today`

Paths: `tools/launcher/Start-Hub.ps1`

One-press launcher. It starts, or reuses, a Python static server bound to 127.0.0.1 and rooted at the repo root, then opens THE HUB in the default browser. It can also stop that background server.

**Entry points**

- `.\Start-Hub.ps1`
  - does: Probes 127.0.0.1:8765..8774 and reuses the first port whose /hub/index.html returns 200 and contains 'Studio Headless OS'. Otherwise it starts python on the first free port, polls every 250 ms for up to 15 s, opens http://localhost:<port>/hub/ and prints 'THE HUB is live at <url>'.
  - changes: may spawn a hidden background python.exe http.server process that outlives the browser; opens a browser tab
- `.\Start-Hub.ps1 -Port <int, ValidateRange 1024-65535, default 8765> -PortSearch <int, ValidateRange 1-50, default 10>`
  - does: Sets the probe range to Port..(Port+PortSearch-1). The range applies both to launching and to -Stop.
  - changes: same as above
- `.\Start-Hub.ps1 -NoBrowser`
  - does: Starts or reuses the server without calling Start-Process on the URL. The 'THE HUB is live at <url>' line prints whether or not this switch is used.
  - changes: may spawn the python server process
- `.\Start-Hub.ps1 -Stop`
  - does: For each port in range that passes Test-HubServer: 1. Get-NetTCPConnection -LocalPort <p> -State Listen gives the owning PIDs. 2. Stop-Process -Id <pid> -Force. Prints 'Stopped N hub server process(es).' or 'No hub server was running.' and returns.
  - changes: kills the hub server process(es)
- `<python.exe|python3.exe> -m http.server <port> --bind 127.0.0.1 --directory <repo root> (Start-Process -WindowStyle Hidden -WorkingDirectory <repo root>)`
  - does: The server the script actually spawns. The executable is resolved with Get-Command python.exe, falling back to python3.exe.
  - changes: serves every file under the repo root on 127.0.0.1:<port>

**Inputs**

- param([ValidateRange(1024,65535)][int]$Port = 8765, [ValidateRange(1,50)][int]$PortSearch = 10, [switch]$Stop, [switch]$NoBrowser)

**Outputs**

- stdout 'THE HUB is live at http://localhost:<port>/hub/'
- stdout 'Stopped N hub server process(es).' or 'No hub server was running.' (with -Stop)

**Reads**

- <root>\hub\index.html (Test-Path existence check; root = two levels above $PSScriptRoot)
- http://127.0.0.1:<p>/hub/index.html (Invoke-WebRequest probe, -TimeoutSec 3)

**Depends on**

- Windows PowerShell (Get-NetTCPConnection, Invoke-WebRequest -UseBasicParsing, Start-Process, System.Net.Sockets.TcpClient)
- Python 3 on PATH as python.exe or python3.exe (http.server module)
- Default browser

**Environment and secret names (names only)**

- PATH (read implicitly by Get-Command to resolve python.exe / python3.exe)

**Gates and checkpoints**

- $ErrorActionPreference = 'Stop'.
- Repo check: it throws "Could not find hub\index.html under '<root>'. Keep Start-Hub.ps1 in tools\launcher\." if <root>\hub\index.html is missing.
- Test-PortInUse opens a TCP connection to 127.0.0.1:<p>.
- Test-HubServer: a port counts as the hub only if it is in use, /hub/index.html returns HTTP 200 within 3 s, and the content matches 'Studio Headless OS'. Only such a port is reused or stopped.
- It throws 'Ports <Port>-<last> are all in use. Pass -Port with a free one.'
- It throws 'Python was not found on PATH. Install Python 3, or serve the repo root yourself and open http://localhost:<Port>/hub/.'
- It throws 'Server on port <free> did not come up within 15s.'
- It deliberately uses python.exe, not pythonw.exe. The code comment says http.server logs to stderr, stderr is None under pythonw, and each connection is dropped.

**Invoked by**

- Studio Hub.lnk shortcuts written by Install-Shortcut.ps1 (Desktop and Start Menu; the Start Menu copy has hotkey CTRL+ALT+H)
- user from a PowerShell prompt

**Invokes**

- python.exe (or python3.exe) -m http.server
- default browser via Start-Process <url>
- Stop-Process -Force (with -Stop)

**Notes**

The server binds 127.0.0.1, but the opened URL uses 'localhost'.

PORT DISAGREEMENT
- This script and tools/launcher/README.md use 8765 (probe 8765-8774).
- .claude/launch.json and the root README.md use 8347. That is outside the default range, so a server started from launch.json is never detected, reused or stopped by this script unless -Port 8347 is passed.
- hub/index.html's offline note says 8000.

The whole repo root is exposed on loopback, not just hub/. That includes control_room.html, dashboard.json and state/.

The repo contains no run log. Evidence of use is indirect: the shortcuts exist, and DECISIONS.md records the hub being rendered.

### Install-Shortcut.ps1

`cli` · status `runs-today`

Paths: `tools/launcher/Install-Shortcut.ps1`, `tools/launcher/hub.ico`, `tools/launcher/.gitignore`, `tools/launcher/README.md`

Generates the hub icon from the HARD MONO palette and writes Desktop and Start Menu .lnk shortcuts that run Start-Hub.ps1 in a hidden window. The Start Menu copy carries a global hotkey.

**Entry points**

- `powershell -ExecutionPolicy Bypass -File .\Install-Shortcut.ps1`
  - does: Writes hub.ico and two '<Name>.lnk' shortcuts (default 'Studio Hub'). The Start Menu (Programs) copy gets hotkey CTRL+ALT+H.
  - changes: tools/launcher/hub.ico; <Desktop>\Studio Hub.lnk; <Programs>\Studio Hub.lnk (both overwritten if present)
- `.\Install-Shortcut.ps1 -Name <string, default 'Studio Hub'>`
  - does: Shortcut file name is <Name>.lnk.
  - changes: same
- `.\Install-Shortcut.ps1 -Hotkey <string, default 'CTRL+ALT+H'>`
  - does: Hotkey set only on shortcuts whose path matches '*\Programs\*' (the Start Menu copy).
  - changes: same
- `.\Install-Shortcut.ps1 -NoHotkey`
  - does: Writes the shortcuts with no hotkey and skips the 'Keyboard shortcut:' line.
  - changes: same

**Inputs**

- param([string]$Name = 'Studio Hub', [string]$Hotkey = 'CTRL+ALT+H', [switch]$NoHotkey)

**Outputs**

- stdout 'Icon written: <path>'
- stdout 'Shortcut written: <lnk>' (twice)
- stdout blank line, then 'Next step (Windows blocks scripted pinning):' and "  right-click the Desktop 'Studio Hub' icon -> Pin to taskbar". The name 'Studio Hub' is hard-coded even when -Name is changed.
- stdout 'Keyboard shortcut: <Hotkey>' (unless -NoHotkey)

**Reads**

- tools/launcher/Start-Hub.ps1 (existence check via Test-Path)

**Writes**

- tools/launcher/hub.ico: PNG-compressed ICO with sizes 256, 64, 48, 32, 16. The design is a #000000 field with a #383838 rule, two #00E5FF parallelogram slashes and a #FFC400 bar.
- [Environment]::GetFolderPath('Desktop')\<Name>.lnk
- [Environment]::GetFolderPath('Programs')\<Name>.lnk (Start Menu)

**Depends on**

- Windows PowerShell
- System.Drawing (Add-Type -AssemblyName System.Drawing)
- WScript.Shell COM object

**Environment and secret names (names only)**

- SystemRoot (used to build the powershell.exe target path)

**Gates and checkpoints**

- $ErrorActionPreference = 'Stop'.
- It throws 'Start-Hub.ps1 is missing from <PSScriptRoot>.' if the launcher is not beside it.
- Taskbar pinning is manual and one-time. Per the script and the launcher README, Windows blocks scripted pinning; the README says 'since 1809'.

**Invoked by**

- user (one-time install)

**Invokes**

- writes shortcuts that run tools/launcher/Start-Hub.ps1

**Notes**

EVIDENCE IT HAS RUN
- tools/launcher/hub.ico exists (4677 bytes, mtime Sep 1 09:52).
- 'Studio Hub.lnk' exists at C:/Users/utopi/OneDrive/Desktop (2552 bytes). This is where GetFolderPath('Desktop') points on this machine; C:/Users/utopi/Desktop/Studio Hub.lnk does not exist.
- 'Studio Hub.lnk' exists at C:/Users/utopi/AppData/Roaming/Microsoft/Windows/Start Menu/Programs (2576 bytes).
- Both .lnk files are dated Aug 31 22:35, earlier than hub.ico and Install-Shortcut.ps1 (Sep 1 09:52).

FILES
- tools/launcher/.gitignore ignores hub.ico ('# Generated by Install-Shortcut.ps1').
- tools/launcher/README.md says hub.ico is safe to delete and gets rebuilt.
- Re-running regenerates the icon and overwrites both shortcuts.

### Studio Hub.lnk shortcuts (generated)

`launcher` · status `generated`

Paths: `C:/Users/utopi/OneDrive/Desktop/Studio Hub.lnk (outside repo)`, `C:/Users/utopi/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Studio Hub.lnk (outside repo)`

The daily entry point: a click or Ctrl+Alt+H runs Start-Hub.ps1 in a hidden window.

**Entry points**

- `<SystemRoot>\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "<repo>\tools\launcher\Start-Hub.ps1"`
  - does: The shortcut target and arguments set by Install-Shortcut.ps1. WorkingDirectory = repo root, WindowStyle = 7 (minimized), IconLocation = '<repo>\tools\launcher\hub.ico,0', Description = 'Serve Creative Headquarters and open THE HUB'.
  - changes: see Start-Hub.ps1
- `Ctrl+Alt+H`
  - does: Global hotkey on the Start Menu copy only. It launches Start-Hub.ps1 with default parameters (probe 8765-8774).
  - changes: see Start-Hub.ps1

**Depends on**

- tools/launcher/Start-Hub.ps1
- tools/launcher/hub.ico

**Invoked by**

- user (Desktop/taskbar click, Start Menu, Ctrl+Alt+H)

**Invokes**

- tools/launcher/Start-Hub.ps1

**Notes**

Existence and size were confirmed on disk. The target and arguments are taken from Install-Shortcut.ps1 source. The binary .lnk contents were not parsed.

### hub-static-server (.claude/launch.json)

`launcher` · status `runs-today`

Paths: `.claude/launch.json`

Claude Code preview launch configuration that serves files over HTTP so the hub can fetch its data files.

**Entry points**

- `python3 -m http.server 8347`
  - does: Configuration 'hub-static-server': runtimeExecutable 'python3', runtimeArgs ['-m','http.server','8347'], port 8347, file version '0.0.1'. The hub would be at http://localhost:8347/hub/ if the working directory is the repo root.
  - changes: spawns a python http.server process

**Outputs**

- HTTP static server on port 8347

**Depends on**

- python3 on PATH
- Claude Code preview launcher (reads .claude/launch.json)

**Invoked by**

- Claude Code preview_start with name 'hub-static-server'
- root README.md names it as one way to serve the hub

**Invokes**

- python3 -m http.server

**Notes**

Unlike Start-Hub.ps1, it passes no --bind and no --directory. It serves whatever working directory the launcher uses, which this file does not state.

Port 8347 disagrees with Start-Hub.ps1 (8765-8774) and with the hub/index.html offline note (8000).

It is invoked as 'python3'. Start-Hub.ps1 prefers python.exe and treats python3.exe only as a fallback, and README.md's Windows host may not have python3 on PATH; this is not verified.

The root README.md lists it under 'What runs today', but no file shows that it has been used.

## Usage flows

### One-time install of the launcher

1. From tools/launcher: powershell -ExecutionPolicy Bypass -File .\Install-Shortcut.ps1 (optional -Name, -Hotkey, -NoHotkey).
2. The script writes tools/launcher/hub.ico, <Desktop>\Studio Hub.lnk and <Start Menu Programs>\Studio Hub.lnk. The Programs copy gets hotkey CTRL+ALT+H.
3. Manually right-click the Desktop 'Studio Hub' icon and choose 'Pin to taskbar'.

### Daily launch

1. Press Ctrl+Alt+H or click the Studio Hub shortcut.
2. The shortcut runs: powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File <repo>\tools\launcher\Start-Hub.ps1.
3. Start-Hub probes 127.0.0.1:8765-8774. It reuses a port whose /hub/index.html returns 200 and contains 'Studio Headless OS'. Otherwise it spawns 'python.exe -m http.server <free> --bind 127.0.0.1 --directory <repo root>' hidden and waits up to 15 s.
4. The browser opens http://localhost:<port>/hub/.
5. The hub boots: the last tab is restored from localStorage hub:tab (default library). At the same time it fetches ../dashboard.json (hardware.local_llm overrides) and calls GET {endpoint}/api/tags for the connection chip, twice. Designer Pro mounts and fetches styles.csv.

### Alternate serve paths (port disagreement)

1. Claude Code: preview_start 'hub-static-server' runs python3 -m http.server 8347. Open http://localhost:8347/hub/.
2. Manual, as the offline note says: run python3 -m http.server from the repo root, then open http://localhost:8000/hub/.
3. Opening hub/index.html over file:// shows the amber offline note, and the manifest, dashboard and CSV fetches fail.
4. Each port is a different origin, so localStorage (endpoint, tier, index, overviews) is not shared between them.

### Stop the background server

1. .\Start-Hub.ps1 -Stop only kills listeners on ports in the -Port/-PortSearch range that pass the hub probe.
2. A server started from launch.json on 8347 is outside the default range and is not stopped (unless -Port 8347 is passed).

### Configure Ollama connection

1. Click the header chip (#settingsBtn).
2. Set Endpoint. It is stored as localStorage hub:endpoint; the default is http://localhost:11434. dashboard.json hardware.local_llm.endpoint is applied, and persisted, only if hub:endpoint is unset.
3. Click 'Test connection' (GET /api/tags) to list the served models.
4. Choose Tier sm or md (localStorage hub:tier). The chip label does not refresh until the next refreshConnDot.
5. Optionally click 'Evict resident model'. It sends POST /api/generate keep_alive:0 for the tier model and the embed model.
6. If the test fails while curl works, add the hub origin to OLLAMA_ORIGINS per OBSIDIAN.md § A2 (that section only shows 'app://obsidian.md'), then fully restart Ollama.

### Library refresh and AI overview

1. Run python3 tools/vault_manifest.py --vault <path> manually; the hub does not run it. It writes state/vault_manifest.json.
2. In the Library tab, click 'Refresh manifest' (fetch ../state/vault_manifest.json).
3. Filter by search, kind or status and sort by updated or title. No model is used.
4. Click 'Generate AI overview' on a card. It does an /api/tags check, then /api/generate with the hub:tier model (temperature 0.4, num_predict 200, no num_ctx) on note.body[0:6000]. The result is cached in localStorage hub:overview:<content_hash> and the model stays resident 5m.

### Ask (browser RAG)

1. In the Ask tab, click 'Build / refresh index'. The manifest loads if needed and the embed model family is checked.
2. Each new or changed note is chunked (3200 chars, 480 overlap) and each chunk is embedded via /api/embeddings.
3. The embed model is evicted and the index saved to localStorage hub:index:v1. If it is too large, it is kept in memory only.
4. Optionally set Advanced: Top-k (12), Chunks used (4) and Max answer words (220).
5. Submit a question. Both model families are checked, the question is embedded, and the top-k chunks by cosine similarity are kept.
6. Chunks are packed within tier.payload_tokens*4 chars, up to rerankTo, and the QUERY_TEMPLATE prompt goes to /api/generate (temperature 0.6, top_p 0.95, tier num_ctx and num_predict). The tier model is then evicted.
7. The answer is rendered with [c_<path>_<i>] citations and a sources list with scores. The chat is not persisted.

### Designer Pro blend

1. Enter a Brief (#dpBrief).
2. Pick a domain (style, color, typography, ux, chart, landing, product, icons or motion). On first use this fetches ../tools/ui-ux-pro-max/data/<file>.csv.
3. Type a query. Token-overlap scoring returns the top 40 rows.
4. Press '+ mix' on rows across domains. The corpus checks update with no model: deprecated, risk:high or conditional, cost:high, mode clash, no mode left, complexity stacking, 3+ styles.
5. Click 'Blend into a direction'. The sm tier is resolved from dashboard.json, /api/tags is checked, and /api/generate runs (temperature 0.5, num_predict 420, sm num_ctx). The button becomes 'Cancel' and aborts the request if clicked.
6. Read the output: DIRECTION, CONTRIBUTIONS, TENSIONS and AVOID, citing [ing_n]. It is not saved anywhere and never becomes a token.
7. On zero hits the tab suggests python3 tools/ui-ux-pro-max/scripts/search.py "<q>" --domain <id>. For id 'motion' this command is invalid; the CLI key is 'gsap'.

### Pipeline tab (today) vs live view vs Pipelines integration

1. Today the Pipeline tab renders the 5 hard-coded PREVIEW_STATIONS once at load, with no fetch, no poll and no actions.
2. The live view is the banner link ../control_room.html. router.js there fetches dashboard.json?t=<now> every 5000 ms and renders pipeline.phases[] as label, skill, status word and a progress_pct bar, with pipeline.project in the header.
3. Nothing in code writes dashboard.json.pipeline. router.js writeDashboard and dispatchAPICall are stubs, with a TODO for http://localhost:8787/dashboard/patch.
4. Integration option A: a Pipelines tool writes dashboard.json.pipeline {project, current_phase_id, phases[{id,label,skill,status,progress_pct}], status_enum}. The write must pass tools/verify_system.py check_pipeline (registered skills, enum statuses, complete=100, queued=0). The hub tab then fetches ../dashboard.json and reuses router.js renderPipeline plus the control_room.html .bar, s-compositing and s-review CSS.
5. Integration option B: the Pipeline tab fetches from the Pipelines tool directly. No code or contract for that exists in this repo.

## Relationships

| From | Relation | To |
|---|---|---|
| Install-Shortcut.ps1 | writes <Desktop>\<Name>.lnk and <Programs>\<Name>.lnk; the Programs copy gets hotkey CTRL+ALT+H | Studio Hub.lnk shortcuts (generated) |
| Studio Hub.lnk shortcuts (generated) | runs powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File <repo>\tools\launche… | Start-Hub.ps1 |
| Start-Hub.ps1 | serves the repo root via python http.server on 127.0.0.1:8765-8774 and opens http://localhost:<port>/hub/; re… | THE HUB (hub web app) |
| hub-static-server (.claude/launch.json) | alternate static server on port 8347; disagrees with Start-Hub.ps1 (8765) and the index.html offline note (80… | THE HUB (hub web app) |
| THE HUB (hub web app) | reads hardware.local_llm (endpoint, tiers.sm/md model and context_window_tokens, embed_model) once at boot | dashboard.json |
| THE HUB (hub web app) | contains | Library tab |
| THE HUB (hub web app) | contains | Ask tab |
| THE HUB (hub web app) | contains (mounted at page load) | Designer Pro tab |
| THE HUB (hub web app) | contains | Brushes tab |
| THE HUB (hub web app) | contains | Pipeline tab |
| Library tab | calls getEndpoint, fetchTags, familyMatches, generate, stripThink for the AI overview | HubOllama (hub/ollama.js) |
| Ask tab | calls getEndpoint, fetchTags, familyMatches, chunkText, embed, normalize, retrieve, buildPrompt, generate, ev… | HubOllama (hub/ollama.js) |
| Designer Pro tab | calls getEndpoint, fetchTags, familyMatches, generate (with AbortSignal), stripThink; uses DEFAULT_TIERS | HubOllama (hub/ollama.js) |
| HubOllama (hub/ollama.js) | GET /api/tags; POST /api/embeddings; POST /api/generate; POST /api/generate keep_alive:0 (evict) | Ollama REST server (default http://localhost:11434) |
| Library tab | fetches ../state/vault_manifest.json and reads notes[] | state/vault_manifest.json |
| tools/vault_manifest.py | produces it (--vault default <repo>/vault, --out default <repo>/state/vault_manifest.json) with frontmatter a… | state/vault_manifest.json |
| Ask tab | shares in-memory manifestNotes; Build index calls loadManifest when it is empty | Library tab |
| Ask tab | mirrors 'vault_rag.py ask' in the browser (same CHUNK/OVERLAP/tier limits and prompt); defaults differ (top-k… | tools/vault_rag.py |
| Designer Pro tab | fetches styles, colors, typography, ux-guidelines, charts, landing, products, icons and motion .csv | tools/ui-ux-pro-max/data |
| Designer Pro tab | declares the CLI authoritative; suggests the command on zero hits ('--domain motion' is invalid, because the… | tools/ui-ux-pro-max/scripts/search.py |
| Designer Pro tab | re-reads hardware.local_llm.tiers.sm (model, context_window_tokens) in resolveTier() | dashboard.json |
| Brushes tab | shows it in an iframe; a link opens it on its own | tools/brush-designer/index.html |
| tools/brush-designer/ai/OllamaAssist.js | shares localStorage keys hub:endpoint and hub:tier on the same origin | THE HUB (hub web app) |
| Pipeline tab | banner links to it as the live pipeline view (same origin under Start-Hub) | control_room.html |
| Pipeline tab | would need pipeline.phases[{id,label,skill,status,progress_pct}] and pipeline.project to become live; not rea… | dashboard.json |
| control_room.html | router.js polls dashboard.json?t=<now> every 5000 ms (cache no-store; pauses when hidden) and renders header,… | dashboard.json |
| tools/verify_system.py | check_pipeline() enforces pipeline id uniqueness, current_phase_id validity, registered skills, status_enum a… | dashboard.json |
| tools/reconcile_models.py | --write updates hardware.local_llm.tiers[*].model (and _tiers_note), which the hub then reads as tier models | dashboard.json |
| tools/vault_rag.py | ask --write-dashboard writes hardware.local_llm.context_used_pct and loaded_tier (not pipeline) | dashboard.json |
| router.js | dispatchAPICall 'agent' registry entry; writeDashboard's TODO would POST /dashboard/patch (stub, not implemen… | http://localhost:8787 |
| THE HUB (hub web app) | settings dialog links § A2 for the OLLAMA_ORIGINS fix | OBSIDIAN.md |

**Open questions the files could not settle**

- Is the hub's origin actually allowed by Ollama? OBSIDIAN.md § A2 shows only setx OLLAMA_ORIGINS "app://obsidian.md". The hub hint says the hub origin must be added but does not name a port (8765, 8347 or 8000). The repo does not say whether Ollama accepts localhost origins by default.
- The three ports (8765 from Start-Hub, 8347 from launch.json, 8000 from the offline note) are separate browser origins. The cached hub:index:v1, hub:overview:*, hub:endpoint and hub:tier do not carry over between them. Should one port be canonical?
- Which vault is the Library meant to show? state/vault_manifest.json points at C:\Users\utopi\Creative-Writing (64 notes). README.md describes the Library as Content MDs in the repo's vault/, which is the vault_manifest.py default.
- What should produce live pipeline state for the Pipeline tab? No code writes dashboard.json.pipeline, and router.js writeDashboard and dispatchAPICall are stubs pointing at http://localhost:8787. Should the external Pipelines tool write the dashboard.json pipeline schema (and satisfy verify_system.py check_pipeline, which requires phase skills registered in registries.skills), or should the tab read Pipelines directly?
- Should the Pipeline tab use dashboard.json's phase vocabulary (6 phases, each bound to a skill) or the preview's station vocabulary (Ideation, Context Resolution, Generation, Review, Export)? The two do not correspond.
- Has the Ask index ever been built, has an AI overview ever been generated, and has the md tier been used? That state lives only in browser localStorage and no repo file records it.
- The two Studio Hub.lnk files are dated Aug 31 22:35, earlier than the current Install-Shortcut.ps1 and hub.ico (Sep 1 09:52). Were they produced by the current version of the installer? The binary .lnk contents were not parsed.
- When Claude Code starts hub-static-server from .claude/launch.json, which working directory and bind address does it use? The file sets neither.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: stripFrontmatter is exported but no hub file calls it, so frontmatter is chunked and embedded as-is.
  - evidence: tools/vault_manifest.py build() calls parse_frontmatter(raw) and stores only 'body': body.strip() (lines 132, 167). The manifest's note.body therefore already has YAML frontmatter removed, and the Ask tab does not embed it. It is true that stripFrontmatter is never called (it appears only in hub/ollama.js lines 97 and 174).
- **corrected**: The shape router.js consumes is pipeline = {project, current_phase_id, phases[...], status_enum}.
  - evidence: router.js reads d.pipeline.project (renderHeader, line 57) and p.phases[].{id,label,skill,status,progress_pct} (renderPipeline, lines 66-84). It never reads current_phase_id or status_enum; a grep across all .js/.html/.py files finds them only in tools/verify_system.py check_pipeline().
- **added**: (absent) Constraints a Pipelines writer of dashboard.json.pipeline must satisfy.
  - evidence: tools/verify_system.py check_pipeline() (lines 310-334), run in CI by .github/workflows/verify.yml line 26, fails on: - duplicate phase ids - a current_phase_id that is not a phase id - a phase.skill not in registries.skills - a status outside status_enum - progress_pct outside 0-100 - a complete phase with progress other than 100, or a queued phase with progress other than 0
- **corrected**: Start-Hub entry point: 'powershell -ExecutionPolicy Bypass -File tools/launcher/Start-Hub.ps1'.
  - evidence: This exact command does not appear in source. tools/launcher/Start-Hub.ps1 .EXAMPLE shows '.\Start-Hub.ps1' and '.\Start-Hub.ps1 -Stop'. The shortcut form is in Install-Shortcut.ps1 lines 95-96: powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "<Launcher>".
- **corrected**: -NoBrowser starts or reuses the server without opening the browser, and prints 'THE HUB is live at <url>'.
  - evidence: Start-Hub.ps1 lines 90-92: the 'THE HUB is live at $url' line is emitted on every non -Stop run. -NoBrowser only skips Start-Process $url.
- **corrected**: state/vault_manifest.json was built 2026-09-01T04:30:49Z.
  - evidence: state/vault_manifest.json line 3: "built": "2026-09-01T04:30:49.101105+00:00". Line 2 has vault C:\Users\utopi\Creative-Writing and line 4 has count 64.
- **corrected**: stripThink() removes <think>…</think> and a leading 'ANSWER:'.
  - evidence: hub/ollama.js line 94: replace(/<think>[\s\S]*?<\/think>/g, '').replace(/^ANSWER:\s*/m, '').trim(). The m flag without g removes the first 'ANSWER:' at the start of any line. Text before it is kept.
- **corrected**: Daily launch flow: hub boots by fetching dashboard.json, then /api/tags, then restores the last tab.
  - evidence: hub/app.js runs in this order: - line 22: fires the async dashboard.json fetch - line 54: synchronous showTab(localStorage hub:tab || 'library') - line 103: refreshConnDot() - line 35: refreshConnDot() again in the fetch's finally The tab is restored before the dashboard overrides land, and /api/tags is called twice at boot.
- **added**: (absent) Designer Pro fetches the CSV corpus only when its tab is used.
  - evidence: hub/designer-pro.js lines 441 and 444-445: mount() runs on DOMContentLoaded whatever tab is active and calls run() on activeDomain 'style'. That fetches ../tools/ui-ux-pro-max/data/styles.csv at page load.
- **corrected**: The corpus counts in the tab hint (79 styles, 192 palettes, 74 font pairings, 119 UX guidelines) were not verified.
  - evidence: Counting rows that start with digits and a comma in tools/ui-ux-pro-max/data/: - styles.csv: 88 rows, 9 with Status deprecated (79 non-deprecated) - colors.csv: 192 - typography.csv: 74 - ux-guidelines.csv: 119 The hint is consistent. The tab loads all 88 style rows and flags the deprecated ones.
- **added**: (absent) Hub domain coverage compared with the CLI.
  - evidence: tools/ui-ux-pro-max/scripts/core.py CSV_CONFIG also has react (react-performance.csv), web (app-interface.csv) and google-fonts (google-fonts.csv). hub/designer-pro.js DOMAINS does not include them. data/ui-reasoning.csv is also unused by the hub. The 'motion' vs 'gsap' mismatch is confirmed: core.py line 59 has 'gsap' mapped to motion.csv, and search.py line 99 builds choices=list(CSV_CONFIG.keys()).
- **added**: (absent) Ask index partial-failure behaviour.
  - evidence: hub/app.js lines 292-304: chunks are pushed one part at a time inside the try. If embedding fails part-way, the pushed chunks keep note.content_hash. alreadyDone (line 288) then marks the note as done, so later builds do not retry it.
- **added**: (absent) Library AI overview context window.
  - evidence: hub/app.js line 233: options are {temperature:0.4, num_predict:200} with no num_ctx, so the tier's num_ctx from dashboard.json or DEFAULT_TIERS is not applied to this call.
- **added**: (absent) The dashboard endpoint is persisted.
  - evidence: hub/app.js line 34: when hub:endpoint is unset, HubOllama.setEndpoint(llm.endpoint) writes it to localStorage. Later changes to dashboard.json's endpoint are then ignored for that origin.
- **corrected**: Before every model call, a tab calls GET /api/tags and checks HubOllama.familyMatches.
  - evidence: True for Library (app.js line 225), Build index (276), Ask (356-358) and Designer Pro (designer-pro.js line 323). The settings #evictBtn (app.js lines 83-88) calls evict with no tags check. The Ask flow also never evicts the embed model after embedding the question; it evicts only the tier model (line 371).
- **corrected**: Mode clash is 'blocked': one style has Preferred Mode dark while another has 'Dark Mode ✓' not-recommended.
  - evidence: hub/designer-pro.js lines 142-150 filter the style rows into darkPref and darkBad independently and never require the two rows to differ. Status/risk/cost checks apply to mix rows of any domain; the mode, complexity and count checks apply only to style rows.
- **added**: (absent) Install-Shortcut next-step text ignores -Name.
  - evidence: tools/launcher/Install-Shortcut.ps1 line 119 hard-codes "right-click the Desktop 'Studio Hub' icon -> Pin to taskbar" whatever -Name is set to.
- **corrected**: Desktop 'Studio Hub.lnk' exists under C:/Users/utopi/OneDrive/Desktop, and the Start Menu copy under %APPDATA%.
  - evidence: Both confirmed on disk: - C:/Users/utopi/OneDrive/Desktop/Studio Hub.lnk (2552 bytes) - C:/Users/utopi/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Studio Hub.lnk (2576 bytes) Added detail: both are dated Aug 31 22:35, earlier than hub.ico and Install-Shortcut.ps1 (Sep 1 09:52). C:/Users/utopi/Desktop/Studio Hub.lnk does not exist.
- **added**: (absent) The Studio Hub.lnk shortcuts as a separate entry point artifact.
  - evidence: The files exist on disk outside the repo, and their target and arguments come from Install-Shortcut.ps1 lines 95-113. They are listed as a separate 'generated' launcher entry.
- **added**: (absent) Evidence the hub tabs have been exercised.
  - evidence: DECISIONS.md line 567: 'Rendered at 375 / 1000 / 1440px on all five Hub tabs'. vault/studio-os/ui/ui-ux-intelligence-integration.md line 180: '137s for a 3-ingredient blend, llama3.1:8b, CPU only'. No file records an Ask index build or an AI overview run.
- **added**: (absent) CI coverage of hub and launcher.
  - evidence: .github/workflows/verify.yml runs 'node --check router.js' only (line 59). Nothing checks hub/*.js or tools/launcher/*.ps1. vault/studio-os/ui/ui-ux-intelligence-integration.md line 135 says check_palette_parity reads only control_room.html.
- **corrected**: Pipeline item 5: system_status {state, mode, active_skill, last_heartbeat, blocked_reason} is an optional feed router.js renders.
  - evidence: router.js renderHeader (lines 52-64) uses state, mode, active_skill and last_heartbeat. blocked_reason exists in dashboard.json line 28, but router.js never reads it (grep finds no match).
- **corrected**: HubOllama uses the legacy /api/embeddings route.
  - evidence: hub/ollama.js lines 56-63 call POST /api/embeddings with {model, prompt, keep_alive:'5m'} and read data.embedding. tools/vault_rag.py lines 324 and 406 use the same route. 'Legacy' is a characterization the repo files do not state, so it was removed.
- **unverifiable**: The hub-static-server serves the repo root and binds its default interface.
  - evidence: .claude/launch.json has only runtimeExecutable python3, runtimeArgs ['-m','http.server','8347'] and port 8347, with no --directory or --bind. The working directory the preview launcher uses is not stated in any repo file.
