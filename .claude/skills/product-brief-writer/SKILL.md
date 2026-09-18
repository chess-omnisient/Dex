---
name: product-brief-writer
description: Write a one-page product brief to get buy-in before investing in full specs. Use when pitching a new product, feature, or initiative — requesting discovery resources or getting approval before a PRD. Works for both data product and platform features.
effort: low
output: "PM's personal repo: drafts/specs/brief-[product]-[YYYY-MM-DD].md"
---

# Product Brief Writer

Write one-page product briefs to get buy-in before investing in full specs.

## Area Configuration

This skill works across both product areas. Determine the area from the PM's request or the initiative being pitched, then apply the matching configuration.

| | Data Product | Platform |
|---|---|---|
| **Context files** | `context/product-data.md`, `context/strategy-data.md`, `context/goals-data.md` | `context/product-platform.md`, `context/strategy-platform.md`, `context/goals-platform.md` |
| **Output path** | `output/data-product/{client}/brief-[product]-[YYYY-MM-DD].md` | `output/platform/brief-[product]-[YYYY-MM-DD].md` |
| **Who has the problem** | Data seller, data buyer, end user | PM, engineer, internal ops, platform user, partner developer |
| **Delivery model options** | Dashboard / API / Batch / Cleanroom / Managed service | API / UI / SDK / CLI / Internal tool / Infrastructure |
| **Strategic fit framing** | Which market stream? (from strategy-data.md) | Which platform priority? (from strategy-platform.md) |
| **Why now examples** | Client request, contract at risk, competitive pressure, marketplace gap | Internal team bottleneck, scaling constraint, tech debt risk, developer experience friction |
| **Impact metrics** | Revenue, adoption, match rates, time-to-delivery | Developer velocity, onboarding time, error rates, operational load |
| **Effort framing** | Sprint count, data engineering capacity | Sprint count, platform engineering capacity |
| **Context report example** | "Commerce Media is listed as a Stream 3 pipeline opportunity in strategy-data.md — 'strong commercial interest, needs discovery.'" | "Self-serve ingestion is flagged in strategy-platform.md as the top bottleneck — 4 teams blocked on manual onboarding." |

Always read `context/company.md` regardless of area.

## When to Use This Skill

- Pitching a new product idea, feature, or initiative to CPO or leadership
- Getting approval before investing in discovery or a full PRD
- Requesting resources for a new initiative
- Aligning stakeholders on whether an opportunity is worth pursuing
- Feeding the POV → PDLC → Product Build gate (Opportunity Framing stage)

## The Problem

A full PRD is overkill for getting initial buy-in. You don't need 4 pages of specs to get a "yes, let's explore this." You need a one-page pitch that answers: What's the problem? Why now? What's the ask?

## What You'll Need

**Critical inputs (ask if not provided):**
1. What problem are you trying to solve?
2. Who has this problem?
3. What evidence do you have that it's worth solving?

**Nice-to-have inputs:**
- Rough solution direction
- Competitive context
- Rough sizing (effort, impact)
- Your specific ask (discovery time, headcount, budget)

## Process

### Step 1: Check Your Context

Read the PM's context files silently:
- `context/company.md` → strategic fit, competitive positioning
- Area-specific product, strategy, and goals files (see Area Configuration)

Also check for the PM's personal preferences (output tone, format, technical depth).

**Report what you found.** Use area-appropriate framing (see Area Configuration for examples).

### Step 2: Gather Problem Details

If the PM hasn't provided enough context, ask:
> "To write a compelling brief, I need:
> 1. What problem are you proposing to solve?
> 2. Who experiences this? (I found [X] in context — is that the target?)
> 3. What's your ask? (e.g., 2 sprints of discovery, approval to proceed to PRD)
>
> I can pull evidence from context files if relevant."

**Do NOT write a brief for a problem you don't understand. Get clarity first.**

### Step 3: Define the Problem

- Who has this problem? (specific segment — use area-appropriate user types from Area Configuration)
- What is the problem? (in their words if possible)
- How big is it? (quantify if possible)
- What's the evidence? Tag each piece:
  - `confirmed` — signed, verified, contracted
  - `indicated` — reported by sales/stakeholders/internal teams
  - `assumed` — inference without direct evidence

### Step 4: Explain Why Now

- Strategic alignment (from area-specific strategy file)
- Competitive or operational pressure (from company.md)
- Customer or team urgency (see Area Configuration for typical drivers)
- Opportunity cost of waiting

### Step 5: Propose Solution Direction

High-level approach, not detailed specs:
- What's the general direction? (2-3 sentences max)
- What's the delivery model? (see Area Configuration for options)
- What's explicitly NOT in scope?

### Step 6: Estimate Impact and Effort

- **Impact:** Who benefits, how, measurable outcome if possible (see Area Configuration for typical metrics)
- **Effort:** T-shirt size (S/M/L/XL), rough sprint count
- **Confidence:** How confident are you in these estimates?

Don't fabricate metrics. Use baselines from context files or mark as `[PLACEHOLDER]`.

### Step 7: State Your Ask

Be explicit:
- Time (e.g., "2 sprints for discovery")
- People (e.g., "1 PM, 1 engineer for POV")
- Decision (e.g., "approval to proceed to PRD")
- Decision maker and deadline

### Step 8: Generate Brief

## Output Template

```markdown
# Product Brief: [Product/Initiative Name]

**Area:** [Data Product / Platform]
**Author:** [name] | **Date:** [date]
**Status:** Proposed | Approved | In Discovery | Rejected
**Pipeline stage:** Opportunity Framing

---

## Context
*From PM OS context files:*
- **Strategic fit:** [from area-specific strategy file]
- **Related products:** [from area-specific product file]
- **Competitive/operational:** [from company.md]

---

## Problem

**Who has this problem?**
- [User type]: [who]

**What is the problem?**
[Problem statement — one paragraph max]

**Evidence:**
| Source | Signal | Confidence |
|--------|--------|:----------:|
| | | confirmed / indicated / assumed |

**Impact of not solving:**
[What happens if we don't do this?]

---

## Why Now

- **Strategic fit:** [alignment with current priorities]
- **Pressure:** [competitive, operational, or partner urgency]
- **Urgency:** [client demand, team bottleneck, contract risk]
- **Opportunity cost:** [what we lose by waiting]

---

## Solution Direction

**Approach:** [2-3 sentences — high level only]
**Delivery model:** [see Area Configuration for options]

**What this IS:**
- [included]

**What this is NOT:**
- [excluded]

---

## Impact & Effort

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| [primary metric] | [baseline or PLACEHOLDER] | [target] | H/M/L |

**Effort:** [T-shirt size] — [rough sprint count]
**Confidence in estimate:** [Low (need discovery) / Medium / High]

---

## The Ask

- [ ] [Specific ask — e.g., "Approve 1 sprint of discovery"]
- [ ] [Specific ask — e.g., "Assign engineer for POV"]

**Decision needed by:** [date]
**Decision maker:** [name]

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| [risk] | H/M/L | H/M/L |

**Open questions:**
- [ ] [question] — will answer in discovery
```

## Tips

1. **One page means one page.** If it's longer, you're not ready to pitch — you need to sharpen.
2. **Lead with evidence.** "5 clients indicated interest" or "4 teams blocked weekly" beats "people want this."
3. **Be specific about the ask.** "Approve 2 sprints" not "let us work on this."
4. **Connect to strategy.** Show which market stream or platform priority this serves.
5. **This is not a PRD.** If the brief is approved, write a full PRD next using `/prd-generator`.
