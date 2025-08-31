from __future__ import annotations
from flask import Blueprint, make_response, request
from .analyze import analyze
from ..services.report_service import build_pdf_report

report_bp = Blueprint("report", __name__)

@report_bp.post("/report/pdf")
def report_pdf():
    resp = analyze()
    if isinstance(resp, tuple):
        data, status = resp
        if status != 200:
            return resp
        analysis = data.get_json()
    else:
        analysis = resp.get_json()

    if request.is_json:
        body = request.get_json(silent=True) or {}
        analysis["_inputs"] = body

    pdf_bytes = build_pdf_report(analysis)
    r = make_response(pdf_bytes)
    r.headers.set('Content-Type', 'application/pdf')
    r.headers.set('Content-Disposition', 'attachment', filename='resume-analysis.pdf')
    return r