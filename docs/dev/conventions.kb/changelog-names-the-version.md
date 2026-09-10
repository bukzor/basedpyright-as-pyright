# The changelog names the version

`CHANGELOG.md` is where a release version is authored.
`lib/changelog/get-version` prints the topmost heading matching `## X.Y.Z`, and
that is the version a release publishes.

```markdown
## Unreleased ← not a version; skipped

## 0.1.1 ← this is what releases

## 0.1.0
```

Deciding the version in this file means deciding it in a reviewed change rather
than at the moment someone pushes, and it gives the number a place to sit next
to the reason for it. Work with no version yet goes under `## Unreleased`, which
cannot be released — a changelog holding only unreleased work makes
`get-version` fail rather than guess.

Why the number lives in one authored place at all:
[single-source-of-truth](../principles.kb/single-source-of-truth.md).
