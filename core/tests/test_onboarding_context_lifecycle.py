"""Lifecycle-owned persistence for confirmed onboarding context."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.lifecycle import service
from core.transaction.engine import PlanRejected


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    system = vault / "System"
    system.mkdir(parents=True)
    (system / "user-profile.yaml").write_text(
        yaml.safe_dump({"name": "Example User", "calendar": {"work_calendar": "Old"}}, sort_keys=False),
        encoding="utf-8",
    )
    return vault


def test_confirmed_onboarding_context_is_previewed_then_transactionally_applied(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    profile = vault / "System" / "user-profile.yaml"
    original = profile.read_text(encoding="utf-8")

    previewed = service.build_and_preview_onboarding_context(
        vault,
        working_context={"role_focus": "Lead product work", "key_people": []},
        calendar_source={"provider": "apple", "work_calendar": "Work"},
    )

    assert profile.read_text(encoding="utf-8") == original
    assert previewed["preview"]["working_context"] == {
        "role_focus": "Lead product work",
        "key_people": [],
    }
    assert previewed["preview"]["calendar_source"] == {
        "provider": "apple",
        "work_calendar": "Work",
    }

    executed = service.execute_approved_onboarding_context(
        vault,
        previewed["preview"],
        previewed["approval_token"],
    )

    saved = yaml.safe_load(profile.read_text(encoding="utf-8"))
    assert saved["working_context"] == previewed["preview"]["working_context"]
    assert saved["calendar"] == previewed["preview"]["calendar_source"]
    assert executed["receipt"]["purpose"] == "onboarding-context"


def test_confirmed_onboarding_context_refuses_google_calendar(tmp_path: Path) -> None:
    vault = _vault(tmp_path)

    with pytest.raises(PlanRejected, match="Apple Calendar or no calendar"):
        service.build_and_preview_onboarding_context(
            vault,
            working_context={"role_focus": "Lead product work", "key_people": []},
            calendar_source={"provider": "google", "calendar_id": "primary"},
        )
