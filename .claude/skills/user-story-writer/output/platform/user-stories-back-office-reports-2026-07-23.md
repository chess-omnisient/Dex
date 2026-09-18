# User Stories: Back Office — Reports (Empty State, Edit Action, Allow-Editing Toggle)

**Area:** Platform
**Source:** ClickUp task [8699phnag](https://app.clickup.com/t/8699phnag) — "UXUI | Back Office | Reports" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Back Office module, Reports table and Add/Edit Report modals
- **Target user:** Platform user (internal back-office operator managing reports)
- **Kept as a single story per the source ticket's own scope** (empty state, edit action, checkbox→toggle on two modals). Note: this bundles three independently-shippable UI concerns — see the INVEST caveat below before sprint-planning it as one unit.
- **X2 = the design system**, not a count — resolved in the sibling [Dataset Reports empty-state story](user-stories-dataset-reports-view-empty-state-2026-07-23.md) written the same day for the same parent epic; carried over here so it isn't re-flagged as ambiguous.
- **Design:** [Figma — Back Office, node 0-1](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=0-1)
- **Epic context:** Part of "Align Pages to X2" — same initiative as the Datasets Reports and Dataset Schemas story sets already written for sibling tickets under this epic.
- **Sprint/cycle:** Not yet assigned in the source ticket

---

## Story: Back Office Reports — Empty State, Edit Action, and Allow-Editing Toggle

**As a** platform user,
**I want to** see an empty state when there are no reports, use an edit button on each report row, set "allow editing" with a toggle instead of a checkbox on the Add and Edit report modals, see updated copy and a "Delete" primary action on the Delete Report modal, and see the Edit Report modal's primary action labeled "Save",
**So that** the Back Office Reports experience is complete, consistent with the X2 design system, and I can manage reports without confusion or extra navigation steps.

### Acceptance Criteria

**AC1: Empty state shown when there are no reports**
Given the Back Office Reports table has zero reports,  
When a user views the Reports table,  
Then an X2-pattern empty state is displayed instead of an empty table grid.

**AC2: Edit button present and opens the correct report**
Given the Back Office Reports table has one or more rows,  
When a user clicks the edit button next to the actions icon on a specific row,  
Then the edit report modal opens pre-populated with that exact report's data (not a blank form or another report's data).

**AC3: Toggle replaces checkbox on the Edit Report modal**
Given a user opens the Edit Report modal for an existing report,  
When they view the "allow editing" control,  
Then it is rendered as a toggle, not a checkbox, reflecting the report's current "allow editing" value.

**AC4: Toggle replaces checkbox on the Add Report modal, and both persist the same underlying value**
Given a user opens the Add Report modal to create a new report,  
When they view and change the "allow editing" control and save,  
Then it is rendered as a toggle (not a checkbox) defaulting to the checkbox's prior default, and the persisted value matches exactly what the checkbox's checked/unchecked state would have persisted.

**AC5: Delete Report modal copy and heading updated, primary action labeled "Delete"**
Given a user opens the Delete Report modal for a report,  
When the modal renders,  
Then the modal heading and body copy match the updated X2 copy, and the primary action button reads "Delete".

**AC6: Edit Report modal primary action relabeled to "Save"**
Given a user opens the Edit Report modal for an existing report,  
When they view the modal's primary action button,  
Then it reads "Save" (replacing its prior label), and clicking it persists the edited report exactly as before.

### Design
[Figma — Back Office, node 0-1](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=0-1)

### INVEST Check
- [ ] **Independent** — Does not hold, as written. The empty state, edit action, toggle swap, and modal copy/label updates touch five largely unrelated parts of the UI (table zero-state, actions column, three modals) with no shared dependency between them. Kept together only because the source ticket scoped it that way.
- [x] **Negotiable** — Copy, icon placement, and exact toggle styling are flexible within the X2 component library
- [x] **Valuable** — Each piece removes a real point of confusion or friction (unclear zero state, indirect edit path, ambiguous checkbox, inconsistent modal copy/labels)
- [x] **Estimable** — Each piece is individually well-scoped; combined estimate is additive (empty-state render + actions-column change + modal control swap + modal copy/label changes)
- [ ] **Small** — Does not hold, as written. Five separable UI changes in one story is larger than a single sprint-sized unit should be; if velocity or review cycles suffer, split back into the stories below the AC1/AC2/AC3–AC4/AC5/AC6 boundaries.
- [x] **Testable** — Each acceptance criterion below is independently verifiable, even though they ship together

### Edge Cases
- Reports exist but all are filtered out by a search/filter control (unconfirmed whether this table has filters) → confirm whether this needs its own empty-state variant, or reuses the same one
- Row for a report that has been deleted between page load and edit-click → show an error/toast rather than opening a broken modal
- User lacks permission to edit a specific report → edit button is hidden or disabled for that row (confirm permission model with engineering — not specified in source ticket)
- Rapid double-click on edit → single modal instance, not duplicate modals
- Existing reports with "allow editing" already set (true/false) → toggle must reflect the existing stored value correctly, not reset to a default
- User toggles the control but cancels the modal without saving → value must not persist (same behavior as the checkbox had)

### Technical Notes
- Reuse the platform's existing X2 empty-state component/pattern, already used for the sibling Datasets Reports empty state, rather than building a new one
- Confirm whether the edit button is additive to the existing actions column or replaces an existing action
- Toggle swap is a like-for-like control change on the same underlying boolean field — no backend/data model change expected; confirm it's the platform's existing X2 toggle component
- Permission/visibility rules for edit per report are not defined in the source ticket — flag with PM/engineering before estimating

### Out of Scope
- Empty states for other Back Office tables/pages
- The contents/fields of the edit report modal itself, beyond the toggle change
- Any other fields or checkboxes on the Add/Edit Report modals beyond "allow editing"

---

## Suggested Delivery Note

If this is estimated and it lands larger than a single sprint-sized unit, split along the AC groupings above — AC1 (empty state), AC2 (edit action), AC3–AC4 (toggle) — each ships independently with no sequencing dependency between them.

---

## Open Questions (flag before sprint-ready)
1. What permission rules, if any, govern whether the edit button is visible/enabled per report row?
2. Does the Back Office Reports table have filter/search functionality that would need its own empty-state variant, distinct from the "zero reports at all" case?
3. Should the Back Office empty-state visual/copy match the Datasets Reports empty state exactly, or have Back-Office-specific messaging?
4. Is the edit button additive to the existing actions column, or does it replace an existing action?

## Related Context
- **Source ticket:** [ClickUp 8699phnag](https://app.clickup.com/t/8699phnag)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Sibling story set:** [Datasets — Reports Table (View Action & Empty State)](user-stories-dataset-reports-view-empty-state-2026-07-23.md) — same epic, same X2 empty-state pattern, source of the "X2 = design system" resolution
- **Design:** [Figma — Back Office, node 0-1](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=0-1)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Back Office stories
