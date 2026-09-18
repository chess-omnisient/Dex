---
name: business-case-custom
description: Generate an Omnisient-branded document (PPTX/PDF, 16:9) for pitching a tool, upgrade, or investment to executives and procurement, or for a decision paper — using Omnisient's product design system by default.
---

# Business case / decision paper generator

Builds a concise, motivational document for an executive/procurement audience, in Omnisient's real brand identity: brand blue/dark-blue, outlined cards, icon chips, pill badges, and the real logo.

Output: a `.pptx` (and optionally a converted `.pdf`), 16:9, max ~15 slides.

**Default style is the product design system** — see `references/product-design-system.md`. A legacy navy pitch-deck style also exists (`references/design-system.md`, modeled on the original Intercom Pro deck) — only use it if the user explicitly asks for that specific older look. Don't mix the two styles in one document.

## Process

### Step 1: Gather the business case

If the user hasn't already given you the details, ask for them (see `references/product-content-schema.md` → "Gathering inputs" for the exact list): topic, current state, the proposal, before/after comparison, stakeholders/who benefits, the product or mechanism being proposed, cost numbers (with currency), why now, and the specific ask. Don't guess factual claims (pricing, security posture, customer references) — research and cite sources, or ask.

Keep the writing style tight – see `references/product-design-system.md` (short headlines, one-sentence callouts, real numbers, no filler).

### Step 2: Write the content JSON

Read `references/product-content-schema.md` for the full block schema, and `references/product-example-content.json` for a worked 7-slide example. Write a new JSON file (in the scratchpad, or wherever you're building the deck): each slide has `eyebrow`, `title`, optional `lead`, and `blocks` (`cardGrid`, `twoPanel`, `pillRow`, `banner`, `paragraph`). Drop or merge sections that don't apply; stay under ~15 slides.

### Step 3: Check pptxgenjs is installed

```bash
node -e "require.resolve('pptxgenjs')" || npm install pptxgenjs --save
```

(It's already a project dependency – this is just a safety check.)

### Step 4: Render the deck

```bash
node .claude/skills/business-case-custom/scripts/build-product-deck.cjs <content.json> <output.pptx>
```

(For the legacy navy style only: `scripts/build-deck.cjs` with the schema in `references/content-schema.md`.)

### Step 5: Convert to PDF (optional)

```bash
soffice --headless --convert-to pdf --outdir <dir> <output.pptx>
```

### Step 6: Sanity-check the render

Before handing it back, convert every page to PNG and look at it – layout bugs (overlapping text, overflowing cards) are easy to introduce in the content JSON and easy to catch visually:

```bash
pdftoppm -png -r 120 <output.pdf> <prefix>
```

Then read the resulting PNGs. Fix any overflow by shortening text or giving the offending block an explicit `"h"` (see product-design-system.md's "Lessons learned" section — this happens often, budget for it).

### Step 7: Save and hand off

Save the final `.pptx`/`.pdf` wherever the user wants it (ask if unclear – likely `06-Resources/`, or a project folder). Don't leave working files in the scratchpad only.

## Notes

- This is a custom skill, protected from Dex updates.
- **Default style**: design system, palette, logo, and components live in `references/product-design-system.md`; content JSON schema and gathering checklist in `references/product-content-schema.md`; rendering logic in `scripts/product-deck-lib.cjs` (primitives) + `scripts/build-product-deck.cjs` (the generic renderer you run).
- **Legacy navy style** (opt-in only): `references/design-system.md`, `references/content-schema.md`, `scripts/deck-lib.cjs`, `scripts/build-deck.cjs`.
- Don't hand-edit slide positions in a one-off script; extend the relevant `*-deck-lib.cjs` if a new block type is genuinely needed, and add it to the matching content-schema doc.
