---
name: prd-generator
description: Generate a structured PRD for a product or feature. Use after a product brief has been approved, or for features already committed that need full specification. Defines WHAT we're building and WHY — not HOW (that's engineering's tech spec). Works for both data product and platform features.
effort: high
output: "PM's personal repo: drafts/specs/prd-[product]-[YYYY-MM-DD].md"
---

# PRD Generator

Generate structured PRDs for products and features — grounded in shared context, with selective challenge where the cost of being wrong is highest.

## Area Configuration

This skill works across both product areas. Determine the area from the PM's request or the product being specified, then apply the matching configuration.

| | Data Product | Platform |
|---|---|---|
| **Context files** | `context/product-data.md`, `context/strategy-data.md`, `context/goals-data.md` | `context/product-platform.md`, `context/strategy-platform.md`, `context/goals-platform.md` |
| **Output path** | `output/data-product/{client}/prd-[product]-[YYYY-MM-DD].md` | `output/platform/prd-[product]-[YYYY-MM-DD].md` |
| **Target segment framing** | Data seller → Data buyer → End user → Primary persona | Internal team → Platform user → Downstream consumer → Primary persona |
| **Architecture section** | Data Architecture: sources, identity & matching, privacy/governance, delivery mode, commercial model, consumer contracts, data quality requirements, platform capability mapping | Technical Architecture: system components, integration points, tenant model, API surface, service dependencies, SLOs |
| **Scope framing** | Marketplace context: supply-push vs demand-pull, adoption/engagement/monetisation/liquidity | Platform context: internal vs external, self-serve vs managed, scalability requirements |
| **Solution direction** | Data flow or user flow Mermaid diagram; delivery model (Dashboard / API / Batch / Cleanroom / Managed) | System flow or user flow Mermaid diagram; delivery model (API / UI / SDK / CLI / Internal tool) |
| **Success metrics** | Revenue, adoption, match rates, data quality, time-to-delivery | Developer velocity, adoption, error rates, latency, operational load, onboarding time |
| **Risk framing (V/U/F/V/E)** | Ethical Data risk expanded for personal data, credit data, ML models, decision support | Ethical Data replaced with **Operational Risk** — blast radius, multi-tenancy, backward compatibility, migration safety |
| **Sign-off roles** | Product owner, engineering lead, data engineering, customer success, stakeholder(s) | Product owner, engineering lead, platform architect, security, dependent team leads |

Always read `context/company.md` and `context/personas.md` (if it exists) regardless of area.

## When to Use This Skill

- After a product brief has been approved and the bet has been made
- Formalising a feature that's been discussed verbally and is committed for build
- Getting alignment with engineering before they start solution design
- Retrofitting a PRD for something already in build that needs documentation

## The Problem

PRDs are either too vague (engineers ask "what do you actually want?") or too detailed (nobody reads them). A good PRD is 2-4 pages. It should be comprehensive enough to answer key questions but concise enough that stakeholders will actually read it. Focus on the problem and success criteria — not implementation details.

**A PRD defines WHAT you're building and WHY (owned by Product).**
**A technical spec defines HOW to build it (owned by Engineering).**
**The PRD comes first and informs the technical spec.**

## What You'll Need

**Critical inputs (ask if not provided):**
1. What problem are we solving?
2. Who has this problem? (see Area Configuration for user types)
3. What evidence do we have?

**Nice-to-have inputs:**
- Approved product brief (if one exists, pull from it)
- Research, interview notes, sales conversations, internal feedback
- Existing related PRDs for consistency

## Process

### Step 1: Context Load

Read the PM's context files silently:

**From pm-os-team:**
- `context/company.md` → strategic fit, competitive positioning, platform capabilities
- Area-specific product, strategy, and goals files (see Area Configuration)
- `context/personas.md` → if it exists

**Check for existing artifacts:**
- Is there an approved product brief for this? Pull problem, evidence, and scope from it — don't re-ask what's already answered.
- Are there related PRDs in `output/`? Reference for consistency in structure and language.

**Report to the user what you found.** Examples by area:

> **Data product example:**
> "I loaded context for this PRD:
> - CICTR is listed as a TU Suite product in product-data.md (Phase 1 in build)
> - Strategy-data.md shows TU Suite is Stream 2 (Growth Engine) — SA traction = global credibility lever
> - Platform capabilities needed: Identity Resolution, Clean Room, Analytics, API Distribution — all fully supported
> - I found an approved product brief — I'll use its problem statement and evidence as the starting point."

> **Platform example:**
> "I loaded context for this PRD:
> - Self-serve ingestion is listed in product-platform.md as a Q2 priority
> - Strategy-platform.md shows reducing platform team bottlenecks is the top lever
> - 4 teams currently blocked on manual onboarding (from goals-platform.md)
> - I found an approved brief — I'll use its problem statement as the starting point."

### Step 2: Problem & Evidence Synthesis

**If a product brief exists:** Pull problem and evidence from it. Confirm with the PM: "I'm using the problem statement from your approved brief. Anything to update?"

**If no brief exists, ask:**
1. What problem are we solving? (one paragraph max)
2. Who has this problem? (specific segment)
3. What evidence do we have?

**Evidence grounding rules:**
- Use verbatim quotes or specific data from provided sources
- Tag each piece of evidence:
  - `confirmed` — signed, verified, contracted
  - `indicated` — reported by sales/stakeholders/internal teams
  - `assumed` — inference without direct evidence
- Never fabricate quotes or data. Use `assumed` markers instead.

**Selective challenge — apply only when needed:**
- If all evidence is `assumed` → "What's the strongest signal you have that this is real? Can you point to a conversation or data point?"
- If problem statement describes a solution → "You're describing what to build — what's the underlying problem it solves?"
- If problem is vague → "What happens if we don't build this? Who is hurt and how?"
- If evidence is strong → acknowledge and move on. Don't slow down what's already clear.

**Context-specific framing:**

For data products:
- Is this supply-push (seller initiated) or demand-pull (buyer requested)?
- What's the marketplace context? (adoption, engagement, monetisation, liquidity)
- Impact of inaction — what happens if we don't build this?

For platform:
- Is this internal-push (platform team initiative) or demand-pull (other teams requesting)?
- What's the operational context? (bottleneck, scaling, developer experience)
- Impact of inaction — what teams are blocked and what's the cost?

### Step 3: Target Segment & Architecture

**Target segment** (use area-appropriate framing from Area Configuration):

For data products:
- Data seller(s) — who provides the data?
- Data buyer(s) — who pays / consumes?
- End users — who within the buyer org actually uses the product?
- Primary persona — design for this person's workflow

For platform:
- Internal team(s) — who builds on or operates this?
- Platform user(s) — who directly uses this capability?
- Downstream consumers — who benefits indirectly?
- Primary persona — design for this person's workflow

**Architecture section** (use area-appropriate sections from Area Configuration):

For data products — **Data Architecture:**
- What data sources are involved?
- Identity & matching model — how are records linked across parties?
- Privacy & governance constraints — PII handling, LRC restrictions, PrivSec requirements
- Delivery mode — Dashboard / API / Batch / Self-serve cleanroom / Managed service
- Commercial model — Subscription / CPM / Per-call / Revenue share / TBD

Consumer contracts:

| Consumer | Format | Freshness SLA | Access Method |
|---|---|---|---|

Data quality requirements:

| Dimension | Target | Circuit Breaker (halt/alert threshold) |
|---|---|---|
| Completeness | [e.g., <1% null in required fields] | [e.g., halt if >5%] |
| Accuracy | [e.g., 100% match vs benchmark] | [e.g., immediate investigation on any discrepancy] |
| Timeliness | [e.g., available within X of source refresh] | [e.g., alert if >2x target] |
| Consistency | [e.g., single metric definition across all views] | |
| Validity | [e.g., all business rules enforced at ingestion] | |

Platform capability mapping:

| Capability | Required? | Status |
|---|:---:|---|
| Data Ingestion, Quality & Standardisation | | |
| Identity Fabric & Proprietary Data Assets | | |
| Privacy-Preserving Identity Resolution | | |
| Clean Room Collaboration Engine | | |
| Governed Analytics & Intelligence Workspace | | |
| Audience Activation & Distribution | | |
| Platform Governance & Trust | | |
| API & Data Product Distribution | | |

For platform — **Technical Architecture:**
- What system components are involved?
- Integration points — what existing services does this touch?
- Tenant model — single-tenant, multi-tenant, team-scoped?
- API surface — new endpoints, changes to existing?
- Service dependencies — what must exist before this works?

Service level objectives:

| Metric | Target | Measurement |
|---|---|---|
| Availability | [e.g., 99.9%] | [how measured] |
| Latency (p50/p99) | [e.g., 200ms/1s] | [endpoint or flow] |
| Error rate | [e.g., <0.1%] | [scope] |

### Step 4: Scope & Boundaries

**Appetite (optional):** If the team uses time-boxed scope (e.g., Shape Up style), state the time constraint here. If not, skip this.

**In scope:** What's included in this version (bullet list). Be specific.

**No-gos:** What we will NOT do, even if asked. These are explicit exclusions that prevent scope creep.

**Rabbit holes:** Known areas where scope could expand if we're not careful.

| Rabbit Hole | Why It Could Expand | Mitigation |
|---|---|---|

**Future considerations:** Things we might do later but are deliberately deferring.

**One challenge to apply:** "If you had half the time, what would you cut?" — this sharpens scope faster than any other technique.

### Step 5: Solution Direction & Dependencies

**Solution direction — WHAT, not HOW:**
- Core concept in 2-3 sentences
- Key user flow — include a **Mermaid flow diagram** where appropriate to visualise the user flow, data flow, or process flow. Follow with numbered steps for detail. Use `%%{init: {'theme': 'neutral'}}%%` for diagram theming.

**What this PRD does NOT include:**
- Detailed UI design (design's job)
- Technical implementation details (engineering's tech spec)
- SQL schemas or API contracts (engineering owns these)

If the PM starts going into implementation detail, redirect: "That's valuable — capture it for the tech spec. For the PRD, let's stay at the what-and-why level."

**Dependencies:**

| Type | Dependency | Why Needed | Status / Timeline |
|---|---|---|---|
| Feature | | | |
| Team | | | |
| External | | | |

**Critical path:** Which dependency blocks launch if delayed? Flag this clearly.

### Step 6: Success Metrics & Risks

**Success metrics — dual lens:**

Lagging indicators (post-launch outcomes — did it work?):

| Metric | Current Baseline | Target | Timeframe |
|---|---|---|---|
| | [actual or PLACEHOLDER] | | |

Leading indicators (pre-launch signals — are we on track?):

| Signal | Current | Target | What This Predicts |
|---|---|---|---|

If baselines aren't available, mark as `[PLACEHOLDER — need actual baseline]`. Don't fabricate numbers.

**Risk assessment:**

For data products — use **V/U/F/V/E** (Value, Usability, Feasibility, Viability, Ethical Data):

| Type | Question | Risk | Impact | Mitigation |
|---|---|---|:---:|---|
| **Value** | Are we solving a real problem? | | H/M/L | |
| **Usability** | Can users figure it out? | | H/M/L | |
| **Feasibility** | Can we build it? Platform dependencies? | | H/M/L | |
| **Viability** | Does it work commercially? | | H/M/L | |
| **Ethical Data** | Can we build trust while delivering value? | | H/M/L | |

**Ethical Data — expanded section** (when product involves personal data, credit data, ML models, or decision support):
- **Bias:** Could the data or model produce unfair outcomes for any population segment?
- **Privacy:** PII handling, consent, data minimisation, PrivSec compliance
- **Transparency:** Can we explain what the product does to buyers, sellers, and regulators?
- **Governance:** Who controls access? Who approves use cases? What audit trails exist?
- **Veto authority:** Who can halt or modify the product if ethical concerns arise post-launch?

For platform — use **V/U/F/V/O** (Value, Usability, Feasibility, Viability, Operational):

| Type | Question | Risk | Impact | Mitigation |
|---|---|---|:---:|---|
| **Value** | Are we solving a real problem? | | H/M/L | |
| **Usability** | Can users figure it out? | | H/M/L | |
| **Feasibility** | Can we build it? Dependencies? | | H/M/L | |
| **Viability** | Does it work operationally at scale? | | H/M/L | |
| **Operational** | What's the blast radius if it breaks? | | H/M/L | |

**Operational Risk — expanded section** (when feature affects shared infrastructure):
- **Blast radius:** What breaks if this fails? How many teams/products affected?
- **Backward compatibility:** Does this break existing integrations or workflows?
- **Migration safety:** Can we migrate incrementally? What's the rollback path?
- **Multi-tenancy:** Could one team's usage affect another's performance?
- **On-call burden:** Does this add operational load? Who owns it?

**Open questions** (max 5 — focused, actionable):

| Question | Who Can Answer | Needed By |
|---|---|---|

For each open question, if possible suggest a validation approach.

### Step 7: Generate PRD

Assemble the PRD from Steps 1-6. Output follows this structure:

## Output Template

```markdown
# PRD: [Product Name]

**Area:** [Data Product / Platform]
**Author:** [name] | **Date:** [date] | **Version:** [v1]
**Status:** Draft | In Review | Approved
**Pipeline stage:** [Opportunity Framing / Solution Shaping / Build-ready]
**Product brief:** [link to approved brief, or "N/A"]

---

## Context
*Loaded from PM OS context files:*
- **Strategic fit:** [from area-specific strategy file]
- **Related products:** [from area-specific product file]
- **Competitive/operational:** [from company.md]
- **Quarterly priority:** [from area-specific goals file]

---

## Problem

[1-2 paragraphs — clear, specific, grounded]

### Evidence

| Source | Signal | Confidence |
|--------|--------|:----------:|
| | | confirmed / indicated / assumed |

### Context
- **Supply/demand dynamic:** [supply-push / demand-pull / joint]
- **Impact of inaction:** [what happens if we don't build this]

---

## Target Segment

- **Primary persona:** [design for this person]

---

## Architecture

<!-- Include the area-appropriate architecture section from Step 3 -->

---

## Scope

### In Scope
- [bullet list — specific deliverables for this version]

### No-Gos
- [things we will NOT do, even if asked]

### Rabbit Holes

| Rabbit Hole | Why It Could Expand | Mitigation |
|---|---|---|

### Future Considerations
- [deferred items — not no-gos, just not now]

---

## Solution Direction

[2-3 sentences — WHAT we're building, not HOW]

### Key User Flow

[Mermaid flow diagram visualising the user flow, data flow, or process flow]

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Dependencies

| Type | Dependency | Why Needed | Status / Timeline |
|---|---|---|---|
| Feature | | | |
| Team | | | |
| External | | | |

**Critical path:** [which dependency blocks launch if delayed?]

---

## Success Metrics

### Lagging Indicators (post-launch — did it work?)

| Metric | Baseline | Target | Timeframe |
|---|---|---|---|

### Leading Indicators (pre-launch — are we on track?)

| Signal | Current | Target | Predicts |
|---|---|---|---|

---

## Risks

| Type | Risk | Impact | Mitigation |
|---|---|:---:|---|

---

## Open Questions

| Question | Who Can Answer | Needed By | Validation Approach |
|---|---|---|---|

---

## Sign-off

| Role | Name | Status |
|---|---|---|

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1 | [date] | [name] | Initial draft |
```

## Framework References

- **Cagan's V/U/F/V Risk Framework** from *Inspired* and *Empowered* — extended with Ethical Data risk (data products) or Operational risk (platform)
- **Shape Up** (Basecamp) — appetite, no-gos, rabbit holes for scope control
- **Evidence confidence tagging** — confirmed / indicated / assumed markers to distinguish signal quality

## Tips

1. **Context files make this better.** The more current your context files are, the more grounded the PRD output will be.
2. **This is not a tech spec.** If you're writing SQL or API contracts, stop — that's engineering's job. The PRD defines WHAT and WHY.
3. **Be honest about evidence.** "I think" is fine — just label it as `assumed`. The team can then decide what to validate.
4. **No-gos prevent scope creep.** Stating what you won't do is as important as stating what you will.
5. **Update as you learn.** The PRD is a living document — version it as new information comes in.
6. **If no brief exists, consider writing one first.** Use `/product-brief-writer` to get alignment before investing in the full PRD.
