# Release request refs

A release is requested by pushing a branch:

```
triggers/release/vX.Y.Z
```

- **`triggers/`** — the ref is a verb, not a line of development. Anything under
  this namespace exists to start a pipeline, and the pipeline deletes it once
  consumed. `release/*` is deliberately avoided: it collides with the widespread
  convention for long-lived release _maintenance_ branches, so every tool and
  reader would mis-classify it.
- **`vX.Y.Z`** — the version the pusher believes they are releasing. It is an
  assertion, not a source; `lib/ci/require-releasable` compares it against
  [the changelog](changelog-names-the-version.md) and refuses on disagreement.

Success is recorded by the pipeline pushing the `vX.Y.Z` tag. A tag ruleset
admits only the release identity, so the record cannot be written by hand:
[no-human-bypass](../principles.kb/no-human-bypass.md).

The asymmetry is the point. A request is cheap and revocable — delete the branch
and nothing is burned. The record is neither, so nothing but the pipeline may
write one.
