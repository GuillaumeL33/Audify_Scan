import ast
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Finding, Scan
from ..schemas import ScanDetail, ScanSummary
from ..services.scan_service import run_scan
from ..utils.file_utils import validate_solidity_file

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanSummary)
async def create_scan(code: str | None = Form(default=None), files: list[UploadFile] | None = File(default=None), db: Session = Depends(get_db)):
    if not code and not files:
        raise HTTPException(status_code=400, detail="Provide Solidity code or .sol files")
    items: list[dict[str, str]] = []
    if code:
        items.append({"filename": "pasted_code.sol", "content": code})
    if files:
        for f in files:
            try:
                validate_solidity_file(f)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            items.append({"filename": f.filename, "content": (await f.read()).decode("utf-8")})

    scan = run_scan(db, items)
    count = db.query(Finding).filter(Finding.scan_id == scan.id).count()
    return ScanSummary(scan_id=scan.id, score=scan.score, risk_level=scan.risk_level, findings_count=count)


@router.get("/{scan_id}", response_model=ScanDetail)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
    return ScanDetail(id=scan.id, score=scan.score, risk_level=scan.risk_level, summary=scan.summary, findings=findings)
