from __future__ import annotations
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def build_pdf_report(analysis_json: dict) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    width, height = LETTER

    y = height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y, "Resume Analyzer Report")
    y -= 0.3 * inch

    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, y, analysis_json.get("summary", ""))
    y -= 0.4 * inch

    scores = analysis_json.get("scores", {})
    line = f"ATS: {scores.get('ats_score',0)}  |  Keywords: {scores.get('keyword_score',0)}  |  Overall: {scores.get('overall_score',0)}"
    c.drawString(1 * inch, y, line)
    y -= 0.3 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Top Missing Keywords")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    for kw in (analysis_json.get("missing_keywords", [])[:12]):
        c.drawString(1.1 * inch, y, f"• {kw}")
        y -= 0.2 * inch
        if y < 1 * inch:
            c.showPage(); y = height - 1 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, y, "Section Alignment (Similarity %)")
    y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    for sec in scores.get("section_alignment", [])[:8]:
        c.drawString(1.1 * inch, y, f"{sec.get('section')}: {sec.get('similarity')}%")
        y -= 0.2 * inch
        if y < 1 * inch:
            c.showPage(); y = height - 1 * inch

    if analysis_json.get("suggestions"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y, "Suggestions")
        y -= 0.25 * inch
        c.setFont("Helvetica", 10)
        for s in analysis_json.get("suggestions", [])[:8]:
            c.drawString(1.1 * inch, y, f"• {s}")
            y -= 0.2 * inch
            if y < 1 * inch:
                c.showPage(); y = height - 1 * inch

    c.showPage()
    c.save()
    return buf.getvalue()