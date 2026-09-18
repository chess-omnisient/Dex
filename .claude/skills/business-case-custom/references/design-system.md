# Design system

Extracted from `06-Resources/Intercom-Pro-Business-Case.pptx`. All values are baked into `scripts/deck-lib.cjs` – this doc is a quick-reference cheat sheet, not something you re-derive by hand.

## Palette

| Token | Hex | Used for |
|---|---|---|
| Navy | `0D1B4B` | Cover background, dark panels, headline text |
| Accent blue | `3A6FD8` | Top chrome bar, kicker labels, blue callout bars |
| Card fill | `F0F4FB` | Light card backgrounds |
| Card fill (alt) | `F6F8FC` | Table row stripe, blue callout background |
| Card border | `E4E8F2` | Card outlines, footer hairline, table borders |
| Risk fill | `FDF2F2` | Risk/caveat callout background |
| Risk accent | `B91C1C` | Risk callout bar |
| Body text | `2C2C44` | Lead paragraphs, callout text, bullet lists |
| Card body text | `475569` | Card description text |
| Footer gray | `94A3B8` | Footer text, page numbers |
| Light-on-navy | `FFFFFF` / `CFE0FF` / `DBE6FB` | Text on navy panels/cover |

## Type

Font: **Poppins** everywhere. No other font. (The original Intercom Pro reference deck used Arial; Poppins is now the Omnisient standard for every deck this skill generates going forward.)

| Element | Size | Weight |
|---|---|---|
| Cover title | 34pt | bold |
| Slide headline | 25pt | bold |
| Kicker (section label) | 11pt | bold, uppercase |
| Lead paragraph | 14.5pt | regular |
| Card title | 13pt | bold |
| Card body | 11pt | regular |
| Callout text | 11.5pt | regular |
| Footer | 8pt | regular |

## Layout

16:9, 10in × 5.625in.

Every content slide (everything after the cover) gets the same chrome, handled automatically by `addContentSlide` / `renderContentSlide`:
- Thin full-width accent-blue bar at the very top
- Small accent-blue square, top right
- Bold uppercase kicker, top left (the section name – "TODAY", "THE PROPOSAL", "THE NUMBERS", etc.)
- Bold navy headline below the kicker
- Footer hairline + "Omnisient · {topic} · Confidential" (left) + page number (right)

## Slide skeleton (narrative arc)

The reference deck's arc, in order. Not every new business case needs all ten – combine or drop sections to stay under ~15 slides, but keep the order:

1. **Cover** – deck title + one-line subtitle
2. **Today / current state** – what's true now, the problem (cards + navy panel work well)
3. **The proposal** – what you're asking for, in one paragraph + a card grid
4. **The comparison** – before vs. after (light card "today" vs. navy panel "proposed")
5. **Why it matters** – benefits by stakeholder group (2-column cards)
6. **Spotlight** – the specific product/feature being proposed, explained plainly
7. **How it works** – mechanism, in 2-3 concrete use cases (card grid)
8. **The numbers** – cost table (current vs. proposed) + included/overage-risk callouts
9. **Why now** – strategic fit, timing (bullet list)
10. **Next steps** – the concrete ask + a closing CTA banner (navy panel)

## Writing style (executive/procurement audience)

- Headlines: short, declarative, no filler ("Intercom is our support front door," not "An overview of our current support tooling")
- Lead paragraphs: 1-2 sentences max
- Card bodies: one short sentence, not a paragraph
- Callouts: exactly one "so what" sentence – the takeaway a skimming exec needs
- Use real numbers wherever possible (cost, %, time saved) – never vague adjectives
- Cut anything that doesn't change the ask or the decision
- En dashes only, never em dashes, anywhere in the deck
