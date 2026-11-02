#!/usr/bin/env python3
"""The check of a project's reasoning records: the form of every article,
decision and fact, that every reference resolves, that the decisions'
premises and the facts' follows form no cycle, and that no decision in force
rests on a replaced article or a lost decision; and, against a base revision
with --ready, that the records only grew: no id removed, no article or fact
reworded, a decision's history only added to, and a choice it changed kept as
replaced. Its messages say what it checks."""
import argparse
import os
import re
import subprocess
import sys

ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
REF = re.compile(rf"(?<![A-Za-z0-9])([CFD]):({ID})(?![A-Za-z0-9])")
ARTICLE = re.compile(rf"^## Article (\d+) \(({ID})\)\. \S")
REPLACES = re.compile(rf"^Replaces: (C:{ID})$")
HEADS = {"F": re.compile(rf"^Fact ({ID})( \(assumed\))?: (\S.*)$"), "D": re.compile(rf"^Decision ({ID}): (\S.*)$")}
HEAD_WORDS = {"F": "Fact", "D": "Decision"}
OPENINGS = {"F": "'Fact <id>: <text>' or 'Fact <id> (assumed): <text>'", "D": "'Decision <id>: <question>'"}
FIELD = re.compile(r"^([A-Z][a-z]*(?: [a-z]+)*):(?: |$)")
FIELDS = {"F": ("Follows",), "D": ("Chosen", "Rejected", "Replaced", "Broke", "Lost")}
LISTS = ("Rejected", "Replaced", "Broke", "Lost")
ITEMS = {
    "Rejected": (re.compile(r"^- (\S.*?): (\S.*?); rejected because \S"),
                 "'- <option>: <what it does better>; rejected because <reason>'"),
    "Replaced": (re.compile(r"^- (\S.*?): chosen (because|so that) (\S.*); replaced because \S"),
                 "'- <choice>: chosen because|so that <its reasons>; replaced because <the base that changed>'"),
    "Broke": (re.compile(rf"^- (\S.*?): breaks on ([CFD]:{ID})$"), "'- <revision>: breaks on <reference>'"),
    "Lost": (re.compile(rf"^- (with|back with) (D:{ID}), (\S.*)$"),
             "'- with D:<id>, <approach>' or '- back with D:<id>, <approach>'"),
}
CHOSEN = re.compile(r"^(\S.*?),? (because|so that) (\S.*)$")
FOLLOWS = re.compile(rf"^F:{ID}$")
FENCE = "```"
INLINE = re.compile(rf"\{{F:({ID})( \(assumed\))?: ([^\s{{}}][^{{}}]*)\}}")
INLINE_FOLLOWS = re.compile(rf"^(\S.*?); follows (F:{ID})$")
INLINE_FORMS = "'{F:<id>: <text>}', '{F:<id> (assumed): <text>}' or '{F:<id>: <text>; follows F:<id>}'"
DATE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
CODE_SPAN = re.compile(r"`[^`]+`")
# The common source and configuration extensions that make a word a file name without a slash.
EXTENSIONS = ("bash", "c", "cc", "cfg", "conf", "cpp", "cs", "css", "env", "go", "h", "hpp", "html", "ini", "java",
              "js", "json", "jsx", "kt", "lock", "lua", "md", "mjs", "php", "pl", "plist", "ps1", "py", "rb", "rs",
              "scss", "sh", "sql", "svelte", "swift", "toml", "ts", "tsx", "vue", "xml", "yaml", "yml", "zsh")
FILE_NAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:" + "|".join(EXTENSIONS) + r")$")
EXTENSION = re.compile(r"\.[A-Za-z][A-Za-z0-9]*$")
HOST = re.compile(r"^(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$")
KINDS = {"C": "article", "F": "fact", "D": "decision"}


def plain(text):
    """Text with each fact it declares inline read as a citation of that fact, since a declaration may move."""
    return INLINE.sub(lambda match: f"F:{match[1]}", text)


def is_path(token):
    """Whether a word names a path or a file: a slash and an extension, or a common source or configuration file.
    A web address is no path."""
    word = token.lstrip("\"'`([{<").rstrip("\"'`.,;:!?)]}>")
    if "://" in word or word.startswith("www."):
        return False
    if "/" in word:
        if HOST.match(word.split("/", 1)[0]):
            return False
        return bool(EXTENSION.search(word.rsplit("/", 1)[1]))
    return bool(FILE_NAME.match(word))


class Record:
    def __init__(self, kind, ident, path, start):
        self.kind = kind
        self.id = ident
        self.path = path
        self.start = start
        self.lines = []
        self.fields = {}  # field name -> (line number, value)
        self.items = {}  # list field -> [(line number, text, the match of its form or None)]
        self.question = ""  # a decision's
        self.statement = ""  # a fact's: what is or was the case
        self.assumed = False
        self.follows = None  # a fact's (line number, the fact it follows)
        self.data = None  # a fact's lines of data, fenced after its head in facts/
        self.inline = False  # a fact declared in a decision's reasons

    @property
    def ref(self):
        return f"{self.kind}:{self.id}"

    def text(self):
        """An article as compared with a base; its number is its place, not its content."""
        lines = list(self.lines)
        lines[0] = re.sub(r"^## Article \d+ ", "## Article ", lines[0])
        return "\n".join(lines)

    def declaration(self):
        """A fact as compared with a base, wherever it is declared."""
        data = None if self.data is None else tuple(self.data)
        return (self.assumed, self.statement, data, self.follows[1] if self.follows else None)

    def numbered(self):
        return enumerate(self.lines, self.start)

    def chosen(self):
        """A decision's choice as (option, 'because' or 'so that', reasons)."""
        if "Chosen" not in self.fields:
            return None
        match = CHOSEN.match(plain(self.fields["Chosen"][1]))
        return (match[1], match[2], match[3].rstrip(".")) if match else None

    def listed(self, name):
        """The matches of the items of a list field that read as its form."""
        return [match for _number, _text, match in self.items.get(name, ()) if match]

    def lost_with(self):
        """The decision a decision is lost with, when the last item of its Lost is a 'with'."""
        items = self.items.get("Lost")
        if items and items[-1][2] and items[-1][2][1] == "with":
            return items[-1][2][2]
        return None


class Records:
    def __init__(self):
        self.errors = []
        self.records = {}  # ref -> Record
        self.resting = None  # record -> the decisions resting on it directly

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

    def check_layout(self, texts):
        if "constitution.md" not in texts:
            self.err("constitution.md", "missing")
        for path in sorted(texts):
            parts = path.split("/")
            if path == "constitution.md":
                continue
            if parts[0] in ("facts", "derivations") and len(parts) > 1 and path.endswith(".md"):
                for depth in range(2, len(parts)):
                    node = "/".join(parts[:depth]) + ".md"
                    if node not in texts:
                        self.err(path, f"its directory has no node file {node}")
                continue
            self.err(path, "not part of the records: constitution.md, facts/**.md, derivations/**.md")

    # ---- the constitution --------------------------------------------------

    def parse_constitution(self, path, text):
        current = None
        expected = 1
        prev = "blank"
        for number, line in enumerate(text.split("\n"), 1):
            loc = f"{path}:{number}"
            if line.startswith("## "):
                self.close(current)
                current = None
                prev = "head"
                match = ARTICLE.match(line)
                if not match:
                    self.err(loc, "an article is headed '## Article <n> (<id>). <title>'")
                    continue
                if int(match[1]) != expected:
                    self.err(loc, f"article {match[1]} where article {expected} comes next")
                expected = int(match[1]) + 1
                current = self.open("C", match[2], path, number)
                current.lines.append(line)
                continue
            if current is None:
                continue
            current.lines.append(line)
            if line.startswith("Replaces:"):
                match = REPLACES.match(line)
                if not match:
                    self.err(loc, "an article's 'Replaces' reads 'Replaces: C:<id>', naming the article it replaces")
                else:
                    if prev != "blank":
                        self.err(loc, "a field must be separated from the line before it by a blank line")
                    if "Replaces" in current.fields:
                        self.err(loc, f"a second 'Replaces' field in {current.ref}")
                    else:
                        current.fields["Replaces"] = (number, match[1])
            prev = "blank" if not line.strip() else "text"
        self.close(current)
        if expected == 1:
            self.err(path, "the constitution has no article")
        for record in self.records.values():
            if record.kind == "C" and not any(line.strip() and not line.startswith("Replaces:")
                                              for line in record.lines[1:]):
                self.err(f"{path}:{record.start}", f"{record.ref} has no text")

    # ---- decisions and facts -----------------------------------------------

    def parse_entries(self, path, text, kind):
        head = HEADS[kind]
        word = HEAD_WORDS[kind]
        current = None
        count = 0
        prev = "start"
        in_list = None
        fence = None  # the line that opened a data block not yet closed
        for number, line in enumerate(text.split("\n"), 1):
            loc = f"{path}:{number}"
            if fence is not None:
                current.lines.append(line)
                if line == FENCE:
                    fence = None
                    prev = "data"
                else:
                    current.data.append(line)
                continue
            match = head.match(line)
            if current is not None and not match:
                current.lines.append(line)
            if not line.strip():
                prev = "blank"
                in_list = None
                continue
            if match:
                if prev not in ("start", "blank"):
                    self.err(loc, "a record must be separated from the line before it by a blank line")
                self.close(current)
                current = self.open(kind, match[1], path, number)
                current.lines.append(line)
                if kind == "F":
                    current.assumed = bool(match[2])
                    current.statement = match[3]
                else:
                    current.question = match[2]
                count += 1
                prev = "head"
                in_list = None
                continue
            if line.startswith(word + " "):
                self.err(loc, f"a record opens {OPENINGS[kind]}, its id lowercase words joined by hyphens")
                prev = "other"
                continue
            if kind == "F" and line.startswith(FENCE):
                prev_was = prev
                prev = "other"
                in_list = None
                if current is None:
                    self.err(loc, "a data block before the first record")
                elif line != FENCE:
                    self.err(loc, "a data block is fenced by a line '```' alone, before it and after it")
                else:
                    if prev_was != "blank":
                        self.err(loc, "a data block must be separated from the line before it by a blank line")
                    if current.data is not None:
                        self.err(loc, f"a second data block in {current.ref}")
                    else:
                        current.data = []
                    fence = number
                continue
            field = FIELD.match(line)
            if field:
                name = field[1]
                value = line[len(name) + 1:].strip()
                prev_was = prev
                prev = "field"
                in_list = None
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
                if name in LISTS:
                    if value:
                        self.err(loc, f"'{name}:' stands alone, its items on the lines after it")
                    in_list = name
                    current.items.setdefault(name, [])
                elif not value:
                    self.err(loc, f"an empty '{name}' field")
                elif name == "Follows":
                    if FOLLOWS.match(value):
                        current.follows = (number, value)
                    else:
                        self.err(loc, "'Follows' names the one fact this one follows: 'Follows: F:<id>'")
                current.fields[name] = (number, value)
                continue
            if kind == "D" and line.startswith("- "):
                if not in_list or prev not in ("field", "item"):
                    self.err(loc, "a list item must follow its field's line or the item before it")
                else:
                    form, shape = ITEMS[in_list]
                    found = form.match(plain(line))
                    if not found:
                        self.err(loc, f"a {in_list} item reads {shape}")
                    current.items[in_list].append((number, line, found))
                prev = "item"
                continue
            self.err(loc, "a line outside the record format; each field is one line")
            prev = "other"
        if fence is not None:
            self.err(f"{path}:{fence}", "a data block that is never closed")
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
        if record.kind == "D":
            self.declare_inline(record)
            self.check_decision(record)
        if record.kind in ("D", "F"):
            self.check_words(record)

    def declare_inline(self, record):
        """The facts a decision declares in its reasons, each a record of its own."""
        for number, line in record.numbered():
            for start in re.finditer(r"\{F:", line):
                match = INLINE.match(line, start.start())
                if not match:
                    self.err(f"{record.path}:{number}", f"an inline fact reads {INLINE_FORMS}")
                    continue
                fact = self.open("F", match[1], record.path, number)
                fact.inline = True
                fact.lines = [match[0]]
                fact.assumed = bool(match[2])
                follows = INLINE_FOLLOWS.match(match[3])
                fact.statement = follows[1] if follows else match[3]
                fact.follows = (number, follows[2]) if follows else None

    def check_decision(self, record):
        where = f"{record.path}:{record.start}"
        if "Chosen" not in record.fields:
            self.err(where, f"{record.ref} has no 'Chosen'")
        else:
            number, value = record.fields["Chosen"]
            if not any(mark in f" {plain(value)} " for mark in (" because ", " so that ")):
                self.err(f"{record.path}:{number}", f"the Chosen of {record.ref} gives no 'because' or 'so that'")
            if not any(match[1] in ("C", "D") for match in REF.finditer(value)):
                self.err(f"{record.path}:{number}", f"the Chosen of {record.ref} cites no article and no decision; "
                                                    "a decision rests on at least one, cited there")
        for name in LISTS:
            if name in record.fields and not record.items.get(name):
                self.err(f"{record.path}:{record.fields[name][0]}", f"a '{name}:' list with no item")
        if "Rejected" not in record.fields and "Replaced" not in record.fields:
            self.err(where, f"{record.ref} has no 'Rejected' and no 'Replaced'; a decision added names another "
                            "option, and only one revised may have none left")
        for number, line in record.numbered():
            if DATE.search(INLINE.sub("", line)):
                self.err(f"{record.path}:{number}", "a date; a decision holds no date but in a fact it declares")

    def check_words(self, record):
        """No code, file or path in a decision or a fact."""
        for number, line in record.numbered():
            loc = f"{record.path}:{number}"
            for span in CODE_SPAN.finditer(line):
                self.err(loc, f"a code span, {span[0]}; a record names no code, files or paths")
            for token in line.split():
                if is_path(token):
                    self.err(loc, f"'{token}' names a path or a file; a record names none")

    # ---- the whole -------------------------------------------------------------

    def check_whole(self):
        for record in self.records.values():
            if record.inline:
                continue
            for number, line in record.numbered():
                for match in REF.finditer(line):
                    if match[0] not in self.records:
                        self.err(f"{record.path}:{number}", f"{match[0]} resolves to no {KINDS[match[1]]}")
        self.check_lost()
        self.check_cycles({ref: [p for p in self.premises(ref) if p.startswith("D:")] for ref in self.decisions()},
                          "the decisions' premises")
        follows = {}
        for ref, record in self.records.items():
            if record.kind == "F":
                follows[ref] = [record.follows[1]] if record.follows and record.follows[1] in self.records else []
        self.check_cycles(follows, "the facts' follows")
        self.check_facts_cited()
        self.check_in_force()

    def decisions(self):
        return sorted(ref for ref, record in self.records.items() if record.kind == "D")

    def premises(self, ref):
        """What a decision cites or declares in Chosen and Rejected that resolves."""
        record = self.records[ref]
        lines = [record.fields["Chosen"][1]] if "Chosen" in record.fields else []
        lines += [text for _number, text, _match in record.items.get("Rejected", ())]
        return sorted({match[0] for line in lines for match in REF.finditer(line) if match[0] in self.records})

    def check_lost(self):
        for ref in self.decisions():
            record = self.records[ref]
            for number, _text, match in record.items.get("Lost", ()):
                if not match or match[2] not in self.records:
                    continue
                choices = [replaced[1] for replaced in self.records[match[2]].listed("Replaced")]
                if match[3] not in choices:
                    self.err(f"{record.path}:{number}", f"{ref} is lost with '{match[3]}', which the Replaced of "
                                                        f"{match[2]} does not hold; a Lost item words the approach "
                                                        "as that Replaced does")

    def check_cycles(self, edges, what):
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
                    self.err(f"{record.path}:{record.start}", f"{what} form a cycle: " + " -> ".join(cycle))
                    continue
                if following not in state:
                    state[following] = "open"
                    path.append(following)
                    stack.append(iter(edges[following]))

    def check_facts_cited(self):
        cited = {match[0] for ref in self.decisions() for _number, line in self.records[ref].numbered()
                 for match in REF.finditer(line)}
        for ref, record in sorted(self.records.items()):
            if record.kind == "F" and not record.inline and ref not in cited:
                self.err(f"{record.path}:{record.start}",
                         f"{ref} is cited by no decision; a fact enters only when a decision rests on it")

    def check_in_force(self):
        replaced = {}
        for ref, record in sorted(self.records.items()):
            if record.kind == "C" and "Replaces" in record.fields:
                replaced.setdefault(record.fields["Replaces"][1], ref)
        for ref in self.decisions():
            record = self.records[ref]
            if record.lost_with():
                continue
            where = f"{record.path}:{record.start}"
            for premise in self.premises(ref):
                if premise in replaced:
                    self.err(where, f"{ref} is in force and rests on {premise}, which {replaced[premise]} replaces; "
                                    "a replaced article binds nothing")
                elif premise.startswith("D:") and self.records[premise].lost_with():
                    self.err(where, f"{ref} is in force and rests on {premise}, which is lost with "
                                    f"{self.records[premise].lost_with()}; a lost decision binds nothing")

    def dependents(self, ref):
        """The decisions that rest on a record, directly or through others: what a revision of it derives again."""
        if self.resting is None:
            self.resting = {}
            for other in self.decisions():
                for premise in self.premises(other):
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
        for ref, then in sorted(base.records.items()):
            now = self.records.get(ref)
            if now is None:
                self.err(f"{then.path}:{then.start}",
                         f"{ref} stood here at the base and is gone; the records only grow, and no id is removed")
            elif now.kind == "C" and now.text() != then.text():
                self.err(f"{now.path}:{now.start}", f"{ref} changed since the base; an article is never reworded")
            elif now.kind == "F" and now.declaration() != then.declaration():
                self.err(f"{now.path}:{now.start}", f"{ref} changed since the base; a fact is never reworded, "
                                                    "a later state or a correction is a new fact beside it")
            elif now.kind == "D":
                self.check_revision(now, then)

    def check_revision(self, now, then):
        """A decision against itself at the base: its question kept, its history grown, a changed choice replaced."""
        ref = now.ref
        if plain(now.question) != plain(then.question):
            self.err(f"{now.path}:{now.start}", f"the question of {ref} changed since the base; it never changes")
        for name in ("Replaced", "Broke", "Lost"):
            old = [plain(text) for _number, text, _match in then.items.get(name, ())]
            new = [plain(text) for _number, text, _match in now.items.get(name, ())]
            if new[:len(old)] != old:
                line = now.fields[name][0] if name in now.fields else now.start
                self.err(f"{now.path}:{line}", f"the {name} items of {ref} at the base changed, moved or went; "
                                               f"{name} only grows, at its end")
        replaced_before = len(then.items.get("Replaced", ()))
        revised = len(now.items.get("Replaced", ())) > replaced_before
        was = then.chosen()
        if was and plain(now.fields.get("Chosen", (0, ""))[1]) != plain(then.fields["Chosen"][1]):
            kept = [(match[1], match[2], match[3].rstrip("."))
                    for _number, _text, match in now.items.get("Replaced", [])[replaced_before:] if match]
            if was not in kept:
                line = now.fields["Chosen"][0] if "Chosen" in now.fields else now.start
                self.err(f"{now.path}:{line}", f"the Chosen of {ref} changed since the base, but no new Replaced item keeps "
                                               f"the choice it held, '{was[0]}', with the reasons it was chosen on")
        options = {match[1]: plain(text) for _number, text, match in now.items.get("Rejected", ()) if match}
        taken = now.chosen()
        line = now.fields["Rejected"][0] if "Rejected" in now.fields else now.start
        for _number, text, match in then.items.get("Rejected", ()):
            if not match:
                continue
            option = match[1]
            if option in options:
                if options[option] != plain(text) and not revised:
                    self.err(f"{now.path}:{line}", f"the rejected option '{option}' of {ref} has other reasons than at "
                                                   "the base, with no new Replaced item; they change only when the "
                                                   "decision is revised")
            elif not (taken and taken[0] == option):
                self.err(f"{now.path}:{line}", f"the rejected option '{option}' of {ref} at the base is gone; an option "
                                               "stays in Rejected or is taken up as Chosen")

    # ---- reporting -------------------------------------------------------------

    def metrics(self):
        records = self.records.values()
        return {
            "articles": sum(r.kind == "C" for r in records),
            "facts": sum(r.kind == "F" for r in records),
            "decisions": sum(r.kind == "D" for r in records),
            "rejected": sum(len(r.items.get("Rejected", ())) for r in records),
            "assumed": sum(r.kind == "F" and r.assumed for r in records),
        }

    def report(self, base_metrics):
        counts = []
        for name, value in self.metrics().items():
            if base_metrics is None:
                counts.append(f"{name}: {value}")
            else:
                counts.append(f"{name}: {value} (base {base_metrics[name]}, {value - base_metrics[name]:+d})")
        print("  ".join(counts))


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
                        help="with --base: the records only grew since it, nothing removed or reworded")
    parser.add_argument("--ascii", action="store_true", help="the project keeps its records in English")
    parser.add_argument("--dependents", nargs="+", metavar="REF",
                        help="list every decision resting on each record named, directly or through others")
    args = parser.parse_args()
    records = Records()
    base_metrics = None
    if not os.path.isdir(args.root):
        records.err(args.root, "no such directory")
    else:
        records.load(worktree(args.root), args.ascii)
        records.check_whole()
        for ref in args.dependents or []:
            if ref not in records.records:
                records.err("--dependents", f"{ref} is no record")
                continue
            resting = records.dependents(ref)
            print(f"dependents of {ref}: {len(resting)}")
            for other in resting:
                record = records.records[other]
                print(f"  {other} ({record.path}:{record.start})")
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
