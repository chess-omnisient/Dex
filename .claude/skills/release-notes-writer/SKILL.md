---
name: release-notes-writer
description: "Draft the client-facing release notes article for a release window (e.g. \"July 2026\") from the Release Communications ClickUp board: Major/Minor items plus any Patch items the user wants disclosed, no client-tagged or internal items, each item's comms copy and KB link taken from its ticket, written in the release-notes tone, then saved as a markdown file or written to the Intercom article as a draft. Use to generate, draft, or update release notes. Not for help articles; use help-article-writer."
effort: medium
output: "The user's choice: a markdown file saved where they say for review, or written straight to the target Intercom article as a draft once the user confirms (never published)."
---

# Release Notes Writer

Pulls qualifying items from the **Release Communications** board, applies the release-notes tone and
structure, and drafts the article for the user to review before it goes live. Not for individual help
articles: `help-article-writer` refuses release-note framing because the two have opposite voice rules.
Run `release-comms-board-prep` first; it writes the ticket copy this skill reads.

## Fixed Rules

- **Board:** Release Communications, list `901218643488`
  (https://app.clickup.com/9012824942/v/li/901218643488).
- **Read-only in ClickUp.** This skill never changes a ticket.
- **Release Type:** Major and Minor by default. Patch items go in when the user wants to disclose them
  to customers, and then only the ones they name. Never Hotfix unless the user says so.
- **Any tag excludes a ticket.** Cross-client items carry no tags; client-scoped and internal items do
  (`shoprite`, `transunion`, `altronhealthtech`, `fnb`, `mena`, `internal`, and new ones over time).
  Treat "has a tag" as the signal, not a name list. If a tag's meaning is genuinely unclear, flag it.
- **Ignore subtasks and the generic `[Month] Release [Year]` container** (e.g. "August Release 2026"),
  whatever their fields say. All content lives on the parent ticket; a parent with no comms copy is a
  gap to flag, never something to find on a child task.
- **Sourcing:** `### Release Comms Description` is the copy, `#### Knowledge Base Resource` is the KB
  link (or "None"), `#### To do:` is an internal checklist to ignore. Run the framework's editorial
  check before using ticket copy: internal-only names, competitor references, and ticket jargon get
  flagged, not published.
- **Article title is the Release Window month + 1.** `Release Window` tracks the sprint; the article is
  titled for the month the newsletter goes out. `Release Window: July 2026` lands in **"Release Notes:
  August 2026."** This is expected, not a bug.
- **Ground every item in a real ticket.** No invented items, no plausible filler, no invented KB link
  where the ticket says "None".
- **This skill never publishes.** It saves a markdown file or writes the confirmed target article as an
  Intercom draft (Step 7); the user publishes in Intercom. Call `update_article` or `create_article`
  only on that confirmed article, never on any other article, and never in a scheduled run.

## Ask The User

Ask only these by default:

1. **Release window** (e.g. "July 2026"), mapped to the `Release Window` field.
2. **Are there Patch items to disclose to customers this run?** Ask every time. Default is none.

Ask only when it comes up:

- **Lead order,** if more than one Major item qualifies. Don't guess relative importance.
- **Target article,** only if the lookup in Step 2 is ambiguous or finds nothing. If it doesn't exist,
  ask whether to create it (`create_article`).
- If the user gives a different angle for an item, use it in place of (not blended with) that ticket's
  copy, still grounded in what the ticket says the feature does. Everything else comes from its ticket.

## Process

### Step 1: Ground Yourself

Read `references/release-notes-tone-and-structure.md` in full; it's the complete rule set for how the
article reads. Find 1 or 2 recent release notes articles with `search_articles` ("Release Notes") and
read them with `get_article` as a tone and structure check.

### Step 2: Find The Target Article

Search Intercom for "Release Notes: [Release Window month + 1] [Year]" with `search_articles`. Don't
assume an article titled for the Release Window month is the right one. Name the article by title and
ID in the handoff.

### Step 3: Pull Candidate Tickets

Read-only ClickUp fetch on list `901218643488`. `filter_tasks` ignores custom field filters, so run 2
queries and merge, deduping by ID: (1) `include_closed: true`, `date_closed_from` the 1st of the window
month, `date_closed_to` the last day of the following month; (2) `include_closed: false`, no date
bound. Always run both.

Drop subtasks, the `[Month] Release [Year]` container task, and any ticket with a tag (note the tags
you dropped). For each remaining ticket get `custom_fields` and `description`. Map each dropdown's
stored index through its `type_config.options`; never hardcode index to name. Keep tickets where
Release Type is Major or Minor (or a Patch ticket the user named) and Release Window matches. Drop
tickets with neither field set.

For each kept ticket note: ID, name, URL, Release Type, the text under `### Release Comms Description`
(or `MISSING`), and the text under `#### Knowledge Base Resource` (or `MISSING`).

### Step 4: Check The Content

Pass a tag whose meaning is genuinely unclear back to the user rather than assuming. For each kept
ticket, ask the user for comms-ready copy where the description is `MISSING`; never draft from the
engineering description. Run the framework's editorial check on each description: internal-only
names, competitor references, and ticket jargon get flagged, not published.

### Step 5: Order And Draft

Majors first, in the user's order; the lead Major gets the most detail (bullets if it has several
parts, a warning callout if the ticket calls for one). Minors follow, shorter, in ticket order unless
the user says otherwise. Apply the framework's heading, bullet, KB link, and divider conventions,
especially its 2 strict rules: every item heading is H2, and every `<hr>` has one blank line above and
below. Note the banner image as a placement note only (`Release Notes.png` style); this skill doesn't
generate images.

### Step 6: Check KB Links, Review, Save, And Hand Off

Check each "Learn more" link with `get_article` on the article ID in the link:

- **Found and published:** fine.
- **Found but draft:** customers can't open it. Flag it and leave the link out until it's published.
- **Not found:** flag it; don't guess a replacement.

The ticket's link is corrected only on the ticket, by `release-comms-board-prep` or the user.

Then check the draft yourself: nothing pending described as live, no internal names, codenames, client
names or competitors, and the copy follows the framework. Item copy comes from its ticket, so don't
rewrite it to apply a finding. List each finding against its ticket in the handoff for the user to
accept, and change the draft only for those they accept.

In the handoff, list the target article (title and ID), the tickets included (with IDs), what was
flagged and why (missing copy, ambiguous tag, editorial concern, KB link), and the Major ordering.

### Step 7: Save Or Write To Intercom

Ask the user which they want:

- **Markdown file:** ask where to save it, then save
  `release-notes-{release-window-slug}-{YYYY-MM-DD}.md` there with `status: draft`.
- **Intercom draft:** write it to the confirmed target article as a draft. If the target article is
  already published, `update_article` changes it live; say so and get an explicit yes first. Never set
  `state: published`; the user publishes in Intercom.

Before any Intercom write, scan the draft for placeholder or AI text that must not land in the article:
`MISSING` copy, flagged items, the banner placement note, notes to the reviewer, and anything addressed
to the user rather than the reader. List what you found and ask whether to resolve, remove or keep each
one. Then name the target article by title and ID and wait for a yes before the call. Write only to the
confirmed article.

`update_article`'s `body` is raw HTML, and whitespace between block tags becomes blank paragraphs. Butt
tags together with no newlines or indentation, and make each deliberate blank line an explicit
`<p>&nbsp;</p>`. 2 things a live push showed are easy to get wrong:

- **Give the "Learn more" link the same spacer as the `<hr>`:** a `<p>&nbsp;</p>` before the link
  paragraph, as framework rule 7 requires around every `<hr>`.
- **Check headings landed as true Heading 2.** `<h2>` in the payload doesn't reliably survive Intercom's
  editor. After pushing, re-open the article (or ask the user to look) and fix any downgraded heading
  in the editor.
