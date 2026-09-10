# Changelog

The topmost version heading is the version a release publishes — this file is
where a release version is decided, in a reviewed change, rather than at the
moment someone pushes. `lib/changelog/get-version` reads it.

Work that has not been assigned a version goes under `## Unreleased`, which is
not a version and cannot be released.

## Unreleased

## 0.1.1

### Fixed

- Ship `py.typed`, so downstream type checkers honor this package's annotations
  instead of ignoring them. Without it the 0.1.0 wheel was, to a type checker,
  untyped — which for a typing shim is most of the point.

### Changed

- A release is now requested by pushing `triggers/release/vX.Y.Z` and recorded
  by the pipeline pushing the `vX.Y.Z` tag. See
  [ADR 0002](docs/adr/0002-release-requested-by-branch-recorded-by-tag.md).
- The package version derives from the git tag (hatch-vcs); `pyproject.toml` no
  longer carries a number.

## 0.1.0

Initial release: redirect the `pyright` wrapper's engine to basedpyright, gated
by `PYRIGHT=basedpyright`. See
[ADR 0001](docs/adr/0001-redirect-pyright-engine-to-a-fork.md).
