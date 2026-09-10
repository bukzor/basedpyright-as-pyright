# Commit point and reconciliation

You cannot get true atomicity across git and a package registry. Don't try.
Instead pick a commit point and make everything else idempotent and reconciled.

- **The tag is the commit point, written last.** `release` runs
  `require-releasable` → `ensure-built` → `ensure-published` (idempotent) → and
  only then writes the tag as the *record of success*. A tag therefore *means*
  "this was released," which makes "every release comes from a green SHA" true by
  construction rather than by hope.
- **Publish is idempotent and convergent.** Absent → publish; byte-identical →
  no-op; divergent → error (never overwrite). A crash mid-release leaves a
  recoverable, detectable state, never a silently inconsistent one.
- **Reconcile both directions.** An audit flags tags-without-packages (retry) and
  packages-without-tags (alarm — something bypassed the pipeline).

This is [the triad](invariant-gate-audit-triad.md) and
[fail-closed](fail-closed-never-quietly-wrong.md) applied to the release moment.
