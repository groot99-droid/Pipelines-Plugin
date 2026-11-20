# What has been verified, and what has not

The plugin was written from Vast's public API documentation (docs.vast.ai/api, read 2026-11-19) and
tested against the fake in `tests/fake_vast.py`. A first live run on 2026-11-19 (two one-hour rentals
of an RTX 3090, Blender 5.2.1 renders with Cycles on OptiX) settled the items marked `[x]`. Each
carries what was seen. `[ ]` is still open.

## The first run

- [x] `account` returns `balance_usd` and `credit_usd`. The live fields are `balance` and `credit`; a
  promotional credit shows as `credit`, with `balance` at 0.
- [x] `search_offers` returns offers.
  - [x] The `PUT /search/asks/` body shape (`{"q": {...}}`) is accepted.
  - [x] Field names `dph_total`, `gpu_ram` in MB, `reliability2`, `disk_space` are right.
  - [x] `verified` is always null on a live offer; the field is `verification` (`"verified"` or
    `"unverified"`). Fixed in 0.1.1.
  - [x] `dph_total` does **not** include storage for the disk asked for: listed 0.1889, live 0.195 and
    0.2133 with a 30 GB disk. 0.1.1 adds an estimate to `quote`.
  - [ ] The estimate itself (`storage_cost` in $/GB/month, over 730 hours) has not been compared with a
    live instance's price.
  - [ ] The `min_cuda` filter (`cuda_max_good` `gte`), added in 0.1.1, has not been sent to Vast.
- [x] `quote` then `rent` with `confirm: true` creates an instance, after a fix: an `id` filter matches
  nothing on Vast, so `quote` refused every offer as `offer_gone`. 0.1.1 looks the offer up by
  `ask_contract_id`.
  - [x] `PUT /asks/{id}/` answers `{"success": true, "new_contract": <id>}`.
  - [x] The `label` and `onstart` fields are kept.
- [x] `POST /instances/{id}/ssh/` with `{"ssh_key": ...}` attaches the key; ssh answered about 30 s
  after `rent`.
- [x] `wait_ready` sees `actual_status: running`, `ssh_host` and `ssh_port`, and ssh answers.
- [x] The `gpu_info` recipe runs.
- [x] **Watchdog.** It stopped both rentals at their deadline (1.02 h and 1.04 h counted). The status
  word afterwards is `exited`, not `stopped`.
- [x] `destroy` with `confirm: true` removes the instance (`DELETE /instances/{id}/` on v0 still works),
  and `instances` no longer lists it.
- [x] `instances` works after a fix: the v0 list answers HTTP 410, and 0.1.1 calls
  `/api/v1/instances/`.

## Found on the live run, fixed in 0.1.1, not yet tried live

- [ ] **Background start.** `run_shell` with `background` and the background recipes timed out after
  60 s and returned no `job_id`, though the job ran to its end. 0.1.1 detaches the job from ssh and
  returns the `job_id` even when ssh does not answer. Confirm that a background start now returns at
  once, and that `job_status` follows it.
- [ ] **The `blender` environment's own install.** download.blender.org answered 403 to wget and curl,
  so the 0.1.0 onstart never installed Blender and reported nothing. On the run, 5.2.1 was installed by
  hand from mirror.clarkson.edu (about 3 minutes) and its sha256 matched. 0.1.1 does the same from the
  onstart, with the sha256 pinned (two mirrors publish the same value; blender.org's own file could not
  be fetched to compare). Confirm that `ready` shows `.blender-ready` without help.

## Seen on the live run, not fixed

- ssh through Vast's proxy was intermittent: several short calls hung for 30-40 s, one `upload` timed
  out and worked on a retry, and a 900 MB `download` took about 10 minutes.
- The account was charged more than hours x the live hourly price ($0.54 against about $0.42 for the
  two rentals). The plugin does not meter bandwidth or the disk of a stopped instance.
- No tool extends a rental or restarts a stopped instance; a second hour was a second rental.
- An MCP client may keep the server's old process after the code changes; restart the client.

## Environments

- [ ] `blender`:
  - [x] The `nvidia/cuda:12.4.1-runtime-ubuntu22.04` image starts with ssh on Vast.
  - [ ] Blender 5.2.1 installs from the onstart (see above).
  - [x] `blender_script` runs a script headless, and Cycles renders with OptiX on the GPU.
  - [ ] `blender_render` with `device: OPTIX` renders a frame (the recipe itself was not run).
  - [x] Blender's library dependencies cover Cycles on that image.
- [ ] `comfy`:
  - [ ] `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime` starts.
  - [ ] The `v0.3.10` tag clones and its requirements install.
  - [ ] `comfy_start` serves on 127.0.0.1:8188.
  - [ ] A `tunnel` reaches it from the laptop.
- [ ] Which custom nodes and models the image-to-3D workflow needs. Install them with
  `comfy_install_node` and `comfy_fetch_model`, then record them in `recipes.json` as a new environment
  or recipe, so later rentals do not rediscover them.

## Deferred

- No volume support yet. Files live on the instance's disk and go when it is destroyed.
- Interruptible (bid) instances are not offered. `search_offers` asks for `on-demand` only.
- Windows: `ssh` and `scp` ship with Windows 10 and later, and the live run was driven from Windows.
  The tunnel is started with `start_new_session`, which is POSIX only, and has not been tried there.
