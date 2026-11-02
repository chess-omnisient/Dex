---
name: release-notes-writer-custom
description: "Generate a client-facing release notes article for a given release window (e.g. \"July 2026\") by pulling qualifying items from the Release Communications ClickUp board, applying the team's release-notes tone/structure, and drafting into a target Intercom article. Filters to Major/Minor release-type items only, excludes anything tagged to a specific client or marked internal, and pulls each item's ready-made comms description and KB link straight from its ticket. Use when asked to generate, draft, or update a monthly (or ad hoc) release notes article. Not for individual help articles — use help-article-writer for those."
effort: medium
output: "The target Intercom article, updated via update_article (or created via create_article) once the PM confirms the draft. The article is the deliverable — this skill does not write a file."
---

# Release Notes Writer

Generates the monthly (or ad hoc) client-facing release notes article: pulls qualifying items from the
**Release Communications** ClickUp board, applies the team's release-notes tone and structure, and
drafts them into a target Intercom article for the PM to review before it goes live.

**Not for individual help articles.** Use `help-article-writer` for those — it explicitly refuses
release-note framing because the two article types have opposite voice rules (see
`frameworks/release-notes-tone-and-structure.md` vs. `frameworks/article-tone-and-voice.md`).

## What's fixed vs. what to ask for

**Fixed, baked into this skill — don't ask about these:**
- **Board:** Release Communications, `https://app.clickup.com/9012824942/v/li/901218643488`
  (list ID `901218643488`).
- **Release type filter:** Major and Minor only. Never include Patch or Hotfix unless the PM explicitly
  says otherwise for this run.
- **Exclusion rule:** exclude any ticket carrying **any tag at all**. In practice every genuinely
  cross-client item on this board carries no tags, and every client-scoped or internal-only item does
  (`shoprite`, `transunion`, `altronhealthtech`, `fnb`, `mena`, `internal`, and others not yet seen on
  the board). Treat "has a tag" as the signal, not a hardcoded name list — new client tags will show up
  over time that aren't in this list. If a ticket has a tag you don't recognize as client/internal
  and you genuinely can't tell whether it's scoping-relevant, flag it to the PM rather than guessing
  either way.
- **Sourcing within a ticket:** the `### Release Comms Description` section is the copy; the `####
  Knowledge Base Resource` section is the KB link (or "None"); `#### To do:` is an internal checklist,
  ignore it. See `frameworks/release-notes-tone-and-structure.md` for the full sourcing rule and the
  editorial check on ticket copy before it's used verbatim.
- **Tone and structure:** `frameworks/release-notes-tone-and-structure.md` — read this every time, it's
  the complete rule set for how the article reads and is organized.
- **The Intercom article's title is always one month later than the ClickUp `Release Window`.**
  `Release Window` tracks the sprint the work is linked to; the Intercom article is titled for the month
  the newsletter actually goes out, which is the following month. A ticket with `Release Window: July
  2026` lands in an article titled **"Release Notes: August 2026."** Never assume the release window
  month and the article title month are the same — that mismatch is expected, not a bug to flag.
- **Ignore every subtask, always.** All the content lives on the main (parent) ticket. Never open a
  subtask looking for a `Release Comms Description` or a KB link — if a parent ticket doesn't have one,
  that's a gap to flag to the PM, not something to go find on a child task.
- **Ignore the generic `[Month] Release [Year]` container task** (e.g. "August Release 2026") entirely
  — it's a placeholder/tracking task, never a real release item, regardless of what its Release Type or
  Release Window fields say.

**Ask the PM for these — they change every run:**
1. **Release window** — which month (e.g. "July 2026")? Maps to the ticket's `Release Window` field.
   Remember the target Intercom article will be titled for the *following* month.
2. **Target Intercom article** — try to locate it yourself first (title "Release Notes: [Release Window
   month + 1] [Year]"), then confirm the ID/link with the PM before drafting into it — don't rely on the
   title match alone for something client-facing. If it doesn't exist yet, ask whether to create a new
   blank one or use `create_article`.
3. **If more than one Major-type item qualifies** — which leads, and in what order? Don't guess at
   relative importance.
4. **Are there any Patch-type items that should be included this run?** Ask this every time — don't
   wait for the PM to raise it. Default is still to exclude Patch/Hotfix; if the PM names specific
   patch tickets, include only those, not every patch in the window.
5. **Does any qualifying item need to be framed from a different angle than its ticket's `Release
   Comms Description`?** Ask this every time. The ticket copy is the default source, but the PM may
   want a specific item pitched differently for this release (different emphasis, a different
   audience angle, leading with a different benefit) — get that direction before drafting that item,
   and use it in place of (not blended with) the ticket copy for that item only. Everything else still
   comes from its ticket as-is.

## Process

### Step 1: Ground yourself

Read `frameworks/release-notes-tone-and-structure.md` in full — don't rely on the summary above, it's
abbreviated. Then pull 1-2 recent past release-note articles from Intercom (`list_articles` /
`get_article`, `state: published`, titles like "Release Notes: [Month] [Year]"). Those published
articles are the live tone/structure reference and the grounding for house voice and product naming —
the framework doc captures the pattern as of when it was written, not a frozen template.

Everything else comes from the tickets. Don't go looking for company or product context elsewhere: if a
ticket's copy needs context you don't have, that's a gap to flag to the PM, not one to fill from
background knowledge.

### Step 2: Pull candidate tickets

The underlying tool has no working filter for custom field values (Release Window, Release Type) — this
was tested directly against the board: passing a `custom_fields` filter to `filter_tasks` is silently
ignored and returns the unfiltered list. There is no way to ask the API for "just July 2026" directly;
don't try to invent an undocumented parameter for it.

**Pull with two separate queries, not one unbounded scan of the whole board.** An earlier version of
this skill tried to narrow the pull with a single `date_closed_from`/`date_closed_to` query (reasoning:
ticket close dates cluster around the month the newsletter goes out, Release Window month + 1). That's a
real pattern, but it's a trap as the *only* filter: it catches tickets only once they have `date_closed`
set, and silently drops real qualifying tickets that are still open — which is the normal case any time
this skill runs for the *current or upcoming* release window (e.g. drafting the August 2026 window's
article in late August, before its items have shipped). A live run confirmed the failure mode directly: a
date-bounded query for the August 2026 window returned 48 tasks and missed both real qualifying items
(both still open).

The other extreme — always pulling the entire board with no filter — works today (a few hundred tasks,
2-4 pages) but doesn't scale: this board only grows, and most of that growth is old, already-published,
already-closed tickets that will never be relevant again. Re-scanning all of that every run is waste that
compounds over time.

So run two bounded queries and merge the results:

1. **Closed tickets, date-bounded** — `list_ids: ["901218643488"]`, `include_closed: true`,
   `date_closed_from` = the 1st of the Release Window month, `date_closed_to` = the last day of the
   *following* month (Release Window month + 1). This catches everything that's already shipped for the
   window, and stays cheap forever — it's bounded by a 2-month slice, not by total board history.
2. **Open tickets, unbounded** — `list_ids: ["901218643488"]`, `include_closed: false` (or simply omit
   `include_closed`), no date bound. This catches everything still in flight, *regardless of which
   window it belongs to* (an open ticket could be tagged to a past, current, or future Release Window).
   Leaving this unbounded is safe and stays cheap over time for a different reason than query 1: the
   number of currently-open tickets is bounded by the team's active WIP, not by how long the board has
   existed — a well-run board doesn't accumulate thousands of permanently-open tasks the way it
   accumulates closed history. If this query ever comes back suspiciously large (the board isn't being
   kept groomed, or a status change stopped counting as "closed"), flag that to the PM rather than
   silently eating the cost — that's a sign the assumption behind this approach needs rechecking.

Merge and dedupe the two result sets before continuing triage. This is why board status
(`to do`/`in progress`/`in review`/`ready`/`live`) isn't a *relevance* signal for release notes (an open
or closed ticket can equally qualify) — it's only used here to scope which of the two cheap queries
catches a given ticket.

Drop, without further inspection:
- **Any subtask** (a task with a non-null `parent`). All release-note content lives on the parent
  ticket — never open a subtask for content, even if the parent looks incomplete.
- **The generic `[Month] Release [Year]` container task** — a placeholder/tracking task, never a real
  release item.

Drop any remaining ticket with one or more tags per the exclusion rule above.

### Step 3: Filter by release type and window

For each remaining candidate, fetch the full task (`include: ["custom_fields", "description"]`). Read
the `Release Type` and `Release Window` custom fields' `type_config.options` to map the stored `value`
(an index) to its option name — don't hardcode index-to-name, the option order isn't guaranteed stable.
Keep only tickets where Release Type is Major or Minor (or Patch, if the PM opted in for this run) and
Release Window matches the requested month.

A ticket with no value set on either field isn't a release item — drop it without flagging.

### Step 4: Extract each item's content

Per `frameworks/release-notes-tone-and-structure.md`'s sourcing section: pull the `### Release Comms
Description` text and the `#### Knowledge Base Resource` value from each qualifying ticket's
description. Flag (don't silently skip) any qualifying ticket missing the `### Release Comms
Description` section — ask the PM for comms-ready copy rather than drafting from the raw engineering
description. Run the editorial check on each description before using it — internal-only names,
competitor references, or ticket jargon get flagged to the PM, not published as-is.

For any item the PM flagged in scoping question 5, use their stated angle as the basis for that item's
copy instead of the ticket's `Release Comms Description` — still ground it in what the ticket actually
says the feature does, just written from the direction the PM gave, not the ticket's own framing.

### Step 5: Order and draft

Separate Major from Minor items. If multiple Majors, use the PM's stated order from the scoping
question; the lead Major gets the most detail (bullet breakdown if it has multiple parts, a warning
callout if the ticket calls for one). Minor items follow, each shorter, in ticket order unless the PM
specifies otherwise. Apply the heading, paragraph/bullet, KB-link, and `<hr>`-divider conventions from
the framework doc — in particular, its two strict formatting rules: every item heading is H2 (`##`),
and every `<hr>` divider has one blank line above and below it. Note the banner image as a placement
note only (`Release Notes.png` style, matching prior releases) — this skill doesn't generate images,
same as `help-article-writer`.

### Step 6: Hand the draft to the PM

Show the full drafted article in the conversation for review — don't write it to a file, and don't push
it anywhere yet. Alongside the draft, list: which tickets were included (with IDs), which were flagged
and why (missing comms description, ambiguous tag, editorial concern), and the lead-Major ordering
decision. Wait for the PM to confirm before touching the Intercom article — this is client-facing and
goes out under the company's name.

### Step 7: Push to Intercom (once confirmed)

This is the skill's output — the Intercom article, not a file. Use `update_article` against the target
article confirmed in scoping (or `create_article` if the PM asked for a new one).

`update_article`'s `body` is raw HTML, and whitespace/newlines between block-level tags become unwanted
blank paragraphs — so the tags themselves must butt together with no newlines/indentation, and any
deliberate blank line has to be an explicit `<p>&nbsp;</p>`. Two things confirmed by a live push that are
easy to get wrong:

- **Give the "Learn more" KB link the same blank-line spacer as the `<hr>` divider gets.** A link
  paragraph placed directly after the item's body paragraph with no spacer reads as butted-up-against it.
  Insert a `<p>&nbsp;</p>` before the link paragraph, the same way the framework doc's rule 7 requires one
  above and below every `<hr>`.
- **Verify headings actually land as a true Heading 2 block, not just a `<h2>` tag in the payload.**
  Sending `<h2>...</h2>` in the API body doesn't reliably survive as a real "Heading 2" style block once
  Intercom's editor renders it — confirmed on a live push where the headings came through but not as H2.
  After pushing, re-open the article (or ask the PM to eyeball it) and confirm each item heading is
  actually styled as Heading 2 in Intercom's own editor; fix in the editor if it downgraded.

## Guardrails

- **Ground every item in a real ticket.** No invented items, no filling gaps with "plausible" copy —
  same hallucination discipline as `help-article-writer`.
- **Tag presence is the exclusion signal, not a fixed name list.** Don't assume you've seen every
  client/internal tag that exists — a new one showing up should still get excluded by the "any tag"
  rule even if it's not in this doc.
- **Don't include Patch/Hotfix items** unless the PM names specific ones in answer to the scoping
  question — never include every patch in the window just because the PM said yes.
- **Don't invent a KB link** where the ticket says "None."
- **Don't publish ticket copy verbatim without the editorial check** — internal context in a ticket
  field is common and easy to miss if you just copy-paste.
- **This skill drafts; it doesn't publish.** Get explicit PM confirmation before pushing to the live
  Intercom article.
- **Don't match the Intercom article by the same month as the Release Window.** They're always one
  month apart (article = Release Window month + 1) — confirm the actual target article with the PM
  rather than assuming a same-named article is the right one.
- **Never source content from a subtask, and never treat the generic `[Month] Release [Year]` container
  as a release item** — both are dropped in Step 2, before any content extraction.
- **Step 2's date-bounded query alone is not enough.** A `date_closed` range filter only catches
  already-closed tickets and silently misses real, still-open qualifying items — confirmed in practice:
  it dropped both qualifying items for a window whose ship month hadn't started yet. Always pair it with
  the unbounded open-tickets query and merge the results — don't skip the second query just because the
  first one came back with results.
