"""The headless branch of assemble-3d: run the assembly plan in a Blender with
no window.

    blender -b --factory-startup --python studio/pipeline/bpy/assemble.py -- \
        --layout <run folder>/assembly.json --out <run folder>/blender [--steps import,normalize,...]

It must run inside Blender (or a Python with the `bpy` module). It starts from
an empty scene, then runs each step of bpy/assemble_plan.py in order: the very
code that `assemble_plan.py emit` prints for the live branch. It writes, under
--out: the .blend, the .glb and the preview the layout names, steps/<step>.py
(the code as it ran, for the note's Method) and assemble_report.json (what
each step printed). A step that fails stops the run; what ran before it is
in the report.

Exit codes: 0 done, 1 the layout or a step failed, 2 usage error.
"""

import argparse
import contextlib
import io
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import assemble_plan as plan_module  # noqa: E402

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2


def arguments(argv):
    if argv is None:
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="assemble.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--steps", default=",".join(plan_module.STEPS),
                        help=f"comma-separated, in this order: {','.join(plan_module.STEPS)}")
    parser.add_argument("--keep-scene", action="store_true",
                        help="do not empty the scene first (the default empties it)")
    return parser.parse_args(argv)


def run_step(code, step):
    """Run one step's code, and return (the ROSW reports it printed, all output)."""
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        exec(compile(code, f"<assemble step {step}>", "exec"), {"__name__": f"rosw_{step}"})
    output = captured.getvalue()
    reports = [json.loads(line[5:]) for line in output.splitlines() if line.startswith("ROSW ")]
    return reports, output


def main(argv=None):
    args = arguments(argv)
    steps = [s for s in args.steps.split(",") if s]
    unknown = [s for s in steps if s not in plan_module.STEPS]
    if unknown or steps != [s for s in plan_module.STEPS if s in steps]:
        print(f"error     --steps takes these, in this order: {','.join(plan_module.STEPS)}", file=sys.stderr)
        return EXIT_USAGE
    try:
        plan = plan_module.load(args.layout, args.out)
    except plan_module.Invalid as problem:
        print(f"invalid   {problem}", file=sys.stderr)
        return EXIT_FAILED
    missing = plan_module.missing_models(plan)
    if missing:
        print(f"invalid   no model at {', '.join(missing)}", file=sys.stderr)
        return EXIT_FAILED
    import bpy  # only now: the plan can be checked without Blender

    out = Path(plan["out"])
    (out / "steps").mkdir(parents=True, exist_ok=True)
    if not args.keep_scene:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    report = {"blender": bpy.app.version_string, "layout": str(Path(args.layout).resolve()), "steps": []}
    status = EXIT_OK
    for step in steps:
        code = plan_module.step_code(plan, step)
        (out / "steps" / f"{step}.py").write_text(code, encoding="utf-8", newline="\n")
        try:
            found, output = run_step(code, step)
        except Exception:  # a step's failure is the report's, not a crash
            report["steps"].append({"step": step, "failed": traceback.format_exc(limit=3)})
            print(f"FAILED    {step}", file=sys.stderr)
            print(report["steps"][-1]["failed"], file=sys.stderr)
            status = EXIT_FAILED
            break
        report["steps"].extend(found or [{"step": step, "printed": output[-2000:]}])
        print(f"done      {step}: {json.dumps(found[-1] if found else {})[:300]}")
    (out / "assemble_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8",
                                              newline="\n")
    print(f"report    {out / 'assemble_report.json'}")
    return status


if __name__ == "__main__":
    sys.exit(main())
