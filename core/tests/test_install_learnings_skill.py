"""Contract tests for /install-learnings.

Apply is a separate concern from capture. These tests lock that split, the
routing-table pointer, the implemented/dropped status contract, and the
ban on fabricating edits or deleting entries.
"""

from pathlib import Path

import pytest

from core.utils.validators import validate_skill_frontmatter

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".claude/skills/install-learnings/SKILL.md"
EVALS = ROOT / ".claude/skills/install-learnings/evals/trigger-cases.yaml"
ROUTING = ROOT / ".claude/reference/session-learnings-routing.md"


def _frontmatter_description() -> str:
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    fm = text.split("---\n", 2)[1]
    for line in fm.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("no description in frontmatter")


def test_skill_exists_with_evals_and_valid_frontmatter() -> None:
    assert SKILL.is_file()
    assert EVALS.is_file()
    assert ROUTING.is_file()
    assert validate_skill_frontmatter(SKILL) == []


def test_description_routes_apply_not_capture() -> None:
    desc = _frontmatter_description().lower()
    assert "when the user says" in desc
    assert "daily-review" in desc
    assert "dex-backlog" in desc
    assert "capturing a new learning" in desc


def test_body_keeps_capture_and_apply_separate() -> None:
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "do not extract new learnings" in text
    assert "daily-review" in text
    assert "session-learnings-routing.md" in text


def test_status_contract_and_no_silent_deletes() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "implemented (YYYY-MM-DD — where)" in text
    assert "dropped (YYYY-MM-DD — reason)" in text
    assert "Never delete" in text or "never delete" in text
    assert "Never fabricate" in text or "never fabricate" in text


def test_inspects_destination_before_claiming_implemented() -> None:
    text = SKILL.read_text(encoding="utf-8").lower()
    assert "read that file back" in text or "read the destination file back" in text
    assert "do not mark implemented" in text


def test_capture_flows_do_not_install_and_review_hands_off() -> None:
    daily = (ROOT / ".claude/skills/daily-review/SKILL.md").read_text(encoding="utf-8")
    whats_new = (ROOT / ".claude/skills/dex-whats-new/SKILL.md").read_text(encoding="utf-8")
    assert "Capture only" in daily or "capture only" in daily.lower()
    assert "/install-learnings" in daily
    assert "Reviewing here does not install" in whats_new or "does not install" in whats_new
    assert "/install-learnings" in whats_new


@pytest.mark.parametrize(
    "needle",
    ["positive:", "negative:", "ambiguous:", "missing_prerequisite:", "failure_recovery:"],
)
def test_evals_carry_the_canonical_case_buckets(needle: str) -> None:
    text = EVALS.read_text(encoding="utf-8")
    assert needle in text
    assert "daily-review" in text
    assert "dex-backlog" in text
