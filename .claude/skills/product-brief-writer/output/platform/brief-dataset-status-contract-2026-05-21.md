# Product Brief: Dataset Status Contract

**Area:** Platform  
**Author:** Chess | **Date:** 2026-05-21  
**Status:** Proposed  
**Pipeline stage:** Opportunity Framing  
**Supersedes:** [brief-dataset-upload-status-aggregation-2026-05-21.md](brief-dataset-upload-status-aggregation-2026-05-21.md)  
**Companion fix (Sprint 6):** [brief-dataset-status-sync-2026-05-18.md](brief-dataset-status-sync-2026-05-18.md)

---

## Context

- **Strategic fit:** Platform reliability — the dataset status signal is the trust contract between the product and the user. It is the primary (and often only) indicator users rely on to decide when a dataset is safe to consume. That contract is currently broken in at least two confirmed places
- **Related products:** Datasets module, Web App, upload pipeline, hydration service
- **Affected area:** Dataset status display — no enforced rule exists for what `ready` means across different lifecycle triggers
- **Discovery source:** Two triggers confirmed by PM; a third (Prepared Datasets) remains uninvestigated

---

## Problem

**Who has this problem?**  
Any user who interacts with a dataset beyond its initial creation — specifically anyone who:
- Uploads new data to an existing dataset, or
- Changes a customer identifier or dedupe field (triggering rehydration)

This covers the standard ongoing workflow for most active dataset users.

**What is the problem?**  
The product displays `ready` on a dataset in at least two scenarios where the data is not actually ready:

**Trigger 1 — Upload to existing dataset**  
When a user uploads new data, child sub-dataset records are created and go through their own `processing` → `ready` (or `failed`) lifecycle. The parent dataset ignores this entirely — it retains its own status independently. A user can upload data, see `ready` on the parent, and proceed — not knowing their upload is still processing or has failed silently.

**Trigger 2 — Customer identifier change**  
When a user changes a customer identifier or dedupe field, a full dataset rehydration is triggered. The hydration service updates status in `[dat].[DataCollections]`, but the UI reads from `[dat].[DataCollectionDetails]` — which rehydration does not write to. The user sees `ready` on a dataset that is actively being rebuilt.

These are not isolated bugs. They are two instances of the same structural gap: **no enforced contract for what `ready` means across dataset lifecycle flows.** The existing brief (Sprint 6) fixes the rehydration write path. This brief addresses the upload aggregation gap and proposes establishing the status contract that prevents new triggers from silently breaking the same way.

| Trigger | Status failure type | Currently covered? |
|---|---|:---:|
| Upload to existing dataset | Aggregation gap — parent ignores child states | No |
| Customer identifier / dedupe change | Write-path bug — rehydration writes wrong table | Sprint 6 |
| Prepared Datasets | Unknown | Unknown |

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| PM observation | Parent stays `ready` while child uploads are `processing` or `failed` — reproduced in live product | confirmed |
| Rudy (MAF, UAE) — [869bbv7dj](https://app.clickup.com/t/869bbv7dj) | cust_id change → rehydration triggered → UI showed `ready` throughout | confirmed |
| Code review (Rudy) | Root cause confirmed: UI reads `DataCollectionDetails`; rehydration writes `DataCollections` only | confirmed |
| JTBD analysis (2026-05-21) | Root job opportunity score: 19/20 — highest priority job extracted from this problem space | indicated |
| Prepared Datasets flow | Status source unknown — not yet investigated | assumed |

**Impact of not solving:**  
Users consume, share, or build on datasets they believe are complete and stable — when they are actively rebuilding or missing uploaded data. The system does not error. It silently serves wrong results. For clients like MAF where dataset accuracy drives campaign matching or audience targeting, this is a correctness risk with no warning signal and no way for the user to detect it.

---

## Why Now

- **Sprint 6 is already fixing one trigger** — the rehydration write-path fix is scoped and pending Werner sign-off. Closing the upload aggregation gap in the following sprint addresses the second confirmed trigger while the architectural context is fresh
- **Same root cause, compounding risk** — both bugs exist because there is no authoritative status rule across flows. Every new dataset lifecycle trigger added in future is at risk of silently breaking status until this contract is defined
- **User trust degrades permanently** — every instance where a user acts on a `ready` status and gets wrong results reduces confidence in the signal. This is harder to recover than the mechanics
- **Prepared Datasets is a known unknown** — deferring means a third flow may be silently broken and we won't find out until a client reports it

---

## Solution Direction

**Approach:** Two-part fix:

1. **Upload status aggregation (this brief):** Parent dataset status derives from the worst-child state across all upload records. `ready` at the parent level means all children are `ready`. If any child is `processing`, the parent shows `processing`. If any child has `failed`, the parent surfaces a degraded or action-required state with inline detail ("3 of 4 uploads ready · 1 failed") and a direct path to the failed record.

2. **Status contract (spans both briefs):** As part of accepting either fix as Done, document the authoritative status rule per flow. Define what `ready` means. This prevents future flows from silently inheriting the same broken pattern.

**Delivery model:** Backend logic change (status aggregation) + lightweight UI indicator (badge/count on parent). No new screens.

**What this IS:**
- Composite status logic — parent derives state from child upload records
- `ready` means all children are ready — no exceptions
- Failed upload surfacing — unmissable signal at the parent level with remediation path
- Status contract documentation — authoritative rule per flow, required for Done on both briefs

**What this is NOT:**
- A redesign of the upload flow or dataset creation
- A new notifications or alerting system
- Changes to how sub-dataset records are created or stored
- A replacement for the rehydration write-path fix (Sprint 6)

---

## Impact & Effort

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| Parent status accuracy when uploads in flight | 0% — always shows `ready` | 100% | H |
| Parent status accuracy during rehydration | 0% — always shows `ready` | 100% (via Sprint 6 fix) | H |
| User-visible signal when upload fails | None | Unmissable badge + inline detail | H |
| Flows with documented status contract | 0 / 5 | 5 / 5 | H |
| Prepared Datasets status accuracy | Unknown | Defined + correct | M |

**Effort:** Small–Medium. Status aggregation logic is bounded. UI is additive (badge/count). Estimate: 3–8 story points depending on how upload sub-records are modelled and whether the rehydration fix creates a reusable propagation pattern.

**Confidence in estimate:** Low — needs a 1-day discovery spike to confirm the data model before sizing. Could collapse to 3 points if the Sprint 6 write-path pattern is reusable.

---

## The Ask

- [ ] Approve discovery spike (1–2 days): map how upload sub-records relate to the parent in `DataCollections` / `DataCollectionDetails`; confirm whether the Sprint 6 fix creates a reusable aggregation pattern
- [ ] Approve composite status logic + failure surfacing fix (Sprint 7 or alongside Sprint 6 if discovery confirms overlap)
- [ ] Require status contract documentation as acceptance criteria for Done on both this fix and the Sprint 6 rehydration fix
- [ ] Approve investigation of Prepared Datasets status source to close the third known unknown

**Decision needed by:** Before Sprint 7 planning  
**Decision maker:** CPO / Engineering Lead

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| Composite status logic conflicts with existing parent status writes | M | H |
| Sprint 6 rehydration fix and this fix touch the same write path — scope collision or reuse opportunity | M | M |
| Prepared Datasets uses a third broken status model — scope expands | M | M |
| Frequent upload failures create noise if surfaced aggressively | L | M |

**Open questions:**
- [ ] How are upload sub-records linked to the parent in the status tables? Foreign key, status flag, or other? Determines whether the fix is a query change or a write-path change. **Blocker for sizing.**
- [ ] Does the Sprint 6 fix (Werner) create a status propagation pattern reusable here? If yes, this may fold into Sprint 6 scope
- [ ] Is DataCollectionDetails deliberately bypassed during rehydration? (Carried from Sprint 6 brief — Werner confirmation still pending)
- [ ] Should `processing` children block the parent from `ready`, or is `partial` a distinct valid state? Product decision needed before dev starts
- [ ] What is the Prepared Datasets status source — and is it broken in the same way?
