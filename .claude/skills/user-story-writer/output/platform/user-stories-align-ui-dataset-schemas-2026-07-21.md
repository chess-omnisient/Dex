# User Stories: Align UI Dataset Schemas

**Area:** Platform
**Source:** ClickUp task [8699pay33](https://app.clickup.com/t/8699pay33) — "UXUI | Align UI Dataset Schemas" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-21
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Datasets module, dataset schema table
- **Target user:** Platform user (internal/customer user managing dataset schemas)
- **Platform Area (ClickUp):** Datasets | **Squad:** Platform squad | **Squad tag:** UXUI
- **Source ticket's single user story bundled 3 concerns** (view action, details panel, empty state) — decomposed below per INVEST (each must be independently shippable/testable)
- **Design:** [Figma — Datasets, node 7337-8598](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=7337-8598)
- **Epic context:** Part of "Align Pages to X2" — broader initiative to align legacy pages to the X2 design system. No epic description was available in ClickUp; assume schema table/detail page styling should follow X2 patterns already established elsewhere (confirm with design if unclear).
- **Sprint/cycle:** Not yet assigned (Roadmap View: Backlog)

---

## Story 1: View Action on Dataset Schema Table

**As a** platform user,
**I want to** click a "View" action on a row in the dataset schema table,
**So that** I can navigate directly to that specific dataset schema's detail page.

### INVEST Check
- [x] **Independent** — Pure UI/navigation change to the actions column; no dependency on Stories 2–3
- [x] **Negotiable** — Icon vs. text label, column ordering are flexible per Figma
- [x] **Valuable** — Gives users a direct, primary path into schema detail instead of an indirect click target
- [x] **Estimable** — Single component change (actions column) plus a route/link
- [x] **Small** — One table, one action
- [x] **Testable** — Clear navigation target per row

### Acceptance Criteria

**AC1: View button present on every schema row**
Given the dataset schema table has one or more rows,
When a user views the actions column,
Then a "View" action is displayed as the primary action for each row (per Figma node 7337-8598).

**AC2: View navigates to the correct schema**
Given a user clicks "View" on a specific schema row,
When the navigation completes,
Then the user lands on that exact dataset schema's detail page (not a generic or wrong schema).

**AC3: Details panel appears on the specific dataset schema**
Given a user clicks "View" and lands on the specific dataset schema's detail page,
When the page renders,
Then the additional details panel is shown on the side of the schema table, containing the notification user's name and surname, and their email.

**AC4: Empty state when there are no schemas to display**
Given a dataset has zero schemas,
When a user views the dataset schema table,
Then an X2 empty state is shown instead of an empty table grid.
*Needs confirmation: the source ticket's "Add X2 empty state" is ambiguous — it may mean "two empty states" (e.g. no schemas at all vs. no results for a filter) or "the X2 design system's empty-state component." Confirm intended meaning with design/PM before estimating this AC.*

**AC5: Side navigation and page heading renamed to "Dataset Schemas"**
Given a user is anywhere on the dataset schema table or a specific schema's detail page,
When they view the side navigation and the page heading,
Then both display "Dataset Schemas" (not the prior/legacy name).

**AC6: Schema ID shown in its own column, no longer in a tooltip**
Given a user views the dataset schema table,
When they look at a schema row,
Then the Schema ID is displayed in a dedicated column,
And it is no longer shown only on hover via tooltip.

**AC7: Delete modal restyled to X2 patterns**
Given a user triggers delete on a schema row,
When the delete confirmation modal opens,
Then it displays with the updated X2 styling (per Figma node 7337-8598), replacing the prior modal styling.

**AC8: Toast feedback on delete success or failure**
Given a user confirms a delete action on a schema,
When the delete completes,
Then a success toast is shown confirming the schema was deleted;
And given the delete fails,
When the error occurs,
Then a failure toast is shown explaining the action did not complete.

### Edge Cases
- Row for a schema that has been deleted/archived between page load and click → show an error/toast and keep user on the table rather than a broken detail page
- User lacks permission to view a specific schema → "View" is hidden or disabled for that row (confirm permission model with engineering — not specified in source ticket)
- Rapid double-click on "View" → single navigation, not duplicate tabs/requests
- Schemas exist but all are filtered out by a search/filter control → confirm whether this needs its own empty-state variant (relates to AC4 ambiguity above)
- Data fetch fails (error, not empty) → must show an error state, not the empty state — do not conflate the two
- Rename must be consistent everywhere the old name appears (breadcrumbs, page titles/tab titles, links from other pages) — not just the side nav item and heading called out in AC5
- Long Schema ID values → truncate with ellipsis in the column, full value on hover or via copy action (not a tooltip-only reveal, which is what AC6 removes)
- Existing integrations/tests that relied on hovering for the Schema ID (if any) → confirm none exist before removing the tooltip behavior
- User closes/dismisses the delete modal without confirming → no delete occurs, no toast is shown
- Delete modal opened for a schema that gets deleted or changed by another user in the meantime → confirm expected behavior (stale-state error vs. silent no-op) with engineering
- Multiple rapid delete actions in sequence → confirm toasts stack/queue rather than overwrite each other

### Technical Notes
- Confirm whether "View" replaces an existing primary action or is additive to the actions column
- Permission/visibility rules for "View" per schema are not defined in the source ticket — flag with PM/engineering before estimating
- Reuse the platform's existing X2 empty-state component/pattern if one exists (check Figma library referenced in the design link)
- **Blocking question for PM:** clarify what "X2 empty state" means in AC4 before this story is sprint-ready
- Confirm the legacy name being replaced (not specified in source ticket) so QA can verify no stale references remain
- AC7/AC8 assume a delete action on schemas already exists and is only being restyled/given feedback — not present anywhere in the original ClickUp ticket. If delete functionality doesn't already exist, this is new scope (build, not restyle) and should be split into its own story rather than folded in here
- Confirm whether toast feedback (AC8) should also apply to other existing actions on this page (e.g. edit, if present) or is scoped to delete only

### Out of Scope
- Editing or changing the notification user from the details panel (view-only per source ticket)

---

## Story 2: Notification User Details Panel on Dataset Schema Detail

**As a** platform user,
**I want to** see a details panel alongside the schema table on a dataset schema's detail page, showing the notification user's name and email,
**So that** I know who is set to receive notifications for that schema without leaving the page.

### INVEST Check
- [x] **Independent** — Can ship without Story 1 (though Story 1 is the primary entry point) or Story 3
- [x] **Negotiable** — Panel placement/styling flexible within Figma constraints
- [x] **Valuable** — Surfaces ownership/notification context at the point of use, reducing lookups elsewhere
- [x] **Estimable** — One new panel component + one data fetch (notification user record)
- [x] **Small** — Single page addition, read-only display
- [x] **Testable** — Field presence and values are explicit and verifiable

### Acceptance Criteria

**AC1: Details panel visible on the schema detail page**
Given a user navigates to a specific dataset schema's detail page,
When the page loads,
Then a details panel is displayed on the side of the schema table (per Figma node 7337-8598).

**AC2: Panel shows notification user's name and surname**
Given the schema has a notification user assigned,
When the details panel renders,
Then it displays that user's first name and surname.

**AC3: Panel shows notification user's email**
Given the schema has a notification user assigned,
When the details panel renders,
Then it displays that user's email address.

**AC4: No notification user assigned**
Given a schema has no notification user assigned,
When the details panel renders,
Then it shows a clear "No notification user set" state rather than blank or broken fields.

### Edge Cases
- Notification user's account has been deactivated/deleted → show name/email if available, with a visual indicator that the user is inactive, rather than erroring
- Very long name or email → truncate with ellipsis, full value on hover/tooltip
- Multiple notification users per schema (if the data model supports it) → not covered by source ticket; confirm with PM whether this is single-user only

### Technical Notes
- Requires confirming the data source for "notification user" per schema — is this a stored field on the schema record, or derived from a separate notifications/subscriptions table?
- Confirm cardinality (one notification user per schema, per the source ticket's phrasing "the notification user's details" — singular)

### Out of Scope
- Editing or changing the notification user from this panel (view-only per source ticket)
- Notification delivery/preferences logic itself

---

## Story 3: Empty State for Dataset Schema Table

**As a** platform user,
**I want to** see a clear empty state when there are no schemas to display,
**So that** I understand the table is intentionally empty rather than broken or still loading.

### INVEST Check
- [x] **Independent** — Standalone UI state, no dependency on Stories 1–2
- [x] **Negotiable** — Copy and illustration are flexible within the X2 empty-state pattern
- [x] **Valuable** — Prevents user confusion ("is this broken?") on a page with no data
- [x] **Estimable** — Reuses/extends existing X2 empty-state component
- [x] **Small** — Single conditional render
- [x] **Testable** — Zero-state condition is explicit

### Acceptance Criteria

**AC1: Empty state shown when no schemas exist**
Given a dataset has zero schemas,
When a user views the dataset schema table,
Then an X2-pattern empty state is displayed instead of an empty table grid.

**AC2: Empty state is distinct from a loading state**
Given the schema data has finished loading and returned zero results,
When the empty state renders,
Then it is visually distinct from any loading/skeleton state (no flicker between the two).

**AC3: Second empty-state variant (per "X2 empty state" — AC4 in source ticket)**
Given the source ticket calls for two empty states ("X2 empty state" — quantity of 2),
When [the second scenario — e.g. filtered/search results with zero matches, vs. genuinely zero schemas] occurs,
Then the appropriate variant is shown.
*Needs confirmation: the source ticket's "Add X2 empty state" is ambiguous — it may mean "two empty states" (e.g. no schemas at all vs. no results for a filter) or "the X2 design system's empty-state component." Confirm intended meaning with design/PM before estimating this AC.*

### Edge Cases
- Schemas exist but all are filtered out by a search/filter control → confirm whether this needs its own empty-state variant (relates to AC3 ambiguity above)
- Data fetch fails (error, not empty) → must show an error state, not the empty state — do not conflate the two

### Technical Notes
- Reuse the platform's existing X2 empty-state component/pattern if one exists (check Figma library referenced in the design link)
- **Blocking question for PM:** clarify what "X2 empty state" means in AC4 of the source ticket before this story is sprint-ready

### Out of Scope
- Empty states for other tables/pages outside the dataset schema table

---

## Story Dependencies

```
Story 1 (View action) ── independent, unblocks primary navigation into schema detail
Story 2 (details panel) ── independent of Story 1, but only reachable via Story 1's nav in practice
Story 3 (empty state) ── fully independent
```

## Suggested Sprint Ordering
1. **Story 1** — unblocks the navigation path the rest of the epic depends on
2. **Story 2** — builds out the detail page users land on from Story 1
3. **Story 3** — independent; can run in parallel with either, but resolve the AC3 ambiguity with PM/design before pulling into a sprint

---

## Open Questions (flag before sprint-ready)
1. What does "X2 empty state" (quantity 2) mean in the source ticket's AC4 — two distinct empty-state scenarios, or the X2 design system's empty-state component? (Story 3)
2. What permission rules, if any, govern whether "View" is visible/enabled per schema row? (Story 1)
3. Is "notification user" strictly one user per schema, or could the data model support multiple? (Story 2)
4. Parent epic "UXUI | Align Pages to X2" has no description in ClickUp — confirm there are no additional X2 alignment requirements (spacing, typography, component versions) beyond what's in the Figma link.

## Related Context
- **Source ticket:** [ClickUp 8699pay33](https://app.clickup.com/t/8699pay33)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Design:** [Figma — Datasets](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=7337-8598)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Datasets-area stories
