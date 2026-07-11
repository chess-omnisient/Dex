"""Start every shipped Dex MCP server and perform a real stdio initialize."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from core.utils.mcp_handshake import mcp_stdio_handshake

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_TEMPLATE = REPO_ROOT / "System" / ".mcp.json.example"


def _dex_owned_servers() -> list[tuple[str, Path, dict[str, str]]]:
    config = json.loads(MCP_TEMPLATE.read_text(encoding="utf-8"))
    servers = []
    prefix = "{{VAULT_PATH}}/"
    for name, entry in config["mcpServers"].items():
        command = entry.get("command")
        args = entry.get("args", [])
        script_args = [
            argument
            for argument in args
            if isinstance(argument, str) and argument.startswith(f"{prefix}core/mcp/")
        ]
        if not isinstance(command, str) or not command.endswith("/.venv/bin/python") or len(script_args) != 1:
            continue
        script = REPO_ROOT / script_args[0].removeprefix(prefix)
        servers.append((name, script, entry.get("env", {})))
    return servers


DEX_OWNED_SERVERS = _dex_owned_servers()
assert DEX_OWNED_SERVERS, "System/.mcp.json.example contains no Dex-owned Python servers"


@pytest.mark.parametrize(
    ("server_name", "script", "configured_env"),
    DEX_OWNED_SERVERS,
    ids=[name for name, _script, _env in DEX_OWNED_SERVERS],
)
def test_dex_owned_server_completes_stdio_initialize(
    server_name: str,
    script: Path,
    configured_env: dict[str, str],
    fixture_vault: Path,
    tmp_path: Path,
) -> None:
    vault = tmp_path / "vault"
    shutil.copytree(fixture_vault, vault)
    home = tmp_path / "home"
    home.mkdir()
    env = {
        "HOME": str(home),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONPATH": str(REPO_ROOT),
        "PYTHONUNBUFFERED": "1",
        "VAULT_PATH": str(vault),
    }
    env.update(
        {
            key: value.replace("{{VAULT_PATH}}", str(vault))
            for key, value in configured_env.items()
            if isinstance(key, str) and isinstance(value, str)
        }
    )

    result = mcp_stdio_handshake(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        env=env,
        timeout=10,
    )

    assert result.ok, f"{server_name}: {result.error}\nstderr:\n{result.stderr}"
    assert result.response is not None
    assert result.response["jsonrpc"] == "2.0"
    assert result.response["id"] == 1
    assert isinstance(result.response["result"]["capabilities"], dict)
    assert isinstance(result.response["result"]["serverInfo"], dict)
