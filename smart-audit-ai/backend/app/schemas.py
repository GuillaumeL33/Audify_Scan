from pydantic import BaseModel, Field
from typing import List


class FindingOut(BaseModel):
    title: str
    severity: str
    category: str = ""
    file: str = ""
    line: int = 0
    description: str
    impact: str = ""
    exploit_scenario: str = ""
    recommendation: str = ""
    patch_example: str = ""
    status: str = "open"
    code_snippet: str = ""


class ScanCreateRequest(BaseModel):
    project_name: str = "Untitled Project"
    code: str | None = None


class ScanSummary(BaseModel):
    scan_id: int
    score: int
    risk_level: str
    findings_count: int


class ScanDetail(BaseModel):
    id: int
    score: int
    risk_level: str
    summary: str
    findings: List[FindingOut]


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
