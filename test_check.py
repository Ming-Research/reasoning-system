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

Everything follows the aim.
"""
FACTS = "Fact speed: The machine runs one job at a time.\n"
DERIVATIONS = """Decision serial: Jobs run one at a time, instead of in parallel, because the machine runs one job at a time.

Rests on: C:aim, F:speed

Rejected:
- Parallel jobs: rejected because the machine runs one job at a time (F:speed).

Decision queue: Jobs wait in a queue, because they run one at a time.

Rests on: C:rule, D:serial
"""
ENTRY = """## 2026-01-01 Start the records

Changed: C:aim added, C:rule added, F:speed added, D:serial added, D:queue added

Why: The project starts.

Re-examined: none

Ruling: the fixture's ruling
"""
NEXT_ENTRY = """## 2026-01-02 Change the queue

Changed: D:queue changed

Why: The queue is ordered.

Re-examined: none rests on it

Ruling: the fixture's second ruling
"""


class Fixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="reasoning-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("reasoning/constitution.md", CONSTITUTION)
        self.write("reasoning/facts/machine.md", FACTS)
        self.write("reasoning/derivations/jobs.md", DERIVATIONS)
        self.write("reasoning/log.md", "# Log\n\n" + ENTRY)

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


class FormTests(Fixture):
    def test_records_in_the_format_pass_and_are_counted(self):
        result = self.assert_passes()
        self.assertIn("articles: 2  facts: 1  derivations: 2  rejected: 1  open: 0  assumed: 0", result.stdout)

    def test_an_article_heading_out_of_the_format(self):
        self.replace("reasoning/constitution.md", "## Article 2 (rule). A rule", "## Article 2 rule")
        self.assert_fails("an article is headed")

    def test_articles_numbered_out_of_order(self):
        self.replace("reasoning/constitution.md", "## Article 2 (rule)", "## Article 3 (rule)")
        self.assert_fails("article 3 where article 2 comes next")

    def test_an_id_used_twice_in_its_kind(self):
        self.write("reasoning/derivations/more.md", "Decision serial: Again, because of C:aim.\n\nRests on: C:aim\n")
        self.assert_fails("D:serial is also at derivations/jobs.md:1")

    def test_an_id_out_of_the_format(self):
        self.replace("reasoning/derivations/jobs.md", "Decision queue:", "Decision Queue:")
        self.assert_fails("a record opens 'Decision <id>: <text>'")

    def test_a_reference_that_resolves_to_nothing(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial", "Rests on: C:rule, D:serial, F:missing")
        self.assert_fails("F:missing resolves to no fact")

    def test_a_citation_its_rests_on_does_not_list(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:aim, F:speed", "Rests on: C:aim")
        self.assert_fails("D:serial cites F:speed, which its Rests on does not list")

    def test_rests_on_lists_only_references(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial", "Rests on: C:rule and D:serial")
        self.assert_fails("in Rests on is no reference")

    def test_derivations_in_a_cycle(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:aim, F:speed", "Rests on: C:aim, F:speed, D:queue")
        self.assert_fails("the derivations form a cycle")

    def test_a_derivation_without_because(self):
        self.replace("reasoning/derivations/jobs.md", "Jobs wait in a queue, because they run one at a time.",
                     "Jobs wait in a queue.")
        self.assert_fails("D:queue gives no 'because'")

    def test_a_fact_no_derivation_cites(self):
        self.write("reasoning/facts/machine.md", FACTS + "\nFact disk: The disk is slow.\n")
        self.assert_fails("F:disk is cited by no derivation")

    def test_a_derivation_that_reaches_no_article(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:aim, F:speed", "Rests on: F:speed")
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial", "Rests on: D:serial")
        self.assert_fails("D:serial reaches no article of the constitution")

    def test_an_open_derivation_may_cite_nothing_and_what_rests_on_it_is_listed(self):
        self.write("reasoning/derivations/order.md",
                   "Decision order: Jobs keep their order.\n\n"
                   "Open: the reason, which is wholly missing; asked\n\n"
                   "Decision report: The report lists jobs in order, because they keep their order.\n\n"
                   "Rests on: D:order\n")
        result = self.assert_passes()
        self.assertIn("open: 1  assumed: 0  on-open: 1", result.stdout)
        self.assertIn("  resting on D:order: D:report", result.stdout)

    def test_a_derivation_without_rests_on(self):
        self.replace("reasoning/derivations/jobs.md", "\nRests on: C:rule, D:serial\n", "")
        self.assert_fails("D:queue has no 'Rests on'")

    def test_a_rejected_item_out_of_the_format(self):
        self.replace("reasoning/derivations/jobs.md", "- Parallel jobs: rejected because", "- Parallel jobs, since")
        self.assert_fails("a rejected item reads")

    def test_a_rejected_list_with_no_item(self):
        self.replace("reasoning/derivations/jobs.md",
                     "- Parallel jobs: rejected because the machine runs one job at a time (F:speed).\n", "")
        self.assert_fails("a 'Rejected:' list with no item")

    def test_a_field_without_a_blank_line_before_it(self):
        self.replace("reasoning/derivations/jobs.md", "at a time.\n\nRests on: C:aim", "at a time.\nRests on: C:aim")
        self.assert_fails("a field must be separated from the line before it by a blank line")

    def test_a_field_the_kind_does_not_have(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial",
                     "Rests on: C:rule, D:serial\n\nHolds while: the machine is small")
        self.assert_fails("no field 'Holds while'")

    def test_a_field_on_two_lines(self):
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial", "Rests on: C:rule,\nD:serial")
        self.assert_fails("a line outside the record format")

    def test_a_date_in_a_derivation(self):
        self.replace("reasoning/derivations/jobs.md", "Jobs wait in a queue,", "Since 2026-01-01 jobs wait in a queue,")
        self.assert_fails("a date; a record holds no history")

    def test_a_fact_that_cites_a_record(self):
        self.write("reasoning/facts/machine.md", "Fact speed: The machine runs one job at a time, by C:aim.\n")
        self.assert_fails("C:aim: a fact is given and cites no record")

    def test_open_derivations_and_assumed_facts_are_listed(self):
        self.write("reasoning/facts/machine.md", FACTS + "\nAssumed: until the machine is measured\n")
        self.replace("reasoning/derivations/jobs.md", "Rests on: C:rule, D:serial",
                     "Rests on: C:rule, D:serial\n\nOpen: why a queue and not a stack; asked")
        result = self.assert_passes()
        self.assertIn("open: 1  assumed: 1", result.stdout)
        self.assertIn("open D:queue (derivations/jobs.md:8): why a queue and not a stack; asked", result.stdout)
        self.assertIn("assumed F:speed (facts/machine.md:1): until the machine is measured", result.stdout)

    def test_subjects_nest_under_their_node_file(self):
        self.write("reasoning/facts/machine/disk.md", "Fact disk: The disk is slow.\n")
        self.write("reasoning/derivations/jobs/order.md",
                   "Decision order: Jobs keep their order, because of D:queue and the slow disk.\n\nRests on: D:queue, F:disk\n")
        self.assert_passes()

    def test_a_directory_without_its_node_file(self):
        self.write("reasoning/derivations/other/order.md", "Decision order: Kept, because of D:queue.\n\nRests on: D:queue\n")
        self.assert_fails("its directory has no node file derivations/other.md")

    def test_a_file_that_is_no_record(self):
        for path in ("reasoning/notes.md", "reasoning/derivations/jobs.txt"):
            with self.subTest(path=path):
                self.write(path, "notes\n")
                self.assert_fails("not part of the records")
                (self.root / path).unlink()

    def test_a_node_file_with_no_record(self):
        self.write("reasoning/derivations/empty.md", "\n")
        self.assert_fails("derivations/empty.md: holds no derivation")

    def test_missing_constitution_or_log(self):
        for path in ("reasoning/constitution.md", "reasoning/log.md"):
            with self.subTest(path=path):
                text = self.read(path)
                (self.root / path).unlink()
                self.assert_fails(path.split("/")[1] + ": missing")
                self.write(path, text)

    def test_non_ascii_text_only_when_the_project_is_english(self):
        self.replace("reasoning/derivations/jobs.md", "Jobs wait in a queue", "Jobs wait in a queue \u2014 in order \u2014")
        self.assert_passes()
        self.assert_fails("non-ASCII text", "--ascii")

    def test_a_carriage_return(self):
        self.write("reasoning/facts/machine.md", FACTS.replace("\n", "\r\n"))
        self.assert_fails("a carriage return")


class LogTests(Fixture):
    def test_an_entry_missing_a_field(self):
        self.replace("reasoning/log.md", "\nRuling: the fixture's ruling\n", "")
        self.assert_fails("the entry gives no 'Ruling'")

    def test_a_changed_item_without_its_verb(self):
        self.replace("reasoning/log.md", "D:queue added", "D:queue")
        self.assert_fails("'D:queue' in Changed is no '<reference> added'")

    def test_entries_out_of_order(self):
        older = NEXT_ENTRY.replace("2026-01-02", "2025-12-31")
        self.write("reasoning/log.md", "# Log\n\n" + older + "\n" + ENTRY)
        self.assert_fails("an entry newer than the one above it")

    def test_a_repeated_heading(self):
        self.write("reasoning/log.md", "# Log\n\n" + ENTRY + "\n" + ENTRY)
        self.assert_fails("the heading repeats")

    def test_a_removed_id_used_again(self):
        removal = NEXT_ENTRY.replace("D:queue changed", "D:queue removed")
        self.write("reasoning/log.md", "# Log\n\n" + removal + "\n" + ENTRY)
        self.assert_fails("D:queue was removed in the log entry '2026-01-02 Change the queue'")


class ReadyTests(Fixture):
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

    def change_queue(self):
        self.replace("reasoning/derivations/jobs.md", "Jobs wait in a queue,", "Jobs wait in an ordered queue,")

    def test_a_logged_change_passes_and_counts_against_the_base(self):
        self.change_queue()
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + NEXT_ENTRY + "\n")
        result = self.assert_passes(*self.ready())
        self.assertIn("derivations: 2 (base 2, +0)", result.stdout)

    def test_a_change_without_a_new_entry(self):
        self.change_queue()
        self.assert_fails("the records changed since the base, but the log has no new entry", *self.ready())

    def test_a_change_the_new_entry_does_not_name(self):
        self.change_queue()
        self.replace("reasoning/facts/machine.md", "one job", "a single job")
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + NEXT_ENTRY + "\n")
        self.assert_fails("F:speed was changed since the base, but no new log entry names it", *self.ready())

    def test_a_change_named_with_the_wrong_verb(self):
        self.change_queue()
        entry = NEXT_ENTRY.replace("D:queue changed", "D:queue added")
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + entry + "\n")
        self.assert_fails("D:queue was changed since the base, but the new entries name it added", *self.ready())

    def test_a_new_entry_naming_what_did_not_change(self):
        self.change_queue()
        entry = NEXT_ENTRY.replace("D:queue changed", "D:queue changed, D:serial changed")
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + entry + "\n")
        self.assert_fails("a new log entry names D:serial, which did not change since the base", *self.ready())

    def test_a_merged_entry_changed(self):
        self.change_queue()
        self.replace("reasoning/log.md", "Why: The project starts.", "Why: The project started.")
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + NEXT_ENTRY + "\n")
        self.assert_fails("a merged log entry was changed, moved or removed", *self.ready())

    def test_a_removed_record_is_named_removed(self):
        self.replace("reasoning/derivations/jobs.md", "\nDecision queue: Jobs wait in a queue, because they run one at a time.\n\nRests on: C:rule, D:serial\n", "")
        entry = NEXT_ENTRY.replace("D:queue changed", "D:queue removed")
        self.replace("reasoning/log.md", "# Log\n\n", "# Log\n\n" + entry + "\n")
        self.assert_passes(*self.ready())

    def test_a_moved_or_renumbered_record_is_no_change(self):
        text = self.read("reasoning/derivations/jobs.md")
        queue = text.index("Decision queue:")
        self.write("reasoning/derivations/jobs.md", text[:queue].rstrip("\n") + "\n")
        self.write("reasoning/derivations/queue.md", text[queue:])
        self.assert_passes(*self.ready())

    def test_readiness_needs_a_base_that_resolves(self):
        self.assert_fails("--ready: needs --base", "--ready")
        tree = self.git("rev-parse", "HEAD^{tree}")
        for base in ("no-such-revision", tree):
            with self.subTest(base=base):
                self.assert_fails("resolves to no commit", "--base", base, "--ready")

    def ci_base(self, event, ref, before=""):
        return subprocess.run(["sh", str(CI_BASE), event, ref, before], cwd=self.root, text=True, capture_output=True)

    def test_a_push_to_main_compares_with_the_tip_before_it(self):
        self.change_queue()
        self.commit("Change")
        result = self.ci_base("push", "refs/heads/main", self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.base)

    def test_a_pull_request_compares_with_its_fork_point(self):
        self.git("checkout", "--quiet", "-b", "work")
        self.change_queue()
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
