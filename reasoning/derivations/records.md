Decision record-kinds: A project's reasoning is kept as its constitution, its facts, its derivations and its log, instead of also keeping research notes or a list of exceptions, because the content is the axioms, the facts and the decisions, and a revision must show that what rested on it was examined.

Rests on: C:purpose, C:coherence, C:facts-given, C:membership

Rejected:
- Research notes in the records: rejected because how facts are established is the project's, not the system's (C:facts-given).
- A list of exceptions: rejected because a departure from the constitution is an incoherence, to be revised, not kept beside it (C:coherence).

Decision agents-read: The records are written for the agents that read and keep them, because the owner understands and controls the system through agents.

Rests on: C:agents-read

Rejected:
- Writing each record so that a person who has not seen where it came from can read it alone: rejected because no person reads the records without an agent (C:agents-read).

Decision tree-layout: Facts and derivations are each kept as a tree by subject, a node file <subject>.md with the subjects under it in <subject>/, instead of one flat directory of files, because the records grow to hundreds, and a tree keeps each directory to the subjects at one level.

Rests on: F:records-grow

Rejected:
- One flat directory of files for each kind: rejected because it grows with the whole project (F:records-grow).

Decision facts-when-cited: A fact enters the records only when a derivation rests on it, and only as given, instead of the records keeping how it was established and whether it still holds, because where a fact comes from and whether it holds are the project's.

Rests on: C:facts-given, C:membership

Decision assumed-facts: A fact the project chose or estimated rather than established is marked Assumed, with what would settle or overturn it, because a derivation resting on it holds only as firmly as it, and the mark shows which derivations to examine again when it settles.

Rests on: C:coherence, C:facts-given

Decision ids: Every article, fact and derivation has an id that stays when its record moves or is reworded and is never used again once removed, and records cite each other by id, instead of by position or by file path, because coherence is checked by following premises, and a revision finds what rests on it by them.

Rests on: C:coherence

Rejected:
- Citing by position or by file path: rejected because records move, and a position or a path breaks where an id holds.

Decision rests-on: Each derivation lists in Rests on every article, fact and derivation it cites, instead of leaving them in its prose, because a conclusion is checked against its premises, and what rests on a changed record is found through them.

Rests on: C:coherence, D:ids

Decision open-derivations: A derivation whose premise has not been found is kept, marked Open with what is missing and where it was asked, instead of being left out of the records or kept with words in place of its premise, because the records stay checkable while premises are found one at a time, and the mark lists what is still missing.

Rests on: C:coherence, D:words-not-reasons, D:ask-for-premise

Rejected:
- Leaving a decision out of the records until its premise is found: rejected because the decision holds meanwhile, and nothing would show it rests on nothing (C:coherence).

Decision rejected-list: Each derivation lists the approaches it rejected, each with why it was rejected, because the reasoning of the trade-off, why one is kept and the others rejected, is what links a decision to the rest.

Rests on: C:owner-inputs

Decision replaced-kept: A decision a revision replaces becomes a Rejected item of the derivation replacing it, its reason citing the premise it lost on, instead of only the log saying what was replaced, because a later change to that premise must reopen it, and a change finds only what cites the changed record.

Rests on: C:coherence, D:rejected-list, D:rests-on, D:dependents-examined, D:log

Rejected:
- Keeping each replaced decision as a record of its own beside the one that replaced it, with paired moves between them: rejected because the Rejected item already carries what it was and the premise it lost on, and the log carries when (D:log).

Decision log: Every revision is logged with what changed, why, what resting on it was examined again and the owner's ruling it carries out, newest first, and a merged entry is never changed, while a derivation holds no history, because a revision must show that what rested on it was examined and that the owner ruled it, and a derivation's history is not part of its reasoning.

Rests on: C:coherence, C:owner-inputs, C:membership

Decision checkable-format: The records are plain text in a format a check can read, in the language and character set the project sets, instead of in one language for every project, because coherence must be checkable, and the language serves no coherence.

Rests on: C:coherence, C:membership
