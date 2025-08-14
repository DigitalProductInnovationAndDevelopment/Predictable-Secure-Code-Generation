from typing import Protocol
from pathlib import Path
from platform.domain.models.requirements import Requirement

class CodeGenProvider(Protocol):
    language: str
    def build_prompt(self, requirement: Requirement, context: dict) -> str: ...
    def postprocess(self, files: list) -> list: ...

class MetadataProvider(Protocol):
    language: str
    extensions: set[str]
    def parse_file(self, path: Path, content: str): ...

class SyntaxValidator(Protocol):
    language: str
    def validate(self, file: Path, content: str): ...
