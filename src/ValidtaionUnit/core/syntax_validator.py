"""
Syntax validation component for Python code.
"""

import ast
import time
import logging
from typing import Dict, Any, List
from pathlib import Path

from ..models.validation_result import ValidationResult, ValidationStatus
from ..utils.helpers import ValidationHelper
from ..utils.config import ValidationConfig


class SyntaxValidator:
    """Validates Python code syntax and basic structure."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

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
            python_files = self._get_files_from_metadata(metadata, codebase_path)

            if not python_files:
                result.add_warning("No Python files found for syntax validation")
                result.metadata["files_checked"] = 0
                return result

            # Validate each file
            files_checked = 0
            syntax_errors = 0

            for file_path in python_files:
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
                self._validate_imports(python_files, result, codebase_path)

            if self.config.syntax_check_indentation:
                self._validate_indentation(python_files, result)

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

    def _validate_file_syntax(self, file_path: str, result: ValidationResult):
        """Validate syntax of a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse with AST
            try:
                ast.parse(content, filename=file_path)
                self.logger.debug(f"Syntax OK: {file_path}")
            except SyntaxError as e:
                error_msg = f"Syntax error: {e.msg}"
                result.add_error(
                    error_msg,
                    file_path=file_path,
                    line_number=e.lineno,
                    column=e.offset,
                    error_code="SYNTAX_ERROR",
                )
                self.logger.warning(f"Syntax error in {file_path}: {error_msg}")

        except UnicodeDecodeError as e:
            result.add_error(
                f"Encoding error: {str(e)}",
                file_path=file_path,
                error_code="ENCODING_ERROR",
            )
        except Exception as e:
            result.add_error(
                f"Unexpected error: {str(e)}",
                file_path=file_path,
                error_code="UNEXPECTED_ERROR",
            )

    def _validate_imports(
        self, python_files: List[str], result: ValidationResult, codebase_path: str
    ):
        """Validate import statements."""
        import_errors = 0

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=file_path)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        self._check_import_node(node, file_path, result, codebase_path)

            except Exception as e:
                self.logger.debug(f"Could not check imports in {file_path}: {e}")
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

    def _validate_indentation(self, python_files: List[str], result: ValidationResult):
        """Validate indentation consistency."""
        for file_path in python_files:
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
