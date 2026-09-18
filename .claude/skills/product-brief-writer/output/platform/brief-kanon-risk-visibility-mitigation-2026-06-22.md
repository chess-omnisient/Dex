# Product Brief: KANON Risk Visibility & Mitigation Workflow

**Area:** Platform
**Author:** chess@omnisient.com | **Date:** 2026-06-22
**Status:** Proposed
**Pipeline stage:** Opportunity Framing

---

## Context

- **Strategic fit:** Privacy-preserving technology is Omnisient's stated core differentiator. KANON currently operates as invisible infrastructure — this feature promotes it to a visible, user-controlled trust layer. Aligns directly with the platform's GDPR/POPIA compliance posture and the self-serve roadmap (top VoC priority).
- **Related products:** Data Factory / My Datasets, Project Creation flow, KANON1/KANON2 engine, OMN-ID identity graph, SQL View (`_A` schema), Insights Portal, Activation pipeline
- **Affected area:** End-to-end project creation flow — from dataset registration through to cleanroom join. Two insertion points: My Datasets (pre-grooming stage) and Project Creation (per-project risk review).
- **Discovery source:** PM-shaped PRD (approved), client urgency from financial institutions and retailers, GDPR/POPIA regulatory obligations

---

## Problem

**Who has this problem?**
- **Data sellers (data owners):** Upload datasets without visibility into which fields carry re-identification risk before committing to a collaboration project
- **Data buyers (data recipients):** Create projects against datasets without understanding which fields will be dropped or rounded by KANON2 during processing — surprises at project run time
- **Omnisient (platform compliance):** Cannot demonstrate proactive data minimization controls to regulators or enterprise clients without surfacing KANON analysis results to users

**What is the problem?**
KANON analysis runs at dataset registration (KANON1) and again at project processing (KANON2), but its outputs are never shown to users. Platform users have no visibility into which fields are classified as High or Medium re-identification risk, no ability to act on those classifications before data enters the cleanroom, and no mechanism to produce mitigated views at the My Datasets stage for reuse across projects. As a result, KANON mitigations happen silently as a black-box step, users cannot inspect or sign off on what data will be shared, and the platform cannot evidence a user-controlled data minimization process to regulators or prospective enterprise clients.

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| PRD: KANON Visibility & Control (PM-approved) | KANON outputs currently invisible to users; no UI exists for field-level risk review | confirmed |
| VoC Synthesis — financial institutions and retailers | Clients from regulated industries (banking, retail) explicitly requested risk visibility and control ahead of project commitments | indicated |
| GDPR / POPIA compliance obligations | Platform must demonstrate contextual data minimization as a privacy posture — silent KANON enforcement alone is insufficient for audit | confirmed |
| PM urgency scorecard | GDPR/POPIA Alignment rated High Priority; Client Requests rated High; SQL View Architecture Fit rated Medium-High | confirmed |
| KANON2 architecture review | Fields dropped or rounded silently at project run time — no user confirmation step exists today | confirmed |
| My Datasets module (current state) | KANON1 results stored in registry per table/column but exposed nowhere in UI | confirmed |

**Impact of not solving:**
Enterprise clients in financial services and retail will continue to require manual Omnisient staff involvement to validate risk posture before projects. Regulators requesting evidence of proactive data minimization will find none — KANON enforcement happens server-side with no audit trail of user review. Omnisient's privacy-first positioning remains a backend claim rather than a demonstrable product feature. Projects built against non-mitigated views carry residual re-identification risk that could expose the platform to regulatory liability under POPIA and GDPR.

---

## Why Now

- **Regulatory pressure:** GDPR and POPIA compliance are non-negotiable platform requirements. Proactive, user-visible data minimization is increasingly the expected posture — not just a nice-to-have. Financial sector clients are pushing for it explicitly.
- **Client pipeline:** Financial institutions and retailers with higher compliance thresholds are blocked or slowed on project creation without risk visibility. This is an active conversion and retention risk in the current pipeline.
- **Self-serve roadmap alignment:** The #1 VoC priority is reducing dependence on Omnisient staff for project setup. KANON risk controls in the UI are a prerequisite for fully self-serve project creation on regulated datasets — without it, PMs or support must intervene before every sensitive project.
- **Architectural readiness:** The SQL View `_A` schema pattern is already designed and approved. KANON1 registry data is already being written at dataset registration. The building blocks exist — this feature connects them with a UI layer.
- **Opportunity cost:** Every sprint without this feature is a sprint where users cannot inspect, validate, or reuse mitigated dataset views. Projects that run against unmitigated data accumulate technical and regulatory risk that becomes harder to remediate after the fact.

---

## Solution Direction

**Approach:** Implement a dual-stage KANON risk visibility and control system. Stage 1: surface KANON1 risk reports in My Datasets with UI controls for pre-grooming (drop fields, round numeric mediums, name the view) — producing reusable SQL views in the `_A` schema. Stage 2: at project creation, show the KANON risk report for the selected dataset, allow lightweight per-project field overrides, and auto-generate a project-scoped SQL view. The cleanroom join and all downstream flows consume the mitigated view, not the original dataset.

**Delivery model:** UI (risk report surfaces, field controls) + Infrastructure (SQL view generation, KANON2 integration, `_A` schema registration)

**What this IS:**
- KANON1 risk report display in My Datasets (field-level High/Medium classification, per-column)
- Pre-grooming controls in My Datasets: drop field, round numeric Medium (nearest 10, 100, 1000), confirm and name resulting view
- KANON2 execution on user-edited field selections to validate the mitigated output
- Auto-generation of SQL view in `_A` schema; view registered as a dataset in the platform
- Risk report display at project creation: selected dataset fields with risk classifications surfaced pre-commit
- Per-project override controls (lighter version of pre-grooming): drop or round fields at project scope
- Project links to mitigated view, not original dataset; cleanroom join operates on view only
- Seller-facing risk report visibility at project acceptance step
- Audit log entry for user review and acceptance of risk report (satisfies GDPR/POPIA evidence requirement)

**What this is NOT:**
- Changes to the KANON classification engine or scoring logic (KANON1/KANON2 back-end)
- Changes to the OMN-ID identity graph or iURN resolution
- Changes to the activation pipeline (Census, Meta, TikTok) — those already receive hashed IDs only
- A redesign of the Insights Portal or Power BI reporting layer
- Support for risk classification types other than High, Medium-Numeric, and Medium-Text (no new KANON categories introduced)
- Real-time KANON re-scoring on field edits (KANON2 runs on confirmed selections, not on every UI interaction)

---

## Impact & Effort

**Impact:**
This feature moves KANON from a silent infrastructure component to a user-controlled compliance surface. The direct outcomes are: (1) users can inspect and mitigate re-identification risk before data enters the cleanroom — eliminating the silent black-box problem; (2) mitigated views are reusable across projects, reducing repeated manual setup for the same dataset; (3) the platform generates a user-acknowledged audit record of risk review, satisfying regulatory evidence requirements; (4) project abandonment and support cycles caused by unexpected KANON2 field drops at run time are reduced.

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| User visibility into KANON field risk at project creation | 0% (no UI exists) | 100% of projects on KANON-analysed datasets | H |
| Reusable pre-groomed dataset views created via UI | 0 | Available for all My Datasets with KANON1 results | H |
| Project abandonment / support escalations due to unexpected KANON2 drops | [PLACEHOLDER — no baseline logged] | Measurable reduction within 2 sprints post-launch | M |
| Compliance audit evidence (user-acknowledged risk review) | None | Logged per project, per dataset version | H |
| Staff involvement required for risk validation on regulated datasets | High (manual, every project) | Low (self-serve for standard risk profiles) | M |

**Effort:** M — 3–4 sprints across platform engineering capacity

Breakdown:
- Sprint 1: KANON1 risk report UI in My Datasets (read-only); field-level classification display
- Sprint 2: Pre-grooming controls (drop/round), KANON2 trigger on selections, SQL view generation + `_A` schema registration
- Sprint 3: Project creation risk report display + per-project override controls; project links to view not original dataset
- Sprint 4: Seller-facing risk report at project acceptance; audit log entries; end-to-end QA across project types (Overlap, ACE, Financial Inclusion)

Dependencies: KANON1 registry API must be queryable by the web app (confirm with backend). SQL view generation may require a new service endpoint. `_A` schema registration must work for both pre-groomed views and project-scoped views.

**Confidence in estimate:** Medium — architecture is well-defined and KANON1 data already exists. Main unknowns are API surface availability and whether the KANON2 trigger can be invoked without running the full project processing pipeline.

---

## The Ask

- [ ] Approve and proceed directly to full PRD

**Decision needed by:** Before next sprint planning cycle
**Decision maker:** Tegan

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| KANON1 registry API not yet queryable by the web app — requires new endpoint before UI work can start | M | H |
| KANON2 trigger cannot be invoked independently of full project processing pipeline — requires refactor | M | H |
| SQL view generation in `_A` schema conflicts with existing view naming or schema permissions for multi-party projects | L | H |
| Pre-groomed view in My Datasets goes stale if source dataset is re-uploaded or rehydrated — versioning logic needed | M | M |
| Seller risk report at acceptance exposes field classifications the seller did not expect — requires UX framing guidance | L | M |
| Rounding controls (nearest 10/100/1000) are insufficient for some numeric field types (e.g. currency at large scale) — edge cases in QA | L | M |

**Open questions:**
- [ ] Is the KANON1 registry currently accessible via a web-app-facing API, or does it only write to the internal registry at hydration time? **Blocker before UI sprint starts.**
- [ ] Can KANON2 be invoked as a standalone validation step on user-selected field edits, without triggering full project processing? If not, the pre-grooming validation model needs to be redesigned. **Blocker before sprint 2.**
- [ ] What is the view naming convention for `_A` schema views — auto-generated, user-named, or both? Needs UX decision before build.
- [ ] Does the project creation flow need to enforce KANON completion (lock/warn if no KANON1 exists for selected dataset) — and if so, what is the fallback for legacy datasets without KANON1 results?
- [ ] Are per-project override views separate `_A` schema objects from pre-groomed My Datasets views, or can they reference/extend them? Affects storage model and view registration logic.
