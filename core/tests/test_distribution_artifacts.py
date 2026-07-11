"""Regression tests for artifacts produced from the public repository."""

from __future__ import annotations

import io
import subprocess
import tarfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _archive_members() -> set[str]:
    """Return paths from the archive users receive from the current checkout."""
    result = subprocess.run(
        ["git", "archive", "--worktree-attributes", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        return set(archive.getnames())


def test_git_archive_keeps_skill_scripts_but_strips_top_level_scripts() -> None:
    members = _archive_members()

    assert ".claude/skills/anthropic-docx/scripts/document.py" in members
    assert not any(path == "scripts" or path.startswith("scripts/") for path in members)
