# PRD: Dataset Upload Availability Column

**Area:** Platform
**Author:** Tegan | **Date:** 2026-06-24 | **Version:** v1
**Status:** draft
**Pipeline stage:** Solution Shaping
**Product brief:** N/A (feature committed; PRD authored directly)

---

## Context

- **Strategic fit:** Self-service is the platform direction — let clients resolve their own dataset state without contacting Omnisient staff. This feature surfaces upload state in the product so owners self-serve rather than raising a support request. Underpins Omnisient's #1 core capability, Data Ingestion, Quality & Standardisation.
- **Related surface:** Web App › Datasets › My Datasets › Available. Builds directly on the parent/child dataset status model.
- **Operational:** Series-B-stage org maturing its platform surfaces and reducing manual, staff-assisted support — the column removes a recurring "why does my dataset say Ready when my upload isn't?" support touchpoint by adding in a new "uploads" column.
- **Quarterly priority:** Platform strategy/goals docs not yet finalised. Flag: confirm this PRD maps to a current platform OKR.

---

## Problem

The Available Datasets table shows a single Parent status — and by design the Parent stays Ready while a new file uploaded to that dataset (its Child upload) is checked and hydrated in the background. This keeps the live dataset usable, but it has a hidden cost: when a re-upload gets stuck — Failed, Under Review, or Requires Review — the dataset still reads "Ready," so nobody is prompted or receives any signal that something is wrong. The owner isn't told their newest upload needs action; the table gives no indication at all.

(Shares and projects are created against snapshots of the data, so a stuck re-upload does not mean a partner is silently collaborating against bad data — the issue is purely the absence of a signal to the owner that an upload needs attention.)

A dataset increasingly accumulates multiple co-existing uploads under one parent (e.g. successive monthly transaction files). Today, the only ways to learn an upload's state are to check the Upload Activity Log, or to open the dataset's detail view and read the dataset history modal — both require leaving the table and digging in. Owners need that answer at a glance, from the Available table itself, without opening anything that their full dataset with all child uploads are available/not available.

### Evidence

### Context

- **Push/pull dynamic:** Internal-push — promote self-service so clients resolve upload state in-product rather than relying on Omnisient staff support.
- **Impact of inaction:** Owners continue to have no signal when a re-upload is stuck or failed; Omnisient staff keep absorbing support requests from clients who don't understand why a dataset says Ready when their latest upload isn't actually live.

---

## Target Segment

- **Internal team:** Customer Success / Omnisient staff — today field the "says Ready but isn't" questions; benefit from owners self-serving the signal.
- **Platform user / primary persona:** Dataset owner — the client-org user who registers datasets and performs re-uploads (Desktop Connect / Server Connect → Web App), and needs to know from the list whether every constituent upload is live and which one needs attention if not.

---

## Display Logic & Rules

**Display contract (the rule the column renders):**

**Which Child statuses count:**

**Existing uploads.** The column must compute correctly for datasets that already exist, including their historical uploads — not only uploads created after launch.

**Parent unaffected.** The Parent status stays Ready regardless of the fraction. The only thing that flips the Parent to Processing is a Customer Identifier change (existing behaviour, out of scope here).

**On 0/1.** The only way 0/1 occurs is a dataset with a single upload that has been marked for deletion: in that case the Parent shows Marked for Deletion and the fraction reads 0/1 (the upload is still counted until it is purged). It is otherwise not expected, because a registered dataset's founding upload was already taken to Ready by the registration flow.

### Icon matrix

The fraction always renders. Alongside it, an icon must show when an upload needs attention — using the existing-style attention icons (the same family used for PII leaks and high error rates today). Icons stack when more than one category is present.

A tooltip / hover on the column summarises the breakdown in words (e.g. "2 of 3 uploads ready · 1 requires review").

---

## System Impact

**Surfaces & subsystems touched**

**Cross-cutting concerns triggered**

**Blast radius / downstream effects**

Assumption (in scope to rely on, not to fix): because shares and projects run on data snapshots, an incomplete fraction does not mean a partner is querying bad data. Out of scope: any change to downstream access controls in the Own Data Prep tools (SQLPad / Jupyter) or in project usage.
Adjacency: touching Datasets → also consider existing uploads. Read-from here, not changed.

---

## Scope

### In Scope

- A new column on My Datasets › Available rendering ready/total per dataset, displayed by default but toggleable off in the column-customization panel.
- Attention icon(s) per the icon matrix (warning icon on upload failure; existing PII-leak / error-rate icons for review states), plus a hover tooltip breakdown.
- The count is clickable, opening the existing dataset history modal for per-upload context (we reuse that modal — we do not build a new breakdown view or use the expand-row).
- Correct computation for pre-existing datasets and their historical uploads, not just new uploads.
- In-app notifications and emails to the owner on upload success / failure for existing datasets.
- Graceful handling of 1/1 and the 0/1 (single upload marked for deletion) case.

### No-Gos

- No change to the Parent status model. Parent stays Ready; the fraction does not drive Parent status.
- No change to upload/review/PII machinery, status names, or the Customer-Identifier→Processing behaviour.
- No new per-upload management UI — reuse the existing dataset history modal.
- No changes to downstream access controls in Own Data Prep tools or project usage.
- No auto-deletion or auto-resolution of stuck uploads — denominator only changes on actual deletion.
- Not on Unregistered, Partner Datasets, or Dataset Shares tabs.

### Rabbit Holes

---

## Solution Direction

Add a single column to the Available Datasets table that shows, per dataset, how many of its constituent uploads are live (ready/total), with an attention icon when an upload needs the owner's action. The Parent status keeps its existing meaning (registered and usable); the new column exposes the completeness the Parent deliberately hides, and pairs it with notifications so owners are actively told when an upload to an existing dataset succeeds or fails. Clicking the count opens the existing dataset history modal for detail.

### Key User Flow

1. An owner uploads a new file to an existing Available dataset; it becomes a Child upload and runs the standard checks + hydration.
2. While it's in flight, the column shows the dataset as incomplete (e.g. 3/4); Parent stays Ready.
3. If it reaches Ready, the count reaches its full total (e.g. 3/3) and a success notification + email fire. If it stalls (Failed / Under Review / Requires Review) it stays counted but not ready, an attention icon appears per the matrix, and a failure notification + email fire.
4. The owner clicks the count to open the dataset history modal for context, then resolves the upload or deletes it (on purge the denominator decrements).

This PRD defines WHAT and WHY. UI layout, exact icon assets, the aggregate API contract, and the refresh mechanism are for Design and Engineering's tech spec.

---

## Dependencies

**Critical path:** Confirming the parent→constituent-upload data model — that all co-existing uploads under a parent (including historical) are enumerable with their statuses. Without it there is nothing to count.

---

## Success Metrics

TBD — to be defined.

---

## Risks

### Operational Risk Assessment

- **Blast radius:** Low — an additive display column + notifications on one table; no change to status machinery, Parent status, or downstream access. Relies on the snapshot assumption above; does not touch collaboration data paths.
- **Backward compatibility:** No change to Parent status, upload flow, or APIs consumed elsewhere; existing integrations unaffected.
- **Migration safety:** Additive UI + read aggregate + notification wiring; no data migration; trivially reversible (toggle the column off / disable notifications).
- **Multi-tenancy:** Counts are org-scoped like existing tables; no cross-tenant exposure.
- **On-call burden:** Negligible beyond notification delivery; no new async data jobs.

---

## Open Questions

---

## Sign-off
