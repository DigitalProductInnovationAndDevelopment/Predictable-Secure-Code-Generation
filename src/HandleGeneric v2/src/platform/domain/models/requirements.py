from pydantic import BaseModel
from typing import List


class Requirement(BaseModel):
    id: str
    title: str
    description: str
    acceptance: List[str] = []
