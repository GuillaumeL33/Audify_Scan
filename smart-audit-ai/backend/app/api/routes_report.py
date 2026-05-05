import ast
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Report

router = APIRouter(prefix="/api/scans", tags=["reports"])


@router.get("/{scan_id}/report.json")
def report_json(scan_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return JSONResponse(content=ast.literal_eval(report.json_report))


@router.get("/{scan_id}/report.md")
def report_markdown(scan_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return PlainTextResponse(content=report.markdown_report)
