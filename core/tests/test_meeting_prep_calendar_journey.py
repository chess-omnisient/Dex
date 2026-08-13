"""Journey contract for calendar-first meeting preparation.

The meeting-prep surface is an instruction workflow rather than Python code, so
this test evaluates the two prompts that execute the journey together.  A
presence-only check can stay green while the inline skill reads a rich calendar
record and then hands only display names to its gathering agent.  This contract
pins the information flow across that boundary.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / ".claude/skills/meeting-prep/SKILL.md"
AGENT_PATH = REPO_ROOT / ".claude/skills/meeting-prep/AGENT_INSTRUCTIONS.md"


def _section(body: str, start: str, end: str) -> str:
    return body.split(start, 1)[1].split(end, 1)[0]


def _assert_calendar_invite_journey(skill: str, agent: str) -> None:
    arguments = _section(skill, "## Arguments", "## What This Does")
    calendar_step = _section(skill, "### Step 0:", "### Step 1:")
    delegation = _section(
        skill,
        "### Delegated gathering (large-vault scaling)",
        "Prepare for an upcoming meeting",
    )
    agent_lookup = _section(agent, "### 1.2 Attendee Lookup", "### 1.3 Related Projects")

    # Default journey: calendar first, across the user's calendars, then ask
    # only when the returned status or matching result requires a fallback.
    assert "calendar before prompting" in arguments
    assert 'calendar_name="all"' in calendar_step
    assert calendar_step.index("calendar_get_events_with_attendees") < calendar_step.index(
        "**Ask when the calendar cannot answer.**"
    )
    for state in ("feature_status", "broken", "permission", "user_message"):
        assert state in calendar_step

    # The inline phase filters a mixed invite before delegation.
    for field in ("person_page", "email", "status", "type", "is_current_user"):
        assert field in calendar_step
        assert field in delegation
        assert field in agent
    for excluded in (
        "is_current_user",
        "Room",
        "Resource",
        "Group",
        "Declined",
        "Delegated",
    ):
        assert excluded in calendar_step

    # The cross-context seam is structured records, not a comma-separated
    # display-name placeholder.  Resolved pages win; email/name lookup is only
    # a fallback for records without one.
    assert "{{ATTENDEE_RECORDS}}" in delegation
    assert "{{ATTENDEE_RECORDS}}" in agent
    assert "{{ATTENDEES}}" not in delegation
    assert "{{ATTENDEES}}" not in agent
    assert agent_lookup.index("person_page") < agent_lookup.index("lookup_person")
    assert "only when `person_page` is empty" in agent_lookup


def test_calendar_invite_drives_structured_attendee_research_journey() -> None:
    """A real invite remains authoritative through delegated research.

    The representative invite contains the user, a room, a group, a declined
    guest, and two attending people.  The workflow must describe filtering the
    first four and must carry the attending people's resolved identity fields
    into the gathering prompt instead of reducing them back to names.
    """

    _assert_calendar_invite_journey(
        SKILL_PATH.read_text(encoding="utf-8"),
        AGENT_PATH.read_text(encoding="utf-8"),
    )
