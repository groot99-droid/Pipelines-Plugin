# color_science.context.md — BRAND CONSTANT
### Studio Headless OS · Router.md §3 gate · Gates: adobe_firefly, adobe_suite_uxp, ui_ux_intelligence

## 0. PROVENANCE

**L0 AUTHORED.** Transcribed from `skills/css_html_ui.skill.md` ARTIFACT A — the
token dictionary already in force in this repository. Seven of the values below are
re-verified on every run by `tools/verify_system.py → check_palette_parity`.

Nothing here was generated or inferred. Where a constraint the brand-gate contract
asks for has no source, this file says so rather than inventing one — per
Router.md §0, a constraint the system cannot source is a constraint it does not
have. Read §5 before treating this file as a colour pipeline.

**2026-09-01 — HARD MONO.** §§2–4 carry the retheme (DECISIONS.md § D10), applied
under ARTIFACT A's `operator-approval only` mutation policy. Ten values still; the
same four accents bound to the same four states. Every ratio in §4 was recomputed
against the new grounds, and a third floor was added for the inversion model.

---

## 1. ROUTING GLOSSARY

| Ask about | Jump to |
|---|---|
| The palette, exact hex values | `## 2. Palette` |
| What each colour is allowed to mean | `## 3. Semantic binding` |
| Contrast floors | `## 4. Contrast` |
| Working space, LUTs, grading | `## 5. Unresolved` |

---

## 2. Palette

The complete studio palette. Ten values; there is no eleventh.

| Token | Hex | Role |
|---|---|---|
| `bg` | `#000000` | ground |
| `bg-raise` | `#0B0B0B` | raised surface |
| `bg-panel` | `#141414` | panel surface |
| `line` | `#383838` | rule |
| `ink` | `#FFFFFF` | primary text |
| `ink-dim` | `#9E9E9E` | secondary text |
| `cyan` | `#00E5FF` | state: nominal |
| `amber` | `#FFC400` | state: waiting |
| `alert` | `#FF3B30` | state: blocked |
| `queued` | `#8A8AFF` | state: idle |

The three grounds sit within 8% of each other on purpose. They are not a depth
ladder — `line` does the separating, and a region distinguishable only by its
background value is a region missing its border (`visual_identity` §2).

The palette is not advisory: `check_palette_parity` re-reads `bg`, `bg-raise`,
`bg-panel`, `cyan`, `amber`, `alert`, and `queued` from ARTIFACT A on every run and
fails if `control_room.html` disagrees.

---

## 3. Semantic binding

`cyan → nominal · amber → waiting · alert → blocked · queued → idle`

This is the same table as `visual_identity` §3, and the two must not drift. The
duplication is deliberate — a colour gate and an identity gate both need it — but
if they ever disagree, ARTIFACT A `semantic.*` is the tiebreak.

An accent used outside its bound state is a violation, including "close enough"
uses: amber as a highlight, cyan as emphasis, alert as a decorative rule.

---

## 4. Contrast

Three floors, all measured, none traded against another.

**Text — 4.5:1 on all three grounds.** Worst case is `alert` at 5.19:1 on
`bg-panel`; `ink-dim` sits at 6.88:1 there, and `ink` at 18.42:1.

**Non-text — 3.0:1 on its own ground.** Every accent used as a status dot, node
border, or progress fill clears it against `line` as well as against the grounds;
worst case is `alert` on `line` at 3.31:1.

**Inversion — 4.5:1 for ground ink on an accent fill.** This floor is new on
2026-09-01 and exists because elevation stopped being a glow and became a solid
fill (`visual_identity` §5): a live element prints `bg` on top of its state accent,
so an accent too dark to carry black text is rejected no matter how well it reads
as text. Worst case is `bg` on `alert` at 5.92:1.

Measured, before and after:

| token | 2026-08-31 | HARD MONO | on |
|---|---|---|---|
| `ink` | 11.59:1 | **18.42:1** | `bg-panel` |
| `ink-dim` | 6.34:1 | **6.88:1** | `bg-panel` |
| `cyan` | 9.58:1 | **11.98:1** | `bg-panel` |
| `amber` | 7.56:1 | **11.53:1** | `bg-panel` |
| `alert` | 5.78:1 | **5.19:1** | `bg-panel` |
| `queued` | 5.55:1 | **6.28:1** | `bg-panel` |
| `alert` (non-text) | 3.39:1 | **3.31:1** | `line` |

`alert` is the only value that moved down, and it moved down because the ground it
is measured against moved down with it — `bg-panel` went from `#1B2238` to
`#141414`, so every ratio in that column is against a darker ground than before.
It clears both floors that bind it. It is also the value with the least headroom in
the palette, so a future change that pushes red further toward primary `#FF0000`
(4.61:1 on `bg-panel`, 2.93:1 on `line`) fails the non-text floor and is rejected.

This is stricter than the file said before 2026-08-31. The earlier text claimed ink
cleared AA and hedged that dim ink was "structure, not reading matter" — a measured
audit showed that hedge was covering two real failures: `ink-dim` at **3.78:1**
while carrying 10–11px labels, and `queued` at **2.23:1**, below even the 3.0 floor
that applies to it as a status dot. Both were palette bugs, not acceptable trade-offs.
The floors are recorded in ARTIFACT A `contrast_floor` so a future value that
regresses any of the three is rejected rather than re-hedged.

Dim ink is still **secondary**, and should not hold the only copy of something the
operator must read — but that is an information-hierarchy rule, not a contrast
excuse.

Verify any new pairing before it ships:

```bash
python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux
```

---

## 5. Unresolved

The brand-gate contract asks this file for **working space, LUTs, and grading
rules**. Those have no source in this repository and are **not invented here**.

What §2 gives you is a UI token set in sRGB hex. It is not a colour-managed
pipeline: there is no declared working space, no LUT, no grading ladder, and
nothing that tells `adobe_suite_uxp` what to do with a linear EXR.

Stated plainly, so a route does not mistake this file's existence for an answer:
**`adobe_firefly` and `adobe_suite_uxp` load this gate at L0 and get a palette, not
a colour pipeline.** A task needing a working space or a grade treats that specific
constraint as unresolved and says so in its attestation. A file existing does not
make every question in it answered.

Closing this requires an operator decision — which working space, which delivery
transform — or enough precedent in `vault/` to derive one. `ui_ux_intelligence`
cannot supply it: `colors.csv` holds product palettes, not colour-management policy.
