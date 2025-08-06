"""
Test validation component for running and analyzing test cases.
"""

import os
import time
import logging
import subprocess
from typing import Dict, Any, List, Tuple
from pathlib import Path

from ..models.validation_result import ValidationResult, ValidationStatus
from ..utils.helpers import ValidationHelper
from ..utils.config import ValidationConfig


class TestValidator:
    """Validates test cases and their execution."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def validate(
        self, codebase_path: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate test cases in the codebase.

        Args:
            codebase_path: Path to the codebase directory
            metadata: Metadata about the codebase

        Returns:
            ValidationResult with test validation results
        """
        start_time = time.time()
        result = ValidationResult(
            step_name="Test Validation", status=ValidationStatus.VALID, is_valid=True
        )

        try:
            self.logger.info("Starting test validation")

            # Find test files
            test_files = self._find_test_files(codebase_path)

            if not test_files:
                result.add_warning("No test files found in the codebase")
                result.metadata["test_files_found"] = 0
                result.metadata["tests_executed"] = 0
                return result

            self.logger.info(f"Found {len(test_files)} test files")

            # Check test structure
            self._validate_test_structure(test_files, result)

            # Run tests
            test_results = self._run_tests(codebase_path, result)

            # Analyze coverage if available
            coverage_info = self._analyze_coverage(codebase_path, result)

            # Set metadata
            result.metadata.update(
                {
                    "test_files_found": len(test_files),
                    "test_files": [
                        str(Path(f).relative_to(codebase_path)) for f in test_files
                    ],
                    "test_framework": self._detect_test_framework(codebase_path),
                    "coverage_info": coverage_info,
                    **test_results,
                }
            )

            self.logger.info("Test validation completed")

        except Exception as e:
            result.add_error(f"Test validation failed: {str(e)}")
            result.status = ValidationStatus.ERROR
            self.logger.error(f"Test validation error: {e}")

        finally:
            result.execution_time = time.time() - start_time

        return result

    def _find_test_files(self, codebase_path: str) -> List[str]:
        """Find test files in the codebase."""
        return ValidationHelper.find_test_files(
            codebase_path, self.config.test_patterns, self.config.test_directories
        )

    def _validate_test_structure(self, test_files: List[str], result: ValidationResult):
        """Validate the structure of test files."""
        for test_file in test_files:
            try:
                self._check_test_file_structure(test_file, result)
            except Exception as e:
                result.add_warning(
                    f"Could not analyze test file structure: {str(e)}",
                    file_path=test_file,
                )

    def _check_test_file_structure(self, test_file: str, result: ValidationResult):
        """Check the structure of a single test file."""
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic checks
            if (
                "import unittest" not in content
                and "import pytest" not in content
                and "def test_" not in content
            ):
                result.add_warning(
                    "Test file doesn't appear to use a recognized test framework",
                    file_path=test_file,
                )

            # Count test functions
            test_function_count = content.count("def test_")
            if test_function_count == 0:
                result.add_warning(
                    "No test functions found (functions starting with 'test_')",
                    file_path=test_file,
                )

            # Check for docstrings in test functions
            if "def test_" in content and '"""' not in content and "'''" not in content:
                result.add_info(
                    "Consider adding docstrings to test functions for better documentation",
                    file_path=test_file,
                )

        except Exception as e:
            self.logger.debug(f"Error checking test file structure {test_file}: {e}")

    def _run_tests(
        self, codebase_path: str, result: ValidationResult
    ) -> Dict[str, Any]:
        """Run the test suite."""
        test_results = {
            "tests_executed": False,
            "test_runner": None,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "test_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
        }

        try:
            # Try pytest first, then unittest
            runner_results = self._try_pytest(codebase_path) or self._try_unittest(
                codebase_path
            )

            if runner_results:
                test_results.update(runner_results)
                test_results["tests_executed"] = True

                # Analyze results
                if test_results["exit_code"] == 0:
                    self.logger.info("All tests passed")
                else:
                    result.add_error(
                        f"Tests failed with exit code {test_results['exit_code']}",
                        error_code="TEST_FAILURE",
                    )

                    # Parse failure details from stderr/stdout
                    self._parse_test_failures(test_results, result)
            else:
                result.add_warning(
                    "Could not run tests - no suitable test runner found"
                )

        except Exception as e:
            result.add_error(f"Error running tests: {str(e)}")
            self.logger.error(f"Test execution error: {e}")

        return test_results

    def _try_pytest(self, codebase_path: str) -> Dict[str, Any]:
        """Try to run tests with pytest."""
        try:
            # Check if pytest is available
            check_cmd = ["python", "-m", "pytest", "--version"]
            exit_code, _, _ = ValidationHelper.run_command(
                check_cmd, cwd=codebase_path, timeout=10
            )

            if exit_code != 0:
                return None

            # Run pytest
            pytest_args = ["python", "-m", "pytest"] + self.config.pytest_args
            exit_code, stdout, stderr = ValidationHelper.run_command(
                pytest_args, cwd=codebase_path, timeout=self.config.test_timeout
            )

            # Parse pytest output
            test_stats = self._parse_pytest_output(stdout)

            return {
                "test_runner": "pytest",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                **test_stats,
            }

        except Exception as e:
            self.logger.debug(f"Could not run pytest: {e}")
            return None

    def _try_unittest(self, codebase_path: str) -> Dict[str, Any]:
        """Try to run tests with unittest."""
        try:
            # Run unittest discovery
            cmd = ["python", "-m", "unittest", "discover", "-v"]
            exit_code, stdout, stderr = ValidationHelper.run_command(
                cmd, cwd=codebase_path, timeout=self.config.test_timeout
            )

            # Parse unittest output
            test_stats = self._parse_unittest_output(stdout, stderr)

            return {
                "test_runner": "unittest",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                **test_stats,
            }

        except Exception as e:
            self.logger.debug(f"Could not run unittest: {e}")
            return None

    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test statistics."""
        stats = {
            "test_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
        }

        try:
            lines = output.split("\n")
            for line in lines:
                line = line.strip()

                # Look for result summary line
                if " passed" in line or " failed" in line or " skipped" in line:
                    # Example: "5 passed, 2 failed, 1 skipped in 0.05s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            stats["passed_count"] = int(parts[i - 1])
                        elif part == "failed" and i > 0:
                            stats["failed_count"] = int(parts[i - 1])
                        elif part == "skipped" and i > 0:
                            stats["skipped_count"] = int(parts[i - 1])

            stats["test_count"] = (
                stats["passed_count"] + stats["failed_count"] + stats["skipped_count"]
            )

        except Exception as e:
            self.logger.debug(f"Could not parse pytest output: {e}")

        return stats

    def _parse_unittest_output(self, stdout: str, stderr: str) -> Dict[str, int]:
        """Parse unittest output to extract test statistics."""
        stats = {
            "test_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
        }

        try:
            # Combine stdout and stderr
            output = stdout + stderr
            lines = output.split("\n")

            for line in lines:
                line = line.strip()

                # Look for result summary
                if line.startswith("Ran ") and " test" in line:
                    # Example: "Ran 5 tests in 0.001s"
                    parts = line.split()
                    if len(parts) >= 2:
                        stats["test_count"] = int(parts[1])

                # Look for failure/error info
                if "FAILED" in line and "failures=" in line:
                    # Parse failures and errors
                    if "failures=" in line:
                        start = line.find("failures=") + 9
                        end = (
                            line.find(",", start) if "," in line[start:] else len(line)
                        )
                        stats["failed_count"] = int(line[start:end])

            # Assume passed = total - failed - skipped
            stats["passed_count"] = (
                stats["test_count"] - stats["failed_count"] - stats["skipped_count"]
            )

        except Exception as e:
            self.logger.debug(f"Could not parse unittest output: {e}")

        return stats

    def _parse_test_failures(
        self, test_results: Dict[str, Any], result: ValidationResult
    ):
        """Parse test failure details."""
        stderr = test_results.get("stderr", "")
        stdout = test_results.get("stdout", "")

        # Look for specific failure patterns
        failure_patterns = ["FAILED", "ERROR", "AssertionError", "Exception"]

        output_lines = (stderr + stdout).split("\n")

        for line_num, line in enumerate(output_lines):
            for pattern in failure_patterns:
                if pattern in line:
                    # Try to extract file and line info
                    file_info = self._extract_file_info_from_traceback(
                        output_lines, line_num
                    )

                    result.add_error(
                        f"Test failure: {line.strip()}",
                        file_path=file_info.get("file"),
                        line_number=file_info.get("line"),
                        error_code="TEST_FAILURE",
                    )
                    break

    def _extract_file_info_from_traceback(
        self, lines: List[str], start_line: int
    ) -> Dict[str, Any]:
        """Extract file and line information from traceback."""
        file_info = {"file": None, "line": None}

        try:
            # Look backwards for file references
            for i in range(max(0, start_line - 10), start_line):
                line = lines[i].strip()
                if 'File "' in line and "line " in line:
                    # Example: File "/path/to/file.py", line 10, in function_name
                    parts = line.split('"')
                    if len(parts) >= 2:
                        file_info["file"] = parts[1]

                    line_part = line.split("line ")
                    if len(line_part) >= 2:
                        line_num_str = line_part[1].split(",")[0]
                        try:
                            file_info["line"] = int(line_num_str)
                        except ValueError:
                            pass
                    break
        except Exception:
            pass

        return file_info

    def _analyze_coverage(
        self, codebase_path: str, result: ValidationResult
    ) -> Dict[str, Any]:
        """Analyze test coverage if available."""
        coverage_info = {
            "coverage_available": False,
            "coverage_percentage": 0.0,
            "meets_requirement": True,
        }

        try:
            # Check for coverage files
            coverage_files = [".coverage", "coverage.xml", "htmlcov/index.html"]

            coverage_file_found = None
            for cov_file in coverage_files:
                full_path = os.path.join(codebase_path, cov_file)
                if os.path.exists(full_path):
                    coverage_file_found = cov_file
                    break

            if coverage_file_found:
                coverage_info["coverage_available"] = True

                # Try to run coverage report
                try:
                    cmd = ["python", "-m", "coverage", "report", "--show-missing"]
                    exit_code, stdout, stderr = ValidationHelper.run_command(
                        cmd, cwd=codebase_path, timeout=30
                    )

                    if exit_code == 0:
                        coverage_percentage = self._parse_coverage_output(stdout)
                        coverage_info["coverage_percentage"] = coverage_percentage

                        if coverage_percentage < self.config.required_test_coverage:
                            coverage_info["meets_requirement"] = False
                            result.add_warning(
                                f"Test coverage ({coverage_percentage:.1f}%) below required threshold ({self.config.required_test_coverage:.1f}%)",
                                error_code="LOW_COVERAGE",
                            )
                        else:
                            result.add_info(
                                f"Test coverage: {coverage_percentage:.1f}%"
                            )

                except Exception as e:
                    self.logger.debug(f"Could not run coverage report: {e}")

        except Exception as e:
            self.logger.debug(f"Error analyzing coverage: {e}")

        return coverage_info

    def _parse_coverage_output(self, output: str) -> float:
        """Parse coverage percentage from coverage report output."""
        try:
            lines = output.split("\n")
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    # Look for percentage in the line
                    parts = line.split()
                    for part in parts:
                        if part.endswith("%"):
                            return float(part[:-1])
        except Exception:
            pass

        return 0.0

    def _detect_test_framework(self, codebase_path: str) -> str:
        """Detect which test framework is being used."""
        frameworks = []

        # Check for pytest
        try:
            cmd = ["python", "-m", "pytest", "--version"]
            exit_code, _, _ = ValidationHelper.run_command(
                cmd, cwd=codebase_path, timeout=5
            )
            if exit_code == 0:
                frameworks.append("pytest")
        except Exception:
            pass

        # Check for unittest (always available)
        frameworks.append("unittest")

        return ", ".join(frameworks)
