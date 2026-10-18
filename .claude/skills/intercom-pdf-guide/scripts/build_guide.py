#!/usr/bin/env python3
"""Render a branded PDF guide from a JSON config: cover + interactive TOC + chapters.

Usage:
    python3 build_guide.py <config.json>

See references/config-schema.md in this skill for the full config and block schema.
"""

import json
import os
import sys

from fpdf import FPDF
from PIL import Image
from pypdf import PdfReader, PdfWriter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FONT_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "fonts")
DEFAULT_COVER = os.path.join(SCRIPT_DIR, "..", "assets", "covers", "Cover Page SC.pdf")
DEFAULT_LEGAL_URL = "https://omnisient.com/privacy-center"

DEFAULT_BRAND = {
    "blue_dark": [24, 46, 96],
    "blue": [26, 92, 168],
    "blue_light": [232, 240, 249],
    "gray_text": [55, 58, 64],
    "gray_muted": [120, 124, 132],
    "gray_rule": [214, 218, 224],
}

_REPLACEMENTS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "—": "-", "–": "-", "•": "-", "…": "...",
    " ": " ", "‐": "-", "‑": "-", "→": "->",
}


def sanitize(text):
    if not isinstance(text, str):
        return text
    for old, new in _REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def img_size(path):
    with Image.open(path) as im:
        return im.size


class GuidePDF(FPDF):
    def __init__(self, cfg):
        super().__init__(format="A4")
        self.cfg = cfg
        brand = {**DEFAULT_BRAND, **cfg.get("brand", {})}
        self.c_blue_dark = tuple(brand["blue_dark"])
        self.c_blue = tuple(brand["blue"])
        self.c_blue_light = tuple(brand["blue_light"])
        self.c_gray_text = tuple(brand["gray_text"])
        self.c_gray_muted = tuple(brand["gray_muted"])
        self.c_gray_rule = tuple(brand["gray_rule"])

        font_dir = cfg.get("font_dir", DEFAULT_FONT_DIR)
        regular = cfg.get("font_regular", os.path.join(font_dir, "Poppins-Regular.ttf"))
        bold = cfg.get("font_bold", os.path.join(font_dir, "Poppins-Bold.ttf"))
        self.add_font("Body", "", regular)
        self.add_font("Body", "B", bold)

        self.set_auto_page_break(auto=True, margin=28)
        self.set_margins(18, 20, 18)
        self.current_chapter = ""
        self.toc_links = {}
        self.chapter_pages = {}
        self.page_offset = 1  # one cover page is always prepended after generation

    # ---- auto-sanitize text passed through fpdf's text-rendering calls ----
    def cell(self, *args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = sanitize(kwargs["text"])
        elif len(args) >= 3:
            args = list(args)
            args[2] = sanitize(args[2])
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = sanitize(kwargs["text"])
        elif len(args) >= 3:
            args = list(args)
            args[2] = sanitize(args[2])
        return super().multi_cell(*args, **kwargs)

    def write(self, *args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = sanitize(kwargs["text"])
        elif len(args) >= 2:
            args = list(args)
            args[1] = sanitize(args[1])
        return super().write(*args, **kwargs)

    # ---- running header / footer ----
    def header(self):
        if self.cfg.get("include_toc", True) and self.page_no() == 1:
            return  # TOC page has its own title treatment
        self.set_font("Body", "", 8)
        self.set_text_color(*self.c_gray_muted)
        self.set_y(10)
        self.cell(0, 6, self.cfg.get("header_title", self.cfg["title"]), align="L")
        self.set_y(10)
        self.cell(0, 6, self.current_chapter, align="R")
        self.set_draw_color(*self.c_gray_rule)
        self.set_line_width(0.3)
        self.line(18, 17, 192, 17)
        self.set_y(22)

    def footer(self):
        self.set_draw_color(*self.c_gray_rule)
        self.set_line_width(0.2)
        self.line(18, 279, 192, 279)
        self.set_font("Body", "", 7.2)
        toc_link = self.toc_links.get("__toc__")
        left = "Table of Contents"
        prefix = sanitize(
            f"{self.cfg.get('copyright', '')}  -  {self.cfg.get('website', '')}  -  "
        )
        legal_text = "Legal Policies"
        legal_url = self.cfg.get("legal_url", DEFAULT_LEGAL_URL)
        show_breadcrumb = self.page_no() > 1 and self.cfg.get("include_toc", True)
        right = self.cfg.get("breadcrumb", "") if show_breadcrumb else ""
        w = self.w - 36
        y = 281
        # Optional back-link to the TOC in the footer's left slot. Set
        # "footer_toc_link": false in the config to drop it entirely.
        show_toc_link = self.cfg.get("include_toc", True) and self.cfg.get("footer_toc_link", True)
        self.set_xy(18, y)
        if not show_toc_link:
            pass  # footer's left slot is unused
        elif toc_link is not None and self.page_no() > 1:
            self.set_text_color(*self.c_blue)
            self.cell(35, 5, left, link=toc_link)
        else:
            self.set_text_color(*self.c_gray_muted)
            self.cell(35, 5, left)
        # Fit the centred copyright/legal block between the TOC link and the breadcrumb:
        # shrink the footer font a little if needed, and drop the breadcrumb if it still won't fit.
        span_l = (18 + 35 + 2) if show_toc_link else 18   # after the TOC link, if shown
        for size in (7.2, 6.8, 6.4, 6.0):
            self.set_font("Body", "", size)
            prefix_w = self.get_string_width(prefix)
            legal_w = self.get_string_width(legal_text)
            right_w = self.get_string_width(right) if right else 0
            span_r = 18 + w - right_w - 3    # before the right-aligned breadcrumb
            if prefix_w + legal_w <= span_r - span_l:
                break
        else:
            right, right_w = "", 0
            span_r = 18 + w
        # Position the copyright/legal block. With a TOC link present, space the
        # three groups evenly (equal gaps either side of the block) — centring it
        # looks lopsided whenever the left and right items differ in width. With
        # no TOC link, centre the block on the page and let the breadcrumb sit
        # right-aligned, which is the conventional two-element footer.
        # Position the copyright/legal block.
        #
        # With a TOC link in the left slot, three groups share the footer, so
        # split the free space between the two fixed neighbours evenly.
        #
        # Without it there are only two groups, and the conventional layout is a
        # page-centred block with the breadcrumb right-aligned. Centring on the
        # leftover span instead would leave visibly lopsided gaps, because that
        # span excludes the breadcrumb's width on the right but has no
        # equivalent item on the left. Fall back to span-centring only if a
        # page-centred block would actually collide with a neighbour.
        block_w = prefix_w + legal_w
        if show_toc_link:
            start_x = span_l + (span_r - span_l - block_w) / 2
        else:
            page_centre_x = 18 + w / 2 - block_w / 2
            if page_centre_x >= span_l and page_centre_x + block_w <= span_r:
                start_x = page_centre_x
            else:
                start_x = span_l + (span_r - span_l - block_w) / 2
        start_x = max(start_x, span_l)
        self.set_xy(start_x, y)
        self.set_text_color(*self.c_gray_muted)
        self.cell(prefix_w, 5, prefix)
        if legal_url:
            self.set_text_color(*self.c_blue)
            self.cell(legal_w, 5, legal_text, link=legal_url)
        else:
            self.cell(legal_w, 5, legal_text)
        self.set_text_color(*self.c_gray_muted)
        self.set_xy(18, y)
        self.cell(w, 5, right, align="R")
        self.set_y(287)
        self.set_font("Body", "", 8)
        self.cell(0, 5, str(self.page_no() + self.page_offset), align="C")

    # ---- block primitives ----
    def start_chapter(self, key, title):
        self.current_chapter = title
        self.add_page()
        self.chapter_pages[key] = self.page_no()
        link = self.toc_links.get(key)
        if link is not None:
            self.set_link(link, page=self.page_no())
        self.start_section(title)
        self.set_font("Body", "B", 19)
        self.set_text_color(*self.c_blue)
        self.multi_cell(0, 9, title, align="L")
        self.ln(7)

    def _continue_on_new_page(self):
        # Continuation pages reuse the chapter's running header (drawn from
        # self.current_chapter), so they must NOT call start_section again —
        # that would add a duplicate PDF bookmark for every overflow page.
        self.add_page()

    def b_h2(self, text):
        self.ln(1)
        self.set_font("Body", "B", 13)
        self.set_text_color(*self.c_blue_dark)
        self.multi_cell(0, 7, text, align="L")
        self.ln(1.5)

    def b_h3(self, text):
        self.set_font("Body", "B", 11)
        self.set_text_color(*self.c_gray_text)
        self.multi_cell(0, 6, text, align="L")
        self.ln(1)

    def b_p(self, text, bold_lead=None):
        self.set_font("Body", "", 10.3)
        self.set_text_color(*self.c_gray_text)
        if bold_lead:
            self.set_font("Body", "B", 10.3)
            self.write(5.6, bold_lead)
            self.set_font("Body", "", 10.3)
            self.write(5.6, text)
            self.ln(7)
        else:
            self.multi_cell(0, 5.6, text, align="L")
        self.ln(1.5)

    def b_bullets(self, items, ordered=False, start=1, indent=0):
        self.set_font("Body", "", 10.3)
        self.set_text_color(*self.c_gray_text)
        for i, item in enumerate(items, start):
            marker = f"{i}." if ordered else ("–" if indent else "•")
            x0 = self.get_x() + indent
            self.set_x(x0 + 4)
            # bypass the sanitize-wrapped cell() so the bullet glyph survives
            FPDF.cell(self, 6, 5.6, marker)
            self.set_x(x0 + 10)
            self.multi_cell(self.w - self.r_margin - x0 - 10, 5.6, item, align="L")
            self.ln(0.5)
        self.ln(1.5)

    def b_code(self, text):
        self.set_font("Courier", "", 8.6)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(244, 245, 247)
        self.set_draw_color(*self.c_gray_rule)
        box_w = self.w - self.l_margin - self.r_margin
        avail_w = box_w - 6
        raw_lines = text.strip("\n").split("\n")
        lines = []
        for raw in raw_lines:
            if not raw or self.get_string_width(raw) <= avail_w:
                lines.append(raw)
                continue
            words = raw.split(" ")
            cur = ""
            for word in words:
                trial = f"{cur} {word}".strip() if cur else word
                if self.get_string_width("  " + trial) <= avail_w:
                    cur = trial
                else:
                    if cur:
                        lines.append(cur)
                    cur = "  " + word
            if cur:
                lines.append(cur)
        x, y = self.get_x(), self.get_y()
        h = 4.6 * len(lines) + 4
        if y + h > 270:
            self._continue_on_new_page()
            x, y = self.get_x(), self.get_y()
        self.rect(x, y, box_w, h, style="DF")
        self.set_xy(x + 3, y + 2.2)
        for line in lines:
            self.set_x(x + 3)
            self.cell(0, 4.6, line, new_x="LMARGIN", new_y="NEXT")
        self.set_xy(x, y + h + 3)

    def b_note(self, text):
        self.set_font("Body", "", 9.6)
        x, y = self.get_x(), self.get_y()
        w = self.w - self.l_margin - self.r_margin
        lines = self.multi_cell(w - 8, 5.2, text, align="L", dry_run=True, output="LINES")
        h = 5.2 * len(lines) + 6
        if y + h > 270:
            self._continue_on_new_page()
            x, y = self.get_x(), self.get_y()
        self.set_fill_color(*self.c_blue_light)
        self.rect(x, y, w, h, style="F")
        self.set_text_color(*self.c_gray_text)
        self.set_xy(x + 4, y + 3)
        self.multi_cell(w - 8, 5.2, text, align="L")
        self.set_xy(x, y + h + 3)

    def _image_fit(self, path, max_w_ratio):
        """Compute the on-page (w, h) an image will render at, without drawing it."""
        iw, ih = img_size(path)
        avail_w = (self.w - self.l_margin - self.r_margin) * max_w_ratio
        w = avail_w
        h = w * ih / iw
        max_h = 95
        if h > max_h:
            h = max_h
            w = h * iw / ih
        return w, h

    def _image_block_height(self, path, caption, max_w_ratio):
        """Total vertical space b_image will consume for this image, border/caption included."""
        _, h = self._image_fit(path, max_w_ratio)
        return (h + 2) + (11 if caption else 4)

    def _heading_height(self, text, level):
        """Total vertical space a b_h2/b_h3 call will consume, without drawing it."""
        if level == 2:
            self.set_font("Body", "B", 13)
            line_h, pre, post = 7, 1, 1.5
        else:
            self.set_font("Body", "B", 11)
            line_h, pre, post = 6, 0, 1
        lines = self.multi_cell(0, line_h, text, align="L", dry_run=True, output="LINES")
        return pre + line_h * len(lines) + post

    def b_image(self, path, caption=None, max_w_ratio=0.85):
        w, h = self._image_fit(path, max_w_ratio)
        if self.get_y() + h > 268:
            self._continue_on_new_page()
        x = self.l_margin + (self.w - self.l_margin - self.r_margin - w) / 2
        self.set_draw_color(*self.c_gray_rule)
        self.rect(x - 1, self.get_y() - 1, w + 2, h + 2)
        self.image(path, x=x, y=self.get_y(), w=w, h=h)
        self.set_y(self.get_y() + h + 2)
        if caption:
            self.set_font("Body", "", 8.3)
            self.set_text_color(*self.c_gray_muted)
            self.cell(0, 5, caption, align="C")
            self.ln(6)
        else:
            self.ln(4)

    def _table_head_height(self, headers, rows, col_widths=None):
        """Vertical space the header row plus the first body row will take, without drawing."""
        self.set_font("Body", "", 8.6)
        avail = self.w - self.l_margin - self.r_margin
        n = len(headers) if headers else max(len(r) for r in rows)
        if col_widths:
            widths = [avail * (w / sum(col_widths)) for w in col_widths]
        else:
            widths = [avail / n] * n
        total = 0
        for cells in ([headers] if headers else []) + rows[:1]:
            h = 5.2
            for i, c in enumerate(cells):
                lines = self.multi_cell(widths[i] - 4, 4.6, c, dry_run=True, output="LINES")
                h = max(h, len(lines) * 4.6 + 2.6)
            total += h
        return total

    def b_table(self, headers, rows, col_widths=None):
        self.set_font("Body", "", 8.6)
        avail = self.w - self.l_margin - self.r_margin
        n = len(headers) if headers else max(len(r) for r in rows)
        if col_widths:
            widths = [avail * (w / sum(col_widths)) for w in col_widths]
        else:
            widths = [avail / n] * n

        def row_height(cells):
            h = 5.2
            for i, c in enumerate(cells):
                w = widths[i] - 4
                lines = self.multi_cell(w, 4.6, c, dry_run=True, output="LINES")
                h = max(h, len(lines) * 4.6 + 2.6)
            return h

        def draw_row(cells, is_header=False):
            h = row_height(cells)
            if self.get_y() + h > 270:
                self._continue_on_new_page()
            x0, y0 = self.get_x(), self.get_y()
            self.set_fill_color(*(self.c_blue_light if is_header else (255, 255, 255)))
            self.set_draw_color(*self.c_gray_rule)
            x = x0
            for w in widths:
                self.rect(x, y0, w, h, style="DF")
                x += w
            x = x0
            for i, c in enumerate(cells):
                self.set_xy(x + 2, y0 + 1.3)
                self.set_font("Body", "B" if is_header else "", 8.6)
                self.set_text_color(*(self.c_blue_dark if is_header else self.c_gray_text))
                self.multi_cell(widths[i] - 4, 4.6, c, align="L")
                x += widths[i]
            self.set_xy(x0, y0 + h)

        if headers:
            # Keep the header row together with the first body row.
            need = row_height(headers) + (row_height(rows[0]) if rows else 0)
            if self.get_y() + need > 270:
                self._continue_on_new_page()
            draw_row(headers, is_header=True)
        for r in rows:
            draw_row(r)
        self.ln(3)

    def b_link_card(self, title, url):
        if self.get_y() + 17 > 268:
            self._continue_on_new_page()
        self.set_font("Body", "B", 10.3)
        self.set_text_color(*self.c_blue)
        x, y = self.get_x(), self.get_y()
        w = self.w - self.l_margin - self.r_margin
        self.set_fill_color(*self.c_blue_light)
        self.rect(x, y, w, 14, style="F")
        self.set_xy(x + 4, y + 3)
        self.cell(0, 5, title)
        self.set_xy(x + 4, y + 8.5)
        self.set_font("Body", "", 9)
        self.set_text_color(*self.c_gray_muted)
        self.cell(0, 4.5, url, link=url)
        self.set_xy(x, y + 17)


BLOCK_HANDLERS = {
    "h2": lambda pdf, b: pdf.b_h2(b["text"]),
    "h3": lambda pdf, b: pdf.b_h3(b["text"]),
    "p": lambda pdf, b: pdf.b_p(b["text"], bold_lead=b.get("bold_lead")),
    "bullets": lambda pdf, b: pdf.b_bullets(
        b["items"], ordered=b.get("ordered", False), start=b.get("start", 1), indent=b.get("indent", 0)
    ),
    "code": lambda pdf, b: pdf.b_code(b["text"]),
    "note": lambda pdf, b: pdf.b_note(b["text"]),
    "image": lambda pdf, b: pdf.b_image(
        os.path.join(pdf.cfg["images_dir"], b["file"]),
        caption=b.get("caption"),
        max_w_ratio=b.get("max_w_ratio", 0.85),
    ),
    "table": lambda pdf, b: pdf.b_table(b["headers"], b["rows"], col_widths=b.get("col_widths")),
    "link_card": lambda pdf, b: pdf.b_link_card(b["title"], b["url"]),
}


def render_chapter(pdf, chapter):
    pdf.start_chapter(chapter["key"], chapter["title"])
    blocks = chapter["blocks"]
    for i, block in enumerate(blocks):
        # Keep a heading on the same page as the image right below it — otherwise
        # the heading can end up orphaned at the bottom of a page while its image
        # gets pushed to the top of the next one.
        if block["type"] in ("h2", "h3") and i + 1 < len(blocks) and blocks[i + 1]["type"] == "image":
            next_block = blocks[i + 1]
            heading_h = pdf._heading_height(block["text"], level=2 if block["type"] == "h2" else 3)
            image_path = os.path.join(pdf.cfg["images_dir"], next_block["file"])
            image_h = pdf._image_block_height(
                image_path, next_block.get("caption"), next_block.get("max_w_ratio", 0.85)
            )
            if pdf.get_y() + heading_h + image_h > 268:
                pdf._continue_on_new_page()
        elif block["type"] in ("h2", "h3") and i + 1 < len(blocks):
            # Don't leave a heading stranded at the foot of a page with its content on the next one.
            heading_h = pdf._heading_height(block["text"], level=2 if block["type"] == "h2" else 3)
            next_block = blocks[i + 1]
            need = 18
            if next_block["type"] == "table":
                need = pdf._table_head_height(
                    next_block["headers"], next_block["rows"], next_block.get("col_widths")
                ) + 2
            if pdf.get_y() + heading_h + need > 268:
                pdf._continue_on_new_page()
        BLOCK_HANDLERS[block["type"]](pdf, block)


def build(cfg, with_real_page_numbers, page_map=None):
    pdf = GuidePDF(cfg)
    pdf.set_creator(cfg.get("author", ""))
    pdf.set_title(cfg["title"])
    pdf.set_author(cfg.get("author", ""))

    include_toc = cfg.get("include_toc", True)

    if include_toc:
        pdf.toc_links["__toc__"] = pdf.add_link(page=1)
    for ch in cfg["chapters"]:
        pdf.toc_links[ch["key"]] = pdf.add_link(page=1)

    if include_toc:
        pdf.add_page()
        pdf.set_link(pdf.toc_links["__toc__"], page=pdf.page_no())
        pdf.current_chapter = "Table of Contents"
        pdf.set_font("Body", "B", 22)
        pdf.set_text_color(*pdf.c_blue)
        pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

        has_parts = any(ch.get("part") for ch in cfg["chapters"])
        row_h = 7.4 if has_parts else 8.5
        last_part = None
        for ch in cfg["chapters"]:
            part = ch.get("part")
            if has_parts and part != last_part:
                if pdf.get_y() + 3 + row_h * 3 > 270:
                    pdf.add_page()
                pdf.ln(3 if last_part is not None else 0)
                pdf.set_font("Body", "B", 11)
                pdf.set_text_color(*pdf.c_blue_dark)
                pdf.cell(0, row_h, part or "", new_x="LMARGIN", new_y="NEXT")
                last_part = part
            page_label = "  " if not with_real_page_numbers else str(page_map[ch["key"]] + pdf.page_offset)
            if pdf.get_y() + row_h > 272:
                pdf.add_page()
            indent = 6 if has_parts else 0
            pdf.set_x(pdf.l_margin + indent)
            pdf.set_font("Body", "", 10.5 if has_parts else 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(150 - indent, row_h, ch["title"], link=pdf.toc_links[ch["key"]])
            pdf.set_font("Body", "", 10.5 if has_parts else 11)
            pdf.set_text_color(*pdf.c_blue)
            pdf.cell(0, row_h, page_label, align="R", link=pdf.toc_links[ch["key"]])
            pdf.ln(row_h)

    for ch in cfg["chapters"]:
        render_chapter(pdf, ch)

    return pdf


def main():
    if len(sys.argv) != 2:
        print("Usage: build_guide.py <config.json>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path) as f:
        cfg = json.load(f)

    if not cfg.get("cover_pdf"):
        cfg["cover_pdf"] = DEFAULT_COVER
        print(f"No cover_pdf specified — defaulting to the standard cover template: {DEFAULT_COVER}")

    config_dir = os.path.dirname(os.path.abspath(config_path))
    if not os.path.isabs(cfg["images_dir"]):
        cfg["images_dir"] = os.path.join(config_dir, cfg["images_dir"])
    if not os.path.isabs(cfg["output"]):
        cfg["output"] = os.path.join(config_dir, cfg["output"])
    if not os.path.isabs(cfg["cover_pdf"]):
        cfg["cover_pdf"] = os.path.join(config_dir, cfg["cover_pdf"])

    # Pass 1: measure where each chapter lands.
    measure_pdf = build(cfg, with_real_page_numbers=False)
    page_map = dict(measure_pdf.chapter_pages)

    # Pass 2: render again with the real page numbers baked into the TOC.
    final_pdf = build(cfg, with_real_page_numbers=True, page_map=page_map)
    content_path = cfg["output"] + ".content.tmp.pdf"
    final_pdf.output(content_path)

    writer = PdfWriter()
    writer.append(PdfReader(cfg["cover_pdf"]))
    writer.append(PdfReader(content_path))
    with open(cfg["output"], "wb") as f:
        writer.write(f)
    os.remove(content_path)

    print("Chapters and their final page numbers:")
    for ch in cfg["chapters"]:
        print(f"  {ch['title']:<55} p.{page_map[ch['key']] + 1}")
    print(f"\nTotal pages: {len(PdfReader(cfg['output']).pages)}")
    print(f"Saved: {cfg['output']}")


if __name__ == "__main__":
    main()
