from sqlalchemy.orm import Session

from ..analyzers.claude_analyzer import run_claude_analysis
from ..analyzers.normalizer import normalize_and_dedup
from ..analyzers.scoring import calculate_score
from ..analyzers.slither_analyzer import run_slither_if_available
from ..analyzers.static_analyzer import run_static_analysis
from ..config import settings
from ..models import Finding, Report, Scan
from .report_service import build_report


def run_scan(db: Session, files: list[dict[str, str]]) -> Scan:
    scan = Scan(status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    static_findings = run_static_analysis(files)
    slither_findings = run_slither_if_available(files) if settings.enable_slither else []
    claude_findings = run_claude_analysis(settings.anthropic_api_key, settings.claude_model, files, static_findings)
    findings = normalize_and_dedup(static_findings + slither_findings + claude_findings)
    score, level = calculate_score(findings)

    for f in findings:
        db.add(Finding(scan_id=scan.id, **{k: f.get(k, "") for k in Finding.__table__.columns.keys() if k not in {"id", "scan_id"}}))

    report_json, report_md = build_report(scan.id, score, level, findings)
    db.add(Report(scan_id=scan.id, json_report=str(report_json), markdown_report=report_md))
    scan.status = "completed"
    scan.score = score
    scan.risk_level = level
    scan.summary = report_json["executive_summary"]
    db.commit()
    db.refresh(scan)
    return scan
