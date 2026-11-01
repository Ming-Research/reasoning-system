# Reasoning rules: writing

For agents that derive decisions and add them to the records or revise them.

## 1. Deriving a decision

- A decision's question is its head. Its reasons cite each premise: at least one article or earlier decision, which give
  what matters in the weighing, and the facts it needs. Conclude only what the premises give.
- Record a decision only for a real choice. Why an option loses is never the choice turned round.
- Write the choice, the reasons that decide it and the qualifications it needs, in as few words as keep its meaning. A
  reason may be the purpose the choice serves.
- A record names no paths, no files, modules, functions, types, tables or fields, no ids or numbers of steps or states:
  a step is named by what it does. No record only restates an interface or an implementation. A number the project sets
  is configuration and is not written, unless the number itself was a real choice.
- No word in a decision or a fact takes its meaning from a conversation, card or work, or from when it was written: no
  "the new flow", "until now" or "option B", no number that a work, a task or a card goes by.
- A fact is declared where it is first stated, and says when it holds, where that matters.
- Record the reasons the owner gives for a choice as facts, citing the article or decision that makes them matter.
- A decision whose premises are not found is not recorded: ask the owner for them.
- How the project's maintainers keep its repository (branches, the limits of a machine) is no decision of the project.

## 2. Adding and revising

No article or approach is reworded once recorded. Each addition, and each revision with the decisions it changes, goes
to the owner as one card, and is recorded once accepted.

- **An addition** answers a question no decision answers, with a real choice. It takes the articles and decisions as
  they stand, changes none of them, and brings the facts its reasons need.
- **A revision** names the base that changed and derives the question again on it. The choice replaced is kept as
  replaced, with the reasons it was chosen on and the base it lost on; it is also an option again when it still trades
  off against the new choice. The options are weighed again against the new choice. When the new base leaves a single
  option, the decision takes it, and its card shows the derivation rather than a choice. Dropping something the project
  does is a revision of the decision it stands under, to not doing it.
- **Deriving again.** When an article is replaced or a decision revised, derive again every decision resting on it: it
  stands, resting on the new article where one replaced the old; or it is revised in the same card; or, when its
  question arises only under the approach replaced, it is lost with it. Derive again the decisions resting on each one
  revised; those resting on one lost are lost with it, and those resting on one that stood are left as they are. A new
  fact is weighed against the decisions it bears on, found by their questions and by the decisions resting on the fact
  it follows, and recorded only when it changes one.
- **What is kept.** A decision lost with an approach stays as it was, marked as lost with it, and so does every decision
  resting on it. Taking the approach up again brings them back to be derived again, each marked as back with it. A
  revision explored and found to break on a record it would have had to change is kept with the decision it would have
  revised, naming that record, and recorded with the card that explored it. Attempts made while coding are not kept.
- **Follows and replaces.** A new fact names the fact it follows, and an article the owner adds names the article it
  replaces.

## 3. Format

The records are plain text in the language and character set the project sets. Each field is one line, with a blank line
between fields; list items follow straight after their field. A decision holds no dates but in the facts it declares,
and no account of how it came to be; the log does.

The decisions, and the facts in `facts/`, are each a tree, by concept and by subject; the log is newest first. A tree
has a node file `<subject>.md` at its top, and the subjects under it in a directory of the same name beside it,
`<subject>/`, to any depth. Every article, fact and decision has an id: lowercase words joined by hyphens, unique in its
kind, never reused, and kept when its record moves.

**An article.** Articles are numbered from 1 in the order they were added.

```
## Article <n> (<id>). <title>

<text>

Replaces: C:<id>
```

**A decision.** A node file is named after the concept it governs and holds the decisions on it.

```
Decision <id>: <the question it answers>

Chosen: <the option taken>, because <why it wins, citing its premises>

Rejected:
- <another option>: <what it does better>; rejected because <why that loses on the premises>

Replaced:
- <a choice replaced>: chosen because <its reasons>; replaced because <the base that changed>

Broke:
- <a revision explored>: breaks on <the record>

Lost:
- with D:<id>, <the approach, as that decision's Replaced words it>
- back with D:<id>, <the approach>
```

`so that <the purpose it serves>` may stand for `because`, in `Chosen` and in `Replaced`. `Rejected` holds the options;
a decision added has at least one, and one revised may have none left. `Replaced`, `Broke` and `Lost` are history and
are given only when there is one; a decision whose last item in `Lost` is a `with` binds nothing.

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

A reference resolves to the one record or declaration with its id. The articles, decisions and facts cited or declared
in `Chosen` and `Rejected` are the decision's premises, at least one article or decision among those in `Chosen`; a
reference in `Replaced`, `Broke` or `Lost` is no premise.

**A log entry.**

```
## <YYYY-MM-DD> <title>

Changed: <reference> <added, revised, re-derived or lost>, ...

Why: <the question added, or the base that changed, and the derivation>

Derived again: <each record resting on what changed, and whether it stood, was revised or was lost>
```

`re-derived` is a decision whose choice stood and whose text changed: resting on a new article, gaining an item in
`Broke`, or brought back. An addition gives no `Derived again`.

Run the check after every change, and with `--base <the revision before the change> --ready` before the change is
merged:

```
python3 -B <system>/check.py --root reasoning [--ascii]
```

`--dependents <reference>...` lists the decisions resting on each record named.
