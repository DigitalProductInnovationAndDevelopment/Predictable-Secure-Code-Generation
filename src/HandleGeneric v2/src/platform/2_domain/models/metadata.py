from pydantic import BaseModel
from typing import List

class FileMetadata(BaseModel):
    path: str
    language: str
    loc: int = 0
    functions: List[str] = []
    classes: List[str] = []
    imports: List[str] = []

class ProjectMetadata(BaseModel):
    files: List[FileMetadata] = []
    languages: List[str] = []
