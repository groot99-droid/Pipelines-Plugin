"""The compute gate: one token authorises one heavy local job. Requires pyyaml.

    python studio/pipeline/compute_gate.py evaluate <class> [--probe FILE] [--all]
    python studio/pipeline/compute_gate.py mint     <class> [--probe FILE] [--force]
    python studio/pipeline/compute_gate.py consume  <run-id>
    python studio/pipeline/compute_gate.py release
    python studio/pipeline/compute_gate.py status

`evaluate` reads a probe (probe.py's JSON; taken live when --probe is not
given) and checks it against the class's thresholds in machine.yaml. It
writes nothing. `mint` evaluates and, on PASS, writes the token under the
run folder; on DENY it writes nothing, so a denial never removes a live
token. `consume` stamps the run that is using the token; a token consumed by
one run is not another's. `release` removes an orphaned token.

The laws, from machine.yaml: a metric the probe could not read fails a
threshold that names it; one thermal reading is enough, but not none; one
live token at a time. The token's TTL counts from the mint, and a re-mint by
the same class refreshes it and keeps who holds it.

Three defects of the Creative-Headquarters gate are fixed here: a denial
overwrote a live token; a re-issue cleared who held it; its test wrote to the
real token. The token's place comes from the spec, so the tests never touch
it.

Exit codes: 0 PASS or done, 1 DENY or refused, 2 usage error.
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage, load_yaml, now, read_text,
    stamp, write_text,
)

HERE = Path(__file__).resolve().parent
MACHINE_PATH = HERE / "machine.yaml"


def load_machine(path=MACHINE_PATH):
    try:
        machine = load_yaml(read_text(path))
    except ValueError as err:
        raise Usage(f"{path} does not parse: {err}")
    for key in ("classes", "token", "laws", "every_class", "remedies"):
        if key not in machine:
            raise Usage(f"{path} has no `{key}`")
    return machine


def token_path(env, machine):
    return env.runs / machine["token"]["file"]


def metric(probe, dotted):
    value = probe
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    if isinstance(value, bool):
        return value
    return value


def check_threshold(probe, key, want):
    """(metric name, ok, sentence). A null metric fails: an unverifiable gate
    is closed."""
    for suffix, rule in (("_min", "min"), ("_max", "max"), ("_in", "in")):
        if key.endswith(suffix):
            name = key[: -len(suffix)]
            break
    else:
        raise Usage(f"machine.yaml threshold `{key}` ends in neither _min, _max nor _in")
    got = metric(probe, name)
    if got is None:
        return name, False, f"{name} is unreadable (null), and an unverifiable gate is closed"
    if rule == "in":
        ok = got in want
        return name, ok, f"{name} = {got!r} {'is' if ok else 'is not'} one of {want}"
    if isinstance(got, bool) or not isinstance(got, (int, float)):
        return name, False, f"{name} = {got!r} is not a number"
    if rule == "min":
        ok = got >= want
        return name, ok, f"{name} = {got} {'>=' if ok else '<'} {want}"
    ok = got <= want
    return name, ok, f"{name} = {got} {'<=' if ok else '>'} {want}"


def evaluate(machine, probe, workload):
    """{"workload", "verdict", "checks": [(name, ok, sentence)], "reasons", "remedies"}."""
    classes = machine["classes"]
    if workload not in classes:
        raise Usage(f"no class `{workload}` in machine.yaml. Declared: {', '.join(sorted(classes))}")
    thresholds = {k: v for k, v in machine["every_class"].items()}
    thresholds.update({k: v for k, v in classes[workload].items() if k != "describes"})
    checks = [check_threshold(probe, key, want) for key, want in thresholds.items()]
    either = machine["laws"].get("thermal_either") or []
    names = [key[: key.rfind("_")] for key in either]
    thermal = [c for c in checks if c[0] in names]
    if thermal and machine["laws"].get("null_closes", True):
        readable = [c for c in thermal if "unreadable" not in c[2]]
        if readable:  # one reading is enough: drop the unreadable ones
            checks = [c for c in checks if c not in thermal or "unreadable" not in c[2]]
        else:
            checks = [c for c in checks if c not in thermal]
            checks.append(("thermal", False, "both thermal readings are unreadable, so the gate is closed"))
    failed = [c for c in checks if not c[1]]
    remedies = []
    for name, _, _ in failed:
        text = machine["remedies"].get(name)
        if text and text not in remedies:
            remedies.append(text)
    return {"workload": workload, "verdict": "DENY" if failed else "PASS", "checks": checks,
            "reasons": [c[2] for c in failed], "remedies": remedies}


def load_token(env, machine):
    path = token_path(env, machine)
    if not path.is_file():
        return None
    try:
        token = json.loads(read_text(path))
    except (json.JSONDecodeError, Usage):
        return None
    return token if isinstance(token, dict) and token.get("verdict") == "PASS" else None


def token_age(token):
    return time.time() - float(token.get("ts_epoch") or 0)


def token_live(token):
    return token is not None and token_age(token) < float(token.get("ttl_seconds") or 0)


def read_probe(path):
    if path:
        try:
            probe = json.loads(read_text(path))
        except json.JSONDecodeError as err:
            raise Usage(f"{path} is not a probe: {err}")
    else:
        import probe as probe_module  # beside this file
        probe = probe_module.probe()
    if not isinstance(probe, dict):
        raise Usage("a probe is a JSON object")
    return probe


def print_verdict(found, probe, ttl):
    age = time.time() - float(probe.get("ts_epoch") or time.time())
    if age > ttl:
        print(f"warning   the probe is {int(age)}s old, older than the token TTL. Take a fresh one.")
    print(f"{found['workload']:16s} {found['verdict']}")
    for name, ok, sentence in found["checks"]:
        print(f"    {'ok  ' if ok else 'FAIL'}  {sentence}")
    for text in found["remedies"]:
        print(f"    remedy: {text}")


def cmd_evaluate(env, machine, args):
    probe = read_probe(args.probe)
    ttl = machine["token"]["ttl_seconds"]
    workloads = sorted(machine["classes"]) if args.all else [args.workload]
    if not args.all and not args.workload:
        raise Usage("name a class, or pass --all")
    worst = EXIT_OK
    for workload in workloads:
        found = evaluate(machine, probe, workload)
        print_verdict(found, probe, ttl)
        if found["verdict"] != "PASS":
            worst = EXIT_REFUSED
    return worst


def cmd_mint(env, machine, args):
    if not args.workload:
        raise Usage("name a class to mint for")
    probe = read_probe(args.probe)
    ttl = machine["token"]["ttl_seconds"]
    found = evaluate(machine, probe, args.workload)
    held = load_token(env, machine)
    if machine["laws"].get("single_flight", True) and token_live(held) and held["workload"] != args.workload:
        if args.force:
            print(f"warning   --force overrides a live token held by {held['workload']}"
                  + (f" (consumed by {held['consumed_by']})" if held.get("consumed_by") else ""),
                  file=sys.stderr)
        else:
            found["verdict"] = "DENY"
            found["checks"].append(("single_flight", False,
                                    f"a live {held['workload']} token has {int(held['ttl_seconds'] - token_age(held))}s left"))
            found["reasons"].append("single_flight")
            found["remedies"].append(machine["remedies"]["single_flight"])
    print_verdict(found, probe, ttl)
    if found["verdict"] != "PASS":
        print("    the token on disk is untouched")
        return EXIT_REFUSED
    same = held if token_live(held) and held["workload"] == args.workload else None
    token = {
        "verdict": "PASS",
        "workload": args.workload,
        "minted_at": stamp(now()),
        "ts_epoch": time.time(),
        "ttl_seconds": ttl,
        "memory_budget_gb": metric(probe, "memory.dynamic_claim_limit_gb"),
        "probe_snapshot": {"gpu": metric(probe, "gpu.status"), "available_gb": metric(probe, "memory.available_gb"),
                           "power": metric(probe, "power.source"), "cpu_perf_pct": metric(probe, "thermal.cpu_perf_pct"),
                           "thermal_c": metric(probe, "thermal.cpu_temp_c")},
        "consumed_by": same.get("consumed_by") if same else None,
        "law": "one token, one job. Consume it with `compute_gate.py consume <run-id>`; a denial for another class leaves it alone.",
    }
    write_text(token_path(env, machine), json.dumps(token, indent=2) + "\n")
    print(f"    token: {token_path(env, machine)} -> PASS, {ttl}s"
          + (f", held by {token['consumed_by']}" if token["consumed_by"] else "")
          + (f", budget {token['memory_budget_gb']} GB" if token["memory_budget_gb"] is not None else ""))
    return EXIT_OK


def cmd_consume(env, machine, args):
    token = load_token(env, machine)
    if not token_live(token):
        raise Refused("no live PASS token. Mint one first: compute_gate.py mint <class>")
    holder = token.get("consumed_by")
    if holder and holder != args.run_id:
        raise Refused(f"the token is held by run `{holder}`. One token, one job.")
    token["consumed_by"] = args.run_id
    token["consumed_at"] = stamp(now())
    write_text(token_path(env, machine), json.dumps(token, indent=2) + "\n")
    print(f"consumed  {token['workload']} token by {args.run_id}, {int(token['ttl_seconds'] - token_age(token))}s left")
    return EXIT_OK


def cmd_release(env, machine, args):
    path = token_path(env, machine)
    if path.is_file():
        path.unlink()
        print(f"released  {path}")
    else:
        print("no token to release")
    return EXIT_OK


def cmd_status(env, machine, args):
    token = load_token(env, machine)
    if token is None:
        print("token     none")
        return EXIT_OK
    left = int(token["ttl_seconds"] - token_age(token))
    print(f"token     {token['workload']} {'live' if left > 0 else 'expired'}"
          + (f", {left}s left" if left > 0 else "")
          + (f", held by {token['consumed_by']}" if token.get("consumed_by") else ", unconsumed"))
    return EXIT_OK


def build_parser():
    parser = argparse.ArgumentParser(prog="compute_gate.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs and the token are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    parser.add_argument("--assets-dir", help="where kept artifacts go (default: from the spec)")
    parser.add_argument("--machine", default=str(MACHINE_PATH), help="the machine file to read")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("evaluate", help="verdict for a class; writes nothing")
    p.add_argument("workload", nargs="?")
    p.add_argument("--probe")
    p.add_argument("--all", action="store_true")
    p.set_defaults(run=cmd_evaluate)
    p = sub.add_parser("mint", help="evaluate and, on PASS, write the token")
    p.add_argument("workload", nargs="?")
    p.add_argument("--probe")
    p.add_argument("--force", action="store_true")
    p.set_defaults(run=cmd_mint)
    p = sub.add_parser("consume", help="stamp the run that uses the token")
    p.add_argument("run_id")
    p.set_defaults(run=cmd_consume)
    p = sub.add_parser("release", help="remove the token")
    p.set_defaults(run=cmd_release)
    p = sub.add_parser("status", help="the token as it stands")
    p.set_defaults(run=cmd_status)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        env = Env(args.spec, args.runs_dir, args.vault_dir, args.context_dir, args.assets_dir)
        machine = load_machine(args.machine)
        return args.run(env, machine, args)
    except Refused as problem:
        print(f"REFUSED   {problem}", file=sys.stderr)
        return EXIT_REFUSED
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
