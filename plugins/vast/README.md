# vast

Rent Vast.ai GPUs from Claude and run headless Blender, ComfyUI and your own commands on them. The
`vast` MCP server (`server/server.py`) is stdlib Python; it reaches Vast's REST API with `urllib` and
the instance with the system's own `ssh` and `scp`.

**Nothing in this plugin has been run against a live Vast account yet.** The tests use a fake API and
fake ssh. `UNVERIFIED.md` lists what to check on the first real run.

## Install

```
/plugin marketplace add groot99-droid/Pipelines-Plugin
/plugin install vast@rosw
```

## Setup

- **API key.** Create one at cloud.vast.ai (Account, then Keys) and make it available as
  `VAST_API_KEY`. The server looks for it in three places, in this order:
  1. the `VAST_API_KEY` environment variable;
  2. a `NAME=value` keys file named by `VAST_KEYS_FILE`;
  3. the Vast CLI's own file (`vastai set api-key` writes it).

  The server never shows the key, and never writes it anywhere.
- **SSH key.** You need an OpenSSH key pair, by default `~/.ssh/id_ed25519` (`ssh-keygen -t ed25519`),
  or set `VAST_SSH_KEY` to the private key's path. Only the `.pub` is sent to Vast. Known hosts are
  kept in the server's own file under `VAST_STATE_DIR`.
- **Folders.**
  - `VAST_WORK_DIR` (default `./vast-work`) is the only local folder files are uploaded from and
    downloaded into.
  - `VAST_STATE_DIR` (default `~/.vast-mcp`) holds the ledger (`state.json`, `events.jsonl`) and
    `known_hosts`.
- **`python`.** It must be on PATH. If only `python3` is, edit the command in `.mcp.json`.

## What it does

| Tool | Does |
|---|---|
| `account`, `list_recipes`, `search_offers`, `instances`, `job_status` | Read only. |
| `quote` | Prices an offer against the budget. Spends nothing. |
| `rent` | Rents the quoted offer. Spends money, and needs `confirm: true`. |
| `wait_ready`, `upload`, `download` | Readiness and scp, kept inside the work and job folders. |
| `run_recipe` | Runs a named, typed command from `recipes.json`. Arguments are shell-quoted, never spliced. |
| `run_shell` | Runs any command. Needs `confirm: true` on every call, and the command is logged. |
| `tunnel` | An ssh `-L` tunnel bound to 127.0.0.1, for ComfyUI or any web UI. |
| `stop`, `destroy`, `reap` | End the spend. Each needs `confirm: true`. |

The environments in `recipes.json` are:

| Environment | Image and setup |
|---|---|
| `base` | CUDA 12.4 runtime. |
| `blender` | Blender 5.2.1 LTS from a mirror, checked against a sha256 pinned in `recipes.json`. |
| `comfy` | ComfyUI v0.3.10 on PyTorch 2.5.1, listening on localhost only. |

## The budget

`limits.json` holds the author's biweekly limits: each price band gets a number of GPU hours over a
rolling 14 days.

| $/hr | hours per 14 days |
|---|---|
| ≤ 1.00 | 100 |
| ≤ 1.50 | 50 |
| ≤ 2.50 | 30 |
| ≤ 5.00 | 10 |
| ≤ 10.00 | 4 |
| > 10.00 | refused |

How the hours are counted:
- A live rental reserves hours up to its deadline.
- An ended rental counts the hours it ran.
- `quote` caps a rental at what its band has left.
- `rent` re-reads the price and refuses if it has risen by more than 2%, and refuses a quote that is
  stale (over 15 minutes old) or already used.
- The bands use Vast's listed price. That price leaves out the disk you ask for, so `quote` also shows
  an estimate with it (`dph_with_disk_estimate`). Bandwidth, and the disk of a stopped instance until
  it is destroyed, are billed on top and are not metered here.

Every rental's onstart starts a watchdog that stops the instance at its deadline. It uses the
instance-scoped `CONTAINER_API_KEY` Vast injects, so it works with your laptop closed. That watchdog is
stopped two live rentals at their deadline (see `UNVERIFIED.md`). `reap` is the fallback.

Every tool result carries a `spend` block with live rentals, dollars spent so far, and the hours each
band has left.

## Tests

```
python -m unittest discover -s plugins/vast/tests
python plugins/vast/server/server.py --selftest
```

The tests run a fake Vast API on 127.0.0.1, fake `ssh`/`scp` binaries and an injected clock. They
never use a real key or the network.
