"""Tests of the records check, its readiness check against a base and the CI base selection. The checks run in this
process on records held in memory; a few cases run the command line and the CI script in one git repository."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check  # noqa: E402

CHECK = HERE / "check.py"
CI_BASE = HERE / "review-base.sh"

CONSTITUTION = """# Constitution

## Article 1 (aim). The aim

The project does one thing.

## Article 2 (rule). A rule

Jobs keep the order they came in.
"""
TURNAROUND = """
## Article 3 (turnaround). Turnaround

Jobs finish as soon as they can.

Replaces: C:rule
"""
FACTS = "Fact speed: The machine ran one job at a time when measured on 2026-01-05.\n"
DATA_FACT = """
Fact runs (assumed): Each job takes about as long as the others, as timed on 2026-01-05.

```
job  seconds
a    10
b    11
```

Follows: F:speed
"""
SERIAL = """Decision serial: How many jobs run at once?

Chosen: one-at-a-time, because the project does one thing (C:aim) and the machine runs one job at a time (F:speed), so several would only wait inside it.

Options:
- one-at-a-time: run each job alone
  + over several: no job waits on another inside the machine
- several: run jobs side by side
  + over one-at-a-time: they could finish sooner together
"""
QUEUE_CHOSEN = ("Chosen: first-come, because jobs keep the order they came in (C:rule), which shortest-first breaks, "
                "and {F:bursts: jobs arrive in bursts}.")
QUEUE_OPTIONS = """Options:
- first-come: run jobs in the order they came
  + over shortest-first: keeps the order they came in (C:rule)
- shortest-first: run the shortest waiting job next
  + over first-come: finishes more jobs sooner
"""
QUEUE = f"""Decision queue: In what order do waiting jobs run?

Given: D:serial/one-at-a-time

{QUEUE_CHOSEN}

{QUEUE_OPTIONS}"""
QUEUE_REVISED = """Chosen: shortest-first, because jobs finish as soon as they can (C:turnaround), which first-come holds back behind long jobs.

Options:
- first-come: run jobs in the order they came
  + over shortest-first: keeps the order they came in
- shortest-first: run the shortest waiting job next
  + over first-come: finishes more jobs sooner (C:turnaround)

Replaced:
- first-come -> shortest-first: first-come, because jobs keep the order they came in (C:rule), which shortest-first breaks, and {F:bursts: jobs arrive in bursts}; replaced because C:turnaround replaces C:rule.

Broke:
- shortest-within-burst: breaks on D:serial
"""
TIES = """Decision ties: How are jobs that came in at once ordered?

Given: D:queue/first-come

Chosen: by-name, because jobs keep the order they came in (D:queue) and a job's place should not change from run to run, as at random it would.

Options:
- by-name: order them by name
  + over at-random: the same place each run
- at-random: order them at random
  + over by-name: needs no names
"""
TIES_LOST = "\nLost:\n- with D:queue/first-come\n"
REPORT = """
Decision report: In what order does the report list jobs?

Chosen: as-run, because jobs that came at once are ordered by name (D:ties), and by size would hide it.

Options:
- as-run: in the order they ran
  + over by-size: shows the order they ran in
- by-size: grouped by size
  + over as-run: groups alike jobs
"""
JOBS = "derivations/jobs.md"
DECISIONS = SERIAL + "\n" + QUEUE + "\n" + TIES


class Case(unittest.TestCase):
    """Records in memory: constitution.md, facts/machine.md and derivations/jobs.md, all passing."""

    def setUp(self):
        self.texts = {"constitution.md": CONSTITUTION, "facts/machine.md": FACTS, JOBS: DECISIONS}

    def files(self):
        return {path: text if isinstance(text, bytes) else text.encode("utf-8") for path, text in self.texts.items()}

    def replace(self, old, new, path=JOBS):
        self.assertIn(old, self.texts[path])
        self.texts[path] = self.texts[path].replace(old, new, 1)

    def revise(self):
        """Article 3 replaces the rule, D:queue is revised on it, and D:ties is lost with the choice replaced."""
        self.texts["constitution.md"] += TURNAROUND
        self.replace(QUEUE_CHOSEN + "\n\n" + QUEUE_OPTIONS, QUEUE_REVISED)
        self.texts[JOBS] += TIES_LOST

    def run_check(self, base=None, ready=False, ascii_only=False, dependents=()):
        return check.check_files(self.files(), base, ready, ascii_only, dependents)

    def assert_passes(self, **kwargs):
        errors, listed, report = self.run_check(**kwargs)
        self.assertEqual(errors, [])
        return listed, report

    def assert_fails(self, needle, **kwargs):
        errors, _listed, _report = self.run_check(**kwargs)
        self.assertTrue(any(needle in error for error in errors), f"no error with {needle!r} in {errors}")


class FilesTests(Case):
    def test_the_records_pass(self):
        _listed, report = self.assert_passes()
        self.assertIn("decisions: 3", report[0])

    def test_text(self):
        self.texts[JOBS] = DECISIONS.replace("\n", "\r\n").encode("utf-8")
        self.assert_fails("a carriage return")
        self.setUp()
        self.texts["facts/machine.md"] = b"Fact speed: \xff\n"
        self.assert_fails("not UTF-8 text")
        self.setUp()
        self.replace("one thing.", "one thing, déjà.", "constitution.md")
        self.assert_passes()
        self.assert_fails("non-ASCII text", ascii_only=True)

    def test_layout(self):
        del self.texts["constitution.md"]
        self.assert_fails("constitution.md: missing")
        self.setUp()
        self.texts["log.md"] = "## 2026-01-05 Start\n"
        self.assert_fails("log.md: not part of the records")
        self.setUp()
        self.texts["derivations/jobs/report.md"] = REPORT.lstrip("\n")
        self.assert_passes()
        del self.texts[JOBS]
        self.assert_fails("its directory has no node file derivations/jobs.md")

    def test_constitution(self):
        cases = {
            "an article is headed": ("## Article 2 (rule). A rule", "## Article 2 (Rule). A rule"),
            "article 3 where article 2 comes next": ("## Article 2 (rule)", "## Article 3 (rule)"),
            "C:rule has no text": ("Jobs keep the order they came in.\n", ""),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new, "constitution.md")
                self.assert_fails(needle)
        self.setUp()
        self.texts["constitution.md"] += "\n## Article 3 (Wrong). A third\n\nText.\n\n## Article 4 (fourth). A fourth\n\nText.\n"
        errors, _listed, _report = self.run_check()
        self.assertFalse(any("article 4 where" in error for error in errors), errors)
        self.setUp()
        self.texts["constitution.md"] = "# Constitution\n"
        self.assert_fails("the constitution has no article")
        self.setUp()
        self.texts["constitution.md"] += TURNAROUND.replace("Replaces: C:rule", "Replaces: rule")
        self.assert_fails("'Replaces' reads 'Replaces: C:<id>'")
        self.setUp()
        self.texts["constitution.md"] += TURNAROUND + "\nReplaces: C:aim\n"
        self.assert_fails("a second 'Replaces' field")


class DecisionTests(Case):
    def test_head_and_fields(self):
        cases = {
            "a record opens 'Decision <id>: <question>'": ("Decision serial:", "Decision Serial:"),
            "no field 'Rejected'": ("Options:\n- one-at-a-time", "Rejected:\n- one-at-a-time"),
            "a field must be separated from the line before it": ("once?\n\nChosen:", "once?\nChosen:"),
            "'Options:' stands alone": ("Options:\n- one-at-a-time", "Options: one\n- one-at-a-time"),
            "a line outside the record format": ("  + over several: no job", "  but over several: no job"),
            "D:serial has no 'Options'": (SERIAL[SERIAL.index("Options:"):], ""),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new)
                self.assert_fails(needle)
        self.setUp()
        self.texts[JOBS] += "\nOptions:\n- extra: one more\n"
        self.assert_fails("a second 'Options' field")

    def test_chosen(self):
        self.replace("Chosen: one-at-a-time, because", "Chosen: one-at-a-time because")
        self.assert_fails("the Chosen of D:serial reads")
        self.setUp()
        self.replace("Chosen: one-at-a-time, because", "Chosen: alone, because")
        self.assert_fails("takes 'alone', which is no option in its Options")
        self.setUp()
        self.replace("Chosen: one-at-a-time, because", "Chosen: one-at-a-time, so that")
        self.assert_passes()

    def test_options_name_one_another(self):
        cases = {
            "an Options item reads": ("- several: run", "- Several: run"),
            "a '+' line reads": ("  + over several: no job", "  + better than several: no job"),
            "names the option itself": ("  + over several: no job", "  + over one-at-a-time: no job"),
            "names 'many', which is no option": ("  + over several: no job", "  + over several, many: no job"),
            "is listed twice": ("- several: run jobs side by side\n", "- several: run jobs side by side\n- several: x\n"
                                                                     "  + over one-at-a-time: y\n"),
            "a '+' line follows straight after its option": ("side by side\n  + over", "side by side\n\n  + over"),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new)
                self.assert_fails(needle)

    def test_every_option_named_by_every_other(self):
        self.replace("  + over one-at-a-time: they could finish sooner together\n",
                     "  + over one-at-a-time: they could finish sooner together\n- batches: run jobs in batches\n"
                     "  + over one-at-a-time, several: fewer starts\n")
        self.assert_fails("the '+' lines of the option 'one-at-a-time' of D:serial do not name 'batches'")
        self.replace("  + over several: no job waits", "  + over several, batches: no job waits")
        self.replace("  + over one-at-a-time: they could", "  + over one-at-a-time, batches: they could")
        self.assert_passes()

    def test_one_option_only_in_a_revision(self):
        single = SERIAL[:SERIAL.index("- several:")]
        self.replace(SERIAL, single.replace("  + over several: no job waits on another inside the machine\n", ""))
        self.assert_fails("D:serial has one option and no 'Replaced'")
        self.replace("one-at-a-time: run each job alone\n", "one-at-a-time: run each job alone\n  + over x: y\n")
        self.assert_fails("a '+' line under the one option of D:serial")

    def test_replaced_moves_lead_to_the_chosen(self):
        self.revise()
        self.assert_passes()
        kept = "- first-come -> shortest-first: first-come, because"
        cases = {
            "a Replaced item reads": (kept, "- first-come to shortest-first: first-come, because"),
            "takes 'shortest-first', not 'first-come'": (kept, "- first-come -> shortest-first: shortest-first, because"),
            "moves to 'first-come', but its Chosen takes 'shortest-first'": (kept, "- first-come -> first-come: "
                                                                                  "first-come, because"),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.revise()
                self.replace(old, new)
                self.assert_fails(needle)
        self.setUp()
        self.revise()
        self.replace("C:turnaround replaces C:rule.\n",
                     "C:turnaround replaces C:rule.\n- first-come -> shortest-first: first-come, because of x; "
                     "replaced because of y.\n")
        self.assert_fails("moves from 'first-come', but the one before it moved to 'shortest-first'")

    def test_a_move_to_itself(self):
        self.revise()
        chosen = QUEUE_REVISED.splitlines()[0]
        self.replace(chosen, chosen.replace("long jobs.", "long jobs, waiting jobs taken by length."))
        self.replace("replaces C:rule.\n", "replaces C:rule.\n- shortest-first -> shortest-first: "
                     + chosen[len("Chosen: "):] + "; replaced because the length of a job is known before it runs "
                     "(C:turnaround).\n")
        self.assert_passes()

    def test_broke_and_lost(self):
        self.revise()
        self.replace("breaks on D:serial", "breaks on the serial decision")
        self.assert_fails("a Broke item reads")
        self.setUp()
        self.revise()
        self.replace("- with D:queue/first-come", "- with D:queue")
        self.assert_fails("a Lost item reads")
        self.setUp()
        self.revise()
        self.replace("- with D:queue/first-come", "- with D:serial/several")
        self.assert_fails("D:ties is lost with D:serial/several, which its Given does not name")

    def test_lost_through_a_decision_given(self):
        self.revise()
        self.texts[JOBS] += REPORT.replace("Chosen: as-run", "Given: D:ties/by-name\n\nChosen: as-run") + TIES_LOST
        self.assert_passes()

    def test_dates(self):
        self.replace("the project does one thing (C:aim)", "the project does one thing (C:aim) since 2026-01-05")
        self.assert_fails("a date; a decision holds no date but in a fact it declares")
        self.setUp()
        self.replace("{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrived in bursts on 2026-01-05}")
        self.assert_passes()

    def test_an_article_or_a_decision_cited_where_it_weighs(self):
        self.replace("(C:aim)", "")
        self.assert_fails("D:serial cites no article and no decision in its Chosen or its Options")
        self.setUp()
        chosen = "Chosen: by-name, because jobs keep the order they came in (D:queue)"
        self.replace(chosen, "Chosen: by-name, because jobs keep the order they came in")
        self.assert_fails("D:ties cites no article and no decision")


    def test_a_head_that_does_not_read_gives_its_lines_to_no_record(self):
        self.replace("Decision queue:", "Decision Queue:")
        errors, _listed, _report = self.run_check()
        self.assertIn("a record opens 'Decision <id>: <question>'", errors[0])
        for wrong in ("a second 'Chosen'", "form a cycle", "do not name"):
            self.assertFalse(any(wrong in error for error in errors), errors)

    def test_an_option_that_does_not_read_still_counts(self):
        self.replace("- several: run", "- Several: run")
        errors, _listed, _report = self.run_check()
        self.assertTrue(any("an Options item reads" in error for error in errors), errors)
        self.assertFalse(any("one option" in error for error in errors), errors)

    def test_a_last_lost_item_that_does_not_read(self):
        self.revise()
        self.replace("- with D:queue/first-come", "- with D:queue/first-come.")
        errors, _listed, _report = self.run_check()
        self.assertTrue(any("a Lost item reads" in error for error in errors), errors)
        self.assertFalse(any("is in force" in error for error in errors), errors)

    def test_a_double_id_is_still_checked(self):
        self.texts[JOBS] += "\n" + TIES.replace("(D:queue)", "(D:queue, C:nothing)")
        self.assert_fails("D:ties is also at")
        self.assert_fails("C:nothing resolves to no article")


class FactTests(Case):
    def test_inline_facts(self):
        self.replace("{F:bursts: jobs arrive in bursts}", "{F:bursts}")
        self.assert_fails("an inline fact reads")
        self.setUp()
        self.replace("{F:bursts: jobs arrive in bursts}", "{F:bursts (assumed): jobs arrive in bursts; follows F:speed}")
        self.assert_passes()
        self.texts["facts/machine.md"] += "\nFact bursts: jobs arrive in bursts\n"
        self.assert_fails("F:bursts is also at")

    def test_facts_in_their_files(self):
        self.texts["facts/machine.md"] += DATA_FACT
        self.replace("(F:speed)", "(F:speed, F:runs)")
        _listed, report = self.assert_passes()
        self.assertIn("assumed F:runs", "\n".join(report))
        self.setUp()
        self.texts["facts/machine.md"] += DATA_FACT.replace("\n```\njob", "\n```text\njob")
        self.replace("(F:speed)", "(F:speed, F:runs)")
        errors, _listed, _report = self.run_check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("a data block is fenced by a line '```' alone", errors[0])
        cases = {
            "a data block that is never closed": ("b    11\n```\n", "b    11\n"),
            "'Follows' names the one fact": ("Follows: F:speed", "Follows: speed"),
            "no field 'Assumed'": ("Follows: F:speed", "Assumed: yes"),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.texts["facts/machine.md"] += DATA_FACT
                self.replace("(F:speed)", "(F:speed, F:runs)")
                self.replace(old, new, "facts/machine.md")
                self.assert_fails(needle)

    def test_a_fact_no_decision_cites(self):
        self.texts["facts/machine.md"] += DATA_FACT
        self.assert_fails("F:runs is cited by no decision")

    def test_follows(self):
        self.texts["facts/machine.md"] += DATA_FACT.replace("Follows: F:speed", "Follows: F:fast")
        self.replace("(F:speed)", "(F:speed, F:runs)")
        self.assert_fails("F:fast resolves to no fact")
        self.setUp()
        self.texts["facts/machine.md"] = FACTS.rstrip("\n") + "\n\nFollows: F:runs\n" + DATA_FACT
        self.replace("(F:speed)", "(F:speed, F:runs)")
        self.assert_fails("the facts' follows form a cycle")


class ReferenceTests(Case):
    def test_references_resolve(self):
        cases = {
            "C:goal resolves to no article": ("(C:aim)", "(C:goal)"),
            "F:slow resolves to no fact": ("(F:speed)", "(F:slow)"),
            "D:queue/fifo resolves to no option of D:queue": ("Given: D:queue/first-come", "Given: D:queue/fifo"),
            "only a decision names options": ("(F:speed)", "(F:speed/fast)"),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new)
                self.assert_fails(needle)

    def test_premises_in_a_cycle(self):
        self.replace("(C:aim)", "(C:aim, D:ties)")
        self.assert_fails("the decisions' premises form a cycle")

    def test_dependents_rest_on_the_premises_not_on_history(self):
        listed, _report = self.assert_passes(dependents=("F:speed",))
        self.assertEqual(listed[0], "dependents of F:speed: 3")
        self.revise()
        listed, _report = self.assert_passes(dependents=("C:rule", "D:serial"))
        self.assertIn("dependents of C:rule: 0", listed)
        self.assertIn("dependents of D:serial: 2", listed)
        self.assert_fails("C:nothing is no record", dependents=("C:nothing",))
        listed, _report = self.assert_passes(dependents=("D:serial/one-at-a-time",))
        self.assertIn("dependents of D:serial: 2", listed)

    def test_a_decision_in_force_on_what_binds_nothing(self):
        self.texts["constitution.md"] += TURNAROUND
        self.assert_fails("D:queue is in force and rests on C:rule, which C:turnaround replaces")
        self.setUp()
        self.revise()
        self.replace(TIES_LOST, "")
        self.assert_fails("D:ties is in force and its Given names D:queue/first-come, but D:queue takes "
                          "'shortest-first'")
        self.setUp()
        self.revise()
        self.texts[JOBS] += REPORT
        self.assert_fails("D:report is in force and rests on D:ties, which is lost with D:queue/first-come")

    def test_a_decision_back_with_an_option(self):
        self.revise()
        self.texts[JOBS] += "- back with D:queue/first-come\n"
        self.assert_fails("D:ties is in force and its Given names D:queue/first-come")


class WordsTests(Case):
    def test_code_spans_and_paths(self):
        cases = {
            "a code span, `take_step()`": "the step `take_step()` runs",
            "'crates/engine/src/cards.rs' names a path": "the step in crates/engine/src/cards.rs runs",
            "'flow.json' names a path or a file": "the step in flow.json runs",
        }
        for needle, words in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace("the project does one thing", words)
                self.assert_fails(needle)
        self.setUp()
        self.texts["facts/machine.md"] = FACTS.replace("measured", "measured with `time`")
        self.assert_fails("a code span, `time`")
        self.setUp()
        self.replace("the project does one thing", "the step in `flow.json` runs")
        errors, _listed, _report = self.run_check()
        self.assertEqual(len(errors), 1, errors)

    def test_words_that_are_no_path(self):
        self.replace("the project does one thing", "the project does one thing, as https://example.org/a/b.html "
                     "and github.com/x/y.md say, e.g. and Node and v5.5")
        self.assert_passes()


class ReadyTests(Case):
    """The records against a base: they only grow."""

    def ready(self, base):
        return {"base": base, "ready": True}

    def test_a_revision_passes_and_counts_against_the_base(self):
        base = self.files()
        self.revise()
        _listed, report = self.assert_passes(**self.ready(base))
        self.assertIn("articles: 3 (base 2, +1)", report[0])

    def test_a_base_in_an_earlier_form_is_not_compared(self):
        base = self.files()
        base["derivations/order.md"] = b"## D:serial. How many jobs run at once?\n\nRests on: C:rule\n"
        self.replace(TIES, "")
        listed, _report = self.assert_passes(**self.ready(base))
        self.assertIn("the base does not pass the check as it stands", listed[0])

    def test_a_record_removed_or_moved(self):
        base = self.files()
        self.replace(TIES, "")
        self.assert_fails("D:ties stood here at the base and is gone", **self.ready(base))
        self.setUp()
        self.texts["derivations/order.md"] = TIES
        self.replace(TIES, "")
        self.assert_passes(**self.ready(base))

    def test_articles_facts_questions_and_given_never_change(self):
        base = self.files()
        cases = {
            "C:rule changed since the base": ("Jobs keep the order", "Jobs always keep the order", "constitution.md"),
            "F:speed changed since the base": ("one job at a time when", "one job when", "facts/machine.md"),
            "F:bursts changed since the base": ("jobs arrive in bursts", "jobs arrive in waves", JOBS),
            "the question of D:serial changed": ("How many jobs run at once?", "How many jobs run together?", JOBS),
            "the Given of D:queue changed": ("Given: D:serial/one-at-a-time", "Given: D:serial", JOBS),
        }
        for needle, (old, new, path) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new, path)
                self.assert_fails(needle, **self.ready(base))

    def test_history_only_grows_at_its_end(self):
        self.revise()
        base = self.files()
        self.replace("- shortest-within-burst: breaks on D:serial", "- shortest-within-burst: breaks on C:aim")
        self.assert_fails("the Broke items of D:queue at the base changed", **self.ready(base))
        self.setUp()
        self.revise()
        self.replace("- shortest-within-burst: breaks on D:serial",
                     "- shortest-within-burst: breaks on D:serial\n- longest-first: breaks on C:turnaround")
        self.assert_passes(**self.ready(base))

    def test_a_changed_chosen_is_kept_whole_as_replaced(self):
        base = self.files()
        self.revise()
        self.replace("{F:bursts: jobs arrive in bursts}; replaced", "{F:bursts: jobs arrive in bursts}, mostly; replaced")
        self.assert_fails("the first new Replaced item of D:queue keeps a Chosen other than the one it held at the base",
                          **self.ready(base))
        self.setUp()
        self.replace("so several would only wait inside it.", "so several would only queue inside it.")
        self.assert_fails("the Chosen of D:serial changed since the base", **self.ready(base))

    def test_an_article_replaced_is_cited_anew_without_a_revision(self):
        self.texts[JOBS] = SERIAL + "\n" + QUEUE.replace("(C:rule)", "(C:rule, D:serial)")
        base = self.files()
        self.texts["constitution.md"] += TURNAROUND
        self.texts[JOBS] = SERIAL + "\n" + QUEUE.replace("(C:rule)", "(C:turnaround, D:serial)")
        self.assert_passes(**self.ready(base))

    def test_options_change_only_in_a_revision(self):
        base = self.files()
        cases = {
            "what the option 'several' of D:serial is changed": ("- several: run jobs side by side",
                                                                 "- several: run jobs next to each other"),
            "the Options of D:serial changed since the base with no new Replaced item":
                ("  + over one-at-a-time: they could finish sooner together",
                 "  + over one-at-a-time: they finish sooner together"),
        }
        for needle, (old, new) in cases.items():
            with self.subTest(needle=needle):
                self.setUp()
                self.replace(old, new)
                self.assert_fails(needle, **self.ready(base))

    def test_a_decision_added_weighs_two_options(self):
        base = self.files()
        single = REPORT[:REPORT.index("- by-size:")].replace("  + over by-size: shows the order they ran in\n", "")
        self.texts[JOBS] += single.replace(", and by size would hide it", "") + "\nReplaced:\n- by-size -> as-run: " \
            "by-size, because it groups (D:ties); replaced because x\n"
        self.assert_fails("D:report is added with one option", **self.ready(base))


class GrowthTests(Case):
    ready = ReadyTests.ready

    def test_nothing_removed(self):
        base = self.files()
        for path, old in (("constitution.md", "## Article 2 (rule). A rule\n\nJobs keep the order they came in.\n"),
                          ("facts/machine.md", FACTS)):
            with self.subTest(path=path):
                self.setUp()
                self.replace(old, "", path)
                self.assert_fails("stood here at the base and is gone", **self.ready(base))

    def test_options_reordered_or_cited_anew(self):
        base = self.files()
        self.replace("- one-at-a-time: run each job alone\n  + over several: no job waits on another inside the machine\n"
                     "- several: run jobs side by side\n  + over one-at-a-time: they could finish sooner together\n",
                     "- several: run jobs side by side\n  + over one-at-a-time: they could finish sooner together\n"
                     "- one-at-a-time: run each job alone\n  + over several: no job waits on another inside the machine\n")
        self.assert_passes(**self.ready(base))
        self.setUp()
        self.replace("- first-come: run jobs in the order they came", "- first-come: run jobs in the order they came (C:rule)")
        base = self.files()
        speedy = TURNAROUND.replace("Article 3 (turnaround). Turnaround", "Article 4 (speedy). Speed").replace(
            "Replaces: C:rule", "Replaces: C:turnaround")
        self.texts["constitution.md"] += TURNAROUND + speedy
        self.texts[JOBS] = self.texts[JOBS].replace("C:rule", "C:speedy")
        self.assert_passes(**self.ready(base))

    def test_options_and_history_change_only_in_a_revision(self):
        base = self.files()
        self.replace("  + over one-at-a-time: they could finish sooner together\n",
                     "  + over one-at-a-time: they could finish sooner together\n- batches: run jobs in batches\n"
                     "  + over one-at-a-time, several: fewer starts\n")
        self.replace("  + over several: no job waits", "  + over several, batches: no job waits")
        self.replace("  + over one-at-a-time: they could", "  + over one-at-a-time, batches: they could")
        self.assert_fails("the Options of D:serial changed since the base with no new Replaced item", **self.ready(base))
        serial_chosen = SERIAL.splitlines()[2][len("Chosen: "):]
        self.texts[JOBS] = self.texts[JOBS].replace(
            "  + over one-at-a-time, several: fewer starts\n",
            "  + over one-at-a-time, several: fewer starts\n\nReplaced:\n- one-at-a-time -> one-at-a-time: anything "
            "at all; replaced because nothing\n", 1)
        self.assert_fails("a Replaced item of D:serial keeps reads", **self.ready(base))
        self.texts[JOBS] = self.texts[JOBS].replace("- one-at-a-time -> one-at-a-time: anything at all;",
                                                    "- one-at-a-time -> one-at-a-time: " + serial_chosen + ";")
        self.assert_passes(**self.ready(base))
        self.setUp()
        self.revise()
        base = self.files()
        for old, new, needle in (("- with D:queue/first-come", "- with D:queue/first-come\n- back with D:queue/first-come",
                                  None),
                                 ("replaced because C:turnaround replaces C:rule.", "replaced because the rule went.",
                                  "the Replaced items of D:queue at the base changed")):
            with self.subTest(new=new):
                self.setUp()
                self.revise()
                self.replace(old, new)
                if needle is None:
                    errors, _listed, _report = self.run_check(**self.ready(base))
                    self.assertFalse(any("Lost items" in error for error in errors), errors)
                else:
                    self.assert_fails(needle, **self.ready(base))
        self.setUp()
        base = self.files()
        self.replace("Decision serial: How many jobs run at once?\n", "Decision serial: How many jobs run at once?\n\n"
                     "Given: C:aim\n")
        self.assert_fails("the Given of D:serial changed since the base", **self.ready(base))


class CommandLineTests(unittest.TestCase):
    """The command line and the CI base selection, in one git repository: the records committed as a base, then
    revised in the worktree."""

    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="reasoning-check-")
        cls.addClassCleanup(temporary.cleanup)
        cls.root = Path(temporary.name)
        case = Case()
        case.setUp()
        for path, data in case.files().items():
            target = cls.root / "reasoning" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        cls.git("init", "--quiet", "--initial-branch", "main")
        cls.git("add", ".")
        cls.git("commit", "--quiet", "-m", "Start")
        cls.base = cls.git("rev-parse", "HEAD")
        cls.git("update-ref", "refs/remotes/origin/main", cls.base)
        case.revise()
        for path, data in case.files().items():
            (cls.root / "reasoning" / path).write_bytes(data)

    @classmethod
    def git(cls, *args):
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "-c",
                               "user.name=Reasoning check", "-c", "user.email=check@example.invalid", *args],
                              cwd=cls.root, text=True, capture_output=True, check=True).stdout.strip()

    def check(self, *args):
        return subprocess.run([sys.executable, "-B", str(CHECK), "--root", "reasoning", *args],
                              cwd=self.root, text=True, capture_output=True)

    def test_the_command_line(self):
        result = self.check("--base", self.base, "--ready", "--dependents", "D:serial")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dependents of D:serial: 2", result.stdout)
        self.assertIn("reasoning check: ok", result.stdout)
        for args, needle in ((("--ready",), "--ready: needs --base"),
                             (("--base", "no-such-revision", "--ready"), "resolves to no commit")):
            with self.subTest(args=args):
                result = self.check(*args)
                self.assertEqual(result.returncode, 1)
                self.assertIn(needle, result.stderr)

    def ci_base(self, event, ref, before=""):
        return subprocess.run(["sh", str(CI_BASE), event, ref, before], cwd=self.root, text=True, capture_output=True)

    def test_the_ci_base(self):
        result = self.ci_base("push", "refs/heads/main", self.base)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing an empty comparison", result.stderr)
        result = self.ci_base("pull_request", "refs/pull/1/merge")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.base)
        result = self.ci_base("schedule", "refs/heads/main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported event", result.stderr)


if __name__ == "__main__":
    unittest.main()
