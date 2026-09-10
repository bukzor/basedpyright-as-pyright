# Self-guarding effects

Every effect re-checks its own invariants before acting; it does not trust the
orchestration to have checked. `ensure-published` itself calls
`require-releasable` before uploading, so there is no path — wrong UI, a human in
a hurry, a misordered script, a careless future workflow — that can publish an
un-green or unreachable SHA.

The guard is co-located with the dangerous action, so bypassing the guard
requires bypassing the action. That is the difference between "the pipeline is
careful" (hope) and "the operation is incapable of misfiring" (the goal).

This is [fail-closed](fail-closed-never-quietly-wrong.md) applied at the unit
level, and it is what makes [thin entry points](thin-entry-thick-core.md) safe:
the safety lives in the verb, not in the caller. Its system-level counterpart is
[no-human-bypass](no-human-bypass.md): a self-guard only binds callers that go
through the script, so access control must ensure there is no other door.
