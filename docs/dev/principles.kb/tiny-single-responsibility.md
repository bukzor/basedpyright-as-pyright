# Tiny, single-responsibility scripts

Each script does one thing and asserts one precondition. This is what meshes the
three ideals that otherwise conflict:

- **agnostic vs concrete** — the platform surface shrinks to a few named
  [providers](quarantine-the-platform-surface.md) instead of being smeared
  through a long procedure. You can see and lint the boundary.
- **fail-closed vs usable** — one responsibility is one local guard, total and
  obvious, instead of a big procedure with half-checked branches where the
  quiet-wrong path hides.
- **general vs specific** — small orthogonal verbs recombine into any workflow a
  user or system might want; a fat `do-the-release` fits only the one shape its
  author imagined.

The cost is real: more files, plus composition logic that must live somewhere (it
lives in the thin `lib/ci/` policy scripts, which stay thin because the pieces are
sharp). The win: "doing it wrong" stops being a discipline you maintain and
becomes a state the system can't represent.
