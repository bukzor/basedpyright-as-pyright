# Thin entry, thick portable core

The entry point — a GitHub Actions job, a `make` target, a human at a shell, a
cron robot — does nothing but supply a SHA and credentials and call one verb. All
logic lives in the scripts under `lib/`.

This is what makes the system agnostic to its UI and trigger: every trigger
funnels into the same verb, so a new CI provider needs new
[providers/](quarantine-the-platform-surface.md) only — never a new release path.
The proof is that the entry points collapse to one line:

    lib/ci/release "$(git rev-parse HEAD)"   # human or robot, at a shell
    lib/ci/release "$SHA"                     # the whole CI job, minus plumbing

Be agnostic about the entry point as much as possible, and no more: the trigger
itself is *supposed* to vary — don't abstract it, just make it funnel inward. See
[mechanism-policy-split](mechanism-policy-split.md) for where the logic lives.
