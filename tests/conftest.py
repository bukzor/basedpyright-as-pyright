"""Shared fixtures for the end-to-end / acceptance tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the project wheel once per session; return its path."""
    dist = tmp_path_factory.mktemp("dist")
    subprocess.run(["uv", "build", "--wheel", str(_REPO), "-o", str(dist)], check=True)
    (built,) = dist.glob("*.whl")
    return built
