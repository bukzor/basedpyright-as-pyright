# ADR 0001 — Redirect the `pyright` engine to a fork (basedpyright), gated by `$PYRIGHT`

- Status: Accepted
- Date: 2026-06-24
- Deciders: bukzor

## Context

We want a fork of pyright — basedpyright — to back **everything** that expects
pyright.

### Goals

- **Cover every mode of pyright use** through a *single* redirect mechanism (if
  possible): the `pyright` CLI, `python -m pyright`, `import pyright`, the
  language server, and whatever else reaches for pyright.
- **No per-project futzing.**
- **Opt-in, explicit, reversible.** Redirecting one tool's engine to a fork is
  unusual; it must be a deliberate, visible, undoable act — never silent ambient
  behavior. This is what the `export PYRIGHT=basedpyright` gate buys.

### Non-goals

- **Generalizing to arbitrary other forks.** The `PYRIGHT` variable happens to
  name its target, so the mechanism is not hostile to it — but supporting other
  forks is not designed for and not a goal.

The motivating consumers are the editor / Claude Code language server, the CLI,
and `pytest-pyright` typesafety tests run in CI (express type-relevant
assertions; regression-test weak typing). `pytest-pyright` is the initial,
currently-primary driver, but the CLI and langserver follow right behind and rank
coequal — the mechanism must serve all of them, not overfit to the CI case.

The obstacle is that there are *two different "pyrights"*, and consumers bind to
the **wrapper's** API:

- **(W) the `pyright` PyPI wrapper** (RobertCraigie): a rich Python API —
  `pyright.run() -> CompletedProcess`, `cli`, `langserver`, `errors`, `node`,
  `_utils` — that locates Microsoft pyright's JS engine and runs it. `pytest-pyright`
  binds to this: it does `import pyright; pyright.run('--outputjson', ...)`.
- **(B) `basedpyright`**: the actual fork. Its *engine* is JS
  (`index.js`, `langserver.index.js`); its PyPI package is a **minimal, differently
  shaped launcher** (`basedpyright.pyright:main`) with **no `run`/`cli`/`errors`**.

Both (W) and (B) are merely launchers around a JS engine — that split is the
crux, and is unlike pure-Python forks (mypy, Pillow) where the fork *is* the
implementation.

## Decision

Ship a small standalone package that, **gated by the `PYRIGHT` environment
variable**, makes the genuine `pyright` wrapper (W) run a fork's engine (B).

We keep (W) entirely intact and swap **only its engine seam**. Both `cli.run`
and `langserver.run` resolve their JS via `pkg_dir = install_pyright(...)` then
run `pkg_dir / "index.js"` (resp. `langserver.index.js`). basedpyright's
distribution directory contains files of **those exact names**. So redirecting
`install_pyright()` to return `Path(basedpyright.__file__).parent` makes the
*entire* wrapper — `import pyright`, `pyright.run`, the CLI, the language server,
`python -m pyright` — drive basedpyright, with **zero symbol mirroring**.

`import pyright` still returns the real, full wrapper; the engine underneath is
basedpyright.

### The `PYRIGHT` contract (parallels `COVERAGE_PROCESS_START` / `SETUPTOOLS_USE_DISTUTILS`)

- **unset** → no-op; real pyright; near-zero startup cost.
- **`PYRIGHT=basedpyright`** → redirect the engine to basedpyright.
- The variable both **gates** and **names** the target — supporting other forks
  is a non-goal (see above), not a feature we are building toward.

### Mechanism

1. **Standalone package** — like coverage.py's subprocess `.pth` once was:
   isolated, independently install/uninstall, minimal footprint.
2. **One-line `.pth`** (per the `site` single-line rule):
   `import basedpyright_as_pyright; basedpyright_as_pyright.install()`.
3. **`install()`** — modeled on setuptools `_distutils_hack`: read
   `os.environ.get("PYRIGHT")`; if it names a fork, register a `sys.meta_path`
   finder that lets the real `pyright` import proceed and then patches its engine
   seam (`_utils.install_pyright`) to the fork's dist dir. If unset, return
   immediately.
4. **Packaging** — hatchling `force-include` lands the `.pth` at the site-packages
   root so it is recorded in `RECORD` and removed by `pip uninstall`.

## Alternatives considered

- **α — alias `import pyright` → basedpyright's modules** (meta-path name
  redirect). *Rejected: it does not work.* basedpyright's PyPI package lacks the
  wrapper API (`run`/`cli`/`errors`), so `pytest-pyright` and similar break. The
  redirect transport is fine; the *target* is wrong.
- **Faithful façade** — a `pyright` package that re-exports `run`/`cli`/
  `langserver`/`errors`/… delegating to basedpyright. *Rejected:* N brittle
  seams that rot the moment either upstream changes; mirrors only the objects we
  thought of and lets the rest flounder.
- **Fork-as-name (basedmypy/Pillow/pycryptodome style)** — get basedpyright to
  ship under the `pyright` import name on PyPI. *Deferred:* it is the fork's call
  to make upstream, and pyright's launcher/engine split makes it less clean than
  for pure-Python forks. We may still pursue it upstream; this package is the
  local, immediate, low-rot answer.

## Consequences

**Positive**

- **Opt-in, explicit, reversible**: the redirect happens only under
  `export PYRIGHT=basedpyright`, is visible in the environment, and is undone by
  unsetting it. Unset is also zero-cost.
- Uniform: LSP, CLI, `import`, and `pytest-pyright` all served by basedpyright
  from one install.
- `import pyright` actually works — the full, faithful wrapper API, backed by the
  basedpyright engine. The single-seam, no-mirroring approach is how the current
  design achieves that; see Decision and Alternatives.

**Risks / mitigations**

- Couples to one internal seam (`pyright._utils.install_pyright`). It is a single,
  well-defined boundary; pin/test against it. Far smaller surface than a façade.
- The `.pth` runs at **every** interpreter start — mitigated by the env-gate
  returning immediately when `PYRIGHT` is unset.
- `.pth` handling is installer-specific (notably `uv` has been reported to mangle
  `.pth` differently from `pip`). **Test matrix: install + uninstall under both
  `pip` and `uv`, asserting the `.pth` appears in `RECORD` and is removed.** Avoid
  setuptools `data_files` (wrong install scheme directory).
- Startup-hook "magic": mitigated by being a small, env-gated, standalone,
  documented package.

**Open**

- Whether `pyright.__pyright_version__` should also report basedpyright's version
  (the CLI banner already does).

## Implementation & repository

- Repo `basedpyright-as-pyright`, **public**, created with `gh repo create --public`, at
  `~/repo/github.com/bukzor/basedpyright-as-pyright` (self-owned-repo convention).
- **Tag the pristine scaffold first.** Commit the unedited copier output as
  commit #1 and `git tag scaffold-baseline` *before any hand-edits*. Then
  `git diff scaffold-baseline..HEAD` later yields the exact template delta to
  harvest upstream — a clean baseline that cannot be reconstructed once edits
  and scaffold output entangle. (Feeds the template-harvest task:
  `template.python-project/.claude/todo.kb/2026-06-27-000-harvest-template-improvements-from-basedpyright-as-pyright.md`.)
- **Honor the conventions in `~/repo/github.com/bukzor/template.python-project`**
  (the repo is scaffolded from it via copier: `pyright`/`pytest-pyright`,
  `bin/pnpm-run`, `.envrc`, pre-commit, `typesafety/`, etc.). Do not redefine
  them here; honor them.
- **Caveat — the template is app-form, not lib-form.** It ships no
  `[build-system]` and a root `main.py` rather than an installable package, so
  it cannot supply the distribution bits this project needs (hatchling
  build-system, importable `basedpyright_as_pyright` package, `force-include`
  of the `.pth`). Adding those here is *supplying what the template omits*, not
  redefining its conventions. Tracked upstream as a `project_type: app | lib`
  copier question (`template.python-project/.claude/todo.kb/2026-06-24-000-copier-projecttype-app--lib-question.md`).

## References (prior art)

- **setuptools `_distutils_hack`** — `.pth`-triggered `sys.meta_path` finder that
  makes `import distutils` resolve to setuptools' vendored copy; gated by
  `SETUPTOOLS_USE_DISTUTILS`. The near-exact template for this redirect.
- **coverage.py** — `.pth` containing `import coverage; coverage.process_startup()`,
  gated by `COVERAGE_PROCESS_START`; canonical "run code at every interpreter
  start, env-gated" precedent (and once a standalone package).
- **CPython `site`** — `.pth` lines beginning with `import` are executed at
  startup, expressly "to load 3rd-party import hooks"; `sitecustomize`/`usercustomize`.
- **Fork-as-name precedents** — basedmypy (installed in place of `mypy`), Pillow
  (`PIL`), pycryptodome (`Crypto`) / pycryptodomex (`Cryptodome`), mysqlclient
  (`MySQLdb`).
- **Runtime aliasing** — `pymysql.install_as_MySQLdb()` (`sys.modules`), `six.moves`,
  `python-future` `install_aliases()`.
