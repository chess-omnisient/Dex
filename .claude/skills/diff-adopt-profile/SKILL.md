---
name: diff-adopt-profile
description: Adopt a full Heydex profile — fetch the published profile bundle, save the ordered workflows locally, and guide the user through installing the whole set into Dex
---

## What This Command Does

**In plain English:** Pulls down someone's full published Heydex profile, not just one workflow. You get the profile overview, the ordered workflow set, each methodology document, and the optional Love Letter. Then you walk the user through adopting the whole profile into their own Dex setup.

**How to run it:**
```text
/diff-adopt-profile @dave
/diff-adopt-profile https://heydex.ai/diff/@dave/
```

## Arguments

`$ARGUMENTS` must be either:
- a handle like `@dave`
- a public Heydex profile URL like `https://heydex.ai/diff/@dave/`

If missing or invalid:
```text
/diff-adopt-profile expects a Heydex handle or public profile URL.

Examples:
  /diff-adopt-profile @dave
  /diff-adopt-profile https://heydex.ai/diff/@dave/
```

## Hosted Contract

Always fetch the bundle from:

```text
GET https://heydex.ai/api/profile-bundle?handle=<handle>
```

Expected contract:
- `contractVersion: "2026-04-10"`
- `profile`
- `workflows` — ordered list, each with `diffId`, `name`, `description`, `methodology`, `tags`, `roles`, `integrations`
- `loveLetter` — optional

Do **not** use the normal public profile page payload for this command. The whole point is to pull the dedicated runtime bundle.

## Flow

### 1. Resolve and fetch

1. Resolve the handle from the argument.
2. Fetch `/api/profile-bundle`.
3. Parse the JSON.
4. If the bundle is missing, 404s, or has the wrong contract version, stop and explain the failure plainly.

### 2. Introduce the profile

Lead with what makes the profile useful:

```text
[displayName] — [role], [company]

This profile contains [N] published workflows:
  1. [workflow name]
  2. [workflow name]
  ...

[If loveLetter exists]
WHY THIS PROFILE EXISTS
"[loveLetter.text]"

Want to bring this full profile into your Dex setup? [Yes] [Show me the workflows first]
```

If the user wants to inspect first, walk them through the workflows in order before asking again.

### 3. Save the bundle locally before building

Before generating any local skills or hooks, save the raw hosted bundle into the user's DexDiff profile draft area:

- root: `DEXDIFF_PROFILE_DRAFTS_DIR`
- profile folder: `DEXDIFF_PROFILE_DRAFTS_DIR/adopted/<handle>/`
- manifest: `profile-bundle.json`
- workflows: `workflows/01-<diff-id>.yaml`, `02-<diff-id>.yaml`, etc.
- optional Love Letter: `love-letter.md`

Also write an adoption log to:

```text
System/.dex/adoptions/profiles/<handle>.json
```

The log should include:
- `profile_handle`
- `profile_display_name`
- `adopted_at`
- `source`
- `bundle_contract_version`
- `manifest_path`
- `workflow_ids`
- `workflow_paths`
- `love_letter_path`

### 4. Discovery pass across the whole profile

Do one shared discovery pass for the whole profile:
- detect the user's role
- scan folders
- check integrations
- note existing skills that overlap

Then reuse that shared context across every workflow instead of restarting discovery from scratch for each one.

### 5. Preview one combined install plan

Show one combined plan covering:
- the full ordered workflow set
- which local skills would be created or enhanced
- folders/templates/hooks that would be added
- any conflicts that need decisions

Keep the workflow order from the hosted bundle.

### 6. Build after one approval gate

Only build after the user approves the combined plan.

For each workflow:
- use the same adoption principles as `/diff-adopt`
- generate local skills fresh from the methodology
- never install foreign code directly
- never overwrite existing files without explicit confirmation

### 7. Finish with first-use guidance

End by explaining:
- what was installed
- the order the workflows are meant to be used in
- where the saved bundle lives locally
- how to inspect installed workflows with `/diff-list`

## Important Rules

- Treat this as a real runtime command, not future-state.
- Always use the dedicated profile bundle contract.
- Keep single-workflow adoption as `/diff-adopt @handle/diffId`.
- Do not introduce multi-select workflow picking into this command.
- Preserve workflow order from the hosted bundle.
- Save the bundle locally before generating anything else.
- Never overwrite existing files without approval.
