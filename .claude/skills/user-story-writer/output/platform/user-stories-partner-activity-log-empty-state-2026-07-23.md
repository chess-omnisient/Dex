# User Stories: Partner Activity Log — Empty State

**Area:** Platform
**Source:** ClickUp task [8699phn2n](https://app.clickup.com/t/8699phn2n) — "UXUI | Partner Activity" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Connections module, Partner Activity Log table
- **Target user:** Platform user (viewing partner/connection activity)
- **PDLC Phase (ClickUp):** Ready For Dev | **Roadmap View:** Backlog | **Priority:** High
- **Request Type:** Feature Request
- **Design:** [Figma — Connections / Collaboration Environment, node 0-1](https://www.figma.com/design/5Rgt0dM3LuJipGKsEgoveL/Connections---Collaboration-Environment?node-id=0-1) (4 reference screenshots also attached to the source ticket)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Upload Activity Status Column story](user-stories-dataset-upload-activity-status-column-2026-07-23.md), the [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md), and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), all written for sibling tickets under this epic.
- **Downstream dependency:** A separate ticket, ["Table Filter Persistence | Implement for Partner Activity Log"](https://app.clickup.com/t/8699pzeuz), is blocked by this one — filter persistence work on this table can't start until the empty state ships. This confirms the Partner Activity Log is a filterable table, which shapes the empty-state edge cases below (no logs at all vs. no logs matching an active filter).
- **Sprint/cycle:** Not yet assigned (Roadmap View: Backlog, though PDLC Phase is Ready For Dev)

---

## Story 1: Partner Activity Log Empty State

**As a** platform user,
**I want to** see a clear empty state when the Partner Activity Log has no activity to display,
**So that** I understand there's genuinely nothing to see (rather than assuming the table is broken or still loading).

### INVEST Check
- [x] **Independent** — Pure frontend addition to the Partner Activity Log table; no dependency on other stories in this epic
- [x] **Negotiable** — Exact empty-state copy, illustration, and layout are flexible within the Figma spec
- [x] **Valuable** — Prevents users from misreading a blank table as a bug or a stuck load
- [x] **Estimable** — Single conditional render: empty state vs. populated table
- [x] **Small** — One state on one table
- [x] **Testable** — Binary condition (logs present vs. absent) with a deterministic visual outcome

### Acceptance Criteria

**AC1: Empty state shown when there are no logs**
Given a user navigates to the Partner Activity Log,
When there are no activity logs to display,
Then the X2 empty state (per Figma node 0-1) is shown in place of the table.
*Source ticket AC1: "An empty state is displayed if there are no logs to display."*

**AC2: Table shown when logs exist**
Given a user navigates to the Partner Activity Log,
When one or more activity logs exist,
Then the table renders normally and the empty state is not shown.

**AC3: Empty state matches X2 design system**
Given the empty state is displayed,
When a user views it,
Then its layout, copy, and iconography match the X2 empty-state pattern defined in Figma node 0-1 — not the platform's pre-X2 empty state (if one currently exists on this page).

### Edge Cases
- **No logs at all vs. no logs matching an active filter** — since a filter-persistence story is already queued for this table, confirm whether "no results for the current filter" should show this same empty state or a distinct "no matches, clear filter" variant (see Open Questions)
- **Loading state vs. empty state** — confirm the empty state only renders after the data fetch resolves with zero rows, not during the fetch itself (otherwise a slow load could flash the empty state before real data arrives)
- **Log data fails to load (error)** — ticket only specifies the zero-logs case; an error/failed-fetch state is a separate concern and should not silently reuse this empty state

### Technical Notes
- Confirm whether a shared X2 empty-state component already exists (the sibling Reports Table and Upload Activity stories under this same epic likely use one) — reuse rather than building a new one per table
- Sequencing: this story should land before or alongside the "Table Filter Persistence" work on this same table ([8699pzeuz](https://app.clickup.com/t/8699pzeuz)), since that ticket is explicitly blocked on this one

### Out of Scope
- Table Filter Persistence itself (tracked separately in [8699pzeuz](https://app.clickup.com/t/8699pzeuz))
- Any redesign of the populated (non-empty) table view
- Error/failed-fetch state handling

---

## Story Dependencies

```
Story 1 (this ticket) ──→ Table Filter Persistence for Partner Activity Log (8699pzeuz, separate ticket, blocked on this one)
```

## Suggested Sprint Ordering
1. Story 1 — Partner Activity Log Empty State — unblocks the queued Table Filter Persistence work

---

## Open Questions (flag before sprint-ready)
1. Should "no logs at all" and "no logs matching the current filter" show the same empty state, or does the filter-persistence work require a distinct "no matches" variant?
2. Does an X2 empty-state component already exist from the sibling Reports Table / Upload Activity stories in this epic, or does each table need its own implementation?
3. Is there an existing pre-X2 empty state on this page today that needs to be replaced, or is this net-new?

## Related Context
- **Source ticket:** [ClickUp 8699phn2n](https://app.clickup.com/t/8699phn2n)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Downstream ticket:** [ClickUp 8699pzeuz — "Table Filter Persistence | Implement for Partner Activity Log"](https://app.clickup.com/t/8699pzeuz) (blocked on this story)
- **Sibling story sets (same epic):** [Upload Activity Status Column](user-stories-dataset-upload-activity-status-column-2026-07-23.md) (2026-07-23), [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md) (2026-07-23), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21)
- **Design:** [Figma — Connections / Collaboration Environment, node 0-1](https://www.figma.com/design/5Rgt0dM3LuJipGKsEgoveL/Connections---Collaboration-Environment?node-id=0-1)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Connections-area stories
