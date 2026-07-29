"""Tests for the historic-release acceptance fleet builder."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import release_fleet


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repo = tmp_path / "releases"
    _git(tmp_path, "init", "--quiet", str(repo))
    _git(repo, "config", "user.name", "Dex Fleet Tests")
    _git(repo, "config", "user.email", "fleet-tests@example.invalid")
    return repo


def _tag_release(
    repo: Path,
    version: str,
    content: str,
    *,
    allow_empty: bool = False,
    suffix: str | None = None,
) -> str:
    (repo / "README.md").write_text(content + "\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    commit_args = ["commit", "--quiet", "-m", f"release {version}"]
    if allow_empty:
        commit_args.insert(1, "--allow-empty")
    _git(repo, *commit_args)
    commit = _git(repo, "rev-parse", "HEAD")
    tag = f"dist/release/v{version}-{suffix or commit[:7]}"
    _git(repo, "tag", "-a", tag, "-m", tag)
    return tag


def test_discovers_each_distinct_distribution_tree_once(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    first = _tag_release(repo, "1.61.0", "one")
    second = _tag_release(repo, "1.61.0", "two")
    _tag_release(repo, "1.62.0", "two", allow_empty=True)

    releases = release_fleet.discover_distribution_releases(repo)

    assert [release.tag for release in releases] == sorted([first, second])


def test_rejects_distribution_tag_that_does_not_name_its_commit(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "actual", suffix="deadbee")

    with pytest.raises(release_fleet.FleetError, match="does not match"):
        release_fleet.discover_distribution_releases(repo)
