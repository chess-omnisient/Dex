---
name: comms-way-forward-custom
description: Prepares the Product Release Comms Way Forward deck for the upcoming sprint. Pulls live release tasks from the ClickUp Release Communications Board, classifies and tags each item, shows a preview for confirmation, then generates a sprint-named HTML file and PDF ready to circulate.
---

# Comms Way Forward

Prepares the Product Release Comms Way Forward deck for the upcoming sprint. Pulls live release tasks from the ClickUp Release Communications Board, classifies and tags each item, shows a preview for confirmation, then generates a sprint-named HTML file and PDF ready to circulate.

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

## Step 2 — Query ClickUp Release Communications Board

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

## Step 3 — Enrich each task

For every task returned, resolve the following three attributes:

### a. Platform / Data Product tag

Check the task's assignee list:
- Olivia Landsberg (member ID `87874670`) is an assignee → tag = **Platform** (`tag-platform`)
- Tristan Venter (member ID `99769856`) is an assignee → tag = **Data Product** (`tag-dataproduct`)
- Neither → mark as **untagged** (dealt with in Step 4)

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

## Step 4 — Resolve untagged tasks

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

## Step 5 — Preview and confirm

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

DECISIONS REQUIRED ({TBC count} items)
  • {task name}
  ...
─────────────────────────────────────────────
Proceed? Press Enter to generate the deck, or reply with corrections.
```

Wait for user confirmation or corrections. If the user provides corrections (e.g. "move X from minor to patch", "mark Y as confirmed"), apply them before proceeding.

---

## Step 6 — Read CSS from template

Find the most recently modified file matching `sprint wrap up and way forward/product-release-comms-way-forward*.html`.

If no file is found, report:
```
No existing deck found in "sprint wrap up and way forward/". The skill uses the most recent deck's <head> block for CSS.
Create or place a deck file there and re-run.
```
Abort.

Extract the full `<head>` block from that file (from `<!DOCTYPE html>` through `</head>`) and copy it verbatim into the new file. This preserves the Poppins font, brand palette, and all CSS classes without duplication.

---

## Step 7 — Generate 4-slide HTML

Assemble the new HTML file with these four slides in order.

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

Each `.minor-item`:
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

## Step 8 — Write HTML and export PDF

Write to `sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html`.

If that file already exists, ask:
```
"sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html" already exists. Overwrite? (yes/no)
```
Wait for response. Abort if "no".

After writing the HTML, automatically run the Edge headless PDF export (no prompt needed):

```
msedge.exe --headless --print-to-pdf="C:/Users/AimeeMalan/OneDrive - omnisient.com/Documents/GitHub/Aimee's Omnisient repo/sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.pdf" --print-to-pdf-no-header --no-margins --disable-gpu "file:///C:/Users/AimeeMalan/OneDrive%20-%20omnisient.com/Documents/GitHub/Aimee's%20Omnisient%20repo/sprint%20wrap%20up%20and%20way%20forward/product-release-comms-way-forward-sprint-{N}.html"
```

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
| No template HTML in `sprint wrap up and way forward/` | Report and abort |
| Output HTML already exists | Ask before overwriting |
| Edge headless PDF command fails | Report the error. HTML file is still saved. User can re-run PDF export manually. |
| ClickUp MCP unavailable | "ClickUp MCP is not connected. Connect it in Claude Code settings and re-run." Abort. |

---

## Key references

- **Release Communications Board list ID:** `901218643488`
- **Olivia Landsberg (Platform):** member ID `87874670`
- **Tristan Venter (Data Product):** member ID `99769856`
- **Release Type values:** Major / Minor / Patch / Hotfix / Standard / Internal
- **Release Window field:** free-text — must match ClickUp exactly
- **Template file location:** `sprint wrap up and way forward/product-release-comms-way-forward*.html` (most recently modified)
- **Output location:** `sprint wrap up and way forward/product-release-comms-way-forward-sprint-{N}.html` and `.pdf`

**Note:** This skill uses `clickup_filter_tasks` and related tools. Prefer the `claude_ai_ClickUp` tools if both ClickUp MCP integrations are connected (`clickup-mcp` lacks `clickup_filter_tasks`); fall back to whichever ClickUp MCP is available if names differ slightly.
