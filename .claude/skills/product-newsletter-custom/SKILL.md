---
name: product-newsletter-custom
description: "Draft the Omnisient product newsletter email for a release comms window from the Release Communications ClickUp board. Asks for the sprint window and the comms month, finds the tickets marked for the newsletter, turns each one's Release Comms Description into a short headline and body paragraph, and builds a branded HTML email with placeholder images for the dated header and each news piece. Use when the user says 'write the newsletter', 'draft the product newsletter', 'build the what's-new email', 'the monthly customer email', or asks for the newsletter for a given month. Not for the longer client-facing release notes article; use release-notes-writer. Not for grooming the ticket copy this reads; use release-comms-board-prep."
effort: medium
output: "A single standalone HTML email saved to 04-Projects/Release_Comms/newsletters/newsletter-YYYY-MM.html, with labelled placeholder boxes for the header graphic and each news-piece image for the user to swap. Read-only in ClickUp; nothing is sent."
---

# Product Newsletter

Builds the monthly product newsletter email from the **Release Communications** board: the short,
2-up "what's new" email that goes out to platform users, not the full release notes article.

Downstream of `release-comms-board-prep` (which writes the ticket copy this reads) and a sibling of
`release-notes-writer` (same source, same window, longer article, different medium). Run those for
their own outputs; this one only makes the email.

## Fixed Rules

- **Board:** Release Communications, list `901218643488`
  (https://app.clickup.com/9012824942/v/li/901218643488).
- **Read-only in ClickUp.** This skill never creates, updates, closes or comments on a ticket.
- **This skill never sends.** It writes an HTML file. The user puts it into the email platform.
- **Two windows, asked separately, and they differ by design.** `Release Window` tracks the sprint; the
  newsletter goes out the following month. `Release Window: September 2026` produces the
  **October 2026** newsletter. Expected, not a bug. Never derive one from the other silently: ask both
  (see **Ask The User**) and state the pairing back before drafting.
- **Any tag excludes a ticket.** Cross-client items carry no tags; client-scoped and internal ones do
  (`shoprite`, `transunion`, `altronhealthtech`, `fnb`, `mena`, `internal`, `airvantage`, and new ones
  over time). Treat "has a tag" as the signal, not a name list. Flag a tag whose meaning is genuinely
  unclear instead of guessing.
- **Ground every piece in a real ticket.** No invented features, no plausible filler, no invented KB
  link where the ticket says "None". If the copy isn't on the board, ask for it.
- **Never generate the images.** Placeholders only, labelled with what belongs there (Step 6).

## How Newsletter Items Are Marked

A news piece is **the parent of a `Newsletter Section` subtask** — never the subtask, never the
`[Month] Release [Year]` container, and never a `Newsletter` subtask (which is a "send the
newsletter" checklist item with no copy). `references/newsletter-copy-and-layout.md` §12 has the
full rule and the 2 traps that catch this: blank board-template scaffolding, and tickets marked for
a future window.

## Ask The User

Ask these two up front, in one message, before any ClickUp call:

1. **Sprint window** — the `Release Window` value exactly as it reads on the board, e.g.
   "September 2026". Offer the board's current options if they're unsure.
2. **Release comms window** — the month the newsletter goes out, e.g. "October 2026". Normally the
   month after the sprint window; confirm rather than assume, since skipped months happen.

Ask these only when they come up:

- **Lead order**, when more than 2 pieces qualify. Don't guess relative importance.
- **Missing copy**, when a selected ticket has no `### Release Comms Description`. Ask the user for
  comms-ready copy; never draft from the `### Development Summary`, which is written for engineers.
- **Intro angle**, only if the pieces don't share an obvious theme (Step 5).

Always ask, once the pieces are selected (Step 4):

- **The Intercom article link for each news piece** — the "Learn more →" target. Ask for all of them
  in one message, listing each piece by headline, and show the ticket's
  `#### Knowledge Base Resource` beside it as a suggestion where it holds a real URL. The field is
  frequently "None" or "TBC", so the user's answer is the source of truth and overrides it.
- **The release notes article link** — the "Read the full release notes →" target in the intro.

A piece with no link is allowed: say so, and render it with the "Learn more →" line removed rather
than a dead or guessed link.

## Process

### Step 1: Confirm The Two Windows

State the pairing back in one line before doing anything else:

> Sprint window **September 2026** → newsletter for **October 2026**. Correct?

Wait for a yes. A wrong pairing pulls the wrong release's content and is invisible later in the HTML.

### Step 2: Pull The Window's Tickets

Read-only on list `901218643488`. `filter_tasks` ignores custom field filters, so run 2 queries and
merge, deduping by ID:

1. `include_closed: true`, `subtasks: true`, `date_closed_from` the 1st of the sprint-window month,
   `date_closed_to` the last day of the following month.
2. `include_closed: false`, `subtasks: true`, no date bound.

Always run both. Shipped work is closed work, so closed tickets are in scope.

### Step 3: Select The News Pieces

From the merged set:

1. Find every subtask named `Newsletter Section`.
2. For each, take its `parent` — that's the candidate news piece.
3. Fetch each parent with `include: ["custom_fields", "description"]`. Map each dropdown's stored
   index through its `type_config.options`; never hardcode index to name.
4. Keep it when `Release Window` matches the sprint window and it has no tags. Drop tagged tickets
   and name the tags you dropped. Drop the `[Month] Release [Year]` container by name.

**When nothing is marked:** say so plainly, then list the window's untagged **Major and Minor**
tickets as candidates (ID, name, Release Type) and ask which to include. Don't auto-include them, and
don't stop the run — an ungroomed board is the normal case, not an error.

Note per kept ticket: ID, name, URL, Release Type, the text under `### Release Comms Description`
(or `MISSING`), and the text under `#### Knowledge Base Resource` (or `None`).

### Step 4: Check The Content

For each kept ticket, run the editorial check from
`references/newsletter-copy-and-layout.md`: internal-only names, codenames, client names, competitor
references and ticket jargon get flagged to the user, not published. Where the description is
`MISSING`, ask the user for copy (see **Ask The User**).

**Then ask for the links.** In one message, list each selected piece and ask for its Intercom
article URL, plus the release notes article URL for the intro. Where the ticket's
`#### Knowledge Base Resource` holds a real URL, show it as the suggested answer; where it says
"None", "TBC" or is missing, say so and leave it blank for the user to fill.

Verify each URL the user gives with `get_article` on its article ID:

- **Found and published** — use it as the "Learn more" target.
- **Found but draft** — customers can't open it. Tell the user it's still a draft and ask whether to
  publish it first or drop the link for now.
- **Not found** — say so and ask again; never guess a replacement or fall back to the ticket's field
  after the user has given an answer.

### Step 5: Write The Copy

Read `references/newsletter-copy-and-layout.md` in full before writing a word. It carries the
headline formula, the body-paragraph shape, the length budgets and the worked example from the
September 2026 edition.

Per piece: one **headline** (title case, 3–8 words, the user-facing outcome) and one **body**
paragraph of 2–3 sentences, condensed from that ticket's Release Comms Description. The newsletter is
shorter than the release notes article: cut the bullet lists, keep what the reader gains.

Then the **intro**: "Hi there," plus 1–2 sentences naming what this release focuses on, written after
the pieces so it reflects what's actually in them.

### Step 6: Build The HTML

Start from `references/template.html` and fill its `{{TOKENS}}`; don't rebuild email-safe markup from
scratch. `references/newsletter-copy-and-layout.md` §7 explains why the layout is shaped that way, and
what changes with 1 or 3 pieces instead of 2. Table-based layout, inline styles, 800px — email
clients, not browsers.

Every image is a **labelled placeholder** `<div>`, never a generated graphic and never an empty box.
Each placeholder states exactly what belongs there and at what size, so the user can swap it without
reopening the skill:

- **Header graphic** — the gradient banner carrying the comms month, e.g. "What's new in October 2026".
- **One per news piece** — a product screenshot of the feature described.

Keep each placeholder's `id` stable (`img-header`, `img-piece-1`, …) so a later pass can find it.

### Step 7: Disclosure Check Before Saving

This file goes to every platform user, so a leak here reaches customers. Before saving, run the
disclosure checklist in `references/newsletter-copy-and-layout.md` §11 against the fully assembled
copy and confirm each line of it out loud. It covers client names, person names, ticket and dev
story IDs, internal roadmap language, and anything described as live that isn't.

A hit is not something to fix silently. Name it, show the line, and ask the user before changing or
cutting it. If any hit is unresolved, don't save.

### Step 8: Save And Hand Off

Save to `04-Projects/Release_Comms/newsletters/newsletter-YYYY-MM.html`, named for the **comms**
month. Create the folder if missing. Don't overwrite an existing file without saying so and asking.

Then read the saved file back and confirm before reporting done: it exists, every `{{TOKEN}}` is
filled, and each placeholder id named in the handoff is actually present. Never claim the newsletter
is ready on the strength of having written it.

In the handoff, give:

- The file path, and both windows as confirmed in Step 1.
- Each piece included: ticket name, ID, headline.
- Every image placeholder still to be filled, by id and what it needs.
- Anything flagged: missing copy, dropped tags, ambiguous tag, draft or dead KB link, editorial
  concern.
- The reminder that nothing was sent and no ticket was changed.

## What Good Looks Like

A reader who uses the platform daily skims it in under a minute and knows what changed and whether
they need to act. Two pieces, 35–55 words each, every claim traceable to a ticket.

**Anti-patterns, in the order they actually happen:**

- **Pasting the Release Comms Description straight in.** It's written for the article and carries a
  bullet list. The email needs it condensed to 2–3 sentences, or the piece runs triple length.
- **Headlining with the ticket name.** "Locked project screen shows every locking reason at once" is
  a ticket. "Locked Projects: See Every Blocking Issue At Once" is a headline.
- **Marketing adjectives.** "Powerful", "seamless", "game-changing". Say what it does.
- **Generating the images.** Placeholders only, always.
- **Filling a thin month.** One real piece beats two where the second is padding. Say the month was
  quiet and ask whether to send at all.
- **Silently pairing the wrong windows.** The sprint window and the comms month differ by design;
  confirm the pairing rather than deriving it (Step 1).
