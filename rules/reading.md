# Reasoning rules: reading

For every agent whose work rests on a project's records.

Whoever works on the project reads its records together with its code, never one without the other: the records for
what was decided and rejected, the code for what is built.

## 1. The records

The project keeps its records in `reasoning/`:

- `constitution.md`, **the axioms**: the owner's, and only the owner sets them.
- `derivations/`, **the decisions**: how the project does something. Each answers one question: from its premises,
  articles, facts and earlier decisions it cites, it takes one option, and names the other options,
  each with what it does better and why that loses on the premises.
- `facts/`, **the facts that carry much data**, such as measurements, kept apart so that the decisions resting on them
  stay short, and cited by their ids.
- `log.md`, **every change to the records**, with why.

No decision contradicts another, an article, or a fact it rests on. The records name nothing that exists only in one
implementation, and the project's code, tests and configuration do not cite them; commit messages, pull requests and
cards may.

A reference reads `C:<id>` (an article), `F:<id>` (a fact) or `D:<id>` (a decision).

**Facts** are what is or was the case, as of when it was found: about the world, the tools, the project as it runs, or
the owner. Each is declared once, most inline among a decision's reasons as `{F:<id>: ...}`, one that carries much data
in `facts/`, and is cited elsewhere as `F:<id>`. A fact is known or assumed: an assumed fact takes part in deriving like
any other, its correctness assumed rather than known, and is marked so. A fact is recorded only when a decision rests on
it, and is never removed or reworded: a later state, or the correction of a mistake, is a new fact beside it.

## 2. What is in force

The records only grow, so they keep what no longer binds: an article another has replaced, a choice a decision
replaced with the decisions lost with it, and the revisions explored that broke. These bind nothing, and each is marked
so. They are kept to be read: before proposing an approach, read whether a decision rejected it, or a revision like it
broke, and on what. Taking a rejected approach up again is a revision of the decision that rejected it, naming the base
that changed since.

A fact holds of when it was found. A new decision is derived from the latest fact on its matter; a decision derived from
an earlier one stands unless the later fact changes it.

A decision stands until it is revised, and only a change to one of its bases can revise it: an article replaced, a new
fact (what the decision was found to have missed, or the need a work brings, among them), or a decision it rests on
revised. Whoever finds such a change, or meets a real choice no decision makes, raises it to the owner with what was
found, naming the base where there is one, and does not settle it alone.

## 3. What a real choice is

A choice is real, wherever one is spoken of, only when it has options that trade off against one another: approaches
none of which another beats on every count or by an overwhelming balance, so that each is better than each other in
something and worse in something else. An approach another beats so is no option, and with one option left there is no
choice. Whether a choice seems obvious, or fits an article or a fact, does not decide whether it is one; weighing the
options against one another on the premises does. A decision names every other option of its choice.

## 4. Words are evidence, not reasons

The owner and the agents derive by the same first principles, from the same premises. Nobody's words are a reason, the
owner's or any agent's; what someone said holds in its context and its time, and is evidence of the reasoning behind it,
to be understood. When the owner chooses between approaches, the decision rests on the reasons given for the choice,
which are facts like any other; that the owner chose is no reason.

- **Find the reasoning behind the words**: which article, fact or decision they rest on, and act on what follows from
  those premises. A lasting preference or habit of the owner is a fact, a premise on which approaches are weighed like
  any other.
- **When the reasoning cannot be found, ask** the owner for the premise, rather than guess it or act on "the owner said
  so". Do not ask what the records already give.
- **When the words contradict the decisions, say so to the owner**, quoting both sides and the premises each rests on.
  Either the words were mistaken or out of their context, and the decision stands; or they bring what the records
  lack, a new fact or an article the owner changes, and the decision is studied again for a revision.
