#!/usr/bin/env python3
"""The check of a project's reasoning records: the form of every article,
decision and fact, that a decision's options name one another and its moves in
Replaced lead to its Chosen, that every reference resolves, that a decision is
lost only with what its Given names, that the decisions' premises and the
facts' follows form no cycle, and that no decision in force rests on a replaced
article, a lost decision or an option no longer chosen; and, against a base
revision with --ready, that the records only grew: no id removed, no article,
fact, question, Given or option reworded, a decision's history only added to,
and a changed choice or options kept as replaced. Its messages say what it
checks."""
import argparse
import os
import re
import subprocess
import sys

ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
REF = re.compile(rf"(?<![A-Za-z0-9])([CFD]):({ID})(?:/({ID}))?(?![A-Za-z0-9])")
ARTICLE = re.compile(rf"^## Article (\d+) \(({ID})\)\. \S")
REPLACES = re.compile(rf"^Replaces: (C:{ID})$")
HEADS = {"F": re.compile(rf"^Fact ({ID})( \(assumed\))?: (\S.*)$"), "D": re.compile(rf"^Decision ({ID}): (\S.*)$")}
HEAD_WORDS = {"F": "Fact", "D": "Decision"}
OPENINGS = {"F": "'Fact <id>: <text>' or 'Fact <id> (assumed): <text>'", "D": "'Decision <id>: <question>'"}
FIELD = re.compile(r"^([A-Z][a-z]*(?: [a-z]+)*):(?: |$)")
FIELDS = {"F": ("Follows",), "D": ("Given", "Chosen", "Options", "Replaced", "Broke", "Lost")}
LISTS = ("Options", "Replaced", "Broke", "Lost")
ITEMS = {
    "Options": (re.compile(rf"^- ({ID}): (\S.*)$"),
                "'- <option-id>: <what it is>', its id lowercase words joined by hyphens"),
    "Replaced": (re.compile(rf"^- ({ID}) -> ({ID}): (\S.*); replaced because \S"),
                 "'- <option-id> -> <option-id>: <the Chosen it replaces, whole>; replaced because <the base that "
                 "changed>'"),
    "Broke": (re.compile(rf"^- (\S.*?): breaks on ([CFD]:{ID})$"), "'- <revision>: breaks on <reference>'"),
    "Lost": (re.compile(rf"^- (with|back with) (D:{ID}/{ID}|[CF]:{ID})$"),
             "'- with <reference>' or '- back with <reference>', naming D:<id>/<option-id>, C:<id> or F:<id>"),
}
OVER = re.compile(rf"^  \+ over ({ID}(?:, {ID})*): \S")
OVER_FORM = "'  + over <option-id>[, <option-id>...]: <what it does better than them>', indented two spaces"
CHOSEN = re.compile(rf"^({ID}), (because|so that) (\S.*)$")
CHOSEN_FORM = "'<option-id>, because|so that <the weighing>'"
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


def record_of(match):
    """The record a reference names: for an option, the decision that names it."""
    return f"{match[1]}:{match[2]}"


def choice(text):
    """A Chosen, or the Chosen a Replaced item keeps, as (its option id, 'because' or 'so that', the weighing)."""
    match = CHOSEN.match(plain(text))
    return (match[1], match[2], match[3]) if match else None


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
        self.over = {}  # an option's line number -> its '+' lines, [(line number, text, the match of its form or None)]
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

    def value(self, name):
        """A one-line field's value, empty when the field is not given."""
        return self.fields[name][1] if name in self.fields else ""

    def chosen(self):
        """A decision's choice as (its option id, 'because' or 'so that', the weighing)."""
        return choice(self.fields["Chosen"][1]) if "Chosen" in self.fields else None

    def listed(self, name):
        """The matches of the items of a list field that read as its form."""
        return [match for _number, _text, match in self.items.get(name, ()) if match]

    def options(self):
        """A decision's options that read as their form, as {option id: what it is}."""
        return {match[1]: match[2] for match in self.listed("Options")}

    def option_ids(self):
        """The ids a reference D:<id>/<option-id> may name: those in Options and those in Replaced."""
        return set(self.options()) | {match[side] for match in self.listed("Replaced") for side in (1, 2)}

    def weighed(self):
        """The text of each Options item and each '+' line, where a decision weighs its options."""
        texts = [text for _number, text, _match in self.items.get("Options", ())]
        return texts + [text for lines in self.over.values() for _number, text, _match in lines]

    def lost_with(self):
        """What a decision is lost with, when the last item of its Lost is a 'with'."""
        items = self.items.get("Lost")
        if items and items[-1][2] and items[-1][2][1] == "with":
            return items[-1][2][2]
        return None

    def lost_unread(self):
        """Whether the last item of a decision's Lost does not read as its form, so that it is not known to be lost."""
        items = self.items.get("Lost")
        return bool(items) and items[-1][2] is None


class Records:
    def __init__(self):
        self.errors = []
        self.records = {}  # ref -> Record
        self.doubles = []  # records whose id another record of the kind already has
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
                    number_only = re.match(r"^## Article (\d+)\b", line)
                    if number_only:
                        expected = int(number_only[1]) + 1
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
        skipping = False  # after a head that does not read as one, until the next
        for number, line in enumerate(text.split("\n"), 1):
            loc = f"{path}:{number}"
            if skipping and not head.match(line):
                continue
            skipping = False
            if fence is not None:
                current.lines.append(line)
                if line == FENCE:
                    fence = None
                    prev = "data"
                else:
                    current.data.append(line)
                continue
            match = head.match(line)
            if current is not None and not match and not line.startswith(word + " "):
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
                self.err(loc, f"a record opens {OPENINGS[kind]}, its id lowercase words joined by hyphens; its lines "
                              "are not read")
                self.close(current)
                current = None
                skipping = True
                count += 1
                prev = "blank"
                in_list = None
                continue
            if kind == "F" and line.startswith(FENCE):
                prev_was = prev
                prev = "other"
                in_list = None
                if current is None:
                    self.err(loc, "a data block before the first record")
                else:
                    if line != FENCE:
                        self.err(loc, "a data block is fenced by a line '```' alone, before it and after it")
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
            if kind == "D" and line.lstrip().startswith("+"):
                options = current.items.get("Options") if current is not None else None
                if in_list != "Options" or prev not in ("item", "over") or not options:
                    self.err(loc, "a '+' line follows straight after its option or the '+' line before it")
                else:
                    found = OVER.match(plain(line))
                    if not found:
                        self.err(loc, f"a '+' line reads {OVER_FORM}")
                    current.over.setdefault(options[-1][0], []).append((number, line, found))
                prev = "over"
                continue
            if kind == "D" and line.startswith("- "):
                if not in_list or prev not in ("field", "item", "over"):
                    self.err(loc, "a list item must follow its field's line or the item before it")
                else:
                    form, shape = ITEMS[in_list]
                    found = form.match(plain(line))
                    if not found:
                        self.err(loc, f"{'an' if in_list[0] in 'AEIOU' else 'a'} {in_list} item reads {shape}")
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
            self.doubles.append(record)
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
        ref = record.ref
        where = f"{record.path}:{record.start}"
        for name in ("Chosen", "Options"):
            if name not in record.fields:
                self.err(where, f"{ref} has no '{name}'")
        for name in LISTS:
            if name in record.fields and not record.items.get(name):
                self.err(f"{record.path}:{record.fields[name][0]}", f"'{name}:' with no item under it")
        options = self.check_options(record)
        taken = record.chosen()
        if "Chosen" in record.fields:
            where = f"{record.path}:{record.fields['Chosen'][0]}"
            if taken is None:
                self.err(where, f"the Chosen of {ref} reads {CHOSEN_FORM}")
            elif options and taken[0] not in options:
                self.err(where, f"the Chosen of {ref} takes '{taken[0]}', which is no option in its Options")
        if not any(match[1] in ("C", "D") for text in [record.value("Chosen")] + record.weighed()
                   for match in REF.finditer(text)):
            self.err(where, f"{ref} cites no article and no decision in its Chosen or its Options; a decision rests on "
                            "at least one, cited there")
        self.check_replaced(record, taken)
        for number, line in record.numbered():
            if DATE.search(INLINE.sub("", line)):
                self.err(f"{record.path}:{number}", "a date; a decision holds no date but in a fact it declares")

    def check_options(self, record):
        """Each option named once; with two options or more, each one's '+' lines name every other; with one, none,
        and the decision is a revision. Returns the option ids."""
        ref = record.ref
        options = []
        for number, _text, match in record.items.get("Options", ()):
            if not match:
                continue
            if match[1] in options:
                self.err(f"{record.path}:{number}", f"the option '{match[1]}' of {ref} is listed twice; an option id "
                                                    "is unique in its decision")
            else:
                options.append(match[1])
        for number, _text, match in record.items.get("Options", ()):
            if not match:
                continue
            option = match[1]
            lines = record.over.get(number, ())
            if len(record.items.get("Options", ())) == 1:
                for line, _text, _found in lines:
                    self.err(f"{record.path}:{line}", f"a '+' line under the one option of {ref}; a decision left with "
                                                      "one option gives it none")
                continue
            named = set()
            for line, _text, found in lines:
                if not found:
                    continue
                for other in found[1].split(", "):
                    if other == option:
                        self.err(f"{record.path}:{line}", f"a '+' line of the option '{option}' of {ref} names the "
                                                          "option itself; it names others of the decision")
                    elif other not in options:
                        self.err(f"{record.path}:{line}", f"a '+' line of the option '{option}' of {ref} names "
                                                          f"'{other}', which is no option in its Options")
                    named.add(other)
            missing = ", ".join(f"'{other}'" for other in options if other != option and other not in named)
            if missing:
                self.err(f"{record.path}:{number}", f"the '+' lines of the option '{option}' of {ref} do not name "
                                                    f"{missing}; with two options or more, each option's '+' lines "
                                                    "name every other")
        if len(record.items.get("Options", ())) == 1 and not record.items.get("Replaced"):
            self.err(f"{record.path}:{record.start}", f"{ref} has one option and no 'Replaced'; only a revision leaves "
                                                      "a decision with one, and a decision added weighs two or more")
        return options

    def check_replaced(self, record, taken):
        """Each Replaced item keeps whole the Chosen of the option it moves from; each moves on from where the one
        before it moved to, and the last moves to the Chosen."""
        ref = record.ref
        before = None  # the option the item before moved to
        where = None
        for number, _text, match in record.items.get("Replaced", ()):
            if not match:
                before = None
                continue
            where = f"{record.path}:{number}"
            kept = choice(match[3])
            if kept is None:
                self.err(where, f"the Chosen a Replaced item of {ref} keeps reads {CHOSEN_FORM}")
            elif kept[0] != match[1]:
                self.err(where, f"the Chosen a Replaced item of {ref} keeps takes '{kept[0]}', not '{match[1]}', the "
                                "option it moves from")
            if before is not None and match[1] != before:
                self.err(where, f"a Replaced item of {ref} moves from '{match[1]}', but the one before it moved to "
                                f"'{before}'; each moves on from where the one before moved to")
            before = match[2]
        if before is not None and taken and before != taken[0]:
            self.err(where, f"the last Replaced item of {ref} moves to '{before}', but its Chosen takes '{taken[0]}'; "
                            "the last move is to the Chosen")

    def check_words(self, record):
        """No code, file or path in a decision or a fact."""
        for number, line in record.numbered():
            loc = f"{record.path}:{number}"
            for span in CODE_SPAN.finditer(line):
                self.err(loc, f"a code span, {span[0]}; a record names no code, files or paths")
            for token in CODE_SPAN.sub(" ", line).split():
                if is_path(token):
                    self.err(loc, f"'{token}' names a path or a file; a record names none")

    # ---- the whole -------------------------------------------------------------

    def check_whole(self):
        for record in list(self.records.values()) + self.doubles:
            if record.inline:
                continue
            for number, line in record.numbered():
                for match in REF.finditer(line):
                    self.check_reference(f"{record.path}:{number}", match)
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

    def check_reference(self, where, match):
        """A reference resolves to its record, and D:<id>/<option-id> to an option that decision names."""
        target = self.records.get(record_of(match))
        if target is None:
            self.err(where, f"{match[0]} resolves to no {KINDS[match[1]]}")
        elif match[3] and match[1] != "D":
            self.err(where, f"{match[0]} resolves to no {KINDS[match[1]]}; only a decision names options")
        elif match[3] and match[3] not in target.option_ids():
            self.err(where, f"{match[0]} resolves to no option of {target.ref}, in its Options or its Replaced")

    def decisions(self):
        return sorted(ref for ref, record in self.records.items() if record.kind == "D")

    def premises(self, ref):
        """What a decision cites or declares in Given, Chosen and Options that resolves, an option standing for the
        decision that names it."""
        record = self.records[ref]
        texts = [record.value("Given"), record.value("Chosen")] + record.weighed()
        return sorted({record_of(match) for text in texts for match in REF.finditer(text)
                       if record_of(match) in self.records})

    def check_lost(self):
        """A decision is lost only with what its Given names, or with what a decision its Given names is lost with."""
        for ref in self.decisions():
            record = self.records[ref]
            given = list(REF.finditer(record.value("Given")))
            named = {match[0] for match in given}
            for match in given:
                if match[1] == "D" and record_of(match) in self.records:
                    named |= {lost[2] for lost in self.records[record_of(match)].listed("Lost")}
            for number, _text, match in record.items.get("Lost", ()):
                if match and match[2] not in named:
                    self.err(f"{record.path}:{number}", f"{ref} is lost with {match[2]}, which its Given does not name, "
                                                        "nor the Lost of a decision its Given names")

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
        cited = {record_of(match) for ref in self.decisions() for _number, line in self.records[ref].numbered()
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
            if record.lost_with() or record.lost_unread():
                continue
            where = f"{record.path}:{record.start}"
            for premise in self.premises(ref):
                if premise in replaced:
                    self.err(where, f"{ref} is in force and rests on {premise}, which {replaced[premise]} replaces; "
                                    "a replaced article binds nothing")
                elif premise.startswith("D:") and self.records[premise].lost_with():
                    self.err(where, f"{ref} is in force and rests on {premise}, which is lost with "
                                    f"{self.records[premise].lost_with()}; a lost decision binds nothing")
            for match in REF.finditer(record.value("Given")):
                if match[1] != "D" or not match[3] or record_of(match) not in self.records:
                    continue
                taken = self.records[record_of(match)].chosen()
                if taken and taken[0] != match[3]:
                    self.err(where, f"{ref} is in force and its Given names {match[0]}, but {record_of(match)} takes "
                                    f"'{taken[0]}'; a decision whose question arises under an option no longer chosen "
                                    "is lost with it")

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
        # An article replaced since the base, mapped to the article replacing it, for a decision citing it instead.
        recited = {record.fields["Replaces"][1]: ref for ref, record in sorted(self.records.items())
                   if record.kind == "C" and "Replaces" in record.fields and ref not in base.records}
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
                self.check_revision(now, then, recited)
        for ref, now in sorted(self.records.items()):
            if now.kind == "D" and ref not in base.records and len(now.options()) == 1:
                self.err(f"{now.path}:{now.start}", f"{ref} is added with one option; a decision added weighs two or "
                                                    "more")

    def check_revision(self, now, then, recited):
        """A decision against itself at the base: its question and Given kept, its history grown, a changed Chosen
        kept whole in a new Replaced item, what each option is kept, and its options changed only in a revision."""
        ref = now.ref

        def recite(text):
            """Text with each article replaced since the base read as the article now replacing it."""
            def latest(ref):
                seen = set()
                while ref in recited and ref not in seen:
                    seen.add(ref)
                    ref = recited[ref]
                return ref
            return REF.sub(lambda match: latest(match[0]), plain(text)).rstrip(".")

        def weighed(record):
            """The Options as compared with a base: each option's '+' lines, in any order, by its id."""
            found = {}
            for number, text, match in record.items.get("Options", ()):
                key = match[1] if match else text
                found[key] = sorted(recite(over) for _line, over, _match in record.over.get(number, ()))
            return found

        if plain(now.question) != plain(then.question):
            self.err(f"{now.path}:{now.start}", f"the question of {ref} changed since the base; it never changes")
        if plain(now.value("Given")) != plain(then.value("Given")):
            line = now.fields["Given"][0] if "Given" in now.fields else now.start
            self.err(f"{now.path}:{line}", f"the Given of {ref} changed since the base; it never changes")
        for name in ("Replaced", "Broke", "Lost"):
            old = [plain(text) for _number, text, _match in then.items.get(name, ())]
            new = [plain(text) for _number, text, _match in now.items.get(name, ())]
            if new[:len(old)] != old:
                line = now.fields[name][0] if name in now.fields else now.start
                self.err(f"{now.path}:{line}", f"the {name} items of {ref} at the base changed, moved or went; "
                                               f"{name} only grows, at its end")
        revised = now.items.get("Replaced", [])[len(then.items.get("Replaced", ())):]
        was = then.value("Chosen")
        line = now.fields["Chosen"][0] if "Chosen" in now.fields else now.start
        if was and revised:
            first = revised[0][2]
            if first and recite(first[3]) != recite(was):
                self.err(f"{now.path}:{revised[0][0]}", f"the first new Replaced item of {ref} keeps a Chosen other "
                                                        "than the one it held at the base; it keeps that one whole")
        elif was and recite(now.value("Chosen")) != recite(was):
            self.err(f"{now.path}:{line}", f"the Chosen of {ref} changed since the base, but no new Replaced item "
                                           "keeps whole the one it held there; only citing an article in place of the "
                                           "one it replaced needs none")
        whats = then.options()
        for number, _text, match in now.items.get("Options", ()):
            if match and match[1] in whats and recite(match[2]) != recite(whats[match[1]]):
                self.err(f"{now.path}:{number}", f"what the option '{match[1]}' of {ref} is changed since the base; "
                                                 "what an option is never changes")
        if not revised and weighed(now) != weighed(then):
            line = now.fields["Options"][0] if "Options" in now.fields else now.start
            self.err(f"{now.path}:{line}", f"the Options of {ref} changed since the base with no new Replaced item; "
                                           "an option or a '+' line is added, changed or removed only in a revision")

    # ---- reporting -------------------------------------------------------------

    def metrics(self):
        records = self.records.values()
        return {
            "articles": sum(r.kind == "C" for r in records),
            "facts": sum(r.kind == "F" for r in records),
            "decisions": sum(r.kind == "D" for r in records),
            "options": sum(len(r.items.get("Options", ())) for r in records),
            "assumed": sum(r.kind == "F" and r.assumed for r in records),
        }

    def report(self, base_metrics):
        """The counts, against the base where there is one, and each assumed fact."""
        counts = []
        for name, value in self.metrics().items():
            if base_metrics is None:
                counts.append(f"{name}: {value}")
            else:
                counts.append(f"{name}: {value} (base {base_metrics[name]}, {value - base_metrics[name]:+d})")
        lines = ["  ".join(counts)]
        for record in sorted(self.records.values(), key=lambda r: (r.path, r.start)):
            if record.kind == "F" and record.assumed:
                lines.append(f"assumed {record.ref} ({record.path}:{record.start}): {record.statement}")
        return lines


def check_files(files, base=None, ready=False, ascii_only=False, dependents=()):
    """The check of the records in files, which maps each path under the records' root to its bytes; with base, the
    records at the revision before the change, they are counted against it and, with ready, checked to have only grown
    since it, unless the base does not pass the check as it stands, as when its records were kept in an earlier form:
    then the records are checked as they are, and a line says so. Returns the errors, the lines listed, and the report
    given when there is no error."""
    records = Records()
    records.load(files, ascii_only)
    records.check_whole()
    listed = []
    for ref in dependents:
        ref = ref.split("/")[0]
        if ref not in records.records:
            records.err("--dependents", f"{ref} is no record")
            continue
        resting = records.dependents(ref)
        listed.append(f"dependents of {ref}: {len(resting)}")
        listed += [f"  {other} ({records.records[other].path}:{records.records[other].start})" for other in resting]
    base_metrics = None
    if base is not None:
        then = Records()
        then.load(base)
        then.check_whole()
        if then.errors:
            listed.append(f"the base does not pass the check as it stands ({len(then.errors)} error(s)), as when its "
                          "records were kept in an earlier form: the records are checked as they are, not against it")
        else:
            base_metrics = then.metrics()
            if ready:
                records.check_ready(then)
    return records.errors, listed, records.report(base_metrics)


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
    errors = []
    report = []
    if not os.path.isdir(args.root):
        errors.append(f"{args.root}: no such directory")
    else:
        base = None
        if args.ready and args.base is None:
            errors.append("--ready: needs --base")
        if args.base is not None:
            if not base_exists(args.root, args.base):
                errors.append(f"--base: {args.base!r} resolves to no commit")
            else:
                base = files_at(args.root, args.base)
        found, listed, report = check_files(worktree(args.root), base, args.ready, args.ascii, args.dependents or ())
        errors = found + errors
        for line in listed:
            print(line)
    if errors:
        for error in errors:
            print("error: " + error, file=sys.stderr)
        print(f"reasoning check: {len(errors)} error(s)", file=sys.stderr)
        return 1
    for line in report:
        print(line)
    print("reasoning check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
