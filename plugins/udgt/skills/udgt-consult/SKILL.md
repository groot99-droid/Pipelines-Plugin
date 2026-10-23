---
name: udgt-consult
description: Look things up in an existing UDGT teardown of a game while working on that game - why a decision was made, what a section of the design doc says, which data records and code a mechanic touches, what the owner said in a brief, what is planned next. Use before changing a game that has a teardown, or when asked "why is it like this" about it. Not for writing the teardown (that is udgt-teardown).
---
# UDGT consult

A teardown folder holds `profile.json`, `teardown.json`, `answers.json` and `chapters/`. Below, `udgt`
means `python ${CLAUDE_PLUGIN_ROOT}/engine/udgt.py` and `P` is that folder's `profile.json`. If you do
not know where the teardown folder is, look for the path the game repository's own instructions give,
and if you still cannot find it, ask the owner.

1. `udgt query "<words>" --profile P [--kind decision|section|record|message|plan|answer...] [--area A]`
   ranks nodes by the words. Ids work as words (`A115`, `3.11`, `killer`).
2. `udgt show <node-id> --profile P` prints the node, what it cites, what cites it and, for a
   decision, the commits that name it.
3. Read the chapter that discusses it (`chapters/*.md`, which cite nodes as `[[id]]`) and the owner's
   answers for its stage (`--kind answer`).
4. Then read the source the node points at (`source.path:line`, relative to the game checkout): the
   teardown is a map of the game, not a copy of it.

If `udgt check --profile P` reports the teardown as stale, say so before relying on it, and offer
`udgt scan`. Quote the owner's answers verbatim and attribute chapter analysis to the teardown, not to
the owner.
