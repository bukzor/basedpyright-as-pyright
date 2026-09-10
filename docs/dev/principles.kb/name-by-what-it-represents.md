# Name by what it represents, not its type

You would never name a variable `int`. The same applies to directories and
scripts: name them for the thing, not the category.

- `providers/github/`, not `adapters/` — "adapter" is a type; "github" is the
  thing.
- `lib/git/`, `lib/pypi/`, `lib/dist/` — the subject each facility acts on — not
  a catch-all `lib/utils/` or `lib/helpers/`.

The payoff compounds where `ls` is discovery: a reader infers content from the
name. When a type-named bucket starts to strain, that strain is the signal to
split it by represented subject.
