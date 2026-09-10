# Quarantine the platform surface

Be agnostic as much as possible — and no more. Four things are irreducibly tied
to the platform and cannot be abstracted away, only quarantined:

1. context discovery (what SHA/ref; is this a PR?),
2. credential acquisition (OIDC vs a local keyring),
3. check-status query (the provider's Checks API),
4. the trigger itself (which is *supposed* to vary — let it).

These live under `lib/ci/providers/<name>/`, named for what they represent (the
platform), not their type. Everything downstream consumes the *normalized*
context a provider emits, never `$GITHUB_*` directly.

Enforce it: a `require-no-platform-leak` lint fails the build if any file outside
`providers/` mentions `GITHUB_`, `gh`, OIDC, or a registry host. The portability
invariant thus [fails closed](fail-closed-never-quietly-wrong.md) instead of
rotting. Today there is one provider, `github`; see
[obvious-failure-punting](obvious-failure-punting.md) for why hardcoding it is
safe.
