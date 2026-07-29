"""Focused contracts for the one-time lifecycle-era updater bridge."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import dex_update_bridge as bridge


class _Service:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def build_and_preview_topology_migration(self, vault_root: Path):
        self.calls.append("topology-preview")
        return {"preview": {"step": "topology"}, "approval_token": "topology-token"}

    def execute_approved_topology_migration(self, vault_root: Path, preview, approved_token: str):
        self.calls.append(f"topology-execute:{approved_token}")
        assert preview == {"step": "topology"}
        return {"receipt": "topology"}

    def build_and_preview_delivered_release(self, vault_root: Path, release):
        self.calls.append("release-preview")
        assert release == bridge.FOUNDATION.identity()
        return {"preview": {"step": "release"}, "approval_token": "release-token"}

    def execute_approved_delivered_release(self, vault_root: Path, preview, approved_token: str):
        self.calls.append(f"release-execute:{approved_token}")
        assert preview == {"step": "release"}
        return {"receipt": "release"}



class _SplitService(_Service):
    def build_and_preview_topology_migration(self, vault_root: Path):
        self.calls.append("topology-preview")
        return {
            "topology": "post-split",
            "preview": {"status": "already complete"},
            "approval_token": None,
        }


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    (vault / ".git").mkdir(parents=True)
    (vault / ".dex" / "brain.git").mkdir(parents=True)
    (vault / "System").mkdir()
    return vault


def _completed_vault(tmp_path: Path) -> Path:
    vault = _vault(tmp_path)
    (vault / "System" / ".dex").mkdir()
    (vault / "System" / ".dex" / "topology.json").write_text(
        '{"topology":"brain-vault-split","vaultGitDir":".git",'
        '"brainGitDir":".dex/brain.git","installedRelease":"'
        + bridge.FOUNDATION.commit
        + '","environment":{"DEX_VAULT":"'
        + str(vault)
        + '"}}\n',
        encoding="utf-8",
    )
    (vault / ".git" / "dex-vault-v2").write_text('{"role":"vault"}\n', encoding="utf-8")
    (vault / ".dex" / "brain.git" / "dex-brain-v2").write_text(
        '{"role":"brain","installed":"' + bridge.FOUNDATION.commit + '"}\n',
        encoding="utf-8",
    )
    return vault


def test_foundation_pin_is_closed_and_uses_only_the_release_channel() -> None:
    assert bridge.FOUNDATION.identity() == {
        "tag": "dist/release/v1.80.5-9211053",
        "tag_object": "ff94463b191bb2c503ffec42ce288e961ca79659",
        "commit": "9211053235d7c1837a6e327bff1596b593323fc6",
        "tree": "d394658e2bf1125b96eb5afdace24f3a5ba3107e",
        "version": "1.80.5",
        "channel": "stable",
    }


def test_bridge_success_copy_names_the_canonical_dex_update_command() -> None:
    source = Path(bridge.__file__).read_text(encoding="utf-8")
    assert "future updates use /dex-update." in source
    assert "Future updates use /dex update." not in source


def test_release_pin_rejects_a_mutable_or_incomplete_identity() -> None:
    with pytest.raises(bridge.BridgeError, match="immutable distribution"):
        bridge.ReleasePin("release", "a" * 40, "b" * 40, "c" * 40, "1.80.5")
    with pytest.raises(bridge.BridgeError, match="malformed"):
        bridge.ReleasePin("dist/release/v1.80.5-aaaaaaa", "not-a-hash", "b" * 40, "c" * 40, "1.80.5")


def test_bridge_requires_two_new_approvals_and_routes_writes_through_foundation_service(tmp_path: Path) -> None:
    service = _Service()
    answers = iter(("APPLY", "APPLY"))
    fetched: list[Path] = []
    vault = _vault(tmp_path)

    result = bridge.run_bridge(
        vault,
        service,
        fetch_foundation=lambda root, _pin: fetched.append(root),
        input_fn=lambda _prompt: next(answers),
        output_fn=lambda _line: None,
    )

    assert result["foundation"] == bridge.FOUNDATION.identity()
    assert service.calls == [
        "topology-preview",
        "topology-execute:topology-token",
        "release-preview",
        "release-execute:release-token",
    ]
    assert fetched == [vault]


def test_bridge_stops_before_any_release_fetch_when_topology_preview_is_not_approved(tmp_path: Path) -> None:
    service = _Service()

    with pytest.raises(bridge.BridgeError, match="no change"):
        bridge.run_bridge(
            _vault(tmp_path),
            service,
            fetch_foundation=lambda _vault, _pin: pytest.fail("release fetch must not happen"),
            input_fn=lambda _prompt: "no",
            output_fn=lambda _line: None,
        )

    assert service.calls == ["topology-preview"]


def test_bridge_rejects_a_symlinked_vault_before_calling_the_service_or_fetching(tmp_path: Path) -> None:
    service = _Service()
    target = _vault(tmp_path)
    linked = tmp_path / "linked-vault"
    linked.symlink_to(target, target_is_directory=True)

    with pytest.raises(bridge.BridgeError, match="contains a symlink"):
        bridge.run_bridge(
            linked,
            service,
            fetch_foundation=lambda _vault, _pin: pytest.fail("release fetch must not happen"),
            input_fn=lambda _prompt: pytest.fail("approval must not be requested"),
            output_fn=lambda _line: pytest.fail("preview must not be rendered"),
        )

    assert service.calls == []


@pytest.mark.parametrize("private_parent", (".venv", ".dex"))
def test_bridge_rejects_a_symlinked_private_parent_before_service_or_fetch(
    tmp_path: Path, private_parent: str
) -> None:
    service = _Service()
    vault = _vault(tmp_path)
    target = tmp_path / f"{private_parent.removeprefix('.')}target"
    private_path = vault / private_parent
    if private_path.exists():
        private_path.rename(target)
    else:
        target.mkdir()
    (vault / private_parent).symlink_to(target, target_is_directory=True)

    with pytest.raises(bridge.BridgeError, match=rf"{private_parent} must not be a symlink"):
        bridge.run_bridge(
            vault,
            service,
            fetch_foundation=lambda _vault, _pin: pytest.fail("release fetch must not happen"),
            input_fn=lambda _prompt: pytest.fail("approval must not be requested"),
            output_fn=lambda _line: pytest.fail("preview must not be rendered"),
        )

    assert service.calls == []


def test_normal_virtualenv_python_symlink_remains_accepted(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    venv = vault / ".venv"
    (venv / "bin").mkdir(parents=True)
    (venv / "pyvenv.cfg").write_text("home = /synthetic\n", encoding="utf-8")
    (venv / "bin" / "python").symlink_to(Path(sys.executable))

    assert bridge._validate_vault(vault) == vault
    assert bridge._installed_python(vault) == venv / "bin" / "python"


def test_bridge_stops_before_delivered_release_execution_when_second_preview_is_not_approved(tmp_path: Path) -> None:
    service = _Service()
    answers = iter(("APPLY", "no"))

    with pytest.raises(bridge.BridgeError, match="no change"):
        bridge.run_bridge(
            _vault(tmp_path),
            service,
            fetch_foundation=lambda _vault, _pin: None,
            input_fn=lambda _prompt: next(answers),
            output_fn=lambda _line: None,
        )

    assert service.calls == ["topology-preview", "topology-execute:topology-token", "release-preview"]


def test_bridge_does_not_repeat_a_completed_topology_conversion(tmp_path: Path) -> None:
    service = _SplitService()
    vault = _vault(tmp_path)
    answers = iter(("APPLY",))

    result = bridge.run_bridge(
        vault,
        service,
        fetch_foundation=lambda _vault, _pin: None,
        input_fn=lambda _prompt: next(answers),
        output_fn=lambda _line: None,
    )

    assert result["topology_receipt"] == {"skipped": "already-brain-vault-split"}
    assert service.calls == ["topology-preview", "release-preview", "release-execute:release-token"]


def test_bridge_resumes_offline_without_fetching_or_revalidating_an_advanced_channel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _SplitService()
    monkeypatch.setattr(bridge, "_foundation_is_installed", lambda _vault, _pin: True)

    result = bridge.run_bridge(
        _vault(tmp_path),
        service,
        fetch_foundation=lambda _vault, _pin: pytest.fail("completed bridge must not fetch"),
        input_fn=lambda _prompt: pytest.fail("already-installed bridge must not request approval"),
        output_fn=lambda _line: pytest.fail("already-installed bridge must not render a preview"),
    )

    assert result["topology_receipt"] == {"skipped": "foundation-already-installed"}
    assert result["delivery_receipt"] == {"skipped": "foundation-already-installed"}
    assert service.calls == []


def test_completed_foundation_requires_all_durable_split_markers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = _completed_vault(tmp_path)
    monkeypatch.setattr(bridge, "_run_git", lambda *_arguments: bridge.FOUNDATION.commit)

    assert bridge._foundation_is_installed(vault, bridge.FOUNDATION) is True

    topology = vault / "System" / ".dex" / "topology.json"
    topology.write_text('{"topology":"brain-vault-split"}\n', encoding="utf-8")
    with pytest.raises(bridge.BridgeError, match="markers do not agree"):
        bridge._foundation_is_installed(vault, bridge.FOUNDATION)


def test_main_resumes_completed_foundation_before_runtime_or_source_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _completed_vault(tmp_path)
    monkeypatch.setattr(bridge, "_run_git", lambda *_arguments: bridge.FOUNDATION.commit)
    monkeypatch.setattr(
        bridge,
        "_reexec_in_installed_runtime",
        lambda *_arguments: pytest.fail("completed bridge must not re-exec"),
    )
    monkeypatch.setattr(
        bridge,
        "acquire_foundation_source",
        lambda: pytest.fail("completed bridge must not download source"),
    )

    assert bridge.main(["--vault", str(vault)]) == 0
    output = capsys.readouterr().out
    assert '"foundation-already-installed"' in output


def test_git_subprocess_environment_excludes_caller_git_and_credential_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_run(arguments, **kwargs):
        captured["arguments"] = arguments
        captured["environment"] = kwargs["env"]
        return subprocess.CompletedProcess(arguments, 0, stdout=b"ok\n", stderr=b"")

    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/private/attacker-config")
    monkeypatch.setenv("GIT_DIR", "/private/attacker-repository")
    monkeypatch.setenv("GIT_SSH_COMMAND", "attacker-command")
    monkeypatch.setenv("HOME", "/private/credential-home")
    monkeypatch.setenv("PYTHONPATH", "/private/attacker-python")
    monkeypatch.setattr(bridge.subprocess, "run", fake_run)

    assert bridge._run_git(tmp_path, "rev-parse", "HEAD") == "ok"

    environment = captured["environment"]
    assert isinstance(environment, dict)
    assert environment["GIT_CONFIG_GLOBAL"] == os.devnull
    assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
    assert environment["GIT_TERMINAL_PROMPT"] == "0"
    assert "HOME" not in environment
    assert "PYTHONPATH" not in environment
    assert "GIT_DIR" not in environment
    assert "GIT_SSH_COMMAND" not in environment
    assert "credential.helper=" in captured["arguments"]
