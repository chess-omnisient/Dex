---
name: process-meetings
description: "Turn a pasted meeting transcript into a structured meeting note, updated person pages and extracted tasks. Use when the user says 'process my meetings', 'process this meeting', 'here's a transcript', 'catch up my notes', or pastes meeting notes or a transcript. Also use to re-process unprocessed notes already in 00-Inbox/Meetings/. Not for prepping an upcoming meeting; use `meeting-prep`."
model_hint: balanced
hooks:
  PostToolUse:
    - matcher: Write
      type: command
      command: "node .claude/hooks/post-meeting-person-update.cjs"
---

## Execution mode

Run inline in the current conversation. This skill asks the user for the
transcript, so it cannot be delegated to a subagent that has no way to reach
them. Do not fork, and do not call the Agent tool.

The only exception is a bulk re-processing pass over many existing unprocessed
notes in `00-Inbox/Meetings/`, where the user explicitly asks for a background
run. In that case the gathering phase may be delegated using
`AGENT_INSTRUCTIONS.md`. Everything else — asking for the paste, confirming soft
commitments, resolving ambiguous person matches, presenting the summary — stays
in this conversation.

**If any delegated run fails, times out, or returns nothing usable,** say so
plainly and run the processing inline from the same `AGENT_INSTRUCTIONS.md`.

**A report from a subagent is a claim, not evidence.** Before repeating its
counts, verify them cheaply against the vault:

- Every task it says it created: confirm the ID appears in `03-Tasks/Tasks.md`.
- Every meeting it says it stamped: confirm the `tasks-extracted` marker is in
  that note.
- Every person or company page it says it created: confirm the file exists.

If a claim does not hold, say so and treat that meeting as unprocessed.

# Process Meetings

Turn a meeting transcript the user pastes into Claude into a structured meeting
note in the vault, with person and company pages updated, tasks extracted to
`03-Tasks/Tasks.md`, and everything linked together.

**There is no automatic meeting sync.** Granola, Otter, Zoom and Teams are not
connected. Meetings arrive one way: the user pastes the transcript (or the
summary plus transcript) into the conversation. Never tell the user to check a
sync, never offer `/granola-setup`, and never report "no meetings synced" —
if there is nothing to process, ask for a paste.

## Arguments

- No arguments: ask the user to paste the transcript (Step 1)
- Transcript already pasted in this conversation: skip the ask, process it
- `"search term"`: find an existing note in `00-Inbox/Meetings/` by title or
  attendee and re-process it
- `--people-only`: only update person/company pages (skip tasks)
- `--no-todos`: create the note but don't extract tasks
- `--backlog`: process unstamped notes already in `00-Inbox/Meetings/`

---

## Process

### Step 1: Get the Transcript

If the user has already pasted a transcript or meeting notes in this
conversation, use it and go straight to Step 2. Don't ask for something you
already have.

Otherwise ask for it, in one short message:

> "Paste the meeting transcript here — the summary and the transcript if you
> have both, or just whatever you've got. I'll handle the rest."

Accept whatever shape it arrives in: a full recorder export with an overview,
key takeaways, next steps and a verbatim transcript; a bare transcript; or
rough typed notes. Work with what's there and never ask the user to reformat it.

**Only ask follow-up questions when the answer changes the note.** Everything
below is usually inferable from the paste itself, so infer first and ask only
what you genuinely can't resolve:

- **Date:** read it from the paste. If absent, assume today and say so in one
  line rather than asking.
- **Title:** derive it from the subject matter and the attendees, matching the
  vault's existing naming (for example "Aimee Chess Check-in", "CNL Week 0
  Working Session"). Confirm the title with the user when presenting the
  summary, not before processing.
- **Attendees:** read them from the attendee line or from the speaker labels in
  the transcript.
- **Company:** default to the user's own company from
  `System/user-profile.yaml` for an internal meeting; use the client's name
  when the meeting is clearly external.

Batch anything you genuinely must ask into a single question, not a series.

### Step 2: Write the Meeting Note

Create `00-Inbox/Meetings/YYYY-MM-DD - {Title}.md` in the vault's established
format:

```markdown
---
date: YYYY-MM-DD
time: "HH:MM"
type: meeting-note
source: manual-paste
title: "{Title}"
participants: ["{Name}", "{Name}"]
company: "{Company}"
duration: "{Duration, if stated}"
---
# {Title}

**Date:** YYYY-MM-DD | **Duration:** {duration}
**Attendees:** [[Firstname_Lastname|Firstname Lastname]], {names without pages left plain}

## Overview

{2-4 sentences: what the meeting was about and what changed as a result.}

## Key Decisions

- **{The decision in bold}** — {the reasoning, constraint or caveat behind it.}

## Discussion Notes

### {Topic}
{What was actually said, with names, numbers, dates and constraints. Prose, not
bullets. One section per substantive topic.}

## Action Items

### For Me
- [ ] {Task}

### For Others
- [ ] {Name}: {Task}

```

Rules for the note itself:

- **Only what's in the transcript.** Every claim must be traceable to the
  paste. Don't infer decisions that weren't made or soften ones that were.
- **Keep the specifics.** Names, dates, numbers, deadlines, the exact wording of
  a commitment. Those are the reason the note exists.
- **Wiki-link people who have pages**, plain text for those who don't (Step 3
  may create the page; link it then).
- **Leave the raw transcript out of the note** unless the user asks for it. The
  structured note is the artifact. If the transcript is worth keeping, save it
  under the same date as `YYYY-MM-DD - {Title} - transcript.md`.
- **Split "For Me" from "For Others" accurately.** Only items the user
  themselves owns go under "For Me" — those become tasks in Step 5. Items owned
  by other people stay as a record and never become the user's tasks.
- **Personal and off-topic chat does not go in the note.** Leave, family,
  weekend plans and similar are not meeting content.

Write the note, then show the user the Overview, Key Decisions and both Action
Items lists for confirmation before creating any tasks.

### Step 3: Update Person Pages

For each participant:

1. **Load the email domain** from `System/user-profile.yaml` (`email_domain`).

2. **Classify Internal/External:** domain matches → Internal, otherwise
   External. With no email address, infer from context (a colleague named in
   internal discussion is Internal; a named client contact is External). When
   genuinely unclear, ask rather than guess.

3. **Look up the person** with the Work MCP `lookup_person` tool.
   - If it returns `ambiguous: true`, do not create a page. Surface the possible
     matches to the user.
   - If a match exists, update that existing page.

4. **If no match exists**, call the Work MCP `create_person` tool with `name`,
   `role` when known, `emails` when available, `location` (internal/external),
   the company, and a short source note. Do not hand-write the page template.

5. **If the page exists**, add the meeting under "Recent Interactions" inside
   the `<!-- dex:auto:recent-interactions -->` block, in exactly this format:

   ```
   - [{Meeting Title}](00-Inbox/Meetings/{date} - {Title}.md) — {date}
   ```

   Keep a maximum of 20 entries, drop the oldest, and update `last_interaction`
   in the frontmatter. If a line for that meeting path is already there, change
   nothing.

6. **Capture significant context.** If the transcript reveals a role change,
   a new reporting line, a project someone now owns, or a standing
   constraint, update that person's "Key Context" section. This is the whole
   point of processing a meeting — don't skip it because it wasn't an action
   item.

### Step 4: Update Company Pages

For each external company mentioned as a counterparty:

1. Check whether `05-Areas/Companies/{Company}.md` exists.
2. If not, create it with an Overview table, Key Contacts linking the person
   pages, Meeting History, and a note that it was auto-created from the meeting.
3. If it exists, add any new contacts to "Key Contacts" and the meeting to
   "Meeting History".

Skip this for a purely internal meeting.

### Step 4.5: Enrichment

**Soft commitments (always runs).** Run the Work MCP `detect_soft_commitments`
tool over the discussion notes to catch the things the user said they'd do
without writing them down ("we should revisit pricing", "let me think about the
migration", "I'll take a look at that"). Also read for them yourself — the
transcript is right there and a pasted conversation carries far more of these
than a recorder summary does.

**Never auto-create a task from a soft commitment.** List each one, marked
*(soft commitment — confirm before creating)*, and let the user decide.

**Semantic links (if QMD available).** Check the QMD `status` tool. If healthy,
use `query` to link the meeting to related projects in `04-Projects/` and to
find earlier mentions of new people. If QMD isn't installed, skip silently.

### Step 5: Extract Tasks (unless --no-todos or --people-only)

For each unchecked item under "## Action Items > ### For Me":

1. Extract the task description.
2. **Infer the pillar** by matching the task against each pillar's `keywords`
   and `description` in `System/pillars.yaml`, and resolve it to the unique
   pillar `id`. Per CLAUDE.md, default to Customer Experience when no pillar
   clearly matches.
3. **Preserve the exact source checkbox line text** verbatim for
   `stamp_source_line`.
4. Create the task, letting `create_task` generate the ID and stamp it back:

   ```
   create_task(
     title: "{task description}",
     priority: "P2",   // P1 if the transcript says urgent or names a deadline today
     pillar: "{resolved pillar ID}",
     people: ["{participant page paths}"],
     source: "{meeting note path}",
     stamp_source_line: "{exact source checkbox line text}"
   )
   ```

   `people` values must resolve to existing person page paths — prefer the ones
   returned by Step 3. If only a bare name is available, pass that name
   unchanged and let `create_task` resolve it. Never construct or guess a path.

   **Why `stamp_source_line` is mandatory:** completion sync only finds a line
   containing BOTH a checkbox AND the `^task-YYYYMMDD-XXX` anchor. Omit the
   stamp and the action item is permanently invisible to sync.

5. **Verify every result before marking the meeting extracted:**
   - Require `success: true` for every `create_task` call.
   - Require either `stamp.stamped: true`, or `reason: "already_anchored"` with
     that line's existing anchor equal to the returned `task.task_id`.
   - If creation or stamping is unresolved, surface the exact failed line and
     leave the meeting unstamped. Do not retry a task that was created but not
     stamped.

6. **Only after every action item is verified**, append the marker to the note:

   ```markdown
   <!-- tasks-extracted: 2026-10-28T10:30:00Z -->
   ```

   **The marker is a one-way door.** Stamping a note whose tasks failed to
   create loses those action items silently. When in doubt, leave it unstamped
   and say so.

7. **Also stamp a meeting with nothing to extract.** A note with no action items
   still gets the marker once processed; an unstamped note keeps being flagged
   as waiting.

A note containing `<!-- dex:skip-processing -->` is excluded entirely: no tasks,
no stamp.

### Step 6: Auto-link People in the Note

After finishing edits, run once for the note:

```bash
node .scripts/auto-link-people.cjs "<note-file>"
```

Use `--dry-run` first to preview.

### Step 7: Verify Entity Coverage

Run `node .scripts/meeting-intel/verify-entities.cjs` and show its one-line
summary. If `ENTITY_SUGGESTIONS_FILE` lists suggested people, list them and ask:
"Want me to create these pages? (`dismiss` or `never` also fine)"

- Accepted: call `create_person`, mark the suggestion `accepted`, set the
  contact state to `created` with its page path.
- Dismissed: mark the suggestion `dismissed`.
- Never: mark the suggestion `suppressed`.

### Step 8: Summary Report

```
## Meeting Processed ✅

**Note:** [2026-10-28 - {Title}](00-Inbox/Meetings/2026-10-28 - {Title}.md)

### Updates Made

**Person pages:**
- Created: 1 new (Neels Oosthuizen)
- Updated: 2 existing (Aimee Malan, Olivia Landsberg)

**Company pages:** none (internal meeting)

**Tasks extracted:** 6 items added to 03-Tasks/Tasks.md

| Task | Pillar | ID |
|------|--------|-----|
| ... | ... | task-20261028-001 |

### Needs You

- Soft commitments detected, *(confirm before creating)*: [list, or none]
- Ambiguous person matches: [list, or none]
- Entity suggestions awaiting a decision: [list, or none]
- Action items left unstamped because a task failed: [list with the exact line]
```

---

## Backlog Mode (`--backlog`)

To catch up on notes already in `00-Inbox/Meetings/` that were never processed:

```bash
find 00-Inbox/Meetings -name "*.md" -mtime -30 | head -50
```

A note is unprocessed if it has no `<!-- tasks-extracted: -->` marker and no
`<!-- dex:skip-processing -->`. Report what's waiting, then run Steps 3-7 for
each one the user confirms. Skip Steps 1-2: the note already exists.

---

## Error Handling

For MCP responses, follow CLAUDE.md's `feature_status` rendering convention.

**If the user runs the skill with nothing pasted:** ask for the transcript
(Step 1). That is the normal path, not an error.

**If `create_task` fails:** report the exact action item line that failed, leave
the note unstamped, and keep going with the remaining items. Never silently drop
one.

**If `lookup_person` is ambiguous:** never guess. Show the candidates and ask.

---

## Examples

```
/process-meetings
```
> "Paste the meeting transcript here — the summary and the transcript if you have
> both, or just whatever you've got."

```
/process-meetings
[user pastes a transcript]
```
> "Processing the Aimee / Neels / Chess catch-up from today. Here's the note
> before I create tasks..."

```
/process-meetings --backlog
```
> "3 notes in 00-Inbox/Meetings/ have never been processed. Want me to do all
> three?"

```
/process-meetings --people-only
```
> "Updating person and company pages only, skipping task extraction."

---

## Track Usage (Silent)

Update `System/usage_log.md` to mark meeting processing as used.

**Analytics (Silent):**

Call `track_event` with event_name `meeting_processed` and properties:
- `meetings_count`: number of meetings processed
- `people_created`: number of new person pages created
- `todos_extracted`: number of tasks extracted

This only fires if the user has opted into analytics. No action needed if it
returns "analytics_disabled".
