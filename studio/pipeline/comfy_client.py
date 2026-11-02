"""The ComfyUI client: one image to a textured 3D model (Trellis 2 or Pixal3D) through a
ComfyUI server, from the workflow in comfy/workflows/. Standard library only.

    python studio/pipeline/comfy_client.py check
    python studio/pipeline/comfy_client.py plan   --image PATH [--engine trellis2|pixal3d] [--seed N] [--no-remove-background]
    python studio/pipeline/comfy_client.py run    --image PATH --out DIR [same options] [--timeout S] [--confirm]
    python studio/pipeline/comfy_client.py status PROMPT_ID

`check` reaches the server, lists the node classes and model files the workflow needs, and says which are
missing. `plan` prints what `run` would change in the workflow and sends nothing. `run` without --confirm
is a dry run: it checks the server and the files and prints the request, and posts nothing. With --confirm
it uploads the image, queues the workflow, waits, and downloads the model into --out through a .part file.

Every run is written to OUT/comfy_tasks.json: the image's sha256 (never its path), the engine, the seeds,
the prompt id and the files with their sha256. A run that matches a recorded one (same image, engine, seeds,
background step) whose files are still there is reused and posts nothing.

The server is COMFY_URL (default http://127.0.0.1:8188). A server on another machine is refused unless
--allow-remote is given and the URL is https: the image is sent to it. The machine this studio runs on
(machine.yaml) has no CUDA, and these models need a CUDA GPU, so in practice COMFY_URL names a GPU
machine the author runs. The compute gate describes this machine, so it is not consulted for a remote server.

The workflow names models by file name. `check` compares those with what the server lists; it does not
download models. Which node ids the client changes is BINDINGS below, and each is checked against the
workflow's node class, so a re-exported workflow with shifted ids is refused instead of patched wrongly.

Exit codes: 0 done, 1 refused or the server said no, 2 usage error.
"""

import argparse
import copy
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from download import DownloadError, download
from studio_common import EXIT_OK, EXIT_REFUSED, EXIT_USAGE, Refused, Usage, now, open_console, read_text, stamp, write_text

WORKFLOW = Path(__file__).resolve().parent / "comfy" / "workflows" / "pixal3d_trellis2_image_to_3d.json"
LEDGER = "comfy_tasks.json"
DEFAULT_URL = "http://127.0.0.1:8188"
IMAGE_KINDS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
IMAGE_LIMIT = 20 * 1024 * 1024

# node id -> (class_type it must have, input it is set through)
BINDINGS = {
    "image": ("122", "LoadImage", "image"),
    "trellis2": ("316", "PrimitiveBoolean", "value"),       # False = Pixal3D, True = Trellis 2
    "remove_background": ("248", "ComfySwitchNode", "switch"),
    "seeds": [("3", "KSampler", "seed"), ("12", "KSampler", "seed"), ("18", "KSampler", "seed"), ("23", "KSampler", "seed")],
    "output": ("322", "Save3DAdvanced", None),
}
LOADERS = {  # class_type -> input that names a model file
    "UNETLoader": "unet_name", "VAELoader": "vae_name", "CLIPVisionLoader": "clip_name",
    "LoadMoGeModel": "model_name", "LoadBackgroundRemovalModel": "bg_removal_name",
}
LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")


# ── the server ───────────────────────────────────────────────────────────────

def server_url(allow_remote=False):
    url = (os.environ.get("COMFY_URL") or DEFAULT_URL).rstrip("/")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise Usage("COMFY_URL must be an http(s) address")
    if parts.hostname in LOCAL_HOSTS:
        return url
    if not allow_remote:
        raise Refused(f"COMFY_URL names another machine ({parts.hostname}). The image would be sent there; "
                      "add --allow-remote if that is meant.")
    if parts.scheme != "https":
        raise Refused("a server on another machine must be reached over https")
    return url


def call(base, method, path, body=None, headers=None, expect_json=True, timeout=60):
    request = urllib.request.Request(base + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as err:
        raise Refused(f"the server said {err.code} to {method} {path.split('?')[0]}: {message(err)}") from None
    except (urllib.error.URLError, OSError) as err:
        raise Refused(f"cannot reach the ComfyUI server at {base}: {getattr(err, 'reason', err)}. "
                      "Start ComfyUI, or set COMFY_URL.") from None
    if not expect_json:
        return data
    try:
        return json.loads(data.decode("utf-8"))
    except ValueError:
        raise Refused(f"the server's answer to {method} {path.split('?')[0]} was not JSON") from None


def message(err):
    try:
        found = json.loads(err.read().decode("utf-8", "replace"))
        text = (found.get("error") or {}).get("message") if isinstance(found.get("error"), dict) else found.get("error")
        text = text or found.get("message") or json.dumps(found)
    except (ValueError, AttributeError):
        text = getattr(err, "reason", "") or ""
    return " ".join(str(text).split())[:300]


# ── the workflow ─────────────────────────────────────────────────────────────

def load_workflow():
    try:
        flow = json.loads(read_text(WORKFLOW))
    except (ValueError, Usage) as err:
        raise Usage(f"{WORKFLOW.name} does not load: {err}")
    wanted = [BINDINGS["image"], BINDINGS["trellis2"], BINDINGS["remove_background"], BINDINGS["output"], *BINDINGS["seeds"]]
    for node, class_type, field in wanted:
        found = flow.get(node)
        if not found or found.get("class_type") != class_type:
            raise Usage(f"{WORKFLOW.name}: node {node} should be {class_type}, found "
                        f"{found.get('class_type') if found else 'nothing'}. The workflow was re-exported; "
                        "update BINDINGS in comfy_client.py.")
        if field and field not in found.get("inputs", {}):
            raise Usage(f"{WORKFLOW.name}: node {node} ({class_type}) has no input `{field}`")
    return flow


def patched(flow, image_name, engine, seed, remove_background):
    out = copy.deepcopy(flow)
    node, _, field = BINDINGS["image"]
    out[node]["inputs"][field] = image_name
    node, _, field = BINDINGS["trellis2"]
    out[node]["inputs"][field] = engine == "trellis2"
    node, _, field = BINDINGS["remove_background"]
    out[node]["inputs"][field] = bool(remove_background)
    if seed is not None:
        for offset, (node, _, field) in enumerate(BINDINGS["seeds"]):
            out[node]["inputs"][field] = seed + offset
    return out


def seeds_of(flow):
    return [flow[node]["inputs"][field] for node, _, field in BINDINGS["seeds"]]


def needs(flow):
    """(class types used, [(class, input, file name)] the workflow loads)."""
    classes = sorted({node["class_type"] for node in flow.values()})
    files = []
    for node in flow.values():
        field = LOADERS.get(node["class_type"])
        if field and isinstance(node["inputs"].get(field), str):
            files.append((node["class_type"], field, node["inputs"][field]))
    return classes, sorted(set(files))


def pick(engine, flow):
    """Which model files this engine actually uses: the other engine's UNet is left out of the check."""
    keep = {"trellis2": "pixal3d", "pixal3d": "trellis_2_int8"}[engine]
    classes, files = needs(flow)
    return classes, [f for f in files if not (f[0] == "UNETLoader" and keep in f[2])]


def audit(base, flow, engine):
    """Compare the workflow with what the server has: (missing classes, missing files)."""
    info = call(base, "GET", "/object_info")
    classes, files = pick(engine, flow)
    missing_classes = [c for c in classes if c not in info]
    missing_files = []
    for class_type, field, name in files:
        if class_type in missing_classes:
            continue
        try:
            options = info[class_type]["input"]["required"][field][0]
        except (KeyError, IndexError, TypeError):
            continue  # the server does not list options for this input; nothing to compare
        if isinstance(options, list) and name not in options:
            missing_files.append((class_type, name))
    return missing_classes, missing_files


# ── the image ────────────────────────────────────────────────────────────────

def read_image(path):
    path = Path(path)
    kind = IMAGE_KINDS.get(path.suffix.lower())
    if kind is None:
        raise Usage(f"{path.name}: the image must be one of {', '.join(sorted(IMAGE_KINDS))}")
    try:
        size = path.stat().st_size
    except OSError as err:
        raise Usage(f"cannot read {path.name}: {err.strerror}")
    if size == 0 or size > IMAGE_LIMIT:
        raise Usage(f"{path.name}: the image must be between 1 byte and {IMAGE_LIMIT // (1 << 20)} MB")
    return path.read_bytes(), kind


def multipart(name, data, kind):
    boundary = uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: {kind}\r\n\r\n").encode()
    tail = (f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\nfalse\r\n--{boundary}--\r\n").encode()
    return head + data + tail, f"multipart/form-data; boundary={boundary}"


# ── the ledger ───────────────────────────────────────────────────────────────

def load_ledger(out):
    path = out / LEDGER
    if not path.is_file():
        return {"tasks": []}
    try:
        return json.loads(read_text(path))
    except ValueError as err:
        raise Usage(f"{path} does not parse: {err}. It is written only by comfy_client.py.")


def save_ledger(out, ledger):
    write_text(out / LEDGER, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")


def request_key(image_sha, engine, seeds, remove_background):
    """The same image, engine, seeds, background step and workflow file give the same key."""
    text = json.dumps([image_sha, engine, seeds, bool(remove_background), sha256_of(WORKFLOW)])
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


# ── commands ─────────────────────────────────────────────────────────────────

def report_audit(base, flow, engine):
    missing_classes, missing_files = audit(base, flow, engine)
    for name in missing_classes:
        print(f"missing   node class {name}")
    for class_type, name in missing_files:
        print(f"missing   model file {name} (for {class_type})")
    return missing_classes, missing_files


def cmd_check(args):
    base = server_url(args.allow_remote)
    stats = call(base, "GET", "/system_stats")
    for device in stats.get("devices", []):
        vram = device.get("vram_total")
        print(f"device    {device.get('name', '?')}" + (f", {vram / (1 << 30):.0f} GB VRAM" if vram else ""))
    flow = load_workflow()
    bad = False
    for engine in ("trellis2", "pixal3d"):
        print(f"engine    {engine}")
        missing = report_audit(base, flow, engine)
        bad = bad or any(missing)
    if bad:
        raise Refused("the server is missing what the workflow needs; install the custom nodes and models it names")
    print("ok        every node class and model file the workflow names is on the server")
    return EXIT_OK


def common(args):
    flow = load_workflow()
    data, kind = read_image(args.image)
    seed = args.seed
    engine = args.engine
    use_bg = not args.no_remove_background
    image_sha = hashlib.sha256(data).hexdigest()
    seeds = [seed + i for i in range(len(BINDINGS["seeds"]))] if seed is not None else seeds_of(flow)
    return flow, data, kind, engine, seed, use_bg, image_sha, seeds


def cmd_plan(args):
    flow, data, kind, engine, seed, use_bg, image_sha, seeds = common(args)
    print(f"image       {Path(args.image).name}, {len(data)} bytes, sha256 {image_sha[:16]}")
    print(f"engine      {engine} (node {BINDINGS['trellis2'][0]} = {engine == 'trellis2'})")
    print(f"background  {'removed first' if use_bg else 'kept as is'}")
    print(f"seeds       {seeds}")
    classes, files = pick(engine, flow)
    print(f"needs       {len(classes)} node classes, {len(files)} model files")
    for _, _, name in files:
        print(f"            {name}")
    print("nothing was sent")
    return EXIT_OK


def cmd_run(args):
    flow, data, kind, engine, seed, use_bg, image_sha, seeds = common(args)
    out = Path(args.out)
    key = request_key(image_sha, engine, seeds, use_bg)
    ledger = load_ledger(out) if out.exists() else {"tasks": []}
    for task in reversed(ledger["tasks"]):
        if task.get("key") == key and task.get("status") == "done" and all((out / f["name"]).is_file() for f in task["files"]):
            print(f"reuse     prompt {task['prompt_id']} already made {', '.join(f['name'] for f in task['files'])}; nothing posted")
            return EXIT_OK

    base = server_url(args.allow_remote)
    missing = report_audit(base, flow, engine)
    if any(missing):
        raise Refused("the server is missing what the workflow needs (listed above); nothing was sent")
    print(f"request   {engine}, seeds {seeds}, background {'removed' if use_bg else 'kept'}, image sha256 {image_sha[:16]}, server {urllib.parse.urlsplit(base).netloc}")
    if not args.confirm:
        print("dry run   nothing was uploaded or queued. Add --confirm to run it.")
        return EXIT_OK

    name = f"rosw_{image_sha[:12]}{Path(args.image).suffix.lower()}"
    body, content_type = multipart(name, data, kind)
    uploaded = call(base, "POST", "/upload/image", body, {"Content-Type": content_type})
    remote_name = uploaded.get("name") or name
    if uploaded.get("subfolder"):
        remote_name = f"{uploaded['subfolder']}/{remote_name}"
    prompt = patched(flow, remote_name, engine, seed, use_bg)
    queued = call(base, "POST", "/prompt", json.dumps({"prompt": prompt, "client_id": uuid.uuid4().hex}).encode(),
                  {"Content-Type": "application/json"})
    if queued.get("node_errors"):
        raise Refused(f"the server rejected the workflow: {json.dumps(queued['node_errors'])[:300]}")
    prompt_id = queued.get("prompt_id")
    if not prompt_id:
        raise Refused("the server did not return a prompt id")
    task = {"key": key, "prompt_id": prompt_id, "engine": engine, "seeds": seeds, "remove_background": use_bg,
            "image_sha256": image_sha, "queued": stamp(now()), "status": "queued", "files": []}
    ledger["tasks"].append(task)
    out.mkdir(parents=True, exist_ok=True)
    save_ledger(out, ledger)
    print(f"queued    prompt {prompt_id}")

    entry = wait_for(base, prompt_id, args.timeout, args.interval)
    files = outputs(entry)
    if not files:
        task["status"] = "failed"
        save_ledger(out, ledger)
        raise Refused("the workflow finished but its Save 3D node returned no file; open the prompt in ComfyUI to see why")
    for item in files:
        query = urllib.parse.urlencode({"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")})
        target = out / Path(item["filename"]).name
        try:
            found = download(f"{base}/view?{query}", target)
        except DownloadError as problem:
            raise Refused(f"{problem}. The prompt {prompt_id} is done on the server; run `status {prompt_id}` and download again.") from None
        task["files"].append({"name": target.name, "bytes": found["bytes"], "sha256": found["sha256"]})
        print(f"kept      {target}  {found['bytes']} bytes")
    task["status"] = "done"
    task["finished"] = stamp(now())
    save_ledger(out, ledger)
    print("done      keep the file through the studio's own step if this is part of a run; this client writes only to --out")
    return EXIT_OK


def wait_for(base, prompt_id, timeout, interval):
    deadline = time.monotonic() + timeout
    while True:
        found = call(base, "GET", f"/history/{urllib.parse.quote(prompt_id)}")
        entry = found.get(prompt_id)
        if entry:
            status = entry.get("status") or {}
            if status.get("status_str") == "error":
                raise Refused(f"the workflow failed on the server: {error_text(status)}")
            if status.get("completed", True) and entry.get("outputs") is not None:
                return entry
        if time.monotonic() >= deadline:
            raise Refused(f"still running after {timeout} s. It was not cancelled; check it with: comfy_client.py status {prompt_id}")
        time.sleep(interval)


def error_text(status):
    for event in status.get("messages", []):
        if isinstance(event, list) and len(event) == 2 and isinstance(event[1], dict) and event[0] == "execution_error":
            data = event[1]
            return f"{data.get('node_type', '?')}: {str(data.get('exception_message', '')).strip()[:200]}"
    return "no reason given"


def outputs(entry):
    """The files the Save 3D node reported: any dict with a filename, however the server nests it."""
    node = entry.get("outputs", {}).get(BINDINGS["output"][0], {})
    found = []

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("filename"), str):
                found.append(value)
            else:
                for inner in value.values():
                    walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)
        elif isinstance(value, str) and value.lower().endswith((".glb", ".gltf", ".obj", ".fbx", ".usd", ".usdz", ".ply", ".stl")):
            found.append({"filename": value.rsplit("/", 1)[-1], "subfolder": value.rsplit("/", 1)[0] if "/" in value else "", "type": "output"})

    walk(node)
    return found


def cmd_status(args):
    base = server_url(args.allow_remote)
    entry = call(base, "GET", f"/history/{urllib.parse.quote(args.prompt_id)}").get(args.prompt_id)
    if not entry:
        queue = call(base, "GET", "/queue")
        ids = [item[1] for item in queue.get("queue_running", []) + queue.get("queue_pending", []) if len(item) > 1]
        print("running or waiting" if args.prompt_id in ids else "unknown to the server")
        return EXIT_OK
    status = entry.get("status") or {}
    print(f"status    {status.get('status_str', 'done')}")
    for item in outputs(entry):
        print(f"file      {item.get('subfolder', '')}/{item['filename']}".replace("//", "/"))
    return EXIT_OK


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--allow-remote", action="store_true", help="allow a server on another machine (https only)")
    sub = parser.add_subparsers(dest="command", required=True)

    def image_options(p):
        p.add_argument("--image", required=True)
        p.add_argument("--engine", choices=("trellis2", "pixal3d"), default="trellis2")
        p.add_argument("--seed", type=int, help="first seed; the four samplers use seed, seed+1, seed+2, seed+3")
        p.add_argument("--no-remove-background", action="store_true")

    sub.add_parser("check").set_defaults(run=cmd_check)
    p = sub.add_parser("plan")
    image_options(p)
    p.set_defaults(run=cmd_plan)
    p = sub.add_parser("run")
    image_options(p)
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=int, default=3600)
    p.add_argument("--interval", type=float, default=3.0)
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(run=cmd_run)
    p = sub.add_parser("status")
    p.add_argument("prompt_id")
    p.set_defaults(run=cmd_status)
    return parser


def main(argv=None):
    open_console()
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except Refused as problem:
        print(f"REFUSED   {problem}", file=sys.stderr)
        return EXIT_REFUSED
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
