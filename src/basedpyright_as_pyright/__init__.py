"""Make the genuine ``pyright`` wrapper run a fork's engine (basedpyright).

Gated by the ``PYRIGHT`` environment variable and installed via a ``.pth`` file
that calls :func:`install` at interpreter startup. Unset ``PYRIGHT`` makes it a
near-zero-cost no-op.

The redirect swaps a single seam: ``pyright._utils.install_pyright``, the
function the wrapper uses to locate the JS engine directory. We patch it the
moment ``pyright._utils`` loads, so the later ``from ._utils import
install_pyright`` in ``cli``/``langserver`` binds the patched version. We do not
preserve the wrapper's npm/version/cache logic — the replacement simply returns
the fork's package directory, which holds ``index.js`` / ``langserver.index.js``.
"""

from __future__ import annotations

import os
import sys
import importlib
from collections.abc import Sequence
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder
from pathlib import Path
from types import ModuleType

_TARGET = "pyright._utils"


def install() -> None:
    """Register the engine redirect when ``$PYRIGHT`` names a fork.

    Safe to call at every interpreter startup: returns immediately when
    ``PYRIGHT`` is unset, and never raises — a failure here must not break
    interpreter startup for an opt-in convenience.
    """
    try:
        fork = os.environ.get("PYRIGHT")
        if not fork:
            return
        if any(isinstance(finder, _EngineRedirect) for finder in sys.meta_path):
            return  # idempotent
        sys.meta_path.insert(0, _EngineRedirect(fork))
        already = sys.modules.get(_TARGET)
        if already is not None:  # rare: pyright imported before us
            _redirect(already, fork)
    except Exception:
        pass


class _EngineRedirect(MetaPathFinder):
    """Wrap the loader for ``pyright._utils`` so it patches on load."""

    def __init__(self, fork: str) -> None:
        self._fork = fork

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        del target  # part of the finder protocol; unused here
        if fullname != _TARGET:
            return None
        # `path` is pyright's __path__, handed to us by the import system, so
        # PathFinder resolves the real module without re-entering meta_path.
        spec = PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return None
        spec.loader = _PatchingLoader(spec.loader, self._fork)
        return spec


class _PatchingLoader(Loader):
    """Delegates to the real loader, then redirects the engine seam."""

    def __init__(self, inner: Loader, fork: str) -> None:
        self._inner = inner
        self._fork = fork

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        return self._inner.create_module(spec)

    def exec_module(self, module: ModuleType) -> None:
        self._inner.exec_module(module)
        _redirect(module, self._fork)


def _redirect(utils_module: ModuleType, fork: str) -> None:
    """Point ``install_pyright`` at the fork's engine directory."""
    original = getattr(utils_module, "install_pyright")

    def install_pyright(args: tuple[object, ...], *, quiet: bool | None = None) -> Path:
        try:
            engine = importlib.import_module(fork)
            assert engine.__file__ is not None
            return Path(engine.__file__).parent
        except Exception:
            return original(args, quiet=quiet)  # fork missing -> real pyright

    setattr(utils_module, "install_pyright", install_pyright)
