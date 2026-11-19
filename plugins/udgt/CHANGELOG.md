# Changelog

## Unreleased

- Skill udgt-field-research (2026-10-29, `3d0ae8d`): a toolset on Agent Reach that keeps cited outside
  sources under a teardown's `research/`.
- Agent udgt-citation-checker (2026-10-31, `ebe3d49`): checks one chapter's `[[node-id]]`, `path:line` and
  quoted answers. Worked examples in the udgt-teardown skill.

## 0.1.0

- Engine `engine/udgt.py` (stdlib only): scan, check, diff, brief, record, build, query, show, stages.
- Extractors: documents and numbered sections, the decision log, named tables, JSON datasets, code areas
  and anchors, design tokens, palettes, UI copy, screens, screenshots, git history, stated plans, and
  the citations between them.
- Lore kept outside the game (a profile's `lore` roots): Markdown works taken by their frontmatter,
  each with its `##` sections, linked to the sections they cite.
- Explorer page themed from the game's own tokens and fonts, with a menu-style title view and records
  dealt as cards.
- Skills: udgt-teardown, udgt-consult. Agent: udgt-chapter-analyst (read-only).
