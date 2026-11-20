# Not verified yet

Everything here was written from Vast's public API documentation (docs.vast.ai/api, read 2026-11-19)
and tested only against the fake in `tests/fake_vast.py`. The first live run settles each item.

## The first run

Do it on the machine that holds the keys, with a cheap card and a short cap (for example a 3090 at
$0.20–0.40/hr for 0.5 h).

- [ ] `account` returns `balance_usd`. The field may be named differently: check `GET /users/current/`.
- [ ] `search_offers` returns offers.
  - [ ] Confirm the `PUT /search/asks/` body shape (`{"q": {...}}`).
  - [ ] Confirm the field names: `dph_total`, `gpu_ram` in MB, `reliability2`, `disk_space`.
  - [ ] Confirm that `dph_total` includes storage for the disk you will ask for.
- [ ] `quote` then `rent` with `confirm: true` creates an instance.
  - [ ] Confirm that `PUT /asks/{id}/` answers `{"success": true, "new_contract": <id>}`.
  - [ ] Confirm that the `label` and `onstart` fields are kept.
- [ ] `POST /instances/{id}/ssh/` with `{"ssh_key": ...}` attaches the key. If it doesn't, put the
  key on the account once at cloud.vast.ai.
- [ ] `wait_ready` sees `actual_status: running`, `ssh_host` and `ssh_port`, and `ssh root@host -p port`
  answers.
- [ ] Run the `gpu_info` recipe.
- [ ] **Watchdog.** Rent with `hours: 0.2` and leave it alone. After 12 minutes the instance should show
  `stopped`. This confirms that `CONTAINER_ID` and `CONTAINER_API_KEY` are injected, and that the
  instance-scoped key may stop its own instance with `PUT /instances/{id}/ {"state": "stopped"}`.
- [ ] `destroy` with `confirm: true` removes the instance, and `instances` no longer lists it.

## Environments

- [ ] `blender`:
  - [ ] The `nvidia/cuda:12.4.1-runtime-ubuntu22.04` image starts with ssh on Vast.
  - [ ] Blender 4.2.3 downloads and the sha256 check passes.
  - [ ] `blender_render` with `device: OPTIX` renders a frame on the GPU.
  - [ ] Blender's library dependencies cover Cycles on that image.
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
- Windows: `ssh` and `scp` ship with Windows 10 and later. The tunnel is started with
  `start_new_session`, which is POSIX only, and has not been tried on Windows.
