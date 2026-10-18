---
name: dashboard-bugs-custom
description: Build or update the monthly Bug Dashboard report set (a scrollable dashboard HTML and a 3-slide presentation-ready HTML deck) tracking Technical Issue / Bug tickets across all clients. Adapted from the ShopriteX Support Report skill — same stat conventions, layout fixes, and verification discipline, retargeted from one client's full ticket mix to bugs only, across every client.
---

# Bug Dashboard

Build or update the monthly **Bug Dashboard** report set in `BugsDashboard/`: a scrollable dashboard HTML and a 3-slide presentation-ready HTML deck. Unlike the ShopriteX Support Report (one client, every ticket type), this dashboard tracks **Technical Issue / Bug tickets only, across every client** — it's the cross-client bug-health view. This skill is protected from Dex updates; edit `.claude/skills/dashboard-bugs-custom/SKILL.md` directly to change it.

## Usage

```
/dashboard-bugs-custom [--month <Month YYYY>] [--update <what changed>]
```

- `--month "September 2026"` — reporting period. Drives filenames (`Bugs_Dashboard_<Month><YYYY>.html`, etc.) and the "Reporting period" tag. If omitted, ask the user.
- `--update "<description>"` — if this is an incremental edit to an *existing* month's report (new bug, corrected severity, removed ticket, client reassignment, etc.) rather than a fresh month, describe the change here. Skip straight to **Path B** below.
- If neither is given, ask the user whether this is a **new month** (Path A) or an **update to an existing report** (Path B).

---

## The two artifacts

Both live in `BugsDashboard/`:

| File | Purpose |
|---|---|
| `Bugs_Dashboard_<Month><YYYY>.html` | The canonical, scrollable dashboard. Source of truth for all styling and copy. |
| `Bugs_Dashboard_<Month><YYYY>_Slides.html` | A 3-slide, fixed-16:9-canvas HTML deck derived from the dashboard: 1 executive summary + 2 appendix (ticket detail) slides. Standalone file, own `<style>` block (tuned smaller/denser than the dashboard's). |

A PPTX mirror isn't part of this skill by default — the two HTML artifacts cover the same content with far less risk. If a PPTX is explicitly requested later, mirror the ShopriteX Support Report skill's PPTX build process and pitfalls (integer EMU coordinates, `spcPct` thousandths-of-a-percent, strict-parser verification) rather than improvising a new approach.

Treat the dashboard HTML as the **template of record**. When starting a new month, copy the previous month's dashboard file forward and edit in place rather than re-deriving the CSS from this doc — that guarantees styling never drifts between the two artifacts.

---

## Path A — New month

1. **Copy forward.** Duplicate the most recent month's dashboard HTML and deck HTML under the new month's filenames. Update the `<title>`, `<h1>`, and "Reporting period" tag in both.
2. **Gather raw ticket data** — see *Ticket sourcing discipline* below. Do not invent or estimate ticket facts.
3. **Populate stats** — see *Stat conventions* below for every KPI formula.
4. Work through **Build order** below.
5. Run the **Verification checklist** before reporting done.

## Path B — Update an existing month

1. Identify exactly what changed (new bug, corrected field, removed ticket, client reassignment, re-ordered row, restyled section, etc.).
2. Make the edit in the **dashboard HTML first** — it's the source of truth.
3. Propagate the same data change to the **slides HTML**.
4. Recompute every downstream aggregate the change touches (see *Stat conventions* — nothing is independent; a single ticket edit can ripple through 6–8 numbers).
5. Run the **Verification checklist**.

---

## Ticket sourcing discipline

This is the single most important rule from the ShopriteX Support Report skill this dashboard is adapted from: **never guess a ticket's facts.**

- Every ticket's created/resolved timestamps, root cause, resolution, severity, and **client** must come from the actual Intercom conversation or ClickUp task — fetched live, not inferred from a title.
- Only include tickets whose ticket type is genuinely **Technical Issue / Bug**. If a ticket looks bug-adjacent but is really a Platform Support Query or Data Science Query, leave it out of this dashboard — it belongs in that client's own support report, not here.
- If the user gives a URL and it turns out to point to the wrong conversation, say so and find the right one via `mcp__claude_ai_Intercom__search` (search on distinctive phrases from the ticket description) rather than silently proceeding with the wrong source.
- If a user-provided fact (a date, a severity, a client) conflicts with what you find in the actual system, ask or flag it rather than quietly overwriting.
- Track each ticket's true origin system (Intercom vs ClickUp) and true client — don't assume; get both from the record, not the requester's framing.
- Two tickets that look similar (same title pattern, same requester) may be genuinely different tickets on different dates, or for different clients — check the timestamps and client before merging or assuming duplication.
- If a "new" ticket turns out to be the same underlying conversation as one already in the table (discovered via matching dates/content), merge them into one row rather than leaving a duplicate.

---

## Bug taxonomy

Because every tracked ticket here is a bug by definition, the dimension that varies is **which client it belongs to**, not ticket type. Adjust the taxonomy accordingly:

- **Client** (own chip color per client, used consistently across every chart and the detail table): assign each client a distinct color the first time it appears in a report, then reuse that exact color in every subsequent month — don't let a client's chip color drift between editions. Keep a running color-assignment note (e.g. a comment block at the top of the dashboard HTML) so future months stay consistent.
- **Severity**: Sev 1 (critical) → Sev 4 (low), plus `N/A` (`--unknown` grey) for tickets where severity genuinely doesn't apply (e.g. external-dependency investigations, not faults on Omnisient's side).
- **Status**: `Closed` (green pill) or `In progress` (amber pill) — no other states in the detail table.
- **Bucket** (drives the header tag and several KPIs — every tracked ticket falls into exactly one):
  - **New this month** — created within the reporting month.
  - **Carried over** — created before the reporting month, still open *or* closed within it. (A bug created last month and closed this month is still "carried over," not "new.")

There is no "Service request" bucket in this dashboard — a service request (access grant, data provisioning) is by definition not a bug, so it's simply out of scope here rather than tracked-and-excluded. If something you're about to add isn't actually a fault, it doesn't belong in this dashboard at all.

---

## Stat conventions (exact formulas)

These numbers are cross-checked against each other in the dashboard — get one wrong and it becomes visible as an inconsistency between the KPI tiles and the side detail. Recompute **all** of these after any ticket-level edit:

- **Total Tickets** = new this month + carried over.
- **Tickets Created This Month** = count of "new this month" bucket.
- **Tickets Carried Over** = count of "carried over" bucket (open *or* closed).
- **Open Tickets** = count with Status = In progress, "of N tracked this period" where N = Total Tickets.
- **Closed Tickets** = Total Tickets − Open Tickets, "of N tracked this period."
- **Clients Affected** = count of distinct clients represented in the tracked ticket set this period — a dashboard-specific KPI this skill adds beyond the ShopriteX original, since cross-client spread is the point of this view.
- **Average Time to Resolve** = mean of **business-hours** duration (see formula below) across closed tickets that have **both** a real created and resolved timestamp — **excluding**:
  - tickets whose long duration reflects an external dependency, not Omnisient's own resolution effort (tag the row `(external dependency)` and asterisk its business-days figure in the detail table);
  - tickets whose duration was driven by a late-stage scope change rather than delay in fixing the fault;
  - tickets whose only "resolution" timestamp is an unreliable bulk/automated close (e.g. a sprint-close date in ClickUp that doesn't reflect the real fix date — always confirm the real resolution date with the requester/assignee instead).
  - State the excluded ticket(s) and the sample size (`n = X closed tickets`) in the KPI's note line so the number is auditable at a glance.
- **Total Sev 1-3** / **Total Sev 4-5** = counts by severity band across all tracked tickets with a known severity; note any excluded/N/A ticket explicitly (e.g. "1 ticket N/A — external dependency").
- **Business-hours / business-days formula**: iterate each calendar day from created to resolved; for weekdays only, intersect with the 09:00–17:00 SAST window and sum the overlap in hours; business days = business hours ÷ 8. (SAST = UTC+2 — convert Intercom/ClickUp epoch timestamps accordingly.) Do this in a short Python snippet per ticket rather than approximating by eye.
- **Outside SLA** flags: compare each closed ticket's business-days figure (or, for still-open tickets, days-since-created) against the SLA Resolution Windows target for its severity. List every breach in the "Tickets outside of SLA" panel — this is a dedicated panel, not an inline table annotation.

**SLA Resolution Windows** (fixed reference table, does not change month to month unless the business changes its targets):

| Severity | Target | Description |
|---|---|---|
| Sev 1 | 8 hours | Critical — immediate business impact |
| Sev 2 | 24 hours | High — significant impact, workaround available |
| Sev 3 | 3 business days | Medium — moderate impact |
| Sev 4 | 5 business days | Low — minor impact or cosmetic |

---

## Build order

1. **Dashboard HTML** — update in this order top to bottom: header (title + reporting period), Bug Stats (grouped KPI tiles, 3-column grid), the four chart panels (New bugs by client / Bugs by severity level / New bugs by week & client / Bugs outside of SLA), SLA Resolution Windows table, full ticket detail table, footer note.
2. **Charts as plain divs, not `<canvas>` or a charting library** — reuse this repo's `.chart` / `.col` / `.bar-stack` / `.seg` div pattern with inline `height` (px on the dashboard, `%` on the deck) driving bar height, so there's no JS dependency and the file stays a single static HTML document.
3. **Weekly bucketing for "New bugs by week & client"**: bucket every tracked ticket (not just "new this month" ones — carried-over tickets bucket into the week they were actually created, even if that's the prior month) by the Monday-starting week of its creation date. Verify the totals reconcile against the by-client chart's totals (same tickets, different grouping) before finalizing bar heights.
4. **Slides HTML** — build/update *after* the dashboard is finalized, copying its data 1:1. Key differences from the dashboard, all deliberate:
   - Fixed `1280×720` `.slide` canvases (16:9), `page-break-after:always` for clean print/PDF export, a small `N / 3 · Executive Summary`-style corner label per slide.
   - Bug Stats uses a **4-column** grid (2 rows for 8 tiles) rather than the dashboard's 3-column layout — the deck is much more vertically constrained than a scrolling page.
   - Global `html{font-size:14px}` (vs. the dashboard's 16px default) as a blanket compaction lever, on top of per-component size reductions.
   - Ticket detail table split across the two appendix slides (5 rows each), columns: Ticket / What happened / Client / Created / Resolved / TTR (bd) / Sev / Status.
   - SLA Resolution Windows table goes on the **second** appendix slide, under its ticket rows — not on the executive summary slide, and not duplicated onto both appendix slides.

---

## HTML layout pitfalls (hard-won in the ShopriteX Support Report skill — apply here too)

- **Table rows bunching at the top with dead space below**: when a table sits inside a flexible-height wrapper (`.table-wrap{flex:1}`), rows do **not** stretch to fill it by default — they take natural content height and leave the remainder empty. Fix: `table{height:100%}` + `tbody tr{height:1%}` (a standard CSS trick that makes rows distribute the container's full height evenly). Apply this to any table you place inside a flexible container.
- **Content overflowing a rounded panel's corners**: any `.panel`/`.sla-panel` that can possibly get more content than its allotted height needs `overflow:hidden` as a safety net, otherwise a table or text block's sharp rectangular corner visibly pokes past the panel's `border-radius`. Add this defensively to every card-style container in the deck, not just the ones you've seen overflow.
- **Long unbroken strings (ticket IDs, or a long client name concatenated with a ticket slug) overflow into the next table column** with `table-layout:fixed` unless you set `overflow-wrap:break-word; word-break:break-word` on `td`.
- **Fixed-height slide canvases are unforgiving** — after any font-size or padding change, re-render and visually check for clipping; don't assume a change is "small enough" not to matter. A KPI note growing by one line, or a client-chip legend wrapping to a second row as more clients get added over time, can push content past the 720px boundary with no visible warning except the render itself. This dashboard is especially exposed to this failure mode because the number of distinct clients (and thus chip-legend width) can grow month to month in a way a single-client report never has to handle — budget extra legend space or plan a wrap strategy up front.
- **Rebalance, don't just shrink, when two grid siblings need different amounts of space.** Two `.charts-row` panels sharing one CSS grid row get equal height by default even if one genuinely needs more (e.g. a growing client legend vs. a short bar chart) — use a `flex` ratio override on the row (e.g. `flex:1.15`) rather than cramming the needier panel's internal spacing down to nothing.

---

## Verifying the HTML artifacts (do this before reporting done)

Headless Chromium/Edge screenshots are the only reliable way to catch layout bugs in this project — do not declare a layout change done from reading the CSS alone.

**macOS:**

```bash
HTML="<absolute path to the .html file>"
OUT="<absolute path to a temp .png>"
EDGE="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
PROFILE="/tmp/edge_shot_profile_$RANDOM"
pkill -f "Microsoft Edge" 2>/dev/null
sleep 1
"$EDGE" --headless=new --disable-gpu --no-sandbox --user-data-dir="$PROFILE" --window-size=1360,2400 --screenshot="$OUT" "file://$HTML"
```

If Edge isn't installed, swap in Chrome (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`) with the same flags.

Notes learned the hard way (from the ShopriteX Support Report skill this one is adapted from):
- **Always kill any running `msedge` process first** and use a **fresh `--user-data-dir` every run** (a random suffix is simplest) — reusing a profile or leaving a prior instance running causes a `"Multiple targets are not supported in headless mode"` failure with no screenshot produced, silently.
- `--window-size` sets the *capture* viewport — make it tall enough to capture every slide in one shot for a full-page review (e.g. `1360,2400` for a 3-slide deck), or crop a specific region with PIL afterward for a close-up check of one area.
- The task-manager `ERROR: fallback_task_provider` lines in stderr are noise from this Edge build — ignore them; check whether the output file exists for actual success.
- Delete the screenshot file from the repo directory once you've reviewed it (via the Read tool) — it's a temp artifact, not a deliverable.
- If a screenshot shows unexpected overflow/clipping that you can't explain from the CSS, consider that the user's own browser may not have the Google Fonts `<link>` load (no network, ad blocker, etc.), causing a fallback font with different line-height metrics — build a little extra vertical margin into fixed-height layouts rather than tuning to a pixel-exact fit against one specific font.

---

## Verification checklist

Before reporting the task done:

- [ ] Every number in the Bug Stats KPI tiles reconciles: Total = new this month + carried over; Open + Closed = Total; Sev band counts + "N/A"/unknown count = Total.
- [ ] Every chart's totals (by client, by severity, by week) sum to the same Total Tickets figure (or the explicitly-narrower subset the chart is scoped to — e.g. "new this month" charts summing to the new-this-month count, not the grand total).
- [ ] Every ticket's facts (dates, severity, client, description) were pulled from a live Intercom/ClickUp lookup this session or a prior one already confirmed — not guessed.
- [ ] Every included ticket is genuinely a Technical Issue / Bug — nothing from another ticket type slipped in.
- [ ] Client chip colors match the running color-assignment note from prior months — no client's color silently changed.
- [ ] Dashboard HTML and Slides HTML agree on every ticket's data (title, dates, severity, client, status) — a discrepancy here is the most common regression when only one file gets updated.
- [ ] Both HTML files rendered via headless screenshot and visually checked for overflow/clipping after any layout-affecting change.
- [ ] All temporary render/diagnostic files were deleted from the repo directory.
