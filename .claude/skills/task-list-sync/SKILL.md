---
name: task-list-sync
description: Groom your task list and post a curated snapshot to your manager's ClickUp doc for review. Run every second working day.
---

## When to use

Run this skill every second working day (roughly Mon / Wed / Fri cadence) to share an up-to-date snapshot of your task list with your manager. Before invoking, make sure your local task file (`03-Tasks/Tasks.md`) reflects the current state of your work, this skill will surface anything that looks stale or unprioritized but it is not a substitute for keeping the source list maintained day to day.

Invoke with `/task-list-sync`.

## Workflow

### Step 1: Pull the task list

Read tasks from `03-Tasks/Tasks.md`. Group them by their existing priority bucket (P0 / P1 / P2 / P3) and the Unprioritized section. Note status flags (in_progress, completed, blocked) and last-touched dates if available.

### Step 2: Interactive grooming

Walk through the tasks with the user before anything else happens:

- For every item in the Unprioritized section, suggest a priority (P0-P3) with a one-line rationale and ask for confirmation. Move confirmed items into their priority bucket in `03-Tasks/Tasks.md`.
- For each P0 and P1 item, ask whether the status is still accurate. Update flags to `in_progress`, `completed`, or `blocked` as the user confirms.
- Flag any item with no apparent activity in the last 7+ days as stale. Ask whether it should stay, be deprioritized, or be removed.
- Save changes back to `03-Tasks/Tasks.md` as they are confirmed, do not batch the write until the end.

### Step 3: Sensitive-item scan

Before formatting anything for ClickUp, scan the (now-groomed) task list for items that look personal, sensitive, or otherwise inappropriate to share with a manager. Triggers include:

- Career development notes ("apply for X", "review compensation", "1:1 prep about role")
- Health, family, or personal admin
- Anything tagged `# Career:`, `# Personal:`, or similar
- Items that read like private journaling or self-reflection rather than work commitments

For each flagged item, surface it to the user one at a time and ask:

- **Include** as-is
- **Exclude** entirely (will not appear in ClickUp)
- **Mask** (replace title with a generic placeholder like "Personal task" but keep the priority slot)

If the user chooses **Exclude**, the item is dropped before formatting and is never written to the ClickUp output. Decisions are made fresh each run, do not cache exclusions across invocations.

### Step 4: Format the snapshot

Build a markdown document grouped by priority (P0 / P1 / P2 / P3), in that order. Within each bucket, show:

- Task title
- Status flag (in_progress / blocked / completed) as a short indicator
- Any masked placeholders from Step 3

Only include items the user opted to share. Skip empty priority buckets. Add a short summary line at the top: "X items shared, Y items excluded."

### Step 5: Create the ClickUp sub-page

Use `mcp__clickup__clickup_create_document_page` with:

- **Workspace ID:** `9012824942`
- **Document ID:** `8ck9jve-25572`
- **Parent page ID:** `8ck9jve-84852`
- **Page name:** `Task List - {{date}}` using today's date in the format `20 May 2026` (e.g. `Task List - 20 May 2026`)
- **Body:** the formatted snapshot from Step 4

Capture the URL of the new sub-page for use in Step 6.

### Step 6: Notify the reviewer

Reviewer: **Tegan Carton-Barber**.

Attempt the following in order, stopping after the first that succeeds. Every notification must include the disclaimer "(Automated post via Task List Sync.)" so it is clear this came from the automation, not from user directly.

1. **Comment on the page mentioning the reviewer.** Add a comment on the new sub-page with `@Tegan Carton-Barber` and the body: `Task list ready for your review. (Automated post via Task List Sync.)`
2. **Direct message via ClickUp Chat.** Send a DM to Tegan Carton-Barber with the page URL and: `New Task List - {{date}} ready for your review at [link]. (Automated post via Task List Sync.)`
3. **Inline mention in page body (fallback).** If neither of the above is supported, prepend this line to the top of the page body: `@Tegan Carton-Barber, please review. (Automated post via Task List Sync.)`

If option 1 succeeds, still attempt option 2 as a supplementary notification (the user asked for both a page mention and a direct message where possible). Only skip to fallback option 3 if both 1 and 2 fail.

### Step 7: Confirm to the user

Tell the user:

- Sub-page URL
- Which notification path(s) succeeded (page comment, DM, body fallback)
- Count of items shared and items excluded

## Cadence

This skill does not auto-fire. Run it every second working day. If you want a reminder, set up a recurring nudge with `/schedule` or a calendar event, the skill itself does not schedule its own next run.

## Configuration

The following values are pre-configured for your environment:

- **ClickUp Workspace ID:** `9012824942`
- **ClickUp Document ID:** `8ck9jve-25572`
- **ClickUp Parent page ID:** `8ck9jve-84852`
- **Reviewer:** Tegan Carton-Barber
- **Source task file:** `03-Tasks/Tasks.md`

If you need to change any of these, edit the corresponding step in the workflow above.
