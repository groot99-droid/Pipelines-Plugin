"""`ve publish ...` command line. All behaviour lives in service.py; this file only parses arguments and prints."""
from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from videoeditor.publish import handoff, ledger, package, secrets
from videoeditor.publish import service
from videoeditor.publish.errors import PublishError
from videoeditor.publish.platforms import NAMES, get


def _edit_dir(a) -> Path:
    return (a.edit_dir or Path("edit")).resolve()


def _platforms(arg: str | None, pkg: package.PostPackage | None = None) -> list[str]:
    names = [p.strip() for p in arg.split(",") if p.strip()] if arg else (pkg.platforms if pkg else [])
    bad = [n for n in names if n not in NAMES]
    if bad:
        raise PublishError(f"unknown platform(s): {', '.join(bad)} (choose from {', '.join(NAMES)})")
    return names


def cmd_init(a) -> None:
    import getpass

    pub = get(a.platform)
    print(pub.init(ask=input, ask_secret=getpass.getpass, say=print, manual=a.manual, port=a.port))


def cmd_prepare(a) -> None:
    caption = a.caption if a.caption is not None else (a.caption_file.read_text(encoding="utf-8") if a.caption_file else None)
    if caption is None:
        raise PublishError("give --caption or --caption-file")
    overrides: dict = {}
    for item in a.caption_for or []:
        plat, _, text = item.partition("=")
        if plat not in NAMES or not text:
            raise PublishError(f"--caption-for expects PLATFORM=TEXT, got {item!r}")
        overrides.setdefault(plat, {})["caption"] = text
    kids = True if a.made_for_kids else False if a.not_made_for_kids else None
    names = _platforms(a.platforms)
    pkg = package.build(a.video, caption, title=a.title, tags=[t for t in (a.tags or "").split(",") if t.strip()],
                        platforms=names, alt_text=a.alt, ai_generated=a.ai_generated, branded_content=a.branded,
                        made_for_kids=kids, overrides=overrides)
    path = package.save(pkg, _edit_dir(a))
    print(f"package saved: {path}")
    _print_plans(pkg, names, public=False)


def _print_plans(pkg, names: list[str], public: bool) -> None:
    if not names:
        print("no platforms chosen yet: add --platforms youtube,bluesky,... to `ve publish prepare`")
    for n in names:
        p = service.make_plan(pkg, n, public=public)
        print(f"\n== {p['title']} ==")
        mode = p["mode"] or "(not allowed without --public)"
        print(f"mode: {mode}" + (f"  [{get(n).spec.draft_note}]" if p["mode"] == "draft" else ""))
        if p["blocked"]:
            print(f"blocked: {p['blocked']}")
        if p["gated"]:
            print(f"note: {p['gated']}")
        if p["cost"]:
            print(f"COST: {p['cost']}")
        for i in p["issues"]:
            print(f"  {'ERROR' if i.severity == 'error' else 'warn '} {i.message}")
        for s in p["steps"]:
            print(f"  - {s}")
    if names:
        print("\nNothing was sent. To send: ve publish send --platform NAME --yes [--public]")


def cmd_plan(a) -> None:
    pkg = package.load(_edit_dir(a))
    _print_plans(pkg, _platforms(a.platforms, pkg), public=a.public)


def cmd_send(a) -> None:
    edit = _edit_dir(a)
    pkg = package.load(edit)
    if a.platform not in NAMES:
        raise PublishError(f"unknown platform '{a.platform}'")
    res = service.send(pkg, a.platform, edit_dir=edit, confirm=a.yes, public=a.public, accept_cost=a.accept_cost, force=a.force)
    print(f"{res.platform}: {res.status} ({res.mode})" + (f"\n  id:  {res.id}" if res.id else "") +
          (f"\n  url: {res.url}" if res.url else "") + (f"\n  {res.note}" if res.note else ""))


def cmd_handoff(a) -> None:
    pkg = package.load(_edit_dir(a))
    for n in _platforms(a.platform, pkg):
        print(handoff.checklist(pkg, n, instance=secrets.get("mastodon", "instance")))
        print()
        url = handoff.UPLOAD_PAGES.get(n)
        if a.open and url:
            webbrowser.open(url)


def cmd_status(a) -> None:
    print("configured:")
    for n in NAMES:
        print(f"  {n:10s} {'yes' if get(n).is_configured() else 'no'}")
    entries = ledger.read(_edit_dir(a))
    print(f"\nledger ({len(entries)} entries):")
    for e in entries[-10:]:
        print(f"  {e['ts']}  {e['platform']:10s} {e['mode']:6s} {e['status']:7s} {e.get('url') or e.get('id') or ''}")
    print(f"\nkeyring: {'available' if secrets.keyring_available() else 'NOT available (use VE_<PLATFORM>_* environment variables)'}")


SECRET_NAMES = ("token", "client_id", "client_secret", "identifier", "app_password", "instance", "user_id", "service")


def cmd_revoke(a) -> None:
    gone = [n for n in SECRET_NAMES if secrets.delete(a.platform, n)]
    print(f"removed from the keyring: {', '.join(gone) or 'nothing'}")
    print("Also remove this app's access in the platform's own security settings; environment variables are untouched.")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="ve publish", description="Send a finished video through official platform APIs (dry run by default)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def edit(p):
        p.add_argument("--edit-dir", type=Path, help="default: ./edit")

    p = sub.add_parser("init", help="store credentials / log in to a platform")
    p.add_argument("platform", choices=NAMES)
    p.add_argument("--manual", action="store_true", help="paste the redirect URL instead of listening on localhost")
    p.add_argument("--port", type=int, default=0, help="fixed loopback port for the OAuth redirect")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("prepare", help="build and validate the publishing package (no network)")
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--caption")
    p.add_argument("--caption-file", type=Path)
    p.add_argument("--caption-for", action="append", metavar="PLATFORM=TEXT", help="per-platform caption (repeatable)")
    p.add_argument("--title")
    p.add_argument("--tags", help="comma separated, without #")
    p.add_argument("--alt", help="alt text / description for accessibility")
    p.add_argument("--platforms", help="comma separated: " + ",".join(NAMES))
    p.add_argument("--ai-generated", action="store_true", help="disclose AI-generated/synthetic content where a platform has a field")
    p.add_argument("--branded", action="store_true", help="paid partnership / branded content disclosure")
    k = p.add_mutually_exclusive_group()
    k.add_argument("--made-for-kids", action="store_true")
    k.add_argument("--not-made-for-kids", action="store_true")
    edit(p)
    p.set_defaults(fn=cmd_prepare)

    p = sub.add_parser("plan", help="show what each platform would receive (no network)")
    p.add_argument("--platforms")
    p.add_argument("--public", action="store_true", help="plan the public variant")
    edit(p)
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("send", help="send to ONE platform (needs --yes)")
    p.add_argument("--platform", required=True, choices=NAMES)
    p.add_argument("--yes", action="store_true", help="actually send; without it this is a dry run")
    p.add_argument("--public", action="store_true", help="post publicly (default is the platform's private/draft mode)")
    p.add_argument("--accept-cost", action="store_true", help="acknowledge platforms that charge per post")
    p.add_argument("--force", action="store_true", help="send even if the same post was already sent")
    edit(p)
    p.set_defaults(fn=cmd_send)

    p = sub.add_parser("handoff", help="no API: print where to upload and the caption to paste")
    p.add_argument("--platform", help="comma separated; default: the package's platforms")
    p.add_argument("--open", action="store_true", help="open the platform's upload page in your browser")
    edit(p)
    p.set_defaults(fn=cmd_handoff)

    p = sub.add_parser("status", help="which platforms are configured, and recent sends")
    edit(p)
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("revoke", help="delete this platform's stored credentials from the keyring")
    p.add_argument("platform", choices=NAMES)
    p.set_defaults(fn=cmd_revoke)

    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except PublishError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1) from None
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1) from None
    except EOFError:
        print("error: this step needs interactive input (a terminal). Set the VE_<PLATFORM>_* environment variables instead.",
              file=sys.stderr)
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
