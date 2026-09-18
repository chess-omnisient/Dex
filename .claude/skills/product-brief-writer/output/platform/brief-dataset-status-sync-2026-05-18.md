# Product Brief: Dataset Status Consistency Fix

**Area:** Platform  
**Author:** Chess | **Date:** 2026-05-18  
**Status:** Proposed  
**Pipeline stage:** Opportunity Framing  
**ClickUp ref:** [869bbv7dj](https://app.clickup.com/t/869bbv7dj)

---

## Context

- **Strategic fit:** Platform stability and reliability — correct status display is foundational to safe dataset consumption across all downstream flows (marketplace, analytics, connections)
- **Related products:** Datasets module, Web App, Hydration service
- **Affected area:** `[dat].[DataCollections]` / `[dat].[DataCollectionDetails]` — the two tables that govern dataset status are written to inconsistently across flows
- **Discovery source:** Reported by Rudy (MAF / UAE) — cust_id change triggered rehydration but UI showed 'Ready' instead of 'Processing'

---

## Problem

**Who has this problem?**
- All clients who use the Datasets module — anyone who triggers a rehydration via cust_id change or dedupe field change is exposed
- Platform engineering — no documented rule exists for which table owns status in which flow

**What is the problem?**  
When a dataset goes through rehydration (triggered by a customer identifier or dedupe field change), the dataset status does not update in the UI. The UI reads status from `[dat].[DataCollectionDetails]`, but rehydration only writes status to `[dat].[DataCollections]`. As a result, users see 'Ready' on a dataset that is actively being rebuilt — creating risk of stale or corrupted data being consumed downstream.

This is not an isolated bug. The status write pattern is inconsistent across all dataset lifecycle flows with no single source of truth:

| Flow | Writes to DataCollections | Writes to DataCollectionDetails |
|---|:---:|:---:|
| New Upload | ✓ | ✓ |
| Existing Upload | — | ✓ |
| PII Leak detection | — | ✓ |
| Rehydration (cust_id / dedupe change) | ✓ | — ← **Bug** |
| Prepared Datasets | ❓ | ❓ (unknown) |

There is no enforced contract — which table is authoritative depends on which flow you're in. This is a latent reliability risk for every flow, not just rehydration.

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| Rudy (MAF, UAE) — [869bbv7dj](https://app.clickup.com/t/869bbv7dj) | Reproduced: cust_id change → rehydration triggered → status stayed 'Ready' in UI | confirmed |
| Code review (Rudy) | Root cause identified: UI reads DataCollectionDetails; rehydration writes DataCollections only | confirmed |
| Prepared Datasets flow | Status source unknown — not yet investigated | assumed |
| Other rehydration triggers (future) | Any new flow that writes DataCollections only is silently broken | assumed |

**Impact of not solving:**  
A downstream consumer (analytics, cleanroom, marketplace) treats a rehydrating dataset as ready and runs queries against stale or mid-rebuild data. This is a silent data integrity risk — the system doesn't error, it just serves wrong results. For clients like MAF, this could affect campaign matching or audience accuracy without any visible warning.

---

## Why Now

- **Client affected:** MAF (UAE) is on the impacted dataset (`mafcrfdata`) — no workaround exists
- **No workaround:** Confirmed in the ticket — the user has no way to know the dataset is rebuilding
- **Systemic risk:** The root cause is architectural — every rehydration event is silently broken
- **Prepared Datasets unknown:** We don't know if this affects a third flow — deferring increases risk surface
- **Sprint 6 window:** Platform squad has capacity — fixing this now avoids it becoming a Sev 1 in a higher-stakes client environment

---

## Solution Direction

**Approach:** Update the rehydration write path to propagate status changes to `[dat].[DataCollectionDetails]` when `[dat].[DataCollections]` is updated. This makes rehydration consistent with the new upload flow — both tables reflect the current state. Confirmation needed from the hydration service owner (Werner) that DataCollectionDetails is not deliberately bypassed during rehydration before committing to this approach.

**Delivery model:** Backend fix — targeted change to the rehydration write path. No UI changes, no new surfaces.

**What this IS:**
- Propagate status to DataCollectionDetails on rehydration trigger (cust_id change, dedupe field change)
- Investigate and document Prepared Datasets status source
- Document the authoritative status rule per flow as part of AC

**What this is NOT:**
- A redesign of the dataset status model
- Changes to upload, PII leak, or any other existing flows
- A UI change

---

## Impact & Effort

**Impact:**
Any client who triggers a rehydration (cust_id or dedupe field change) currently sees the wrong dataset status — 'Ready' when the data is actively rebuilding. Fixing this eliminates silent data corruption risk for all rehydration events across all clients and regions. Secondary benefit: documenting the status write rule per flow closes a latent risk in Prepared Datasets and any future flows.

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| Rehydration status accuracy | 0% (always shows wrong status) | 100% | H |
| Flows with documented status rule | 0 / 5 | 5 / 5 | H |
| Prepared Datasets status source | Unknown | Defined | M |

**Effort:** Small — 5 story points (already sized). Targeted backend change to the rehydration write path. No UI work, no migration, no new surfaces.

**Confidence in estimate:** Medium. Root cause is confirmed and the fix is well-scoped. Two unknowns that could expand scope: (1) whether DataCollectionDetails is deliberately bypassed during rehydration; (2) the Prepared Datasets status source is uninvestigated and could reveal a second fix needed.

---

## The Ask

- [ ] Approve fix for rehydration flow: propagate status to `[dat].[DataCollectionDetails]` on cust_id / dedupe field change
- [ ] Approve investigation of Prepared Datasets status source (within same sprint)
- [ ] Approve documentation of authoritative status rule per flow (acceptance criteria for Done)

**Decision needed by:** Before Sprint 6 sprint planning  
**Decision maker:** CPO / Engineering Lead

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| Fix breaks Existing Upload or PII Leak flow (shared write path) | M | H |
| Prepared Datasets uses a third status model — scope expands | M | M |
| Other rehydration triggers (not yet known) follow same broken pattern | L | H |

**Open questions:**
- [ ] Is DataCollectionDetails deliberately bypassed during rehydration? If Werner had a reason for excluding it (e.g. the details record is recreated fresh mid-rehydration), Option A breaks things and Option B becomes necessary. **Blocker before dev starts.**
- [ ] What is the status source for Prepared Datasets? It's the only flow with no documented write behaviour — could be fine, or could have the same bug. Must be checked before closing as Done.
- [ ] Does the UI ever fall back to DataCollections when DataCollectionDetails is missing or stale? If fallback logic already exists, it changes how we test the fix and suggests the read path is more complex than assumed.
