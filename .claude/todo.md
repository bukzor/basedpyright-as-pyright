---
managed-by: Skill(llm-subtask)
status: active
---

# Upstream template fixes found building this repo

Fixes for the upstream template (`template.python-project`), surfaced while
scaffolding and building this project. All three are visible in
`git diff scaffold-baseline..HEAD`. Port them upstream — canonical home is the
template's harvest task (`template.python-project/.claude/todo.kb/2026-06-27-000-harvest-template-improvements-from-basedpyright-as-pyright.md`).

- [ ] **`project_type: app | lib` copier question** — the scaffold is app-form
      (root `main.py`, no `[build-system]`); a library needs a build-system +
      package layout. Added here by hand.
- [ ] **`pytest-pyright` dev pin is unresolvable** — template pins `>=0.0.7`,
      which does not exist on PyPI (only `<=0.0.6`); the scaffolded dev env
      can't resolve as shipped. Lowered to `>=0.0.6` here.
- [ ] **no CI is scaffolded** — the template's workflows live outside
      `copier-template/`, so generated repos get no `.github/workflows`. Added
      `ci.yml` (strict pyright + pytest) and `dependabot.yml` here.
