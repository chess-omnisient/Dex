# Omnisient brand reference

The single source of truth for how Omnisient-produced documents, decks, dashboards and help content look and read. Everything here is confirmed fact, not estimation: the colours and logo were confirmed directly, and the typography and token conventions are extracted from the shipped exec reports.

Point skills, templates and new team members at this file rather than re-deriving a palette per document.

**Last updated:** 2026-10-27

---

## 1. Colour

### Core brand

| Token | Hex | Used for |
|---|---|---|
| Main blue | `#3272B9` | Eyebrow text, positive icon chips, numbered badges, primary accents, links |
| Secondary (dark) blue | `#30297E` | Titles, card titles, banner fills, platform-level items |
| Border | `#E4E7F0` | Card and panel outlines (print/deck contexts) |
| Row fill | `#F1F3FA` | Light rows inside panels, pill backgrounds |
| Subtext grey | `#6B7280` | Card descriptions, footers |

There is no third brand accent. No violet, no purple beyond the secondary blue. Where older code exposes a `violet` token it is an alias for `#30297E`, kept only so existing calls don't need renaming.

Never substitute a different blue because it "looks close". These two hexes are the brand.

### Web and dashboard tokens

Screen artifacts (dashboards, slide HTML, reports) declare the full token set on `:root`. Light values:

```css
:root{
  --font-ui:'Poppins',"Segoe UI",ui-sans-serif,system-ui,-apple-system,Helvetica,Arial,sans-serif;
  --font-data:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
  --brand:#3272B9; --brand-dark:#30297E;
  --navy-ink:#333333; --accent:#3272B9; --accent-light:#7eb3f5;
  --paper:#ffffff; --surface:#f6f8fc; --card:#ffffff; --border:#dfe4f0;
  --text:#333333; --text-muted:#5b6178; --text-faint:#8890a6;
  --good:#1f9e6d; --good-bg:#e6f6ef; --warn:#e0902e; --warn-bg:#fdf1e2;
  --bad:#d64545;  --bad-bg:#fdecec;
  --sev1:#d64545; --sev2:#e0902e; --sev3:#3272B9; --sev4:#8b7cf0; --unknown:#b7bccb;
  --backdrop:#e7e9f2; --callout-bg:#fdf6ec; --callout-br:#f0dcc0; --accent-wash:#e8eefb;
  --shadow:0 1px 3px rgba(16,20,24,.08), 0 8px 24px rgba(16,20,24,.06);
  color-scheme:light;
}
```

Dark values lighten the hues rather than reusing the light ones, so bars keep contrast on a dark ground:

```css
--navy-ink:#eef0f2; --accent:#5598e7; --accent-light:#7eb3f5;
--paper:#171b1f; --surface:#1d2228; --card:#171b1f; --border:#2b323a;
--text:#eef0f2; --text-muted:#b9c0c8; --text-faint:#8a929b;
--good:#2fbf85; --good-bg:#13261d; --warn:#f0b429; --warn-bg:#2b2310;
--bad:#ef6b6b;  --bad-bg:#2e1616;
--sev1:#ef6b6b; --sev2:#f0b429; --sev3:#5598e7; --sev4:#a79af5; --unknown:#6b737b;
--backdrop:#0f1215; --callout-bg:#2b2310; --callout-br:#4a3c18; --accent-wash:#16273b;
--shadow:0 1px 3px rgba(0,0,0,.5), 0 8px 24px rgba(0,0,0,.4);
color-scheme:dark;
```

### Client identity colours

A client's colour is permanent once assigned. It must stay identical across every edition and every report so a reader who has learned the legend is never misled.

| Client | Light | Dark |
|---|---|---|
| Shoprite | `#0f9d58` | `#2fbf6a` |
| Strive | `#16a3a3` | `#2fb8b8` |
| Absa | `#c2185b` | `#e0477f` |
| Standard Bank | `#8a6d3b` | `#b08d4e` |
| TransUnion | `#e07b39` | `#f0944c` |
| Platform (not a client) | `#30297E` | `#9085e9` |

When a new client first appears, assign a distinct colour, record it in both this table and the carry-forward comment block at the top of the report HTML, and never let it drift.

### One meaning per colour

This is the rule that most often gets broken, and it actively misleads readers.

- `--client-*` identify a client. Nothing else.
- `--sev1..4` identify a severity band. Nothing else.
- `--good` / `--warn` / `--bad` say whether a number is good or bad.

Never borrow across families. A chart of priority bands or workflow states uses judgement colours or a neutral ramp, never client or severity colours. Two adjacent charts must never use the same colour for two different meanings.

---

## 2. Typography

Two families, no third.

- **Poppins** (`--font-ui`) for all prose, headings and labels. Never Arial as a substitute in a deck.
- **IBM Plex Mono** (`--font-data`) for tabular figures only: KPI values, chart totals, durations, pill numbers. Monospace digits align down a column, which is the entire reason it is there. Don't use it for prose.

---

## 3. Logo

Use the real asset at `06-Resources/logo.png` (2000 × 532px, 3.76:1). Never hand-draw an approximation, never recreate it in shapes.

Placement in decks: top-right, 0.5in margin, default width 1.3in.

In dark mode, invert a dark-ink logo with `filter:brightness(0) invert(1)` — dark mode only, never in print.

---

## 4. Document layouts

### Decks (PPTX/PDF)

16:9, 10in × 5.625in. Every slide carries:

- a small blue uppercase eyebrow
- a bold dark-blue title below it (keep to roughly 35 characters at 22pt, or it wraps into the hairline)
- the real logo top-right
- a hairline under the header block
- a footer hairline with tagline and page number

No coloured top chrome bar. That belongs to the legacy navy style only.

Components available in `.claude/skills/business-case-custom/scripts/product-deck-lib.cjs`: `addHeader`, `addLead`, `addPanel`, `addPanelRows`, `addPillRow`, `addCardGrid`, `addBanner`, `addFooter`. Prefer the JSON-driven renderer (`build-product-deck.cjs`) over calling primitives in a one-off script.

Budget real height for wrapped text. A one-line lead sentence is about 100 characters; a second line needs roughly 0.2in extra clearance before whatever sits below it, or it collides. Always render to PNG and look before handing anything over.

Icons are simple glyphs (✓, ✕, a number) in coloured rounded-square chips, not true vector icons. That reads as clean and systematic. Don't attempt a literal icon-for-icon recreation of a reference screenshot.

### Dashboards and report HTML

Light and dark theme, always. Follow the reader's OS via `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])`, plus an explicit `:root[data-theme="dark"]` block so a pinned choice wins. Declare `color-scheme` in each.

Add a small fixed-position theme toggle that saves to `localStorage` inside a try/catch, because storage throws in private windows and the page still has to render.

**Any circulated PDF is always light.** The print block re-declares the full light palette, and the headless renderer pins `prefers-color-scheme: light` plus `data-theme="light"`. A dark deck wastes ink and reads badly projected. Hide the theme toggle in print and in the PDF render, alongside the slide nav.

### The legacy navy style

Dark panels, accent-blue chrome bar, modelled on the original Intercom Pro deck. Exists at `.claude/skills/business-case-custom/references/design-system.md`. Opt-in only, on explicit request for that specific older look. Never blend the two styles in one document.

---

## 5. Editorial conventions

### Dashes

En dashes only (–), never em dashes. This applies to every authored artifact: chat, documents, articles, HTML.

### Executive reports

- **Verdict first.** Open with the conclusion in one sentence carrying a direction, a magnitude and what is at stake for clients. Qualifications come after, never before.
- **Trend is mandatory.** Every headline KPI carries a prior-month delta, coloured by whether it is good or bad *for clients*, not by whether the number rose. More fixes shipped is up and good. More open exposure is up and bad.
- **Close with the ask.** An explicit "What we need from EXCO" block of at most 3 decisions or resource requests, each with a named owner.
- **Carry forward.** Keep a comment block at the top of the HTML holding this month's headline figures and colour assignments, so the next edition has its deltas without re-deriving them.
- **Restraint.** Charts only where shape beats text. Label bars directly rather than adding a legend. Round in headline positions, keep full precision in detail tables.
- **Squint test.** Render it and look at reduced size. The verdict, the bad numbers and the start of the detail should each be identifiable without reading a word.

### Source discipline

Reports contain only claims traceable to the sources given at the start. Never fill a gap by inference. If a user-supplied fact conflicts with the system of record, flag it rather than quietly overwriting.

### Writing style

Short headlines. One-sentence callouts. Real numbers. No filler. Don't guess factual claims such as pricing, security posture or customer references: research and cite, or ask.

### Changelog and release-facing copy

Written for a smart non-technical executive. Any word that reader would have to look up fails the entry. Words that have failed in practice: symlink, byte-for-byte, backend, repo, schema, regex, hash, daemon, env var, idempotent. Numbers are fine when they carry felt meaning ("a seven-month-old vault"), not when they are implementation detail ("~12k files").

---

## 6. Where this is implemented

| Thing | Location |
|---|---|
| Logo asset | `06-Resources/logo.png` |
| Deck design system | `.claude/skills/business-case-custom/references/product-design-system.md` |
| Deck renderer | `.claude/skills/business-case-custom/scripts/build-product-deck.cjs` |
| Deck content schema | `.claude/skills/business-case-custom/references/product-content-schema.md` |
| Legacy navy style | `.claude/skills/business-case-custom/references/design-system.md` |
| Dashboard conventions | `.claude/skills/dashboard-bugs-custom/SKILL.md` |
| Reference dashboard HTML | `Omnisient.CenterofExcellence/TechExco/TechExco_VoC_Bugs_October2026_Slides.html` |

When starting a new edition of a recurring report, copy the previous month's file forward and edit in place. Re-deriving the CSS from this document is how styling drifts.
