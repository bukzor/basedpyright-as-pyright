# No human bypass

The meta-invariant that makes every other one hold: only the release pipeline may
write to the prod registry or move release tags. If a human can hand-publish
(`twine upload`) or push a tag by hand, every
[self-guard](self-guarding-effects.md) and
[gate](invariant-gate-audit-triad.md) is moot — the dangerous action has a second
door with no lock.

Enforce it with access control, not etiquette: registry credentials live only in
the pipeline's environment (OIDC, short-lived), and tag-protection rules let only
the release identity create or move tags. A human *triggering* the pipeline is
fine; a human *being* the pipeline is not.

The audit that catches a breach is the packages-without-tags half of
[reconciliation](commit-point-and-reconciliation.md): a published artifact with no
release tag means something wrote to prod outside the pipeline.
