---
name: story-breakdown
description: Break down PRDs and epics into INVEST-validated user stories with story point estimates
---

# Story Breakdown

Break down PRDs, epics, and features into well-structured user stories with INVEST validation, acceptance criteria, and Fibonacci story point estimates. Acts as a senior agile coach — pragmatic, constructive, and collaborative.

## Usage

```
/story-breakdown                          → Interactive: asks what to break down
/story-breakdown <path-to-prd>            → Break down a PRD into epics and stories
/story-breakdown --refine <story-text>    → Refine a single user story against INVEST
/story-breakdown --estimate               → Estimate stories against prior velocity data
```

## Prerequisites

### Tone Calibration (Silent)
Read `System/user-profile.yaml` for communication preferences. Default: direct, professional, coaching tone.

### Load Reference Principles (Silent)
Read these resource files to ground all assessments in the team's own standards:

1. **`06-Resources/User_Stories_and_Estimation.md`** — INVEST principles, story point scale (1–13+), good vs. bad story examples, acceptance criteria format
2. **`06-Resources/Definition_of_Ready_and_Done.md`** — Definition of Ready checklist (validates stories are sprint-ready), Definition of Done (validates completion)
3. **`06-Resources/Agile_Process.md`** — Sprint flow, backlog refinement process, ownership model (PO = what/why, Tech Lead = how)
4. **`06-Resources/RICE_Framework.md`** — Prioritisation scoring (Reach, Impact, Confidence, Effort) with Omnisient extensions
5. **`06-Resources/Project_Epics.md`** — Existing epic structures and patterns for reference

If any file is missing, proceed with built-in knowledge but note which references were unavailable.

### Demo Mode Check (Silent)
Read `.claude/reference/demo-mode.md`. If demo mode is active, use synthetic data.

## Process

### Phase 1: Understand the Input

**If a PRD path is provided:**
- Read the PRD file
- Identify: core problem, solution scope, delivery phases, key stakeholders, technical components, success metrics
- Map the solution to potential epic boundaries (look for natural phase breaks, distinct user groups, or independent technical domains)

**If a story or epic is pasted directly:**
- Parse the story text, acceptance criteria, and any context
- Skip to Phase 3 (INVEST Assessment) or Phase 4 (Story Splitting) as appropriate

**If interactive (no arguments):**
Ask: "What would you like to break down? You can:
- Share a path to a PRD file
- Paste an epic or feature description
- Paste a user story for refinement"

### Phase 2: Epic Decomposition (PRD → Epics)

Only runs when the input is a PRD or large feature scope.

**a) Identify Epic Boundaries**
Break the PRD scope into epics based on:
- **Delivery phases** — If the PRD defines sprints or phases, each phase is typically an epic
- **Distinct user groups** — Different actors (e.g., analysts vs. back-office admins) often map to separate epics
- **Independent technical domains** — Backend services, frontend flows, and infrastructure can be separate epics
- **Value delivery milestones** — Each epic should deliver independently usable value

**b) For Each Epic, Produce:**
```markdown
### Epic: [Epic Name]

**Goal:** [One sentence — what value does this epic deliver?]
**Actor(s):** [Who benefits?]
**Delivery phase:** [Sprint/phase from PRD, if specified]
**Dependencies:** [Other epics, spikes, or external teams]
**Estimated scope:** [T-shirt size: S/M/L/XL — based on story count and complexity]

**Stories contained:** [List story titles — detailed in Phase 3]
```

**c) Present the epic map to the user.**
Ask: "Does this epic structure make sense? Want to adjust boundaries before I break each epic into stories?"

Wait for confirmation before proceeding to Phase 3.

### Phase 3: Story Writing & INVEST Assessment

For each epic (or for a single story in refine mode):

**a) Write User Stories**
Each story follows the format:
```
As a [specific user role],
I want to [concrete action or capability],
so that [measurable outcome or value].
```

Rules:
- One user goal per story. If a story has multiple goals, split it.
- Frame from the end user's perspective, not the system's perspective.
- Use the team's language (from the PRD or existing stories) — don't invent new terminology.
- Keep stories outcome-oriented, not implementation-prescriptive.
- Remove implementation details — those belong in technical tasks, not stories.

**b) Write Acceptance Criteria**
For each story, write 3–5 acceptance criteria:
```markdown
**Acceptance Criteria:**
- [ ] Given [context], when [action], then [expected outcome]
- [ ] Given [edge case], when [action], then [expected handling]
- [ ] [Non-functional requirement if relevant — e.g., audit logged, < 2s response]
```

Rules:
- Each criterion must be independently testable
- Cover the primary success path + 1-2 key edge cases
- Include non-functional requirements where the PRD specifies them (performance, security, audit)
- Align with Definition of Done from `06-Resources/Definition_of_Ready_and_Done.md`

**c) INVEST Assessment**
Assess each story against all six dimensions. Use a compact format:

```markdown
**INVEST Check:**
| Dimension | Pass | Notes |
|-----------|------|-------|
| Independent | Y/N | Can be built and delivered without other stories |
| Negotiable | Y/N | Implementation details are flexible |
| Valuable | Y/N | Delivers clear user or business value |
| Estimable | Y/N | Team can estimate effort with reasonable confidence |
| Small | Y/N | Fits within a single sprint |
| Testable | Y/N | Acceptance criteria are specific and verifiable |
```

If any dimension fails:
- Explain the gap in 1 sentence
- Propose a fix (rewrite, split, or add context)
- Apply the fix in the story output

**d) Definition of Ready Check**
Against the checklist from `06-Resources/Definition_of_Ready_and_Done.md`:
- Clear and concise (INVEST-validated above)
- Acceptance criteria defined and testable
- Functional and non-functional requirements specified
- UI/Design needs identified (wireframes, new vs. existing elements)
- Dependencies identified
- Effort estimated (story points — see Phase 4)
- Priority established

Flag any gaps as "Needs before sprint commitment: [item]"

### Phase 4: Story Point Estimation

**a) Load Calibration Data**
- Search `03-Tasks/Tasks.md` and any sprint data in `06-Resources/Sprints_and_Releases.md` for previously estimated stories
- If ClickUp is connected, search for completed stories with story points in recent sprints
- If no prior data exists, use the reference scale from `06-Resources/User_Stories_and_Estimation.md`

**b) Estimate Using Fibonacci Scale**
For each story, assign points using this scale (from team's own reference):

| Points | Meaning | Typical Scope |
|--------|---------|---------------|
| 1 | Trivial | Few hours, minimal risk |
| 2 | Small | Less than 1 day, well-understood |
| 3 | Small-medium | 1–2 days, some moving parts |
| 5 | Medium | Couple of days, requires collaboration |
| 8 | Large | ~1 week, significant complexity or uncertainty |
| 13 | Very large | Multi-day, cross-team or high uncertainty |
| 20+ | Epic-sized | **Must be split** — too large for a single story |

**c) Justify Each Estimate**
For each story, provide:
```markdown
**Story Points:** [N]
**Reasoning:** [1-2 sentences comparing to similar work or explaining complexity drivers]
**Confidence:** High / Medium / Low
```

- **High confidence**: Similar work done before, well-understood domain
- **Medium confidence**: Some unknowns but reasonable assumptions
- **Low confidence**: Significant unknowns — recommend a spike or timeboxed investigation

If a story estimates at 13+, flag it and recommend splitting (return to Phase 3).

**d) Epic Summary**
After estimating all stories in an epic:
```markdown
**Epic Total:** [sum] points across [N] stories
**Estimated sprints:** [total / team velocity] (if velocity known, otherwise note as TBD)
**Risk stories:** [list any with Low confidence estimates]
```

### Phase 5: Story Splitting (When Needed)

Triggered when a story is too large (13+ points) or contains multiple user goals.

**Splitting Strategies** (choose the most appropriate):
1. **By user goal** — Each distinct outcome becomes its own story
2. **By workflow step** — Break a multi-step flow into sequential stories
3. **By user role** — Different actors get separate stories
4. **By data variation** — Handle different data types or cases separately
5. **By happy path vs. edge cases** — Core flow first, error handling as follow-up
6. **By CRUD operation** — Separate create, read, update, delete
7. **By platform** — If behaviour differs across frontend/backend/admin

For each sub-story:
- Write title and full story text
- Write 2–3 acceptance criteria
- Estimate story points
- Run INVEST check
- Link back to parent story/epic for traceability

Present the proposed split and **wait for user confirmation** before finalising.

### Phase 6: Output & Persistence

**a) Generate the Breakdown Document**
Create a structured markdown file with the full breakdown:

```markdown
# Story Breakdown: [PRD/Epic Name]

**Source:** [PRD file path or description]
**Date:** [today's date]
**Total Stories:** [count]
**Total Story Points:** [sum]
**Estimated Sprints:** [estimate or TBD]

---

## Epic 1: [Name]
[Epic details from Phase 2]

### Story 1.1: [Title]
[Full story, AC, INVEST, points from Phases 3-4]

### Story 1.2: [Title]
...

---

## Epic 2: [Name]
...

---

## Summary

| Epic | Stories | Points | Confidence | Dependencies |
|------|---------|--------|------------|--------------|
| ... | ... | ... | ... | ... |

### Definition of Ready Gaps
[List any items that need resolution before sprint commitment]

### Recommended Spikes
[List any stories with Low confidence that need investigation first]

### RICE Scores (Optional)
[If user requests prioritisation, score each epic/story using the RICE framework]
```

**b) Save Location**
- If the PRD lives in `04-Projects/[project-folder]/`, save the breakdown alongside it as `[Project]_Story_Breakdown.md`
- If no project context, save to `00-Inbox/` and mention it can be moved

**c) Offer Next Steps**
After presenting the breakdown, offer:
1. "Want me to create these as tasks in your task backlog?" (uses Work MCP `work_mcp_create_task`)
2. "Want me to create these in ClickUp?" (uses ClickUp MCP if connected)
3. "Want to adjust any stories or estimates before we lock this down?"
4. "Want me to run RICE scoring on these to help with prioritisation?"

## Refinement Mode (`--refine`)

When refining a single story (not breaking down a PRD):

1. Read the story text and any existing acceptance criteria
2. Run INVEST assessment (Phase 3c)
3. Identify gaps and propose rewrites
4. Strengthen acceptance criteria
5. Estimate story points with reasoning
6. If the story needs splitting, propose sub-stories (Phase 5)
7. Present the refined story with before/after comparison

Output format:
```markdown
## Original Story
[as provided]

## INVEST Assessment
[table with gaps highlighted]

## Refined Story
[rewritten story text]

## Acceptance Criteria
[strengthened criteria]

## Story Points: [N]
[reasoning]

## Recommendations
[any splits, dependencies, or concerns]
```

## Estimation Mode (`--estimate`)

When estimating without full breakdown:

1. Read the stories provided (from file or pasted)
2. Load calibration data (Phase 4a)
3. Estimate each story (Phase 4b-c)
4. Provide summary table with totals and confidence levels
5. Flag any stories that need splitting

## Edge Cases

- **No prior stories with points:** Base estimates on relative complexity using the reference scale. Note that estimates will improve as the team builds velocity history.
- **Story text is missing or vague:** Ask for missing context before refinement. Don't guess at intent.
- **Multiple goals in one story:** Always split. Highlight the distinct goals and propose separate stories.
- **Conflicting acceptance criteria:** Resolve by aligning with the PRD's stated outcomes. Flag the conflict for the user.
- **PRD has no clear phases:** Propose epic boundaries based on value delivery and technical independence. Ask the user to validate.
- **Dependencies create coupling:** Flag stories that can't be truly Independent in the INVEST check. Suggest sequencing but keep them as separate stories.

## Error Handling

| Situation | Response |
|-----------|----------|
| PRD file not found | "I couldn't find that file. Can you check the path or paste the content directly?" |
| No resources found | "I couldn't load the team's story/estimation references — proceeding with standard INVEST and Fibonacci principles." |
| ClickUp not connected | "ClickUp isn't connected, so I'll save the breakdown as a markdown file. You can create tickets manually or connect ClickUp later." |
| Story too vague to estimate | "This story has too many unknowns for a confident estimate. I'd recommend a spike first — here's what it should investigate." |

## Track Usage (Silent)

Update `System/usage_log.md` — check the story-breakdown feature box if it exists. If it doesn't exist yet, skip silently.
