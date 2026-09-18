# Content JSON schema

`scripts/build-deck.cjs` renders a deck from a JSON file with this shape:

```json
{
  "meta": { "topic": "Short Topic For Footer", "date": "2026-08-19" },
  "slides": [
    { "type": "cover", "title": "...", "subtitle": "..." },
    { "type": "content", "kicker": "TODAY", "headline": "...", "blocks": [ ... ] }
  ]
}
```

- `meta.topic` – goes in every footer: "Omnisient · {topic} · Confidential". Keep it short (2-4 words).
- `meta.date` – shown on the cover slide only.
- `slides[0]` should be `type: "cover"`. Every other slide is `type: "content"` with a `kicker` (short, all-caps section label – you don't need to type it in caps, the renderer uppercases it) and a `headline`.

## Block types

Blocks stack vertically in the order given, starting just under the headline. Use `row` to place blocks side by side.

- **cardGrid** – `{ "type": "cardGrid", "cards": [{ "title": "...", "body": "..." }, ...] }`. 2 or 3 cards read best.
- **navyPanel** – `{ "type": "navyPanel", "title": "...", "bullets": ["...", "..."] }` (or `"body": "..."` instead of bullets for a paragraph). Use for current-state summaries, "proposed" comparisons, taglines.
- **callout** – `{ "type": "callout", "tone": "blue", "text": "..." }`. `tone` is `"blue"` (normal takeaway) or `"red"` (risk/caveat). One sentence.
- **bulletList** – `{ "type": "bulletList", "items": ["...", "..."] }`. Plain bullets, no card box – use for strategic points and next-step actions.
- **table** – `{ "type": "table", "headers": ["", "Current", "Proposed"], "rows": [["Plan", "$29/mo", "$99/mo"], ...] }`.
- **paragraph** – `{ "type": "paragraph", "text": "..." }`. A lead sentence or two, no box.
- **row** – `{ "type": "row", "blocks": [ <block>, <block> ], "gap": 0.2 }`. Lays out 2+ blocks side by side. Give a block `"weight": 2` to make it wider relative to its row siblings (default weight is 1). Used for: cards-left/panel-right (today slide), panel-vs-panel (comparison slide), two side-by-side callouts (numbers slide risk boxes).

Every block except `row` can take an explicit `"h"` (inches) to override its default height if the auto-flow spacing looks off.

**In practice this is needed often, not rarely.** Default heights (`cardGrid`/`navyPanel` 1.5in, `callout` 0.5in) assume short single-line content. Any `navyPanel` or card with 2+ bullets, or any wrapped one-line bullet, will overflow and bleed into the block below it – this happened on 3 of 9 slides in the first real deck built with this skill. Rule of thumb: for a `navyPanel`/`cardGrid` with bullets, budget ~0.35in per bullet line (assume a wrap if a bullet is longer than ~55 characters) plus 0.5in for the title/padding, and set `"h"` explicitly. When two blocks sit in the same `row`, give both the same explicit `"h"` so their boxes align – otherwise the shorter one looks visually mismatched even though it doesn't overflow. Always check the rendered PNG (Step 6) rather than assuming the default is fine.

## Worked example

See `references/example-content.json` for a full 3-slide example (cover, a "today" slide with a row of cards + panel, and a numbers slide with a table + two callouts) that was used to validate the renderer.

## Gathering inputs before writing the JSON

Before generating a deck, get the following from the user (ask directly, don't guess numbers):

1. **Topic** – what's being proposed (one short phrase for the footer/cover)
2. **Current state** – what's true today, and what's missing or costly about it
3. **The proposal** – what specifically is being asked for
4. **Comparison** – today vs. after, in concrete terms
5. **Stakeholders** – who benefits and how (by team/role)
6. **The product/mechanism** – what it is and how it actually works, 2-3 use cases
7. **Numbers** – current cost, proposed cost, currency, any overage/risk terms
8. **Why now** – the strategic or timing argument
9. **The ask** – the exact next step and who needs to approve it

Skip sections that don't apply rather than padding – stay under ~15 slides total.
