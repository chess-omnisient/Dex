"""Tests for the vault backup engine, installer, and restore tool.

All filesystem-only: no network, and every rclone interaction is mocked.
"""

import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from core.backup import backup_vault, install_backup_job, restore_vault

# --- fixtures ---------------------------------------------------------------

@pytest.fixture
def vault(tmp_path):
    root = tmp_path / "vault"
    (root / "System" / "integrations").mkdir(parents=True)
    (root / "05-Areas" / "People").mkdir(parents=True)
    (root / "05-Areas" / "People" / "Ada_Lovelace.md").write_text("# Ada\n")
    (root / ".env").write_text("ANTHROPIC_API_KEY=secret\n")
    (root / ".mcp.json").write_text("{}\n")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "bulk.js").write_text("x")
    return root


def write_config(vault, destination, backend="folder", extra=""):
    (vault / "System" / "integrations" / "config.yaml").write_text(
        "backup:\n"
        "  enabled: true\n"
        f"  backend: {backend}\n"
        f"  destination: {destination}\n"
        + extra
    )


def read_stamp(vault):
    return json.loads((vault / "System" / ".dex" / "backup-last-run.json").read_text())


def make_set(dest, stamp):
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{backup_vault.PREFIX}{stamp}.tar.gz").write_bytes(b"archive")
    (dest / f"{backup_vault.PREFIX}{stamp}.sha256").write_text("sums\n")


# --- retention maths --------------------------------------------------------

def test_prune_keeps_gfs_ladder_and_deletes_the_rest(tmp_path):
    dest = tmp_path / "backups"
    stamps = [
        "20260711-020000",  # newest: today
        "20260710-020000",  # yesterday
        "20260709-020000",  # older daily, outside daily=2
        "20260630-020000",  # previous ISO week and month
        "20260501-020000",  # older month, outside monthly=2
    ]
    for stamp in stamps:
        make_set(dest, stamp)
    backend = backup_vault.FolderBackend({"destination": str(dest)})
    pruned = backup_vault.prune(backend, {"daily": 2, "weekly": 1, "monthly": 2})

    assert sorted(pruned) == ["20260501-020000", "20260709-020000"]
    remaining = backend.list_sets()
    assert remaining == ["20260711-020000", "20260710-020000", "20260630-020000"]
    # a pruned set loses every file, not just the archive
    assert not list(dest.glob("*20260709*"))


def test_prune_never_deletes_the_newest_set_even_with_zero_retention(tmp_path):
    dest = tmp_path / "backups"
    make_set(dest, "20260711-020000")
    make_set(dest, "20260710-020000")
    backend = backup_vault.FolderBackend({"destination": str(dest)})
    pruned = backup_vault.prune(backend, {"daily": 0, "weekly": 0, "monthly": 0})
    assert pruned == ["20260710-020000"]
    assert backend.list_sets() == ["20260711-020000"]


def test_prune_never_deletes_an_unrecognised_stamp(tmp_path):
    dest = tmp_path / "backups"
    make_set(dest, "20260711-020000")
    make_set(dest, "not-a-timestamp")
    backend = backup_vault.FolderBackend({"destination": str(dest)})
    pruned = backup_vault.prune(backend, {"daily": 1, "weekly": 0, "monthly": 0})
    assert pruned == []
    assert (dest / f"{backup_vault.PREFIX}not-a-timestamp.tar.gz").exists()


# --- exclusion filter -------------------------------------------------------

@pytest.mark.parametrize("relative,expected", [
    (".env", True),
    (".env.local", True),
    (".mcp.json", True),
    ("node_modules/bulk.js", True),
    ("04-Projects/demo/node_modules/dep/index.js", True),
    (".venv/bin/python", True),
    ("System/backup/backup.log", True),
    (".claude/worktrees/scratch/file.md", True),
    ("05-Areas/People/Ada_Lovelace.md", False),
    ("System/user-profile.yaml", False),
    ("04-Projects/environments.md", False),
])
def test_excluded_paths(relative, expected):
    assert backup_vault.excluded(relative) is expected


def test_archive_excludes_secrets_and_bulk_but_keeps_notes(vault, tmp_path):
    workdir = tmp_path / "work"
    workdir.mkdir()
    artifacts = backup_vault.build_artifacts(vault, workdir, "20260711-020000")
    archive = artifacts[0]
    with tarfile.open(archive) as tar:
        names = tar.getnames()
    assert f"{backup_vault.ARCNAME}/05-Areas/People/Ada_Lovelace.md" in names
    assert not any(".env" in name for name in names)
    assert not any(".mcp.json" in name for name in names)
    assert not any("node_modules" in name for name in names)


# --- stamp on every outcome -------------------------------------------------

def test_failure_writes_stamp_with_the_error(vault):
    write_config(vault, destination="")  # deliberately unconfigured
    assert backup_vault.run_backup(vault) == 1
    stamp = read_stamp(vault)
    assert stamp["ok"] is False
    assert "backup.destination is not set" in stamp["error"]


def test_unknown_backend_fails_loudly_and_is_stamped(vault, tmp_path):
    write_config(vault, destination=str(tmp_path / "dest"), backend="carrier-pigeon")
    assert backup_vault.run_backup(vault) == 1
    stamp = read_stamp(vault)
    assert stamp["ok"] is False
    assert "unknown backup backend" in stamp["error"]


def test_successful_run_stores_set_and_writes_ok_stamp(vault, tmp_path):
    dest = tmp_path / "backups"
    write_config(vault, destination=str(dest))
    assert backup_vault.run_backup(vault) == 0
    stamp = read_stamp(vault)
    assert stamp["ok"] is True
    assert stamp["backend"] == "folder"
    archives = list(dest.glob(f"{backup_vault.PREFIX}*.tar.gz"))
    sidecars = list(dest.glob(f"{backup_vault.PREFIX}*.sha256"))
    assert len(archives) == 1 and len(sidecars) == 1
    assert not list(dest.glob("*.partial"))


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_git_vault_gets_a_verified_history_bundle(vault, tmp_path):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
           "HOME": str(tmp_path), "PATH": "/usr/bin:/bin"}
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=vault, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=vault, check=True, env=env)
    dest = tmp_path / "backups"
    write_config(vault, destination=str(dest))
    assert backup_vault.run_backup(vault) == 0
    bundles = list(dest.glob(f"{backup_vault.PREFIX}*.bundle"))
    assert len(bundles) == 1
    sidecar = next(dest.glob(f"{backup_vault.PREFIX}*.sha256"))
    assert bundles[0].name in sidecar.read_text()


# --- backend selection and rclone degradation -------------------------------

def test_rclone_backend_fails_gracefully_when_binary_is_absent(monkeypatch):
    def missing(*_args, **_kwargs):
        raise FileNotFoundError("rclone")
    monkeypatch.setattr(backup_vault.subprocess, "run", missing)
    with pytest.raises(RuntimeError, match="not installed or not on PATH"):
        backup_vault.RcloneBackend({"remote": "b2:dex-backups"})


def test_rclone_backend_requires_a_remote(monkeypatch):
    monkeypatch.setattr(
        backup_vault.subprocess, "run",
        lambda *_a, **_k: pytest.fail("must not probe rclone without a remote"),
    )
    with pytest.raises(RuntimeError, match="backup.remote is not set"):
        backup_vault.RcloneBackend({"remote": ""})


def test_rclone_failure_during_a_run_is_stamped(vault, monkeypatch):
    write_config(vault, destination="", backend="rclone",
                 extra="  remote: b2:dex-backups\n")

    def missing(*_args, **_kwargs):
        raise FileNotFoundError("rclone")
    monkeypatch.setattr(backup_vault.subprocess, "run", missing)
    assert backup_vault.run_backup(vault) == 1
    stamp = read_stamp(vault)
    assert stamp["ok"] is False
    assert "rclone" in stamp["error"]


# --- config parsing ---------------------------------------------------------

def test_config_without_yaml_module_still_parses(monkeypatch):
    text = (
        "enabled:\n"
        "  notion: false\n"
        "backup:\n"
        "  enabled: true\n"
        "  backend: folder  # a comment\n"
        "  destination: '/Users/pat/OneDrive/Dex Backups'\n"
        "  retention:\n"
        "    daily: 5\n"
        "    weekly: 2\n"
        "hooks:\n"
        "  meeting_prep:\n"
        "    use_notion: false\n"
    )
    block = backup_vault.parse_backup_block_without_yaml(text)
    assert block["enabled"] == "true"
    assert block["backend"] == "folder"
    assert block["destination"] == "/Users/pat/OneDrive/Dex Backups"
    assert block["retention"] == {"daily": "5", "weekly": "2"}


def test_load_config_honours_legacy_retention_days(vault):
    (vault / "System" / "integrations" / "config.yaml").write_text(
        "backup:\n"
        "  enabled: true\n"
        "  destination: /backups\n"
        "  retention_days: 9\n"
    )
    config = backup_vault.load_config(vault)
    assert config["retention"] == {"daily": 9, "weekly": 0, "monthly": 0}


def test_load_config_defaults_when_block_is_absent(vault):
    config = backup_vault.load_config(vault)
    assert config["enabled"] is False
    assert config["backend"] == "folder"
    assert config["retention"] == {"daily": 7, "weekly": 4, "monthly": 3}


# --- installer --------------------------------------------------------------

def test_build_plist_pins_interpreter_environment_and_schedule(tmp_path):
    payload = install_backup_job.build_plist(
        tmp_path, "/opt/example/bin/python3", hour=12, minute=30)
    assert payload["Label"] == "com.dex.vault-backup"
    assert payload["ProgramArguments"][0] == "/opt/example/bin/python3"
    assert payload["ProgramArguments"][1] == str(
        tmp_path / "core" / "backup" / "backup_vault.py")
    assert payload["EnvironmentVariables"]["VAULT_PATH"] == str(tmp_path)
    assert "/usr/bin" in payload["EnvironmentVariables"]["PATH"]
    assert payload["StartCalendarInterval"] == {"Hour": 12, "Minute": 30}
    assert payload["WorkingDirectory"] == str(tmp_path)


def test_installer_refuses_a_temporary_checkout(tmp_path):
    worktree = tmp_path / "worktrees" / "scratch"
    worktree.mkdir(parents=True)
    assert install_backup_job.looks_like_temporary_checkout(worktree)
    plain = tmp_path / "real-vault"
    plain.mkdir()
    assert not install_backup_job.looks_like_temporary_checkout(plain)
    (plain / ".git").write_text("gitdir: elsewhere\n")
    assert install_backup_job.looks_like_temporary_checkout(plain)


def test_installer_prints_cron_guidance_on_other_platforms(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(install_backup_job.sys, "platform", "linux")
    code = install_backup_job.main(["--vault", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 2
    assert "crontab -e" in out
    assert "Nothing was installed" in out


# --- restore tool -----------------------------------------------------------

@pytest.fixture
def backed_up(vault, tmp_path):
    dest = tmp_path / "backups"
    write_config(vault, destination=str(dest))
    assert backup_vault.run_backup(vault) == 0
    stamp = read_stamp(vault)["set"]
    return vault, dest, stamp


def test_verify_passes_on_an_intact_set(backed_up):
    _vault, dest, stamp = backed_up
    findings = restore_vault.verify_set(dest, stamp)
    assert any("checksum matches" in finding for finding in findings)


def test_verify_detects_a_damaged_archive(backed_up):
    _vault, dest, stamp = backed_up
    archive = dest / f"{backup_vault.PREFIX}{stamp}.tar.gz"
    archive.write_bytes(archive.read_bytes() + b"corruption")
    with pytest.raises(restore_vault.RestoreError, match="does not match"):
        restore_vault.verify_set(dest, stamp)


def test_test_mode_extracts_to_a_temporary_folder_only(backed_up, capsys):
    vault_root, dest, _stamp = backed_up
    code = restore_vault.main(["test", "--source", str(dest),
                              "--vault", str(vault_root)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Test restore succeeded" in out
    assert "Nothing was changed" in out


def test_restore_refuses_the_live_vault_and_non_empty_targets(backed_up, tmp_path):
    vault_root, dest, stamp = backed_up
    with pytest.raises(restore_vault.RestoreError, match="live vault"):
        restore_vault.restore(dest, stamp, vault_root, vault_root)
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "existing.txt").write_text("keep me")
    with pytest.raises(restore_vault.RestoreError, match="not empty"):
        restore_vault.restore(dest, stamp, occupied, vault_root)
    assert (occupied / "existing.txt").read_text() == "keep me"


def test_restore_extracts_into_a_fresh_folder(backed_up, tmp_path, capsys):
    vault_root, dest, stamp = backed_up
    target = tmp_path / "restored"
    restore_vault.restore(dest, stamp, target, vault_root)
    restored_note = (target / backup_vault.ARCNAME / "05-Areas" / "People"
                     / "Ada_Lovelace.md")
    assert restored_note.read_text() == "# Ada\n"
    assert not (target / backup_vault.ARCNAME / ".env").exists()


def test_pick_set_prefers_newest_and_validates_requests(tmp_path):
    dest = tmp_path / "backups"
    make_set(dest, "20260710-020000")
    make_set(dest, "20260711-020000")
    assert restore_vault.pick_set(dest, None) == "20260711-020000"
    assert restore_vault.pick_set(dest, "20260710-020000") == "20260710-020000"
    with pytest.raises(restore_vault.RestoreError, match="not found"):
        restore_vault.pick_set(dest, "20990101-000000")
