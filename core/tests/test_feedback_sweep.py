"""Tests for the once-daily feedback status sweep (core/utils/feedback_sweep.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.utils import feedback_sweep


def _write_ticket(vault: Path, ticket: str, notified_at: int = 100) -> Path:
    directory = vault / "System" / ".dex" / "feedback"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ticket}.json"
    path.write_text(
        json.dumps(
            {
                "ticket": ticket,
                "sent_at": 100,
                "status": "received",
                "status_changed_at": 100,
                "last_notified_status_changed_at": notified_at,
                "report": {"summary": "Sync stopped on empty meetings."},
            }
        ),
        encoding="utf-8",
    )
    return path


def _server_report(**overrides):
    report = {
        "ticket": "DEX-142",
        "feature": "/process-meetings",
        "summary": "Sync stopped on empty meetings.",
        "status": "fixed",
        "statusChangedAt": 200,
        "fixedInVersion": "1.82.0",
        "comment": "Great catch — thank you.",
        "question": None,
        "createdAt": 100,
    }
    report.update(overrides)
    return report


@pytest.fixture()
def vault(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_sweep, "_auth_token", lambda: "token")
    return tmp_path


def test_no_tickets_means_no_network_and_no_output(tmp_path, monkeypatch):
    def explode(_token):
        raise AssertionError("network must not be touched without tickets")

    monkeypatch.setattr(feedback_sweep, "_fetch_status", explode)
    assert feedback_sweep.sweep(tmp_path) is None


def test_no_auth_means_no_network(tmp_path, monkeypatch):
    _write_ticket(tmp_path, "DEX-142")
    monkeypatch.setattr(feedback_sweep, "_auth_token", lambda: None)

    def explode(_token):
        raise AssertionError("network must not be touched without a linked account")

    monkeypatch.setattr(feedback_sweep, "_fetch_status", explode)
    assert feedback_sweep.sweep(tmp_path) is None


def test_fixed_status_produces_notice_once_only(vault, monkeypatch):
    _write_ticket(vault, "DEX-142")
    monkeypatch.setattr(feedback_sweep, "_fetch_status", lambda token: [_server_report()])
    monkeypatch.setenv("DEX_FEEDBACK_SWEEP_FORCE", "1")

    notice = feedback_sweep.sweep(vault)
    assert notice is not None
    assert "DEX-142" in notice
    assert "fixed in v1.82.0" in notice
    assert "Great catch" in notice
    assert "/dex-update" in notice

    # Same server state again: already notified, stays silent.
    assert feedback_sweep.sweep(vault) is None


def test_quiet_transition_updates_record_without_notice(vault, monkeypatch):
    path = _write_ticket(vault, "DEX-142")
    monkeypatch.setattr(
        feedback_sweep,
        "_fetch_status",
        lambda token: [_server_report(status="investigating", fixedInVersion=None, comment=None)],
    )
    monkeypatch.setenv("DEX_FEEDBACK_SWEEP_FORCE", "1")

    assert feedback_sweep.sweep(vault) is None
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["status"] == "investigating"
    assert record["last_notified_status_changed_at"] == 200


def test_question_produces_answerable_notice(vault, monkeypatch):
    _write_ticket(vault, "DEX-158")
    monkeypatch.setattr(
        feedback_sweep,
        "_fetch_status",
        lambda token: [
            _server_report(
                ticket="DEX-158",
                status="needs_info",
                question="Does this happen for people added before July?",
                fixedInVersion=None,
            )
        ],
    )
    monkeypatch.setenv("DEX_FEEDBACK_SWEEP_FORCE", "1")

    notice = feedback_sweep.sweep(vault)
    assert notice is not None
    assert "DEX-158" in notice
    assert "before July" in notice
    assert "/feedback" in notice


def test_daily_claim_blocks_second_attempt(vault, monkeypatch):
    _write_ticket(vault, "DEX-142")
    calls = []

    def fetch(token):
        calls.append(token)
        return [_server_report()]

    monkeypatch.setattr(feedback_sweep, "_fetch_status", fetch)
    feedback_sweep.sweep(vault)
    feedback_sweep.sweep(vault)
    assert len(calls) == 1


def test_network_failure_is_silent(vault, monkeypatch):
    _write_ticket(vault, "DEX-142")
    monkeypatch.setattr(feedback_sweep, "_fetch_status", lambda token: None)
    monkeypatch.setenv("DEX_FEEDBACK_SWEEP_FORCE", "1")
    assert feedback_sweep.sweep(vault) is None


def test_main_emits_session_start_hook_json(vault, monkeypatch, capsys):
    _write_ticket(vault, "DEX-142")
    monkeypatch.setattr(feedback_sweep, "_fetch_status", lambda token: [_server_report()])
    monkeypatch.setenv("DEX_FEEDBACK_SWEEP_FORCE", "1")

    assert feedback_sweep.main(["--vault", str(vault), "--session-start"]) == 0
    output = capsys.readouterr().out.strip()
    decoded = json.loads(output)
    context = decoded["hookSpecificOutput"]["additionalContext"]
    assert decoded["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "DEX-142" in context


def test_main_never_raises_even_on_broken_vault(tmp_path, capsys):
    # A file where the feedback directory should be must not crash the hook.
    weird = tmp_path / "System" / ".dex"
    weird.parent.mkdir(parents=True)
    weird.write_text("not a directory", encoding="utf-8")
    assert feedback_sweep.main(["--vault", str(tmp_path), "--session-start"]) == 0
    assert capsys.readouterr().out == ""
