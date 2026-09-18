# User Stories: Partner Datasets Empty State — Remove Blue Circle Icon

**Area:** Platform
**Source:** ClickUp task [OMNIC-218](https://app.clickup.com/t/869e79wyd) — "Remove the blue circle on the empty state on Partner datasets"
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type and the attached screenshot.*

- **Product:** Omnisient platform — Datasets module, Partner Datasets empty state
- **Target user:** Platform user with no partner dataset access yet
- **PDLC Phase (ClickUp):** Backlog | **Problem Assessment:** Minor Inconvenience | **Request Type:** Enhancement
- **Reference screenshot:** attached to the source ticket — shows the current empty state: illustration, "You don't have access to any partner datasets yet!" heading, "Setup a connection first." subtext, a **"Setup a connection" link prefixed with a small blue circle outline icon**, and a "Visit Our Knowledge Base" button below it
- **Design intent (per ticket):** "The empty state designs were updated to remove the blue circle before the action" — i.e., the small circle icon to the left of the "Setup a connection" link should be dropped, leaving the link text (and its trailing arrow icon) standalone
- **Sprint/cycle:** Not yet assigned (Backlog)

---

## Story 1: Remove Blue Circle Icon from Partner Datasets Empty State

**As a** platform user with no partner dataset access,
**I want to** see the "Setup a connection" action without a redundant blue circle icon in front of it,
**So that** the empty state matches the current design system and doesn't look visually cluttered or outdated.

### INVEST Check
- [x] **Independent** — Isolated visual change to one element on one empty state; no dependency on other stories
- [x] **Negotiable** — Exact spacing/alignment after removal is left to engineering, provided the circle itself is gone
- [x] **Valuable** — Keeps the page aligned with the updated design system, avoiding a visibly stale empty state
- [x] **Estimable** — Single icon removal, trivial to size
- [x] **Small** — One element, one page
- [x] **Testable** — Binary, visually verifiable pass/fail

### Acceptance Criteria

**AC1: Blue circle icon is removed from the action**
Given a user views the Partner Datasets empty state,  
When the page renders the "Setup a connection" action,  
Then no blue circle icon appears to the left of the link text.

**AC2: Remaining elements are unaffected**
Given the blue circle icon has been removed,  
When a user views the empty state,  
Then the heading, subtext, "Setup a connection" link text and its trailing icon, and the "Visit Our Knowledge Base" button remain unchanged in content and function.

**AC3: Layout holds after removal**
Given the blue circle icon has been removed,  
When a user views the "Setup a connection" row,  
Then the remaining text and icon are aligned cleanly with no leftover gap, orphaned spacing, or misalignment where the circle used to sit.

### Edge Cases
- **Icon removed via CSS `display:none` vs. removed from markup** → prefer removing from markup/component so no dead DOM node or unused asset remains
- **Shared component reuse** — confirm whether this circle icon is a shared "empty state action" component used elsewhere (e.g., other empty states across the platform); if so, scope whether this change should apply globally or only to the Partner Datasets instance (ticket only specifies Partner Datasets)
- **Responsive/mobile view** — verify the link row still aligns correctly at narrow widths once the icon is gone

### Technical Notes
- Reference screenshot on the source ticket shows the exact current state to diff against
- Check if the circle icon is a standalone element or baked into a shared empty-state action component before removing, to avoid breaking other empty states that may still want it

### Out of Scope
- Any other visual changes to the Partner Datasets empty state (heading copy, illustration, button styling)
- Changes to empty states on other pages, even if they share the same action component

---

## Story Dependencies

```
Story 1 (standalone — no dependencies)
```

## Suggested Sprint Ordering
1. Story 1 — only story in this set, ready to pick up as-is

---

## Related Context
- **PRD:** None — direct bug/enhancement ticket, no PRD
- **Source ticket:** [OMNIC-218](https://app.clickup.com/t/869e79wyd)
