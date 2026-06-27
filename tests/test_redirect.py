"""End-to-end: with this package installed, a fresh interpreter routes pyright
to basedpyright iff ``$PYRIGHT`` names it.

This builds a wheel, installs it into a throwaway venv, and drives the *real*
entrypoints (`pyright` CLI and `python -m pyright`) — the most believable proof
that the ``.pth`` startup hook and the engine redirect work together. It
automates the four-quadrant manual check:

    {console script, python -m} x {PYRIGHT unset, PYRIGHT=basedpyright}
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def venv_bin(tmp_path_factory: pytest.TempPathFactory, wheel: Path) -> Path:
    """Install the wheel into a throwaway venv; return its ``bin/``."""
    env_dir = tmp_path_factory.mktemp("venv")
    subprocess.run(["uv", "venv", str(env_dir)], check=True)
    bin_dir = env_dir / "bin"
    subprocess.run(
        ["uv", "pip", "install", "--python", str(bin_dir / "python"), str(wheel)],
        check=True,
    )
    return bin_dir


def _version(argv: Sequence[str], *, pyright: str | None) -> str:
    """Run ``argv`` with ``PYRIGHT`` set/unset; return stdout."""
    env = {k: v for k, v in os.environ.items() if k != "PYRIGHT"}
    if pyright is not None:
        env["PYRIGHT"] = pyright
    proc = subprocess.run(argv, capture_output=True, text=True, env=env, check=True)
    return proc.stdout


def _argv(venv_bin: Path, entrypoint: str) -> tuple[str, ...]:
    if entrypoint == "console":
        return (str(venv_bin / "pyright"), "--version")
    return (str(venv_bin / "python"), "-m", "pyright", "--version")


@pytest.mark.parametrize("entrypoint", ["console", "module"])
def it_uses_real_pyright_when_unset(venv_bin: Path, entrypoint: str) -> None:
    out = _version(_argv(venv_bin, entrypoint), pyright=None)
    assert out.startswith("pyright "), out
    assert "basedpyright" not in out, out


@pytest.mark.parametrize("entrypoint", ["console", "module"])
def it_uses_basedpyright_when_set(venv_bin: Path, entrypoint: str) -> None:
    out = _version(_argv(venv_bin, entrypoint), pyright="basedpyright")
    assert "basedpyright" in out, out
