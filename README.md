# Reasoning system

A logical derivation system for planning and designing a project rigorously: a project's axioms, the facts its
derivations take as given, and the decisions derived from them, kept rigorous and coherent through every revision.

## Contents

- `rules/reading.md`: for every agent whose work rests on a project's reasoning.
- `rules/writing.md`: for agents that derive and change a project's records; it also gives how a project's
  `reasoning/` directory is laid out and the format of each record.
- `rules/dcr.md`: the design coherence review, which checks that a change keeps the records coherent.
- `rules/extension-work.md`: an extension, keeping a project's work in line with its derivations.
- `rules/extension-cards.md`: an extension, putting a revision to the owner as a card.
- `check.py`: the check of a project's records, with `test_check.py` its tests; Python 3 and its standard library only.
- `review-base.sh`: picks the revision a CI job checks a change against.
- `reasoning/`: this system's own records, kept by its own rules: its constitution, the facts and derivations its rules
  come from, and its log.

## Using it in a project

The project adds this repository as a submodule at its root, `reasoning-system/`, keeps its records in `reasoning/`,
and gives its agents the rules their roles need. Its CI checks the records on every push and pull request, with the
full history (`fetch-depth: 0`):

```sh
base=$(sh reasoning-system/review-base.sh "$GITHUB_EVENT_NAME" "$GITHUB_REF" "$PUSH_BEFORE")
python3 -B reasoning-system/check.py --root reasoning --base "$base" --ready
```

where `PUSH_BEFORE` is `${{ github.event.before }}`. Add `--ascii` when the project keeps its records in English.
