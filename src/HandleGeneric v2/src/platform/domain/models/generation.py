from pydantic import BaseModel
from typing import List, Optional


class GeneratedFile(BaseModel):
    path: str
    content: str
    language: Optional[str] = None


class CodeGenReport(BaseModel):
    files: List[GeneratedFile]
    rationale: str | None = None
    cost_tokens: int | None = None
    generation_time_seconds: float | None = None

    def summary(self) -> str:
        files_summary = f"Generated {len(self.files)} files"
        if self.cost_tokens:
            files_summary += f" ({self.cost_tokens} tokens)"
        if self.generation_time_seconds:
            files_summary += f" in {self.generation_time_seconds:.2f}s"
        return files_summary + "."
