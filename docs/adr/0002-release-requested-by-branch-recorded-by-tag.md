# ADR 0002 — A release is requested by a branch and recorded by a tag

- Status: Accepted
- Date: 2026-09-10
- Deciders: bukzor

## Context

This repo needed to publish to PyPI without a human ever holding registry
credentials. Trusted publishing (OIDC) settles the credential half. What took
three passes is the _trigger_: which act starts a release, what decides the
version, and what the git tag means afterward.

The first implementation triggered on `push: tags: ["v*"]`. It worked -- 0.1.0
reached PyPI that way on 2026-09-10 -- but it contradicts the design rules
already written down here:

- [no-human-bypass] wants tag creation restricted to the release identity. A
  tag-triggered pipeline requires the opposite: a human must push the tag, so
  the gate can never be turned on.
- [commit-point] wants the tag written _last_, as the record that a release
  succeeded. A trigger is written first, by definition.

Under a tag trigger these cannot both hold, so something else has to carry the
request.

The second pass moved the request to a `release/v*` branch -- and left the
version number in the pusher's hands, one ref-name earlier. That is a real
improvement, since the act becomes revocable, but a smaller one than it appears,
and it still fails [single-source-of-truth]: a number typed at push time is
authored at push time, reviewed by nobody.

## Decision

**The branch is the request; the changelog is the truth; the tag is the
receipt.**

A release is started by pushing `triggers/release/vX.Y.Z`. The version in that
ref is an _assertion_, not a source: `CHANGELOG.md` decides the version, in a
reviewed change, and the pipeline refuses when the two disagree. Stating an
expectation the system then verifies is `git push --force-with-lease` applied to
releases -- the disagreement is the signal, because it means someone's belief
about what is shipping is wrong while that is still free to discover.

The pipeline then, via `lib/ci/require-releasable`:

1. refuses if the request's version and the changelog's disagree;
2. refuses if the tree is dirty -- hatch-vcs answers a dirty tree with a dev
   version rather than an error, so cleanliness decides what gets built;
3. refuses if that version is already released, since a published version is
   immutable and re-releasing one can only fail, later and louder;
4. refuses if the SHA is not reachable from the default branch, because only
   there has CI run.

It then runs strict `pyright` and `pytest`, tags **locally**, builds, uploads to
TestPyPI, promotes those same bytes to PyPI, and finally **pushes the tag** and
deletes the request branch.

`workflow_dispatch` remains as a rehearsal. It now takes **no inputs**: the
changelog names the version, so a rehearsal can invent nothing. It stops after
TestPyPI and additionally probes that PyPI accepts this workflow as a publisher,
minting an OIDC token that is never used.

### The gates live in `lib/`, not in YAML

[thin-entry-thick-core] says the CI job supplies a SHA and calls one verb. The
gates are therefore shell scripts under `lib/`, and the workflow calls
`lib/ci/require-releasable "$SHA" "$REQUEST_REF"`. That is what makes the
release rules runnable at a terminal, testable in `tests/release_gates_test.py`,
and portable to another provider -- and `lib/ci/require-no-platform-leak` fails
the build if anything outside `lib/ci/providers/` learns the platform's name.

Publishing itself stays a `pypa/gh-action-pypi-publish` step rather than a
`lib/pypi/publish` verb. Re-implementing the OIDC token exchange to satisfy the
pattern would trade a maintained, audited path for a hand-rolled one; this is a
[deliberate punt][punting], and it fails loudly the day a second provider
appears.

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
  with tag protection, and the tag would mean "someone wanted this" rather than
  "this shipped" -- a claim that is false whenever a run fails.
- **A versionless trigger** (`triggers/release`, version derived silently).
  _Rejected:_ it makes the release act blind -- you learn what you shipped by
  reading the tag afterward. Same machinery cost as checking an assertion, minus
  the check.
- **Deriving the version from conventional commits.** _Rejected for now:_ this
  repo's log is only loosely conventional (`sweh:`, `todo:`, `packaging:`, and
  bare sentences), so the derivation would be wrong from day one. A changelog
  entry is also a better audit trail than a commit-message convention.
- **`workflow_dispatch` as the release trigger**, version as an input.
  _Rejected:_ the intent then exists only in an Actions log -- not a ref, not
  attributable in git history, not reviewable, and not revocable by deleting
  something.
- **`GITHUB_TOKEN` plus an Integration bypass actor.** _Rejected:_ unavailable
  here (HTTP 422, above). Would be the better choice under an organization.
- **A repository-admin bypass actor.** _Rejected:_ the admin is the human the
  rule exists to stop.
- **`release/v*` as the request namespace** (the second pass). _Rejected:_ it
  collides with the widespread convention for long-lived release _maintenance_
  branches. See [release-request-refs].
- **`SETUPTOOLS_SCM_PRETEND_VERSION` instead of a local tag.** _Rejected:_ the
  local tag is what `hatch-vcs` already wants, and it is the same object the
  release later pushes -- so what was built and what is recorded cannot drift.
- **Publishing straight to PyPI with no TestPyPI leg** (what `bukzor-tools` and
  `typed-json` do). _Rejected here:_ the rehearsal is what lets [build-once]
  promote a _checked_ artifact rather than a hoped-for one.

## Consequences

**Positive**

- Every rule above holds at once: the tag is written last, by the release
  identity, and no version number is authored anywhere but the changelog.
- The dangerous act is revocable. A wrong request branch is deleted and nothing
  is burned; only a successful upload is irreversible.
- The gates run at a terminal and under `pytest`, so "would this release be
  allowed?" is answerable without pushing anything.

**Risks / mitigations**

- **A long-lived credential now exists** -- the price of removing the human from
  tag-writing, and the one thing the tag-triggered design did not need. Scoped
  to one repo, one job, one ref; rotation is deleting the deploy key and
  re-running `gh secret set`.
- **The tag job can fail after a successful upload**, leaving a published
  version with no tag. Mitigated by making that job last and independently
  re-runnable (`gh run rerun --job`), so recovery never re-publishes. This is
  exactly the packages-without-tags drift [commit-point] wants reconciled, and
  no audit job exists yet.
- **`hatch-vcs` needs git metadata at build time.** Installing from a released
  sdist is unaffected (the version is baked into `PKG-INFO`), but building from
  an unpacked tarball without `.git` fails.
- **Two runs for one version** would both build and then collide at the
  registry, after the irreversible half had begun for one of them. Mitigated by
  a `concurrency` group keyed on the ref.

**Open**

- No reconciliation audit yet: nothing detects a tag without a package, or a
  package without a tag. [the triad] calls a gate without an audit hope.
- `lib/pypi/` and `lib/dist/` remain unbuilt, so "build once, promote unchanged"
  is enforced by the workflow's shape rather than by a verb that could be run
  anywhere.

## Related

- [ADR 0001][adr-0001] -- what this package does and why it exists.
- Conventions this decision establishes: [release-request-refs],
  [changelog-names-the-version].
- Design rules it serves: [no-human-bypass], [commit-point],
  [single-source-of-truth], [build-once], [thin-entry-thick-core], [the triad].

[adr-0001]: 0001-redirect-pyright-engine-to-a-fork.md
[release-request-refs]: ../dev/conventions.kb/release-request-refs.md
[changelog-names-the-version]:
  ../dev/conventions.kb/changelog-names-the-version.md
[no-human-bypass]: ../dev/principles.kb/no-human-bypass.md
[commit-point]: ../dev/principles.kb/commit-point-and-reconciliation.md
[single-source-of-truth]: ../dev/principles.kb/single-source-of-truth.md
[build-once]: ../dev/principles.kb/build-once-promote-unchanged.md
[thin-entry-thick-core]: ../dev/principles.kb/thin-entry-thick-core.md
[the triad]: ../dev/principles.kb/invariant-gate-audit-triad.md
[punting]: ../dev/principles.kb/obvious-failure-punting.md
