"""Helpers for whole-profile DexDiff adoption."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from core.paths import DEXDIFF_PROFILE_DRAFTS_DIR, DEX_RUNTIME_DIR, VAULT_ROOT

PROFILE_BUNDLE_CONTRACT_VERSION = "2026-04-10"
PROFILE_ADOPTIONS_DIR = DEX_RUNTIME_DIR / "adoptions" / "profiles"


def normalize_handle(handle: str) -> str:
    normalized = handle.strip()
    if normalized.startswith("@"):
        normalized = normalized[1:]
    if not normalized:
        raise ValueError("Profile handle is required")
    return normalized


def build_profile_bundle_url(base_url: str, handle: str) -> str:
    normalized_handle = normalize_handle(handle)
    return f"{base_url.rstrip('/')}/api/profile-bundle?handle={quote(normalized_handle)}"


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return cleaned or "workflow"


def _relative_to_vault(path: Path) -> str:
    try:
        return str(path.relative_to(VAULT_ROOT))
    except ValueError:
        return str(path)


def validate_profile_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    contract_version = bundle.get("contractVersion")
    if contract_version != PROFILE_BUNDLE_CONTRACT_VERSION:
        raise ValueError(
            f"Unsupported profile bundle contract version: {contract_version!r}"
        )

    profile = bundle.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("Profile bundle is missing profile metadata")

    handle = normalize_handle(str(profile.get("handle", "")))
    workflows = bundle.get("workflows")
    if not isinstance(workflows, list) or len(workflows) == 0:
        raise ValueError("Profile bundle must include at least one workflow")

    normalized_workflows: list[dict[str, Any]] = []
    for workflow in workflows:
        if not isinstance(workflow, dict):
            raise ValueError("Workflow entry must be an object")
        diff_id = str(workflow.get("diffId", "")).strip()
        methodology = str(workflow.get("methodology", "")).strip()
        if not diff_id or not methodology:
            raise ValueError("Each workflow requires diffId and methodology")
        normalized_workflows.append(
            {
                **workflow,
                "diffId": diff_id,
                "methodology": methodology,
            }
        )

    love_letter = bundle.get("loveLetter")
    if love_letter is not None and not isinstance(love_letter, dict):
        raise ValueError("loveLetter must be null or an object")

    return {
        **bundle,
        "profile": {
            **profile,
            "handle": handle,
        },
        "workflows": normalized_workflows,
        "loveLetter": love_letter,
    }


def get_profile_storage_dir(handle: str) -> Path:
    return DEXDIFF_PROFILE_DRAFTS_DIR / "adopted" / normalize_handle(handle)


def write_profile_bundle(bundle: dict[str, Any], source: str) -> dict[str, Any]:
    validated = validate_profile_bundle(bundle)
    handle = validated["profile"]["handle"]

    storage_dir = get_profile_storage_dir(handle)
    workflows_dir = storage_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = storage_dir / "profile-bundle.json"
    manifest_payload = {
        "saved_at": datetime.now(UTC).isoformat(),
        "source": source,
        **validated,
    }
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    workflow_paths: list[Path] = []
    for index, workflow in enumerate(validated["workflows"], start=1):
        file_name = f"{index:02d}-{_slugify(workflow['diffId'])}.yaml"
        workflow_path = workflows_dir / file_name
        workflow_path.write_text(f"{workflow['methodology'].rstrip()}\n", encoding="utf-8")
        workflow_paths.append(workflow_path)

    love_letter_path: Path | None = None
    if validated["loveLetter"] and validated["loveLetter"].get("text"):
        love_letter_path = storage_dir / "love-letter.md"
        love_letter_path.write_text(
            "# Love Letter\n\n" + validated["loveLetter"]["text"].strip() + "\n",
            encoding="utf-8",
        )

    adoption_log_path = write_profile_adoption_log(
        validated,
        source=source,
        manifest_path=manifest_path,
        workflow_paths=workflow_paths,
        love_letter_path=love_letter_path,
    )

    return {
        "storage_dir": storage_dir,
        "manifest_path": manifest_path,
        "workflow_paths": workflow_paths,
        "love_letter_path": love_letter_path,
        "adoption_log_path": adoption_log_path,
    }


def write_profile_adoption_log(
    bundle: dict[str, Any],
    *,
    source: str,
    manifest_path: Path,
    workflow_paths: list[Path],
    love_letter_path: Path | None = None,
) -> Path:
    validated = validate_profile_bundle(bundle)
    handle = validated["profile"]["handle"]

    PROFILE_ADOPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    adoption_path = PROFILE_ADOPTIONS_DIR / f"{_slugify(handle)}.json"
    payload = {
        "profile_handle": handle,
        "profile_display_name": validated["profile"].get("displayName"),
        "adopted_at": datetime.now(UTC).isoformat(),
        "source": source,
        "bundle_contract_version": validated["contractVersion"],
        "manifest_path": _relative_to_vault(manifest_path),
        "workflow_ids": [workflow["diffId"] for workflow in validated["workflows"]],
        "workflow_paths": [_relative_to_vault(path) for path in workflow_paths],
        "love_letter_path": _relative_to_vault(love_letter_path) if love_letter_path else None,
    }
    adoption_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return adoption_path
