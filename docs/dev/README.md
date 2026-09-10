# Design knowledge base

Design rules for this project's CI/CD system, split by how long each stays true.
`principles.kb/` holds the reasoning — rules that would survive porting this
repo to another CI provider, another registry, or another language.
`conventions.kb/` holds the concrete choices that bind only this repo; each
names the principle it serves rather than re-arguing it. When the two disagree,
the principle is the older commitment and the convention is what moves.

Neither records a decision. Point-in-time choices — with their context, their
alternatives, and the reason the rejected ones lost — live in `docs/adr/`, which
is usually where a convention here came from.

What they describe is a vocabulary of tiny, single-responsibility scripts under
`lib/`, runnable by a human _or_ a robot. Entry points — GitHub Actions, `make`,
a shell, cron — stay thin: they supply arguments and call one verb, so the rules
of a release are answerable at a terminal rather than only inside CI.
