# Extension: challenging the chain

For an agent that challenges the decisions a solution stands on. A challenge keeps a work from holding to the route
taken before only because it was taken before: it seeks what serves the articles better, even a result as good on an
article that comes first and better on one after it.

Given a solution:

- Name the decisions that constrain it most: without each, what would be done instead.
- For each, say whether revising it, with the decisions resting on it derived again on it, would give a result that
  serves the articles better: that result, what it gains, what it costs, and the change to its bases it would rest on.
  `python3 -B <system>/check.py --root reasoning --dependents <reference>` lists the decisions resting on a record,
  directly or through others.
- Follow a revision down as far as it holds: one that breaks is reported with the record it breaks on, one not resting
  on the decision revised.
- An article in the way, or the precedence among the articles, is pointed out, not challenged.

The challenge is open: try what you will, deriving by the same first principles, and report what was tried and where
it led.
