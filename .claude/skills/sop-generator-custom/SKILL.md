---
name: sop-generator-custom
description: Generate a structured Standard Operating Procedure from ClickUp stories. Prompts for a topic name, searches ClickUp, and publishes a PM-quality SOP doc with definitions, personas, story links, and operating principles.
---

# SOP Generator

Generate a complete, PM-quality Standard Operating Procedure for any product area. The skill searches ClickUp for all relevant stories, extracts context, and publishes a structured SOP document directly into ClickUp — linked to every referenced story.

Approach this as a highly skilled, technically minded product manager with 10 years of experience. The SOP should be clear, precise, and actionable — not generic. Every section should be grounded in what the stories actually say.

---

## Step 1: Get the SOP Topic

Before doing anything else, ask:

```
What topic should the SOP cover?

Give me the name — e.g. "FMCG", "Loyalty", "Campaign Attribution".
I'll search ClickUp for all stories referencing it and build the SOP from there.
```

Wait for the user's response. Store it as `{topic}`.

---

## Step 2: Search ClickUp for All References

Search ClickUp for `{topic}` using `clickup_search` with `count: 50`.

Collect **all** results — tasks, docs, and chat. Note for each:
- Task ID and custom ID (e.g., OMNI-1234)
- Task name
- Status
- ClickUp URL
- Task type (Epic, User Story, Sprint, etc.)
- Parent task (if it's a subtask/child story)

If there are more results (cursor returned), fetch the next page too.

If no results are found:
```
No ClickUp stories found for "{topic}". Double-check the spelling or try a related term.
```
Stop here if no results.

---

## Step 3: Extract Story Detail

For each **task** result (not docs/chat), call `clickup_get_task` with `detail_level: detailed`.

If a task result is a large file (saved to disk), use `jq` to extract:
```bash
jq -r '.name, .status.status, (.text_content // .description // "none")' <file>
```

Priority: focus on tasks with substantial descriptions (user story statements, acceptance criteria, terminology tables). Skim or skip tasks with only sprint notes or "deferred to sprint X" content.

Also fetch the **parent epic** if one is referenced (call `clickup_get_task` with `subtasks: true`) — the subtask list reveals the full sprint roadmap.

For any **doc** result that looks like project documentation (not a standup or handover), fetch it using `clickup_get_document_pages` to get the epic description, decision log, and definitions.

---

## Step 4: Synthesise the SOP

Think like a senior PM reading these stories cold. Extract:

**Definition of `{topic}`:**
- What is it in the real world (industry/domain definition)?
- What specific problem does it have that Omnisient solves?
- Use exact terminology from the stories (decision logs, glossary tables, user story statements)

**Product offering:**
- What does Omnisient deliver for this topic?
- Map capabilities to story names and statuses (✅ Live, 🔄 In Progress, 📋 Planned)
- Include how key data flows or processes work (e.g., indirect customer base pipeline, activation flows)

**Target users / personas:**
- Who is the primary user? (Pull from "As a..." user story statements)
- What are their jobs-to-be-done, pain points, and actions in the product?
- Who are supporting roles?

**Data parties and responsibilities:**
- Who contributes data, who receives it, who operates the platform?

**Sprint roadmap:**
- List sprints in order with status from the epic's subtask list

**Key operating principles:**
- Pull from decision logs, AC rules, and notable constraints in the stories
- These are the "never forget" rules that govern how the product works

---

## Step 5: Find the Right ClickUp Doc to Publish Into

Look at the doc results from Step 2. Identify if there is an existing **Project Documentation** doc for this topic. If yes, note its `document_id` and the relevant parent `page_id`.

If no existing doc is found, ask the user:
```
I didn't find an existing Project Documentation doc for "{topic}" in ClickUp.
Should I create the SOP as a standalone document, or do you have a doc ID I should add it to?
```

---

## Step 6: Publish the SOP to ClickUp

Call `clickup_create_document_page` with:
- `document_id`: the identified or provided doc ID
- `parent_page_id`: the relevant parent page (if applicable)
- `name`: `{topic} — Standard Operating Procedure`
- `sub_title`: `Product definition, personas, delivery roadmap, and story references`
- `content_format`: `text/md`
- `content`: the full SOP (see template below)

---

## SOP Template

```markdown
## 1. Purpose

This SOP defines what {topic} is, who it serves, what Omnisient delivers, and how the product operates. It is the reference document for sales, product, delivery, and engineering teams.

---

## 2. What is {topic}?

[Industry/domain definition — 2-3 sentences]

**The core problem {topic} clients face:** [Specific pain point this product solves]

**Omnisient's role:** [What Omnisient does for them]

### Key Terminology

| Term | Definition |
|------|------------|
| [Term] | [Definition from stories] |

---

## 3. Product Offering

[2-sentence summary of the product]

### Capability Overview

| Capability | Description | Status |
|-----------|-------------|--------|
| [Feature] | [What it does] | ✅ Live / 🔄 In Progress / 📋 Planned |

### [Key Process Name — e.g. "How X Works"]

[Step-by-step process extracted from stories]

---

## 4. Target Users

### Persona 1: [Primary User Title]

**Who:** [Role description from user story "As a..." statements]

**Their job:** [JTBD]

**Their pain points:**
- [Pain point]

**What they do in the product:**
- [Action]

### Persona 2: [Supporting Role] *(if applicable)*

[Shorter description]

---

## 5. Data Parties and Responsibilities

| Party | Role | Responsibility |
|-------|------|----------------|
| [Party] | [Role] | [What they own] |

---

## 6. Sprint Delivery Roadmap

| Sprint | Description | Status |
|--------|-------------|--------|
| [Sprint ID] | [Description] | ✅ / 🔄 / 📋 |

---

## 7. Referenced ClickUp Stories

| Story ID | Name | Status | Link |
|----------|------|--------|------|
| [OMNI-XXXX] | [Name] | [Status] | [View](url) |

---

## 8. Key Operating Principles

- [Principle extracted from decision log or AC]
- [Principle]
```

---

## Step 7: Confirm to User

```
✅ SOP created in ClickUp: [{topic} — Standard Operating Procedure]({clickup_url})

Here's what's in it:

**What is {topic}?** [1-sentence summary of the definition]

**Product offering:** [1-sentence summary]

**Aimed at:** [Persona 1 title] (primary) [+ Persona 2 if applicable]

**Stories linked:** {n} ClickUp stories referenced — OMNI-XXXX through OMNI-XXXX

Let me know if any section needs expanding or if there are stories I missed.
```

---

## Notes

- This is a custom skill, protected from Dex updates
- Edit `.claude/skills/sop-generator-custom/SKILL.md` to modify
- The SOP is always grounded in actual story content — don't invent capabilities or personas
- If a story has no description, note it as "description pending" rather than fabricating content
- Fetch the next search cursor page if 50 results are returned — completeness matters
