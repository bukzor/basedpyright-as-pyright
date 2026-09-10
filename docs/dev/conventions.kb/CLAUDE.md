# conventions.kb — maintenance guide

## What belongs here

One concrete, repo-specific convention per file: a naming or layout choice a
maintainer must follow to keep the CI/CD scripts consistent. The convention is
the *what*; it states the rule and shows the shape.

## What does not

- The reasoning behind a convention — that lives in `../principles.kb/`. Link to
  it; don't restate it.
- One-off decisions with alternatives and context — those are `docs/adr/`.

## When to add

When a new naming or layout rule is settled. Keep each file to one convention so
`ls` stays a useful index.
