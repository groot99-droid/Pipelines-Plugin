"""The Meshy client: text or an image to a 3D model, and the steps after it,
for the studio's asset-3d pipeline. Stdlib HTTP; requires pyyaml (the spec).

    python studio/pipeline/meshy_client.py balance
    python studio/pipeline/meshy_client.py animations [--search WORD] [--category NAME]
    python studio/pipeline/meshy_client.py create <op> <run-id> --name ASSET [inputs] [--set KEY=VALUE ...] [--confirm]
    python studio/pipeline/meshy_client.py status   <run-id>
    python studio/pipeline/meshy_client.py wait     <run-id> [--name ASSET] [--timeout S] [--interval S]
    python studio/pipeline/meshy_client.py download <run-id> --name ASSET --op OP [--format glb] [--part PART] [--thumbnail]

Ops (see OPS): preview and refine (text to 3D, in two steps), image (image
to 3D), remesh, retexture, rig, animate. Inputs: --prompt TEXT, --image
PATH|URL, --model PATH|URL, and --from ASSET:OP for a task this run already
made. Any other field goes in with --set, and only the fields OPS lists for
the op are accepted, so a misspelt field is refused instead of being ignored
by the service.

`create` without --confirm is a dry run: it prints the request it would send,
the credits it would spend and the balance, and writes nothing. With
--confirm it posts only when the run is at its execute stage and the author's
execute go-ahead is recorded. Every task goes into the run folder's
meshy_tasks.json. A create that matches a recorded task (the same asset, op
and request) reuses it and posts nothing, so a re-run after a crash never pays
twice. A different request for an op already made needs --again.

`download` asks the service for the task afresh, because its file links are
signed and expire, and writes the file into the run folder's meshy/ through a
.part file checked against Content-Length. Kept files go to the assets folder
through studio_run.py keep, never from here. The links are never stored.

The key is MESHY_API_KEY, read from the user key file (ROSW_KEYS_FILE, else
~/.rosw/keys.env, written by docs/setup_keys.py) or else the environment. Its
value is never printed. MESHY_BASE_URL points the client at another server
(the tests run a fake one); it must be https unless it is this machine.

Exit codes: 0 done, 1 refused or the service said no, 2 usage error.
"""

import argparse
import base64
import hashlib
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage, current_stage,
    latest_confirmation, load_state, now, open_console, read_text, stamp, write_text,
)

BASE_URL = "https://api.meshy.ai"
KEY_NAME = "MESHY_API_KEY"
PLACEHOLDERS = {"your-key-here", "Add_Key"}  # "no key yet", as llm.py and setup_keys.py
LEDGER = "meshy_tasks.json"
DOWNLOADS = "meshy"
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_MODEL_BYTES = 100 * 1024 * 1024  # a model sent as a data URI; a URL may be larger
MAX_PROMPT = 800
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELED"}
IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
MODEL_SUFFIXES = {".glb", ".gltf", ".obj", ".fbx", ".stl"}

# What each op posts, from docs.meshy.ai/en/api (read 2026-10-29). `inputs`
# maps an input flag to the field it fills; `from` lists the ops a --from
# task may be, and the field its id goes in. `fields` is everything --set may
# give. Deprecated fields are left out on purpose.
_FORMATS = "target_formats"
OPS = {
    "preview": {
        "path": "/openapi/v2/text-to-3d", "fixed": {"mode": "preview"},
        "inputs": {"prompt": "prompt"}, "requires": ["prompt"],
        "fields": {"model_type", "ai_model", "geometry_resolution", "should_remesh", "topology",
                   "decimation_mode", "target_polycount", "pose_mode", "moderation", _FORMATS,
                   "alpha_thumbnail", "auto_size", "origin_at"},
    },
    "refine": {
        "path": "/openapi/v2/text-to-3d", "fixed": {"mode": "refine"},
        "inputs": {"prompt": "texture_prompt", "image": "texture_image_url"},
        "from": (["preview"], "preview_task_id"), "requires": ["from"],
        "fields": {"enable_pbr", "texture_resolution", "ai_model", "remove_lighting", _FORMATS,
                   "alpha_thumbnail", "auto_size", "origin_at", "moderation"},
    },
    "image": {
        "path": "/openapi/v1/image-to-3d", "fixed": {},
        "inputs": {"image": "image_url", "prompt": "texture_prompt"}, "requires": ["image"],
        "fields": {"model_type", "ai_model", "geometry_resolution", "should_texture", "enable_pbr",
                   "texture_resolution", "texture_image_url", "should_remesh", "topology",
                   "decimation_mode", "target_polycount", "save_pre_remeshed_model", "pose_mode",
                   "image_enhancement", "remove_lighting", "moderation", _FORMATS, "auto_size",
                   "origin_at", "alpha_thumbnail", "multi_view_thumbnails"},
    },
    "remesh": {
        "path": "/openapi/v1/remesh", "fixed": {},
        "inputs": {"model": "model_url"},
        "from": (["preview", "refine", "image", "remesh", "retexture"], "input_task_id"),
        "requires": ["from|model"],
        "fields": {_FORMATS, "topology", "target_polycount", "decimation_mode", "alpha_thumbnail"},
    },
    "retexture": {
        "path": "/openapi/v1/retexture", "fixed": {},
        "inputs": {"model": "model_url", "prompt": "text_style_prompt", "image": "image_style_url"},
        "from": (["preview", "refine", "image", "remesh", "retexture"], "input_task_id"),
        "requires": ["from|model", "prompt|image"],
        "fields": {"ai_model", "enable_original_uv", "enable_pbr", "texture_resolution",
                   "remove_lighting", _FORMATS, "alpha_thumbnail"},
    },
    "rig": {
        "path": "/openapi/v1/rigging", "fixed": {},
        "inputs": {"model": "model_url"},
        "from": (["refine", "image", "remesh", "retexture"], "input_task_id"),
        "requires": ["from|model"],
        "fields": {"height_meters"},
    },
    "animate": {
        "path": "/openapi/v1/animations", "fixed": {},
        "inputs": {}, "from": (["rig"], "rig_task_id"), "requires": ["from"],
        "fields": {"action_id", "action_ids", "post_process"},
    },
}

# Where a finished task keeps its files. Model tasks list them under
# model_urls by format; rig and animate name each file under `result`.
RESULT_FILES = {
    "rig": {"glb": "rigged_character_glb_url", "fbx": "rigged_character_fbx_url"},
    "animate": {"glb": "animation_glb_url", "fbx": "animation_fbx_url", "usdz": "processed_usdz_url"},
}
RIG_PARTS = {"walking", "running"}  # rig's basic_animations: <part>_glb_url, <part>_fbx_url

_LITE = {"meshy-6-lite", "meshy-t2", "meshy-t2.5"}


def estimate_credits(op, body):
    """What the request should cost, by Meshy's pricing page (2026-10-29). An
    estimate: the task's consumed_credits, logged after it runs, is the fact."""
    lite = body.get("ai_model") in _LITE or body.get("model_type") == "smart-topology"
    ultra = 5 if body.get("geometry_resolution") in ("2k", "4k") else 0
    eight_k = body.get("texture_resolution") == "8k"
    if op == "preview":
        return (5 if lite else 20) + ultra
    if op in ("refine", "retexture"):
        return 15 if eight_k else 10
    if op == "image":
        if body.get("should_texture") is False:
            return (5 if lite else 20) + ultra
        return ((20 if lite else 35) if eight_k else (15 if lite else 30)) + ultra
    if op in ("remesh", "rig"):
        return 5
    if op == "animate":
        return 3 * len(body.get("action_ids") or [body.get("action_id")])
    return None


# ── the key ──────────────────────────────────────────────────────────────────

def user_keys_file():
    """The per-user key file, outside the repo. The same rule as
    creative-writing/pipeline/llm.py user_keys_file; a test keeps them in step."""
    return os.environ.get("ROSW_KEYS_FILE") or os.path.join(
        os.path.expanduser("~"), ".rosw", "keys.env")


def read_key_file(path):
    """KEY=VALUE lines, as llm.py _load_env_file reads them. Never printed."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return {}
    found = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        if value and value not in PLACEHOLDERS:
            found[key.strip()] = value
    return found


def api_key():
    value = read_key_file(user_keys_file()).get(KEY_NAME) or os.environ.get(KEY_NAME, "")
    if not value or value in PLACEHOLDERS:
        raise Refused(f"{KEY_NAME} is not set. The author adds it with python docs/setup_keys.py "
                      "(it goes to ~/.rosw/keys.env, outside the repo).")
    return value


def base_url():
    url = (os.environ.get("MESHY_BASE_URL") or BASE_URL).rstrip("/")
    parts = urllib.parse.urlsplit(url)
    local = parts.hostname in ("127.0.0.1", "localhost", "::1")
    if parts.scheme != "https" and not (parts.scheme == "http" and local):
        raise Usage(f"MESHY_BASE_URL must be https (or http on this machine), not {parts.scheme}://")
    return url


# ── HTTP ─────────────────────────────────────────────────────────────────────

def call(method, path, body=None, retries=3):
    """One API request, as JSON. A 429 waits Retry-After and tries again."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(retries + 1):
        request = urllib.request.Request(base_url() + path, data=data, method=method)
        request.add_header("Authorization", f"Bearer {api_key()}")
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw.strip() else {}
        except urllib.error.HTTPError as err:
            detail = service_message(err)
            if err.code == 429 and attempt < retries and not detail.startswith("NoMorePendingTasks"):
                time.sleep(min(float(err.headers.get("Retry-After") or 5), 60))
                continue
            raise Refused(f"Meshy said {err.code} to {method} {path}: {detail}") from None
        except urllib.error.URLError as err:
            raise Refused(f"could not reach Meshy ({err.reason})") from None
    raise Refused(f"Meshy kept saying 429 to {method} {path}")


def service_message(err):
    try:
        found = json.loads(err.read().decode("utf-8", "replace"))
        text = found.get("message") or found.get("error") or json.dumps(found)
    except (ValueError, AttributeError):
        text = err.reason or ""
    return " ".join(str(text).split())[:300]


def fetch_file(url, target):
    """A result file, into target, through target.part. No key is sent: the
    link is signed by the service and goes to its file host."""
    if urllib.parse.urlsplit(url).scheme not in ("https", "http"):
        raise Refused("the service gave a file link that is not http(s)")
    part = target.with_name(target.name + ".part")
    target.parent.mkdir(parents=True, exist_ok=True)
    digest, size = hashlib.sha256(), 0
    try:
        with urllib.request.urlopen(url, timeout=120) as response, part.open("wb") as out:
            expected = response.headers.get("Content-Length")
            while True:
                chunk = response.read(1 << 16)
                if not chunk:
                    break
                out.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if expected is not None and int(expected) != size:
            raise Refused(f"{target.name}: got {size} bytes of {expected}. Nothing was kept; download again.")
        os.replace(part, target)
    except (urllib.error.URLError, http.client.HTTPException, OSError) as err:
        raise Refused(f"{target.name}: the download failed ({getattr(err, 'reason', None) or type(err).__name__}). "
                      "Nothing was kept; download again.") from None
    finally:
        if part.exists():
            part.unlink()
    return {"file": target.name, "bytes": size, "sha256": digest.hexdigest()}


# ── the run and its ledger ───────────────────────────────────────────────────

def run_folder(env, run_id):
    load_state(env, run_id)  # the run exists and its state parses
    return env.run_dir(run_id)


def load_ledger(run_dir):
    path = run_dir / LEDGER
    if not path.is_file():
        return {"tasks": []}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as err:
        raise Usage(f"{path} does not parse: {err}. It is written only by meshy_client.py.")


def save_ledger(run_dir, ledger):
    write_text(run_dir / LEDGER, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")


def find(ledger, name, op):
    """The latest task this run made for an asset and op."""
    for task in reversed(ledger["tasks"]):
        if task["name"] == name and task["op"] == op:
            return task
    return None


def require_go_ahead(env, run_id):
    state = load_state(env, run_id)
    if state["status"] != "active":
        raise Refused(f"the run is {state['status']}")
    stage = current_stage(env, state)
    if stage is None or stage["id"] != "execute":
        raise Refused(f"the run is at `{stage['id'] if stage else 'its end'}`. "
                      "Meshy is called at execute, after the recipe was confirmed.")
    if not latest_confirmation(state, "execute"):
        raise Refused("no execute go-ahead is recorded. Show the recipe, and after a clear yes: "
                      f'studio_run.py confirm {run_id} execute --words "<what the author said>"')
    if env.pipeline(state["pipeline"]).get("class") != "spend":
        raise Refused(f"`{state['pipeline']}` does not spend credits, so it does not call Meshy")


# ── building a request ───────────────────────────────────────────────────────

def parse_value(text):
    """--set values are JSON where they parse (true, 30000, ["glb","fbx"]), else text."""
    try:
        return json.loads(text)
    except ValueError:
        return text


def data_uri(path, kinds, limit, what):
    path = Path(path)
    if not path.is_file():
        raise Usage(f"{path} is not a file")
    suffix = path.suffix.lower()
    if suffix not in kinds:
        raise Usage(f"{what} must be one of {', '.join(sorted(kinds))}, not {suffix or 'no suffix'}")
    raw = path.read_bytes()
    if len(raw) > limit:
        raise Usage(f"{path.name} is {len(raw) // (1024 * 1024)} MB; the service takes {limit // (1024 * 1024)} MB")
    mime = kinds[suffix] if isinstance(kinds, dict) else "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def source_value(given, kinds, limit, what):
    """A URL is passed as it is; a local file goes as a data URI."""
    if urllib.parse.urlsplit(given).scheme in ("http", "https"):
        return given
    return data_uri(given, kinds, limit, what)


def build_request(op, args, ledger):
    spec = OPS[op]
    body = dict(spec["fixed"])
    given = {"prompt": args.prompt, "image": args.image, "model": args.model}
    for flag, value in given.items():
        if value is None:
            continue
        if flag not in spec["inputs"]:
            raise Usage(f"`{op}` takes no --{flag}")
        if flag == "prompt":
            if len(value) > MAX_PROMPT:
                raise Usage(f"--prompt is {len(value)} characters; the service takes {MAX_PROMPT}")
            body[spec["inputs"][flag]] = value
        elif flag == "image":
            body[spec["inputs"][flag]] = source_value(value, IMAGE_TYPES, MAX_IMAGE_BYTES, "--image")
        else:
            body[spec["inputs"][flag]] = source_value(value, MODEL_SUFFIXES, MAX_MODEL_BYTES, "--model")
    if args.source:
        if "from" not in spec:
            raise Usage(f"`{op}` takes no --from")
        ops, field = spec["from"]
        name, _, from_op = args.source.partition(":")
        if from_op not in ops:
            raise Usage(f"--from for `{op}` is ASSET:OP with OP one of {', '.join(ops)}")
        task = find(ledger, name, from_op)
        if task is None:
            raise Refused(f"this run made no `{from_op}` for `{name}`")
        if task.get("status") != "SUCCEEDED":
            raise Refused(f"{name}:{from_op} is {task.get('status')}, not SUCCEEDED. Wait for it first.")
        body[field] = task["id"]
    for item in args.set or []:
        key, sep, value = item.partition("=")
        if not sep:
            raise Usage(f"--set {item}: write KEY=VALUE")
        if key not in spec["fields"]:
            raise Usage(f"`{op}` has no field `{key}`. It takes: {', '.join(sorted(spec['fields']))}")
        body[key] = parse_value(value)
    present = {"prompt": args.prompt, "image": args.image, "model": args.model, "from": args.source}
    for need in spec["requires"]:
        choices = need.split("|")
        found = [c for c in choices if present.get(c) is not None]
        if not found:
            raise Usage(f"`{op}` needs " + " or ".join(f"--{c}" for c in choices))
        if len(found) > 1 and need == "prompt|image":
            raise Usage(f"`{op}` takes --prompt or --image, not both")
    if op == "animate" and ("action_id" in body) == ("action_ids" in body):
        raise Usage("`animate` needs exactly one of --set action_id=N or --set action_ids=[N,...]")
    return spec["path"], body


def request_hash(path, body):
    return hashlib.sha256(json.dumps([path, body], sort_keys=True).encode("utf-8")).hexdigest()


def shown(body):
    """The body as it may be printed and logged: a data URI becomes its size and hash."""
    out = {}
    for key, value in body.items():
        if isinstance(value, str) and value.startswith("data:"):
            head, _, payload = value.partition(",")
            out[key] = f"{head},<{len(payload) * 3 // 4} bytes, sha256 {hashlib.sha256(payload.encode()).hexdigest()[:12]}>"
        else:
            out[key] = value
    return out


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_balance(env, args):
    found = call("GET", "/openapi/v1/balance")
    print(f"balance   {found.get('balance')} credits"
          + (f" ({found.get('monthly_credits')} monthly, {found.get('permanent_credits')} permanent)"
             if "monthly_credits" in found else ""))
    return EXIT_OK


def cmd_animations(env, args):
    query = {k: v for k, v in (("search", args.search), ("category", args.category)) if v}
    path = "/openapi/v1/animations/library" + (f"?{urllib.parse.urlencode(query)}" if query else "")
    found = call("GET", path)
    rows = found if isinstance(found, list) else found.get("result") or found.get("data") or []
    for row in rows[: args.limit]:
        print(f"{row.get('action_id'):>6}  {row.get('name')}  ({row.get('category')}"
              + (f" / {row.get('sub_category')}" if row.get("sub_category") else "") + ")")
    print(f"{len(rows)} action(s)" + (f", first {args.limit} shown" if len(rows) > args.limit else ""))
    return EXIT_OK


def cmd_create(env, args):
    run_dir = run_folder(env, args.run_id)
    ledger = load_ledger(run_dir)
    path, body = build_request(args.op, args, ledger)
    digest = request_hash(path, body)
    cost = estimate_credits(args.op, body)
    earlier = find(ledger, args.name, args.op)
    if earlier and earlier["request_sha"] == digest and earlier.get("status") not in ("FAILED", "CANCELED"):
        print(f"reused    {args.name}:{args.op} is task {earlier['id']} ({earlier.get('status')}). "
              "The same request was made before; nothing was posted.")
        return EXIT_OK
    print(f"request   POST {path}")
    print(json.dumps(shown(body), indent=2, ensure_ascii=False))
    print(f"estimate  {cost} credits (Meshy's pricing page; the task reports what it spent)")
    if earlier and earlier["request_sha"] != digest and not args.again:
        raise Refused(f"{args.name}:{args.op} was made before with a different request (task "
                      f"{earlier['id']}). A changed request is a new recipe step; pass --again "
                      "if the confirmed recipe says to make it again.")
    if not args.confirm:
        try:
            cmd_balance(env, args)
        except Refused as problem:
            print(f"balance   unknown: {problem}")
        print("DRY RUN   nothing was posted and nothing was written. Add --confirm after the go-ahead.")
        return EXIT_OK
    require_go_ahead(env, args.run_id)
    found = call("POST", path, body)
    task_id = found.get("result")
    if not isinstance(task_id, str) or not task_id:
        raise Refused(f"Meshy answered without a task id: {json.dumps(found)[:200]}")
    ledger["tasks"].append({
        "name": args.name, "op": args.op, "id": task_id, "endpoint": path,
        "request_sha": digest, "request": shown(body), "estimate": cost,
        "status": "PENDING", "created": stamp(now()), "downloads": [],
    })
    save_ledger(run_dir, ledger)
    print(f"posted    {args.name}:{args.op} is task {task_id}")
    return EXIT_OK


def refresh(task):
    """Ask the service for a task. Its record is updated with the status and
    what it spent; its signed links are returned, never stored."""
    found = call("GET", f"{task['endpoint']}/{task['id']}")
    task["status"] = found.get("status", task.get("status"))
    task["progress"] = found.get("progress")
    if found.get("consumed_credits") is not None:
        task["consumed_credits"] = found["consumed_credits"]
    error = (found.get("task_error") or {}).get("message")
    if error:
        task["error"] = " ".join(str(error).split())[:300]
    files = sorted((found.get("model_urls") or {}).keys())
    if files:
        task["formats"] = files
    return found


def describe(task):
    spent = f", spent {task['consumed_credits']}" if task.get("consumed_credits") is not None else ""
    progress = f" {task['progress']}%" if task.get("progress") not in (None, 100) else ""
    error = f", error: {task['error']}" if task.get("error") else ""
    return f"{task['name']}:{task['op']:<9} {task['id']}  {task.get('status')}{progress}{spent}{error}"


def cmd_status(env, args):
    run_dir = run_folder(env, args.run_id)
    ledger = load_ledger(run_dir)
    if not ledger["tasks"]:
        print("no Meshy task in this run")
        return EXIT_OK
    for task in ledger["tasks"]:
        if task.get("status") not in TERMINAL and not args.offline:
            refresh(task)
        print(describe(task))
    if not args.offline:
        save_ledger(run_dir, ledger)
    return EXIT_OK


def cmd_wait(env, args):
    run_dir = run_folder(env, args.run_id)
    ledger = load_ledger(run_dir)
    waiting = [t for t in ledger["tasks"]
               if t.get("status") not in TERMINAL and (args.name is None or t["name"] == args.name)]
    if not waiting:
        print("nothing to wait for")
    deadline = time.monotonic() + args.timeout
    while waiting:
        for task in list(waiting):
            refresh(task)
            if task["status"] in TERMINAL:
                waiting.remove(task)
                print(describe(task))
        save_ledger(run_dir, ledger)
        if waiting:
            if time.monotonic() > deadline:
                raise Refused(f"{len(waiting)} task(s) still running after {args.timeout}s. "
                              "Run wait again; nothing is lost.")
            time.sleep(args.interval)
    failed = [t for t in ledger["tasks"] if t.get("status") in ("FAILED", "CANCELED")
              and (args.name is None or t["name"] == args.name)]
    return EXIT_REFUSED if failed else EXIT_OK


def result_link(task, found, fmt, part):
    if task["op"] in RESULT_FILES:
        result = found.get("result") or {}
        if part:
            if task["op"] != "rig" or part not in RIG_PARTS:
                raise Usage(f"--part is for rig: one of {', '.join(sorted(RIG_PARTS))}")
            return (result.get("basic_animations") or {}).get(f"{part}_{fmt}_url")
        key = RESULT_FILES[task["op"]].get(fmt)
        if key is None:
            raise Usage(f"`{task['op']}` gives {', '.join(RESULT_FILES[task['op']])}, not {fmt}")
        return result.get(key)
    if part:
        raise Usage("--part is for rig")
    return (found.get("model_urls") or {}).get(fmt)


def cmd_download(env, args):
    run_dir = run_folder(env, args.run_id)
    require_go_ahead(env, args.run_id)
    ledger = load_ledger(run_dir)
    task = find(ledger, args.name, args.op)
    if task is None:
        raise Refused(f"this run made no `{args.op}` for `{args.name}`")
    found = refresh(task)
    save_ledger(run_dir, ledger)
    if task["status"] != "SUCCEEDED":
        raise Refused(f"{args.name}:{args.op} is {task['status']}; there is nothing to download")
    wanted = [(result_link(task, found, args.format, args.part),
               f"{args.name}-{args.op}{'-' + args.part if args.part else ''}.{args.format}")]
    if args.thumbnail:
        wanted.append((found.get("thumbnail_url"), f"{args.name}-{args.op}-thumb.png"))
    for link, file_name in wanted:
        if not link:
            raise Refused(f"{args.name}:{args.op} has no {file_name.rsplit('.', 1)[1]} file. "
                          f"It has: {', '.join(task.get('formats') or []) or 'none listed'}")
        got = fetch_file(link, run_dir / DOWNLOADS / file_name)
        got["at"] = stamp(now())
        task["downloads"] = [d for d in task.get("downloads", []) if d["file"] != got["file"]] + [got]
        save_ledger(run_dir, ledger)
        print(f"saved     {DOWNLOADS}/{got['file']}  {got['bytes']} bytes  sha256 {got['sha256']}")
    return EXIT_OK


def build_parser():
    parser = argparse.ArgumentParser(prog="meshy_client.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    parser.add_argument("--assets-dir", help="where kept artifacts go (default: from the spec)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("balance", help="the account's credits (free)")
    p.set_defaults(run=cmd_balance)
    p = sub.add_parser("animations", help="the animation library, for animate's action_id (free)")
    p.add_argument("--search")
    p.add_argument("--category", help="WalkAndRun, BodyMovements, DailyActions, Fighting or Dancing")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(run=cmd_animations)
    p = sub.add_parser("create", help="post one task; a dry run without --confirm")
    p.add_argument("op", choices=sorted(OPS))
    p.add_argument("run_id")
    p.add_argument("--name", required=True, help="the asset's slug in this run, e.g. lantern")
    p.add_argument("--prompt")
    p.add_argument("--image", help="a png, jpg or webp file, or an https link")
    p.add_argument("--model", help="a glb, gltf, obj, fbx or stl file, or an https link")
    p.add_argument("--from", dest="source", help="ASSET:OP, a task this run made")
    p.add_argument("--set", action="append", metavar="KEY=VALUE")
    p.add_argument("--again", action="store_true", help="make an op again with a changed request")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(run=cmd_create)
    p = sub.add_parser("status", help="the run's tasks, refreshed")
    p.add_argument("run_id")
    p.add_argument("--offline", action="store_true", help="print the ledger; ask the service nothing")
    p.set_defaults(run=cmd_status)
    p = sub.add_parser("wait", help="poll until the run's tasks finish")
    p.add_argument("run_id")
    p.add_argument("--name")
    p.add_argument("--timeout", type=float, default=1800)
    p.add_argument("--interval", type=float, default=10)
    p.set_defaults(run=cmd_wait)
    p = sub.add_parser("download", help="a finished task's file, into the run folder")
    p.add_argument("run_id")
    p.add_argument("--name", required=True)
    p.add_argument("--op", required=True, choices=sorted(OPS))
    p.add_argument("--format", default="glb", choices=["glb", "fbx", "obj", "usdz", "stl", "3mf", "blend"])
    p.add_argument("--part", help="rig only: walking or running")
    p.add_argument("--thumbnail", action="store_true", help="also save the task's thumbnail")
    p.set_defaults(run=cmd_download)
    return parser


def main(argv=None):
    open_console()
    args = build_parser().parse_args(argv)
    try:
        env = Env(args.spec, args.runs_dir, args.vault_dir, args.context_dir, args.assets_dir)
        return args.run(env, args)
    except Refused as problem:
        print(f"REFUSED   {problem}", file=sys.stderr)
        return EXIT_REFUSED
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
