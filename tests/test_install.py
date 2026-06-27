"""Acceptance: the redirect is active only while the package is installed —
under both ``pip`` and ``uv``.

Asserts observable behavior (which engine actually runs), not the ``.pth``
implementation detail. The uninstall assertion subsumes a file check: if the
``.pth`` survived uninstall, ``PYRIGHT=basedpyright`` would still route to
basedpyright, so "no effect after uninstall" proves the cleanup.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

_DIST = "basedpyright-as-pyright"


def _pyright_version(python: Path, *, pyright: str | None) -> str:
    env = {k: v for k, v in os.environ.items() if k != "PYRIGHT"}
    if pyright is not None:
        env["PYRIGHT"] = pyright
    out = subprocess.run(
        [str(python), "-m", "pyright", "--version"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return out.stdout


def _make_venv(tmp_path: Path, *, seed: bool) -> Path:
    env_dir = tmp_path / "venv"
    cmd = ["uv", "venv", str(env_dir)]
    if seed:  # pip itself must be present for the pip case
        cmd.append("--seed")
    subprocess.run(cmd, check=True)
    return env_dir / "bin" / "python"


def _install(installer: str, python: Path, wheel: Path) -> None:
    if installer == "pip":
        subprocess.run([str(python), "-m", "pip", "install", str(wheel)], check=True)
    else:
        subprocess.run(["uv", "pip", "install", "--python", str(python), str(wheel)], check=True)


def _uninstall(installer: str, python: Path) -> None:
    if installer == "pip":
        subprocess.run([str(python), "-m", "pip", "uninstall", "-y", _DIST], check=True)
    else:
        subprocess.run(["uv", "pip", "uninstall", "--python", str(python), _DIST], check=True)


@pytest.fixture(params=["pip", "uv"])
def installer(request: pytest.FixtureRequest) -> str:
    return str(request.param)


def it_redirect_is_active_only_while_installed(
    tmp_path: Path, wheel: Path, installer: str
) -> None:
    python = _make_venv(tmp_path, seed=(installer == "pip"))
    _install(installer, python, wheel)

    # Installed: the env var redirects pyright to basedpyright.
    assert "basedpyright" in _pyright_version(python, pyright="basedpyright")

    _uninstall(installer, python)

    # Uninstalled: PYRIGHT=basedpyright has no effect; real pyright runs.
    after = _pyright_version(python, pyright="basedpyright")
    assert "basedpyright" not in after
    assert after.startswith("pyright "), after
