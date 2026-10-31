Decision check-script: The format, the references and the logging of every revision are checked by a script, run on every change, instead of by the review's reading alone, because agents vary in what they let through, while a check that can fail makes a violation impossible or visible.

Rests on: C:coherence, F:agents-vary, D:checkable-format

Rejected:
- Leaving the format to the review's reading: rejected because agents vary in what they let through (F:agents-vary).

Decision check-in-python: The check is a Python script using only the standard library, instead of a compiled program, because it runs wherever a project's agents work, with no compiling and no toolchain.

Rests on: F:python-no-toolchain, D:check-script

Rejected:
- A compiled program whose parser a project's own code could share: rejected because every project keeping its records would need that toolchain to run the check (F:python-no-toolchain).

Decision dependents-query: The check lists, for any record named, every derivation resting on it directly or through others, instead of leaving them to be found by reading, because a revision examines again every record resting on what it changes, and that is the cost a challenge of the chain weighs.

Rests on: D:check-script, D:dependents-examined, D:challenge-the-chain

Decision ready-gate: A revision reaches the project's main line only with a new log entry naming every record it adds, changes or removes, checked against the revision before it, and with no merged entry changed, because a derivation changes only by the owner's ruling and every revision is logged, and a rule nothing checks is not kept.

Rests on: D:revision-by-ruling, D:log, D:check-script
