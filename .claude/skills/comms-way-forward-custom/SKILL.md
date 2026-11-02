---
name: comms-way-forward-custom
description: Prepares the Product Release Comms Way Forward deck for the upcoming sprint. Always reads the previous sprint's comms wrap-up first for real action item statuses and settled comms decisions, then pulls live release tasks from the ClickUp Release Communications Board, reconciles the two and reports any conflicts, shows a preview for confirmation, and generates a sprint-named HTML file and PDF ready to circulate.
---

# Comms Way Forward

Prepares the Product Release Comms Way Forward deck for the upcoming sprint. Reads the previous
sprint's comms wrap-up for what was actually decided and completed, pulls live release tasks from the
ClickUp Release Communications Board, reconciles the two, shows a preview for confirmation, then
generates a sprint-named HTML file and PDF ready to circulate.

**The wrap-up is not optional.** ClickUp holds tickets; the wrap-up holds the decisions made about
them. A deck built from the board alone reports finished work as outstanding and re-opens questions
the last session already closed.

## Usage

```
/comms-way-forward-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August"
/comms-way-forward-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August" --release-date "6 August 2026"
```

**Flags:**
- `--sprint <N>` — sprint number, required (e.g. `7`)
- `--window "<name>"` — release window name exactly as it appears in ClickUp (required)
- `--release-date "<date>"` — optional human-readable release date; derived from `--window` if omitted

---

## Step 1 — Resolve sprint metadata

Parse flags. Derive the month and year from the `--window` string if `--release-date` is not provided (e.g. "July 2026 Window — Sprint 7, release 6 August" → month/year = "July 2026", release date = "6 August 2026").

Set the following variables for use throughout:
- `SPRINT_NUM` = the number from `--sprint`
- `SPRINT_LABEL` = "Sprint {N} 2026" — used in `slide-section-label` divs on data slides
- `COVER_SUBTITLE` = "Sprint {N} Planning Session" — used on the cover slide
- `MONTH_YEAR` = month + year derived from window (e.g. "July 2026")
- `WINDOW_NAME` = the full `--window` string, passed verbatim to ClickUp

If `--sprint` or `--window` is missing, report:

```
Usage: /comms-way-forward-custom --sprint <N> --window "<ClickUp window name>"
Example: /comms-way-forward-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August"
Both flags are required.
```

Abort.

---

## Step 2 — Read the previous sprint's wrap-up (MANDATORY)

**Never build a way forward deck from ClickUp alone.** The board holds tickets; it does not hold the
decisions the last session made about them. Those live in the previous sprint's wrap-up deck, and
skipping it produces a deck that re-asks settled questions and reports completed work as outstanding.

Read `sprint{N-1}-comms-wrap-up.html` in the deck directory. If it is missing, say so plainly and
continue — but tell the user the carry-over statuses and comms decisions are unverified, and do not
present invented statuses as fact.

Extract three things:

1. **Action item statuses** from the "Sprint {N-2} & {N-1} Action Items – Follow-Up" slide. Each row
   carries an explicit Done / To do. These are the real statuses for the way forward deck's
   "Revisiting Actions from Sprint {N-1}" slide. Carry forward the wrap-up's status verbatim; never
   default every row to "Carried over", and never infer a status from outside evidence (a published
   article does not close an item the wrap-up still lists as To do — the item may have further steps).

2. **Items rolling to this sprint**, from the "Items Rolling to Sprint {N}" slide. Each row carries a
   **Decision** that is already settled. Honour it:
   - A decision of "internal comms only" means no client-facing comms slide entry and no action item
     asking whether a client article is needed.
   - "No comms this sprint" means the item is reported as deferred, not raised as a TBC.
   - A Release Type stated here (e.g. Minor) overrides the ClickUp Release Type when the two disagree;
     flag the disagreement to the user rather than silently picking one.

3. **Comms status and tier placement** for anything that appeared in the wrap-up's own Major / Minor /
   Patch slides, so an item does not silently change tier between decks.

Then reconcile against the ClickUp pull in Step 3. Report every conflict to the user in the Step 6
preview — a ticket whose board state contradicts a wrap-up decision is the single most important thing
for them to see, because the wrap-up decision is usually the newer and more considered of the two.

Tickets created on the board *after* the wrap-up date have no wrap-up entry. That is expected, not a
conflict; treat them as new and mark them as such in the preview.

---

## Step 3 — Query ClickUp Release Communications Board

Use `clickup_filter_tasks` on list **`901218643488`** (Release Communications Board).

Filter by:
- Release Window custom field = `WINDOW_NAME` (exact match)
- Include assignees and all custom fields in the response

Group the returned tasks by their Release Type custom field value:
- **Major** — Release Type = Major
- **Minor** — Release Type = Minor
- **Patch** — Release Type = Patch
- **Hotfix** — Release Type = Hotfix

Ignore tasks with Release Type = Standard or Internal (these do not appear in the deck).

If zero tasks are returned across all groups, report:

```
No tasks found for window: "{WINDOW_NAME}"
Check that this matches the exact Release Window field value in ClickUp, then re-run.
```

Abort.

---

## Step 4 — Enrich each task

For every task returned, resolve the following three attributes:

### a. Platform / Data Product tag

Check the task's assignee list:
- Olivia Landsberg (member ID `87874670`) is an assignee → tag = **Platform** (`tag-platform`)
- Tristan Venter (member ID `99769856`) is an assignee → tag = **Data Product** (`tag-dataproduct`)
- Neither → mark as **untagged** (dealt with in Step 5)

If both assignees are present on one task, apply the primary assignee's tag. If unclear, flag as untagged.

### b. Client tag

Scan the task name for known client indicators (case-insensitive):

| Pattern in task name | Client tag |
|---|---|
| Shoprite / SHNS / SHAV / FMCG / RM- | `tag-shoprite` |
| TransUnion / TU- / BI Viz | `tag-transunion` |
| FNB | `tag-fnb` |
| AirVantage / Airvantage | `tag-airvantage` |
| None of the above | No client tag (platform-wide) |

### c. Proposed comms status

Check the task description and any subtask names for comms deliverable keywords (email, banner, article, product tour, newsletter, intercom, etc.):
- If confirmed comms deliverables are evident in the description or completed subtasks → mark as **Confirmed** (will render in green `.confirmed-cell`)
- Otherwise → mark as **TBC — to discuss in session** (will render in amber `.tbd-cell`)

### d. Minor: platform-wide vs client-specific

- No client tag identified in step (b) → platform-wide (goes in left column)
- Any client tag identified → client-specific (goes in right column)

---

## Step 5 — Resolve untagged tasks

If any tasks were flagged as untagged (neither Olivia nor Tristan in assignees), present them for manual classification:

```
The following tasks have no Platform/Data Product assignee. Please classify each:

  [1] {task name} — assignees: {comma-separated names or "unassigned"}
  [2] {task name} — assignees: {comma-separated names or "unassigned"}

Reply with: 1=platform 2=data-product
(or "skip" to leave untagged — they will appear without a tag pill)
```

Wait for the user's response before continuing. Apply their classifications.

If there are no untagged tasks, skip this step silently.

---

## Step 6 — Preview and confirm

Before generating the HTML, show a structured summary of what will be written:

```
─────────────────────────────────────────────
Sprint {N} | {WINDOW_NAME}
─────────────────────────────────────────────

MAJOR RELEASES ({count})
  • {task name} [Platform | Data Product] — Confirmed / TBC
  ...

MINOR RELEASES ({count})
  Platform-wide ({count}):
    {task names}
  Client-specific ({count}):
    {task names with client}

PATCH & HOTFIX ({count})
  • {task name} [Patch | Hotfix] — Confirmed / TBC
  ...

CARRIED OVER FROM SPRINT {N-1} ({count})
  Done ({count}):      {items the wrap-up marked Done}
  Still open ({count}): {items the wrap-up marked To do}

CONFLICTS WITH THE SPRINT {N-1} WRAP-UP ({count})
  • {task name} — board says {X}, wrap-up decided {Y} on {date}
  ...

DECISIONS REQUIRED ({TBC count} items)
  • {task name}
  ...
  (excludes anything the wrap-up already settled)
─────────────────────────────────────────────
Proceed? Press Enter to generate the deck, or reply with corrections.
```

Wait for user confirmation or corrections. If the user provides corrections (e.g. "move X from minor to patch", "mark Y as confirmed"), apply them before proceeding.

**The conflicts block is not optional.** If it is empty, print "No conflicts with the Sprint {N-1}
wrap-up" so the user can see the check ran. An item the wrap-up settled must never reappear as a
decision required — that is the main failure this step exists to catch.

---

## Step 7 — Read CSS from template

Find the most recently modified file matching `sprint wrap up and way forward/product-release-comms-way-forward*.html`.

If no file is found, report:
```
No existing deck found in "sprint wrap up and way forward/". The skill uses the most recent deck's <head> block for CSS.
Create or place a deck file there and re-run.
```
Abort.

Extract the full `<head>` block from that file (from `<!DOCTYPE html>` through `</head>`) and copy it verbatim into the new file. This preserves the Poppins font, brand palette, and all CSS classes without duplication.

---

## Step 8 — Generate the HTML

Assemble the new HTML file in this slide order. The deck is **not** four slides — that was an early
version. The shipped format, set by the Sprint 10 deck, is:

1. **Cover**
2. **Agenda** + Sprint {N-1} Spotlight (5 headline carried-over items, owner + item)
3. **Revisiting Actions from Sprint {N-1}** — statuses taken from the Step 2 wrap-up, not invented
4. *(continued)* — split when the table exceeds ~7 rows
5. **Major Releases** — one release per slide when a row's text is long
6. *(continued)*
7. **Minor Releases – Platform-wide**
8. **Minor Releases – {Client}** — one slide per client grouping
9. **Minor Releases – {Other clients}**
10. **Patch & Hotfix Releases**
11. **Action Items Out of Sprint {N}**

Split any slide rather than letting it overflow (see the fit rules at the end of this step). Add an
**AM Actions** slide carrying a ready-to-send client email only when something in the window has
actually shipped and warrants a client notification.

### Slide 1 — Cover

Use the same `.slide-cover` structure as the template cover slide. Set:
- `.cover-label` text → `INTERNAL`
- `.cover-title` text → `Product Release Comms Way Forward`
- `.cover-subtitle` text → `COVER_SUBTITLE` (e.g. "Sprint 7 Planning Session")

### Slide 2 — Major Releases

```html
<div class="slide">
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading">Major Releases</div>
  <table class="tier-table">
    <thead>
      <tr>
        <th style="width:27%">Feature / User Story</th>
        <th style="width:43%">Description</th>
        <th style="width:30%">Proposed Comms</th>
      </tr>
    </thead>
    <tbody>
      <!-- one <tr> per major task -->
    </tbody>
  </table>
</div>
```

For each major task row:
- Feature cell: task name + `<span class="client-tag tag-platform">Platform</span>` or `tag-dataproduct`
- Description cell: task description (truncate to 2–3 sentences if long)
- Comms cell: confirmed text in `class="confirmed-cell"`, or `class="tbd-cell"` for TBC

### Slide 3 — Minor Releases

```html
<div class="slide">
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading">Minor Releases</div>
  <div class="minor-grid">
    <div class="minor-col platform">
      <div class="minor-col-header">Platform-wide</div>
      <!-- one .minor-item per platform-wide task -->
    </div>
    <div class="minor-col client-spec">
      <div class="minor-col-header">Client-Specific</div>
      <!-- one .minor-item per client-specific task, with client tag pills -->
    </div>
  </div>
</div>
```

**Markup note:** the shipped decks do not use `.minor-item` divs and the template CSS defines no such
class. Each `.minor-col` holds an `<h4>` header and a `<ul>`, with one `<li>` per task (`<li class="tbd">`
for TBC items). Follow the template's actual markup, not the `.minor-item` shape sketched below.

Each minor list item:
- Platform-wide: task name + Platform/Data Product tag pill + comms note (`.comms-note`)
- Client-specific: task name + client tag pill (e.g. `tag-shoprite`) + Platform/Data Product tag pill + comms note
- TBD items: add class `tbd` to the `.minor-item` div

### Slide 4 — Patch & Hotfix Releases

```html
<div class="slide">
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading">Patch &amp; Hotfix Releases</div>
  <table class="tier-table tier-table-sm">
    <thead>
      <tr>
        <th style="width:30%">Feature / User Story</th>
        <th style="width:9%">Type</th>
        <th style="width:39%">Description</th>
        <th style="width:22%">Proposed Comms</th>
      </tr>
    </thead>
    <tbody>
      <!-- one <tr> per patch/hotfix task -->
    </tbody>
  </table>
  <!-- Decisions Required note-box -->
</div>
```

For each row:
- Feature cell: task name + Platform/Data Product tag pill
- Type cell: `<span class="tier-badge badge-patch">Patch</span>` or `badge-hotfix`
- Comms cell: `.confirmed-cell` or `.tbd-cell`

Decisions Required block (include if any TBC items exist across all slides):

```html
<div class="note-box" style="margin-top:10px; padding:8px 12px;">
  <strong style="font-size:11.5px;">Decisions required in this session</strong>
  <ul style="margin-top:4px; display:grid; grid-template-columns:1fr 1fr; gap:2px 16px;">
    <li style="font-size:11px; margin-bottom:0;">{task name} — comms scope + owner</li>
    <!-- one li per TBC item across all three slides -->
  </ul>
</div>
```

### Tag pill reference

Use these exact class combinations:

```html
<span class="client-tag tag-platform">Platform</span>
<span class="client-tag tag-dataproduct">Data Product</span>
<span class="client-tag tag-shoprite">Shoprite</span>
<span class="client-tag tag-transunion">TransUnion</span>
<span class="client-tag tag-fnb">FNB</span>
<span class="client-tag tag-airvantage">Airvantage</span>
```

### Slide fit rules (slides are a fixed 960×540 — content does not reflow)

Overflow is silently clipped: the browser shows no error, the PDF simply loses the bottom of the
slide. Budget before generating, then verify after.

- **Dense status tables** (`status-table-dense`, ~9px rows): about **7 rows** fit with a note box
  below, or ~9 without one. Split beyond that and put the note box on the final part only.
- **Tier tables** (`tier-table`, full prose in three columns): about **2 rows** of short text fit.
  A row whose Description or Proposed Comms runs past ~400 characters needs a slide of its own.
- **Split headings** take a part marker: `Major Releases <span style="font-weight:400;
  opacity:0.6;">(1 of 2)</span>`. Keep related rows together when splitting — never separate two rows
  describing the same item.

**Verify visually before reporting done.** Count-based estimates are not enough; a single long cell
overflows a two-row table. Screenshot each dense slide and look at it:

```bash
# split one slide into its own file, then:
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=960,540 --screenshot=slide.png "file:///path/to/slide.html"
```

Check every slide carrying a tier table or more than 6 table rows. A slide whose content ends flush
with the bottom edge is clipped, not merely full.

---

### Print CSS to inject

Add this block inside `<head>` of the generated file, after the main styles, to ensure clean PDF output:

```css
@media print {
  @page {
    size: 960px 540px;
    margin: 0;
  }
  body {
    margin: 0;
    padding: 0;
  }
  .slide {
    page-break-after: always;
    break-after: page;
    width: 960px !important;
    height: 540px !important;
    overflow: hidden;
  }
}
```

---

## Step 9 — Write HTML and export PDF

Write to `sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html`.

If that file already exists, ask:
```
"sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html" already exists. Overwrite? (yes/no)
```
Wait for response. Abort if "no".

After writing the HTML, automatically run the headless Chrome PDF export (no prompt needed). Run it
from the deck directory so the paths stay relative and no absolute user path is hardcoded:

```bash
cd "<deck directory>" && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="product-release-comms-way-forward-sprint-{N}.pdf" \
  "file://$(pwd | sed 's/ /%20/g')/product-release-comms-way-forward-sprint-{N}.html"
```

The deck's own `@page { size: 960px 540px; margin: 0 }` drives the output, so each slide becomes one
720×405pt page (16:9) with no scaling. Chrome logs `CVDisplayLinkCreateWithCGDisplay failed` on macOS
headless — that is harmless noise, not a failure; check the exit code and the written byte count.

If Chrome is not at that path, fall back to `/html-to-pdf-custom`, which renders via Puppeteer.
Verify the result with `mdls -name kMDItemNumberOfPages -name kMDItemPageWidth <pdf>` — expect 4 pages
at 720pt wide.

Confirm both outputs:

```
HTML saved: sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html
PDF saved:  sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.pdf
4 slides | {major} major · {minor} minor · {patch+hotfix} patch/hotfix
```

---

## Error handling

| Condition | Response |
|---|---|
| Missing `--sprint` or `--window` | Show usage, abort |
| No tasks found for window | Report window name, suggest checking ClickUp, abort |
| Previous sprint's wrap-up missing | Say so plainly, continue, and state that carry-over statuses and comms decisions are unverified. Never invent statuses to fill the gap. |
| Board state contradicts a wrap-up decision | Surface it in the Step 6 preview conflicts block and let the user choose. Do not silently pick one. |
| No template HTML in `sprint wrap up and way forward/` | Report and abort |
| Output HTML already exists | Ask before overwriting |
| Headless Chrome PDF command fails | Report the error. HTML file is still saved. Fall back to `/html-to-pdf-custom`, or the user can re-run the export manually. |
| ClickUp MCP unavailable | "ClickUp MCP is not connected. Connect it in Claude Code settings and re-run." Abort. |

---

## Key references

- **Previous sprint's wrap-up:** `Omnisient.CenterofExcellence/sprint wrap up and way forward/sprint{N-1}-comms-wrap-up.html`
  — the authoritative record of action item statuses and comms decisions. Always read it (Step 2).
  Its "Items Rolling to Sprint {N}" slide carries decisions that override the ClickUp board.
- **Release Communications Board list ID:** `901218643488`
- **Olivia Landsberg (Platform):** member ID `87874670`
- **Tristan Venter (Data Product):** member ID `99769856`
- **Release Type values:** Major / Minor / Patch / Hotfix / Standard / Internal
- **Release Window field:** dropdown (field id `5ec0e701-fa08-4b95-bf24-8efa54a54c07`) — pass the plain
  month-year option name, e.g. `"November 2026"`. Options run May 2026 through December 2026. A long
  descriptive string such as `"November 2026 Window — Sprint 11, release 22 November"` matches nothing
  and aborts at Step 3.
- **Release Type field id:** `5433b55a-54c6-4882-968a-8798b0db8414` (Hotfix / Patch / Minor / Major / Standard)
- **Reading field values:** `clickup_get_task` does not expose custom field values in its response. To
  group by Release Type, call `clickup_filter_tasks` once per type with a `custom_fields` filter on both
  the window and the type option id. `task.get_many` via `clickup_execute_operator` returns 400 here —
  do not spend calls on it.
- **Template file location:** `Omnisient.CenterofExcellence/sprint wrap up and way forward/product-release-comms-way-forward*.html` (most recently modified)
- **Output location:** same directory, `product-release-comms-way-forward-sprint-{N}.html` and `.pdf`
- **Logo:** each slide embeds an inline base64 SVG. Reuse the data URI from the template rather than
  regenerating it — the cover uses `filter: brightness(0) invert(1)`, inner slides `height:22px`.

**Note:** This skill uses `clickup_filter_tasks` and related tools. Prefer the `claude_ai_ClickUp` tools if both ClickUp MCP integrations are connected (`clickup-mcp` lacks `clickup_filter_tasks`); fall back to whichever ClickUp MCP is available if names differ slightly.
