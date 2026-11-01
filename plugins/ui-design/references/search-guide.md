# Search guide (ui-design-catalog, on demand)

Detail the `ui-design-catalog` skill reads when a task needs it. The skill body keeps the
workflow and the query contract; this file holds the options.

## Persisting: page overrides, --force, retrieval

With a page-specific override, add `--page "dashboard"` to also create `design-system/<project-slug>/pages/dashboard.md`. If Master already exists, a new page file is created without changing Master; an existing page file is skipped unless `--force` is explicitly authorized.

If `design-system/<project-slug>/MASTER.md` already exists, `--persist` **skips writing and leaves it untouched** unless you also pass `--force` — check whether it exists first (and read it) before regenerating, so you don't silently discard prior decisions the user or a teammate made.

Read an existing `MASTER.md` before deciding whether `--force` is justified. Never use `--force` without explicit user authorization.

**Retrieval when building a specific page:**
1. Read `design-system/<project-slug>/MASTER.md`
2. Check if `design-system/<project-slug>/pages/<page-name>.md` exists — if so, its rules override Master
3. Otherwise use Master rules exclusively

## Design dials (optional)

Three optional 1-10 sliders that tune `--design-system` output without changing your query. Add any combination of them to the same command:

```bash
python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```

| Dial | Low (1-3) | Mid (4-7) | High (8-10) |
|------|-----------|-----------|-------------|
| `--variance` | Centered / minimal (biases toward Minimalism-style categories) | Balanced / modern | Bold / asymmetric (biases toward Brutalism, Bento Grids) |
| `--motion` | Subtle micro-interactions | Standard scroll/stagger motion | Complex choreography (pin, Flip, SplitText) |
| `--density` | Spacious (24-96px spacing scale) | Standard (16-64px, current default) | Dense/dashboard (8-32px spacing scale) |

- `--motion` attaches a ready-to-use motion preset pulled from `--domain gsap`, matched to the resolved tier (Subtle/Standard/Complex). Each preset carries four implementations — a GSAP snippet, spring params (stiffness/damping/mass) for Motion/Framer Motion, a CSS-native snippet, and an explicit `prefers-reduced-motion` fallback — plus framework notes, Do/Don't, and performance notes. Rows that are not spring-shaped (scroll-scrubbed, looping, timer-driven) say so rather than giving a number.
- `--density` overrides the `--space-*` CSS variable table in the ASCII/markdown/MASTER.md output — use it for dashboards (high) vs. marketing pages (low) without hand-editing tokens.
- Leaving a dial unset keeps that part of the output exactly as it was before (no behavior change).

**Example:**
```bash
python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "internal analytics dashboard" --design-system --variance 8 --motion 7 --density 8 -p "Ops Console"
```

## Output Formats

`--design-system` supports `-f ascii` (default, terminal display) and `-f markdown` (documentation). `-f dtcg` emits the design system as W3C Design Tokens Community Group JSON instead of ASCII or markdown — use it when the tokens need to reach a design tool or a build pipeline rather than a reader. `-f shadcn` emits a shadcn/ui `:root` block in `oklch()` instead, drop-in compatible with tweakcn themes.

Every generated palette is checked against WCAG 2.2. Text pairs must clear 4.5:1; non-text pairs (border, focus ring) are reported at 3:1 but stay **advisory**, because 1.4.11 only applies when the boundary is the sole indicator of a component. Pass `--strict-contrast` to make a text-pair failure exit non-zero and skip persistence, so a failing palette never reaches disk. The full report also rides along in `$extensions["cc.uupm"].contrast` in DTCG output.

`--json` works for every search mode and overrides `-f`; for `--design-system` it includes the raw design system dict plus persistence status. In text output, long prose fields are clipped at 300 characters (code and snippet columns are exempt) — add `--full` to read them whole.

## Tips for Better Results

- Keep one dominant intent and 2–5 meaningful terms per query: `"keyboard focus modal"`, not a full audit checklist
- Retry once with a narrower phrase or explicit domain/stack; do not cycle through unrelated keywords
- Use `--design-system` for a new project/page and `--domain` for a focused concern
- Pass the detected stack explicitly for implementation-specific guidance

| Problem | What to Do |
|---------|------------|
| Can't decide on style/color | Re-run `--design-system` with different keywords |
| Dark mode contrast issues | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §6: `color-dark-mode` + `color-accessible-pairs` |
| Animations feel unnatural | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §7: `spring-physics` + `easing` + `exit-faster-than-enter` |
| Form UX is poor | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §8: `inline-validation` + `error-clarity` + `focus-management` |
| Navigation feels confusing | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §9: `nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| Layout breaks on small screens | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §5: `mobile-first` + `breakpoint-consistency` |
| Performance / jank | `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` §3: `virtualize-lists` + `main-thread-budget` + `debounce-throttle` |
