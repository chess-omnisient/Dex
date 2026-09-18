# User Stories: Back Office — Manage Users, Manage Companies

**Area:** Platform
**Source:** ClickUp task [869e7dqpa](https://app.clickup.com/t/869e7dqpa) — "UXUI | Back Office | Users" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*No `context/` files exist yet for this skill (no company.md, personas.md, or product-platform.md), and no separate PRD covers this ticket. Everything below is derived directly from the ClickUp ticket's description, ACs, and linked Figma.*

- **Product:** Omnisient platform — Back Office module (Manage Users table, Manage Companies table)
- **Target user:** Back Office admin — an internal platform user who manages platform users and companies
- **User JTBD:** Not documented in a personas file for this area. Inferred from the ticket: the Back Office admin needs to edit users and companies without leaving the table view, and needs an empty table to clearly read as "no data" rather than "broken."
- **PDLC Phase (ClickUp):** Ready for Dev | **Roadmap View:** Backlog | **Priority:** Normal
- **Squad:** UXUI
- **Design:** [Figma — Back Office, node 15-171](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=15-171)
- **Epic:** Part of "UXUI | Align Pages to X2"
- **Sprint/cycle:** Not yet assigned

**Note on scope:** the source ticket's Novatiq partner-configuration ACs (originally AC6–AC8) have been removed from this story at your request. This story now covers only the Manage Users empty state and the edit actions added to both tables. The ticket's own "As a platform user, I want to see a..." sentence is also cut off in the source — see Open Questions.

---

## Story: Back Office Table Improvements — Empty State and Edit Actions

**As a** Back Office admin,
**I want to** see an empty state when Manage Users has no data, and edit users and companies directly from their tables,
**So that** I can manage platform users and companies without misreading blank data or leaving the table view.

### INVEST Check
- [x] **Independent** — Two closely related UI additions (empty state, edit actions) with no Novatiq/config dependency
- [x] **Negotiable** — Copy, icon placement, and modal reuse are all flexible per Figma
- [x] **Valuable** — Prevents a blank table from being misread as broken, and gives admins direct one-click access to editing
- [x] **Estimable** — Both pieces wire into existing modals/patterns; no unresolved scope blockers remain
- [x] **Small** — One empty state, two edit actions — fits comfortably in a sprint
- [x] **Testable** — Each AC below is independently verifiable

### Acceptance Criteria

**AC1: Empty state shown when there are no users**
Given a Back Office admin navigates to the Manage Users table,  
When there are no users to display,  
Then the empty state (per Figma node 15-171) renders in place of the table.  
*Source ticket AC1: "Add an empty state if there are no users."*

**AC2: Table renders normally when users exist**
Given a Back Office admin navigates to the Manage Users table,  
When one or more users exist,  
Then the table renders normally and the empty state does not appear.  

**AC3: Edit button appears next to the actions icon on Manage Users**
Given a Back Office admin views a row in the Manage Users table,  
When they look at the row's action area,  
Then an edit button appears next to the existing actions icon (per Figma node 15-171).  
*Source ticket AC2: "Add an edit button next to the actions icon."*

**AC4: Edit button opens the edit user modal**
Given a Back Office admin clicks the edit button on a specific user row,  
When the click registers,  
Then the edit user modal opens, pre-populated with that user's data.  
*Source ticket AC3: "The edit button opens the edit user modal."*

**AC5: Edit button appears next to the actions icon on Manage Companies**
Given a Back Office admin views a row in the Manage Companies table,  
When they look at the row's action area,  
Then an edit button appears next to the existing actions icon (per Figma node 15-171).  
*Source ticket AC4: "Add an edit button next to the actions icon on Manage Companies."*

**AC6: Edit button opens the edit company modal**
Given a Back Office admin clicks the edit button on a specific company row,  
When the click registers,  
Then the edit company modal opens, pre-populated with that company's data.  
*Source ticket AC5: "The edit button opens the edit company modal."*

**AC7: Tooltip added next to "Is Admin Contact?" field**
Given a Back Office admin opens the edit user modal,  
When they view the "Is Admin Contact?" field,  
Then a tooltip appears next to it explaining what the field controls.  
*Source: new AC — "Edit user modal, add a tooltip next to 'Is Admin Contact?'"*

**AC8: "Back Office User" field relabeled**
Given a Back Office admin opens the edit user modal,  
When they view the field previously labeled "Back Office User,"  
Then it now reads "Is Back Office User?"  
*Source: new AC — "Update text 'Back Office User' to 'Is Back Office User?'"*

**AC9: Password fields shown directly instead of a change password button**
Given a Back Office admin opens the edit user modal,  
When the modal renders,  
Then the change password button no longer appears, and both password fields display directly in the modal instead.  
*Source: new AC — "Remove change password button and instead show both password fields."*

**AC10: Manage Users context menu updated to match design**
Given a Back Office admin opens the context menu on a row in the Manage Users table,  
When they view the menu,  
Then the "Manage Companies" item displays the updated icon, the reset two-factor authentication item reads "Reset 2-Factor Authentication" (previously "Reset Two Factor Authentication"), and the items appear in the order specified by the latest Figma design.  
*Source: new AC — "In the table context menu update the Manage Companies icon. Text on Reset 2-Factor Authentication has updated from 'Reset Two Factor Authentication'. Adjust order of context menu to align with designs."*

**AC11: Add user modal — tooltip and label updated**
Given a Back Office admin opens the add user modal,  
When they view the "Is Admin Contact?" field and the field previously labeled "Back Office User,"  
Then a tooltip appears next to "Is Admin Contact?", and the other field now reads "Is Back Office User?"  
*Source: new AC — "Add user modal - add a tooltip next to 'Is Admin Contact?', update text 'Back Office User' to 'Is Back Office User?'"*

**AC12: Manage Companies detail view icon colors match design**
Given a Back Office admin views the Manage Companies detail view,  
When they look at the Default Company and Admin Contact icons,  
Then both icons display the colors specified in the latest Figma design.  
*Source: new AC — "Manage companies detail view - Default company & Admin contact icon colour should reflect designs."*

**AC13: Manage Companies detail view context menu — disabled tooltips and updated icon**
Given a Back Office admin opens the context menu in the Manage Companies detail view,  
When a menu item is disabled, and when they view the "Manage Permissions" item,  
Then a tooltip explains why the disabled item is unavailable, and "Manage Permissions" displays the updated icon.  
*Source: new AC — "Manage companies detail view, context menu - add the disabled tooltips. Update manage permissions icon."*

**AC14: Edit user company — tooltip added to "Is Admin Contact"**
Given a Back Office admin opens the edit user company view from the Manage Companies detail view,  
When they view the "Is Admin Contact" field,  
Then a tooltip appears next to it explaining what the field controls.  
*Source: new AC — "Manage companies detail view, Edit user company - add tooltip to 'Is Admin Contact'."*

**AC15: Add user (Manage Companies detail view) — tooltip added and primary action relabeled**
Given a Back Office admin opens the add user view from the Manage Companies detail view,  
When they view the "Is Admin Contact?" field and the modal's primary action button,  
Then a tooltip appears next to "Is Admin Contact?", and the primary action button reads "Assign."  
*Source: new AC — "Manage companies detail view, Add User - add tooltip to 'Is Admin Contact?', update primary action to be 'Assign'."*

### Edge Cases
- No users at all vs. no users matching an active search/filter — confirm whether both cases use the same empty state or a distinct "no matches" variant
- Data fetch fails outright (error) — must not silently reuse the empty state for a failed fetch; out of scope here
- A user or company is deleted/archived between page load and clicking edit → show an error/toast and refresh the table rather than opening a stale modal
- Rapid double-click on an edit button → a single modal opens, not duplicates
- Admin lacks permission to edit a specific user or company → visibility/disabled rule not specified in source ticket
- Both password fields shown but left blank on save → confirm whether this means "no change" or triggers a validation error (AC9)
- The two password fields don't match → confirm expected validation/error messaging (AC9)

### Technical Notes
- Confirm whether an X2-standard empty-state component already exists elsewhere in Back Office to reuse for AC1
- Edit user modal's internal fields are no longer fully out of scope: AC7–9 change its tooltip, label, and password UI directly, though the edit company modal remains pre-existing/untouched
- Confirm tooltip copy/content for "Is Admin Contact?" (AC7) — not specified in source

### Out of Scope
- Novatiq partner configuration (entry point, modal, and table display) — removed from this story; track separately if still needed
- Internal save logic of the edit user and edit company modals (assumed pre-existing, aside from the field changes in AC7–9)
- Bulk edit across multiple users or companies
- Error/failed-fetch state handling for either table

---

## Open Questions (flag before sprint-ready)
1. The source ticket's user story is cut off ("I want to see a...") — confirm no intent was lost in this consolidation.
2. Should "no users at all" and "no users matching a filter/search" show the same empty state, or a distinct "no matches" variant? (AC1–2)
3. Are there permission rules for who can edit a given user or company? (AC3–6)
4. Should the removed Novatiq configuration ACs be tracked as a separate story/ticket, or are they no longer in scope at all?
5. What should the "Is Admin Contact?" tooltip say? (AC7, AC11, AC14, AC15)
6. Do the two password fields require matching/confirmation validation, and what happens if both are left blank on save? (AC9)
7. What is the updated Figma link/node for the Manage Users context menu (icon, copy, order)? Not yet provided — current story only references node 15-171 for the empty state/edit buttons. (AC10)
8. What copy should the disabled-item tooltips show, and which context menu items are disabled and under what condition (e.g., permission level)? (AC13)

## Related Context
- **Source ticket:** [ClickUp 869e7dqpa](https://app.clickup.com/t/869e7dqpa)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Design:** [Figma — Back Office, node 15-171](https://www.figma.com/design/Wo4PyjTmUe3xu3yTi5mNIQ/Back-Office?node-id=15-171)
- **Personas/JTBD:** Not yet documented for this skill area — candidate to seed a `context/personas.md` for future Back Office stories
