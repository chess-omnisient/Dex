# Product design system (default)

The **default** visual language for every document this skill produces — the official Omnisient brand identity, not an estimate. Implemented in `scripts/product-deck-lib.cjs` and rendered generically via `scripts/build-product-deck.cjs` + `references/product-content-schema.md`. The older navy Intercom-Pro style (`design-system.md` / `scripts/deck-lib.cjs`) is now a legacy/alternate option — only use it if the user explicitly asks for that specific older look (e.g. references the original Intercom Pro deck by name).

## When to use which style

- **Product design system (default)** — use unless told otherwise. White background, outlined cards, brand blue/dark-blue, icon chips, pill badges. Fits both a short pitch and a denser decision paper (scene-setting, requirements, comparisons, deep dive).
- **Navy style** (legacy, opt-in only) — dark panels, accent-blue chrome bar, modeled on the original Intercom Pro deck. Use only on explicit request.

Don't blend the two styles in one document.

## Palette

The **official Omnisient brand colors** — confirmed directly by the user, not estimated from screenshots. Don't substitute other blues/purples.

| Token | Hex | Used for |
|---|---|---|
| Main blue | `3272B9` | Eyebrow text, "positive/we have" icon chips, numbered card badges, primary-side panel accent |
| Secondary (dark) blue | `30297E` | Titles, card titles, "negative/we don't have" icon chips, banner fill, comparison-side panel accent |
| Border | `E4E7F0` | Card and panel outlines |
| Row fill | `F1F3FA` | Light rows inside panels, pill backgrounds |
| Subtext gray | `6B7280` | Card descriptions, footer |

There is no third brand accent color (no violet/purple beyond the secondary blue) — `COLORS.violet` in the code is just an alias for secondary blue, kept only so calls using `tone: 'no'` don't need renaming.

Font: **Poppins**, always — never Arial.

## Logo

Use the real Omnisient logo asset at `06-Resources/logo.png` (2000×532px, aspect ratio 3.76:1) — never a hand-drawn approximation. `addLogo(slide, {w})` embeds it via `addImage`, right-aligned with a 0.5in margin, default width 1.3in. If the logo file ever moves, update `LOGO_PATH` in `product-deck-lib.cjs`.

## Layout

16:9, 10in × 5.625in.

Every slide: small blue uppercase eyebrow, bold dark-blue title below it, the real Omnisient logo top-right, a hairline under the header block, and a footer hairline + tagline + page number at the bottom. No colored top chrome bar (that's a navy-style-only element).

## Components (`product-deck-lib.cjs` exports)

- `addHeader(slide, {eyebrow, title})` — the header block described above. Keep titles short enough to stay on one line at this width (~35 characters is a safe budget at 22pt) — a wrapped title collides with the hairline.
- `addLead(slide, {text, y, h})` — one-line intro sentence under the header hairline. Budget ~100 characters to stay on one line; a second line can collide with whatever's placed right below it unless you push that content down.
- `addPanel(slide, {x,y,w,h,accent,label,icon})` — an outlined card with a colored top accent line and an icon+label header. Returns the y to start rows at.
- `addPanelRows(slide, {x,y,w,items,tone})` — stacks `addPanelRow` items (icon chip + light-gray row + text). `tone: 'check'` (main blue) or `'no'` (secondary blue).
- `addPillRow(slide, {x,y,w,pills})` — a row of equal-width pill badges, each `{label, sub, bg, text}`.
- `addCardGrid(slide, {x,y,w,cols,cards,h})` — bordered card grid; cards can have `num` (numbered circle badge), `title`, `desc`, and `tags` (small checkmark pill tags at the card's bottom).
- `addBanner(slide, {x,y,w,h,icon,text})` — solid dark-blue CTA/callout banner, white bold text.
- `addFooter(slide, {tagline, pageNum})`.

For everyday use, prefer the generic JSON-driven renderer (`build-product-deck.cjs` + `product-content-schema.md`) over calling these primitives directly in a one-off script — it's faster to iterate on and keeps every deck consistent.

## Lessons learned building the first decks in this system

- Same overflow lesson as the navy style: budget real height for wrapped text, don't trust defaults blindly, and always render to PNG and look (see SKILL.md's sanity-check step).
- Two-line lead paragraphs need extra clearance before the next element (panel top bars sit right at a fixed y — a wrapped lead sentence can visually collide with them). Either shorten the lead to one line, or add ~0.2in more y-offset to whatever comes next.
- Icons are approximated with simple glyphs in colored rounded-square chips (✓, ✕, a number) rather than true vector icons (eye, shield, gate) — PptxGenJS has no icon library, and hand-drawing bespoke icon shapes per concept isn't worth the time. This reads as "clean and systematic," not a defect — don't attempt a literal icon-for-icon recreation of a reference screenshot's iconography.
- Brand colors and the logo asset are fixed facts, not creative choices — confirm them once (as done here) and reuse, don't re-estimate per deck.
