# Product Brief: Dataset Table Status Display

**Area:** Platform
**Author:** Chess | **Date:** 2026-05-22
**Status:** Proposed
**Pipeline stage:** Opportunity Framing
**Related briefs:**
- [Dataset Status Contract](brief-dataset-status-contract-2026-05-21.md) — backend fix: status aggregation + write-path consistency
- [Dataset Status Sync (Sprint 6)](brief-dataset-status-sync-2026-05-18.md) — rehydration write-path bug

---

## Context
- **Strategic fit:** Platform reliability — the datasets list view is the primary surface users consult before consuming data. A low-salience status signal here is where trust is lost, regardless of backend accuracy
- **Related products:** Datasets module, Web App (table list view + dataset detail page)
- **Scope note:** UI-only. Assumes the backend status aggregation fix (Status Contract brief) is in flight. A correct backend signal behind a broken display layer is still a user-facing failure

---

## Problem

**Who has this problem?**
Any user scanning the datasets table to assess readiness before consuming, sharing, or acting on data — the primary use case for the list view.

**What is the problem?**
The datasets table communicates sub-dataset health through a single warning icon. That icon competes with other visual elements in a dense table row, doesn't distinguish between "one failed" and "still processing", and requires the user to notice it and click through before they understand what's wrong. Users anchored on the parent `Ready` label may never register the icon at all — the detail page is accurate, the list is not doing its job.

**Evidence:**

| Source | Signal | Confidence |
|--------|--------|:----------:|
| PM observation | Warning icon exists in table but reported as "easy to miss" — users proceed from the list without clicking through | confirmed |
| JTBD analysis (2026-05-22) | "Failures should demand attention, not wait to be noticed" — opportunity score 12/20 | indicated |
| Status Contract brief (2026-05-21) | Notes "unmissable badge" as desired outcome but doesn't specify list vs. detail distinction | indicated |
| UX heuristics | Icon-only signals underperform in scanned lists — users read text, not icons | assumed |

**Impact of not solving:**
The backend aggregation fix makes the status signal accurate. Without this UI fix, an accurate signal is still communicated through a low-salience icon. Users who miss it proceed with false confidence — identical outcome to today, even after the backend ships.

---

## Why Now

- **Backend fix is in flight** — the Status Contract brief is pending approval. The UI fix must land in the same window, otherwise we ship a correct backend behind a still-broken display layer
- **Low cost** — scoped to a single table cell. No new surfaces, no schema changes. Data already exists in the detail page; this is a surfacing change
- **Trust is formed at the list** — the list view is where users form their first read of dataset health. Fixing it alongside the backend is the only way to fully close the user-facing problem

---

## Solution Direction

**Approach:** Replace the status button-only pattern in the status column with a text-based composite indicator that communicates sub-dataset composition at a glance. `X / Y ready` answers the question users actually bring to the list without requiring a click-through.

**Delivery model:** UI change — datasets table row, status cell only.

**Proposed display logic:**

| Sub-dataset state | What the table shows |
|---|---|
| All children ready | `Ready` (no change) |
| 1+ children processing | `2 / 3 ready ⏳` |
| 1+ children failed | `2 / 3 ready ⚠` |
| Mix of processing + failed | `1 / 3 ready ⚠` |

**What this IS:**
- Sub-dataset count in list view: `X / Y ready`
- Text-led composite status for partial/failed states — icon is secondary, not sole signal
- Link from count to detail page (existing behaviour preserved)

**What this is NOT:**
- A redesign of the datasets table
- A new notifications system
- Changes to the detail page (already accurate)
- Dependent on a specific backend approach — works with rollup status or as an additive display layer

---

## Impact & Effort

| Metric | Current | Target | Confidence |
|--------|---------|--------|:----------:|
| User detects failed/processing upload from list without clicking through | ~0% (icon-only) | High — text count is scannable | M |
| Time to discover a failed upload | Notice icon → click → scan detail page | Visible at list level, no interaction required | M |
| False confidence in `Ready` with partial uploads | High | Eliminated (combined with backend fix) | H |

**Effort:** XS — 1–3 story points. Change scoped to the status cell. Data already available at detail page level — confirm whether the list query needs a child record count join added.
**Confidence in estimate:** High — no schema changes. One engineering spike (half-day) if list query doesn't already join child counts.

---

## The Ask

- [ ] Approve table status cell update: `X / Y ready` composite indicator for partial/failed states
- [ ] Confirm whether the list view query already fetches child upload record counts (spike: half-day if not)
- [ ] Sequence alongside the Status Contract backend fix so both land together

**Decision needed by:** Before the Status Contract fix ships
**Decision maker:** CPO / Engineering Lead

---

## Risks & Open Questions

| Risk | Likelihood | Impact |
|------|:----------:|:------:|
| List view query doesn't join child records — adds backend work to a UI-only brief | M | L |
| `X / Y` count creates confusion if users don't understand what sub-datasets are | L | M |
| Showing `processing` state in the list creates refresh pressure | L | L |

**Open questions:**
- [ ] Does the list view query already fetch child upload record counts, or does it need a new join? Determines whether this is purely frontend
- [ ] Should `processing` children show a count, or only `failed`? (More informative vs. less noisy)
- [ ] Is there a max sub-dataset count where the display needs truncating?
