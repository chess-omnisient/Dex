# Product Brief: Dataset Upload Status Aggregation

**Area:** Platform  
**Author:** Chess | **Date:** 2026-05-21  
**Status:** Proposed  
**Pipeline stage:** Opportunity Framing  
**Related brief:** [Dataset Status Consistency Fix](brief-dataset-status-sync-2026-05-18.md) — upstream write-path bug (rehydration)

---

## Context

- **Strategic fit:** Platform reliability — status signals are the trust contract between the system and the user. A misleading status on a dataset that has incomplete uploads is a silent data integrity risk identical in character to the rehydration bug already in flight
- **Related products:** Datasets module, Web App, upload pipeline
- **Affected area:** Parent dataset status display — does not reflect the aggregate state of its child upload records
- **Related:** The rehydration brief (`brief-dataset-status-sync-2026-05-18.md`) identified that `DataCollections` and `DataCollectionDetails` have no enforced status contract across flows. This brief surfaces the same structural gap in the upload path

---

## Problem

**Who has this problem?**  
Any user who uploads data to an existing dataset — which is the standard workflow for enriching or appending to a dataset over time.

**What is the problem?**  
When a user uploads to an existing dataset, one or more sub-dataset records are created and go through their own status lifecycle: `processing` → `ready` (or `failed`). The parent dataset, however, retains its own status independently — it stays `ready` regardless of what its child upload records are doing.

This means a user can:
1. Upload new data to a dataset
2. See the parent dataset marked `ready`
3. Use that dataset — or share it — believing all their data is included
4. Not realise their upload is still processing, or failed silently

The product is showing `ready` when it means *"the original data is ready — your new uploads may or may not be."* Users have no way to distinguish these states from the surface they trust.

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| PM observation (direct) | Parent dataset stays `ready` while child uploads are `processing` or `failed` — reproduced in live product | confirmed |
| JTBD analysis (2026-05-21) | Opportunity score 17/20 — highest-ranked job: "know when my dataset is truly ready to use" | indicated |
| Rehydration brief (2026-05-18) | Same architectural pattern: multiple flows, no single status authority, UI reads from one table | confirmed |
| Downstream usage patterns | Users share and consume datasets based on top-level status alone — no evidence they check sub-records | indicated |

**Impact of not solving:**  
Users run queries, trigger downstream jobs, or share datasets they believe are complete — when uploads are still processing or have failed. The product doesn't error. It serves silently incomplete data. For any client relying on dataset completeness for matching, scoring, or audience targeting, this is a correctness risk with no visible warning.

---

## Why Now

- **Same root cause as Sprint 6 bug:** The rehydration brief already surfaces the architectural problem — no enforced status contract across flows. Fixing rehydration without addressing upload aggregation leaves a second gap open and risks the same class of bug recurring
- **User trust is the casualty:** Every time a user discovers their `ready` dataset was incomplete, confidence in the status signal erodes. This is harder to recover than fixing the mechanics
- **Scope is bounded:** The upload path is already partially understood from the rehydration investigation. The fix is likely additive to work already planned
- **JTBD score:** Opportunity score of 17 — the highest-priority job extracted from this problem space. Unmet need is significant, satisfaction is near-zero

---

## Solution Direction

**Approach:** Introduce composite status logic for parent datasets — the parent status should reflect the worst-child state across all its upload records. A parent is only `ready` when all children are `ready`. If any child is `processing`, the parent shows `processing`. If any child has `failed`, the parent surfaces a degraded or action-required state. The parent status should never be treated as independent of its children.

**Delivery model:** Backend logic change + lightweight UI indicator. No new screens required.

**What this IS:**
- Status aggregation: parent derives state from child upload records
- Clear status semantics: `ready` means all children are ready
- Failure surfacing: failed uploads create an ambient signal at the parent level (badge, warning, count)
- Inline detail: "3 of 4 uploads ready · 1 failed" with a path to the failed upload

**What this is NOT:**
- A redesign of the upload flow
- A new notifications system
- Changes to how sub-dataset records are created or stored
- A replacement for the rehydration fix — that's a separate write-path bug

---

## Impact & Effort

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| Parent status accuracy when uploads in flight | 0% (always shows `ready`) | 100% | H |
| User-visible signal when upload fails | None | Unmissable badge / warning | H |
| Trust in dataset status signal | Low (broken by silent failures) | High | M |

**Effort:** Small–Medium. Core logic change is bounded — aggregate child states and propagate to parent. UI surface is additive (badge/count). Estimate: 3–8 story points depending on how the upload relationship is modelled in the DB and whether the fix can reuse the rehydration write path work.

**Confidence in estimate:** Low — needs discovery to confirm how upload sub-records relate to the parent in `DataCollections` / `DataCollectionDetails`, and whether the rehydration fix creates a reusable pattern.

---

## The Ask

- [ ] Approve discovery spike (1–2 days): map how upload sub-records relate to the parent dataset in the status tables; confirm whether the rehydration fix creates a reusable aggregation pattern
- [ ] Approve design of composite status logic and failure surfacing (same sprint or next)
- [ ] Sequence this alongside or immediately after the rehydration fix to close both gaps in the same architectural area

**Decision needed by:** Before Sprint 7 planning  
**Decision maker:** CPO / Engineering Lead

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| Composite status logic conflicts with existing parent status writes | M | H |
| Rehydration fix (Sprint 6) and this fix touch the same write path — scope collision | M | M |
| "Failed" upload surfacing creates alert fatigue if uploads fail frequently | L | M |

**Open questions:**
- [ ] How are upload sub-records linked to the parent in `DataCollections` / `DataCollectionDetails`? Is it a foreign key, a status flag, or something else? This determines whether the fix is a query change or a write-path change
- [ ] Does the rehydration fix (Werner's sign-off pending) create a status propagation pattern we can reuse here? If yes, this brief becomes an extension of Sprint 6 scope, not a new initiative
- [ ] Should a `processing` child block the parent from being `ready`, or should partial readiness be a distinct state (e.g. `partial`)? Needs product decision before dev starts
- [ ] What is the expected failure UX — inline warning, toast, email notification, or all three?
