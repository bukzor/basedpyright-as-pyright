# Invariant / gate / audit triad

Three distinct things; never conflate them.

- **Invariant** — a property true of a *state* at all times. "main is always at a
  SHA whose exact tree passed CI." "Every published version is immutable."
- **Gate** — what preserves an invariant at a *transition*: branch protection,
  required checks, a merge queue, tag-protection rules.
- **Audit** — what *detects* that an invariant drifted anyway: a reconciliation
  job that flags a tag whose SHA isn't green, or a published artifact with no tag.

A gate without an audit is hope. Admin overrides, manual publishes, and deleted
tags all violate invariants the gate "guaranteed." So every invariant we name
gets both an enforcing gate and a drift-detecting audit. See
[commit-point-and-reconciliation](commit-point-and-reconciliation.md) for the
release-time instance.
