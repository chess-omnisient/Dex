---
name: comms-wrap-up-custom
description: Prepares the Sprint Product Release Comms Wrap-Up deck — the end-of-sprint session that reviews action items from last time, confirms what's rolling to the next sprint, assigns AM execution owners for client notifications, and locks final comms status for major/minor/patch releases. Pulls from the ClickUp Release Communications Board and the prior sprint's deck, then generates a sprint-named HTML file and PDF.
---

# Comms Wrap-Up

Prepares the **Sprint Comms Wrap-Up** deck — the companion session to `/comms-way-forward-custom`, run near the end of the sprint to close the loop: revisit last session's action items, confirm what rolls to the next sprint, lock in AM execution owners for client-facing notifications, and finalize comms status across major/minor/patch/hotfix releases.

Unlike the way-forward deck (fully derived from ClickUp), several slides here are meeting-driven — action item feedback, agenda, and AM Actions details come from the live session, not a task field. This skill gathers that from the user, pulls the release tables from ClickUp for the rest, and assembles the full deck.

## Usage

```
/comms-wrap-up-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August"
/comms-wrap-up-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August" --session-date "28 July 2026"
```

**Flags:**
- `--sprint <N>` — sprint number being wrapped up, required (e.g. `7`)
- `--window "<name>"` — release window name exactly as it appears in ClickUp, required
- `--session-date "<date>"` — date of the wrap-up session; defaults to today if omitted

---

## Step 1 — Resolve sprint metadata

Parse flags. Set:
- `SPRINT_NUM` = the number from `--sprint`
- `NEXT_SPRINT` = `SPRINT_NUM + 1`
- `SPRINT_LABEL` = "Sprint {N} 2026" — used in `slide-section-label` on data slides
- `WINDOW_NAME` = the full `--window` string, passed verbatim to ClickUp
- `SESSION_DATE` = `--session-date`, or today's date if omitted

If `--sprint` or `--window` is missing, report:

```
Usage: /comms-wrap-up-custom --sprint <N> --window "<ClickUp window name>"
Example: /comms-wrap-up-custom --sprint 7 --window "July 2026 Window — Sprint 7, release 6 August"
Both flags are required.
```

Abort.

---

## Step 2 — Pull last session's open items

Find the most recent prior deck in `sprint wrap up and way forward/` — either a `sprint{N-1}-comms-wrap-up.html` or a `product-release-comms-way-forward-sprint-{N-1}.html`. Prefer the wrap-up if both exist (it reflects the latest decisions).

From that file, extract:
- Any table row or note-box item that reads as an open action, a "Decisions required" list, or (in a prior wrap-up) an "Items Rolling to Sprint {N}" table — these become the starting list for this sprint's **Action Items Follow-Up**.
- Any `.tag-carryover` or explicitly rolled-forward items.

If no prior deck is found, tell the user:

```
No prior deck found in "sprint wrap up and way forward/" to seed action items from.
I can still build the deck — just walk me through the open items directly.
```

Continue rather than aborting; Step 3 will collect them interactively instead.

---

## Step 3 — Collect Action Items Follow-Up

Present the carried-over items (or, if none were found, ask the user to list them) and collect, for each one:
- **Feedback** — what happened since last session (1–3 sentences, names/owners inline in **bold**)
- **Status** — one of `In progress`, `To do`, `Done`, `On hold`, or `TBC — decision today`

Ask in one batch:

```
Action Items Follow-Up — Sprint {N}

For each item below, give me the feedback/update and current status
(in progress / to do / done / on hold / TBC):

  1. {owner} — {item name}
  2. {owner} — {item name}
  ...
```

Wait for the user's response before continuing.

---

## Step 4 — Confirm items rolling to Sprint {N+1}

Ask which items — from the Action Items Follow-Up list, or new items surfaced this sprint — are rolling forward, and for each, collect:
- **Feature / User Story** name + Platform/Data Product tag + client tag(s) if any
- **Type** — `Major` / `Minor` / `Patch` / `Hotfix`
- **Status** — usually `To do`
- **Decision** — the comms decision reached this session (e.g. "no client comms needed", "release notes only", "Intercom article required")

```
Which items are rolling into Sprint {N+1}, and what was decided on each
(comms scope, owner, whether client-facing)?
```

If the user says "closed out" for any item instead (fully resolved, no longer carried), collect it separately for the Agenda slide's "Closed out" note instead of the rollover table.

---

## Step 5 — AM Actions slides

Ask whether any items need a dedicated **AM Actions** slide — these are for client-facing notifications that need a named owner, explicit recipient list, and either an email template or messaging guidelines. Typical triggers: an automatic platform update that affects client integrations, or a client-approval-gated notification to third parties (e.g. banks).

```
Any items this sprint need a dedicated AM Actions slide (owner + recipients +
email template/messaging, beyond the standard release tables)?
```

For each one, collect:
- **Title** and one-line description of what's happening
- **Metadata strip** (3 cards): e.g. Release Date / Notification Deadline / Impacted Clients, or Drafted By / Target / Recipients — whichever trio fits
- Either:
  - **Owner cards** — one per AM: name, client, what they own, recipient To/Cc lists, plus an example email template, **or**
  - **Core messaging + stakeholder directory** — bullet list of approved talking points, plus a stakeholder box grouped by client tag with named contacts and a shared CC line
- Any **watchlist** note (amber `.note-box`) or **status** note (default `.note-box`) to close the slide

Skip this step silently if the user says none are needed.

---

## Step 6 — Pull release tables from ClickUp

Use `clickup_filter_tasks` on list **`901218643488`** (Release Communications Board), filtered by Release Window = `WINDOW_NAME`, same as `/comms-way-forward-custom`. Group by Release Type (Major / Minor / Patch / Hotfix; ignore Standard / Internal).

Enrich each task exactly as in `/comms-way-forward-custom` Step 3 (Platform/Data Product tag from assignee, client tag from name pattern, platform-wide vs client-specific split for Minor). In addition, resolve:

### Status (new for the wrap-up deck)

Read the task's ClickUp status field and map to a badge:

| ClickUp status | Badge class | Label |
|---|---|---|
| Complete / Done | `background:#d1fae5 !important; color:#065f46 !important;` | Done |
| In Progress / Doing | `background:#e0f2fe !important; color:#0369a1 !important;` | In progress |
| To Do / Open | `background:#f1f5f9 !important; color:#475569 !important;` | To do |
| Blocked / On Hold | `background:#fde8e8 !important; color:#b91c1c !important;` | On hold |
| Anything pending a same-session decision | `background:#fff8e1 !important; color:#92400e !important;` | TBC — decision today |

### Proposed comms (refined)

Unlike the way-forward deck's binary Confirmed/TBC, use the actual comms text decided this sprint if it's known (from the task description, completed subtasks, or what the user stated in Steps 3–5). Still render confirmed text with `class="confirmed-cell"` and anything undecided with `class="tbd-cell"`.

If zero tasks are returned, report and ask whether to proceed with only the meeting-driven slides (Agenda, Action Items, Rollover, AM Actions):

```
No ClickUp tasks found for window: "{WINDOW_NAME}"
Continue with just the session slides (Agenda, Action Items, Rollover, AM Actions) and skip
the Major/Minor/Patch tables? (yes/no)
```

---

## Step 7 — Preview and confirm

Show a structured summary before generating anything:

```
─────────────────────────────────────────────
Sprint {N} Comms Wrap-Up | {WINDOW_NAME}
─────────────────────────────────────────────

ACTION ITEMS FOLLOW-UP ({count})
  • {item} — {status}
  ...

ROLLING TO SPRINT {N+1} ({count})
  • {item} [{type}] — {decision}
  ...

AM ACTIONS SLIDES ({count})
  • {title}
  ...

MAJOR RELEASES ({count}) · MINOR — CLIENT-WIDE ({count}) · MINOR — CLIENT-SPECIFIC ({count}) · PATCH/HOTFIX ({count})

DECISIONS STILL OUTSTANDING ({count})
  • {item}
  ...
─────────────────────────────────────────────
Proceed? Press Enter to generate the deck, or reply with corrections.
```

Wait for confirmation or corrections; apply corrections before continuing.

---

## Step 8 — Read CSS from template

Find the most recently modified file matching `sprint wrap up and way forward/*.html`. Extract its full `<head>` block (from `<!DOCTYPE html>` through `</head>`) and copy it verbatim into the new file — this preserves the Poppins font, brand palette, and every CSS class (`tier-table*`, `minor-grid`, `session-card`, `note-box`, `metadata-strip`, `steps-list`, `status-table*`, `client-tag`/`tag-*`, `tier-badge`/`badge-*`) without redefining any of it.

If no template file is found, report and abort:
```
No existing deck found in "sprint wrap up and way forward/" to source CSS from.
Place a deck file there and re-run.
```

---

## Step 9 — Generate the deck

Assemble slides in this order. Reuse `.slide-logo-wrap` (with the Omnisient logo, `height:22px` unless noted) on every non-cover slide.

### Slide 1 — Cover

```html
<div class="slide slide-cover">
  <div>
    <div class="cover-logo-wrap">
      <img src="omnisient-logo.svg" alt="Omnisient" class="slide-logo" style="filter: brightness(0) invert(1);" />
    </div>
    <div class="cover-label">Internal</div>
    <div class="cover-title">Sprint {N} Product Release<br>Comms Wrap-Up</div>
  </div>
  <div class="cover-footer">
    <span>{SESSION_DATE}</span>
  </div>
</div>
```

### Slide 2 — Agenda

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">Session overview</div>
  <div class="slide-heading">Sprint {N} Comms Wrap-Up</div>
  <div style="display:flex; flex-direction:column; gap:10px; flex:1; min-height:0;">
    <div style="font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#0d1b4b;">Session Agenda</div>
    <div style="background:#f0f4fb; border-radius:6px; padding:20px 26px; flex:1;">
      <ol class="steps-list" style="gap:16px;">
        <!-- one <li><span class="step-num">n</span><span>{agenda item}</span></li> per agenda point (4-6 typical) -->
      </ol>
    </div>
    <!-- only if the user named closed-out items in Step 4 -->
    <div class="note-box done" style="margin-top:0; padding:9px 14px;">
      <strong style="font-size:11px;">Closed out</strong><br>
      <span style="font-size:11px;">{closed-out item summary}</span>
    </div>
  </div>
</div>
```

### Slide 3 — Action Items Follow-Up

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">Session overview</div>
  <div class="slide-heading-sm">Sprint {N} Action Items — Follow-Up</div>
  <table class="status-table status-table-compact" style="margin-top:0; table-layout:fixed;">
    <thead>
      <tr>
        <th style="padding:0 8px; text-align:left; font-size:9px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; color:#3a6fd8; border-bottom:1px solid #e4e8f2; width:20%;">Item</th>
        <th style="padding:0 8px; text-align:left; font-size:9px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; color:#3a6fd8; border-bottom:1px solid #e4e8f2; width:66%;">Feedback</th>
        <th style="padding:0 8px; text-align:left; font-size:9px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; color:#3a6fd8; border-bottom:1px solid #e4e8f2; width:14%;">Status</th>
      </tr>
    </thead>
    <tbody>
      <!-- one row per Step 3 item: <td><strong>{owner}</strong> — {item}</td><td>{feedback}</td><td style="{status badge style from Step 6 table}">{status label}</td> -->
    </tbody>
  </table>
</div>
```

If the follow-up list runs past ~10 rows, split across two slides with the same heading (append " (cont.)" to the second) rather than shrinking the font past `font-size:9px`.

### Slide 4 — Items Rolling to Sprint {N+1}

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">Rolling forward</div>
  <div class="slide-heading" style="margin-bottom:10px; padding-bottom:8px;">Items Rolling to Sprint {N+1}</div>
  <table class="tier-table tier-table-roomy">
    <thead>
      <tr>
        <th style="width:24%">Feature / User Story</th>
        <th style="width:8%">Type</th>
        <th style="width:14%">Status</th>
        <th style="width:54%">Decision</th>
      </tr>
    </thead>
    <tbody>
      <!-- one row per Step 4 item; Type = tier-badge (badge-major/minor/patch/hotfix); Status = tier-badge badge-todo (or matching status) -->
    </tbody>
  </table>
</div>
```

### AM Actions slides (0 or more, from Step 5)

Two layouts, both `padding:28px 40px` on `.slide` and both using a `metadata-strip`-style row of 3 inline cards (`background:#f0f4fb` normal, `background:#fef2f2; border:1px solid #fecaca` for the urgent one) directly under the heading, then a `display:grid; grid-template-columns:53% 45%; gap:12px` two-column body.

**Layout A — Owner + email template** (use when there's a concrete outbound notification with To/Cc lists):

```html
<div class="slide" style="padding:28px 40px;">
  <div class="slide-logo-wrap" style="...height:20px..."></div>
  <div class="slide-section-label" style="margin-bottom:4px;">AM Actions</div>
  <div class="slide-heading" style="font-size:18px; margin-bottom:6px; padding-bottom:8px;">{title}</div>
  <div style="display:flex; gap:10px; margin-bottom:7px;"><!-- 3 metadata cards --></div>
  <p style="font-size:10.5px; color:#3a3a55; line-height:1.45; margin-bottom:7px;">{one-line context}</p>
  <div style="display:grid; grid-template-columns:53% 45%; gap:12px; height:340px;">
    <div style="display:flex; flex-direction:column; gap:5px; overflow:hidden;">
      <div style="font-size:9px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#b91c1c;">Owners to execute</div>
      <!-- one owner card per AM, background:#f0f4fb; border-radius:5px; padding:7px 10px; with name/client header, what they own, To/Cc grid -->
      <!-- optional amber watchlist note-box -->
    </div>
    <div style="display:flex; flex-direction:column; overflow:hidden;">
      <div style="font-size:9px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#0d1b4b; margin-bottom:4px;">Example email template</div>
      <div style="background:#f8faff; border:1px solid #dde4f0; border-radius:6px; padding:10px 12px; flex:1; font-size:10px; color:#2c2c44; line-height:1.55; overflow:hidden;">
        <!-- Subject line, divider, Hi, body paragraphs, sign-off -->
      </div>
    </div>
  </div>
</div>
```

**Layout B — Messaging + stakeholder directory** (use when approval is needed before a fixed distribution list, e.g. bank/partner notifications):

```html
<div style="display:grid; grid-template-columns:53% 45%; gap:12px; height:250px;">
  <div style="display:flex; flex-direction:column; gap:5px; overflow:hidden;">
    <div style="font-size:9px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#b91c1c;">Core messaging</div>
    <div style="background:#f0f4fb; border-radius:5px; padding:8px 10px; flex:1; overflow:hidden;">
      <!-- key messaging header + <ul> of → bullet points -->
    </div>
  </div>
  <div style="display:flex; flex-direction:column; overflow:hidden;">
    <div style="font-size:9px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#0d1b4b; margin-bottom:4px;">Key stakeholders</div>
    <div style="background:#f8faff; border:1px solid #dde4f0; border-radius:6px; padding:10px 12px; flex:1; font-size:10.5px; color:#2c2c44; line-height:1.7; overflow:hidden;">
      <!-- one block per client-tag pill with contacts, then a border-top CC line -->
    </div>
  </div>
</div>
<div class="note-box" style="margin-top:8px; padding:7px 12px;"><strong style="font-size:10.5px;">Status:</strong> <span style="font-size:10.5px;">{status note}</span></div>
```

### Major Releases

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading">Major Releases</div>
  <table class="tier-table">
    <thead>
      <tr>
        <th style="width:22%">Feature / User Story</th>
        <th style="width:36%">Description</th>
        <th style="width:30%">Proposed Comms</th>
        <th style="width:12%">Status</th>
      </tr>
    </thead>
    <tbody><!-- one row per major task --></tbody>
  </table>
</div>
```

### Minor Releases — Client-Wide

```html
<div class="slide" style="padding-left:24px; padding-right:24px;">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading-sm">Minor Releases — Client-Wide</div>
  <table class="tier-table tier-table-cozy">
    <thead>
      <tr>
        <th style="width:23%">Feature / User Story</th>
        <th style="width:35%">Description</th>
        <th style="width:28%">Proposed Comms</th>
        <th style="width:14%">Status</th>
      </tr>
    </thead>
    <tbody><!-- one row per platform-wide minor task, tag-platform pill --></tbody>
  </table>
</div>
```

### Minor Releases — Client-Specific

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading-sm">Minor Releases — Client-Specific</div>
  <table class="tier-table tier-table-cozy tight">
    <thead>
      <tr>
        <th style="width:22%">Feature / User Story</th>
        <th style="width:33%">Description</th>
        <th style="width:31%">Proposed Comms</th>
        <th style="width:14%">Status</th>
      </tr>
    </thead>
    <tbody><!-- one row per client-specific minor task, Platform/Data Product pill + client tag pill(s) --></tbody>
  </table>
</div>
```

### Patch & Hotfix Releases

```html
<div class="slide">
  <div class="slide-logo-wrap">...</div>
  <div class="slide-section-label">{SPRINT_LABEL}</div>
  <div class="slide-heading">Patch &amp; Hotfix Releases</div>
  <table class="tier-table tier-table-sm">
    <thead>
      <tr>
        <th style="width:25%">Feature / User Story</th>
        <th style="width:8%">Type</th>
        <th style="width:33%">Description</th>
        <th style="width:20%">Proposed Comms</th>
        <th style="width:14%">Status</th>
      </tr>
    </thead>
    <tbody><!-- one row per patch/hotfix task; Type = tier-badge badge-patch/badge-hotfix --></tbody>
  </table>
</div>
```

### Tag and badge reference

```html
<span class="client-tag tag-platform">Platform</span>
<span class="client-tag tag-dataproduct">Data Product</span>
<span class="client-tag tag-shoprite">Shoprite</span>
<span class="client-tag tag-transunion">TransUnion</span>
<span class="client-tag tag-fnb">FNB</span>
<span class="client-tag tag-airvantage">Airvantage</span>
<span class="client-tag tag-mtn">MTN</span>
<span class="client-tag tag-sbsa">SBSA</span>
<span class="client-tag tag-nedbank">Nedbank</span>
<span class="client-tag tag-maf">MAF</span>
<span class="client-tag tag-altronhealth">AltronHealthTech</span>

<span class="tier-badge badge-major">Major</span>
<span class="tier-badge badge-minor">Minor</span>
<span class="tier-badge badge-patch">Patch</span>
<span class="tier-badge badge-hotfix">Hotfix</span>
<span class="tier-badge badge-todo">To do</span>
```

### Print CSS

Confirm the extracted `<head>` already contains the `@media print` block (`@page { size: 960px 540px; margin: 0; }` plus `.slide` break rules). If the template lacks it, add it — see `/comms-way-forward-custom` for the exact block.

---

## Step 10 — Write HTML and export PDF

Write to `sprint wrap up and way forward/sprint{N}-comms-wrap-up.html`.

If that file already exists, ask:
```
"sprint wrap up and way forward/sprint{N}-comms-wrap-up.html" already exists. Overwrite? (yes/no)
```
Wait for response; abort if "no".

After writing, run the Edge headless PDF export automatically (no prompt needed), mirroring `/comms-way-forward-custom`:

```
msedge.exe --headless --print-to-pdf="C:/Users/AimeeMalan/OneDrive - omnisient.com/Documents/GitHub/Aimee's Omnisient repo/sprint wrap up and way forward/sprint{N}-comms-wrap-up.pdf" --print-to-pdf-no-header --no-margins --disable-gpu "file:///C:/Users/AimeeMalan/OneDrive%20-%20omnisient.com/Documents/GitHub/Aimee's%20Omnisient%20repo/sprint%20wrap%20up%20and%20way%20forward/sprint{N}-comms-wrap-up.html"
```

Confirm both outputs:

```
HTML saved: sprint wrap up and way forward/sprint{N}-comms-wrap-up.html
PDF saved:  sprint wrap up and way forward/sprint{N}-comms-wrap-up.pdf
{slide count} slides | {action items} action items · {rollover} rolling to Sprint {N+1} · {am actions} AM Actions
· {major} major · {minor} minor · {patch+hotfix} patch/hotfix
```

---

## Error handling

| Condition | Response |
|---|---|
| Missing `--sprint` or `--window` | Show usage, abort |
| No prior deck found to seed action items | Warn, continue by collecting items directly from the user |
| No ClickUp tasks found for window | Ask whether to proceed with session-only slides, or abort |
| No template HTML in `sprint wrap up and way forward/` | Report and abort — CSS must come from an existing deck |
| Output HTML already exists | Ask before overwriting |
| Edge headless PDF command fails | Report the error; HTML is still saved, PDF can be re-run manually |
| ClickUp MCP unavailable | "ClickUp MCP is not connected. Connect it in Claude Code settings and re-run." Abort. |

---

## Key references

- **Release Communications Board list ID:** `901218643488`
- **Olivia Landsberg (Platform):** member ID `87874670`
- **Tristan Venter (Data Product):** member ID `99769856`
- **Release Type values:** Major / Minor / Patch / Hotfix / Standard / Internal
- **Release Window field:** free-text — must match ClickUp exactly
- **Template/CSS source:** most recently modified file in `sprint wrap up and way forward/*.html`
- **Prior-session source:** `sprint wrap up and way forward/sprint{N-1}-comms-wrap-up.html`, falling back to `product-release-comms-way-forward-sprint-{N-1}.html`
- **Output location:** `sprint wrap up and way forward/sprint{N}-comms-wrap-up.html` and `.pdf`
- **Sibling skill:** `/comms-way-forward-custom` generates the forward-looking planning deck this one wraps up; they share the board, CSS system, and tag/badge conventions

**Note:** Prefer `claude_ai_ClickUp` tools if both ClickUp MCP integrations are connected (`clickup-mcp` lacks `clickup_filter_tasks`); fall back to whichever is available if tool names differ slightly.
