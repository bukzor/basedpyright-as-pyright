# Mechanism outside lib/ci, policy inside it

- **Mechanism** — the raw, reusable operations: tag↔version, "is this SHA
  reachable from `main`?", "is this version on the index?", build. These live in
  subject-named directories *outside* `lib/ci/` (`lib/git/`, `lib/pypi/`,
  `lib/dist/`) because a developer wants them at a terminal with no CI involved.
  A facility only a robot ever runs rots.
- **Policy** — the gating *compositions* that encode our CI/CD rules
  (`require-releasable`, `ensure-published`, `release`, `reconcile`). These live
  in `lib/ci/`. They stay thin because the pieces they compose are sharp.

Pushing facilities outside `lib/ci/` is deliberate: it lets them be reused in any
context where they apply. See [lib-layout](../conventions.kb/lib-layout.md) for
the directory map and [tiny-single-responsibility](tiny-single-responsibility.md)
for why the pieces stay small.
