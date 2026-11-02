# Reasoning system

A project's decisions kept as records derived from its owner's axioms and the facts it takes as given. The system does
two things: it derives each decision, and it evolves the records from one coherent state to the next, their information
only growing.

## Derivation

A decision answers one question. It weighs the options that answer it, each with what it does better than each other, by
the articles of the project's constitution and, where they pull apart, by the precedence the constitution sets; the
weighing is a judgment, stated in its reasons. It takes one option and says why each other loses. Its premises are the
articles, facts and earlier decisions it cites, an article or a decision among them. Only a choice the owner must rule
is a decision: a real one, options that trade off, each better than each other in something, which is a contract others
build on, a trade between articles that no rule or measure settles, or a scope or bar the work is judged by. Any other
choice is made where it lives and is not recorded. No decision contradicts another, an article, or a fact it rests on.

## Evolution

The records only grow. Facts and articles are only added; a later state or a correction is a new fact beside the old,
and an article the owner changes is a new one replacing the old. A decision changes only when one of its bases changes:
an article replaced, a new fact, or a decision it rests on revised. A revision keeps the choice it replaces with the
weighing it was chosen on and the base it lost on; the decisions resting on it are derived again; a decision whose
question arose only under the option replaced is lost with it, and back with it if it returns; a revision explored whose
break was established is kept with the record it broke on. Each addition and each revision goes to the owner as a card.

## The records

`reasoning/` holds `constitution.md` (the owner's articles), `derivations/` (the decisions, a tree by concept) and
`facts/` (facts carrying much data; most facts are declared inline in the decisions). The records name nothing that
exists only in one implementation, and the project's code does not cite them.

## Contents

- `rules/reading.md`: for everyone working on a project.
- `rules/writing.md`: for those who add to the records or revise them; it gives the format.
- `rules/dcr.md`: the design coherence review of a change to the records.
- `rules/extension-work.md`: an extension, the review of a work against the decisions once its code is written.
- `rules/extension-cards.md`: an extension, putting an addition or a revision to the owner as a card.
- `rules/extension-challenge.md`: an extension, challenging the decisions a solution stands on.
- `guides/building.md`: building a project's records from nothing, or rebuilding them; given to no agent.
- `check.py`: the check of a project's records, with `test_check.py` its tests; Python 3 and its standard library.
- `review-base.sh`: picks the revision a CI job checks the records against.
- `reasoning/`: this system's own records, to be rebuilt in the current form.

## Using it in a project

The project keeps its records in `reasoning/`, gives each agent the rule files its role needs, and checks the records
on every push and pull request with `check.py` taken at a fixed commit of this repository, in a directory `<system>`,
with the full history (`fetch-depth: 0`):

```sh
base=$(sh <system>/review-base.sh "$GITHUB_EVENT_NAME" "$GITHUB_REF" "$PUSH_BEFORE")
python3 -B <system>/check.py --root reasoning --base "$base" --ready
```

where `PUSH_BEFORE` is `${{ github.event.before }}`. Add `--ascii` when the project keeps its records in English.
