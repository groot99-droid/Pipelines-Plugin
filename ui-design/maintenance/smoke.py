#!/usr/bin/env python3
"""Smoke-test the catalog's search registry against the counts spec.yaml declares.

Every domain in core.CSV_CONFIG and every stack in core.AVAILABLE_STACKS must
answer a focused query with at least one result. Catches registry/CSV
regressions early -- a domain or stack registered in core.py but missing its
CSV, or a CSV emptied by a botched merge.

The registry size is compared with ui-design/spec.yaml first, so adding or
removing a domain or stack fails loudly until spec.yaml is updated on purpose.
Each probe runs the real search.py entry point, not core.py directly.

Usage:
    python ui-design/maintenance/smoke.py domains [query]
    python ui-design/maintenance/smoke.py stacks  [query]

Exit codes:
    0 -- every domain (or stack) returned at least one result
    1 -- at least one returned none
    2 -- environment problem (search.py missing, spec.yaml unreadable, or a
         registry whose size disagrees with spec.yaml)
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parent
SCRIPTS_DIR = TOOL_ROOT / "catalog" / "scripts"
SEARCH = SCRIPTS_DIR / "search.py"
SPEC = TOOL_ROOT / "spec.yaml"

DOMAIN_PROBES = {
    "style": "minimalism ui glassmorphism design",
    "color": "healthcare app calming trustworthy",
    "chart": "time series chart trend dashboard",
    "landing": "hero testimonials cta conversion landing page",
    "product": "saas dashboard app product",
    "ux": "accessibility keyboard navigation focus",
    "typography": "font pairing heading body typography",
    "icons": "warning icon glyph symbol",
    "gsap": "gsap scroll reveal stagger animation",
    "react": "react performance rerender waterfall suspense",
    "web": "aria form accessibility input outline",
    "google-fonts": "google font family sans serif variable",
}

STACK_PROBES = {
    "react": "React useState for component local state",
    "nextjs": "Next.js App Router for a new project",
    "vue": "Vue Composition API for a new project",
    "svelte": "Svelte 5 $state rune for reactive state",
    "astro": "Astro islands architecture interactive components",
    "swiftui": "SwiftUI @State for view-local value state",
    "react-native": "functional React Native components",
    "flutter": "prefer StatelessWidget when Flutter UI has no mutable state",
    "nuxtjs": "Nuxt file-based page routing",
    "nuxt-ui": "install the Nuxt UI module",
    "html-tailwind": "Tailwind z-index utility scale for layered UI",
    "shadcn": "install shadcn components with the CLI",
    "jetpack-compose": "pure Jetpack Compose UI composables",
    "threejs": "Three.js OrbitControls must be imported separately",
    "angular": "standalone Angular components for a new project",
    "laravel": "reusable Laravel Blade UI components",
    "javafx": "launch JavaFX UI from an Application subclass",
    "wpf": "WPF INotifyPropertyChanged data binding updates",
    "winui": "WinUI InfoBar for status messages",
    "avalonia": "Avalonia XAML namespace declaration",
    "uno": "Uno Platform WinUI XAML API surface",
    "uwp": "UWP compiled x:Bind data binding",
}


class EnvironmentProblem(Exception):
    """The smoke test cannot run at all -- reported as exit 2, not a failed probe."""


def load_spec():
    try:
        import yaml
    except ImportError as exc:
        raise EnvironmentProblem(
            "The 'pyyaml' package is required to read spec.yaml. "
            "Install it with: pip install pyyaml") from exc
    try:
        with SPEC.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except OSError as exc:
        raise EnvironmentProblem(f"Cannot read {SPEC}: {exc}") from exc


def load_core():
    if not SEARCH.is_file():
        raise EnvironmentProblem(f"search.py not found at {SEARCH}")
    sys.path.insert(0, str(SCRIPTS_DIR))
    import core
    return core


def rel(path):
    return Path(path).relative_to(REPO_ROOT).as_posix()


def probe_count(query, flag, name):
    """Result count from `search.py <query> <flag> <name> -n 1 --json`; 0 on any error."""
    proc = subprocess.run(
        [sys.executable, str(SEARCH), query, flag, name, "-n", "1", "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        return 0
    if payload.get("error"):
        return 0
    return int(payload.get("count", 0))


def diagnostics(core, kind, name, query):
    try:
        if kind == "domains":
            result = core.search(query, domain=name, max_results=1, diagnostics=True)
        else:
            result = core.search_stack(query, name, max_results=1, diagnostics=True)
        return json.dumps(result.get("diagnostics", {}), sort_keys=True)
    except Exception:  # diagnostics are best-effort; never mask the real failure
        return "unavailable"


def run(kind, args):
    core = load_core()
    if kind == "domains":
        names, probes, flag = list(core.CSV_CONFIG), DOMAIN_PROBES, "--domain"
    else:
        names, probes, flag = list(core.AVAILABLE_STACKS), STACK_PROBES, "--stack"

    declared = load_spec().get(kind) or []
    if len(names) != len(declared):
        raise EnvironmentProblem(
            f"core.py registers {len(names)} {kind}, spec.yaml declares {len(declared)}. "
            f"Update spec.yaml after an intentional registry change.")

    width = max(len(n) for n in names) + 2
    if args.query:
        print(f"Smoke-testing {len(names)} {kind} with override query {args.query!r}:")
    else:
        print(f"Smoke-testing {len(names)} {kind} with focused probes:")

    failed = []
    for name in names:
        query = args.query or probes.get(name)
        if not query:
            print(f"  FAIL  {name:<{width}} missing smoke probe", file=sys.stderr)
            failed.append(name)
            continue
        count = probe_count(query, flag, name)
        if count > 0:
            print(f"  PASS  {name:<{width}} {count}")
            continue
        print(f"  FAIL  {name:<{width}} 0 results, diagnostics={diagnostics(core, kind, name, query)}",
              file=sys.stderr)
        print(f"        retry: python {rel(SEARCH)} {shlex.quote(query)} {flag} {name} -n 1 --json",
              file=sys.stderr)
        failed.append(name)

    print()
    if failed:
        print(f"FAIL: {len(failed)}/{len(names)} {kind} returned 0 results: {', '.join(failed)}",
              file=sys.stderr)
        print(f"      rerun all: python {rel(Path(__file__).resolve())} {kind}", file=sys.stderr)
        return 1
    print(f"OK: {len(names)}/{len(names)} {kind} returned at least 1 result")
    return 0


def cmd_domains(args):
    return run("domains", args)


def cmd_stacks(args):
    return run("stacks", args)


def build_arg_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_domains = sub.add_parser("domains", help="Probe every registered search domain.")
    p_domains.add_argument("query", nargs="?", default=None,
                           help="Use this query for every domain instead of the built-in probes.")
    p_domains.set_defaults(func=cmd_domains)

    p_stacks = sub.add_parser("stacks", help="Probe every registered stack.")
    p_stacks.add_argument("query", nargs="?", default=None,
                          help="Use this query for every stack instead of the built-in probes.")
    p_stacks.set_defaults(func=cmd_stacks)

    return parser


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        sys.exit(args.func(args))
    except EnvironmentProblem as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
