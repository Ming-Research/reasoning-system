"""Tests of the records check, its readiness check against a base and the CI
base selection. Each case builds its own records in a temporary directory."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
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

Chosen: One at a time, because the project does one thing (C:aim) and the machine runs one job at a time (F:speed).

Rejected:
- Several at once: they finish sooner together; rejected because the machine runs one job at a time (F:speed).
"""
QUEUE_CHOICE = """Chosen: First come, first served, because jobs keep the order they came in (C:rule) and run one at a time (D:serial), and {F:bursts: jobs arrive in bursts}.

Rejected:
- Shortest first: it finishes more jobs sooner; rejected because it breaks the order they came in (C:rule).
"""
QUEUE_REVISED = """Chosen: Shortest first, because jobs finish as soon as they can (C:turnaround) and run one at a time (D:serial).

Rejected:
- First come, first served: it keeps the order jobs came in; rejected because a long job holds back the short ones behind it (C:turnaround).

Replaced:
- First come, first served: chosen because jobs keep the order they came in (C:rule) and run one at a time (D:serial), and {F:bursts: jobs arrive in bursts}; replaced because C:turnaround replaces C:rule.

Broke:
- Shortest first within each burst: breaks on D:serial
"""
TIES_REJECTED = "- At random: it needs no names; rejected because a job's place would change from run to run (D:queue).\n"
TIES_LOST = "\nLost:\n- with D:queue, First come, first served\n"
TIES = """Decision ties: How are jobs that came in at once ordered?

Chosen: By name, because jobs keep the order they came in (D:queue), and those that came at once have none of their own.

Rejected:
""" + TIES_REJECTED
DECISIONS = SERIAL + "\nDecision queue: In what order do waiting jobs run?\n\n" + QUEUE_CHOICE + "\n" + TIES
REPORT = """
Decision report: In what order does the report list jobs?

Chosen: In the order they ran, because jobs that came at once are ordered by name (D:ties).

Rejected:
- By size: it groups alike jobs; rejected because it hides the order they ran in (D:ties).
"""
SERIAL_CHOSEN = ("Chosen: One at a time, because the project does one thing (C:aim) and the machine runs one job at a "
                 "time (F:speed).")
SERIAL_REASON = "rejected because the machine runs one job at a time (F:speed)."
SERIAL_REVISED = ("Chosen: One at a time, because the project does one thing (C:aim) and "
                  "{F:cores: the machine has one core}.")
SERIAL_REPLACED = ("\nReplaced:\n- One at a time: chosen because the project does one thing (C:aim) and the machine "
                   "runs one job at a time (F:speed); replaced because the machine was found to have one core (F:cores).\n")
JOBS = "reasoning/derivations/jobs.md"
CONSTITUTION_PATH = "reasoning/constitution.md"
FACTS_PATH = "reasoning/facts/machine.md"


class Fixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="reasoning-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write(CONSTITUTION_PATH, CONSTITUTION)
        self.write(FACTS_PATH, FACTS)
        self.write(JOBS, DECISIONS)

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))

    def read(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def replace(self, path, old, new):
        text = self.read(path)
        self.assertIn(old, text)
        self.write(path, text.replace(old, new, 1))

    def revise(self):
        """Article 3 replaces the rule, D:queue is revised on it, and D:ties is lost with the choice replaced."""
        self.write(CONSTITUTION_PATH, CONSTITUTION + TURNAROUND)
        self.replace(JOBS, QUEUE_CHOICE, QUEUE_REVISED)
        self.replace(JOBS, TIES_REJECTED, TIES_REJECTED + TIES_LOST)

    def check(self, *args):
        return subprocess.run([sys.executable, "-B", str(CHECK), "--root", "reasoning", *args],
                              cwd=self.root, text=True, capture_output=True)

    def assert_passes(self, *args):
        result = self.check(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def assert_fails(self, diagnostic, *args):
        result = self.check(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stderr)

    def assert_each_fails(self, path, cases, *args):
        """Each (old, new, diagnostic): the change fails with the diagnostic, and is undone after."""
        text = self.read(path)
        for old, new, diagnostic in cases:
            with self.subTest(new=new):
                self.replace(path, old, new)
                self.assert_fails(diagnostic, *args)
                self.write(path, text)


class FilesTests(Fixture):
    """The text of the files, and which files the records are."""

    def test_records_in_the_format_pass_and_are_counted(self):
        result = self.assert_passes()
        self.assertIn("articles: 2  facts: 2  decisions: 3  rejected: 3  assumed: 0", result.stdout)
        self.assertIn("reasoning check: ok", result.stdout)

    def test_non_ascii_text_only_when_the_project_is_english(self):
        self.replace(JOBS, "In what order do waiting jobs run?", "In what order \u2014 if any \u2014 do jobs run?")
        self.assert_passes()
        self.assert_fails("non-ASCII text", "--ascii")

    def test_a_carriage_return(self):
        self.write(FACTS_PATH, FACTS.replace("\n", "\r\n"))
        self.assert_fails("a carriage return")

    def test_text_that_is_not_utf8(self):
        (self.root / FACTS_PATH).write_bytes(b"Fact speed: The machine \xff runs one job at a time.\n")
        self.assert_fails("facts/machine.md: not UTF-8 text")

    def test_subjects_nest_under_their_node_file(self):
        self.write("reasoning/facts/machine/disk.md", "Fact disk: The disk is slow.\n")
        self.write("reasoning/derivations/jobs/order.md",
                   "Decision order: Do jobs keep their order on disk?\n\n"
                   "Chosen: They do, because they wait in a queue (D:queue) and the disk is slow (F:disk).\n\n"
                   "Rejected:\n- They do not: it writes less; rejected because the queue keeps the order (D:queue).\n")
        self.assert_passes()

    def test_a_directory_without_its_node_file(self):
        self.write("reasoning/derivations/other/order.md", SERIAL.replace("serial", "order"))
        self.assert_fails("its directory has no node file derivations/other.md")

    def test_a_file_that_is_no_record(self):
        for path in ("reasoning/notes.md", "reasoning/derivations/jobs.txt", "reasoning/log.md"):
            with self.subTest(path=path):
                self.write(path, "notes\n")
                self.assert_fails("not part of the records")
                (self.root / path).unlink()

    def test_a_node_file_with_no_record(self):
        self.write("reasoning/derivations/empty.md", "\n")
        self.assert_fails("derivations/empty.md: holds no decision")

    def test_a_missing_constitution(self):
        (self.root / CONSTITUTION_PATH).unlink()
        self.assert_fails("constitution.md: missing")


class ConstitutionTests(Fixture):
    """The articles, and an article that replaces another."""

    def test_an_article_that_replaces_another(self):
        self.revise()
        result = self.assert_passes()
        self.assertIn("articles: 3", result.stdout)

    def test_an_article_heading_out_of_the_format(self):
        self.replace(CONSTITUTION_PATH, "## Article 2 (rule). A rule", "## Article 2 rule")
        self.assert_fails("an article is headed")

    def test_articles_numbered_out_of_order(self):
        for old, new, diagnostic in (("## Article 2 (rule)", "## Article 3 (rule)", "article 3 where article 2 comes next"),
                                     ("## Article 1 (aim)", "## Article 0 (aim)", "article 0 where article 1 comes next")):
            with self.subTest(new=new):
                self.write(CONSTITUTION_PATH, CONSTITUTION.replace(old, new))
                self.assert_fails(diagnostic)

    def test_a_constitution_with_no_article(self):
        self.write(CONSTITUTION_PATH, "# Constitution\n")
        self.assert_fails("the constitution has no article")

    def test_an_article_with_no_text(self):
        for text in (CONSTITUTION + "\n## Article 3 (empty). Empty\n",
                     CONSTITUTION + "\n## Article 3 (empty). Empty\n\nReplaces: C:rule\n"):
            with self.subTest(text=text[-30:]):
                self.write(CONSTITUTION_PATH, text)
                self.assert_fails("C:empty has no text")

    def test_a_replaces_field_out_of_the_format(self):
        self.revise()
        for new in ("Replaces: rule", "Replaces: D:serial", "Replaces: C:rule, C:aim"):
            with self.subTest(new=new):
                self.write(CONSTITUTION_PATH, CONSTITUTION + TURNAROUND.replace("Replaces: C:rule", new))
                self.assert_fails("an article's 'Replaces' reads 'Replaces: C:<id>'")

    def test_a_replaces_field_without_a_blank_line_before_it(self):
        self.revise()
        self.write(CONSTITUTION_PATH, CONSTITUTION + TURNAROUND.replace("can.\n\nReplaces", "can.\nReplaces"))
        self.assert_fails("a field must be separated from the line before it by a blank line")

    def test_a_second_replaces_field(self):
        self.revise()
        self.write(CONSTITUTION_PATH, CONSTITUTION + TURNAROUND + "\nReplaces: C:aim\n")
        self.assert_fails("a second 'Replaces' field in C:turnaround")


class DecisionTests(Fixture):
    """A decision's head, its fields and their items, and the dates it may hold."""

    def test_a_decision_head_out_of_the_format(self):
        self.assert_each_fails(JOBS, (
            ("Decision queue:", "Decision Queue:", "a record opens 'Decision <id>: <question>'"),
            ("Decision queue: In what order do waiting jobs run?", "Decision queue:",
             "a record opens 'Decision <id>: <question>'"),
        ))

    def test_an_id_used_twice_in_its_kind(self):
        self.write("reasoning/derivations/more.md", SERIAL)
        self.assert_fails("D:serial is also at derivations/jobs.md:1; an id is unique in its kind")

    def test_a_decision_without_chosen(self):
        self.replace(JOBS, SERIAL_CHOSEN + "\n\n", "")
        self.assert_fails("D:serial has no 'Chosen'")

    def test_fields_out_of_the_format(self):
        self.assert_each_fails(JOBS, (
            (SERIAL_CHOSEN, "Chosen:", "an empty 'Chosen' field"),
            ("time (F:speed).\n\nRejected:", "time (F:speed).\nRejected:",
             "a field must be separated from the line before it by a blank line"),
            ("Rejected:\n- Several", "Rejected: Several at once\n- Several", "'Rejected:' stands alone"),
            ("Rejected:\n- Several", "Rejected:\n\n- Several", "a list item must follow its field's line or the item before it"),
            (SERIAL_CHOSEN, SERIAL_CHOSEN + "\n\n" + SERIAL_CHOSEN, "a second 'Chosen' field in D:serial"),
            (SERIAL_CHOSEN, SERIAL_CHOSEN + "\n\nRests on: C:aim, F:speed",
             "no field 'Rests on'; a decision has Chosen, Rejected, Replaced, Broke, Lost"),
            (SERIAL_CHOSEN, SERIAL_CHOSEN + "\n\nOpen: why one", "no field 'Open'"),
            ("one thing (C:aim) and", "one thing (C:aim)\nand", "a line outside the record format"),
            ("Decision queue:", "Decision queue: And?\nDecision other:",
             "a record must be separated from the line before it by a blank line"),
        ))

    def test_a_list_with_no_item(self):
        self.revise()
        self.replace(JOBS, "Broke:\n- Shortest first within each burst: breaks on D:serial\n", "Broke:\n")
        self.assert_fails("a 'Broke:' list with no item")

    def test_chosen_gives_because_or_so_that(self):
        self.replace(JOBS, "Chosen: By name, because jobs", "Chosen: By name, so that jobs")
        self.assert_passes()
        self.replace(JOBS, "Chosen: By name, so that jobs", "Chosen: By name, as jobs")
        self.assert_fails("the Chosen of D:ties gives no 'because' or 'so that'")

    def test_a_because_only_in_a_fact_declared_is_none(self):
        self.replace(JOBS, "First come, first served, because jobs keep the order they came in (C:rule) and",
                     "First come, first served, as jobs keep the order they came in (C:rule) and")
        self.replace(JOBS, "{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts because users batch}")
        self.assert_fails("the Chosen of D:queue gives no 'because' or 'so that'")

    def test_a_rejected_item_says_what_the_option_does_better(self):
        self.assert_each_fails(JOBS, (
            ("- Several at once: they finish sooner together; rejected because",
             "- Several at once: rejected because", "a Rejected item reads '- <option>: <what it does better>"),
            ("together; rejected because", "together, rejected as", "a Rejected item reads"),
        ))

    def test_history_items(self):
        self.revise()
        self.assert_passes()
        self.assert_each_fails(JOBS, (
            ("- First come, first served: chosen because jobs keep",
             "- First come, first served: picked because jobs keep", "a Replaced item reads"),
            ("{F:bursts: jobs arrive in bursts}; replaced because", "{F:bursts: jobs arrive in bursts}",
             "a Replaced item reads"),
            ("breaks on D:serial", "breaks on the serial decision", "a Broke item reads '- <revision>: breaks on <reference>'"),
            ("breaks on D:serial", "breaks on D:serial and D:queue", "a Broke item reads"),
            ("- with D:queue, First come", "- lost with D:queue, First come", "a Lost item reads '- with D:<id>, <approach>'"),
            ("- with D:queue, First come", "- with queue, First come", "a Lost item reads"),
        ))

    def test_a_purpose_given_in_a_replaced_item(self):
        self.revise()
        self.replace(JOBS, "- First come, first served: chosen because jobs keep the order",
                     "- First come, first served: chosen so that jobs keep the order")
        self.assert_passes()

    def test_a_lost_item_names_an_approach_the_decision_replaced(self):
        self.revise()
        self.replace(JOBS, "- with D:queue, First come, first served", "- with D:queue, Last come, first served")
        self.assert_fails("D:ties is lost with 'Last come, first served', which the Replaced of D:queue does not hold")
        self.replace(JOBS, "- with D:queue, Last come", "- with D:serial, First come")
        self.assert_fails("which the Replaced of D:serial does not hold")

    def test_a_decision_with_no_rejected_has_a_replaced(self):
        self.replace(JOBS, "\nRejected:\n- Several at once: they finish sooner together; " + SERIAL_REASON + "\n", "")
        self.assert_fails("D:serial has no 'Rejected' and no 'Replaced'")
        self.write(JOBS, DECISIONS)
        self.revise()
        self.replace(JOBS, "Rejected:\n- First come, first served: it keeps the order jobs came in; rejected because a "
                           "long job holds back the short ones behind it (C:turnaround).\n\n", "")
        self.assert_passes()

    def test_a_date_only_in_a_fact_declared(self):
        self.replace(JOBS, "{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrived in bursts on 2026-01-05}")
        self.assert_passes()
        self.assert_each_fails(JOBS, (
            ("How many jobs run at once?", "How many jobs run at once since 2026-01-01?", "a date; a decision holds no date"),
            ("they finish sooner together", "they finished sooner on 2026-01-02", "derivations/jobs.md:6: a date"),
        ))


class FactTests(Fixture):
    """Facts declared inline and in facts/: each declared once, cited, and what it follows."""

    def cite_runs(self):
        self.write(FACTS_PATH, FACTS + DATA_FACT)
        self.replace(JOBS, "a time (F:speed).\n\nRejected:", "a time (F:speed, F:runs).\n\nRejected:")

    def test_inline_facts_in_each_form(self):
        for new in ("{F:bursts (assumed): jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts; follows F:speed}",
                    "{F:bursts (assumed): jobs arrive in bursts; follows F:speed}"):
            with self.subTest(new=new):
                self.write(JOBS, DECISIONS.replace("{F:bursts: jobs arrive in bursts}", new))
                result = self.assert_passes()
                self.assertIn("facts: 2", result.stdout)
                self.assertIn("assumed: " + ("1" if "assumed" in new else "0"), result.stdout)

    def test_an_inline_fact_out_of_the_format(self):
        self.assert_each_fails(JOBS, tuple(
            ("{F:bursts: jobs arrive in bursts}", new, "an inline fact reads '{F:<id>: <text>}'")
            for new in ("{F:bursts jobs arrive in bursts}", "{F:bursts:}", "{F:bursts (guessed): jobs arrive in bursts}",
                        "{F:bursts: jobs arrive in bursts")))

    def test_a_fact_in_facts_with_its_data_and_what_it_follows(self):
        self.cite_runs()
        result = self.assert_passes()
        self.assertIn("facts: 3  decisions: 3  rejected: 3  assumed: 1", result.stdout)

    def test_a_fact_in_facts_out_of_the_format(self):
        self.cite_runs()
        self.assert_each_fails(FACTS_PATH, (
            ("Fact runs (assumed):", "Fact runs (Assumed):", "a record opens 'Fact <id>: <text>' or 'Fact <id> (assumed): <text>'"),
            ("Follows: F:speed", "Assumed: until timed again", "no field 'Assumed'; a fact has Follows"),
            ("Follows: F:speed", "Follows: D:serial", "'Follows' names the one fact this one follows"),
            ("Follows: F:speed", "Follows: F:speed, F:runs", "'Follows' names the one fact"),
            ("b    11\n```\n", "b    11\n", "a data block that is never closed"),
            ("others, as timed on 2026-01-05.\n\n```", "others, as timed on 2026-01-05.\n```",
             "a data block must be separated from the line before it by a blank line"),
            ("\n```\njob", "\n```text\njob", "a data block is fenced by a line '```' alone"),
            ("Follows: F:speed", "```\nc    12\n```\n\nFollows: F:speed", "a second data block in F:runs"),
            ("Follows: F:speed", "It was timed by hand.", "a line outside the record format"),
        ))

    def test_a_fact_declared_twice(self):
        self.write(FACTS_PATH, FACTS + "\nFact bursts: Jobs arrive in bursts.\n")
        self.assert_fails("F:bursts is also at derivations/jobs.md:10")
        self.write(FACTS_PATH, FACTS)
        self.replace(JOBS, "have none of their own.", "have none of their own, as {F:bursts: they come together}.")
        self.assert_fails("F:bursts is also at derivations/jobs.md:10")

    def test_a_fact_in_facts_no_decision_cites(self):
        self.write(FACTS_PATH, FACTS + "\nFact disk: The disk is slow.\n")
        self.assert_fails("F:disk is cited by no decision")

    def test_a_fact_cited_only_in_a_decisions_history(self):
        self.revise()
        self.write(FACTS_PATH, FACTS + "\nFact disk: The disk is slow.\n")
        self.replace(JOBS, "replaced because C:turnaround replaces C:rule.",
                     "replaced because C:turnaround replaces C:rule, and the disk is slow (F:disk).")
        self.assert_passes()

    def test_what_a_fact_follows(self):
        self.assert_each_fails(JOBS, (
            ("{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts; follows F:nothing}",
             "F:nothing resolves to no fact"),
            ("{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts; follows F:bursts}",
             "the facts' follows form a cycle: F:bursts -> F:bursts"),
        ))
        self.write(FACTS_PATH, FACTS + "\nFollows: F:bursts\n")
        self.replace(JOBS, "{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts; follows F:speed}")
        self.assert_fails("the facts' follows form a cycle: F:bursts -> F:speed -> F:bursts")


class ReferenceTests(Fixture):
    """References, a decision's premises, their cycles, and what a decision in force rests on."""

    def test_a_reference_that_resolves_to_nothing(self):
        self.assert_each_fails(JOBS, (
            ("(C:aim)", "(C:nothing)", "C:nothing resolves to no article"),
            ("(F:speed).\n\nRejected:", "(F:nothing).\n\nRejected:", "F:nothing resolves to no fact"),
            ("(D:serial)", "(D:nothing)", "D:nothing resolves to no decision"),
            ("How many jobs", "As D:nothing asks, how many jobs", "D:nothing resolves to no decision"),
        ))

    def test_chosen_cites_an_article_or_a_decision(self):
        self.replace(JOBS, "one thing (C:aim) and", "one thing and")
        self.assert_fails("derivations/jobs.md:3: the Chosen of D:serial cites no article and no decision")
        self.replace(JOBS, "(F:speed).\n\nDecision queue", "(F:speed, C:aim).\n\nDecision queue")
        self.assert_fails("the Chosen of D:serial cites no article and no decision")

    def test_premises_in_a_cycle(self):
        self.replace(JOBS, "one thing (C:aim) and", "one thing (C:aim), as ties are broken (D:ties), and")
        self.assert_fails("the decisions' premises form a cycle: D:queue -> D:serial -> D:ties -> D:queue")

    def test_the_dependents_of_a_record(self):
        result = self.assert_passes("--dependents", "C:aim", "D:ties", "F:bursts")
        self.assertIn("dependents of C:aim: 3\n  D:queue (derivations/jobs.md:8)\n  D:serial (derivations/jobs.md:1)\n"
                      "  D:ties (derivations/jobs.md:15)", result.stdout)
        self.assertIn("dependents of D:ties: 0", result.stdout)
        self.assertIn("dependents of F:bursts: 2\n  D:queue (derivations/jobs.md:8)\n  D:ties (derivations/jobs.md:15)",
                      result.stdout)
        self.assert_fails("--dependents: D:nothing is no record", "--dependents", "D:nothing")

    def test_a_premise_in_rejected_is_a_premise_and_one_in_history_is_none(self):
        self.replace(JOBS, "they finish sooner together;", "they finish sooner together, out of order (C:rule);")
        result = self.assert_passes("--dependents", "C:rule")
        self.assertIn("dependents of C:rule: 3\n  D:queue", result.stdout)
        self.assertIn("  D:serial (derivations/jobs.md:1)", result.stdout)
        self.write(JOBS, DECISIONS)
        self.revise()
        result = self.assert_passes("--dependents", "C:rule", "F:bursts")
        self.assertIn("dependents of C:rule: 0", result.stdout)
        self.assertIn("dependents of F:bursts: 0", result.stdout)

    def test_a_decision_in_force_on_a_replaced_article(self):
        self.write(CONSTITUTION_PATH, CONSTITUTION + TURNAROUND)
        self.assert_fails("D:queue is in force and rests on C:rule, which C:turnaround replaces")

    def test_a_decision_in_force_on_a_lost_decision(self):
        self.revise()
        self.write(JOBS, self.read(JOBS) + REPORT)
        self.assert_fails("D:report is in force and rests on D:ties, which is lost with D:queue")

    def test_a_decision_lost_with_the_one_it_rests_on(self):
        self.revise()
        self.write(JOBS, self.read(JOBS) + REPORT + TIES_LOST)
        self.assert_passes()

    def test_a_decision_back_with_an_approach_is_in_force_again(self):
        self.revise()
        self.write(JOBS, self.read(JOBS) + REPORT)
        self.replace(JOBS, TIES_LOST, TIES_LOST + "- back with D:queue, First come, first served\n")
        self.assert_passes()


class WordsTests(Fixture):
    """No code span and no path or file name in a decision or a fact."""

    def test_a_code_span(self):
        self.replace(JOBS, "How many jobs run at once?", "How many `jobs` run at once?")
        self.assert_fails("derivations/jobs.md:1: a code span, `jobs`; a record names no code")

    def test_a_path_or_a_file_name(self):
        self.assert_each_fails(JOBS, tuple(
            ("they finish sooner together;", f"they finish sooner together, as {word} shows;",
             f"'{word}' names a path or a file")
            for word in ("src/run.rs", "../jobs/run.py", "run.py", "Cargo.toml", "flow.json")))

    def test_a_code_span_or_a_path_in_a_fact(self):
        self.write(FACTS_PATH, FACTS.replace("one job", "one `job`"))
        self.assert_fails("facts/machine.md:1: a code span, `job`")
        self.write(FACTS_PATH, FACTS + DATA_FACT.replace("a    10", "src/a.rs    10"))
        self.replace(JOBS, "a time (F:speed).\n\nRejected:", "a time (F:speed, F:runs).\n\nRejected:")
        self.assert_fails("'src/a.rs' names a path or a file")

    def test_words_that_are_no_path(self):
        self.replace(JOBS, "they finish sooner together;",
                     "they finish sooner together, as https://example.com/run.html and example.com/jobs.html say, "
                     "read and/or written, at 3.5 jobs a second, e.g. in bursts;")
        self.assert_passes()


class ReadyTests(Fixture):
    """The records against a base in a temporary repository: they only grow."""

    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Reasoning check fixture")
        self.git("config", "user.email", "reasoning-check@example.invalid")
        self.base = self.commit("Start")
        self.git("branch", "-M", "main")
        self.git("update-ref", "refs/remotes/origin/main", self.base)

    def git(self, *args):
        return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
                              cwd=self.root, text=True, capture_output=True, check=True).stdout.strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def ready(self):
        return ("--base", self.base, "--ready")

    def test_a_revision_passes_and_counts_against_the_base(self):
        self.revise()
        result = self.assert_passes(*self.ready())
        self.assertIn("articles: 3 (base 2, +1)  facts: 2 (base 2, +0)  decisions: 3 (base 3, +0)  "
                      "rejected: 3 (base 3, +0)  assumed: 0 (base 0, +0)", result.stdout)

    def test_counts_against_a_base_without_readiness(self):
        self.write(JOBS, DECISIONS + REPORT)
        result = self.assert_passes("--base", self.base)
        self.assertIn("decisions: 4 (base 3, +1)", result.stdout)

    def test_a_record_removed(self):
        self.replace(JOBS, "\n" + TIES, "")
        self.assert_fails("derivations/jobs.md:15: D:ties stood here at the base and is gone", *self.ready())
        self.write(JOBS, DECISIONS)
        self.write(CONSTITUTION_PATH, CONSTITUTION.replace("\n## Article 2 (rule). A rule\n\nJobs keep the order they "
                                                           "came in.\n", ""))
        self.assert_fails("C:rule stood here at the base and is gone", *self.ready())
        self.write(CONSTITUTION_PATH, CONSTITUTION)
        self.replace(JOBS, "{F:bursts: jobs arrive in bursts}", "jobs arrive in bursts")
        self.assert_fails("F:bursts stood here at the base and is gone", *self.ready())

    def test_records_moved_are_no_change(self):
        text = self.read(JOBS)
        queue = text.index("Decision queue:")
        self.write(JOBS, text[:queue].rstrip("\n") + "\n")
        self.write("reasoning/derivations/queue.md", text[queue:].replace("{F:bursts: jobs arrive in bursts}", "F:bursts"))
        self.write(FACTS_PATH, FACTS + "\nFact bursts: jobs arrive in bursts\n")
        self.assert_passes(*self.ready())

    def test_an_article_reworded(self):
        self.replace(CONSTITUTION_PATH, "The project does one thing.", "The project does one thing well.")
        self.assert_fails("C:aim changed since the base; an article is never reworded", *self.ready())

    def test_a_fact_reworded(self):
        self.assert_each_fails(FACTS_PATH, (
            ("one job", "a single job", "F:speed changed since the base; a fact is never reworded"),
            ("Fact speed:", "Fact speed (assumed):", "F:speed changed since the base"),
            (FACTS, FACTS + "\n```\none job\n```\n", "F:speed changed since the base"),
        ), *self.ready())
        self.assert_each_fails(JOBS, (
            ("{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in large bursts}", "F:bursts changed since the base"),
            ("{F:bursts: jobs arrive in bursts}", "{F:bursts: jobs arrive in bursts; follows F:speed}",
             "F:bursts changed since the base"),
        ), *self.ready())

    def test_a_question_changed(self):
        self.replace(JOBS, "In what order do waiting jobs run?", "In what order do jobs run?")
        self.assert_fails("the question of D:queue changed since the base; it never changes", *self.ready())

    def test_history_only_grows_at_its_end(self):
        self.revise()
        self.base = self.commit("Revise")
        self.replace(JOBS, TIES_LOST, TIES_LOST + "- back with D:queue, First come, first served\n")
        self.assert_passes(*self.ready())
        self.write(JOBS, self.read(JOBS).replace("- back with D:queue, First come, first served\n", ""))
        self.assert_each_fails(JOBS, (
            ("replaced because C:turnaround replaces C:rule.", "replaced because the rule went.",
             "the Replaced items of D:queue at the base changed, moved or went"),
            ("\nBroke:\n- Shortest first within each burst: breaks on D:serial\n", "",
             "the Broke items of D:queue at the base changed, moved or went"),
            ("Lost:\n- with D:queue", "Lost:\n- back with D:queue, First come, first served\n- with D:queue",
             "the Lost items of D:ties at the base changed, moved or went"),
        ), *self.ready())

    def test_a_changed_choice_is_kept_as_replaced(self):
        self.replace(JOBS, "Chosen: First come, first served, because", "Chosen: Oldest first, because")
        self.assert_fails("the Chosen of D:queue changed since the base, but no new Replaced item keeps the choice it "
                          "held, 'First come, first served', with the reasons it was chosen on", *self.ready())
        self.write(JOBS, DECISIONS)
        self.revise()
        self.replace(JOBS, "chosen because jobs keep the order they came in (C:rule) and run",
                     "chosen because jobs keep their order (C:rule) and run")
        self.assert_fails("the Chosen of D:queue changed since the base, but no new Replaced item", *self.ready())

    def test_reasons_changed_only_in_a_revision(self):
        self.replace(JOBS, SERIAL_CHOSEN, SERIAL_REVISED)
        self.assert_fails("the Chosen of D:serial changed since the base, but no new Replaced item", *self.ready())
        self.replace(JOBS, "they finish sooner together; " + SERIAL_REASON,
                     "they finish sooner together; rejected because the machine has one core (F:cores).")
        self.replace(JOBS, SERIAL_REVISED, SERIAL_REVISED + "\n" + SERIAL_REPLACED.rstrip("\n"))
        self.assert_passes(*self.ready())
        self.write(JOBS, DECISIONS)
        self.replace(JOBS, "they finish sooner together;", "they would finish sooner together;")
        self.assert_fails("the rejected option 'Several at once' of D:serial has other reasons than at the base, with "
                          "no new Replaced item", *self.ready())

    def test_a_rejected_option_never_disappears(self):
        self.replace(JOBS, "- Several at once:", "- Many at once:")
        self.assert_fails("the rejected option 'Several at once' of D:serial at the base is gone", *self.ready())

    def test_a_rejected_option_taken_up_as_chosen(self):
        self.revise()
        self.assert_passes(*self.ready())
        self.replace(JOBS, "Chosen: Shortest first, because", "Chosen: Shortest job first, because")
        self.assert_fails("the rejected option 'Shortest first' of D:queue at the base is gone", *self.ready())

    def test_readiness_needs_a_base_that_resolves(self):
        self.assert_fails("--ready: needs --base", "--ready")
        tree = self.git("rev-parse", "HEAD^{tree}")
        for base in ("no-such-revision", tree):
            with self.subTest(base=base):
                self.assert_fails("resolves to no commit", "--base", base, "--ready")

    def ci_base(self, event, ref, before=""):
        return subprocess.run(["sh", str(CI_BASE), event, ref, before], cwd=self.root, text=True, capture_output=True)

    def test_a_push_to_main_compares_with_the_tip_before_it(self):
        self.revise()
        self.commit("Change")
        result = self.ci_base("push", "refs/heads/main", self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.base)

    def test_a_pull_request_compares_with_its_fork_point(self):
        self.git("checkout", "--quiet", "-b", "work")
        self.revise()
        self.commit("Change")
        result = self.ci_base("pull_request", "refs/pull/1/merge")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.base)

    def test_a_main_base_equal_to_head_fails(self):
        result = self.ci_base("push", "refs/heads/main", self.base)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing an empty comparison", result.stderr)

    def test_an_unhandled_event_fails(self):
        result = self.ci_base("schedule", "refs/heads/main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported event", result.stderr)


if __name__ == "__main__":
    unittest.main()
