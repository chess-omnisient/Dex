# User Stories: Admin — Users & Permissions

**Area:** Platform
**Source:** ClickUp task [8699phn0t](https://app.clickup.com/t/8699phn0t) — "UXUI | Admin | Users" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-24
**Status:** Draft

---

## Context

*No `context/` files exist yet for this skill (no company.md, personas.md, or product-platform.md), and no separate PRD covers this ticket. Everything below is derived directly from the ClickUp ticket's description.*

- **Product:** Omnisient platform — Admin module (Manage Users table, User Permissions screen)
- **Target user:** Platform admin — an internal user who manages other users' access and permissions
- **User JTBD:** Not documented in a personas file for this area. Inferred from the ticket: an admin needs to quickly edit a user without hunting through a menu, and needs to configure a long list of permissions (77 total, per the ticket) without losing track of what's already been granted.
- **List:** Product Roadmap | **Status:** Open | **Priority:** Normal
- **Tags:** uxui
- **Epic:** Part of "UXUI | Align Pages to X2"
- **Dependencies:** Ticket has 1 recorded dependency in ClickUp — not resolved here; confirm before sprint if it blocks this story.
- **Sprint/cycle:** Not yet assigned

**Note on scope:** Combined into a single story at your request, matching how the source ticket bundles the Manage Users table and Permissions screen together. Flagging one INVEST trade-off below (see Small).

---

## Story: Admin Users — Table Edit Access, Empty State, and Permissions Screen Overhaul

**As a** platform admin,  
**I want to** see a clear empty state and dedicated edit button on the Manage Users table, and search, count, and expand/collapse permissions by section on the Permissions screen,  
**So that** I can manage users and configure their access — including a 77-item permissions list — without misreading a blank table, hunting through a menu, or losing track of what's already been granted.

### INVEST Check
- [ ] **Independent** — Two separable surfaces (Users table, Permissions screen) bundled into one story; no data dependency between them, but they could ship as two independent stories
- [x] **Negotiable** — Empty-state copy, icon placement, column count, and modal reuse are all flexible per design
- [x] **Valuable** — Removes ambiguity for a blank table, speeds up the most common row action, and makes a long permissions list navigable and auditable at a glance
- [x] **Estimable** — Reuses existing modal patterns; components (search, counter, expand/collapse, checkbox) are standard patterns
- [ ] **Small** — Spans two distinct screens with 11 combined ACs; larger than a typical single-sprint story — see note below
- [x] **Testable** — Each AC below is independently verifiable

**Note on Small/Independent:** this story covers two UI surfaces that don't share components or state. If sprint capacity is tight, split at the "---" break below into "Users Table" and "Permissions Screen" stories — each would pass Small and Independent cleanly on its own.

### Acceptance Criteria

**AC1: Empty state shown when there are no users**  
Given a platform admin navigates to the Manage Users table,  
When there are no users to display,  
Then an empty state renders in place of the table.

**AC2: Table renders normally when users exist**  
Given a platform admin navigates to the Manage Users table,  
When one or more users exist,  
Then the table renders normally and the empty state does not appear.

**AC3: Edit is removed from the actions menu**  
Given a platform admin opens the actions menu on a user row,  
When the menu renders,  
Then "Edit" no longer appears as a menu item.

**AC4: Edit button appears next to the actions icon**  
Given a platform admin views a row in the Manage Users table,  
When they look at the row's action area,  
Then a dedicated edit button appears next to the actions icon.

**AC5: Edit button opens the edit user modal**  
Given a platform admin clicks the edit button on a specific user row,  
When the click registers,  
Then the edit user modal opens, pre-populated with that user's data.

**AC6: Search bar filters permissions**  
Given a platform admin is on the Permissions screen,  
When they type a query into the search bar in the top card,  
Then only permissions matching the query remain visible across the section cards.

**AC7: Selected-count summary updates live**  
Given a platform admin is on the Permissions screen,  
When permissions are toggled on or off,  
Then the top card's count (e.g. "55/77 permissions allowed") updates immediately to reflect the current selection.

**AC8: Expand all opens every section card**  
Given a platform admin is on the Permissions screen with one or more section cards collapsed,  
When they click "Expand all,"  
Then every section card opens to show its permissions.

**AC9: Collapse all closes every section card**  
Given a platform admin is on the Permissions screen with one or more section cards expanded,  
When they click "Collapse all,"  
Then every section card closes, showing only its header.

**AC10: Permissions are grouped into per-section cards with headings and icons**  
Given a platform admin is on the Permissions screen,  
When the page loads,  
Then each platform section renders as its own card with a heading and a relevant icon, and permissions within each card align in equal columns.

**AC11: Select-all checkbox toggles an entire section**  
Given a platform admin views a section card's header,  
When they tick the select-all checkbox at the right of that header,  
Then every permission within that card is enabled (and unticking disables all of them).

**AC12: Section header shows an allowed-permissions chip, colored by completeness**  
Given a platform admin views a section card's header,  
When the card renders,  
Then a chip next to the heading shows the count of allowed permissions in that section (e.g. "2/3"), displayed in green if all permissions in the section are allowed, or blue if only a portion are allowed.

### Edge Cases
- No users at all vs. no users matching an active search/filter — confirm whether both use the same empty state or a distinct "no matches" variant
- Data fetch fails outright (error state) — must not silently reuse the empty state for a failed fetch; out of scope here
- Row where the current admin is editing their own account — confirm no special-casing is needed
- Search query matches permissions in a currently-collapsed card — confirm whether matching cards auto-expand to show results
- Search query with zero matches — needs an explicit no-results state
- Partial selection within a card — confirm whether the select-all checkbox shows an indeterminate state rather than plain checked/unchecked
- Very long permission names — confirm column alignment still holds
- Select-all interaction with search active — confirm whether it toggles all permissions in the section or only the currently-filtered subset

### Technical Notes
- Edit modal is presumed to be the existing "edit user" modal already used elsewhere in Admin; confirm reuse vs. a new variant
- Selected-count control depends on a single source of truth for permission state shared across all section cards and the search/expand controls
- Confirm the "77 permissions" total is fixed or can vary by user role/tenant — affects whether the counter is hardcoded or computed

### Out of Scope
- Any other actions-menu items besides Edit
- Bulk edit
- Changing which permissions exist or how they're grouped into sections
- Bulk permission templates/presets across users

---

## Open Questions
- The ticket lists 1 dependency in ClickUp that wasn't surfaced in this summary view — confirm what it is before sprint planning, in case it affects scope.
- No personas.md or product-platform.md exists yet, so target-user framing above is inferred from the ticket alone, not sourced from documented JTBD.
- If this doesn't fit in one sprint, split back into the two sub-stories noted under Small above — AC1-5 (Users table) and AC6-11 (Permissions screen).

## Related Context
- **ClickUp task:** [8699phn0t](https://app.clickup.com/t/8699phn0t)
- **Parent epic:** [869e23kfj](https://app.clickup.com/t/869e23kfj) — "UXUI | Align Pages to X2"
