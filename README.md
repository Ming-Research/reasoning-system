# Reasoning system

A project's decisions kept as a tree, derived from its axioms and the facts it takes as given. The system does two
things: it derives each decision, and it evolves the whole from one coherent state to the next, its information only
growing.

## Derivation

A decision answers one question. From its premises (articles of the project's constitution, facts, earlier decisions;
at least one article or earlier decision among them) it weighs the approaches that answer the question by what each
gives and what each costs, and takes one. Its content is the choice: that approach and not the others, each named. A
recorded decision can be a premise of later ones. No decision contradicts another, an article, or a fact it rests on.

Only a real choice is a decision. A choice is real when every approach in it has real advantages and real costs, so
that taking one gives something up. An approach better on every count, or by an overwhelming balance, leaves no choice,
and nothing is recorded. Whether a choice seems obvious, or fits an article or a fact, does not decide whether it is
one; weighing each approach's advantages and costs on the premises does. The same standard holds wherever a choice is
spoken of. So every decision names at least one approach not chosen, with what that approach does better and why
that loses on the decision's premises, never the choice turned round; an approach with no real advantage is not named.

## Evolution

The records only grow. Nothing in them is deleted and nothing is lost: an overturned choice stays as an approach that
lost, a mistaken fact beside its correction. Every step of their evolution brings information in, and they stay coherent
as they grow. The decisions grow by additions and revisions, each put to the owner.

- **Facts are only added.** A fact holds of when it was found: a later state of the world, such as a price that has
  dropped since, is a new fact beside it, and a fact found mistaken stays as what was taken to be the case, its
  correction a second fact. A new fact is recorded only when a decision rests on it: one an addition needs, or one that
  changes a decision, which is then studied again and revised by a card. A new fact that does neither is not recorded.
  A fact no current choice rests on stays, cited by the approach that lost on its successor.
- **An addition** answers a question no decision answers. It takes the articles and decisions as they stand and brings
  the facts its reasons need (what is the case, given inline in a decision's reasons, is a fact too). It changes no
  article and no decision.
- **A revision** overturns a decision, and is possible only when one of the decision's bases changed: a new fact (what
  the decision was found to have missed, or the need a work brings, among them), an article, or a decision it rests on.
  With none of them changed, no decision can be overturned. A revision names the base that changed; the choice it
  replaces is kept as an approach not chosen, saying the base it lost on; every decision resting on the one overturned
  loses that premise and is derived again, and may come out the same or change; one card covers the revision and every
  decision it changes with it. Taking up an approach a decision rejected is a revision of that decision, and so is
  dropping something the project does: the decision it stands under is revised to not doing it.
- **What stays**: the approaches that lost, with the decisions made under them while they were chosen, and the
  revisions explored that broke on a record they would have had to change, so that no path is explored again
  unknowingly. Attempts made while coding are not paths and are not kept.

## The records

- **The constitution**: the owner's axioms. Only the owner sets it. An article is never edited: one the owner changes
  is a new article, the old one kept as replaced by it.
- **Facts**: what is or was the case as of when it was found, about the world, the tools, the project as it runs, or the
  owner, recorded only when a decision rests on them, and only ever added. Most stand inline among a decision's
  reasons; one that carries much data, such as measurements, is kept apart in `facts/` so that the decisions stay
  short. A lasting preference or habit of the owner is a fact; nobody's words are a reason. A fact is known or assumed:
  an assumed fact takes part in deriving like any other, its correctness assumed rather than known.
- **Decisions**: how the project does something, kept as derivations, each a real choice as above. A decision whose
  premises are not known is not recorded until they are found, asked of the owner when need be.

The records name nothing that exists only in one implementation: no paths, no names of files, modules, functions,
types, tables or fields, no ids or numbers of steps or states; a step is named by what it does. No record only
restates an interface or an implementation. A number the project sets, such as a wait or a limit, is configuration,
unless the number itself was a real choice. The project's code, tests and configuration do not cite the records either;
commit messages, pull requests and cards may.

## Working with them

An extension of the system, given in full in `rules/extension-work.md`. Work starts from the project's code and its
records. The decisions answering the questions the work raises are read, each decision stating its question, with
the approaches they rejected. Then:

- Code and records found to disagree: the code is made to follow the records, unless the records are wrong, which is a
  revision. Two decisions found to contradict each other: a revision.
- Work with no real choice in it, against no decision: it is done, and the records stay as they are.
- A real choice the work makes: an addition, with all its premises, the decisions as they stand taken as given.
- Work a decision stands in the way of: a revision put to the owner, with at least two options, the work done under the
  records as they are (it cannot be done, or only awkwardly) and the records changed (where, and how they stay
  coherent).

One work may bring both additions and revisions.

## Contents

- `rules/reading.md`: for every agent whose work rests on a project's records.
- `rules/writing.md`: for agents that derive decisions and change the records; it also gives the layout of a
  project's `reasoning/` directory and the format of each record.
- `rules/dcr.md`: the design coherence review, which checks an addition or a revision.
- `rules/extension-work.md`: an extension, keeping a project's work in line with its decisions.
- `rules/extension-cards.md`: an extension, putting an addition or a revision to the owner as a card.
- `check.py`: the check of a project's records, with `test_check.py` its tests; Python 3 and its standard library only.
- `review-base.sh`: picks the commit a CI job checks the records against.
- `reasoning/`: this system's own records, to be rebuilt by these rules.

## Using it in a project

The project keeps its records in `reasoning/`, gives its agents the rules their roles need, and checks the records on
every push and pull request with `check.py` taken at a fixed commit of this repository, in a directory `<system>`
(a submodule, or a copy downloaded), with the full history (`fetch-depth: 0`):

```sh
base=$(sh <system>/review-base.sh "$GITHUB_EVENT_NAME" "$GITHUB_REF" "$PUSH_BEFORE")
python3 -B <system>/check.py --root reasoning --base "$base" --ready
```

where `PUSH_BEFORE` is `${{ github.event.before }}`. Add `--ascii` when the project keeps its records in English.
