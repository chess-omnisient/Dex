"""Command-level coverage for the Obsidian wiki-link migration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_SCRIPT = REPO_ROOT / "core/obsidian/migrate_to_wikilinks.py"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git(vault: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "user.name=Dex Test", "-c", "user.email=test@example.com", *args],
        cwd=vault,
        check=True,
        capture_output=True,
        text=True,
    )


def test_fresh_vault_migration_only_rewrites_user_content(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    product_files = {
        "CLAUDE.md": "Read `.claude/skills/README.md`, README, and ^task-20260128-010.\n",
        ".claude/skills/README.md": "This README is product documentation.\n",
        "docs/Dex_Technical_Guide.md": "Example: `^task-20260128-011`.\n",
    }
    placeholders = (
        "04-Projects/README.md",
        "05-Areas/People/README.md",
        "05-Areas/Companies/README.md",
    )
    for relative, content in product_files.items():
        _write(vault / relative, content)
    for relative in placeholders:
        _write(vault / relative, "Placeholder README only.\n")
    tasks = vault / "03-Tasks/Tasks.md"
    _write(
        tasks,
        "Keep README plain and `^task-20260128-001` literal.\n"
        "Convert the real anchor ^task-20260128-002.\n",
    )

    tools = tmp_path / "bin"
    for name in ("osascript", "afplay"):
        executable = tools / name
        _write(executable, "#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)

    _git(vault, "init", "-q")
    _git(vault, "add", "-A")
    _git(vault, "commit", "-q", "-m", "pristine fresh vault")
    head_before = _git(vault, "rev-parse", "HEAD").stdout.strip()

    result = subprocess.run(
        [sys.executable, str(MIGRATION_SCRIPT)],
        cwd=vault,
        env={**os.environ, "PATH": f"{tools}:{os.environ['PATH']}", "VAULT_PATH": str(vault)},
        input="\n",
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Found 0 people" in result.stdout
    assert "Found 0 projects" in result.stdout
    assert "Found 0 companies" in result.stdout
    assert "git reset --hard HEAD~1" not in result.stdout
    assert head_before in result.stdout
    assert _git(vault, "rev-parse", "HEAD").stdout.strip() == head_before
    for relative, content in product_files.items():
        assert (vault / relative).read_text(encoding="utf-8") == content
    assert tasks.read_text(encoding="utf-8") == (
        "Keep README plain and `^task-20260128-001` literal.\n"
        "Convert the real anchor [[^task-20260128-002]].\n"
    )
