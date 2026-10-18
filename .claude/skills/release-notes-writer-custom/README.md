# release-notes-writer (Claude Code skill)

Generates a client-facing release notes article for a given release window by pulling
qualifying items from the Release Communications ClickUp board, applying the team's
release-notes tone and structure, and drafting into a target Intercom article.

## What's in here

| File | What it is |
|---|---|
| `SKILL.md` | The skill itself. Claude Code loads this when you run `/release-notes-writer`. |
| `frameworks/release-notes-tone-and-structure.md` | The tone/structure rule set the skill reads on every run. The skill does not work without it. |

## Install

1. Copy the skill into your repo so it lands at `.claude/skills/release-notes-writer/SKILL.md`:

   ```
   mkdir -p .claude/skills/release-notes-writer
   cp SKILL.md .claude/skills/release-notes-writer/
   ```

   The folder name must be `release-notes-writer` and must sit directly under `.claude/skills/`.
   A skill nested any deeper isn't discovered and won't show up as a slash command.

2. Copy the framework doc to `frameworks/release-notes-tone-and-structure.md` at your repo root:

   ```
   mkdir -p frameworks
   cp frameworks/release-notes-tone-and-structure.md frameworks/
   ```

3. Restart Claude Code and run `/release-notes-writer`.

## What it expects from the surrounding repo

Nothing beyond the two files in this zip. The skill reads its tickets from ClickUp and its tone
reference from published Intercom articles, and its output is the Intercom article itself. It
doesn't read shared context files or write a draft to disk.

One optional reference: `SKILL.md` mentions a companion `help-article-writer` skill (and its
`frameworks/article-tone-and-voice.md`) as the contrast case for individual help articles. Neither
is needed to run this skill.

## Connectors it needs

- **ClickUp**: reads the Release Communications board (list ID `901218643488`).
- **Intercom**: reads past release-note articles for a tone check, and pushes the final draft
  via `update_article` once the PM confirms.

Board IDs, filter rules, and the Intercom-title-is-one-month-later convention are hardcoded in
`SKILL.md` under "What's fixed vs. what to ask for". Change those there if you're running it
against a different board.
