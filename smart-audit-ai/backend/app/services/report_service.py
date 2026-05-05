from collections import Counter


def build_report(scan_id: int, score: int, risk_level: str, findings: list[dict]) -> tuple[dict, str]:
    sev = Counter([f.get("severity", "Informational") for f in findings])
    report = {
        "scan_id": scan_id,
        "executive_summary": "Automated Solidity audit with static + optional Slither + optional Claude review.",
        "score": score,
        "risk_level": risk_level,
        "severity_breakdown": dict(sev),
        "findings": findings,
        "checklist": ["Access control reviewed", "External calls reviewed", "Economic risks reviewed"],
    }
    md = f"# Audit Report\n\n- Scan ID: {scan_id}\n- Score: {score}/100\n- Risk: {risk_level}\n\n## Findings\n"
    for f in findings:
        md += f"\n### [{f['severity']}] {f['title']}\n- File: {f.get('file','')}:{f.get('line',0)}\n- Description: {f.get('description','')}\n- Impact: {f.get('impact','')}\n- Exploit: {f.get('exploit_scenario','')}\n- Recommendation: {f.get('recommendation','')}\n- Patch: ```solidity\n{f.get('patch_example','')}\n```\n"
    return report, md
