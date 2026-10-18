#!/usr/bin/env python3
"""Convert the saved Intercom article HTML in articles/ into config.json for build_guide.py.

Downloads every <img> into images/, converts each article's HTML into the block schema
documented in the intercom-pdf-guide skill, and writes config.json next to this script.

Usage:  python3 make_config.py [--no-download]
"""
import html as htmlmod
import json
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
ARTICLES = os.path.join(HERE, "articles")
IMAGES = os.path.join(HERE, "images")
DOWNLOAD = "--no-download" not in sys.argv

# (part, [(article_id, chapter title)]) in reading order.
PARTS = [
    ("PII", [
        ("13513032", "Supported Personally Identifiable Information (PII) Types"),
    ]),
    ("Analytics tools: SQLPad, Jupyter and Power BI", [
        ("8057225", "Jupyter Notebook"),
        ("9866691", "Using Jupyter Notebook for Package Management"),
        ("11958191", "Available Packages and Libraries for Jupyter Notebook"),
        ("13229825", "How to Create a SQLPad Export"),
        ("14152998", "SQLPad Troubleshooting Guide"),
        ("15968482", "Approvals"),
        ("13230382", "Up-Skilling Guide: How to Assess SQLPad Exports with Confidence"),
        ("9127106", "Power BI Reports"),
        ("11496645", "Export Power BI Reports as PDF, PNG, or PPT"),
    ]),
]

MERGED = {
    "intro": [
        ("7135001", "A simple explanation of the Omnisient Platform"),
        ("7134996", "Technical overview"),
    ]
}

DROP_HEADINGS = re.compile(r"^\s*(related(\s+articles)?|further reading)\s*:?\s*$", re.I)

# Characters Poppins cannot draw (emoji, pictographs, dingbats, variation selectors, ZWSP).
STRIP_RE = re.compile(
    "[\U0001F000-\U0001FFFF⌀-⏿☀-➿⬀-⯿️​✓]"
)


def clean(text):
    text = text.replace("​", "").replace("\xa0", " ")
    text = text.replace("⋮", "...")  # ⋮ context-menu glyph
    text = text.replace("**", "")
    text = STRIP_RE.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "ul", "ol", "pre", "table", "tr", "tbody"}


def inline_text(el):
    """Flatten an element to text, turning <br> and block boundaries into newlines."""
    parts = []
    for c in el.children:
        if isinstance(c, NavigableString):
            parts.append(str(c))
        elif c.name == "br":
            parts.append("\n")
        elif c.name == "img":
            continue
        elif c.name == "li":
            parts.append("\n- " + inline_text(c).strip() + "\n")
        elif c.name in BLOCK_TAGS:
            parts.append("\n" + inline_text(c) + "\n")
        else:
            parts.append(inline_text(c))
    return "".join(parts)


def cell_text(td):
    raw = inline_text(td).strip()
    if re.fullmatch(r"[✅❌]\s*¹?", raw):
        raw = raw.replace("✅", "Yes").replace("❌", "No")
    return clean(raw)


def is_code_only(p):
    codes = p.find_all("code")
    if not codes:
        return False
    return clean("".join(c.get_text() for c in codes)) == clean(inline_text(p))


def p_blocks(p):
    txt = clean(inline_text(p))
    if not txt or txt == "[Screenshot]":
        return []
    if is_code_only(p):
        return [{"type": "code", "text": txt}]
    first = next((c for c in p.children if not (isinstance(c, NavigableString) and not str(c).strip())), None)
    if isinstance(first, Tag) and first.name == "b":
        lead = clean(first.get_text())
        if lead and txt.startswith(lead) and len(lead) < len(txt) - 1:
            rest = txt[len(lead):].lstrip()
            return [{"type": "p", "text": rest, "bold_lead": lead + " "}]
    return [{"type": "p", "text": txt}]


def heading_block(h):
    txt = clean(inline_text(h))
    if not txt:
        return []
    if h.name == "h4" and len(txt) > 110:
        return [{"type": "p", "text": txt}]
    return [{"type": "h2" if h.name in ("h1", "h2") else "h3", "text": txt}]


class Ctx:
    def __init__(self, aid):
        self.aid = aid
        self.img_n = 0


def image_blocks(img, ctx, caption=None, min_w=100):
    try:
        w = int(img.get("width") or 0)
    except ValueError:
        w = 0
    if w and w < min_w:
        return []
    src = htmlmod.unescape(img.get("src", ""))
    if not src:
        return []
    ctx.img_n += 1
    path = urlparse(src).path
    ext = os.path.splitext(path)[1].lower() or ".png"
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        ext = ".png"
    fname = f"{ctx.aid}_{ctx.img_n:02d}{ext}"
    dest = os.path.join(IMAGES, fname)
    if DOWNLOAD and not os.path.exists(dest):
        r = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", "-o", dest, src], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  !! download failed {fname}: {r.stderr.strip()}")
    blk = {"type": "image", "file": fname}
    if caption:
        blk["caption"] = caption
    return [blk]


def list_blocks(lst, ctx, depth=0):
    ordered = lst.name == "ol"
    try:
        start = int(lst.get("start") or 1)
    except ValueError:
        start = 1
    out, pending, n = [], [], start
    prefix = ""

    def flush():
        nonlocal pending, n
        if pending:
            blk = {"type": "bullets", "items": pending, "ordered": ordered}
            if ordered and blk_start[0] != 1:
                blk["start"] = blk_start[0]
            if depth:
                blk["indent"] = 8 * depth
            out.append(blk)
            pending = []

    blk_start = [start]
    for li in lst.find_all("li", recursive=False):
        text_parts, tail = [], []
        for c in li.children:
            if isinstance(c, NavigableString):
                if str(c).strip():
                    text_parts.append(str(c))
            elif c.name in ("ul", "ol"):
                tail.append(("list", c))
            elif c.name == "pre":
                tail.append(("code", clean(inline_text(c))))
            elif c.name == "p" and is_code_only(c):
                tail.append(("code", clean(inline_text(c))))
            elif c.name == "div" and c.find("img"):
                for img in c.find_all("img"):
                    tail.append(("img", img))
            else:
                text_parts.append(inline_text(c))
        txt = clean(" ".join(text_parts)).replace("\n", " ")
        if not pending:
            blk_start[0] = n
        if txt:
            pending.append(prefix + txt)
        n += 1
        if tail:
            flush()
            for kind, val in tail:
                if kind == "list":
                    out.extend(list_blocks(val, ctx, depth + 1))
                elif kind == "code":
                    out.append({"type": "code", "text": val})
                elif kind == "img":
                    out.extend(image_blocks(val, ctx))
    flush()
    return out


def table_blocks(table, ctx):
    rows_el = table.find_all("tr")
    if not rows_el:
        return []
    matrix, extra_imgs = [], []
    for tr in rows_el:
        cells = tr.find_all(["td", "th"], recursive=False)
        texts = []
        for td in cells:
            texts.append(cell_text(td))
            for img in td.find_all("img"):
                first = cell_text(cells[0]) if cells else None
                extra_imgs.extend(image_blocks(img, ctx, caption=first or None, min_w=100))
        matrix.append((tr, texts))
    ncols = max(len(t) for _, t in matrix)
    first_tr, first_texts = matrix[0]
    first_cells = first_tr.find_all(["td", "th"], recursive=False)
    has_bg = any("background-color" in (td.get("style") or "") for td in first_cells)
    # A header row has every cell *entirely* bold. A cell that merely contains a bold
    # phrase (e.g. a label/description row) is body content, not a header.
    def fully_bold(td):
        txt = re.sub(r"\s+", "", cell_text(td))
        if not txt:
            return True
        bold = re.sub(r"\s+", "", clean(" ".join(inline_text(b) for b in td.find_all("b"))))
        return bold == txt

    all_bold = all(fully_bold(td) for td in first_cells) and any(cell_text(td) for td in first_cells)
    is_th = any(td.name == "th" for td in first_cells)
    headers, rows = [], []
    if has_bg or is_th or all_bold:
        headers = first_texts + [""] * (ncols - len(first_texts))
        body = matrix[1:]
    else:
        body = matrix
    for _, texts in body:
        rows.append(texts + [""] * (ncols - len(texts)))
    if not rows and not headers:
        return extra_imgs
    blk = {"type": "table", "headers": headers, "rows": rows}
    if ncols == 2:
        blk["col_widths"] = [32, 68]
    elif ncols == 3:
        blk["col_widths"] = [28, 40, 32]
    elif ncols == 4 and ctx.aid == "11958191":
        blk["col_widths"] = [22, 44, 12, 22]
    return [blk] + extra_imgs


def callout_blocks(div, ctx):
    lines = []
    for c in div.children:
        if isinstance(c, NavigableString):
            if str(c).strip():
                lines.append(str(c))
        elif c.name in ("h1", "h2", "h3", "h4"):
            lines.append(clean(inline_text(c)))
        elif c.name in ("ul", "ol"):
            for i, li in enumerate(c.find_all("li", recursive=False), 1):
                marker = f"{i}. " if c.name == "ol" else "- "
                lines.append(marker + clean(inline_text(li)).replace("\n", " "))
        else:
            lines.append(inline_text(c))
    txt = clean("\n".join(lines))
    if not txt:
        return []
    return [{"type": "note", "text": txt}]


def video_blocks(div, title):
    iframe = div.find("iframe")
    if not iframe:
        return []
    src = htmlmod.unescape(iframe.get("src", ""))
    m = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]+)", src)
    url = f"https://www.youtube.com/watch?v={m.group(1)}" if m else src
    return [{"type": "link_card", "title": f"Watch the video: {title}", "url": url}]


def convert(aid, title):
    with open(os.path.join(ARTICLES, f"{aid}.html"), encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    ctx = Ctx(aid)
    blocks, skipping = [], False
    for el in soup.contents:
        if isinstance(el, NavigableString):
            continue
        name = el.name
        if name in ("h1", "h2", "h3", "h4"):
            txt = clean(inline_text(el))
            if DROP_HEADINGS.match(txt or ""):
                skipping = True
                continue
            skipping = False
            blocks.extend(heading_block(el))
            continue
        if skipping:
            continue
        if name == "p":
            blocks.extend(p_blocks(el))
        elif name in ("ul", "ol"):
            blocks.extend(list_blocks(el, ctx))
        elif name == "pre":
            blocks.append({"type": "code", "text": clean(inline_text(el))})
        elif name == "hr":
            continue
        elif name == "table":
            blocks.extend(table_blocks(el, ctx))
        elif name == "div":
            cls = " ".join(el.get("class") or [])
            if "intercom-h2b-video" in cls:
                blocks.extend(video_blocks(el, title))
            elif "intercom-interblocks-table-container" in cls:
                for t in el.find_all("table"):
                    blocks.extend(table_blocks(t, ctx))
            elif "intercom-interblocks-callout" in cls:
                blocks.extend(callout_blocks(el, ctx))
            elif el.find("img"):
                for img in el.find_all("img"):
                    blocks.extend(image_blocks(img, ctx))
            else:
                txt = clean(inline_text(el))
                if txt:
                    blocks.append({"type": "p", "text": txt})
        else:
            txt = clean(inline_text(el))
            if txt:
                blocks.append({"type": "p", "text": txt})
    # Merge consecutive code blocks separated by nothing (Intercom splits them per line sometimes).
    merged = []
    for b in blocks:
        if b["type"] == "code" and merged and merged[-1]["type"] == "code":
            merged[-1]["text"] += "\n" + b["text"]
        else:
            merged.append(b)
    return merged


def main():
    os.makedirs(IMAGES, exist_ok=True)
    chapters = []
    for part, items in PARTS:
        for aid, title in items:
            if aid in MERGED:
                blocks = []
                for sub_id, sub_title in MERGED[aid]:
                    blocks.append({"type": "h2", "text": sub_title})
                    blocks.extend(convert(sub_id, sub_title))
            else:
                blocks = convert(aid, title)
            print(f"{title:<62} {len(blocks):>3} blocks")
            chapters.append({"key": f"a{aid}", "title": title, "part": part, "blocks": blocks})

    cfg = {
        "output": "Omnisient_Platform_Guide_for_Analysts.pdf",
        "images_dir": "images",
        "cover_pdf": "cover.pdf",
        "title": "Omnisient Platform Guide for Analysts",
        "header_title": "Omnisient Platform Guide for Analysts",
        "breadcrumb": "Platform Guide for Analysts",
        "copyright": "© 2014-2026. Omnisient (Pty) Ltd. All rights reserved.",
        "website": "www.omnisient.com",
        "legal_url": "https://omnisient.com/privacy-center",
        "author": "Omnisient",
        "chapters": chapters,
    }
    with open(os.path.join(HERE, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    print(f"\nWrote config.json with {len(chapters)} chapters; images in {IMAGES}")


if __name__ == "__main__":
    main()
