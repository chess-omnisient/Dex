"""Lifecycle tests for immutable proactive-health snapshots."""

from datetime import datetime, timedelta, timezone

import pytest

from core.health import reporter
from core.health.doctor_reporter import refresh_from_doctor
from core.health.snapshot import (
    HEALTH_RELATIVE,
    SNAPSHOTS_RELATIVE,
    HealthRefreshAlreadyExists,
    HealthRefreshBusyError,
    HealthStore,
    IncompleteHealthReport,
    SnapshotAlreadyExists,
)

NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
FIXTURE_IDENTITY = reporter.ReporterIdentity(
    namespace="fixture.health",
    id="doctor",
    version="1.0.0",
)
FIXTURE_SPEC = reporter.ReporterSpec(
    identity=FIXTURE_IDENTITY,
    checks=(("first-check", "1.0.0"), ("second-check", "1.0.0")),
)


def _normalized(refresh_id: str, *, verdict: str = "OK"):
    return reporter.normalize_report(
        {
            "contract": reporter.CONTRACT,
            "reporter": FIXTURE_IDENTITY.to_dict(),
            "refresh_id": refresh_id,
            "generated_at": NOW.isoformat(),
            "results": [
                {
                    "id": f"fixture.health/{local_id}",
                    "check_version": "1.0.0",
                    "verdict": verdict,
                    "detail": "Fixture check completed.",
                }
                for local_id, _version in FIXTURE_SPEC.checks
            ],
        },
        spec=FIXTURE_SPEC,
        now=NOW,
    )


def test_complete_refresh_publishes_an_immutable_snapshot_and_atomic_pointer(tmp_path):
    store = HealthStore(tmp_path, retention=2)
    with store.refresh("refresh-001", started_at=NOW.isoformat()) as refresh:
        snapshot = refresh.publish(
            _normalized("refresh-001"),
            snapshot_id="snapshot-001",
            completed_at=(NOW + timedelta(minutes=1)).isoformat(),
        )

    snapshot_path = tmp_path / SNAPSHOTS_RELATIVE / "snapshot-001.json"
    pointer_path = store.latest_path
    snapshot_bytes = snapshot_path.read_bytes()
    pointer_bytes = pointer_path.read_bytes()

    assert snapshot.overall_status == "healthy"
    assert store.read_latest() == snapshot
    assert store.read_refresh("refresh-001").state == "complete"
    assert store.read_refresh("refresh-001").snapshot_id == "snapshot-001"
    assert snapshot_path.is_file()
    assert pointer_path.is_file()
    assert b"snapshot-001" in pointer_bytes

    # Session-start-style reads are read-only: no bytes change and no new path
    # is introduced by reading the complete state.
    assert store.read_latest() == snapshot
    assert snapshot_path.read_bytes() == snapshot_bytes
    assert pointer_path.read_bytes() == pointer_bytes


def test_refresh_from_doctor_keeps_doctor_as_the_authority(monkeypatch, tmp_path):
    store = HealthStore(tmp_path)
    calls = []

    def collect_reporter(*, refresh_id, heal, context):
        calls.append((refresh_id, heal, context))
        return _normalized(refresh_id)

    monkeypatch.setattr("core.utils.doctor.collect_reporter", collect_reporter)
    snapshot = refresh_from_doctor(
        store,
        refresh_id="refresh-doctor",
        heal=True,
        started_at=NOW.isoformat(),
        completed_at=(NOW + timedelta(minutes=1)).isoformat(),
    )

    assert snapshot.refresh_id == "refresh-doctor"
    assert calls == [("refresh-doctor", True, None)]
    assert store.read_latest() == snapshot


def test_failure_and_partial_refresh_preserve_the_previous_latest_snapshot(tmp_path):
    store = HealthStore(tmp_path)
    with store.refresh("refresh-good", started_at=NOW.isoformat()) as refresh:
        first = refresh.publish(
            _normalized("refresh-good"),
            snapshot_id="snapshot-good",
            completed_at=(NOW + timedelta(minutes=1)).isoformat(),
        )

    with store.refresh("refresh-offline", started_at=(NOW + timedelta(minutes=2)).isoformat()) as refresh:
        result = refresh.inconclusive("offline while checking calendar")

    assert result.state == "inconclusive"
    assert result.snapshot_id is None
    assert "offline" in result.detail
    assert store.read_latest() == first

    # Leaving a refresh scope without publishing is an interrupted/inconclusive
    # attempt, while the last complete snapshot remains authoritative.
    with store.refresh("refresh-interrupted", started_at=(NOW + timedelta(minutes=3)).isoformat()):
        pass
    assert store.read_refresh("refresh-interrupted").state == "inconclusive"
    assert store.read_latest() == first


def test_rejected_report_is_not_published_and_is_recorded_as_inconclusive(tmp_path):
    store = HealthStore(tmp_path)
    rejected = reporter.NormalizationResult(
        report=_normalized("refresh-rejected").report,
        accepted=False,
        errors=("missing-check-first-check",),
    )

    with store.refresh("refresh-rejected", started_at=NOW.isoformat()) as refresh:
        with pytest.raises(IncompleteHealthReport):
            refresh.publish(rejected)

    assert store.read_latest() is None
    assert store.read_refresh("refresh-rejected").state == "inconclusive"
    assert not list((tmp_path / SNAPSHOTS_RELATIVE).glob("*.json"))


def test_only_one_refresh_writer_is_active_and_stale_lock_metadata_is_recoverable(tmp_path):
    store = HealthStore(tmp_path)
    with store.refresh("refresh-owner", started_at=NOW.isoformat()):
        with pytest.raises(HealthRefreshBusyError):
            with store.refresh("refresh-contender", started_at=NOW.isoformat()):
                pass

    lock_path = store.coordination_lock_path
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("stale and malformed", encoding="utf-8")
    with store.refresh("refresh-recovered", started_at=NOW.isoformat()) as refresh:
        refresh.inconclusive("recovered stale coordination file")
    assert store.read_refresh("refresh-recovered").state == "inconclusive"


def test_refresh_identity_is_single_use(tmp_path):
    store = HealthStore(tmp_path)
    with store.refresh("refresh-once", started_at=NOW.isoformat()) as refresh:
        refresh.inconclusive("first attempt")

    with pytest.raises(HealthRefreshAlreadyExists):
        with store.refresh("refresh-once", started_at=NOW.isoformat()):
            pass
    assert store.read_refresh("refresh-once").detail == "first attempt"


def test_snapshot_identity_cannot_be_overwritten_and_latest_is_preserved(tmp_path):
    store = HealthStore(tmp_path)
    with store.refresh("refresh-original", started_at=NOW.isoformat()) as refresh:
        original = refresh.publish(
            _normalized("refresh-original"),
            snapshot_id="snapshot-fixed",
            completed_at=(NOW + timedelta(minutes=1)).isoformat(),
        )

    with store.refresh("refresh-collision", started_at=(NOW + timedelta(minutes=2)).isoformat()) as refresh:
        with pytest.raises(SnapshotAlreadyExists):
            refresh.publish(
                _normalized("refresh-collision"),
                snapshot_id="snapshot-fixed",
                completed_at=(NOW + timedelta(minutes=3)).isoformat(),
            )

    assert store.read_latest() == original
    assert store.read_refresh("refresh-collision").state == "failed"


def test_retention_prunes_only_after_the_new_pointer_is_published(tmp_path):
    store = HealthStore(tmp_path, retention=2)
    for index in range(4):
        refresh_id = f"refresh-{index:03d}"
        with store.refresh(refresh_id, started_at=(NOW + timedelta(minutes=index)).isoformat()) as refresh:
            refresh.publish(
                _normalized(refresh_id),
                snapshot_id=f"snapshot-{index:03d}",
                completed_at=(NOW + timedelta(minutes=index + 1)).isoformat(),
            )

    paths = {path.stem for path in (tmp_path / SNAPSHOTS_RELATIVE).glob("*.json")}
    assert paths == {"snapshot-002", "snapshot-003"}
    assert store.read_latest().snapshot_id == "snapshot-003"


def test_reading_without_a_snapshot_does_not_create_health_state(tmp_path):
    store = HealthStore(tmp_path)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert store.read_latest() is None

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert before == after
    assert HEALTH_RELATIVE not in after
