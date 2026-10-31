# Reasoning rules: the design coherence review (DCR)

For the review that checks a change to the records. Read `reading.md` and `writing.md` first.

## 1. What to read

- The change to the records, whole.
- Every record it adds, changes or removes, with what each rests on.
- Every record resting on those, found through `Rests on`.
- What `check.py` printed against the change's base, with `--ready`.

Say which records you read.

## 2. What to check

1. **The records cohere.** Every premise a derivation lists is used by it. No derivation contradicts another, or
   narrows one without saying so.
2. **What rests on a change was examined again.** Every record resting on what changed holds still or was revised,
   and the log says which. A replaced decision is kept as a `Rejected` item citing the premise it lost on.
3. **The facts cited are in the records.** Whether a fact holds is the project's, not this review's; a value the
   project has not established is marked `Assumed`.
4. **The reasons are derivations.** Each reason derives from its cited premises. None is someone's words: the owner's
   input enters only as the constitution or as a ruling; a premise not yet found is marked `Open`.
5. **The records pass the check,** as `check.py` reports it.

## 3. How to report

For each finding, quote both sides and the premises each rests on, and say what would resolve it. A finding is never
resolved by citing someone's words.
