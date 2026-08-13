# Session-learnings routing

How a **pending** session learning becomes a change that affects the next
session — or an honest `dropped` with a reason. Capture (`/daily-review`,
session-end, the learning-review reminder) stays a separate concern. This
file is the routing table `/install-learnings` and the Stop hook point at.
Edit the destinations here without touching hook code.

## Shipped trigger defaults

The Stop hook fires when **both** are true:

- **Volume:** 8 pending entries or more
- **Age floor:** the oldest pending entry is at least 14 days old

Empty and new vaults stay silent. A busy first week of captures does not
fire. Three old notes also do not fire — `/install-learnings` can still be
run by hand. A vault that is keeping up never sees the hook.

The hook asks for one routing pass (typically 1–4 clusters), then stops. It
does not try to clear an 80-entry pile in one session.

## Status values

Leave capture as:

```markdown
**Status:** pending
```

After a real routing decision, rewrite that line in place. Do not delete the
entry.

```markdown
**Status:** implemented (YYYY-MM-DD — where it went)
**Status:** dropped (YYYY-MM-DD — reason)
```

`dropped` is the third state for wrong, obsolete, or already-covered notes.
Without it, stale entries either linger forever or get quietly deleted.

Do not fabricate an edit to make the count drop. Do not delete an obsolete
entry to hide it.

## Routing table

Prefer **one rule covering a cluster** of related entries over eight tiny
edits. The clusters are where the value is.

| Kind of learning | Where it has to go |
|---|---|
| Behavioural — how the assistant should work | `CLAUDE.md` user-extensions block (`## USER_EXTENSIONS_START` … `## USER_EXTENSIONS_END`). If the same rule belongs in a standing memory note, add it there too and keep the user-extensions line as the session-visible copy. |
| A defect in a skill | That skill's `SKILL.md`, as a real numbered step — not prose in a "notes" section. |
| A small, safe defect in code or config | Fix it in place. If it is not small and safe, capture it as a backlog idea with `capture_idea` and mark the learning implemented to that idea id, or dropped if it is not an idea either. |
| An environment or platform fact | The matching file in `.claude/reference/` |

Do not put preferences that Claude's built-in memory already owns into
session learnings or user-extensions. See [Memory_Ownership.md](../../docs/Dex_System/Memory_Ownership.md).

## Clustering

1. Read pending entries across `System/Session_Learnings/*.md` (skip `README.md` and session-end markers that have no status).
2. Group by the file that would change next-session behaviour, not by the day they were captured.
3. Write one durable rule per cluster. Mark every covered entry `implemented` pointing at that same destination.
4. Leave unrelated pending entries pending. Another pass will take them.

## Quality bar

A good pass leaves behind a behaviour change the next session will actually
follow, and a status line that says where each routed entry went. A dropped
entry names why. The pending count falls because something was installed or
honestly declined — not because notes were deleted or rewritten as done
without a matching file change.

## Related

- Skill: `/install-learnings` (`.claude/skills/install-learnings/SKILL.md`)
- Capture: `/daily-review`
- Review without applying: `/dex-whats-new --learnings`
- Product ideas (not session-learning routing): `/dex-backlog`
