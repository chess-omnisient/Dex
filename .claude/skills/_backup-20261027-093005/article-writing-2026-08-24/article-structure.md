# Structure in Help Center Articles

Standards for how a help article is organized and formatted — what goes first, when to use a
table vs. prose, and the fixed set of formatting conventions the team uses consistently.
Complementary to `article-tone-and-voice.md` (how a sentence should sound) and
`image-usage-in-help-articles.md` (when and how images are used).

---

## Table of Contents

1. [Open with a quick overview, grounded in an example](#open-with-a-quick-overview-grounded-in-an-example)
2. [Short paragraphs, one idea each](#short-paragraphs-one-idea-each)
3. [Tables over prose for 2+ variants](#tables-over-prose-for-2-variants)
4. [Numbers: numerals vs. spelled out](#numbers-numerals-vs-spelled-out)
5. [Heading hierarchy](#heading-hierarchy)
6. [Bold UI labels exactly as they appear](#bold-ui-labels-exactly-as-they-appear)
7. [Refer to UI elements precisely](#refer-to-ui-elements-precisely)
8. [Bullets, inline code, and breadcrumbs](#bullets-inline-code-and-breadcrumbs)
9. ["What you'll need" — only when real prerequisites exist](#what-youll-need--only-when-real-prerequisites-exist)
10. ["Where to find" — only when navigation isn't obvious](#where-to-find--only-when-navigation-isnt-obvious)
11. [Typed callouts](#typed-callouts)
12. [Numbered steps only when order matters](#numbered-steps-only-when-order-matters)
13. [Footnotes for table caveats](#footnotes-for-table-caveats)
14. [Group sections by concern, not history](#group-sections-by-concern-not-history)
15. [Code belongs in a code block, never a screenshot](#code-belongs-in-a-code-block-never-a-screenshot)
16. [No manually-curated "Related Articles" section](#no-manually-curated-related-articles-section)
17. [Intercom HTML conventions](#intercom-html-conventions)
18. [Pre-write checklist](#pre-write-checklist)

---

## Open with a quick overview, grounded in an example

The first thing in every article is a quick overview of what the functionality *is* — not a
runway, not a table of contents, not a restated title. Ground it in a concrete example wherever
the concept is abstract enough to need one.

This is the exact point where structure and tone & voice meet: the opening carries the tone rules
(present tense, no promotional language, no announcement framing — see
`article-tone-and-voice.md`) more than any other sentence in the article, because it's the
reader's first signal of what kind of article this is.

Two opening formulas, both acceptable:

- **"[UI location] is where you [verb]"** — "Database Settings > Data Source is where you choose
  which database or data warehouse to connect to..."
- **"[Feature] is a [thing]" / "[Feature] lets you [verb]"** — "Selections let you create a
  filtered sub-set of customers from the data available within a project — a precision audience
  built from the attributes that matter to you. For example, a segment of customers over the age
  of 30 who haven't yet purchased a property."

Keep the opening to **1-3 short paragraphs, with no heading above it** — it's the article's
introduction, not a section in its own right. Close it on a phrase that sets up what follows, so
the transition into the first real heading doesn't feel abrupt.

---

## Short paragraphs, one idea each

This isn't just an opening-paragraph rule — it applies everywhere in the article. One idea per
paragraph, short enough to scan at a glance. If a paragraph is doing two jobs (e.g., explaining a
concept *and* listing its exceptions), split it, or move the exceptions into a table per the rule
below.

---

## Tables over prose for 2+ variants

Auth methods, options, statuses, roles, notification events, project types, dataset types — any
time there are 2 or more variants of the same kind of thing, use a table. Never a bulleted wall of
"Option A does X, Option B does Y."

Frame the table as **"supported / available,"** never as a closed set stated in prose ("there are
only three ways to..."). This lets a new row get added when the underlying functionality grows,
without needing to rewrite a sentence — see the timelessness rule in `article-tone-and-voice.md`.

> "Supported providers: Microsoft / Azure SQL Server, MySQL / MariaDB, PostgreSQL, Snowflake, Hive
> ODBC, Databricks, Google BigQuery" — framed as a current list, not a closed one.

**Table formatting conventions:**
- Header row background `#e8e8e880` (grey), bold header text. Use the default/plain text color,
  not white — white-on-`#e8e8e880` is a legibility problem (light text on light grey).
- **Two-column glossary tables** (term / definition) are the standard format for defining several
  terms at once.
- **Boolean/status columns are centered** in the cell.
- **Never leave a boolean cell blank.** Use an explicit ❌ for "not applicable" or "no access" — a
  blank cell is ambiguous between "no" and "not filled in yet."
- **Annotate a conditional ✅** with a short parenthetical, e.g. "✅ (project owner)," "✅ (if
  assigned)."

---

## Numbers: numerals vs. spelled out

- **In prose, spell out small counts** — "Two things must be in place," "Three workspace sizes are
  available."
- **In tables and exact measurements, always use numerals** — `2` CPU, `8 GB` RAM, not "two CPU,
  eight gigabytes." A number a reader might scan for (a spec, a quantity to match against their
  own setup) should be a numeral so it's scannable, not a word to parse.

---

## Heading hierarchy

- **H1** for major sections, **H2** for subsections, **H3** for granular breakdowns within a
  subsection.
- A flat H1 → H2 hierarchy (skipping H3 entirely) is fine for reference/matrix-style articles.
  Go to H3 only when a subsection itself has multiple distinct breakdowns worth separating (e.g.
  a table of operators broken out by data type).
- **Headings are descriptive, not vague.** A reader should know what's in a section from its
  heading alone, without opening it — "Project Lifecycle" or "Project Expiry and Locking," not
  "Other Information" or "More Details."
- **Sibling headings at the same level use parallel grammatical structure.** If one subsection
  heading is gerund-led ("Creating a Project"), its siblings should be too, not a mix of gerunds
  and plain nouns.
  > **Bad:** "Creating a Project," "Selecting a Dataset," "Matching Types," "Project Roles" — three
  > gerund-led headings, then a plain noun phrase breaks the pattern.
  > **Good:** "Assigning Project Roles" restores parallelism.
- **Heading case: Title Case.** Capitalize the main words of every heading, at every level.
- **Headings are never bolded.** The heading level itself carries the visual weight — don't wrap
  heading text in additional bold formatting on top of it.

---

## Bold UI labels exactly as they appear

Button, field, toggle, and tab names are bolded verbatim, matching on-screen capitalization and
wording exactly, so the reader can pattern-match against the real UI without translating. This
includes actions described in prose ("always bold actions") — not just labels inside tables. The
same discipline applies to feature/product names even when not bolded — spell and capitalize a
given name (e.g. "SQLPad," "Jupyter Notebook") the same way everywhere, not as a stylistic choice
per sentence.

---

## Refer to UI elements precisely

- **"Select," not "click."** Not every reader interacts via a mouse click — keyboard navigation,
  touch, and screen readers all "select" without "clicking." "Select" describes the outcome, not
  the input method.
  > **Bad:** "Click the **+** icon next to..." **Good:** "Select the **+** icon next to..." Use
  > "select" consistently for this kind of action throughout an article — don't mix "click" and
  > "select" for the same kind of interaction.
- **Refer to elements by their name/label, not by screen position.** Don't say "the button on the
  right" or "the option above" — layouts shift across screen sizes and redesigns, but a named
  element ("the **Create Project** button") stays findable regardless.

---

## Bullets, inline code, and breadcrumbs

- **Unordered lists** for non-sequential items (requirements, options).
- **Ordered lists** for sequential steps — see [Numbered steps only when order
  matters](#numbered-steps-only-when-order-matters) below for when a sequence deserves a full
  numbered-step treatment vs. a simple ordered list.
- **Bold the lead-in term** inside a bullet, before the explanation — e.g. "**Add Rule** lets you
  add another condition..."
- **Inline `` `code` ``** for commands, filenames, and placeholders inside a sentence;
  **`<pre><code>` blocks** for multi-line snippets. See also [Code belongs in a code
  block](#code-belongs-in-a-code-block-never-a-screenshot).
- **Navigation breadcrumbs are written inline and bolded, with a real arrow** — "**Admin →
  Users**," not spelled out in prose ("go to Admin, then Users").

---

## "What you'll need" — only when real prerequisites exist

A prerequisite checklist ahead of the steps, so a missing precondition surfaces immediately rather
than halfway through. **Only include this section when the functionality actually has
prerequisites** — a required subscription, a permission, another feature that must be enabled
first, or a dependency on another article's setup. Don't manufacture a "What You'll Need" section
for functionality that has none; an empty or padded gate is worse than no gate at all.

---

## "Where to find" — only when navigation isn't obvious

A short section — steps plus a navigation screenshot — showing the reader where in the platform a
feature lives. Include it when the entry point isn't obvious from the article's title alone (e.g.
a feature reachable from two different places, or nested a few levels deep); skip it when the
feature's location is already self-evident from the opening sentence.

---

## Typed callouts

Callouts are **color-coded**, and each color is tied to exactly one purpose — don't mix purposes
within a color:

| Color | Emoji | Use for |
|---|---|---|
| Amber | ⚠️ | Warnings — missing prerequisites, troubleshooting, "this will get declined" |
| Amber | 🔐 | Permissions |
| Red / pink | ⚠️ | Irreversible or destructive actions ("Deactivation can't be undone") |
| Blue / indigo | 💡 or 🚀 | Tips, clarifications, edge cases, definitions, or a notable/higher-tier feature |
| Gray | none, or bold "Note:" | Lower-stakes asides, cross-references to a related feature |

⚠️ spans two colors by severity — amber for a recoverable warning (a missing prerequisite, a step
that will get declined), red/pink only for something the reader can't undo. Don't use red/pink for
a merely inconvenient mistake.

Emoji usage rules, independent of color:

| Emoji | Rule |
|---|---|
| ⚠️ | Warning or destructive-action callouts only |
| 💡 | Tips — either inside a blue/indigo callout, or inline in body text |
| 🚀 | Flags a new or higher-tier feature; always inside a callout |
| 👉 | An **inline pointer**, not a callout — sits immediately before a "Learn more" / "See [X]
article" link, outside any colored box |
| ✅ / ❌ | Table cells only, as explicit boolean indicators — never a callout marker |

---

## Numbered steps only when order matters

Use numbered steps for genuine sequences (Step 1, Step 2...) where doing them out of order breaks
the flow. Everywhere else — reference-heavy sections, a settings table, a list of independent
options — use flat headers, not numbers. Don't number things just to look procedural.

**Each step is one action.** Don't compress two distinct actions into a single numbered step —
split them, so the reader can confirm they've completed one thing before moving to the next.

> **Good:** a sign-in sequence written as five single-action steps — opens the login page; detects
> the organization and redirects; the identity provider authenticates; a token is sent back; the
> token is validated and the user is logged in — rather than bundling any two of these into one
> step.

---

## Footnotes for table caveats

Use footnote markers (¹ ²) to attach an edge case or caveat to a specific table cell, instead of
breaking the table's scannability with an inline aside or an extra column that's mostly empty.

> "✅¹ ... ¹ Greyed out if the partner has not enabled selections on their dataset share
> agreement." — the wording follows `article-tone-and-voice.md`'s hedging rule (a fully
> deterministic if-then doesn't get a "may").

---

## Group sections by concern, not history

Structure the article around the reader's mental model of the *concern* (e.g., all lifecycle
content — status, approvals, expiry, notifications — grouped together as one narrative), not
around the order features happened to ship in. A reader looking for "what happens when this
expires" shouldn't have to jump between three unrelated sections to piece it together.

---

## Code belongs in a code block, never a screenshot

If the thing being shown is text or code, use a real code block — not a screenshot of it.
Screenshotted text can't be copied, searched, or read by a screen reader. This is already stated
in `image-usage-in-help-articles.md`'s "Choosing the image type" table; it's restated here as a
structure rule because it's the boundary between "use an image" and "use a code block." For a
short inline value inside a sentence, use inline `` `code` `` rather than a full block — see
[Bullets, inline code, and breadcrumbs](#bullets-inline-code-and-breadcrumbs).

---

## No manually-curated "Related Articles" section

Don't add a hand-written "Related Articles" or "See Also" list at the end of an article. Intercom
surfaces related articles itself — that's its job, not the writer's.

This doesn't touch the 👉 inline pointer from the typed-callouts list above: a specific, contextual
link to another article, placed exactly where a claim needs it (e.g., "See Audience Activation
Channels for the full list of supported destinations," right where that option is described), is
doing real work and stays. What's out is a generic, loosely-related list of links bolted onto the
bottom of the article with no specific reason for each entry.

---

## Intercom HTML conventions

Two mechanical conventions for when an article is authored or exported as Intercom HTML, not just
written as markdown — these exist because Intercom's own editor produces specific markup, and
diverging from it is what causes visible formatting drift after publish.

**Table headers:** bold text (not white — see the table-formatting note above) on a grey
background:

```html
<table role="presentation" style="border: 1px solid #c6c9c0; border-radius: 6px; border-collapse: separate; border-spacing: 0;">
  <tbody>
    <tr>
      <td style="background-color: #e8e8e880; padding: 8px;"><p class="no-margin"><b>Column Header</b></p></td>
      <td style="background-color: #e8e8e880; border-left: 1px solid #c6c9c0; padding: 8px;"><p class="no-margin"><b>Column Header</b></p></td>
    </tr>
    <tr>
      <td style="border-top: 1px solid #c6c9c0; padding: 8px;"><p class="no-margin">Cell</p></td>
      <td style="border-left: 1px solid #c6c9c0; border-top: 1px solid #c6c9c0; padding: 8px;"><p class="no-margin">Cell</p></td>
    </tr>
  </tbody>
</table>
```

Header background is `#e8e8e880`, not any other shade.

**Paragraph spacing:** every paragraph is `<p class="no-margin">...</p>`, and the visual gap
between paragraphs comes from a single empty `<p class="no-margin"></p>` inserted between them —
never from the browser's default paragraph margin, and never from a double `<br>`. Skipping the
`no-margin` class lets top and bottom paragraph margins stack between consecutive paragraphs,
which reads as noticeably larger spacing once published than the same content looks like in a
markdown editor, even though nothing about the visible line breaks changed. If spacing looks
"correct" in a markdown draft but inflated after it hits Intercom, this is the first thing to
check.

---

## Pre-write checklist

Before drafting, confirm:

- [ ] The opening states what the thing *is*, in 1-3 paragraphs with no heading, grounded in a
      concrete example if abstract, closing on a transition into the first section.
- [ ] Paragraphs are short, one idea each, throughout the article — not just in the opening.
- [ ] Every set of 2+ variants is a table, framed as "supported/available."
- [ ] Table headers are bold on `#e8e8e880`, boolean cells are centered with explicit ❌/✅
      (parenthetical if conditional) and never left blank.
- [ ] Small counts in prose are spelled out; measurements and table values are numerals.
- [ ] Headings follow H1 → H2 → H3 (flat where reference/matrix-style), are descriptive rather
      than vague, use Title Case, are never bolded, and are grammatically parallel with their
      siblings.
- [ ] UI labels, actions, and feature/product names are exact and consistently capitalized.
- [ ] Instructions say "select," not "click," and name the element rather than its screen position.
- [ ] Bullet lead-in terms are bolded; inline values use `` `code` ``; breadcrumbs are bolded with
      a real arrow.
- [ ] "What You'll Need" is included only if real prerequisites exist.
- [ ] "Where to find" is included only if the navigation path isn't already obvious.
- [ ] Callouts use the right color for their purpose, and the right emoji rule (👉 is an inline
      pointer, not a callout; ✅/❌ are table-only).
- [ ] Numbered steps are used only where order genuinely matters, and each step is one action.
- [ ] Table caveats use footnote markers, not inline asides.
- [ ] Sections are grouped by concern, not by when the feature shipped.
- [ ] Any code or command is a code block (or inline code for a short value), never a screenshot.
- [ ] No manually-curated "Related Articles" section — Intercom handles that.
- [ ] If exported as HTML: table headers use bold text on `#e8e8e880`, and every paragraph carries
      `class="no-margin"` with spacing done via a single empty paragraph, not default margins.

## Sources

Cross-checked against industry technical-writing style guides — Google Developer Documentation
Style Guide, Microsoft Writing Style Guide, and GitLab Docs Style Guide — for consistency with
established norms.
