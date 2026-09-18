# Information Architecture in Help Center Articles

Standards for how articles relate to *each other* — content scoping, when to split one topic into
several articles, and when to extract shared functionality into its own article. This is a
different level of concern from `article-structure.md` (how one article is organized internally)
and `article-tone-and-voice.md` (how a sentence should sound) — this doc is about the shape of the
article *set*, not any single article.

---

## Table of Contents

1. [Collections are the top-level scope](#collections-are-the-top-level-scope)
2. [Summary style: hub articles and child articles](#summary-style-hub-articles-and-child-articles)
3. [Single-sourcing: extract shared functionality into its own article](#single-sourcing-extract-shared-functionality-into-its-own-article)
4. [Deciding whether to extract or inline](#deciding-whether-to-extract-or-inline)
5. [Linking conventions](#linking-conventions)
6. [Avoiding orphaned or duplicated content](#avoiding-orphaned-or-duplicated-content)
7. [Pre-write checklist](#pre-write-checklist)
8. [Sources](#sources)

---

## Collections are the top-level scope

Every article belongs to exactly one Collection, based on its primary functional scope. The
Collection is the first scoping decision — decide it before deciding whether the article needs to
be split or merged with anything else.

Collections currently configured (framed as "current," not closed — add a row when a new one is
configured, same as any other supported/available list in this doc set):

| Collection | Scope |
|---|---|
| Getting Started | Onboarding: account setup, key concepts, orientation for a brand-new user |
| Datasets | Preparing, cleaning, and understanding data — dataset types, mapping, collaboration |
| Uploading Data | Getting data into the platform — Server Connect, Desktop Connect |
| Projects | Core analytical products — ACE, Financial Inclusion, BasketScore, and other project types |
| Audience Selections and Activations | Building Selections and pushing them to activation channels |
| Analytics and Modelling | In-platform analysis tools — SQLPad, Jupyter Notebook |
| Omnisient Platform (Web App) | Core UI/navigation — workspace layout, platform-wide functionality |
| Admin and Settings | Organization, user, permission, and platform configuration management |
| Trust Center | Data security, privacy, compliance, certifications |
| Contact Omnisient | Support requests, bug reports, feature requests |

If a new article doesn't cleanly fit an existing Collection, that's a flag, not a guess — raise it
rather than forcing the article into the closest-sounding one or inventing a new Collection
unilaterally. Collection taxonomy changes are a deliberate decision, same as any other context
change.

---

## Summary style: hub articles and child articles

When one functional area has multiple significant sub-features — a settings section with several
distinct pages, for example — write a **hub article** that briefly orients the reader to each
sub-feature and links out to a **child article** for any sub-feature with enough content to stand
on its own. The hub stays an overview; depth lives in the children.

This is the same principle behind Wikipedia's "summary style" editorial guideline: a main article
gives a short overview of a subtopic and links to "Main article: X" once that subtopic has enough
content to warrant its own page, rather than growing the main article indefinitely.

**When to split a sub-feature out into its own child article:** the sub-feature has enough
internal structure — its own steps, tables, or prerequisites — that inlining it in the hub would
make the hub too long to scan, or it serves a task distinct enough that a reader wouldn't need the
rest of the hub to use it.

**The hub article is still an article** — it follows the same opening-formula and structure rules
as any other article (see `article-structure.md`). Its scope is just "orient and route," not
"explain everything."

---

## Single-sourcing: extract shared functionality into its own article

When the *same* functionality is used by two or more otherwise-independent articles, extract it
into its own standalone article and link to it from every parent, rather than duplicating the
content in each one.

This is the core idea behind topic-based authoring and single-sourcing in structured-writing
practice: write a reusable, standalone unit of content once, and reference it from wherever it's
needed. The payoff is maintenance, not just avoiding repetition — when the shared functionality
changes (a new option gets added, a new provider is supported), there's exactly one article to
update, and every parent that links to it is automatically current.

**Trigger:** it's not just *similar* content across two articles — it's the *same* functionality,
genuinely shared, with enough internal structure (a table, a set of steps) to be worth its own
article rather than a paragraph repeated in each parent.

---

## Deciding whether to extract or inline

Neither the hub/child split nor the single-sourcing extraction has a hard size threshold — both
come down to the same judgment call: **if the content in question would need its own heading,
table, or step sequence to explain properly, give it its own article. If it's a sentence or two,
inline it** in whichever parent(s) need it.

Re-evaluate this as functionality grows. Content that started as a short inline mention can
outgrow that spot — when it does, extracting it into its own article and replacing the inline text
with a link is a normal, expected edit, not a sign the original article was wrong.

---

## Linking conventions

- **Hub → child links are the hub's core content**, not a bolted-on list. This is different in
  kind from the "no manually-curated Related Articles section" rule in `article-structure.md` —
  that rule bans a generic, loosely-related list of links added to the bottom of an otherwise
  unrelated article. A hub article's entire purpose is to list and link its children; that's
  structural navigation, not decoration.
- **Parent → shared-article links use the existing 👉 inline pointer** (see
  `article-structure.md`'s typed-callouts section), placed at the exact point where the shared
  content would otherwise have been explained in full.
- **Child/shared articles don't need to link back to every parent.** A shared article can be
  referenced by several parents without listing all of them — Intercom's own related-article
  surfacing handles discovery in that direction.

---

## Avoiding orphaned or duplicated content

Before publishing a new article, check two things:

- **Is this functionality already documented elsewhere?** If so, link to it (per single-sourcing
  above) instead of re-explaining it. Re-explaining creates a second copy that can silently drift
  out of sync with the first.
- **Does this article's scope overlap enough with an existing one that they should be merged**,
  rather than coexisting as two similar, competing articles on the same topic? Overlapping scope
  is a sign the Collection or hub/child boundary needs revisiting, not a reason to just publish
  and sort it out later.

---

## Pre-write checklist

Before drafting, confirm:

- [ ] The article's Collection is decided first, before any other scoping decision.
- [ ] If the functional area has multiple significant sub-features, a hub article orients and
      links; each child article carries its own depth.
- [ ] If the same functionality is used by 2+ otherwise-independent articles, it lives in its own
      standalone article, linked from each parent — not duplicated.
- [ ] The extract-vs-inline call is based on whether the content needs its own heading/table/steps
      — not an arbitrary word count.
- [ ] Hub-to-child links are treated as core content; parent-to-shared-article links use the 👉
      inline pointer at the point of relevance.
- [ ] A check was made for existing content covering the same functionality before writing new
      content from scratch.

## Sources

Grounded in structured-writing practice: Wikipedia's "summary style" editorial guideline (main
article + linked sub-articles once a subtopic earns its own page) and topic-based
authoring/single-sourcing principles (write a reusable unit of content once, reference it from
every place it's needed, maintain it in one place).
