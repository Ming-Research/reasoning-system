Decision log-kept: Is a log of changes kept beside the records?

Chosen: no-log, because what a log entry held is held elsewhere or needed only before a change lands {F:log-parts-held: of a log entry's parts, what changed is held by the repository's history, why by the decisions' Chosen and Replaced, and the card and its ruling by the commit or pull request, while which decisions were derived again and stood is checked by the review before the change lands, as found on 2026-11-01}, so with-log keeps twice what serves coherence once (C:membership); its record of the decisions that stood would show a change's coherence after it landed (C:derive-and-evolve), which the review has shown before.

Options:
- no-log: the constitution, the facts and the decisions only
  + over with-log: nothing kept twice, nothing to keep in step
- with-log: those and an entry for every change: what changed, why, the card and its ruling, what was derived again
  + over no-log: which decisions were derived again and stood, kept after the change landed

Decision rewording: Is the text of a record ever reworded?

Chosen: never, because only so can the records' growth be checked mechanically from one state to the next (C:derive-and-evolve), while keeping-meaning needs a judgment on every edit that the meaning held, and lets it drift unseen; current wording serves the agents reading the records (C:agents-read), but coherence comes first (C:precedence).

Options:
- never: a change is a new record, or a revision that keeps what it replaces
  + over keeping-meaning: growth checked mechanically, nothing drifting unseen
- keeping-meaning: wording may change where the meaning stays, as when a name changes
  + over never: the wording kept current for the agents reading it

Decision record-medium: In what medium are the records written?

Chosen: plain-text, because the agents read and write them as they do prose (C:agents-read), and the form a check reads is a few lines of grammar; structured-data parses exactly (C:agents-read), but with costs the agents bear {F:structured-costs (assumed): records kept as data with a rendered view bring noisy merges, quoting errors by agents and a second artifact to keep in step}.

Options:
- plain-text: plain text in a fixed form a check reads
  + over structured-data: read and written as prose, one artifact
- structured-data: data, JSON or TOML, read through a rendered view
  + over plain-text: parsed exactly, with no grammar of its own

Decision decision-parts: What parts does a decision have?

Chosen: options-weighed, because whether each option beats each other in something can then be checked (C:derive-and-evolve), which prose-rejected hides {F:rejected-without-gains: none of the 117 rejected items in wf-agents' records as moved in on 2026-10-31 said what the option did better, as counted on 2026-11-01}, while naming each option's gains and costs exposed what prose missed {F:gains-expose: rewriting twelve decisions of wf-agents' records as moved in on 2026-10-31 with each option's gains and costs named exposed missing options, padded ones, missing premises and a revision with no changed base, on 2026-11-01}; prose-rejected is shorter (C:agents-read), but coherence comes first (C:precedence). A form that records a revision as a new record superseding the old is no option, since D:replaced-place keeps a replaced choice inside its decision.

Options:
- options-weighed: the question, what it arises under, the choice with its weighing, and the options weighed, each on its own
  + over prose-rejected: whether each option beats each other in something shows
- prose-rejected: the choice with its reasons, and the approaches rejected with why
  + over options-weighed: shorter (C:agents-read)

Decision option-costs: Does an option state its costs beside its gains?

Given: D:decision-parts/options-weighed

Chosen: gains-only, because each trade is then written once, as a gain of one option over another, whose cost it is {F:mirror-drift (assumed): a trade written on both options, as a gain of one and a cost of the other, comes to be worded differently on each side}, so that the two writings of one trade cannot come to disagree (C:derive-and-evolve), and the pairwise gains already show each option better and worse than each other; gains-and-costs reads each option whole (C:agents-read), but coherence comes first (C:precedence).

Options:
- gains-only: what each option does better than which others; a cost is another's gain
  + over gains-and-costs: each trade written once
- gains-and-costs: each option's gains and its costs, both
  + over gains-only: each option read whole in one place

Decision premise-place: Where does a decision name its premises?

Chosen: where-they-bear, because a premise cited where it bears shows what it gives the weighing, and a list beside the reasons can name one the reasons do not use or miss one they do (C:derive-and-evolve); listed finds the premises in one glance (C:agents-read), but coherence comes first (C:precedence).

Options:
- where-they-bear: cited in the reasons where each bears
  + over listed: each premise tied to what it gives
- listed: a list of premises beside the reasons
  + over where-they-bear: every premise in one line

Decision replaced-place: Where is a choice a revision replaces kept?

Chosen: inside, because a decision's question then keeps one id through every revision, which the decisions resting on it cite (C:derive-and-evolve); superseding-record keeps each choice whole on its own, but moves the id they cite.

Options:
- inside: in the decision's own history, with the weighing it was chosen on and the base it lost on
  + over superseding-record: one id for the question through every revision
- superseding-record: a new record for the new choice, the old marked superseded
  + over inside: each choice read whole in a record of its own

Decision broken-kept: Is a revision explored and found to break kept?

Chosen: kept, because a path explored and abandoned with no record is explored again (F:paths-explored-again), and the record it broke on says when it might hold (C:derive-and-evolve); dropped keeps the decisions shorter (C:agents-read), but coherence comes first (C:precedence).

Options:
- kept: with the decision it would have revised, naming the record it broke on
  + over dropped: not explored again unknowingly
- dropped: only what was chosen is recorded
  + over kept: shorter decisions

Decision tree-layout: How are the decisions and the facts arranged?

Chosen: nested-by-concept, because an agent finds the decisions its work meets by the concepts it touches {F:agents-find-by-concept (assumed): an agent looks up the decisions its work meets by the concepts the work touches} within a limited context {F:context-limited: an agent holds a limited context, which the records and the code it reads share}, which the records' size makes matter {F:records-size: wf-agents' records held 526 decisions on 2026-11-01} (C:agents-read), and the decisions on one concept, resting on one another, are reviewed for coherence together (C:derive-and-evolve); one-level groups by concept with one place fewer to choose, flat has none, and one-file is read in one go, but each makes the reader take in more to find less.

Options:
- nested-by-concept: a node file for each concept, the concepts under it in a directory of its name
  + over one-level, flat, one-file: only the concepts met are read, at any depth
- one-level: a file for each concept, all in one directory
  + over nested-by-concept: no depth to choose
  + over flat, one-file: found by concept
- flat: a file for each decision
  + over nested-by-concept, one-level: no place to choose for a decision
  + over one-file: the smallest diffs
- one-file: every decision in one file
  + over nested-by-concept, one-level, flat: read whole in one go

Decision fact-place: Where is a fact declared?

Chosen: inline, because a fact is read where its reasoning is each time a decision first resting on it is read, while every fact is sought in one place only when a new fact must name the one it follows (C:agents-read); a fact carrying much data is kept in a file of facts all the same, since inline it would bury the reasoning it serves.

Options:
- inline: in the reasons of the decision first resting on it
  + over facts-file: read where it first bears
- facts-file: every fact in the files of facts, cited from the decisions
  + over inline: every fact found in one place

Decision assumed-mark: Is a fact that is assumed, not known, marked, and how?

Chosen: marked-only, because whoever follows a decision sees which of its premises are taken rather than established (C:same-reasoning), the mark saying nothing of whether a fact holds (C:facts-as-found); unmarked keeps one form for every fact (C:agents-read), a saving smaller than knowing how firmly a decision rests; what would overturn an assumed fact is a later fact, which revises what rests on it whether foreseen or not (C:facts-as-found), and with-settling writes in advance a list that is never whole {F:predictions-incomplete (assumed): a list of what would overturn a fact, written in advance, leaves things out, and reads as if what it leaves out would not matter}.

Options:
- marked-only: marked assumed
  + over unmarked: shows which premises are taken, not established
  + over with-settling: claims nothing about what has not been found
- with-settling: marked assumed, with what would settle or overturn it
  + over marked-only: what to look for, written beside it (C:agents-read)
  + over unmarked: which premises are taken, and what to look for
- unmarked: declared as any fact, with no mark
  + over marked-only, with-settling: one form for every fact (C:agents-read)

Decision record-ids: How is a record referred to?

Chosen: stable-ids, because an agent following a reason must look up every reference whose name says nothing, within its limited context (F:context-limited), more than the length a number saves (C:agents-read); positions are no option, since a record is never reworded (D:rewording), so a reference by position would go false with every move (C:derive-and-evolve).

Options:
- stable-ids: an id of lowercase words naming the record, unique in its kind, never reused
  + over numbers: says what it names, followed without a lookup
- numbers: a number for each record, never reused
  + over stable-ids: shorter (C:agents-read)

Decision implementation-names: Does a record name what exists only in one implementation?

Chosen: none, because a record is never reworded (D:rewording) while such names change with work that revises no decision, so a record naming them goes false (C:derive-and-evolve) {F:names-voided: wf-agents' records as moved in on 2026-10-31 held 99 records naming code paths or step numbers, which a rename or a renumbering makes false, as counted on 2026-11-01}; named points straight into the code (C:agents-read), but coherence comes first (C:precedence).

Options:
- none: a step or a part named by what it does
  + over named: stays true across renames and renumbering
- named: paths, files, functions, tables and step numbers named as they are
  + over none: points straight at the code (C:agents-read)

Decision context-words: Does a record use words whose meaning comes from where or when it was written?

Chosen: none, because a record is never reworded (D:rewording) and is read long after it is written by agents who carry nothing from then but what is written {F:agents-no-memory: an agent carries nothing from one session to the next but what is written, as seen in every agent working on the records to 2026-11-01}, so such a word loses its meaning for good, and the reason it carries can no longer be checked against its premises (C:derive-and-evolve) {F:context-words-voided: wf-agents' records as moved in on 2026-10-31 were full of words and marks bound to their context and time, such as step numbers a renumbering voids, as found on 2026-11-01}; bound is shorter and natural to write (C:agents-read), but coherence comes first (C:precedence).

Options:
- none: no word taking its meaning from a conversation, card or work, or from when it was written
  + over bound: means the same to every later reader
- bound: words as they came, such as "until now" or "option B"
  + over none: shorter and natural to write (C:agents-read)

Decision set-numbers: Are the numbers a project sets written in its records?

Chosen: configuration, because a record is never reworded (D:rewording), so a number tuned without a new reason would leave it false (C:derive-and-evolve); recorded shows every number beside its decision (C:agents-read), but coherence comes first (C:precedence). A number that was itself a real choice is a decision of its own, recorded as one.

Options:
- configuration: a number set is configuration, written in the records only when the number itself was a real choice
  + over recorded: tuned freely, the records staying true
- recorded: every number set written in the decision it belongs to
  + over configuration: every number found beside its reason
