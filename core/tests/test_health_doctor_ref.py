"""Tests for the structured, non-authorizing Doctor handoff contract."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from core.health import reporter
from core.health.doctor_ref import (
    DOCTOR_REF_CONTRACT,
    DOCTOR_ROUTE,
    DoctorReference,
    EvidenceReference,
    FreshnessContext,
    canonical_doctor_reference_bytes,
    resolve_doctor_reference,
)
from core.health.doctor_reporter import DOCTOR_REPORTER_IDENTITY, DOCTOR_REPORTER_SPEC
from core.health.snapshot import HealthSnapshot
from core.utils import doctor

NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
SNAPSHOT_AT = (NOW + timedelta(minutes=1)).isoformat()
CHECK_IDS = ("doctor.core/jobs.fresh", "doctor.core/mcp.registered")


def _snapshot(*, snapshot_id="snapshot-doctor", include_checks=CHECK_IDS):
    all_definitions = (*doctor.QUICK_CHECKS, *doctor.DEEP_CHECKS)
    results = [
        {
            "id": f"{DOCTOR_REPORTER_IDENTITY.namespace}/{definition.id}",
            "check_version": "1.0.0",
            "verdict": "OK",
            "detail": "Doctor check completed.",
        }
        for definition in all_definitions
        if f"{DOCTOR_REPORTER_IDENTITY.namespace}/{definition.id}" in include_checks
        or include_checks is None
    ]
    # A complete Doctor snapshot is used for the normal path. The resolver's
    # missing-check behavior is covered with a deliberately generic envelope.
    if include_checks == CHECK_IDS:
        results = [
            {
                "id": f"{DOCTOR_REPORTER_IDENTITY.namespace}/{definition.id}",
                "check_version": "1.0.0",
                "verdict": "OK",
                "detail": "Doctor check completed.",
            }
            for definition in all_definitions
        ]
        normalized = reporter.normalize_report(
            {
                "contract": reporter.CONTRACT,
                "reporter": DOCTOR_REPORTER_IDENTITY.to_dict(),
                "refresh_id": "refresh-doctor",
                "generated_at": NOW.isoformat(),
                "results": results,
            },
            spec=DOCTOR_REPORTER_SPEC,
        )
    else:
        normalized = reporter.normalize_report(
            {
                "contract": reporter.CONTRACT,
                "reporter": DOCTOR_REPORTER_IDENTITY.to_dict(),
                "refresh_id": "refresh-doctor",
                "generated_at": NOW.isoformat(),
                "results": results,
            }
        )
    assert normalized.accepted is True
    return HealthSnapshot.from_normalized(
        normalized,
        snapshot_id=snapshot_id,
        completed_at=SNAPSHOT_AT,
    )


def _reference(**overrides):
    values = {
        "issue_id": "health.issue/jobs-fresh",
        "primary_cause_id": "health.cause/jobs-fresh",
        "dependency_ids": ("health.dependency/mcp",),
        "check_ids": CHECK_IDS,
        "snapshot_id": "snapshot-doctor",
        "snapshot_at": SNAPSHOT_AT,
        "freshness": FreshnessContext(
            state="fresh",
            as_of=SNAPSHOT_AT,
            max_age_seconds=3600,
        ),
        "evidence": (
            EvidenceReference(
                id="health.evidence/jobs-fresh",
                kind="check",
                ref="doctor://jobs.fresh",
            ),
        ),
    }
    return DoctorReference(**(values | overrides))


def test_reference_is_canonical_and_resolves_against_latest_doctor_snapshot():
    reference = _reference()
    raw = reference.to_dict()
    restored = DoctorReference.from_mapping(raw)
    handoff = resolve_doctor_reference(
        raw,
        latest_snapshot=_snapshot(),
        now=NOW + timedelta(minutes=2),
    )

    assert raw["contract"] == DOCTOR_REF_CONTRACT
    assert raw["route"] == DOCTOR_ROUTE
    assert restored == reference
    assert canonical_doctor_reference_bytes(reference).endswith(b"\n")
    assert handoff.status == "ready"
    assert handoff.route == DOCTOR_ROUTE
    assert handoff.issue_id == "health.issue/jobs-fresh"
    assert handoff.check_ids == CHECK_IDS
    assert handoff.evidence == reference.evidence


def test_stale_or_missing_context_preserves_identity_and_falls_back_safely():
    reference = _reference()
    stale_latest = _snapshot(snapshot_id="snapshot-new")

    stale = resolve_doctor_reference(
        reference.to_dict(),
        latest_snapshot=stale_latest,
        now=NOW + timedelta(minutes=2),
    )
    missing = resolve_doctor_reference(
        reference.to_dict(),
        latest_snapshot=None,
        now=NOW + timedelta(minutes=2),
    )
    old = resolve_doctor_reference(
        replace(
            reference,
            freshness=FreshnessContext(
                state="fresh",
                as_of=SNAPSHOT_AT,
                max_age_seconds=60,
            ),
        ).to_dict(),
        latest_snapshot=_snapshot(),
        now=NOW + timedelta(hours=2),
    )

    for result in (stale, missing, old):
        assert result.status in {"stale", "unknown"}
        assert result.route == DOCTOR_ROUTE
        assert result.issue_id == reference.issue_id
        assert result.primary_cause_id == reference.primary_cause_id
        assert result.snapshot_id == reference.snapshot_id


def test_malformed_and_incompatible_references_never_authorize_a_repair():
    reference = _reference()
    malformed = reference.to_dict()
    malformed["contract"] = "dex.health.doctor-ref/v2"
    malformed_result = resolve_doctor_reference(
        malformed,
        latest_snapshot=_snapshot(),
        now=NOW + timedelta(minutes=2),
    )

    unsupported_check = replace(
        reference,
        check_ids=("doctor.core/not-registered",),
    )
    incompatible = resolve_doctor_reference(
        unsupported_check.to_dict(),
        latest_snapshot=_snapshot(),
        now=NOW + timedelta(minutes=2),
    )

    assert malformed_result.status == "unknown"
    assert malformed_result.route == DOCTOR_ROUTE
    assert malformed_result.issue_id == reference.issue_id
    assert incompatible.status == "incompatible"
    assert incompatible.route == DOCTOR_ROUTE
    assert incompatible.check_ids == ("doctor.core/not-registered",)


def test_reference_with_missing_selected_check_is_unknown_not_silently_retargeted():
    reference = _reference(check_ids=("doctor.core/jobs.fresh",))
    snapshot_without_check = _snapshot(
        snapshot_id="snapshot-doctor",
        include_checks=("doctor.core/mcp.registered",),
    )
    result = resolve_doctor_reference(
        reference.to_dict(),
        latest_snapshot=snapshot_without_check,
        now=NOW + timedelta(minutes=2),
    )

    assert result.status == "unknown"
    assert result.route == DOCTOR_ROUTE
    assert result.check_ids == ("doctor.core/jobs.fresh",)
