"""Compatibility checks for existing Doctor, smoke, and SessionStart state."""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.health import reporter
from core.health.doctor_reporter import DOCTOR_REPORTER_IDENTITY
from core.health.snapshot import HealthStore
from core.utils import doctor, session_health
from core.utils.health_session import format_session_health, read_session_health

NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


def _legacy_doctor_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "generated_at": NOW.isoformat(),
        "checks": [
            {
                "id": doctor.QUICK_CHECKS[0].id,
                "feature": doctor.QUICK_CHECKS[0].feature,
                "verdict": "OK",
                "detail": "Legacy Doctor detail remains authoritative.",
                "heal": {"tier": 1, "action": "legacy repair"},
                "user_message": "Legacy user-facing Doctor guidance remains available.",
            }
        ],
    }


def test_existing_doctor_report_shape_is_not_replaced_by_the_adapter(monkeypatch):
    legacy = _legacy_doctor_report()
    calls: list[dict[str, object]] = []

    def collect(*, deep, heal, context):
        calls.append({"deep": deep, "heal": heal, "context": context})
        return legacy

    monkeypatch.setattr(doctor, "collect", collect)
    normalized = doctor.collect_reporter(refresh_id="refresh-compat", heal=True)

    assert calls == [{"deep": True, "heal": True, "context": None}]
    assert normalized.accepted is False
    assert any(error.startswith("missing-check-") for error in normalized.errors)
    assert "heal" not in normalized.report.results[0].to_dict()
    assert "user_message" not in normalized.report.results[0].to_dict()
    # The legacy object is untouched; Doctor still owns its detailed contract.
    assert legacy["checks"][0]["heal"] == {"tier": 1, "action": "legacy repair"}


def test_existing_legacy_files_are_left_untouched_and_preparing_is_quiet(tmp_path):
    system = tmp_path / "System"
    system.mkdir()
    doctor_path = system / ".doctor-last-run.json"
    smoke_path = system / ".smoke-last-run.json"
    doctor_bytes = json.dumps(_legacy_doctor_report(), sort_keys=True).encode() + b"\n"
    smoke_bytes = json.dumps(
        {
            "schema_version": 1,
            "generated_at": NOW.isoformat(),
            "journeys": [],
            "summary": {"ok": 1, "off": 0, "broken": 0, "unknown": 0},
        },
        sort_keys=True,
    ).encode() + b"\n"
    doctor_path.write_bytes(doctor_bytes)
    smoke_path.write_bytes(smoke_bytes)

    assert read_session_health(tmp_path, now=NOW).state == "preparing"
    assert format_session_health(tmp_path, now=NOW) == ""
    assert doctor_path.read_bytes() == doctor_bytes
    assert smoke_path.read_bytes() == smoke_bytes
    assert not (tmp_path / "System" / ".dex" / "health").exists()


def test_new_snapshot_state_coexists_with_legacy_reports_without_migration(tmp_path):
    system = tmp_path / "System"
    system.mkdir()
    doctor_path = system / ".doctor-last-run.json"
    smoke_path = system / ".smoke-last-run.json"
    doctor_path.write_text(json.dumps(_legacy_doctor_report()), encoding="utf-8")
    smoke_path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    before = {path: path.read_bytes() for path in (doctor_path, smoke_path)}

    identity = reporter.ReporterIdentity("fixture.health", "compat", "1.0.0")
    normalized = reporter.normalize_report(
        {
            "contract": reporter.CONTRACT,
            "reporter": identity.to_dict(),
            "refresh_id": "refresh-compat-snapshot",
            "generated_at": NOW.isoformat(),
            "results": [
                {
                    "id": "fixture.health/compat-check",
                    "check_version": "1.0.0",
                    "verdict": "OK",
                    "detail": "Compatibility check completed.",
                }
            ],
        }
    )
    assert normalized.accepted is True
    with HealthStore(tmp_path).refresh("refresh-compat-snapshot", started_at=NOW.isoformat()) as refresh:
        refresh.publish(normalized, snapshot_id="snapshot-compat", completed_at=NOW.isoformat())

    assert {path: path.read_bytes() for path in (doctor_path, smoke_path)} == before
    assert (tmp_path / "System" / ".dex" / "health" / "latest.json").is_file()
    assert DOCTOR_REPORTER_IDENTITY.namespace == "doctor.core"


def test_legacy_session_health_gate_remains_independent_of_proactive_health(tmp_path):
    # The existing daily smoke fallback still uses its own marker/report pair;
    # adding the proactive snapshot surface must not make a stale smoke report
    # look successful or suppress its retry.
    smoke = tmp_path / "System" / ".smoke-last-run.json"
    smoke.parent.mkdir(parents=True)
    smoke.write_text(
        json.dumps(
            {
                "generated_at": NOW.isoformat(),
                "summary": {"broken": 0, "unknown": 0},
            }
        ),
        encoding="utf-8",
    )
    assert session_health.needs_session_start_check(tmp_path, now=NOW) is True
