"""The release gates, exercised against throwaway repositories.

These scripts decide whether a version may be published, so their *failure*
modes are the interesting part: a truncated history must refuse to answer rather
than answer wrongly, and a typo'd revision must not read as a rejected release.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

LIB = Path(__file__).resolve().parent.parent / "lib"


def _run(argv: Sequence[str | Path], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(arg) for arg in argv],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(cwd)},
    )


def _git(*argv: str, cwd: Path) -> None:
    subprocess.run(["git", *argv], cwd=cwd, check=True, capture_output=True)


def _commit(repo: Path, message: str) -> str:
    _git("commit", "--allow-empty", "-m", message, cwd=repo)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with two commits on `main` and one off it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-b", "main", cwd=repo)
    _git("config", "user.email", "test@example.com", cwd=repo)
    _git("config", "user.name", "Test", cwd=repo)
    _commit(repo, "one")
    _commit(repo, "two")
    return repo


class DescribeRequireReachableFrom:
    def it_accepts_an_ancestor(self, repo: Path) -> None:
        first = subprocess.run(
            ["git", "rev-parse", "HEAD~1"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert (
            _run(
                [LIB / "git/require-reachable-from", first, "main"], cwd=repo
            ).returncode
            == 0
        )

    def it_accepts_the_tip_itself(self, repo: Path) -> None:
        """Reflexive: releasing the exact commit `main` points at is the normal case."""
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert (
            _run(
                [LIB / "git/require-reachable-from", head, "main"], cwd=repo
            ).returncode
            == 0
        )

    def it_rejects_a_commit_off_the_branch(self, repo: Path) -> None:
        _git("checkout", "-b", "side", "HEAD~1", cwd=repo)
        aside = _commit(repo, "aside")
        result = _run([LIB / "git/require-reachable-from", aside, "main"], cwd=repo)
        assert result.returncode == 1, result.stderr

    def it_distinguishes_an_unaskable_question_from_a_no(self, repo: Path) -> None:
        """A typo'd revision exits 2, not 1 -- it is not a rejected release."""
        result = _run([LIB / "git/require-reachable-from", "nonsuch", "main"], cwd=repo)
        assert result.returncode == 2, result.stderr

    def it_refuses_to_answer_in_a_shallow_clone(
        self, repo: Path, tmp_path: Path
    ) -> None:
        """A truncated history reports false negatives; refusing beats guessing."""
        shallow = tmp_path / "shallow"
        subprocess.run(
            ["git", "clone", "--depth", "1", f"file://{repo}", str(shallow)],
            check=True,
            capture_output=True,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=shallow,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        result = _run([LIB / "git/require-reachable-from", head, "HEAD"], cwd=shallow)
        assert result.returncode == 2, result.stderr
        assert "shallow" in result.stderr


class DescribeChangelogGetVersion:
    def it_reads_the_topmost_version(self, repo: Path) -> None:
        (repo / "CHANGELOG.md").write_text("# Changelog\n\n## 1.2.3\n\n## 1.2.2\n")
        result = _run([LIB / "changelog/get-version"], cwd=repo)
        assert result.stdout.strip() == "1.2.3", result.stderr

    def it_skips_an_unreleased_heading(self, repo: Path) -> None:
        (repo / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n\n## 1.2.3\n")
        result = _run([LIB / "changelog/get-version"], cwd=repo)
        assert result.stdout.strip() == "1.2.3", result.stderr

    def it_errors_rather_than_printing_nothing(self, repo: Path) -> None:
        """A `get-` that cannot answer must fail, not emit an empty string."""
        (repo / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n")
        result = _run([LIB / "changelog/get-version"], cwd=repo)
        assert result.returncode != 0
        assert result.stdout.strip() == ""


class DescribeGetRequestedVersion:
    @pytest.mark.parametrize(
        "ref",
        ["triggers/release/v1.2.3", "refs/heads/triggers/release/v1.2.3"],
    )
    def it_reads_the_version_from_the_ref(self, ref: str, repo: Path) -> None:
        result = _run([LIB / "ci/get-requested-version", ref], cwd=repo)
        assert result.stdout.strip() == "1.2.3", result.stderr

    @pytest.mark.parametrize("ref", ["main", "release/v1.2.3", "triggers/release/v"])
    def it_rejects_a_ref_that_is_not_a_request(self, ref: str, repo: Path) -> None:
        assert _run([LIB / "ci/get-requested-version", ref], cwd=repo).returncode == 2
