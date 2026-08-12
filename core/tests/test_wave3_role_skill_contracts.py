"""Instruction-contract evidence for the Wave 3 role-pack skills.

These checks prove that each shipped instruction contains a complete, role-specific
method and honest safety boundaries. They are supporting evidence only: they do not
pretend to execute the user's workflow or earn a ``verified`` Lens evidence level.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

ROLE_SKILLS = {
    "audience-intel": ".claude/skills/_available/marketing/audience-intel/SKILL.md",
    "campaign-review": ".claude/skills/_available/marketing/campaign-review/SKILL.md",
    "content-calendar": ".claude/skills/_available/marketing/content-calendar/SKILL.md",
    "messaging-audit": ".claude/skills/_available/marketing/messaging-audit/SKILL.md",
    "architecture-decision": ".claude/skills/_available/engineering/architecture-decision/SKILL.md",
    "incident-review": ".claude/skills/_available/engineering/incident-review/SKILL.md",
    "tech-debt": ".claude/skills/_available/engineering/tech-debt/SKILL.md",
    "board-prep": ".claude/skills/_available/finance/board-prep/SKILL.md",
    "close-status": ".claude/skills/_available/finance/close-status/SKILL.md",
    "variance-analysis": ".claude/skills/_available/finance/variance-analysis/SKILL.md",
    "expansion-opportunities": ".claude/skills/_available/customer-success/expansion-opportunities/SKILL.md",
    "health-score": ".claude/skills/_available/customer-success/health-score/SKILL.md",
    "renewal-prep": ".claude/skills/_available/customer-success/renewal-prep/SKILL.md",
    "metrics-review": ".claude/skills/_available/operations/metrics-review/SKILL.md",
    "process-audit": ".claude/skills/_available/operations/process-audit/SKILL.md",
    "design-review": ".claude/skills/_available/design/design-review/SKILL.md",
    "design-system-audit": ".claude/skills/_available/design/design-system-audit/SKILL.md",
}

REQUIRED_HEADINGS = (
    "## When to use",
    "## Inputs and source discipline",
    "## Method",
    "## Truth and uncertainty rules",
    "## Output contract",
    "## Safety and write boundaries",
    "## Verification and recovery",
)

# Each tuple is one required idea. Alternatives inside a tuple are accepted, but
# every idea must be present. This keeps the gate qualitative and role-specific
# rather than using a misleading word- or byte-count threshold.
METHOD_REQUIREMENTS: dict[str, tuple[tuple[str, ...], ...]] = {
    "audience-intel": (
        ("time-box", "time window"),
        ("deduplicat",),
        ("quote", "source", "date"),
        ("persona", "observed", "inferred"),
    ),
    "campaign-review": (
        ("baseline",),
        ("target", "actual"),
        ("attribution",),
        ("correlation", "causation"),
    ),
    "content-calendar": (
        ("timezone",),
        ("committed", "idea"),
        ("collision", "duplicate"),
        ("undated",),
    ),
    "messaging-audit": (
        ("canonical", "baseline"),
        ("source", "date", "matrix"),
        ("intentional variation",),
        ("unsupported claim",),
    ),
    "architecture-decision": (
        ("proposed", "accepted", "superseded"),
        ("decision authority", "human decision"),
        ("alternatives", "trade-off"),
        ("adr", "immutable", "history"),
    ),
    "incident-review": (
        ("timezone", "timeline"),
        ("fact", "hypothes"),
        ("blameless",),
        ("prevention", "evidence"),
    ),
    "tech-debt": (
        ("deduplicat",),
        ("first-seen", "first seen"),
        ("impact", "effort", "confidence"),
        ("security", "escalat"),
    ),
    "board-prep": (
        ("as-of", "as of"),
        ("currency", "unit"),
        ("reconcil", "actual"),
        ("draft for human review",),
    ),
    "close-status": (
        ("authoritative checklist",),
        ("counted", "denominator"),
        ("blocked", "unknown", "not started"),
        ("critical path", "dependency"),
    ),
    "variance-analysis": (
        ("formula", "sign"),
        ("materiality",),
        ("reconcil", "total"),
        ("timing", "permanent", "hypothes"),
    ),
    "expansion-opportunities": (
        ("expressed need",),
        ("fit", "speculation"),
        ("potential value", "invent"),
        ("crm", "outreach", "commercial"),
    ),
    "health-score": (
        ("configured scoring rubric",),
        ("dated", "freshness"),
        ("unknown", "not scored"),
        ("silence", "churn"),
    ),
    "renewal-prep": (
        ("contract", "arr", "renewal"),
        ("dated outcome",),
        ("risk", "unknown"),
        ("pricing", "customer communication", "human"),
    ),
    "metrics-review": (
        ("metric definition",),
        ("unit", "time window", "source"),
        ("baseline", "target"),
        ("anomal", "validation"),
    ),
    "process-audit": (
        ("start", "end", "owner"),
        ("sample", "observation"),
        ("bottleneck", "queue", "handoff"),
        ("experiment", "success measure"),
    ),
    "design-review": (
        ("review mode", "prepare", "document"),
        ("artifact", "version"),
        ("requirement", "evidence"),
        ("recommendation", "decision"),
    ),
    "design-system-audit": (
        ("canonical component", "canonical token"),
        ("sample", "coverage"),
        ("adoption", "denominator"),
        ("exception", "intentional"),
    ),
}


def _frontmatter_description(text: str) -> str:
    match = re.search(r"(?m)^description:\s*(.+)$", text)
    return match.group(1).strip().strip('"') if match else ""


def role_skill_contract_errors(skill_id: str, text: str) -> list[str]:
    """Return every evidence-and-depth contract failure for one role skill."""
    lowered = text.lower()
    errors: list[str] = []

    if not _frontmatter_description(text).lower().startswith("use when "):
        errors.append("frontmatter description must route with 'Use when ...'")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading {heading!r}")

    common_ideas = {
        "anti-trigger": ("do not use", "not for"),
        "source provenance": ("source", "date", "as-of"),
        "truth states": ("observed", "inferred", "unknown", "stale", "contradict"),
        "read-only default": ("read-only",),
        "controlled writes": ("preview", "confirm", "human"),
        "output uncertainty": ("confidence", "unknown", "contradiction"),
        "verification": ("read back", "reconcile", "fail"),
    }
    for label, terms in common_ideas.items():
        missing = [term for term in terms if term not in lowered]
        if missing:
            errors.append(f"{label} is incomplete; missing {', '.join(missing)}")

    for alternatives in METHOD_REQUIREMENTS[skill_id]:
        if not any(term in lowered for term in alternatives):
            errors.append("role method is incomplete; expected one of " + ", ".join(alternatives))

    return errors


@pytest.mark.parametrize("skill_id", tuple(ROLE_SKILLS))
def test_wave3_role_skill_meets_evidence_and_depth_contract(skill_id: str) -> None:
    path = REPO_ROOT / ROLE_SKILLS[skill_id]
    text = path.read_text(encoding="utf-8")

    assert not role_skill_contract_errors(skill_id, text), (
        f"{skill_id} does not meet the Wave 3 evidence-and-depth contract:\n- "
        + "\n- ".join(role_skill_contract_errors(skill_id, text))
    )


def test_role_specific_method_gate_fails_on_deliberate_mutation() -> None:
    """Prove the gate notices loss of method, not just headings or file presence."""
    skill_id = "audience-intel"
    text = (REPO_ROOT / ROLE_SKILLS[skill_id]).read_text(encoding="utf-8")
    assert not role_skill_contract_errors(skill_id, text), "positive control must pass"

    mutated = re.sub(r"(?i)deduplicat(?:e|es|ed|ing|ion)", "combine", text)
    assert mutated != text, "fixture must contain the role-specific deduplication method"

    errors = role_skill_contract_errors(skill_id, mutated)
    assert any("deduplicat" in error for error in errors)
