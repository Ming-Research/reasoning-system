# Reasoning rules: reading

For every agent whose work rests on the project's reasoning. An agent that also derives and changes the records reads
`writing.md` too; the design coherence review reads `writing.md` and `dcr.md` too. All of them rest on the constitution
of the reasoning system, kept with these rules and apart from any project's records. Extensions of the system have
rules of their own: `extension-work.md` for keeping the work in line with the derivations, and `extension-cards.md` for
putting revisions to the owner.

## 1. The records

The project keeps its reasoning in one place, `reasoning/`:

- `constitution.md`, **the axioms**: whom the project serves, what it is for and why. Only the owner sets it; nothing
  in it is derived.
- `facts/`, **what the derivations take as given**: only facts some derivation rests on. Where a fact comes from and
  whether it holds are the project's to establish, not the system's. A fact marked `Assumed` is a value the project
  chose or estimated and has not established.
- `derivations/`, **the decisions**. Each is one choice where workable approaches had to be traded off: `Decision` is
  the choice and why; `Rests on` names every article, fact and derivation it cites; `Open` marks one whose premise is
  still missing; `Rejected` lists the approaches not chosen, with why, the decisions it replaced among them.
- `log.md`, **every revision**, with why, what was examined again and the owner's ruling.

A reference reads `C:<id>` (an article), `F:<id>` (a fact) or `D:<id>` (a derivation).

## 2. Choices no derivation covers

A choice between workable approaches that no derivation covers is not settled alone: raise it, with what you found and
why, so that it is derived and the records revised. Ordinary steps with one workable way need nothing.

## 3. Words are evidence, not reasons

Nobody's words are a reason: not the owner's, not an agent's, not the architect's. What someone said holds in its
context and its time. Above all, the owner's words are not truth to be obeyed: they are evidence of the owner's
reasoning, to be understood.

- **Understand the reasoning behind the words.** Find what they rest on: which axiom, which fact, which decision. Act on
  what follows from those premises.
- **When the reasoning cannot be found, ask.** If the owner did not say why, and nothing in the records gives it, ask
  the owner for the premise. Do not guess it, and do not act on "the owner said so" in its place. Do not ask what the
  records already give.
- **When the words contradict the derivations, say so.** Point it out to the owner, quoting both sides and the
  premises each rests on. Either the words were mistaken or out of their context, and the derivation stands; or they
  show something the records lack (a fact that changed, a missing premise, a better line of reasoning), and the
  derivations are examined for a revision.

## 4. Who decides what

- The owner's inputs are the constitution and the decisions. The owner sets the constitution and rules every revision
  of a derivation, trading approaches off with the reasoning for it.
- Agents derive, propose derivations and keep the records. The design coherence review checks them.
- No derivation contradicts the constitution or the facts it rests on.
