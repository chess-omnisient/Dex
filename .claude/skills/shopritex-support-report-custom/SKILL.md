---
name: shopritex-support-report-custom
description: Build or update the monthly ShopriteX Support Metrics report set (a scrollable dashboard HTML, a 3-slide presentation-ready HTML deck, and an optional synced PPTX appendix). Encodes hard-won fixes for ticket sourcing, stat conventions, and layout bugs from past editions.
---

# ShopriteX Support Report

Build or update the monthly **ShopriteX Support Metrics** report set in `SHX_operationalmeet/`: a scrollable dashboard HTML, a 3-slide presentation-ready HTML deck, and (optionally) a synced PPTX appendix. This skill encodes everything learned building the July 2026 edition, including several hard-won fixes for bugs that are easy to reintroduce.

## Usage

```
/shopritex-support-report-custom [--month <Month YYYY>] [--update <what changed>]
```

- `--month "July 2026"` — reporting period. Drives filenames (`ShopriteX_Support_<Month><YYYY>.html`, etc.) and the "Reporting period" tag. If omitted, ask the user.
- `--update "<description>"` — if this is an incremental edit to an *existing* month's report (new ticket, corrected severity, removed internal ticket, etc.) rather than a fresh month, describe the change here. Skip straight to **Path B** below.
- If neither is given, ask the user whether this is a **new month** (Path A) or an **update to an existing report** (Path B).

---

## The three artifacts

All live in `SHX_operationalmeet/`:

| File | Purpose |
|---|---|
| `ShopriteX_Support_<Month><YYYY>.html` | The canonical, scrollable dashboard. Source of truth for all styling and copy. |
| `ShopriteX_Support_<Month><YYYY>_Slides.html` | A 3-slide, fixed-16:9-canvas HTML deck derived from the dashboard: 1 executive summary + 2 appendix (ticket detail) slides. Standalone file, own `<style>` block (tuned smaller/denser than the dashboard's). |
| `ShopriteX_Support_<Month><YYYY>.pptx` | Optional native PowerPoint mirror of the deck. Only build/update this if explicitly asked — see **PPTX pitfalls** below before touching it. |

Treat the dashboard HTML as the **template of record**. When starting a new month, copy the previous month's dashboard file forward and edit in place rather than re-deriving the CSS from this doc — that guarantees styling never drifts between the two artifacts.

---

## Path A — New month

1. **Copy forward.** Duplicate the most recent month's dashboard HTML, deck HTML, and (if in use) PPTX under the new month's filenames. Update the `<title>`, `<h1>`, and "Reporting period" tag in all three.
2. **Gather raw ticket data** — see *Ticket sourcing discipline* below. Do not invent or estimate ticket facts.
3. **Populate stats** — see *Stat conventions* below for every KPI formula.
4. Work through **Build order** below.
5. Run the **Verification checklist** before reporting done.

## Path B — Update an existing month

1. Identify exactly what changed (new ticket, corrected field, removed ticket, re-ordered row, restyled section, etc.).
2. Make the edit in the **dashboard HTML first** — it's the source of truth.
3. Propagate the same data change to the **slides HTML** and, if it exists and is in use, the **PPTX**.
4. Recompute every downstream aggregate the change touches (see *Stat conventions* — nothing is independent; a single ticket edit can ripple through 6–8 numbers).
5. Run the **Verification checklist**.

---

## Ticket sourcing discipline

This is the single most important rule from building past editions: **never guess a ticket's facts.**

- Every ticket's created/resolved timestamps, root cause, resolution, severity, and ticket type must come from the actual Intercom conversation or ClickUp task — fetched live, not inferred from a title.
- If the user gives a URL and it turns out to point to the wrong conversation, say so and find the right one via `mcp__claude_ai_Intercom__search` (search on distinctive phrases from the ticket description) rather than silently proceeding with the wrong source.
- If a user-provided fact (a date, a severity) conflicts with what you find in the actual system, ask or flag it rather than quietly overwriting.
- Track each ticket's true origin system (Intercom vs ClickUp) — don't assume; the source column/attribution has been wrong from assumption more than once in past editions.
- Two tickets that look similar (same title pattern, same requester) may be genuinely different tickets on different dates — check the timestamps before merging or assuming duplication.
- If a "new" ticket turns out to be the same underlying conversation as one already in the table (discovered via matching dates/content), merge them into one row rather than leaving a duplicate — this has happened before when a ticket was re-described from a second source.

---

## Ticket taxonomy

- **Ticket Type** (own chip color, used consistently across every chart and the detail table):
  - Technical Issue / Bug — `--chip-bug`
  - Platform Support Query — `--chip-plat`
  - Data Science Query — `--chip-dsq`
- **Severity**: Sev 1 (critical) → Sev 4 (low), plus `N/A` (`--unknown` grey) for tickets where severity genuinely doesn't apply (e.g. external-dependency investigations, not faults on Omnisient's side).
- **Status**: `Closed` (green pill) or `In progress` (amber pill) — no other states in the detail table.
- **Bucket** (drives the header tag and several KPIs — every tracked ticket falls into exactly one):
  - **New this month** — created within the reporting month.
  - **Carried over** — created before the reporting month, still open *or* closed within it. (A ticket created last month and closed this month is still "carried over," not "new.")
  - **Service request** — a data-access / provisioning request rather than an incident (e.g. granting a partner audience access). Tracked in the total but excluded from incident-style KPIs (Sev counts, Time to Resolve). Only use this bucket for genuine non-incident asks — when in doubt, ask the user rather than reclassifying an incident as a service request to make the numbers tidier.

---

## Stat conventions (exact formulas)

These numbers are cross-checked against each other in the dashboard — get one wrong and it becomes visible as an inconsistency between the KPI tiles and the side detail. Recompute **all** of these after any ticket-level edit:

- **Total Tickets** = new this month + carried over + service requests.
- **Tickets Created This Month** = count of "new this month" bucket.
- **Tickets Carried Over** = count of "carried over" bucket (open *or* closed).
- **Open Tickets** = count with Status = In progress, "of N tracked this period" where N = Total Tickets.
- **Closed Tickets** = Total Tickets − Open Tickets, "of N tracked this period."
- **Average Time to Resolve** = mean of **business-hours** duration (see formula below) across closed tickets that have **both** a real created and resolved timestamp — **excluding**:
  - tickets whose long duration reflects an external dependency, not Omnisient's own resolution effort (tag the row `(external dependency)` and asterisk its business-days figure in the detail table);
  - tickets whose duration was driven by a late-stage scope change rather than delay in fixing a fault;
  - tickets whose only "resolution" timestamp is an unreliable bulk/automated close (e.g. a sprint-close date in ClickUp that doesn't reflect the real fix date — always confirm the real resolution date with the requester/assignee instead);
  - pure service requests (access grants, data provisioning) — these aren't "faults" to resolve.
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

1. **Dashboard HTML** — update in this order top to bottom: header (title + reporting period), User Stats, Dataset Stats, Ticket Stats (grouped KPI tiles, 3-column grid), the four chart panels (New tickets by type / Tickets by severity level / New tickets by week & type / Tickets outside of SLA), SLA Resolution Windows table, full ticket detail table, footer note.
2. **Charts as plain divs, not `<canvas>` or a charting library** — this repo's convention is `.chart` / `.col` / `.bar-stack` / `.seg` divs with inline `height` (px on the dashboard, `%` on the deck) driving bar height, so there's no JS dependency and the file stays a single static HTML document. Reuse this pattern for every new bar chart; don't introduce a new charting approach.
3. **Weekly bucketing for "New tickets by week & type"**: bucket every tracked ticket (not just "new this month" ones — carried-over tickets bucket into the week they were actually created, even if that's the prior month) by the Monday-starting week of its creation date. Verify the totals reconcile against the Ticket Type chart's totals (same tickets, different grouping) before finalizing bar heights.
4. **Slides HTML** — build/update *after* the dashboard is finalized, copying its data 1:1. Key differences from the dashboard, all deliberate:
   - Fixed `1280×720` `.slide` canvases (16:9), `page-break-after:always` for clean print/PDF export, a small `N / 3 · Executive Summary`-style corner label per slide.
   - User Stats + Dataset Stats sit **side by side** in one row (not stacked) to save vertical space; Ticket Stats uses a **4-column** grid (2 rows for 8 tiles) rather than the dashboard's 3-column layout — the deck is much more vertically constrained than a scrolling page, and both changes are needed to fit all four chart panels on the executive summary slide.
   - Global `html{font-size:14px}` (vs. the dashboard's 16px default) as a blanket compaction lever, on top of per-component size reductions.
   - Ticket detail table split across the two appendix slides (5 rows each), same 8 columns as the dashboard (Ticket / What happened / Ticket Type / Created / Resolved / TTR (bd) / Sev / Status).
   - SLA Resolution Windows table goes on the **second** appendix slide, under its ticket rows — not on the executive summary slide, and not duplicated onto both appendix slides.
5. **PPTX** (only if requested) — see pitfalls below before starting; budget significantly more time than the HTML artifacts.

---

## HTML layout pitfalls (hard-won, do not relearn these)

- **Table rows bunching at the top with dead space below**: when a table sits inside a flexible-height wrapper (`.table-wrap{flex:1}`), rows do **not** stretch to fill it by default — they take natural content height and leave the remainder empty. Fix: `table{height:100%}` + `tbody tr{height:1%}` (a standard CSS trick that makes rows distribute the container's full height evenly). Apply this to any table you place inside a flexible container.
- **Content overflowing a rounded panel's corners**: any `.panel`/`.sla-panel` that can possibly get more content than its allotted height needs `overflow:hidden` as a safety net, otherwise a table or text block's sharp rectangular corner visibly pokes past the panel's `border-radius`. Add this defensively to every card-style container in the deck, not just the ones you've seen overflow.
- **Long unbroken strings (ticket IDs like `DGMTRedemptionDec20257Jul2026`) overflow into the next table column** with `table-layout:fixed` unless you set `overflow-wrap:break-word; word-break:break-word` on `td`.
- **Fixed-height slide canvases are unforgiving** — after any font-size or padding change, re-render and visually check for clipping; don't assume a change is "small enough" not to matter. The deck's vertical budget is tight by design (see Build order §4), so a KPI note growing by one line or a chart's legend wrapping to a second row can push content past the 720px boundary with no visible warning except the render itself.
- **Rebalance, don't just shrink, when two grid siblings need different amounts of space.** Two `.charts-row` panels sharing one CSS grid row get equal height by default even if one genuinely needs more (e.g. a 3-row status list vs. a short bar chart) — use a `flex` ratio override on the row (e.g. `flex:1.15`) rather than cramming the needier panel's internal spacing down to nothing.

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

**Windows** (original authoring environment — kept for reference if this skill runs there):

```powershell
$html = "<absolute path to the .html file>"
$out  = "<absolute path to a temp .png>"
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
$args = "--headless=new --disable-gpu --no-sandbox --user-data-dir=`"$env:TEMP\edge_shot_profile_$(Get-Random)`" --window-size=1360,2400 --screenshot=`"$out`" `"$html`""
Start-Process -FilePath $edge -ArgumentList $args -Wait -NoNewWindow
```

Notes learned the hard way:
- **Always kill any running `msedge` process first** and use a **fresh `--user-data-dir` every run** (a random suffix is simplest) — reusing a profile or leaving a prior instance running causes a `"Multiple targets are not supported in headless mode"` failure with no screenshot produced, silently.
- `--window-size` sets the *capture* viewport — make it tall enough to capture every slide in one shot for a full-page review (e.g. `1360,2400` for a 3-slide deck), or crop a specific region with PIL afterward for a close-up check of one area.
- The task-manager `ERROR: fallback_task_provider` lines in stderr are noise from this Edge build — ignore them; check `Test-Path $out` for actual success.
- Delete the screenshot file from the repo directory once you've reviewed it (via the Read tool) — it's a temp artifact, not a deliverable.
- If a screenshot shows unexpected overflow/clipping that you can't explain from the CSS, consider that the user's own browser may not have the Google Fonts `<link>` load (no network, ad blocker, etc.), causing a fallback font with different line-height metrics — build a little extra vertical margin into fixed-height layouts rather than tuning to a pixel-exact fit against one specific font.

---

## PPTX pitfalls (read before touching the PPTX)

Building/editing the PPTX by splicing its XML parts directly (via Python `zipfile`) is the only practical approach for targeted edits, but PowerPoint's XML parser is **much stricter** than `python-pptx`'s reader — `python-pptx` will happily open a file that real PowerPoint rejects outright with an opaque `E_FAIL` COM error. Two specific bugs caused hours of debugging in past editions:

1. **Every EMU coordinate (`<a:off>`, `<a:ext>`) must be a plain integer.** Python division (`width / 3`) produces a float; embedding that directly into the XML (e.g. `cx="2721138.666..."`) parses fine as XML but fails PowerPoint's stricter type validation for the whole *file*, not just that shape — and the failure mode is a generic "can't open this file," not a helpful error pointing at the bad shape. **Wrap every coordinate in `int(round(x))` before formatting it into XML**, with no exceptions.
2. **`<a:spcPct val="...">` (paragraph line-spacing) is in *thousandths of a percent*, not percent.** `val="105"` means 0.105% (paragraphs collapse to near-zero height, rendering as visually overlapping text) — you want `val="105000"` for 105%. Same thousandths convention applies anywhere else `ST_TextSpacingPercentOrPercentString` is used.

**Verification protocol** (do all of this before saying the PPTX is done — `python-pptx` opening it successfully proves nothing):
1. After building, grep the generated XML for every `<a:off>`/`<a:ext>` pair and assert `cx > 0`, `cy > 0`, `x >= 0`, `y >= 0`, and integer-valued.
2. Actually open the file with a real, strict OOXML parser — `python-pptx` is too lenient to trust:
   - **macOS with PowerPoint installed:** drive it via AppleScript, which is scriptable on Mac just like COM on Windows:
     ```bash
     osascript -e '
     tell application "Microsoft PowerPoint"
       try
         open POSIX file "<absolute path>"
         set slideCount to count of slides of active presentation
         close active presentation saving no
         return "opened ok, slides: " & slideCount
       on error errMsg
         return "ERROR: " & errMsg
       end try
     end tell'
     ```
   - **macOS without PowerPoint:** fall back to LibreOffice headless, which parses OOXML strictly enough to catch the same float-EMU and `spcPct` bugs:
     ```bash
     soffice --headless --convert-to pdf --outdir /tmp "<absolute path to .pptx>"
     ```
     A conversion failure or garbled output is the equivalent signal to a COM `E_FAIL`.
   - **Windows** (original authoring environment):
     ```powershell
     $ppt = New-Object -ComObject PowerPoint.Application
     try {
       $pres = $ppt.Presentations.Open("<absolute path>")
       Write-Output "opened ok, slides: $($pres.Slides.Count)"
       $pres.Close()
     } catch { Write-Output "ERROR: $($_.Exception.Message)" }
     finally { $ppt.Quit() }
     ```
3. If it fails, **bisect** — rebuild a minimal version of just the new/changed slide content against a known-good prior commit of the file (`git show <sha>:<path> > temp.pptx`) and add sections back one at a time until it breaks, rather than guessing at the cause. This is how both bugs above were actually found.
4. Once it opens, export each slide to PNG and visually check it with the Read tool:
   - **macOS with PowerPoint:** AppleScript's `save ... in ... as` only exports the whole deck, not per-slide PNGs cleanly — easiest is exporting all slides as images via `save active presentation in "<folder>" as save as PNG` (creates one PNG per slide in `<folder>`), then reading each.
   - **macOS via LibreOffice:** `soffice --headless --convert-to png --outdir /tmp "<absolute path>"` (converts the first slide only — for all slides, convert to PDF first, then rasterize each page with `pdftoppm` or similar).
   - **Windows:** export via the same COM session (`$pres.Slides.Item(1).Export(path, "PNG", 1600, 900)`).
5. Delete any diagnostic/bisection `.pptx` copies and any temp PNG/PDF exports from the repo directory when done.

If the PPTX isn't explicitly requested, prefer **not** building it — the two HTML artifacts cover the same content with far less risk, and the PPTX is a substantial time investment relative to its marginal value once the HTML deck exists.

---

## Verification checklist

Before reporting the task done:

- [ ] Every number in the Ticket Stats KPI tiles reconciles: Total = new + carried-over + service-requests; Open + Closed = Total; Sev band counts + "N/A"/unknown count = Total.
- [ ] Every chart's totals (by type, by severity, by week) sum to the same Total Tickets figure (or the explicitly-narrower subset the chart is scoped to — e.g. "new this month" charts summing to the new-this-month count, not the grand total).
- [ ] Every ticket's facts (dates, severity, type, description) were pulled from a live Intercom/ClickUp lookup this session or a prior one already confirmed — not guessed.
- [ ] Dashboard HTML and Slides HTML agree on every ticket's data (title, dates, severity, type, status) — a discrepancy here is the most common regression when only one file gets updated.
- [ ] Both HTML files rendered via headless screenshot and visually checked for overflow/clipping after any layout-affecting change.
- [ ] If a PPTX exists and was touched, it passed the strict-open test (PowerPoint/AppleScript, LibreOffice, or COM depending on platform) and was screenshot-verified.
- [ ] All temporary render/diagnostic files were deleted from the repo directory.
