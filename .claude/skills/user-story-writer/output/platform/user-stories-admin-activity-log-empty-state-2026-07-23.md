# User Stories: Admin — Activity Log (Empty State)

**Area:** Platform
**Source:** ClickUp task [8699phn4f](https://app.clickup.com/t/8699phn4f) — "UXUI | Admin | Activity Log" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Admin module, Activity Log table
- **Target user:** Platform user (admin reviewing account/system activity)
- **PDLC Phase (ClickUp):** Ready for Dev | **Roadmap View:** Backlog | **Priority:** Normal
- **Request Type:** Not set on ticket (treated as Enhancement — aligning an existing table to the X2 design system)
- **Design:** [Figma — Admin, node 0-1](https://www.figma.com/design/hjRmeL4sizajFC17PzpBpN/Admin?node-id=0-1)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Admin API Keys Table story set](user-stories-admin-api-keys-table-2026-07-23.md), [Partner Activity Log Empty State story](user-stories-partner-activity-log-empty-state-2026-07-23.md), [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md), [Upload Activity Status Column story](user-stories-dataset-upload-activity-status-column-2026-07-23.md), and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), all written for sibling tickets under this epic.
- **Downstream dependency:** A separate ticket, ["Table Filter Persistence | Admin | Implement for Activity Log"](https://app.clickup.com/t/8699pzezv), is blocked by this one — filter persistence work on the Admin Activity Log table can't start until this ships. This confirms the table is filterable, which shapes the edge cases below (no logs at all vs. no logs matching an active filter).
- **Sprint/cycle:** Not yet assigned

---

## Story 1: Empty State for Admin Activity Log

**As a** platform user,
**I want to** see a clear X2-styled empty state when the Admin Activity Log has no activity to display,
**So that** I understand there's genuinely nothing to see, rather than assuming the table is broken or still loading.

### INVEST Check
- [x] **Independent** — Standalone UI state; no dependency on other stories in this epic
- [x] **Negotiable** — Copy and illustration are flexible within the X2 empty-state pattern
- [x] **Valuable** — Prevents users from misreading a blank Activity Log as a bug or a stuck load
- [x] **Estimable** — Reuses/extends the platform's existing X2 empty-state component
- [x] **Small** — Single conditional render
- [x] **Testable** — Zero-state condition is explicit

### Acceptance Criteria

**AC1: Empty state shown when there are no activity logs**
Given a user navigates to the Admin Activity Log,
When there are no activity logs to display,
Then the X2 empty state (per Figma node 0-1) is shown in place of the table.
*Source ticket AC1: "An empty state is displayed if there are no activity logs to display."*

**AC2: Table shown when activity logs exist**
Given a user navigates to the Admin Activity Log,
When one or more activity log entries exist,
Then the table renders normally and the empty state is not shown.

**AC3: Empty state is distinct from a loading state**
Given the activity log data has finished loading and returned zero results,
When the empty state renders,
Then it is visually distinct from any loading/skeleton state (no flicker between the two).

### Edge Cases
- **No logs at all vs. no logs matching an active filter** — since a filter-persistence story is already queued for this table, confirm whether "no results for the current filter" should show this same empty state or a distinct "no matches, clear filter" variant (see Open Questions)
- **Data fetch fails (error, not empty)** — ticket only specifies the zero-logs case; an error/failed-fetch state is a separate concern and should not silently reuse this empty state
- **New activity logged while the empty state is showing** — if the platform supports live updates elsewhere, confirm whether the first logged event should replace the empty state without a manual refresh

### Technical Notes
- Confirm whether a shared X2 empty-state component already exists (the sibling Admin API Keys, Partner Activity Log, Reports Table, and Dataset Schemas stories under this same epic likely use one) — reuse rather than building a new one per table
- Sequencing: this story should land before or alongside the "Table Filter Persistence" work on this same table ([8699pzezv](https://app.clickup.com/t/8699pzezv)), since that ticket is explicitly blocked on this one

### Out of Scope
- Table Filter Persistence itself (tracked separately in [8699pzezv](https://app.clickup.com/t/8699pzezv))
- Any redesign of the populated (non-empty) table view
- Error/failed-fetch state handling

---

## Story Dependencies

```
Story 1 (this ticket) ──→ Table Filter Persistence for Admin Activity Log (8699pzezv, separate ticket, blocked on this one)
```

## Suggested Sprint Ordering
1. Story 1 — Admin Activity Log Empty State — unblocks the queued Table Filter Persistence work

---

## Open Questions (flag before sprint-ready)
1. Should "no logs at all" and "no logs matching the current filter" show the same empty state, or does the filter-persistence work require a distinct "no matches" variant?
2. Does an X2 empty-state component already exist from the sibling Admin API Keys / Partner Activity Log / Reports Table stories in this epic, or does each table need its own implementation?
3. Is there an existing pre-X2 empty state on this page today that needs to be replaced, or is this net-new?

## Related Context
- **Source ticket:** [ClickUp 8699phn4f](https://app.clickup.com/t/8699phn4f)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Downstream ticket:** [ClickUp 8699pzezv — "Table Filter Persistence | Admin | Implement for Activity Log"](https://app.clickup.com/t/8699pzezv) (blocked on this story)
- **Sibling story sets (same epic):** [Admin API Keys Table](user-stories-admin-api-keys-table-2026-07-23.md) (2026-07-23), [Partner Activity Log Empty State](user-stories-partner-activity-log-empty-state-2026-07-23.md) (2026-07-23), [Upload Activity Status Column](user-stories-dataset-upload-activity-status-column-2026-07-23.md) (2026-07-23), [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md) (2026-07-23), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21)
- **Design:** [Figma — Admin, node 0-1](https://www.figma.com/design/hjRmeL4sizajFC17PzpBpN/Admin?node-id=0-1)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Admin-area stories
