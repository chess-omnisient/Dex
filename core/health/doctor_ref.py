"""Structured, non-authorizing handoff references into Doctor.

Health owns the reference carried by an issue.  Doctor owns resolution: this
module only validates the reference, checks it against a supplied latest
snapshot and the registered Doctor check identities, and returns a safe route
when the context cannot be restored.  It never contains diagnosis, evidence
contents, preview data, or repair authority.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from core.utils import doctor

from .snapshot import HealthSnapshot

DOCTOR_REF_CONTRACT = "dex.health.doctor-ref/v1"
DOCTOR_ROUTE = "/dex-doctor"

HANDOFF_STATUSES = frozenset({"ready", "unknown", "stale", "incompatible"})
FRESHNESS_STATES = frozenset({"fresh", "stale", "unknown"})
MAX_DEPENDENCIES = 32
MAX_CHECKS = 64
MAX_EVIDENCE = 16
MAX_EVIDENCE_REF_LENGTH = 240
MAX_REASON_LENGTH = 240
MAX_AGE_SECONDS = 7 * 24 * 60 * 60

_TOKEN_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_QUALIFIED_ID_RE = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*/"
    r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)
_OPAQUE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

_REF_KEYS = frozenset(
    {
        "contract",
        "route",
        "issue_id",
        "primary_cause_id",
        "dependency_ids",
        "check_ids",
        "snapshot_id",
        "snapshot_at",
        "freshness",
        "evidence",
    }
)
_FRESHNESS_KEYS = frozenset({"state", "as_of", "max_age_seconds"})
_EVIDENCE_KEYS = frozenset({"id", "kind", "ref"})


def _timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _bounded(value: object, limit: int) -> str:
    text = value if isinstance(value, str) else str(value)
    text = " ".join(text.split())
    if not text:
        return "unknown"
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _valid_token(value: object) -> bool:
    return isinstance(value, str) and _TOKEN_RE.fullmatch(value) is not None


def _valid_qualified_id(value: object) -> bool:
    return isinstance(value, str) and _QUALIFIED_ID_RE.fullmatch(value) is not None


def _valid_opaque_id(value: object) -> bool:
    return isinstance(value, str) and _OPAQUE_ID_RE.fullmatch(value) is not None


def _doctor_check_ids() -> frozenset[str]:
    return frozenset(
        f"doctor.core/{definition.id}"
        for definition in (*doctor.QUICK_CHECKS, *doctor.DEEP_CHECKS)
    )


@dataclass(frozen=True)
class FreshnessContext:
    """Bounded freshness claims attached to a handoff reference."""

    state: str
    as_of: str
    max_age_seconds: int

    def __post_init__(self) -> None:
        if self.state not in FRESHNESS_STATES:
            raise ValueError(f"invalid freshness state: {self.state!r}")
        if not _timestamp(self.as_of):
            raise ValueError("freshness as_of must be timezone-aware ISO-8601")
        if type(self.max_age_seconds) is not int or not 0 < self.max_age_seconds <= MAX_AGE_SECONDS:
            raise ValueError("freshness max_age_seconds is outside the bounded v1 range")

    @classmethod
    def from_mapping(cls, value: object) -> "FreshnessContext":
        if not isinstance(value, Mapping) or set(value) != _FRESHNESS_KEYS:
            raise ValueError("freshness must contain exactly the v1 fields")
        return cls(
            state=value["state"],  # type: ignore[arg-type]
            as_of=value["as_of"],  # type: ignore[arg-type]
            max_age_seconds=value["max_age_seconds"],  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "as_of": self.as_of,
            "max_age_seconds": self.max_age_seconds,
        }


@dataclass(frozen=True)
class EvidenceReference:
    """A bounded pointer to evidence, never the evidence contents."""

    id: str
    kind: str
    ref: str

    def __post_init__(self) -> None:
        if not _valid_qualified_id(self.id):
            raise ValueError("evidence id must be a stable namespaced identity")
        if not _valid_token(self.kind):
            raise ValueError("evidence kind must be a stable token")
        if not isinstance(self.ref, str) or not self.ref.strip():
            raise ValueError("evidence ref must be a non-empty bounded reference")
        if len(self.ref) > MAX_EVIDENCE_REF_LENGTH:
            raise ValueError("evidence ref exceeds the bounded limit")

    @classmethod
    def from_mapping(cls, value: object) -> "EvidenceReference":
        if not isinstance(value, Mapping) or set(value) != _EVIDENCE_KEYS:
            raise ValueError("evidence reference must contain exactly the v1 fields")
        return cls(
            id=value["id"],  # type: ignore[arg-type]
            kind=value["kind"],  # type: ignore[arg-type]
            ref=value["ref"],  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "kind": self.kind, "ref": self.ref}


@dataclass(frozen=True)
class DoctorReference:
    """Canonical v1 reference carried by a user-facing Health Issue."""

    issue_id: str
    primary_cause_id: str
    dependency_ids: tuple[str, ...]
    check_ids: tuple[str, ...]
    snapshot_id: str
    snapshot_at: str
    freshness: FreshnessContext
    evidence: tuple[EvidenceReference, ...] = ()
    route: str = DOCTOR_ROUTE

    def __post_init__(self) -> None:
        if self.route != DOCTOR_ROUTE:
            raise ValueError("Doctor handoff route must be /dex-doctor")
        if not _valid_qualified_id(self.issue_id):
            raise ValueError("issue_id must be a stable namespaced identity")
        if not _valid_qualified_id(self.primary_cause_id):
            raise ValueError("primary_cause_id must be a stable namespaced identity")
        if not isinstance(self.dependency_ids, tuple) or len(self.dependency_ids) > MAX_DEPENDENCIES:
            raise ValueError("dependency_ids exceed the bounded v1 limit")
        if not isinstance(self.check_ids, tuple) or not self.check_ids or len(self.check_ids) > MAX_CHECKS:
            raise ValueError("check_ids must contain a bounded non-empty selection")
        if not _valid_opaque_id(self.snapshot_id):
            raise ValueError("snapshot_id must be a bounded opaque identifier")
        if not _timestamp(self.snapshot_at):
            raise ValueError("snapshot_at must be timezone-aware ISO-8601")
        if self.freshness.as_of != self.snapshot_at:
            raise ValueError("freshness as_of must match snapshot_at")
        if any(not _valid_qualified_id(item) for item in self.dependency_ids):
            raise ValueError("dependency ids must be stable namespaced identities")
        if len(set(self.dependency_ids)) != len(self.dependency_ids):
            raise ValueError("dependency ids cannot repeat")
        if self.primary_cause_id in self.dependency_ids:
            raise ValueError("primary cause cannot repeat as a dependency")
        if any(not _valid_qualified_id(item) for item in self.check_ids):
            raise ValueError("check ids must be stable namespaced identities")
        if len(set(self.check_ids)) != len(self.check_ids):
            raise ValueError("check ids cannot repeat")
        if not isinstance(self.evidence, tuple) or len(self.evidence) > MAX_EVIDENCE:
            raise ValueError("evidence references exceed the bounded v1 limit")
        if any(type(item) is not EvidenceReference for item in self.evidence):
            raise TypeError("evidence must contain EvidenceReference records")
        evidence_ids = [item.id for item in self.evidence]
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("evidence ids cannot repeat")

    @classmethod
    def from_mapping(cls, value: object) -> "DoctorReference":
        if not isinstance(value, Mapping) or set(value) != _REF_KEYS:
            raise ValueError("Doctor reference must contain exactly the v1 fields")
        if value.get("contract") != DOCTOR_REF_CONTRACT:
            raise ValueError("unsupported Doctor reference contract")
        dependencies = value["dependency_ids"]
        checks = value["check_ids"]
        evidence = value["evidence"]
        if not isinstance(dependencies, list) or not isinstance(checks, list) or not isinstance(evidence, list):
            raise ValueError("Doctor reference lists must be JSON arrays")
        return cls(
            issue_id=value["issue_id"],  # type: ignore[arg-type]
            primary_cause_id=value["primary_cause_id"],  # type: ignore[arg-type]
            dependency_ids=tuple(dependencies),
            check_ids=tuple(checks),
            snapshot_id=value["snapshot_id"],  # type: ignore[arg-type]
            snapshot_at=value["snapshot_at"],  # type: ignore[arg-type]
            freshness=FreshnessContext.from_mapping(value["freshness"]),
            evidence=tuple(EvidenceReference.from_mapping(item) for item in evidence),
            route=value["route"],  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": DOCTOR_REF_CONTRACT,
            "route": self.route,
            "issue_id": self.issue_id,
            "primary_cause_id": self.primary_cause_id,
            "dependency_ids": list(self.dependency_ids),
            "check_ids": list(self.check_ids),
            "snapshot_id": self.snapshot_id,
            "snapshot_at": self.snapshot_at,
            "freshness": self.freshness.to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class DoctorHandoff:
    """Resolution result that always provides a safe general Doctor route."""

    status: str
    reason: str
    issue_id: str | None = None
    primary_cause_id: str | None = None
    dependency_ids: tuple[str, ...] = ()
    check_ids: tuple[str, ...] = ()
    snapshot_id: str | None = None
    snapshot_at: str | None = None
    evidence: tuple[EvidenceReference, ...] = ()
    route: str = DOCTOR_ROUTE

    def __post_init__(self) -> None:
        if self.status not in HANDOFF_STATUSES:
            raise ValueError(f"invalid Doctor handoff status: {self.status!r}")
        if self.route != DOCTOR_ROUTE:
            raise ValueError("Doctor fallback route must be /dex-doctor")
        if not isinstance(self.reason, str) or not self.reason.strip() or len(self.reason) > MAX_REASON_LENGTH:
            raise ValueError("Doctor handoff reason must be bounded and non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "status": self.status,
            "reason": self.reason,
            "issue_id": self.issue_id,
            "primary_cause_id": self.primary_cause_id,
            "dependency_ids": list(self.dependency_ids),
            "check_ids": list(self.check_ids),
            "snapshot_id": self.snapshot_id,
            "snapshot_at": self.snapshot_at,
            "evidence": [item.to_dict() for item in self.evidence],
        }


def canonical_doctor_reference_bytes(reference: DoctorReference) -> bytes:
    """Return deterministic JSON bytes for a validated handoff reference."""

    if type(reference) is not DoctorReference:
        raise TypeError("reference must be a DoctorReference")
    return _canonical(reference.to_dict())


def _preserved_issue_fields(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        return {}
    preserved: dict[str, object] = {}
    for field in ("issue_id", "primary_cause_id", "snapshot_id", "snapshot_at"):
        candidate = value.get(field)
        valid = _valid_opaque_id(candidate) if field in {"snapshot_id"} else (
            _timestamp(candidate) if field == "snapshot_at" else _valid_qualified_id(candidate)
        )
        if valid:
            preserved[field] = candidate
    return preserved


def _invalid_handoff(value: object, reason: object) -> DoctorHandoff:
    preserved = _preserved_issue_fields(value)
    return DoctorHandoff(
        status="unknown",
        reason=_bounded(reason, MAX_REASON_LENGTH),
        issue_id=preserved.get("issue_id"),  # type: ignore[arg-type]
        primary_cause_id=preserved.get("primary_cause_id"),  # type: ignore[arg-type]
        snapshot_id=preserved.get("snapshot_id"),  # type: ignore[arg-type]
        snapshot_at=preserved.get("snapshot_at"),  # type: ignore[arg-type]
    )


def _now(now: datetime | None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def resolve_doctor_reference(
    value: object,
    *,
    latest_snapshot: HealthSnapshot | None,
    now: datetime | None = None,
) -> DoctorHandoff:
    """Validate and resolve a reference without diagnosing or authorizing repair."""

    if not isinstance(value, Mapping) or value.get("contract") != DOCTOR_REF_CONTRACT:
        return _invalid_handoff(value, "Doctor handoff context is missing or unsupported")
    try:
        reference = DoctorReference.from_mapping(value)
    except (TypeError, ValueError, KeyError) as error:
        return _invalid_handoff(value, f"Doctor handoff context is malformed: {error}")

    common = {
        "issue_id": reference.issue_id,
        "primary_cause_id": reference.primary_cause_id,
        "dependency_ids": reference.dependency_ids,
        "check_ids": reference.check_ids,
        "snapshot_id": reference.snapshot_id,
        "snapshot_at": reference.snapshot_at,
        "evidence": reference.evidence,
    }
    if latest_snapshot is None:
        return DoctorHandoff(
            status="unknown",
            reason="The referenced health snapshot is unavailable; opening general Doctor.",
            **common,
        )
    if type(latest_snapshot) is not HealthSnapshot:
        return DoctorHandoff(
            status="unknown",
            reason="The available health snapshot is not compatible; opening general Doctor.",
            **common,
        )
    if latest_snapshot.snapshot_id != reference.snapshot_id:
        return DoctorHandoff(
            status="stale",
            reason="The referenced health snapshot is no longer the latest; opening general Doctor.",
            **common,
        )
    if latest_snapshot.completed_at != reference.snapshot_at:
        return DoctorHandoff(
            status="incompatible",
            reason="The referenced snapshot timestamp cannot be verified; opening general Doctor.",
            **common,
        )
    if reference.freshness.state != "fresh":
        return DoctorHandoff(
            status=reference.freshness.state,
            reason="The referenced health context is not fresh; opening general Doctor.",
            **common,
        )

    current = _now(now)
    completed = datetime.fromisoformat(latest_snapshot.completed_at.replace("Z", "+00:00"))
    age_seconds = (current - completed).total_seconds()
    if age_seconds < 0 or age_seconds > reference.freshness.max_age_seconds:
        return DoctorHandoff(
            status="stale",
            reason="The referenced health context is stale; opening general Doctor.",
            **common,
        )

    registered = _doctor_check_ids()
    if any(check_id not in registered for check_id in reference.check_ids):
        return DoctorHandoff(
            status="incompatible",
            reason="The reference contains an unsupported Doctor check; opening general Doctor.",
            **common,
        )
    available = {result.id for result in latest_snapshot.report.results}
    if any(check_id not in available for check_id in reference.check_ids):
        return DoctorHandoff(
            status="unknown",
            reason="The referenced Doctor check is unavailable in this snapshot; opening general Doctor.",
            **common,
        )

    return DoctorHandoff(
        status="ready",
        reason="Doctor handoff context restored.",
        **common,
    )


__all__ = [
    "DOCTOR_REF_CONTRACT",
    "DOCTOR_ROUTE",
    "DoctorHandoff",
    "DoctorReference",
    "EvidenceReference",
    "FreshnessContext",
    "canonical_doctor_reference_bytes",
    "resolve_doctor_reference",
]
