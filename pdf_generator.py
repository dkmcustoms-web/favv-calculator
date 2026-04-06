"""
FAVV PDF Report Generator - uses reportlab
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# DKM brand colours
BLUE       = colors.HexColor("#003d7a")
LIGHT_BLUE = colors.HexColor("#7eb8f7")
BG_GREY    = colors.HexColor("#f4f6f9")
ROW_ALT    = colors.HexColor("#f0f4ff")
WHITE      = colors.white
TEXT_DARK  = colors.HexColor("#222222")
TEXT_MID   = colors.HexColor("#555555")


def genereer_pdf(product_type: str, invoer: dict, resultaat: dict) -> bytes:
    """Generate a professional A4 PDF report and return as bytes."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title="FAVV Retribution Report",
        author="DKM Customs",
    )

    W = A4[0] - 40*mm  # usable width
    datum = datetime.now().strftime("%d/%m/%Y  %H:%M")
    totaal = resultaat.get("TOTAAL", 0)
    nz = resultaat.get("NZ korting toegepast", False)

    styles = getSampleStyleSheet()

    # Custom styles
    def S(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    title_style   = S("FTitle",   fontSize=22, textColor=WHITE,     fontName="Helvetica-Bold", alignment=TA_LEFT, leading=26)
    sub_style     = S("FSub",     fontSize=10, textColor=LIGHT_BLUE, fontName="Helvetica",     alignment=TA_LEFT)
    label_style   = S("FLabel",   fontSize=8,  textColor=TEXT_MID,  fontName="Helvetica",      spaceAfter=2, leading=11)
    value_style   = S("FValue",   fontSize=10, textColor=TEXT_DARK, fontName="Helvetica-Bold", leading=13)
    section_style = S("FSection", fontSize=8,  textColor=BLUE,      fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4, leading=10)
    amount_style  = S("FAmount",  fontSize=26, textColor=WHITE,     fontName="Helvetica-Bold", alignment=TA_CENTER, leading=30)
    total_lbl     = S("FTLbl",    fontSize=9,  textColor=LIGHT_BLUE,fontName="Helvetica",      alignment=TA_CENTER, leading=12)
    footer_style  = S("FFooter",  fontSize=7,  textColor=colors.HexColor("#aaaaaa"), fontName="Helvetica", alignment=TA_CENTER)
    nz_style      = S("FNZ",      fontSize=8,  textColor=colors.HexColor("#856404"), fontName="Helvetica-Bold", alignment=TA_CENTER)

    story = []

    # ── HEADER BANNER ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<b>FAVV</b>", S("FLogoBox", fontSize=18, textColor=BLUE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        [Paragraph("Retribution Report", title_style),
         Paragraph("Royal Decree Tariffs 2026 · Port of Antwerp", sub_style)],
        Paragraph(f"DKM Customs<br/><font size='8'>{datum}</font>",
                  S("FRight", fontSize=10, textColor=WHITE, fontName="Helvetica", alignment=TA_RIGHT, leading=14)),
    ]]
    header_table = Table(header_data, colWidths=[22*mm, W - 60*mm, 38*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), BLUE),
        ("BACKGROUND",   (0, 0), (0, 0),   WHITE),
        ("ROUNDEDCORNERS", [6]),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (0, 0),   6),
        ("RIGHTPADDING", (0, 0), (0, 0),   6),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (1, 0), (1, 0),   12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6*mm))

    # ── PRODUCT TYPE ───────────────────────────────────────────────────────────
    story.append(Paragraph("PRODUCT TYPE", section_style))
    pt_table = Table([[Paragraph(product_type, value_style)]], colWidths=[W])
    pt_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ROW_ALT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 4*mm))

    # ── PARAMETERS ─────────────────────────────────────────────────────────────
    if invoer:
        story.append(Paragraph("INPUT PARAMETERS", section_style))
        param_items = list(invoer.items())
        # arrange in 2 columns
        rows = []
        for i in range(0, len(param_items), 2):
            row = []
            for j in range(2):
                if i + j < len(param_items):
                    k, v = param_items[i + j]
                    cell = [Paragraph(k.upper(), label_style), Paragraph(str(v), value_style)]
                else:
                    cell = [""]
                row.append(cell)
            rows.append(row)

        param_table = Table(rows, colWidths=[W/2, W/2])
        param_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND",    (0, 0), (-1, -1), BG_GREY),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.5, colors.HexColor("#e0e8f0")),
        ]))
        story.append(param_table)
        story.append(Spacer(1, 4*mm))

    # ── TOTAL AMOUNT BOX ───────────────────────────────────────────────────────
    nz_row = []
    if nz:
        nz_row = [[Paragraph("✓  New Zealand discount 22.5% applied", nz_style)]]

    total_data = [
        [Paragraph("TOTAL FAVV RETRIBUTION", total_lbl)],
        [Paragraph(f"€ {totaal:,.2f}", amount_style)],
    ] + nz_row

    total_table = Table(total_data, colWidths=[W])
    ts = [
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]
    if nz:
        ts += [
            ("BACKGROUND",    (0, 2), (-1, 2), colors.HexColor("#fff8e0")),
            ("TOPPADDING",    (0, 2), (-1, 2), 6),
            ("BOTTOMPADDING", (0, 2), (-1, 2), 6),
        ]
    total_table.setStyle(TableStyle(ts))
    story.append(total_table)
    story.append(Spacer(1, 5*mm))

    # ── COST BREAKDOWN ─────────────────────────────────────────────────────────
    story.append(Paragraph("COST BREAKDOWN", section_style))

    breakdown_items = [(k, v) for k, v in resultaat.items()
                       if k not in ("TOTAAL", "NZ korting toegepast")]

    bd_data = [["Description", "Amount"]]
    for k, v in breakdown_items:
        bd_data.append([
            Paragraph(k, S("BDLabel", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica", leading=12)),
            Paragraph(f"€ {v:,.2f}", S("BDAmount", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica-Bold",
                                        alignment=TA_RIGHT, leading=12)),
        ])
    # Total row
    bd_data.append([
        Paragraph("<b>TOTAL</b>", S("BDTotal", fontSize=10, textColor=WHITE, fontName="Helvetica-Bold", leading=13)),
        Paragraph(f"<b>€ {totaal:,.2f}</b>", S("BDTotalAmt", fontSize=10, textColor=WHITE,
                                                 fontName="Helvetica-Bold", alignment=TA_RIGHT, leading=13)),
    ])

    n = len(bd_data)
    bd_table = Table(bd_data, colWidths=[W * 0.68, W * 0.32])
    bd_style = [
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("TOPPADDING",    (0, 0), (-1, 0),  7),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
        ("LEFTPADDING",   (0, 0), (-1, 0),  10),
        # Data rows
        ("TOPPADDING",    (0, 1), (-1, -2), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -2), 7),
        ("LEFTPADDING",   (0, 1), (-1, -2), 10),
        ("LINEBELOW",     (0, 1), (-1, -2), 0.5, colors.HexColor("#e4e9f0")),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("RIGHTPADDING",  (1, 0), (1, -1),  10),
        # Alternating rows
        *[("BACKGROUND", (0, i), (-1, i), ROW_ALT) for i in range(2, n - 1, 2)],
        # Total row
        ("BACKGROUND",    (0, n-1), (-1, n-1), BLUE),
        ("TOPPADDING",    (0, n-1), (-1, n-1), 9),
        ("BOTTOMPADDING", (0, n-1), (-1, n-1), 9),
        ("LEFTPADDING",   (0, n-1), (-1, n-1), 10),
    ]
    bd_table.setStyle(TableStyle(bd_style))
    story.append(bd_table)

    story.append(Spacer(1, 8*mm))

    # ── FOOTER ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Royal Decree Retributions 2026 · Published 29/12/2025 · Belgian Official Gazette · DKM Customs",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()
