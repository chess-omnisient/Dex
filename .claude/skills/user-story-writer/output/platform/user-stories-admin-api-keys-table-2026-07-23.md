# User Stories: Admin — API Keys Table (Empty State, Delete Action, Date Column)

**Area:** Platform
**Source:** ClickUp task [8699phn6m](https://app.clickup.com/t/8699phn6m) — "UXUI | Admin | API Keys" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Admin module, API Keys table
- **Target user:** Platform user (admin managing API keys)
- **PDLC Phase (ClickUp):** Ready for Dev | **Priority:** Normal
- **Request Type:** Not set on ticket (treated as Enhancement — aligning an existing table to the X2 design system)
- **Source ticket's single user story bundled 3 concerns** (empty state, delete action replacing the actions menu, new date column) — decomposed below per INVEST (each must be independently shippable/testable)
- **Design:** [Figma — Admin, node 8-911](https://www.figma.com/design/hjRmeL4sizajFC17PzpBpN/Admin?node-id=8-911)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Partner Activity Log Empty State story](user-stories-partner-activity-log-empty-state-2026-07-23.md), [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md), [Upload Activity Status Column story](user-stories-dataset-upload-activity-status-column-2026-07-23.md), and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), all written for sibling tickets under this epic.
- **Downstream dependency:** A separate ticket, ["Table Filter Persistence | Admin | Implement for API Keys"](https://app.clickup.com/t/8699pzexx), is blocked by this one — filter persistence work on the API Keys table can't start until this ships. This confirms the API Keys table is a filterable table, which shapes the edge cases below.
- **Sprint/cycle:** Not yet assigned

---

## Story 1: Empty State for API Keys Table

**As a** platform user,
**I want to** see a clear X2-styled empty state when there are no API keys to display,
**So that** I understand there's genuinely nothing to see, rather than assuming the table is broken or still loading.

### INVEST Check
- [x] **Independent** — Standalone UI state; no dependency on Story 2 or Story 3
- [x] **Negotiable** — Copy and illustration are flexible within the X2 empty-state pattern
- [x] **Valuable** — Prevents users from misreading a blank API Keys table as a bug or a stuck load
- [x] **Estimable** — Reuses/extends the platform's existing X2 empty-state component
- [x] **Small** — Single conditional render
- [x] **Testable** — Zero-state condition is explicit

### Acceptance Criteria

**AC1: Empty state shown when there are no API keys**
Given a user navigates to the API Keys table,
When there are no API keys to display,
Then the X2 empty state (per Figma node 8-911) is shown in place of the table.
*Source ticket AC1: "An empty state is displayed if there are no API keys to display."*

**AC2: Table shown when API keys exist**
Given a user navigates to the API Keys table,
When one or more API keys exist,
Then the table renders normally and the empty state is not shown.

**AC3: Empty state is distinct from a loading state**
Given the API keys data has finished loading and returned zero results,
When the empty state renders,
Then it is visually distinct from any loading/skeleton state (no flicker between the two).

### Edge Cases
- **No API keys at all vs. no keys matching an active filter** — since a filter-persistence story is already queued for this table, confirm whether "no results for the current filter" should show this same empty state or a distinct "no matches, clear filter" variant (see Open Questions)
- **Data fetch fails (error, not empty)** — ticket only specifies the zero-keys case; an error/failed-fetch state is a separate concern and should not silently reuse this empty state
- **Key created while the empty state is showing** — if the platform supports live updates elsewhere, confirm whether creating the first key should replace the empty state without a manual refresh

### Technical Notes
- Confirm whether a shared X2 empty-state component already exists (the sibling Partner Activity Log, Reports Table, and Dataset Schemas stories under this same epic likely use one) — reuse rather than building a new one per table

### Out of Scope
- Empty states for other tables/pages outside the API Keys table
- Error/failed-fetch state handling

---

## Story 2: Delete Action Replaces Actions Menu on API Keys Table

**As a** platform user,
**I want to** see a direct "delete" button in place of the actions menu on each API key row,
**So that** I can remove a key in one click instead of opening a menu first.

### INVEST Check
- [x] **Independent** — Pure UI change to the actions column; no dependency on Story 1 or Story 3
- [x] **Negotiable** — Icon vs. text label, exact placement flexible per Figma
- [x] **Valuable** — Removes an unnecessary click (open menu → select delete) for what is likely the only action on this table
- [x] **Estimable** — Single component swap (actions menu → delete button) plus the existing delete dialogue
- [x] **Small** — One table, one action
- [x] **Testable** — Clear before/after UI state and a deterministic dialogue-open behavior

### Acceptance Criteria

**AC1: Delete button replaces the actions menu**
Given a user views a row in the API Keys table,
When they look at the actions column,
Then a "delete" button is shown in place of the previous actions menu (per Figma node 8-911).
*Source ticket AC2: "A 'delete' button replaces the actions menu and opens the delete dialogue."*

**AC2: Delete button opens the delete confirmation dialogue**
Given a user clicks the "delete" button on a specific API key row,
When the click registers,
Then the existing delete confirmation dialogue opens, scoped to that specific key.

**AC3: Delete action is keyboard/screen-reader accessible**
Given a user navigates the table via keyboard,
When they tab to a row's "delete" button and activate it,
Then the same dialogue opens as with a mouse click.

### Edge Cases
- **Row for a key that's already been deleted/revoked between page load and click** → show an error/toast and refresh the table rather than opening a dialogue for a key that no longer exists
- **Rapid double-click on "delete"** → single dialogue open, not duplicate dialogues or duplicate delete requests
- **User lacks permission to delete a specific key** (e.g., a key owned by another admin) → confirm whether "delete" is hidden, disabled, or always available for any platform user on this table (not specified in source ticket)
- **No other actions currently exist on this menu besides delete** — confirm this is true; if the actions menu currently exposes anything beyond delete (e.g., "regenerate," "view details"), those actions need a new home before the menu can be fully replaced

### Technical Notes
- Confirm the actions menu being replaced doesn't currently expose any action other than delete — if it does, this story's scope needs to grow or those actions need an alternate placement (flag with design/PM before estimating)
- Reuse the existing delete confirmation dialogue rather than building a new one — ticket implies it already exists ("opens the delete dialogue")
- Permission/visibility rules for "delete" per key are not defined in the source ticket — flag with PM/engineering before estimating

### Out of Scope
- The internal behavior/API call of the delete confirmation dialogue itself (assumed to already exist and work — this story only wires up the new entry point)
- Any other actions menu on other tables in the Admin module

---

## Story 3: Date Column on API Keys Table

**As a** platform user,
**I want to** see a "date" column on the API Keys table,
**So that** I know when each key was created (or last used, per design) without having to look it up elsewhere.

### INVEST Check
- [x] **Independent** — Additive column; no dependency on Story 1 or Story 2
- [x] **Negotiable** — Column placement, formatting, and exact date semantics (created vs. last used) are flexible within the Figma spec
- [x] **Valuable** — Surfaces key age/recency directly in the table, supporting decisions like "is this key stale enough to rotate or delete?"
- [x] **Estimable** — Single new column bound to an existing or new date field
- [x] **Small** — One column, one table
- [x] **Testable** — Column presence and value formatting are directly verifiable

### Acceptance Criteria

**AC1: Date column is present on the table**
Given a user views the API Keys table,
When the table renders,
Then a "date" column is displayed (per Figma node 8-911).
*Source ticket AC3: "A 'date' column is added to the table."*

**AC2: Date column shows a correctly formatted value per row**
Given an API key with a known creation date,
When the row renders,
Then the date column displays that date in the platform's standard date format.

**AC3: Date column handles missing/null dates gracefully**
Given an API key row where the date value is missing or null (e.g., a legacy key created before this field was tracked),
When the row renders,
Then the column shows a clear placeholder (e.g., "—" or "Unknown") rather than a blank cell or an error.

### Edge Cases
- **Which date is this?** — ticket doesn't specify "created" vs. "last used" vs. "last rotated"; confirm against Figma/design before estimating (see Open Questions)
- **Legacy keys with no recorded date** — confirmed handling in AC3, but confirm whether backfilling this data is in scope or genuinely out of scope
- **Sorting by date column** — unconfirmed whether the table supports column sorting; if it does, confirm the new column should be sortable like the others

### Technical Notes
- Confirm the underlying date field already exists on the API key data model, or whether it needs to be added/backfilled — this materially changes scope
- Confirm date formatting matches the platform's existing date-column conventions elsewhere in Admin (for consistency, not a new pattern)

### Out of Scope
- Backfilling date data for legacy keys, unless confirmed in scope during refinement
- Sorting/filtering by date, unless the table's existing columns already support this

---

## Story Dependencies

```
Story 1 (empty state)    ── independent
Story 2 (delete action)  ── independent
Story 3 (date column)    ── independent

All three ──→ Table Filter Persistence for API Keys (8699pzexx, separate ticket, blocked on this one)
```

All three stories can be built and shipped in parallel — there is no sequencing dependency between them. The downstream Table Filter Persistence ticket depends on this work landing, but doesn't gate the order among Stories 1–3.

## Suggested Sprint Ordering
1. **Story 1, 2, and 3** can run in parallel — none blocks the others
2. Resolve the actions-menu-contents question (Story 2) and the date-semantics question (Story 3) early — both affect scope/estimate before sprint commitment
3. Prioritize landing all three before or alongside the queued Table Filter Persistence work ([8699pzexx](https://app.clickup.com/t/8699pzexx)), since that ticket is explicitly blocked on this one

---

## Open Questions (flag before sprint-ready)
1. Does the current actions menu expose anything beyond "delete"? If so, where do those actions go once the menu is replaced? (Story 2)
2. What are the permission rules, if any, for who can delete a given API key? (Story 2)
3. Is the new "date" column showing created date, last-used date, or last-rotated date? (Story 3)
4. Do legacy API keys have this date value recorded, or does it need to be backfilled? (Story 3)
5. Should "no keys at all" and "no keys matching the current filter" show the same empty state, or does the filter-persistence work require a distinct "no matches" variant? (Story 1)

## Related Context
- **Source ticket:** [ClickUp 8699phn6m](https://app.clickup.com/t/8699phn6m)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Downstream ticket:** [ClickUp 8699pzexx — "Table Filter Persistence | Admin | Implement for API Keys"](https://app.clickup.com/t/8699pzexx) (blocked on this story)
- **Sibling story sets (same epic):** [Partner Activity Log Empty State](user-stories-partner-activity-log-empty-state-2026-07-23.md) (2026-07-23), [Upload Activity Status Column](user-stories-dataset-upload-activity-status-column-2026-07-23.md) (2026-07-23), [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md) (2026-07-23), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21)
- **Design:** [Figma — Admin, node 8-911](https://www.figma.com/design/hjRmeL4sizajFC17PzpBpN/Admin?node-id=8-911)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Admin-area stories
