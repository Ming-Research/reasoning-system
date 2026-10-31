#!/usr/bin/env python3
"""The check of a project's reasoning records: the form of every record, that
every reference resolves and is listed in its derivation's Rests on, that the
derivations form no cycle and no removed id is used again, and, against a base
revision with --ready, that every change is logged and no merged log entry
changed. Its messages say what it checks."""
import argparse
import os
import re
import subprocess
import sys

ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
REF = re.compile(rf"(?<![A-Za-z0-9])([CFD]):({ID})(?![A-Za-z0-9])")
REF_ONLY = re.compile(rf"^[CFD]:{ID}$")
ARTICLE = re.compile(rf"^## Article (\d+) \(({ID})\)\. \S")
HEADS = {"F": re.compile(rf"^Fact ({ID}): \S"), "D": re.compile(rf"^Decision ({ID}): \S")}
HEAD_WORDS = {"F": "Fact", "D": "Decision"}
FIELD = re.compile(r"^([A-Z][a-z]*(?: [a-z]+)*):(?: |$)")
FIELDS = {"F": ("Assumed",), "D": ("Rests on", "Open", "Rejected")}
REJECTED_ITEM = re.compile(r"^- \S.*?: rejected because \S")
DATE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
LOG_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2}) \S")
LOG_FIELDS = ("Changed", "Why", "Re-examined", "Ruling")
CHANGE = re.compile(rf"^([CFD]:{ID}) (added|changed|removed)$")
KINDS = {"C": "article", "F": "fact", "D": "derivation"}


class Record:
    def __init__(self, kind, ident, path, start):
        self.kind = kind
        self.id = ident
        self.path = path
        self.start = start
        self.lines = []
        self.fields = {}  # field name -> (line number, value)
        self.rejected = 0

    @property
    def ref(self):
        return f"{self.kind}:{self.id}"

    def text(self):
        """The record as compared with a base; an article's number is its place, not its content."""
        lines = list(self.lines)
        if self.kind == "C":
            lines[0] = re.sub(r"^## Article \d+ ", "## Article ", lines[0])
        return "\n".join(lines)

    def numbered(self):
        return enumerate(self.lines, self.start)


class Entry:
    def __init__(self, heading, line, date):
        self.heading = heading
        self.line = line
        self.date = date
        self.lines = [heading]
        self.fields = {}
        self.changes = []

    def text(self):
        return "\n".join(self.lines).rstrip("\n")


class Records:
    def __init__(self):
        self.errors = []
        self.records = {}  # ref -> Record
        self.entries = []
        self.resting = None  # derivation -> the derivations resting on it directly

    def err(self, where, message):
        self.errors.append(f"{where}: {message}")

    # ---- loading ---------------------------------------------------------

    def load(self, files, ascii_only=False):
        """files maps a path relative to the records' root to its bytes."""
        texts = {}
        for path, data in sorted(files.items()):
            if b"\r" in data:
                self.err(path, "a carriage return; the records end their lines with \\n alone")
            if ascii_only:
                for number, raw in enumerate(data.split(b"\n"), 1):
                    if any(byte > 127 for byte in raw):
                        self.err(f"{path}:{number}", "non-ASCII text; the project keeps its records in English")
            try:
                texts[path] = data.decode("utf-8").replace("\r", "")
            except UnicodeDecodeError:
                self.err(path, "not UTF-8 text")
        self.check_layout(texts)
        if "constitution.md" in texts:
            self.parse_constitution("constitution.md", texts["constitution.md"])
        for path, text in sorted(texts.items()):
            if path.startswith("facts/") and path.endswith(".md"):
                self.parse_entries(path, text, "F")
            elif path.startswith("derivations/") and path.endswith(".md"):
                self.parse_entries(path, text, "D")
        if "log.md" in texts:
            self.parse_log(texts["log.md"])

    def check_layout(self, texts):
        for required in ("constitution.md", "log.md"):
            if required not in texts:
                self.err(required, "missing")
        for path in sorted(texts):
            parts = path.split("/")
            if len(parts) == 1 and path in ("constitution.md", "log.md"):
                continue
            if parts[0] in ("facts", "derivations") and len(parts) > 1 and path.endswith(".md"):
                for depth in range(2, len(parts)):
                    node = "/".join(parts[:depth]) + ".md"
                    if node not in texts:
                        self.err(path, f"its directory has no node file {node}")
                continue
            self.err(path, "not part of the records: constitution.md, facts/**.md, derivations/**.md, log.md")

    # ---- the constitution --------------------------------------------------

    def parse_constitution(self, path, text):
        current = None
        expected = 1
        for number, line in enumerate(text.split("\n"), 1):
            if line.startswith("## "):
                self.close(current)
                current = None
                match = ARTICLE.match(line)
                if not match:
                    self.err(f"{path}:{number}", "an article is headed '## Article <n> (<id>). <title>'")
                    continue
                if int(match[1]) != expected:
                    self.err(f"{path}:{number}", f"article {match[1]} where article {expected} comes next")
                expected = int(match[1]) + 1
                current = self.open("C", match[2], path, number)
            if current is not None:
                current.lines.append(line)
        self.close(current)
        if expected == 1:
            self.err(path, "the constitution has no article")
        for record in self.records.values():
            if record.kind == "C" and not any(line.strip() for line in record.lines[1:]):
                self.err(f"{path}:{record.start}", f"{record.ref} has no text")

    # ---- facts and derivations ---------------------------------------------

    def parse_entries(self, path, text, kind):
        head = HEADS[kind]
        word = HEAD_WORDS[kind]
        current = None
        count = 0
        prev = "start"
        in_list = False
        for number, line in enumerate(text.split("\n"), 1):
            loc = f"{path}:{number}"
            match = head.match(line)
            if current is not None and not match:
                current.lines.append(line)
            if DATE.search(line):
                self.err(loc, "a date; a record holds no history, the log does")
            if not line.strip():
                prev = "blank"
                in_list = False
                continue
            if match:
                if prev not in ("start", "blank"):
                    self.err(loc, "a record must be separated from the line before it by a blank line")
                self.close(current)
                current = self.open(kind, match[1], path, number)
                current.lines.append(line)
                count += 1
                prev = "head"
                in_list = False
                continue
            if line.startswith(word + " "):
                self.err(loc, f"a record opens '{word} <id>: <text>', its id lowercase words joined by hyphens")
                prev = "other"
                continue
            field = FIELD.match(line)
            if field:
                name = field[1]
                value = line[len(name) + 1:].strip()
                prev_was = prev
                prev = "field"
                in_list = False
                if name not in FIELDS[kind]:
                    allowed = ", ".join(FIELDS[kind])
                    self.err(loc, f"no field '{name}'; a {KINDS[kind]} has {allowed}")
                    continue
                if current is None:
                    self.err(loc, "a field before the first record")
                    continue
                if prev_was != "blank":
                    self.err(loc, "a field must be separated from the line before it by a blank line")
                if name in current.fields:
                    self.err(loc, f"a second '{name}' field in {current.ref}")
                if name == "Rejected":
                    if value:
                        self.err(loc, "'Rejected:' stands alone, its items on the lines after it")
                    in_list = True
                elif not value:
                    self.err(loc, f"an empty '{name}' field")
                current.fields[name] = (number, value)
                continue
            if line.startswith("- "):
                if not in_list or prev not in ("field", "item"):
                    self.err(loc, "a list item must follow 'Rejected:' or the item before it")
                elif not REJECTED_ITEM.match(line):
                    self.err(loc, "a rejected item reads '- <approach>: rejected because <reason>'")
                else:
                    current.rejected += 1
                prev = "item"
                continue
            self.err(loc, "a line outside the record format; each field is one line")
            prev = "other"
        self.close(current)
        if count == 0:
            self.err(path, f"holds no {KINDS[kind]}")

    def open(self, kind, ident, path, number):
        record = Record(kind, ident, path, number)
        if record.ref in self.records:
            first = self.records[record.ref]
            self.err(f"{path}:{number}", f"{record.ref} is also at {first.path}:{first.start}; an id is unique in its kind")
            return record
        self.records[record.ref] = record
        return record

    def close(self, record):
        if record is None:
            return
        while record.lines and not record.lines[-1].strip():
            record.lines.pop()
        if record.kind == "F":
            for number, line in record.numbered():
                for match in REF.finditer(line):
                    self.err(f"{record.path}:{number}", f"{match[0]}: a fact is given and cites no record")
        if record.kind == "D":
            self.check_derivation(record)

    def check_derivation(self, record):
        where = f"{record.path}:{record.start}"
        if " because " not in record.lines[0] and "Open" not in record.fields:
            self.err(where, f"{record.ref} gives no 'because'; only an Open derivation may give no reason")
        if record.fields.get("Rejected") is not None and record.rejected == 0:
            self.err(f"{record.path}:{record.fields['Rejected'][0]}", "a 'Rejected:' list with no item")
        if "Rests on" not in record.fields:
            if "Open" not in record.fields:
                self.err(where, f"{record.ref} has no 'Rests on'; only an Open derivation may cite nothing")
            for number, line in record.numbered():
                for match in REF.finditer(line):
                    self.err(f"{record.path}:{number}", f"{record.ref} cites {match[0]}, which its Rests on does not list")
            return
        rests_line, value = record.fields["Rests on"]
        premises = [item.strip() for item in value.split(",")]
        for premise in premises:
            if not REF_ONLY.match(premise):
                self.err(f"{record.path}:{rests_line}", f"'{premise}' in Rests on is no reference 'C:<id>', 'F:<id>' or 'D:<id>'")
        if len(set(premises)) != len(premises):
            self.err(f"{record.path}:{rests_line}", "Rests on lists a reference twice")
        for number, line in record.numbered():
            if number == rests_line:
                continue
            for match in REF.finditer(line):
                if match[0] not in premises:
                    self.err(f"{record.path}:{number}", f"{record.ref} cites {match[0]}, which its Rests on does not list")

    # ---- the log -------------------------------------------------------------

    def parse_log(self, text):
        entry = None
        prev = "start"
        for number, line in enumerate(text.split("\n"), 1):
            loc = f"log.md:{number}"
            if line.startswith("## "):
                match = LOG_HEADING.match(line)
                if not match:
                    self.err(loc, "a log entry is headed '## <YYYY-MM-DD> <title>'")
                entry = Entry(line, number, match[1] if match else "")
                self.entries.append(entry)
                prev = "head"
                continue
            if entry is None:
                if line.strip() and not line.startswith("# "):
                    self.err(loc, "a line before the first log entry")
                continue
            entry.lines.append(line)
            if not line.strip():
                prev = "blank"
                continue
            name = next((field for field in LOG_FIELDS if line.startswith(field + ":")), None)
            if name is None:
                self.err(loc, "a line outside the log entry format; each field is one line")
                prev = "other"
                continue
            if prev != "blank":
                self.err(loc, "a field must be separated from the line before it by a blank line")
            prev = "field"
            if name in entry.fields:
                self.err(loc, f"a second '{name}' field")
            value = line[len(name) + 1:].strip()
            entry.fields[name] = (number, value)
            if name == "Changed":
                for item in (part.strip() for part in value.split(",")):
                    match = CHANGE.match(item)
                    if match:
                        entry.changes.append((match[1], match[2]))
                    else:
                        self.err(loc, f"'{item}' in Changed is no '<reference> added', 'changed' or 'removed'")
        headings = {}
        for index, entry in enumerate(self.entries):
            loc = f"log.md:{entry.line}"
            for name in LOG_FIELDS:
                if not entry.fields.get(name, (0, ""))[1]:
                    self.err(loc, f"the entry gives no '{name}'")
            if entry.heading in headings:
                self.err(loc, f"the heading repeats log.md:{headings[entry.heading]}")
            headings.setdefault(entry.heading, entry.line)
            if index and entry.date and self.entries[index - 1].date and entry.date > self.entries[index - 1].date:
                self.err(loc, "an entry newer than the one above it; the log is newest first")

    # ---- the whole -------------------------------------------------------------

    def check_whole(self):
        for record in self.records.values():
            for number, line in record.numbered():
                for match in REF.finditer(line):
                    if match[0] not in self.records:
                        self.err(f"{record.path}:{number}", f"{match[0]} resolves to no {KINDS[match[1]]}")
        for entry in self.entries:
            for ref, verb in entry.changes:
                if verb == "removed" and ref in self.records:
                    record = self.records[ref]
                    self.err(f"{record.path}:{record.start}",
                             f"{ref} was removed in the log entry '{entry.heading[3:]}', and an id is never used again")
        self.check_cycles()
        self.check_facts_cited()
        self.check_grounded()

    def premises(self, ref):
        """What a derivation's Rests on lists that resolves."""
        record = self.records[ref]
        if "Rests on" not in record.fields:
            return []
        items = (item.strip() for item in record.fields["Rests on"][1].split(","))
        return sorted({item for item in items if item in self.records})

    def derivations(self):
        return sorted(ref for ref, record in self.records.items() if record.kind == "D")

    def is_open(self, ref):
        return "Open" in self.records[ref].fields

    def check_cycles(self):
        edges = {ref: [p for p in self.premises(ref) if p.startswith("D:")] for ref in self.derivations()}
        state = {}
        for root in sorted(edges):
            if root in state:
                continue
            path = [root]
            stack = [iter(edges[root])]
            state[root] = "open"
            while stack:
                following = next(stack[-1], None)
                if following is None:
                    state[path.pop()] = "done"
                    stack.pop()
                    continue
                if state.get(following) == "open":
                    cycle = path[path.index(following):] + [following]
                    record = self.records[following]
                    self.err(f"{record.path}:{record.start}", "the derivations form a cycle: " + " -> ".join(cycle))
                    continue
                if following not in state:
                    state[following] = "open"
                    path.append(following)
                    stack.append(iter(edges[following]))

    def check_facts_cited(self):
        cited = {premise for ref in self.derivations() for premise in self.premises(ref)}
        for ref, record in sorted(self.records.items()):
            if record.kind == "F" and ref not in cited:
                self.err(f"{record.path}:{record.start}",
                         f"{ref} is cited by no derivation; a fact enters only when a derivation rests on it")

    def reaches(self, ref, found, seen=None):
        """Whether a derivation reaches a record that found() accepts through what it rests on."""
        seen = set() if seen is None else seen
        stack = [ref]
        while stack:
            current = stack.pop()
            for premise in self.premises(current):
                if found(premise):
                    return True
                if premise.startswith("D:") and premise not in seen:
                    seen.add(premise)
                    stack.append(premise)
        return False

    def check_grounded(self):
        for ref in self.derivations():
            if self.is_open(ref):
                continue
            if self.reaches(ref, lambda p: p.startswith("C:") or (p.startswith("D:") and self.is_open(p))):
                continue
            record = self.records[ref]
            self.err(f"{record.path}:{record.start}",
                     f"{ref} reaches no article of the constitution through what it rests on, and no Open derivation")

    def on_open(self, ref):
        """The derivations that rest on an Open derivation, directly or through others."""
        if self.resting is None:
            self.resting = {}
            for other in self.derivations():
                for premise in self.premises(other):
                    if premise.startswith("D:"):
                        self.resting.setdefault(premise, set()).add(other)
        found = set()
        stack = [ref]
        while stack:
            for other in self.resting.get(stack.pop(), ()):
                if other not in found and other != ref:
                    found.add(other)
                    stack.append(other)
        return sorted(found)

    # ---- against a base --------------------------------------------------------

    def check_ready(self, base):
        now = [entry.text() for entry in self.entries]
        then = [entry.text() for entry in base.entries]
        fresh = len(now) - len(then)
        if fresh < 0 or now[fresh:] != then:
            self.err("log.md", "a merged log entry was changed, moved or removed; the log grows only at its top")
            fresh = max(fresh, 0)
        named = {}
        for entry in self.entries[:fresh]:
            for ref, verb in entry.changes:
                named.setdefault(ref, set()).add(verb)
        actual = {}
        for ref in set(self.records) | set(base.records):
            if ref not in self.records:
                actual[ref] = "removed"
            elif ref not in base.records:
                actual[ref] = "added"
            elif self.records[ref].text() != base.records[ref].text():
                actual[ref] = "changed"
        if actual and not fresh:
            self.err("log.md", "the records changed since the base, but the log has no new entry")
            return
        for ref, verb in sorted(actual.items()):
            if ref not in named:
                self.err("log.md", f"{ref} was {verb} since the base, but no new log entry names it")
            elif verb not in named[ref]:
                self.err("log.md", f"{ref} was {verb} since the base, but the new entries name it {', '.join(sorted(named[ref]))}")
        for ref in sorted(set(named) - set(actual)):
            self.err("log.md", f"a new log entry names {ref}, which did not change since the base")

    # ---- reporting -------------------------------------------------------------

    def metrics(self):
        records = self.records.values()
        return {
            "articles": sum(r.kind == "C" for r in records),
            "facts": sum(r.kind == "F" for r in records),
            "derivations": sum(r.kind == "D" for r in records),
            "rejected": sum(r.rejected for r in records),
            "open": sum(r.kind == "D" and "Open" in r.fields for r in records),
            "assumed": sum(r.kind == "F" and "Assumed" in r.fields for r in records),
            "on-open": len({other for ref in self.derivations() if self.is_open(ref) for other in self.on_open(ref)}),
        }

    def report(self, base_metrics):
        counts = []
        for name, value in self.metrics().items():
            if base_metrics is None:
                counts.append(f"{name}: {value}")
            else:
                counts.append(f"{name}: {value} (base {base_metrics[name]}, {value - base_metrics[name]:+d})")
        print("  ".join(counts))
        for record in sorted(self.records.values(), key=lambda r: (r.path, r.start)):
            for name, label in (("Open", "open"), ("Assumed", "assumed")):
                if name in record.fields:
                    print(f"{label} {record.ref} ({record.path}:{record.start}): {record.fields[name][1]}")
            if record.kind == "D" and self.is_open(record.ref):
                resting = self.on_open(record.ref)
                if resting:
                    print(f"  resting on {record.ref}: {', '.join(resting)}")


def worktree(root):
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        for name in filenames:
            if name.startswith("."):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "rb") as handle:
                files[os.path.relpath(path, root).replace(os.sep, "/")] = handle.read()
    return files


def git(root, *args, data=None):
    return subprocess.run(["git", *args], cwd=root, input=data, capture_output=True, check=True).stdout


def base_exists(root, base):
    probe = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "--end-of-options", f"{base}^{{commit}}"],
                           cwd=root, capture_output=True)
    return probe.returncode == 0


def files_at(root, base):
    """The records' files at a revision, keyed by their path under the root."""
    blobs = []
    for item in git(root, "ls-tree", "-r", "-z", base, "--", ".").split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        _mode, kind, oid = meta.split()
        name = path.decode()
        if kind == b"blob" and not any(part.startswith(".") for part in name.split("/")):
            blobs.append((name, oid))
    files = {}
    if not blobs:
        return files
    out = git(root, "cat-file", "--batch", data=b"".join(oid + b"\n" for _, oid in blobs))
    pos = 0
    for name, _oid in blobs:
        end = out.index(b"\n", pos)
        size = int(out[pos:end].split()[2])
        files[name] = out[end + 1:end + 1 + size]
        pos = end + 1 + size + 1
    return files


def main():
    parser = argparse.ArgumentParser(description="check a project's reasoning records")
    parser.add_argument("--root", default="reasoning", help="the records' directory")
    parser.add_argument("--base", help="the revision before the change, to compare with")
    parser.add_argument("--ready", action="store_true",
                        help="with --base: every change is named in a new log entry, and no merged entry changed")
    parser.add_argument("--ascii", action="store_true", help="the project keeps its records in English")
    args = parser.parse_args()
    records = Records()
    base_metrics = None
    if not os.path.isdir(args.root):
        records.err(args.root, "no such directory")
    else:
        records.load(worktree(args.root), args.ascii)
        records.check_whole()
        if args.ready and args.base is None:
            records.err("--ready", "needs --base")
        if args.base is not None:
            if not base_exists(args.root, args.base):
                records.err("--base", f"{args.base!r} resolves to no commit")
            else:
                base = Records()
                base.load(files_at(args.root, args.base))
                base_metrics = base.metrics()
                if args.ready:
                    records.check_ready(base)
    if records.errors:
        for error in records.errors:
            print("error: " + error, file=sys.stderr)
        print(f"reasoning check: {len(records.errors)} error(s)", file=sys.stderr)
        return 1
    records.report(base_metrics)
    print("reasoning check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
