# Product design system — content JSON schema

`scripts/build-product-deck.cjs` renders a document from a JSON file with this shape:

```json
{
  "meta": { "tagline": "Short tagline for every footer" },
  "slides": [
    { "eyebrow": "SECTION LABEL", "title": "...", "lead": "One-line intro sentence.", "blocks": [ ... ] }
  ]
}
```

- `meta.tagline` — shown in every footer, left-aligned, next to the page number.
- Every slide gets the same header automatically: uppercase eyebrow, bold title, the real Omnisient logo top-right, hairline below. There's no separate "cover" slide type in this style — slide 1 is just a normal slide, usually with a 3-card summary (problem/proposal/ask) as its only block.
- `lead` is optional — a single-sentence intro under the header hairline. Keep it to ~100 characters so it doesn't wrap (a wrapped lead can collide with whatever block comes right after it).

## Block types

Blocks stack vertically in the order given.

- **cardGrid** — `{ "type": "cardGrid", "cols": 3, "cardH": 1.05, "cards": [{ "num": 1, "title": "...", "desc": "...", "tags": ["..."] }] }`. `num` (optional) draws a numbered circle badge — use it for sequential/ranked cards, omit it for parallel cards. `tags` (optional) draws small checkmark pill tags at the card's bottom. `cardH` sets each card's height explicitly — always set this rather than trusting the 1.05in default once descriptions run past ~2 lines.
- **twoPanel** — side-by-side outlined panels (the "we have / we don't", "proposed / retained" pattern):
  ```json
  { "type": "twoPanel", "h": 1.85,
    "left": { "label": "...", "icon": "check", "accent": "main", "items": ["...", "..."] },
    "right": { "label": "...", "icon": "no", "accent": "secondary", "items": ["...", "..."] } }
  ```
  `icon` is `"check"` (positive, main blue) or `"no"` (negative, secondary/dark blue). `accent` colors the panel's top bar and header text the same way. Always set `h` explicitly, budgeting ~0.4in per item (more if an item is long enough to wrap).
- **pillRow** — `{ "type": "pillRow", "pills": [{ "label": "...", "sub": "...", "bg": "F1F3FA", "text": "30297E" }] }`. Equal-width pill badges. `bg`/`text` are hex strings without `#`.
- **banner** — `{ "type": "banner", "text": "...", "icon": "⚑" }`. Solid dark-blue CTA/callout banner, white bold text. `icon` defaults to a flag; pass `"!"` for a risk/caution note.
- **paragraph** — `{ "type": "paragraph", "text": "..." }`. A plain block of body text with no box — use for a "who else is in the field" aside or similar.

Every block accepts `"gapAfter"` (inches) to override the default 0.2in gap before the next block.

## Worked example

See `references/product-example-content.json` — a full 7-slide business case (the Mintlify deck) covering every block type: cover-style card grid, twoPanel comparisons, a numbered card grid, a plain card grid, a paragraph aside, a risk banner, and a closing pillRow + banner. Rendering this file byte-for-byte reproduces the deck that was hand-verified slide by slide.

## Gathering inputs before writing the JSON

Same checklist as the legacy navy style (see `content-schema.md` → "Gathering inputs") — topic, current state, proposal, comparison, stakeholders, mechanism, numbers, why now, the ask. Don't guess numbers; ask, or research and cite sources for anything factual (pricing, security posture, customer claims) rather than inventing them.
