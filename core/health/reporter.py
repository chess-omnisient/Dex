"""Strict, versioned reporter contract for proactive Dex health.

Reporters contribute factual, snapshot-scoped check results.  This module does
not assign user impact, group root causes, choose severity, or authorize Doctor
repairs.  Those are separate layers with separate authority.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

CONTRACT_NAME = "dex.health.reporter"
CONTRACT_VERSION = 1
CONTRACT = f"{CONTRACT_NAME}/v{CONTRACT_VERSION}"

DEFAULT_CHECK_VERSION = "1.0.0"
NORMALIZER_NAMESPACE = "dex.health.normalizer"
NORMALIZER_ID = "validator"
NORMALIZER_VERSION = "1.0.0"

VERDICTS = frozenset({"OK", "OFF", "BROKEN", "UNKNOWN"})
FEATURE_STATUSES = frozenset({"ok", "off", "not_installed", "broken", "unknown"})

# These limits keep malformed reporter output from becoming a log or snapshot
# amplification vector.  The reporter contract carries technical detail only;
# long-form evidence belongs to Doctor and is added by a later layer.
MAX_DETAIL_LENGTH = 512
MAX_FEATURE_LENGTH = 160
MAX_DIAGNOSTIC_LENGTH = 240
MAX_RESULTS = 128

_TOKEN = r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*"
_TOKEN_RE = re.compile(rf"^{_TOKEN}$")
_QUALIFIED_CHECK_RE = re.compile(rf"^({_TOKEN})/({_TOKEN})$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_REFRESH_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

_ENVELOPE_KEYS = frozenset({"contract", "reporter", "refresh_id", "generated_at", "results"})
_REPORTER_KEYS = frozenset({"namespace", "id", "version"})
_REQUIRED_RESULT_KEYS = frozenset({"id", "check_version", "verdict", "detail"})
_RESULT_KEYS = _REQUIRED_RESULT_KEYS | frozenset({"feature", "feature_status"})


def _is_semver(value: object) -> bool:
    return isinstance(value, str) and _SEMVER_RE.fullmatch(value) is not None


def _is_token(value: object) -> bool:
    return isinstance(value, str) and _TOKEN_RE.fullmatch(value) is not None


def _bounded_text(value: object, limit: int) -> str:
    """Collapse whitespace and cap untrusted text before it enters a report."""

    text = value if isinstance(value, str) else str(value)
    text = " ".join(text.split())
    if not text:
        return "unknown"
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _error(errors: list[str], code: str, detail: object) -> None:
    errors.append(f"{code}: {_bounded_text(detail, MAX_DIAGNOSTIC_LENGTH)}")


def _timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _fallback_timestamp(now: datetime | None) -> str:
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return reference.isoformat()


@dataclass(frozen=True)
class ReporterIdentity:
    """Stable reporter identity; namespace is globally unique."""

    namespace: str
    id: str
    version: str

    def __post_init__(self) -> None:
        if not _is_token(self.namespace):
            raise ValueError("reporter namespace must be a lowercase stable token")
        if not _is_token(self.id):
            raise ValueError("reporter id must be a lowercase stable token")
        if not _is_semver(self.version):
            raise ValueError("reporter version must be strict SemVer")

    def to_dict(self) -> dict[str, str]:
        return {"namespace": self.namespace, "id": self.id, "version": self.version}


@dataclass(frozen=True)
class CheckResult:
    """One factual technical result from a reporter.

    User-facing status, severity, impact, dependency, freshness, evidence, and
    Doctor references deliberately do not appear here.  They are projections
    owned by proactive health and Doctor, not by an individual reporter.
    """

    id: str
    check_version: str
    verdict: str
    detail: str
    feature: str | None = None
    feature_status: str | None = None

    def __post_init__(self) -> None:
        if _QUALIFIED_CHECK_RE.fullmatch(self.id) is None:
            raise ValueError("check id must be a namespaced id such as doctor.core/jobs.fresh")
        if not _is_semver(self.check_version):
            raise ValueError("check_version must be strict SemVer")
        if self.verdict not in VERDICTS:
            raise ValueError(f"invalid Doctor verdict: {self.verdict!r}")
        if not isinstance(self.detail, str) or not self.detail.strip():
            raise ValueError("check detail must be a non-empty string")
        if len(self.detail) > MAX_DETAIL_LENGTH:
            raise ValueError("check detail exceeds the bounded reporter limit")
        if self.feature is not None:
            if not isinstance(self.feature, str) or not self.feature.strip():
                raise ValueError("check feature must be a non-empty string or null")
            if len(self.feature) > MAX_FEATURE_LENGTH:
                raise ValueError("check feature exceeds the bounded reporter limit")
        if self.feature_status is not None and self.feature_status not in FEATURE_STATUSES:
            raise ValueError(f"invalid feature status: {self.feature_status!r}")

    def to_dict(self) -> dict[str, str]:
        result: dict[str, str] = {
            "id": self.id,
            "check_version": self.check_version,
            "verdict": self.verdict,
            "detail": self.detail,
        }
        if self.feature is not None:
            result["feature"] = self.feature
        if self.feature_status is not None:
            result["feature_status"] = self.feature_status
        return result


@dataclass(frozen=True)
class ReporterSpec:
    """Known reporter identity plus its stable local check/version registry."""

    identity: ReporterIdentity
    checks: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for check_id, check_version in self.checks:
            if not _is_token(check_id):
                raise ValueError(f"invalid local check id: {check_id!r}")
            if check_id in seen:
                raise ValueError(f"duplicate local check id: {check_id!r}")
            if not _is_semver(check_version):
                raise ValueError(f"invalid check version for {check_id!r}")
            seen.add(check_id)

    @classmethod
    def from_mapping(
        cls,
        identity: ReporterIdentity,
        checks: Mapping[str, str],
    ) -> "ReporterSpec":
        return cls(identity=identity, checks=tuple(checks.items()))

    @property
    def check_versions(self) -> dict[str, str]:
        return dict(self.checks)

    def qualified_id(self, local_id: str) -> str:
        return f"{self.identity.namespace}/{local_id}"


@dataclass(frozen=True)
class ReporterEnvelope:
    """Canonical, validated reporter wire envelope."""

    contract: str
    reporter: ReporterIdentity
    refresh_id: str
    generated_at: str
    results: tuple[CheckResult, ...]

    def __post_init__(self) -> None:
        if self.contract != CONTRACT:
            raise ValueError(f"unsupported reporter contract: {self.contract!r}")
        if not isinstance(self.refresh_id, str) or _REFRESH_ID_RE.fullmatch(self.refresh_id) is None:
            raise ValueError("refresh_id must be a bounded opaque identifier")
        if not _timestamp(self.generated_at):
            raise ValueError("generated_at must be timezone-aware ISO-8601")
        if not isinstance(self.results, tuple) or not self.results:
            raise ValueError("reporter envelope must contain at least one result")
        if any(type(result) is not CheckResult for result in self.results):
            raise ValueError("reporter results must be CheckResult records")
        ids = [result.id for result in self.results]
        if len(ids) != len(set(ids)):
            raise ValueError("reporter envelope cannot contain duplicate check ids")
        if len(ids) > MAX_RESULTS:
            raise ValueError("reporter envelope contains too many results")

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": self.contract,
            "reporter": self.reporter.to_dict(),
            "refresh_id": self.refresh_id,
            "generated_at": self.generated_at,
            "results": [result.to_dict() for result in self.results],
        }


@dataclass(frozen=True)
class NormalizationResult:
    """Normalized report plus whether it was safe to accept as complete input."""

    report: ReporterEnvelope
    accepted: bool
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be boolean")
        if not isinstance(self.errors, tuple) or any(not isinstance(item, str) for item in self.errors):
            raise TypeError("normalization errors must be a tuple of strings")

    def to_dict(self) -> dict[str, Any]:
        return self.report.to_dict()


_NORMALIZER_IDENTITY = ReporterIdentity(
    namespace=NORMALIZER_NAMESPACE,
    id=NORMALIZER_ID,
    version=NORMALIZER_VERSION,
)


def _unknown_result(suffix: str, detail: object) -> CheckResult:
    safe_suffix = suffix if _is_token(suffix) else "invalid-result"
    return CheckResult(
        id=f"{NORMALIZER_NAMESPACE}/{safe_suffix}",
        check_version=DEFAULT_CHECK_VERSION,
        verdict="UNKNOWN",
        detail=_bounded_text(detail, MAX_DETAIL_LENGTH),
    )


def _valid_refresh_id(value: object) -> bool:
    return isinstance(value, str) and _REFRESH_ID_RE.fullmatch(value) is not None


def _parse_reporter(value: object) -> ReporterIdentity | None:
    if not isinstance(value, Mapping) or set(value) != _REPORTER_KEYS:
        return None
    try:
        return ReporterIdentity(
            namespace=value["namespace"],
            id=value["id"],
            version=value["version"],
        )
    except (TypeError, ValueError):
        return None


def _parse_check_id(value: object) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    match = _QUALIFIED_CHECK_RE.fullmatch(value)
    return match.groups() if match else None


def _unknown_for_entry(index: int, detail: object) -> CheckResult:
    return _unknown_result(f"invalid-result-{index}", detail)


def normalize_report(
    value: object,
    *,
    spec: ReporterSpec | None = None,
    now: datetime | None = None,
) -> NormalizationResult:
    """Validate and normalize an untrusted reporter envelope.

    A malformed or unsupported report is never silently discarded.  The
    returned canonical envelope contains one or more explicit ``UNKNOWN``
    technical results, while ``accepted`` tells a refresh publisher whether the
    report met its registered contract and completeness requirements.
    """

    errors: list[str] = []
    results: list[CheckResult] = []
    fallback_generated_at = _fallback_timestamp(now)

    if not isinstance(value, Mapping):
        _error(errors, "invalid-envelope", "report must be a JSON object")
        results.append(_unknown_result("invalid-report", "Reporter report was not a JSON object"))
        envelope = ReporterEnvelope(
            contract=CONTRACT,
            reporter=_NORMALIZER_IDENTITY,
            refresh_id="unknown-refresh",
            generated_at=fallback_generated_at,
            results=tuple(results),
        )
        return NormalizationResult(envelope, False, tuple(errors))

    keys = set(value)
    missing_keys = _ENVELOPE_KEYS - keys
    extra_keys = keys - _ENVELOPE_KEYS
    if missing_keys:
        _error(errors, "missing-envelope-fields", ", ".join(sorted(missing_keys)))
    if extra_keys:
        _error(errors, "unknown-envelope-fields", ", ".join(sorted(map(str, extra_keys))))

    contract = value.get("contract")
    contract_ok = contract == CONTRACT
    if not contract_ok:
        _error(errors, "unsupported-contract", contract if isinstance(contract, str) else type(contract).__name__)

    source_reporter = _parse_reporter(value.get("reporter"))
    if source_reporter is None:
        _error(errors, "invalid-reporter", "reporter identity is missing or malformed")

    reporter = source_reporter or _NORMALIZER_IDENTITY
    reporter_supported = contract_ok and source_reporter is not None
    if spec is not None:
        reporter_supported = reporter_supported and source_reporter == spec.identity
        if source_reporter is not None and source_reporter != spec.identity:
            _error(
                errors,
                "unsupported-reporter",
                f"{source_reporter.namespace}/{source_reporter.id}@{source_reporter.version}",
            )
    if not reporter_supported:
        reporter = _NORMALIZER_IDENTITY

    refresh_id = value.get("refresh_id")
    if not _valid_refresh_id(refresh_id):
        _error(errors, "invalid-refresh-id", "refresh_id is missing or malformed")
        refresh_id = "unknown-refresh"

    generated_at = value.get("generated_at")
    if not _timestamp(generated_at):
        _error(errors, "invalid-generated-at", "generated_at is missing or not timezone-aware ISO-8601")
        generated_at = fallback_generated_at

    raw_results = value.get("results")
    if not isinstance(raw_results, list):
        _error(errors, "invalid-results", "results must be a JSON array")
        raw_results = []

    if len(raw_results) > MAX_RESULTS:
        _error(errors, "too-many-results", f"at most {MAX_RESULTS} results are supported")
        raw_results = raw_results[:MAX_RESULTS]

    expected_versions = spec.check_versions if spec is not None and reporter_supported else {}
    seen: set[str] = set()

    if reporter_supported:
        for index, raw_result in enumerate(raw_results):
            if not isinstance(raw_result, Mapping):
                _error(errors, f"invalid-result-{index}", "result must be a JSON object")
                results.append(_unknown_for_entry(index, "Reporter result was not a JSON object"))
                continue

            result_keys = set(raw_result)
            missing_result_keys = _REQUIRED_RESULT_KEYS - result_keys
            extra_result_keys = result_keys - _RESULT_KEYS
            if missing_result_keys or extra_result_keys:
                if missing_result_keys:
                    _error(errors, f"invalid-result-{index}", f"missing fields: {', '.join(sorted(missing_result_keys))}")
                if extra_result_keys:
                    _error(
                        errors,
                        f"invalid-result-{index}",
                        f"unknown fields: {', '.join(sorted(map(str, extra_result_keys)))}",
                    )
                results.append(_unknown_for_entry(index, "Reporter result shape was not recognized"))
                continue

            parsed_id = _parse_check_id(raw_result.get("id"))
            if parsed_id is None:
                _error(errors, f"invalid-result-{index}", "check id is not a qualified stable id")
                results.append(_unknown_for_entry(index, "Reporter result has an invalid check id"))
                continue

            namespace, local_id = parsed_id
            check_id = raw_result["id"]
            expected_version = expected_versions.get(local_id)
            recognized = (
                spec is None
                or (namespace == spec.identity.namespace and expected_version is not None)
            )
            if not recognized:
                _error(errors, f"unrecognized-check-{index}", check_id)
                results.append(
                    CheckResult(
                        id=check_id,
                        check_version=DEFAULT_CHECK_VERSION,
                        verdict="UNKNOWN",
                        detail="Reporter returned a check that is not registered for this reporter",
                    )
                )
                continue

            if check_id in seen:
                _error(errors, f"duplicate-check-{index}", check_id)
                results.append(_unknown_for_entry(index, "Reporter returned a duplicate check result"))
                continue
            seen.add(check_id)

            check_version = raw_result.get("check_version")
            if not _is_semver(check_version) or (expected_version is not None and check_version != expected_version):
                _error(errors, f"unsupported-check-version-{index}", check_version)
                results.append(
                    CheckResult(
                        id=check_id,
                        check_version=expected_version or DEFAULT_CHECK_VERSION,
                        verdict="UNKNOWN",
                        detail="Reporter returned an unsupported check version",
                    )
                )
                continue

            verdict = raw_result.get("verdict")
            detail = raw_result.get("detail")
            feature = raw_result.get("feature")
            feature_status = raw_result.get("feature_status")
            invalid_detail = not isinstance(detail, str) or not detail.strip()
            invalid_feature = feature is not None and (
                not isinstance(feature, str) or not feature.strip() or len(feature) > MAX_FEATURE_LENGTH
            )
            invalid_feature_status = feature_status is not None and feature_status not in FEATURE_STATUSES
            if verdict not in VERDICTS or invalid_detail or invalid_feature or invalid_feature_status:
                _error(errors, f"invalid-check-{index}", "verdict or technical fields are malformed")
                results.append(
                    CheckResult(
                        id=check_id,
                        check_version=check_version,
                        verdict="UNKNOWN",
                        detail="Reporter returned malformed technical check data",
                    )
                )
                continue
            if len(detail) > MAX_DETAIL_LENGTH:
                _error(errors, f"oversized-detail-{index}", f"maximum length is {MAX_DETAIL_LENGTH}")
                results.append(
                    CheckResult(
                        id=check_id,
                        check_version=check_version,
                        verdict="UNKNOWN",
                        detail="Reporter returned technical detail beyond the bounded limit",
                    )
                )
                continue

            results.append(
                CheckResult(
                    id=check_id,
                    check_version=check_version,
                    verdict=verdict,
                    detail=detail,
                    feature=feature,
                    feature_status=feature_status,
                )
            )

        if spec is not None:
            for local_id, check_version in spec.checks:
                qualified_id = spec.qualified_id(local_id)
                if qualified_id not in seen:
                    _error(errors, f"missing-check-{local_id}", "registered check did not return a result")
                    results.append(
                        CheckResult(
                            id=qualified_id,
                            check_version=check_version,
                            verdict="UNKNOWN",
                            detail="Reporter did not return this registered check result",
                        )
                    )
    elif raw_results:
        _error(errors, "unsupported-reporter", "reporter could not be validated")

    if not reporter_supported:
        results = [
            _unknown_result(
                "unsupported-report",
                "Reporter envelope was malformed or unsupported; no technical results were accepted",
            )
        ]

    if not results:
        _error(errors, "empty-report", "report contained no usable technical results")
        results.append(_unknown_result("empty-report", "Reporter returned no technical results"))

    # The synthetic normalizer namespace prevents a validation result from
    # impersonating any accepted reporter check.
    if errors and not any(result.id.startswith(f"{NORMALIZER_NAMESPACE}/") for result in results):
        results.append(_unknown_result("invalid-envelope", "Reporter envelope failed strict validation"))

    envelope = ReporterEnvelope(
        contract=CONTRACT,
        reporter=reporter,
        refresh_id=refresh_id,
        generated_at=generated_at,
        results=tuple(results),
    )
    return NormalizationResult(envelope, not errors, tuple(errors))


def canonical_reporter_bytes(report: ReporterEnvelope) -> bytes:
    """Return deterministic JSON bytes for a validated reporter envelope."""

    if not isinstance(report, ReporterEnvelope):
        raise TypeError("report must be a ReporterEnvelope")
    return (
        json.dumps(
            report.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
