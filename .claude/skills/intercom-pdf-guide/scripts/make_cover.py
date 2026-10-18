#!/usr/bin/env python3
"""Edit the title block on a branded cover PDF, keeping everything else untouched.

Omnisient's cover templates draw their title as separate real vector-text runs
(one per line) on top of layered background artwork, not baked into a flat
image. That means a line can be surgically removed (revealing the background
beneath, already fully painted) and replaced, or a new line can be added
below an existing one, both without any image reconstruction.

Usage:
    python3 make_cover.py replace <template.pdf> "<old text>" "<new text>" <output.pdf> [size]
    python3 make_cover.py add-below <template.pdf> "<after text>" "<new text>" <output.pdf>

replace    finds the span matching <old text> exactly, redacts it, and inserts
           <new text> centered on the same spot.
add-below  finds the span matching <after text>, and inserts <new text> as a
           new line directly below it, same font/size/color, page-centered.
           Line spacing is inferred from the gap between <after text>'s line
           and the line above it when there is one; otherwise it defaults to
           1.2x the font size (Omnisient's own title line spacing).

Both auto-shrink the font size (down to a floor) if the text would otherwise
run past a safe margin.
"""

import os
import sys

import fitz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POPPINS_BOLD = os.path.join(SCRIPT_DIR, "..", "assets", "fonts", "Poppins-Bold.ttf")

MARGIN = 60             # pt, safe horizontal margin from each page edge
MIN_SIZE_RATIO = 0.55   # never shrink below this fraction of the reference size
DEFAULT_LINE_SPACING_RATIO = 1.2  # fallback: gap between line tops, as a multiple of font size


def _color_from_int(color_int):
    return ((color_int >> 16) & 255) / 255, ((color_int >> 8) & 255) / 255, (color_int & 255) / 255


def _all_spans(page):
    spans = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans.extend(line["spans"])
    return spans


def find_span(page, text):
    for span in _all_spans(page):
        if span["text"].strip() == text.strip():
            return span
    return None


def _fit_size(font, text, ref_size, max_width):
    min_size = ref_size * MIN_SIZE_RATIO
    fit_size = ref_size
    while fit_size > min_size and font.text_length(text, fontsize=fit_size) > max_width:
        fit_size -= 0.5
    return fit_size


def _draw_centered_line(page, font, text, size, color, center_x, top_y):
    """Insert `text`, centered on center_x, with its font-bbox top at top_y."""
    max_width = page.rect.width - 2 * MARGIN
    fit_size = _fit_size(font, text, size, max_width)
    text_width = font.text_length(text, fontsize=fit_size)
    baseline_y = top_y + font.ascender * fit_size
    origin = fitz.Point(center_x - text_width / 2, baseline_y)
    page.insert_font(fontname="CoverTitle", fontfile=POPPINS_BOLD)
    page.insert_text(origin, text, fontsize=fit_size, fontname="CoverTitle", color=color)
    if fit_size < size:
        print(f"Note: shrank font from {size:.1f}pt to {fit_size:.1f}pt to fit {text!r}.")


def _overlap_group(spans, seed):
    """All spans whose bboxes form one transitively-overlapping vertical chain with seed.

    PyMuPDF's redaction removes a whole span if the redact rect touches any
    part of its reported bbox — and this font's bbox is ascender-to-descender
    per its global metrics, not actual ink, so tightly-leaded lines report
    overlapping bboxes even when none of them visually touch (e.g. neither
    line uses its descender allowance). There's no rect that redacts one
    line's real ink without also touching a bbox-overlapping neighbor's span,
    so the only safe move is to redact every span in the whole overlapping
    chain at once and redraw all of them (changed and unchanged alike).
    """
    group = [seed]
    changed = True
    while changed:
        changed = False
        group_rect = fitz.Rect()
        for s in group:
            group_rect |= fitz.Rect(s["bbox"])
        for s in spans:
            if s in group:
                continue
            if fitz.Rect(s["bbox"]).intersects(group_rect):
                group.append(s)
                changed = True
    return group


def replace_line(template_path, old_text, new_text, output_path, uniform_size=None):
    doc = fitz.open(template_path)
    page = doc[0]

    all_spans = _all_spans(page)
    span = next((s for s in all_spans if s["text"].strip() == old_text.strip()), None)
    if span is None:
        raise ValueError(
            f"No text span matching {old_text!r} found on page 1 of {template_path}. "
            "Open the PDF and check the exact text (including capitalization)."
        )

    group = _overlap_group(all_spans, span)

    redact_rect = fitz.Rect()
    for s in group:
        redact_rect |= fitz.Rect(s["bbox"])
    page.add_redact_annot(redact_rect, fill=None)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    font = fitz.Font(fontfile=POPPINS_BOLD)
    center_x = page.rect.width / 2  # Omnisient's title lines are page-centered
    # uniform_size re-draws every line of the title group at one size, so the
    # block reads as a single consistent unit. Without it each line keeps the
    # template's own size, which leaves a long replacement line visibly smaller
    # than its neighbours after auto-shrinking to fit.
    for s in group:
        bbox = fitz.Rect(s["bbox"])
        text = new_text if s is span else s["text"]
        size = uniform_size if uniform_size else s["size"]
        _draw_centered_line(page, font, text, size, _color_from_int(s["color"]), center_x, bbox.y0)

    doc.save(output_path)
    doc.close()


def add_line_below(template_path, after_text, new_text, output_path, line_spacing=None):
    doc = fitz.open(template_path)
    page = doc[0]

    anchor = find_span(page, after_text)
    if anchor is None:
        raise ValueError(
            f"No text span matching {after_text!r} found on page 1 of {template_path}. "
            "Open the PDF and check the exact text (including capitalization)."
        )

    bbox = fitz.Rect(anchor["bbox"])
    size = anchor["size"]
    color = _color_from_int(anchor["color"])
    center_x = page.rect.width / 2  # Omnisient's title lines are centered on the page, not the anchor bbox

    if line_spacing is None:
        same_style = sorted(
            (s for s in _all_spans(page) if abs(s["size"] - size) < 0.01),
            key=lambda s: s["bbox"][1],
        )
        y_tops = [s["bbox"][1] for s in same_style]
        anchor_top = bbox.y0
        prior_tops = [y for y in y_tops if y < anchor_top - 1]
        if prior_tops:
            line_spacing = anchor_top - max(prior_tops)
        else:
            line_spacing = size * DEFAULT_LINE_SPACING_RATIO

    font = fitz.Font(fontfile=POPPINS_BOLD)
    _draw_centered_line(page, font, new_text, size, color, center_x, bbox.y0 + line_spacing)

    doc.save(output_path)
    doc.close()


def main():
    if len(sys.argv) not in (6, 7) or sys.argv[1] not in ("replace", "add-below"):
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    mode, template_path, ref_text, new_text, output_path = sys.argv[1:6]
    # Optional 6th arg: draw every line of the title block at this size.
    uniform_size = float(sys.argv[6]) if len(sys.argv) == 7 else None
    if mode == "replace":
        replace_line(template_path, ref_text, new_text, output_path, uniform_size=uniform_size)
    else:
        add_line_below(template_path, ref_text, new_text, output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()