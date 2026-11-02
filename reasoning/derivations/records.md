Decision rewording: Is the text of a record ever reworded?

Chosen: never, because only so can the records' growth be checked mechanically from one state to the next (C:derive-and-evolve), while keeping-meaning needs a judgment on every edit that the meaning held, and lets it drift unseen; current wording serves the agents reading the records (C:agents-read), but coherence comes first (C:precedence).

Options:
- never: a change is a new record, or a revision that keeps what it replaces
  + over keeping-meaning: growth checked mechanically, nothing drifting unseen
- keeping-meaning: wording may change where the meaning stays, as when a name changes
  + over never: the wording kept current for the agents reading it

Decision record-medium: In what medium are the records written?

Chosen: plain-text, because the agents read and write the records as they do prose, at every work that meets a decision (C:agents-read), and the form a check reads is a few lines of grammar, which it reads as exactly as a standard parser reads data; structured-direct, which the decision first missed {F:medium-option-missed: the decision on the records' medium did not weigh data read and written directly, with no rendered view, as a review found on 2026-11-02}, is parsed by a standard parser in any language, sparing a project's tools that read the records' form a parser of their own {F:project-parses-records: wf-agents' engine splits the records by their heads itself, to compare a card's revision, as of 2026-11-01} (C:efficient), but puts the reasons, most of a record, into quoted strings {F:quoted-reasons (assumed): agents writing long reasons into quoted strings of data make quoting errors that prose does not}, read and written less as prose (C:agents-read), while the records are read and written at every work and parsed by a project's tools seldom; structured-data adds a rendered view, with costs the agents bear {F:structured-costs (assumed): records kept as data with a rendered view bring noisy merges, quoting errors by agents and a second artifact to keep in step}.

Options:
- plain-text: plain text in a fixed form a check reads
  + over structured-data: read and written as prose, one artifact
  + over structured-direct: read and written as prose (C:agents-read)
- structured-data: data, JSON or TOML, read through a rendered view
  + over plain-text: parsed exactly, with no grammar of its own
  + over structured-direct: read through a view made for reading (C:agents-read)
- structured-direct: data, TOML or YAML with one field to a line, read and written directly
  + over plain-text: parsed by a standard parser in any language, with no grammar of its own (C:efficient)
  + over structured-data: one artifact

Replaced:
- plain-text -> plain-text: plain-text, because the agents read and write them as they do prose (C:agents-read), and the form a check reads is a few lines of grammar; structured-data parses exactly (C:agents-read), but with costs the agents bear F:structured-costs.; replaced because F:medium-option-missed

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
