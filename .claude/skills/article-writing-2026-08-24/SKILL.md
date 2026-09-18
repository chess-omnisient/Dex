---
name: help-article-writer
description: "Draft or substantially revise an Intercom help-center article using the team's tone & voice, structure, information architecture, and image guidelines. Asks scoping questions up front (new vs. existing, Collection, hub/child/shared-article shape, article type, prerequisites, grounding source) to keep content grounded in real system functionality and minimize hallucination. Recommends image placements per the image guidelines, each with ready-to-use alt text and an export filename. Use when drafting a new help article or restructuring an existing one. Not for release notes (separate, not-yet-written guidelines)."
effort: high
output: "output/{area}/published/article-{slug}-{YYYY-MM-DD}.md with status: draft, per the frontmatter contract (or output/{area}/drafts/ for exploratory work)."
---

# Help Article Writer

Writes Intercom help-center articles the way this team writes them — grounded in real
functionality, in the team's established tone, voice, structure, and information architecture,
with image placement suggestions built in. This skill is intentionally **strict and verbose**: it
asks more upfront questions than a typical PM OS skill, because the cost of a hallucinated,
off-tone, or badly-scoped article published to customers is high, and because articles need to
stay accurate as functionality changes sprint over sprint.

**Not for release notes.** Release notes are a distinct article type with their own voice
(chronological/announcement framing is *correct* there) and their own guidelines, which don't
exist yet. If the request is a release note or changelog entry, say so and stop — don't force it
through this skill's timeless-framing rules.

## Before You Start — Read These

Read all four, every time, regardless of article type:

1. `frameworks/article-tone-and-voice.md` — sentence-level voice: tense, person, banned language,
   timeless framing.
2. `frameworks/article-structure.md` — document organization: opening formula, tables vs. prose,
   heading rules, callouts, section grouping.
3. `frameworks/article-information-architecture.md` — how this article relates to *other*
   articles: Collection assignment, hub/child decomposition, single-sourcing shared functionality.
4. `frameworks/image-usage-in-help-articles.md` — when an image belongs, image type, placement,
   and the accessibility/privacy/craft standards for any image you recommend.

These four are the complete rule set — don't restate their contents from memory or an earlier
draft; re-read them each time in case they've changed.


## Scoping Questions

Ask these before drafting anything. Skip a question only if the author has already answered it in
their request. These exist to keep the article grounded in verified functionality and correctly
scoped against the rest of the article set — **the fewer of these you skip, the less hallucination
and rework risk later.**

**Identity and location**
1. **New article, or revising an existing one?** If existing, get the Intercom article ID/URL or
   the local file path — needed to diff against, and to inherit its `status`/frontmatter rather
   than starting blank.
2. **Which Collection does this belong to?** (Getting Started, Datasets, Uploading Data, Projects,
   Audience Selections and Activations, Analytics and Modelling, Omnisient Platform/Web App, Admin
   and Settings, Trust Center, Contact Omnisient — see
   `frameworks/article-information-architecture.md` for the current list.) If it doesn't cleanly
   fit one, flag that rather than forcing it into the closest-sounding Collection.
3. **Is this a hub, a child, or a standalone article — and is there shared functionality
   involved?** Per `article-information-architecture.md`: if the functional area has multiple
   significant sub-features, this may need a hub article (orients + links) plus separate child
   articles (depth), rather than one long article. If the *same* functionality is already used by
   another, otherwise-independent article, it should be single-sourced — extracted to its own
   article and linked from each parent — rather than duplicated here. Check for existing content
   covering the same functionality before assuming this needs new content at all.

**What it's about**
4. **What article type is this?** How-to guide, reference, explanation/overview, or a hybrid
   (e.g., reference table + explanation intro)? This determines which structure conventions
   actually apply — the "What You'll Need" gate and numbered steps are how-to conventions; a pure
   reference article won't use either.
5. **What is the actual functionality this documents, and what's the source of truth for it?**
   Acceptable sources: a shipped feature you can point to in `context/platform/`, a completed
   ClickUp story/ticket, direct SME knowledge from the author, or a live walkthrough of the feature.
   If the answer is "not sure" or "just write something plausible" — **stop and ask again.** Don't
   draft functionality claims without a named source; this is the main hallucination guard.
6. **Does real documentation or ClickUp content already exist that might conflict or be stale?**
   If so, get it, and note explicitly in the draft (as an internal comment, not published text)
   which specifics came from the author directly overriding a stale doc, so the correction isn't
   silently re-derived wrong later.
7. **Are there real prerequisites** — a subscription, a permission/role, another feature that must
   already be enabled, a dependency on another article's setup? If none, skip the "What You'll
   Need" section entirely rather than manufacturing one.
8. **Who is the primary reader?** General platform user, an org admin, an IT/security contact
   (e.g., for SSO-type setup), or a partner? This affects which examples and UI states to describe.
9. **Does the content vary by project type, subscription tier, or role?** If yes, it needs a
   "supported/available" table, not flat prose — flag this now so the draft doesn't need
   restructuring later.
10. **Any unconfirmed specifics** — a value, a timeline, a behavior — that aren't nailed down yet?
    Flag these as placeholders with a named owner to confirm with, rather than inventing a
    plausible-sounding number.
11. **Does this introduce new terminology** the reader won't already know? If several terms need
    defining, a two-column glossary table up front may be worth it.

**Images**
12. **Do you have (or can you capture) real screenshots**, or should this skill only produce
    placement *recommendations* for you to fill in? Default to recommendations — this skill
    cannot capture or generate actual screenshots.

## Process

### Step 1: Ground the content

Using the answers to Q5–Q6, assemble what you actually know to be true about the functionality.
If a claim can't be traced to `context/platform/`, a ClickUp item, or something the author told you
directly, don't include it — flag the gap instead of filling it with a plausible-sounding
sentence. This is the single most important step for reducing hallucination; treat it as a hard
gate, not a formality.

### Step 2: Decide Collection and article shape

Using the answers to Q2–Q3 and `article-information-architecture.md`: confirm the Collection,
decide whether this is a hub, a child, or a standalone article, and check whether any part of it
should be single-sourced from (or extracted into) a separate shared article instead of drafted
fresh. Resolve this before drafting — restructuring after a full draft exists is more expensive
than deciding up front.

### Step 3: Pick the article type and applicable structure

From Q4, decide which structure conventions apply (see `article-structure.md`). A reference
article doesn't need numbered steps; a how-to guide does if the steps are order-dependent. A hub
article stays an overview and routes to children rather than going deep itself. Don't apply every
convention to every article — apply the ones the type and shape call for.

### Step 4: Draft

Apply `article-tone-and-voice.md` and `article-structure.md` in full — re-read them rather than
relying on the highlights below, since these are the two easiest rules to slip on and the most
likely to have been refined since your last read:
- Open with a quick overview grounded in a concrete example if abstract; Title Case, never-bolded
  headings; tables for 2+ variants framed as "supported/available."
- Present tense; second person for reader actions, imperative in numbered steps; no
  "we"/"our"/"us"; no "please"; no promotional or anthropomorphizing language; no
  temporal/announcement framing (this rule has no exceptions in this skill — see the "not for
  release notes" note above).
- "Select," not "click"; name UI elements, not their screen position; one action per numbered
  step; footnotes for table caveats; sections grouped by concern.
- Any code/command goes in a code block (or inline code for a short value), never a screenshot
  placeholder. No manually-curated "Related Articles" section — a hub article's links to its
  children are the exception (see `article-information-architecture.md`).

### Step 5: Recommend image placements

For each point in the draft where an image would earn its place (apply the image doc's core test
and the Orient/Confirm/Explain job test), insert a placement recommendation inline, in this exact
format:

```
> 🖼️ **Image suggestion ([Orient / Confirm / Explain]):** [what the image should show and why it
> earns its place here — finish "without this image, the reader would have to..."]
> - **Type:** [Screenshot / Diagram / Decorative]
> - **Alt text:** "[≤155 characters, describing intent, ready to copy]"
> - **Filename:** `[descriptive-filename-in-title-case.png]`
```

Give real, usable alt text and filenames per the image doc's accessibility rules — not
placeholders like "image here." If the image type is a screenshot, remind the author inline that it
must be captured from dummy/sandboxed data, never real platform data (see the image doc's privacy
section).

Don't over-recommend. If the core test in the image doc says text/table/bold-label would do the
job as well, don't suggest an image there — say so, so the author knows it was considered and
rejected, not missed.

### Step 6: Request verification before finalizing

Before treating the draft as done, explicitly ask the author:
- Have you (or an SME) personally verified these steps/values against the current platform state?
- Is there anything in the draft marked as a placeholder or assumption that still needs
  confirming?

Don't let a draft go to `status: ready` with an unconfirmed placeholder still in it — either get
the confirmation or leave it flagged as an open item in the handoff.

### Step 7: Save

Follow the standard artifact lifecycle: determine area from the current user's preferences
(`context/preferences/{current-user}.yaml`, or ask), save to `output/{area}/published/` with
`status: draft` on a feature branch (or `output/{area}/drafts/` if this is exploratory), using the
frontmatter contract (`title`, `status`, `author`, `created`). In the handoff to the author, state the
Collection and article shape decided in Step 2 (hub/child/standalone, and what it links to or is
linked from) so that's visible without re-deriving it. Flip to `status: ready` only once Step 6's
verification is confirmed and before the PR that merges it to `main`.

## Guardrails

- **Ground every claim.** No functionality detail without a traceable source (Step 1). When in
  doubt, ask again rather than draft around the gap.
- **No duplicated or orphaned content.** Before drafting new content, check whether it's already
  covered elsewhere (per `article-information-architecture.md`) — link to it instead of
  re-explaining it.
- **No release-note framing, ever, in this skill.** If the request is actually a release note,
  say so and stop.
- **Don't skip scoping questions to save time.** This skill is deliberately verbose because the
  failure mode (a published article with invented specifics, off-tone voice, or duplicated/
  orphaned content) is expensive to catch later.
- **Images are recommendations only** — this skill does not capture, generate, or export actual
  image files. It produces the placement, job, alt text, and filename; a human captures the image.
