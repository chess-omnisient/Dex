"""Stop-hook contract for installing pending session learnings.

The hook is detection-only. It never writes a learning file, never dumps
entry text (personal-data gate), and fail-opens.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "install-learnings.py"
TODAY = date(2026, 8, 13)


def _run_hook(vault: Path, payload: dict, *, dedup: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(vault)
    env["DEX_INSTALL_LEARNINGS_TODAY"] = TODAY.isoformat()
    if dedup is not None:
        env["DEX_INSTALL_LEARNINGS_DEDUP_FILE"] = str(dedup)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=vault,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def _pending_block(title: str) -> str:
    return (
        f"## [14:32] - {title}\n\n"
        "**What happened:** A check continued after a failed command.\n"
        "**Why it matters:** The next session repeated the same miss.\n"
        "**Suggested fix:** Add a numbered verification step to the skill.\n"
        "**Status:** pending\n\n"
        "---\n"
    )


def _seed_backlog(vault: Path, *, count: int, oldest_age_days: int) -> None:
    marker = vault / "System" / ".onboarding-complete"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("{}\n", encoding="utf-8")
    directory = vault / "System" / "Session_Learnings"
    directory.mkdir(parents=True, exist_ok=True)
    oldest = TODAY - timedelta(days=oldest_age_days)
    for offset in range(count):
        day = oldest + timedelta(days=offset)
        (directory / f"{day.isoformat()}.md").write_text(
            f"# Session Learnings - {day.isoformat()}\n\n"
            + _pending_block(f"Clustered miss {offset}"),
            encoding="utf-8",
        )


def test_hook_fails_open_for_empty_and_invalid_stdin(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    for stdin in ("", "{not-json"):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            cwd=tmp_path,
            env=env,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""


def test_empty_and_new_vaults_are_silent(tmp_path: Path) -> None:
    result = _run_hook(tmp_path, {"hook_event_name": "Stop"})
    assert result.returncode == 0
    assert result.stdout == ""

    marker = tmp_path / "System" / ".onboarding-complete"
    marker.parent.mkdir(parents=True)
    marker.write_text("{}\n", encoding="utf-8")
    directory = tmp_path / "System" / "Session_Learnings"
    directory.mkdir(parents=True)
    (directory / "2026-08-12.md").write_text(
        "# Session Learnings - 2026-08-12\n\n" + _pending_block("Fresh miss"),
        encoding="utf-8",
    )
    result = _run_hook(tmp_path, {"hook_event_name": "Stop"})
    assert result.stdout == ""


def test_threshold_blocks_stop_once_per_day_without_leaking_entry_text(
    tmp_path: Path,
) -> None:
    _seed_backlog(tmp_path, count=8, oldest_age_days=70)
    dedup = tmp_path / "dedup"
    payload = {"hook_event_name": "Stop", "session_id": "install-learnings-test"}

    first = _run_hook(tmp_path, payload, dedup=dedup)
    assert first.returncode == 0, first.stderr
    output = json.loads(first.stdout)
    assert output["decision"] == "block"
    reason = output["reason"]
    assert "8 unused" in reason
    assert "oldest 70 days" in reason
    assert "install-learnings" in reason
    assert "session-learnings-routing.md" in reason
    assert "Clustered miss" not in reason
    assert "failed command" not in reason

    second = _run_hook(tmp_path, payload, dedup=dedup)
    assert second.returncode == 0
    assert second.stdout == ""


def test_stop_hook_active_does_not_loop(tmp_path: Path) -> None:
    _seed_backlog(tmp_path, count=8, oldest_age_days=70)
    result = _run_hook(
        tmp_path,
        {"hook_event_name": "Stop", "stop_hook_active": True},
        dedup=tmp_path / "dedup",
    )
    assert result.returncode == 0
    assert result.stdout == ""


def test_hook_never_writes_a_learning_file(tmp_path: Path) -> None:
    _seed_backlog(tmp_path, count=8, oldest_age_days=70)
    before = {
        path: path.read_text(encoding="utf-8")
        for path in (tmp_path / "System" / "Session_Learnings").glob("*.md")
    }
    _run_hook(tmp_path, {"hook_event_name": "Stop"}, dedup=tmp_path / "dedup")
    after = {
        path: path.read_text(encoding="utf-8")
        for path in (tmp_path / "System" / "Session_Learnings").glob("*.md")
    }
    assert after == before


def test_settings_wires_the_stop_wrapper() -> None:
    settings = json.loads(
        (REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    commands = []
    for group in settings.get("hooks", {}).get("Stop", []):
        for hook in group.get("hooks", []):
            commands.append(hook.get("command", ""))
    assert any("install-learnings.sh" in command for command in commands)
    assert any(
        "CLAUDE_PROJECT_DIR" in command
        for command in commands
        if "install-learnings" in command
    )


def test_hook_source_does_not_capture_or_delete() -> None:
    source = HOOK.read_text(encoding="utf-8")
    assert "daily-review" in source
    assert "never writes a learning" in source
    assert "unlink" not in source
    assert "os.remove" not in source
