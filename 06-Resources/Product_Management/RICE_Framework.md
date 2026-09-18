# RICE Framework

# Explanation
The RICE scoring model is a popular choice for product teams as a tool to be able to identify ideas that have the highest potential for our business by calculating a RICE score.

RICE stands for Reach, Impact, Confidence, and Effort, which are the parameters used to calculate the score, and help measure the potential of the different ideas.

# Components of RICE
It is important that we use the same metrics across all scores for all features to ensure a fair comparison of scores. Below will outline the way to think about the scores.

## **Reach**
_How many users does this feature impact?_

Reach represents the **estimated exposure of a feature across the platform**, calculated as the **number of companies exposed to the feature multiplied by the typical number of active users per company**.
### How to Assess Reach
Reach is estimated using two components:
1. **Company Exposure**
    1. The number of active companies for which the feature is available or applicable (e.g. subscription eligibility, feature gating).
2. **User Exposure per Company**
    1. The typical number of active users within those companies who are likely to encounter or use the feature.
### Examples
**Example 1: Feature available to all companies and all users**
*   Company A: 1 user
*   Company B: 3 users
*   Company C: 5 users

**Reach** = 1 + 3 + 5 = 9 users

**Example 2: Feature behind a subscription or paywall**
*   Only Company B and C have access

**Reach** = 3 + 5 = 8 users

* * *
## Impact
_How meaningful is this feature to your users._

Impact measures the **magnitude of value delivered** if this feature is successfully released. It reflects **how strongly the feature changes outcomes**, not how many users are affected (that is captured by Reach).

Impact is composed of two dimensions:
*   **Commercial Impact** — direct or indirect revenue value
*   **Strategic Impact** — platform leverage, future optionality, or long-term risk reduction
These are assessed separately and combined to derive the final Impact score used in RICE.

**Total Impact** = Commercial Impact + Strategic Impact

### **Commercial Impact** Scoring Guide **(0-3)**

Measures the degree to which the feature contributes to revenue, retention, or monetisation.

*   **3** → **Enables new enterprise revenue.** Unlocks new revenue streams, pricing models, or materially increases deal size.
*   **2** → **Major expansion or retention impact.** Drives upsell, renewals, or materially reduces churn.
*   **1** → **Minor revenue impact.** Incremental revenue, deal support, or indirect commercial benefit.
*   **0** → **None.** No meaningful commercial impact.

### Strategic Impact Scoring Guide (0-2)

Measures long-term platform value and strategic leverage.

*   **2** → **Platform unlock.** Enables multiple future products, significant scale, or major risk reduction.
*   **1** → **Meaningful architectural or capability improvement.** Improves extensibility, consistency, or long-term maintainability.
*   **0** → **None.** No meaningful strategic impact.

* * *
## Confidence
_How confident are you in your RICE estimates for this feature._

Confidence reflects how certain you are that the **Reach, Impact, and Effort scores** accurately represent reality. Use this to discount ideas that are early, speculative, or based on assumptions rather than evidence. A lower confidence score reduces the overall RICE score, ensuring uncertainty is explicitly factored into prioritization.

### Scoring Guide **(0.0 – 1.0)**

*   **1.0** → **High confidence:** Backed by strong data, customer validation, or prior delivery experience.
*   **0.75** → **Medium confidence:** Supported by some evidence, with reasonable assumptions.
*   **0.5** → **Low confidence:** Largely hypothesis-driven or based on limited information.

* * *
## Effort
_How much work will this feature take to deliver?_

**Effort** represents the estimated delivery cost of a feature, expressed as the total number of **resource-sprints** required to complete the work.

It is calculated as:

**Effort = number of resources × number of sprints**

### **Examples**
*   1 resource over 1 sprint = **1**
*   1 resource over 2 sprints = **2**
*   2 resources over 3 sprints = **6**

This value is used as the denominator in the RICE formula. Doing this ensures that initiatives requiring more time or resources score lower unless they deliver proportionally higher value.

# Extended RICE (Risk & Dependency Adjusted)
_In complex organizations, base RICE often needs refinement to reflect **risk reduction** and **delivery constraints**. The Omnisient calculations includes two additional modifiers._

## Risk Reduction Multiplier
Some initiatives create value primarily by **reducing future risk** rather than delivering immediate, visible user impact. This adjustment ensures that critical risk-mitigation work is fairly represented in prioritization without overriding the core RICE model.

**Typical examples include:**
*   Platform stabilization and reliability improvements
*   Security and privacy enhancements
*   Technical debt reduction
*   Regulatory or compliance requirements

These initiatives may have **lower immediate Reach or Impact**, but deliver **long-term strategic and operational value**.

| Risk Reduction Level | Multiplier |
| ---| --- |
| None | 1.0 |
| Low | 1.1 |
| Medium | 1.25 |
| High | 1.5 |

**Risk Adjusted Score = Base RICE × Risk Multiplier**

## Dependency Alignment
Some initiatives depend on external teams, third parties, or prerequisite work that introduces delivery uncertainty. This adjustment ensures that initiatives with heavy dependencies are **prioritized appropriately**, even if their underlying value is strong.

**Dependencies typically:**
*   Slow delivery timelines
*   Increase coordination and sequencing risk
*   Reduce near-term value realization

This adjustment reflects the **cost of complexity**, not the quality of the idea itself.

| Dependency Level | Multiplier |
| ---| --- |
| None | 1.0 |
| Minor | 0.9 |
| Moderate | 0.75 |
| Blocking/Heavy | 0.5 |

**Final RICE = Risk Adjusted Score × Dependency Multiplier**

# Final Extended Formula

**((Reach × (Commercial + Strategic Impact) × Confidence) / Effort) × Risk Reduction Multiplier × Dependency Multiplier**

# How to Interpret RICE Scores
*   **Higher score = higher priority**
*   Scores are **relative**, not absolute
*   **Use RICE to:**
    *   Rank backlog items
    *   Compare initiatives across teams
    *   Support roadmap trade-offs

## Recommended Practice
*   Compare items **within the same portfolio or timeframe**
*   Recalculate when assumptions change
*   Use RICE as **decision support**, not as a replacement for judgment

# Strengths of RICE
*   Objective and repeatable
*   Encourages data-driven discussions
*   Makes trade-offs explicit
*   Scales from stories to portfolio items

# Limitations of RICE
*   Depends on estimate quality
*   Can undervalue strategic bets if misused
*   Requires calibration across teams

Best used alongside qualitative input such as vision alignment and regulatory commitments.

# When to Use RICE
*   Product backlog prioritization
*   Quarterly planning
*   Portfolio sequencing
*   Dependency-heavy environments
*   Executive decision forums

# RICE-Weight Delivery

**What we're doing**
We're introducing a "RICE-weighted delivery" metric per platform area. Every User Story has a RICE score (Reach, Impact, Confidence, Effort), adjusted for risk reduction and dependency complexity using our extended formula.

**How it works**
Each month the Final RICE score of stories that moved to Done ("RICE Delivered"). The RICE score of newly created stories ("RICE Added") and the total remaining backlog RICE is also tracked. This gives a month-over-month view of whether we're delivering higher-value work and whether each area's value backlog is shrinking or growing.

**Why we're doing it**
It creates an objective way to show progress beyond ticket counts: delivering 5 low-value items isn't the same as delivering 2 high-leverage ones. It also makes platform work visible, since our model explicitly accounts for strategic impact and risk reduction.

**Value it adds**
*   Clear month-to-month signal of **delivery value**, not just throughput
*   Better alignment discussions: **where we're investing vs what we're delivering**
*   Stronger governance for platform areas: highlights when backlog value is accumulating vs being retired
