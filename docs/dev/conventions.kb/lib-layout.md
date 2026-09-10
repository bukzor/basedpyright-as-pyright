# lib/ layout

`lib/` contains only directories. Two kinds:

- **Subject facilities** (mechanism) — `lib/git/`, `lib/changelog/`,
  `lib/pypi/`, `lib/dist/`. Reusable operations named for the subject they act
  on, usable by a human or a robot in any context, CI or not.
- **CI policy** — `lib/ci/`: the gating compositions, plus the platform
  quarantine under `providers/`.

```
lib/
  changelog/  get-version
  git/        require-reachable-from, require-clean-tree, require-tag-absent
  pypi/       publish, published
  dist/       build
  ci/
    providers/github/   get-context, get-check-status, get-publish-creds
    get-requested-version
    require-green, require-releasable, require-no-platform-leak
    ensure-published, ensure-tagged
    release, reconcile
```

Names here that do not exist yet are the shape they must take when they do.

Script names take their prefix from the [verb taxonomy](verb-taxonomy.md), which
is what makes a bare `ls` of these directories readable as contracts rather than
as a pile of utilities.

Subject directories rather than one `lib/ops/` bucket: this applies
[name-by-what-it-represents](../principles.kb/name-by-what-it-represents.md) and
keeps mechanism cleanly outside the
[policy](../principles.kb/mechanism-policy-split.md) layer. The split between
`lib/<subject>/` (raw) and `lib/ci/` (guarded, composed) _is_ the
mechanism/policy boundary.
