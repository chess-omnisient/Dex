#!/usr/bin/env python3
"""Once-daily session-start sweep for /feedback report news.

Checks heydex.ai for status changes and questions on the feedback reports this
vault has filed, and surfaces them once at session start. Design rules
(contract: docs/feedback-loop-contract.md):

- Zero cost for non-reporters: exits immediately unless claim-ticket files
  exist under System/.dex/feedback/ and a terminal connection is linked.
- Bounded and once daily: the day is claimed before any network work
  (update-verifier pattern), one GET with a short timeout, never retries.
- Pull only: nothing on the server can reach into this machine; this script
  asks, the server answers.
- Never noisy, never fatal: any failure is silent and exits 0. A notice is
  emitted at most once per (ticket, status change).
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

HEYDEX_API_BASE_URL = "https://gallant-reindeer-229.eu-west-1.convex.site"
HTTP_TIMEOUT_SECONDS = 8
AUTH_MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000
TICKET_PATTERN = re.compile(r"^DEX-\d{1,10}$")

ACTIONABLE_STATUSES = {"fixed", "wont_fix", "needs_info"}


def _api_base() -> str:
    return (os.environ.get("DEX_FEEDBACK_API_BASE") or HEYDEX_API_BASE_URL).rstrip("/")


def _auth_token() -> "str | None":
    path = Path.home() / ".dex" / "heydex-auth.json"
    try:
        auth = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    token = str(auth.get("sessionToken") or "").strip()
    timestamp = auth.get("timestamp")
    if not token or not isinstance(timestamp, (int, float)):
        return None
    if int(time.time() * 1000) - int(timestamp) > AUTH_MAX_AGE_MS:
        return None
    return token


def _feedback_dir(vault: Path) -> Path:
    return vault / "System" / ".dex" / "feedback"


def _state_path(vault: Path) -> Path:
    return vault / "System" / ".dex" / "feedback-sweep.json"


def _load_tickets(vault: Path) -> dict:
    tickets = {}
    directory = _feedback_dir(vault)
    if not directory.is_dir():
        return tickets
    for path in sorted(directory.glob("DEX-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ticket = record.get("ticket")
        if isinstance(ticket, str) and TICKET_PATTERN.match(ticket):
            tickets[ticket] = (path, record)
    return tickets


def _claim_today(vault: Path) -> bool:
    """Claim today's attempt before doing any work; True if we own today."""
    state_path = _state_path(vault)
    today = date.today().isoformat()
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    if state.get("last_attempt_date") == today and not os.environ.get("DEX_FEEDBACK_SWEEP_FORCE"):
        return False
    state["last_attempt_date"] = today
    state["last_attempt_at"] = datetime.now(timezone.utc).isoformat()
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        return False
    return True


def _fetch_status(token: str) -> "list | None":
    url = f"{_api_base()}/api/feedback/status"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                return None
            body = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None
    try:
        decoded = json.loads(body)
    except json.JSONDecodeError:
        return None
    reports = decoded.get("reports") if isinstance(decoded, dict) else None
    return reports if isinstance(reports, list) else None


def _short(summary: str, limit: int = 60) -> str:
    flattened = " ".join(str(summary).split())
    return flattened if len(flattened) <= limit else flattened[: limit - 3] + "..."


def _notice_for(report: dict) -> "str | None":
    ticket = report.get("ticket")
    status = report.get("status")
    summary = _short(report.get("summary") or "")
    comment = report.get("comment")
    if status == "fixed":
        version = report.get("fixedInVersion")
        line = f"◆ Good news on a bug you reported. {ticket} — {summary} — is fixed"
        line += f" in v{version}." if version else "."
        if comment:
            line += f'\n  Dave says: "{comment}"'
        line += "\n  Run /dex-update when you're ready."
        return line
    if status == "needs_info" and report.get("question"):
        return (
            f"◆ A question about {ticket} ({summary}):\n"
            f'  "{report["question"]}"\n'
            "  Run /feedback to answer — Dex can gather the answer for you, and you approve it before it goes."
        )
    if status == "wont_fix":
        line = f"◆ An update on {ticket} ({summary}): this one can't be fixed."
        if comment:
            line += f'\n  Dave says: "{comment}"'
        return line
    return None


def sweep(vault: Path) -> "str | None":
    tickets = _load_tickets(vault)
    if not tickets:
        return None
    token = _auth_token()
    if token is None:
        return None
    if not _claim_today(vault):
        return None

    reports = _fetch_status(token)
    if reports is None:
        return None

    notices = []
    for report in reports:
        ticket = report.get("ticket")
        if ticket not in tickets:
            continue
        path, record = tickets[ticket]
        changed_at = report.get("statusChangedAt")
        if not isinstance(changed_at, int):
            continue

        already_notified = record.get("last_notified_status_changed_at")
        is_new = not isinstance(already_notified, int) or changed_at > already_notified

        record["status"] = report.get("status")
        record["status_changed_at"] = changed_at
        for source, target in (
            ("question", "question"),
            ("comment", "comment"),
            ("fixedInVersion", "fixed_in_version"),
        ):
            if report.get(source) is not None:
                record[target] = report[source]

        if is_new and report.get("status") in ACTIONABLE_STATUSES:
            notice = _notice_for(report)
            if notice:
                notices.append(notice)
                record["last_notified_status_changed_at"] = changed_at
        elif is_new:
            # Quiet transitions (e.g. received → investigating) update the
            # local record without a session-start interruption.
            record["last_notified_status_changed_at"] = changed_at

        try:
            path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError:
            continue

    if not notices:
        return None
    return "\n\n".join(notices)


def main(argv: "list[str] | None" = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    vault = None
    session_start = False
    index = 0
    while index < len(args):
        if args[index] == "--vault" and index + 1 < len(args):
            vault = Path(args[index + 1]).expanduser()
            index += 2
            continue
        if args[index] == "--session-start":
            session_start = True
        index += 1

    if vault is None:
        vault = Path(os.environ.get("VAULT_PATH") or os.getcwd())

    try:
        notice = sweep(vault.resolve())
    except Exception:
        return 0

    if notice:
        if session_start:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": f"\n{notice}\n",
                        }
                    }
                )
            )
        else:
            print(notice)
    return 0


if __name__ == "__main__":
    sys.exit(main())
