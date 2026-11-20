---
name: vast-gpu
description: Rent a Vast.ai GPU through this plugin's vast MCP server and run headless Blender renders and scripts, ComfyUI workflows, or the user's own commands on it, then bring the results back and destroy the instance. Every rental is quoted against the user's biweekly per-price-band hour budgets and needs their go-ahead. Use when the user wants GPU work done in the cloud, a Blender render on a real GPU, ComfyUI image-to-3D (Trellis 2, Pixal3D) or other GPU workflows, or asks what is running and costing money on Vast. Not for Meshy or other hosted 3D APIs, and not for a Blender running on the user's own machine.
---

# Rent a GPU on Vast.ai

Paths start from `${CLAUDE_PLUGIN_ROOT}`. The server is `${CLAUDE_PLUGIN_ROOT}/server/server.py`,
registered in this plugin's `.mcp.json` as `vast`. Its tools are `account`, `list_recipes`,
`search_offers`, `quote`, `rent`, `instances`, `wait_ready`, `upload`, `download`, `run_recipe`,
`run_shell`, `job_status`, `tunnel`, `stop`, `destroy` and `reap`.

**Renting spends the user's money.** The server enforces its own rules, and you follow these on top:

- Never pass `confirm: true` to `rent`, `run_shell`, `stop`, `destroy` or `reap` until the user has said
  yes to that exact call in this conversation. Show them what it will do first. The call without
  `confirm` is a dry run that shows you what to show them.
- Every result carries a `spend` block with the live rentals, the dollars spent so far, and the hours each
  price band has left in its 14-day window. Mention it whenever something is running.
- When the work is done, download what is needed and then `destroy` (with the user's go-ahead). A stopped
  instance still bills its disk.
- Never read, print or ask for the API key or the ssh private key. `account` reports only whether a key is
  set.

## The budget

`${CLAUDE_PLUGIN_ROOT}/limits.json` holds the user's limits. Each price band gives a number of GPU hours
per rolling 14 days: up to $1.00/hr for 100 h, $1.50 for 50 h, $2.50 for 30 h, $5.00 for 10 h, and
$10.00 for 4 h. Anything above $10/hr is refused. A rental counts against the band its price falls in.
While it lives it reserves hours up to its deadline. When it ends, it counts the hours it actually ran.

`quote` caps the requested hours at what the band has left. It refuses when a band is spent or an offer
is over the ceiling. Do not look for a way around a refusal: tell the user which band is spent and when
hours come back, or offer a cheaper band.

## The walk-through

1. **`account`**: is a key set, and what is the balance. If no key is set, tell the user to set
   `VAST_API_KEY` (or `VAST_KEYS_FILE`), or to run `vastai set api-key` once, and stop.
2. **`list_recipes`**: the environments (`base`, `blender`, `comfy`) and the recipes each one runs.
3. **`search_offers`**: filter by `gpu_name`, `min_gpu_ram_gb`, `max_dph`, `geolocation` and `min_cuda`
   (pass the environment's `cuda` from `list_recipes`). Results are cheapest first, each with
   `band_hours_left`. A Blender render or Trellis 2 wants 24 GB or more.
4. **`quote`**: pass `offer_id`, `environment` and `hours`. Show the user the $/hr, the estimate with the
   disk (`dph_with_disk_estimate`, `worst_case_cost_with_disk_usd`), `cap_hours`, any `warnings` and
   `leaves_this_machine`, and ask for the go-ahead. The estimate leaves out bandwidth.
5. **`rent`** with `confirm: true` after they say yes. The quote is spent once, and expires after 15
   minutes.
6. **`wait_ready`**. The environment's onstart may still be installing after ssh answers. The `ready`
   recipe shows its markers (`.blender-ready`, `.comfy-ready`). A `.blender-failed` marker means the
   install gave up: read `logs/blender-install.log` in the same output, tell the user, and do not keep
   waiting on a billing instance.
7. **Work**:
   - `upload` takes a path relative to `VAST_WORK_DIR` on this machine and a path relative to
     `/workspace/job` there.
   - `run_recipe` runs a named recipe. Background recipes return a `job_id`; poll it with `job_status`.
     A result with `start_confirmed: false` means ssh did not answer in time: the job may be running, so
     ask `job_status` before starting it again.
   - `run_shell` is only for what no recipe covers.
   - `download` brings results back into `VAST_WORK_DIR`. Check the returned sha256 and size.
8. **`destroy`** with the user's go-ahead. Then call `instances` to confirm nothing is left running.

## Blender

- Rent with `environment: "blender"`. It gives Blender 5.2.1 LTS, checked against a sha256 pinned in
  `recipes.json`.
- Upload the `.blend` and its textures, then run the `blender_render` recipe. Its arguments are `blend`,
  `output` (e.g. `render/frame_####`), `frame_start`, `frame_end` and `device` (`OPTIX`, `CUDA` or
  `CPU`).
- For scripted scenes, upload the script and its inputs and run `blender_script` with `script` and
  `args`. It runs `blender -b --factory-startup --python <script> -- <args>` from `/workspace/job`.

## ComfyUI

1. Rent with `environment: "comfy"`, which gives ComfyUI v0.3.10. When `ready` shows `.comfy-ready`,
   run `comfy_start`.
2. Open a tunnel: `tunnel` with `action: "open"`, the `instance_id` and `local_port: 8188`. ComfyUI is
   now at `http://127.0.0.1:8188` on this machine, and never listens on a public port there.
3. Find out what the workflow lacks with ComfyUI's own `/object_info`, or with the user's client.
   - Add missing custom nodes with `comfy_install_node`: a GitHub `repo`, a folder `name`, and a pinned
     `ref` (prefer a commit).
   - Add missing models with `comfy_fetch_model`: a Hugging Face `url`, a models `folder`, and a
     `filename`.
   - Then run `comfy_start` again.
4. Close the tunnel when done (`action: "close"`). `destroy` closes it too.

## When something goes wrong

- **`no_ssh_key`**: the user needs an OpenSSH key pair, by default `~/.ssh/id_ed25519` (or set
  `VAST_SSH_KEY`). Only the `.pub` is ever sent.
- **`price_changed` or `offer_gone`**: search and quote again.
- **`instances` shows `over_deadline: true`**: the on-box watchdog should already have stopped it. Offer
  `reap` (dry run first).
- **An instance shows `in_ledger: false`**: it was rented outside this server and is not budgeted here.
  Tell the user; do not destroy it unasked.
- **Nothing has been run against a live account yet.** `${CLAUDE_PLUGIN_ROOT}/UNVERIFIED.md` lists what to
  check on the first run. If an endpoint answers in a shape the server does not expect, report it plainly.
