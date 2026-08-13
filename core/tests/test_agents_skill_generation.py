"""Tests for generating `.agents/skills/` from canonical `.claude/skills/`."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "scripts/generate-agents-skills.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_agents_skills", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generator_is_deterministic() -> None:
    generator = _load_generator()
    first = generator.expected_adapters(REPO_ROOT)
    second = generator.expected_adapters(REPO_ROOT)
    assert first.keys() == second.keys()
    assert first == second
    assert any(path.name == "SKILL.md" for path in first)


def test_strip_removes_nested_hooks_and_keeps_portable_keys() -> None:
    generator = _load_generator()
    source = """---
name: example
description: "A skill. Use when testing."
model_hint: balanced
model_routing:
  default: balanced
hooks:
  PostToolUse:
    - matcher: Write
      type: command
      command: "node .claude/hooks/example.cjs"
context: conversation
---

Body mentions hooks in prose.
"""
    stripped, comment, body = generator.transform_skill_markdown(
        source, source_relative=".claude/skills/example/SKILL.md"
    )
    assert "name: example" in stripped
    assert "model_hint: balanced" in stripped
    assert "hooks:" not in stripped
    assert "model_routing:" not in stripped
    assert "context:" not in stripped
    assert "PostToolUse" not in stripped
    assert "Generated from `.claude/skills/example/SKILL.md`" in comment
    assert "Body mentions hooks in prose." in body


def test_custom_skill_directories_are_not_generated_or_deleted(tmp_path: Path) -> None:
    generator = _load_generator()
    repo = tmp_path / "vault"
    source = repo / ".claude" / "skills" / "demo"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Demo. Use when testing.\n---\n\nHello.\n",
        encoding="utf-8",
    )
    custom = repo / ".agents" / "skills" / "demo-custom"
    custom.mkdir(parents=True)
    (custom / "SKILL.md").write_text(
        "---\nname: demo-custom\ndescription: User owned.\n---\n\nMine.\n",
        encoding="utf-8",
    )
    stale = repo / ".agents" / "skills" / "stale-hand-port"
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text("stale\n", encoding="utf-8")

    assert generator.write_adapters(repo) == 0
    generated = (repo / ".agents" / "skills" / "demo" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "name: demo" in generated
    assert "Generated from" in generated
    assert (custom / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: demo-custom")
    assert not stale.exists()
    assert generator.check_adapters(repo) == 0


def test_check_mode_fails_when_an_adapter_is_stale(tmp_path: Path) -> None:
    generator = _load_generator()
    repo = tmp_path / "vault"
    source = repo / ".claude" / "skills" / "demo"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Demo. Use when testing.\n---\n\nHello.\n",
        encoding="utf-8",
    )
    assert generator.write_adapters(repo) == 0
    adapter = repo / ".agents" / "skills" / "demo" / "SKILL.md"
    adapter.write_text(adapter.read_text(encoding="utf-8") + "hand edit\n", encoding="utf-8")
    assert generator.check_adapters(repo) != 0


def test_cli_check_passes_on_the_committed_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    # The adapters are generated in this change; --check must pass once they
    # are written. If this fails locally, run the generator and commit.
    assert result.returncode == 0, result.stdout + result.stderr
    assert "adapters are current" in result.stdout
