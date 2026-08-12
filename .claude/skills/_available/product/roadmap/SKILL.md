---
name: roadmap
description: Review roadmap, surface blockers, check alignment with priorities
role_groups: [product, operations]
jtbd: |
  You're constantly asked "what's on the roadmap?" and need to check alignment. 
  This scans your projects, surfaces blockers and stale initiatives, and checks 
  if your current work aligns with your strategic pillars.
time_investment: "10-15 minutes per review"
---

## Purpose

Review your product roadmap holistically - surface blockers, identify stale initiatives, and ensure alignment with strategic priorities. This gives you a quick health check of all roadmap work.

## Evidence, authority, and recovery

Treat a roadmap review as a dated evidence report, not a projection of what might be true.

- Use the canonical status source for each project: the project's explicit status entry and status date in its `04-Projects/` record. Record that source ID/path, status date, and the review as-of date. A filesystem modified time is only a freshness clue, never a substitute for a missing status date.
- Cite source evidence for every status, blocker, milestone, pillar, alignment claim, and feedback item. Keep meeting notes or task snippets as corroborating sources unless the canonical record is updated; if sources conflict, show the contradiction and leave the status `unknown` until a human resolves it.
- `unknown` is distinct from `blocked`: use `blocked` only when the canonical record explicitly names an unresolved dependency preventing progress; use `unknown` when status is absent, stale without a current status entry, or contradictory. Staleness is a freshness warning, not proof of a blocker.
- Define every denominator. For each count or percentage, state the numerator, the full cohort used as the denominator, timeframe, and exclusions (including projects with unknown status). If a denominator cannot be established, report a count and mark the rate `unknown` rather than inventing arithmetic.
- Never invent absent status, dates, blockers, dependencies, milestones, pillar tags, customer feedback, counts, or health scores. Do not infer a blocker from silence or a stale file.
- Recommendations are not human decisions. Before any project update or document creation, show an exact preview with the target path, operation, and complete proposed content or diff; require explicit confirmation from the human authority before changing anything.
- After an approved change, read back the target and compare it with the confirmed preview. If the write fails or the read-back differs, report the exact failure, preserve the prior content, do not claim success, and recover by re-reading the current record and presenting a corrected preview for fresh human confirmation.

## Usage

- `/roadmap` - Full roadmap review
- `/roadmap [pillar-name]` - Filter by specific pillar

---

## Step 1: Gather Roadmap Context

Read roadmap-related projects and context:

1. **Scan 04-Projects/** for project files
2. **Read System/pillars.yaml** for strategic pillars
3. **Read 01-Quarter_Goals/Quarter_Goals.md** (if quarterly planning enabled)
4. **Search for roadmap mentions** in recent meeting notes (last 30 days)

---

## Step 2: Analyze Projects

For each project in 04-Projects/, extract:

**Status indicators:**
- Canonical status source and status date (flag if > 14 days old; if the status date is absent, mark freshness and status `unknown`)
- Filesystem last modified date as a secondary freshness clue only, never as the status date
- Completion status (in progress, blocked, completed)
- Pillar tags (ensure they exist and are valid)

**Blockers:**
- Search for keywords: "blocked", "waiting", "dependency", "need"
- Extract stakeholder dependencies
- Identify missing decisions

Treat keyword matches as leads, not proof. Confirm a blocker from the canonical status source; otherwise report the project as `unknown` and cite the source evidence that is missing or contradictory.

**Alignment:**
- Check if project tags match pillars in System/pillars.yaml
- Verify project supports a quarterly goal (if applicable)
- Note projects without clear pillar alignment

---

## Step 3: Check Recent Feedback

Search recent meeting notes (00-Inbox/Meetings/ from last 30 days) for:

- Customer feedback on roadmap items
- Stakeholder concerns about priorities
- Competitive mentions that might affect roadmap
- Requests for roadmap changes or updates

---

## Step 4: Generate Roadmap Summary

Present findings in this format:

```markdown
# 📋 Roadmap Review

**Date:** [Today's date]
**Projects reviewed:** [Count]
**As of:** [Review date]

---

## 🎯 Active Initiatives

[For each in-progress project:]

### [Project Name]
**Pillar:** [Pillar tag]
**Status:** [Status indicator]
**Last updated:** [Days ago]
**Next milestone:** [If available]

[Brief status summary from project file]

---

## 🚨 Attention Needed

[Projects that need attention - stale, blocked, or misaligned]

### [Project Name]
**Issue:** [Stale / Blocked / No pillar alignment]
**Details:** [Specific problem]
**Suggested action:** [What to do next]

---

## 💡 Recent Stakeholder Feedback

[Key feedback from recent meetings that affects roadmap]

- **[Person/Customer]** - [Feedback summary]
- **[Person/Customer]** - [Feedback summary]

---

## ✅ Alignment Check

**Pillars with active work:**
- [Pillar 1]: [X projects]
- [Pillar 2]: [X projects]

**Pillars without active work:**
- [Pillar]: [Note if this is intentional or a gap]

---

## 📊 Summary

**Health score:** [Good / Needs Attention / Blocked]
- [X] projects on track
- [X] projects need attention
- [X] projects blocked

**Denominator definitions:** [For every count or percentage, state the numerator, cohort/denominator, timeframe, and exclusions; disclose projects with unknown status]

**Recommended actions:**
1. [Top priority action]
2. [Second priority action]
3. [Third priority action]
```

---

## Step 5: Offer Follow-Ups

After presenting the summary, ask:

> "Want me to:
> 1. Dive deeper into any specific project?
> 2. Create a roadmap update doc for stakeholders?
> 3. Update a stale project with current status?"

---

## Filter Behavior

When user specifies a pillar (e.g., `/roadmap customer-experience`):

1. Filter projects to only those tagged with that pillar
2. Check for gaps in that pillar's roadmap
3. Suggest opportunities based on recent customer feedback related to that pillar

---

## Integration with Other Skills

- **After running this:** Suggest `/customer-intel` if feedback patterns emerge
- **If blockers found:** Suggest `/meeting-prep` for key stakeholder discussions
- **If misalignment detected:** Suggest reviewing System/pillars.yaml

---

## Example Output

```markdown
# 📋 Roadmap Review

**Date:** 2026-01-28
**Projects reviewed:** 8

---

## 🎯 Active Initiatives

### Payments Redesign
**Pillar:** Revenue Growth
**Status:** In Progress
**Last updated:** 3 days ago
**Next milestone:** Design review on Friday

On track. Engineering started implementation. Sarah (design) needs 
feedback by Wed for final mockups.

### Real-time Notifications
**Pillar:** Product Quality
**Status:** In Progress
**Last updated:** 2 days ago
**Next milestone:** Beta launch Feb 5

Engineering complete. QA testing in progress. Beta group identified 
(10 customers).

---

## 🚨 Attention Needed

### Dashboard Analytics v2
**Issue:** Stale (21 days since update)
**Details:** No recent activity. Last note: "waiting on data team"
**Suggested action:** Check in with data team lead on timeline

### Mobile App Refresh
**Issue:** Blocked
**Details:** Waiting on design system components from design team
**Suggested action:** Schedule checkpoint with design team this week

### Customer Portal Improvements
**Issue:** No pillar alignment
**Details:** No pillar tag found in project file
**Suggested action:** Tag with appropriate pillar or clarify strategic fit

---

## 💡 Recent Stakeholder Feedback

- **Acme Corp (Sarah)** - Frustrated with reporting time, wants dashboards
- **Engineering (Mike)** - API refactor taking longer than expected, may impact Q1
- **Sales team** - 3 prospects asked about mobile app during demos this month

---

## ✅ Alignment Check

**Pillars with active work:**
- Revenue Growth: 3 projects
- Product Quality: 2 projects
- Customer Experience: 2 projects

**Pillars without active work:**
- Team Development: No active projects (intentional - focus is external)

---

## 📊 Summary

**Health score:** Needs Attention
- 5 projects on track
- 2 projects need attention
- 1 project blocked

**Recommended actions:**
1. Unblock Dashboard Analytics v2 - check data team status
2. Resolve Mobile App Refresh blocker - design checkpoint
3. Add pillar tag to Customer Portal Improvements
```
