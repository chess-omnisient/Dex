"""Targeted evidence, authority, and recovery checks for mature Wave 3 skills.

These skills already contain substantial role methods. The Wave 3 bar therefore
checks their known truth and safety gaps rather than rewarding a mechanical rewrite
or a file-size threshold. Like the deeper role contract, this is supporting evidence.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

MATURE_SKILLS = {
    "account-plan": ".claude/skills/_available/sales/account-plan/SKILL.md",
    "call-prep": ".claude/skills/_available/sales/call-prep/SKILL.md",
    "deal-review": ".claude/skills/_available/sales/deal-review/SKILL.md",
    "pipeline-health": ".claude/skills/_available/sales/pipeline-health/SKILL.md",
    "pipeline-sync": ".claude/skills/pipeline-sync/SKILL.md",
    "customer-intel": ".claude/skills/_available/product/customer-intel/SKILL.md",
    "feature-decision": ".claude/skills/_available/product/feature-decision/SKILL.md",
    "roadmap": ".claude/skills/_available/product/roadmap/SKILL.md",
    "career-setup": ".claude/skills/_available/capabilities/career/skills/career-setup/SKILL.md",
    "career-coach": ".claude/skills/_available/capabilities/career/skills/career-coach/SKILL.md",
    "resume-builder": ".claude/skills/_available/capabilities/career/skills/resume-builder/SKILL.md",
    "quarter-plan": ".claude/skills/_available/capabilities/quarter_goals/skills/quarter-plan/SKILL.md",
    "quarter-review": ".claude/skills/_available/capabilities/quarter_goals/skills/quarter-review/SKILL.md",
}

AMENDMENT_HEADING = "## Evidence, authority, and recovery"

ROLE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "account-plan": (
        r"per-field provenance|field provenance",
        r"unknown.*do not infer|do not infer.*unknown",
        r"write preview|preview the exact",
        r"read back.*saved plan|saved plan.*read back",
    ),
    "call-prep": (
        r"freshness.*as-of|as-of.*freshness",
        r"unknown objective.*unknown objection|unknown objection.*unknown objective",
        r"invented intent|do not infer intent",
        r"read-only",
    ),
    "deal-review": (
        r"canonical activity date",
        r"unchecked deal",
        r"unknown value.*exclude|exclude.*unknown value",
        r"denominator.*coverage|coverage.*denominator",
    ),
    "pipeline-health": (
        r"configured.*confirmed.*stage|confirmed.*configured.*stage",
        r"missing.*zero|zero.*missing",
        r"benchmark.*source|source.*benchmark",
        r"denominator.*arithmetic|arithmetic.*denominator",
    ),
    "pipeline-sync": (
        r"companion.*prerequisite|prerequisite.*companion",
        r"partial read|incomplete read",
        r"idempot.*retry|retry.*idempot",
        r"read back.*reconcil|reconcil.*read back",
    ),
    "customer-intel": (
        r"source id.*source date|source date.*source id",
        r"deduplicat",
        r"quote fidelity|exact quote",
        r"insufficient evidence",
    ),
    "feature-decision": (
        r"recommendation.*decision authority|decision authority.*recommendation",
        r"unknown effort.*unknown evidence|unknown evidence.*unknown effort",
        r"preview.*confirm|confirm.*preview",
        r"preserve.*earlier decision|earlier decision.*preserve",
    ),
    "roadmap": (
        r"canonical status.*status date|status date.*canonical status",
        r"unknown.*blocked|blocked.*unknown",
        r"denominator",
        r"source.*evidence|evidence.*source",
    ),
    "career-setup": (
        r"05-areas/career/evidence",
        r"consent.*sensitive|sensitive.*consent",
        r"hook failure|capture failure",
        r"room.*mcp.*verif|mcp.*room.*verif",
    ),
    "career-coach": (
        r"missing evidence.*missing competency|missing competency.*missing evidence",
        r"confidence.*source|source.*confidence",
        r"hr.*manager.*limit|manager.*hr.*limit",
        r"save preview.*confirm|confirm.*save preview",
    ),
    "resume-builder": (
        r"invented metric|do not invent metrics",
        r"supplied estimate|estimate label",
        r"render.*pagination|pagination.*render",
        r"cross-file.*confirm|confirm.*cross-file",
    ),
    "quarter-plan": (
        r"fiscal.*quarter boundar|quarter boundar.*fiscal",
        r"preview every.*mutation|mutation.*preview every",
        r"preserve.*conflict.*bytes|conflict.*preserve.*bytes",
        r"read back",
    ),
    "quarter-review": (
        r"source every statistic|statistic source",
        r"unknown",
        r"separate.*consent.*mutation|consent.*separate.*mutation",
        r"idempotent.*completion percentage|completion percentage.*idempotent",
    ),
}


def mature_skill_amendment_errors(skill_id: str, text: str) -> list[str]:
    lowered = text.lower()
    errors = []
    if AMENDMENT_HEADING not in text:
        errors.append(f"missing heading {AMENDMENT_HEADING!r}")
    common = {
        "provenance": ("source", "date", "as-of"),
        "uncertainty": ("unknown", "contradict"),
        "honesty": ("never invent",),
        "controlled change": ("preview", "confirm", "human"),
        "verification": ("read back", "fail"),
    }
    for label, terms in common.items():
        missing = [term for term in terms if term not in lowered]
        if missing:
            errors.append(f"{label} is incomplete; missing {', '.join(missing)}")
    for pattern in ROLE_REQUIREMENTS[skill_id]:
        if re.search(pattern, lowered, re.DOTALL) is None:
            errors.append(f"known role gap remains; expected /{pattern}/")

    if skill_id == "career-setup" and "06-resources/career_evidence" in lowered:
        errors.append("contradictory legacy career evidence path remains")
    if skill_id == "resume-builder" and re.search(r"</?thinking>", text, re.I):
        errors.append("reasoning-tag exposure remains")
    return errors


@pytest.mark.parametrize("skill_id", tuple(MATURE_SKILLS))
def test_mature_wave3_skill_closes_its_known_evidence_and_depth_gaps(
    skill_id: str,
) -> None:
    text = (REPO_ROOT / MATURE_SKILLS[skill_id]).read_text(encoding="utf-8")
    errors = mature_skill_amendment_errors(skill_id, text)

    assert not errors, f"{skill_id} Wave 3 amendment gaps:\n- " + "\n- ".join(errors)


def test_mature_skill_gate_detects_loss_of_a_known_method() -> None:
    skill_id = "pipeline-health"
    text = (REPO_ROOT / MATURE_SKILLS[skill_id]).read_text(encoding="utf-8")
    assert not mature_skill_amendment_errors(skill_id, text), "positive control must pass"

    mutated = re.sub(r"(?i)denominator", "sample", text)
    assert mutated != text
    errors = mature_skill_amendment_errors(skill_id, mutated)
    assert any("denominator" in error for error in errors)
