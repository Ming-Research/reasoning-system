# Reasoning rules: deriving and changing the records

For agents that derive decisions and change the records. Read `reading.md` first; this adds what an editor does.

## 1. Deriving

- Derive from the constitution, the facts and earlier derivations, by first principles. Name the premises, and conclude
  only what they give.
- Where the premises leave several workable approaches, the trade-off is put to the owner. The owner's ruling keeps one
  approach and rejects the others, with the reasoning; that reasoning is what links the new derivation to what it rests
  on.
- An earlier derivation is a premise, not a wall. When a question is better answered by changing an earlier
  derivation, revise it rather than work around it, provided the revision is better by the same axioms.
- A fact enters the records only when a derivation rests on it, as given. A value the project chose or estimated
  rather than established is marked `Assumed`, with what would settle or overturn it.
- A derivation whose premise has not been found yet is kept, marked `Open` with what is missing and where it was asked,
  until the premise is found; it is not left out, and words do not stand in for the premise.
- Record only decisions that shape later work. Write a shared rule once, on the common ancestor. The owner adjusts the
  threshold when the records grow too fine or too thin.

## 2. Changing the records

- A derivation changes only by a revision the owner rules. Find, through `Rests on`, every record resting on what you
  change, and examine each again: it still holds, or it is revised in the same change.
- When a revision replaces a decision, the replaced choice becomes a `Rejected` item of the derivation that replaces
  it, its reason citing the premise it lost on, so that a change to that premise reopens it.
- A fact that the project changes reopens every derivation resting on it.
- A change to the constitution re-derives every derivation resting on the articles it changed.
- Log every revision. A merged log entry is never changed.
- Run the system's check (section 3) after every change.

## 3. How the records are stored

The records are plain text in the language and character set the project sets, in a format a check can read. Each
field is one line, with a blank line between fields; list items follow straight after their field.

**The check.** `check.py` in the system's repository checks the format, that every reference resolves and is listed in
its derivation's `Rests on`, that the derivations form no cycle, that no removed id is used again, that every fact is
cited by a derivation, and that every derivation not marked `Open` reaches an article through what it rests on. It
lists what is open or assumed, and the derivations resting on each open one:

```
python3 -B <system>/check.py --root reasoning [--ascii]
```

With `--base <revision> --ready` it also checks, against the revision before the change, that every record added,
changed or removed is named in a new log entry with its verb, and that no merged entry changed. A change reaches the
main line only when that passes. `--ascii` is for a project whose records are English only.

**Layout.**

```
reasoning/
  constitution.md   the axioms
  facts/            the facts the derivations rest on, a tree by subject
  derivations/      the decisions, a tree by concept
  log.md            every revision, newest first
```

Each tree has a node file `<subject>.md` at its top, and the subjects under a node in a directory of the same name
beside it, `<subject>/`, to any depth.

**Ids.** Every article, fact and derivation has an id: lowercase words joined by hyphens, unique in its kind, never
reused, and kept when its record moves or is reworded. Every reference must resolve, and the derivations' references
form no cycle.

**The constitution.** Each article is headed `## Article <n> (<id>). <title>`, numbered from 1.

**A fact.** A node file holds one or more facts of its subject.

```
Fact <id>: <what is taken as given>.

Assumed: <what would settle or overturn it>
```

A fact cites no record. `Assumed` is given only for a value the project has not established.

**A derivation.** A node file is named after the concept it governs and holds one or more derivations of it.

```
Decision <id>: <the choice>, instead of <the approach not chosen>, because <the derivation>.

Rests on: <every reference the derivation cites, comma-separated>

Open: <the premise still missing, and where it was asked>

Rejected:
- <approach>: rejected because <how it differs from the choice, not the choice turned around>
```

A reason is required, after `because`, or after `so that` when it is the purpose the choice serves; so is `Rests on`.
Only an `Open` derivation whose reason or premises are wholly missing may give neither. `instead of` is given when one
approach stands against the choice. `Open` and `Rejected` are given when there is something to give. A derivation holds no dates, history or progress; how it came to be is in the
log.

**A log entry.**

```
## <date> <title>

Changed: <reference> <added, changed or removed>, ...

Why: <the derivation>

Re-examined: <each record resting on what changed, and whether it holds or was revised>

Ruling: <the owner's ruling it carries out>
```
