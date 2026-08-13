# Background Processing Guide

Some skills take minutes, not seconds. Background processing lets you keep working while heavy operations run.

Dex capability tiers (see the README): **Tier 2 Skills** cover these journeys on Cursor, Codex, and other Agent Skills harnesses. **Tier 3 Full** (Claude Code) adds in-chat hooks on top. Meeting sync itself is already a scheduled **Tier 1 Core** job — it does not need a harness hook.

## How It Works

### Claude Code CLI
Background agents run in a separate process. The skill acknowledges immediately and processes in the background. You get a notification when done.

### Cursor
Background execution works differently — skills provide progress updates during execution and break large batches into smaller chunks with intermediate output.

## Candidate Skills

| Skill | Why Background | Typical Duration |
|-------|---------------|-----------------|
| `/process-meetings` | Heavy I/O, no interaction needed | 2-5 min for 5+ meetings |
| `/review-article` | 22 parallel subagents | 3-8 min |
| Intel pipelines (YouTube, Newsletter) | External API calls | 1-3 min each |

## Design Pattern

All background-capable skills follow this pattern:

1. **Acknowledge** — Tell the user what's happening and how long to expect
2. **Process** — Do the work silently
3. **Summarize** — Report what was done with key metrics

## When NOT to Use Background

- Interactive skills that need user input mid-flow
- Quick operations (<30 seconds)
- Skills where the user needs to review output immediately

## Implementation Notes

- Skills declare background capability in their prompt
- The harness (Claude Code / Cursor) decides execution model. That difference is packaging (**Tier 2** vs **Tier 3**), not a second skill body.
- Progress can be written to a status file for polling
- Background skills should be idempotent — safe to re-run if interrupted
