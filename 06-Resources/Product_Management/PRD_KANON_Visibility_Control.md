# Shaped Solution PRD: Better KANON Visibility and Control

# \[Product / Feature / Project\] Info

**Date:** 2026-03-16
**Author:** Chess Ashley-Cooper
**Stakeholders:** Data Product Growth, Engineering, Data Engineering, CRO / Seller Success, Compliance / Legal
**Epic:** \[Add link to Epic\]

* * *
## Approval & Next Steps
### Decision
*   **Approved** - Proceeds to build phase
*   **Needs Revision** - Specific feedback: \_\_\_\_\_\_\_\_\_\_\_\_\_
*   **Declined** - Reason: \_\_\_\_\_\_\_\_\_\_\_\_\_
### Sign-offs Required
- [ ] Head of Data Product Growth
- [ ] CTO / Engineering Lead / Data Engineering Lead
- [ ] CRO / Head of Growth / Seller Success (for marketplace impact)
- [ ] CPO
### Next Steps if Approved
1. Assign to squad and delivery window
2. Kick-off planning session with Engineering + Data Engineering
3. Define KANON1 registry schema and SQL view generation spec
4. Set progress check-ins (weekly)
* * *
## _Overall PRD Completion Checklist_
_Use this master checklist to ensure your pitch is ready for review:_
- [x] **_Problem section is complete_** _(all guiding questions answered, definition of done met)_
- [x] **_Appetite section is complete_** _(clear time box, resources identified)_
- [x] **_Solution section is complete_** _(simple, visual, implementable)_
- [x] **_Rabbit holes are identified_** _(risks mitigated)_
- [x] **_No-gos are explicit_** _(scope is bounded)_
- [x] **_Success metrics are defined_** _(we know how to measure impact)_
- [ ] **_Stakeholders have reviewed_** _(feedback incorporated)_
- [x] **_Pitch is at the right altitude_** _(not too detailed, not too vague)_
- [ ] **_This can realistically be built within the stated appetite_**
- [x] **_Both buyer and seller impact is considered_**
* * *
**_Notes:_**
*   _This pitch should take 1-2 hours to write, not days_
*   _It's a commitment to a problem and an approach, not a detailed specification_
*   _Details get figured out during the build phase by the team doing the work_
*   _The pitch should be understandable to someone unfamiliar with the problem in 5 minutes_

# 1. Problem / Opportunity Framing: Better KANON Visibility and Control

**Date:** 2026-03-16
**Author:** Chess Ashley-Cooper
**Stakeholders:** Data Product Growth, Engineering, Data Engineering, CRO / Seller Success, Compliance / Legal
**Epic:** \[Add link to Epic\]
* * *
## 1\. Problem
### The Core Issue

Users creating projects on the Omnisient platform have no visibility into the re-identification risk of the fields in their datasets before data enters the cleanroom. There is no mechanism to review a KANON risk report at project creation, and no UI controls to mitigate risks (e.g. rounding numeric fields, excluding high-risk columns). This means potentially risky columns can flow into projects without inspection or control — a gap in privacy-by-design that exposes the platform and its users to compliance risk under GDPR and POPIA.

On the seller side, data owners accepting projects have no visibility into the KANON risk profile of the data being brought into the collaboration — limiting their ability to make informed acceptance decisions.

**Evidence:**
*   Regulated and high-reputation brands are holding back engagement due to missing privacy controls at the data level
*   Regulators are increasingly focused on contextual use and data minimization — the current flow does not demonstrate proactive risk management
*   Repeat KANON execution per project creates inefficiency — users cannot pre-certify datasets for reuse
*   Support cycles and user confusion around data safety are creating friction in the collaboration workflow

**Who is affected:**
*   **Data recipients (buyers)** — Cannot inspect or control field-level risk before project creation
*   **Data owners (sellers)** — Cannot see the risk profile of data entering collaborations they approve
*   **Platform trust** — Absence of visible privacy controls weakens audit, demo, and competitive positioning

**What happens if we don't solve this:**
*   Compliance exposure under GDPR/POPIA for insufficient data minimization controls
*   Lost enterprise deals where procurement/legal require demonstrable privacy safeguards
*   Continued support overhead from users unsure about data safety
*   Competitive disadvantage against PET platforms with built-in risk visibility

### _Definition of Done:_
- [x] _Problem statement is clear and specific (not generic)_
- [x] _Supporting evidence is documented (customer quotes, data, competitive intel)_
- [x] _Target user persona/segment is identified_
- [x] _Impact on business goals is articulated (growth, retention, revenue)_
- [ ] _All stakeholders agree this problem is worth solving now_
* * *
## 2\. Appetite
### Time Commitment
6 weeks (big batch) — phased delivery recommended:
*   **Phase 1 (weeks 1–3):** KANON pre-grooming in My Datasets (Data Factory stage)
*   **Phase 2 (weeks 4–6):** Project-level risk report and lighter override controls at project creation

### Resource Allocation
*   2 backend engineers (SQL view generation, KANON1 registry, schema work)
*   1 frontend engineer (Risk Controls UI, report display)
*   0.5 data engineer (KANON analysis pipeline, caching strategy)
*   0.5 product designer (risk report UX, mitigation controls)

### Strategic Context
Privacy-preserving technology is Omnisient's core differentiator. This feature moves KANON from a backend process to a user-facing capability — transforming it from infrastructure into a trust-building product feature. Delivering this ahead of upcoming compliance reviews and enterprise sales cycles strengthens both the platform's regulatory posture and its go-to-market narrative.

### Urgency Scorecard

| Criteria | Impact | Priority |
|----------|--------|----------|
| GDPR/POPIA Alignment | High | High |
| Client Requests (financial institutions, retailers) | Medium–High | High |
| Reusability in My Datasets | Medium | Medium |
| SQL View Architecture | High fit | Medium–High |
| Competitive Differentiation | Medium | Medium |

### _Definition of Done:_
*   [x] Clear time boundary is set (with specific start/end dates if known)
*   [x] Resource requirements are documented and feasible
*   [x] Trade-offs are explicitly acknowledged
*   [ ] Timeline is validated by engineering/design leads
*   [x] Appetite constrains the scope (solution fits within the box)
* * *

# 2. Solution Shaping: Better KANON Visibility and Control

**Date:** 2026-03-16
**Author:** Chess Ashley-Cooper
**Stakeholders:** Data Product Growth, Engineering, Data Engineering, CRO / Seller Success, Compliance / Legal
**Epic:** \[Add link to Epic\]
* * *
## 1\. Solution
### Core Concept

Give users visibility into field-level re-identification risk via KANON reports, and provide UI controls to mitigate risks (rounding, field exclusion) before data enters the cleanroom. Mitigations are enforced through auto-generated SQL views that replace the original dataset reference — no data duplication, fully aligned with existing architecture.

### Two Report Surfaces

This feature delivers two distinct report experiences:

**1. Dataset Risk Report (Buyer — Project Creation, Step 1)**
Displayed when the buyer selects their own table during project creation. Pulls from the OmniConnect KANON1 table, which classifies field risk into classes:
*   **High** — Field will be dropped
*   **Medium-Numeric** — Field will be rounded and some records dropped
*   **Medium-Text (varchar)** — Records will be dropped

> _KANON1 previously included a "Low" class. Confirmed: Low has been removed. Only High and Medium classes will be shown._

The buyer can then:
*   **Continue** — Proceed to project creation with defaults applied
*   **Edit** — Select fields to remove, choose rounding levels for numeric medium-risk fields, and name the resulting view
*   **Remove + Create New** — Remove this table and select another
*   **Go to Own Data Prep** — Exit to create and register a new table manually

**2. Seller Approval Risk Report (Seller — Project Approval Step)**
Displayed to the data owner when they receive a project approval request. Shows the risk profile of the data entering the collaboration, plus a drift report. Gives the seller control to:
*   **Accept** — Approve the project
*   **Reject** — Decline the project

### Key Elements

**For Data Recipients (Buyers):**
*   PII Re-identification Risk Report displayed in Step 1 of project creation, after selecting own table(s)
*   Risk Controls UI: per-field actions — Accept (keep), Remove (drop), Edit (select rounding level for numeric mediums)
*   User names the view that will be created to apply their changes
*   SQL view created in user's \_A schema with edits applied, auto-registered
*   View replaces original table for the rest of the project creation process
*   Pre-grooming capability in My Datasets / Available Datasets — risk report stored with dataset at registration, instantly available

**For Data Owners (Sellers):**
*   Risk report visible at project approval step — informed acceptance/rejection
*   Drift report integrated into project approvals
*   Seller can edit their own table based on drift report before approving

**Platform/Technical Components:**
*   **KANON1** — Runs during hydration (dataset registration), not during project creation. Identifies columns that would cause a customer to be identified. Results stored in KANON1 registry per table/column. Resource-intensive but pre-computed, so always ready to display instantly when user selects a dataset.
*   **KANON2** — Runs during project creation ("processing" phase). Responsible for dropping and rounding columns, removing uniquely identifiable records, and removing the customer identifier. Creates the registered new table.
*   **SQL View generation** — Views created in user's \_A schema with necessary edits applied, auto-registered. Project links to view, not original table.
*   **View naming** — User provides a name for the view at creation time (system name also stored)

### User Flow

1. **User uploads data** — Raw file ingested, PII hashed, stored in My Datasets
2. **KANON1 runs during hydration** — Risk report created automatically at dataset registration. Results stored with the dataset — no per-project regeneration needed
3. **Buyer creates project** — Selects own table. Platform instantly fetches KANON1 report for that dataset
4. **Reviews PII Re-identification Risk Report** — Fields shown with risk class (High/Medium) and how the platform will treat each
5. **Chooses action:**
    *   **Continue** — Accept defaults and proceed to Step 2
    *   **Edit fields** — Remove fields, set rounding levels for numeric mediums, name the view
    *   **Remove + Create New** — Discard this table, select another
    *   **Go to Own Data Prep** — Exit to manually create and register a new table (requires re-registration)
6. **If editing:** SQL view created in user's \_A schema with edits applied, auto-registered. View used for rest of project process.
7. **KANON2 runs during project processing** — Applies drops and rounding, removes uniquely identifiable records and customer identifier. Registers new table.
8. **Seller receives project approval** — Sees risk report and drift report. Can edit their own table or accept/reject.
9. **Joins via OMN-ID** — Federated matching applied only on fields that passed privacy filter
10. **Builds cohorts** — Remaining safe fields used for audience building
11. **Activates campaigns** — Hashed IDs and attributes sent to activation channels
12. **Receives attribution** — Metrics linked back via OMN-ID on privacy-safe cohorts

### Where Does the Risk Report Live?

| Option | Pros | Cons |
|--------|------|------|
| **Project-Level only** | User has contextual awareness (which project, which partner). Promotes just-in-time risk mitigation. | Requires real-time KANON generation or pre-caching. Adds friction to project creation. |
| **My Datasets** (recommended primary home) | Allows grooming of data once before reuse across many projects. Reduces resource strain by pre-computing KANON. Report tied to dataset schema at registration — clean lineage. Same dataset across many projects avoids regenerating. | Users may not know where data will be used. Less flexibility per use case. |

**Recommendation:** Store the risk report with the dataset (My Datasets / Available Datasets) but surface it contextually during project creation Step 1. This gives:
1. **Performance** — KANON1 runs during hydration, always ready to display instantly
2. **Logical data lineage** — Report tied to dataset content/schema at registration time, not any specific project
3. **Reusability** — All consumers (and sharers) can view the risk assessment without duplicating effort

### Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| **No report found** | Block "Continue". Offer "Go to Own Data Prep" or "Select another table". Provide link to (re)registration. |
| **Report older than N days or schema hash mismatch** | Prompt user to use the latest report or re-hydrate the dataset. |
| **Legacy Low class in old reports** | Low class has been removed from KANON1. Ensure legacy reports that contain Low rows still render but hide Low rows unless a "Show deprecated" toggle is enabled. |
| **User creates new table from edits** | New table requires re-registration (hydration + KANON1). User should be warned this takes time. |

### _Definition of Done:_
*   [x] Solution is described at the right altitude (not too detailed, not too vague)
*   [x] User value is immediately clear
*   [x] Both sides of the marketplace are considered
*   [x] Visual representation is included — see [Shape_KANON_Breadboard.md](Shape_KANON_Breadboard.md)
*   [ ] Technical approach is feasible (validated with engineering)
*   [x] Solution fits within stated appetite
*   [x] Success metrics are identified
* * *
## 2\. Rabbit Holes
### Risks and Complexities to Avoid

1. **No KANON1 report at project creation**
    *   **Risk:** If KANON1 hasn't run during hydration (e.g. legacy datasets registered before this feature), the buyer hits a dead end at project creation
    *   **Mitigation:** Block "Continue" and offer clear escape routes: "Go to Own Data Prep" or "Select another table" with a link to (re)registration. Never attempt real-time KANON1 generation — it's too resource-intensive.

2. **SQL View proliferation and management**
    *   **Risk:** Every edit creates a new view in \_A schema. Over time, orphaned views accumulate and become hard to manage.
    *   **Mitigation:** Implement view lifecycle management — views tied to project lifecycle. When a project is archived/deleted, associated views are flagged for cleanup. Add a view registry to track lineage.

3. **Rounding logic complexity**
    *   **Risk:** Supporting arbitrary rounding options across different data types could balloon scope. Rounding options for KANON2 visibility in KANON1 need to be defined.
    *   **Mitigation:** V1 supports a fixed set of rounding options for numeric fields only. Custom rounding is a no-go for this appetite. Rounding options TBD with engineering.

4. **Stale reports on schema change**
    *   **Risk:** If the dataset schema changes after KANON1 ran (columns added/removed/renamed), the risk report is inaccurate and could give false confidence.
    *   **Mitigation:** Store schema hash with KANON1 report. On project creation, compare current schema hash to report hash. If mismatch, prompt user to re-hydrate before continuing.

5. **Seller report accuracy and timing**
    *   **Risk:** If the recipient modifies fields after the seller reviews the risk report, the seller's view is stale
    *   **Mitigation:** Seller sees the final mitigated view at acceptance time, not an intermediate state. Any recipient edits reset the acceptance flow.

6. **Re-registration time after "Create New Table"**
    *   **Risk:** If a buyer chooses to create a new table from edits, it requires full re-registration (hydration + KANON1). This can take significant time and may surprise the user.
    *   **Mitigation:** Warn the user clearly before they commit. Offer the SQL view path as the faster alternative for most cases.

7. **Combined data risk (cross-party)**
    *   **Risk:** Does the combination of buyer + seller data increase/decrease identification risk? Current proposal only shows each party their own risk profile in isolation.
    *   **Mitigation:** Out of scope for V1. Flag as a future consideration — may require both parties to see each other's risk report, which has significant privacy implications to work through.

### _Definition of Done:_
*   [x] Top 3-5 risks are explicitly identified
*   [x] Each risk has a clear mitigation strategy or constraint
*   [ ] Engineering team has reviewed and validated concerns
*   [x] Legal/compliance risks are flagged if applicable
*   [x] Dependencies are documented
*   [ ] Team agrees on which risks are acceptable vs. dealbreakers
* * *
## 3\. No-Gos
### Out of Scope

**Functionality Exclusions:**
*   Custom rounding logic beyond the fixed set (nearest 10, 100, 1000)
*   Automated field recommendations ("you should drop this column") — V1 shows risk, user decides
*   Bulk KANON analysis across all datasets — V1 is per-dataset, manually triggered or at ingestion
*   KANON analysis on derived/output datasets (cohorts, audiences) — only source datasets

**Use Case Exclusions:**
*   Cross-project KANON comparison (e.g., "how does my risk profile differ across 5 projects")
*   Third-party or external KANON integrations
*   Mobile-responsive risk controls UI

**Future Considerations:**
*   Automated risk-based field recommendations using ML
*   KANON-as-a-service for external compliance audits
*   Cross-dataset risk correlation analysis
*   Granular permission controls for who can edit mitigations vs. who can only view
*   Combined cross-party risk analysis — does the combination of buyer + seller data increase/decrease identification risk? Would require both parties to see each other's report.
*   Desktop Connect placement — explore surfacing KANON risk report in Desktop Connect as an alternative entry point

### _Definition of Done:_
*   [x] Clear boundaries are set around what's excluded
*   [x] Rationale for exclusions is documented (appetite, complexity, or strategic choice)
*   [ ] Stakeholders agree on what's out of scope
*   [x] Future considerations are captured for roadmap
*   [x] No-gos prevent scope creep during execution
* * *
## 4\. Success Metrics
### How We'll Measure Success

**Primary Metrics:**
*   Percentage of projects created with KANON report reviewed (target: >70% within 3 months of launch)
*   Number of field mitigations applied per project (indicates users are actively managing risk)
*   Reduction in compliance-related support tickets or escalations (target: 30% reduction within 6 months)

**Secondary Metrics:**
*   Adoption of My Datasets pre-grooming (datasets with KANON1 pre-computed)
*   Seller acceptance rate change (do sellers accept faster when they can see the risk report?)
*   Enterprise deal conversion where privacy controls were a factor in procurement/legal sign-off
*   Average time from project creation to project acceptance (friction impact)

### Target Outcomes
*   Users can inspect and mitigate field-level re-identification risk before data enters any collaboration
*   Data owners can make informed acceptance decisions based on visible risk profiles
*   Platform demonstrates proactive, auditable privacy controls for GDPR/POPIA compliance
*   Reusable, pre-certified datasets reduce repeat KANON execution and support overhead
* * *

# 3. Post-launch recap (TBC)

_Once the product is launched and the experiment outcomes are analyzed, the team reflects on whether they achieved their objectives and what they learned that could be of benefit to themselves and other teams._
_When the objectives are not achieved, teams often go back to experimenting with other approaches until they reach their desired outcome. In some cases, newly uncovered insights might lead to fundamental changes to their solution or even to the problem framing._

# Appendix

## Platform Flow Integration

| Stage | Description |
|-------|-------------|
| **Data Factory** | Own data is tokenized, hashed, and registered under My Datasets. KANON analysis optionally run at ingestion or triggered manually. Outputs stored in KANON1 registry per table/column. |
| **Project Creation** | User selects dataset. If no prior KANON, warn/lock. Otherwise, show risk report per field, auto-sourced from KANON1. |
| **Risk Controls UI** | User reviews fields flagged as High/Medium. For Medium Numeric, selects rounding. For any, opts to drop column. Results in new SQL View in \_A schema, auto-registered. Project links to view, not original dataset. |
| **OMN-ID / Cleanroom Join** | View enters join graph. Only pre-filtered, mitigated columns are seen by the other party. |
| **Insights Portal** | Cohorts, audiences, and overlap reports derived from mitigated view. Data minimization intact. |
| **Activation & Attribution** | Outputs (pseudonymized cohorts, token files) reflect only safe fields. Attribution via identity graph works on iURNs and back-joins to the view. |

## Validation

*   ✔ Makes sense functionally — Project-level re-ID risk management gives recipients awareness and control
*   ✔ Enforces privacy-by-design — Especially when receiver initiates processing inside a cleanroom
*   ✔ Supports principle of least privilege — Let the user drop/high-pass risky fields early
*   ✔ SQL View approach is efficient — Replaces original table without duplicating data, fits current architecture

## Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | ~~Is the "Low" risk class still populated in KANON1?~~ **Resolved:** Low has been removed. UI will only show High and Medium. | Robin | ✅ Done |
| 2 | What are the specific rounding options for numeric medium-risk fields? (e.g. nearest 10, 100, 1000?) | Engineering | TBD |
| 3 | Does the combination of buyer + seller data increase/decrease identification risk? If so, both parties may need to see each other's risk report. | Robin / Legal | TBD |
| 4 | Can we show each party the other's data in the risk report? (Privacy implications) | Legal | TBD |
| 5 | Is the Drift Report tied to project approvals specifically, or is it a separate feature? (Paul didn't mention — double check) | Paul | Pending |
| 6 | How does the existing Data Processing Report relate to this? Can we add edit function and risk rating to it? | Engineering | TBD |
| 7 | Does the KANON1 report update automatically when dataset schema changes, or only on re-hydration? | Engineering | TBD |
| 8 | Priority between Seller Approval Risk Report and Dataset Risk Report — which ships first? | Product | TBD |
| 9 | Is this feature tied to the project squad or a separate initiative? | Product | TBD |

## User Story Map Reference

Source: ClickUp Whiteboard — [User Story Map: Better KANON visibility and control](https://app.clickup.com/9012824942/whiteboards/8ck9jve-21712)

### User Stories

**Story 1 — Buyer Risk Visibility (Project Creation)**
> As a user whose data was shared with, when creating a project: I would like to see a report on the various columns in my table that might pose a re-identification risk inside the project and how they might be treated.

**Story 2 — Buyer Field Editing (Risk Mitigation)**
> As a user creating a project, while viewing the risk report on my own table: I would like to select which fields should not be pulled into the project and a preferred rounding level for numeric medium risk fields — and thereby reduce the impact of dropped records due to KANON.

**Story 3 — Dataset-Level Risk Report**
> Put the risk report with datasets rather than only inside a project — but surface it contextually during project creation.

**Story 4 — Seller Risk Visibility (Project Approval)**
> Risk Report (KANON) visible to Seller when creating a Project (project approval). Add Drift Report to Project Approvals for Seller.

### Delivery Phases

| Phase | Scope | Notes |
|-------|-------|-------|
| **Initial / Baby Step** | View risk report on project creation (buyer). View risk report on project approval (seller). | Currently: Data Processing Report exists but lacks edit function and risk rating. |
| **Enhancement** | Buyer edits fields based on risk report. Seller edits based on drift report. | More convenient user flow. Improvement to decision making. Gives Seller control. |
| **Original + Enhancements** | Full edit controls, SQL view generation, auto-registration. Integrated into project approval flow. | Some confusion in original scoping on whether it was just viewing or editing — clarified as both. |