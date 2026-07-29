"""Focused contracts for the one-time lifecycle-era updater bridge."""

from __future__ import annotations

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
    assert "Future updates use dex-update." in source
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


def test_bridge_can_resume_after_the_foundation_was_installed_before_a_later_step(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _SplitService()
    monkeypatch.setattr(bridge, "_foundation_is_installed", lambda _vault, _pin: True)

    result = bridge.run_bridge(
        _vault(tmp_path),
        service,
        fetch_foundation=lambda _vault, _pin: None,
        input_fn=lambda _prompt: pytest.fail("already-installed bridge must not request approval"),
        output_fn=lambda _line: pytest.fail("already-installed bridge must not render a preview"),
    )

    assert result["delivery_receipt"] == {"skipped": "foundation-already-installed"}
    assert service.calls == ["topology-preview"]
