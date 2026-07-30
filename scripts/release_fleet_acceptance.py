#!/usr/bin/env python3
"""Fail-closed orchestration for the cross-platform historic updater fleet."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import stat
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.update.journey_protocol import (
    SUPPORTED_PLATFORMS,
    JourneyProtocolError,
    load_update_journey_protocol,
)
from scripts import release_fleet
from scripts.dex_update_bridge import FOUNDATION

EXPECTED_HISTORIC_CASES = 168
COHORT_SCHEMA_VERSION = 1
ACCEPTANCE_SOURCE = "scripts/release_fleet_acceptance.py"
_COHORT_FIELDS = frozenset({"schema_version", "foundation", "case_count", "cases"})
_RELEASE_FIELDS = frozenset({"tag", "version", "commit", "tree"})
_SEMVER = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)$"
)
_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_SIGNED_FIELDS = frozenset({"payload", "signature"})
_SESSION_FIELDS = frozenset(
    {
        "schema_version",
        "session_id",
        "cohort_sha256",
        "foundation",
        "follow_up_tag",
        "source_commit",
        "acceptance_source_sha256",
        "platforms",
        "case_count",
        "journey_count",
    }
)
_RECEIPT_FIELDS = frozenset(
    {
        "schema_version",
        "session_id",
        "platform",
        "cohort_sha256",
        "foundation_tag",
        "follow_up_tag",
        "source_commit",
        "acceptance_source_sha256",
        "case_count",
        "started",
        "completed",
        "passed",
        "failed",
        "case_result_sha256",
    }
)


@dataclass(frozen=True)
class PlatformExecution:
    """One process's in-memory report and still-live executor capabilities."""

    report: release_fleet.AcceptanceReport
    executor_runs: tuple[object, ...]
    counts: dict[str, int]


@dataclass(frozen=True)
class FleetInputs:
    """All immutable identities shared by one acceptance session."""

    releases: tuple[release_fleet.DistributionRelease, ...]
    foundation: release_fleet.ImmutableRelease
    follow_up: release_fleet.ImmutableRelease
    protocol: object
    source_commit: str
    acceptance_source_sha256: str
    cohort_sha256: str


class PlatformFleetFailure(release_fleet.FleetError):
    """One platform stopped before its complete live verdict."""

    def __init__(self, message: str, counts: Mapping[str, int]) -> None:
        super().__init__(message)
        self.counts = dict(counts)


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = _SEMVER.fullmatch(value)
    if match is None:
        raise release_fleet.FleetError(f"historic release has invalid version: {value}")
    return tuple(int(match[name]) for name in ("major", "minor", "patch"))


def _release_document(release: release_fleet.DistributionRelease) -> dict[str, str]:
    return {
        "tag": release.tag,
        "version": release.version,
        "commit": release.commit,
        "tree": release.tree,
    }


def _foundation_document(foundation: Mapping[str, str] | None) -> dict[str, str]:
    expected = FOUNDATION.identity()
    supplied = dict(foundation) if foundation is not None else expected
    if supplied != expected:
        raise release_fleet.FleetError("historic cohort foundation identity does not match the pinned bridge")
    return expected


def _historic_releases(
    releases: Sequence[release_fleet.DistributionRelease],
    *,
    foundation: Mapping[str, str],
) -> tuple[release_fleet.DistributionRelease, ...]:
    boundary = _version_tuple(foundation["version"])
    historic = tuple(release for release in releases if _version_tuple(release.version) <= boundary)
    expected_foundation = {field: foundation[field] for field in ("tag", "version", "commit", "tree")}
    if sum(_release_document(release) == expected_foundation for release in historic) != 1:
        raise release_fleet.FleetError("historic cohort does not contain the exact pinned foundation release")
    return historic


def frozen_cohort_manifest(
    releases: Sequence[release_fleet.DistributionRelease],
    *,
    foundation: Mapping[str, str] | None = None,
    expected_count: int = EXPECTED_HISTORIC_CASES,
) -> dict[str, object]:
    """Freeze the accepted historic trees through the immutable foundation."""

    foundation_identity = _foundation_document(foundation)
    historic = _historic_releases(releases, foundation=foundation_identity)
    if len(historic) != expected_count:
        raise release_fleet.FleetError(f"historic cohort has {len(historic)} trees; expected {expected_count}")
    return {
        "schema_version": COHORT_SCHEMA_VERSION,
        "foundation": foundation_identity,
        "case_count": len(historic),
        "cases": [_release_document(release) for release in historic],
    }


def releases_from_frozen_cohort(
    source: str,
    *,
    current_releases: Sequence[release_fleet.DistributionRelease],
    foundation: Mapping[str, str] | None = None,
    expected_count: int = EXPECTED_HISTORIC_CASES,
) -> tuple[release_fleet.DistributionRelease, ...]:
    """Validate a frozen cohort while allowing only post-foundation releases."""

    foundation_identity = _foundation_document(foundation)
    try:
        document = json.loads(source)
    except json.JSONDecodeError as error:
        raise release_fleet.FleetError("historic cohort manifest is not valid JSON") from error
    if (
        not isinstance(document, Mapping)
        or set(document) != _COHORT_FIELDS
        or document.get("schema_version") != COHORT_SCHEMA_VERSION
        or document.get("foundation") != foundation_identity
    ):
        raise release_fleet.FleetError("historic cohort manifest has an invalid foundation identity or shape")
    cases = document.get("cases")
    count = document.get("case_count")
    if not isinstance(cases, list) or not isinstance(count, int) or count != expected_count or count != len(cases):
        raise release_fleet.FleetError("historic cohort manifest has an invalid case count")

    parsed: list[release_fleet.DistributionRelease] = []
    for index, case in enumerate(cases, start=1):
        if (
            not isinstance(case, Mapping)
            or set(case) != _RELEASE_FIELDS
            or any(not isinstance(case[field], str) or not case[field] for field in _RELEASE_FIELDS)
        ):
            raise release_fleet.FleetError(f"historic cohort manifest case {index} is invalid")
        parsed.append(
            release_fleet.DistributionRelease(
                tag=str(case["tag"]),
                version=str(case["version"]),
                commit=str(case["commit"]),
                tree=str(case["tree"]),
            )
        )
    if len({release.tag for release in parsed}) != len(parsed):
        raise release_fleet.FleetError("historic cohort manifest repeats a release tag")

    current_historic = _historic_releases(
        current_releases,
        foundation=foundation_identity,
    )
    parsed_by_tag = {release.tag: release for release in parsed}
    current_by_tag = {release.tag: release for release in current_historic}
    unexpected = sorted(current_by_tag.keys() - parsed_by_tag.keys())
    if unexpected:
        raise release_fleet.FleetError(
            "unexpected historical release appeared at or before the foundation: " + ", ".join(unexpected)
        )
    if parsed_by_tag != current_by_tag or tuple(parsed) != current_historic:
        raise release_fleet.FleetError("historic cohort identity drift")
    return tuple(parsed)


def assert_platform_report_bound(
    report: release_fleet.AcceptanceReport,
    *,
    protocol: object,
    running_platform: str,
    expected_start_tags: set[str],
) -> None:
    """Bind one live-process report to one member of the exact protocol set."""

    protocol_platforms = tuple(getattr(protocol, "platforms", ()))
    if protocol_platforms != SUPPORTED_PLATFORMS:
        raise release_fleet.FleetError("released journey protocol platforms are not the exact supported set")
    if running_platform not in protocol_platforms:
        raise release_fleet.FleetError("running platform is not declared by the protocol")
    if report.platforms != (running_platform,):
        raise release_fleet.FleetError("a live platform report must declare exactly one running platform")
    release_fleet.assert_complete(report, expected_start_tags)


def verify_acceptance_source_bound(repo: Path, source_commit: str) -> str:
    """Require this running orchestrator to equal its publisher-commit bytes."""

    if _HEX_40.fullmatch(source_commit) is None:
        raise release_fleet.FleetError("acceptance orchestrator source commit is invalid")
    try:
        released = release_fleet._tag_file(repo, source_commit, ACCEPTANCE_SOURCE)
    except release_fleet.FleetError as error:
        raise release_fleet.FleetError("released acceptance orchestrator source is unavailable") from error
    running = Path(__file__).resolve().read_bytes()
    if running != released:
        raise release_fleet.FleetError("running acceptance orchestrator bytes do not match the publisher commit")
    return hashlib.sha256(running).hexdigest()


def load_fleet_inputs(
    repo: Path,
    cohort_path: Path,
    *,
    foundation_tag: str,
    follow_up_tag: str,
) -> FleetInputs:
    """Resolve and bind every immutable input before any journey can start."""

    try:
        cohort_bytes = cohort_path.read_bytes()
    except OSError as error:
        raise release_fleet.FleetError("historic cohort manifest is unavailable") from error
    try:
        cohort_source = cohort_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise release_fleet.FleetError("historic cohort manifest is not valid UTF-8") from error
    releases = releases_from_frozen_cohort(
        cohort_source,
        current_releases=release_fleet.discover_distribution_releases(repo),
    )
    foundation = release_fleet.resolve_immutable_release(repo, foundation_tag)
    follow_up = release_fleet.resolve_immutable_release(repo, follow_up_tag)
    if foundation.identity() != FOUNDATION.identity():
        raise release_fleet.FleetError("fleet acceptance foundation is not the pinned v1.80.5 identity")
    if foundation.tag == follow_up.tag or foundation.commit == follow_up.commit:
        raise release_fleet.FleetError("foundation and follow-up must be different immutable releases")
    try:
        protocol = load_update_journey_protocol(
            release_fleet._tag_file(
                repo,
                follow_up.tag,
                release_fleet.UPDATE_JOURNEY_RELATIVE,
            )
        )
    except (release_fleet.FleetError, JourneyProtocolError) as error:
        raise release_fleet.FleetError("follow-up released journey protocol is unavailable or invalid") from error
    _require_protocol_platforms(protocol.platforms)
    if protocol.foundation != foundation.identity():
        raise release_fleet.FleetError("released journey protocol names a different foundation")
    source_commit = release_fleet._verify_released_protocol_artifacts(
        repo,
        follow_up,
        protocol,
    )
    acceptance_source_sha256 = verify_acceptance_source_bound(repo, source_commit)
    return FleetInputs(
        releases=releases,
        foundation=foundation,
        follow_up=follow_up,
        protocol=protocol,
        source_commit=source_commit,
        acceptance_source_sha256=acceptance_source_sha256,
        cohort_sha256=hashlib.sha256(cohort_bytes).hexdigest(),
    )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sign(payload: Mapping[str, object], key: bytes) -> dict[str, object]:
    if not isinstance(key, bytes) or len(key) != 32:
        raise release_fleet.FleetError("fleet acceptance session key must be exactly 32 bytes")
    return {
        "payload": dict(payload),
        "signature": hmac.new(
            key,
            _canonical_bytes(payload),
            hashlib.sha256,
        ).hexdigest(),
    }


def _verified_payload(
    signed: object,
    *,
    key: bytes,
    fields: frozenset[str],
    context: str,
) -> dict[str, object]:
    if not isinstance(signed, Mapping) or set(signed) != _SIGNED_FIELDS:
        raise release_fleet.FleetError(f"{context} has an invalid signed shape")
    payload = signed.get("payload")
    signature = signed.get("signature")
    if (
        not isinstance(payload, Mapping)
        or set(payload) != fields
        or not isinstance(signature, str)
        or _HEX_64.fullmatch(signature) is None
    ):
        raise release_fleet.FleetError(f"{context} has an invalid signed shape")
    expected = _sign(dict(payload), key)["signature"]
    assert isinstance(expected, str)
    if not hmac.compare_digest(signature, expected):
        raise release_fleet.FleetError(f"{context} signature is invalid")
    return dict(payload)


def _require_protocol_platforms(platforms: Sequence[str]) -> tuple[str, ...]:
    value = tuple(platforms)
    if value != SUPPORTED_PLATFORMS:
        raise release_fleet.FleetError("fleet acceptance protocol platforms are not exactly darwin and linux")
    return value


def create_acceptance_session(
    *,
    cohort_sha256: str,
    foundation: Mapping[str, str] | None,
    follow_up_tag: str,
    source_commit: str,
    acceptance_source_sha256: str,
    protocol_platforms: Sequence[str],
    key: bytes,
    expected_count: int = EXPECTED_HISTORIC_CASES,
    session_id: str,
) -> dict[str, object]:
    """Create one authenticated session shared by both platform processes."""

    platforms = _require_protocol_platforms(protocol_platforms)
    foundation_identity = _foundation_document(foundation)
    if (
        _HEX_64.fullmatch(cohort_sha256) is None
        or _HEX_64.fullmatch(acceptance_source_sha256) is None
        or _HEX_64.fullmatch(session_id) is None
        or _HEX_40.fullmatch(source_commit) is None
        or release_fleet.RELEASE_TAG.fullmatch(follow_up_tag) is None
        or expected_count < 1
    ):
        raise release_fleet.FleetError("fleet acceptance session identity is invalid")
    return _sign(
        {
            "schema_version": 1,
            "session_id": session_id,
            "cohort_sha256": cohort_sha256,
            "foundation": foundation_identity,
            "follow_up_tag": follow_up_tag,
            "source_commit": source_commit,
            "acceptance_source_sha256": acceptance_source_sha256,
            "platforms": list(platforms),
            "case_count": expected_count,
            "journey_count": expected_count * len(platforms),
        },
        key,
    )


def sign_platform_receipt(
    session: object,
    *,
    platform: str,
    case_result_sha256: str,
    key: bytes,
    started: int,
    completed: int,
    passed: int,
    failed: int,
) -> dict[str, object]:
    """Authenticate a live platform verdict for later cross-process aggregation."""

    session_payload = _verified_payload(
        session,
        key=key,
        fields=_SESSION_FIELDS,
        context="fleet acceptance session",
    )
    platforms = _require_protocol_platforms(
        session_payload.get("platforms", ())  # type: ignore[arg-type]
    )
    if (
        platform not in platforms
        or _HEX_64.fullmatch(case_result_sha256) is None
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in (started, completed, passed, failed)
        )
    ):
        raise release_fleet.FleetError("platform fleet receipt identity is invalid")
    foundation = session_payload["foundation"]
    assert isinstance(foundation, Mapping)
    return _sign(
        {
            "schema_version": 1,
            "session_id": session_payload["session_id"],
            "platform": platform,
            "cohort_sha256": session_payload["cohort_sha256"],
            "foundation_tag": foundation["tag"],
            "follow_up_tag": session_payload["follow_up_tag"],
            "source_commit": session_payload["source_commit"],
            "acceptance_source_sha256": session_payload["acceptance_source_sha256"],
            "case_count": session_payload["case_count"],
            "started": started,
            "completed": completed,
            "passed": passed,
            "failed": failed,
            "case_result_sha256": case_result_sha256,
        },
        key,
    )


def aggregate_signed_platform_receipts(
    session: object,
    receipts: Sequence[object],
    *,
    key: bytes,
    protocol_platforms: Sequence[str],
    expected_count: int = EXPECTED_HISTORIC_CASES,
) -> dict[str, object]:
    """Produce one verdict from exact signed Darwin and Linux process receipts."""

    platforms = _require_protocol_platforms(protocol_platforms)
    session_payload = _verified_payload(
        session,
        key=key,
        fields=_SESSION_FIELDS,
        context="fleet acceptance session",
    )
    if (
        tuple(session_payload.get("platforms", ())) != platforms
        or session_payload.get("case_count") != expected_count
        or session_payload.get("journey_count") != expected_count * len(platforms)
    ):
        raise release_fleet.FleetError("fleet acceptance session is not bound to the protocol platforms and cohort")

    by_platform: dict[str, dict[str, object]] = {}
    for signed in receipts:
        receipt = _verified_payload(
            signed,
            key=key,
            fields=_RECEIPT_FIELDS,
            context="platform fleet receipt",
        )
        platform = receipt.get("platform")
        if not isinstance(platform, str) or platform in by_platform:
            raise release_fleet.FleetError("platform receipts do not cover the exact protocol platforms")
        by_platform[platform] = receipt
    if set(by_platform) != set(platforms) or len(by_platform) != len(platforms):
        raise release_fleet.FleetError("platform receipts do not cover the exact protocol platforms")

    for platform in platforms:
        receipt = by_platform[platform]
        foundation = session_payload["foundation"]
        assert isinstance(foundation, Mapping)
        identity_fields = (
            receipt.get("session_id") == session_payload["session_id"],
            receipt.get("cohort_sha256") == session_payload["cohort_sha256"],
            receipt.get("foundation_tag") == foundation["tag"],
            receipt.get("follow_up_tag") == session_payload["follow_up_tag"],
            receipt.get("source_commit") == session_payload["source_commit"],
            receipt.get("acceptance_source_sha256") == session_payload["acceptance_source_sha256"],
            receipt.get("case_count") == expected_count,
            isinstance(receipt.get("case_result_sha256"), str)
            and _HEX_64.fullmatch(str(receipt["case_result_sha256"])) is not None,
        )
        if not all(identity_fields):
            raise release_fleet.FleetError(f"{platform}: platform fleet receipt is not bound to the session")
        counts = tuple(receipt.get(field) for field in ("started", "completed", "passed", "failed"))
        if counts != (expected_count, expected_count, expected_count, 0):
            raise release_fleet.FleetError(f"{platform}: platform fleet receipt is incomplete or failed")

    total = expected_count * len(platforms)
    return {
        "outcome": "HISTORIC_FLEET_ACCEPTED",
        "acceptance": True,
        "platforms": list(platforms),
        "case_count": expected_count,
        "journey_count": total,
        "discovered": expected_count,
        "started": total,
        "completed": total,
        "passed": total,
        "failed": 0,
        "session_id": session_payload["session_id"],
    }


def collect_platform_runs(
    repo: Path,
    *,
    output: Path,
    releases: Sequence[release_fleet.DistributionRelease],
    foundation_tag: str,
    follow_up_tag: str,
    running_platform: str,
    journey_runner: Callable[..., object] = release_fleet.run_journey,
) -> PlatformExecution:
    """Run one platform sequentially and retain every live executor result."""

    counts = {
        "discovered": len(releases),
        "started": 0,
        "completed": 0,
        "passed": 0,
        "failed": 0,
    }
    executor_runs: list[object] = []
    case_documents: list[dict[str, object]] = []
    for release in releases:
        counts["started"] += 1
        try:
            run = journey_runner(
                repo,
                output=output,
                starting_tag=release.tag,
                foundation_tag=foundation_tag,
                follow_up_tag=follow_up_tag,
            )
            case = getattr(run, "case", None)
            if not isinstance(case, Mapping):
                raise release_fleet.FleetError(f"{release.tag}: journey returned no live case evidence")
            case_documents.append(dict(case))
            executor_runs.append(run)
            counts["completed"] += 1
            counts["passed"] += 1
        except Exception as error:
            counts["failed"] += 1
            raise PlatformFleetFailure(
                f"{release.tag}: platform journey failed: {error}",
                counts,
            ) from error

    try:
        report = release_fleet.acceptance_report_from_json(
            json.dumps(
                {
                    "foundation_tag": foundation_tag,
                    "follow_up_tag": follow_up_tag,
                    "platforms": [running_platform],
                    "cases": case_documents,
                },
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
    except Exception as error:
        counts["failed"] += 1
        raise PlatformFleetFailure(
            f"platform journey report is malformed: {error}",
            counts,
        ) from error
    return PlatformExecution(report, tuple(executor_runs), counts)


def _platform_receipt_boundary():
    evidence_validator = release_fleet.assert_evidence_bound
    complete_validator = release_fleet.assert_complete
    platform_validator = assert_platform_report_bound

    def finalize_live_platform_execution(
        execution: PlatformExecution,
        *,
        repo: Path,
        evidence_root: Path,
        foundation: release_fleet.ImmutableRelease,
        follow_up: release_fleet.ImmutableRelease,
        protocol: object,
        expected_start_tags: set[str],
        session: object,
        key: bytes,
        cohort_sha256: str,
        source_commit: str,
        acceptance_source_sha256: str,
        expected_count: int = EXPECTED_HISTORIC_CASES,
    ) -> dict[str, object]:
        """Validate live authority, then and only then authenticate one receipt."""

        if (
            release_fleet.assert_evidence_bound is not evidence_validator
            or release_fleet.assert_complete is not complete_validator
            or globals().get("assert_platform_report_bound") is not platform_validator
        ):
            raise release_fleet.FleetError("fleet acceptance validator changed during the live process")
        platform_validator(
            execution.report,
            protocol=protocol,
            running_platform=execution.report.platforms[0] if len(execution.report.platforms) == 1 else "",
            expected_start_tags=expected_start_tags,
        )
        evidence_validator(
            execution.report,
            repo=repo,
            evidence_root=evidence_root,
            foundation=foundation,
            follow_up=follow_up,
            executor_runs=execution.executor_runs,
        )

        counts = execution.counts
        if counts != {
            "discovered": expected_count,
            "started": expected_count,
            "completed": expected_count,
            "passed": expected_count,
            "failed": 0,
        }:
            raise release_fleet.FleetError("live platform execution is incomplete or failed")
        session_payload = _verified_payload(
            session,
            key=key,
            fields=_SESSION_FIELDS,
            context="fleet acceptance session",
        )
        if (
            session_payload.get("cohort_sha256") != cohort_sha256
            or session_payload.get("foundation") != foundation.identity()
            or session_payload.get("follow_up_tag") != follow_up.tag
            or session_payload.get("source_commit") != source_commit
            or session_payload.get("acceptance_source_sha256") != acceptance_source_sha256
            or session_payload.get("case_count") != expected_count
            or tuple(session_payload.get("platforms", ())) != tuple(getattr(protocol, "platforms", ()))
        ):
            raise release_fleet.FleetError("live platform execution is not bound to the acceptance session")
        cases = [
            {field: getattr(case, field) for field in sorted(release_fleet.CASE_RESULT_KEYS)}
            for case in execution.report.cases
        ]
        return sign_platform_receipt(
            session,
            platform=execution.report.platforms[0],
            case_result_sha256=hashlib.sha256(_canonical_bytes(cases)).hexdigest(),
            key=key,
            started=counts["started"],
            completed=counts["completed"],
            passed=counts["passed"],
            failed=counts["failed"],
        )

    return finalize_live_platform_execution


finalize_live_platform_execution = _platform_receipt_boundary()
del _platform_receipt_boundary


def _write_exclusive(path: Path, content: bytes, *, mode: int) -> None:
    if not path.parent.is_dir():
        raise release_fleet.FleetError(f"acceptance output parent does not exist: {path.parent}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
    except FileExistsError as error:
        raise release_fleet.FleetError(f"acceptance output already exists: {path}") from error
    try:
        view = memoryview(content)
        while view:
            view = view[os.write(descriptor, view) :]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def write_session_key(path: Path, *, key: bytes | None = None) -> bytes:
    """Create one private, non-reusable acceptance-session key."""

    value = secrets.token_bytes(32) if key is None else key
    if not isinstance(value, bytes) or len(value) != 32:
        raise release_fleet.FleetError("fleet acceptance session key must be exactly 32 bytes")
    _write_exclusive(path, value, mode=0o600)
    return value


def read_session_key(path: Path) -> bytes:
    """Open one private key without following links or accepting loose modes."""

    try:
        metadata = path.lstat()
    except OSError as error:
        raise release_fleet.FleetError("fleet acceptance session key is missing") from error
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o600
        or path.is_symlink()
        or metadata.st_size != 32
    ):
        raise release_fleet.FleetError("fleet acceptance session key is unsafe")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            value = os.read(descriptor, 33)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise release_fleet.FleetError("fleet acceptance session key is unsafe") from error
    if len(value) != 32:
        raise release_fleet.FleetError("fleet acceptance session key is unsafe")
    return value


def _read_json(path: Path, *, context: str) -> object:
    try:
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
            raise OSError("not a regular file")
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise release_fleet.FleetError(f"{context} is unavailable or invalid") from error


def _assert_session_matches_inputs(
    session: object,
    *,
    key: bytes,
    inputs: FleetInputs,
) -> dict[str, object]:
    payload = _verified_payload(
        session,
        key=key,
        fields=_SESSION_FIELDS,
        context="fleet acceptance session",
    )
    expected = {
        "schema_version": 1,
        "cohort_sha256": inputs.cohort_sha256,
        "foundation": inputs.foundation.identity(),
        "follow_up_tag": inputs.follow_up.tag,
        "source_commit": inputs.source_commit,
        "acceptance_source_sha256": inputs.acceptance_source_sha256,
        "platforms": list(_require_protocol_platforms(inputs.protocol.platforms)),
        "case_count": EXPECTED_HISTORIC_CASES,
        "journey_count": EXPECTED_HISTORIC_CASES * len(SUPPORTED_PLATFORMS),
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        raise release_fleet.FleetError("fleet acceptance session does not match the immutable fleet inputs")
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or _HEX_64.fullmatch(session_id) is None:
        raise release_fleet.FleetError("fleet acceptance session identity is invalid")
    return payload


def _running_platform() -> str:
    if sys.platform == "darwin":
        return "darwin"
    if sys.platform.startswith("linux"):
        return "linux"
    raise release_fleet.FleetError("historic fleet acceptance supports macOS and Linux only")


def _add_bound_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--foundation-tag", required=True)
    parser.add_argument("--follow-up-tag", required=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Freeze, execute, or aggregate the formal historic release fleet."""

    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    cohort = subcommands.add_parser(
        "cohort",
        help="freeze all immutable historic trees through the pinned foundation",
    )
    cohort.add_argument("--repo", type=Path, required=True)
    cohort.add_argument("--output", type=Path, required=True)
    session = subcommands.add_parser(
        "session",
        help="bind one authenticated acceptance session to immutable release inputs",
    )
    _add_bound_input_arguments(session)
    session.add_argument("--session-output", type=Path, required=True)
    session.add_argument("--key-output", type=Path, required=True)
    platform = subcommands.add_parser(
        "platform",
        help="run all frozen starts on this platform and mint one live-bound receipt",
    )
    _add_bound_input_arguments(platform)
    platform.add_argument("--session", type=Path, required=True)
    platform.add_argument("--key", type=Path, required=True)
    platform.add_argument("--output", type=Path, required=True)
    platform.add_argument("--receipt-output", type=Path, required=True)
    aggregate = subcommands.add_parser(
        "aggregate",
        help="verify exact Darwin and Linux receipts and produce one fleet verdict",
    )
    _add_bound_input_arguments(aggregate)
    aggregate.add_argument("--session", type=Path, required=True)
    aggregate.add_argument("--key", type=Path, required=True)
    aggregate.add_argument(
        "--receipt",
        action="append",
        type=Path,
        required=True,
        help="signed platform receipt; provide once for Darwin and once for Linux",
    )
    aggregate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "cohort":
        manifest = frozen_cohort_manifest(release_fleet.discover_distribution_releases(args.repo))
        _write_exclusive(args.output, _json_bytes(manifest), mode=0o644)
        print(
            json.dumps(
                {
                    "outcome": "HISTORIC_COHORT_FROZEN",
                    "acceptance": False,
                    "foundation_tag": FOUNDATION.tag,
                    "case_count": manifest["case_count"],
                    "output": str(args.output),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    inputs = load_fleet_inputs(
        args.repo,
        args.cohort,
        foundation_tag=args.foundation_tag,
        follow_up_tag=args.follow_up_tag,
    )
    if args.command == "session":
        for output in (args.session_output, args.key_output):
            if output.exists() or output.is_symlink():
                raise release_fleet.FleetError(f"acceptance output already exists: {output}")
        key = write_session_key(args.key_output)
        signed_session = create_acceptance_session(
            cohort_sha256=inputs.cohort_sha256,
            foundation=inputs.foundation.identity(),
            follow_up_tag=inputs.follow_up.tag,
            source_commit=inputs.source_commit,
            acceptance_source_sha256=inputs.acceptance_source_sha256,
            protocol_platforms=inputs.protocol.platforms,
            key=key,
            session_id=secrets.token_hex(32),
        )
        _write_exclusive(
            args.session_output,
            _json_bytes(signed_session),
            mode=0o644,
        )
        print(
            json.dumps(
                {
                    "outcome": "HISTORIC_FLEET_SESSION_CREATED",
                    "acceptance": False,
                    "discovered": len(inputs.releases),
                    "started": 0,
                    "completed": 0,
                    "passed": 0,
                    "failed": 0,
                    "session_output": str(args.session_output),
                    "key_output": str(args.key_output),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    key = read_session_key(args.key)
    signed_session = _read_json(
        args.session,
        context="fleet acceptance session",
    )
    _assert_session_matches_inputs(signed_session, key=key, inputs=inputs)

    if args.command == "platform":
        if args.output.exists() or args.output.is_symlink():
            raise release_fleet.FleetError(f"platform fleet output already exists: {args.output}")
        try:
            args.output.mkdir(mode=0o700)
        except OSError as error:
            raise release_fleet.FleetError(f"platform fleet output cannot be created: {args.output}") from error
        running_platform = _running_platform()
        execution = collect_platform_runs(
            args.repo,
            output=args.output,
            releases=inputs.releases,
            foundation_tag=inputs.foundation.tag,
            follow_up_tag=inputs.follow_up.tag,
            running_platform=running_platform,
        )
        receipt = finalize_live_platform_execution(
            execution,
            repo=args.repo,
            evidence_root=args.output.resolve(),
            foundation=inputs.foundation,
            follow_up=inputs.follow_up,
            protocol=inputs.protocol,
            expected_start_tags={release.tag for release in inputs.releases},
            session=signed_session,
            key=key,
            cohort_sha256=inputs.cohort_sha256,
            source_commit=inputs.source_commit,
            acceptance_source_sha256=inputs.acceptance_source_sha256,
        )
        _write_exclusive(
            args.receipt_output,
            _json_bytes(receipt),
            mode=0o644,
        )
        print(
            json.dumps(
                {
                    "outcome": "HISTORIC_PLATFORM_ACCEPTED",
                    "acceptance": False,
                    "platform": running_platform,
                    **execution.counts,
                    "receipt_output": str(args.receipt_output),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    receipts = [_read_json(path, context=f"platform fleet receipt {path}") for path in args.receipt]
    result = aggregate_signed_platform_receipts(
        signed_session,
        receipts,
        key=key,
        protocol_platforms=inputs.protocol.platforms,
    )
    _write_exclusive(args.output, _json_bytes(result), mode=0o644)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except release_fleet.FleetError as error:
        raise SystemExit(f"FAIL: {error}") from error
