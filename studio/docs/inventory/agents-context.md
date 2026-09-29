# Agents, brand gates, domain libraries

Subsystem `agents-context` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 24 entries · 20 corrections made to the first reading.

## Summary

Three kinds of markdown file make up this subsystem. None is executable, and no code reads the content of any of them.

(1) agents/ holds nine Claude Code sub-agent persona files: business-analyst, code-reviewer, content-strategist, debugger, documentation-writer, frontend-developer, project-manager, test-expert and ux-consultant. README.md says they were vendored from the "Claude-Code" repo. Each frontmatter holds only `name` and `description`; no file declares `tools` or `model`. README.md says to install them by copying into ~/.claude/agents/ and to invoke them with `claude --agent <name>`. Nothing in the repo confirms that flag exists. They are generic software-engineering personas. They are not registered in dashboard.json and are not in the Router.md §3 routing table. They never mention brand gates, the vault or Content MDs. Nothing in the repo invokes them. Router.md §1 and README.md list them as "9 sub-executor definitions", and ~/.claude/agents/ does not exist on this machine.

(2) context/brand/ is for the ten brand-gate constants that Router.md §3 makes mandatory or conditional for the nine skills. Three are authored at L0: visual_identity, typography_system and color_science. They were transcribed from skills/css_html_ui.skill.md ARTIFACT A (DECISIONS.md D9) and rewritten for HARD MONO on 2026-09-01 (D10). Two of them declare their own gaps:
- visual_identity §7: generated-imagery motifs, framing and texture.
- color_science §5: working space, LUTs and grading.

The other seven are not on disk: motion_language, sound_identity, brand_voice, narrative_continuity, render_philosophy, pipeline_ethics and memory_discipline. Router.md §5 resolves an unauthored gate in three steps:
- L1: recall from a vault Content MD whose `context_brand` names the gate (confidence 0.9).
- L2: derive from at least 3 notes (confidence 0.3-0.8).
- L3: nothing found. Manual and supervised modes ask the operator; autonomous mode parks the task.

dashboard.json sets the mode to autonomous. Today the vault holds one real Content MD, whose context_brand is [visual_identity, typography_system, color_science]. So none of the seven can resolve at L1 or L2, and all seven land at L3. context/brand/README.md defines the contract: which skills each gate gates, what each must answer, and the format. Nothing implements the ladder in code. README.md says "no code implements" the Router, and router.js reports only whether a gate is authored at L0.

(3) context/domain/ holds ten general reference libraries, each 216 lines with the same structure:
- §1 is a routing glossary: ten categories A-J with ten "Subcategory Triggers" each. It points to "## 2.X", but the headings on disk are "### 2.X".
- §2.A-2.J hold ten numbered nodes each (2.X.1-2.X.10).
- §3 "EXECUTION VARIABLES (The Hand-off Payload)" defines primary_domain_bias, system_exclusion_tokens and hardware_render_overrides.

§3 says the payload is "passed to corresponding `.skill.md` scripts", but no skill file names any library or payload key. The libraries are retrieval material only. Router.md §3 forbids a library from satisfying a brand gate. router.js enforces this by resolving only to context/brand/, and tools/verify_system.py check_domain_libraries enforces it for the dashboard registry. vault/SCHEMA.md lists `context_domain` as an optional frontmatter field without defining it. One real note uses it: vault/studio-os/ui/ui-ux-intelligence-integration.md, with [typography_ad_arts].

Machine checks: tools/verify_system.py runs in CI (.github/workflows/verify.yml) and exits 1 on any failure and 0 otherwise. The checks that touch this subsystem are:
- check_brand_gates: authored flag against disk, the path pattern, and gates_skills against registered skills.
- check_domain_libraries: declared libraries exist; none doubles as a gate.
- check_skill_headers: mandatory_context names only declared gates.
- check_context_loaded: only authored gates may be claimed as loaded.
- check_router_js and check_router_md: gate roles are mentioned; router.js builds no context/domain/ path.
- check_palette_parity: compares only 7 hex tokens between ARTIFACT A and control_room.html.

The §0 provenance of visual_identity and typography_system says they are "machine-enforced" by check_palette_parity. That overstates it: no typography value and no line/ink/ink-dim/spacing/radius/motion/focus value is checked, and the gate files themselves are never read. Several documents are stale about gate state: BOOT.md, README.md lines 119-121 and 158-159, vault/_migration/GAP-ANALYSIS.md §6, and the check_brand_gates docstring. dashboard.json matches the files on disk.

## Tools

### business-analyst

`agent` · status `vendored`

Paths: `agents/business-analyst.md`

Claude Code sub-agent persona: a technical business analyst who turns stakeholder goals into requirements, user stories with acceptance criteria, process maps, feasibility/impact assessments and decision documents.

**Entry points**

- `copy agents/business-analyst.md into ~/.claude/agents/ (README.md line 102: "copy into `~/.claude/agents/`"; no install script exists in the repo)`
  - does: Installs the agent definition for Claude Code
  - changes: writes ~/.claude/agents/business-analyst.md (outside the repo)
- `claude --agent business-analyst`
  - does: Runs Claude Code as this agent. The invocation is stated only in README.md line 103; the flag cannot be verified from repo files
  - changes: nothing stated

**Inputs**

- feature request or business problem
- stakeholder goals; constraints (timeline, budget, technical limitations, team capacity, dependencies)

**Outputs**

- user stories with acceptance criteria
- requirements documents structured by priority
- decision logs (options, tradeoffs, recommendations)
- process flow diagrams (text or mermaid)
- impact assessments (effort, value, risk)

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- 5-step procedure: clarify the goal -> map the current state -> identify constraints -> define scope (in/out/deferred) -> write up requirements, acceptance criteria, open questions, risks and the recommended approach

**Invoked by**

- user, via `claude --agent business-analyst` after a manual copy to ~/.claude/agents/ (README.md)

**Notes**

Frontmatter verbatim: name: business-analyst | description: Technical business analyst for bridging business needs and technical implementation. Use when translating stakeholder goals into requirements, writing user stories with acceptance criteria, mapping processes, assessing feasibility, or facilitating tradeoff discussions. | tools: ABSENT | model: ABSENT. Source repo per the README 'Where each piece came from' table: Claude-Code. README calls it 'Portable as-is'. It is not in dashboard.json registries or the Router.md §3 table. ~/.claude/agents/ does not exist on this machine (read-only check), so it is not installed at user level.

### code-reviewer

`agent` · status `vendored`

Paths: `agents/code-reviewer.md`

Claude Code sub-agent persona: a senior code reviewer checking a change for correctness, security, design, readability, performance and testing.

**Entry points**

- `copy agents/code-reviewer.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/code-reviewer.md (outside the repo)
- `claude --agent code-reviewer`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- pull request or code change (review the change, not the entire file)

**Outputs**

- review comments categorised as Blocker / Suggestion / Nit / Question / Praise, with specific alternatives (pseudocode allowed)

**Reads**

- the changed code

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Order: correctness first, then clarity, then style
- Blocker = must fix before merge (correctness issue, security vulnerability, data-loss risk)

**Invoked by**

- user, via `claude --agent code-reviewer` (README.md)

**Notes**

Frontmatter verbatim: name: code-reviewer | description: Senior code review agent for assessing quality, identifying bugs, and suggesting improvements. Use when reviewing pull requests, auditing code changes, checking for security issues, or evaluating adherence to best practices. | tools: ABSENT | model: ABSENT. Checklist sections: Correctness; Security (input validation, authn/authz, secrets in code, SQLi/XSS/CSRF, dependency CVEs); Design & Architecture; Readability & Maintainability; Performance (O(n^2), N+1, pagination); Testing. Source repo: Claude-Code.

### content-strategist

`agent` · status `vendored`

Paths: `agents/content-strategist.md`

Claude Code sub-agent persona for messaging and positioning, content architecture, voice and tone, copy and microcopy, and content planning.

**Entry points**

- `copy agents/content-strategist.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/content-strategist.md (outside the repo)
- `claude --agent content-strategist`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- product and audience context
- existing content to review

**Outputs**

- value propositions and messaging frameworks (headline, subhead, supporting points, proof points)
- landing-page copy, CTAs, microcopy, error messages
- voice and tone definitions
- editorial calendars, content audits, repurposing plans

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Content review questions: who is it for; the one takeaway; does the structure support scanning; is there a clear next action; does it sound like 'us'

**Invoked by**

- user, via `claude --agent content-strategist` (README.md)

**Notes**

Frontmatter verbatim: name: content-strategist | description: Content strategist for bridging technical products and their audiences. Use when shaping messaging and positioning, structuring content systems, writing landing page copy, defining voice and tone, or planning content architecture. | tools: ABSENT | model: ABSENT. It defines voice itself and never references the brand_voice gate, which is unauthored. Source repo: Claude-Code.

### debugger

`agent` · status `vendored`

Paths: `agents/debugger.md`

Claude Code sub-agent persona for systematic debugging: reproduce, isolate, understand, fix the root cause, verify, and add a regression test.

**Entry points**

- `copy agents/debugger.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/debugger.md (outside the repo)
- `claude --agent debugger`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- exact error message
- steps to reproduce
- expected vs actual behaviour
- environment details

**Outputs**

- root-cause hypothesis verified by tracing the execution path
- minimal fix with explanation
- suggested regression test

**Reads**

- relevant code
- recent changes (git blame, recent changes, recent deployments)

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Reproduce first: 'If you can't reproduce it, you can't verify the fix'
- Verify completely: the original bug is fixed, no existing tests broke, related functionality still works, performance implications considered

**Invoked by**

- user, via `claude --agent debugger` (README.md)

**Notes**

Frontmatter verbatim: name: debugger | description: Expert debugging agent for analyzing errors, tracing execution, and fixing runtime bugs. Use when you need to investigate stack traces, identify root causes, inspect variable states, or step through logic to resolve issues. | tools: ABSENT | model: ABSENT. Bug patterns it checks: off-by-one, null/undefined access, race conditions, state management, type coercion, encoding, environment differences, dependency issues. Source repo: Claude-Code.

### documentation-writer

`agent` · status `vendored`

Paths: `agents/documentation-writer.md`

Claude Code sub-agent persona for READMEs, API docs, guides and tutorials, architecture docs, and code comments or docstrings.

**Entry points**

- `copy agents/documentation-writer.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/documentation-writer.md (outside the repo)
- `claude --agent documentation-writer`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- code to document
- target audience (end users / developers / ops)

**Outputs**

- README
- API documentation
- guides and tutorials
- architecture and design docs
- JSDoc/docstrings and 'why' comments

**Reads**

- the code being documented

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Procedure: read and understand the code -> identify the audience -> start with the highest-value doc type -> use real, working examples -> flag gaps or ambiguities

**Invoked by**

- user, via `claude --agent documentation-writer` (README.md)

**Notes**

Frontmatter verbatim: name: documentation-writer | description: Technical documentation specialist for writing docs people actually read and find useful. Use when writing READMEs, API docs, guides, tutorials, architecture docs, or improving inline code comments and docstrings. | tools: ABSENT | model: ABSENT. Writing standards: active voice, second person, front-load the answer, consistent terminology, structure for scanning, version-aware. Source repo: Claude-Code.

### frontend-developer

`agent` · status `vendored`

Paths: `agents/frontend-developer.md`

Claude Code sub-agent persona for clean, performant, accessible UI code (React/Vue/Svelte), state management, performance and accessibility.

**Entry points**

- `copy agents/frontend-developer.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/frontend-developer.md (outside the repo)
- `claude --agent frontend-developer`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- UI feature or component requirements
- the project's existing conventions

**Outputs**

- UI component code that handles loading, error and empty states
- frontend architecture review

**Reads**

- existing project code and conventions

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Match the project's existing conventions and patterns
- Handle loading, error and empty states for every async operation
- Touch targets at least 44x44px; respect user preferences (color scheme, reduced motion, font size)

**Invoked by**

- user, via `claude --agent frontend-developer` (README.md)

**Notes**

Frontmatter verbatim: name: frontend-developer | description: Senior frontend developer for writing clean, performant, accessible UI code. Use when building React/Vue/Svelte components, handling state management, optimizing performance, ensuring accessibility, or reviewing frontend architecture decisions. | tools: ABSENT | model: ABSENT. It mentions 'Design token usage' and 'No magic numbers' only in general terms. It does not reference css_html_ui ARTIFACT A or the brand gates the Router requires for UI skills. Source repo: Claude-Code.

### project-manager

`agent` · status `vendored`

Paths: `agents/project-manager.md`

Claude Code sub-agent persona for task breakdown, scope control, risk and dependency identification, status updates and planning.

**Entry points**

- `copy agents/project-manager.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/project-manager.md (outside the repo)
- `claude --agent project-manager`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- a feature, project or goal

**Outputs**

- task lists with relative complexity (small/medium/large), dependencies and sequencing
- status updates (done / in progress / blocked)
- decision logs and timelines in markdown
- risk lists with mitigations

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Flag tasks that need clarification or decisions before work can start
- Name scope creep explicitly

**Invoked by**

- user, via `claude --agent project-manager` (README.md)

**Notes**

Frontmatter verbatim: name: project-manager | description: Pragmatic technical project manager for breaking down work, tracking progress, and shipping on time. Use when decomposing features into tasks, managing scope, identifying risks and dependencies, or structuring status updates and planning sessions. | tools: ABSENT | model: ABSENT. Frameworks it mentions: MoSCoW, ICE scoring, effort/impact matrix. Source repo: Claude-Code.

### test-expert

`agent` · status `vendored`

Paths: `agents/test-expert.md`

Claude Code sub-agent persona for writing tests, reviewing existing tests for false confidence and brittleness, and advising on test strategy.

**Entry points**

- `copy agents/test-expert.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/test-expert.md (outside the repo)
- `claude --agent test-expert`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- code under test
- existing tests
- the project's test framework (Jest, Pytest, Vitest, Go testing, etc.)

**Outputs**

- tests in Arrange-Act-Assert / Given-When-Then form, named as behaviour specifications
- test review findings (false confidence, missing coverage, brittleness, slow tests, duplication)
- test strategy advice

**Reads**

- code and existing tests

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- Deterministic always: no flaky tests, no timing dependencies, no unmocked external services, no test-ordering dependencies

**Invoked by**

- user, via `claude --agent test-expert` (README.md)

**Notes**

Frontmatter verbatim: name: test-expert | description: Senior test engineer for improving test strategy, writing excellent tests, and reviewing test quality. Use when writing new tests, reviewing existing tests for false confidence or brittleness, or advising on testing strategy and coverage. | tools: ABSENT | model: ABSENT. Source repo: Claude-Code.

### ux-consultant

`agent` · status `vendored`

Paths: `agents/ux-consultant.md`

Claude Code sub-agent persona for reviewing UI components, flows and designs for accessibility, information architecture, interaction design and consistency.

**Entry points**

- `copy agents/ux-consultant.md into ~/.claude/agents/ (README.md; no install script)`
  - does: Installs the agent definition
  - changes: writes ~/.claude/agents/ux-consultant.md (outside the repo)
- `claude --agent ux-consultant`
  - does: Runs Claude Code as this agent. Stated in README.md only; unverifiable from repo
  - changes: nothing stated

**Inputs**

- UI components, flows, designs, or code viewed through its rendered output

**Outputs**

- usability findings prioritised by impact (blockers such as accessibility failures and broken flows before polish)

**Reads**

- UI code and designs

**Depends on**

- Claude Code CLI (`claude`)

**Gates and checkpoints**

- WCAG 2.1 AA minimum; contrast 4.5:1 for text and 3:1 for large text/UI elements; prefers-reduced-motion

**Invoked by**

- user, via `claude --agent ux-consultant` (README.md)

**Notes**

Frontmatter verbatim: name: ux-consultant | description: Senior UX consultant for catching usability problems and elevating experience quality. Use when reviewing UI components, flows, or designs for accessibility, information architecture, interaction design, and consistency issues. | tools: ABSENT | model: ABSENT. Its 4.5:1 and 3:1 figures match the text and non-text floors in color_science §4, but the agent file does not reference that gate. Source repo: Claude-Code.

### visual_identity (brand gate)

`context` · status `partial`

Paths: `context/brand/visual_identity.context.md`

L0-authored brand constant for interface identity: dark-ground instrumentation, flat grounds, hard rules, sharp corners, a closed four-accent state vocabulary, and elevation by inversion. An agent following Router.md loads it in full before running any skill it gates.

**Entry points**

- `Router.md §5 L0: 'context/brand/<name>.context.md exists. -> Load in full. Confidence 1.0. Done.'`
  - does: Satisfies the visual_identity slot in the Router §3 routing table. The agent follows the contract; no code reads the file
  - changes: nothing. The §6 attestation template line is '<name> L0 AUTHORED 1.00 context/brand/<name>.context.md'
- `python3 tools/verify_system.py (or --quiet for exit code only; exit 0 = consistent, 1 = at least one FAIL)`
  - does: check_brand_gates confirms that the dashboard.json authored flag matches the file on disk and that the path is context/brand/visual_identity.context.md. check_palette_parity compares bg, bg-raise, bg-panel, cyan, amber, alert and queued between skills/css_html_ui.skill.md ARTIFACT A and control_room.html. It does not read this file
  - changes: nothing (only prints). `--quiet` is the only argv flag

**Inputs**

- transcribed from skills/css_html_ui.skill.md ARTIFACT A (the token dictionary)
- DECISIONS.md D9; D10 (HARD MONO, from styles.csv -> brutalism + minimalism-and-swiss-style and google-fonts.csv -> JetBrains Mono)

**Outputs**

- §2 grounds: ground #000000 (page base, never a panel); raised #0B0B0B; panel #141414; line #383838 (rules, borders and dividers, never a fill); ink #FFFFFF; ink dim #9E9E9E. Separation is a rule, not a tone step. Gradients are off-limits. Light mode does not exist in the studio's own tooling
- §3 closed accent vocabulary: cyan #00E5FF = active/healthy/complete; amber #FFC400 = awaiting/review/warning; alert #FF3B30 = blocked/error/violation; queued #8A8AFF = queued/idle/disabled. Decorative colour is a violation. A readout (count, heading, label, link in prose) is not a state
- §4 structure: 12 columns, 16px gutter, 1440px max; new regions are grid areas; spacing steps 4/8/16/24/32px; radii 0; rules are 1px hairline, 2px for a panel's internal division, 2px in an accent for an element reporting a state; breakpoints tablet 980px, mobile 640px; control_room.html is the reference implementation
- §5 depth and motion: elevation is inversion (a solid accent fill with ground-coloured ink), for a live condition only; a standing caution takes a heavy accent rule instead. Motion is `width .12s linear` for fills and a `1.2s steps(1, end)` heartbeat blink; no easing, no hover transitions; motion.* tokens null out under prefers-reduced-motion. Focus is `2px solid #00E5FF` with a 2px offset, applied globally via :focus-visible
- §6 off-limits: raw hex/px or rgba() restatements in generated markup (derive with color-mix()); regressing the ARTIFACT A contrast_floor; a fifth accent or decorative accent use; light-mode surfaces; removing :focus-visible; shadow, glow or gradient elevation; non-zero radius; a second typeface or third weight; eased hover transitions; absolutely-positioned patches

**Reads**

- skills/css_html_ui.skill.md (ARTIFACT A, as source)
- control_room.html (reference implementation)

**Depends on**

- skills/css_html_ui.skill.md ARTIFACT A
- control_room.html
- DECISIONS.md D9/D10

**Gates and checkpoints**

- Mandatory gate for adobe_firefly, higgsfield_api, css_html_ui and ui_ux_intelligence (file header, Router.md §3, dashboard.json gates_skills)
- Conditional gate ('Also load if flagged in dashboard', Router.md §3) for adobe_suite_uxp and blender_python. No flag mechanism exists in dashboard.json or router.js
- Mutation policy: ARTIFACT A mutation_policy 'operator-approval only; agent proposes, never commits token changes'. skills/ui_ux_intelligence.skill.md is the declared regeneration path (D9), bound by its ARTIFACT D 4-step loop, and has no commit authority
- DECLARED GAP §7 'Unresolved': generated imagery (motifs, framing, texture) has no source. adobe_firefly and higgsfield_api get interface constraints only. Closure: (1) the operator authors §7, or (2) once 3 or more Content MDs of kind design or character carry imagery decisions, Router §5 L2 derives it, marked provisional. Until then a route needing imagery motifs must say so in its attestation

**Invoked by**

- agent executing Router.md §2-§6 (L0 load)
- router.js: renderContext and routeSkill. brandPath(role) = `context/brand/${role}.context.md`; authored state is read from dashboard.json; the UI reports L0 only
- tools/verify_system.py check_brand_gates (existence vs authored flag), run locally and in .github/workflows/verify.yml
- skills/adobe_firefly.skill.md (PAYLOAD BUILD composes the prompt from visual_identity vocabulary; VALIDATE checks against visual_identity constraints)
- skills/ui_ux_intelligence.skill.md ARTIFACT D step 2 DIFF against context/brand/*.context.md

**Notes**

README 'Must answer': 'What does work from this studio look like? Motifs, framing, texture, what is off-limits.' It answers interface look and off-limits; motifs, framing and texture are the declared §7 gap. The §1 routing glossary maps: surface/ground/panels/borders -> §2; colour meaning -> §3; layout/grid/spacing -> §4; glow/elevation/motion -> §5; off-limits -> §6; generated imagery -> §7 Unresolved. §0 says the file is 'machine-enforced by tools/verify_system.py -> check_palette_parity, which fails the build if control_room.html drifts from it'. That function checks only 7 hex tokens between ARTIFACT A and control_room.html. It never reads this file and checks nothing for line, ink, ink-dim, spacing, radius, motion or focus. context/brand/README.md lists this gate's skills as 'firefly, higgsfield, css_html_ui, suite_uxp*', omitting ui_ux_intelligence and blender_python*. Its sections are cited in comments in hub/styles.css (§3) and tools/brush-designer/styles.css (§4). Named in context_brand by vault/studio-os/ui/ui-ux-intelligence-integration.md and by the example note vault/_examples/example-stipple-brush.md (an underscore directory, ignored by ingest).

### typography_system (brand gate)

`context` · status `runs-today`

Paths: `context/brand/typography_system.context.md`

L0-authored brand constant for the studio's own surfaces: one family (JetBrains Mono) in two weights plus a single 500 step, a fixed six-step size scale, tracking values, and a hierarchy carried by weight, size, tracking and case (never colour).

**Entry points**

- `Router.md §5 L0: load context/brand/typography_system.context.md in full (confidence 1.0)`
  - does: Satisfies the typography_system slot in the Router §3 routing table. The agent follows the contract; no code reads the file
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "JetBrains Mono" --domain google-fonts`
  - does: Licence verification command given in §5, run against the vendored catalogue. argparse: positional query; --domain/-d choices = CSV_CONFIG keys (style, color, chart, landing, product, ux, typography, icons, gsap, react, web, google-fonts); also --stack/-s, --max-results/-n 1-20, --json, --full
  - changes: nothing. A plain domain search prints only; --persist writes design-system/<project-slug>/MASTER.md and takes effect only together with --design-system

**Inputs**

- transcribed from skills/css_html_ui.skill.md ARTIFACT A (font, type_scale)
- DECISIONS.md D9, D10
- tools/ui-ux-pro-max/data/google-font-licenses.json (licence record)
- tools/ui-ux-pro-max/data/google-fonts.csv (the wght 100..800 axis, per D10)

**Outputs**

- §2 family: display = `'JetBrains Mono', ui-monospace, monospace` at weight 800 (brand mark, headings, phase names, numerals); mono = the same stack at weight 400 (body, data, labels, logs). 500 is only for a status word that must out-weigh surrounding data. No second typeface and no third role. Mono is the body face. An un-tokened font-family is a protocol violation
- §3 scale: xs 10px, sm 11px, base 13px, md 14px, lg 20px, xl 30px (xl is the brand mark only, one per surface). Tracking: labels 0.18em, display 0.08em (tightened from 0.14em), brand 0.02em. ink-dim history: #6E7690 (3.78:1) -> #9AA4C0 (6.34:1) -> #9E9E9E (6.88:1 on panel)
- §4 hierarchy: display/xl -> display/lg -> display/md -> display/sm uppercase -> mono/base -> mono/sm dim -> mono/xs dim uppercase. Case is load-bearing: section labels, status words, phase names and controls are uppercase; prose and data are not
- §5 licensing: SIL OFL, embeddable. google-font-licenses.json records license OFL, date_added 2020-11-18, designers JetBrains / Philipp Nurullin / Konstantin Bulenkov, verifiedAt 2026-08-13. The variable wght axis runs 100..800
- §6 scope: governs only studio surfaces (control_room.html, hub/, anything HQ ships as its own interface), not product or client work. There, ui_ux_intelligence picks a pairing from typography.csv and persists it to that project's own design system

**Reads**

- skills/css_html_ui.skill.md (source)
- tools/ui-ux-pro-max/data/google-font-licenses.json (cited)

**Depends on**

- skills/css_html_ui.skill.md ARTIFACT A
- tools/ui-ux-pro-max/scripts/search.py (Python 3, stdlib)

**Gates and checkpoints**

- Mandatory gate for css_html_ui and ui_ux_intelligence (file header, Router.md §3, dashboard.json gates_skills)
- Conditional gate for adobe_firefly (Router.md §3 'if flagged in dashboard')
- An un-tokened font-family in generated CSS is a protocol violation (css_html_ui §0 anti-hallucination law)
- Mutation policy: operator-approval only. ui_ux_intelligence proposes and does not commit (D9, ARTIFACT D)
- Self-declared caveats (no formal 'Unresolved' section): no licence check has been run against a shipping artifact, so verify before a distributed binary embeds the font. The 10px/13px sizes sit below the 16px body minimum that ui_ux_intelligence returns from ux-guidelines.csv. The file declares that minimum not in force for studio surfaces, and routed tasks must not 'correct' toward it

**Invoked by**

- agent executing Router.md §2-§6
- router.js (L0 authored-flag display)
- tools/verify_system.py check_brand_gates (existence vs flag; local and CI)
- skills/ui_ux_intelligence.skill.md (cites typography_system §3 and §6; ARTIFACT D diff target)

**Invokes**

- tools/ui-ux-pro-max/scripts/search.py (as a documented verification command)

**Notes**

README 'Must answer': 'Typefaces, scale, tracking, hierarchy, licensing.' All five are answered (§2-§5). §1 routing glossary: typeface and weights -> §2; sizes/scale/tracking -> §3; hierarchy -> §4; licensing -> §5; product and client work -> §6. §0 says it is 'machine-enforced by tools/verify_system.py -> check_palette_parity', but that function checks only colour hex tokens and no typography value. context/brand/README.md lists this gate's skills as 'css_html_ui, firefly*', omitting ui_ux_intelligence. Status 'runs-today' means only that the file is authored and resolves at L0 for an agent. No code reads its content.

### color_science (brand gate)

`context` · status `partial`

Paths: `context/brand/color_science.context.md`

L0-authored brand constant: the complete 10-value studio palette, the semantic binding of the four accents to states, and three measured contrast floors. It explicitly declares that it is not a colour-managed pipeline.

**Entry points**

- `Router.md §5 L0: load context/brand/color_science.context.md in full (confidence 1.0)`
  - does: Satisfies the color_science slot in the Router §3 routing table (agent-followed contract)
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux`
  - does: Verification command that §4 says to run for any new colour pairing before it ships
  - changes: nothing (plain domain search; --persist applies only with --design-system)
- `python3 tools/verify_system.py`
  - does: check_palette_parity re-reads bg, bg-raise, bg-panel, cyan, amber, alert and queued from ARTIFACT A and FAILs if control_room.html's --<token> custom properties disagree. The file says 'Seven of the values below are re-verified on every run'
  - changes: nothing; exit 0 consistent / 1 any FAIL

**Inputs**

- transcribed from skills/css_html_ui.skill.md ARTIFACT A (color, semantic, contrast_floor)
- DECISIONS.md D10 (and the D9 addendum on the 2026-08-31 WCAG fixes)

**Outputs**

- §2 palette, 10 values ('there is no eleventh'): bg #000000 ground; bg-raise #0B0B0B; bg-panel #141414; line #383838 rule; ink #FFFFFF; ink-dim #9E9E9E; cyan #00E5FF nominal; amber #FFC400 waiting; alert #FF3B30 blocked; queued #8A8AFF idle. The three grounds sit within 8% of each other and are not a depth ladder
- §3 semantic binding: cyan->nominal, amber->waiting, alert->blocked, queued->idle. The same table as visual_identity §3; if they disagree, ARTIFACT A semantic.* is the tiebreak. 'Close enough' uses are violations
- §4 contrast floors: text 4.5:1 on all three grounds (worst: alert 5.19:1 on bg-panel; ink-dim 6.88:1; ink 18.42:1); non-text 3.0:1 on its own ground, including line (worst: alert on line 3.31:1); inversion 4.5:1 for ground ink on an accent fill (worst: bg on alert 5.92:1). HARD MONO vs 2026-08-31 on bg-panel: ink 18.42 (11.59), ink-dim 6.88 (6.34), cyan 11.98 (9.58), amber 11.53 (7.56), alert 5.19 (5.78), queued 6.28 (5.55); alert non-text on line 3.31 (3.39). Pushing alert toward #FF0000 (4.61:1 on bg-panel, 2.93:1 on line) fails the non-text floor

**Reads**

- skills/css_html_ui.skill.md (source)

**Depends on**

- skills/css_html_ui.skill.md ARTIFACT A contrast_floor and semantic.*
- tools/verify_system.py
- tools/ui-ux-pro-max/scripts/search.py

**Gates and checkpoints**

- Mandatory gate for adobe_firefly, adobe_suite_uxp and ui_ux_intelligence (file header, Router.md §3, dashboard.json gates_skills)
- Conditional gate for higgsfield_api (Router.md §3)
- Contrast floors are recorded in ARTIFACT A contrast_floor; any value that regresses one is rejected
- DECLARED GAP §5 'Unresolved': no working space, no LUTs, no grading rules, and no guidance for a linear EXR. The palette is sRGB hex UI tokens only. adobe_firefly and adobe_suite_uxp 'get a palette, not a colour pipeline'. A task needing a working space or grade marks it unresolved in its attestation. Closure: an operator decision (working space, delivery transform) or enough vault precedent. ui_ux_intelligence cannot supply it (colors.csv holds product palettes, not colour-management policy)

**Invoked by**

- agent executing Router.md §2-§6
- router.js (L0 authored-flag display)
- tools/verify_system.py check_brand_gates (existence) and check_palette_parity (7 values, via ARTIFACT A and control_room.html, not this file)
- skills/adobe_firefly.skill.md V2 palette lock 'per color_science context'
- skills/adobe_suite_uxp.skill.md V2 colour pipeline and the ARTIFACT curve line 'values from color_science context ONLY'

**Invokes**

- tools/ui-ux-pro-max/scripts/search.py (documented verification)

**Notes**

README 'Must answer': 'Working space, LUTs, palette with hex values, grading rules.' It answers only the palette with hex values; working space, LUTs and grading are the declared §5 gap. §1 routing glossary: palette/hex -> §2; meaning -> §3; contrast floors -> §4; working space/LUTs/grading -> §5 Unresolved. context/brand/README.md lists this gate's skills as 'firefly, suite_uxp, higgsfield*', omitting ui_ux_intelligence. Tension: adobe_suite_uxp.skill.md V2 states a 'studio default: export sRGB IEC61966-2.1 for web', while this file says no delivery transform is declared.

### unauthored brand gates (7)

`context` · status `specified-not-implemented`

Paths: `context/brand/motion_language.context.md`, `context/brand/sound_identity.context.md`, `context/brand/brand_voice.context.md`, `context/brand/narrative_continuity.context.md`, `context/brand/render_philosophy.context.md`, `context/brand/pipeline_ethics.context.md`, `context/brand/memory_discipline.context.md`, `context/brand/README.md`

Seven brand constants that Router.md §3 names as mandatory or conditional gates but that do not exist on disk (glob confirms; dashboard.json authored:false). Until they are authored, each resolves through the Router §5 vault ladder (L1 recall / L2 derivation) or, at L3, is asked about (manual/supervised) or parks the task (autonomous).

**Entry points**

- `Router.md §5 ladder: L1 query vault Content MDs whose frontmatter `context_brand` includes <name> and read `## Decisions in Force` (conf 0.9, cite note id); else L2 derive from at least 3 notes of related `kind`, weighting complete over in-progress and recent over old (conf 0.3-0.8, marked PROVISIONAL, cite every note); else L3 unresolved`
  - does: Resolves an unauthored gate at run time. It is an agent-followed contract; no code implements L1 or L2 (README.md: 'no code implements it'; router.js defers the ladder to the agent)
  - changes: the Content MD (`## Decisions in Force` for provisional constraints; on park, `## Next Steps` first item plus `status: blocked`) and the dashboard.json event_log (PARKED / PROVISIONAL with context name and Content MD path, §9)

**Inputs**

- vault/ Content MDs (frontmatter context_brand; section ## Decisions in Force)

**Outputs**

- motion_language must answer: 'Camera grammar, easing, shot lengths, transitions to avoid.'
- sound_identity must answer: 'Instrumentation, tempo range, mix targets, sonic signature.'
- brand_voice must answer: 'Diction, register, person, banned phrasings.'
- narrative_continuity must answer: 'Canon rules, character/environment persistence, what may not be retconned.'
- render_philosophy must answer: 'Quality bar, when to re-render vs. accept, output specs.'
- pipeline_ethics must answer: 'Disclosure, provenance, sourcing rules, what is never generated.'
- memory_discipline must answer: 'Quotable vs. summarizable, retention, what leaves the machine.'

**Reads**

- vault/**/*.md Content MDs (L1/L2; underscore-prefixed directories are ignored by ingest per vault/README.md)

**Depends on**

- Router.md §4-§6, §9, §10
- vault/SCHEMA.md (context_brand field)
- dashboard.json registries.context_brand_gates and system_status.mode

**Gates and checkpoints**

- motion_language: mandatory for higgsfield_api and blender_python
- sound_identity: mandatory for suno_audio
- brand_voice: mandatory for suno_audio and css_html_ui
- narrative_continuity: mandatory for higgsfield_api; conditional for suno_audio (Router §3 and README '*'). dashboard gates_skills lists only higgsfield_api
- render_philosophy: mandatory for adobe_suite_uxp, blender_python and hardware_compute
- pipeline_ethics: mandatory for hardware_compute; conditional for local_rag_orchestration (Router §3). README and dashboard gates_skills list it without the conditional marker
- memory_discipline: mandatory for local_rag_orchestration
- Mode gate (Router §5; mode from dashboard.json system_status.mode, currently 'autonomous'): L0/L1 proceed in all modes; L2 conf>=0.70 -> manual ask / supervised proceed-flag / autonomous proceed-flag; L2 conf<0.70 -> ask / ask / proceed provisionally, flag hard; L3 -> ask / ask / park. 'L3 halts in every mode'
- Router §10: never present a derived (L2) constraint as authored; never execute at L3
- Current resolution: vault/ holds one non-underscore Content MD (vault/studio-os/ui/ui-ux-intelligence-integration.md) whose context_brand is [visual_identity, typography_system, color_science]. None of the seven can resolve at L1, and fewer than 3 notes means no L2. All seven land at L3 and, in autonomous mode, park (consistent with dashboard.json blocked_reason and context_note)

**Invoked by**

- agent executing Router.md §2-§6
- router.js routeSkill: logs PARKED locally with 'not resolved at L0' for any non-authored gate; renderContext labels them 'not authored — §5 ladder, L3 parks'
- tools/verify_system.py check_brand_gates (asserts authored:false matches absence on disk)

**Notes**

README format rule: markdown with a routing glossary at the top to match context/domain/, then the substance. No minimum length; the Router only requires that the file exist and be readable. Authoring one promotes it to L0 and requires flipping dashboard.json registries.context_brand_gates[].authored to true (BOOT.md 'Why it still says BLOCKED'); check_brand_gates fails if the flag and the disk disagree. Routing consequences: css_html_ui cannot fully resolve at L0 because brand_voice is unauthored (DECISIONS.md D9: 'css_html_ui still parks on brand_voice'). suno_audio, higgsfield_api, blender_python, adobe_suite_uxp, hardware_compute and local_rag_orchestration each have at least one unauthored mandatory gate. Only adobe_firefly (visual_identity + color_science) and ui_ux_intelligence (all three authored gates) have every mandatory gate authored, subject to the declared gaps. vault/_migration/GAP-ANALYSIS.md (pre-D9) assesses the unmigrated 63-work Creative-Writing corpus: it could back brand_voice and narrative_continuity, memory_discipline weakly, and none of the others. It recommends authoring sound_identity and memory_discipline first, since each unblocks a skill outright. Skill files state some gate content inline without being gate sources: css_html_ui V2 ('Copy in UI follows brand_voice context: sentence case, plain verbs, controls named for what they do') and local_rag_orchestration V1 (memory_discipline defines quotable vs summarizable).

### brand-gate contract (context/brand/README.md)

`doc` · status `partial`

Paths: `context/brand/README.md`

Explains why context/brand/ exists and how it differs from context/domain/. Lists the ten required gate files (which skills each gates and what each must answer), the file format, and how routes run while gates are unauthored.

**Entry points**

- `read context/brand/README.md`
  - does: Human and agent reference for authoring gate files
  - changes: nothing

**Outputs**

- table of the 10 required files -> gated skills (short names; '*' = conditional, 'loaded only when flagged in dashboard.json') -> 'Must answer'
- format rule: markdown, routing glossary at top (match context/domain/), no minimum length
- behaviour until authored: resolved from the vault and marked provisional; only L3 (no file and no precedent) parks
- guidance: author a file when the same provisional constraint keeps being derived ('The system is telling you what it keeps having to guess'); authoring does not retroactively change past output

**Depends on**

- Router.md §3, §5

**Gates and checkpoints**

- '*' = conditional, loaded only when flagged in dashboard.json (no such flag exists in dashboard.json)

**Invoked by**

- referenced by Router.md §1/§3, README.md, BOOT.md, dashboard.json context_note, visual_identity §7, color_science/visual_identity provenance, the tools/verify_system.py check_brand_gates docstring, and vault/_migration/GAP-ANALYSIS.md

**Notes**

Stale in places. The header still reads 'Status: NOT YET AUTHORED' although three gates are authored. The gating table uses short skill names (firefly, higgsfield, suite_uxp, local_rag). It omits ui_ux_intelligence from visual_identity, color_science and typography_system, and omits blender_python* from visual_identity. It quotes Router '§7: refuses to invent context-file contents', but that text is not in Router.md: §7 is Content MD emission, and the only 'invent' wording is §0 ('invented is not allowed at all').

### ai_creative_strategies_context (domain library)

`context` · status `partial`

Paths: `context/domain/ai_creative_strategies_context.md`

General reference library on AI/LLM creative strategy: latent space, context windows, multi-model orchestration, prompting, hallucination, fine-tuning, evaluation, handoffs, intent alignment and agentic behaviour. Retrieval material only; never a brand gate.

**Entry points**

- `Jump to ## 2.A (glossary wording; heading on disk is '### 2.A', line 51)`
  - does: Latent Space Mapping & Navigation Engineering. Triggers: Embedding Space Geometry, Interpolation & Traversal, Semantic Direction Vectors, Dimensionality & Manifolds, Seed & Determinism Control, Concept Steering, Latent Blending & Mixing, Nearest-Neighbor Retrieval, Disentanglement, Out-of-Distribution Regions
  - changes: nothing
- `Jump to ## 2.B`
  - does: Context Window Optimization & Token Consolidation. Triggers: Token Budget Allocation, Context Compression, Chunking & Segmentation, Retrieval-Augmented Injection, Position & Recency Effects, Context Rot Mitigation, Summarization Buffers, Attention & Salience, Prompt Caching, Long-Context Degradation
  - changes: nothing
- `Jump to ## 2.C`
  - does: Multi-Model Chain Orchestration & Data Handoffs. Triggers: Sequential Model Pipelines, Specialist Model Routing, Output-to-Input Formatting, Intermediate Representation, Parallel & Ensemble Calls, Error Propagation Control, Latency & Cost Tradeoffs, Tool & Function Calling, Handoff Schema Contracts, Fallback & Retry Logic
  - changes: nothing
- `Jump to ## 2.D`
  - does: Prompt Engineering Synthesis & Meta-Instruction Logic. Triggers: Role & Persona Framing, Few-Shot Exemplars, Chain-of-Thought Prompting, Output Format Constraints, Negative & Exclusion Prompts, Decomposition & Task Splitting, Meta-Prompting & Self-Refinement, Delimiter & Structure Cues, Instruction Priority & Ordering, Temperature & Sampling Control
  - changes: nothing
- `Jump to ## 2.E`
  - does: Model Drift, Degeneracy, & Hallucination Mitigation. Triggers: Hallucination Detection, Grounding & Citation, Repetition & Degeneracy, Consistency & Self-Contradiction, Confidence Calibration, Verification & Fact-Checking, Drift Over Long Generation, Sampling-Induced Errors, Overconfidence Correction, Guardrail Consistency
  - changes: nothing
- `Jump to ## 2.F`
  - does: Dataset Curation, Fine-Tuning, & LORA Calibration Dynamics. Triggers: Data Quality & Cleaning, Labeling & Annotation, Fine-Tuning vs Prompting, LoRA & Adapter Methods, Hyperparameter Tuning, Overfitting & Regularization, Dataset Balance & Bias, Evaluation Split Design, Catastrophic Forgetting, Style & Domain Adaptation
  - changes: nothing
- `Jump to ## 2.G`
  - does: Generative Feedback Loops & Evaluation Frameworks. Triggers: Automated Evaluation Metrics, Human-in-the-Loop Review, LLM-as-Judge, Reward Modeling, Iterative Refinement Loops, Benchmark & Test Suites, A/B Output Comparison, Self-Consistency Checking, Rubric-Based Scoring, Regression & Drift Monitoring
  - changes: nothing
- `Jump to ## 2.H`
  - does: Model Handoff Context Preservation Strategies. Triggers: State Serialization, Summary & Memory Compression, Session Continuity, Context Reconstruction, Structured Handoff Documents, Key Fact Extraction, Reference & Pointer Passing, Versioned Context Snapshots, Cross-Session Persistence, Lossy vs Lossless Handoff
  - changes: nothing
- `Jump to ## 2.I`
  - does: Guardrail Bypass & Intent Alignment Calibration. Triggers: Intent Clarification, Alignment & Refusal Boundaries, Ambiguity Resolution, Safe Completion Framing, False-Positive Refusal Reduction, Steering Toward User Goal, Constraint Communication, Legitimate Use Verification, Value & Policy Consistency, Transparent Limitation Disclosure
  - changes: nothing
- `Jump to ## 2.J`
  - does: Emergent Agentic Behaviors & Autonomous Iteration Constraints. Triggers: Goal Decomposition & Planning, Tool Use & Environment Action, Self-Correction Loops, Termination & Stop Conditions, Resource & Cost Bounding, Memory & Scratchpad Use, Multi-Step Reasoning, Reflection & Critique, Autonomy Guardrails, Loop & Runaway Prevention
  - changes: nothing

**Inputs**

- user raw prompt keywords matched against the §1 Subcategory Triggers

**Outputs**

- §3 primary_domain_bias: 0.0 (neutral default; steered toward LatentSpace/Context/Orchestration/Prompting/Agentic)
- §3 system_exclusion_tokens: hallucination-unsupported-claim, context-rot, degenerate-repetition, over-refusal-false-positive, runaway-loop, catastrophic-forgetting, uncalibrated-overconfidence, unbounded-resource-use, lossy-critical-handoff, inconsistent-guardrail
- §3 hardware_render_overrides: target_temperature task-appropriate-low-factual-high-creative; target_context_strategy RAG-compress-chunk; target_grounding cited-verified; target_handoff structured-lossless-key-facts; target_agentic_bounds capped-iterations-confirmed-consequential-actions

**Gates and checkpoints**

- Never satisfies a Router §3 mandatory slot (Router.md §1/§3; router.js resolves only context/brand/; verify_system check_domain_libraries fails if a declared library path is also a gate path)

**Invoked by**

- agent retrieval under Router.md §1 ('the glossary exists so the agent can jump to the relevant theory')
- Content MD frontmatter context_domain (vault/SCHEMA.md optional field)

**Notes**

Structure (shared by all 10 libraries): §1 glossary lines 3-44 (A-J, 10 triggers each; the system note says 'exactly 10'); §2 at line 48 with a system note '15-20 words/node'; ### 2.A-2.J at lines 51, 67, 83, 99, 115, 131, 147, 163, 179, 195, each holding nodes 2.X.1-2.X.10 named after the triggers; §3 at line 211. The §2 headings match the §1 category names exactly. Registered in dashboard.json registries.context_domain_libraries. §3 says the payload is 'passed to corresponding .skill.md scripts', but no skill file names this library or any payload key.

### cinematic_videography_context (domain library)

`context` · status `partial`

Paths: `context/domain/cinematic_videography_context.md`

General reference library on cinematography: optics, sensors, lighting, colour science, blocking, camera movement, editing, auteur method, VFX, texture and noise. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Optics and Lens Physics. Triggers: Focal Length & FOV, Aperture & DOF, Lens Distortion & Aberration, Bokeh & Circle of Confusion, Anamorphic vs Spherical, Coatings & Flare, Focus Breathing & Pulling, Diffraction & Sharpness Falloff, Vintage vs Modern Character, Macro & Tilt-Shift
  - changes: nothing
- `Jump to ## 2.B`
  - does: Camera Form Factors & Sensor Technology. Triggers: Sensor Size & Crop Factor, Global vs Rolling Shutter, Dynamic Range & Latitude, RAW/LOG Pipelines, Frame Rate & Shutter Angle, Bit Depth & Chroma Subsampling, ND Filtration, Codec Compression, Large/Medium Format, Body Ergonomics & Rigs
  - changes: nothing
- `Jump to ## 2.C`
  - does: Lighting Math & Luminance Geometry. Triggers: Inverse-Square Falloff, Key/Fill/Back Ratios, Kelvin & Color Temp Mixing, Hard vs Soft Diffusion, Motivated vs Practical Sourcing, Volumetric Fog & Scattering, Bounce & Negative Fill, Contrast Ratio & Latitude, Three-Point vs Naturalistic, Gobos & Textured Shadow
  - changes: nothing
- `Jump to ## 2.D`
  - does: Color Science & Chromatic Emulation. Triggers: Gamut & Space Conversion, LUT Construction, Film Stock Emulation, Skin Tone Priority, Complementary & Split-Tone, Saturation & Vibrance Math, Highlight Rolloff & Shadow Crush, White Balance & Tint, Day-for-Night & Bleach Bypass, HDR vs SDR Mastering
  - changes: nothing
- `Jump to ## 2.E`
  - does: Scene Blocking & Composition Dynamics. Triggers: Rule of Thirds & Golden Ratio, Leading Lines, Depth Layering FG/MG/BG, Negative Space & Tension, Axis of Action & 180, Symmetry vs Asymmetry, Actor Blocking, Frame-Within-Frame, Eyeline Matching, Aspect Ratio Intent
  - changes: nothing
- `Jump to ## 2.F`
  - does: Camera Movement Mechanics. Triggers: Static vs Handheld, Dolly & Track, Crane & Jib Arcs, Steadicam & Gimbal, Whip Pans & Snap Zooms, Drone Choreography, Push-In/Pull-Out Psychology, Dutch Angle, Match-Move & Motion Control, Long Take & Oner
  - changes: nothing
- `Jump to ## 2.G`
  - does: Pacing & Temporal Editing Theory. Triggers: Cut Frequency & ASL, Continuity vs Jump Cut, Montage Theory, Match Cuts, J-Cut & L-Cut, Cross-Cutting, Slow Motion & Ramping, Freeze Frame, Rhythm to Music, Cold Open & Act Breaks
  - changes: nothing
- `Jump to ## 2.H`
  - does: Auteur Directorial Methodologies. Triggers: Visual Motif Repetition, Long-Take Philosophy, Genre Subversion, Recurring Collaborators, Thematic Obsession Mapping, Symbolic Color Coding, Dialogue Minimalism/Maximalism, Formal Constraint, Diegetic Blending, Tonal Consistency
  - changes: nothing
- `Jump to ## 2.I`
  - does: Practical vs. Digital VFX Integration. Triggers: Miniatures & Forced Perspective, Practical Pyrotechnics, Green/Bluescreen Keying, Digital Compositing Stacks, Mocap & Digital Doubles, Matte Painting, Rotoscoping, CG Lighting Match, Practical-First Bias, Grain & Plate Match
  - changes: nothing
- `Jump to ## 2.J`
  - does: Textural Artifacting & Noise Profiling. Triggers: Film Grain Structure, Chromatic Aberration Sim, Halation & Bloom, Lens Flare & Ghosting, Vignetting, Sensor Noise vs Grain, Compression Artifacting & Banding, Scan Damage, Dust & Emulsion Wear, Sharpening Halos & Aliasing
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Optics/Lighting/Color/Movement/Pacing)
- §3 system_exclusion_tokens: oversharpened, plastic-skin, uncanny-CG, flat-lighting, motion-smear-artifact, banding, aliased-edges, blown-highlights, crushed-blacks-unintentional, jello-shutter
- §3 hardware_render_overrides: target_bit_depth 10-16bit; target_gamut Rec.2020/DCI-P3; target_shutter_angle 180deg_default; target_grain_profile user-specified; target_codec highest-available-lossless-intermediate

**Gates and checkpoints**

- Never satisfies a §3 gate. context/brand/README.md: 'a treatise on cinematography says nothing about *your* brand'

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

Same 216-line structure as the other libraries; headings on disk are '### 2.X'. The §3 consumer is unspecified. Its 2.D (LUT, gamut, HDR) is general reference and cannot fill the color_science §5 gap, because domain libraries never satisfy gates (Router §3).

### classical_illustration_context (domain library)

`context` · status `partial`

Paths: `context/domain/classical_illustration_context.md`

General reference library on classical illustration: composition math, light and value, colour systems, anatomy, perspective, edges, traditional media, materials, line and atmospheric perspective. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Dynamic Symmetry & Compositional Mathematics. Triggers: Golden Ratio & Phi Grid, Root Rectangles, Rule of Thirds, Rabatment & Armature, Focal Point Placement, Visual Weight Balance, Directional Lines & Flow, Notan & Mass Distribution, Radial & Grid Systems, Cropping & Frame Ratio
  - changes: nothing
- `Jump to ## 2.B`
  - does: Light Physics, Value Scales, & Form Rendering. Triggers: Value Scale & Key, Light Logic & Terminator, Core Shadow & Occlusion, Reflected & Bounce Light, Cast Shadow Geometry, Specular Highlight, Form Modeling Planes, Chiaroscuro & Tenebrism, Local Value vs Light Value, Ambient Occlusion
  - changes: nothing
- `Jump to ## 2.C`
  - does: Color Systems, Harmonies, & Gamut Masking. Triggers: Hue-Value-Chroma Model, Color Temperature, Complementary & Analogous, Gamut Masking, Color Constancy & Adaptation, Atmospheric Color Shift, Simultaneous Contrast, Limited Palette Strategy, Color Mixing (Subtractive), Mood & Emotional Color
  - changes: nothing
- `Jump to ## 2.D`
  - does: Human Anatomy, Kinesiology, & Proportions. Triggers: Skeletal Landmarks, Muscle Groups & Insertion, Canonical Proportion, Gesture & Line of Action, Contrapposto & Weight, Foreshortening, Facial Anatomy & Planes, Hands & Feet Construction, Joint Mechanics & Range, Age & Body Type Variation
  - changes: nothing
- `Jump to ## 2.E`
  - does: Perspective Geometry & Spatial Depth. Triggers: One/Two/Three-Point, Horizon & Eye Level, Vanishing Points, Foreshortening & Convergence, Ellipse & Circle Projection, Curvilinear Perspective, Scale & Diminution, Overlap & Occlusion Depth, Grid & Floor Projection, Isometric & Axonometric
  - changes: nothing
- `Jump to ## 2.F`
  - does: Edge Control & Visual Focus Mechanics. Triggers: Hard vs Soft Edges, Lost & Found Edges, Focal Contrast Hierarchy, Depth of Field Emulation, Edge as Depth Cue, Rendering Restraint, Detail Concentration, Selective Sharpness, Silhouette Read, Edge Variety Rhythm
  - changes: nothing
- `Jump to ## 2.G`
  - does: Traditional Media Chemistry & Emulation. Triggers: Oil Paint Behavior, Watercolor & Transparency, Gouache Opacity, Graphite & Charcoal, Ink & Line Media, Pastel & Chalk, Fresco & Tempera, Impasto & Texture, Medium & Binder Chemistry, Substrate & Ground Prep
  - changes: nothing
- `Jump to ## 2.H`
  - does: Texture, Material, & Surface Reflection Logic. Triggers: Reflectance & Albedo, Specular vs Diffuse Surface, Metal Rendering, Skin & Subsurface Scatter, Fabric & Cloth Behavior, Glass & Transparency, Rough vs Smooth Texture, Wetness & Sheen, Fresnel & Grazing Angle, Material Weathering
  - changes: nothing
- `Jump to ## 2.I`
  - does: Stylistic Line Dynamics & Structural Draftsmanship. Triggers: Line Weight Variation, Contour & Cross-Contour, Gesture vs Structural Line, Hatching & Crosshatching, Line Economy, Constructive Drawing, Sight-Size Measuring, Rhythm & Flow Lines, Calligraphic Mark, Block-In & Refinement
  - changes: nothing
- `Jump to ## 2.J`
  - does: Atmospheric & Environmental Perspective Theory. Triggers: Aerial Perspective Fade, Value Compression by Distance, Chroma Reduction Depth, Warm-Cool Depth Shift, Edge Softening Distance, Atmospheric Scattering, Depth Layering Planes, Contrast Falloff, Light Diffusion & Haze, Sky-Ground Value Relationship
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Composition/Value/Color/Anatomy/Perspective)
- §3 system_exclusion_tokens: flat-lighting, muddy-color, broken-anatomy, tangent-edges, uniform-edge-treatment, inconsistent-light-source, wrong-perspective, oversaturated-distance, symmetry-error, floating-ungrounded-forms
- §3 hardware_render_overrides: target_value_structure readable-notan; target_light_logic consistent-single-or-defined; target_edge_hierarchy focal-priority; target_palette harmony-controlled; target_output layered-render-with-construction-underdrawing

**Gates and checkpoints**

- Never satisfies a §3 gate

**Invoked by**

- agent retrieval (Router.md §1)
- context_domain [classical_illustration] in the vault/SCHEMA.md frontmatter example and in vault/_examples/example-stipple-brush.md (an underscore directory, ignored by ingest and excluded from the verify_system note count)

**Notes**

Only §1 and the headings were read in full. The §3 consumer is unspecified.

### creative_analytical_writing_context (domain library)

`context` · status `partial`

Paths: `context/domain/creative_analytical_writing_context.md`

General reference library on narrative and analytical writing: macro structure, scene beats, character, dialogue, prose cadence, rhetoric, exposition, screenplay/Fountain format, emotional resonance and editing. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Global Macro-Narrative Structural Frameworks. Triggers: Three-Act Structure, Hero's Journey, Five-Act Freytag, Save the Cat Beats, Nonlinear/Fractured Timeline, Kishōtenketsu, Frame Narrative, In Medias Res, Braided/Multi-POV Structure, Circular/Recursive Form
  - changes: nothing
- `Jump to ## 2.B`
  - does: Micro-Scene Architecture & Structural Beats. Triggers: Scene Goal & Conflict, Value Charge Shift, Beat/Action Units, Scene-Sequel Pairing, Turning Point & Reversal, Entry & Exit Hooks, Setting as Pressure, Micro-Tension Threading, Time Compression, Scene Purpose Audit
  - changes: nothing
- `Jump to ## 2.C`
  - does: Character Psychology & Voice Profiling. Triggers: Want vs Need, Wound & Backstory, Ghost & Lie, Moral Complexity, Idiolect & Speech Signature, Arc Types, Interiority & Consciousness, Contradiction & Flaw, Agency & Decision, Foil & Contrast Mapping
  - changes: nothing
- `Jump to ## 2.D`
  - does: Dialogue Mechanics & Subtextual Layering. Triggers: Subtext & Withholding, Beat Attribution & Tags, On-the-Nose Avoidance, Rhythm & Interruption, Register & Diction Shift, Conflict Escalation, Exposition Concealment, Silence & Pause, Distinctive Cadence, Power Dynamics in Speech
  - changes: nothing
- `Jump to ## 2.E`
  - does: Pacing, Cadence, & Prose Syntax Dynamics. Triggers: Sentence Length Variation, Paragraph Rhythm, White Space & Density, Scene vs Summary, Tension Modulation, Syntactic Parallelism, Fragment & Run-On Intent, Sound & Prosody, Momentum & Drag Control, Chapter/Section Breaks
  - changes: nothing
- `Jump to ## 2.F`
  - does: Analytical Formats, Rhetoric, & Dialectics. Triggers: Thesis-Argument-Evidence, Ethos/Pathos/Logos, Dialectical Synthesis, Toulmin Model, Counterargument & Rebuttal, Syllogism & Deduction, Inductive Reasoning, Logical Fallacy Detection, Comparative Framework, Steelman & Charitable Reading
  - changes: nothing
- `Jump to ## 2.G`
  - does: Expository Logic & World Ingestion Prose. Triggers: Show vs Tell Calibration, Iceberg Withholding, Info-Dump Avoidance, Drip-Feed Revelation, Diegetic Exposition, Contextual Grounding, Sensory Anchoring, Concept Scaffolding, Reader Knowledge Modeling, Curiosity Gap Engineering
  - changes: nothing
- `Jump to ## 2.H`
  - does: Script Formatting Standards & Fountain Syntax. Triggers: Slugline & Scene Heading, Action Line Convention, Character Cue & Dialogue, Parenthetical Usage, Transitions, Fountain Markup, Dual Dialogue, Page-Per-Minute Rule, Shot & Camera Direction, Title Page & Metadata
  - changes: nothing
- `Jump to ## 2.I`
  - does: Emotional Resonance & Narrative Anchoring. Triggers: Empathy & Identification, Stakes Escalation, Catharsis Engineering, Dramatic Irony, Setup & Payoff, Emotional Whiplash Control, Universal Theme Anchor, Vulnerability Beats, Sensory Emotional Memory, Earned vs Cheap Emotion
  - changes: nothing
- `Jump to ## 2.J`
  - does: Editorial Iteration & Textual Optimization Protocols. Triggers: Line vs Developmental Edit, Redundancy Excision, Filter Word Removal, Active vs Passive Voice, Clarity & Concision Pass, Consistency & Continuity Check, Read-Aloud Cadence Test, Kill-Your-Darlings Triage, Structural Reordering, Voice Preservation
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Structure/Character/Dialogue/Analytical/Editorial)
- §3 system_exclusion_tokens: on-the-nose-dialogue, info-dump, filter-words, passive-voice-default, purple-prose, cliche-phrasing, unearned-emotion, head-hopping-POV, telling-over-showing, redundant-repetition
- §3 hardware_render_overrides: target_format prose/screenplay/analytical; target_POV user-specified; target_tense consistent; target_citation_style user-specified; target_output draft-with-revision-notes

**Gates and checkpoints**

- Never satisfies a §3 gate (it cannot stand in for brand_voice or narrative_continuity)

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

vault/_migration/GAP-ANALYSIS.md §3 says this library and world_building_context 'map plausibly' as context_domain for the 63 works in the external groot99-droid/Creative-Writing repo, and the other 8 do not. Those works have NOT been migrated ('Assessment only — no files have been migrated').

### digital_3d_motion_context (domain library)

`context` · status `partial`

Paths: `context/domain/digital_3d_motion_context.md`

General reference library on 3D and motion: PBR shading, topology, rigging, simulation, animation curves, virtual cameras, GI lighting, modelling workflows, compositing passes and real-time asset optimisation. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: PBR Shading Math & Rendering Algorithms. Triggers: BRDF & Energy Conservation, Metallic-Roughness Workflow, Specular-Glossiness Workflow, Fresnel & Grazing Reflectance, Microfacet Distribution, Albedo & Base Color, Normal & Bump Mapping, Ray Tracing vs Rasterization, Path Tracing & Monte Carlo, Subsurface Scattering
  - changes: nothing
- `Jump to ## 2.B`
  - does: Topology Optimization & Polygonal Flow. Triggers: Edge Loop Flow, Quad vs Triangle vs Ngon, Poles & Singularities, Deformation-Ready Topology, Subdivision Surface Prep, Retopology Workflow, Poly Density Distribution, UV-Aware Topology, Hard-Surface Support Loops, Manifold & Watertight Geometry
  - changes: nothing
- `Jump to ## 2.C`
  - does: Kinematic Systems, Rigging, & Deformations. Triggers: Skeletal Joint Hierarchy, Forward vs Inverse Kinematics, Skin Weighting & Falloff, Blend Shapes & Morphs, Control Rig & Constraints, Corrective & Driven Shapes, Deformer Stacks, Facial Rigging Systems, Spline & Ribbon Rigs, Muscle & Jiggle Systems
  - changes: nothing
- `Jump to ## 2.D`
  - does: Dynamic Simulations & Particle Physics. Triggers: Rigid Body Dynamics, Soft Body & Cloth, Fluid & Smoke Solvers, Particle Systems, Force Fields & Emitters, Collision Detection, Hair & Fur Dynamics, Fracture & Destruction, Constraint Networks, Cache & Bake Simulation
  - changes: nothing
- `Jump to ## 2.E`
  - does: Animation Curves, Interpolation, & Bezier Math. Triggers: Keyframe & Interpolation, Bezier & Tangent Handles, Ease In/Out & Spacing, Graph Editor & F-Curves, Twelve Principles, Timing & Spacing, Arcs & Trajectory, Overshoot & Follow-Through, Cycles & Loops, Motion Blur & Sampling
  - changes: nothing
- `Jump to ## 2.F`
  - does: Camera Rigging & Virtual Cinematography. Triggers: Focal Length & FOV, Depth of Field & Aperture, Camera Constraints & Path, Virtual Camera & Mocap, Framing & Composition, Camera Shake & Handheld Sim, Multi-Cam & Cuts, Lens Distortion Emulation, Match-Move & Tracking, Aspect Ratio & Sensor
  - changes: nothing
- `Jump to ## 2.G`
  - does: Lighting Environments & Global Illumination (GI). Triggers: Direct vs Indirect Light, HDRI & Image-Based Lighting, Area & Portal Lights, Bounce & Color Bleeding, Ambient Occlusion Pass, Caustics, Light Linking & Exclusion, Volumetric & Atmospheric, Three-Point CG Setup, Physical Light Units
  - changes: nothing
- `Jump to ## 2.H`
  - does: Hard-Surface vs. Organic Modeling Workflows. Triggers: Box vs Poly Modeling, Sculpting & Dynamesh, Boolean Operations, Bevel & Chamfer Logic, Curve & Surface (NURBS), Procedural & Parametric, Kitbashing & Assembly, Detail Sculpt & Layers, Panel & Seam Design, Symmetry & Radial Modeling
  - changes: nothing
- `Jump to ## 2.I`
  - does: Composite Pass Architecture & Motion Graphics Integration. Triggers: Render Pass & AOV, Node-Based Compositing, Cryptomatte & ID Mattes, Deep Compositing, Color Management (ACES), 2D-3D Integration, Motion Graphics Layering, Roto & Keying in Comp, 'Glow, Bloom, Lens FX', Multi-Pass Reassembly
  - changes: nothing
- `Jump to ## 2.J`
  - does: Asset Optimization & Universal Real-Time Pipelines. Triggers: LOD & Decimation, Texture Atlasing & Baking, Draw Call Reduction, glTF/USD Interchange, Normal Map Baking, Instancing & Batching, Shader Optimization, Poly Budget Management, Real-Time GI (Lumen/Baked), Cross-Platform Export
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Shading/Topology/Rigging/Simulation/Lighting)
- §3 system_exclusion_tokens: non-manifold-geometry, ngon-in-deformation, energy-non-conserving-shader, candy-wrapper-skinning, linear-interpolation-default, unmotivated-camera-shake, GI-fireflies, over-budget-polycount, baked-lighting-in-albedo, self-intersecting-mesh
- §3 hardware_render_overrides: target_renderer path-traced-or-realtime; target_color_space ACES; target_poly_budget platform-specific; target_texture_res power-of-two; target_export_format glTF/USD/FBX; target_frame_rate 24-60fps

**Gates and checkpoints**

- Never satisfies a §3 gate (it cannot stand in for motion_language or render_philosophy)

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

The §2.I trigger `Glow, Bloom, Lens FX` is one backticked label that contains commas. The §3 consumer is unspecified.

### multimedia_fusion_context (domain library)

`context` · status `partial`

Paths: `context/domain/multimedia_fusion_context.md`

General reference library on transmedia and interactive-media engineering: story distribution, interoperability, containers and codecs, real-time DOM logic, streaming, multi-sensory UX, state engines, cross-hardware deployment, telemetry and build pipelines. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Transmedia Storytelling Systems. Triggers: Narrative Distribution Across Media, Canon & Continuity Management, Platform-Native Story Fragments, Entry Point Design, World Bible & Story Guide, Audience Participation Layers, Cross-Media Reward Structures, Additive Comprehension, Franchise Ecosystem Logic, Story Migration & Handoff
  - changes: nothing
- `Jump to ## 2.B`
  - does: Cross-Platform Code & Interoperability Architectures. Triggers: API & Data Exchange, Framework Abstraction Layers, Platform-Agnostic Codebase, Web Standards & Compatibility, SDK & Library Integration, Version & Dependency Management, Middleware & Bridging, Progressive Enhancement, Feature Detection & Fallback, Native vs Hybrid Architecture
  - changes: nothing
- `Jump to ## 2.C`
  - does: Asset Containerization & File Type Standardization. Triggers: Container Format Standards, Codec Selection & Compatibility, Metadata Embedding, Lossless vs Lossy Encoding, Universal Interchange Formats, Asset Versioning, Compression & Optimization, Manifest & Bundle Structure, DRM & Rights Encoding, Cross-Platform File Validation
  - changes: nothing
- `Jump to ## 2.D`
  - does: Real-Time Interactive Logic & DOM Synchronization. Triggers: Event Loop & Async Handling, State Binding & Reactivity, DOM Diffing & Virtual DOM, WebSocket & Live Data, Input Handling & Debounce, Animation Frame Sync, Render Optimization, Client-Server State Sync, Latency Compensation, Concurrency & Race Conditions
  - changes: nothing
- `Jump to ## 2.E`
  - does: Streaming Mechanics & Optimization Frameworks. Triggers: Adaptive Bitrate Streaming, Buffering & Preload Strategy, CDN & Edge Distribution, Latency & Live Streaming, Codec & Transcoding Pipelines, Chunk & Segment Delivery, Bandwidth Detection, Progressive vs On-Demand, Quality of Service Metrics, Caching & Prefetch
  - changes: nothing
- `Jump to ## 2.F`
  - does: Multi-Sensory UI/UX Integration Protocols. Triggers: Visual-Audio Synchronization, Haptic Feedback Integration, Spatial & 3D Interfaces, Voice & Conversational UI, Gesture & Motion Input, Accessibility Multi-Modal, Cross-Sensory Consistency, Ambient & Peripheral Cues, Feedback Loop Design, Sensory Load Balancing
  - changes: nothing
- `Jump to ## 2.G`
  - does: Interactive State Engine Orchestration. Triggers: State Machine Architecture, Global vs Local State, Event-Driven Transitions, Persistence & Hydration, Undo/Redo & History, State Synchronization, Derived & Computed State, Side Effect Management, State Debugging & Inspection, Conflict Resolution Logic
  - changes: nothing
- `Jump to ## 2.H`
  - does: Cross-Hardware Media Deployment Scalability. Triggers: Device Capability Detection, Responsive & Adaptive Rendering, Performance Budgeting, GPU vs CPU Workload, Memory & Resource Management, Battery & Thermal Constraints, Screen & Resolution Scaling, Input Modality Adaptation, Graceful Degradation, Platform Store Compliance
  - changes: nothing
- `Jump to ## 2.I`
  - does: User Ingestion Metrics & Feedback Integration Loops. Triggers: Telemetry & Event Tracking, Session & Behavior Analytics, Heatmap & Interaction Mapping, A/B & Feature Flagging, Error & Crash Reporting, Feedback Collection Channels, Funnel & Retention Metrics, Real-Time Monitoring, Privacy-Compliant Tracking, Data-Driven Iteration Loop
  - changes: nothing
- `Jump to ## 2.J`
  - does: Automated Pipeline Asset Compilation & Assembly Rules. Triggers: Build System & Bundling, Dependency Resolution, Asset Transformation Pipeline, Minification & Tree-Shaking, Continuous Integration, Automated Testing Gates, Artifact Versioning & Tagging, Environment Configuration, Deployment Automation, Pipeline Caching & Incremental Build
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Transmedia/Interop/Streaming/State/Pipeline)
- §3 system_exclusion_tokens: platform-lock-in, blocking-synchronous-render, unhandled-race-condition, memory-leak, non-compliant-privacy-tracking, redundant-transmedia-content, unvalidated-asset, monolithic-state, manual-error-prone-deploy, degradation-total-failure
- §3 hardware_render_overrides: target_interchange_format open-standard-glTF/USD/JSON; target_streaming adaptive-bitrate; target_state_arch predictable-machine; target_build CI-automated-tested; target_deployment cross-platform-graceful-degradation

**Gates and checkpoints**

- Never satisfies a §3 gate

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

The §3 consumer is unspecified.

### music_ambience_context (domain library)

`context` · status `partial`

Paths: `context/domain/music_ambience_context.md`

General reference library on music and sound: harmony, rhythm, psychoacoustics, spatial audio, synthesis, acoustic instruments, foley and ambience, arrangement, leitmotif, and mixing and mastering. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Advanced Harmonic & Modal Theory. Triggers: Modal Interchange, Extended/Altered Voicings, Chromatic Mediants, Modes of Major Scale, Polytonality, Voice Leading & Counterpoint, Secondary Dominants, Pedal Points & Drone, Quartal/Quintal Harmony, Microtonality & Just Intonation
  - changes: nothing
- `Jump to ## 2.B`
  - does: Rhythmic Structures & Time Signatures. Triggers: Simple vs Compound Meter, Polyrhythm & Polymeter, Syncopation & Displacement, Odd Time Signatures, Groove Pocket & Swing, Metric Modulation, Ostinato & Rhythmic Cells, Tempo Rubato, Clave & Cross-Cultural Rhythm, Rhythmic Density & Layering
  - changes: nothing
- `Jump to ## 2.C`
  - does: Psychoacoustic Engineering. Triggers: Frequency Masking, Haas Effect & Precedence, Binaural Beats, Fletcher-Munson Loudness, Transient Perception, Spectral Balance & Masking, Auditory Streaming, Doppler Simulation, Perceived Warmth & Saturation, Ear Fatigue
  - changes: nothing
- `Jump to ## 2.D`
  - does: Spatial Audio & Soundstage Geometry. Triggers: Stereo Width & Panning, Binaural & HRTF, Ambisonics & 360 Audio, Reverb Decay & Room Model, Object-Based Audio (Atmos), Depth Placement, Surround Channel Architecture, Phase Coherence, Early Reflections, Elevation & Height Channels
  - changes: nothing
- `Jump to ## 2.E`
  - does: Synthesis & Signal Processing Dynamics. Triggers: Subtractive Synthesis, FM/Phase Modulation, Wavetable & Granular, ADSR Envelope, LFO Modulation, Compression & Dynamics, EQ Curves, Distortion & Saturation, Sidechain & Ducking, Modular Routing & CV
  - changes: nothing
- `Jump to ## 2.F`
  - does: Acoustic Instrumentation & Texturing. Triggers: String Timbre & Bowing, Woodwind Overtone & Breath, Brass Harmonic Series, Percussion Resonance & Damping, Piano Action & Pedaling, Extended/Prepared Techniques, Ensemble Blend, Solo vs Section Voicing, Cultural/Ethnic Timbres, Articulation & Dynamics
  - changes: nothing
- `Jump to ## 2.G`
  - does: Foley & Ambient Soundscapes. Triggers: Footstep & Material Foley, Environmental Bed & Room Tone, Weather Layers, Prop & Impact Design, Crowd & Walla, Mechanical/Industrial Textures, Biophonic & Wildlife, Silence & Negative Space, Field Recording, Layered Ambience Density
  - changes: nothing
- `Jump to ## 2.H`
  - does: Arrangement & Structural Archetypes. Triggers: Verse-Chorus-Bridge, Through-Composed, AABA Song Form, Buildup & Drop, Call-and-Response, Instrumentation Density Curve, Intro/Outro Framing, Variation & Development, Tension-Release Pacing, Cinematic Cue Timing
  - changes: nothing
- `Jump to ## 2.I`
  - does: Leitmotif & Melodic Development. Triggers: Motif Identity & Interval, Thematic Transformation, Melodic Contour, Sequence & Repetition, Countermelody, Character-Theme Mapping, Motivic Fragmentation, Diatonic vs Chromatic, Hook Construction, Foreshadowing & Callback
  - changes: nothing
- `Jump to ## 2.J`
  - does: Mixing & Mastering Reference Standards. Triggers: Gain Staging & Headroom, Spectrum Balance, Stereo Bus Processing, LUFS Loudness Standards, Reference Track Comparison, Multiband Compression, Stem Mixing & Print, Dithering & Bit-Depth, Platform Delivery Specs, A/B Translation Testing
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Harmony/Rhythm/Synthesis/Spatial/Mastering)
- §3 system_exclusion_tokens: muddy-low-mid, harsh-sibilance, over-compressed-pumping, phase-cancellation, clipping-distortion, unintentional-mono-collapse, ear-fatigue-frequencies, banding-in-reverb-tail, aliasing-artifacts, undefined-transients
- §3 hardware_render_overrides: target_sample_rate 48-96kHz; target_bit_depth 24-32bit-float; target_LUFS platform-specific; target_stereo_field full-width-mono-compatible; target_export_format lossless-stem-or-print

**Gates and checkpoints**

- Never satisfies a §3 gate (it cannot stand in for the unauthored sound_identity gate)

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

The §3 consumer is unspecified.

### social_media_marketing_context (domain library)

`context` · status `partial`

Paths: `context/domain/social_media_marketing_context.md`

General reference library on social media marketing: algorithms, consumer psychology, funnels, hooks and editing, analytics, community, copywriting, trends, influencers and the content lifecycle. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Algorithmic Dynamics & Platform Retentive Physics. Triggers: Ranking Signal Weighting, Watch Time & Retention, Engagement Velocity, Recommendation Systems, Reach vs Impressions, Shadow-Ban & Suppression, Feed vs Discovery Surfaces, Recency vs Evergreen Weighting, Platform-Specific Algorithms, Signal Gaming Risk
  - changes: nothing
- `Jump to ## 2.B`
  - does: Consumer Neuro-Psychology & Emotional Triggers. Triggers: Dopamine & Variable Reward, Emotional Arousal & Sharing, Social Proof & Bandwagon, Scarcity & FOMO, Curiosity Gap, Reciprocity & Commitment, Cognitive Bias Exploitation, Identity & Belonging, Loss Aversion Framing, Attention Bottleneck Physics
  - changes: nothing
- `Jump to ## 2.C`
  - does: Campaign Frameworks & Funnel Engineering. Triggers: TOFU-MOFU-BOFU Stages, Awareness to Conversion Path, Retargeting & Remarketing, Objective & KPI Mapping, Budget Allocation, Multi-Touch Attribution, Lead Magnet & Capture, Nurture Sequence Design, Full-Funnel Content Mix, Conversion Rate Optimization
  - changes: nothing
- `Jump to ## 2.D`
  - does: Multimedia Editing Optimization & Hook Design. Triggers: First-Three-Second Hook, Pattern Interrupt, Pacing & Cut Rhythm, Caption & Text Overlay, Aspect Ratio & Framing, Thumbnail Design, Audio & Trending Sound, Loop & Rewatch Design, Subtitle & Silent Viewing, Retention Curve Editing
  - changes: nothing
- `Jump to ## 2.E`
  - does: Analytics Ingestion & Performance Optimization Metrics. Triggers: Engagement Rate Calculation, Reach & Impression Metrics, Conversion & ROAS, Cohort & Retention Analysis, A/B & Multivariate Testing, Attribution Modeling, Vanity vs Actionable Metrics, Funnel Drop-Off Analysis, Benchmark & Baseline Setting, Dashboard & Reporting
  - changes: nothing
- `Jump to ## 2.F`
  - does: Community Architecture & Organic Engagement Loops. Triggers: Community Building Cadence, UGC & Co-Creation, Engagement Reply Strategy, Group & Forum Cultivation, Superfan & Advocate Nurture, Ritual & Recurring Format, Moderation & Norm Setting, Two-Way Dialogue Loops, Belonging & Identity Signaling, Retention & Reactivation
  - changes: nothing
- `Jump to ## 2.G`
  - does: Copywriting Dynamics & Micro-CTA Iterations. Triggers: Hook Headline Formulas, Benefit vs Feature Framing, Voice & Tone Calibration, CTA Verb & Urgency, Microcopy & Button Text, Story & Narrative Copy, Objection Preemption, Readability & Scannability, Emotional vs Rational Appeal, Copy Length Optimization
  - changes: nothing
- `Jump to ## 2.H`
  - does: Trend Sourcing, Vector Mapping, & Velocity Arbitrage. Triggers: Trend Detection Signals, Early vs Peak Entry Timing, Format & Sound Trends, Cultural Moment Alignment, Trend Adaptation vs Copying, Velocity & Decay Curves, Niche vs Mass Trend, Meme Mechanics, Cross-Platform Trend Migration, Newsjacking & Reactivity
  - changes: nothing
- `Jump to ## 2.I`
  - does: Influencer, Collab, & Distribution Node Mapping. Triggers: Tier & Reach Segmentation, Audience Fit & Alignment, Engagement Authenticity Audit, Collab Format Structures, Compensation & Deal Models, Distribution Network Effects, Cross-Promotion Mechanics, Whitelisting & Amplification, Relationship & Long-Term Partnership, Fraud & Fake Follower Detection
  - changes: nothing
- `Jump to ## 2.J`
  - does: Content Lifecycle Architecture & Evergreen Engineering. Triggers: Content Pillar Strategy, Repurposing & Atomization, Evergreen vs Timely Balance, Content Calendar & Cadence, Batch Production Workflow, Refresh & Update Cycles, Cross-Platform Adaptation, Archive & Resurfacing, Series & Format Systems, Lifecycle Performance Decay
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Algorithm/Psychology/Funnel/Hook/Analytics)
- §3 system_exclusion_tokens: clickbait-no-payoff, engagement-bait, vanity-metric-focus, manipulative-dark-pattern, platform-agnostic-crosspost, fake-follower-partnership, saturated-trend-copy, tone-deaf-newsjack, spammy-CTA, inauthentic-engagement
- §3 hardware_render_overrides: target_aspect_ratio platform-native; target_hook_window first-3-seconds; target_captions always-on-silent-optimized; target_metric_focus actionable-not-vanity; target_export multi-platform-adapted-variants

**Gates and checkpoints**

- Never satisfies a §3 gate

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

The §3 consumer is unspecified.

### typography_ad_arts_context (domain library)

`context` · status `partial`

Paths: `context/domain/typography_ad_arts_context.md`

General reference library on typography and advertising arts: grids, micro-typography, hierarchy, brand psychology, ad layout, signage, print production, interface ergonomics, type history and WCAG legibility. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Grid Geometry & Structural Frameworks. Triggers: Column & Modular Grids, Baseline Grid, Margins & Gutters, Golden Section Layout, Rule of Thirds & Focal Zones, Manuscript & Symmetrical Grid, Compound & Hierarchical Grids, Breaking the Grid, Responsive Grid Reflow, White Space & Negative Structure
  - changes: nothing
- `Jump to ## 2.B`
  - does: Micro-Typography, Kerning, & Glyphic Anatomy. Triggers: Glyph Anatomy Terms, Kerning & Pair Adjustment, Tracking & Letterspacing, Leading & Line Height, Ligatures & Alternates, Hyphenation & Justification, Widows & Orphans, Optical Alignment, x-Height & Cap Height, Rag & Rhythm Control
  - changes: nothing
- `Jump to ## 2.C`
  - does: Visual Hierarchy Scaling & Reading Paths. Triggers: Type Scale & Modular Ratio, Weight & Contrast Hierarchy, Reading Gravity & Z-Pattern, F-Pattern Scanning, Emphasis Techniques, Grouping & Proximity, Size & Position Priority, Color & Value Hierarchy, Entry Point & Flow, Information Layering
  - changes: nothing
- `Jump to ## 2.D`
  - does: Brand Psychology & Chromatic Identity. Triggers: Color Psychology Associations, Brand Palette Systems, Logo & Mark Design, Brand Voice & Tone, Consistency & Guidelines, Cultural Color Semiotics, Contrast & Accessibility Ratios, Emotional Resonance Mapping, Recognition & Recall, Identity System Scalability
  - changes: nothing
- `Jump to ## 2.E`
  - does: Advertising Design Systems & Layout Theory. Triggers: AIDA & Persuasion Structure, Headline & Body Hierarchy, Focal Image & Hero Shot, Call-to-Action Placement, Campaign Consistency, Copy-Visual Integration, Format & Media Adaptation, Balance & Tension Layout, Rule of Odds & Grouping, A/B Layout Testing
  - changes: nothing
- `Jump to ## 2.F`
  - does: Signage, Wayfinding, & Environmental Graphics. Triggers: Legibility at Distance, Directional & Identification Signage, Iconography & Pictograms, Contrast & Viewing Angle, Placement & Sightlines, Material & Durability, Multilingual & Universal Design, Wayfinding System Logic, Regulatory & ADA Standards, Environmental Scale Integration
  - changes: nothing
- `Jump to ## 2.G`
  - does: Print Production, Inks, & Material Finishes. Triggers: CMYK vs Spot Color, 'Bleed, Trim, & Safe Zone', Resolution & DPI, Paper Stock & Weight, Offset vs Digital Printing, Special Finishes (Foil/Emboss), Overprint & Trapping, Color Proofing & Calibration, Binding & Folding, Prepress & File Prep
  - changes: nothing
- `Jump to ## 2.H`
  - does: Digital Interface Ergonomics & Responsive Systems. Triggers: Responsive Breakpoints, Touch Target Sizing, Fitts's & Hick's Law, Component & Design Systems, Fluid Type & Spacing, Visual Feedback & States, Navigation Patterns, Cognitive Load Reduction, Cross-Device Consistency, Progressive Disclosure
  - changes: nothing
- `Jump to ## 2.I`
  - does: History of Type Design & Stylistic Movements. Triggers: Serif Classification, Sans-Serif Evolution, Type Anatomy Lineage, Movement Aesthetics, Metal to Digital Transition, Display vs Text Faces, Revival & Reinterpretation, Cultural Type Traditions, Variable Font Technology, Typeface Pairing Logic
  - changes: nothing
- `Jump to ## 2.J`
  - does: WCAG Accessibility Standards & Legibility Physics. Triggers: Contrast Ratio Thresholds, Minimum Type Size, Color-Blind Safe Palettes, Screen Reader Semantics, Focus & Keyboard Navigation, Text Spacing Requirements, Alt Text & Descriptions, Motion & Animation Safety, Readability Metrics, Reflow & Zoom Support
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Grid/Typography/Hierarchy/Brand/Accessibility)
- §3 system_exclusion_tokens: poor-contrast, orphans-widows, inconsistent-spacing, grid-violation-unintentional, illegible-small-type, color-only-encoding, misaligned-optical, cramped-margins, muddy-hierarchy, non-compliant-WCAG
- §3 hardware_render_overrides: target_color_mode CMYK-print/RGB-screen; target_resolution 300dpi-print/72-150dpi-screen; target_contrast WCAG-AA-minimum; target_grid modular-baseline-aligned; target_export print-ready-bleed/responsive-web

**Gates and checkpoints**

- Never satisfies a §3 gate (it cannot stand in for typography_system or visual_identity)

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain: vault/studio-os/ui/ui-ux-intelligence-integration.md (context_domain [typography_ad_arts]; context_brand [visual_identity, typography_system, color_science]; skills [ui_ux_intelligence, css_html_ui]; status in-progress). This is the only non-example Content MD in vault/

**Notes**

The §2.G trigger `Bleed, Trim, & Safe Zone` is one backticked label that contains commas. Its general 'Minimum Type Size' guidance is the kind of default that typography_system §3 declares not in force for studio surfaces.

### world_building_context (domain library)

`context` · status `partial`

Paths: `context/domain/world_building_context.md`

General reference library on worldbuilding: geopolitics, socio-economics, resources, anthropology, history and continuity, architecture, biomes, technology grounding, conlangs and factions. Retrieval material only.

**Entry points**

- `Jump to ## 2.A`
  - does: Geopolitical Mechanics & Power Distributions. Triggers: Sovereignty & Borders, Governance Systems, Power Balance & Hegemony, Diplomacy & Treaties, Warfare & Deterrence, Succession & Legitimacy, Espionage & Intelligence, Trade Blocs & Sanctions, Insurgency & Rebellion, Territorial Resource Contest
  - changes: nothing
- `Jump to ## 2.B`
  - does: Macro & Micro Socio-Economics. Triggers: Currency & Exchange Systems, Class Stratification, Labor & Production Modes, Supply & Demand Dynamics, Trade Routes & Logistics, Taxation & Redistribution, Market vs Command Economy, Debt & Credit Systems, Scarcity & Abundance Cycles, Informal & Black Markets
  - changes: nothing
- `Jump to ## 2.C`
  - does: Resource Distribution & Thermodynamic Constraints. Triggers: Energy Sources & Density, Water & Hydrological Cycles, Food Systems & Caloric Load, Material & Mineral Extraction, Carrying Capacity, Entropy & Waste Management, Renewable vs Finite Resources, Distribution Networks, Resource Curse Dynamics, Conservation Laws & Limits
  - changes: nothing
- `Jump to ## 2.D`
  - does: Anthropological Evolution & Cultural Heritage. Triggers: Kinship & Family Structure, Ritual & Rites of Passage, Myth & Cosmology, Taboo & Social Norms, Material Culture & Craft, Migration & Diaspora, Oral vs Written Tradition, Cultural Diffusion & Syncretism, Status & Prestige Systems, Foodways & Cuisine Identity
  - changes: nothing
- `Jump to ## 2.E`
  - does: Historical Timelines & Continuity Mapping. Triggers: Chronology & Dating Systems, Cause-Effect Event Chains, Golden Ages & Collapses, Foundational Myths & Origins, Dynastic & Regime Change, Technological Epoch Shifts, Continuity Consistency Audit, Alternate History Divergence, Recorded vs Lost History, Cyclical vs Linear Time Models
  - changes: nothing
- `Jump to ## 2.F`
  - does: Architectural Eras & Structural Philosophies. Triggers: Material & Construction Method, Vernacular & Climate Response, Monumental & Sacred Structures, Urban Planning & Density, Load-Bearing & Structural Logic, Ornamentation & Symbolism, Defensive Architecture, Infrastructure & Utilities, Ruins & Decay Layering, Stylistic Era Signatures
  - changes: nothing
- `Jump to ## 2.G`
  - does: Biome Ecosystems & Environmental Physics. Triggers: Climate Zones & Weather Systems, Flora & Vegetation Layers, Fauna & Food Webs, Geology & Landform Genesis, Hydrosphere & Ocean Currents, Atmospheric Composition, Ecological Succession, Biodiversity & Endemism, Natural Disaster Cycles, Human-Environment Interaction
  - changes: nothing
- `Jump to ## 2.H`
  - does: Technological & Scientific Grounding Paradigms. Triggers: Tech Level Consistency, Energy & Propulsion Systems, Communication & Information Tech, Medical & Biotech Capability, Materials Science Limits, Magic-as-System Rules, Automation & Computation, Scientific Method & Discovery, Tech Diffusion & Access, Unintended Consequence Modeling
  - changes: nothing
- `Jump to ## 2.I`
  - does: Language, Lexicons, & Nomenclature Systems. Triggers: Phonology & Sound Inventory, Morphology & Word Formation, Syntax & Grammar Rules, Naming Conventions, Writing Systems & Scripts, Dialect & Register Variation, Etymology & Loanwords, Idiom & Figurative Language, Language Evolution & Drift, Constructed Language Consistency
  - changes: nothing
- `Jump to ## 2.J`
  - does: Factional Ideologies & Institutional Systems. Triggers: Belief Systems & Doctrine, Institutional Hierarchy, Recruitment & Membership, Ideology vs Practice Gap, Schism & Reform, Symbols & Iconography, Enforcement & Orthodoxy, Inter-Factional Conflict, Founding & Legitimacy Narrative, Ritual & Organizational Culture
  - changes: nothing

**Inputs**

- user prompt keywords matched against the §1 triggers

**Outputs**

- §3 primary_domain_bias 0.0 (steered toward Geopolitics/Economics/Ecology/Technology/Culture)
- §3 system_exclusion_tokens: anachronism, tech-inconsistency, deus-ex-machina, unmotivated-faction, thermodynamic-violation, monoculture-flattening, arbitrary-conlang, isolated-acausal-history, resource-magic-handwave, single-biome-planet
- §3 hardware_render_overrides: target_consistency_check cross-reference-lore; target_scale macro-to-micro; target_causality cause-effect-chained; target_plausibility physics-grounded-or-ruled; target_output bible-entry-with-continuity-notes

**Gates and checkpoints**

- Never satisfies a §3 gate (it cannot stand in for narrative_continuity)

**Invoked by**

- agent retrieval (Router.md §1)
- Content MD context_domain

**Notes**

vault/_migration/GAP-ANALYSIS.md says this library 'maps plausibly' as context_domain for the 63 works in the external groot99-droid/Creative-Writing repo. They are unmigrated; the analysis is an assessment only.

## Usage flows

### Install and run a sub-executor agent

1. Copy agents/<name>.md into ~/.claude/agents/ (README.md lines 102-103). There is no install script; the repo has no .claude/agents/, and ~/.claude/agents/ does not exist on this machine
2. Run `claude --agent <name>` (README.md; flag unverifiable from repo), where <name> is one of business-analyst, code-reviewer, content-strategist, debugger, documentation-writer, frontend-developer, project-manager, test-expert, ux-consultant
3. The agent follows the procedure in its body (e.g. debugger: reproduce -> isolate -> understand -> fix -> verify). No tools or model are pinned in the frontmatter, and the agent does not load Router.md, the brand gates or the vault

### Brand-gate resolution for a routed skill (Router.md §2-§9)

1. Trigger A (intent pattern) or Trigger B (asset type, or a dashboard phase in awaiting_render/compositing/queued/blocked) fires; the agent HALTs (§2)
2. 1 MODE: read dashboard.json -> system_status.mode (currently 'autonomous') (§4)
3. 2 RESOLVE: look up the skill's mandatory contexts in the §3 table (mirrored by each skill header's `mandatory_context:` and by router.js resolveGates). Union them for multi-skill tasks. Conditional contexts load 'if flagged in dashboard' (no flag key exists)
4. 3 LADDER: for each context: L0 file context/brand/<name>.context.md exists -> load in full (1.0); L1 vault notes whose context_brand includes <name> -> ## Decisions in Force (0.9); L2 derive from >=3 related-kind notes (0.3-0.8, PROVISIONAL); L3 unresolved. For authored gates with declared gaps (visual_identity §7 imagery; color_science §5 working space/LUT/grade), treat the missing constraint as unresolved. Apply the mode gate; park at L3 (autonomous) or ask (manual/supervised)
5. 4 RECALL: locate or create the Content MD (from vault/_templates/content-md.md, status seed); read Overview, Next Steps, Decisions in Force and Method in full (§7)
6. 5 VERIFY: print the §6 ROUTER INTERCEPT attestation listing every §3 context with level, confidence and source (⚠ PROVISIONAL for L2) before any tool call
7. 6 STATE: confirm no phase conflict; write the phase -> in_progress
8. 7 EXECUTE: open the .skill.md and follow Prerequisites -> Execution Process -> Embedded Artifacts
9. 8 WRITEBACK: update the Content MD (Timeline append, Next Steps rewrite, Decisions in Force with derived ones marked, etc.), then dashboard.json plus an event_log entry. PARKED/PROVISIONAL/INTERCEPT_VIOLATION are logged with context name and Content MD path (§9)

### Author one of the seven unauthored gates (promote to L0)

1. Notice the same provisional constraint being derived repeatedly (context/brand/README.md: 'The system is telling you what it keeps having to guess'); GAP-ANALYSIS.md suggests sound_identity and memory_discipline first
2. Write context/brand/<name>.context.md: markdown, a routing glossary at the top matching context/domain/, then substance answering the README 'Must answer' column; no minimum length
3. Set dashboard.json registries.context_brand_gates[role=<name>].authored to true (BOOT.md 'Why it still says BLOCKED')
4. Run `python3 tools/verify_system.py`. check_brand_gates fails if the authored flag and the disk disagree, if the path is not context/brand/<role>.context.md, or if a gates_skills entry is not a registered skill. CI (.github/workflows/verify.yml) runs the same on push to main and on PRs
5. From then on routes resolve that constant at L0 (1.0); router.js stops logging PARKED for it. Past output is not retroactively changed

### Change an authored brand constant (visual_identity / typography_system / color_science)

1. ui_ux_intelligence ARTIFACT D: 1 GENERATE (`search.py "<studio brief>" --design-system --json`, no --persist); 2 DIFF against context/brand/*.context.md and css_html_ui ARTIFACT A; 3 IMPACT (which control_room.html values move; would check_palette_parity still pass); 4 PROPOSE to the operator and stop. Agents never commit (ARTIFACT A mutation_policy 'operator-approval only; agent proposes, never commits token changes')
2. The operator approves; the change lands in skills/css_html_ui.skill.md ARTIFACT A (the source of truth; semantic.* is the tiebreak) and ARTIFACT B
3. Transcribe the change into the affected gate file(s) and control_room.html (the reference implementation). DECISIONS.md D10 is the precedent (HARD MONO, 2026-09-01)
4. For colour pairings run `python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux` and confirm the three floors (text 4.5, non-text 3.0 including on line, inversion 4.5)
5. For typeface licensing run `python3 tools/ui-ux-pro-max/scripts/search.py "JetBrains Mono" --domain google-fonts`
6. Run `python3 tools/verify_system.py`. check_palette_parity fails on drift in bg, bg-raise, bg-panel, cyan, amber, alert or queued between ARTIFACT A and control_room.html. No other brand-gate value is machine-checked, and the gate files themselves are never parsed

### Retrieve theory from a domain library

1. Match the user's raw prompt keywords against the §1 'Subcategory Triggers' of a context/domain/*_context.md file
2. Jump to the target section named by the matching category (the glossary says '## 2.X'; the heading on disk is '### 2.X')
3. Read the nodes 2.X.1-2.X.10 there (one per trigger, 15-20 words each per the §2 system note)
4. Optionally take the §3 hand-off payload (primary_domain_bias, system_exclusion_tokens, hardware_render_overrides). The file says it is 'passed to corresponding .skill.md scripts', but no skill consumes it
5. Record the library in the Content MD frontmatter `context_domain: [<short name>]` (vault/SCHEMA.md optional field; examples use short names like typography_ad_arts). It never satisfies a Router §3 brand gate

## Relationships

| From | Relation | To |
|---|---|---|
| visual_identity (brand gate) | mandatory gate (Router.md §3, file header, dashboard gates_skills) | adobe_firefly |
| visual_identity (brand gate) | mandatory gate | higgsfield_api |
| visual_identity (brand gate) | mandatory gate | css_html_ui |
| visual_identity (brand gate) | mandatory gate | ui_ux_intelligence |
| visual_identity (brand gate) | conditional gate, 'if flagged in dashboard' (Router.md §3); no flag mechanism exists | adobe_suite_uxp |
| visual_identity (brand gate) | conditional gate (Router.md §3) | blender_python |
| color_science (brand gate) | mandatory gate | adobe_firefly |
| color_science (brand gate) | mandatory gate | adobe_suite_uxp |
| color_science (brand gate) | mandatory gate | ui_ux_intelligence |
| color_science (brand gate) | conditional gate (Router.md §3) | higgsfield_api |
| typography_system (brand gate) | mandatory gate | css_html_ui |
| typography_system (brand gate) | mandatory gate | ui_ux_intelligence |
| typography_system (brand gate) | conditional gate (Router.md §3) | adobe_firefly |
| unauthored brand gates (7) | motion_language and narrative_continuity are mandatory gates | higgsfield_api |
| unauthored brand gates (7) | motion_language and render_philosophy are mandatory gates | blender_python |
| unauthored brand gates (7) | sound_identity and brand_voice mandatory; narrative_continuity conditional | suno_audio |
| unauthored brand gates (7) | brand_voice mandatory gate (D9: css_html_ui 'still parks on brand_voice') | css_html_ui |
| unauthored brand gates (7) | render_philosophy mandatory gate | adobe_suite_uxp |
| unauthored brand gates (7) | pipeline_ethics and render_philosophy mandatory gates | hardware_compute |
| unauthored brand gates (7) | memory_discipline mandatory; pipeline_ethics conditional per Router §3 (listed plainly in README and dashboar… | local_rag_orchestration |
| visual_identity (brand gate) | transcribed from; ARTIFACT A is the source of truth | skills/css_html_ui.skill.md ARTIFACT A |
| typography_system (brand gate) | transcribed from (font, type_scale) | skills/css_html_ui.skill.md ARTIFACT A |
| color_science (brand gate) | transcribed from; ARTIFACT A semantic.* is the tiebreak; contrast_floor recorded there | skills/css_html_ui.skill.md ARTIFACT A |
| skills/ui_ux_intelligence.skill.md ARTIFACT D | declared regeneration path (D9); 4-step GENERATE/DIFF/IMPACT/PROPOSE loop; proposes only, operator commits (a… | visual_identity (brand gate) |
| ui_ux_intelligence | selects product/client typography from typography.csv, outside this gate's scope (§6) | typography_system (brand gate) |
| color_science (brand gate) | duplicates the §3 semantic accent table deliberately; they must not drift | visual_identity (brand gate) |
| typography_system (brand gate) | defers 'colour is state' to visual_identity §3; visual_identity §6 forbids a second typeface or third weight… | visual_identity (brand gate) |
| visual_identity (brand gate) | reference implementation of the identity | control_room.html |
| hub/styles.css | comment cites visual_identity §3; hub/ is a studio surface governed by typography_system §6 | visual_identity (brand gate) |
| tools/brush-designer/styles.css | comment cites visual_identity §4 | visual_identity (brand gate) |
| skills/adobe_suite_uxp.skill.md | V2 colour pipeline says 'studio default: export sRGB IEC61966-2.1 for web', and its curve artifact takes 'val… | color_science (brand gate) |
| skills/adobe_firefly.skill.md | PAYLOAD BUILD composes the prompt from visual_identity vocabulary; VALIDATE checks visual_identity constraint… | visual_identity (brand gate) |
| skills/css_html_ui.skill.md | V2 states brand_voice rules inline ('sentence case, plain verbs, controls named for what they do') while the… | unauthored brand gates (7) |
| skills/local_rag_orchestration.skill.md | V1: memory_discipline defines quotable vs summarizable; load it before writing any answer | unauthored brand gates (7) |
| tools/verify_system.py | check_palette_parity verifies 7 of its 10 hex values (via ARTIFACT A vs control_room.html, not by reading the… | color_science (brand gate) |
| tools/verify_system.py | check_brand_gates asserts authored flag == file on disk, path = context/brand/<role>.context.md, and gates_sk… | unauthored brand gates (7) |
| tools/verify_system.py | check_domain_libraries: FAIL if a dashboard-declared library is missing or doubles as a gate path; WARN only… | ai_creative_strategies_context (domain library) |
| .github/workflows/verify.yml | runs it on push to main, on pull_request and on workflow_dispatch; also runs --quiet under -W error::Encoding… | tools/verify_system.py |
| typography_system (brand gate) | licence verification: search.py "JetBrains Mono" --domain google-fonts | tools/ui-ux-pro-max/scripts/search.py |
| color_science (brand gate) | contrast verification: search.py "contrast ratio text legibility" --domain ux | tools/ui-ux-pro-max/scripts/search.py |
| router.js | brandPath(role) resolves gates to context/brand/<role>.context.md; a hard-coded resolveGates table mirrors th… | visual_identity (brand gate) |
| Router.md | §1/§3 point readers to it for gate authoring | brand-gate contract (context/brand/README.md) |
| BOOT.md | 'Why it still says BLOCKED' gives the authoring procedure (write the file, flip the authored flag); its gate-… | unauthored brand gates (7) |
| Router.md | §1/§3: domain libraries are retrieval material and never satisfy a mandatory slot (applies to all 10) | typography_ad_arts_context (domain library) |
| vault Content MD frontmatter context_brand | L1 lookup key for recalling ## Decisions in Force; no current note names any of the seven | unauthored brand gates (7) |
| vault/studio-os/ui/ui-ux-intelligence-integration.md | context_domain reference (the only real Content MD) | typography_ad_arts_context (domain library) |
| vault/_examples/example-stipple-brush.md | context_domain reference in an example note (underscore directory, ignored by ingest) | classical_illustration_context (domain library) |
| vault/_migration/GAP-ANALYSIS.md | assesses the unmigrated Creative-Writing corpus as able to back brand_voice and narrative_continuity; recomme… | unauthored brand gates (7) |
| ai_creative_strategies_context (domain library) | §3 hand-off payload 'passed to corresponding .skill.md scripts'; no skill file names any library or payload k… | skills/*.skill.md |
| README.md | documents install (copy to ~/.claude/agents/) and invocation (`claude --agent <name>`) for all 9 agents; sour… | business-analyst |
| frontend-developer | no link: the agent does not reference ARTIFACT A or the brand gates even though it covers the same UI domain | css_html_ui |

**Open questions the files could not settle**

- The agent frontmatter declares no `tools` and no `model`. The repo does not say which tool set or model applies when they run, and the `claude --agent` flag is asserted only in README.md.
- Which .skill.md is the 'corresponding' consumer of each domain library's §3 hand-off payload? No skill file names any library or payload key, and no mapping is defined.
- Router §3 and context/brand/README.md say conditional contexts load 'if flagged in dashboard', but no flag or conditional key exists in dashboard.json, router.js (whose resolveGates has mandatory columns only) or the skill headers. How is a conditional gate flagged?
- The gate-to-skill tables disagree. context/brand/README.md omits ui_ux_intelligence for visual_identity, color_science and typography_system, and omits blender_python* for visual_identity. dashboard.json gates_skills includes one conditional binding (pipeline_ethics -> local_rag_orchestration) but omits all the others (narrative_continuity -> suno_audio, visual_identity -> adobe_suite_uxp/blender_python, color_science -> higgsfield_api, typography_system -> adobe_firefly). Router.md §3 appears to be the authority, but this is not stated.
- visual_identity §0 and typography_system §0 say they are machine-enforced by check_palette_parity, but the function checks only 7 colour hex tokens and never reads a gate file. Is enforcement intended for typography, spacing, radius, motion, focus, line, ink or ink-dim values, or for parity between the gate files and ARTIFACT A?
- Stale gate-state text: BOOT.md ('None is authored', state BLOCKED), README.md lines 119-121 and 158-159, GAP-ANALYSIS.md §6, and the check_brand_gates docstring predate D9. dashboard.json (state DEGRADED, 3 authored) matches the files on disk. Will these documents be updated?
- context/brand/README.md quotes Router '§7: refuses to invent context-file contents'. That text is not in the current Router.md (§7 is Content MD emission; §0 says 'invented is not allowed at all'). Was the reference simply not updated?
- Does adobe_suite_uxp V2's 'studio default: export sRGB IEC61966-2.1 for web' count as a declared delivery transform? color_science §5 says none exists.
- skills/css_html_ui.skill.md P3 and adobe_firefly V2 read dashboard.json active_variables.master_palette, which does not exist in the current dashboard.json (active_variables holds only content_md, resolved_context and provisional_constraints). Is that palette check dead?
- Do inline brand_voice rules in css_html_ui V2 ('sentence case, plain verbs...') count as a source for the unauthored brand_voice gate? Router §5 recognises only an authored file or vault Content MDs.
- The domain library §2 node texts were not read beyond one sample (ai_creative 2.A); per scope, only headings were verified. Node-level usage details are not captured.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: check_domain_libraries 'requires every context/domain/*_context.md to exist and never be declared as a gate' (cross_links, tools/verify_system.py -> ai_creative_strategies_context)
  - evidence: tools/verify_system.py lines 104-119: it FAILs only if a path in dashboard registries.context_domain_libraries is missing on disk, or if a declared library path equals a gate path. A library on disk but not declared only WARNs. check_protocol_files merely counts *_context.md files for an OK message.
- **corrected**: vault/_migration/GAP-ANALYSIS.md says creative_analytical_writing and world_building 'map plausibly onto the 63 migrated notes'
  - evidence: GAP-ANALYSIS.md lines 3-5: the 63 works are in the external repo groot99-droid/Creative-Writing, and it is 'Assessment only — no files have been migrated'. Line 107 is the context_domain row. vault/ holds only one non-underscore Content MD.
- **corrected**: Open question: dashboard.json context_note ('still park at L3 per §5') contradicts Router.md §3/§5 and context/brand/README.md
  - evidence: dashboard.json system_status.blocked_reason says 'vault/ holds 1 Content MD, which is below the >=3 L2 needs'. The only real note (vault/studio-os/ui/ui-ux-intelligence-integration.md) has context_brand [visual_identity, typography_system, color_science], so none of the seven gates resolves at L1 or L2 and all land at L3. That is consistent with Router §5 and matches the vault on disk. The stale documents are BOOT.md lines 156-161 ('None is authored', state BLOCKED), README.md lines 119-121 ('The ten context/brand/ constants are still unauthored') and 158-159 ('all ten gates reported as pending and the state declared BLOCKED'), GAP-ANALYSIS.md §6 line 186, and the verify_system.py check_brand_gates docstring. dashboard state is DEGRADED.
- **corrected**: search.py verification commands in the gate files 'mutate nothing without --persist'
  - evidence: tools/ui-ux-pro-max/scripts/search.py lines 121-171: persist= is passed only inside the `if args.design_system:` branch. A plain `--domain` search (the form both gate files document) only prints, whether or not --persist is given.
- **corrected**: Domain library sections are at '## 2.A' ... '## 2.J' (entry_point commands and flow)
  - evidence: The glossary text literally says 'Jump to ## 2.A' (e.g. ai_creative_strategies_context.md line 7), and Router.md §1 also says '## 2.A … ## 2.J'. But the actual headings on disk in all ten files are level-3 '### 2.A' ... '### 2.J' at lines 51, 67, ..., 195. Commands are kept verbatim with a note.
- **corrected**: Brand-gate resolution flow: resolve ladder -> print attestation -> execute -> writeback
  - evidence: Router.md §2 intercept sequence: 1 MODE, 2 RESOLVE, 3 LADDER (+ mode gate; park at L3), 4 RECALL (locate/create the Content MD; read Overview, Next Steps, Decisions in Force, Method in full), 5 VERIFY (attestation before any tool call), 6 STATE (confirm no phase conflict; write phase -> in_progress), 7 EXECUTE, 8 WRITEBACK. The inventory flow omitted RECALL and STATE.
- **corrected**: Summary: 'At L3 (nothing found) the task parks'
  - evidence: Router.md §5 mode gate table: L3 -> manual 'ask', supervised 'ask', autonomous 'park'. The prose says 'L3 halts in every mode'. dashboard.json system_status.mode is 'autonomous', so today L3 parks.
- **corrected**: Content MDs record which libraries they used in context_domain 'per vault/SCHEMA.md'
  - evidence: vault/SCHEMA.md lines 58 and 70 only list context_domain as an optional frontmatter field, with the example [classical_illustration]. No semantics are defined.
- **corrected**: typography_system §5: google-font-licenses.json records ... 'variable wght axis 100..800'
  - evidence: google-font-licenses.json lines 7495-7506 hold name, license OFL, date_added 2020-11-18, designers, status and verifiedAt 2026-08-13, but no axis data. DECISIONS.md D10 line 495 attributes 'wght: 100..800' to google-fonts.csv.
- **corrected**: frontend-developer gate: 'respect prefers-reduced-motion and color scheme'
  - evidence: agents/frontend-developer.md line 52: 'Respects user preferences (color scheme, reduced motion, font size)'.
- **added**: verify_system.py: only '--quiet' flag noted
  - evidence: tools/verify_system.py docstring lines 10-13: `python3 tools/verify_system.py` (human output), `--quiet` (exit code only); 'Exit 0 = consistent, 1 = at least one FAIL'. .github/workflows/verify.yml runs it on push to main, on pull_request and on workflow_dispatch, plus `python3 -W error::EncodingWarning tools/verify_system.py --quiet`.
- **added**: Machine checks limited to check_brand_gates, check_domain_libraries, check_palette_parity
  - evidence: tools/verify_system.py also runs checks touching gates: check_skill_headers (every skills/*.skill.md mandatory_context names a declared gate role), check_context_loaded (system_status.context_loaded may name only authored gates), check_router_md (WARN if a role is not backticked in Router.md), and check_router_js (router.js must read STATE?.registries?.context_brand_gates, must build context/brand/ and never context/domain/ paths, WARN if a role is missing).
- **added**: router.js reads gate state only from dashboard.json
  - evidence: router.js lines 295-308 carry a hard-coded resolveGates table (skill -> mandatory gates, no conditional column) mirroring Router.md §3. Only the authored flag comes from dashboard.json (isAuthoredL0, lines 315-318). The verify_system.py check_router_js docstring says router.js 'must not carry a second, divergent copy of the binding map', but it only WARNs on missing role names and does not compare the table.
- **added**: Regeneration path for the authored gates described only as 'ui_ux_intelligence proposes'
  - evidence: skills/ui_ux_intelligence.skill.md ARTIFACT D (lines 241-260): 1 GENERATE (--design-system against the studio brief, --json, no --persist); 2 DIFF against context/brand/*.context.md AND css_html_ui ARTIFACT A; 3 IMPACT (every control_room.html value that would move; would check_palette_parity still pass); 4 PROPOSE to the operator and stop. Writing the gate files, css_html_ui.skill.md or control_room.html without step 4 is an intercept violation.
- **added**: Authored-gate entries do not state the README 'Must answer' columns
  - evidence: context/brand/README.md lines 39-41: visual_identity 'Motifs, framing, texture, what is off-limits'; color_science 'Working space, LUTs, palette with hex values, grading rules'; typography_system 'Typefaces, scale, tracking, hierarchy, licensing'. These are now recorded in each entry with coverage against the declared gaps.
- **added**: No analysis of which unauthored gates vault precedent could serve
  - evidence: vault/_migration/GAP-ANALYSIS.md §6 (lines 190-203, 275-277): the Creative-Writing corpus could serve brand_voice and narrative_continuity, memory_discipline weakly, and none of the others. It recommends authoring sound_identity and memory_discipline first. The document predates D9 (it says all 10 gates are unauthored and there are 8 skills).
- **added**: Consumers of the authored gates limited to Router/router.js/verify_system
  - evidence: hub/styles.css line 330 cites visual_identity §3; tools/brush-designer/styles.css line 40 cites visual_identity §4; skills/adobe_firefly.skill.md lines 59/66/72 use the visual_identity and color_science contexts; skills/adobe_suite_uxp.skill.md lines 76/161 use color_science (including a 'studio default: export sRGB IEC61966-2.1 for web' that color_science §5 does not declare); skills/css_html_ui.skill.md V2 line 66 states brand_voice rules inline; skills/local_rag_orchestration.skill.md line 125 uses memory_discipline.
- **added**: Agents never installed (open question)
  - evidence: Read-only check on this machine: the ~/.claude/agents directory does not exist, and the repo has only .claude/launch.json (no .claude/agents/). No file other than README.md and Router.md §1 mentions the agent names or `claude --agent`.
- **unverifiable**: `claude --agent <name>` invokes an agent
  - evidence: The only source is README.md lines 102-103. No repo file defines or exercises this CLI flag; it is kept with a note.
- **added**: vault/_examples/example-stipple-brush.md is a Content MD that uses classical_illustration
  - evidence: It does carry context_domain [classical_illustration] and context_brand [visual_identity], but vault/README.md line 21 says 'Directories prefixed `_` are ignored by ingest', and verify_system.py check_context_loaded excludes underscore directories from the note count. It is an example, not precedent.
