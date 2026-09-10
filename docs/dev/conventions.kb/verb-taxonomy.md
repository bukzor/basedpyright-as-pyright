# Verb taxonomy: get / require / ensure

A script's prefix encodes its failure and idempotency contract. The prefix is a
promise; [fail-closed](../principles.kb/fail-closed-never-quietly-wrong.md) is how
each one keeps it.

- **`get-X`** — pure read. Prints exactly one value to stdout (diagnostics to
  stderr, so `$(...)` stays clean); exits non-zero if the answer is unknowable.
  Never prints a default. No side effects.
- **`require-X`** — guard. The exit code is the truth; no side effects. "Pending"
  and "missing" count as failure, not pass.
- **`ensure-X`** — idempotent check-or-do. Fast-paths to a no-op if already
  satisfied; performs the action if not; **errors on divergence or
  impossibility** — never overwrites, never silently skips. This is the home of
  "idempotent-or-refuse" effects (`ensure-published`, `ensure-tagged`).
- **bare verb** (`build`, `publish`) — a raw effect, not guaranteed idempotent.
  It is conspicuous *by the absence* of a safe prefix: the missing
  get/require/ensure is the warning that it is not safe to blind-rerun.

No `do-` prefix. It is noise, and it would reassure-by-symmetry exactly the verbs
that deserve the least reassurance. Mark the safe cases; leave the sharp one bare.
