---
name: jtbd-extractor
description: Turn raw research into Jobs-to-be-Done statements showing what users are really trying to accomplish. Use when you have interview transcripts, survey responses, or customer feedback and need to extract underlying needs. Works for both data product and platform features.
effort: medium
output: "PM's personal repo: drafts/research/jtbd-[persona]-[YYYY-MM-DD].md"
---

# JTBD Extractor

Turn raw research into Jobs-to-be-Done statements showing what users are really trying to accomplish — reframing feature requests as underlying needs and uncovering opportunities.

## Area Configuration

This skill works across both product areas. Determine the area from the PM's request or the product being discussed, then apply the matching configuration.

| | Data Product | Platform |
|---|---|---|
| **Context files** | `context/product-data.md`, `context/strategy-data.md`, `context/goals-data.md` | `context/product-platform.md`, `context/strategy-platform.md`, `context/goals-platform.md` |
| **User types** | Data buyer, data seller, end user, internal analyst | PM, engineer, internal ops, platform user, partner developer |
| **Output path** | `output/data-product/{client}/jtbd-[persona]-[YYYY-MM-DD].md` | `output/platform/jtbd-[persona]-[YYYY-MM-DD].md` |
| **Multi-sided framing** | Supply side (seller) vs demand side (buyer) — jobs differ by marketplace role | Producer (team building on platform) vs consumer (team using platform capabilities) — jobs differ by integration direction |
| **Domain examples** | "I need to assess credit risk" not "Give me a credit score" | "I need to onboard a new data source quickly" not "Build an ingestion wizard" |
| **Functional job examples** | Get a credit score to my underwriter; know which attributes are available for my segment | Deploy a new pipeline without waiting on another team; see why a job failed without reading logs |
| **Emotional job examples** | Confident in the data; in control of risk | Confident the platform won't break my product; in control of my release schedule |

Always read `context/company.md` and `context/personas.md` (if it exists) regardless of area.

## When to Use This Skill

- Reframing feature requests into underlying needs
- Finding innovation opportunities in existing product portfolios
- Uncovering unmet jobs during discovery for new products or platform capabilities
- Training the team to think in jobs, not features or datasets

## What You'll Need

**Critical inputs (ask if not provided):**
- Interview transcripts, survey responses, support tickets, or customer feedback
- Which product or area this research relates to

**Nice-to-have inputs:**
- Context on the user relationships (buyer/seller or producer/consumer)
- Existing persona documentation
- Prior JTBD analysis for comparison

## Process

### Step 1: Context Load

Read the PM's context files silently:

**From pm-os-team:**
- `context/company.md` → platform capabilities, competitive positioning
- Area-specific product, strategy, and goals files (see Area Configuration)
- `context/personas.md` → existing persona JTBD if documented (may not exist yet)

**Report to the user what you found.** Examples by area:

> **Data product example:**
> "I loaded context for this JTBD extraction:
> - Product-data.md shows CICTR is in Phase 1 build for TransUnion — I'll look for jobs related to credit intelligence
> - No personas.md exists yet — I'll flag if this research warrants creating one
> - Strategy-data.md shows TU Suite targets credit bureaus globally — I'll frame jobs in that market context"

> **Platform example:**
> "I loaded context for this JTBD extraction:
> - Product-platform.md shows the ingestion pipeline is used by 4 internal teams
> - Strategy-platform.md shows self-serve is a priority this quarter
> - I'll look for jobs related to reducing platform team bottlenecks"

### Step 2: Request Research Data

If research data hasn't been provided, ask:
> "I need research data to extract jobs from. Do you have any of these?
> - Interview transcripts or notes
> - Survey responses (especially open-ended)
> - Support tickets or feature requests
> - Customer feedback or sales call notes
> - Internal team feedback or friction logs
>
> You can paste it here or point me to files."

Do not generate placeholder output without actual data.

### Step 3: Identify Jobs

Extract statements that reveal what users are trying to accomplish:
- Listen for "I need to...", "I'm trying to...", "I want to..."
- Look beyond the literal request to the underlying goal
- Pay attention to multi-sided dynamics — different user types often have different jobs for the same product or capability

### Step 4: Format as JTBD

Structure each job properly:
```
When [situation/trigger],
I want to [motivation/action],
So I can [expected outcome].
```

### Step 5: Categorise Jobs

Sort jobs into three types:
- **Functional:** The practical task
- **Emotional:** How they want to feel
- **Social:** How they want to be perceived

### Step 6: Score Opportunities

Rate each job on:
- **Importance:** How much does this matter? (1-10)
- **Satisfaction:** How well served is this today? (1-10)
- **Opportunity** = Importance + (Importance - Satisfaction)

Be honest about confidence. If inferring scores from limited data:
> "Scores are estimated from this research. Validate with quantitative research before prioritising."

## Output Template

```markdown
# Jobs-to-be-Done Analysis

**Area:** [Data Product / Platform]
**Source:** [Research inputs]
**Product Context:** [Product/market from context files]
**Author:** [name] | **Date:** [date]
**Status:** Draft

---

## Context
*Loaded from PM OS context files:*
- **Related products:** [from area-specific product file]
- **Strategic fit:** [from area-specific strategy file]
- **Known personas:** [from personas.md, or "Not yet documented"]
- **Known jobs:** [any JTBD already documented]

---

## Jobs Identified

*Opportunity Score = Importance + (Importance - Satisfaction). Higher = bigger opportunity.*

### Functional Jobs
| Job Statement | Importance | Satisfaction | Opportunity | Evidence |
|---|---|---|---|---|
| When [situation], I want to [action], so I can [outcome] | /10 | /10 | | [Quote or behaviour] |

### Emotional Jobs
| Job Statement | Importance | Satisfaction | Opportunity | Evidence |
|---|---|---|---|---|
| When [situation], I want to feel [emotion], so I can [outcome] | /10 | /10 | | [Quote or behaviour] |

### Social Jobs
| Job Statement | Importance | Satisfaction | Opportunity | Evidence |
|---|---|---|---|---|
| When [situation], I want to be seen as [perception] | /10 | /10 | | [Quote or behaviour] |

---

## Product Lens

<!-- For data products: -->
*How these jobs map to the data product marketplace:*

| Job | Who Hires the Product | Supply or Demand Side | Current Product Coverage |
|---|---|---|---|
| | [data buyer / seller / end user] | [supply-push / demand-pull] | [covered / gap / partial] |

<!-- For platform: -->
*How these jobs map to platform usage:*

| Job | Who Has This Job | Producer or Consumer | Current Platform Coverage |
|---|---|---|---|
| | [PM / engineer / ops / partner] | [building on platform / using platform] | [covered / gap / partial] |

---

## Top Opportunities

### 1. [Highest opportunity job]
**Job:** [Full statement]
**Why Underserved:** [Current solutions fail because...]
**Desired Outcomes:**
- [Outcome 1]
- [Outcome 2]
**Solution Space:** [Types of solutions that could address this]

### 2. [Second highest]
[Same structure]

---

## Feature Request Translation
| Request (What They Said) | Job (What They Need) |
|---|---|
| | |

---

## Comparison to Existing Understanding
- **Confirms:** [Jobs that match existing knowledge]
- **Expands:** [New jobs not previously documented]
- **Contradicts:** [Jobs that conflict with assumptions]

---

## Recommendations
1. [How to address top opportunity]
2. [Research to validate scores]

## Suggested Next Steps
- [ ] Update or create `personas.md` with new jobs discovered
- [ ] Validate importance/satisfaction scores with quantitative research
- [ ] Feed high-opportunity jobs into opportunity-solution-tree or product brief
```

## Framework Reference

**Jobs-to-be-Done** (Christensen/Ulwick):
- People don't buy products, they hire them to do a job
- Jobs are stable; solutions change
- Opportunity = Importance + (Importance - Satisfaction)

## Tips

1. **Multi-sided products have multi-sided jobs.** For data products: seller, buyer, and end user. For platform: producer teams and consumer teams. Extract jobs for each side.
2. **Focus on jobs, not features.** "I need a hole" not "Hire a drill." This applies equally to data products ("assess credit risk" not "credit score") and platform ("deploy without waiting" not "CI/CD pipeline").
3. **Emotional and social jobs often drive decisions.** "I want to feel confident recommending this to my board" (data product) or "I want to be seen as the team that ships fast" (platform) — these are more actionable than feature requests.
4. **Flag confidence levels.** Low-confidence scores need validation before prioritising.
5. **Connect to existing context.** The more current your context files are, the better the comparison to existing understanding.
