#!/usr/bin/env python3
"""Discover immutable historic Dex release trees for fleet acceptance."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

RELEASE_TAG = re.compile(
    r"^dist/release/v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)-(?P<short>[0-9a-f]{7,64})$"
)


class FleetError(RuntimeError):
    """The historic release fleet could not be built safely."""


@dataclass(frozen=True)
class DistributionRelease:
    """One immutable published release tree that a user may be running."""

    tag: str
    version: str
    commit: str
    tree: str


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise FleetError(message)
    return result.stdout.strip()


def _git_lines(repo: Path, *arguments: str) -> tuple[str, ...]:
    output = _git(repo, *arguments)
    return tuple(line for line in output.splitlines() if line)


def _version_key(version: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in version.split("."))
    if len(parts) != 3:
        raise FleetError(f"distribution tag has an invalid semantic version: {version}")
    return parts  # type: ignore[return-value]


def discover_distribution_releases(repo: Path) -> tuple[DistributionRelease, ...]:
    """Return every distinct immutable tree behind the public distribution tags."""

    seen_trees: set[str] = set()
    discovered: list[DistributionRelease] = []
    for tag in _git_lines(repo, "tag", "--list", "dist/release/v*"):
        match = RELEASE_TAG.fullmatch(tag)
        if match is None:
            continue
        commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
        if not commit.startswith(match.group("short")):
            raise FleetError(f"{tag}: tag suffix does not match its commit")
        tree = _git(repo, "rev-parse", f"{tag}^{{tree}}")
        if tree in seen_trees:
            continue
        seen_trees.add(tree)
        discovered.append(
            DistributionRelease(
                tag=tag,
                version=match.group("version"),
                commit=commit,
                tree=tree,
            )
        )
    return tuple(sorted(discovered, key=lambda item: (_version_key(item.version), item.tag)))
