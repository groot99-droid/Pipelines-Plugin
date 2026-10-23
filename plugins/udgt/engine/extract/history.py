"""How it was made: the game's git history, read with `git log` (read-only).

Kept: every commit (short hash, date, subject, the decision ids its subject cites), one node per
merged pull request (number, branch, date, round), per-day counts, and per-document change
counts with first and last dates. A shallow clone is reported, since its history starts late.
"""

import re
import subprocess

from .common import Part

SEP = "\x1f"


def git(game, *args):
    try:
        out = subprocess.run(["git", "-C", str(game), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def extract(game, profile, doc_paths=()):
    spec = profile.get("history", {})
    part = Part()
    log = git(game, "log", f"--format=%h{SEP}%ad{SEP}%s{SEP}%p", "--date=short")
    if log is None:
        part.notes.append("not a git checkout, or git is missing: no history")
        return part, {}
    shallow = (git(game, "rev-parse", "--is-shallow-repository") or "").strip() == "true"
    head = (git(game, "rev-parse", "HEAD") or "").strip()
    pr_rx = re.compile(spec.get("pr", r"Merge pull request #(\d+) from \S+?/(\S+)"))
    cite_rx = re.compile(spec.get("cites", r"\b(A\d{1,3})\b"))
    round_rx = [re.compile(p) for p in spec.get("round", [r"\br(\d+)-", r"\bRound (\d+)\b"])]
    commits, days = [], {}
    for line in log.splitlines():
        parts = line.split(SEP)
        if len(parts) < 4:
            continue
        short, date, subject, parents = parts
        cites = sorted(set(cite_rx.findall(subject)))
        merge = len(parents.split()) > 1
        commits.append({"h": short, "d": date, "s": subject, "m": merge, "ids": cites})
        days[date] = days.get(date, 0) + 1
        m = pr_rx.search(subject)
        if m:
            num, branch = m.group(1), m.group(2)
            rnd = next((int(r.search(branch).group(1)) for r in round_rx if r.search(branch)), None)
            part.node(f"pr:{num}", "pr", "history", f"#{num} {branch}", source=None,
                      meta={"date": date, "branch": branch, "round": rnd, "commit": short})
        for cid in cites:
            part.edge(f"commit:{short}", f"dec:{cid}", "cites")
    if shallow:
        part.notes.append("the game checkout is shallow: run `git fetch --unshallow` for the full history")
    doc_hist = {}
    for relpath in doc_paths:
        out = git(game, "log", "--follow", "--format=%ad", "--date=short", "--", relpath)
        if out:
            dates = out.split()
            doc_hist[relpath] = {"changes": len(dates), "first": dates[-1], "last": dates[0]}
    first = commits[-1]["d"] if commits else None
    last = commits[0]["d"] if commits else None
    part.node("history:summary", "history", "history", "Git history",
              meta={"commits": len(commits), "merges": sum(c["m"] for c in commits),
                    "first": first, "last": last, "shallow": shallow, "head": head,
                    "days": dict(sorted(days.items()))})
    return part, {"commits": commits, "docs": doc_hist, "head": head, "shallow": shallow}
