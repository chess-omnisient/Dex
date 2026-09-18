---
name: user-story-writer
description: Turn features into sprint-ready user stories that are Independent, Negotiable, Valuable, Estimable, Small, and Testable. Use when translating PRD requirements into engineering-ready stories with acceptance criteria. Works for both data product and platform features.
effort: low
output: "PM's personal repo: drafts/specs/user-stories-[feature]-[YYYY-MM-DD].md"
---

# User Story Writer

Turn features into sprint-ready stories that are Independent, Negotiable, Valuable, Estimable, Small, and Testable — grounded in shared context.

## Area Configuration

This skill works across both product areas. Determine the area from the PM's request or the PRD being broken down, then apply the matching configuration.

| | Data Product | Platform |
|---|---|---|
| **Context files** | `context/product-data.md`, `context/strategy-data.md`, `context/goals-data.md` | `context/product-platform.md`, `context/strategy-platform.md`, `context/goals-platform.md` |
| **Output path** | `output/data-product/{client}/user-stories-[feature]-[YYYY-MM-DD].md` | `output/platform/user-stories-[feature]-[YYYY-MM-DD].md` |
| **User types** | Data buyer, data seller, end user, internal analyst, platform admin | PM, engineer, internal ops, platform user, partner developer |
| **AC patterns** | Data quality thresholds, match rates, delivery format/SLA compliance, privacy constraints | API response codes, latency thresholds, error handling, auth/permissions, UI states |
| **Edge case patterns** | Data quality below threshold, missing/null fields, identity resolution failures, concurrent deliveries | Invalid input, auth failures, rate limiting, concurrent requests, partial failures, tenant isolation |
| **Dependency patterns** | Pipeline dependencies (ingestion → matching → delivery) | Service dependencies (API → worker → database → event) |
| **Story example** | "As a **TU credit analyst**, I want to **view matched consumer records in the clean room**, so that **I can assess credit risk without exposing raw PII**" | "As a **data engineer**, I want to **configure a new ingestion source via the UI**, so that **I don't need to wait for the platform team to onboard it manually**" |

Always read `context/company.md` and `context/personas.md` (if it exists) regardless of area.

## When to Use This Skill

- Translating PRD requirements into sprint-ready stories for engineering
- Writing stories during backlog grooming or sprint planning
- Breaking down large features into deliverable increments
- Ensuring acceptance criteria are clear before engineering starts

## What You'll Need

**Critical inputs (ask if not provided):**
- Description of the feature or capability
- Which user type this serves (see Area Configuration)

**Nice-to-have inputs:**
- Approved PRD to pull requirements from
- JTBD analysis for the target user
- Technical constraints or dependencies

## Process

### Step 1: Context Load

Read the PM's context files silently:

**From pm-os-team:**
- `context/company.md` → platform capabilities, team structure
- Area-specific product, strategy, and goals files (see Area Configuration)
- `context/personas.md` → persona JTBD, pain points (may not exist yet)

**Check for existing artifacts:**
- Is there an approved PRD for this feature? Pull scope and requirements from it.
- Is there a JTBD analysis? Connect stories to identified jobs.

**Report to the user what you found.** Examples by area:

> **Data product example:**
> "I loaded context for these user stories:
> - Found the CICTR PRD in output/data-product/transunion/ → I'll pull scope items from it
> - Product-data.md shows the data buyer is TransUnion SA
> - No personas.md yet → I'll use the PRD's target segment to frame the user type"

> **Platform example:**
> "I loaded context for these user stories:
> - Found the self-serve ingestion PRD in output/platform/ → I'll pull scope items from it
> - Product-platform.md shows 4 teams currently depend on manual onboarding
> - I'll write stories from the data engineer's perspective"

### Step 2: Gather Feature Details

If the PM hasn't provided enough context, ask:
> "I need to understand the capability before writing stories:
> 1. What feature or capability are we adding?
> 2. Who is the primary user? (see user types for your area)
> 3. What's the user trying to accomplish?
>
> Or point me to a PRD if you have one — I'll extract stories from the scope section."

### Step 3: Format as User Story

```
As a [user type],
I want to [action/capability],
So that [benefit/outcome].
```

Use area-appropriate user types (see Area Configuration). Be specific — "data buyer credit analyst" is better than "user."

### Step 4: Validate Against INVEST

- **I**ndependent: Can be delivered alone without other stories
- **N**egotiable: Implementation details can be discussed with engineering
- **V**aluable: Delivers user value, not just technical work
- **E**stimable: Team can estimate effort
- **S**mall: Fits in a sprint
- **T**estable: Has clear pass/fail criteria

If a story fails INVEST, decompose it or flag the issue.

### Step 5: Write Acceptance Criteria

Use Given/When/Then format (BDD). Each AC gets a bolded heading line, then Given/When/Then each on their own line:
```
**AC1: [Short label]**
Given [context],  
When [action],  
Then [expected result].
```

**Formatting rule — always apply, no exceptions:** end the `Given` and `When` lines with two trailing spaces (a Markdown hard break) so they render on separate lines instead of collapsing into one paragraph. A single newline alone is not enough — Markdown merges it into the previous line. Only the final `Then` line has no trailing hard break (paragraph ends there).

Use area-appropriate AC patterns (see Area Configuration) to ensure acceptance criteria cover the right concerns.

### Step 6: Identify Edge Cases

What could go wrong? What are the boundaries? Use area-appropriate edge case patterns (see Area Configuration) as a starting checklist.

## Output Template

```markdown
# User Stories: [Feature Name]

**Area:** [Data Product / Platform]
**Source:** [PRD link or feature description]
**Author:** [name] | **Date:** [date]
**Status:** Draft

---

## Context
*Loaded from PM OS context files:*
- **Product:** [from area-specific product file]
- **Target user:** [from PRD or personas.md]
- **User JTBD:** [from JTBD analysis or PRD]
- **Sprint/cycle:** [if known]

---

## Story 1: [Short Title]

**As a** [user type],
**I want to** [action],
**So that** [benefit — connect to user goals].

### INVEST Check
- [x] **Independent** — Can be delivered without dependencies on other stories
- [x] **Negotiable** — Implementation details are flexible
- [x] **Valuable** — Delivers [specific user value]
- [x] **Estimable** — Clear scope allows team to estimate effort
- [x] **Small** — Can be completed in a single sprint
- [x] **Testable** — Has clear acceptance criteria below

### Acceptance Criteria

**AC1: [Happy Path]**
Given [context],  
When [action],  
Then [expected result].

**AC2: [Alternate Path]**
Given [context],  
When [action],  
Then [expected result].

**AC3: [Error/Edge Case]**
Given [context],  
When [action],  
Then [expected result].

### Edge Cases
- [Edge case 1] → Expected behaviour: [X]
- [Edge case 2] → Expected behaviour: [X]

### Technical Notes
- [Note for engineering — dependencies, constraints]

### Out of Scope
- [What this story does NOT include]

---

## Story Dependencies

```
Story 1 ──→ Story 3 (Story 3 requires Story 1's output)
Story 2 (independent — can be built in parallel)
```

## Suggested Sprint Ordering
1. [Story X] — unblocks other work
2. [Story Y] — independent, can run in parallel
3. [Story Z] — depends on Story X

---

## Related Context
- **PRD:** [link]
- **JTBD analysis:** [link if applicable]
- **Platform capabilities:** [from company.md if relevant]
```

## Framework Reference

**INVEST criteria** (Bill Wake) with **BDD acceptance criteria**:
- Stories should be Independent, Negotiable, Valuable, Estimable, Small, Testable
- Acceptance criteria use Given/When/Then for clarity and testability

## Tips

1. **Pull from the PRD scope section.** Each "in scope" bullet can often become one or more stories.
2. **Use concrete user types.** "As a TU credit analyst" or "As a data engineer on the pipeline team" — not "As a user."
3. **Connect "so that" to real jobs.** Link to JTBD analysis or persona pain points, not generic benefits.
4. **Quality is a first-class AC.** For data products: data quality thresholds. For platform: latency and error handling. Always include these.
5. **Keep stories small.** If it can't be done in a sprint, decompose it. A story that takes 3 sprints is a feature, not a story.
6. **Include dependency mapping.** Both data product pipelines and platform services have ordering constraints — make them explicit.
