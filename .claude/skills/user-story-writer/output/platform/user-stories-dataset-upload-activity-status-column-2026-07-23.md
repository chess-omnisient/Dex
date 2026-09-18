# User Stories: Datasets — Upload Activity Status Column

**Area:** Platform
**Source:** ClickUp task [8699phn12](https://app.clickup.com/t/8699phn12) — "UXUI | Upload Activity" (parent epic: [869e23kfj](https://app.clickup.com/t/869e23kfj) "UXUI | Align Pages to X2")
**Author:** chess | **Date:** 2026-07-23
**Status:** Draft

---

## Context

*Loaded from ClickUp — no `personas.md` or platform context files exist yet for this skill, so target user is taken directly from the ticket's stated user type.*

- **Product:** Omnisient platform — Datasets module, Upload Activity table
- **Target user:** Platform user (internal/customer user monitoring dataset upload activity)
- **PDLC Phase (ClickUp):** Backlog | **Roadmap View:** Backlog | **Platform Area:** Datasets
- **Request Type:** Feature Request | **Priority:** High
- **Design:** [Figma — Datasets, node 2-17907](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=2-17907)
- **Epic context:** Part of "Align Pages to X2" — the same initiative covered by the [Reports Table story set](user-stories-dataset-reports-view-empty-state-2026-07-23.md) and the [Dataset Schemas story set](user-stories-align-ui-dataset-schemas-2026-07-21.md), both written for sibling tickets under this epic.
- **Source ticket's single user story bundles 3 tightly-coupled ACs** (column rename, colour-coded pill, header tooltip) — all describe one cohesive capability (a clearer, glanceable status column), so they are kept as a single story rather than decomposed further. Splitting a header rename into its own story would produce a unit smaller than is useful to plan or estimate independently.
- **Sprint/cycle:** Not yet assigned (Roadmap View: Backlog)

---

## Story 1: Upload Status Column with Colour-Coded Pill

**As a** platform user,
**I want to** see an "Upload Status" column that shows each upload's current state as a colour-coded pill, with a tooltip explaining the column,
**So that** I can tell at a glance whether my uploads completed, are still running, or failed — without opening each row.

### INVEST Check
- [x] **Independent** — Pure frontend change to the Upload Activity table; no dependency on other stories in this epic
- [x] **Negotiable** — Exact pill shape, tooltip copy, and colour tokens are flexible within the Figma spec
- [x] **Valuable** — Lets users assess upload health at a glance instead of reading a plain-text status per row
- [x] **Estimable** — Single column: rename + conditional styling + a header tooltip
- [x] **Small** — One column in one table
- [x] **Testable** — Each status maps to one deterministic visual state

### Acceptance Criteria

**AC1: Column renamed to "Upload Status"**
Given a user views the Upload Activity table,
When the table renders,
Then the column previously labelled "Status" is labelled "Upload Status" (per Figma node 2-17907).
*Source ticket AC1: "Change 'Status' column name to 'Upload Status'."*

**AC2: Status displayed as a colour-coded pill**
Given an upload has a status of `complete`, `started`, or `failed`,
When a user views its row in the Upload Status column,
Then the status is shown as a pill coloured green (`complete`), amber (`started`), or red (`failed`), with the status text inside the pill.
*Source ticket AC2: "Displays the current status of the upload with a colour-coded pill. Green for complete, Amber for started, Red for failed."*

**AC3: Tooltip on the column header**
Given a user hovers over the "Upload Status" column header,
When the hover is sustained,
Then a tooltip appears reading: "This shows the status of your upload from Desktop Connect / Server Connect to the Omnisient Platform."
*Source ticket AC3: "Displays a tooltip on the column name 'Upload Status'."*

**AC4: Pill colour and text stay in sync**
Given an upload's status changes (e.g. `started` → `complete`),
When the table next reflects that upload's row,
Then the pill's colour and text both update together — never a mismatched colour/text pair.

### Edge Cases
- Null/missing status value on an upload row (e.g. a data gap) → not addressed by the 3 confirmed statuses; should not silently render a blank/uncoloured pill (see Open Questions)
- Touch devices where hover doesn't trigger (AC3) → tooltip needs a tap/focus-triggered equivalent, not hover-only
- Colour-blind users relying solely on pill colour → status text inside the pill (AC2) already provides a non-colour signal, so this is mitigated by design as specified

### Technical Notes
- Upload statuses are confirmed limited to `complete` / `started` / `failed` — no other states to design for
- A pill/badge component already exists on the platform (confirmed) — reuse it rather than building a new one; confirm it exposes green/amber/red variants, or extend it if not
- Tooltip copy confirmed: "This shows the status of your upload from Desktop Connect / Server Connect to the Omnisient Platform." — implies uploads can originate from either Desktop Connect or Server Connect; confirm the status column doesn't need a separate source/origin indicator (ticket doesn't ask for one, but the tooltip references both paths)
- Confirm colour tokens against Figma node 2-17907 rather than hand-picking green/amber/red hex values

### Out of Scope
- Changing the underlying upload status values or state machine (this story is display-only)
- Filtering/sorting the Upload Activity table by status (separate story if needed)
- Dataset-level status badges (covered by the separate dataset status story set, linked above)

---

## Open Questions (flag before sprint-ready)
1. Does the existing pill/badge component already support green/amber/red variants, or does it need extending?
2. How should a null/missing upload status render, given only 3 statuses are otherwise possible? (edge case, not expected in normal operation)
3. The tooltip references uploads coming from either Desktop Connect or Server Connect — does the Upload Status column (or row) need to indicate which source a given upload came from, or is that out of scope here?

## Related Context
- **Source ticket:** [ClickUp 8699phn12](https://app.clickup.com/t/8699phn12)
- **Parent epic:** [ClickUp 869e23kfj — "UXUI | Align Pages to X2"](https://app.clickup.com/t/869e23kfj)
- **Sibling story sets (same epic):** [Reports Table — View Action & Empty State](user-stories-dataset-reports-view-empty-state-2026-07-23.md) (2026-07-23), [Dataset Schemas](user-stories-align-ui-dataset-schemas-2026-07-21.md) (2026-07-21)
- **Related prior work:** [Dataset Upload Status Visibility](user-stories-dataset-upload-status-2026-05-19.md) (2026-05-19) — addresses dataset-level status propagation; this story is scoped to the Upload Activity table's own status column, a narrower display concern
- **Design:** [Figma — Datasets, node 2-17907](https://www.figma.com/design/zqQPXYwnW89M4PRuHccXEZ/Datasets?node-id=2-17907)
- **Personas/JTBD:** Not yet documented for this skill — candidate to seed `context/personas.md` for future Datasets-area stories
