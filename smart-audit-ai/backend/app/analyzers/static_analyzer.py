import re
from typing import Any

PATTERNS = [
    ("Reentrancy risk", "High", r"\.call\{|call\.value|send\("),
    ("Use of tx.origin", "High", r"tx\.origin"),
    ("Dangerous delegatecall", "Critical", r"delegatecall"),
    ("selfdestruct usage", "High", r"selfdestruct"),
    ("Timestamp dependence", "Medium", r"block\.timestamp"),
    ("Insecure randomness", "High", r"block\.number|blockhash|timestamp"),
    ("Unchecked low-level call", "High", r"\.(call|delegatecall|staticcall)\("),
    ("Floating pragma", "Low", r"pragma solidity \^"),
    ("Hardcoded privileged address", "Medium", r"0x[a-fA-F0-9]{40}"),
    ("Unsafe assembly", "Medium", r"assembly\s*\{"),
    ("Possible missing input validation", "Low", r"function .*\)\s*(public|external)"),
    ("Unbounded loop", "Medium", r"for\s*\(.*;.*;.*\)|while\s*\("),
]


def run_static_analysis(files: list[dict[str, str]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for f in files:
        code = f["content"]
        lines = code.splitlines()
        for title, severity, pattern in PATTERNS:
            for i, line in enumerate(lines, start=1):
                if re.search(pattern, line):
                    findings.append({
                        "title": title,
                        "severity": severity,
                        "category": "static",
                        "file": f["filename"],
                        "line": i,
                        "description": f"Pattern detected: {pattern}",
                        "impact": "Potential security issue.",
                        "exploit_scenario": "An attacker may exploit this depending on logic.",
                        "recommendation": "Review logic and apply secure pattern.",
                        "patch_example": "// Apply checks-effects-interactions and access control",
                        "status": "open",
                        "code_snippet": line.strip(),
                    })
    return findings
