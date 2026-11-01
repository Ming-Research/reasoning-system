# Extension: reviewing the work against the decisions

For the review of a work whose code, specifications or configuration the decisions govern, once it is written. It looks
for where the work changes the design on its own: a shortcut, another method, more than was decided, a part dropped
unsaid. Work toward the decisions in steps is no departure: a decision carried out in part, so long as what is carried
out is as it says; a part left out of a rewrite to be carried out again, or an old approach still running while a
migration goes on, so long as the work says so and leaves what remains to do tracked where later work will find it, such
as in a comment or a document.

## 1. What to read

- The whole change, what it directly affects, and wherever an approach it replaces is still carried out.
- The decisions on the questions these meet, those the work adds or revises among them, with what each rejected and
  replaced.

## 2. What to check

For each change in the work:

1. **Nothing beyond the decisions.** Each real choice it makes, such as whether the project does something at all, is
   governed by a decision: name the decision. One none governs is a finding, a missing addition.
2. **Nothing otherwise.** What the change has the project do is as the decisions say: it carries out no option a
   decision rejected or choice one replaced, without a revision in the work. One that differs is a finding.
3. **Nothing dropped alone.** For what it deletes, and what it leaves of an approach it replaces, name the decisions
   touched. A part no longer carried out, or an old approach still running, that is not such a step, said and tracked,
   is a finding.

## 3. How to report

Each check gives its judgment, passed, a finding or not verified, and what it rests on. No evidence is no pass: a check
not verified says what evidence would settle it. A finding quotes the work and the decision it fails against, and says
what would resolve it.

## 4. Reviewing again

The review runs once over the whole work. The review again is given the findings and the checks not verified, the
answer to each and what changed since. It decides each check not verified, passed or a finding; it reviews only the
changes since that change a decision or rewrite logic or behaviour beyond a local repair, and what each touched; it
checks that every other change, listed by its author, is of neither kind; and it raises nothing outside these.
