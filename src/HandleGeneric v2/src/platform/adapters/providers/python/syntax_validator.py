"""Python syntax validator using AST parsing."""

import ast
import traceback
from pathlib import Path
from platform.ports.providers import SyntaxValidator
from platform.domain.models.validation import SyntaxResult, SyntaxIssue
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class PythonSyntaxValidator:
    """Python syntax validation using AST."""

    language = "python"

    def validate(self, file: Path, content: str) -> SyntaxResult:
        """Validate Python syntax using ast.parse."""
        issues = []

        try:
            # Parse the AST
            ast.parse(content, filename=str(file))

            logger.debug("Python syntax validation passed", file=str(file))
            return SyntaxResult(status="valid", issues=[])

        except SyntaxError as e:
            # Extract syntax error details
            issue = SyntaxIssue(file=str(file), line=e.lineno, message=f"SyntaxError: {e.msg}")
            issues.append(issue)

            logger.warning("Python syntax error detected", file=str(file), line=e.lineno, msg=e.msg)

        except Exception as e:
            # Handle other parsing errors
            issue = SyntaxIssue(file=str(file), line=None, message=f"Parse error: {str(e)}")
            issues.append(issue)

            logger.error("Python parsing failed", file=str(file), error=str(e))

        # Additional static checks could go here
        self._check_common_issues(content, file, issues)

        status = "invalid" if issues else "valid"
        return SyntaxResult(status=status, issues=issues)

    def _check_common_issues(self, content: str, file: Path, issues: list) -> None:
        """Check for common Python issues beyond syntax."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for mixing tabs and spaces (basic check)
            if "\t" in line and "    " in line:
                issues.append(
                    SyntaxIssue(
                        file=str(file), line=i, message="Warning: Mixed tabs and spaces detected"
                    )
                )

            # Check for trailing whitespace
            if line.endswith(" ") or line.endswith("\t"):
                issues.append(
                    SyntaxIssue(file=str(file), line=i, message="Warning: Trailing whitespace")
                )

            # Check for very long lines (over 120 characters)
            if len(line) > 120:
                issues.append(
                    SyntaxIssue(
                        file=str(file),
                        line=i,
                        message="Warning: Line length exceeds 120 characters",
                    )
                )

    def can_handle(self, file_path: Path) -> bool:
        """Check if this validator can handle the given file."""
        return file_path.suffix == ".py"
