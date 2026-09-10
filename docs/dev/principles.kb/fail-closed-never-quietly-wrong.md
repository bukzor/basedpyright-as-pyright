# Fail closed; never the wrong thing, quietly

Doing it wrong must be an error or impossible — never a quiet wrong outcome. The
contract differs by [verb kind](../conventions.kb/verb-taxonomy.md):

- a `get-` that cannot determine its answer **errors**; it never prints `""` or a
  default a caller mistakes for success.
- a `require-` treats "pending" and "required check missing" as **failure**, not
  pass. This closes the vacuous-pass hole.
- an `ensure-` that finds *divergent* state **errors loudly** — it never
  overwrites and never silently skips.

The one allowed silence is the *right* thing quietly: an idempotent no-op when
state already matches. Forbidden is the *wrong* thing quietly: a divergent
overwrite, a skipped check, a swallowed error. See
[obvious-failure-punting](obvious-failure-punting.md) for how this property
licenses deliberate shortcuts.
