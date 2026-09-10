# principles.kb — maintenance guide

## What belongs here

One design principle per file: a reusable rule that guides *how* the CI/CD system
and its scripts are built, independent of any single entry point or provider. The
filename names the principle.

## What does not

- Concrete naming/layout choices — those are `../conventions.kb/`.
- Point-in-time architecture decisions with context/alternatives — those are
  `docs/adr/`.
- Implementation. A principle explains a rule; it does not contain the code.

## When to add

When a new rule is agreed with the user or derived in design discussion. If a
principle is general beyond this repo (e.g. a pure naming or process rule),
consider promoting it to `~/.claude/design-rules.kb/` instead of duplicating it
here.
