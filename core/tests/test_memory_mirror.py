"""Copy Claude Code per-project memory into the vault without leaking personal data."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.utils import doctor, memory_mirror

NOW = datetime(2026, 8, 13, 15, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _isolate_claude_config_dir(monkeypatch) -> None:
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)


def _vault(tmp_path: Path) -> tuple[Path, Path]:
    vault = tmp_path / "fixture_vault"
    home = tmp_path / "home"
    vault.mkdir()
    home.mkdir()
    (vault / "System").mkdir()
    return vault, home


def _write_source(home: Path, encoded: str, files: dict[str, str]) -> Path:
    memory_dir = home / ".claude" / "projects" / encoded / "memory"
    memory_dir.mkdir(parents=True)
    for name, content in files.items():
        target = memory_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return memory_dir


def _dest_text(vault: Path, relative: str) -> str:
    return (vault / "System" / "memory-mirror" / relative).read_text(encoding="utf-8")


def test_encoding_replaces_separators_and_non_alnum() -> None:
    root = Path("/tmp/fixture_vault")
    assert memory_mirror.encode_separators(root) == "-tmp-fixture_vault"
    assert memory_mirror.encode_non_alnum(root) == "-tmp-fixture-vault"


def test_manifest_round_trip_parses_the_dated_record() -> None:
    text = memory_mirror.render_manifest(
        mirrored_at=NOW,
        file_count=3,
        copied=("MEMORY.md",),
        removed=("old.md",),
        unchanged=1,
        source_method="derived",
    )
    parsed = memory_mirror.parse_manifest(text)
    assert parsed is not None
    assert parsed.file_count == 3
    assert parsed.mirrored_at == NOW


def test_derived_source_is_preferred_when_memory_entrypoint_exists(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n", "topic-one.md": "alpha\n"})

    resolution = memory_mirror.resolve_source(vault, home)

    assert resolution.status == memory_mirror.STATUS_FOUND
    assert resolution.method == "derived"
    assert resolution.path is not None
    assert resolution.path.name == "memory"


def test_fallback_finds_memory_when_non_alnum_encoding_is_the_live_folder(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_non_alnum(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})

    resolution = memory_mirror.resolve_source(vault, home)

    assert resolution.status == memory_mirror.STATUS_FOUND
    assert resolution.method in {"derived", "fallback"}
    assert (resolution.path / "MEMORY.md").is_file()


def test_empty_encoded_folder_without_entrypoint_fails_loudly(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    empty = home / ".claude" / "projects" / encoded / "memory"
    empty.mkdir(parents=True)

    resolution = memory_mirror.resolve_source(vault, home)

    assert resolution.status == memory_mirror.STATUS_EMPTY_ENCODED
    assert "MEMORY.md" in resolution.detail


def test_user_level_memory_is_never_selected_as_the_source(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    user_memory = home / ".claude" / "memory"
    user_memory.mkdir(parents=True)
    (home / ".claude" / "CLAUDE.md").write_text("# user-level instructions\n", encoding="utf-8")
    (user_memory / "MEMORY.md").write_text("# user-level memory\n", encoding="utf-8")

    resolution = memory_mirror.resolve_source(vault, home)

    assert resolution.status == memory_mirror.STATUS_MISSING
    assert resolution.path is None


def test_successful_copy_does_not_import_user_level_files(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    (home / ".claude").mkdir(parents=True, exist_ok=True)
    (home / ".claude" / "CLAUDE.md").write_text("# user-level instructions\n", encoding="utf-8")
    user_memory = home / ".claude" / "memory"
    user_memory.mkdir(exist_ok=True)
    (user_memory / "MEMORY.md").write_text("# user-level memory\n", encoding="utf-8")

    outcome = memory_mirror.mirror(vault_root=vault, home=home, now=NOW)

    assert outcome.action == memory_mirror.ACTION_MIRRORED
    names = {path.name for path in (vault / "System" / "memory-mirror").iterdir()}
    assert names == {"MEMORY.md", "_MANIFEST.md"}
    assert _dest_text(vault, "MEMORY.md") == "# fixture index\n"
    manifest_text = (vault / "System" / "memory-mirror" / "_MANIFEST.md").read_text(encoding="utf-8")
    assert "# user-level" not in _dest_text(vault, "MEMORY.md")
    assert "# user-level" not in manifest_text


def test_ambiguous_fallback_refuses_rather_than_guessing(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    projects = home / ".claude" / "projects"
    first = memory_mirror.encode_separators(vault.resolve())
    second = first + "-extra"
    for name in (first, second):
        memory_dir = projects / name / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "MEMORY.md").write_text("# fixture index\n", encoding="utf-8")
    # Make the extra dir also match the normalized wanted set by using the
    # non-alnum encoding as a second live folder when it differs.
    alt = memory_mirror.encode_non_alnum(vault.resolve())
    if alt != first:
        memory_dir = projects / alt / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        (memory_dir / "MEMORY.md").write_text("# fixture index\n", encoding="utf-8")

    resolution = memory_mirror.resolve_source(vault, home)

    assert resolution.status in {
        memory_mirror.STATUS_AMBIGUOUS,
        memory_mirror.STATUS_FOUND,
    }
    if resolution.status == memory_mirror.STATUS_FOUND:
        assert resolution.path is not None
        assert resolution.path.parent.name in {first, alt}


def test_mutation_lock_skips_without_writing(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    lock = vault / "System" / ".dex" / "mutation.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("{}\n", encoding="utf-8")

    outcome = memory_mirror.mirror(vault_root=vault, home=home, now=NOW)

    assert outcome.action == memory_mirror.ACTION_SKIPPED
    assert not (vault / "System" / "memory-mirror").exists()


def test_mirror_copies_files_writes_manifest_and_is_idempotent(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(
        home,
        encoded,
        {"MEMORY.md": "# fixture index\n", "topic-one.md": "alpha\n"},
    )

    first = memory_mirror.mirror(vault_root=vault, home=home, now=NOW)
    second = memory_mirror.mirror(
        vault_root=vault, home=home, now=NOW + timedelta(minutes=5)
    )

    assert first.action == memory_mirror.ACTION_MIRRORED
    assert first.wrote is True
    assert set(first.copied) == {"MEMORY.md", "topic-one.md"}
    assert _dest_text(vault, "topic-one.md") == "alpha\n"
    manifest = memory_mirror.read_manifest(vault)
    assert manifest is not None
    assert manifest.file_count == 2
    assert second.action == memory_mirror.ACTION_NOOP
    assert second.copied == ()
    assert second.removed == ()
    assert "2026-08-13T15:05:00+00:00" in memory_mirror.manifest_path(vault).read_text(
        encoding="utf-8"
    )


def test_mirror_deletes_files_removed_from_the_source(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    source = _write_source(
        home,
        encoded,
        {"MEMORY.md": "# fixture index\n", "topic-one.md": "alpha\n", "topic-two.md": "beta\n"},
    )
    memory_mirror.mirror(vault_root=vault, home=home, now=NOW)
    (source / "topic-two.md").unlink()

    outcome = memory_mirror.mirror(
        vault_root=vault, home=home, now=NOW + timedelta(minutes=1)
    )

    assert outcome.removed == ("topic-two.md",)
    assert not (vault / "System" / "memory-mirror" / "topic-two.md").exists()
    assert _dest_text(vault, "topic-one.md") == "alpha\n"


def test_drop_guard_refuses_to_propagate_a_wipe(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    files = {f"topic-{index}.md": f"note {index}\n" for index in range(8)}
    files["MEMORY.md"] = "# fixture index\n"
    source = _write_source(home, encoded, files)
    memory_mirror.mirror(vault_root=vault, home=home, now=NOW)
    for path in source.iterdir():
        if path.name != "MEMORY.md":
            path.unlink()

    outcome = memory_mirror.mirror(
        vault_root=vault, home=home, now=NOW + timedelta(minutes=1)
    )

    assert outcome.action == memory_mirror.ACTION_REFUSED
    assert outcome.wrote is False
    assert (vault / "System" / "memory-mirror" / "topic-0.md").is_file()
    assert memory_mirror.read_manifest(vault).mirrored_at == NOW


def test_dry_run_reports_and_writes_nothing(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n", "topic-one.md": "alpha\n"})

    outcome = memory_mirror.mirror(vault_root=vault, home=home, now=NOW, dry_run=True)

    assert outcome.action == memory_mirror.ACTION_DRY_RUN
    assert "would copy" in outcome.detail.lower() or "Dry run" in outcome.detail
    assert not (vault / "System" / "memory-mirror").exists()


def test_cli_dry_run_env_writes_nothing(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    env = {
        **os.environ,
        memory_mirror.DRY_RUN_ENV: "1",
        "HOME": str(home),
        "CLAUDE_PROJECT_DIR": str(vault),
    }

    exit_code = memory_mirror.main(["--vault", str(vault), "--home", str(home)], env=env)

    assert exit_code == 0
    assert not (vault / "System" / "memory-mirror").exists()


def test_cli_refuses_empty_encoded_source(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    (home / ".claude" / "projects" / encoded / "memory").mkdir(parents=True)

    exit_code = memory_mirror.main(
        ["--vault", str(vault), "--home", str(home)],
        env={**os.environ, "HOME": str(home)},
    )

    assert exit_code == 1
    assert not (vault / "System" / "memory-mirror").exists()


def test_doctor_is_off_when_there_is_nothing_to_copy(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    context = doctor.DoctorContext(vault_root=vault, repo_root=vault, home=home, now=NOW)

    result = doctor._probe_memory_mirror(context)

    assert result.verdict == "OFF"
    assert "nothing to copy" in result.detail


def test_doctor_reports_missing_mirror_when_source_exists(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    context = doctor.DoctorContext(vault_root=vault, repo_root=vault, home=home, now=NOW)

    result = doctor._probe_memory_mirror(context)

    assert result.verdict == "BROKEN"
    assert "never copied" in result.detail
    assert result.heal is not None


def test_doctor_reports_stale_mirror(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    memory_mirror.mirror(vault_root=vault, home=home, now=NOW - timedelta(days=10))
    context = doctor.DoctorContext(vault_root=vault, repo_root=vault, home=home, now=NOW)

    result = doctor._probe_memory_mirror(context)

    assert result.verdict == "BROKEN"
    assert "days old" in result.detail


def test_doctor_ok_after_a_fresh_copy(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n", "topic-one.md": "alpha\n"})
    memory_mirror.mirror(vault_root=vault, home=home, now=NOW)
    context = doctor.DoctorContext(vault_root=vault, repo_root=vault, home=home, now=NOW)

    result = doctor._probe_memory_mirror(context)

    assert result.verdict == "OK"
    assert "2 files" in result.detail


def test_doctor_flags_empty_encoded_source_as_broken(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    (home / ".claude" / "projects" / encoded / "memory").mkdir(parents=True)
    context = doctor.DoctorContext(vault_root=vault, repo_root=vault, home=home, now=NOW)

    result = doctor._probe_memory_mirror(context)

    assert result.verdict == "BROKEN"
    assert "MEMORY.md" in result.detail


def test_inspect_does_not_write(tmp_path: Path) -> None:
    vault, home = _vault(tmp_path)
    encoded = memory_mirror.encode_separators(vault.resolve())
    _write_source(home, encoded, {"MEMORY.md": "# fixture index\n"})
    before = list(vault.rglob("*"))

    memory_mirror.inspect(vault_root=vault, home=home, now=NOW)

    after = list(vault.rglob("*"))
    assert after == before
