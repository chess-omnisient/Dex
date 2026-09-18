# Omnisient Operational Constraints

Reference for Ada when evaluating technical options and challenging assumptions.

## Cost Sensitivity

- **Finance scrutinizes all infrastructure spend** — every new service, compute tier, or tool needs justification
- **Azure costs are the primary concern:** Synapse DWU costs, pipeline execution costs, storage costs
- **Always present cost implications** when discussing technical options
- **Prefer options that optimize existing spend** over adding new cost lines
- **Key question to ask:** "What's the monthly run cost of this, and who approved the budget?"

## Compliance & Privacy

- **GDPR and POPIA compliance** are non-negotiable requirements
- **Privacy-preserving is the core product promise** — any architecture that weakens privacy guarantees is a non-starter
- **Data residency requirements** may constrain where compute and storage can live
- **Audit trail needs** — must be able to demonstrate compliance at any time
- **Data lineage** — must track where data comes from and how it's been transformed
- **Key question to ask:** "Does this change affect our privacy guarantees or compliance posture?"

## Legacy System Dependencies

- **Significant stored procedure investment** — years of accumulated business logic
- **Tightly coupled components** — changing one system often affects others
- **Limited architectural flexibility** in some areas due to legacy design decisions
- **Migration is expensive** — always estimate the full cost of change, not just the new thing
- **Key question to ask:** "What existing systems does this touch, and what's the blast radius?"

## Tool Sprawl

- **Organizational mandate to minimize new tools** — every new tool adds:
  - License costs
  - Learning curve for the team
  - Integration and maintenance overhead
  - Another thing to monitor and secure
- **Prefer extending existing tools** over adopting new ones
- **If proposing a new tool**, must justify: Why can't we do this with what we already have?
- **Key question to ask:** "Can we solve this with our existing stack (Synapse + ADF + PowerBI + SPs)?"

## Constrained Engineering & Data Engineering Capacity

- **Small team supporting many stakeholders** — engineering time is the scarcest resource
- **Capacity is a real constraint** on what's technically feasible in any given quarter
- **Realistic timelines matter** — over-promising creates trust debt with engineering
- **Key implications:**
  - Simpler solutions that ship faster often beat elegant solutions that ship later
  - Scope creep is the enemy — protect engineering from unbounded requirements
  - Maintenance burden matters — a feature that's easy to build but hard to maintain is expensive
- **Key question to ask:** "Given current team capacity, is this realistically achievable this quarter?"

## Startup Reality

- **Evolving infrastructure** — the platform is still being built and refined
- **Governance is maturing** — processes and standards are being established, not yet set in stone
- **Speed matters** — but not at the expense of privacy or compliance
- **Strategic partnerships** (TransUnion, Shoprite) create both opportunities and constraints
- **Key question to ask:** "Is this the right time to build this, or should we wait for [dependency] to mature?"

## How to Use These Constraints

When evaluating any technical option, run it through this checklist:

1. **Cost:** What's the monthly/annual cost? Is budget allocated?
2. **Compliance:** Does it affect privacy guarantees?
3. **Legacy:** What existing systems does it touch?
4. **Tool sprawl:** Does it require new tooling? Is that justified?
5. **Capacity:** Can the team realistically build and maintain this?
6. **Timing:** Is this the right moment given the startup's maturity?

If an option fails on 2+ constraints, it's likely not viable without significant tradeoffs.
