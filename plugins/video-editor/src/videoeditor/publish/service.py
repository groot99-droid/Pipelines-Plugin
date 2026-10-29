"""Every safety rule lives here, in one place, so no platform module can bypass them.

  1. Sending needs `confirm=True` (the CLI's --yes). Without it you only ever get a plan.
  2. Nothing public without `public=True`. Where a platform has a private/draft mode that is the default;
     where it has none (Bluesky, X) the platform cannot be used without an explicit public opt-in.
  3. Platforms that cost money (X) additionally need `accept_cost=True`.
  4. Validation errors block sending.
  5. The same video + platform + mode + text is sent once; a repeat needs `force=True`.
"""
from __future__ import annotations

from pathlib import Path

from videoeditor.publish import ledger
from videoeditor.publish.base import Publisher, Result
from videoeditor.publish.errors import NotAllowed, PublishError, ValidationFailed
from videoeditor.publish.package import PostPackage


def get_publisher(platform: str) -> Publisher:
    from videoeditor.publish.platforms import get

    return get(platform)


def resolve_mode(pub: Publisher, public: bool) -> str:
    spec = pub.spec
    if public:
        if "public" not in spec.modes:
            raise NotAllowed(f"{spec.title} has no public mode here")
        return "public"
    if "draft" not in spec.modes:
        raise NotAllowed(f"{spec.title} has no private/draft mode, so it can only be used with --public "
                         f"(and --yes). Nothing was sent.")
    return "draft"


def make_plan(pkg: PostPackage, platform: str, *, public: bool = False, publisher: Publisher | None = None) -> dict:
    pub = publisher or get_publisher(platform)
    spec = pub.spec
    out = {"platform": platform, "title": spec.title, "issues": pub.validate(pkg), "mode": None, "steps": [],
           "blocked": None, "gated": spec.gated_note, "cost": spec.cost_note}
    try:
        out["mode"] = resolve_mode(pub, public)
        out["steps"] = pub.plan(pkg, out["mode"])
    except NotAllowed as e:
        out["blocked"] = str(e)
    return out


def send(pkg: PostPackage, platform: str, *, edit_dir: Path, confirm: bool, public: bool = False,
         accept_cost: bool = False, force: bool = False, publisher: Publisher | None = None) -> Result:
    pub = publisher or get_publisher(platform)
    spec = pub.spec
    if not confirm:
        raise NotAllowed("dry run: nothing was sent. Re-run with --yes to send.")
    mode = resolve_mode(pub, public)
    if spec.cost_note and not accept_cost:
        raise NotAllowed(f"{spec.title} can cost money ({spec.cost_note}). Re-run with --accept-cost to proceed.")
    errors = [i for i in pub.validate(pkg) if i.severity == "error"]
    if errors:
        raise ValidationFailed(platform, errors)
    key = ledger.idempotency_key(pkg.fingerprint(), platform, mode, pkg.full_text(platform))
    prior = ledger.find_success(edit_dir, key)
    if prior and not force:
        raise NotAllowed(f"already sent to {platform} ({prior.get('mode')}, {prior.get('ts')}"
                         f"{', ' + prior['url'] if prior.get('url') else ''}). Use --force to send again.")
    try:
        res = pub.send(pkg, mode, idempotency_key=key)
    except PublishError as e:
        ledger.record(edit_dir, key=key, platform=platform, mode=mode, status="failed", note=str(e)[:300])
        raise
    ledger.record(edit_dir, key=key, platform=platform, mode=mode, status=res.status, remote_id=res.id,
                  url=res.url, note=res.note)
    return res
