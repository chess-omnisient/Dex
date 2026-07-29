#!/usr/bin/env python3
"""Discover immutable historic Dex release trees for fleet acceptance."""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

RELEASE_TAG = re.compile(
    r"^dist/release/v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)-(?P<short>[0-9a-f]{7,64})$"
)
PUBLIC_REMOTE = "https://github.com/davekilleen/Dex.git"
USER_FIXTURES = {
    "00-Inbox/keep.md": b"# User note\nThis must survive updates.\n",
    "03-Tasks/Tasks.md": b"# My task\n- Keep this task exactly.\n",
    "System/user-profile.yaml": b"updates:\n  channel: stable\n",
    ".claude/skills/my-weekly-review/SKILL.md": (
        b"---\nname: my-weekly-review\ndescription: User-authored weekly review.\n"
        b"---\n# User skill\n"
    ),
}


class FleetError(RuntimeError):
    """The historic release fleet could not be built safely."""


@dataclass(frozen=True)
class DistributionRelease:
    """One immutable published release tree that a user may be running."""

    tag: str
    version: str
    commit: str
    tree: str


@dataclass(frozen=True)
class FleetCase:
    """A fresh historic install plus the user content that must survive it."""

    release: DistributionRelease
    vault: Path
    user_hashes: dict[str, str]


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


def safe_case_name(release: DistributionRelease) -> str:
    """Return a filesystem-safe, immutable name for one historic release case."""

    return f"v{release.version}-{release.commit[:12]}"


def hash_user_owned_files(vault: Path) -> dict[str, str]:
    """Hash the fixture files whose bytes an update may never change."""

    hashes: dict[str, str] = {}
    for relative in USER_FIXTURES:
        path = vault / relative
        if path.is_symlink() or not path.is_file():
            raise FleetError(f"user fixture is not a regular file: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def build_fixture(repo: Path, release: DistributionRelease, output: Path) -> FleetCase:
    """Create a disposable old install without overwriting any existing case."""

    if output.exists() and not output.is_dir():
        raise FleetError(f"fleet output is not a directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    vault = output / safe_case_name(release)
    if vault.exists():
        raise FleetError(f"fleet case directory must be empty: {vault}")

    _git(repo, "clone", "--quiet", "--no-checkout", "--no-local", str(repo), str(vault))
    _git(vault, "checkout", "--quiet", "--detach", release.tag)
    _git(vault, "remote", "rename", "origin", "upstream")
    _git(vault, "remote", "set-url", "upstream", PUBLIC_REMOTE)
    _git(vault, "remote", "set-url", "--push", "upstream", "DISABLED")

    for relative, content in USER_FIXTURES.items():
        path = vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    _git(vault, "config", "user.name", "Dex Fleet Fixture")
    _git(vault, "config", "user.email", "fleet@example.invalid")
    _git(vault, "add", "-f", "--", *USER_FIXTURES)
    _git(vault, "commit", "--quiet", "-m", "test: simulated user content")
    return FleetCase(release=release, vault=vault, user_hashes=hash_user_owned_files(vault))
