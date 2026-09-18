---
name: pm-pre-sprint-review
description: "PM business-readiness review of a user story + Implementation Plan before the pre-sprint readiness gate. Runs three checks (problem & AC clarity, AC↔test coverage, approach↔outcome plausibility) and produces a tagged report flagging gaps and concerns. Use when the PM needs to sign off business readiness before a story enters a sprint."
effort: low
output: "Inline structured report; on request, saved to output/{area}/drafts/pm-review-[story-id]-[YYYY-MM-DD].md (a working review, not verified source of truth — area inferred from the author or asked)."
---

# PM Pre-Sprint Review

Three-check business-readiness review the PM runs before the pre-sprint readiness gate, given a user-story doc and an Implementation Plan doc.

## When to Use This Skill

The PM is the accountable sign-off for **business readiness** at the pre-sprint gate. The TO signs off technical readiness; the PM signs off:

1. **Problem clarity and ACs** of the user story (DoR §1 + §2)
2. **Test cases sufficiently cover the ACs** (DoR §8 from the PM's perspective — TO authors them, PM judges coverage of business intent)
3. **Implementation Plan is plausibly aligned with the intended business outcome** — the *how* won't quietly undermine the *what*. This is a plausibility check, not an outcome guarantee.

Use this skill when the PM has both docs available (typically end of shaping week, day before the gate) and wants a structured, consistent review before signing off or raising concerns.

## What You'll Need

**Critical inputs (ask if not provided):**
- The **user story doc** (containing the story + ACs)
- The **Implementation Plan doc** (containing the technical approach and test cases in §6 Testing Readiness)

Each can be supplied in any of these formats — auto-detect from the input string:

| Input pattern | Handling |
|---|---|
| Starts with `https://app.clickup.com/` | Parse as ClickUp URL (see Input Handling below). Fetch via ClickUp MCP. |
| Matches `^[a-z0-9]+-\d+$` (e.g. `8ck9jve-82412`) | ClickUp doc or page ID. Try as page ID first; if that fails, treat as doc ID and list pages. |
| Existing local file path (`.md`, `.pdf`) | Read with the `Read` tool. PDF supported natively. |
| Existing local file path (`.docx`) | Tell the PM you can't read .docx; ask for `.md` export or pasted content. |
| Anything else, multi-line | Treat as pasted markdown content. |

## Input Handling — ClickUp URLs

ClickUp doc URLs look like:

```
https://app.clickup.com/{workspace_id}/docs/{doc_id}/{page_id}
https://app.clickup.com/{workspace_id}/docs/{doc_id}
```

Parse:
- `workspace_id` = digits between `clickup.com/` and `/docs/`
- `doc_id` = segment after `/docs/` (e.g. `8ck9jve-115792`)
- `page_id` = optional final segment (e.g. `8ck9jve-82412`)

Fetch logic:
- If `page_id` present → call `mcp__claude_ai_ClickUp__clickup_get_document_pages` with `document_id=doc_id`, `page_ids=[page_id]`, `workspace_id`, `content_format="text/md"`.
- If no `page_id` → call `mcp__claude_ai_ClickUp__clickup_list_document_pages` first. If exactly one page, fetch it silently. If multiple pages, ask the PM which page to use (this is the only allowed mid-review question — the input is genuinely ambiguous).

## Process

### Step 1: Resolve and fetch both docs

For each of the two inputs, apply the auto-detection rules above and fetch. Hold the user-story content and the Impl-Plan content in working memory. Do not summarise either back to the PM at this stage — go straight to the checks.

### Step 2: Extract structured elements

From the **user story** doc, identify:
- The story statement (As a X, I want Y, so that Z — or equivalent)
- The **Acceptance Criteria** as a numbered list (AC1, AC2, ...)
- The success metric(s) if stated (DoR §2)
- In-scope and out-of-scope statements (DoR §1)

From the **Implementation Plan** doc, identify:
- §1 Technical Approach (high level)
- §3 Data & Integration Design (just enough to spot mismatches)
- §6 Testing Readiness — extract the **test cases** as a list (TC1, TC2, ...) with their type (manual / automated / integration / etc.) and what each asserts

If either doc is missing a section that's needed for a check, that itself becomes a finding.

### Step 3: Run the three checks

Apply each rubric. Assign a per-check verdict from {PASS, CONCERN, BLOCK}:
- **PASS** — no action needed; sign off.
- **CONCERN** — sign off with caveat / raise at gate; not a blocker.
- **BLOCK** — sign-off withheld; must be resolved before the gate.

#### Check 1 — Problem & AC clarity (DoR §1 + §2)

Rubric:
- Problem statement present and specific (not "improve UX" or similarly vague)
- In-scope and out-of-scope are explicit, not assumed
- Affected users / systems / processes identified. **For platform stories**, sanity-check the
  named surfaces against the platform functional map (`context/platform/README.md`): does the story
  acknowledge the cross-cutting concerns its touched surfaces imply (approvals, PII, in-flight data,
  activation)? A missed concern that changes scope or business outcome is a readiness gap — flag it
  (this is scope completeness, not technical critique; stay in the PM lane).
- Story is the smallest it can be — nothing obviously deferrable that doesn't break the core value
- Each AC is observable and testable from a business perspective (an AC like "the system is fast" fails; "p95 response < 500ms" passes)
- Each AC describes outcomes, not implementation
- Success metric(s) defined for how we'll know the release worked, OR explicit deferral noted (the DoR allows "might be pre-mature for short-term")

Severity guide:
- BLOCK: vague problem, no scope boundaries, AC not testable, or critical AC missing
- CONCERN: success metric absent without deferral note, or one AC is borderline observable
- PASS: rubric satisfied

#### Check 2 — Test coverage of ACs

Build a coverage table mapping each AC to the test cases that exercise it. Then evaluate:
- Every AC has at least one test case → required for PASS
- Each mapped test case asserts the AC's observable outcome (not a tangential check)
- Edge cases mentioned within an AC (e.g. "...including when X is null") have corresponding test cases
- Note the manual/automated mix, but **do not grade it** — that's the TO's lane

Severity guide:
- BLOCK: any AC with zero test cases, or an AC with tests that don't assert its outcome
- CONCERN: edge case mentioned in AC but not tested; AC tested only manually where business risk warrants automation (call out, don't insist)
- PASS: every AC mapped, all assertions aligned

#### Check 3 — Approach ↔ business-outcome plausibility

Read Impl Plan §1 (Technical Approach) and §3 (Data & Integration) at high level only. Cross-reference against the AC success metrics, out-of-scope statements, and the implied business outcome.

Look for these classes of mismatch:
- AC implies real-time / sub-second; Impl Plan proposes batch or has no caching/perf strategy
- AC implies async or fire-and-forget; Impl Plan proposes synchronous integration (or vice versa)
- AC mentions multi-region / multi-tenant; Impl Plan §1 says "region-specific: no" or omits tenancy
- AC implies scale (volume, concurrency); Impl Plan has no idempotency, retry, or partition strategy
- Impl Plan introduces a dependency or sequencing requirement that the AC doesn't acknowledge — the value may not land in this sprint
- Out-of-scope item from the user story appears in the Impl Plan, or vice versa

**Wording rules for this check (important):**
- Frame findings as **plausibility / alignment** concerns, not technical critique. The TO owns architecture; the PM owns whether the approach plausibly delivers the business outcome.
- Avoid "this will deliver the outcome" — the outcome is confirmed at delivery (final PM sign-off) and measured post-release.
- Use "this approach is plausibly aligned with..." or "this approach risks not delivering... because..."

Severity guide:
- BLOCK: an obvious mismatch that, if shipped, would mean the AC technically passes but the business outcome doesn't land
- CONCERN: a softer alignment risk worth raising at the gate, not blocking
- PASS: no obvious mismatches against AC success metrics and scope

### Step 4: Produce the report

Use this template exactly. Inline by default. Do not save unless asked.

```markdown
## Pre-Sprint PM Review — [Story ID or short title]
**Reviewer:** [PM name]  **Date:** [YYYY-MM-DD]
**Sources:** [User story link/path] · [Impl Plan link/path]
**Verdict:** READY / NEEDS-REVIEW / BLOCKED — [N BLOCKs, M CONCERNs]

### 1. Problem & AC clarity — [PASS / CONCERN / BLOCK]
[Observations with explicit AC# references. If PASS, one short line is enough.]

### 2. Test coverage of ACs — [PASS / CONCERN / BLOCK]

| AC | Test cases | Coverage |
|---|---|---|
| AC1 | TC1, TC3 | ✓ |
| AC2 | (none) | GAP |
| ... | ... | ... |

[Narrative on gaps, edge cases missed, or assertion misalignments. Note the manual/automated mix without grading.]

### 3. Approach ↔ business outcome (plausibility) — [PASS / CONCERN / BLOCK]
[Observations cross-referencing Impl Plan §1/§3 against AC success metrics and scope. Use plausibility wording, not technical critique.]

### Suggested follow-ups
- [Actionable items for the TO — e.g. "TC for AC2 needs adding"]
- [Actionable items for the business owner / stakeholders — e.g. "confirm whether AC3 latency is hard requirement"]
```

**Verdict mapping:**
- READY = all three checks PASS
- NEEDS-REVIEW = one or more CONCERNs, no BLOCKs
- BLOCKED = one or more BLOCKs

### Step 5: Save on request only

If the PM asks to save (e.g. "save this", "save the report"):
- Save to `output/{area}/drafts/` — a working review is not verified source of truth, so it does not belong in `published/`. Determine the area from the current user's preferences (the OS user running the session, not the doc's `author`) or ask.
- Path: `output/{area}/drafts/pm-review-[story-id]-[YYYY-MM-DD].md`
- Use the story ID if available; otherwise a slug from the story title.

## What This Skill Does NOT Do

Keep PM and TO lanes clean (per the team's TO Role Guide):

- **Does not assess technical soundness** of the Implementation Plan — that's the TO's lane and HOD's escalation.
- **Does not grade test type / quality / automation coverage** beyond AC mapping — that's TO + QA.
- **Does not approve the architecture.**
- **Does not promise the story will deliver the outcome** — only that it's plausibly aligned. Outcome confirmation happens at delivery and post-release via the success metrics in DoR §2/§6.
- **Does not stray into shaping the story or the plan** — this is review, not co-authoring. Findings flag gaps; the TO and PM resolve them in their normal flow.
