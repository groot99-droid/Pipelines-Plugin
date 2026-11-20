"""vast: an MCP server that rents Vast.ai GPUs and runs Blender, ComfyUI and other work on them.

Wire: JSON-RPC 2.0, one message per line on stdin and stdout (the stdio transport of the Model Context
Protocol). Logs go to stderr. Stdlib only; ssh and scp are the system's own OpenSSH.

Spending is guarded here, in the server, because nothing outside it can refuse a tool call:
  * `quote` prices an offer against the biweekly band budgets in limits.json and spends nothing;
  * `rent` needs a fresh, unused quote and confirm=true; without confirm it is a dry run;
  * every rental carries a deadline (the hours its band has left), an on-box watchdog that stops the
    instance at that deadline, and `reap` for anything that outlives it;
  * `run_shell`, `stop`, `destroy` and `reap` need confirm=true too;
  * every result carries a `spend` block: live rentals, $ so far, and the hours each band has left.

Environment:
  VAST_API_KEY     the key (or VAST_KEYS_FILE naming a NAME=value file that holds it)
  VAST_SSH_KEY     private key path, default ~/.ssh/id_ed25519 (only the .pub is sent)
  VAST_STATE_DIR   ledger and known_hosts, default ~/.vast-mcp
  VAST_WORK_DIR    the one local folder uploads come from and downloads go to, default ./vast-work
  VAST_BASE_URL    API base for tests (https, or http on localhost)

Usage: python server.py            serve on stdio
       python server.py --selftest run a handshake and tools/list in-process and exit
"""

from __future__ import annotations

import json
import math
import os
import re
import secrets
import shlex
import socket
import sys
import time
import traceback
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger as ledger_mod  # noqa: E402
import remote as remote_mod  # noqa: E402
from vast_api import VastAPI, VastError, has_key  # noqa: E402

SERVER_NAME = "vast"
SERVER_TITLE = "Vast.ai GPU"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
DEFAULT_PROTOCOL_VERSION = "2025-11-25"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
MAX_LINE = 16 * 1024 * 1024

WATCHDOG = ("(sleep {seconds}; curl -s -X PUT -H \"Authorization: Bearer $CONTAINER_API_KEY\" "
            "-H 'Content-Type: application/json' -d '{{\"state\":\"stopped\"}}' "
            "\"https://console.vast.ai/api/v0/instances/$CONTAINER_ID/\") >/dev/null 2>&1 &")
CURL_FIRST = ("command -v curl >/dev/null 2>&1 || (apt-get update -qq && "
              "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq curl >/dev/null 2>&1)")
LABEL_PREFIX = "claude-vast-"
JOB_ID = re.compile(r"^j_[0-9a-f]{8}$")

INSTRUCTIONS = (
    "Rent Vast.ai GPUs and run Blender, ComfyUI and other work on them. Renting costs real money. "
    "The order is: account and search_offers (free) -> quote (free; prices an offer against the "
    "author's biweekly band budgets) -> show the author the quote -> rent with confirm=true only "
    "after the author says yes -> wait_ready -> upload, run_recipe, download -> destroy. "
    "Never pass confirm=true to rent, run_shell, stop, destroy or reap without the author's go-ahead "
    "for that call. Each result's `spend` block shows what is running and costing money; when work "
    "is done, destroy the instance. ComfyUI listens on the instance's localhost only: open a tunnel "
    "and point COMFY_URL at http://127.0.0.1:<port>."
)


class Tool(NamedTuple):
    name: str
    title: str
    description: str
    input_schema: dict
    handler: object
    read_only: bool = True
    spends: bool = False


class Context(NamedTuple):
    environ: dict
    ledger: object
    remote: object
    recipes: dict
    api_factory: object
    clock: object = time.time
    sleep: object = time.sleep
    log: object = None

    def api(self):
        return self.api_factory(self.environ)


def make_context(environ=None, clock=time.time, sleep=time.sleep, api_factory=None, runner=None,
                 popen=None, log=None):
    environ = dict(os.environ if environ is None else environ)
    folder = ledger_mod.state_dir(environ)
    ledger = ledger_mod.Ledger(folder, ledger_mod.load_limits(), clock=clock)
    kwargs = {}
    if runner is not None:
        kwargs["runner"] = runner
    if popen is not None:
        kwargs["popen"] = popen
    remote = remote_mod.Remote(environ, folder, **kwargs)
    return Context(environ=environ, ledger=ledger, remote=remote, recipes=remote_mod.load_recipes(),
                   api_factory=api_factory or (lambda env: VastAPI(env)), clock=clock, sleep=sleep,
                   log=log)


# ── helpers ──────────────────────────────────────────────────────────────────

def refuse(code, message, hint=None):
    raise VastError(code, message, hint)


def need_confirm(arguments, what, preview):
    if arguments.get("confirm") is not True:
        return {"dry_run": True, "nothing_done": True,
                "to_do_it": f"call again with confirm=true once the author has said yes to {what}",
                **preview}
    return None


def num(value, default=0.0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def trim_offer(offer):
    return {
        "offer_id": offer.get("id"),
        "gpu_name": offer.get("gpu_name"),
        "num_gpus": offer.get("num_gpus"),
        "gpu_ram_gb": round(num(offer.get("gpu_ram")) / 1024, 1),
        "dph_total": round(num(offer.get("dph_total")), 4),
        "reliability": round(num(offer.get("reliability2", offer.get("reliability"))), 4),
        "verified": offer.get("verified"),
        "geolocation": offer.get("geolocation"),
        "cpu_ram_gb": round(num(offer.get("cpu_ram")) / 1024, 1),
        "disk_space_gb": round(num(offer.get("disk_space")), 1),
        "inet_down_mbps": round(num(offer.get("inet_down")), 1),
        "cuda_max_good": offer.get("cuda_max_good"),
    }


def instance_or_refuse(context, instance_id):
    instance = context.api().instance(instance_id)
    if instance is None:
        refuse("no_instance", f"Vast has no instance {instance_id} on this account",
               "instances lists what is running")
    return instance


def running_instance(context, instance_id):
    instance = instance_or_refuse(context, instance_id)
    if instance.get("actual_status") != "running":
        refuse("not_running", f"instance {instance_id} is {instance.get('actual_status') or 'not running yet'}",
               "wait_ready polls until it is running")
    return instance


def onstart_script(environment, deadline_seconds):
    lines = ["#!/bin/bash", CURL_FIRST, WATCHDOG.format(seconds=int(deadline_seconds))]
    lines += environment.get("onstart", [])
    return "\n".join(lines) + "\n"


# ── tools ────────────────────────────────────────────────────────────────────

def t_account(arguments, context):
    if not has_key(context.environ):
        return {"key": "not set", "hint": "set VAST_API_KEY, or VAST_KEYS_FILE naming a file that holds it"}
    user = context.api().user()
    return {"key": "set", "balance_usd": round(num(user.get("balance")), 2),
            "credit_usd": round(num(user.get("credit")), 2)}


def t_list_recipes(arguments, context):
    recipes = context.recipes
    return {
        "job_dir": recipes["job_dir"],
        "environments": {name: {"description": env["description"], "image": env["image"],
                                "disk_gb": env["disk_gb"]} for name, env in recipes["environments"].items()},
        "recipes": {name: {"description": r["description"], "environment": r.get("environment", "any"),
                           "background": bool(r.get("background")), "params": r.get("params", {})}
                    for name, r in recipes["recipes"].items()},
    }


def t_search_offers(arguments, context):
    top = context.ledger.limits["bands"][-1]["max_dph"]
    max_dph = min(num(arguments.get("max_dph"), top), top)
    query = {
        "rentable": {"eq": True},
        "rented": {"eq": False},
        "type": "on-demand",
        "num_gpus": {"eq": int(arguments.get("num_gpus", 1))},
        "dph_total": {"lte": max_dph},
        "reliability2": {"gte": num(arguments.get("min_reliability"), 0.98)},
        "order": [["dph_total", "asc"]],
        "limit": int(arguments.get("limit", 10)),
    }
    if arguments.get("verified", True):
        query["verified"] = {"eq": True}
    if arguments.get("gpu_name"):
        query["gpu_name"] = {"eq": arguments["gpu_name"]}
    if arguments.get("min_gpu_ram_gb"):
        query["gpu_ram"] = {"gte": num(arguments["min_gpu_ram_gb"]) * 1024}
    if arguments.get("min_disk_gb"):
        query["disk_space"] = {"gte": num(arguments["min_disk_gb"])}
    if arguments.get("geolocation"):
        query["geolocation"] = {"in": arguments["geolocation"]}
    offers = [trim_offer(o) for o in context.api().search(query)]
    state = context.ledger.load()
    for offer in offers:
        band = context.ledger.band_for(offer["dph_total"])
        offer["band_hours_left"] = context.ledger.remaining_hours(band, state) if band else 0.0
    return {"offers": offers, "max_dph_searched": max_dph}


def t_quote(arguments, context):
    environment_name = arguments["environment"]
    environment = context.recipes["environments"].get(environment_name)
    if environment is None:
        refuse("bad_environment", f"no environment named {environment_name}", "list_recipes shows them")
    offer = context.api().offer(arguments["offer_id"])
    if offer is None:
        refuse("offer_gone", f"offer {arguments['offer_id']} is no longer rentable", "search_offers again")
    dph = round(num(offer.get("dph_total")), 4)
    band = context.ledger.band_for(dph)
    if band is None:
        refuse("over_ceiling", f"${dph}/hr is above the highest band (${context.ledger.limits['bands'][-1]['max_dph']}/hr)",
               "choose a cheaper offer; the bands are in limits.json")
    remaining = context.ledger.remaining_hours(band)
    if remaining <= 0.01:
        refuse("band_spent", f"the ${band['max_dph']}/hr band has no hours left in this "
               f"{context.ledger.limits.get('window_days', 14)}-day window",
               "choose an offer in a cheaper band, or wait until earlier rentals leave the window")
    hours = min(num(arguments["hours"]), remaining)
    disk = int(arguments.get("disk_gb") or environment["disk_gb"])
    quote = context.ledger.new_quote({
        "offer_id": int(offer["id"]), "dph": dph, "band": band["max_dph"], "environment": environment_name,
        "image": environment["image"], "disk_gb": disk, "cap_hours": round(hours, 3),
        "gpu_name": offer.get("gpu_name"), "num_gpus": offer.get("num_gpus"),
    })
    return {
        "quote_id": quote["quote_id"], "expires_in_seconds": int(quote["expires"] - context.clock()),
        "offer": trim_offer(offer), "environment": environment_name, "image": environment["image"],
        "disk_gb": disk, "dph": dph, "band": f"<= ${band['max_dph']}/hr",
        "band_hours_left_before": remaining, "cap_hours": round(hours, 3),
        "capped": hours < num(arguments["hours"]),
        "worst_case_gpu_cost_usd": round(dph * hours, 2),
        "note": "dph_total is Vast's all-in hourly price as listed; a stopped instance still bills its disk "
                "until destroyed. The on-box watchdog stops the instance at cap_hours.",
        "leaves_this_machine": ["the image name and the onstart script, to Vast and the host",
                                "your ssh public key, to Vast and the host",
                                "every file you upload, to the host"],
    }


def t_rent(arguments, context):
    try:
        state, quote = context.ledger.take_quote(arguments["quote_id"])
    except LookupError as exc:
        refuse("bad_quote", f"quote {arguments['quote_id']} is {exc.args[0]}", "make a new quote")
    preview = {"quote": {k: quote[k] for k in ("quote_id", "offer_id", "gpu_name", "dph", "cap_hours",
                                                "environment", "image", "disk_gb")},
               "worst_case_gpu_cost_usd": round(quote["dph"] * quote["cap_hours"], 2)}
    dry = need_confirm(arguments, "renting this offer", preview)
    if dry:
        return dry
    api = context.api()
    offer = api.offer(quote["offer_id"])
    if offer is None:
        refuse("offer_gone", f"offer {quote['offer_id']} was taken since the quote", "search_offers again")
    dph_now = num(offer.get("dph_total"))
    tolerance = num(context.ledger.limits.get("price_tolerance"), 0.02)
    if dph_now > quote["dph"] * (1 + tolerance):
        refuse("price_changed", f"the price rose from ${quote['dph']}/hr to ${dph_now}/hr", "quote again")
    band = context.ledger.band_for(quote["dph"])
    remaining = context.ledger.remaining_hours(band)
    cap = min(quote["cap_hours"], remaining)
    if cap <= 0.01:
        refuse("band_spent", "the band ran out of hours since the quote", "quote again")
    public = remote_mod.public_key(context.environ)
    environment = context.recipes["environments"][quote["environment"]]
    body = {"client_id": "me", "image": environment["image"], "disk": quote["disk_gb"],
            "runtype": "ssh", "label": LABEL_PREFIX + quote["quote_id"],
            "onstart": onstart_script(environment, cap * 3600)}
    reply = api.create(quote["offer_id"], body)
    instance_id = reply.get("new_contract") if isinstance(reply, dict) else None
    if not reply.get("success", instance_id is not None) or instance_id is None:
        refuse("rent_failed", "Vast did not create the instance: " + str(reply.get("msg") or reply)[:200])
    now = context.clock()
    state = context.ledger.load()
    state["quotes"][quote["quote_id"]]["used"] = True
    state["rentals"].append({"instance_id": int(instance_id), "quote_id": quote["quote_id"],
                             "offer_id": quote["offer_id"], "dph": quote["dph"], "band": quote["band"],
                             "environment": quote["environment"], "started": now,
                             "deadline": now + cap * 3600, "cap_hours": round(cap, 3), "ended": None})
    context.ledger.save(state)
    context.ledger.event("rented", instance_id=int(instance_id), quote_id=quote["quote_id"],
                         dph=quote["dph"], cap_hours=round(cap, 3), environment=quote["environment"])
    warnings = []
    try:
        api.attach_ssh(instance_id, public)
    except VastError as exc:
        warnings.append(f"attaching the ssh key failed ({exc.message}); an account-level key still works")
    return {"rented": True, "instance_id": int(instance_id), "cap_hours": round(cap, 3),
            "deadline_epoch": round(now + cap * 3600), "warnings": warnings,
            "next": "wait_ready, then upload / run_recipe; destroy when done"}


def t_instances(arguments, context):
    api_rows = context.api().instances()
    state = context.ledger.load()
    now = context.clock()
    seen = set()
    rows = []
    for item in api_rows:
        instance_id = int(item.get("id"))
        seen.add(instance_id)
        rental = context.ledger.rental(instance_id, state)
        status = item.get("actual_status") or item.get("cur_state")
        row = {"instance_id": instance_id, "status": status, "gpu_name": item.get("gpu_name"),
               "dph": round(num(item.get("dph_total")), 4), "label": item.get("label"),
               "in_ledger": rental is not None}
        if rental is not None:
            if rental.get("ended") is None and status in ("exited", "stopped", "offline"):
                context.ledger.end_rental(instance_id, "observed_" + str(status))
                rental = context.ledger.rental(instance_id)
            row["hours_run"] = round(((rental.get("ended") or now) - rental["started"]) / 3600, 2)
            row["hours_left"] = round((rental["deadline"] - now) / 3600, 2)
            row["over_deadline"] = rental.get("ended") is None and now > rental["deadline"]
        else:
            row["warning"] = "not in this ledger: rented elsewhere, or by hand; it is not budgeted here"
        rows.append(row)
    for rental in context.ledger.live_rentals():
        if rental["instance_id"] not in seen:
            context.ledger.end_rental(rental["instance_id"], "gone")
    return {"instances": rows}


def t_wait_ready(arguments, context):
    deadline = context.clock() + int(arguments.get("timeout_seconds", 600))
    last = None
    while True:
        instance = instance_or_refuse(context, arguments["instance_id"])
        last = instance.get("actual_status")
        if last == "running" and instance.get("ssh_host"):
            code, _, err = context.remote.run(instance, "mkdir -p /workspace/job/logs && echo ok", timeout=60)
            if code == 0:
                return {"ready": True, "status": last, "ssh": "answers",
                        "note": "the environment's onstart may still be installing; the `ready` recipe shows its markers"}
        if context.clock() >= deadline:
            return {"ready": False, "status": last, "hint": "call wait_ready again, or instances to check"}
        context.sleep(10)


def t_upload(arguments, context):
    local = remote_mod.local_path(context.environ, arguments["local"], must_exist=True)
    destination = remote_mod.remote_path(context.recipes["job_dir"], arguments["remote"])
    instance = running_instance(context, arguments["instance_id"])
    parent = destination.rsplit("/", 1)[0]
    context.remote.run(instance, "mkdir -p " + shlex.quote(parent), timeout=60)
    context.remote.copy(instance, local, destination, upload=True)
    result = {"uploaded": str(local.name), "to": destination}
    if local.is_file():
        result["sha256"] = remote_mod.sha256_file(local)
        result["bytes"] = local.stat().st_size
    context.ledger.event("upload", instance_id=int(arguments["instance_id"]), to=destination,
                         sha256=result.get("sha256"))
    return result


def t_download(arguments, context):
    source = remote_mod.remote_path(context.recipes["job_dir"], arguments["remote"])
    local = remote_mod.local_path(context.environ, arguments["local"])
    instance = running_instance(context, arguments["instance_id"])
    local.parent.mkdir(parents=True, exist_ok=True)
    context.remote.copy(instance, source, local, upload=False)
    result = {"downloaded": source, "to": str(local)}
    if local.is_file():
        result["sha256"] = remote_mod.sha256_file(local)
        result["bytes"] = local.stat().st_size
    context.ledger.event("download", instance_id=int(arguments["instance_id"]), source=source,
                         sha256=result.get("sha256"))
    return result


def start_or_run(context, instance, command, background, timeout):
    job_dir = context.recipes["job_dir"]
    if background:
        job = "j_" + secrets.token_hex(4)
        inner = f"cd {shlex.quote(job_dir)} && ({command}); echo $? > logs/{job}.exit"
        wrapper = (f"mkdir -p {shlex.quote(job_dir)}/logs && cd {shlex.quote(job_dir)} && "
                   f"nohup bash -c {shlex.quote(inner)} > logs/{job}.log 2>&1 & echo $! > "
                   f"{shlex.quote(job_dir)}/logs/{job}.pid; echo started")
        code, out, err = context.remote.run(instance, wrapper, timeout=60)
        if code != 0:
            refuse("start_failed", "the job did not start: " + remote_mod.tail(err, 5))
        return {"job_id": job, "background": True, "next": "job_status with this job_id"}
    code, out, err = context.remote.run(instance, f"cd {shlex.quote(job_dir)} 2>/dev/null; {command}",
                                        timeout=timeout)
    return {"exit_code": code, "stdout_tail": remote_mod.tail(out), "stderr_tail": remote_mod.tail(err, 20)}


def t_run_recipe(arguments, context):
    name = arguments["recipe"]
    command, background = remote_mod.render(name, arguments.get("arguments") or {}, context.recipes)
    recipe = context.recipes["recipes"][name]
    rental = context.ledger.rental(arguments["instance_id"])
    needs = recipe.get("environment")
    if needs and rental is not None and rental["environment"] != needs:
        refuse("wrong_environment", f"{name} needs the `{needs}` environment and this instance was rented "
               f"with `{rental['environment']}`", "rent a new instance with that environment")
    instance = running_instance(context, arguments["instance_id"])
    result = start_or_run(context, instance, command, background, int(arguments.get("timeout_seconds", 600)))
    context.ledger.event("recipe", instance_id=int(arguments["instance_id"]), recipe=name,
                         job_id=result.get("job_id"), exit_code=result.get("exit_code"))
    return {"recipe": name, **result}


def t_run_shell(arguments, context):
    command = arguments["command"]
    dry = need_confirm(arguments, "running this command on the rented instance", {"command": command})
    if dry:
        return dry
    instance = running_instance(context, arguments["instance_id"])
    result = start_or_run(context, instance, command, bool(arguments.get("background")),
                          int(arguments.get("timeout_seconds", 600)))
    context.ledger.event("shell", instance_id=int(arguments["instance_id"]), command=command,
                         job_id=result.get("job_id"), exit_code=result.get("exit_code"))
    return result


def t_job_status(arguments, context):
    job = arguments["job_id"]
    if not JOB_ID.match(job):
        refuse("bad_argument", "job_id looks like j_ and eight hex digits")
    instance = running_instance(context, arguments["instance_id"])
    job_dir = shlex.quote(context.recipes["job_dir"])
    lines = int(arguments.get("lines", 60))
    command = (f"cd {job_dir} && if [ -f logs/{job}.exit ]; then echo \"STATE done $(cat logs/{job}.exit)\"; "
               f"elif kill -0 $(cat logs/{job}.pid 2>/dev/null) 2>/dev/null; then echo 'STATE running'; "
               f"else echo 'STATE unknown'; fi; tail -n {lines} logs/{job}.log 2>/dev/null")
    code, out, err = context.remote.run(instance, command, timeout=60)
    first, _, rest = out.partition("\n")
    parts = first.split()
    state = parts[1] if len(parts) > 1 else "unknown"
    result = {"job_id": job, "state": state, "log_tail": rest.rstrip()}
    if state == "done" and len(parts) > 2:
        result["exit_code"] = int(parts[2]) if parts[2].lstrip("-").isdigit() else parts[2]
    return result


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def t_tunnel(arguments, context):
    action = arguments["action"]
    state = context.ledger.load()
    if action == "list":
        return {"tunnels": state["tunnels"]}
    local_port = int(arguments.get("local_port", 8188))
    key = str(local_port)
    if action == "close":
        record = state["tunnels"].get(key)
        if record is None:
            return {"closed": False, "reason": f"no tunnel on {local_port}"}
        remote_mod.close_pid(record["pid"])
        context.ledger.set_tunnel(key, None)
        return {"closed": True, "local_port": local_port}
    if "instance_id" not in arguments:
        refuse("bad_argument", "opening a tunnel needs instance_id")
    if key in state["tunnels"]:
        refuse("port_taken", f"a tunnel is already open on {local_port}", "close it first, or pick another local_port")
    if not port_free(local_port):
        refuse("port_taken", f"127.0.0.1:{local_port} is in use on this machine", "pick another local_port")
    instance = running_instance(context, arguments["instance_id"])
    remote_port = int(arguments.get("remote_port", 8188))
    pid = context.remote.open_tunnel(instance, local_port, remote_port)
    context.ledger.set_tunnel(key, {"pid": pid, "instance_id": int(arguments["instance_id"]),
                                    "local_port": local_port, "remote_port": remote_port})
    return {"open": True, "local": f"http://127.0.0.1:{local_port}", "remote_port": remote_port,
            "use": f"COMFY_URL=http://127.0.0.1:{local_port} (comfy_client.py needs no --allow-remote)"}


def close_tunnels_for(context, instance_id):
    state = context.ledger.load()
    closed = []
    for key, record in list(state["tunnels"].items()):
        if record["instance_id"] == int(instance_id):
            remote_mod.close_pid(record["pid"])
            context.ledger.set_tunnel(key, None)
            closed.append(record["local_port"])
    return closed


def t_stop(arguments, context):
    instance_id = int(arguments["instance_id"])
    dry = need_confirm(arguments, "stopping this instance",
                       {"instance_id": instance_id, "note": "a stopped instance keeps its disk, which still bills; destroy ends all billing"})
    if dry:
        return dry
    context.api().stop(instance_id)
    closed = close_tunnels_for(context, instance_id)
    context.ledger.end_rental(instance_id, "stopped")
    context.ledger.event("stop", instance_id=instance_id)
    return {"stopped": instance_id, "tunnels_closed": closed}


def t_destroy(arguments, context):
    instance_id = int(arguments["instance_id"])
    dry = need_confirm(arguments, "destroying this instance and everything on its disk",
                       {"instance_id": instance_id, "note": "download what you need first"})
    if dry:
        return dry
    context.api().destroy(instance_id)
    closed = close_tunnels_for(context, instance_id)
    context.ledger.end_rental(instance_id, "destroyed")
    context.ledger.event("destroy", instance_id=instance_id)
    return {"destroyed": instance_id, "tunnels_closed": closed}


def t_reap(arguments, context):
    now = context.clock()
    over = [r["instance_id"] for r in context.ledger.live_rentals() if now > r["deadline"]]
    dry = need_confirm(arguments, "destroying every instance past its deadline", {"would_destroy": over})
    if dry:
        return dry
    destroyed, failed = [], []
    for instance_id in over:
        try:
            context.api().destroy(instance_id)
        except VastError as exc:
            failed.append({"instance_id": instance_id, "error": exc.message})
            continue
        close_tunnels_for(context, instance_id)
        context.ledger.end_rental(instance_id, "reaped")
        destroyed.append(instance_id)
    context.ledger.event("reap", destroyed=destroyed)
    return {"destroyed": destroyed, "failed": failed}


# ── the tool table ───────────────────────────────────────────────────────────

def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


INSTANCE = {"type": "integer", "minimum": 1, "description": "the Vast instance id"}
CONFIRM = {"type": "boolean", "default": False,
           "description": "true only after the author said yes to this exact call; false is a dry run"}
REL = {"type": "string", "minLength": 1, "maxLength": 400}
TIMEOUT = {"type": "integer", "minimum": 5, "maximum": 3600, "default": 600}

TOOLS = {tool.name: tool for tool in (
    Tool("account", "Vast account", "Whether a key is set, and the account balance and credit. Never shows the key.",
         obj({}), t_account),
    Tool("list_recipes", "Environments and recipes",
         "The environments an instance can be rented with (image, disk, what onstart installs) and the named "
         "recipes run_recipe can run, with their parameters.", obj({}), t_list_recipes),
    Tool("search_offers", "Search GPU offers",
         "Cheapest rentable on-demand offers first, capped at the highest price band. Free; rents nothing. "
         "Each offer shows the hours its price band has left this window.",
         obj({"gpu_name": {"type": "string", "maxLength": 60, "description": "exact Vast name, e.g. RTX 4090"},
              "min_gpu_ram_gb": {"type": "number", "minimum": 0, "maximum": 1024},
              "max_dph": {"type": "number", "minimum": 0.01, "maximum": 1000},
              "min_reliability": {"type": "number", "minimum": 0, "maximum": 1},
              "num_gpus": {"type": "integer", "minimum": 1, "maximum": 16, "default": 1},
              "min_disk_gb": {"type": "number", "minimum": 0, "maximum": 100000},
              "verified": {"type": "boolean", "default": True},
              "geolocation": {"type": "array", "maxItems": 30, "items": {"type": "string", "maxLength": 8}},
              "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}}),
         t_search_offers),
    Tool("quote", "Quote a rental",
         "Price one offer for one environment against the biweekly band budgets. Returns a quote_id (valid 15 "
         "minutes), the hour cap, the worst-case cost and what leaves this machine. Spends nothing.",
         obj({"offer_id": {"type": "integer", "minimum": 1},
              "environment": {"type": "string", "maxLength": 40},
              "hours": {"type": "number", "minimum": 0.1, "maximum": 100},
              "disk_gb": {"type": "integer", "minimum": 10, "maximum": 2000}},
             ("offer_id", "environment", "hours")), t_quote),
    Tool("rent", "Rent an instance",
         "Rent the quoted offer. Spends money. Without confirm=true it is a dry run that shows the quote. "
         "Refuses a stale, used or repriced quote, and a band with no hours left.",
         obj({"quote_id": {"type": "string", "pattern": "^q_[0-9a-f]{12}$"}, "confirm": CONFIRM}, ("quote_id",)),
         t_rent, read_only=False, spends=True),
    Tool("instances", "List instances",
         "Every instance on the account with status, price, hours run and hours left, and whether this ledger "
         "knows it. Settles rentals that have stopped or vanished.", obj({}), t_instances),
    Tool("wait_ready", "Wait for an instance",
         "Poll until the instance is running and answers ssh, up to timeout_seconds.",
         obj({"instance_id": INSTANCE, "timeout_seconds": {"type": "integer", "minimum": 10, "maximum": 1800, "default": 600}},
             ("instance_id",)), t_wait_ready),
    Tool("upload", "Upload a file",
         "scp a file or folder from VAST_WORK_DIR to /workspace/job on the instance; returns its sha256.",
         obj({"instance_id": INSTANCE, "local": REL, "remote": REL}, ("instance_id", "local", "remote")),
         t_upload, read_only=False),
    Tool("download", "Download a file",
         "scp a file or folder from /workspace/job on the instance into VAST_WORK_DIR; returns its sha256.",
         obj({"instance_id": INSTANCE, "remote": REL, "local": REL}, ("instance_id", "remote", "local")),
         t_download, read_only=False),
    Tool("run_recipe", "Run a recipe",
         "Run a named recipe (list_recipes) on the instance with type-checked arguments, inserted shell-quoted. "
         "Background recipes return a job_id for job_status.",
         obj({"instance_id": INSTANCE, "recipe": {"type": "string", "maxLength": 60},
              "arguments": {"type": "object"}, "timeout_seconds": TIMEOUT}, ("instance_id", "recipe")),
         t_run_recipe, read_only=False),
    Tool("run_shell", "Run a shell command",
         "Run any command on the instance (in /workspace/job). Needs confirm=true on every call; without it, a "
         "dry run that echoes the command. The command text is kept in the ledger, so put no secret in it.",
         obj({"instance_id": INSTANCE, "command": {"type": "string", "minLength": 1, "maxLength": 4000},
              "background": {"type": "boolean", "default": False}, "timeout_seconds": TIMEOUT, "confirm": CONFIRM},
             ("instance_id", "command")), t_run_shell, read_only=False),
    Tool("job_status", "Background job status",
         "Whether a background job is running or done (with its exit code), and the tail of its log.",
         obj({"instance_id": INSTANCE, "job_id": {"type": "string", "pattern": "^j_[0-9a-f]{8}$"},
              "lines": {"type": "integer", "minimum": 1, "maximum": 500, "default": 60}},
             ("instance_id", "job_id")), t_job_status),
    Tool("tunnel", "ssh tunnel",
         "Open, close or list an ssh tunnel from 127.0.0.1:<local_port> here to 127.0.0.1:<remote_port> on the "
         "instance (ComfyUI is 8188).",
         obj({"action": {"type": "string", "enum": ["open", "close", "list"]}, "instance_id": INSTANCE,
              "local_port": {"type": "integer", "minimum": 1024, "maximum": 65535, "default": 8188},
              "remote_port": {"type": "integer", "minimum": 1, "maximum": 65535, "default": 8188}}, ("action",)),
         t_tunnel, read_only=False),
    Tool("stop", "Stop an instance",
         "Stop the instance (GPU billing ends; its disk still bills). Needs confirm=true.",
         obj({"instance_id": INSTANCE, "confirm": CONFIRM}, ("instance_id",)), t_stop, read_only=False, spends=True),
    Tool("destroy", "Destroy an instance",
         "Destroy the instance and its disk: all billing ends. Download first. Needs confirm=true.",
         obj({"instance_id": INSTANCE, "confirm": CONFIRM}, ("instance_id",)), t_destroy, read_only=False, spends=True),
    Tool("reap", "Reap overdue instances",
         "Destroy every rental past its deadline. Without confirm=true, lists them.",
         obj({"confirm": CONFIRM}), t_reap, read_only=False, spends=True),
)}


def describe_tool(tool):
    if tool.read_only:
        annotations = {"readOnlyHint": True, "openWorldHint": True}
    else:
        annotations = {"readOnlyHint": False, "destructiveHint": tool.spends, "idempotentHint": False,
                       "openWorldHint": True}
    return {"name": tool.name, "title": tool.title, "description": tool.description,
            "inputSchema": tool.input_schema, "annotations": annotations}


# ── argument checking (the subset of JSON Schema the table uses) ─────────────

_PLAIN = {"object": dict, "array": list, "string": str, "boolean": bool}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_arguments(value, schema, where="arguments"):
    kind = schema.get("type")
    if kind == "integer":
        fits = _is_number(value) and (isinstance(value, int) or float(value).is_integer())
    elif kind == "number":
        fits = _is_number(value) and math.isfinite(value)
    elif kind in _PLAIN:
        fits = isinstance(value, _PLAIN[kind])
    else:
        fits = True
    if not fits:
        return f"{where} must be of type {kind}"
    if "enum" in schema and value not in schema["enum"]:
        return f"{where} must be one of: {', '.join(map(str, schema['enum']))}"
    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            return f"{where} must be at least {schema['minimum']}"
        if "maximum" in schema and value > schema["maximum"]:
            return f"{where} must be at most {schema['maximum']}"
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            return f"{where} must have at least {schema['minLength']} characters"
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return f"{where} must have at most {schema['maxLength']} characters"
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            return f"{where} must match {schema['pattern']}"
    elif isinstance(value, list):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            return f"{where} must have at most {schema['maxItems']} items"
        if isinstance(schema.get("items"), dict):
            for position, item in enumerate(value):
                problem = check_arguments(item, schema["items"], f"{where}[{position}]")
                if problem:
                    return problem
    elif isinstance(value, dict):
        properties = schema.get("properties") or {}
        for name in schema.get("required", ()):
            if name not in value:
                return f"{where} needs `{name}`"
        for name, item in value.items():
            if name in properties:
                problem = check_arguments(item, properties[name], f"{where}.{name}")
                if problem:
                    return problem
            elif schema.get("additionalProperties") is False:
                return f"{where} has no `{str(name)[:80]}` (it takes: {', '.join(properties) or 'none'})"
    return None


# ── the dispatcher ───────────────────────────────────────────────────────────

class _Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def _error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _text_block(payload):
    return {"type": "text", "text": json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)}


def _tool_failure(code, message, hint=None):
    return {"content": [_text_block({"error": {"code": code, "message": message, "hint": hint}})], "isError": True}


def _spend(context):
    try:
        return context.ledger.spend_summary()
    except Exception:  # the meter must never break a reply
        return None


def _initialize(params, context):
    asked = params.get("protocolVersion")
    return {"protocolVersion": asked if asked in PROTOCOL_VERSIONS else DEFAULT_PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "title": SERVER_TITLE, "version": SERVER_VERSION},
            "instructions": INSTRUCTIONS}


def _tools_list(params, context):
    return {"tools": [describe_tool(tool) for tool in TOOLS.values()]}


def _tools_call(params, context):
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(name, str) or not isinstance(arguments, dict):
        raise _Refused(INVALID_PARAMS, "tools/call needs a `name` string and an `arguments` object")
    tool = TOOLS.get(name)
    if tool is None:
        raise _Refused(INVALID_PARAMS, f"unknown tool: {name[:80]}")
    problem = check_arguments(arguments, tool.input_schema)
    if problem:
        return _tool_failure("bad_argument", problem, f"tools/list shows the arguments {name} takes")
    try:
        payload = tool.handler(arguments, context)
    except VastError as exc:
        return _tool_failure(exc.code, exc.message, exc.hint)
    except Exception as exc:
        if context.log:
            context.log(f"{name} failed:\n" + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return _tool_failure("internal", f"{name} failed unexpectedly", "the server's stderr log has the details")
    if isinstance(payload, dict) and name not in ("list_recipes",):
        payload = {**payload, "spend": _spend(context)}
    return {"content": [_text_block(payload)], "isError": False}


METHODS = {"initialize": _initialize, "ping": lambda p, c: {}, "tools/list": _tools_list, "tools/call": _tools_call}


def dispatch(message, context):
    if isinstance(message, list):
        replies = [r for r in (dispatch(m, context) for m in message) if r is not None]
        return replies or None
    if not isinstance(message, dict):
        return _error(None, INVALID_REQUEST, "a message must be a JSON object")
    method = message.get("method")
    request_id = message.get("id")
    if not isinstance(method, str):
        return None if ("result" in message or "error" in message) else _error(None, INVALID_REQUEST, "no method")
    if "id" not in message:
        return None
    params = message.get("params") or {}
    handler = METHODS.get(method)
    if handler is None:
        return _error(request_id, METHOD_NOT_FOUND, f"method not found: {method[:80]}")
    if not isinstance(params, dict):
        return _error(request_id, INVALID_PARAMS, "`params` must be an object")
    try:
        return {"jsonrpc": "2.0", "id": request_id, "result": handler(params, context)}
    except _Refused as refusal:
        return _error(request_id, refusal.code, refusal.message)
    except Exception as exc:
        if context.log:
            context.log("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return _error(request_id, INTERNAL_ERROR, "internal error")


def handle_line(line, context):
    line = line.strip()
    if not line:
        return None
    try:
        message = json.loads(line.decode("utf-8"))
    except (ValueError, RecursionError):
        return _encode(_error(None, PARSE_ERROR, "parse error"))
    reply = dispatch(message, context)
    return None if reply is None else _encode(reply)


def _encode(message):
    return json.dumps(message, ensure_ascii=True, separators=(",", ":")).encode("ascii") + b"\n"


def serve(rfile, wfile, context):
    while True:
        line = rfile.readline(MAX_LINE + 1)
        if not line:
            return
        if len(line) > MAX_LINE:
            while line and not line.endswith(b"\n"):
                line = rfile.readline(MAX_LINE + 1)
            wfile.write(_encode(_error(None, INVALID_REQUEST, "line too long")))
            wfile.flush()
            continue
        reply = handle_line(line, context)
        if reply:
            wfile.write(reply)
            wfile.flush()


def selftest():
    context = make_context(log=lambda text: print(text, file=sys.stderr))
    hello = dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                      "params": {"protocolVersion": "2025-06-18"}}, context)
    listed = dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, context)
    names = [tool["name"] for tool in listed["result"]["tools"]]
    print(json.dumps({"server": hello["result"]["serverInfo"], "protocol": hello["result"]["protocolVersion"],
                      "tools": names, "key": "set" if has_key(context.environ) else "not set"}, indent=2))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    out = sys.stdout.buffer
    sys.stdout = sys.stderr  # a stray print must never corrupt the protocol stream
    context = make_context(log=lambda text: print(text, file=sys.stderr, flush=True))
    serve(sys.stdin.buffer, out, context)
    return 0


if __name__ == "__main__":
    sys.exit(main())
