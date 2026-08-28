# This repo is an Obsidian vault

63 works in plain markdown. Open the folder directly and everything —
`00_INDEX.md`'s links, the wikilinks, the folder structure — works as written.

**Obsidian → Open folder as vault → this directory.**

Nothing needs converting. The files are the vault; if you stop using Obsidian
tomorrow you still have 63 markdown files.

---

## Connecting it to Ollama

Ollama runs the model on this laptop. Two ways to use it here, and they are worth
keeping separate:

**In Obsidian, while writing** — a community plugin (Copilot, Smart Connections,
Text Generator) talking to `http://localhost:11434`. Chat about the open note,
continue a paragraph, surface related passages.

**Across the whole archive** — `tools/vault_rag.py` in the `Creative-Headquarters`
repo indexes every note into embeddings and answers questions over all of them:

```bash
cd ../Creative-Headquarters
python3 tools/vault_rag.py index --vault ../Creative-Writing
python3 tools/vault_rag.py ask "which stories share the drowning motif"
```

It answers only from what it retrieves, and cites the chunk ids so every claim
traces back to a file. Asked something the archive does not cover, it says so
rather than inventing it.

**Full setup, both halves, and the failure modes:
[`Creative-Headquarters/OBSIDIAN.md`](../Creative-Headquarters/OBSIDIAN.md).**

The one step everybody skips: Ollama rejects browser origins it does not know, and
Obsidian is a browser. Without `OLLAMA_ORIGINS="app://obsidian.md"` set and Ollama
restarted, plugins report "failed to fetch" while `curl` works fine.

---

## What `.gitignore` keeps out, and why

Obsidian writes machine state and plugin credentials into the vault as a side effect
of normal use. None of it is anything you wrote.

| Ignored | Why |
|---|---|
| `.obsidian/plugins/*/data.json` | Plugin settings — **where API keys land**. A key pasted into a plugin's settings box lives here. |
| `.obsidian/workspace.json`, `cache` | Which notes you had open, window layout. Churns constantly. |
| `.trash/` | Obsidian's local trash. Deleted notes, still fully readable. |
| `.smart-env/`, `*.embeddings.json`, `.rag/` | Local AI caches — hundreds of MB, and a vectorized copy of the entire archive. Rebuildable. |
| `.env`, `*.key`, `*.pem`, `secrets/` | The usual. |
| `_private/`, `99_Private/`, `*.private.md` | **Yours to use.** Anything under these never reaches the remote. |

Vault *settings* — hotkeys, appearance, enabled plugins — stay versioned, so the
vault opens the same way on another machine.

The private-folder rules govern what you add from here on; files already committed
are unaffected. To pull something already in the history back out, moving it into
`_private/` is not enough — the earlier commits still hold it, and that needs a
history rewrite, not an ignore rule.
