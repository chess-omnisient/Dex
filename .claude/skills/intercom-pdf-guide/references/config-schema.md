# Config schema for build_guide.py

Table of contents: [Top-level fields](#top-level-fields) · [Brand colors](#brand-colors) · [Block types](#block-types) · [Converting Intercom HTML to blocks](#converting-intercom-html-to-blocks)

## Top-level fields

```json
{
  "output": "Omnisient_Server_Connect_User_Manual.pdf",
  "images_dir": "images",
  "cover_pdf": "assets/covers/Cover Page SC.pdf",
  "title": "Omnisient Server Connect User Manual",
  "header_title": "Omnisient Server Connect User Manual",
  "breadcrumb": "Server Connect",
  "copyright": "© 2014-2026. Omnisient (Pty) Ltd. All rights reserved.",
  "website": "www.omnisient.com",
  "legal_url": "https://omnisient.com/privacy-center",
  "author": "Omnisient",
  "brand": { "...": "see below, optional" },
  "chapters": [ { "...": "see below" } ]
}
```

- `output` / `images_dir` — resolved relative to the config file's directory if not absolute.
- `cover_pdf` — **required**, but you'll rarely set it explicitly: if omitted, `build_guide.py` defaults to the bundled `assets/covers/Cover Page SC.pdf` template automatically, since that is the standing cover for every guide this skill produces. A single-page PDF prepended as page 1 (untouched, not re-rendered). **Never generate a cover from scratch, point this at a placeholder, or substitute a different file** — if the topic isn't "Server Connect" (the default template's baked-in topic line), use `scripts/make_cover.py replace` (see SKILL.md step 2) to swap that line to the real topic, and pass the result here instead.
- `website`, `breadcrumb`, `copyright` — optional footer content.
- `legal_url` — optional; defaults to `https://omnisient.com/privacy-center` (the standing "Legal Policies" link for every guide) if omitted. Override it only if the user explicitly gives you a different URL for that guide — never invent one yourself.
- `header_title` — defaults to `title` if omitted.
- Every chapter gets an automatic TOC entry (clickable), a PDF bookmark, and a running header/footer. Page numbers in the TOC are computed automatically via a two-pass render — you never compute or hardcode them.

## Brand colors

Optional `brand` object, RGB triplets, all optional (falls back to the Omnisient blue palette used for the Server Connect manual):

```json
{
  "blue_dark":  [#2F2E8C],
  "blue":       [#1678D1],
  "blue_light": [#B7D5F1],
  "gray_text":  [55, 58, 64],
  "gray_muted": [120, 124, 132],
  "gray_rule":  [#626973]
}
```

`blue` is used for H1s — chapter titles and the "Table of Contents" heading (same color for every H1 in the guide). `blue_dark` is used for H2s. `blue` is also used for links, rules, and TOC page numbers. `blue_light` is the fill for note callouts and link cards. Sample these from the client's actual cover/brand artwork (open it, read a few pixel values) rather than guessing — that's how the current defaults were derived from the Omnisient cover. The TOC entry list is deliberately plain: regular-weight black titles, regular-weight blue page numbers, no numbering prefixes, no divider rules between entries, no underline below the heading.

Fonts default to the bundled Poppins (`assets/fonts/Poppins-{Regular,Bold}.ttf`). Override with `font_regular` / `font_bold` (absolute paths) if the brand uses a different typeface — only regular and bold weights are used (headings bold, body regular); don't try to fake italics.

## Block types

Each chapter is `{"key": "...", "title": "...", "blocks": [...]}`. `key` is a short slug (used internally for TOC/bookmark links — not shown to the reader). Blocks render in array order, top to bottom, no exceptions.

| type | fields | notes |
|---|---|---|
| `p` | `text`, optional `bold_lead` | Paragraph. `bold_lead` bolds a leading phrase inline (e.g. "Note: ") before the regular text. |
| `h2` | `text` | Section heading within a chapter. |
| `h3` | `text` | Sub-heading. |
| `bullets` | `items` (list of str), `ordered` (bool), optional `start` (int, default 1) | Numbered (`1.`, `2.`, ...) if `ordered: true`; real bullet points (•) otherwise — never dashes. Numbering restarts at `start` (or 1) for every block — if a single numbered sequence is split across multiple `bullets` blocks (e.g. an `image` block sits between step 3 and step 4), set `start` on each later block so the count continues instead of resetting to 1. |
| `code` | `text` | Monospace block with a light-gray background. Long lines wrap automatically with a hanging indent — don't pre-wrap them yourself. |
| `note` | `text` | Callout box (light blue fill) for tips/warnings. |
| `image` | `file`, optional `caption`, optional `max_w_ratio` (default 0.85) | `file` is a filename inside `images_dir` (not a path). Auto-paginates if it won't fit on the current page. If an `image` block directly follows an `h2`/`h3` block, the renderer keeps them together — it measures both before drawing either, and pushes the heading to the next page rather than leaving it orphaned above an image that got bumped down on its own. This only looks at the block immediately after the heading, so if you want a heading to stay glued to its screenshot, put the `image` block right after the `h2`/`h3` with nothing in between. |
| `table` | `headers` (list), `rows` (list of list), optional `col_widths` (relative weights, e.g. `[30, 45, 100]`) | Auto-wraps cell text and computes row height. Rows split across pages automatically. |
| `link_card` | `title`, `url` | A bordered card with a bold title and the URL underneath, both part of one clickable region. Use for videos, external docs, anything you can't embed directly. Only use URLs you actually fetched/confirmed — never invent one. |

## Converting Intercom HTML to blocks

`get_article` returns HTML in `body.value`. There's no HTML parser bundled in this skill — read the HTML yourself and hand-author the block list, the same way the Server Connect manual was built:

- `<h1>`/`<h2>` → `h2` blocks, `<h3>`/`<h4>` → `h3`.
- `<p>` → `p` (strip tags, keep the text; drop empty `<p class="no-margin"></p>` spacers — they're just Intercom's paragraph-spacing hack, not content).
- `<ol>`/`<ul>` → `bullets` with `ordered` set accordingly.
- `<img src="...">` → download the image (see workflow in SKILL.md) and add an `image` block referencing the downloaded filename.
- `<table>` → `table`, with the header row's cells as `headers`.
- Bash/command snippets that appear as consecutive plain-text lines (Intercom articles rarely use real `<pre><code>` blocks) → a single `code` block, one line per original line.
- Duplicate sections (Intercom articles sometimes repeat a block by editing mistake) — drop the duplicate, keep one.
- Normalize stale version suffixes in product names to the current name — e.g. "Desktop Connect 2.0" and "Desktop Connect V2" (old article titles/headings from when the product was versioned) should read as plain "Desktop Connect" everywhere in the compiled guide: chapter titles, headings, body text, the cover, breadcrumb, everything. Don't touch version numbers that are part of a literal filename or command (e.g. `omnisient-desktop-connect-za-win-v2.0.8.exe`) — those are real and must stay exact.
- Preserve the source's meaning otherwise; don't add caveats or fix factual inconsistencies you notice — that's an editorial call for the article owner, not something to silently correct while compiling.
