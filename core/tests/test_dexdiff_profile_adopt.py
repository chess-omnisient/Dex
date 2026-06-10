"""Tests for core/dexdiff_profile_adopt.py."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

dexdiff_profile_adopt = importlib.import_module("core.dexdiff_profile_adopt")


def _configure_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(dexdiff_profile_adopt, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(
        dexdiff_profile_adopt,
        "DEXDIFF_PROFILE_DRAFTS_DIR",
        tmp_path / "04-Projects" / "DexDiff" / "beta" / "profile",
    )
    monkeypatch.setattr(
        dexdiff_profile_adopt,
        "DEX_RUNTIME_DIR",
        tmp_path / "System" / ".dex",
    )
    monkeypatch.setattr(
        dexdiff_profile_adopt,
        "PROFILE_ADOPTIONS_DIR",
        tmp_path / "System" / ".dex" / "adoptions" / "profiles",
    )


def _bundle() -> dict:
    return {
        "contractVersion": "2026-04-10",
        "profile": {
            "handle": "dave",
            "displayName": "Dave Killeen",
            "role": "Field CPO, EMEA",
            "company": "Pendo",
        },
        "workflows": [
            {
                "diffId": "meeting-prep",
                "name": "Meeting Prep",
                "methodology": 'dexdiff_schema: "2.0"\nname: Meeting Prep\n',
            },
            {
                "diffId": "follow-through",
                "name": "Follow Through",
                "methodology": 'dexdiff_schema: "2.0"\nname: Follow Through\n',
            },
        ],
        "loveLetter": {
            "text": "Dex made my work calmer.",
        },
    }


def test_build_profile_bundle_url_trims_at_prefix():
    url = dexdiff_profile_adopt.build_profile_bundle_url("https://heydex.ai/", "@dave")
    assert url == "https://heydex.ai/api/profile-bundle?handle=dave"


def test_validate_profile_bundle_requires_supported_contract_version():
    with pytest.raises(ValueError):
        dexdiff_profile_adopt.validate_profile_bundle(
            {
                "contractVersion": "bad-version",
                "profile": {"handle": "dave"},
                "workflows": [{"diffId": "meeting-prep", "methodology": "x"}],
            }
        )


def test_write_profile_bundle_creates_manifest_workflows_love_letter_and_log(monkeypatch, tmp_path):
    _configure_paths(monkeypatch, tmp_path)

    result = dexdiff_profile_adopt.write_profile_bundle(
        _bundle(),
        source="https://heydex.ai/api/profile-bundle?handle=dave",
    )

    assert result["manifest_path"].is_file()
    assert [path.name for path in result["workflow_paths"]] == [
        "01-meeting-prep.yaml",
        "02-follow-through.yaml",
    ]
    assert result["love_letter_path"].is_file()
    assert result["adoption_log_path"].is_file()

    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["profile"]["handle"] == "dave"
    assert manifest["workflows"][0]["diffId"] == "meeting-prep"

    adoption_log = json.loads(result["adoption_log_path"].read_text(encoding="utf-8"))
    assert adoption_log["profile_handle"] == "dave"
    assert adoption_log["workflow_ids"] == ["meeting-prep", "follow-through"]
    assert adoption_log["manifest_path"] == "04-Projects/DexDiff/beta/profile/adopted/dave/profile-bundle.json"
    assert adoption_log["love_letter_path"] == "04-Projects/DexDiff/beta/profile/adopted/dave/love-letter.md"
