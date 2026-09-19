# This repo is an Obsidian vault

63 works in plain markdown. Open the folder directly and everything —
`00_INDEX.md`'s links, the wikilinks, the folder structure — works as written.

**Obsidian → Open folder as vault → this directory**
(`Pipelines/creative-writing/vault`). The vault lives inside the `Pipelines`
repo as one tool's data; open *this* folder, not the repo root, or Obsidian will
try to index the pipeline's Python too.

Nothing needs converting. The files are the vault; if you stop using Obsidian
tomorrow you still have 63 markdown files.

Start from [[00_INDEX.md|the index]]. The tooling that writes into this vault is
mapped at [[_Pipelines/_index|Pipelines index]]; its staging area is
[[_Idea_Library/_index|the Idea Library]].

---

## Connecting it to Ollama

Ollama runs the model on this laptop. Two ways to use it here, and they are worth
keeping separate:

**In Obsidian, while writing** — a community plugin (Copilot, Smart Connections,
Text Generator) talking to `http://localhost:11434`. Chat about the open note,
continue a paragraph, surface related passages.

**Across the whole archive, no Ollama needed** — `tools/vault_search.py`, right
here in the vault. Stdlib-only TF-IDF, no network, no embeddings:

```bash
python tools/vault_search.py index                    # rebuild after any change
python tools/vault_search.py search "drowning motif"
```
It cites file + heading/line range for every hit, so each claim traces back to a
file. Re-run `index` after editing content or frontmatter.

**Embeddings-based, in the separate `Creative-Headquarters` repo** —
`tools/vault_rag.py` there indexes every note into embeddings and answers over
all of them. Point it at this vault's new location:

```bash
cd ~/Creative-Headquarters
python3 tools/vault_rag.py index --vault ~/Pipelines/creative-writing/vault
python3 tools/vault_rag.py ask "which stories share the drowning motif"
```
That repo's own `OBSIDIAN.md` has the full setup and failure modes. Note it still
documents the vault at its old top-level path.

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
