---
managed-by: Skill(llm-subtask)
cost-benefit-sweh:
  timebox:
    "@value": 0.5
    rationale:
      "duplicate-shaped: canonical home is the template harvest task; residual
      here is verify-and-flip when upstream lands"
    confidence: unsure
  benefit-2w:
    "@value": 0.1
    rationale:
      bookkeeping only; the substantive value is rated on the template side
    confidence: unsure
---

# Upstream template fixes found building this repo

Fixes for the upstream template (`template.python-project`), surfaced while
scaffolding and building this project. All three are visible in
`git diff scaffold-baseline..HEAD`. Port them upstream — canonical home is the
template's harvest task
(`template.python-project/.claude/todo.kb/2026-06-27-000-harvest-template-improvements-from-basedpyright-as-pyright.md`).

- [ ] **`project_type: app | lib` copier question** — the scaffold is app-form
      (root `main.py`, no `[build-system]`); a library needs a build-system +
      package layout. Added here by hand.
- [ ] **`pytest-pyright` dev pin is unresolvable** — template pins `>=0.0.7`,
      which does not exist on PyPI (only `<=0.0.6`); the scaffolded dev env
      can't resolve as shipped. Lowered to `>=0.0.6` here.
- [ ] **no CI is scaffolded** — the template's workflows live outside
      `copier-template/`, so generated repos get no `.github/workflows`. Added
      `ci.yml` (strict pyright + pytest) and `dependabot.yml` here.

## Release/CD back-port (2026-09-10)

Building the PyPI release pipeline here (ADR 0002) surfaced a much larger set,
written up upstream rather than duplicated here:
`template.python-project/.claude/todo.kb/2026-09-10-000-port-the-release-pipeline-from-basedpyright-as-pyright.md`.

The two findings worth knowing without opening it:

- The template already _mandates_ mechanisms it never shipped —
  `require-no-platform-leak`, `providers/<name>/get-context`, the
  `get`/`require`/`ensure` verbs. This repo's `lib/` is their first
  implementation.
- This repo's `docs/dev/principles.kb/` unknowingly restates the template's
  `docs/dev/technical-policy.kb/` nine times over. Direction of the dedupe is
  undecided; a generated repo can't link into the template at runtime, so the
  shared home may be `~/.claude/design-rules.kb/`.
