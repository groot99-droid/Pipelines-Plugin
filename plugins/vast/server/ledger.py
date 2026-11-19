"""The spend ledger: quotes, rentals, tunnels and the biweekly band budgets.

State lives in VAST_STATE_DIR (default ~/.vast-mcp/):
  state.json    quotes, rentals and tunnels, rewritten atomically after each change
  events.jsonl  an append-only record of every spend, run and stop (never a key, never a link)

A price band is a ceiling on $/hr with a budget of GPU hours over a rolling window (14 days by
default), from limits.json. A rental counts against the band its $/hr falls in:
  * a rental that has ended counts the hours it ran inside the window;
  * a live rental counts from its start to its deadline (or to now, if it has run past it), so
    the hours it may still use are reserved until it ends.
"""

from __future__ import annotations

import json
import os
import secrets
import time
from pathlib import Path

HOUR = 3600.0
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def load_limits(path=None):
    path = Path(path) if path else PLUGIN_ROOT / "limits.json"
    limits = json.loads(path.read_text(encoding="utf-8"))
    bands = sorted(limits["bands"], key=lambda band: band["max_dph"])
    for band in bands:
        if not (band["max_dph"] > 0 and band["hours"] > 0):
            raise ValueError("a band needs a positive max_dph and hours")
    limits["bands"] = bands
    return limits


def state_dir(environ=None):
    environ = os.environ if environ is None else environ
    from vast_api import expand, home  # beside this file
    return expand(environ.get("VAST_STATE_DIR") or home(environ) / ".vast-mcp", environ)


class Ledger:
    def __init__(self, folder, limits, clock=time.time):
        self.folder = Path(folder)
        self.limits = limits
        self.clock = clock
        self.path = self.folder / "state.json"
        self.events_path = self.folder / "events.jsonl"

    # ── storage ──────────────────────────────────────────────────────────────

    def load(self):
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
        state.setdefault("quotes", {})
        state.setdefault("rentals", [])
        state.setdefault("tunnels", {})
        return state

    def save(self, state):
        self.folder.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.folder, 0o700)
        except OSError:
            pass
        part = self.path.with_suffix(".part")
        part.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(part, self.path)

    def event(self, kind, **fields):
        self.folder.mkdir(parents=True, exist_ok=True)
        record = {"at": round(self.clock(), 3), "event": kind, **fields}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    # ── bands ────────────────────────────────────────────────────────────────

    def band_for(self, dph):
        for band in self.limits["bands"]:
            if dph <= band["max_dph"] + 1e-9:
                return band
        return None

    def window_seconds(self):
        return float(self.limits.get("window_days", 14)) * 86400.0

    def counted_seconds(self, rental, now):
        """Seconds of `rental` inside the window that ends at `now`, reservation included."""
        start = rental["started"]
        if rental.get("ended") is not None:
            end = rental["ended"]
        else:
            end = max(rental["deadline"], now)
        window_start = now - self.window_seconds()
        return max(0.0, end - max(start, window_start))

    def band_usage(self, state=None):
        state = self.load() if state is None else state
        now = self.clock()
        rows = []
        for band in self.limits["bands"]:
            seconds = sum(self.counted_seconds(rental, now) for rental in state["rentals"]
                          if rental["band"] == band["max_dph"])
            used = seconds / HOUR
            rows.append({"max_dph": band["max_dph"], "budget_hours": band["hours"],
                         "counted_hours": round(used, 2),
                         "remaining_hours": round(max(0.0, band["hours"] - used), 2)})
        return rows

    def remaining_hours(self, band, state=None):
        for row in self.band_usage(state):
            if row["max_dph"] == band["max_dph"]:
                return row["remaining_hours"]
        return 0.0

    # ── quotes ───────────────────────────────────────────────────────────────

    def new_quote(self, fields):
        state = self.load()
        now = self.clock()
        ttl = float(self.limits.get("quote_ttl_seconds", 900))
        state["quotes"] = {key: quote for key, quote in state["quotes"].items()
                           if quote.get("used") or now - quote["created"] < 7 * 86400}
        quote_id = "q_" + secrets.token_hex(6)
        quote = {**fields, "quote_id": quote_id, "created": now, "expires": now + ttl, "used": False}
        state["quotes"][quote_id] = quote
        self.save(state)
        return quote

    def take_quote(self, quote_id):
        state = self.load()
        quote = state["quotes"].get(quote_id)
        if quote is None:
            raise LookupError("unknown")
        if quote.get("used"):
            raise LookupError("used")
        if self.clock() > quote["expires"]:
            raise LookupError("expired")
        return state, quote

    # ── rentals ──────────────────────────────────────────────────────────────

    def live_rentals(self, state=None):
        state = self.load() if state is None else state
        return [rental for rental in state["rentals"] if rental.get("ended") is None]

    def rental(self, instance_id, state=None):
        state = self.load() if state is None else state
        for rental in state["rentals"]:
            if rental["instance_id"] == int(instance_id):
                return rental
        return None

    def end_rental(self, instance_id, how, at=None):
        state = self.load()
        now = self.clock() if at is None else at
        for rental in state["rentals"]:
            if rental["instance_id"] == int(instance_id) and rental.get("ended") is None:
                rental["ended"] = now
                rental["ended_how"] = how
                self.save(state)
                self.event("rental_ended", instance_id=int(instance_id), how=how,
                           hours=round((rental["ended"] - rental["started"]) / HOUR, 3))
                return rental
        return None

    def spend_summary(self, state=None):
        state = self.load() if state is None else state
        now = self.clock()
        live = []
        for rental in self.live_rentals(state):
            hours = (now - rental["started"]) / HOUR
            live.append({"instance_id": rental["instance_id"], "dph": rental["dph"],
                         "hours_run": round(hours, 2),
                         "cost_so_far_usd": round(hours * rental["dph"], 2),
                         "hours_left": round((rental["deadline"] - now) / HOUR, 2),
                         "over_deadline": now > rental["deadline"]})
        return {"live": live, "bands": self.band_usage(state)}

    # ── tunnels ──────────────────────────────────────────────────────────────

    def set_tunnel(self, key, record):
        state = self.load()
        if record is None:
            state["tunnels"].pop(key, None)
        else:
            state["tunnels"][key] = record
        self.save(state)
