# reach

Claude Code plugin that gives Claude read access to the internet through
[Agent Reach](https://github.com/Panniantong/Agent-Reach): it checks which of 15 platforms
(web, search, YouTube, Reddit, GitHub, Bilibili, RSS, ...) are reachable on your machine, and
routes each to the platform's own upstream tool.

| Skill | What it is |
|---|---|
| `reach-setup` | Is `agent-reach` installed and healthy; how to install it; what each platform still needs |
| `reach-connect` | Wire another skill to Agent Reach: channel map, a Reach block, a new-toolset template, and a checker |
| `agent-reach` | The router: which tool for which platform, with the retry chains in `references/` |

## Install

```
/plugin marketplace add groot99-droid/Pipelines-Plugin
/plugin install reach@rosw
```

## Setup

The plugin carries instructions, not the program. Install the CLI yourself:

```
pipx install "git+https://github.com/groot99-droid/Pipelines-Plugin.git#subdirectory=agent-reach"
agent-reach doctor
```

`agent-reach install` only checks by default. Installing system tools (`--system`) and
logging in to platforms are your decisions: credentials and cookies live in `~/.agent-reach/`,
outside any project, and Claude never reads them. It is read-only: no posting, commenting or liking.
