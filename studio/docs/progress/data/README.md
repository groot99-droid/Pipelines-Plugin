# ROSW Data: repositories, sessions and items

Updated 20 November 2026 from the owner's eleven GitHub repositories and the Claude Code session list. Everything is Markdown, one topic per file, so each can be loaded separately into NotebookLM.

## What is here

| Path | What it holds |
|---|---|
| `repos/01_Pipelines-Plugin.md` to `repos/11_Video-Editor.md` | One document per repository: numbers, activity by month and day, folder layout, document inventory, decision log index (Who-Did-It), questionnaires, skills and plugins (ROSW), pull requests, the repository's own README, CLAUDE.md and key documents quoted in full, and the full commit log. |
| `sessions/ROSW_Sessions.md` | The sessions document: totals, the 18 active sessions, sessions that did not complete, every session by group, and all 257 in time order. |
| `sessions/by_session/` | One Markdown file per session (257 files, named `date_title_idsuffix.md`): ID, state, outcome, origin, dates, tags, what the session reported at the end, items named in its own summary, and items linked from the repositories (label matches, documents and questionnaires, pull requests, commits), with its neighbours in the same group. |
| `sessions/ROSW_Items.md` | Every questionnaire, owner-answers file, orchestrator handoff, status log, session contract, plan, brief, decision log, playtest kit, guide, game design, studio note and teardown chapter, with dates, sizes, question lists and the sessions they link to. It ends with the Who-Did-It round packets. |

## Method and limits

- **Repositories.** Read from the local clones (`git log`, `git ls-files`, files at HEAD). Counts are as cloned. Commit dates are UTC author dates and can differ from when work was done. Who-Did-It's clone has no commits before 29 October although its decision log starts on 9 October.
- **Sessions.** From the session list only: titles, IDs, states, outcomes, origins, dates, tags and end-of-session summaries. Transcripts were not read. Chats in claude.ai are not in this list.
- **Item links** are suggestions. They come from labels in session titles matching commit subjects, and from time overlap with a likely repository. Parallel sessions overlap, so a time match can belong to another session.
- **Verbatim quotes** of repository files keep the repositories' own characters and wording. Lines are quoted with ">".
- **Left out.** Commit email addresses, and anything in the owner's personal record (see the separate personal documents).
