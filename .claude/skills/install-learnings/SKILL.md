---
name: install-learnings
description: "Turn unused session learnings into changes that affect the next session — or honestly drop them with a reason. Use when the user says 'install the learnings', 'apply pending learnings', 'the learnings never get used', 'session learnings are piling up', or when a session-end notice reports the unused pile crossed the install threshold. Also use proactively when `/dex-whats-new` finds pending learnings the user wants applied. Not for capturing a new learning from today's work; use `daily-review`. Not for ranking product ideas; use `dex-backlog`."
---

# /install-learnings

Pending session learnings are an archive until they change a file the next session will follow. This skill is the **apply** half. Capture stays in `/daily-review`. Do not extract new learnings here.

Governing rule: **route into the place that changes behaviour, then record where it went.** Prefer one rule covering a cluster over eight tiny edits. Never fabricate an edit to make the count drop. Never delete an entry to hide it.

Read the routing table before touching files: [session-learnings-routing.md](../../reference/session-learnings-routing.md).

---

## Step 1 — Load pending entries (don't capture)

Read `System/Session_Learnings/*.md`. Skip `README.md` and session-end markers that have no `**Status:**` line. Collect every block whose status is exactly `pending`.

If the folder is missing or there are no pending entries, say so plainly and stop. Do not invent entries.

## Step 2 — Cluster, then choose a destination

Group pending entries by the file that would change next-session behaviour, using the routing table:

| Kind | Destination |
|---|---|
| How the assistant should work | `CLAUDE.md` user-extensions block, and/or a standing memory note |
| A defect in a skill | That skill's `SKILL.md` as a **numbered step**, not prose |
| Small safe code/config defect | Fix it; otherwise `capture_idea` and point the status at the idea id |
| Environment/platform fact | Matching `.claude/reference/` file |

Take **1–4 clusters** this pass unless the user asked to clear the pile. Leave the rest pending.

## Step 3 — Install or drop (no silent deletes)

For each chosen cluster:

- **Install:** make the real file change, then read that file back. Only then rewrite each covered entry's status to `implemented (YYYY-MM-DD — where)`.
- **Drop:** if the note is wrong, obsolete, or already covered, rewrite status to `dropped (YYYY-MM-DD — reason)`. Leave the entry in the file.
- **Skip:** if the right destination is unclear, leave it `pending`.

Do not mark `implemented` unless the destination file now contains the rule. Do not replace `pending` with anything other than `implemented (…)` or `dropped (…)`.

## Step 4 — Inspect, then report

Read back every file that changed, including the learning files whose status lines moved. Report:

- how many entries were pending at the start
- which clusters were installed, and where
- which were dropped, and why
- how many remain pending

Never say "installed / done" without those destinations in hand.

---

## Quality bar

A good run changes next-session behaviour for the clusters it took, records where each routed entry went, and leaves unrelated pending entries untouched. The count falls because something was installed or honestly dropped.

## Anti-patterns (do not do these)

- **Capturing new learnings** during this pass — that is `/daily-review`.
- **Fabricating an edit** so the pending count drops.
- **Deleting** an obsolete entry instead of marking `dropped`.
- **Prose in a skill** where a numbered step is required.
- **Claiming implemented** without reading the destination file back.
- Dumping personal names or vault anecdotes into the report; summarise the rule, not the original story.

## Degradation

- `System/Session_Learnings/` missing → say the folder is not there yet; stop.
- Destination file missing (no `CLAUDE.md`, no matching skill) → leave those entries pending and say why; do not invent a destination.
- A write fails or the read-back does not contain the rule → do not mark implemented; report that cluster as not installed.

---

## Track Usage (Silent)

Update `System/usage_log.md` to mark learnings installed as used.

**Analytics (Silent):** call `track_event` with event_name `learnings_installed` and properties `implemented_count`, `dropped_count` (counts only — no titles, no file contents). Fires only if the user opted into analytics; no action if it returns `analytics_disabled`.
