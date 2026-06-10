---
name: diff-list
description: Show all adopted DexDiff workflows — what's installed, when it was adopted, and what it includes
---

## What This Command Does

**In plain English:** Shows you everything you've adopted via `/diff-adopt` — which workflows are installed, when you adopted them, and what skills they added.

**How to run it:**
```
/diff-list
```

---

## Arguments

None.

---

## Process

### Step 1: Read Adoption Logs

Check `.dex/adoptions/` for JSON files. Each file represents one adopted workflow.

If the directory doesn't exist or is empty:
```
No workflows adopted yet.

Browse workflows at heydex.ai/diff, then use:
  /diff-adopt https://heydex.ai/diff/[workflow-name]
```

### Step 2: Display Summary

For each adoption log, show:

```
Adopted workflows:

  meeting-prep
    "Meeting Prep Ritual" by Dave Killeen
    Adopted: 2026-03-28
    Skills: /meeting-prep, /process-meeting
    Source: DexDiff draft area (`DEXDIFF_DIFFS_DIR`, default `04-Projects/DexDiff/beta/diffs/meeting-prep.yaml`)

  deal-review
    "Deal Review Ritual" by Dave Killeen
    Adopted: 2026-03-25
    Skills: /deal-review, /deals-attention
    Source: https://heydex.ai/diff/deal-review

To remove a workflow: /diff-remove [id]
```

### Step 3: Health Check (Optional)

For each adopted workflow, quickly verify:
- Do the installed skill files still exist?
- If any are missing (manually deleted), flag it:

```
  ⚠ meeting-prep — .claude/skills/process-meeting/SKILL.md is missing
    (may have been manually deleted — run /diff-remove meeting-prep to clean up)
```
