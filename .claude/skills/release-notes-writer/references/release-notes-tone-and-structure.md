# Tone & Structure for Release Notes

Release notes are a distinct article type from the rest of the help center. `article-tone-and-voice.md`
bans temporal/announcement framing everywhere else — release notes are the one place that framing is
correct, because the whole point is "here's what changed this release." Don't apply the timeless-framing
rule here; do apply everything else that isn't specific to that rule (plain sentences, no promotional
language, no meta-commentary).

Grounded in two published examples: [Release Notes: July 2026](https://help.omnisient.com/en/articles/15777797)
and [Release Notes: August 2026](https://help.omnisient.com/en/articles/16105904). Re-pull a couple of
recent ones each time you draft — this doc captures the pattern, not a frozen template — but treat these
two as the baseline if nothing's changed.

---

## Structure

Items 2 and 7 below are strict formatting rules, not stylistic defaults — every generated draft must
match them exactly, not "close enough."

1. **Banner image** at the top (`Release Notes.png`, produced separately — see Guardrails). Not
   something this skill generates.
2. **One H2 heading per item — always `##`, never `#`, `###`, or bold text standing in for a
   heading.** Title Case, no trailing punctuation. The heading names the feature or improvement itself
   — sometimes as a plain feature name ("Selection Builder: Clear Warnings for Unapplied Filter
   Changes"), sometimes with an explicit "New X" framing when the item is a genuinely new capability
   rather than a change to an existing one ("New Data Connector Added: Google BigQuery for Desktop &
   Server Connect"). Both are attested — pick whichever reads more naturally for the item, don't force
   every heading into the same template.
3. **A short paragraph** stating what the feature does and, where it matters, why it matters to the
   reader — concretely, not as a claim. One or two sentences is normal for a minor item.
4. **A bullet list** when the item has multiple distinct parts (a multi-step "how it works," or several
   independent sub-changes bundled under one heading, e.g. "Platform-Wide UI Polish"). Don't force a
   list where prose reads fine.
5. **A callout box** (⚠️ or similar) only for an operational warning the reader must act on before using
   the feature (e.g. "clear notebook outputs before submitting, or it'll be declined"). Not used for
   general emphasis.
6. **A "Learn more about [X] →" link** at the end of the item, only when the ticket names a knowledge
   base article to point to. If the ticket's KB field says "None," there is no link — don't invent one
   or link to something adjacent.
7. **`<hr>` divider** between items, with one blank text-sized line above it and one below it — never
   butted directly against the preceding paragraph or the following heading. Every item gets a divider
   after it except the last.
8. **Order:** the Major-type item (or items) leads, with more detail and, where relevant, a "How it
   works" bullet breakdown and any warning callout — it gets more space because it's the release's
   anchor. Minor items follow in whatever order the user sets, each shorter and lighter, usually a single
   paragraph with an optional link. If there's more than one Major item, ask the user which leads and in
   what order before drafting — don't guess.

## Voice

- Present tense throughout, describing what's true starting now.
- Temporal/announcement framing is fine and expected here ("now available," "you can now," "X is now
  supported") — this is the one article type where that's correct, unlike every other help article.
- Straight to the point, no fluff, no promotional adjectives ("powerful," "seamless," "game-changing").
  State what the feature does; let the reader judge the value.
- "You"/"we" both show up in practice ("Platform users can now connect directly to...", "We've made a
  range of consistency and usability improvements...") — favor "you" for describing what the reader can
  now do, and reserve "we" for framing a bundle of internal-facing work as a single grouped item (the UI
  polish example). Don't use "we" as a default voice throughout.
- No hedging language ("may," "might") unless the outcome genuinely varies by case.
- Each item is short. Even the Major item in these two examples tops out at a paragraph plus a 3-4 item
  bullet list — release notes are a scannable summary, not a full explainer. If an item needs more than
  that to make sense, that's a sign it needs its own help article (link to it) rather than a longer
  release note entry.

## Sourcing each item

Each release note item comes from a ClickUp ticket in the Release Communications board
(`https://app.clickup.com/9012824942/v/li/901218643488`). Within a qualifying ticket's description:

- **`### Release Comms Description`** — the client-facing copy. This is written for this purpose
  already; use it close to verbatim, light-edited for tone/structure consistency with the rest of the
  article. Don't substitute the raw engineering description above/instead of it — that's written for
  engineers, not customers.
- **`#### Knowledge Base Resource`** — either a link (use it for the "Learn more" line) or the literal
  word "None" (no link).
- **`#### To do:`** — an internal checklist for whoever's producing the comms. Not content; ignore it.

If a qualifying ticket has no `### Release Comms Description` section at all, don't fall back to the raw
description — flag it to the user and ask for comms-ready copy instead of drafting one from the
engineering description yourself.

**Editorial check before using ticket copy verbatim:** ticket descriptions are sometimes written with
internal context still in them — an unannounced client/partner name used as an example, a competitor
reference, internal ticket/system jargon. Flag anything like that before it goes into a client-facing
article; don't publish it just because it was in the source field.

## Guardrails

- **No image generation.** This skill produces placement notes only ("banner: same style as prior
  release notes"), same as the help-article-writer skill — a human or a separate design task produces
  the actual banner.
- **Don't invent a KB link.** "None" in the ticket means no link, full stop.
- **Don't pad a minor item to look bigger than it is.** The length differential between the Major
  anchor and the Minor items is deliberate — it signals relative importance to the reader.
