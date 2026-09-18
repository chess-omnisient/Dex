from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "/Users/chess/dex/06-Resources/Knowledge/SUS_Scoring_SaaS_Fintech.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.9 * inch,
    rightMargin=0.9 * inch,
    topMargin=0.9 * inch,
    bottomMargin=0.9 * inch,
)

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#1A2B4A")
TEAL   = colors.HexColor("#0D7377")
LIGHT  = colors.HexColor("#F0F4F8")
MID    = colors.HexColor("#CBD5E0")
WHITE  = colors.white
BLACK  = colors.HexColor("#1A1A2E")

# ── Styles ───────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    fontName="Helvetica-Bold",
    fontSize=24,
    textColor=WHITE,
    alignment=TA_LEFT,
    spaceAfter=4,
)
subtitle_style = ParagraphStyle(
    "DocSubtitle",
    fontName="Helvetica",
    fontSize=11,
    textColor=colors.HexColor("#A8C5DA"),
    alignment=TA_LEFT,
)
h2 = ParagraphStyle(
    "H2",
    fontName="Helvetica-Bold",
    fontSize=13,
    textColor=NAVY,
    spaceBefore=18,
    spaceAfter=6,
    borderPad=0,
)
body = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=10,
    textColor=BLACK,
    leading=15,
    spaceAfter=6,
)
body_bold = ParagraphStyle(
    "BodyBold",
    parent=body,
    fontName="Helvetica-Bold",
)
note = ParagraphStyle(
    "Note",
    fontName="Helvetica-Oblique",
    fontSize=9,
    textColor=colors.HexColor("#555566"),
    leading=13,
    spaceAfter=4,
)
source_style = ParagraphStyle(
    "Source",
    fontName="Helvetica",
    fontSize=8.5,
    textColor=colors.HexColor("#334155"),
    leading=13,
    spaceAfter=3,
)
source_url = ParagraphStyle(
    "SourceURL",
    fontName="Helvetica-Oblique",
    fontSize=8,
    textColor=TEAL,
    leading=12,
    leftIndent=12,
    spaceAfter=6,
)
bullet_style = ParagraphStyle(
    "Bullet",
    fontName="Helvetica",
    fontSize=10,
    textColor=BLACK,
    leading=15,
    leftIndent=12,
    spaceAfter=4,
)

# ── Header block (drawn as a coloured table) ─────────────────────────────────
def header_block():
    header_data = [[
        Paragraph("SUS Scoring in SaaS Fintech", title_style),
        Paragraph("System Usability Scale — Research Brief · June 2026", subtitle_style),
    ]]
    t = Table(header_data, colWidths=[3.8 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), NAVY),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("LEFTPADDING", (0, 0), (0, 0), 18),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return t

# ── Score interpretation table ───────────────────────────────────────────────
def score_table():
    grade_colors = {
        "A+": colors.HexColor("#D4EDDA"),
        "A/B": colors.HexColor("#D4EDDA"),
        "C":  colors.HexColor("#FFF3CD"),
        "D":  colors.HexColor("#FFE0B2"),
        "F":  colors.HexColor("#F8D7DA"),
    }
    header_row = ["Score", "Grade", "What It Means"]
    rows = [
        ["90–100", "A+",  "Best in class — top 4% of all products tested"],
        ["80–89",  "A/B", "Good — users actively recommend to others"],
        ["68–79",  "C",   "Average — usable but meaningful friction exists"],
        ["55–67",  "D",   "Below average — users struggle to complete tasks"],
        ["< 55",   "F",   "Poor — significant redesign required"],
    ]

    cell_style = ParagraphStyle("TC", fontName="Helvetica", fontSize=9.5, leading=13)
    cell_bold  = ParagraphStyle("TCB", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=NAVY)
    hdr_style  = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE, leading=13)

    table_data = [[Paragraph(h, hdr_style) for h in header_row]]
    for row in rows:
        table_data.append([
            Paragraph(row[0], cell_bold),
            Paragraph(row[1], cell_bold),
            Paragraph(row[2], cell_style),
        ])

    col_widths = [1.1 * inch, 0.8 * inch, 5.4 * inch]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)

    style = [
        ("BACKGROUND",   (0, 0), (-1, 0),  TEAL),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, WHITE]),
        ("GRID",         (0, 0), (-1, -1), 0.5, MID),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("LEFTPADDING",  (0, 0), (-1, -1), 9),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]
    # Tint grade cells
    grade_map = {"A+": 0, "A/B": 1, "C": 2, "D": 3, "F": 4}
    bg_list = [
        colors.HexColor("#D4EDDA"),
        colors.HexColor("#D4EDDA"),
        colors.HexColor("#FFF3CD"),
        colors.HexColor("#FFE0B2"),
        colors.HexColor("#F8D7DA"),
    ]
    for i, bg in enumerate(bg_list):
        style.append(("BACKGROUND", (1, i + 1), (1, i + 1), bg))

    t.setStyle(TableStyle(style))
    return t

# ── Divider ──────────────────────────────────────────────────────────────────
def divider():
    return HRFlowable(width="100%", thickness=1, color=MID, spaceAfter=4, spaceBefore=4)

# ── Bullet helper ─────────────────────────────────────────────────────────────
def bullet(text):
    return Paragraph(f"<bullet>•</bullet> {text}", bullet_style)

# ── Numbered list helper ──────────────────────────────────────────────────────
def numbered_list(items):
    return ListFlowable(
        [ListItem(Paragraph(t, bullet_style), leftIndent=16, value=i + 1)
         for i, t in enumerate(items)],
        bulletType="1",
        start=1,
        leftIndent=16,
    )

# ── Build story ───────────────────────────────────────────────────────────────
story = []

story.append(header_block())
story.append(Spacer(1, 18))

# Intro
story.append(Paragraph(
    "<b>SUS</b> — the System Usability Scale — is a validated 10-question survey "
    "that produces a 0–100 score measuring perceived usability. Developed by John "
    "Brooke in 1986, it remains the industry standard: quick (~2 min to complete), "
    "validated across thousands of studies, and product-agnostic.",
    body
))

# ── How It Works ──────────────────────────────────────────────────────────────
story.append(Paragraph("How It Works", h2))
story.append(divider())
story.append(Paragraph(
    "Users rate 10 statements on a 1–5 Likert scale. Half are positively worded "
    "(<i>\"I found the system easy to use\"</i>), half are negatively worded "
    "(<i>\"I needed to learn a lot before I could use it\"</i>). "
    "The scoring formula normalises responses into a 0–100 range.",
    body
))
story.append(Paragraph(
    "Questions alternate positive/negative — this design forces deliberate reading "
    "rather than auto-filling the same answer down the column.",
    note
))
story.append(Spacer(1, 8))

# ── Score Interpretation ──────────────────────────────────────────────────────
story.append(Paragraph("Score Interpretation", h2))
story.append(divider())
story.append(score_table())
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>68 is the global average</b> across ~500 peer-reviewed studies — "
    "that's your baseline. Hitting 68 is not 'good', it's average.",
    note
))

# ── Fintech SaaS Benchmarks ───────────────────────────────────────────────────
story.append(Paragraph("What This Looks Like in Fintech SaaS", h2))
story.append(divider())
story.append(bullet(
    "<b>2025 MeasuringU business software benchmark:</b> Average SUS of <b>70.5</b> "
    "across 23 products (range 61–81). Enterprise tools with complex workflows cluster "
    "at the lower end."
))
story.append(bullet(
    "<b>SUS ↔ NPS correlation:</b> SUS &gt; 80 → promoters; 56–73 → passives; "
    "&lt; 56 → detractors. The clearest leading signal for retention risk."
))
story.append(bullet(
    "<b>Context matters:</b> A score of 65 in a multi-entity reconciliation flow is "
    "very different from 65 in a simple payments dashboard. Benchmark against "
    "comparable complexity, not the global average."
))
story.append(bullet(
    "<b>CES often predicts churn better in B2B:</b> Customer Effort Score is "
    "more predictive of churn in fintech because B2B users don't quit — they "
    "submit tickets and complain to their boss instead."
))

# ── Why Fintech Should Care ───────────────────────────────────────────────────
story.append(Paragraph("Why Fintech Specifically Should Care", h2))
story.append(divider())
story.append(numbered_list([
    "<b>Regulatory complexity creates friction.</b> Compliance flows (KYC, AML, audit "
    "trails) add steps that suppress SUS scores. Knowing <i>where</i> in those flows "
    "friction spikes is the actionable part.",
    "<b>Power users vs. new users diverge sharply.</b> CFOs and AP clerks using the "
    "same tool will give wildly different SUS scores. Segment your surveys or you'll "
    "average out meaningful signal.",
    "<b>Onboarding is the highest-leverage window.</b> First-90-day churn correlates "
    "strongly with early SUS. Running surveys at day 7 and day 30 gives an early "
    "warning system before churn appears in your MRR.",
    "<b>SUS &lt; 68 correlates with support cost spikes.</b> Lower SUS = more tickets "
    "= higher CS cost per account. This is a quantifiable P&amp;L line, not just a "
    "UX metric.",
]))

# ── How to Run It ─────────────────────────────────────────────────────────────
story.append(Paragraph("How to Run It", h2))
story.append(divider())
story.append(numbered_list([
    "Pick a key flow (e.g., invoice approval, bank reconciliation, onboarding).",
    "Send the 10-question survey <i>immediately</i> after users complete that flow.",
    "5+ responses gives you signal; 20+ gives statistical confidence.",
    "Track it quarterly — trend matters more than any single snapshot.",
    "Pair with task completion rate and time-on-task for the full picture.",
]))

# ── Quick Take ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 8))
callout_data = [[Paragraph(
    "<b>Quick Take for Product Decisions</b><br/><br/>"
    "Aim for <b>75+</b> as a product quality floor. "
    "Investigate anything below <b>68</b> as a churn risk. "
    "Treat <b>80+</b> as a usability moat worth surfacing in sales and marketing.",
    ParagraphStyle("Callout", fontName="Helvetica", fontSize=10, textColor=NAVY,
                   leading=15)
)]]
callout = Table(callout_data, colWidths=[7.3 * inch])
callout.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#EBF4F8")),
    ("LEFTPADDING",   (0, 0), (-1, -1), 16),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ("TOPPADDING",    (0, 0), (-1, -1), 14),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ("BOX",           (0, 0), (-1, -1), 1.5, TEAL),
    ("ROUNDEDCORNERS", [6]),
]))
story.append(callout)

# ── Sources ───────────────────────────────────────────────────────────────────
story.append(Spacer(1, 18))
story.append(Paragraph("Sources", h2))
story.append(divider())

sources = [
    ("Measuring Usability with the System Usability Scale (SUS) — MeasuringU",
     "https://measuringu.com/sus/"),
    ("Business Software UX & NPS Benchmarks (2025) — MeasuringU",
     "https://measuringu.com/business-software-ux-2025/"),
    ("SUS Score Benchmarks — usability.uno",
     "https://usability.uno/sus-benchmarks"),
    ("System Usability Scale (SUS) Practical Guide 2026 — UXtweak",
     "https://blog.uxtweak.com/system-usability-scale/"),
    ("Beyond the NPS: Measuring Perceived Usability — Nielsen Norman Group",
     "https://www.nngroup.com/articles/measuring-perceived-usability/"),
    ("How to Run a High Performing UX Audit for SaaS and Fintech — Arise GTM",
     "https://arisegtm.com/blog/ux-audit"),
]
for title, url in sources:
    story.append(Paragraph(f"• {title}", source_style))
    story.append(Paragraph(url, source_url))

doc.build(story)
print(f"PDF created: {OUTPUT}")
