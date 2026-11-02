# Guide: building a tree, or rebuilding one

For whoever builds a project's records from nothing, or rebuilds them from records kept another way. The rules in
`rules/` say what the records are; this gives the order of the work they lead to.

## Building from nothing

1. **The constitution first.** Every decision rests on an article, directly or through other decisions, so none can be
   derived before the articles and their precedence are set.
2. **The questions.** Each decision answers one question the project meets, so the work starts by listing the real
   choices the project has made or must make, from its code, its documents and its owner, each as a question.
3. **In order.** A question that arises only under an option of another decision names it in `Given`, so the decision
   that frames it is derived first.
4. **Each decision** is then derived as `rules/writing.md` says, and put to the owner.

## Rebuilding from records kept another way

1. **The old records are evidence, not records.** They were written by other rules, so copying them over carries what
   these rules keep out: descriptions, names from the implementation, options nobody would take. Each is read for the
   question it answers and for the reasons and facts it gives.
2. **One decision for each question.** Old records answering the same question become one; one answering several
   becomes one for each.
3. **What the old records do not show is a premise not found.** Whether a choice was real, whether an option was more
   than padding, what an approach does better than each other, why the choice fell as it did: where neither the old
   record nor what the work left behind (its discussions, commits and data) shows it, it is asked of the owner, as
   `rules/reading.md` says of any premise not found. An approach with no gain over any other is no option by the same
   rules, and is dropped without asking.
4. **In batches.** The rebuild goes concept by concept, a decision that frames others before them, each batch passing
   the check and the review before it goes to the owner.
