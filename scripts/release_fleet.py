#!/usr/bin/env python3
"""Discover immutable historic Dex release trees for fleet acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.paths import INBOX_DIR, TASKS_FILE, USER_PROFILE_FILE, VAULT_ROOT

RELEASE_TAG = re.compile(
    r"^dist/release/v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)-(?P<short>[0-9a-f]{7,64})$"
)
ARCHIVE_RELEASE_TAG = re.compile(
    r"^dist/archive/v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)-(?P<short>[0-9a-f]{7,64})$"
)
LEGACY_RELEASE_TAG = re.compile(r"^v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)$")
PUBLIC_REMOTE = "https://github.com/davekilleen/Dex.git"
USER_FIXTURES = {
    str(INBOX_DIR.relative_to(VAULT_ROOT) / "keep.md"): b"# User note\nThis must survive updates.\n",
    str(TASKS_FILE.relative_to(VAULT_ROOT)): b"# My task\n- Keep this task exactly.\n",
    str(USER_PROFILE_FILE.relative_to(VAULT_ROOT)): b"updates:\n  channel: stable\n",
    ".claude/skills/my-weekly-review/SKILL.md": (
        b"---\nname: my-weekly-review\ndescription: User-authored weekly review.\n"
        b"---\n# User skill\n"
    ),
}
REPORT_KEYS = frozenset({"foundation_tag", "follow_up_tag", "cases"})
CASE_RESULT_KEYS = frozenset(
    {
        "starting_tag",
        "reached_foundation",
        "reached_follow_up",
        "foundation_doctor_healthy",
        "follow_up_doctor_healthy",
        "user_hashes_before",
        "user_hashes_after_foundation",
        "user_hashes_after_follow_up",
        "transcript_path",
    }
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


@dataclass(frozen=True)
class FleetCase:
    """A fresh historic install plus the user content that must survive it."""

    release: DistributionRelease
    vault: Path
    user_hashes: dict[str, str]


@dataclass(frozen=True)
class CaseResult:
    """Evidence from one historic installation's two-release journey."""

    starting_tag: str
    reached_foundation: bool
    reached_follow_up: bool
    foundation_doctor_healthy: bool
    follow_up_doctor_healthy: bool
    user_hashes_before: dict[str, str]
    user_hashes_after_foundation: dict[str, str]
    user_hashes_after_follow_up: dict[str, str]
    transcript_path: str


@dataclass(frozen=True)
class AcceptanceReport:
    """The complete evidence set required before claiming fleet acceptance."""

    foundation_tag: str
    follow_up_tag: str
    cases: tuple[CaseResult, ...]


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
    """Return every distinct tree behind immutable and legacy public release tags."""

    seen_trees: set[str] = set()
    immutable_identities: dict[tuple[str, str], str] = {}
    discovered: list[DistributionRelease] = []
    candidates: list[tuple[int, str, re.Match[str]]] = []
    for tag in _git_lines(repo, "tag", "--list"):
        distribution_match = RELEASE_TAG.fullmatch(tag)
        if distribution_match is not None:
            candidates.append((0, tag, distribution_match))
            continue
        archive_match = ARCHIVE_RELEASE_TAG.fullmatch(tag)
        if archive_match is not None:
            candidates.append((1, tag, archive_match))
            continue
        legacy_match = LEGACY_RELEASE_TAG.fullmatch(tag)
        if legacy_match is not None:
            candidates.append((2, tag, legacy_match))

    for priority, tag, match in sorted(candidates, key=lambda item: (item[0], item[1])):
        commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
        if priority < 2 and not commit.startswith(match.group("short")):
            raise FleetError(f"{tag}: tag suffix does not match its commit")
        if priority < 2:
            identity = (match.group("version"), match.group("short"))
            existing_commit = immutable_identities.setdefault(identity, commit)
            if existing_commit != commit:
                raise FleetError(
                    f"{tag}: ambiguous immutable distribution identity "
                    f"v{identity[0]}-{identity[1]}"
                )
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


def _create_fixture_vault(repo: Path, release: DistributionRelease, output: Path) -> Path:
    """Clone one historic release without inheriting later release metadata."""

    if output.exists() and not output.is_dir():
        raise FleetError(f"fleet output is not a directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    vault = output / safe_case_name(release)
    if vault.exists():
        raise FleetError(f"fleet case directory must be empty: {vault}")

    _git(
        repo,
        "clone",
        "--quiet",
        "--no-checkout",
        "--no-local",
        "--no-tags",
        str(repo),
        str(vault),
    )
    _git(vault, "fetch", "--quiet", "--no-tags", "origin", f"refs/tags/{release.tag}:refs/tags/{release.tag}")
    _git(vault, "checkout", "--quiet", "--detach", release.tag)
    _git(vault, "remote", "rename", "origin", "upstream")
    _git(vault, "remote", "set-url", "upstream", PUBLIC_REMOTE)
    _git(vault, "remote", "set-url", "--push", "upstream", "DISABLED")

    _git(vault, "config", "user.name", "Dex Fleet Fixture")
    _git(vault, "config", "user.email", "fleet@example.com")
    return vault


def _seed_user_content(vault: Path) -> dict[str, str]:
    """Place fixed user-owned content only after the historic install is ready."""
    for relative, content in USER_FIXTURES.items():
        path = vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    _git(vault, "add", "-f", "--", *USER_FIXTURES)
    _git(vault, "commit", "--quiet", "-m", "test: simulated user content")
    return hash_user_owned_files(vault)


def build_fixture(repo: Path, release: DistributionRelease, output: Path) -> FleetCase:
    """Create a structural historic-release fixture without running its installer."""
    vault = _create_fixture_vault(repo, release, output)
    return FleetCase(release=release, vault=vault, user_hashes=_seed_user_content(vault))


def _run_historic_installer(vault: Path) -> None:
    """Make the cloned release a realistic installed Dex before adding user data."""
    installer = vault / "install.sh"
    if installer.is_symlink() or not installer.is_file():
        raise FleetError("historic release has no safe install.sh to bootstrap its fixture")
    result = subprocess.run(
        ["bash", "install.sh"],
        cwd=vault,
        capture_output=True,
        text=True,
        timeout=15 * 60,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise FleetError(f"historic installer failed for {vault.name}: {detail}")


def build_installed_fixture(repo: Path, release: DistributionRelease, output: Path) -> FleetCase:
    """Install the historic release, then add synthetic user-owned data for updating."""
    vault = _create_fixture_vault(repo, release, output)
    _run_historic_installer(vault)
    return FleetCase(release=release, vault=vault, user_hashes=_seed_user_content(vault))


def assert_complete(report: AcceptanceReport, expected_start_tags: set[str]) -> None:
    """Refuse a release claim unless every historic package completed both hops."""

    if not report.cases:
        raise FleetError("acceptance report contains no historic releases")
    actual_tags = {case.starting_tag for case in report.cases}
    if len(actual_tags) != len(report.cases):
        raise FleetError("acceptance report contains a duplicate historic release")
    missing = sorted(expected_start_tags - actual_tags)
    if missing:
        raise FleetError("acceptance report is missing historic releases: " + ", ".join(missing))
    unexpected = sorted(actual_tags - expected_start_tags)
    if unexpected:
        raise FleetError("acceptance report contains unknown historic releases: " + ", ".join(unexpected))

    for case in report.cases:
        if not case.reached_foundation:
            raise FleetError(f"{case.starting_tag}: foundation release was not reached")
        if not case.reached_follow_up:
            raise FleetError(f"{case.starting_tag}: follow-up release was not reached")
        if not case.foundation_doctor_healthy:
            raise FleetError(f"{case.starting_tag}: Doctor was unhealthy after foundation release")
        if not case.follow_up_doctor_healthy:
            raise FleetError(f"{case.starting_tag}: Doctor was unhealthy after follow-up release")
        if not case.user_hashes_before:
            raise FleetError(f"{case.starting_tag}: user-content evidence is missing")
        if case.user_hashes_before != case.user_hashes_after_foundation:
            raise FleetError(f"{case.starting_tag}: user content changed during foundation release")
        if case.user_hashes_before != case.user_hashes_after_follow_up:
            raise FleetError(f"{case.starting_tag}: user content changed during follow-up release")
        if not case.transcript_path:
            raise FleetError(f"{case.starting_tag}: user-visible journey transcript is missing")


def _required_string(value: Mapping[str, Any], key: str, context: str) -> str:
    candidate = value.get(key)
    if not isinstance(candidate, str) or not candidate:
        raise FleetError(f"{context} has no valid {key}")
    return candidate


def _hash_map(value: object, context: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise FleetError(f"{context} must be a non-empty object")
    hashes: dict[str, str] = {}
    for relative, digest in value.items():
        if (
            not isinstance(relative, str)
            or not relative
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise FleetError(f"{context} contains an invalid user-content hash")
        hashes[relative] = digest
    return hashes


def acceptance_report_from_json(source: str) -> AcceptanceReport:
    """Parse a strict, machine-readable two-release acceptance report."""

    try:
        raw = json.loads(source)
    except json.JSONDecodeError as error:
        raise FleetError("acceptance report is not valid JSON") from error
    if not isinstance(raw, Mapping) or set(raw) != REPORT_KEYS:
        raise FleetError("acceptance report has an invalid top-level shape")
    foundation_tag = _required_string(raw, "foundation_tag", "acceptance report")
    follow_up_tag = _required_string(raw, "follow_up_tag", "acceptance report")
    cases_raw = raw.get("cases")
    if not isinstance(cases_raw, list):
        raise FleetError("acceptance report cases must be a list")

    cases: list[CaseResult] = []
    for index, case_raw in enumerate(cases_raw, start=1):
        context = f"acceptance case {index}"
        if not isinstance(case_raw, Mapping) or set(case_raw) != CASE_RESULT_KEYS:
            raise FleetError(f"{context} has an invalid shape")
        boolean_keys = (
            "reached_foundation",
            "reached_follow_up",
            "foundation_doctor_healthy",
            "follow_up_doctor_healthy",
        )
        if any(not isinstance(case_raw[key], bool) for key in boolean_keys):
            raise FleetError(f"{context} has an invalid boolean verdict")
        cases.append(
            CaseResult(
                starting_tag=_required_string(case_raw, "starting_tag", context),
                reached_foundation=bool(case_raw["reached_foundation"]),
                reached_follow_up=bool(case_raw["reached_follow_up"]),
                foundation_doctor_healthy=bool(case_raw["foundation_doctor_healthy"]),
                follow_up_doctor_healthy=bool(case_raw["follow_up_doctor_healthy"]),
                user_hashes_before=_hash_map(case_raw["user_hashes_before"], context),
                user_hashes_after_foundation=_hash_map(
                    case_raw["user_hashes_after_foundation"], context
                ),
                user_hashes_after_follow_up=_hash_map(
                    case_raw["user_hashes_after_follow_up"], context
                ),
                transcript_path=_required_string(case_raw, "transcript_path", context),
            )
        )
    return AcceptanceReport(foundation_tag, follow_up_tag, tuple(cases))


def _case_manifest(case: FleetCase) -> dict[str, object]:
    return {
        "starting": _release_manifest(case.release),
        "vault": str(case.vault),
        "user_hashes": case.user_hashes,
    }


def _release_manifest(release: DistributionRelease) -> dict[str, str]:
    return {
        "tag": release.tag,
        "version": release.version,
        "commit": release.commit,
        "tree": release.tree,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Build the historic fleet or validate a completed two-release report."""

    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    manifest = subcommands.add_parser("manifest", help="list historic releases without cloning them")
    manifest.add_argument("--repo", type=Path, required=True)
    build = subcommands.add_parser("build", help="build clean historic-release fixtures")
    build.add_argument("--repo", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--starting-tag", help="build only this immutable historic release tag")
    check = subcommands.add_parser("check-report", help="fail closed on incomplete fleet evidence")
    check.add_argument("--repo", type=Path, required=True)
    check.add_argument("report", type=Path)
    args = parser.parse_args(argv)

    if args.command == "manifest":
        releases = discover_distribution_releases(args.repo)
        print(
            json.dumps(
                {"case_count": len(releases), "cases": [_release_manifest(release) for release in releases]},
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "build":
        releases = discover_distribution_releases(args.repo)
        if args.starting_tag:
            releases = tuple(release for release in releases if release.tag == args.starting_tag)
            if not releases:
                raise FleetError(f"historic distribution tag was not found: {args.starting_tag}")
        cases = [build_fixture(args.repo, release, args.output) for release in releases]
        print(
            json.dumps(
                {"case_count": len(cases), "cases": [_case_manifest(case) for case in cases]},
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    report = acceptance_report_from_json(args.report.read_text(encoding="utf-8"))
    expected_start_tags = {release.tag for release in discover_distribution_releases(args.repo)}
    assert_complete(report, expected_start_tags)
    print(f"PASS: {len(report.cases)} historic release trees reached both releases")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FleetError as error:
        raise SystemExit(f"FAIL: {error}") from error
