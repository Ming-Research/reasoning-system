# Extension: keeping the work in line with the derivations

An extension of the reasoning system, not part of it: for agents whose work (code, specifications, configuration) the
derivations govern, and for the review of that work. Read `reading.md` first.

## 1. Solving a problem

Work from the records before choosing how to do anything:

1. Find the derivations that govern the problem, and follow each through what it rests on up to the articles.
2. Derive the solution from them and from the problem itself.
   - Where the records decide it, with one workable way, do it: compare nothing and put nothing to the owner.
   - Where they leave several workable ways, that is a trade-off: compare them and put it to the owner, so that it is
     derived.
3. Challenge the chain the solution stands on. Name the derivations that constrain it most ("without this one, I would
   do..."), and for each say whether revising it would give a clearly better solution by the same articles: that
   solution, what it gains, what it costs, and which records resting on the derivation would be examined again
   (`check.py --dependents`). Go no higher than the articles, which are the owner's: an article in the way is pointed
   out, not challenged.
4. Where a revision would be clearly better, propose it with what rests on it, rather than work around the derivation.
   Where a revision explored breaks on a record below it, propose keeping it as a `Rejected` item of the derivation it
   would have revised, citing the record it broke on.

Approaches are compared only for a trade-off or a revision, not as a step of every work.

## 2. Doing the work

- Do what the derivations decide. A rejected approach stays rejected unless what changed is said.
- When your work would depart from a derivation, do not depart alone: raise it, with what you found and why, so that
  the derivation is examined for a revision.
- A fact that you find no longer holds is the project's to change: say so, with what you saw.

## 3. Reviewing the work

For each change in the work:

- A choice between workable approaches that the work makes must be governed by a derivation; one that none governs is
  a missing derivation, to be derived and put to the owner.
- Work that contradicts a derivation, or implements a rejected approach, without a revision of that derivation, is a
  finding.
- Work removed that leaves a derivation with nothing implementing it, or a rejected approach still implemented, is a
  finding.
- A commitment of the derivations in the work's scope that is missing, half done or a placeholder is a finding.
- A solution whose chain was not challenged is a finding: no derivation named as constraining it, or each one
  dismissed without the solution its revision would give.

Ordinary steps with one workable way need no derivation. Finding the derivations that govern the work is the
reviewer's own reading; nothing in the records maps them to the work.
