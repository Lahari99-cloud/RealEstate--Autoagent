from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .domain import Lead, Recommendation


GOLD = colors.HexColor("#B78A3D")
NAVY = colors.HexColor("#132238")
SLATE = colors.HexColor("#526274")
PALE = colors.HexColor("#F3F6F8")


def build_pdf(run_id: str, lead: Lead, recommendations: list[Recommendation], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"psi-investment-proposal-{run_id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm,
                            title="PSI AI-Generated Investment Proposal", author="PSI AutoAgent")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", fontName="Helvetica-Bold", fontSize=11, textColor=GOLD, leading=14, spaceAfter=5))
    styles.add(ParagraphStyle(name="Hero", fontName="Helvetica-Bold", fontSize=25, textColor=NAVY, leading=29, spaceAfter=8))
    styles.add(ParagraphStyle(name="CardTitle", fontName="Helvetica-Bold", fontSize=15, textColor=NAVY, leading=18))
    styles.add(ParagraphStyle(name="BodyMuted", fontName="Helvetica", fontSize=9, textColor=SLATE, leading=14))
    styles.add(ParagraphStyle(name="Price", fontName="Helvetica-Bold", fontSize=16, textColor=GOLD, leading=19))
    story = [Paragraph("PROPERTY SHOP INVESTMENT", styles["Brand"]),
             Paragraph("Personalized Investment Proposal", styles["Hero"]),
             Paragraph("Prepared by PSI AutoAgent · Decision support, reviewed by a property advisor", styles["BodyMuted"]),
             Spacer(1, 8*mm), HRFlowable(width="100%", color=GOLD, thickness=1.5), Spacer(1, 7*mm)]
    profile = [["BUDGET CAP", f"AED {lead.budget_aed:,}"], ["TARGET AREA", ", ".join(lead.preferred_areas)],
               ["BEDROOMS", str(lead.bedrooms or "Flexible")], ["PURPOSE / TIMELINE", f"{lead.purpose.value.replace('_',' ').title()} · {lead.timeline}"]]
    table = Table(profile, colWidths=[50*mm, 105*mm], hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), PALE), ("TEXTCOLOR", (0,0), (0,-1), SLATE),
                               ("TEXTCOLOR", (1,0), (1,-1), NAVY), ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                               ("FONTNAME", (1,0), (1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 9),
                               ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#DDE3E8")),
                               ("INNERGRID", (0,0), (-1,-1), .25, colors.HexColor("#DDE3E8")),
                               ("LEFTPADDING", (0,0), (-1,-1), 10), ("TOPPADDING", (0,0), (-1,-1), 7),
                               ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
    story += [table, Spacer(1, 9*mm), Paragraph("TOP STRATEGIC MATCHES", styles["Brand"])]
    for index, rec in enumerate(recommendations, 1):
        l = rec.listing
        tags = f"{l.area}  ·  {l.bedrooms} bedrooms  ·  {l.size_sqft:,} sq ft  ·  {l.status.title()}"
        metrics = [[Paragraph(f"AED {l.price_aed:,}", styles["Price"]),
                    Paragraph(f"<b>{rec.net_yield_pct:.2f}%</b><br/><font color='#526274'>projected net yield</font>",
                              ParagraphStyle("Metric", parent=styles["BodyMuted"], alignment=TA_RIGHT))]]
        metric_table = Table(metrics, colWidths=[90*mm, 60*mm])
        risk = " · ".join(rec.risk_flags) if rec.risk_flags else "No material rule-based flags detected"
        card = [[Paragraph(f"{index:02d}  {l.title}", styles["CardTitle"])],
                [Paragraph(tags, styles["BodyMuted"])], [Spacer(1, 2*mm)],
                [Paragraph(l.description, styles["BodyMuted"])], [metric_table],
                [Paragraph(f"<b>Investment case:</b> {rec.area_rationale}", styles["BodyMuted"])],
                [Paragraph(f"<b>Nearby:</b> {', '.join(rec.nearby)}", styles["BodyMuted"])],
                [Paragraph(f"<b>Risk screen:</b> {risk}", styles["BodyMuted"])]]
        box = Table(card, colWidths=[160*mm], hAlign="LEFT")
        box.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.white), ("BOX", (0,0), (-1,-1), .7, colors.HexColor("#DDE3E8")),
                                  ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10),
                                  ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
        story += [box, Spacer(1, 6*mm)]
        if index == 2: story.append(PageBreak())
    story += [Spacer(1, 4*mm), Paragraph("IMPORTANT NOTICE", styles["Brand"]),
              Paragraph("Illustrative estimates only. Rental income, service charges, financing, vacancy and market values can change. This proposal is decision support, not a valuation certificate or guaranteed return. A PSI advisor must verify availability and commercial terms before client delivery.", styles["BodyMuted"])]
    doc.build(story)
    return path

