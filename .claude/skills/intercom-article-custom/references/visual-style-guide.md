# Visual style guide

Derived from five published Help Center articles: Build, Save, and Export Selections with Ease; Selection Builder; Jupyter Notebook; Project Templates; User Management. Four open inconsistencies found across the corpus were resolved below — those decisions are final and apply to all new articles.

---

## Callouts

Four colors, each tied to one purpose. Don't mix purposes within a color.

| Color | Hex | Emoji | Use for |
|---|---|---|---|
| Amber | bg `#feedaf80` | ⚠️ | Warnings only — missing prerequisites, troubleshooting, "this will get declined" |
| Red/pink | bg `#fed9db80` | ⚠️ | Irreversible or destructive actions ("Deactivation can't be undone") |
| Blue/indigo | bg `#e3e7fa80`| 💡 or 🚀 | Tips, clarifications, edge cases, definitions, or a notable/higher-tier feature |
| Gray | bg `#e8e8e880` | none, or bold "**Note:**" | Lower-stakes asides, cross-references to a related feature |

**Resolved:** amber is warnings only. Plain notes and definitions (e.g. "Role: each user is either a User or an Admin") go in a blue callout, not amber — even though one live article puts them in amber.


---

## Emoji

**Resolved:** use this set. Don't use 📌, ✨, or 🎉 — none of the live corpus uses them, and the skill's older rule that restricted emoji to 📌 no longer reflects actual practice.

| Emoji | Use |
|---|---|
| ⚠️ | Warning or destructive-action callouts only |
| 💡 | Tips, either inside a blue callout or inline in body text |
| 🚀 | Flags a new or higher-tier feature, inside a callout |
| 👉 | Inline pointer immediately before a "Learn more" / "See [X] article" link — never inside a callout |
| ✅ / ❌ | Table cells only, as explicit boolean indicators |

---

## Tables

- Border color `#c6c9c0` everywhere, `border-radius: 6px`, `border-collapse: separate; border-spacing: 0`
- Header row: `#e8e8e880` gray, bold header text
- Two-column glossary tables (term/definition):
- Boolean/status columns: center the cell (`class="intercom-align-center"`)

**Resolved:** always use explicit ❌ for "not applicable" or "no access." Never leave the cell blank — a blank cell is ambiguous between "no" and "not filled in yet."

Annotate a ✅ with a short parenthetical when access is conditional, e.g. "✅ (project owner)," "✅ (if assigned)."

---

## Headers

- H1 for major sections, H2 for subsections, H3 for granular breakdowns within a subsection
- Every heading gets an anchor ID (Intercom generates `h_xxxx` automatically) so other articles and in-page links can deep-link to it
- Flat hierarchy (H1 → H2, no H3) is fine for reference/matrix-style articles; go to H3 only when a subsection itself has multiple distinct breakdowns (e.g. operator tables by data type)


---

## Bullets and text

- Unordered lists for non-sequential items (requirements, options)
- Ordered lists for sequential steps
- Bold lead-in terms inside bullets before the explanation (e.g. "**Add Rule** lets you add another condition...")
- Bold for UI element names, button labels, and terms being defined — not for rhetorical emphasis
- `<code>` for inline commands, filenames, and placeholders; `<pre><code>` for multi-line snippets
- Navigation breadcrumbs written inline and bolded, with a real arrow: "**Admin → Users**," not spelled out in prose

---

## Layout

- Open with 1–3 short intro paragraphs (no heading), closing on a phrase that sets up the rest of the article
- Where to find with steps and a screenshot of the navigation
- Screenshots sit directly under the heading they support / below the content (decision to be made)
- Screenshot sizing should match intent: large full-width captures (1390–2085px) for "here's the whole screen" conceptual explanations; small, tightly-cropped captures (~230–870px) for "here's the specific button" procedural steps
- Mixing a short numbered how-to section with a longer reference/matrix section in the same article is fine when the topic genuinely needs both (see User Management)

---

## Annotation toolkit

Source: `article-writing-2026-08-24` skill's `image-usage-in-help-articles.md`. Carried over here so it's documented in the skill actually used for Intercom articles.

Fixed set of tools for drawing attention within a screenshot. Pick whichever fits the moment, but apply it the same way every time it appears in a given article — don't mix blur and highlight border for the same kind of callout within one article.

| Tool | Use when |
|---|---|
| **Blur** | De-focuses the UI around a specific element to draw the eye there. Emphasis only — never redaction. Never rely on blur or mosaic to hide real PII; it's reversible. Fake the data before capture instead. |
| **Numbered circles** | A screenshot has several distinct elements to call out individually, each described in the surrounding text. Primary blue ramp (Light/Normal/Dark); vary the shade across badges in the same image. |
| **Highlight border** | Drawing the eye to one specific action or function — more visually assertive than blur. Well suited to step-by-step articles calling out one thing at a time. Spec: 2px solid `#FF0000`, 5px rounded corners. |

**Every image** (screenshot or diagram): export as PNG at 2x resolution, 1px solid border in Gray03 (`#DBDCDD`), 5px rounded corners. Build from dummy/sandboxed data, never real platform data — this removes redaction as a step entirely since nothing real is ever in frame.