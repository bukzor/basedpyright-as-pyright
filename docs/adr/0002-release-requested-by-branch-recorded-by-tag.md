# ADR 0002 — A release is requested by a branch and recorded by a tag

- Status: Accepted
- Date: 2026-09-10
- Deciders: bukzor

## Context

This repo needed to publish to PyPI without a human ever holding registry
credentials. Trusted publishing (OIDC) settles the credential half. What took
two passes is the _trigger_: which act starts a release, and what the git tag
means afterward.

The first implementation triggered on `push: tags: ["v*"]`. It worked -- 0.1.0
reached PyPI that way on 2026-09-10 -- but it contradicts the design rules
already written down here:

- [no-human-bypass] wants tag creation restricted to the release identity. A
  tag-triggered pipeline requires the opposite: a human must push the tag, so
  the gate can never be turned on.
- [commit-point] wants the tag written _last_, as the record that a release
  succeeded. A trigger is written first, by definition.
- [single-source-of-truth] wants the version derived from the tag rather than
  hand-edited. Combined with a human-pushed tag, that means the human types the
  released version directly into the ref name -- the one number that can never
  be corrected afterward.

Under a tag trigger these three cannot all hold. Something else has to carry the
request.

## Decision

**The branch is the request; the tag is the receipt.**

A release is started by pushing `release/vX.Y.Z`. The pipeline then:

1. refuses if `vX.Y.Z` already exists on the remote (a released version is
   immutable, so re-releasing one is always a mistake);
2. refuses if the SHA is not an ancestor of `main` (only main has passed CI);
3. runs strict `pyright` and `pytest` -- CI never fires on a release ref, so
   this is the only gate between the tree and the index;
4. refuses if the tree is dirty (see below);
5. creates the tag **locally**, builds, and uploads to TestPyPI;
6. promotes that same artifact -- not a rebuild -- to PyPI;
7. **pushes the tag**, then deletes the request branch.

The version comes from `hatch-vcs`: `pyproject.toml` carries
`dynamic = ["version"]` and no number at all. The local tag in step 5 is what
makes the build's version exact.

`workflow_dispatch` remains, as a rehearsal only: it takes a required `version`
input, stops after TestPyPI, and additionally probes that PyPI accepts this
workflow as a publisher (minting an OIDC token that is never used). It never
uploads to PyPI and never writes a tag.

### The release identity is a deploy key

A tag ruleset blocks creation, update, and deletion of `v*` for everyone. The
pipeline needs to be the exception, and on a **user-owned** repo it cannot be
`GITHUB_TOKEN`: adding the GitHub Actions app as a bypass actor is rejected with
`Actor GitHub Actions integration must be part of the ruleset source or owner organization`
-- Integration bypass is an organization feature.

So the release identity is a write-scoped **deploy key**, bypassed via
`actor_type: DeployKey`, with the private half in the `RELEASE_TAG_SSH_KEY` repo
secret and used only by the final `tag` job. `GITHUB_TOKEN` keeps default
permissions; no job is granted `contents: write`.

## Alternatives considered

- **Tag-triggered release** (the first implementation). _Rejected:_ incompatible
  with tag protection, and it makes the human the author of the version number.
  It is what shipped 0.1.0; this ADR replaces it.
- **`workflow_dispatch` as the release trigger**, version as an input.
  _Rejected:_ the intent then exists only in an Actions log -- not a ref, not
  attributable in git history, not reviewable, and not revocable by deleting
  something.
- **`GITHUB_TOKEN` plus an Integration bypass actor.** _Rejected:_ unavailable
  here (HTTP 422, above). Would be the better choice under an organization.
- **A repository-admin bypass actor.** _Rejected:_ the admin is the human the
  rule exists to stop.
- **`SETUPTOOLS_SCM_PRETEND_VERSION` instead of a local tag.** _Rejected:_ the
  local tag is what `hatch-vcs` already wants, and it is the same object the
  release later pushes -- so what was built and what is recorded cannot drift.
- **Publishing straight to PyPI with no TestPyPI leg** (what `bukzor-tools` and
  `typed-json` do). _Rejected here:_ the rehearsal is what lets [build-once]
  promote a _checked_ artifact rather than a hoped-for one.

## Consequences

**Positive**

- Every principle above holds simultaneously: the tag is written last, by the
  release identity, and is the only place a version number is recorded.
- The dangerous act is revocable. A wrong `release/v*` branch is deleted and
  nothing is burned; only a successful upload is irreversible.
- A dispatch rehearses the exact artifact, including the registry handshake,
  without spending a version.

**Risks / mitigations**

- **A long-lived credential now exists.** Mitigated by scope: one repo, write
  access, used by one job to push one ref. Rotating it is deleting the deploy
  key and re-running `gh secret set`.
- **`hatch-vcs` answers a dirty tree with a dev version**
  (`0.1.1.dev0+g773f3b1`) rather than an error, and PyPI rejects such versions
  -- loudly, but late. Mitigated by the clean-tree check before the build and a
  filename check after it.
- **The tag job can fail after a successful upload**, leaving a published
  version with no tag. Mitigated by making that job last and independently
  re-runnable (`gh run rerun --job`), so recovery never re-publishes.
- **`hatch-vcs` needs git metadata at build time.** Installing from a released
  sdist is unaffected (the version is baked into `PKG-INFO`), but building from
  an unpacked tarball without `.git` fails.

**Open**

- 0.1.0 shipped without `py.typed` (the file is untracked), so downstream type
  checkers ignore this package's annotations. Fixed by committing it and
  releasing 0.1.1.

## Related

- [ADR 0001][adr-0001] -- what this package does and why it exists.
- Design rules this decision serves: [no-human-bypass], [commit-point],
  [single-source-of-truth], [build-once], [invariant-gate-audit].

[adr-0001]: 0001-redirect-pyright-engine-to-a-fork.md
[no-human-bypass]: ../dev/principles.kb/no-human-bypass.md
[commit-point]: ../dev/principles.kb/commit-point-and-reconciliation.md
[single-source-of-truth]: ../dev/principles.kb/single-source-of-truth.md
[build-once]: ../dev/principles.kb/build-once-promote-unchanged.md
[invariant-gate-audit]: ../dev/principles.kb/invariant-gate-audit-triad.md
