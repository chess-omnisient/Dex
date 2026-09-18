---
name: ops-sop-generator-custom
description: Generate an operational Standard Operating Procedure (SOP) for an internal tool, platform, or process — access steps, day-to-day procedure, escalation path. Pulls source content from a ClickUp task and/or a live interview, then saves the SOP as a vault file. Modeled on the "SA support toll-free number" SOP.
---

# Ops SOP Generator

Generate a complete, trainee-ready **operational SOP** for an internal tool, platform, or recurring process — the kind of document someone new to a task could follow without asking a follow-up question.

This is different from `/sop-generator-custom`, which builds product-feature SOPs (definitions, personas, sprint roadmaps) from ClickUp user stories. This skill is for **how we operate a tool or workflow day-to-day**: logging into a portal, handling voicemails, triaging a shared inbox, running a recurring manual process — anything with concrete steps, an access/setup procedure, and an escalation path.

Write as a calm, precise operations lead documenting a process for someone covering it for the first time. Concrete steps over vague guidance. Every instruction should be something a trainee could follow literally.

**Never use `clickup_create_document` or `clickup_create_document_page`.** The finished SOP is always saved as a vault markdown file — never published as a ClickUp Doc.

---

## Step 1: Get the Topic and Source

Ask:

```
What process or tool should the SOP cover?

Give me the name — e.g. "SA support toll-free number", "Granola cache reset", "Weekly invoice export".

If there's already a ClickUp task with the details (training notes, screenshots, a recording), give me
the task ID or URL and I'll pull from that. Otherwise I'll ask you through it directly.
```

Store the topic as `{topic}`. If the user gives a ClickUp task ID/URL, note it; otherwise proceed to Step 2 to search.

---

## Step 2: Pull Source Content from ClickUp

**If the user gave a specific task ID/URL:** call `clickup_get_task` (or `mcp__claude_ai_ClickUp__clickup_get_task` with `include: ["description", "attachments", "comments"]`) directly on it.

**Otherwise:** search ClickUp for `{topic}` with `clickup_search`. Look for a task whose description reads like process/training notes (mentions of "training," "SOP," step-by-step language, screenshots, or a recording) rather than a sprint ticket. If one stands out, fetch it in full the same way.

From the task, extract whatever is present:
- Background/context for why the tool or process exists
- Step-by-step access or setup instructions (credentials, portals, logins, 2FA)
- Screenshots or a recording (note their URLs — carry them into the SOP as-is, don't try to re-describe images you can't see)
- Who's involved (owners, trainees, escalation contacts)
- Anything explicitly flagged as unresolved or "to confirm"

If nothing relevant turns up in ClickUp, say so briefly and move straight to Step 3 — don't stall waiting for a task that doesn't exist.

---

## Step 3: Fill Gaps by Interview

Compare what ClickUp gave you against the sections in the template below. Ask the user directly for whatever's missing — don't guess or pad. Ask as a short batch, not one question at a time, e.g.:

```
A few things I still need for the {topic} SOP:

1. What's the recurring check — is this something checked daily, as-needed, or only when something breaks?
2. Escalation: if the primary owner is unavailable, who gets flagged and how?
3. Is there anything about this tool/process that's explicitly *not* worth worrying about (a "don't touch this" note)?
4. Anything still unresolved or pending confirmation that a trainee should know about?
```

Skip any question the source material already answered. If the user doesn't know an answer, leave that section as "To confirm" rather than inventing it — same rule as `/sop-generator-custom`: never fabricate content.

---

## Step 4: Draft the SOP

Use this structure, modeled directly on the golden-standard example (a toll-free number support SOP):

```markdown
# {Topic} — Standard Operating Procedure

## 1. Introduction

[What this tool/process is, why it exists, who it serves. Include any relevant history —
e.g. a past issue that was fixed, or why this replaced a prior approach. 2-4 sentences.]

**Training:** [Who's being trained on this, by whom, and any credential-sharing note — if applicable]

---

## 2. Step-by-Step Guide: [Accessing / Using the Tool]

[Embed any screenshot/recording URLs pulled from the source task here, inline with the relevant step.]

### Step 1 — [First action]
- [Sub-detail]

### Step 2 — [Next action]
- [Sub-detail]

[Continue numbering steps until the user has full access/operational capability.]

---

## 3. Standard Operating Procedure

**[Recurring check — e.g. "As-needed check" / "Daily check"]:**
1. [What to check]
2. [What to do with what's found]

**When investigating a specific period/issue:**
1. [Step]

**Escalation:**
- [Who to flag to, and under what condition]
- [What to do if access/credentials fail]

**What NOT to worry about:**
- [Explicit scope boundary — what's intentionally out of scope for day-to-day operation]

[**Video/screenshot reference** — if the source included one, link it here]

---

## 4. Open Items / To Confirm

- [Anything flagged as unresolved, either from the source task or from gaps the user couldn't fill]
```

Keep sections that don't apply out of the final doc rather than leaving placeholder text — e.g. skip "Escalation" entirely if the user says there's genuinely no escalation path, rather than writing "N/A."

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

**Escalation:** [who, in 1 sentence — or "none defined" if skipped]

**Open items:** {n} — [list briefly, or "none"]

Let me know if any step needs more detail or if I missed part of the process.
```

---

## Notes

- This is a custom skill, protected from Dex updates
- Edit `.claude/skills/ops-sop-generator-custom/SKILL.md` to modify
- Never publish to ClickUp Docs — vault file only, always
- Distinct from `/sop-generator-custom` (product-feature SOPs from user stories) — use this one for tools, access procedures, and recurring operational processes instead
- Ground every step in what the source task or user interview actually said — mark genuine gaps as "To confirm," don't invent process detail
