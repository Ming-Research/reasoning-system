# Reasoning rules: writing

For agents that derive decisions and add them to the records or revise them.

## 1. Deriving a decision

- A decision's question is its head. Its reasons cite each premise where the reasoning bears on it: at least one article
  or earlier decision, which give what matters in the weighing, and the facts it needs. Conclude only what the premises
  give.
- Record a decision only for a real choice. Why an option loses is never the choice turned round. An option's gains rest
  on facts: an approach researched in earnest has them in what its research found, and is weighed and written, so that
  it is not researched again; one only glanced at has none to weigh, and is not written.
- Write the choice, the reasons that decide it and the qualifications it needs, in as few words as keep its meaning. A
  reason may be the purpose the choice serves.
- A record names no paths, no files, modules, functions, types, tables or fields, no ids or numbers of steps or states:
  a step is named by what it does. No record only restates an interface or an implementation, since that holds no
  choice. A number the project sets is configuration and is not written, unless the number itself was a real choice.
- A record is read long after it is written and is never reworded, so no word in a decision or a fact takes its meaning
  from a conversation, card or work, or from when it was written, a meaning lost once they are gone: no "until now" or
  "option B", no number that a work, a task or a card goes by.
- A fact is declared where it is first stated, and says when it holds, where that matters.
- Record the reasons the owner gives for a choice as facts, citing the article or decision that makes them matter.
- A decision whose premises are not found is not recorded: ask the owner for them.
- How its maintainers keep the project's repository, and the machines they use, is how they work on it, not something
  the project does, so it is no decision of the project.

## 2. Adding and revising

No article is reworded once recorded, and no option of a decision has what it is reworded; an option leaves a decision
only when a revision finds it no longer one. Each addition, and each revision with every decision it changes, since the
records stay coherent only with all of them changed, goes to the owner as one card, and is recorded once accepted.

- **An addition** answers a question no decision answers, with a real choice. It takes the articles and decisions as
  they stand, changes none of them, and brings the facts its reasons need.
- **A revision** names the base that changed and derives the question again on it: the options are weighed again in
  place, the `Chosen` replaced is kept whole in `Replaced` with the base it lost on, the choice replaced stays an option
  while it still trades off, and an option the new base leaves with no gain leaves the decision. A change that keeps the
  choice, to its weighing, its qualifications or its options, is a revision too, its `Replaced` item moving from the
  option to itself. When the new base leaves a single option, the decision takes it, and its card shows the derivation
  rather than a choice. Dropping something the project does is a revision of the decision it stands under, to not doing
  it.
- **Deriving again.** When an article is replaced or a decision revised, derive again every decision resting on it: it
  stands, citing the new article in place of the old where one replaced it, nothing else in it changing; or it is
  revised in the same card; or, when its `Given` names what was replaced, it is lost with it. Derive again the decisions
  resting on each one revised; those whose `Given` names one lost, or an option of it, are lost with it, others resting
  on it are derived again, and those resting on one that stood are left as they are. A new fact is weighed against the
  decisions it bears on, found by their questions and by the decisions resting on the fact it follows, and recorded only
  when it changes one.
- **What is kept.** A decision lost with an approach stays as it was, marked as lost with it, and so does every decision
  lost through it. Taking the approach up again brings them back to be derived again, each marked as back with it. A
  revision explored and found to break on a record not resting on the decision it revises is kept with that decision,
  naming the record, and recorded with the card that explored it. Attempts made while coding are not kept: they try ways
  of building what a decision says, not answers to its question.
- **Follows and replaces.** A new fact names the fact it follows, and an article the owner adds names the article it
  replaces.

## 3. Format

The records are plain text in the language and character set the project sets. Each field is one line, with a blank line
between fields; list items follow straight after their field, and an option's `+` lines straight after it, indented two
spaces, one line each. A decision holds no dates but in the facts it declares, and no account of how it came to be.

The decisions, and the facts in `facts/`, are each a tree, by concept and by subject. A tree has a node file
`<subject>.md` at its top, and the subjects under it in a directory of the same name beside it, `<subject>/`, to any
depth. Every article, fact and decision has an id: lowercase words joined by hyphens, unique in its kind, never reused,
and kept when its record moves.

**An article.** Articles are numbered from 1 in the order they were added.

```
## Article <n> (<id>). <title>

<text>

Replaces: C:<id>
```

**A decision.** A node file is named after the concept it governs and holds the decisions on it.

```
Decision <id>: <the question it answers>

Given: <what the question itself arises under: decisions, options of them, articles or facts>

Chosen: <option-id>, because <the weighing: why each other option loses, with the qualifications the choice needs>

Options:
- <option-id>: <what it is>
  + over <option-id>, ...: <what it does better than them>

Replaced:
- <option-id> -> <option-id>: <the Chosen it replaces, whole>; replaced because <the base that changed>

Broke:
- <a revision explored>: breaks on <the record>

Lost:
- with <what the question arose under: D:<id>/<option-id>, C:<id> or F:<id>>
- back with <the same>
```

An option id is lowercase words joined by hyphens naming the approach. With two options or more, each names every other
in a `+ over`; a decision a revision leaves with one option gives it none. `so that <the purpose it serves>` may stand
for `because`. `Given` names `D:<id>/<option-id>` where the question arises only under that option, and `D:<id>` where
it arises whatever that decision chose. `Given`, `Replaced`, `Broke` and `Lost` are given only when there is one. A
decision is lost with an option of another, an article or a fact when its `Given` names it and it is replaced or
followed, or names a decision lost with it; it is back with it when that holds again. One whose last item in `Lost` is a
`with` binds nothing.

**A fact.** Declared inline, in a decision's reasons:

```
{F:<id>: <what is or was the case, and when>}
{F:<id> (assumed): <what is taken to be the case>}
{F:<id>: <what is or was the case, and when>; follows F:<id>}
```

Declared in `facts/`, its data, such as a table, fenced after its head:

````
Fact <id>: <what is or was the case, and when>

```
<its data>
```

Follows: F:<id>
````

`Fact <id> (assumed):` heads an assumed fact there.

A reference resolves to the one record, declaration or approach with its id. The articles, decisions and facts cited or
declared in `Given`, `Chosen` and `Options` are the decision's premises, at least one article or decision among those in
`Chosen` and `Options`; a reference in `Replaced`, `Broke` or `Lost` is no premise.

Run the check after every change, and with `--base <the revision before the change> --ready` before the change is
merged:

```
python3 -B <system>/check.py --root reasoning [--ascii]
```

`--dependents <reference>...` lists the decisions resting on each record named.
