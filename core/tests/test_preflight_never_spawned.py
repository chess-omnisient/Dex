"""Configured work-mcp with no live process must not stay silent.

When sibling core Python MCP processes are running and Task Manager is listed
but has no process, preflight and Doctor reuse the existing
"Task Manager cannot start" voice. An idle machine with no MCP processes stays
quiet so this notice cannot false-alarm a checkup outside a live session.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from core.utils import doctor, preflight

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_core_servers(vault: Path, names: tuple[str, ...]) -> dict[str, Path]:
    mcp_dir = vault / "core" / "mcp"
    mcp_dir.mkdir(parents=True)
    scripts = {}
    servers = {}
    for name in names:
        module = preflight.SERVER_MODULES[name]
        script = mcp_dir / module
        script.write_text("# stub module\n", encoding="utf-8")
        scripts[name] = script
        servers[name] = {
            "command": str(vault / ".venv" / "bin" / "python"),
            "args": [str(script)],
        }
    (vault / ".mcp.json").write_text(json.dumps({"mcpServers": servers}), encoding="utf-8")
    return scripts


def _ok_servers(names: tuple[str, ...]) -> dict[str, dict[str, str]]:
    return {name: {"status": "ok"} for name in names}


def test_never_spawned_when_siblings_live_and_work_mcp_has_no_process(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    scripts = _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))
    cmdlines = [f"python {scripts['calendar-mcp']}"]

    notice = preflight.never_spawned_work_mcp_result(
        _ok_servers(("work-mcp", "calendar-mcp")),
        cmdlines=cmdlines,
    )

    assert notice == {
        "status": "error",
        "error": "Task Manager cannot start",
        "humanError": "Task Manager cannot start",
    }


def test_stays_quiet_when_the_process_table_cannot_be_read(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))
    monkeypatch.setattr(preflight, "list_process_cmdlines", lambda: None)

    assert (
        preflight.never_spawned_work_mcp_result(
            _ok_servers(("work-mcp", "calendar-mcp")),
        )
        is None
    )


def test_stays_quiet_when_no_sibling_core_mcp_is_live(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))

    assert (
        preflight.never_spawned_work_mcp_result(
            _ok_servers(("work-mcp", "calendar-mcp")),
            cmdlines=["unrelated helper"],
        )
        is None
    )


def test_stays_quiet_when_work_mcp_process_is_live(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    scripts = _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))
    cmdlines = [
        f"python {scripts['calendar-mcp']}",
        f"python {scripts['work-mcp']}",
    ]

    assert (
        preflight.never_spawned_work_mcp_result(
            _ok_servers(("work-mcp", "calendar-mcp")),
            cmdlines=cmdlines,
        )
        is None
    )


def test_does_not_replace_a_missing_script_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    scripts = _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))

    assert (
        preflight.never_spawned_work_mcp_result(
            {
                "work-mcp": {
                    "status": "error",
                    "humanError": "Task Manager is missing — dex-core may need reinstalling",
                },
                "calendar-mcp": {"status": "ok"},
            },
            cmdlines=[f"python {scripts['calendar-mcp']}"],
        )
        is None
    )


def test_overlay_is_fresh_and_not_written_to_the_health_cache(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    scripts = _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))
    monkeypatch.setattr(preflight, "check_server", lambda _name: {"status": "ok"})
    monkeypatch.setattr(
        preflight,
        "list_process_cmdlines",
        lambda: [f"python {scripts['calendar-mcp']}"],
    )

    health = preflight.run_preflight()
    cached = json.loads((tmp_path / ".logs" / "mcp-health.json").read_text())

    assert health["servers"]["work-mcp"]["humanError"] == "Task Manager cannot start"
    assert cached["servers"]["work-mcp"]["status"] == "ok"
    assert "humanError" not in cached["servers"]["work-mcp"]


def test_session_preflight_output_uses_existing_task_manager_voice(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("VAULT_PATH", str(tmp_path))
    scripts = _write_core_servers(tmp_path, ("work-mcp", "calendar-mcp"))
    monkeypatch.setattr(preflight, "check_server", lambda _name: {"status": "ok"})
    monkeypatch.setattr(
        preflight,
        "list_process_cmdlines",
        lambda: [f"python {scripts['calendar-mcp']}"],
    )

    output = preflight.format_output(preflight.run_preflight())

    assert "Task Manager cannot start" in output
    assert "Say: 'health check' to investigate" in output


def test_doctor_preflight_queue_reports_never_spawned_work_mcp(
    tmp_path: Path, monkeypatch
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "System").mkdir()
    scripts = _write_core_servers(vault, ("work-mcp", "calendar-mcp"))
    monkeypatch.setattr(preflight, "check_server", lambda _name: {"status": "ok"})
    monkeypatch.setattr(
        preflight,
        "list_process_cmdlines",
        lambda: [f"python {scripts['calendar-mcp']}"],
    )
    context = doctor.DoctorContext(
        vault_root=vault,
        repo_root=REPO_ROOT,
        home=tmp_path / "home",
        now=datetime.now(timezone.utc),
    )
    context.home.mkdir()

    result = doctor._probe_preflight_queue(context)

    assert result.verdict == "BROKEN"
    assert "Task Manager cannot start" in result.detail
