# visual_identity.context.md — BRAND CONSTANT
### Studio Headless OS · Router.md §3 gate · Gates: adobe_firefly, higgsfield_api, css_html_ui, ui_ux_intelligence

## 0. PROVENANCE

**L0 AUTHORED.** Transcribed from `skills/css_html_ui.skill.md` ARTIFACT A — the
token dictionary already in force in this repository and machine-enforced by
`tools/verify_system.py → check_palette_parity`, which fails the build if
`control_room.html` drifts from it.

Nothing here was generated or inferred. This file does not introduce a new brand;
it promotes constraints the studio was **already operating under** from an
implementation detail inside one skill file to a Router-visible L0 gate.

`skills/ui_ux_intelligence.skill.md` is the declared **regeneration path** for this
file (DECISIONS.md § D9). It does not hold authority to rewrite it: ARTIFACT A's
`mutation_policy` is `operator-approval only; agent proposes, never commits`, and
that policy governs this file too. Where a required constraint has no source, this
file says so rather than inventing one — per Router.md §0, a constraint the system
cannot source is a constraint it does not have.

**2026-09-01 — HARD MONO.** §§2–6 were rewritten under that policy, operator-
directed. The corpus rows behind the direction are named in DECISIONS.md § D10:
`styles.csv → brutalism` and `styles.csv → minimalism-and-swiss-style`, blended,
with `google-fonts.csv → JetBrains Mono` as the single family. The identity did not
change kind — it is still dark-ground instrumentation with a closed four-accent
vocabulary. What changed is the surface treatment: flat grounds, hard rules, sharp
corners, and **inversion instead of glow**.

---

## 1. ROUTING GLOSSARY

| Ask about | Jump to |
|---|---|
| Surface treatment, ground, panels, borders | `## 2. Interface identity` |
| What colour is allowed to mean | `## 3. Semantic discipline` |
| Layout structure, grid, spacing rhythm | `## 4. Structural discipline` |
| Glow, elevation, motion | `## 5. Depth and motion` |
| What is off-limits | `## 6. Off-limits` |
| Generated imagery — motifs, framing, texture | `## 7. Unresolved` |

---

## 2. Interface identity

Dark-ground instrumentation, stated bluntly. Near-black ground, flat panels, hard
rules, sharp corners, one monospace family. Nothing is rounded, softened, tinted, or
blurred to imply depth — the studio's own surfaces read as a machine readout, not a
document and not a product page.

| Role | Value | Use |
|---|---|---|
| ground | `#000000` | page base, never a panel |
| raised | `#0B0B0B` | one step up from ground |
| panel | `#141414` | content surfaces |
| line | `#383838` | rules, borders and dividers, never a fill |
| ink | `#FFFFFF` | body and data |
| ink dim | `#9E9E9E` | labels, structure, anything not being read now |

The three grounds are deliberately close. **Separation is a rule, not a tone step** —
if two regions are only distinguishable by their background value, the border is
missing. Gradients, including the decorative radial washes the pre-2026-09-01 body
carried, are off-limits (§6).

**Light mode does not exist.** No surface in this studio's own tooling inverts as a
theme. Product work built for a client is not bound by this — see §7 and
DECISIONS.md § D9.

---

## 3. Semantic discipline

Colour carries state and nothing else. The four accents are a closed vocabulary:

| Accent | Hex | Means |
|---|---|---|
| cyan | `#00E5FF` | active · healthy · complete |
| amber | `#FFC400` | awaiting · review · warning |
| alert | `#FF3B30` | blocked · error · violation |
| queued | `#8A8AFF` | queued · idle · disabled |

**Decorative colour is a violation.** An accent applied to something that has no
state is the most common way this identity degrades. If an element is not
reporting a condition, it is ink or it is dim ink.

Meaning is never re-derived from appearance — "amber-ish for warning" is how a
fifth accent gets invented. The mapping above is the whole of it.

A readout is **not** a state. A count in a panel tick, a heading, a label, a link
in running prose — those are ink or dim ink. The 2026-09-01 pass moved every panel
tick from cyan back to dim ink for exactly this reason: `9 executables` is data,
and data is not a condition.

---

## 4. Structural discipline

- 12 columns, `16px` gutter, `1440px` maximum. New regions are **grid areas**,
  never absolutely-positioned patches.
- Spacing steps are `4 · 8 · 16 · 24 · 32`px — a strict doubling grid. A value
  between two steps is a bug.
- **Radii are `0`.** Panel, chip, bar, pill: all sharp. The `radius.*` tokens still
  exist so consumers resolve to something, and every one of them resolves to zero.
  There is no rounded variant to opt into.
- Rules carry structure, and weight distinguishes their job: `1px` for a hairline
  or divider, `2px` for a panel's internal division (the rule under a heading), and
  `2px` in an accent for an element reporting a state. Never a second grey.
- Breakpoints: tablet `980px`, mobile `640px`.

`control_room.html` is the reference implementation. A new surface that disagrees
with it is wrong until the token dictionary says otherwise.

---

## 5. Depth and motion

There is no depth. Elevation is **inversion**: an element that is live fills solid
with the accent already carrying its state and prints ground-coloured ink on top of
it. A completed station is a filled square; a current tab is a filled cell; a live
warning is a filled block. Everything else is flat.

This replaced the `0 0 10px` accent glow on 2026-09-01, and it is a stronger signal
as well as a plainer one: a solid fill clears 4.5:1 against the ink it carries,
where a bloom clears nothing and only makes a dot look approximately brighter. An
accent fill in a colour the element is not currently signalling is a semantic error,
not a styling choice.

Inversion is for a **live condition**, not for a standing note. A permanent block of
amber shouts louder than whatever it annotates and drains the accent of urgency; a
standing caution takes a heavy rule in the accent instead.

Motion is functional and mechanical: `width .12s linear` for a fill, a hard
`1.2s steps(1, end)` blink for a live heartbeat. No easing curves, no hover
transitions, no decorative animation. Every `motion.*` token nulls out under
`prefers-reduced-motion`.

Focus is always visible: `2px solid #00E5FF`, `2px` offset, applied globally via
`:focus-visible` — not per-component, which is how a control ends up with no ring at
all. Removing it is off-limits (§6), not a trade-off.

---

## 6. Off-limits

- Raw hex or an arbitrary px value in any generated markup — every value resolves
  to a token or it does not ship. This includes `rgba()` restatements of a token:
  a literal copy survives a palette change silently. Derive with `color-mix()`.
- Any value that regresses the ARTIFACT A `contrast_floor`. Every ink and accent
  clears 4.5:1 on all three grounds; every status dot, node, and progress fill
  clears 3.0:1 on its own ground, `line` included; and ground ink printed on an
  accent fill clears 4.5:1 on that fill.
- A fifth accent, or an existing accent used decoratively — a count, a heading, or
  a label is not a state (§3).
- Light-mode surfaces in the studio's own tooling.
- Removing `:focus-visible` styling, for any reason.
- Shadow-based elevation, glow-based elevation, and gradients of any kind,
  including background washes on the page ground.
- A non-zero border radius.
- A second typeface, or a third weight (`typography_system` §2).
- Eased hover transitions. State changes are instant.
- Absolutely-positioned patches instead of grid areas.

---

## 7. Unresolved

This file answers **interface** identity, because that is what the studio has
actually decided. The brand-gate contract (`context/brand/README.md`) also asks
what *generated imagery* from this studio looks like — motifs, framing, texture.

**That has no source yet and is not invented here.** `adobe_firefly` and
`higgsfield_api` load this gate at L0 and will find the interface constraints real
and the imagery constraints absent. Two ways to close it, in order of preference:

1. The operator authors §7 directly — it encodes taste, which is not derivable.
2. Precedent accumulates: once three or more Content MDs of `kind: design` or
   `character` carry imagery decisions, Router.md §5 L2 can derive it, marked
   provisional.

Until then, a route needing imagery motifs states that in its attestation rather
than reading the interface rules above as if they answered the question.
