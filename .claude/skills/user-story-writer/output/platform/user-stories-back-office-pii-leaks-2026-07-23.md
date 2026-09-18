# User Stories: Back Office — PII Leaks (Empty State & Client Notified Icon Color)

**Area:** Platform
**Source:** ClickUp task [8699phndn](https://app.clickup.com/t/8699phndn) — "UXUI | Back Office | PII Leaks" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Back Office module, PII Leaks table
- **Target user:** Platform user (viewing PII leak records in Back Office)
- **PDLC Phase (ClickUp):** Ready for Dev | **Roadmap View:** Backlog | **Priority:** Low
- **Request Type:** Not set on ticket (treated as Enhancement — aligning an existing table to the X2 design system)
- **Kept as a single story per the source ticket's bundling** (empty state + "client notified" icon color). The two concerns touch the same table, are both trivial in scope, and share the ticket's Low priority — combining keeps the story matched 1:1 to the ticket for sprint tracking. Flagging for awareness: the two ACs are functionally independent (one is conditional rendering, the other is styling), so if either slips or needs re-scoping mid-sprint, they can still be split and shipped separately without any rework.
- **Design:** [Figma — Back Office, node 11-854](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=11-854)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Partner Activity Log Empty State story](user-stories-partner-activity-log-empty-state-2026-07-23.md), [Admin API Keys Table story set](user-stories-admin-api-keys-table-2026-07-23.md), [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md), [Upload Activity Status Column story](user-stories-dataset-upload-activity-status-column-2026-07-23.md), and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), all written for sibling tickets under this epic.
- **Downstream dependency:** A separate ticket, ["Table Filter Persistence | Back Office | Implement for PII Leaks"](https://app.clickup.com/t/8699pzevk), is blocked by this one — filter persistence work on the PII Leaks table can't start until this ships. This confirms the PII Leaks table is a filterable table, which shapes the edge cases below.
- **Sprint/cycle:** Not yet assigned

---

## Story 1: PII Leaks Table — Empty State & Client Notified Icon Color

**As a** platform user,
**I want to** see a clear X2-styled empty state when there are no PII leaks to display, and black tick/cross icons in the "client notified" column,
**So that** I understand there's genuinely nothing to see (rather than assuming the table is broken), and the table matches the rest of the X2-aligned platform.

### INVEST Check
- [x] **Independent** — Neither concern depends on other stories in this epic
- [ ] **Negotiable** — Copy/illustration (empty state) and icon asset/weight (color) are flexible within the X2/Figma spec, but note this story covers two unrelated UI concerns bundled from the source ticket
- [x] **Valuable** — Prevents users from misreading a blank table as broken (empty state), and removes an off-pattern color in an otherwise X2-aligned table (icon color)
- [x] **Estimable** — Two small, well-understood changes: one conditional render, one style/token change
- [x] **Small** — Both concerns are trivial individually; combined, still fits comfortably in a sprint
- [x] **Testable** — Each AC below has a clear, deterministic pass/fail condition

### Acceptance Criteria

**AC1: Empty state shown when there are no PII leaks**
Given a user navigates to the PII Leaks table,  
When there are no PII leak records to display,  
Then the X2 empty state (per Figma node 11-854) is shown in place of the table.
*Source ticket AC1: "Add X2 empty state when there are no PII leaks to display."*

**AC2: Table shown when PII leak records exist**
Given a user navigates to the PII Leaks table,  
When one or more PII leak records exist,  
Then the table renders normally and the empty state is not shown.

**AC3: Empty state is distinct from a loading state**
Given the PII leaks data has finished loading and returned zero results,  
When the empty state renders,  
Then it is visually distinct from any loading/skeleton state (no flicker between the two).

**AC4: "Client notified" tick icon is black**
Given a row in the PII Leaks table where the client has been notified,  
When the "client notified" column renders,  
Then the tick icon is displayed in black (per Figma node 11-854).
*Source ticket AC2: "Change the crosses and ticks to black on the client notified column."*

**AC5: "Client notified" cross icon is black**
Given a row in the PII Leaks table where the client has not been notified,  
When the "client notified" column renders,  
Then the cross icon is displayed in black (per Figma node 11-854).

**AC6: Icon color change doesn't affect other semantic meaning**
Given both the tick and cross icons are now the same color,  
When a user scans the column,  
Then tick vs. cross shape alone (not color) remains sufficient to distinguish notified from not-notified — confirm this reads clearly for colorblind users too, since color is no longer a differentiator.

### Edge Cases
- **No PII leaks at all vs. no leaks matching an active filter** — since a filter-persistence story is already queued for this table, confirm whether "no results for the current filter" should show this same empty state or a distinct "no matches, clear filter" variant (see Open Questions)
- **Data fetch fails (error, not empty)** — ticket only specifies the zero-leaks case; an error/failed-fetch state is a separate concern and should not silently reuse this empty state
- **New leak recorded while the empty state is showing** — confirm whether the table should update live or only on manual refresh/re-navigation
- **Third/unknown "client notified" state** — confirm whether this column only ever has two states (yes/no) or whether a pending/unknown state exists that needs its own treatment, since the ticket only mentions two icons
- **Accessibility** — with both icons recolored to black, shape becomes the only differentiator; confirm this passes an accessibility check (contrast, and distinguishability without relying on color)

### Technical Notes
- Confirm whether a shared X2 empty-state component already exists (the sibling Partner Activity Log, API Keys, and Reports Table stories under this same epic likely use one) — reuse rather than building a new one per table
- Icon recolor is likely a token/style-level change (e.g., updating an icon component's color prop) rather than swapping icon assets — consistent with the ticket's "Low" priority
- Check whether the same tick/cross icon pattern (in its current, non-black color) appears elsewhere in Back Office or other X2-alignment tickets in this epic — if so, flag whether those need the same fix or are already tracked separately
- The empty state and icon color change touch different parts of the same component tree and can be built/reviewed independently even though they ship as one story — no need to serialize the two changes

### Out of Scope
- Empty states for other tables/pages outside the PII Leaks table
- Error/failed-fetch state handling
- Any change to the underlying "client notified" logic/data — this is a color/styling change only
- Icon color changes on any table other than PII Leaks

---

## Story Dependencies

```
Story 1 (empty state + icon color) ──→ Table Filter Persistence for PII Leaks (8699pzevk, separate ticket, blocked on this one)
```

## Suggested Sprint Ordering
1. Story 1 — unblocks the queued Table Filter Persistence work; resolve the open questions below before sprint commitment

---

## Open Questions (flag before sprint-ready)
1. Should "no leaks at all" and "no leaks matching the current filter" show the same empty state, or does the filter-persistence work require a distinct "no matches" variant?
2. Does "client notified" ever have a third state (e.g., pending/unknown) beyond tick/cross?
3. With both icons now black, does the column still pass an accessibility check for distinguishability without relying on color?
4. Does the same tick/cross color pattern appear on other tables in this epic that also need recoloring?

## Related Context
- **Source ticket:** [ClickUp 8699phndn](https://app.clickup.com/t/8699phndn)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Downstream ticket:** [ClickUp 8699pzevk — "Table Filter Persistence | Back Office | Implement for PII Leaks"](https://app.clickup.com/t/8699pzevk) (blocked on this story)
- **Sibling story sets (same epic):** [Partner Activity Log Empty State](user-stories-partner-activity-log-empty-state-2026-07-23.md) (2026-07-23), [Admin API Keys Table](user-stories-admin-api-keys-table-2026-07-23.md) (2026-07-23), [Upload Activity Status Column](user-stories-dataset-upload-activity-status-column-2026-07-23.md) (2026-07-23), [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md) (2026-07-23), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21)
- **Design:** [Figma — Back Office, node 11-854](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=11-854)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Back Office-area stories
