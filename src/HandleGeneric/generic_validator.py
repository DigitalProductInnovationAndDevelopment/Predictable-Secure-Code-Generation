"""
Generic code validator for any programming language.

This module provides a language-agnostic code validator that can validate
code in multiple programming languages using registered language providers.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .core.file_detector import FileDetector
from .core.language_registry import get_global_registry
from .language_init import ensure_initialized


class ValidationStatus(Enum):
    """Status of validation operation."""

    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    language: str
    file_path: str
    status: ValidationStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class OverallValidationResult:
    """Overall validation result for a project."""

    status: ValidationStatus
    total_files: int
    valid_files: int
    invalid_files: int
    error_files: int
    execution_time: float
    results_by_language: Dict[str, List[ValidationResult]]
    summary: Dict[str, Any]


class GenericValidator:
    """
    Generic code validator for any programming language.

    This class can validate code in projects containing files in multiple
    programming languages, using the appropriate language providers.
    """

    def __init__(self, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the generic validator.

        Args:
            exclude_patterns: Optional list of file patterns to exclude
        """
        self.logger = logging.getLogger(__name__)

        # Ensure language providers are initialized
        ensure_initialized()

        self.registry = get_global_registry()
        self.file_detector = FileDetector(exclude_patterns)

        self.logger.info("Generic validator initialized")

    def validate_project(
        self,
        project_path: str,
        languages: Optional[List[str]] = None,
        stop_on_first_error: bool = False,
    ) -> OverallValidationResult:
        """
        Validate all supported files in a project.

        Args:
            project_path: Path to the project directory
            languages: Optional list of languages to validate (validate all if None)
            stop_on_first_error: Stop validation on first error

        Returns:
            Overall validation result
        """
        start_time = time.time()

        project_path = Path(project_path)

        self.logger.info(f"Starting validation for project: {project_path}")

        # Validate project path
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")

        # Find files by language
        self.logger.info("Discovering source files...")
        files_by_language = self.file_detector.find_project_files(
            project_path, languages
        )

        if not files_by_language:
            self.logger.warning("No supported source files found in the project")
            return self._create_empty_result(start_time)

        # Validate files for each language
        results_by_language = {}
        total_files = 0
        valid_files = 0
        invalid_files = 0
        error_files = 0

        for language, file_paths in files_by_language.items():
            self.logger.info(f"Validating {len(file_paths)} {language} files...")

            provider = self.registry.get_provider(language)
            if not provider:
                self.logger.warning(f"No provider found for language: {language}")
                continue

            language_results = []

            for file_path in file_paths:
                result = self._validate_single_file(file_path, language, provider)
                language_results.append(result)
                total_files += 1

                if result.status == ValidationStatus.VALID:
                    valid_files += 1
                elif result.status == ValidationStatus.INVALID:
                    invalid_files += 1
                elif result.status == ValidationStatus.ERROR:
                    error_files += 1

                # Stop on first error if requested
                if stop_on_first_error and result.status in [
                    ValidationStatus.INVALID,
                    ValidationStatus.ERROR,
                ]:
                    self.logger.warning(
                        f"Stopping validation due to error in {result.file_path}"
                    )
                    break

            results_by_language[language] = language_results

            # Stop processing other languages if stopping on first error
            if stop_on_first_error and (invalid_files > 0 or error_files > 0):
                break

        # Determine overall status
        if error_files > 0:
            overall_status = ValidationStatus.ERROR
        elif invalid_files > 0:
            overall_status = ValidationStatus.INVALID
        else:
            overall_status = ValidationStatus.VALID

        execution_time = time.time() - start_time

        # Create summary
        summary = {
            "languages_processed": list(results_by_language.keys()),
            "validation_rate": valid_files / total_files if total_files > 0 else 0,
            "error_rate": (
                (invalid_files + error_files) / total_files if total_files > 0 else 0
            ),
            "languages_summary": {},
        }

        for language, results in results_by_language.items():
            lang_valid = sum(1 for r in results if r.status == ValidationStatus.VALID)
            lang_invalid = sum(
                1 for r in results if r.status == ValidationStatus.INVALID
            )
            lang_error = sum(1 for r in results if r.status == ValidationStatus.ERROR)

            summary["languages_summary"][language] = {
                "total": len(results),
                "valid": lang_valid,
                "invalid": lang_invalid,
                "errors": lang_error,
            }

        result = OverallValidationResult(
            status=overall_status,
            total_files=total_files,
            valid_files=valid_files,
            invalid_files=invalid_files,
            error_files=error_files,
            execution_time=execution_time,
            results_by_language=results_by_language,
            summary=summary,
        )

        self.logger.info(
            f"Validation completed in {execution_time:.2f}s - "
            f"Status: {overall_status.value}, "
            f"Valid: {valid_files}/{total_files}"
        )

        return result

    def validate_single_file(self, file_path: str) -> ValidationResult:
        """
        Validate a single source file.

        Args:
            file_path: Path to the source file

        Returns:
            Validation result for the file
        """
        file_path = Path(file_path)

        self.logger.info(f"Validating single file: {file_path}")

        # Validate file path
        if not file_path.exists():
            return ValidationResult(
                language="unknown",
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                message=f"File does not exist: {file_path}",
            )

        if not file_path.is_file():
            return ValidationResult(
                language="unknown",
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                message=f"Path is not a file: {file_path}",
            )

        # Detect language
        language = self.file_detector.detect_language(file_path)
        if not language:
            return ValidationResult(
                language="unknown",
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                message=f"Unsupported file type: {file_path}",
            )

        # Get provider
        provider = self.registry.get_provider(language)
        if not provider:
            return ValidationResult(
                language=language,
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                message=f"No provider available for language: {language}",
            )

        return self._validate_single_file(file_path, language, provider)

    def _validate_single_file(
        self, file_path: Path, language: str, provider
    ) -> ValidationResult:
        """
        Validate a single file using the appropriate language provider.

        Args:
            file_path: Path to the file
            language: Programming language
            provider: Language provider instance

        Returns:
            Validation result
        """
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Validate syntax using provider
            validation_result, error_message = provider.validate_syntax(
                file_path, content
            )

            if validation_result.value == "valid":
                status = ValidationStatus.VALID
                message = "Syntax is valid"
            elif validation_result.value == "invalid":
                status = ValidationStatus.INVALID
                message = error_message or "Syntax validation failed"
            else:
                status = ValidationStatus.ERROR
                message = error_message or "Validation error"

            return ValidationResult(
                language=language,
                file_path=str(file_path),
                status=status,
                message=message,
            )

        except Exception as e:
            self.logger.error(f"Error validating {file_path}: {e}")
            return ValidationResult(
                language=language,
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                message=f"Validation error: {str(e)}",
            )

    def _create_empty_result(self, start_time: float) -> OverallValidationResult:
        """
        Create an empty validation result.

        Args:
            start_time: Validation start time

        Returns:
            Empty validation result
        """
        return OverallValidationResult(
            status=ValidationStatus.VALID,
            total_files=0,
            valid_files=0,
            invalid_files=0,
            error_files=0,
            execution_time=time.time() - start_time,
            results_by_language={},
            summary={
                "languages_processed": [],
                "validation_rate": 0,
                "error_rate": 0,
                "languages_summary": {},
            },
        )

    def get_validation_report(self, result: OverallValidationResult) -> str:
        """
        Generate a human-readable validation report.

        Args:
            result: Validation result to generate report for

        Returns:
            Formatted validation report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CODE VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Overall Status: {result.status.value.upper()}")
        lines.append(f"Total Files: {result.total_files}")
        lines.append(f"Valid Files: {result.valid_files}")
        lines.append(f"Invalid Files: {result.invalid_files}")
        lines.append(f"Error Files: {result.error_files}")
        lines.append(f"Execution Time: {result.execution_time:.2f}s")
        lines.append("")

        if result.summary["languages_processed"]:
            lines.append("RESULTS BY LANGUAGE:")
            lines.append("-" * 30)

            for language in result.summary["languages_processed"]:
                lang_summary = result.summary["languages_summary"][language]
                lines.append(f"{language.upper()}:")
                lines.append(f"  Total: {lang_summary['total']}")
                lines.append(f"  Valid: {lang_summary['valid']}")
                lines.append(f"  Invalid: {lang_summary['invalid']}")
                lines.append(f"  Errors: {lang_summary['errors']}")
                lines.append("")

        # Show detailed errors if any
        has_errors = False
        for language, results in result.results_by_language.items():
            error_results = [
                r
                for r in results
                if r.status in [ValidationStatus.INVALID, ValidationStatus.ERROR]
            ]
            if error_results:
                if not has_errors:
                    lines.append("DETAILED ERRORS:")
                    lines.append("-" * 30)
                    has_errors = True

                lines.append(f"{language.upper()} FILES:")
                for error_result in error_results:
                    lines.append(f"  {error_result.file_path}: {error_result.message}")
                lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
