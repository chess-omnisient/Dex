---
name: release-comms-board-prep
description: "Get the Release Communications ClickUp board into shape. Stage 1 triages candidate dev tickets — named by the user, or found by the `release comms` tag across the sprint list and wider workspace — proposing a Release Type, then creating, linking and assigning each confirmed one on the board. Stage 2 grooms each in-scope release comms ticket: friendly name, Development Summary, Release Comms Description, and Knowledge Base Resource. Run before release-notes-writer. Use to groom, triage, tidy, or populate release comms tickets."
effort: medium
output: "Writes to ClickUp only after the user confirms each write: creates tickets on the Release Communications board (stage 1) and updates their name/markdown_description (stage 2). No file is saved; the triage list and the pre-write preview are the review surfaces."
---

# Release Comms Groomer

Gets the **Release Communications** board (list `901218643488`,
https://app.clickup.com/9012824942/v/li/901218643488) into shape. It's upstream of
`release-notes-writer`, which reads `### Release Comms Description` and `#### Knowledge Base Resource`
close to verbatim as client copy. Not for writing the release notes article itself.

- **Stage 1, triage:** runs when there are candidate dev tickets, from either source:
  - **Named by the user** — a list of ticket links or IDs given this run. Usually the stories that
    shipped, but can also be a flagged subtask or any other ticket.
  - **Discovered by tag** — dev tickets carrying the `release comms` tag, found by scanning the current
    sprint list *and* the wider workspace, subtasks included (Step 2a). The tag is a deliberate human
    marking, so acting on it is not guessing. The tag is the scope: a tagged ticket counts wherever it
    lives, including off the sprint list and under a parent epic.

  Never infer a candidate any other way: status, sprint membership, ticket name and squad are all
  guesses, and guessing stays banned. With no named tickets and no tagged ones, skip to Stage 2.
- **Stage 2, grooming:** always runs, on tickets created in Stage 1 and anything already qualifying on
  the board.

## Rules

**Confirm before every ClickUp write.** A write is any create, update, link, assignment, comment or
field change. Before it, say what will change (ticket name and ID, from what to what) and wait for a
yes, scoped as follows:

- **Stage 1:** the user's Step 4 triage answer is the confirmation for the creates, links and assignments
  it names, and nothing else.
- **Stage 2:** before Step 10, show every ticket groomed this run in one list (old name to new name, and
  the sections to be written) and wait for a yes. Write only what that list showed.
- Anything outside those two lists gets its own confirmation, even mid-run.

**Stage 1**

- **Dedupe is mandatory, and carries more weight on discovered tickets.** Fetch each candidate with
  `include: ["linked_tasks"]`. If a linked task already sits on list `901218643488`, it's already
  tracked: don't create another, note it in the summary. Tag-discovered candidates were not hand-picked
  by the user, so name every already-tracked skip in the handoff rather than dropping it silently — a
  dedupe miss has to be visible.
- **Closed dev tickets are in scope for discovery.** Shipped work is exactly what needs comms, so
  include closed tickets and show each candidate's status in the triage list.
- **Subtasks named by the user are triaged anyway.** Flag a ticket with a non-null `parent` as
  "subtask of <parent name/id>" in the triage list, but triage the exact ticket named; don't redirect to
  the parent. Everywhere else (Stage 2, auto-discovery), a task with a non-null `parent` is never a
  release item.
- **Release Type is your proposal, the user's call.** Propose Hotfix/Patch/Minor/Major/Standard from the
  dev ticket's actual scope and impact. Never create a ticket the user didn't confirm, or with a Release
  Type the user hasn't seen.
- **Release Window** is asked once per run and applied to every ticket created that run (same format as
  `release-notes-writer`, e.g. "August 2026").
- **Assignee is always the current user** via `clickup_resolve_assignees(["me"])`. This puts new tickets
  straight into Stage 2's scope, so one run can triage, create, and groom.
- **Initial body** is the board's blank template with "Link ticket" checked; name it with the dev
  ticket's own name as a placeholder (Stage 2 renames it in the same run):
  ```
  ### Release Comms Description
  E.g. Context of this communication

  #### To do:
  - [x] Link ticket
  - [ ] Review task list
  ```

**Stage 2**

- **Scope:** tickets on list `901218643488` assigned to the current user (`filter_tasks` with
  `list_ids`, `assignees`, `include_closed: false`, `subtasks: false`) where **both** `Release Type`
  and `Release Window` are set. Map stored indexes to `type_config.options`; don't hardcode
  index-to-name. Drop tickets with neither field (deliverable or comms containers such as Banner,
  Article, Intercom, Product Tour, Pre-release Email, Newsletter, Townhall Deck) without flagging, and
  drop the generic `[Month] Release [Year]` container by name. Never groom outside this scope unless
  the user names a ticket.
- **Already groomed means skip, and match the heading loosely.** A ticket is groomed if **any** Release
  Comms Description block holds real copy — anything other than the placeholder
  ("E.g. Context of this communication" or empty). Don't touch it; note it as skipped. Redo only a
  ticket the user names for a redo.
  - **Loose matching.** Authors write this heading freehand. Treat `Release-Comms Description:`, a
    missing `###`, a different heading level and similar near-misses as the section. Existing copy
    must never be mistaken for an absent section, because the cost of a false negative is overwriting
    good client copy.
  - **Duplicate template blocks.** Tickets on this board often carry the template twice: real copy
    under one heading, then a second heading still holding the placeholder. One real block makes the
    ticket groomed — the trailing placeholder never makes it ungroomed. Flag each duplicate in the
    handoff and offer to strip the leftover block as its own confirmed write. Leaving it risks
    `release-notes-writer` reading "E.g. Context of this communication" as client copy.
- **No linked dev ticket means flag, not guess.** Don't write content, don't rename, and never link a
  dev ticket on the user's behalf in Stage 2. Report "no ticket linked".
- **Never touch the `#### To do:` checklist.** Stage 1 checking "Link ticket" on tickets it just
  created is the only exception.
- **Multiple linked dev tickets make one combined write-up**, with no per-story subheadings. Use
  sub-bullets only for genuinely distinct sub-features. If the linked tickets look unrelated, flag and
  ask rather than force an incoherent combined write-up.
- **Ground every sentence in the linked dev tickets.** No invented functionality, no plausible filler.
- **Knowledge Base Resource:** write only a link the user gave or confirmed for that ticket, or the
  literal word "None". Never guess one or reuse another ticket's link.
- **Voice:** Release Comms Description is client-facing; write it in the
  `release-notes-tone-and-structure.md` voice (present tense, plain, no promotional language; "now" and
  "you can now" are correct here). Development Summary is internal (CS and Accounts reading the board):
  plain and non-technical, no article framework voice needed.

## Process

### Step 1: Ground Yourself

Read `references/release-notes-tone-and-structure.md`. Product facts come from the linked dev tickets
(the original user stories) and existing Intercom articles. If you need context neither gives, ask the
user to add it rather than filling the gap yourself.

### Step 2: Resolve Named Tickets And Window (Stage 1)

Resolve each named ticket with `clickup_get_task`. If the user gave none, still go to Step 2a — tag
discovery can supply candidates on its own; only skip ahead to Step 6 once both sources come back
empty. Ask for the Release Window if not given, and ask once the candidate list is settled so a run
that finds nothing never asks for it. If `clickup_resolve_assignees(["me"])` doesn't resolve cleanly,
ask who to assign and filter by.

### Step 2a: Resolve The Current Sprint And Discover Tagged Tickets

Skip this step only if the user named tickets and asked for those alone.

Sprint lists live in folder `90128918665` ("2026 Sprints"), named `Sprint N (M/D - M/D)` with the
sprint's own date range in the name. Resolve the current sprint by finding the list whose range
contains today's date; derive the year from the folder, don't assume the current one. If no list
matches, or more than one does, ask which sprint to scan rather than guessing.

**The tag is the scope, not the list.** Work marked `release comms` routinely sits outside the sprint
list — on a squad's own list, on a "Shared with me" list, or as a subtask of a parent epic. Scanning
only the sprint list silently drops it, and the miss is invisible: the run reports a clean discovery
while shipped work goes uncommunicated. Discovery therefore runs twice, and both passes are mandatory.

1. **Sprint list pass.** `clickup_filter_tasks` on the resolved sprint list with
   `tags: ["release comms"]`, `include_closed: true`, **`subtasks: true`**.
2. **Workspace pass.** `clickup_filter_tasks` with `tags: ["release comms"]`, `include_closed: true`,
   `subtasks: true` and **no `list_ids`**, so the whole workspace is covered. If the tool requires a
   scope, repeat it per space — at minimum Platform Development (`90124084325`) and every space the
   sprint's squads work in, including shared ones. Results outside the sprint list are candidates like
   any other; their list is not a filter.

Merge both passes, de-duplicating by task id, and add the results to the Step 4 triage list alongside
any named tickets. Mark each one's source (named, sprint-list, or off-list), its status, and its list
name where that isn't the sprint list — the user needs to see that an item came from elsewhere.

**Subtasks are in scope for discovery.** A tagged subtask of a parent epic is a real candidate: teams
split delivery into child stories and tag the child that ships the user-visible change. Flag it as
"subtask of <parent name/id>" in the triage list and triage the tagged ticket itself, not the parent.
This overrides the general Stage 2 rule that a task with a non-null `parent` is never a release item;
that rule governs grooming scope on the board, not tag discovery.

**Report the scan, not just the hits.** In the Step 11 handoff, name every list the discovery covered
and how many tagged tickets each returned. A reader cannot tell a genuinely empty sprint from a scan
that looked in one place, so state where you looked.

If both passes return nothing, say so plainly and continue to Stage 2 — an empty tag result means no
dev ticket has been marked for comms, not that discovery failed.

### Step 3: Dedupe And Check For Interrupted Runs

Apply the dedupe and subtask rules. Then check the board for a ticket with the dev ticket's own name
and no linked task: that's an earlier run that stopped between create and link. Don't create another;
link the existing one in Step 5 and say so in the handoff.

### Step 4: Present For Triage

In one scannable list, show each remaining candidate: name, one-line context from its own description,
proposed Release Type, and subtask flag. Get back which to create, any type corrections, and intent on
flagged subtasks, in one round trip.

### Step 5: Create, Link, And Assign

For each confirmed ticket, create it on list `901218643488` with the placeholder name and blank body,
the confirmed `Release Type`, the run's `Release Window`, and the current user as assignee. Link it to
the dev ticket with `clickup_add_task_link` (native task link, not a custom field). Link each ticket
straight after creating it, before moving to the next.

### Step 6: Resolve Scope (Stage 2)

Resolve the current user's ID with `clickup_resolve_assignees(["me"])` if Step 2 didn't already.

### Step 7: Pull Candidates And Linked Dev Tickets

Read-only. `clickup_filter_tasks` on list `901218643488` with `assignees: [<user id>]`,
`include_closed: false`, `subtasks: false`, plus any tickets the user named. For each, get
`custom_fields`, `linked_tasks` and `description` (from the filter results where present, otherwise
`clickup_get_task`). Map each dropdown's stored index through its `type_config.options`; never
hardcode index to name. Drop tickets missing either Release Type or Release Window (unless named) and
the `[Month] Release [Year]` container. Mark `groomed` any ticket where **any** Release Comms
Description block holds anything other than "E.g. Context of this communication" or nothing, matching
the heading loosely per the Stage 2 rules (`Release-Comms Description:`, a missing `###` and similar
near-misses all count). Mark `duplicate_template` any ticket carrying the block more than once. Mark
`no_link` any ticket with no linked task. For every ticket not `groomed`, fetch each linked dev ticket
with `description` and `custom_fields`.

Skip `groomed` tickets unless the user named them for a redo, flag `no_link` ones, and list every
`duplicate_template` ticket in the handoff with the cleanup offer.

### Step 8: Write The Development Summary

- **Functional description:** what the change does, in product and feature terms a non-engineer can
  follow. No implementation detail or internal system names a CS or AM reader wouldn't recognize.
- **Friendly summary:** one short paragraph on what it means in practice.

### Step 9: Confirm Angle And KB Link, Then Write The Release Comms Description

Check each ticket for a perspective fork: the ticket's "Business Value" reads as an internal driver
(compliance, data hygiene, risk closure, tech debt) while the client-visible surface is a UI mechanism
(a warning, status, confirmation, notification). Example: "Disconnect Ad Account and Unshare Linked
Audiences" states its value as closing a data-handling gap, but the client sees the disconnect warning,
the affected-audience list, the "Disconnecting" and "Disconnected" states, and the notifications.

In one round trip across every ticket groomed this run, ask:

- which angle leads, for each ticket with a fork
- the Knowledge Base Resource for each ticket. Suggest 1 to 3 candidates by running `search_articles`
  in Intercom on the feature's distinctive terms. Offer only published articles as title plus URL; for
  a draft say "draft exists: <title>". The user picks one, gives another link, or says None. A suggestion
  is not an answer.

Then write the description for the audience that will read the release note. For smaller emphasis or
tone reframes that aren't a real fork, use judgment and log the divergence in the handoff.

Before any ticket is updated, check every description written this run yourself:

- **Claims:** each statement traces to the linked dev ticket. Rewrite anything that describes unshipped
  work as live or names an internal codename, client or competitor.
- **Copy:** it follows `references/release-notes-tone-and-structure.md`.

### Step 10: Update The Ticket

- **Rename:** drop any leading ticket-code prefix ("ECEN 02-03 |", "AUDACT |", "FMCG 04a-02 |") and
  internal shorthand. Keep a "Fix:" prefix on bug fixes. Title Case, covering the actual change.
- **Body:** insert `### Development Summary` immediately before `### Release Comms Description`, replace
  the placeholder with the Step 9 content, then insert `#### Knowledge Base Resource` right after it with
  the user's link (as a markdown link) or "None". Leave `#### To do:` exactly as is, after all three.
- **Normalise on write.** A ticket being written gets the exact heading `### Release Comms Description`,
  whatever variant it used before, because `release-notes-writer` reads that heading literally. Remove
  any duplicate template block in the same write, keeping one `#### To do:` checklist with its boxes
  untouched. Normalising is only ever part of a write the user already confirmed — never reformat a
  ticket the run is otherwise skipping.
- Use `clickup_update_task` with `name` and `markdown_description`.
- Note the old name in the handoff so the rename can be reversed.

### Step 11: Handoff Summary

This skill writes to ClickUp with no draft folder because the audience is internal. The triage pass,
the Stage 2 pre-write list and this summary are the review surfaces: don't skip any of them or
understate a divergence. Report:

- **Stage 1:** every list the tag scan covered (sprint list and workspace/space passes) and how many
  tagged tickets each returned, then tickets created
  (dev ticket to new ticket, Release Type), already tracked, declined after triage, and subtasks
  triaged on user confirmation. Mark each created ticket's source (named, sprint-list, or off-list, with
  its list name when it came from elsewhere), and name every already-tracked skip rather than only
  counting them.
- **Stage 2:** tickets groomed (old name to new name, single or combined), skipped as already groomed,
  and skipped for no linked dev ticket.
- Tickets carrying a duplicate template block, with the offer to strip the leftover placeholder. Until
  that happens, `release-notes-writer` may read the placeholder as client copy.
- Tickets whose release-note angle materially diverged from the raw dev work, with the reason. These
  need user review before anything downstream treats them as final.
- Tickets written with "None" for Knowledge Base Resource. They need a KB link before
  `release-notes-writer` can give them a "Learn more" line.
