"""Repository discovery gates for the enriched Dex Lens preview."""

from __future__ import annotations

from pathlib import Path

from core.lens_catalog_discovery import (
    discover_mcp_servers,
    discover_scheduled_automations,
    discover_system_engines,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_discovers_exact_core_mcp_boundary_and_131_tools() -> None:
    servers = discover_mcp_servers(REPO_ROOT)

    assert len(servers) == 10
    assert sum(server.tool_count for server in servers) == 131
    assert {server.server_name: server.tool_count for server in servers} == {
        "dex-analytics": 4,
        "dex-calendar-mcp": 15,
        "dex-career-mcp": 8,
        "dex-customization-migration-mcp": 7,
        "dex-granola-mcp": 6,
        "dex-improvements-mcp": 9,
        "dex-onboarding-mcp": 15,
        "dex-resume-mcp": 12,
        "dex-session-memory": 8,
        "dex-work-mcp": 47,
    }
    assert all(server.capability_id == server.server_name for server in servers)
    assert all(server.source_path.startswith("core/mcp/") for server in servers)
    assert all(server.source_path.endswith("_server.py") for server in servers)
    assert all(1 <= len(server.example_tools) <= 5 for server in servers)
    assert all(tuple(sorted(server.example_tools)) == server.example_tools for server in servers)


def test_discovers_four_plists_and_daily_backup_scheduler() -> None:
    automations = discover_scheduled_automations(REPO_ROOT)

    assert [(item.capability_id, item.cadence) for item in automations] == [
        ("com.dex.changelog-checker", "every 6 hours; also at load"),
        ("com.dex.learning-review", "daily at 17:00"),
        ("com.dex.meeting-intel", "every 30 minutes; also at load"),
        ("com.dex.smoke-nightly", "daily at 03:15"),
        ("dex-vault-backup", "daily at a user-selected time"),
    ]
    assert all(item.source_paths for item in automations)
    assert all(item.installer_path for item in automations)
    assert all(item.program_target for item in automations)


def test_discovers_four_reviewed_system_engine_groups() -> None:
    engines = discover_system_engines(REPO_ROOT)

    assert [engine.capability_id for engine in engines] == [
        "entity-temperature-engine",
        "proactive-promise-engine",
        "ritual-intelligence-engine",
        "session-hook-orchestration",
    ]
    assert next(item for item in engines if item.capability_id == "ritual-intelligence-engine").availability == "parked"
    assert all(engine.component_count == len(engine.source_paths) > 0 for engine in engines)
    assert all(1 <= len(engine.example_components) <= 5 for engine in engines)
    hooks = next(item for item in engines if item.capability_id == "session-hook-orchestration")
    assert all(not path.startswith(".claude/hooks/tests/") for path in hooks.source_paths)
    temperature = next(item for item in engines if item.capability_id == "entity-temperature-engine")
    assert "core/entity_engine/temperature.py" in temperature.source_paths
    assert "core/entity_engine/cooling.py" in temperature.source_paths
