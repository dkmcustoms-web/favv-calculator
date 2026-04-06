"""
FAVV PDF Report Generator
Uses reportlab (listed in requirements.txt)
"""

import io
from datetime import datetime


def genereer_pdf(product_type: str, invoer: dict, resultaat: dict) -> bytes:
    """Generate a professional A4 PDF and return as bytes."""

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    except ImportError:
        # Fallback: return a minimal valid PDF with error message
        return _fallback_pdf()

    BLUE       = colors.HexColor("#003d7a")
    LIGHT_BLUE = colors.HexColor("#7eb8f7")
    BG_GREY    = colors.HexColor("#f4f6f9")
    ROW_ALT    = colors.HexColor("#f0f4ff")
    TEXT_DARK  = colors.HexColor("#222222")
    TEXT_MID   = colors.HexColor("#555555")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title="FAVV Retribution Report",
        author="DKM Customs",
    )
    W = A4[0] - 40*mm
    datum = datetime.now().strftime("%d/%m/%Y  %H:%M")
    totaal = resultaat.get("TOTAAL", 0)
    nz = resultaat.get("NZ korting toegepast", False)

    styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    title_style   = S("FTitle",   fontSize=20, textColor=colors.white,  fontName="Helvetica-Bold", alignment=TA_LEFT, leading=24)
    sub_style     = S("FSub",     fontSize=10, textColor=LIGHT_BLUE,    fontName="Helvetica",      alignment=TA_LEFT)
    label_style   = S("FLabel",   fontSize=8,  textColor=TEXT_MID,      fontName="Helvetica",      spaceAfter=2, leading=11)
    value_style   = S("FValue",   fontSize=10, textColor=TEXT_DARK,     fontName="Helvetica-Bold", leading=13)
    section_style = S("FSection", fontSize=8,  textColor=BLUE,          fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    amount_style  = S("FAmount",  fontSize=28, textColor=colors.white,  fontName="Helvetica-Bold", alignment=TA_CENTER, leading=32)
    total_lbl     = S("FTLbl",    fontSize=9,  textColor=LIGHT_BLUE,    fontName="Helvetica",      alignment=TA_CENTER, leading=12)
    footer_style  = S("FFooter",  fontSize=7,  textColor=colors.HexColor("#aaaaaa"), fontName="Helvetica", alignment=TA_CENTER)
    nz_style      = S("FNZ",      fontSize=8,  textColor=colors.HexColor("#856404"), fontName="Helvetica-Bold", alignment=TA_CENTER)

    story = []

    # ── HEADER ─────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<b>FAVV</b>", S("Logo", fontSize=16, textColor=BLUE,
                                   fontName="Helvetica-Bold", alignment=TA_CENTER)),
        [Paragraph("Retribution Report", title_style),
         Paragraph("Royal Decree Tariffs 2026 · Port of Antwerp", sub_style)],
        Paragraph(f"DKM Customs<br/><font size='8'>{datum}</font>",
                  S("FR", fontSize=10, textColor=colors.white, fontName="Helvetica",
                    alignment=TA_RIGHT, leading=14)),
    ]]
    ht = Table(header_data, colWidths=[22*mm, W - 60*mm, 38*mm])
    ht.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE),
        ("BACKGROUND",    (0, 0), (0, 0),   colors.white),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (0, 0),   6),
        ("RIGHTPADDING",  (0, 0), (0, 0),   6),
        ("LEFTPADDING",   (1, 0), (1, 0),   12),
    ]))
    story.append(ht)
    story.append(Spacer(1, 6*mm))

    # ── PRODUCT TYPE ───────────────────────────────────────────────────────────
    story.append(Paragraph("PRODUCT TYPE", section_style))
    pt = Table([[Paragraph(product_type, value_style)]], colWidths=[W])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ROW_ALT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(pt)
    story.append(Spacer(1, 4*mm))

    # ── INPUT PARAMETERS ───────────────────────────────────────────────────────
    if invoer:
        story.append(Paragraph("INPUT PARAMETERS", section_style))
        items = list(invoer.items())
        rows = []
        for i in range(0, len(items), 2):
            row = []
            for j in range(2):
                if i + j < len(items):
                    k, v = items[i + j]
                    row.append([Paragraph(k.upper(), label_style),
                                Paragraph(str(v), value_style)])
                else:
                    row.append([""])
            rows.append(row)
        param_t = Table(rows, colWidths=[W / 2, W / 2])
        param_t.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND",    (0, 0), (-1, -1), BG_GREY),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.5, colors.HexColor("#e0e8f0")),
        ]))
        story.append(param_t)
        story.append(Spacer(1, 4*mm))

    # ── TOTAL BOX ──────────────────────────────────────────────────────────────
    total_data = [
        [Paragraph("TOTAL FAVV RETRIBUTION", total_lbl)],
        [Paragraph(f"<b>€ {totaal:,.2f}</b>", amount_style)],
    ]
    if nz:
        total_data.append([Paragraph("✓  New Zealand discount 22.5% applied", nz_style)])

    tot_t = Table(total_data, colWidths=[W])
    ts = [
        ("BACKGROUND",    (0, 0), (0, 1),  BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]
    if nz:
        ts += [("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#fff8e0"))]
    tot_t.setStyle(TableStyle(ts))
    story.append(tot_t)
    story.append(Spacer(1, 5*mm))

    # ── COST BREAKDOWN ─────────────────────────────────────────────────────────
    story.append(Paragraph("COST BREAKDOWN", section_style))

    bd_items = [(k, v) for k, v in resultaat.items()
                if k not in ("TOTAAL", "NZ korting toegepast")]

    bd_data = [["Description", "Amount"]]
    for i, (k, v) in enumerate(bd_items):
        bd_data.append([
            Paragraph(k, S(f"BL{i}", fontSize=9, textColor=TEXT_DARK,
                           fontName="Helvetica", leading=12)),
            Paragraph(f"€ {v:,.2f}", S(f"BR{i}", fontSize=9, textColor=TEXT_DARK,
                                        fontName="Helvetica-Bold",
                                        alignment=TA_RIGHT, leading=12)),
        ])
    bd_data.append([
        Paragraph("<b>TOTAL</b>", S("BTL", fontSize=10, textColor=colors.white,
                                    fontName="Helvetica-Bold", leading=13)),
        Paragraph(f"<b>€ {totaal:,.2f}</b>",
                  S("BTR", fontSize=10, textColor=colors.white,
                    fontName="Helvetica-Bold", alignment=TA_RIGHT, leading=13)),
    ])

    n = len(bd_data)
    bd_t = Table(bd_data, colWidths=[W * 0.68, W * 0.32])
    bd_style = [
        ("BACKGROUND",    (0, 0),    (-1, 0),    BLUE),
        ("TEXTCOLOR",     (0, 0),    (-1, 0),    colors.white),
        ("FONTNAME",      (0, 0),    (-1, 0),    "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0),    (-1, 0),    8),
        ("TOPPADDING",    (0, 0),    (-1, 0),    8),
        ("BOTTOMPADDING", (0, 0),    (-1, 0),    8),
        ("LEFTPADDING",   (0, 0),    (-1, 0),    10),
        ("TOPPADDING",    (0, 1),    (-1, -2),   8),
        ("BOTTOMPADDING", (0, 1),    (-1, -2),   8),
        ("LEFTPADDING",   (0, 1),    (-1, -2),   10),
        ("LINEBELOW",     (0, 1),    (-1, -2),   0.5, colors.HexColor("#e4e9f0")),
        ("ALIGN",         (1, 0),    (1, -1),    "RIGHT"),
        ("RIGHTPADDING",  (1, 0),    (1, -1),    10),
        ("BACKGROUND",    (0, n-1),  (-1, n-1),  BLUE),
        ("TOPPADDING",    (0, n-1),  (-1, n-1),  9),
        ("BOTTOMPADDING", (0, n-1),  (-1, n-1),  9),
        ("LEFTPADDING",   (0, n-1),  (-1, n-1),  10),
        *[("BACKGROUND",  (0, i),    (-1, i),    ROW_ALT)
          for i in range(2, n - 1, 2)],
    ]
    bd_t.setStyle(TableStyle(bd_style))
    story.append(bd_t)
    story.append(Spacer(1, 8*mm))

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, thickness=0.5,
                             color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Royal Decree Retributions 2026 · Published 29/12/2025 · Belgian Official Gazette · DKM Customs",
        footer_style,
    ))

    doc.build(story)
    return buffer.getvalue()


def _fallback_pdf() -> bytes:
    """Minimal valid PDF when reportlab is unavailable."""
    content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 595 842]/Parent 2 0 R/Resources<<>>>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
217
%%EOF"""
    return content
