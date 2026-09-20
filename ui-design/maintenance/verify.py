#!/usr/bin/env python3
"""Run every ui-design verification gate, in order, and stop at the first failure.

This is the one command that says whether the tool is healthy. It replaces the
source project's `npm run verify:data`. Each gate is an ordinary command you can
run on its own; on failure this prints that gate's output and the exact single
command to re-run it.

Gates, in order:
    1. validate-csv          structural check of every catalog CSV
    2. validate_data         registry, schema and provenance integrity
    3. validate-contract     spec.yaml, the skills and the agent agree with the code
    4. catalog summary       catalog-summary.json is current
    5. engine tests          catalog/scripts/tests
    6. maintainer tests      maintenance/tests
    7. relevance gate        ranking quality and fingerprints
    8. smoke domains         every search domain answers a probe
    9. smoke stacks          every stack answers a probe

Usage:
    python ui-design/maintenance/verify.py

Exit codes:
    0 -- every gate passed
    1 -- a gate failed (its output and its re-run command are on stderr)
"""
import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

GATES = [
    ("validate-csv", ["python", "ui-design/maintenance/validate-csv.py"]),
    ("validate_data", ["python", "ui-design/catalog/scripts/validate_data.py"]),
    ("validate-contract", ["python", "ui-design/maintenance/validate-contract.py"]),
    ("catalog summary", ["python", "ui-design/maintenance/generate-catalog-summary.py", "--check"]),
    ("engine tests", ["python", "-m", "unittest", "discover", "-s", "ui-design/catalog/scripts/tests",
                      "-p", "test_*.py"]),
    ("maintainer tests", ["python", "-m", "unittest", "discover", "-s", "ui-design/maintenance/tests",
                          "-p", "test_*.py"]),
    ("relevance gate", ["python", "ui-design/maintenance/evaluate-relevance.py"]),
    ("smoke domains", ["python", "ui-design/maintenance/smoke.py", "domains"]),
    ("smoke stacks", ["python", "ui-design/maintenance/smoke.py", "stacks"]),
]


def command_line(argv):
    return " ".join(shlex.quote(part) if part != "test_*.py" else f'"{part}"' for part in argv)


def run_gate(argv):
    """Run one gate from the repo root; return (exit_code, combined_output)."""
    proc = subprocess.run(
        [sys.executable, *argv[1:]],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def cmd_verify(args):
    total = len(GATES)
    started = time.monotonic()
    for number, (name, argv) in enumerate(GATES, 1):
        began = time.monotonic()
        code, output = run_gate(argv)
        elapsed = time.monotonic() - began
        if code == 0:
            print(f"[{number}/{total}] {name:<18} ok  ({elapsed:.1f}s)")
            continue
        print(f"[{number}/{total}] {name:<18} FAILED  (exit {code}, {elapsed:.1f}s)", file=sys.stderr)
        print(file=sys.stderr)
        print(output.rstrip(), file=sys.stderr)
        print(file=sys.stderr)
        print(f"FAIL: gate {number}/{total} ({name}). Re-run just this gate with:", file=sys.stderr)
        print(f"    {command_line(argv)}", file=sys.stderr)
        return 1
    print(f"OK: all {total} gates passed  ({time.monotonic() - started:.1f}s)")
    return 0


def build_arg_parser():
    return argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    args = build_arg_parser().parse_args()
    sys.exit(cmd_verify(args))


if __name__ == "__main__":
    main()
