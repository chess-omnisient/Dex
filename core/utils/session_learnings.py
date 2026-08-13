"""Pending session-learning detection and the install-threshold policy.

Capture stays elsewhere (`/daily-review`, session-end). This module only
answers: which entries are still pending, and has the unused pile crossed
the install threshold?

Shipped defaults (documented in `.claude/reference/session-learnings-routing.md`):

- Volume: at least ``MIN_PENDING_COUNT`` pending entries.
- Age floor: the oldest pending entry is at least ``MIN_OLDEST_AGE_DAYS`` days
  old. Empty and new vaults stay silent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

MIN_PENDING_COUNT = 8
MIN_OLDEST_AGE_DAYS = 14
ROUTING_DOC_RELATIVE = ".claude/reference/session-learnings-routing.md"
ONBOARDING_MARKER = Path("System") / ".onboarding-complete"
LEARNINGS_DIR = Path("System") / "Session_Learnings"

STATUS_PENDING = "pending"
STATUS_IMPLEMENTED = "implemented"
STATUS_DROPPED = "dropped"

_DATE_STEM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_STATUS_LINE = re.compile(
    r"^\*\*Status:\*\*\s*"
    r"(pending|implemented|dropped|won't-fix|wont-fix|archived|resolved)"
    r"(?P<detail>\s+.*)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_HEADING = re.compile(r"^##\s+(?:\[\d{2}:\d{2}\]\s*-?\s*|\d{2}:\d{2}\s+-\s+)?(.+)$", re.MULTILINE)
_FIELD = re.compile(
    r"\*\*(What happened|Why it matters|Suggested fix):\*\*\s*(.+?)"
    r"(?=\n\*\*|\n---|\Z)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class LearningEntry:
    """One session-learning block with a status line."""

    date: str
    title: str
    what_happened: str
    why_it_matters: str
    suggested_fix: str
    status: str
    status_detail: str
    path: Path

    @property
    def is_pending(self) -> bool:
        return self.status == STATUS_PENDING

    def as_synthesis_dict(self) -> dict[str, str]:
        """Shape consumed by Improvements MCP ``synthesize_learnings``."""
        return {
            "date": self.date,
            "title": self.title,
            "what_happened": self.what_happened,
            "why_it_matters": self.why_it_matters,
            "suggested_fix": self.suggested_fix,
            "file": str(self.path),
        }


@dataclass(frozen=True)
class BacklogStats:
    """Install-threshold view of the pending pile. Contains no entry text."""

    pending_count: int
    oldest_pending_date: str | None
    oldest_age_days: int | None
    should_prompt_install: bool


def learnings_dir(vault: Path) -> Path:
    return vault / LEARNINGS_DIR


def parse_entries(vault: Path) -> list[LearningEntry]:
    """Parse dated session-learning files. Missing directories yield []."""
    directory = learnings_dir(vault)
    if not directory.is_dir():
        return []

    entries: list[LearningEntry] = []
    for path in sorted(directory.glob("*.md")):
        stem = path.stem
        if not _DATE_STEM.fullmatch(stem):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for block in re.split(r"\n---\n", content):
            entry = _parse_block(path, stem, block)
            if entry is not None:
                entries.append(entry)
    return entries


def pending_entries(
    entries: list[LearningEntry], *, since_date: str | None = None
) -> list[LearningEntry]:
    pending = [entry for entry in entries if entry.is_pending]
    if since_date:
        pending = [entry for entry in pending if entry.date >= since_date]
    return pending


def backlog_stats(
    entries: list[LearningEntry],
    *,
    today: date | None = None,
    onboarded: bool = True,
) -> BacklogStats:
    """Compute the install prompt from already-parsed entries."""
    if not onboarded:
        return BacklogStats(0, None, None, False)

    pending = pending_entries(entries)
    if not pending:
        return BacklogStats(0, None, None, False)

    today = today or date.today()
    oldest = min(pending, key=lambda entry: entry.date)
    oldest_day = _parse_iso_date(oldest.date)
    if oldest_day is None:
        return BacklogStats(len(pending), oldest.date, None, False)

    age_days = (today - oldest_day).days
    should_prompt = (
        len(pending) >= MIN_PENDING_COUNT and age_days >= MIN_OLDEST_AGE_DAYS
    )
    return BacklogStats(len(pending), oldest.date, age_days, should_prompt)


def install_prompt_stats(vault: Path, *, today: date | None = None) -> BacklogStats:
    """Full vault check used by the Stop hook. Silent before onboarding."""
    onboarded = (vault / ONBOARDING_MARKER).is_file()
    if not onboarded:
        return BacklogStats(0, None, None, False)
    return backlog_stats(parse_entries(vault), today=today, onboarded=True)


def render_status(kind: str, when: date, detail: str) -> str:
    """Lock the status line the skill writes after a routing decision."""
    normalized = kind.strip().casefold()
    if normalized not in {STATUS_IMPLEMENTED, STATUS_DROPPED}:
        raise ValueError("status kind must be implemented or dropped")
    cleaned = " ".join(detail.split())
    if not cleaned:
        raise ValueError("status detail is required")
    return f"{normalized} ({when.isoformat()} — {cleaned})"


def _parse_block(path: Path, file_date: str, block: str) -> LearningEntry | None:
    status_match = _STATUS_LINE.search(block)
    if status_match is None:
        return None

    status = status_match.group(1).casefold()
    if status in {"won't-fix", "wont-fix", "archived", "resolved"}:
        # Legacy terminal labels: not pending, not rewritten here.
        pass
    detail = (status_match.group("detail") or "").strip()

    heading = _HEADING.search(block)
    if heading is None:
        return None
    title = heading.group(1).strip()
    if not title:
        return None

    fields = {
        match.group(1).casefold(): match.group(2).strip()
        for match in _FIELD.finditer(block)
    }
    return LearningEntry(
        date=file_date,
        title=title,
        what_happened=fields.get("what happened", ""),
        why_it_matters=fields.get("why it matters", ""),
        suggested_fix=fields.get("suggested fix", ""),
        status=status,
        status_detail=detail,
        path=path,
    )


def _parse_iso_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
