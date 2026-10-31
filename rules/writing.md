# Reasoning rules: deriving and changing the records

For agents that derive decisions and change the records. Read `reading.md` first; this adds what an editor does.

## 1. Deriving

- Derive from the constitution, the facts and earlier derivations, by first principles. Name the premises, and conclude
  only what they give. Say which kind of ground a reason is: a derivation; an observation under its conditions; or a
  principle, which shows a choice fits but not that it is the only one.
- Where the premises leave several workable approaches, the trade-off is put to the owner as a card (section 3). The
  owner's ruling keeps one approach and rejects the others, with the reasoning; that reasoning is what links the new
  derivation to what it rests on.
- An earlier derivation is a premise, not a wall. When a question is better answered by changing an earlier
  derivation, revise it rather than work around it, provided the revision is better by the same axioms.
- A fact enters the records only when a derivation rests on it, as given.
- Record only decisions that shape later work. Write a shared rule once, on the common ancestor. The owner adjusts the
  threshold when the records grow too fine or too thin.

## 2. Changing the records

- A derivation changes only by a revision, put to the owner by a card. Find, through `Rests on`, every record resting
  on what you change, and examine each again: it still holds, or it is revised in the same change.
- A fact that the project changes reopens every derivation resting on it.
- A change to the constitution re-derives every derivation resting on the articles it changed.
- Log every revision.

## 3. Cards

A card is a revision put to the owner. It stands in the design where the design reaches its question, so that the text
before it gives the background, where the design stands and why this is asked; the text around it does not repeat it.
It has:

- one question saying what it decides, in plain words, with no internal names;
- at least three workable options, each with what it does, its cost and its risks; never one approach against not
  doing it, so that whether to do something becomes how much of it to do;
- the recommended option;
- its confidence from 1 to 5, why, and what would overturn it; and where it departs from an earlier ruling;
- the derivations it adds or changes.

The card and its revision say the same thing in different words. A ruled card is never changed: a question that
changes comes back under the same key, saying what changed; a question no longer asked is withdrawn, saying why.

## 4. How the records are stored

The records are plain text in the language and character set the project sets, in a format a check can read; a record
that breaks the format is refused. Each field is one line, with a blank line between fields; list items follow straight
after their field.

**Layout.**

```
reasoning/
  constitution.md   the axioms
  facts/            the facts the derivations rest on, one file per subject
  derivations/      a tree by concept: a root node derivations/<concept>.md, its children in derivations/<concept>/
  log.md            every revision, newest first
```

**Ids.** Every article, fact and derivation has an id: lowercase words joined by hyphens, unique in its kind, never
reused, and kept when its record moves or is reworded. Every reference must resolve, and the derivations' references
form no cycle.

**The constitution.** Each article is headed `## Article <n> (<id>). <title>`.

**A fact.**

```
Fact <id>: <what is taken as given>.
```

**A derivation.** A node file is named after the concept it governs and holds one or more derivations of it.

```
Decision <id>: <the choice>, instead of <the approach not chosen>, because <the derivation>.
Rests on: <references>
Holds while: <the conditions under which it holds>
Rejected:
- <approach>: rejected because <how it differs from the choice, not the choice turned around>
```

`Holds while` and `Rejected` are given when there is something to give. A derivation holds no dates, history or
progress; how it came to be is in the log.

**A log entry.**

```
## <date> <title>
Changed: <references, each added, changed or removed>
Why: <the derivation>
Re-examined: <each record resting on what changed, and whether it holds or was revised>
Card: <the card that put it to the owner>
```
