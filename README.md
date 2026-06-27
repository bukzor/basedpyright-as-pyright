# basedpyright-as-pyright

Make everything that expects **pyright** run **[basedpyright]** instead — the
editor language server, the `pyright` CLI, `python -m pyright`, `import pyright`,
and `pytest-pyright` — from a single install, with no per-project changes.

Opt-in and reversible: it does nothing until you `export PYRIGHT=basedpyright`,
and unsetting that variable restores stock pyright.

[basedpyright]: https://github.com/DetachHead/basedpyright

## Why

[basedpyright] is a fork of pyright with stricter checks and fixes, but lots of
tooling is wired to the name *pyright*: editor plugins shell out to
`pyright-langserver`, CI calls the `pyright` CLI, and `pytest-pyright` does
`import pyright; pyright.run(...)`. Pointing all of those at basedpyright
normally means N separate per-tool, per-project hacks.

The catch is that the two projects are shaped differently. The PyPI `pyright`
package is a *wrapper* with a rich API (`pyright.run()`, `cli`, `langserver`,
`errors`, …) that locates and runs Microsoft pyright's JavaScript engine.
basedpyright's PyPI package is a minimal launcher with none of that API — so you
can't just install it "as pyright". (For the full rationale and the alternatives
that don't work, see [`docs/adr/0001`](docs/adr/0001-redirect-pyright-engine-to-a-fork.md).)

## How it works

This package keeps the genuine `pyright` wrapper completely intact and swaps
**only its engine seam**. The wrapper resolves its JavaScript via one internal
function, `pyright._utils.install_pyright()`, which returns a directory
containing `index.js` / `langserver.index.js`. basedpyright ships files of those
exact names at its package root — so redirecting that one function to
basedpyright's directory makes the *entire* wrapper drive basedpyright, with no
API mirroring.

A `.pth` file (installed at the site-packages root, the same mechanism
coverage.py uses for subprocess coverage) runs a tiny startup hook in every
interpreter. When `PYRIGHT` is unset the hook returns immediately; when it names
a fork, the hook registers an import patch for the seam above. `import pyright`
still gives you the real, full wrapper — only the engine underneath changes.

## Install

```bash
pip install basedpyright-as-pyright
# or: uv pip install basedpyright-as-pyright
```

This pulls in both `pyright` (the wrapper it patches) and `basedpyright` (the
engine it redirects to).

## Use

```bash
export PYRIGHT=basedpyright
```

That's it. Now everything routes through basedpyright:

```console
$ pyright --version
basedpyright 1.39.9
based on pyright 1.1.411

$ python -m pyright --version
basedpyright 1.39.9
```

Unset `PYRIGHT` (or never set it) to get stock pyright back:

```console
$ pyright --version
pyright 1.1.411
```

### Per-project, with direnv

Because the switch is just an environment variable, [direnv] makes it automatic
and project-scoped — add it to a directory's `.envrc` and every shell, editor,
and language server launched from there inherits it:

```bash
# .envrc
export PYRIGHT=basedpyright
```

This is also the cleanest answer for editors: start your editor from a
direnv-enabled directory (or use its direnv integration) so the
language-server process picks up `PYRIGHT`. Keeping the switch in `.envrc` means
the choice lives with the project and is visible in version control.

[direnv]: https://direnv.net/

## Scope & guarantees

- **Opt-in, explicit, reversible.** Controlled entirely by the `PYRIGHT`
  environment variable. Unset is a near-zero-cost no-op.
- **Fail-open.** If anything goes wrong (e.g. basedpyright isn't installed), the
  hook silently falls back to real pyright rather than breaking interpreter
  startup.
- **Single target.** The `PYRIGHT` variable both gates *and* names the target;
  `basedpyright` is what's supported. Generalizing to arbitrary forks is a
  non-goal — the variable leaves the door open, but it isn't designed for.

## License

MIT — see [LICENSE](LICENSE).
