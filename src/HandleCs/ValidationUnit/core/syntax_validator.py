"""
Syntax validation component for Python code.
"""

import ast
import re
import subprocess
import time
import logging
from typing import Dict, Any, List
from pathlib import Path

from src.HandleCs.ValidationUnit.models.validation_result import ValidationResult, ValidationStatus
from src.HandleCs.ValidationUnit.utils.helpers import ValidationHelper
from src.HandleCs.ValidationUnit.utils.config import ValidationConfig


class SyntaxValidator:
    """Validates Python code syntax and basic structure."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        #check for import
        self.using_directive_pattern = re.compile(r'^\s*using\s+([\w.]+)(\s*=\s*[\w.]+)?\s*;')
        self.namespace_pattern = re.compile(r'^\s*namespace\s+([\w.]+)\s*{?')

    def validate(
        self, codebase_path: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate syntax of Python files in the codebase.

        Args:
            codebase_path: Path to the codebase directory
            metadata: Metadata about the codebase

        Returns:
            ValidationResult with syntax validation results
        """
        start_time = time.time()
        result = ValidationResult(
            step_name="Syntax Validation", status=ValidationStatus.VALID, is_valid=True
        )

        try:
            self.logger.info("Starting syntax validation")

            # Get Python files from metadata
            cs_file = self._get_files_from_metadata(metadata, codebase_path)

            if not cs_file:
                result.add_warning("No C# files found for syntax validation")
                result.metadata["files_checked"] = 0
                return result

            # Validate each file
            files_checked = 0
            syntax_errors = 0

            for file_path in cs_file:
                try:
                    self._validate_file_syntax(file_path, result)
                    files_checked += 1
                except Exception as e:
                    self.logger.error(f"Error validating {file_path}: {e}")
                    result.add_error(
                        f"Failed to validate file: {str(e)}", file_path=file_path
                    )
                    syntax_errors += 1

            # Additional checks if enabled
            if self.config.syntax_check_imports:
                self._validate_imports(cs_file, result, codebase_path)

            if self.config.syntax_check_indentation:
                self._validate_indentation(cs_file, result)

            # Set metadata
            result.metadata.update(
                {
                    "files_checked": files_checked,
                    "syntax_errors": syntax_errors,
                    "python_version": self.config.syntax_python_version,
                    "checks_performed": {
                        "syntax": True,
                        "imports": self.config.syntax_check_imports,
                        "indentation": self.config.syntax_check_indentation,
                    },
                }
            )

            self.logger.info(
                f"Syntax validation completed: {files_checked} files checked"
            )

        except Exception as e:
            result.add_error(f"Syntax validation failed: {str(e)}")
            result.status = ValidationStatus.ERROR
            self.logger.error(f"Syntax validation error: {e}")

        finally:
            result.execution_time = time.time() - start_time

        return result

    def _get_files_from_metadata(
        self, metadata: Dict[str, Any], codebase_path: str
    ) -> List[str]:
        """Extract file paths from metadata."""
        files = []
        base_path = Path(codebase_path)

        for file_data in metadata.get("files", []):
            file_path = file_data.get("path", "")
            if file_path:
                full_path = base_path / file_path
                if full_path.exists():
                    files.append(str(full_path))

        return files

    import subprocess

    def _validate_file_syntax(self, file_path: str, result: ValidationResult):
        """Validate syntax of a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            brace_stack = []
            in_multiline_comment = False

            for i, line in enumerate(lines, start=1):
                stripped = line.strip()

                # Handle multiline comments
                if '/*' in line and '*/' not in line:
                    in_multiline_comment = True
                    continue
                if '*/' in line:
                    in_multiline_comment = False
                    continue
                if in_multiline_comment:
                    continue

                # Skip empty lines or single-line comments
                if not stripped or stripped.startswith("//"):
                    continue

                # Check for balanced braces
                for char in stripped:
                    if char == '{':
                        brace_stack.append((i, '{'))
                    elif char == '}':
                        if brace_stack:
                            brace_stack.pop()
                        else:
                            result.add_error(
                                "Unmatched closing brace '}'",
                                file_path=file_path,
                                line_number=i,
                                error_code="CS_BRACE_ERROR"
                            )

                # Check if line ends with semicolon (with exceptions)
                if stripped and not (
                        stripped.endswith(";") or
                        stripped.endswith("{") or
                        stripped.endswith("}") or
                        stripped.endswith(")") or  # method declarations or control flow
                        stripped.endswith(":") or  # labels or switch cases
                        stripped.startswith("[") or  # attributes
                        stripped.startswith("#")  # preprocessor directives
                ):
                    # Also ignore lines that are using directives or class/interface definitions
                    if not (
                            stripped.startswith("using ") or
                            stripped.startswith("namespace ") or
                            stripped.startswith("class ") or
                            stripped.startswith("interface ") or
                            stripped.startswith("enum ") or
                            stripped.startswith("public ") or
                            stripped.startswith("private ") or
                            stripped.startswith("protected ") or
                            stripped.startswith("internal ") or
                            stripped.startswith("static ") or
                            stripped.startswith("abstract ") or
                            stripped.startswith("sealed ") or
                            stripped.startswith("partial ") or
                            stripped.startswith("readonly ") or
                            stripped.startswith("const ") or
                            stripped.startswith("async ") or
                            stripped.startswith("override ") or
                            stripped.startswith("virtual ") or
                            stripped.startswith("extern ") or
                            stripped.startswith("unsafe ") or
                            stripped.startswith("volatile ") or
                            stripped.startswith("fixed ") or
                            stripped.startswith("delegate ") or
                            stripped.startswith("event ") or
                            stripped.startswith("operator ") or
                            stripped.startswith("implicit ") or
                            stripped.startswith("explicit ") or
                            stripped.startswith("get;") or
                            stripped.startswith("set;") or
                            stripped.startswith("return") or
                            stripped.startswith("throw") or
                            stripped.startswith("try") or
                            stripped.startswith("catch") or
                            stripped.startswith("finally") or
                            stripped.startswith("if") or
                            stripped.startswith("else") or
                            stripped.startswith("for") or
                            stripped.startswith("while") or
                            stripped.startswith("do") or
                            stripped.startswith("switch") or
                            stripped.startswith("case") or
                            stripped.startswith("default") or
                            stripped.startswith("break") or
                            stripped.startswith("continue") or
                            stripped.startswith("goto") or
                            stripped.startswith("lock") or
                            stripped.startswith("using") or
                            stripped.startswith("foreach") or
                            stripped.startswith("yield") or
                            stripped.startswith("await") or
                            re.match(r'^\w+\s+\w+\s*\(.*\)\s*$', stripped)  # Method declaration
                    ):
                        result.add_error(
                            "Possible missing semicolon or incomplete statement",
                            file_path=file_path,
                            line_number=i,
                            error_code="CS_MISSING_SEMICOLON"
                        )

            if brace_stack:
                for line_num, _ in brace_stack:
                    result.add_error(
                        "Unmatched opening brace '{'",
                        file_path=file_path,
                        line_number=line_num,
                        error_code="CS_BRACE_ERROR"
                    )

            if not result.errors:
                self.logger.debug(f"Basic syntax heuristic OK: {file_path}")

        except UnicodeDecodeError as e:
            result.add_error(
                f"Encoding error: {str(e)}",
                file_path=file_path,
                error_code="ENCODING_ERROR"
            )
        except Exception as e:
            result.add_error(
                f"Unexpected error: {str(e)}",
                file_path=file_path,
                error_code="UNEXPECTED_ERROR"
            )

    def _validate_imports(
        self, cs_files: List[str], result: ValidationResult, codebase_path: str
    ):

        """Validate using directives in C# files."""
        import_errors = 0

        for file_path in cs_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.readlines()

                namespace_declared = False
                using_directives = []
                first_non_using_line = None

                for i, line in enumerate(content, 1):
                    stripped = line.strip()

                    # Skip empty lines and comments
                    if not stripped or stripped.startswith("//"):
                        continue

                    # Check for namespace declaration
                    if not namespace_declared and self.namespace_pattern.match(stripped):
                        namespace_declared = True
                        continue

                    # Check for using directives
                    if not namespace_declared and self.using_directive_pattern.match(stripped):
                        using_directives.append((i, stripped))
                        continue

                    # First non-using, non-namespace, non-comment line
                    if first_non_using_line is None:
                        first_non_using_line = i
                        break

                # Check if all using directives are at the top
                if first_non_using_line and using_directives:
                    last_using_line = using_directives[-1][0]
                    if last_using_line > first_non_using_line:
                        result.add_warning(
                            "Using directives should be placed before namespace declaration and other code",
                            file_path=file_path,
                            line_number=last_using_line,
                            error_code="CS_USING_PLACEMENT"
                        )

                

            except Exception as e:
                self.logger.debug(f"Could not check using directives in {file_path}: {e}")
                import_errors += 1

        result.metadata["import_errors"] = import_errors

    def _check_import_node(
        self,
        node: ast.AST,
        file_path: str,
        result: ValidationResult,
        codebase_path: str,
    ):
        """Check a single import node."""
        try:
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Check for relative imports outside package
                    if node.level > 0:  # Relative import
                        self._validate_relative_import(
                            node, file_path, result, codebase_path
                        )

                    # Check for problematic imports
                    if node.module in ["__future__"]:
                        # __future__ imports should be at top
                        if node.lineno > 10:  # Rough check
                            result.add_warning(
                                "__future__ imports should be at the top of the file",
                                file_path=file_path,
                                line_number=node.lineno,
                            )

        except Exception as e:
            self.logger.debug(f"Error checking import in {file_path}: {e}")

    def _validate_relative_import(
        self,
        node: ast.ImportFrom,
        file_path: str,
        result: ValidationResult,
        codebase_path: str,
    ):
        """Validate relative import."""
        try:
            # Check if the relative import makes sense
            file_path_obj = Path(file_path)
            codebase_path_obj = Path(codebase_path)

            relative_path = file_path_obj.relative_to(codebase_path_obj)
            path_parts = relative_path.parts[:-1]  # Exclude filename

            if node.level > len(path_parts):
                result.add_warning(
                    f"Relative import goes beyond package root (level {node.level})",
                    file_path=file_path,
                    line_number=node.lineno,
                )

        except Exception as e:
            self.logger.debug(f"Could not validate relative import in {file_path}: {e}")

    def _validate_indentation(self, cs_file: List[str], result: ValidationResult):
        """Validate indentation consistency."""
        for file_path in cs_file:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                self._check_indentation_consistency(lines, file_path, result)

            except Exception as e:
                self.logger.debug(f"Could not check indentation in {file_path}: {e}")

    def _check_indentation_consistency(
        self, lines: List[str], file_path: str, result: ValidationResult
    ):
        """Check for consistent indentation in a file."""
        spaces_count = 0
        tabs_count = 0
        mixed_indentation = False

        for line_num, line in enumerate(lines, 1):
            if line.strip():  # Non-empty line
                leading_whitespace = line[: len(line) - len(line.lstrip())]

                if leading_whitespace:
                    if "\t" in leading_whitespace and " " in leading_whitespace:
                        mixed_indentation = True
                        result.add_warning(
                            "Mixed tabs and spaces in indentation",
                            file_path=file_path,
                            line_number=line_num,
                            error_code="MIXED_INDENTATION",
                        )
                        break
                    elif "\t" in leading_whitespace:
                        tabs_count += 1
                    elif " " in leading_whitespace:
                        spaces_count += 1

        # Check for inconsistent indentation style
        if spaces_count > 0 and tabs_count > 0 and not mixed_indentation:
            result.add_warning(
                "File uses both tabs and spaces for indentation (in different lines)",
                file_path=file_path,
                error_code="INCONSISTENT_INDENTATION",
            )


if __name__ == "__main__":
    import sys

    validator = SyntaxValidator("")

    result = ValidationResult(step_name="SyntaxCheck", status="pending", is_valid=True)
    # Replace with your test .cs file
    test_file_path = "C:\Creatum fortiss\Predictable-Secure-Code-Generation\input\CsExample\Code\Caculator.cs"

    validator._validate_file_syntax(test_file_path, result)
    print(result.get_errors())



