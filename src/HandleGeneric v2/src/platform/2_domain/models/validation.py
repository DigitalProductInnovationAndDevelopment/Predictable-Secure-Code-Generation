from pydantic import BaseModel
from typing import List, Literal

class SyntaxIssue(BaseModel):
    file: str
    line: int | None = None
    message: str

class SyntaxResult(BaseModel):
    status: Literal["valid","invalid","error"]
    issues: List[SyntaxIssue] = []

class TestResult(BaseModel):
    status: Literal["passed","failed","error"]
    passed: int = 0
    failed: int = 0
    errors: int = 0
    report_path: str | None = None

class AILogicFinding(BaseModel):
    requirement_id: str
    verdict: Literal["supported","contradicted","uncertain"]
    rationale: str

class AILogicReport(BaseModel):
    status: Literal["ok","warnings","fail"]
    findings: List[AILogicFinding] = []
