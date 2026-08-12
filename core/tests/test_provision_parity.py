"""Parity guard between the canonical Node provisioner and onboarding seeds."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from core import capabilities
from core.lifecycle import service

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "packages/dex-contracts/dist/portable-vault.contract.json"


def _prepare_provision_vault(
    tmp_path: Path,
    *,
    profile_text: str | None = None,
    companies_default: bool | None = None,
) -> Path:
    vault = tmp_path / "vault"
    (vault / "System").mkdir(parents=True)
    (vault / "core").mkdir()
    (vault / ".scripts").mkdir()
    shutil.copy(REPO_ROOT / "System/.mcp.json.example", vault / "System/.mcp.json.example")
    shutil.copy(
        REPO_ROOT / "System/user-profile-template.yaml",
        vault / "System/user-profile-template.yaml",
    )
    if companies_default is not None:
        template_path = vault / "System/user-profile-template.yaml"
        template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        template["capabilities"]["companies"]["enabled"] = companies_default
        template_path.write_text(
            yaml.safe_dump(template, sort_keys=False),
            encoding="utf-8",
        )
    shutil.copy(REPO_ROOT / "core/paths.py", vault / "core/paths.py")
    shutil.copy(REPO_ROOT / "package.json", vault / "package.json")
    shutil.copy(REPO_ROOT / "CLAUDE.md", vault / "CLAUDE.md")
    if profile_text is not None:
        (vault / "System/user-profile.yaml").write_text(
            profile_text,
            encoding="utf-8",
        )
    return vault


def _invoke_provision(
    vault: Path,
    *options: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "node",
            str(REPO_ROOT / "core/provision.cjs"),
            "--path",
            str(vault),
            *options,
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_provision(vault: Path, *options: str) -> dict:
    completed = _invoke_provision(vault, *options)
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _snapshot_tree(root: Path) -> dict[str, tuple[str, bytes | str]]:
    snapshot: dict[str, tuple[str, bytes | str]] = {}
    for candidate in sorted(root.rglob("*")):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(candidate))
        elif candidate.is_file():
            snapshot[relative] = ("file", candidate.read_bytes())
        elif candidate.is_dir():
            snapshot[relative] = ("directory", "")
    return snapshot


def test_installer_routes_bootstrap_config_to_sanctioned_provision_contract() -> None:
    installer = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")

    assert "--install-config-only" in installer
    assert "System/.mcp.json.example > .mcp.json" not in installer
    assert "mcp_path.write_text" not in installer


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_adopt_preserves_existing_content_while_routing_lifecycle(tmp_path: Path) -> None:
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text="name: Existing User\ncustom: keep\n",
    )
    (vault / "03-Tasks").mkdir()
    tasks = vault / "03-Tasks/Tasks.md"
    tasks.write_text("# My tasks\n", encoding="utf-8")

    summary = _run_provision(vault, "--adopt")

    assert summary["lifecycle_executor"]["api_version"] == service.api_version
    assert summary["lifecycle_executor"]["skipped"] == "no-release-catalog"
    assert "name: Existing User" in (vault / "System/user-profile.yaml").read_text()
    assert "custom: keep" in (vault / "System/user-profile.yaml").read_text()
    assert tasks.read_text(encoding="utf-8") == "# My tasks\n"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_fresh_provision_enables_companies_and_creates_its_room(tmp_path: Path) -> None:
    vault = _prepare_provision_vault(tmp_path)

    _run_provision(vault)

    profile_path = vault / "System/user-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    assert profile["capabilities"]["companies"]["enabled"] is True
    assert capabilities.enabled(
        "companies",
        profile_path=profile_path,
        contract_path=CONTRACT_PATH,
    ) is True
    assert (vault / "05-Areas/Companies").is_dir()


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_onboarding_refuses_room_source_drift_before_any_vault_mutation(
    tmp_path: Path,
) -> None:
    vault = _prepare_provision_vault(tmp_path)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["capabilities"]["career"]["skill_sources"][0]["sha256"] = "0" * 64
    drifted = tmp_path / "drifted-contract.json"
    drifted.write_text(json.dumps(contract), encoding="utf-8")
    before = _snapshot_tree(vault)

    completed = _invoke_provision(
        vault,
        "--onboard",
        env={
            **os.environ,
            "DEX_CAPABILITY_CONTRACT_PATH": str(drifted),
        },
    )

    assert completed.returncode != 0
    errors = " ".join(json.loads(completed.stdout)["errors"]).lower()
    assert "identity" in errors or "sha256" in errors
    assert _snapshot_tree(vault) == before


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("unsafe_kind", ("symlink", "custom-bytes"))
def test_onboarding_refuses_unsafe_active_skill_before_any_vault_mutation(
    tmp_path: Path,
    unsafe_kind: str,
) -> None:
    vault = _prepare_provision_vault(tmp_path)
    target = vault / ".claude/skills/resume-builder"
    target.parent.mkdir(parents=True, exist_ok=True)
    if unsafe_kind == "symlink":
        protected = vault / "05-Areas/Do-Not-Touch"
        protected.mkdir(parents=True)
        (protected / "sentinel.md").write_text("preserve\n", encoding="utf-8")
        target.symlink_to(protected, target_is_directory=True)
    else:
        target.mkdir()
        (target / "SKILL.md").write_text("user-owned custom skill\n", encoding="utf-8")
    before = _snapshot_tree(vault)

    completed = _invoke_provision(vault, "--onboard")

    assert completed.returncode != 0
    errors = " ".join(json.loads(completed.stdout)["errors"]).lower()
    assert "target" in errors or "symlink" in errors
    assert _snapshot_tree(vault) == before


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_adopt_gives_an_existing_vault_without_a_company_opinion_the_room_idempotently(
    tmp_path: Path,
) -> None:
    """A vault that never expressed a choice gets Companies, like Career and
    Quarter Goals. It was previously withheld, which no user could explain."""
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text="name: Existing User\ncustom: keep\n",
        companies_default=True,
    )
    profile_path = vault / "System/user-profile.yaml"

    _run_provision(vault, "--adopt")

    first = profile_path.read_text(encoding="utf-8")
    profile = yaml.safe_load(first)
    assert profile["capabilities"]["companies"]["enabled"] is True
    assert capabilities.enabled(
        "companies",
        profile_path=profile_path,
        contract_path=CONTRACT_PATH,
    ) is True
    assert (vault / "05-Areas/Companies").exists()

    _run_provision(vault, "--adopt")

    assert profile_path.read_text(encoding="utf-8") == first


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_lifecycle_only_update_pins_markerless_existing_vault_transactionally(
    tmp_path: Path,
) -> None:
    original = "# keep this comment\nname: Existing User\ncustom: keep\n"
    vault = _prepare_provision_vault(tmp_path, profile_text=original)
    profile_path = vault / "System/user-profile.yaml"

    first_summary = _run_provision(vault, "--adopt", "--lifecycle-only")

    first = profile_path.read_text(encoding="utf-8")
    profile = yaml.safe_load(first)
    assert first.startswith(original)
    assert profile["capabilities"]["career"]["enabled"] is True
    assert profile["capabilities"]["companies"]["enabled"] is True
    assert profile["capabilities"]["quarter_goals"]["enabled"] is True
    assert first_summary["compatibility_pins"] == ["companies"]
    assert first_summary["mutation_receipt"]["executor"] == "lifecycle-service"
    assert first_summary["mutation_receipt"]["lifecycle_transaction_id"]
    transaction_directories = sorted((vault / "System/.dex/tx").iterdir())

    second_summary = _run_provision(vault, "--adopt", "--lifecycle-only")

    assert profile_path.read_text(encoding="utf-8") == first
    assert second_summary["compatibility_pins"] == []
    assert sorted((vault / "System/.dex/tx").iterdir()) == transaction_directories


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_lifecycle_only_dry_run_previews_the_exact_compatibility_pin(
    tmp_path: Path,
) -> None:
    original = "# keep this comment\nname: Existing User\n"
    vault = _prepare_provision_vault(tmp_path, profile_text=original)

    summary = _run_provision(
        vault,
        "--adopt",
        "--lifecycle-only",
        "--dry-run",
    )

    assert (vault / "System/user-profile.yaml").read_text(encoding="utf-8") == original
    assert not (vault / "System/.dex/tx").exists()
    assert summary["compatibility_pins"] == ["companies"]
    assert summary["lifecycle_executor"]["compatibility_states"] == {
        "career": True,
        "companies": True,
        "quarter_goals": True,
    }
    assert summary["mutation_receipt"]["declared_paths"] == [
        "System/user-profile.yaml"
    ]
    assert summary["mutation_receipt"]["lifecycle_transaction_ids"] == []


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_full_adopt_dry_run_uses_the_transaction_previewed_room_states(
    tmp_path: Path,
) -> None:
    original = "name: Existing User\n"
    vault = _prepare_provision_vault(tmp_path, profile_text=original)

    summary = _run_provision(vault, "--adopt", "--dry-run")

    assert (vault / "System/user-profile.yaml").read_text(encoding="utf-8") == original
    assert "05-Areas/Companies" in summary["created"]
    assert "05-Areas/Career" in summary["created"]
    assert "01-Quarter_Goals" in summary["created"]
    assert summary["lifecycle_executor"]["compatibility_states"] == {
        "career": True,
        "companies": True,
        "quarter_goals": True,
    }


def test_compatibility_pin_recovers_before_inspecting_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text="capabilities:\n  companies:\n    enabled: false\n",
    )
    profile_path = vault / "System/user-profile.yaml"
    calls: list[Path] = []

    def recover(root: Path) -> list[dict]:
        calls.append(Path(root))
        profile_path.write_text("name: Rolled Back\n", encoding="utf-8")
        return []

    monkeypatch.setattr(service.Transaction, "resume", staticmethod(recover))

    result = service._pin_missing_companies_default(vault)

    assert calls == [vault]
    assert result["pinned"] is True
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    assert profile["capabilities"]["companies"]["enabled"] is True


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_lifecycle_only_update_adds_only_companies_to_a_partial_capability_map(
    tmp_path: Path,
) -> None:
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text="capabilities:\n  career:\n    enabled: false\n",
    )

    _run_provision(vault, "--adopt", "--lifecycle-only")

    profile = yaml.safe_load(
        (vault / "System/user-profile.yaml").read_text(encoding="utf-8")
    )
    assert profile["capabilities"] == {
        # Companies is added because this vault never said otherwise; the
        # explicit career: false above is a real choice and is preserved.
        "companies": {"enabled": True},
        "career": {"enabled": False},
    }


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("company_enabled", [True, False])
def test_adopt_preserves_an_existing_explicit_company_choice(
    tmp_path: Path,
    company_enabled: bool,
) -> None:
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text=yaml.safe_dump(
            {
                "name": "Existing User",
                "capabilities": {
                    "companies": {
                        "enabled": company_enabled,
                        "custom": "keep",
                    }
                },
            },
            sort_keys=False,
        ),
        companies_default=True,
    )

    _run_provision(vault, "--adopt")

    profile = yaml.safe_load(
        (vault / "System/user-profile.yaml").read_text(encoding="utf-8")
    )
    assert profile["capabilities"]["companies"] == {
        "enabled": company_enabled,
        "custom": "keep",
    }


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.parametrize("company_enabled", [True, False])
def test_lifecycle_only_update_preserves_an_explicit_company_choice(
    tmp_path: Path,
    company_enabled: bool,
) -> None:
    original = (
        "# keep this comment\n"
        "capabilities:\n"
        "  companies:\n"
        f"    enabled: {'true' if company_enabled else 'false'}\n"
        "    custom: keep\n"
    )
    vault = _prepare_provision_vault(tmp_path, profile_text=original)

    summary = _run_provision(vault, "--adopt", "--lifecycle-only")

    assert (vault / "System/user-profile.yaml").read_text(encoding="utf-8") == original
    assert summary["compatibility_pins"] == []


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_adopt_preserves_a_legacy_capability_opinion(tmp_path: Path) -> None:
    vault = _prepare_provision_vault(
        tmp_path,
        profile_text=(
            "name: Existing User\n"
            "quarterly_planning:\n"
            "  enabled: true\n"
            "  q1_start_month: 4\n"
        ),
        companies_default=True,
    )

    _run_provision(vault, "--adopt")

    profile = yaml.safe_load(
        (vault / "System/user-profile.yaml").read_text(encoding="utf-8")
    )
    assert profile["capabilities"]["companies"]["enabled"] is True
    assert profile["capabilities"]["quarter_goals"]["enabled"] is True
    assert profile["quarterly_planning"]["enabled"] is True
    assert profile["quarterly_planning"]["q1_start_month"] == 4
