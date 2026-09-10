# Build once, promote unchanged

An artifact is built exactly once, and the *same bytes* are promoted through
environments (staging → prod) — never rebuilt per environment. Rebuilding breaks
the invariant "what is in prod is what passed staging."

Corollaries:

- the version is derived once and carried, not recomputed downstream (see
  [single-source-of-truth](single-source-of-truth.md));
- promotion records which artifact is where, so "what is in prod right now?" has
  an authoritative answer;
- provenance ties the artifact back to its source SHA and build inputs, so a
  release is traceable and verifiable.
