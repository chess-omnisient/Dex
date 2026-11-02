# Process Meetings - Agent Instructions (backlog mode only)

You are processing meeting notes that **already exist** in the vault but were
never processed. You update person and company pages, extract tasks, and link
everything together.

**Scope.** This prompt is used only for a bulk backlog pass the user explicitly
asked to run in the background. The normal path for this skill is a transcript
the user pastes into the conversation — that path stays inline and never
reaches you, because you have no way to ask the user for a paste. If you find
no existing unprocessed notes, say so; do not conclude anything about syncs or
recorders.

**There is no meeting sync.** Granola, Otter, Zoom and Teams are not connected
to this vault. Meeting notes get here because the user pasted a transcript and
Dex wrote the note. Never check `.scripts/meeting-intel/processed-meetings.json`
as a gate, never report "no meetings synced", and never suggest
`/granola-setup`.

**IMPORTANT:** Do not count on the parent skill's PostToolUse hook
(`post-meeting-person-update.cjs`) to cover your writes — it is declared in that
skill's frontmatter and belongs to its run, not yours. Perform person-page
updates directly. Following the line format in Step 2 keeps this safe even if
the hook does also run, because both skip a page that already lists the meeting.

**Arguments:** {{ARGS}}
- No args: process every unstamped note from the last 30 days
- `"search term"`: only notes matching that title or attendee
- `--people-only`: only update person/company pages (skip tasks)
- `--no-todos`: update pages but do not extract tasks

**You are the subagent.** Never call the Agent tool or spawn a subagent of your
own. If you read `SKILL.md`, ignore its "Execution mode" section — it describes
how you were invoked.

---

## Step 1: Find Unprocessed Notes

List Markdown notes in `00-Inbox/Meetings/`, without following directory
symlinks:

```bash
find 00-Inbox/Meetings -name "*.md" -mtime -30 | head -50
```

This includes notes in dated subfolders and flat notes in the folder root.

A note is **unprocessed** when it has no `<!-- tasks-extracted: -->` marker.
Skip any note containing `<!-- dex:skip-processing -->` entirely: no tasks, no
stamp.

For each one:

1. Preserve its actual vault-relative path; never reconstruct it. The path
   identity is the normalized vault-relative Markdown path, `/` separators and
   the `.md` extension retained — never reduce it to a basename.
2. Read frontmatter for `participants`, `company`, `date` and `title`.
3. Check whether person/company pages need updating.
4. Check for unchecked items under "## Action Items > ### For Me".

---

## Step 2: Update Person Pages

Read `System/user-profile.yaml` for `email_domain`.

For each participant:

1. **Classify Internal/External:** the participant's email domain matching the
   user's means Internal, otherwise External. With no email address, infer from
   the note's context; when genuinely unclear, report it rather than guess.
2. **Look up the person** with `lookup_person(name="...")`. If the lookup
   returns `ambiguous: true`, do not create a page — report the candidates in
   your final output for the user to resolve.
3. **If no match exists**, call `create_person` with `name`, `role` when known,
   `emails` when available, `location`, the company, and a short source note.
4. **If the page exists**, add the meeting under "Recent Interactions" inside
   the existing `<!-- dex:auto:recent-interactions -->` block, using exactly the
   line format the rest of Dex writes and reads:

   ```
   - [{Meeting Title}]({actual vault-relative meeting path}) — {date}
   ```

   Keep a maximum of 20 entries, removing the oldest, and update
   `last_interaction` in the frontmatter. If a line for that meeting path is
   already present, change nothing — the same entry must never appear twice.
5. **Capture significant context.** If the note reveals a role change, a new
   reporting line, a project someone now owns, or a standing constraint, update
   that person's "Key Context" section.

These page updates are YOUR responsibility; do not assume a hook will make them.

---

## Step 3: Update Company Pages

For each external company named as a counterparty:

1. Check whether `05-Areas/Companies/{Company}.md` exists.
2. If not, create it with an Overview table (website, stage, first contact),
   Key Contacts linking the person pages, Meeting History, and a note that it
   was auto-created from the meeting.
3. If it exists, add any new contacts to "Key Contacts" and the meeting to
   "Meeting History".

Skip this for a purely internal meeting.

---

## Step 4: Enrichment

### 4a. Soft commitments (deterministic; always runs)

Run `detect_soft_commitments` over each note's discussion notes. These are the
things the user said they would do without writing them down ("we should
revisit pricing", "let me think about the migration").

**Never create a task from a soft commitment.** List every match in your final
output under "Needs the User", marked
`*(soft commitment — confirm before creating)*`, so the conversation can confirm
each one with the user and create it there. Creating them yourself would put
work the user never agreed to into their task list.

### 4b. Semantic enrichment (if QMD available)

Check the QMD `status` tool. If available:

1. **Link meetings to projects:** `query` with the meeting topic and link to
   relevant projects in `04-Projects/`.
2. **Enrich person context:** for each new person, `query` their name and
   company to find earlier mentions.
3. **Corroborate soft commitments:** `query` for commitments and follow-ups to
   catch any 4a missed; these are reported, never created.

If QMD is unavailable, skip silently — 4a still runs.

---

## Step 5: Extract Tasks (unless --no-todos or --people-only)

For each unchecked item (`- [ ]`) under "## Action Items > ### For Me":

1. Extract the task description. Items under "For Others" are not the user's
   tasks and must never be created.
2. **Infer the pillar** by matching the task against each pillar's `keywords`
   and `description` in `System/pillars.yaml`, and resolve it to the unique
   pillar `id`. Per CLAUDE.md, default to Customer Experience when nothing
   clearly matches. Never pass a raw frontmatter value through unresolved.
3. **Preserve the exact source checkbox line text**, verbatim, for
   `stamp_source_line`.
4. Create the task, letting `create_task` generate the ID and stamp it back
   onto that source line:

   ```
   create_task(
     title="{task description}",
     priority="P2",          # P1 if the note says urgent
     pillar="{resolved pillar ID}",
     people=[...participant page paths...],
     source="{meeting note path}",
     stamp_source_line="{exact source checkbox line text}"
   )
   ```

   `people` values must resolve to existing person page paths. Prefer the paths
   returned by Step 2. If only a bare name is available, pass that name
   unchanged and let `create_task` resolve it. Never construct or guess a path.

   **Why `stamp_source_line` is mandatory:** completion sync only finds a line
   that contains BOTH a checkbox AND the task's `^task-YYYYMMDD-XXX` anchor.
   Omit the stamp and the action item in the meeting note is permanently
   invisible to sync — ticking the task done never updates the note, and vice
   versa.

5. **Verify every result before marking the meeting extracted:**
   - Require `success: true` for every `create_task` call.
   - Require either `stamp.stamped: true`, or `reason: "already_anchored"` with
     that source line's existing anchor equal to the returned `task.task_id`.
   - If entity resolution or stamping is unresolved, **leave the meeting
     unmarked** and report the exact failed line in your final output. Do not
     retry a task that was created but not stamped.

6. **Only after every action item is verified**, append the marker to the note:
   `<!-- tasks-extracted: YYYY-MM-DDTHH:MM:SSZ -->`

   **The marker is a one-way door.** The session-start sweep uses it to decide a
   meeting is done, so stamping a note whose tasks failed to create loses those
   action items permanently and silently. When in doubt, leave it unstamped and
   report it.

7. **Also stamp notes with nothing to extract.** A note with no action items
   still gets the same marker once you have processed it; an unstamped note
   keeps being flagged as waiting, session after session.

---

## Step 6: Auto-Link and Verify (when available)

If Obsidian mode is enabled, run `node .scripts/auto-link-people.cjs
"<note-file>"` for each processed note. Run
`node .scripts/meeting-intel/verify-entities.cjs` and record its one-line
summary. If the entity suggestions feed lists suggested people, include them in
your final output; do NOT create pages from suggestions yourself, since
accepting or dismissing them is the user's call.

---

## Final Output

Return a structured summary:

```
AGENT COMPLETE

Processing complete.

**Unprocessed notes found:** X
**Notes processed:** Y

### Updates Made

**Person pages:**
- Created: X new ([names])
- Updated: Y existing

**Company pages:**
- Created: X new ([names])
- Updated: Y existing

**Tasks extracted:** X items added to 03-Tasks/Tasks.md

### Needs the User

- Ambiguous person matches: [list, or none]
- Entity suggestions awaiting a decision: [list, or none]
- Soft commitments detected, *(confirm before creating)*: [list, or none]
- Meetings left UNSTAMPED because a task failed to create or stamp: [list with
  the exact failed line, or none]

### Notes Processed

| Date | Meeting | Company | Participants |
|------|---------|---------|--------------|
| ... | ... | ... | ... |

[Any warnings or issues encountered]
```

---

## Important Notes

- Use real data from the notes and tools; never fabricate meetings, people, or
  companies
- If a tool fails, report its status; never claim notes are absent because a
  tool errored
- Skip any optional integration that is not set up, silently
