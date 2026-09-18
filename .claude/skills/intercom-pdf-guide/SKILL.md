---
name: intercom-pdf-guide
description: Compile published Intercom Help Center articles about a product or topic into a single branded PDF user manual, with a cover page, an interactive clickable table of contents (accurate page numbers, PDF bookmarks), consistent running header/footer, and embedded article screenshots. Use when the user asks to turn Intercom/help-center articles into a PDF guide, user manual, or handbook — e.g. "search Intercom for articles about X and make a PDF", "compile the help center docs on Y into a manual", "build a PDF guide from our Intercom articles", or "update the [product] user manual PDF".
---

# Intercom → branded PDF guide

Turns a set of published Intercom Help Center articles into a polished, print-ready PDF manual. Built for Omnisient's Intercom workspace (help.omnisient.com) but works for any Intercom instance reachable via the `intercom` MCP tools.

## Workflow

1. **Scope the article set.** Search Intercom (`search_articles` / `list_articles`, `state: "published"`) for the topic. Group results by Intercom collection (`parent_ids`) and check tags — a keyword search casts wide and pulls in tangentially-related or even wrong-product articles (e.g. searching "Server Connect" also surfaced legacy "Desktop Connect" articles that share a collection but describe a different product). **Confirm the curated article list and chapter order with the user before fetching everything** — this is the one step worth a quick check-in, since scope mistakes here mean redoing the rest.
2. **Get the cover.** A cover page is required — always use the bundled `assets/covers/Cover Page SC.pdf` template (this is the standing default; `build_guide.py` falls back to it automatically if `cover_pdf` is omitted from the config). Don't ask the user for a different cover file or invent one — this is the one to use, every time, unless the user explicitly asks for a different cover file.
   - **Always ask the user for the exact title to put on the cover** before touching it — don't assume it matches the Intercom search phrase or the chapter list verbatim (e.g. the search topic might be "PII" but the cover title they want could be "Supported PII Types", or something else entirely). Confirm the wording, then use it for both the cover's title line and the guide's `title`/`header_title`/`breadcrumb` config fields.
   - That template's title block reads "Omnisient" / "Server Connect" / "User Manual". If the confirmed title is **not** "Server Connect", swap the middle line to it with `scripts/make_cover.py` before pointing `cover_pdf` at the result:
     ```bash
     python3 scripts/make_cover.py replace "assets/covers/Cover Page SC.pdf" "Server Connect" "<new topic text>" <output.pdf>
     ```
     This redacts just that text run (revealing the background art already painted beneath it — no image reconstruction needed) and re-draws the new topic centered in the same spot, auto-shrinking the font if it's too long to fit. Render the result to PNG and show the user before treating it as final. `make_cover.py` also has an `add-below` mode (adds a new line under an existing one, inferring line spacing automatically) for the rare case of starting from a different template that has no topic line at all — but the default template already has one, so `replace` is the normal path.
   - If the confirmed title genuinely is "Server Connect", use the bundled template as-is — no edit needed.
3. **Fetch content.** Call `get_article` for each article in the curated list. For every `<img>` in the body, download it (the Intercom CDN URL in `src` — these are signed URLs that expire, so download promptly rather than linking to them) into an `images/` folder next to the config file.
4. **Convert HTML → blocks.** Hand-convert each article's HTML into the block schema documented in [references/config-schema.md](references/config-schema.md) — headings, paragraphs, bullet lists, code snippets, tables, images, callout notes, and link cards. Read that file before writing the config; it covers all block types and the exact JSON shape. **Drop each article's "Related Articles" section** — it's Intercom navigation chrome, not manual content, and doesn't belong in the printed guide.
5. **Write `config.json`** next to an `images/` folder containing the downloaded screenshots, following [references/config-schema.md](references/config-schema.md).
6. **Render:**
   ```bash
   python3 scripts/build_guide.py config.json
   ```
   This does a two-pass render (page numbers aren't known until the content is laid out once) and merges the cover PDF in front automatically. You never compute page numbers yourself — the script does it.
7. **Visually verify before delivering.** Render each page to PNG (e.g. with PyMuPDF: `page.get_pixmap().save(...)`) and check: no text/table overflow off the page edge, images aren't stretched or cut off, the TOC page numbers match the actual chapter start pages, and the footer/header repeat correctly. This has caught real bugs before (a code block that silently rendered empty, a heading that justify-stretched into unreadable gaps) — always look, don't assume the JSON was right.
8. **Show the PDF in the chat once the run completes.** Don't just report success — render the cover, the TOC, and at least one representative content page to PNG and display them with the Read tool (same as the verification step, but shown to the user, not just checked privately) so they can see the actual result without opening the file themselves. Do this every time the skill finishes, not only on request.

## Reference

Full config schema, block types, brand-color format, and HTML→block conversion tips: [references/config-schema.md](references/config-schema.md).

## Notes

- Fonts default to the bundled Poppins (`assets/fonts/`) — regular for body text, bold for headings/emphasis. There's no italic; use color/size for de-emphasis instead (e.g. muted gray captions) rather than faking an italic style.
- Code blocks stay in a monospace font (Courier) even when the rest of the document uses a brand typeface — this is a deliberate readability exception for shell commands, not an oversight.
- The footer's "Legal Policies" link defaults to `https://omnisient.com/privacy-center` (standing default, same as the cover) — no need to ask for this one. Every other URL that ends up in the PDF (`link_card` blocks, etc.) must come from something the user gave you or a link you actually found in the fetched article content — never guess a company's URL structure.
- Re-running the script overwrites `output` in place; there's no versioning, so keep the config.json and images/ folder around if the user will want to regenerate after edits.
