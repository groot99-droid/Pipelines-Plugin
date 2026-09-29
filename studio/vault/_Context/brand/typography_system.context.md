# typography_system.context.md — BRAND CONSTANT
### Studio Headless OS · Router.md §3 gate · Gates: css_html_ui, ui_ux_intelligence

## 0. PROVENANCE

**L0 AUTHORED.** Transcribed from `skills/css_html_ui.skill.md` ARTIFACT A — the
token dictionary already in force in this repository and machine-enforced by
`tools/verify_system.py → check_palette_parity`.

Nothing here was generated or inferred. This file does not introduce a new type
system; it promotes one the studio was **already operating under** from an
implementation detail inside one skill file to a Router-visible L0 gate.

`skills/ui_ux_intelligence.skill.md` is the declared **regeneration path** for this
file (DECISIONS.md § D9), under ARTIFACT A's `operator-approval only` mutation
policy. It proposes; it does not commit.

**2026-09-01 — HARD MONO.** §§2–5 were rewritten under that policy, operator-
directed (DECISIONS.md § D10). The two-face system collapsed to one family. The
inversion §2 warns about — mono as the body face — did not change; it got stricter.

---

## 1. ROUTING GLOSSARY

| Ask about | Jump to |
|---|---|
| Which typeface, and how the two weights are used | `## 2. The one family` |
| Sizes, the scale, tracking | `## 3. Scale and tracking` |
| Hierarchy rules | `## 4. Hierarchy` |
| Licensing | `## 5. Licensing` |
| Product and client work | `## 6. Scope boundary` |

---

## 2. The one family

One family, two weights. There is no second typeface and no third weight.

| Role | Stack | Weight | Used for |
|---|---|---|---|
| display | `'JetBrains Mono', ui-monospace, monospace` | `800` | brand mark, headings, phase names, numerals |
| mono | `'JetBrains Mono', ui-monospace, monospace` | `400` | body, data, labels, logs |

`500` exists as a single in-between step for a status word that must out-weigh the
data around it without becoming a heading. It is not a third role and nothing else
may take it.

**Mono is the body face**, not an accent for code. This inversion is what gives the
studio's surfaces their instrument-readout character, and it is deliberate — reading
it as a mistake and "fixing" body copy to a sans is the failure mode this section
exists to prevent. Since 2026-09-01 there is no sans in the system at all, so the
"fix" would have to invent a typeface, which §0 does not permit.

Both faces resolving to the same family means **weight, size, tracking and case are
the entire hierarchy** (§4). Losing one of them loses a level.

An un-tokened `font-family` in generated CSS is a protocol violation
(`css_html_ui` §0 anti-hallucination law), not a style preference.

---

## 3. Scale and tracking

| Step | Size |
|---|---|
| xs | `10px` |
| sm | `11px` |
| base | `13px` |
| md | `14px` |
| lg | `20px` |
| xl | `30px` |

Tracking: labels `0.18em`, display `0.08em`, brand `0.02em`. Label tracking is wide
on purpose — at 10–11px it is what keeps a dim uppercase label legible against a
dark ground. Display tracking tightened from `0.14em` on 2026-09-01: at weight `800`
in a monospace, wide tracking reads as a gap rather than as emphasis.

`xl` is **the brand mark and nothing else** — one oversized voice per surface. It is
the one place this system raises its own volume, and a second element at 30px
cancels the effect rather than doubling it. The scale had no step above `20px` before
2026-09-01; that rule was correct for headings and is unchanged for them.

Legibility at these sizes depends on the ink carrying real contrast, which is why
the 2026-08-31 retheme raised `ink-dim` from `#6E7690` (3.78:1, below AA while
carrying 10px labels) to `#9AA4C0` (6.34:1), and why HARD MONO raised it again to
`#9E9E9E` (6.88:1 on panel). A future palette change that lowers it breaks this
scale, not just that colour.

**Note the tension, and do not resolve it silently.** A `10px` label and a `13px`
body sit below the 16px body minimum `ui_ux_intelligence` returns from
`ux-guidelines.csv` for general web UI. That guidance is correct for consumer web
and is **not in force here** — these are dense instrumentation surfaces, viewed at
arm's length on one known display. A routed task must not "correct" the studio
scale toward the database default. For product work the database default applies
and this scale does not (§6).

---

## 4. Hierarchy

Hierarchy is carried by **weight, size, tracking and case together** — never by
colour. Colour is state (`visual_identity` §3), so a heading does not become a
heading by turning cyan, and a count in a panel tick is dim ink no matter how
current it is.

Descending: display/xl (the mark) → display/lg → display/md → display/sm uppercase
(section labels) → mono/base → mono/sm dim → mono/xs dim uppercase.

With one family doing every job, **case is load-bearing**. Section labels, status
words, phase names and controls are uppercase; running prose and data are not.
Uppercasing body copy for emphasis removes the distinction that separates a label
from the thing it labels.

---

## 5. Licensing

JetBrains Mono is open-licensed (SIL OFL) and embeddable. Verified against the
vendored catalogue rather than asserted:

```bash
python3 tools/ui-ux-pro-max/scripts/search.py "JetBrains Mono" --domain google-fonts
```

`tools/ui-ux-pro-max/data/google-font-licenses.json` records it as
`license: OFL`, added 2020-11-18, designers JetBrains / Philipp Nurullin /
Konstantin Bulenkov, `verifiedAt: 2026-08-13`. The variable `wght` axis runs
`100..800`, which is what makes the `400 / 500 / 800` set in §2 available from one
file.

No licence check has been run against a shipping artifact yet. Treat the OFL
statement as accurate for the family and verify before any distributed binary
embeds it.

---

## 6. Scope boundary

This file governs **the studio's own surfaces** — `control_room.html`, `hub/`, and
anything else HQ ships as its own interface.

It does **not** govern typography for product or client work. There,
`ui_ux_intelligence` selects a pairing from `typography.csv` for that product's
category and persists it to that project's own design system. Applying JetBrains
Mono to a client project because it is "the studio font" is a category error — see
DECISIONS.md § D9. A single-family monospace system is a strong choice for an
instrument and a poor default for almost anything else.
