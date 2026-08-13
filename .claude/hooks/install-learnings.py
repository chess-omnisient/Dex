#!/usr/bin/env python3
"""Stop hook: force one install pass when unused session learnings pile up.

Capture stays in `/daily-review` and session-end. This hook never writes a learning.
When the pending pile crosses the shipped volume+age threshold, it blocks Stop
once per UTC day so the model routes existing entries (or honestly drops them)
instead of only archiving them.

Fail-open: invalid stdin, missing Python deps, unwritable vault, or a missing
interpreter all exit 0 with no output. Unwritable dedup degrades to silence,
never to a nag on every Stop.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_HOOK_REPO = Path(__file__).resolve().parents[2]


def _vault_root() -> Path:
    configured = os.environ.get("CLAUDE_PROJECT_DIR")
    if configured:
        return Path(configured)
    return _HOOK_REPO


def _dedup_path(vault: Path) -> Path:
    override = os.environ.get("DEX_INSTALL_LEARNINGS_DEDUP_FILE")
    if override:
        return Path(override)
    return vault / "System" / ".dex" / "install-learnings-dedup"


def _today() -> date:
    override = os.environ.get("DEX_INSTALL_LEARNINGS_TODAY")
    if override:
        return datetime.strptime(override, "%Y-%m-%d").date()
    return datetime.now(timezone.utc).date()


def _claim_today(vault: Path, today: date) -> bool:
    """Return True only after today's prompt marker is known to persist."""
    path = _dedup_path(vault)
    marker = f"prompted:{today.isoformat()}"
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if marker in existing.splitlines():
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(marker + "\n")
        persisted = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return marker in persisted.splitlines()


def _reason(pending_count: int, oldest_age_days: int) -> str:
    return (
        "<install_learnings>\n"
        f"Pending session learnings crossed the install threshold: "
        f"{pending_count} unused, oldest {oldest_age_days} days.\n"
        "\n"
        "Capture and apply stay separate — do not extract new learnings in this pass.\n"
        "Read `.claude/skills/install-learnings/SKILL.md` and "
        "`.claude/reference/session-learnings-routing.md`, then follow that contract:\n"
        "1. Cluster related pending entries; prefer one rule covering several.\n"
        "2. Route each cluster into the file that changes next-session behaviour, "
        "or mark dropped with the date and reason.\n"
        "3. Never fabricate an edit to make the count drop. Never delete an entry "
        "to hide it.\n"
        "4. After routing, read the changed files back, then stop.\n"
        "Do this once (typically 1–4 clusters), then stop. If the last user message "
        "was clearly mid-task, still route one highest-value cluster, then stop.\n"
        "</install_learnings>\n"
    )


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            return 0
        if payload.get("stop_hook_active") is True:
            return 0

        vault = _vault_root()
        if str(_HOOK_REPO) not in sys.path:
            sys.path.insert(0, str(_HOOK_REPO))
        from core.utils.session_learnings import install_prompt_stats

        today = _today()
        stats = install_prompt_stats(vault, today=today)
        if not stats.should_prompt_install:
            return 0
        if stats.oldest_age_days is None:
            return 0
        if not _claim_today(vault, today):
            return 0

        output = {
            "decision": "block",
            "reason": _reason(stats.pending_count, stats.oldest_age_days),
        }
        print(json.dumps(output))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
