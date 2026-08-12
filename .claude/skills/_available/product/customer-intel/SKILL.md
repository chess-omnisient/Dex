---
name: customer-intel
description: Synthesize recent customer feedback and pain points
role_groups: [product, customer_success, sales]
jtbd: |
  Customer feedback is scattered across meeting notes, person pages, and quick 
  captures. This synthesizes recent feedback by theme, shows frequency of mentions, 
  and surfaces patterns you might miss when looking at conversations individually.
time_investment: "5-10 minutes per review"
---

## Purpose

Aggregate and analyze customer feedback from all sources - meeting notes, person pages, feedback captures - to identify patterns, prioritize pain points, and inform product decisions.

## Evidence, authority, and recovery

Treat customer intelligence as an evidence ledger, not as memory or a polished guess.

- For every finding, retain a stable source ID (vault path, note ID, or capture ID), source type, source date (when the customer said or wrote it), and the as-of date (when this review read it). Keep the source ID and source date attached when a finding is summarized.
- Deduplicate repeated copies of the same evidence for frequency counts, but preserve every source ID and source date in the provenance. Distinguish a copied meeting note from an independent mention; duplicate copies are not extra customer mentions.
- Preserve quote fidelity: quoted text must be copied exactly, including wording and meaningful punctuation. Mark omissions or inaudible text explicitly, and label any cleaned-up summary as a paraphrase rather than a quote.
- Keep unknown and contradictory evidence visible. If sources disagree, show each claim with its source ID and date and call out the contradiction; do not silently choose one. If the records do not support a count, customer attribution, urgency, trend, or roadmap status, write `unknown` and return **insufficient evidence** rather than filling the gap.
- Never invent absent facts, including customer names, dates, quotes, counts, sentiment, urgency, trend, or roadmap status. An empty search is not negative feedback.
- Recommendations are not human decisions. Before any create or update, show an exact preview with the target path, operation, and complete proposed content or diff; require explicit confirmation from the human authority before changing anything.
- After an approved change, read back the target and compare it with the confirmed preview before reporting success. If the write fails or the read-back does not match, report the exact failure, preserve the prior content, do not claim completion, and recover by re-reading the source and presenting a corrected preview for fresh human confirmation.

## Usage

- `/customer-intel` - Review last 30 days of feedback
- `/customer-intel [timeframe]` - Specify timeframe (e.g., "last week", "Q1", "last 90 days")
- `/customer-intel [customer-name]` - Deep dive on specific customer

---

## Step 1: Gather Customer Feedback

Search across multiple sources for customer mentions:

### Primary Sources

1. **00-Inbox/Meetings/** - Meeting notes from last 30 days (or specified timeframe)
   - Search for: customer names, company names, "customer said", "feedback", "pain point"
   
2. **People/** - Customer person pages (External/ directory)
   - Check for recent notes, pain points mentioned, feature requests

3. **00-Inbox/Customer_Feedback/** (if exists) - Dedicated feedback captures

4. **04-Projects/** - Customer mentions in project context

Create an evidence ledger before categorizing: one entry per source occurrence with its source ID, source date, as-of date, customer attribution, exact quote or clearly labeled paraphrase, and location. Do not collapse entries yet; this ledger is what preserves provenance through later deduplication.

### Keywords to Search

- Pain points: "frustrated", "pain", "problem", "issue", "struggle"
- Feature requests: "want", "need", "wish", "could we", "feature request"
- Competitive: "competitor", "vs", "compared to", "switching"
- Positive: "love", "great", "works well", "helpful"

---

## Step 2: Categorize and Theme

Group findings into categories:

### Pain Points
- What customers are frustrated with
- What's not working for them
- What's taking too long or too manual

### Feature Requests
- Specific features customers have asked for
- Capabilities they wish existed
- Improvements to existing features

### Competitive Intel
- What competitors are doing better
- Why customers might switch
- What we're missing vs competition

### Wins
- What customers love
- What's working really well
- What differentiates us positively

---

## Step 3: Identify Patterns

For each theme, identify:

1. **Frequency** - How many times this was mentioned
2. **Customers** - Which customers mentioned it
3. **Urgency** - High (blocker), Medium (painful), Low (nice-to-have)
4. **Trend** - Increasing, stable, or decreasing mentions

Count independent source occurrences, not copied text. When deduplicating a repeated capture, retain the full list of source IDs and dates and state how many independent mentions remain. Mark trend as `unknown` when the dated evidence cannot support it.

---

## Step 4: Cross-Reference with Roadmap

Check if pain points or requests are already being addressed:

1. Search 04-Projects/ for related work
2. Note if addressed, planned, or not on roadmap
3. Flag opportunities where demand exists but no work planned

---

## Step 5: Generate Intelligence Report

Present findings in this format:

```markdown
# 🎯 Customer Intelligence Report

**Period:** [Timeframe]
**Sources analyzed:** [Count] distinct source IDs ([Count] meetings, [Count] person pages, [Count] feedback captures; duplicate copies noted separately)
**Customers represented:** [Count]

---

## 🔥 Top Pain Points

### [Pain Point Theme]
**Mentioned by:** [X customers] ([Customer names])
**Frequency:** [X mentions] in last [timeframe]
**Urgency:** High / Medium / Low
**Trend:** ↑ Increasing / → Stable / ↓ Decreasing

**Details:**
- `[Source ID]` — "[Exact quote from customer 1]" — [Customer name], source date [Date], reviewed as of [As-of date]
- `[Source ID]` — "[Exact quote from customer 2]" — [Customer name], source date [Date], reviewed as of [As-of date]

**Roadmap status:** [On roadmap / Planned / Not planned]
**Related project:** [Link to 04-Projects/ file if exists]

---

## ✨ Feature Requests

[Same format as pain points]

---

## 🏆 Competitive Mentions

[Same format]

---

## 💚 What's Working

[Same format]

---

## 🎯 Recommendations

### Immediate Actions
1. [Action based on high-urgency items with increasing trend]
2. [Action based on frequency across multiple customers]

### Product Opportunities
1. [Opportunity where demand exists but no roadmap coverage]
2. [Opportunity where competitive gap is mentioned]

### Customer Follow-Ups
1. [Customer name] - [Why to follow up]
2. [Customer name] - [Why to follow up]

---

## 📊 Summary

**High-urgency items:** [Count]
**Feature requests:** [Count unique requests]
**Competitive threats:** [Count mentions]
**Customers needing follow-up:** [Count]

**Top 3 insights:**
1. [Insight with the strongest signal]
2. [Insight with increasing trend]
3. [Insight with competitive implication]
```

---

## Step 6: Offer Actions

After presenting the report, ask:

> "Want me to:
> 1. Create a feature brief for [top requested item]?
> 2. Update person pages with this intelligence?
> 3. Generate a stakeholder memo on these findings?
> 4. Deep dive on [specific customer or theme]?"

---

## Timeframe Parsing

Support natural language timeframes:
- "last week" = 7 days
- "last month" = 30 days
- "last quarter" = 90 days
- "Q1" = Jan 1 - Mar 31 of current year
- "last 90 days" = 90 days

---

## Customer-Specific Deep Dive

When user specifies a customer:

1. Pull all mentions of that customer across all sources
2. Build chronological timeline of feedback
3. Identify their top pain points and requests
4. Show progression of their sentiment over time
5. Link to their person page for full context

---

## Integration with Other Skills

- **After running this:** Suggest `/feature-decision` for top requested items
- **If competitive gaps found:** Suggest `/roadmap` to check coverage
- **If customer follow-ups needed:** Suggest `/meeting-prep [customer]`

---

## Example Output

```markdown
# 🎯 Customer Intelligence Report

**Period:** Last 30 days (Dec 29 - Jan 28)
**Sources analyzed:** 23 meetings, 12 person pages, 5 feedback captures
**Customers represented:** 18

---

## 🔥 Top Pain Points

### Reporting Takes Too Long
**Mentioned by:** 4 customers (Acme Corp, TechStart, GlobalCo, DataFlow)
**Frequency:** 7 mentions in last 30 days
**Urgency:** High (2 customers called it a "blocker")
**Trend:** ↑ Increasing (3 mentions this week vs 1/week prior)

**Details:**
- "Takes 2 days/month to compile reports manually. Need real-time dashboards." - Sarah (Acme), Jan 24
- "Our team wastes hours every week on reporting. This should be automated." - Mike (TechStart), Jan 20
- "Reporting pain is my team's #1 complaint. They avoid the system because of it." - Lisa (GlobalCo), Jan 15

**Roadmap status:** Not planned
**Related project:** None

---

### Mobile App Performance
**Mentioned by:** 3 customers (Acme Corp, StartupX, InnovateCo)
**Frequency:** 5 mentions in last 30 days
**Urgency:** Medium
**Trend:** → Stable

**Details:**
- "Mobile app is slow to load. Team doesn't use it in the field." - John (StartupX), Jan 18
- "Love the desktop experience but mobile needs work" - Sarah (Acme), Jan 12

**Roadmap status:** On roadmap (Mobile App Refresh project)
**Related project:** 04-Projects/Mobile_App_Refresh.md

---

## ✨ Feature Requests

### Real-time Notifications
**Mentioned by:** 5 customers (Acme, TechStart, GlobalCo, StartupX, FastGrow)
**Frequency:** 8 mentions in last 30 days
**Urgency:** Medium
**Trend:** ↑ Increasing

**Details:**
- "We miss important updates because we don't check the app constantly" - Sarah (Acme), Jan 24
- "Push notifications would be game-changing for our workflow" - FastGrow team, Jan 19

**Roadmap status:** On roadmap (Q1 beta launch Feb 5)
**Related project:** 04-Projects/Real_Time_Notifications.md

---

## 🏆 Competitive Mentions

### Competitor ProductX Has Better Dashboard
**Mentioned by:** 2 customers (TechStart, DataFlow)
**Frequency:** 3 mentions
**Urgency:** High (1 customer evaluating switch)
**Trend:** ↑ Increasing (new threat)

**Details:**
- "ProductX's dashboards are way ahead of yours. We're evaluating a switch." - Mike (TechStart), Jan 20
- "Showed us ProductX demo. Their reporting is impressive." - DataFlow, Jan 16

**Roadmap status:** Not planned
**Related project:** None

---

## 💚 What's Working

### API Integration
**Mentioned by:** 6 customers
**Frequency:** 9 positive mentions

**Details:**
- "API is rock solid. Never had integration issues." - Multiple customers
- "API docs are best-in-class" - Developer at InnovateCo

---

## 🎯 Recommendations

### Immediate Actions
1. **Address reporting pain** - 4 customers, increasing trend, 2 calling it blocker
2. **Respond to ProductX competitive threat** - TechStart evaluating switch

### Product Opportunities
1. **Real-time dashboards** - Strong demand (7 mentions), no roadmap coverage, competitive gap
2. **Automated reporting** - Clear pain point, affects multiple workflows

### Customer Follow-Ups
1. **TechStart (Mike)** - At-risk due to ProductX evaluation, needs reporting solution
2. **Acme Corp (Sarah)** - Consistent high-value feedback, strong champion, engage on roadmap

---

## 📊 Summary

**High-urgency items:** 3
**Feature requests:** 12 unique requests
**Competitive threats:** 2 mentions
**Customers needing follow-up:** 2

**Top 3 insights:**
1. **Reporting pain is accelerating** - Went from background complaint to blocker status
2. **ProductX emerging as competitive threat** - New mentions this month, dashboard focus
3. **Mobile performance preventing adoption** - 3 customers, but already on roadmap
```
