import ast
from pathlib import Path
from platform.domain.models.validation import SyntaxIssue, SyntaxResult

class PythonSyntaxValidator:
    language = "python"

    def validate(self, file: Path, content: str) -> SyntaxResult:
        try:
            ast.parse(content)
            return SyntaxResult(status="valid", issues=[])
        except SyntaxError as e:
            issue = SyntaxIssue(file=str(file), line=e.lineno, message=e.msg)
            return SyntaxResult(status="invalid", issues=[issue])
