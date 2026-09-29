"""Tests for plot_logic.py. stdlib unittest; run from the pipeline folder:

    python -m unittest discover -s tests -v
"""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
sys.path.insert(0, str(PIPELINE))

import plot_logic as pl  # noqa: E402

SPEC = pl.load_spec()
VAULT = (PIPELINE / SPEC["vault_root"]).resolve()


def ledger(rows, *, mode="horror-prose", registers="", ending="cyclical", cols=None):
    """Build a ledger document. rows are (link, because, beat, response, changes) for
    the base columns, with any track values appended when cols adds track columns."""
    cols = cols or ["#", "Link", "Because", "Beat", "Response", "Changes"]
    out = ["## Causal ledger", ""]
    if mode:
        out.append(f"Mode: {mode}")
    if registers:
        out.append(f"Register: {registers}")
    out += ["", "| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for i, r in enumerate(rows, start=1):
        link, because, beat, response, changes, *track = r
        cells = [str(i), link, because, beat, response] + list(track) + [changes]
        out.append("| " + " | ".join(cells) + " |")
    if ending:
        out += ["", f"Ending: {ending}"]
    return "\n".join(out) + "\n"


def run(doc, mode=None, registers=None, spec=SPEC):
    (lg, res), = pl.check_text(doc, spec, mode, registers)
    return res


def codes(res, level=None):
    return [f.code for f in res["findings"] if level is None or f.level == level]


CLEAN = [
    ("open", "-", "Lamp dims early.", "denies", "He logs it instead of looking"),
    ("T", '1 "logs it"', "He logs everything to be safe.", "investigates", "The log outgrows the job"),
    ("B", '2 "the log"', "A page in his own hand he cannot remember.", "denies", "An entry with no memory attached"),
    ("T", '3 "no memory"', "He counts the stair treads to test himself.", "investigates", "The counts disagree by night"),
    ("B", '1 "looking"', "The relief boat does not come.", "none", "No one is coming before the log is done"),
]


class ParseBecause(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(pl.parse_because('3 "weather front"'), ([3], "weather front"))
        self.assertEqual(pl.parse_because("4+5 the strait"), ([4, 5], "the strait"))
        self.assertEqual(pl.parse_because("2: gull"), ([2], "gull"))
        self.assertEqual(pl.parse_because("—"), ([], ""))
        self.assertEqual(pl.parse_because("**7** “the rail”"), ([7], "the rail"))
        self.assertEqual(pl.parse_because("2"), ([2], ""))


class CoreChecks(unittest.TestCase):
    def test_clean_ledger_passes(self):
        res = run(ledger(CLEAN))
        self.assertTrue(res["ok"], codes(res))
        self.assertEqual(res["stats"]["links"], {"open": 1, "T": 2, "B": 2, "A": 0})

    def test_no_ledger(self):
        (lg, res), = pl.check_text("# Outline\n\nJust prose.\n", SPEC)
        self.assertFalse(res["ok"])
        self.assertEqual(codes(res), ["no-ledger"])

    def test_missing_required_column(self):
        doc = "## Causal ledger\n\n| # | Link | Beat |\n|---|---|---|\n| 1 | open | x |\n\nEnding: cyclical\n"
        self.assertIn("columns", codes(run(doc), "error"))

    def test_and_then_is_an_error_at_budget_zero(self):
        rows = list(CLEAN)
        rows[2] = ("A", "-", "A gull will not land.", "denies", "Filed as a weather front")
        res = run(ledger(rows))
        self.assertFalse(res["ok"])
        self.assertIn("and-then", codes(res, "error"))

    def test_and_then_budget_can_be_raised(self):
        spec = copy.deepcopy(SPEC)
        spec["plot_logic"]["defaults"]["max_and_then"] = 1
        rows = list(CLEAN)
        rows[2] = ("A", "-", "A gull will not land.", "denies", "Filed as a weather front")
        rows[3] = ("A", "-", "The door is open again.", "denies", "He indicts himself")
        res = run(ledger(rows), spec=spec)
        levels = [(f.row, f.level) for f in res["findings"] if f.code == "and-then"]
        self.assertEqual(sorted(levels), [(3, "warn"), (4, "error")])   # first within budget, second over

    def test_handle_must_be_in_the_cited_beat(self):
        rows = list(CLEAN)
        rows[2] = ("B", '2 "the gull"', "A page in his own hand.", "denies", "An entry with no memory")
        res = run(ledger(rows))
        self.assertIn("handle-not-found", codes(res, "error"))

    def test_handle_only_in_beat_is_weak(self):
        rows = list(CLEAN)
        rows[2] = ("B", '2 "everything"', "A page in his own hand.", "denies", "An entry with no memory")
        res = run(ledger(rows))
        self.assertTrue(res["ok"], codes(res))
        self.assertIn("handle-weak", codes(res, "warn"))

    def test_missing_handle_warns(self):
        rows = list(CLEAN)
        rows[1] = ("T", "1", "He logs everything.", "investigates", "The log outgrows the job")
        self.assertIn("handle-missing", codes(run(ledger(rows)), "warn"))

    def test_handle_matching_ignores_typography_not_words(self):
        rows = list(CLEAN)
        rows[1] = ("T", "1 “LOGS it!”", "He logs everything.", "investigates", "The log outgrows the job")
        self.assertTrue(run(ledger(rows))["ok"])

    def test_because_must_point_backwards(self):
        rows = list(CLEAN)
        rows[1] = ("T", '4 "the counts"', "He logs everything.", "investigates", "The log outgrows the job")
        self.assertIn("because-invalid", codes(run(ledger(rows)), "error"))

    def test_t_and_b_need_a_because(self):
        rows = list(CLEAN)
        rows[1] = ("T", "-", "He logs everything.", "investigates", "The log outgrows the job")
        self.assertIn("because-missing", codes(run(ledger(rows)), "error"))

    def test_first_row_must_be_open_and_open_takes_no_because(self):
        rows = list(CLEAN)
        rows[0] = ("T", "-", "Lamp dims early.", "denies", "He logs it")
        self.assertIn("first-not-open", codes(run(ledger(rows)), "error"))
        rows[0] = ("open", '2 "x"', "Lamp dims early.", "denies", "He logs it")
        self.assertIn("open-because", codes(run(ledger(rows)), "error"))

    def test_multi_parent_handle(self):
        rows = [
            ("open", "-", "Yrsa wakes weeping.", "none", "She feels a pull toward the centre"),
            ("open", "-", "Corvin wakes starving.", "none", "He is drawn to the strait"),
            ("T", '1+2 "the strait"', "They meet.", "none", "They stand together"),
        ]
        res = run(ledger(rows, mode="epic-fantasy", ending="cost-paid"))
        self.assertTrue(res["ok"], codes(res))

    def test_link_aliases(self):
        rows = [
            ("open", "-", "Lamp dims.", "denies", "He logs it"),
            ("therefore", '1 "logs it"', "He logs more.", "denies", "A bigger log"),
            ("But", '2 "bigger log"', "A page he did not write.", "denies", "An unowned page"),
        ]
        self.assertTrue(run(ledger(rows))["ok"])

    def test_row_numbering(self):
        doc = ledger(CLEAN).replace("| 3 | B |", "| 7 | B |")
        self.assertIn("row-number", codes(run(doc), "error"))


class Shape(unittest.TestCase):
    def _chain(self, links):
        rows = [("open", "-", "Start.", "denies", "state 0")]
        for i, k in enumerate(links, start=1):
            rows.append((k, f'{i} "state {i - 1}"', f"Beat {i}.", "denies", f"state {i}"))
        return rows

    def test_pile_on(self):
        res = run(ledger(self._chain(["B", "B", "B", "T"])))
        self.assertIn("pile-on", codes(res, "warn"))

    def test_smooth_run_and_no_but(self):
        res = run(ledger(self._chain(["T", "T", "T", "T"])))
        self.assertIn("smooth-run", codes(res, "warn"))
        self.assertIn("no-but", codes(res, "warn"))

    def test_alternation_is_clean(self):
        res = run(ledger(self._chain(["B", "T", "B", "T"])))
        self.assertFalse([f for f in res["findings"] if f.level in ("error", "warn")], codes(res))

    def test_a_row_resets_the_run(self):
        spec = copy.deepcopy(SPEC)
        spec["plot_logic"]["defaults"]["max_and_then"] = 9
        rows = self._chain(["B", "B", "A", "B"])
        res = run(ledger(rows), spec=spec)
        self.assertNotIn("pile-on", codes(res))

    def test_no_change_and_repeat_change(self):
        rows = self._chain(["B", "T", "B"])
        rows[2] = rows[2][:4] + ("-",)
        rows[3] = (rows[3][0], '2 "state 1"', rows[3][2], rows[3][3], "state 1")
        res = run(ledger(rows))
        self.assertIn("no-change", codes(res, "warn"))
        self.assertIn("repeat-change", codes(res, "warn"))

    def test_callbacks_are_counted_not_required(self):
        res = run(ledger(self._chain(["B", "T", "B", "T", "B"])))
        self.assertIn("no-callback", codes(res, "info"))
        rows = self._chain(["B", "T", "B", "T", "B"])
        rows[5] = (rows[5][0], '1 "state 0"', rows[5][2], rows[5][3], rows[5][4])
        self.assertNotIn("no-callback", codes(run(ledger(rows))))

    def test_response_values_are_checked(self):
        rows = list(CLEAN)
        rows[1] = ("T", '1 "logs it"', "x", "panics", "The log outgrows the job")
        self.assertIn("response-invalid", codes(run(ledger(rows)), "error"))


class Endings(unittest.TestCase):
    def test_missing_and_unknown(self):
        self.assertIn("ending-missing", codes(run(ledger(CLEAN, ending="")), "error"))
        self.assertIn("ending-unknown", codes(run(ledger(CLEAN, ending="happily")), "error"))

    def test_horror_rejects_a_rescue_as_an_error(self):
        res = run(ledger(CLEAN, ending="cost-paid"))
        self.assertIn("ending-mode", codes(res, "error"))
        self.assertFalse(res["ok"])

    def test_fantasy_only_warns(self):
        res = run(ledger(CLEAN, mode="epic-fantasy", ending="consumed"))
        self.assertIn("ending-mode", codes(res, "warn"))
        self.assertTrue(res["ok"])

    def test_disabled_mode_is_not_applicable(self):
        res = run(ledger(CLEAN, mode="essay-self-help", ending=""))
        self.assertTrue(res["ok"])
        self.assertEqual(codes(res), ["not-applicable"])

    def test_unknown_mode_and_register_are_config_errors(self):
        with self.assertRaises(pl.ConfigError):
            run(ledger(CLEAN, mode="no-such-mode"))
        with self.assertRaises(pl.ConfigError):
            run(ledger(CLEAN), registers=["no-such-register"])


COSMIC_COLS = ["#", "Link", "Because", "Beat", "Response", "Knows", "Changes"]


def cosmic(knows, responses=None):
    base = [
        ("open", "-", "Noticed.", "denies", "step 1"),
        ("T", '1 "step 1"', "Looked.", "investigates", "step 2"),
        ("B", '2 "step 2"', "Found.", "denies", "step 3"),
        ("T", '3 "step 3"', "Followed.", "investigates", "step 4"),
        ("B", '4 "step 4"', "Learned.", "complicit", "step 5"),
    ]
    rows = []
    for i, ((link, because, beat, resp, changes), k) in enumerate(zip(base, knows)):
        rows.append((link, because, beat, (responses or {}).get(i, resp), changes, k))
    return ledger(rows, registers="cosmic", cols=COSMIC_COLS, ending="irreversible-knowledge")


class CosmicRegister(unittest.TestCase):
    def test_good_ladder(self):
        res = run(cosmic(["anomaly", "anomaly", "pattern", "pattern", "scale"]))
        self.assertTrue(res["ok"], codes(res))

    def test_knowledge_cannot_fall(self):
        res = run(cosmic(["anomaly", "pattern", "anomaly", "pattern", "scale"]))
        self.assertIn("track-monotone", codes(res, "error"))

    def test_skipped_rung_warns(self):
        res = run(cosmic(["anomaly", "anomaly", "pattern", "implicated", "implicated"]))
        self.assertIn("track-jump", codes(res, "warn"))

    def test_must_end_at_scale(self):
        res = run(cosmic(["unaware", "anomaly", "anomaly", "pattern", "pattern"]))
        self.assertIn("track-end", codes(res, "error"))

    def test_bad_value_and_missing_column(self):
        self.assertIn("track-value", codes(run(cosmic(["anomaly", "dread", "pattern", "pattern", "scale"])), "error"))
        doc = ledger(CLEAN, registers="cosmic", ending="irreversible-knowledge")
        self.assertIn("track-column", codes(run(doc), "error"))

    def test_witness_only_protagonist_warns(self):
        res = run(cosmic(["anomaly", "anomaly", "pattern", "pattern", "scale"],
                         responses={1: "denies", 3: "complies"}))
        self.assertIn("no-investigates", codes(res, "warn"))
        self.assertTrue(res["ok"], codes(res))

    def test_register_ending_advice(self):
        doc = cosmic(["anomaly", "anomaly", "pattern", "pattern", "scale"]).replace(
            "Ending: irreversible-knowledge", "Ending: recognition")
        res = run(doc, mode="epic-fantasy")
        self.assertIn("ending-register", codes(res, "warn"))


class OtherRegisters(unittest.TestCase):
    PSY_COLS = ["#", "Link", "Because", "Beat", "Response", "Self", "Changes"]
    PSY = [
        ("open", "-", "Colours brighten.", "none", "The world shimmers", "intact"),
        ("T", '1 "shimmers"', "Faces gain eyes.", "none", "Barriers feel gone", "permeable"),
        ("T", '2 "barriers"', "The world replicates.", "none", "Scale becomes unbearable", "fractured"),
        ("B", '3 "unbearable"', "Watched, judged.", "denies", "A fear loop", "fractured"),
        ("T", '4 "fear loop"', "He lets go.", "surrenders", "The loop breaks", "dissolved"),
        ("B", '5 "loop breaks"', "Waking; most is gone.", "none", "Only fragments remain", "reconstituted"),
    ]

    def _psy(self, rows):
        return run(ledger(rows, mode="confessional-poetry", registers="psychedelic",
                          cols=self.PSY_COLS, ending="return-with-residue"))

    def test_psychedelic_good(self):
        res = self._psy(self.PSY)
        self.assertTrue(res["ok"], codes(res))
        self.assertNotIn("turn", codes(res))

    def test_psychedelic_wants_a_surrender_after_the_fracture(self):
        rows = list(self.PSY)
        rows[4] = ("T", '4 "fear loop"', "He fights it.", "resists", "The loop breaks", "dissolved")
        self.assertIn("turn", codes(self._psy(rows), "warn"))

    def test_psychedelic_must_reach_the_fracture(self):
        rows = [r[:5] + ("permeable" if r[5] == "fractured" else r[5],) for r in self.PSY]
        self.assertIn("track-must-include", codes(self._psy(rows), "error"))

    def test_liminal_needs_a_between(self):
        cols = ["#", "Link", "Because", "Beat", "Response", "Place", "Changes"]
        rows = [
            ("open", "-", "Arrive.", "none", "The map shows sites", "outside"),
            ("B", '1 "map shows sites"', "Sites are missing.", "investigates", "Nobody else notices", "crossing"),
            ("T", '2 "nobody else notices"', "It is a different place.", "none", "There is no way back", "inside"),
        ]
        res = run(ledger(rows, registers="liminal", cols=cols, ending="no-return"))
        self.assertIn("track-must-include", codes(res, "error"))
        rows[2] = ("T", '2 "nobody else notices"', "Held.", "none", "There is no way back", "between")
        self.assertTrue(run(ledger(rows, registers="liminal", cols=cols, ending="no-return"))["ok"])


class Rendering(unittest.TestCase):
    def test_rules_block_names_the_columns_and_registers(self):
        text = pl.render_rules(SPEC, "horror-prose", ["cosmic"])
        self.assertIn('"## Causal ledger"', text)
        self.assertIn("| # | Link | Because | Beat | Response | Knows | Changes |", text)
        self.assertIn("anomaly < pattern < scale < implicated", text)
        self.assertIn("rejected", text)                      # horror's ending rule is a hard rule

    def test_rules_block_is_empty_for_modes_without_plot_logic(self):
        self.assertEqual(pl.render_rules(SPEC, "essay-self-help"), "")
        self.assertEqual(pl.render_rules(SPEC, "confessional-poetry"), "")

    def test_a_register_switches_the_ledger_on_for_any_mode(self):
        # Trips Are Like Exes is confessional-poetry AND psychedelic: the register carries the structure.
        text = pl.render_rules(SPEC, "confessional-poetry", ["psychedelic"])
        self.assertIn("Self (psychedelic)", text)
        self.assertNotIn("rejected", text)                   # poetry has no hard ending rule

    def test_template_parses_and_fails_until_filled(self):
        res = run(pl.render_template(SPEC, ["cosmic"]), mode="horror-prose")
        self.assertFalse(res["ok"])                          # blank ending and cells, but no crash

    def test_report_mentions_the_fix(self):
        rows = list(CLEAN)
        rows[2] = ("A", "-", "A gull will not land.", "denies", "Filed as a weather front")
        (lg, res), = pl.check_text(ledger(rows), SPEC)
        report = pl.render_report([(lg, res)], None, [])
        self.assertIn("FAIL", report)
        self.assertIn("row 3", report)


class SpecIntegrity(unittest.TestCase):
    def test_register_examples_exist(self):
        for name, cfg in SPEC["registers"].items():
            for ex in cfg["worked_examples"]:
                self.assertTrue((VAULT / f"{ex}.md").exists(), f"{name}: worked example missing: {ex}")

    def test_register_notes_exist(self):
        for name, cfg in SPEC["registers"].items():
            self.assertTrue((VAULT / f"{cfg['note']}.md").exists(), f"{name}: note missing: {cfg['note']}")

    def test_endings_and_levels_are_consistent(self):
        endings = set(SPEC["plot_logic"]["endings"])
        for m, cfg in SPEC["modes"].items():
            rule = (cfg.get("plot_logic") or {}).get("ending")
            if rule:
                self.assertLessEqual(set(rule["allowed"]), endings, m)
        for name, cfg in SPEC["registers"].items():
            self.assertLessEqual(set(cfg["endings"]), endings, name)
            t = cfg.get("track")
            if t:
                self.assertLessEqual(set(t.get("start", [])), set(t["levels"]), name)
                self.assertLessEqual(set(t.get("must_include", [])), set(t["levels"]), name)
                if t.get("end_at_least"):
                    self.assertIn(t["end_at_least"], t["levels"], name)
            if cfg.get("turn"):
                self.assertIn(cfg["turn"]["after_level"], t["levels"], name)
                self.assertLessEqual(set(cfg["turn"]["response_in"]), set(SPEC["plot_logic"]["responses"]), name)


class CommandLine(unittest.TestCase):
    def _run(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(PIPELINE / "plot_logic.py"), *args],
                              input=stdin, capture_output=True, text=True, encoding="utf-8")

    def test_exit_codes(self):
        ok = self._run("check", "-", "--mode", "horror-prose", stdin=ledger(CLEAN))
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        bad = self._run("check", "-", "--mode", "horror-prose", stdin=ledger(CLEAN, ending="cost-paid"))
        self.assertEqual(bad.returncode, 1)
        usage = self._run("check", "-", "--mode", "nope", stdin=ledger(CLEAN))
        self.assertEqual(usage.returncode, 2)
        self.assertEqual(self._run("check", str(HERE / "does-not-exist.md")).returncode, 2)

    def test_json_output(self):
        out = self._run("check", "-", "--json", stdin=ledger(CLEAN))
        data = json.loads(out.stdout)
        self.assertTrue(data[0]["ok"])


if __name__ == "__main__":
    unittest.main()
