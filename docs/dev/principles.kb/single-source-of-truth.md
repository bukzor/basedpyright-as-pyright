# Single source of truth (version)

A version number is _authored_ in exactly one place. Every other appearance of
it is derived from that place or checked against it — never independently typed.

Authored-once is the property that matters; "the tag is authoritative" is one
way to get it, not the rule itself. `pyproject.toml` _and_ a tag _and_
`__version__` drift because three numbers can be edited by three people. One
authored number, mechanically propagated, has nothing to keep in sync.

The corollary is what to do about the human who still has to say which version
to release: **let them state it, then check it.** A restatement that the system
verifies is not a second source — it is a [gate](invariant-gate-audit-triad.md),
and a disagreement between the two is the most informative failure available,
because it means someone's belief about the release is wrong before anything
ships.

See [commit-point-and-reconciliation](commit-point-and-reconciliation.md) for
how the tag is written as the record, and
[the triad](invariant-gate-audit-triad.md) for the audit that catches drift if
it somehow occurs.
