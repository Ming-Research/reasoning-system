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

Chosen: options-weighed, because whether each option beats each other in something can then be checked (C:derive-and-evolve), which prose-rejected hides {F:rejected-without-gains: none of the 117 rejected items in wf-agents' records as moved in on 2026-10-31 said what the option did better, as counted on 2026-11-01}, while naming each option's gains and costs exposed what prose missed {F:gains-expose: rewriting twelve decisions of wf-agents' records as moved in on 2026-10-31 with each option's gains and costs named exposed missing options, padded ones, missing premises and a revision with no changed base, on 2026-11-01}; prose-rejected is shorter (C:agents-read), but coherence comes first (C:precedence).

Options:
- options-weighed: the question, what it arises under, the choice with its weighing, and the options weighed, each on its own
  + over prose-rejected: whether each option beats each other in something shows
- prose-rejected: the choice with its reasons, and the approaches rejected with why
  + over options-weighed: shorter (C:agents-read)

Decision fact-place: Where is a fact declared?

Chosen: inline, because a fact is read where its reasoning is each time a decision first resting on it is read, while every fact is sought in one place only when a new fact must name the one it follows (C:agents-read); a fact carrying much data is kept in a file of facts all the same, since inline it would bury the reasoning it serves.

Options:
- inline: in the reasons of the decision first resting on it
  + over facts-file: read where it first bears
- facts-file: every fact in the files of facts, cited from the decisions
  + over inline: every fact found in one place

Decision record-ids: How is a record referred to?

Chosen: stable-ids, because an agent following a reason must look up every reference whose name says nothing, within its limited context {F:context-limited: an agent holds a limited context, which the records and the code it reads share}, more than the length a number saves (C:agents-read); positions are no option, since a record is never reworded (D:rewording), so a reference by position would go false with every move (C:derive-and-evolve).

Options:
- stable-ids: an id of lowercase words naming the record, unique in its kind, never reused
  + over numbers: says what it names, followed without a lookup
- numbers: a number for each record, never reused
  + over stable-ids: shorter (C:agents-read)
