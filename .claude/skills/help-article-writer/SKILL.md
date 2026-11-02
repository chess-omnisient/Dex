---
name: help-article-writer
description: "Draft or substantially revise an Intercom help-center article in the team's tone, structure, and information architecture, grounded in the ClickUp user story and existing Intercom articles. Asks a few scoping questions (new or existing, article type, source of truth, audience), then recommends image placements with alt text and filenames. Use when drafting a new help article or restructuring an existing one. Not for release notes; use release-notes-writer."
effort: high
output: "The user's choice: a markdown file saved where they say, or a draft article in Intercom (never published)."
---

# Help Article Writer

Writes Intercom help-center articles grounded in real functionality, in the team's tone, structure,
and information architecture, with image placement suggestions. A hallucinated, off-tone, or badly
scoped article published to customers is expensive, so grounding is a hard gate.

**Not for release notes.** They have their own voice (announcement framing is correct there) and
their own skill, `release-notes-writer`. If the request is a release note or changelog entry, say so
and stop.

## Before You Start

Re-read the frameworks in `references/` each run; don't work from memory or an earlier draft.

- **Always:** `references/article-tone-and-voice.md` (sentence-level voice) and
  `references/article-structure.md` (opening, tables, headings, callouts, grouping).
- **New articles, or when Collection placement or hub/child shape is in question:**
  `references/article-information-architecture.md` (Collections, hub/child decomposition,
  single-sourcing).
- **Only when planning images (Step 4):** `references/image-usage-in-help-articles.md`.

### Sources Of Truth

- **The ClickUp user story.** The original story linked on the Release Comms ticket (or named by the
  user) is the main source for what the feature does. Read its description, acceptance criteria and
  comments with the ClickUp tools.
- **Existing Intercom articles.** Use `search_articles` and `get_article`:
  - **Existing article and neighbors:** search on the feature's terms, then read the matches.
  - **House style:** read 1 or 2 published articles from the same Collection before drafting.
  - **Duplicates and single-sourcing:** search for the topic first. If it's already covered, link to
    that article instead of re-explaining it.
  - **Cross-links:** link only to published articles, using the URL Intercom returns.
- **The user or an SME.** Anything the story and articles don't cover.

If you need product or platform context the ticket and articles don't give (how a screen works,
which roles see it, a value or limit), ask the user to add it. Don't fill the gap from general
knowledge.

This skill never publishes. It saves a markdown file or writes an Intercom draft (Step 6); the user
publishes in Intercom.

## Scoping Questions

Ask these 4 in one message, skipping any the request already answers:

1. **New article, or revising one?** If revising, which one (Intercom ID or URL)? Fetch it with
   `get_article` and inherit its structure rather than starting blank.
2. **Article type?** How-to, reference, explanation or overview, or a hybrid. This decides which
   structure conventions apply.
3. **What's the source of truth for the functionality?** A ClickUp story, the user's own knowledge,
   or a live walkthrough. If the answer is "not sure" or "write something plausible," stop and ask
   again. No functionality claims without a named source.
4. **Who reads it, and are there prerequisites?** Platform user, org admin, IT or security contact, or
   partner; and any subscription, role, or feature that must already be in place.

Infer the rest from the sources, and state each inference in the handoff so the user can correct it:
the Collection and hub, child, or standalone shape; whether content varies by project type, tier, or
role (use a supported/available table if so); new terms needing a glossary; conflicting sources (note
which specifics the user's input overrides); and unconfirmed values (leave as placeholders with a named
owner, never a plausible number). Ask only when an inference is genuinely ambiguous. Images default to
placement recommendations; this skill can't capture screenshots.

## Process

### Step 1: Ground The Content

Assemble what's known to be true from the named source. If a claim can't be traced to the ClickUp
story, an existing article, or the user, leave it out and flag the gap. This is the main hallucination
guard; treat it as a hard gate.

### Step 2: Decide Collection And Shape

For new articles, use `article-information-architecture.md` to confirm the Collection (flag a poor fit
rather than forcing the closest one), decide hub, child, or standalone, and check whether any part
should be single-sourced from or extracted into a shared article. Settle this before drafting.

### Step 3: Pick The Structure And Draft

Apply only the conventions the article type and shape call for (a reference article skips numbered
steps and the "What You'll Need" gate; a hub stays an overview and routes to children). Draft to
`article-tone-and-voice.md` and `article-structure.md`. Skip "What You'll Need" when there are no real
prerequisites. No release-note or temporal framing.

### Step 4: Recommend Image Placements

Load the image framework. Where an image earns its place (its core test and the Orient, Confirm,
Explain job test), insert inline:

```
> 🖼️ **Image suggestion ([Orient / Confirm / Explain]):** [what the image should show and why it
> earns its place here — finish "without this image, the reader would have to..."]
> - **Type:** [Screenshot / Diagram / Decorative]
> - **Alt text:** "[≤155 characters, describing intent, ready to copy]"
> - **Filename:** `[descriptive-filename-in-title-case.png]`
```

Give real alt text and filenames, not placeholders. For screenshots, remind the user inline to capture
from dummy or sandboxed data, never real platform data. Don't over-recommend: where text, a table, or a
bold label would do, say an image was considered and rejected. Images are made in the CX Figma file.

### Step 5: Check And Verify

Check the draft yourself before handing it over:

- **Claims:** every functional statement traces to the story, an existing article, or the user. Nothing
  unshipped described as live; no internal names, codenames, client names or competitors. Anything
  still unsupported becomes a verification item. If the draft conflicts with a published article, tell
  the user which article and what differs.
- **Copy:** the draft follows `article-tone-and-voice.md` and `article-structure.md`.

Ask the user whether they or an SME have verified the steps and values against the current platform,
and whether any placeholder or assumption still needs confirming. List each open item as a direct
question about the content, so the reviewer can answer it quickly.

### Step 6: Save Or Write To Intercom

Ask the user which they want:

- **Markdown file:** ask where to save it, then save `article-{slug}-{YYYY-MM-DD}.md` there with
  frontmatter `title`, `status: draft`, `author`, `created`.
- **Intercom draft:** write it straight to Intercom as a draft, so nobody has to copy sections across.
  - **New article:** `create_article` with `state: draft`, in the confirmed Collection.
  - **Existing published article:** `update_article` changes the live article immediately; Intercom has
    no separate draft through this tool. Say so and offer a markdown file or a new draft article
    instead. Update the live article only if the user explicitly says to.
  - **Never** set `state: published`. The user publishes in Intercom after review.

Before any Intercom write, scan the draft for placeholder or AI text that must not land in an article:
unconfirmed values, `[TBC]`-style placeholders, image suggestion blocks, notes to the reviewer, and
anything addressed to the user rather than the reader. List what you found and ask whether to resolve,
remove or keep each one. Then name the article (title, and ID for an update) and the Collection, and
wait for a yes before the call.

`body` is raw HTML, and whitespace between block tags becomes blank paragraphs. Butt tags together with
no newlines or indentation, and make each deliberate blank line an explicit `<p>&nbsp;</p>`.

In the handoff, state the Collection and shape (and what it links to or is linked from), the inferences
you made, the open questions for the reviewer, and the file path or Intercom article ID.
