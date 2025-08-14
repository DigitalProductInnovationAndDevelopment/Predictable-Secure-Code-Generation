from pydantic import BaseModel
from typing import List

class GeneratedFile(BaseModel):
    path: str
    content: str

class CodeGenReport(BaseModel):
    files: List[GeneratedFile]
    rationale: str | None = None
    cost_tokens: int | None = None

    def summary(self) -> str:
        return f"Generated {len(self.files)} files."
