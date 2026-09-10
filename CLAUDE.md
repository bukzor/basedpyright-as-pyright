--- # workaround: anthropics/claude-code#13003
triggers:
    - when: creating or maintaining a .kb/ collection
      read: skill://llm-kb
git-caution: personal
---

# Claude Setup Instructions

This is a Python project optimized for Claude Code development.

## Quick Start

```bash
# Install development dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Test the setup
uv run pre-commit run --all-files
```

## Development Commands

- **Format code**: `uv run black .`
- **Type check**: `uv run pyright`
- **Run pre-commit**: `uv run pre-commit run`
- **Install package in dev mode**: `uv pip install -e .`

## Features Included

- ✅ **Pyright** in strict mode for type checking
- ✅ **Black** for code formatting
- ✅ **Pre-commit hooks** using `uv run` for consistent tooling
- ✅ **direnv** support with `.envrc`
- ✅ **Minimal gitignore** with only build products
- ✅ **Python 3.10+** requirement

## Project Setup

This project was generated from a copier template. The template has already been
configured with your project details:

- Project name: basedpyright-as-pyright
- Description: Redirect the pyright engine to basedpyright, gated by the PYRIGHT
  env var.
- Python version: 3.10+

To add dependencies, edit `pyproject.toml` and run `uv sync`.

## Pre-commit Hooks

The template includes local pre-commit hooks that use `uv run` to ensure
consistent virtual environment usage:

- **black**: Auto-formats Python code
- **pyright**: Type checking (runs on whole repo for thorough checking)

Both hooks will run before every commit to maintain code quality.

## Design knowledge base

`docs/dev/` holds the design knowledge base (llm-kb pattern). Load
`Skill(llm-kb)` before editing anything under it.

- `principles.kb/` — reusable CI/CD design principles: invariants, fail-closed
  behavior, portability across entry points, and the rules for punting work.
- `conventions.kb/` — concrete choices for this repo: the
  `get`/`require`/`ensure` verb taxonomy and the `lib/` directory layout.

Point-in-time decisions with context and alternatives live in `docs/adr/`.
