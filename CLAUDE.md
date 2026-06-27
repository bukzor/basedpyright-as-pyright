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
- ✅ **Python 3.13+** requirement

## Project Setup

This project was generated from a copier template. The template has already been
configured with your project details:

- Project name: basedpyright-as-pyright
- Description: Redirect the pyright engine to basedpyright, gated by the PYRIGHT env var.
- Python version: 3.13

To add dependencies, edit `pyproject.toml` and run `uv sync`.

## Pre-commit Hooks

The template includes local pre-commit hooks that use `uv run` to ensure
consistent virtual environment usage:

- **black**: Auto-formats Python code
- **pyright**: Type checking (runs on whole repo for thorough checking)

Both hooks will run before every commit to maintain code quality.
