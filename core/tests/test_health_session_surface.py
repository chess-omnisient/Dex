"""Tests for the fixed, read-only proactive-health SessionStart surface."""

from datetime import datetime, timedelta, timezone

from core.health import reporter
from core.health.snapshot import HealthStore
from core.utils.health_session import format_session_health, read_session_health

NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)
IDENTITY = reporter.ReporterIdentity(
    namespace="fixture.health",
    id="session",
    version="1.0.0",
)
SPEC = reporter.ReporterSpec(identity=IDENTITY, checks=(("session-check", "1.0.0"),))


def _publish(store: HealthStore, number: int, verdict: str, completed_at: datetime):
    refresh_id = f"refresh-session-{number}"
    with store.refresh(refresh_id, started_at=(completed_at - timedelta(minutes=1)).isoformat()) as refresh:
        return refresh.publish(
            reporter.normalize_report(
                {
                    "contract": reporter.CONTRACT,
                    "reporter": IDENTITY.to_dict(),
                    "refresh_id": refresh_id,
                    "generated_at": (completed_at - timedelta(minutes=1)).isoformat(),
                    "results": [
                        {
                            "id": "fixture.health/session-check",
                            "check_version": "1.0.0",
                            "verdict": verdict,
                            "detail": "Session fixture check completed.",
                        }
                    ],
                },
                spec=SPEC,
            ),
            snapshot_id=f"snapshot-session-{number}",
            completed_at=completed_at.isoformat(),
        )


def test_no_complete_snapshot_is_quiet_preparing_state(tmp_path):
    assert read_session_health(tmp_path, now=NOW).state == "preparing"
    assert format_session_health(tmp_path, now=NOW) == ""


def test_latest_complete_status_is_visible_without_warnings(tmp_path):
    store = HealthStore(tmp_path)
    _publish(store, 1, "OK", NOW - timedelta(days=2))

    surface = read_session_health(tmp_path, now=NOW)
    output = format_session_health(tmp_path, now=NOW)

    assert surface.state == "healthy"
    assert surface.stale is True
    assert "🩺 Dex health: healthy" in output
    assert "latest complete snapshot" in output
    assert "stale" not in output
    assert "warning" not in output.lower()


def test_only_newly_critical_health_interrupts(tmp_path):
    store = HealthStore(tmp_path)
    _publish(store, 1, "OK", NOW - timedelta(minutes=4))
    _publish(store, 2, "BROKEN", NOW - timedelta(minutes=2))

    first_critical = read_session_health(tmp_path, now=NOW)
    first_output = format_session_health(tmp_path, now=NOW)
    assert first_critical.newly_critical is True
    assert "--- 🚨 Dex health: critical ---" in first_output
    assert "/dex-doctor" in first_output

    _publish(store, 3, "BROKEN", NOW - timedelta(minutes=1))
    ongoing = read_session_health(tmp_path, now=NOW)
    ongoing_output = format_session_health(tmp_path, now=NOW)
    assert ongoing.newly_critical is False
    assert "critical (ongoing)" in ongoing_output
    assert "--- 🚨" not in ongoing_output


def test_recovery_is_unobtrusive_and_failed_refresh_keeps_latest_status(tmp_path):
    store = HealthStore(tmp_path)
    _publish(store, 1, "BROKEN", NOW - timedelta(minutes=3))
    _publish(store, 2, "OK", NOW - timedelta(minutes=2))

    recovered = read_session_health(tmp_path, now=NOW)
    recovered_output = format_session_health(tmp_path, now=NOW)
    assert recovered.recovered is True
    assert recovered_output.startswith("🩺 Dex health: healthy (recovered)")
    assert "🚨" not in recovered_output

    with store.refresh("refresh-session-failed", started_at=NOW.isoformat()) as refresh:
        refresh.inconclusive("offline")
    assert read_session_health(tmp_path, now=NOW).snapshot.snapshot_id == "snapshot-session-2"


def test_unknown_status_is_visible_but_not_an_interrupt(tmp_path):
    store = HealthStore(tmp_path)
    _publish(store, 1, "UNKNOWN", NOW - timedelta(minutes=1))

    surface = read_session_health(tmp_path, now=NOW)
    output = format_session_health(tmp_path, now=NOW)
    assert surface.state == "unknown"
    assert "🩺 Dex health: unknown" in output
    assert "🚨" not in output


def test_session_surface_reads_do_not_create_or_modify_health_state(tmp_path):
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert format_session_health(tmp_path, now=NOW) == ""

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert before == after
