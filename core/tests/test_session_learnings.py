"""Contract for pending session-learning detection and the install threshold.

Personal-data gate: fixtures use generic titles only. No identities, no vault
content copied from a real user.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from core.utils import session_learnings as sl

TODAY = date(2026, 8, 13)


def _write_learning(vault: Path, day: date, body: str) -> Path:
    directory = vault / "System" / "Session_Learnings"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{day.isoformat()}.md"
    path.write_text(
        f"# Session Learnings - {day.isoformat()}\n\n{body}\n",
        encoding="utf-8",
    )
    return path


def _pending_block(title: str, *, status: str = "pending") -> str:
    return (
        f"## [14:32] - {title}\n\n"
        "**What happened:** A check continued after a failed command.\n"
        "**Why it matters:** The next session repeated the same miss.\n"
        "**Suggested fix:** Add a numbered verification step to the skill.\n"
        f"**Status:** {status}\n\n"
        "---\n"
    )


def _onboard(vault: Path) -> None:
    marker = vault / "System" / ".onboarding-complete"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("{}\n", encoding="utf-8")


def test_missing_directory_is_empty_and_silent(tmp_path: Path) -> None:
    stats = sl.install_prompt_stats(tmp_path, today=TODAY)
    assert stats.pending_count == 0
    assert stats.should_prompt_install is False


def test_skips_readme_and_session_end_markers_without_status(tmp_path: Path) -> None:
    _onboard(tmp_path)
    directory = tmp_path / "System" / "Session_Learnings"
    directory.mkdir(parents=True)
    (directory / "README.md").write_text("# Session Learnings\n", encoding="utf-8")
    (directory / "2026-08-01.md").write_text(
        "# Session Learnings - 2026-08-01\n\n"
        "## 09:00 - Session completed\n\n"
        "**Session ended**\n"
        "**Transcript:** `/tmp/example.jsonl`\n\n"
        "_Note: Run /daily-review to extract learnings from this session._\n\n"
        "---\n",
        encoding="utf-8",
    )

    entries = sl.parse_entries(tmp_path)
    assert entries == []
    assert sl.install_prompt_stats(tmp_path, today=TODAY).pending_count == 0


def test_parses_pending_implemented_and_dropped_without_deleting(tmp_path: Path) -> None:
    _onboard(tmp_path)
    _write_learning(
        tmp_path,
        date(2026, 6, 1),
        _pending_block("Guard failed open")
        + _pending_block(
            "Already routed",
            status="implemented (2026-07-01 — CLAUDE.md user-extensions)",
        )
        + _pending_block(
            "Wrong diagnosis",
            status="dropped (2026-07-02 — already covered by the verification rule)",
        )
        + _pending_block("Legacy close", status="won't-fix"),
    )

    entries = sl.parse_entries(tmp_path)
    statuses = {entry.title: entry.status for entry in entries}
    assert statuses["Guard failed open"] == "pending"
    assert statuses["Already routed"] == "implemented"
    assert statuses["Wrong diagnosis"] == "dropped"
    assert statuses["Legacy close"] == "won't-fix"
    pending = sl.pending_entries(entries)
    assert [entry.title for entry in pending] == ["Guard failed open"]


def test_new_vault_volume_without_age_floor_stays_silent(tmp_path: Path) -> None:
    _onboard(tmp_path)
    for offset in range(sl.MIN_PENDING_COUNT):
        day = TODAY - timedelta(days=offset)
        _write_learning(tmp_path, day, _pending_block(f"Fresh miss {offset}"))

    stats = sl.install_prompt_stats(tmp_path, today=TODAY)
    assert stats.pending_count == sl.MIN_PENDING_COUNT
    assert stats.oldest_age_days == sl.MIN_PENDING_COUNT - 1
    assert stats.should_prompt_install is False


def test_old_but_small_pile_stays_silent(tmp_path: Path) -> None:
    _onboard(tmp_path)
    oldest = TODAY - timedelta(days=70)
    _write_learning(tmp_path, oldest, _pending_block("Ten-week-old miss"))
    _write_learning(
        tmp_path,
        oldest + timedelta(days=1),
        _pending_block("Related miss"),
    )

    stats = sl.install_prompt_stats(tmp_path, today=TODAY)
    assert stats.pending_count == 2
    assert stats.oldest_age_days == 70
    assert stats.should_prompt_install is False


def test_volume_and_age_floor_together_prompt_install(tmp_path: Path) -> None:
    _onboard(tmp_path)
    oldest = TODAY - timedelta(days=70)
    for offset in range(sl.MIN_PENDING_COUNT):
        day = oldest + timedelta(days=offset)
        _write_learning(tmp_path, day, _pending_block(f"Clustered miss {offset}"))

    stats = sl.install_prompt_stats(tmp_path, today=TODAY)
    assert stats.pending_count == sl.MIN_PENDING_COUNT
    assert stats.oldest_pending_date == oldest.isoformat()
    assert stats.oldest_age_days == 70
    assert stats.should_prompt_install is True


def test_unonboarded_vault_never_prompts_even_with_a_large_pile(tmp_path: Path) -> None:
    oldest = TODAY - timedelta(days=70)
    for offset in range(sl.MIN_PENDING_COUNT):
        _write_learning(
            tmp_path,
            oldest + timedelta(days=offset),
            _pending_block(f"Pre-setup miss {offset}"),
        )

    stats = sl.install_prompt_stats(tmp_path, today=TODAY)
    assert stats.should_prompt_install is False
    assert stats.pending_count == 0


def test_render_status_records_where_or_why() -> None:
    assert (
        sl.render_status("implemented", TODAY, "CLAUDE.md user-extensions")
        == "implemented (2026-08-13 — CLAUDE.md user-extensions)"
    )
    assert (
        sl.render_status("dropped", TODAY, "already covered by the verification rule")
        == "dropped (2026-08-13 — already covered by the verification rule)"
    )


@pytest.mark.parametrize("kind", ["pending", "archived", ""])
def test_render_status_rejects_silent_count_drops(kind: str) -> None:
    with pytest.raises(ValueError):
        sl.render_status(kind, TODAY, "nowhere")


def test_routing_doc_documents_the_shipped_defaults() -> None:
    root = Path(__file__).resolve().parents[2]
    routing = root / sl.ROUTING_DOC_RELATIVE
    text = routing.read_text(encoding="utf-8")
    assert f"{sl.MIN_PENDING_COUNT} pending" in text
    assert f"{sl.MIN_OLDEST_AGE_DAYS} days" in text
    assert "**Status:** implemented (YYYY-MM-DD —" in text
    assert "**Status:** dropped (YYYY-MM-DD —" in text
    assert "Do not fabricate" in text or "do not fabricate" in text
    assert "Do not delete" in text or "do not delete" in text or "Never delete" in text
