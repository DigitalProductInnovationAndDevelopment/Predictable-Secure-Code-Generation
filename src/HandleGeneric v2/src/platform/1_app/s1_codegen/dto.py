from pydantic import BaseModel
from typing import List
from platform.domain.models.generation import GeneratedFile

class CodeGenInput(BaseModel):
    language: str
    requirements: list[dict]  # simplified for skeleton
    out_dir: str

class CodeGenOutput(BaseModel):
    files: List[GeneratedFile]
    rationale: str | None = None
