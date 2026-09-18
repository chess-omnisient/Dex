# User Stories: Dataset Upload Status Visibility

**Area:** Platform
**Source:** Problem definition — dataset upload status confusion (conversation 2026-05-19)
**Author:** chess | **Date:** 2026-05-19
**Status:** Draft

---

## Context

- **Product:** Omnisient data collaboration platform — dataset management
- **Target user:** Platform user (data analyst / business analyst uploading and using datasets)
- **Problem:** When a user uploads new data to an existing dataset, the dataset shows `ready` while the new uploads are in `processing`. Users assume their new data is already included in the dataset. Upload statuses are only visible via Dataset History — a secondary navigation step.
- **User JTBD:** When I add new data to a dataset, I want to know exactly what state my dataset is in, so I can trust the results I get when I use it in a project.
- **Sprint/cycle:** TBD

---

## Delivery Order

```
Story 1 (composite badge) ── can ship immediately as stopgap
Story 2 (status propagation) ─┐
                               ├── share upload status API work, ship together
Story 3 (inline progress)    ─┘
Story 4 (completion notification) ── independent, ship after Stories 2+3
```

---

## Story 1: Composite Status Badge (Stopgap)

**As a** platform user,
**I want to** see a secondary indicator on the dataset status when uploads are still processing,
**So that** I don't assume my newly uploaded data is already available in the dataset.

### INVEST Check
- [x] **Independent** — UI-only change, no dependency on other stories
- [x] **Negotiable** — Badge design and copy are flexible
- [x] **Valuable** — Immediately reduces user confusion without waiting for backend changes
- [x] **Estimable** — Small, well-scoped frontend change (~1–2 days)
- [x] **Small** — Single component update
- [x] **Testable** — Clear states to verify

### Acceptance Criteria

**AC1: Badge visible when uploads are processing**
Given a dataset has one or more uploads in `processing` state,
When a user views the dataset in the dataset list or dataset detail page,
Then the dataset status shows `Ready · [N] upload(s) processing` with a spinner or clock icon alongside the `ready` badge.

**AC2: Badge absent when all uploads complete**
Given all uploads for a dataset have reached `ready` or `failed` state,
When a user views the dataset,
Then only the base `ready` status is shown — no secondary indicator.

**AC3: Badge reflects accurate count**
Given a dataset has 3 uploads — 2 processing, 1 ready,
When a user views the dataset,
Then the badge reads `Ready · 2 upload(s) processing`.

**AC4: Failed uploads surfaced**
Given a dataset has an upload in `failed` state,
When a user views the dataset,
Then the badge reads `Ready · 1 upload failed` with an error indicator (not a spinner).

### Edge Cases
- All uploads fail → show `Ready · [N] upload(s) failed`, not just `ready`
- Mix of processing and failed → show both counts: `Ready · 1 processing · 1 failed`
- Upload count is 0 (no pending uploads) → show `ready` only, no badge

### Technical Notes
- Requires an API query on the dataset list/detail view: does this dataset have any uploads in `processing` or `failed` state?
- If the upload history endpoint already exists (used by Dataset History page), this query likely reuses the same data source
- Badge should poll or use a websocket/event to update without page refresh if feasible; otherwise a manual refresh trigger is acceptable for v1

### Out of Scope
- Changing the underlying `ready` status value on the dataset (Story 2)
- Showing upload details inline (Story 3)

---

## Story 2: Propagate Upload State to Dataset Status

**As a** platform user,
**I want** the dataset status to change to `updating` when my uploads are processing,
**So that** I immediately know the dataset does not yet contain all my data — without reading a secondary indicator.

### INVEST Check
- [x] **Independent** — Can be delivered without Story 3 (though best shipped together)
- [x] **Negotiable** — Exact status label (`updating`, `syncing`, `ingesting`) is flexible
- [x] **Valuable** — Fixes the root cause; `ready` no longer misleads
- [x] **Estimable** — Backend status logic + UI label update, well-scoped
- [x] **Small** — Single status field change + trigger logic
- [x] **Testable** — Status transitions are explicit and verifiable

### Acceptance Criteria

**AC1: Dataset status changes to `updating` when an upload starts**
Given a user initiates a new upload to an existing `ready` dataset,
When the upload enters `processing` state,
Then the dataset status changes to `updating`.

**AC2: Dataset status reverts to `ready` when all uploads complete**
Given a dataset is in `updating` state with one or more processing uploads,
When all uploads reach `ready` state,
Then the dataset status reverts to `ready`.

**AC3: Existing data remains queryable during `updating`**
Given a dataset is in `updating` state,
When a user attempts to use the dataset in a project or query,
Then the existing data is accessible and the UI displays a contextual note: "This dataset is updating — new uploads are not yet included."

**AC4: `updating` status is visible in the dataset list**
Given a dataset is in `updating` state,
When a user views the dataset list,
Then the dataset shows an `updating` status badge (distinct colour/icon from `ready`).

**AC5: Upload failure does not permanently block `ready`**
Given a dataset has one upload that failed and no other processing uploads,
When the failed upload is the last in the queue,
Then the dataset status reverts to `ready` (not `updating`) and the failed upload is surfaced separately (see Story 3).

### Edge Cases
- Multiple concurrent uploads: dataset stays `updating` until ALL are complete, not just the first
- Upload is cancelled mid-processing → treat as failed; revert dataset status to `ready` if no other uploads pending
- User adds a second upload while first is still processing → dataset remains `updating`, counter increments
- Upload pipeline times out → should transition upload to `failed`, not remain indefinitely in `processing`

### Technical Notes
- Key question before implementation: is dataset status a stored field (requires write trigger) or computed on-the-fly from child upload states (requires logic update only)?
- If stored: need a trigger when upload status changes → update parent dataset status
- New status value `updating` may require a DB migration if status is an enum
- Ensure `updating` is handled gracefully in all downstream consumers of dataset status (project creation, sharing agreements, API responses)

### Out of Scope
- Blocking dataset use while `updating` (AC3 confirms it remains accessible)
- Upload failure notifications (Story 4)

---

## Story 3: Inline Upload Progress on Dataset Page

**As a** platform user,
**I want** to see the status of my recent uploads directly on the dataset page,
**So that** I don't have to navigate to Dataset History to check whether my new data has finished processing.

### INVEST Check
- [x] **Independent** — Can be delivered without Story 2, though best shipped together
- [x] **Negotiable** — Section design, placement, and level of detail are flexible
- [x] **Valuable** — Eliminates a navigation step that currently hides critical status information
- [x] **Estimable** — New UI component + API call, clear scope
- [x] **Small** — Single page addition; reuses existing history data
- [x] **Testable** — States are explicit and verifiable

### Acceptance Criteria

**AC1: Recent uploads section visible on dataset detail page**
Given a dataset has had at least one upload (historical or active),
When a user opens the dataset detail page,
Then a "Recent uploads" section is visible without requiring navigation to Dataset History.

**AC2: Section shows filename, upload date, and status**
Given the "Recent uploads" section is displayed,
When a user views it,
Then each row shows: filename, upload initiated date/time, and current status (`processing`, `ready`, or `failed`).

**AC3: Processing uploads show live status**
Given an upload is in `processing` state,
When a user views the Recent uploads section,
Then that upload row shows a `processing` indicator (spinner or progress signal) that updates without a full page refresh (or refreshes on a reasonable poll interval).

**AC4: Section is limited to the N most recent uploads**
Given a dataset has many historical uploads,
When a user views the Recent uploads section,
Then the section shows the 5 most recent uploads with a "View all in history" link to the full Dataset History.

**AC5: Empty state handled**
Given a dataset has never had an upload (initial dataset only),
When a user views the dataset detail page,
Then the Recent uploads section is not shown (or shows an appropriate empty state).

### Edge Cases
- Failed upload in the list → row shows `failed` with an error indicator; tooltip or expandable message shows the failure reason if available
- Very long filename → truncate with ellipsis, full name on hover
- Upload still processing after an unusually long time → no special treatment in this story; timeout handling is a backend concern (see Story 2 technical notes)

### Technical Notes
- Dataset History page already fetches upload records — this story surfaces the same data on the dataset detail page; confirm the existing endpoint supports filtering to N most recent
- If the history endpoint does not exist as a standalone API (only rendered server-side), a new endpoint may be needed — align with engineering before estimating

### Out of Scope
- Replacing the Dataset History page (it remains for full audit trail)
- Upload cancellation from this section
- Retry failed uploads from this section (separate story if needed)

---

## Story 4: Upload Completion Notification

**As a** platform user,
**I want** to be notified when my dataset uploads have finished processing,
**So that** I can continue my work using the fully updated dataset without having to check manually.

### INVEST Check
- [x] **Independent** — No dependency on Stories 1–3; can be built in parallel
- [x] **Negotiable** — Notification channel (in-app, email, or both) and copy are flexible
- [x] **Valuable** — Removes the need to poll status; supports async workflows
- [x] **Estimable** — Trigger logic + notification delivery; effort depends on existing infrastructure
- [x] **Small** — Single trigger event with one or two notification outputs
- [x] **Testable** — Notification receipt and timing are verifiable

### Acceptance Criteria

**AC1: In-app notification sent when all uploads complete**
Given a user has one or more uploads processing on a dataset,
When all uploads reach `ready` state,
Then an in-app notification appears: "Your dataset [Dataset Name] has finished updating and is ready to use."

**AC2: Notification links to the dataset**
Given the in-app notification has been received,
When the user clicks it,
Then they are taken directly to the dataset detail page.

**AC3: Notification sent once per batch, not per upload**
Given a user initiates 3 uploads simultaneously,
When all 3 complete (regardless of order),
Then a single notification is sent — not one per upload.

**AC4: Failed upload triggers a separate notification**
Given one or more uploads fail,
When the failure occurs,
Then the user receives a distinct notification: "1 upload to [Dataset Name] failed. [View details]" — separate from the completion notification.

**AC5: Notification not sent if user is actively viewing the dataset page**
Given the user is currently on the dataset detail page when uploads complete,
When all uploads finish,
Then no in-app notification is sent (the inline status — Story 3 — is sufficient).

### Edge Cases
- User closes the browser before uploads complete → notification should still be delivered on next login or via email
- Upload takes more than 30 minutes → consider a "still processing" intermediate notification (out of scope for v1)
- User has notifications disabled → respect notification preferences; do not force-show

### Technical Notes
- Effort depends heavily on whether an in-app notification system already exists
- If no notification system exists, this story may need to be scoped down to email-only for v1
- Trigger: on upload status change to `ready` or `failed`, check if all sibling uploads for the parent dataset are resolved, then fire notification event

### Out of Scope
- Push notifications (mobile/browser)
- Configurable notification preferences (separate story)
- Notifications for other dataset events (sharing, deletion)

---

## Related Context
- **VoC Synthesis:** [VoC_Synthesis.md](../../06-Resources/Product_Management/VoC_Synthesis.md) — Theme 3 (Performance & Stability) and Theme 5 (Data Export & Download Friction) are directly related; users already anxious about processing states
- **JTBD:** Not yet formally documented for this persona — this feature is a candidate to seed `personas.md`
- **Platform glossary:** [Platform_Documentation.md](../../06-Resources/Product_Management/Platform_Documentation.md)
