# Product Brief: Dataset Deletion Blocked by Rejected Share

**Area:** Platform
**Author:** chess@omnisient.com | **Date:** 2026-07-02
**Status:** Proposed
**Pipeline stage:** Opportunity Framing

---

## Context

- **Strategic fit:** Self-serve is the platform direction — clients should be able to manage their own datasets without Omnisient staff intervention. A deletion block caused by a stale share state directly undermines this and forces a support touchpoint.
- **Related surface:** Web App › Datasets › My Datasets › Available. Intersects with the Dataset Share Agreement model and deletion validation logic.
- **Operational:** The platform's deletion guard is checking for the existence of a share relationship without accounting for the share's state. Declined, Deactivated, and Locked shares are terminal — no collaboration is happening — yet they continue to block the owner from deleting their own dataset.

---

## Problem

**Who has this problem?**
- **Dataset owner (Company A):** Wants to delete a dataset they own, but the platform blocks them with a message stating the dataset is being shared — even though the share is in a terminal state (Declined, Deactivated, or Locked).

**What is the problem?**
When Company A initiates a dataset share to Company B, the platform places a guard on deletion to protect an active collaboration. This is correct behaviour when a share is New or Accepted. But when a share reaches a terminal state — Declined (partner rejected it), Deactivated, or Locked (share duration expired) — no collaboration is happening or can happen. The deletion guard does not account for this: it continues to treat all share states as blocking. Company A cannot delete their own dataset without Omnisient staff manually resolving the stale relationship.

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| Observed in product | Deletion attempted on Available dataset with rejected share → blocked with share-active error message | confirmed |
| Platform behaviour | Share rejection does not clear the deletion guard — terminal share state and active share state are treated identically by deletion validation | confirmed |
| Self-serve direction | Clients are expected to manage their own dataset lifecycle; this block creates an unexpected hard dependency on staff | indicated |

**Impact of not solving:**
Dataset owners who have initiated and had a share rejected are stuck. They cannot clean up their dataset library without raising a support request. Each instance is a staff-assisted manual resolution that shouldn't exist — and erodes trust in the platform's dataset management as self-serve.

---

## Why Now

- **Correctness:** Declined, Deactivated, and Locked shares are terminal — no collaboration is active. The deletion guard treating them identically to New/Accepted is a logic defect, not a missing feature.
- **Self-serve commitment:** Every support touchpoint caused by a platform logic gap is a direct cost against the self-serve roadmap. This is fixable.
- **Low blast radius:** The fix is scoped to deletion validation logic — only New and Accepted shares should block deletion. No data model changes required.
- **Opportunity cost:** Every week this is unfixed, dataset owners hit the block and raise support tickets. CS absorbs the overhead; clients lose confidence in self-serve.

---

## Solution Direction

**Approach:** Update the dataset deletion validation logic to distinguish between active share states (New, Accepted) and terminal share states (Declined, Deactivated, Locked). Only New and Accepted shares should block deletion. When all shares on a dataset are in terminal states, the owner's deletion rights should be fully restored.

**Delivery model:** Platform (backend validation logic fix + UI message accuracy)

**What this IS:**
- Fix deletion guard to permit deletion when all associated shares are in terminal states (Declined, Deactivated, Locked)
- Optionally: update the error message to be state-specific if a pending/accepted share genuinely blocks (more accurate than a generic "being shared to" message)

**What this is NOT:**
- Changes to the share acceptance/rejection flow itself
- Changes to how active (pending or accepted) shares block deletion — that guard is correct
- A redesign of the Dataset Share Agreement model or connection management
- Auto-deletion of rejected shares (owner retains visibility of share history)

---

## Impact & Effort

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| Dataset deletion success rate when all shares are terminal (Declined, Deactivated, or Locked) | 0% (always blocked) | 100% (unblocked) | H |
| Staff-assisted resolution tickets for this scenario | [PLACEHOLDER] | 0 after fix | H |

**Effort:** XS — 1 sprint or less. Scoped to deletion validation logic; no data model or UI flow changes.
**Confidence in estimate:** High — this is a logic defect in a single validation path, not a feature build.

---

## The Ask

- [ ] Approve to proceed to PRD

**Decision needed by:** Next sprint planning
**Decision maker:** Tegan

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| Other delete guards (e.g. "in active project") may use a similar pattern and have the same terminal-state blind spot | M | M |

**Open questions:**
- [ ] Do other delete guards (e.g. "in active project") use a similar pattern and have the same terminal-state blind spot? — Engineering to confirm during discovery.

**Confirmed:**
- Full share state model:
  - Partner Datasets: New, Accepted, Declined, Locked
  - Dataset Shares: New, Accepted, Declined, Deactivated, Locked
- Terminal states (should NOT block deletion): Declined, Deactivated, Locked (share duration expired)
- Blocking states (should block deletion): New, Accepted
- Activity logs (the record of share creation and decline, per company) are company-level event records — they persist independently after dataset deletion. No cascade or orphan concern.

**No open questions remain.** All share states confirmed, terminal/blocking classification complete.
