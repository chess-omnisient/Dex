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
REPORT_KEYS = frozenset({"foundation_tag", "follow_up_tag", "platforms", "cases"})
STARTING_MANIFEST_KEYS = frozenset({"schema_version", "case_count", "cases"})
STARTING_RELEASE_KEYS = frozenset({"tag", "version", "commit", "tree"})
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
        "foundation_receipt_path",
        "follow_up_receipt_path",
        "foundation_doctor_path",
        "follow_up_doctor_path",
        "follow_up_smoke_path",
        "platform",
        "evidence_manifest_path",
        "evidence_manifest_sha256",
    }
)
# Archive tags are historic starting evidence only.  A hop target must be the
# still-published immutable distribution tag that the release channel can prove.
IMMUTABLE_TARGET_TAGS = (RELEASE_TAG,)
_HEX = re.compile(r"^[0-9a-f]{40}$")
UPDATE_SKILL_RELATIVE = ".claude/skills/dex-update/SKILL.md"
UPDATE_RESCUE_RELATIVE = "docs/UPDATE-RESCUE.md"
EVIDENCE_MANIFEST_KEYS = frozenset(
    {"schema_version", "starting_release", "foundation_release", "follow_up_release", "events", "artifacts"}
)
RUNNER_ARTIFACT_KEYS = frozenset(
    {
        "transcript",
        "historic_update_surface",
        "foundation_update_surface",
        "foundation_receipt",
        "follow_up_receipt",
        "foundation_doctor",
        "follow_up_doctor",
        "follow_up_smoke",
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
    foundation_receipt_path: str = ""
    follow_up_receipt_path: str = ""
    foundation_doctor_path: str = ""
    follow_up_doctor_path: str = ""
    follow_up_smoke_path: str = ""
    platform: str = ""
    evidence_manifest_path: str = ""
    evidence_manifest_sha256: str = ""


@dataclass(frozen=True)
class AcceptanceReport:
    """The complete evidence set required before claiming fleet acceptance."""

    foundation_tag: str
    follow_up_tag: str
    cases: tuple[CaseResult, ...]
    platforms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImmutableRelease:
    """A closed tag identity suitable for an explicitly requested journey hop."""

    tag: str
    tag_object: str
    commit: str
    tree: str
    version: str

    def identity(self) -> dict[str, str]:
        return {
            "tag": self.tag,
            "tag_object": self.tag_object,
            "commit": self.commit,
            "tree": self.tree,
            "version": self.version,
            "channel": "stable",
        }


def _git(repo: Path, *arguments: str, environment: Mapping[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        capture_output=True,
        text=True,
        env=dict(environment) if environment is not None else None,
    )
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise FleetError(message)
    return result.stdout.strip()


def _git_lines(repo: Path, *arguments: str) -> tuple[str, ...]:
    output = _git(repo, *arguments)
    return tuple(line for line in output.splitlines() if line)


def resolve_immutable_release(repo: Path, tag: str) -> ImmutableRelease:
    """Resolve one annotated immutable release tag, never a moving ref."""

    match = next((pattern.fullmatch(tag) for pattern in IMMUTABLE_TARGET_TAGS if pattern.fullmatch(tag)), None)
    if match is None:
        raise FleetError("journey targets must be immutable dist/release tags")
    tag_object = _git(repo, "rev-parse", "--verify", tag)
    if _git(repo, "cat-file", "-t", tag) != "tag":
        raise FleetError(f"{tag}: journey target must be an annotated tag")
    commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
    tree = _git(repo, "rev-parse", f"{tag}^{{tree}}")
    if any(_HEX.fullmatch(value) is None for value in (tag_object, commit, tree)):
        raise FleetError(f"{tag}: journey target identity is malformed")
    if not commit.startswith(match.group("short")):
        raise FleetError(f"{tag}: tag suffix does not match its commit")
    return ImmutableRelease(tag, tag_object, commit, tree, match.group("version"))


def _tag_file(repo: Path, tag: str, relative: str) -> bytes:
    try:
        return _git(repo, "show", f"{tag}:{relative}").encode("utf-8")
    except FleetError as error:
        raise FleetError(f"{tag} has no required {relative} publication record") from error


def _strict_object(source: bytes, context: str, keys: frozenset[str]) -> dict[str, object]:
    try:
        value = json.loads(source)
    except json.JSONDecodeError as error:
        raise FleetError(f"{context} is not valid JSON") from error
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FleetError(f"{context} has an invalid shape")
    return dict(value)


def shipped_update_surface(repo: Path, release: DistributionRelease | ImmutableRelease) -> dict[str, object]:
    """Bind the human-facing `/dex-update` contract to exact released bytes.

    Skills are Markdown instructions, not an executable API.  This evidence is
    deliberately read-only: it proves what the installed release told a person
    to do, but cannot turn prose into a synthetic update command.
    """

    skill = _tag_file(repo, release.tag, UPDATE_SKILL_RELATIVE)
    rescue: bytes | None
    try:
        rescue = _tag_file(repo, release.tag, UPDATE_RESCUE_RELATIVE)
    except FleetError:
        rescue = None
    text = skill.decode("utf-8", "strict")
    required = {
        "service": "core.lifecycle.service" in text,
        "preview": "preview" in text.lower(),
        "approval": "approval" in text.lower() and "Apply this exact update?" in text,
        "receipt": "receipt" in text.lower(),
    }
    delivery = {
        "deliver_latest_release": "deliver_latest_release" in text,
        "build_and_preview_delivered_release": "build_and_preview_delivered_release" in text,
        "execute_approved_delivered_release": "execute_approved_delivered_release" in text,
    }
    identity = release.identity() if isinstance(release, ImmutableRelease) else {
        "tag": release.tag,
        "tag_object": _git(repo, "rev-parse", "--verify", release.tag),
        "commit": release.commit,
        "tree": release.tree,
        "version": release.version,
        "channel": "stable",
    }
    return {
        "release": identity,
        "skill_path": UPDATE_SKILL_RELATIVE,
        "skill_sha256": hashlib.sha256(skill).hexdigest(),
        "rescue_path": UPDATE_RESCUE_RELATIVE if rescue is not None else None,
        "rescue_sha256": hashlib.sha256(rescue).hexdigest() if rescue is not None else None,
        "preview_approval_receipt": required,
        "delivery_operations": delivery,
        "machine_executable": False,
    }


def _has_transaction_receipt(value: object) -> bool:
    """Recognize the service envelope while rejecting a prose-only success claim."""

    if not isinstance(value, Mapping):
        return False
    if isinstance(value.get("transaction_id"), str) and value["transaction_id"]:
        return True
    nested = value.get("receipt")
    return isinstance(nested, Mapping) and isinstance(nested.get("transaction_id"), str) and bool(
        nested["transaction_id"]
    )


def _case_environment(vault: Path, runtime_root: Path) -> dict[str, str]:
    """Return the complete, deliberately small environment for one fixture."""

    home = runtime_root / "home"
    temporary = runtime_root / "tmp"
    home.mkdir(parents=True, exist_ok=False)
    temporary.mkdir(parents=True, exist_ok=False)
    return {
        "HOME": str(home),
        "TMPDIR": str(temporary),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "VAULT_PATH": str(vault),
    }


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_evidence_manifest(
    evidence_root: Path,
    *,
    start: dict[str, object],
    foundation: ImmutableRelease,
    follow_up: ImmutableRelease,
    events: Sequence[Mapping[str, object]],
    artifacts: Mapping[str, Path],
) -> tuple[str, str]:
    """Write the runner-owned, content-addressed index that report checking consumes."""

    artifact_index: dict[str, dict[str, str]] = {}
    for name, artifact in artifacts.items():
        try:
            relative = artifact.resolve().relative_to(evidence_root.parent.resolve())
        except ValueError as error:
            raise FleetError(f"evidence artifact escapes its case directory: {name}") from error
        if artifact.is_symlink() or not artifact.is_file():
            raise FleetError(f"evidence artifact is missing or unsafe: {name}")
        artifact_index[name] = {
            "path": str(relative),
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }

    manifest = {
        "schema_version": 1,
        "starting_release": start,
        "foundation_release": foundation.identity(),
        "follow_up_release": follow_up.identity(),
        "events": [dict(event) for event in events],
        "artifacts": artifact_index,
    }
    path = evidence_root / "evidence-manifest.json"
    _write_json(path, manifest)
    return f"{evidence_root.name}/evidence-manifest.json", hashlib.sha256(path.read_bytes()).hexdigest()


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


def _create_fixture_vault(
    repo: Path,
    release: DistributionRelease,
    output: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> Path:
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
        environment=environment,
    )
    _git(vault, "fetch", "--quiet", "--no-tags", "origin", f"refs/tags/{release.tag}:refs/tags/{release.tag}", environment=environment)
    _git(vault, "checkout", "--quiet", "--detach", release.tag, environment=environment)
    _git(vault, "remote", "rename", "origin", "upstream", environment=environment)
    _git(vault, "remote", "set-url", "upstream", PUBLIC_REMOTE, environment=environment)
    _git(vault, "remote", "set-url", "--push", "upstream", "DISABLED", environment=environment)

    _git(vault, "config", "user.name", "Dex Fleet Fixture", environment=environment)
    _git(vault, "config", "user.email", "fleet@example.com", environment=environment)
    return vault


def _seed_user_content(vault: Path, environment: Mapping[str, str] | None = None) -> dict[str, str]:
    """Place fixed user-owned content only after the historic install is ready."""
    for relative, content in USER_FIXTURES.items():
        path = vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    _git(vault, "add", "-f", "--", *USER_FIXTURES, environment=environment)
    _git(vault, "commit", "--quiet", "-m", "test: simulated user content", environment=environment)
    return hash_user_owned_files(vault)


def build_fixture(repo: Path, release: DistributionRelease, output: Path) -> FleetCase:
    """Create a structural historic-release fixture without running its installer."""
    vault = _create_fixture_vault(repo, release, output)
    return FleetCase(release=release, vault=vault, user_hashes=_seed_user_content(vault))


def _run_historic_installer(vault: Path, environment: Mapping[str, str] | None = None) -> None:
    """Make the cloned release a realistic installed Dex before adding user data."""
    installer = vault / "install.sh"
    if installer.is_symlink() or not installer.is_file():
        raise FleetError("historic release has no safe install.sh to bootstrap its fixture")
    result = subprocess.run(
        ["bash", "install.sh"],
        cwd=vault,
        env=dict(environment) if environment is not None else None,
        capture_output=True,
        text=True,
        timeout=15 * 60,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise FleetError(f"historic installer failed for {vault.name}: {detail}")


def build_installed_fixture(
    repo: Path,
    release: DistributionRelease,
    output: Path,
    *,
    environment: Mapping[str, str] | None = None,
) -> FleetCase:
    """Install the historic release, then add synthetic user-owned data for updating."""
    vault = _create_fixture_vault(repo, release, output, environment=environment)
    _run_historic_installer(vault, environment)
    return FleetCase(release=release, vault=vault, user_hashes=_seed_user_content(vault, environment))


def run_journey(
    repo: Path,
    *,
    output: Path,
    starting_tag: str,
    foundation_tag: str,
    follow_up_tag: str,
) -> None:
    """Fail closed until immutable releases publish a machine-verifiable journey protocol.

    The only evidence emitted today is a hash of the exact shipped `/dex-update`
    and rescue material.  The runner never promotes Markdown instructions into
    commands, invokes lifecycle code, or accepts an external bridge as proof.
    """

    releases = {release.tag: release for release in discover_distribution_releases(repo)}
    start = releases.get(starting_tag)
    if start is None:
        raise FleetError(f"historic distribution tag was not found: {starting_tag}")
    foundation = resolve_immutable_release(repo, foundation_tag)
    follow_up = resolve_immutable_release(repo, follow_up_tag)
    if foundation.tag == follow_up.tag or foundation.commit == follow_up.commit:
        raise FleetError("foundation and follow-up must be different immutable releases")
    # Evidence must not become an untracked vault file that influences either
    # release preview.  Keep it beside a future disposable fixture.
    evidence_relative = f"{safe_case_name(start)}.evidence"
    evidence_root = output / evidence_relative
    if evidence_root.exists():
        raise FleetError("journey evidence directory must be empty")
    transcript_path = evidence_root / "journey-transcript.json"
    result_path = evidence_root / "journey-result.json"
    events: list[dict[str, object]] = []
    result: dict[str, object] = {
        "starting_tag": start.tag,
        "foundation_tag": foundation.tag,
        "follow_up_tag": follow_up.tag,
        "transcript_path": f"{evidence_relative}/journey-transcript.json",
    }

    try:
        historic_surface = shipped_update_surface(repo, start)
        foundation_surface = shipped_update_surface(repo, foundation)
        _write_json(evidence_root / "historic-update-surface.json", historic_surface)
        _write_json(evidence_root / "foundation-update-surface.json", foundation_surface)
        events.extend(
            (
                {
                    "id": "historic-update-surface",
                    "command": ["git", "show", f"{start.tag}:{UPDATE_SKILL_RELATIVE}"],
                    "release": historic_surface["release"],
                    "skill_sha256": historic_surface["skill_sha256"],
                    "rescue_sha256": historic_surface["rescue_sha256"],
                },
                {
                    "id": "foundation-update-surface",
                    "command": ["git", "show", f"{foundation.tag}:{UPDATE_SKILL_RELATIVE}"],
                    "release": foundation_surface["release"],
                    "skill_sha256": foundation_surface["skill_sha256"],
                    "rescue_sha256": foundation_surface["rescue_sha256"],
                },
            )
        )
        result["historic_update_surface"] = historic_surface
        result["foundation_update_surface"] = foundation_surface
        raise FleetError(
            "published /dex-update surfaces are Markdown-only; a future immutable release must "
            "publish a machine-verifiable journey protocol before fleet execution can continue"
        )
    except (FleetError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        result["failure"] = str(error)
        _write_json(transcript_path, {"events": events})
        artifacts: dict[str, Path] = {"transcript": transcript_path}
        if (evidence_root / "historic-update-surface.json").is_file():
            artifacts["historic_update_surface"] = evidence_root / "historic-update-surface.json"
        if (evidence_root / "foundation-update-surface.json").is_file():
            artifacts["foundation_update_surface"] = evidence_root / "foundation-update-surface.json"
        manifest_path, manifest_sha256 = _write_evidence_manifest(
            evidence_root,
            start=historic_surface if "historic_surface" in locals() else {"tag": start.tag},
            foundation=foundation,
            follow_up=follow_up,
            events=events,
            artifacts=artifacts,
        )
        result["evidence_manifest_path"] = manifest_path
        result["evidence_manifest_sha256"] = manifest_sha256
        _write_json(result_path, result)
        raise


def assert_complete(report: AcceptanceReport, expected_start_tags: set[str]) -> None:
    """Refuse a release claim unless every historic package completed both hops."""

    if not report.cases:
        raise FleetError("acceptance report contains no historic releases")
    if report.platforms and len(set(report.platforms)) != len(report.platforms):
        raise FleetError("acceptance report has invalid platform coverage")
    actual_tags = {case.starting_tag for case in report.cases}
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
        if report.platforms and case.platform not in report.platforms:
            raise FleetError(f"{case.starting_tag}: platform is not declared in report coverage")
    if report.platforms:
        expected_cases = {(tag, platform) for tag in expected_start_tags for platform in report.platforms}
        actual_cases = {(case.starting_tag, case.platform) for case in report.cases}
        if len(actual_cases) != len(report.cases):
            raise FleetError("acceptance report contains a duplicate historic release/platform case")
        if actual_cases != expected_cases:
            raise FleetError("acceptance report has incomplete historic release platform coverage")
    elif len(actual_tags) != len(report.cases):
        raise FleetError("acceptance report contains a duplicate historic release")


def _evidence_file(root: Path, relative: str, context: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise FleetError(f"{context} must be a relative evidence path")
    path = root / candidate
    if path.is_symlink() or not path.is_file() or path.resolve().parent != path.parent.resolve():
        raise FleetError(f"{context} is missing or unsafe")
    return path


def _read_evidence_json(root: Path, relative: str, context: str) -> dict[str, object]:
    path = _evidence_file(root, relative, context)
    return _strict_object(path.read_bytes(), context, frozenset({"release", "receipt"}))


def _manifest_artifact(
    root: Path,
    artifacts: Mapping[str, object],
    name: str,
    context: str,
) -> str:
    """Open one content-addressed runner artifact and return its safe relative path."""

    value = artifacts.get(name)
    if not isinstance(value, Mapping) or set(value) != {"path", "sha256"}:
        raise FleetError(f"{context}: runner manifest has no valid {name} artifact")
    path = value.get("path")
    digest = value.get("sha256")
    if not isinstance(path, str) or not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise FleetError(f"{context}: runner manifest has an invalid {name} artifact")
    artifact = _evidence_file(root, path, f"{context} {name} artifact")
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
        raise FleetError(f"{context}: {name} artifact hash does not match runner manifest")
    return path


def assert_evidence_bound(
    report: AcceptanceReport,
    *,
    repo: Path,
    evidence_root: Path,
    foundation: ImmutableRelease,
    follow_up: ImmutableRelease,
) -> None:
    """Open runner-owned evidence and bind it to released source bytes."""

    releases = {release.tag: release for release in discover_distribution_releases(repo)}

    for case in report.cases:
        starting_release = releases.get(case.starting_tag)
        if starting_release is None:
            raise FleetError(f"{case.starting_tag}: starting release is no longer discoverable")
        expected_historic_surface = shipped_update_surface(repo, starting_release)
        expected_foundation_surface = shipped_update_surface(repo, foundation)
        if (
            expected_historic_surface["machine_executable"] is not True
            or expected_foundation_surface["machine_executable"] is not True
        ):
            raise FleetError(
                f"{case.starting_tag}: immutable executable journey protocol is not published; "
                "fleet acceptance cannot pass"
            )
        manifest_path = _evidence_file(
            evidence_root, case.evidence_manifest_path, f"{case.starting_tag} evidence manifest"
        )
        if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != case.evidence_manifest_sha256:
            raise FleetError(f"{case.starting_tag}: evidence manifest hash does not match")
        manifest = _strict_object(
            manifest_path.read_bytes(),
            f"{case.starting_tag} evidence manifest",
            EVIDENCE_MANIFEST_KEYS,
        )
        if (
            manifest["schema_version"] != 1
            or not isinstance(manifest["starting_release"], Mapping)
            or manifest["starting_release"].get("tag") != case.starting_tag
            or manifest["foundation_release"] != foundation.identity()
            or manifest["follow_up_release"] != follow_up.identity()
            or not isinstance(manifest["events"], list)
            or not isinstance(manifest["artifacts"], Mapping)
        ):
            raise FleetError(f"{case.starting_tag}: evidence manifest is not bound to this journey")
        if any(not isinstance(event, Mapping) for event in manifest["events"]):
            raise FleetError(f"{case.starting_tag}: evidence manifest contains an invalid event")
        event_ids = [event.get("id") for event in manifest["events"]]
        required_order = [
            "historic-update-surface",
            "historic-route-refusal",
            "bridge-foundation",
            "foundation-update-surface",
            "foundation-preview",
            "foundation-approval",
            "foundation-receipt",
            "follow-up-installed",
            "follow-up-doctor",
            "follow-up-smoke",
        ]
        if event_ids != required_order:
            raise FleetError(f"{case.starting_tag}: evidence manifest has an invalid event order")
        events = {str(event["id"]): event for event in manifest["events"]}
        if any(
            not isinstance(event.get("command"), list)
            or not event["command"]
            or any(not isinstance(part, str) or not part for part in event["command"])
            for event in events.values()
        ):
            raise FleetError(f"{case.starting_tag}: evidence manifest contains an invalid command")
        if (
            events["historic-update-surface"].get("command")
            != ["git", "show", f"{case.starting_tag}:{UPDATE_SKILL_RELATIVE}"]
            or events["historic-update-surface"].get("release") != expected_historic_surface["release"]
            or events["historic-update-surface"].get("skill_sha256")
            != expected_historic_surface["skill_sha256"]
            or events["historic-update-surface"].get("rescue_sha256")
            != expected_historic_surface["rescue_sha256"]
            or events["historic-route-refusal"].get("release") != expected_historic_surface["release"]
            or events["bridge-foundation"].get("release") != foundation.identity()
            or events["foundation-update-surface"].get("release") != foundation.identity()
            or events["foundation-update-surface"].get("skill_sha256")
            != expected_foundation_surface["skill_sha256"]
            or events["foundation-update-surface"].get("rescue_sha256")
            != expected_foundation_surface["rescue_sha256"]
            or events["foundation-preview"].get("from_release") != foundation.identity()
            or events["foundation-preview"].get("target_release") != follow_up.identity()
            or events["foundation-approval"].get("target_release") != follow_up.identity()
            or events["foundation-approval"].get("answer") != "APPLY"
            or events["foundation-receipt"].get("release") != follow_up.identity()
            or events["follow-up-installed"].get("release") != follow_up.identity()
            or events["follow-up-smoke"].get("platform") != case.platform
        ):
            raise FleetError(f"{case.starting_tag}: evidence manifest commands or identities are not bound")
        artifacts = manifest["artifacts"]
        if set(artifacts) != RUNNER_ARTIFACT_KEYS:
            raise FleetError(f"{case.starting_tag}: runner manifest has an invalid artifact set")
        artifact_paths = {
            name: _manifest_artifact(evidence_root, artifacts, name, case.starting_tag)
            for name in RUNNER_ARTIFACT_KEYS
        }
        if (
            artifact_paths["transcript"] != case.transcript_path
            or artifact_paths["foundation_receipt"] != case.foundation_receipt_path
            or artifact_paths["follow_up_receipt"] != case.follow_up_receipt_path
            or artifact_paths["foundation_doctor"] != case.foundation_doctor_path
            or artifact_paths["follow_up_doctor"] != case.follow_up_doctor_path
            or artifact_paths["follow_up_smoke"] != case.follow_up_smoke_path
        ):
            raise FleetError(f"{case.starting_tag}: evidence manifest artifacts are not bound")
        for artifact_name, expected_surface in (
            ("historic_update_surface", expected_historic_surface),
            ("foundation_update_surface", expected_foundation_surface),
        ):
            surface = _strict_object(
                _evidence_file(
                    evidence_root,
                    artifact_paths[artifact_name],
                    f"{case.starting_tag} {artifact_name}",
                ).read_bytes(),
                f"{case.starting_tag} {artifact_name}",
                frozenset(expected_surface),
            )
            if surface != expected_surface:
                raise FleetError(f"{case.starting_tag}: {artifact_name} is not the released update surface")
        transcript = _evidence_file(evidence_root, case.transcript_path, f"{case.starting_tag} transcript")
        transcript_value = _strict_object(transcript.read_bytes(), f"{case.starting_tag} transcript", frozenset({"events"}))
        if not isinstance(transcript_value["events"], list) or transcript_value["events"] != manifest["events"]:
            raise FleetError(f"{case.starting_tag}: transcript has no journey events")
        foundation_receipt = _read_evidence_json(
            evidence_root, case.foundation_receipt_path, f"{case.starting_tag} foundation receipt"
        )
        follow_receipt = _read_evidence_json(
            evidence_root, case.follow_up_receipt_path, f"{case.starting_tag} follow-up receipt"
        )
        if foundation_receipt["release"] != foundation.identity() or not _has_transaction_receipt(
            foundation_receipt["receipt"]
        ):
            raise FleetError(f"{case.starting_tag}: foundation receipt is not bound to the supplied release")
        if follow_receipt["release"] != follow_up.identity() or not _has_transaction_receipt(
            follow_receipt["receipt"]
        ):
            raise FleetError(f"{case.starting_tag}: follow-up receipt is not bound to the supplied release")
        for label, relative in (
            ("foundation Doctor", case.foundation_doctor_path),
            ("follow-up Doctor", case.follow_up_doctor_path),
        ):
            doctor = _evidence_file(evidence_root, relative, f"{case.starting_tag} {label}")
            try:
                doctor_value = json.loads(doctor.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                raise FleetError(f"{case.starting_tag}: {label} is not valid JSON") from error
            checks = doctor_value.get("checks") if isinstance(doctor_value, Mapping) else None
            if not isinstance(checks, list) or not checks or any(
                not isinstance(item, Mapping) or item.get("verdict") not in {"OK", "OFF"}
                for item in checks
            ):
                raise FleetError(f"{case.starting_tag}: {label} is unhealthy or incomplete")
        smoke = _evidence_file(evidence_root, case.follow_up_smoke_path, f"{case.starting_tag} smoke")
        try:
            smoke_value = json.loads(smoke.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise FleetError(f"{case.starting_tag}: smoke evidence is not valid JSON") from error
        if (
            not isinstance(smoke_value, Mapping)
            or smoke_value.get("status") != "OK"
            or smoke_value.get("platform") != case.platform
        ):
            raise FleetError(f"{case.starting_tag}: smoke/platform evidence is not bound")


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
    platforms_raw = raw.get("platforms")
    if (
        not isinstance(platforms_raw, list)
        or not platforms_raw
        or any(not isinstance(platform, str) or not platform for platform in platforms_raw)
    ):
        raise FleetError("acceptance report platforms must be a non-empty list of strings")
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
                foundation_receipt_path=_required_string(case_raw, "foundation_receipt_path", context),
                follow_up_receipt_path=_required_string(case_raw, "follow_up_receipt_path", context),
                foundation_doctor_path=_required_string(case_raw, "foundation_doctor_path", context),
                follow_up_doctor_path=_required_string(case_raw, "follow_up_doctor_path", context),
                follow_up_smoke_path=_required_string(case_raw, "follow_up_smoke_path", context),
                platform=_required_string(case_raw, "platform", context),
                evidence_manifest_path=_required_string(case_raw, "evidence_manifest_path", context),
                evidence_manifest_sha256=_required_string(case_raw, "evidence_manifest_sha256", context),
            )
        )
    return AcceptanceReport(foundation_tag, follow_up_tag, tuple(cases), tuple(platforms_raw))


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


def starting_release_manifest(releases: Sequence[DistributionRelease]) -> dict[str, object]:
    """Return the generated, exact release-tree set that a fleet report must cover."""

    cases = [_release_manifest(release) for release in releases]
    return {"schema_version": 1, "case_count": len(cases), "cases": cases}


def releases_from_starting_manifest(
    source: str, *, current_releases: Sequence[DistributionRelease]
) -> tuple[DistributionRelease, ...]:
    """Parse a generated manifest and reject drift from the current immutable tags."""

    try:
        raw = json.loads(source)
    except json.JSONDecodeError as error:
        raise FleetError("historic release manifest is not valid JSON") from error
    if not isinstance(raw, Mapping) or set(raw) != STARTING_MANIFEST_KEYS or raw.get("schema_version") != 1:
        raise FleetError("historic release manifest has an invalid shape")
    cases = raw.get("cases")
    count = raw.get("case_count")
    if not isinstance(cases, list) or not isinstance(count, int) or count != len(cases):
        raise FleetError("historic release manifest has an invalid case count")
    parsed: list[DistributionRelease] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, Mapping) or set(case) != STARTING_RELEASE_KEYS:
            raise FleetError(f"historic release manifest case {index} has an invalid shape")
        values = {name: case[name] for name in STARTING_RELEASE_KEYS}
        if any(not isinstance(value, str) or not value for value in values.values()):
            raise FleetError(f"historic release manifest case {index} has invalid values")
        parsed.append(
            DistributionRelease(
                tag=values["tag"],
                version=values["version"],
                commit=values["commit"],
                tree=values["tree"],
            )
        )
    if len({release.tag for release in parsed}) != len(parsed):
        raise FleetError("historic release manifest contains duplicate tags")
    expected = tuple(current_releases)
    if tuple(_release_manifest(release) for release in parsed) != tuple(
        _release_manifest(release) for release in expected
    ):
        raise FleetError("historic release manifest does not match the current immutable release trees")
    return tuple(parsed)


def main(argv: Sequence[str] | None = None) -> int:
    """Build, exercise, or validate deterministic historic release journeys."""

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
    check.add_argument(
        "--starting-manifest",
        type=Path,
        required=True,
        help="generated output from the manifest command for this exact immutable release set",
    )
    check.add_argument("report", type=Path)
    journey = subcommands.add_parser(
        "journey",
        help="record immutable update surfaces and fail closed until an executable journey protocol ships",
    )
    journey.add_argument("--repo", type=Path, required=True)
    journey.add_argument("--output", type=Path, required=True)
    journey.add_argument("--starting-tag", required=True)
    journey.add_argument("--foundation-tag", required=True)
    journey.add_argument("--follow-up-tag", required=True)
    args = parser.parse_args(argv)

    if args.command == "manifest":
        releases = discover_distribution_releases(args.repo)
        print(
            json.dumps(
                starting_release_manifest(releases),
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

    if args.command == "journey":
        run_journey(
            args.repo,
            output=args.output,
            starting_tag=args.starting_tag,
            foundation_tag=args.foundation_tag,
            follow_up_tag=args.follow_up_tag,
        )
        raise FleetError("journey returned without an immutable executable protocol")

    report = acceptance_report_from_json(args.report.read_text(encoding="utf-8"))
    foundation = resolve_immutable_release(args.repo, report.foundation_tag)
    follow_up = resolve_immutable_release(args.repo, report.follow_up_tag)
    if foundation.tag == follow_up.tag or foundation.commit == follow_up.commit:
        raise FleetError("acceptance report foundation and follow-up are not distinct immutable releases")
    generated_starting_releases = releases_from_starting_manifest(
        args.starting_manifest.read_text(encoding="utf-8"),
        current_releases=discover_distribution_releases(args.repo),
    )
    expected_start_tags = {release.tag for release in generated_starting_releases}
    assert_complete(report, expected_start_tags)
    assert_evidence_bound(
        report,
        repo=args.repo,
        evidence_root=args.report.parent.resolve(),
        foundation=foundation,
        follow_up=follow_up,
    )
    print(f"PASS: {len(report.cases)} historic release trees reached both releases")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FleetError as error:
        raise SystemExit(f"FAIL: {error}") from error
