# Session Learnings

System improvements discovered during work sessions.

## What Goes Here

Meta-feedback about Dex itself, captured during `/daily-review`:

- **Mistakes or corrections** — Things that went wrong and how to fix them
- **Preferences mentioned** — Workflow preferences you shared
- **Documentation gaps** — Places where docs were unclear or missing
- **Workflow inefficiencies** — Friction points discovered

## Format

Each learning includes:
- **What happened** — Specific situation
- **Why it matters** — Impact on system/workflow
- **Suggested fix** — Specific action with file paths
- **Status** — `pending`, `implemented (YYYY-MM-DD — where)`, or `dropped (YYYY-MM-DD — reason)`

## Naming Convention

`YYYY-MM-DD.md` (one file per day)

## Workflow

1. **Capture** — Happens during `/daily-review`. Entries are written `pending`. Session-end only logs that a session finished.
2. **Review** — `/dex-whats-new --learnings` summarises patterns. Reviewing does not install.
3. **Install** — `/install-learnings` routes pending entries into the file that changes next-session behaviour, or marks them `dropped` with a reason. A Stop hook asks for this pass when 8+ pending entries have sat at least 14 days. Routing table: `.claude/reference/session-learnings-routing.md`.
4. **Do not delete** an obsolete entry to hide it. Use `dropped`.

## vs. Dex Backlog

**Session Learnings** = specific bugs or doc gaps discovered
**Dex Backlog** = feature ideas and improvements (in `System/Dex_Backlog.md`)

Both feed into system improvements, but learnings are reactive (fixing issues) while the backlog is proactive (new capabilities). A learning that is not small and safe to fix becomes a backlog idea rather than a silent skip.

## Integration

- `/daily-review` captures (status stays `pending`)
- `/dex-whats-new` reviews
- `/install-learnings` installs or honestly drops
- Weekly reviews can offer `/install-learnings` when the unused pile is large

This enables Dex to learn from your usage and improve over time.
