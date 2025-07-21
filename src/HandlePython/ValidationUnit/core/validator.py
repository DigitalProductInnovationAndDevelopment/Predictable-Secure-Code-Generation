"""
Main validator orchestrator that coordinates all validation steps.
"""

import os
import time
import logging
from typing import Dict, Any, Optional

from ..models.validation_result import (
    ValidationResult,
    ValidationStatus,
    OverallValidationResult,
)
from ..utils.helpers import ValidationHelper
from ..utils.config import ValidationConfig
from .syntax_validator import SyntaxValidator
from .test_validator import TestValidator
from .ai_validator import AIValidator


class CodebaseValidator:
    """Main validator that orchestrates all validation steps."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize validators
        self.syntax_validator = SyntaxValidator(self.config)
        self.test_validator = TestValidator(self.config)
        self.ai_validator = AIValidator(self.config)

        # Setup logging
        ValidationHelper.setup_logging(
            self.config.log_level, self.config.verbose_output
        )

        self.logger.info("CodebaseValidator initialized")

    def validate_codebase(
        self, codebase_path: str, metadata_path: str, output_path: Optional[str] = None
    ) -> OverallValidationResult:
        """
        Validate a codebase using all configured validation steps.

        Args:
            codebase_path: Path to the codebase directory
            metadata_path: Path to the metadata.json file
            output_path: Optional path to save validation report

        Returns:
            OverallValidationResult with complete validation results
        """
        start_time = time.time()

        # Initialize overall result
        overall_result = OverallValidationResult(
            codebase_path=codebase_path,
            metadata_path=metadata_path,
            overall_status=ValidationStatus.VALID,
            is_valid=True,
        )

        try:
            self.logger.info(f"Starting validation of codebase: {codebase_path}")

            # Validate inputs
            validation_errors = self._validate_inputs(codebase_path, metadata_path)
            if validation_errors:
                for error in validation_errors:
                    self.logger.error(error)

                # Create error result
                error_result = ValidationResult(
                    step_name="Input Validation",
                    status=ValidationStatus.ERROR,
                    is_valid=False,
                )
                for error in validation_errors:
                    error_result.add_error(error)

                overall_result.add_step_result(error_result)
                return overall_result

            # Load metadata
            try:
                metadata = ValidationHelper.load_metadata(metadata_path)
                self.logger.info(
                    f"Loaded metadata for {len(metadata.get('files', []))} files"
                )
            except Exception as e:
                error_result = ValidationResult(
                    step_name="Metadata Loading",
                    status=ValidationStatus.ERROR,
                    is_valid=False,
                )
                error_result.add_error(f"Failed to load metadata: {str(e)}")
                overall_result.add_step_result(error_result)
                return overall_result

            # Run validation steps
            self._run_validation_steps(codebase_path, metadata, overall_result)

            # Save report if requested
            if output_path and self.config.save_report:
                self._save_validation_report(overall_result, output_path)

            self.logger.info(
                f"Validation completed in {overall_result.total_execution_time:.2f}s - "
                f"Status: {overall_result.overall_status.value}, "
                f"Valid: {overall_result.is_valid}"
            )

        except Exception as e:
            self.logger.error(f"Validation failed with unexpected error: {e}")

            error_result = ValidationResult(
                step_name="Validation Process",
                status=ValidationStatus.ERROR,
                is_valid=False,
            )
            error_result.add_error(f"Unexpected validation error: {str(e)}")
            overall_result.add_step_result(error_result)

        return overall_result

    def _validate_inputs(self, codebase_path: str, metadata_path: str) -> list[str]:
        """Validate input paths and configuration."""
        errors = []

        # Check codebase path
        if not os.path.exists(codebase_path):
            errors.append(f"Codebase path does not exist: {codebase_path}")
        elif not os.path.isdir(codebase_path):
            errors.append(f"Codebase path is not a directory: {codebase_path}")

        # Check metadata path
        if not os.path.exists(metadata_path):
            errors.append(f"Metadata file does not exist: {metadata_path}")
        elif not os.path.isfile(metadata_path):
            errors.append(f"Metadata path is not a file: {metadata_path}")

        # Validate configuration
        config_errors = self.config.validate()
        errors.extend(config_errors)

        return errors

    def _run_validation_steps(
        self,
        codebase_path: str,
        metadata: Dict[str, Any],
        overall_result: OverallValidationResult,
    ):
        """Run all enabled validation steps."""

        # Step 1: Syntax Validation
        if self.config.enable_syntax_validation:
            try:
                self.logger.info("Running syntax validation...")
                syntax_result = self.syntax_validator.validate(codebase_path, metadata)
                overall_result.add_step_result(syntax_result)

                if not syntax_result.is_valid and self.config.stop_on_first_failure:
                    self.logger.warning("Stopping validation due to syntax errors")
                    return

            except Exception as e:
                self.logger.error(f"Syntax validation failed: {e}")
                error_result = ValidationResult(
                    step_name="Syntax Validation",
                    status=ValidationStatus.ERROR,
                    is_valid=False,
                )
                error_result.add_error(f"Syntax validation error: {str(e)}")
                overall_result.add_step_result(error_result)

        # Step 2: Test Validation
        if self.config.enable_test_validation:
            try:
                self.logger.info("Running test validation...")
                test_result = self.test_validator.validate(codebase_path, metadata)
                overall_result.add_step_result(test_result)

                if not test_result.is_valid and self.config.stop_on_first_failure:
                    self.logger.warning("Stopping validation due to test failures")
                    return

            except Exception as e:
                self.logger.error(f"Test validation failed: {e}")
                error_result = ValidationResult(
                    step_name="Test Validation",
                    status=ValidationStatus.ERROR,
                    is_valid=False,
                )
                error_result.add_error(f"Test validation error: {str(e)}")
                overall_result.add_step_result(error_result)

        # Step 3: AI Logic Validation
        if self.config.enable_ai_validation:
            try:
                self.logger.info("Running AI logic validation...")
                ai_result = self.ai_validator.validate(codebase_path, metadata)
                overall_result.add_step_result(ai_result)

            except Exception as e:
                self.logger.error(f"AI validation failed: {e}")
                error_result = ValidationResult(
                    step_name="AI Logic Validation",
                    status=ValidationStatus.ERROR,
                    is_valid=False,
                )
                error_result.add_error(f"AI validation error: {str(e)}")
                overall_result.add_step_result(error_result)

    def _save_validation_report(
        self, overall_result: OverallValidationResult, output_path: str
    ):
        """Save validation report to file."""
        try:
            report_data = overall_result.to_dict()

            # Determine output file path
            if os.path.isdir(output_path):
                filename = self.config.report_filename
                if not filename.endswith(f".{self.config.output_format}"):
                    filename = f"{filename}.{self.config.output_format}"
                output_file = os.path.join(output_path, filename)
            else:
                # If output_path is a file path, use it directly
                output_file = output_path
                # If it doesn't have an extension, add one
                if not output_file.endswith(f".{self.config.output_format}"):
                    output_file = f"{output_file}.{self.config.output_format}"

            ValidationHelper.save_report(
                report_data, output_file, self.config.output_format
            )

            self.logger.info(f"Validation report saved to: {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save validation report: {e}")

    def validate_single_step(
        self, step_name: str, codebase_path: str, metadata_path: str
    ) -> ValidationResult:
        """
        Run a single validation step.

        Args:
            step_name: Name of validation step ("syntax", "test", or "ai")
            codebase_path: Path to codebase
            metadata_path: Path to metadata file

        Returns:
            ValidationResult for the specific step
        """
        try:
            metadata = ValidationHelper.load_metadata(metadata_path)
        except Exception as e:
            result = ValidationResult(
                step_name=f"{step_name.title()} Validation",
                status=ValidationStatus.ERROR,
                is_valid=False,
            )
            result.add_error(f"Failed to load metadata: {str(e)}")
            return result

        if step_name.lower() == "syntax" and self.config.enable_syntax_validation:
            return self.syntax_validator.validate(codebase_path, metadata)
        elif step_name.lower() == "test" and self.config.enable_test_validation:
            return self.test_validator.validate(codebase_path, metadata)
        elif step_name.lower() == "ai" and self.config.enable_ai_validation:
            return self.ai_validator.validate(codebase_path, metadata)
        else:
            result = ValidationResult(
                step_name=f"{step_name.title()} Validation",
                status=ValidationStatus.ERROR,
                is_valid=False,
            )
            result.add_error(f"Unknown or disabled validation step: {step_name}")
            return result

    def get_validation_summary(self, overall_result: OverallValidationResult) -> str:
        """
        Generate a human-readable summary of validation results.

        Args:
            overall_result: Overall validation result

        Returns:
            String summary of validation results
        """
        summary_lines = []

        # Header
        summary_lines.append("VALIDATION SUMMARY")
        summary_lines.append("=" * 50)
        summary_lines.append("")

        # Overall status
        status_emoji = "✅" if overall_result.is_valid else "❌"
        summary_lines.append(
            f"{status_emoji} Overall Status: {overall_result.overall_status.value.upper()}"
        )
        summary_lines.append(f"Valid: {overall_result.is_valid}")
        summary_lines.append(f"Total Errors: {overall_result.total_error_count()}")
        summary_lines.append(f"Total Warnings: {overall_result.total_warning_count()}")
        summary_lines.append(
            f"Execution Time: {overall_result.total_execution_time:.2f}s"
        )
        summary_lines.append("")

        # Step results
        summary_lines.append("STEP RESULTS:")
        summary_lines.append("-" * 30)

        for step_result in overall_result.step_results:
            step_emoji = "✅" if step_result.is_valid else "❌"
            summary_lines.append(f"{step_emoji} {step_result.step_name}")
            summary_lines.append(f"   Status: {step_result.status.value}")
            summary_lines.append(f"   Errors: {step_result.error_count()}")
            summary_lines.append(f"   Warnings: {step_result.warning_count()}")
            summary_lines.append(f"   Time: {step_result.execution_time:.2f}s")

            # Show top problems
            errors = step_result.get_errors()[:3]  # Top 3 errors
            for error in errors:
                location = f" ({error.file_path})" if error.file_path else ""
                summary_lines.append(f"   🔴 {error.message}{location}")

            if step_result.error_count() > 3:
                summary_lines.append(
                    f"   ... and {step_result.error_count() - 3} more errors"
                )

            summary_lines.append("")

        return "\n".join(summary_lines)
