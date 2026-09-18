# User Stories: Datasets — Reports Table (View Action & Empty State)

**Area:** Platform
**Source:** ClickUp task [869e28m0q](https://app.clickup.com/t/869e28m0q) — "UXUI | Datasets | Reports" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Datasets module, Reports table
- **Target user:** Platform user (internal/customer user reviewing dataset reports)
- **PDLC Phase (ClickUp):** Ready for Dev | **Roadmap View:** Backlog | **Region:** ZA
- **Request Type:** Enhancement
- **Source ticket's single user story bundled 2 concerns** (primary view action, empty state) — decomposed below per INVEST (each must be independently shippable/testable)
- **Design:** [Figma — Datasets, node 7337-17498](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=7337-17498)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md) written yesterday for a sibling ticket under this epic.
- **Resolved ambiguity carried over from the sibling story:** that earlier draft flagged "X2 empty state" as ambiguous (two states, vs. the X2 design system). This ticket's "Value / Opportunity" field states *"Align the app to X2 for consistency"* — confirming **X2 is the design system name**, not a count. Treated as resolved here; worth back-porting that correction to the sibling story too.
- **Sprint/cycle:** Not yet assigned (Roadmap View: Backlog)

---

## Story 1: View Action on Reports Table

**As a** platform user,
**I want to** click a "View" action on a row in the Reports table,
**So that** I can navigate directly to that specific Dataset Report's own detail page.

### INVEST Check
- [x] **Independent** — Pure UI/navigation change to the actions column; no dependency on Story 2
- [x] **Negotiable** — Icon vs. text label, exact placement flexible per Figma
- [x] **Valuable** — Gives users a direct, primary path into detail instead of an indirect click target
- [x] **Estimable** — Single component change (actions column) plus a route/link
- [x] **Small** — One table, one action
- [x] **Testable** — Clear navigation target per row

### Acceptance Criteria

**AC1: View button present on every report row**
Given the Reports table has one or more rows,
When a user views the actions column,
Then a "View" action is displayed as the primary action for each row (per Figma node 7337-17498).

**AC2: View navigates to the correct destination**
Given a user clicks "View" on a specific report row,
When the navigation completes,
Then the user lands on that exact Dataset Report's own detail page (not a generic or wrong report).

**AC3: View action is keyboard/screen-reader accessible**
Given a user navigates the table via keyboard,
When they tab to a row's "View" action and activate it,
Then the same navigation occurs as with a mouse click.

### Edge Cases
- Row for a report that has been deleted/archived between page load and click → show an error/toast and keep the user on the table rather than a broken detail page
- User lacks permission to view a specific report → "View" is hidden or disabled for that row (confirm permission model with engineering — not specified in source ticket)
- Rapid double-click on "View" → single navigation, not duplicate tabs/requests
- Reports table has filters/search (unconfirmed) and a filtered row is clicked → same behavior as an unfiltered row

### Technical Notes
- Confirm whether "View" replaces an existing primary action or is additive to the actions column
- Permission/visibility rules for "View" per report are not defined in the source ticket — flag with PM/engineering before estimating
- Confirm whether a Dataset Report detail page already exists (and this is just adding the entry point) or needs to be built as part of this story — the source ticket only specifies the table-side action, not the destination page's contents

### Out of Scope
- The visual design/content of the Dataset Report detail page itself, beyond confirming it exists as a navigation target (covered by a separate story/ticket if it needs to be built)

---

## Story 2: Empty State for Reports Table

**As a** platform user,
**I want to** see a clear X2-styled empty state when there are no reports to display,
**So that** I understand the table is intentionally empty rather than broken or still loading.

### INVEST Check
- [x] **Independent** — Standalone UI state, no dependency on Story 1
- [x] **Negotiable** — Copy and illustration are flexible within the X2 empty-state pattern
- [x] **Valuable** — Prevents user confusion ("is this broken?") on a page with no data
- [x] **Estimable** — Reuses/extends the platform's existing X2 empty-state component
- [x] **Small** — Single conditional render
- [x] **Testable** — Zero-state condition is explicit

### Acceptance Criteria

**AC1: Empty state available when there are no reports**
Given a dataset has zero reports,
When a user views the Reports table,
Then an X2-pattern empty state is displayed instead of an empty table grid (per Figma node 7337-17498).
*Source ticket AC1: "Add X2 empty state when there are no reports to display."*

**AC2: Empty state is distinct from a loading state**
Given the reports data has finished loading and returned zero results,
When the empty state renders,
Then it is visually distinct from any loading/skeleton state (no flicker between the two).

**AC3: Empty state is distinct from an error state**
Given the reports data fetch fails,
When the failure occurs,
Then an error state is shown, not the empty state — the two must not be conflated.

### Edge Cases
- Reports exist but all are filtered out by a search/filter control (unconfirmed whether this table has filters) → confirm whether this needs its own empty-state variant, or reuses the same one
- Data fetch fails (error, not empty) → must show an error state, not the empty state (covered by AC3)
- Transition from empty → first report created while the page is open (if live-updating) → empty state should be replaced by the table without requiring a manual refresh, if the platform supports live updates elsewhere

### Technical Notes
- Reuse the platform's existing X2 empty-state component/pattern (already used or planned for the sibling Dataset Schemas story) rather than building a new one
- Confirm with design whether the Reports empty-state copy/illustration should differ from the Dataset Schemas empty state, or if a shared generic variant is intended

### Out of Scope
- Empty states for other tables/pages outside the Reports table

---

## Story Dependencies

```
Story 1 (View action) ── independent
Story 2 (empty state) ── fully independent
```

Both stories can be built and shipped in parallel — there is no sequencing dependency between them.

## Suggested Sprint Ordering
1. **Story 1** and **Story 2** can run in parallel — neither blocks the other
2. Confirm whether the Dataset Report detail page already exists before estimating Story 1 (see Technical Notes) — if it needs to be built from scratch, that's materially more scope than a table/navigation change alone

---

## Open Questions (flag before sprint-ready)
1. Does the Dataset Report detail page already exist, or does it need to be built as part of Story 1? (Story 1)
2. What permission rules, if any, govern whether "View" is visible/enabled per report row? (Story 1)
3. Does the Reports table have filter/search functionality that would need its own empty-state variant, distinct from the "zero reports at all" case? (Story 2)
4. Should the Reports empty-state visual/copy match the Dataset Schemas empty state exactly, or have report-specific messaging?

## Related Context
- **Source ticket:** [ClickUp 869e28m0q](https://app.clickup.com/t/869e28m0q)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Sibling story set:** [Dataset Schemas — View Action, Details Panel, Empty State](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21) — same epic, same X2 empty-state pattern
- **Design:** [Figma — Datasets, node 7337-17498](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=7337-17498)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Datasets-area stories
