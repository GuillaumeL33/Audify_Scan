import json
import shutil
import subprocess
from pathlib import Path


def run_slither_if_available(files: list[dict[str, str]]) -> list[dict]:
    if not shutil.which("slither"):
        return []

    temp_dir = Path("/tmp/slither_scan")
    temp_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        (temp_dir / f["filename"]).write_text(f["content"], encoding="utf-8")

    result = subprocess.run(
        ["slither", str(temp_dir), "--json", "-"], capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    raw = json.loads(result.stdout)
    findings = []
    for detector in raw.get("results", {}).get("detectors", []):
        elem = detector.get("elements", [{}])[0]
        findings.append({
            "title": detector.get("check", "Slither finding"),
            "severity": detector.get("impact", "Medium").title(),
            "category": "slither",
            "file": elem.get("source_mapping", {}).get("filename_relative", ""),
            "line": elem.get("source_mapping", {}).get("lines", [0])[0],
            "description": detector.get("description", ""),
            "impact": detector.get("impact", ""),
            "exploit_scenario": "See Slither detector details.",
            "recommendation": detector.get("recommendation", ""),
            "patch_example": "",
            "status": "open",
            "code_snippet": "",
        })
    return findings
