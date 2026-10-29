# Which channel answers which question

Channel names are the ones in `agent-reach doctor --json`. The command reference for each is in the
`agent-reach` skill: `${CLAUDE_PLUGIN_ROOT}/skills/agent-reach/references/<file>`.

| The skill needs | Channel(s) | Reference | Setup |
|---|---|---|---|
| Read a page or article at a known URL | `web` | web.md | none |
| Search the web for a topic | `exa_search` | search.md | free key |
| A blog or news feed, new items | `rss` | web.md | none |
| A video's captions or metadata | `youtube`, `bilibili` | video.md | none / login |
| A podcast episode's text | `xiaoyuzhou` | video.md | setup |
| Code, issues, READMEs | `github` | dev.md | none |
| What people say: threads and comments | `reddit`, `v2ex`, `twitter` | social.md | login for reddit and twitter |
| Chinese social and product reviews | `xiaohongshu`, `bilibili` | social.md | login |
| Facebook or Instagram posts | `facebook`, `instagram` | social.md | login |
| Jobs and companies | `linkedin` | career.md | setup |
| Stock quotes and market talk | `xueqiu` | finance.md | login |

Prefer the setup-free channels (`web`, `rss`, `github`, `youtube`, `v2ex`) when they answer the
question; a login-backed channel is a reason to ask the owner first, not a default.
