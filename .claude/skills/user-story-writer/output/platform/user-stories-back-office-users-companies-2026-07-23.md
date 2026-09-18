# User Stories: Back Office — Manage Users, Manage Companies, Novatiq Configuration

**Area:** Platform
**Source:** ClickUp task [869e7dqpa](https://app.clickup.com/t/869e7dqpa) — "UXUI | Back Office | Users" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Back Office module (Manage Users, Manage Companies tables)
- **Target user:** Back Office admin (an internal platform user managing users, companies, and partner configuration)
- **User JTBD:** Not yet documented in `context/personas.md` (doesn't exist for this area) — inferred from the ticket: when managing platform users, companies, and partner integrations, the Back Office admin needs fast, self-serve edit and configuration access without leaving the table view, and needs to trust that an empty table means "no data," not "broken."
- **PDLC Phase (ClickUp):** Ready for Dev | **Priority:** Normal
- **Squad:** UXUI
- **Source ticket's single user story bundled 3 unrelated concerns** across two different tables — an empty state, an edit action, and a Novatiq partner-configuration feature — decomposed below per INVEST (each independently shippable/testable). The source story's "I want to see a..." sentence is also incomplete on the ticket itself.
- **Design:** [Figma — Back Office, node 15-171](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=15-171)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Admin API Keys Table story set](user-stories-admin-api-keys-table-2026-07-23.md), [Partner Activity Log Empty State story](user-stories-partner-activity-log-empty-state-2026-07-23.md), [Admin Activity Log Empty State story](user-stories-admin-activity-log-empty-state-2026-07-23.md), [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md), [Upload Activity Status Column story](user-stories-dataset-upload-activity-status-column-2026-07-23.md), and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), all written for sibling tickets under this epic.
- **Sprint/cycle:** Not yet assigned

---

## Story 1: Empty State for Manage Users Table

**As a** Back Office admin,
**I want to** see a clear X2-styled empty state when there are no users to display,
**So that** I understand there's genuinely nothing to see, rather than assuming the table is broken or still loading.

### INVEST Check
- [x] **Independent** — Standalone UI state; no dependency on Stories 2–5
- [x] **Negotiable** — Copy and illustration are flexible within the X2 empty-state pattern
- [x] **Valuable** — Prevents users from misreading a blank Manage Users table as a bug or a stuck load
- [x] **Estimable** — Likely reuses the same X2 empty-state component built for the sibling Admin/API Keys and Activity Log stories in this epic
- [x] **Small** — Single conditional render
- [x] **Testable** — Zero-state condition is explicit

### Acceptance Criteria

**AC1: Empty state shown when there are no users**
Given a Back Office admin navigates to the Manage Users table,  
When there are no users to display,  
Then the X2 empty state (per Figma node 15-171) is shown in place of the table.  
*Source ticket AC1: "Add an empty state if there are no users."*

**AC2: Table shown when users exist**
Given a Back Office admin navigates to the Manage Users table,  
When one or more users exist,  
Then the table renders normally and the empty state is not shown.  

**AC3: Empty state is distinct from a loading state**
Given the users data has finished loading and returned zero results,  
When the empty state renders,  
Then it is visually distinct from any loading/skeleton state (no flicker between the two).  

### Edge Cases
- **No users at all vs. no users matching an active filter/search** — confirm whether "no matches" should reuse this empty state or show a distinct "no matches, clear filter" variant (see Open Questions)
- **Data fetch fails (error, not empty)** — ticket only specifies the zero-users case; an error/failed-fetch state is a separate concern and should not silently reuse this empty state

### Technical Notes
- Reuse the shared X2 empty-state component from the Admin API Keys / Activity Log stories rather than building a new one for this table

### Out of Scope
- Empty states for other Back Office tables besides Manage Users
- Error/failed-fetch state handling

---

## Story 2: Edit Action on Manage Users Table

**As a** Back Office admin,
**I want to** click an edit button next to the actions icon on a user row,
**So that** I can open that user's edit modal directly, without hunting through a menu.

### INVEST Check
- [x] **Independent** — Pure UI addition to the actions column of Manage Users; no dependency on Story 1, 3, 4, or 5
- [x] **Negotiable** — Icon style and exact spacing relative to the actions icon are flexible per Figma
- [x] **Valuable** — Surfaces the most common row action (edit) as a direct one-click affordance
- [x] **Estimable** — Single button addition wired to an existing edit-user modal
- [x] **Small** — One table, one added action
- [x] **Testable** — Clear before/after UI state and deterministic modal-open behavior

### Acceptance Criteria

**AC1: Edit button appears next to the actions icon**
Given a Back Office admin views a row in the Manage Users table,  
When they look at the row's action area,  
Then an "edit" button is shown next to the existing actions icon (per Figma node 15-171).  
*Source ticket AC2: "Add an edit button next to the actions icon."*

**AC2: Edit button opens the edit user modal**
Given a Back Office admin clicks the "edit" button on a specific user row,  
When the click registers,  
Then the edit user modal opens, pre-populated with that user's data.  
*Source ticket AC3: "The edit button opens the edit user modal."*

**AC3: Edit action is keyboard/screen-reader accessible**
Given a Back Office admin navigates the table via keyboard,  
When they tab to a row's "edit" button and activate it,  
Then the same modal opens as with a mouse click.  

### Edge Cases
- **User being edited is deleted/deactivated between page load and click** → show an error/toast and refresh the table rather than opening a modal for a user that no longer exists
- **Rapid double-click on "edit"** → single modal open, not duplicate modals
- **Admin lacks permission to edit a specific user** (e.g., editing a higher-privilege account) → confirm whether "edit" is hidden, disabled, or always available (not specified in source ticket)

### Technical Notes
- Confirm the edit user modal referenced already exists (ticket implies it does: "opens the edit user modal") — this story only wires up the entry point, not the modal itself
- Permission/visibility rules for who can edit which users are not defined in the source ticket — flag with PM/engineering before estimating

### Out of Scope
- The internal behavior/fields/save logic of the edit user modal itself (assumed pre-existing)
- Bulk edit of multiple users at once

---

## Story 3: Edit Action on Manage Companies Table

**As a** Back Office admin,
**I want to** click an edit button next to the actions icon on a company row,
**So that** I can open that company's edit modal directly, without hunting through a menu.

### INVEST Check
- [x] **Independent** — Pure UI addition to the actions column of Manage Companies; no dependency on Story 1, 2, 4, or 5
- [x] **Negotiable** — Icon style and placement flexible per Figma
- [x] **Valuable** — Same one-click editing benefit as Story 2, applied to companies
- [x] **Estimable** — Single button addition wired to an existing edit-company modal
- [x] **Small** — One table, one added action
- [x] **Testable** — Clear before/after UI state and deterministic modal-open behavior

### Acceptance Criteria

**AC1: Edit button appears next to the actions icon on Manage Companies**
Given a Back Office admin views a row in the Manage Companies table,  
When they look at the row's action area,  
Then an "edit" button is shown next to the existing actions icon (per Figma node 15-171).  
*Source ticket AC4: "Add an edit button next to the actions icon on Manage Companies."*

**AC2: Edit button opens the edit company modal**
Given a Back Office admin clicks the "edit" button on a specific company row,  
When the click registers,  
Then the edit company modal opens, pre-populated with that company's data.  
*Source ticket AC5: "The edit button opens the edit company modal."*

**AC3: Edit action is keyboard/screen-reader accessible**
Given a Back Office admin navigates the table via keyboard,  
When they tab to a row's "edit" button and activate it,  
Then the same modal opens as with a mouse click.  

### Edge Cases
- **Company being edited is archived/deleted between page load and click** → show an error/toast and refresh the table rather than opening a modal for a company that no longer exists
- **Rapid double-click on "edit"** → single modal open, not duplicate modals
- **Admin lacks permission to edit a specific company** → confirm visibility/disabled rules (not specified in source ticket)

### Technical Notes
- Confirm the edit company modal referenced already exists (ticket implies it does: "opens the edit company modal")
- This story is functionally identical in shape to Story 2 but targets a different table/modal — do not merge into Story 2, since Manage Users and Manage Companies are independently deliverable and testable

### Out of Scope
- The internal behavior/fields/save logic of the edit company modal itself (assumed pre-existing)
- The Novatiq configuration entry point covered in Stories 4–5

---

## Story 4: Novatiq Configuration Entry Point on Manage Companies Table

**As a** Back Office admin,
**I want to** configure a company's Novatiq partner settings from the Manage Companies table,
**So that** I can set up Novatiq partners for a company without leaving the table view.

### INVEST Check
- [x] **Independent** — Additive column/action; does not require Story 1, 2, or 3, though it likely ships alongside Story 3 since both touch Manage Companies row actions
- [x] **Negotiable** — Whether this is a column-level action, a row action, or part of the edit-company modal is flexible pending design detail
- [x] **Valuable** — Lets admins manage partner configuration inline, reducing context-switching to a separate screen
- [x] **Estimable** — Depends on confirming whether the "relevant modal" (AC7) is new or existing (see Open Questions) — this significantly affects size
- [x] **Small** — Scoped to opening the configuration surface only; does not include the display logic (that's Story 5)
- [x] **Testable** — Modal-open behavior is directly verifiable once the entry point is defined

### Acceptance Criteria

**AC1: Novatiq configuration control is added to the table**
Given a Back Office admin views the Manage Companies table,  
When the table renders,  
Then a Novatiq configuration control is present (per Figma node 15-171).  
*Source ticket AC6: "Add the novatiq configuration to the table."*

**AC2: Configuring Novatiq opens the relevant modal**
Given a Back Office admin interacts with the Novatiq configuration control for a specific company,  
When they trigger it,  
Then the relevant Novatiq configuration modal opens, scoped to that company.  
*Source ticket AC7: "When configuring the novatiq opens the relevant modal."*

**AC3: Modal reflects the company's current Novatiq configuration**
Given a company that already has Novatiq partners configured,  
When the configuration modal opens for that company,  
Then it shows the currently configured partners, not a blank form.  

### Edge Cases
- **Company has no Novatiq partners configured yet** → modal opens in an empty/add state rather than erroring
- **Company is deleted/archived between page load and click** → show an error/toast and refresh the table rather than opening a modal for a company that no longer exists
- **Concurrent edits** — two admins configuring the same company's Novatiq partners at the same time; confirm last-write-wins vs. a conflict warning (not specified in source ticket)

### Technical Notes
- **Critical open item:** the source ticket does not clarify whether "the relevant modal" (AC7) is a net-new modal or an existing one being reused — this must be resolved before estimating, since it changes this story's size substantially
- Confirm whether this entry point lives in the actions column (alongside the new edit button from Story 3) or elsewhere in the row/table per Figma

### Out of Scope
- The display/truncation logic of configured partners in the table itself (covered in Story 5)
- Deleting or fully removing a company's Novatiq configuration, unless confirmed in scope during refinement

---

## Story 5: Display Configured Novatiq Partners in Manage Companies Table

**As a** Back Office admin,
**I want to** see a company's configured Novatiq partners directly in the Manage Companies table, truncated after two,
**So that** I can scan partner configuration at a glance without opening each company's modal.

### INVEST Check
- [x] **Independent** — Pure display/rendering logic; can be built once Story 4's configuration exists, but the display itself doesn't require Story 4 to ship first if seeded with existing data — flagged as sequenced below since it needs configured data to show anything meaningful
- [x] **Negotiable** — Exact truncation UI (e.g., "+2 more" vs. a tooltip) is flexible per Figma
- [x] **Valuable** — Gives admins an at-a-glance view of partner configuration across all companies
- [x] **Estimable** — Single column/cell rendering with a defined truncation rule
- [x] **Small** — One display rule, one table
- [x] **Testable** — Truncation behavior is explicit and directly verifiable (max of 2, then truncate)

### Acceptance Criteria

**AC1: Configured Novatiq partners are shown in the table**
Given a company has one or more Novatiq partners configured,  
When the Manage Companies table renders that company's row,  
Then the configured Novatiq partners are displayed in the row (per Figma node 15-171).  
*Source ticket AC8 (part 1): "The Novatiq configuration should then show in the table with the Novatiq partners..."*

**AC2: Display truncates after 2 partners**
Given a company has more than 2 Novatiq partners configured,  
When the row renders,  
Then only the first 2 partners are shown, followed by a truncation indicator (e.g., "+N more").  
*Source ticket AC8 (part 2): "...max of 2 and then truncate."*

**AC3: No truncation indicator when 2 or fewer partners are configured**
Given a company has exactly 1 or 2 Novatiq partners configured,  
When the row renders,  
Then both/all are shown with no truncation indicator.  

**AC4: No partners configured shows a clear empty value**
Given a company has no Novatiq partners configured,  
When the row renders,  
Then the cell shows a clear placeholder (e.g., "—" or "None") rather than a blank cell.  

### Edge Cases
- **Exactly 2 partners** — confirm no truncation indicator appears (AC3 covers this, but flag with design to confirm the boundary)
- **Truncation indicator interaction** — confirm whether "+N more" is static text or an interactive element (e.g., tooltip/expand) showing the full list (not specified in source ticket)
- **Partner name length** — long partner names combined with the 2-max truncation could still overflow the cell width; confirm truncation/ellipsis behavior at the text level too

### Technical Notes
- Depends on Story 4's configuration modal existing to populate real data for testing, but the rendering logic itself can be built in parallel against seeded/mock data
- Confirm the truncation indicator's interaction model with design before estimating

### Out of Scope
- Editing partners directly from the truncated display (must go through the Story 4 modal)
- Sorting/filtering the Manage Companies table by Novatiq partner

---

## Story Dependencies

```
Story 1 (Manage Users empty state) — independent
Story 2 (Manage Users edit action) — independent
Story 3 (Manage Companies edit action) — independent, shares a row/actions area with Story 4
Story 4 ──→ Story 5 (Story 5 needs Story 4's configured data to render meaningfully)
```

## Suggested Sprint Ordering
1. **Story 1 and Story 2** can start immediately — no open questions block estimation
2. **Story 3** can start immediately alongside Story 2 (same shape, different table)
3. Resolve the "new modal vs. existing modal" question for **Story 4** before sprint commitment — it materially changes scope
4. **Story 4** before **Story 5** — the display story needs real configured data (or seeded mock data) to be meaningfully testable
5. Confirm the Novatiq entry point's placement relative to Story 3's edit button, since both land in the same row/actions area

---

## Open Questions (flag before sprint-ready)
1. What was the second half of the source ticket's user story ("I want to see a...")? The ticket's story is cut off — confirm intent isn't lost in this decomposition. (All stories)
2. Should "no users at all" and "no users matching a filter/search" show the same empty state, or a distinct "no matches" variant? (Story 1)
3. Are there permission rules for who can edit a given user or company? (Stories 2, 3)
4. Is the Novatiq "relevant modal" (AC7) a new modal being built, or an existing one being reused/extended? This is the single biggest scope unknown in this ticket. (Story 4)
5. Where does the Novatiq configuration entry point live relative to the new edit button — same actions cluster, separate column, or elsewhere? (Story 4)
6. Is the "+N more" truncation indicator static or interactive (tooltip/expand to see the full partner list)? (Story 5)
7. How are concurrent edits to a company's Novatiq configuration handled? (Story 4)

## Related Context
- **Source ticket:** [ClickUp 869e7dqpa](https://app.clickup.com/t/869e7dqpa)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Sibling story sets (same epic):** [Admin API Keys Table](user-stories-admin-api-keys-table-2026-07-23.md), [Partner Activity Log Empty State](user-stories-partner-activity-log-empty-state-2026-07-23.md), [Admin Activity Log Empty State](user-stories-admin-activity-log-empty-state-2026-07-23.md), [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md), [Upload Activity Status Column](user-stories-dataset-upload-activity-status-column-2026-07-23.md), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md)
- **Design:** [Figma — Back Office, node 15-171](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=15-171)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Back Office-area stories
