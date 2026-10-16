---
name: ops-sop-generator-custom
description: Generate an operational Standard Operating Procedure (SOP) for an internal tool, platform, or process — purpose, background, workflow, step-by-step procedure, outcome branches, escalation path. Pulls source content from a ClickUp task and/or a live interview, then saves the SOP as a vault file. Modeled on the CNL Approval Process SOP.
---

# Ops SOP Generator

Generate a complete, trainee-ready **operational SOP** for an internal tool, platform, or recurring process — the kind of document someone new to a task could follow without asking a follow-up question.

This is different from `/sop-generator-custom`, which builds product-feature SOPs (definitions, personas, sprint roadmaps) from ClickUp user stories. This skill is for **how we operate a tool or workflow day-to-day**: reviewing a submission queue, logging into a portal, handling voicemails, triaging a shared inbox, running a recurring manual process — anything with concrete steps, a reference surface, and an escalation path.

Write as a calm, precise operations lead documenting a process for someone covering it for the first time. Concrete steps over vague guidance. Every instruction should be something a trainee could follow literally, and every judgement call should say what "good" looks like rather than leaving it to instinct.

**Never use `clickup_create_document` or `clickup_create_document_page`.** The finished SOP is always saved as a vault markdown file — never published as a ClickUp Doc.

---

## Step 1: Get the Topic and Source

Ask:

```
What process or tool should the SOP cover?

Give me the name — e.g. "CNL approval process", "SA support toll-free number", "Weekly invoice export".

If there's already a ClickUp task with the details (training notes, screenshots, a recording), give me
the task ID or URL and I'll pull from that. Otherwise I'll ask you through it directly.
```

Store the topic as `{topic}`. If the user gives a ClickUp task ID/URL, note it; otherwise proceed to Step 2 to search.

---

## Step 2: Pull Source Content from ClickUp

**If the user gave a specific task ID/URL:** call `clickup_get_task` (or `mcp__claude_ai_ClickUp__clickup_get_task` with `include: ["description", "attachments", "comments"]`) directly on it.

**Otherwise:** search ClickUp for `{topic}` with `clickup_search`. Look for a task whose description reads like process/training notes (mentions of "training," "SOP," step-by-step language, screenshots, or a recording) rather than a sprint ticket. If one stands out, fetch it in full the same way.

From the task, extract whatever is present:

- Background/context for why the tool or process exists, and what it replaced
- What triggers the process — a submission, an email, a schedule, a failure
- Step-by-step access or setup instructions (credentials, portals, logins, 2FA)
- The reference surface the operator works in: screen names, table columns, available actions, statuses, declaration or policy text, form fields
- **Every screenshot and recording URL**, in the order they appear and with the step each one illustrates — carry them into the SOP verbatim. Don't try to re-describe an image you can't see; place the link and let it speak.
- Who's involved: owners, trainees, reviewers, escalation contacts, notification recipients (aliases and distribution lists count)
- Decision criteria — what makes an item pass or fail, approve or decline
- Anything explicitly flagged as unresolved or "to confirm"

If nothing relevant turns up in ClickUp, say so briefly and move straight to Step 3 — don't stall waiting for a task that doesn't exist.

---

## Step 3: Fill Gaps by Interview

Compare what ClickUp gave you against the sections in the template below. Ask the user directly for whatever's missing — don't guess or pad. Ask as a short batch, not one question at a time, e.g.:

```
A few things I still need for the {topic} SOP:

1. What kicks this off — a submission, an email to a shared alias, a schedule, or something breaking?
2. Where does the operator actually do the work — which screen or system, and what are they looking at?
3. What are the possible outcomes, and what happens on each one (who gets notified, what changes)?
4. How do they know which outcome is right — what makes something pass or fail?
5. Escalation: what makes something stop being routine, who gets flagged, and what do they do in the meantime?
6. Anything explicitly *not* worth worrying about (a "don't touch this" note)?
7. Anything still unresolved or pending confirmation that a trainee should know about?
```

Skip any question the source material already answered. If the user doesn't know an answer, leave that section as "To confirm" rather than inventing it — same rule as `/sop-generator-custom`: never fabricate content.

---

## Step 4: Draft the SOP

**First, read the golden standard:** `reference/golden-standard-cnl-sop.md` in this skill's folder. It's a real shipped SOP (the CNL approval process) with notes on why each section is shaped the way it is. Read it before drafting — the template below is the skeleton, that file shows what the skeleton looks like with muscle on it. Copy its shape, never its content.

Use the structure below. It establishes *what this is and why*, then *where the work happens*, then *the steps*, then *each outcome in full*, then *when to stop and escalate*.

Section headings in `{braces}` are named for the actual process — "Review Process" for a review queue, "Daily Check" for a recurring sweep, "Approval"/"Decline" for approve/reject outcomes. Don't ship the literal brace text.

```markdown
# {Topic} — Standard Operating Procedure

## Purpose

[What this SOP defines, for whom. One short paragraph: which team owns this process, what it
covers — trigger, review, criteria, communication. State scope plainly so a reader knows within
two sentences whether this document is the one they need.]

---

## Background

[What the tool or system is, who it serves, and what the manual or prior approach was if that
history matters. Name where work arrives from, and which teams or aliases it routes to.
2-5 sentences. This is context, not instruction — no steps here.]

---

## Workflow Overview

[Recording or demo link from the source task, if one exists — bare URL or markdown link, placed
here before the diagram.]

[Optional ASCII flow diagram in a fenced code block. Include one only when the process genuinely
branches into more than one outcome and the branches are hard to hold in your head from prose
alone. A linear 5-step process doesn't need a picture of a line. When you do include one, keep it
plain: steps top to bottom with arrows, branches side by side in boxes.]

---

## {Reference section — the thing being operated}

[The surface the operator works in, documented before the procedure starts so steps can refer to
it without re-explaining. Pick whichever of these the process actually has:

- Screen location and how to get there ("Navigate to **Back Office > Notebook Approvals**")
- A screenshot of that screen, inline
- A table of columns/fields and what each one means
- The actions available, and on which items they're available
- Policy, declaration, or criteria text the operator is checking against — quoted in full, not
  summarized, because the operator will be comparing against the exact wording

Use more than one reference section if the process spans more than one surface.]

---

## {Process name — e.g. Review Process / Daily Check / Access Steps}

### Step 1: [First action, as an imperative]

[What to do and what you'll see. Place the relevant screenshot inline here, directly under the
step it illustrates. Where the step involves judgement, spell out what to look for — specific
patterns, field names, red flags — in a short numbered or bolded sub-list, not a vague
"check it's correct".]

### Step 2: [Next action]

[Continue until the operator reaches a decision point or the task is complete.]

### Step 3: Make a decision

[If the process branches, this step hands off to the outcome sections below. Say how the choice
is registered — which menu, which button.]

---

## {Outcome A — e.g. Approval}

If [condition]:

1. [Action]
2. [What the system does]
3. [What changes for the end user]
4. [Who gets notified, and with what]

---

## {Outcome B — e.g. Decline}

If [condition]:

1. [Action]
2. [Action — including anything the operator must write or supply]
   - **Doing this well:** [Concrete guidance with a real example of a good version, quoted.
     This is where the SOP earns its keep — it's the difference between an operator who
     follows the steps and one who does the job properly.]

[Inline screenshot of the outcome, if the source had one.]

[What the recipient sees and what they can do next.]

---

## Escalation

Escalate if:

- [Specific trigger condition]
- [Specific trigger condition]
- [Specific trigger condition]

In these cases, [what to do with the item in hand, who to notify, and what to hold off on until
it's been reviewed].

---

## What NOT to Worry About

- [Explicit scope boundary — what's intentionally out of scope for day-to-day operation]

---

## Open Items / To Confirm

- [Anything flagged as unresolved, either from the source task or from gaps the user couldn't fill]
```

**Rules for the draft:**

- **Screenshots are required inline.** Every screenshot URL from the source task goes into the SOP, placed under the step or section it illustrates, using `![](url)` for images and a plain link for recordings. Never collect them in a trailing "references" dump, and never drop one because you couldn't tell what it showed.
- **The diagram is optional.** Generate an ASCII flow only for genuinely branching processes. Skip it for linear ones.
- **Quote criteria, don't paraphrase them.** Declaration text, policy wording, and pass/fail standards go in verbatim — the operator is checking against exact wording.
- **Every judgement step says what good looks like.** If a step requires the operator to decide something, give the patterns, examples, or red flags that drive the decision.
- **Drop sections that don't apply** rather than leaving placeholder text — skip Escalation entirely if there's genuinely no escalation path, rather than writing "N/A."

---

## Step 5: Save to the Vault

Save the SOP to `06-Resources/SOPs/{Topic}.md` (create the `SOPs/` folder if it doesn't exist yet).

Use frontmatter:

```markdown
---
title: {Topic} — Standard Operating Procedure
type: sop
source_task: {ClickUp task URL, if one was used}
created: {YYYY-MM-DD}
---
```

After writing the file, run the auto-link script since SOPs typically name people (owners, escalation contacts, trainees):

```bash
node .scripts/auto-link-people.cjs "06-Resources/SOPs/{Topic}.md"
```

---

## Step 6: Confirm to User

```
✅ SOP saved: [06-Resources/SOPs/{Topic}.md](06-Resources/SOPs/{Topic}.md)

**Covers:** [1-sentence summary of what the tool/process does]

**Outcomes documented:** [e.g. "Approve / Decline" — or "single path" if it doesn't branch]

**Escalation:** [who and when, in 1 sentence — or "none defined" if skipped]

**Screenshots carried across:** {n}

**Open items:** {n} — [list briefly, or "none"]

Let me know if any step needs more detail or if I missed part of the process.
```

---

## Notes

- This is a custom skill, protected from Dex updates
- Edit `.claude/skills/ops-sop-generator-custom/SKILL.md` to modify
- Never publish to ClickUp Docs — vault file only, always
- Distinct from `/sop-generator-custom` (product-feature SOPs from user stories) — use this one for tools, access procedures, review queues, and recurring operational processes instead
- Ground every step in what the source task or user interview actually said — mark genuine gaps as "To confirm," don't invent process detail
- Golden-standard reference lives at `reference/golden-standard-cnl-sop.md` (the CNL Approval Process SOP: Purpose → Background → Workflow Overview → Back Office reference → Review Process → Approval/Decline → Escalation). Read it at Step 4. If the house SOP style changes, update that file rather than rewriting the template here.
