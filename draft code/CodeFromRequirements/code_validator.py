import subprocess
import os
import sys
from typing import List, Dict, Any, NamedTuple
from config import Config
import logging


class ValidationResult(NamedTuple):
    """Result of code validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    test_results: Dict[str, Any]


class CodeValidator:
    """Validates code changes using linting, syntax checking, and testing"""

    def __init__(self):
        self.config = Config()

    def validate_changes(self, changes_made: Dict[str, Any]) -> ValidationResult:
        """
        Validate all code changes

        Returns:
            ValidationResult with validation status and details
        """
        all_errors = []
        all_warnings = []
        test_results = {}

        files_to_validate = changes_made.get("files_created", []) + changes_made.get(
            "files_modified", []
        )

        try:
            # Validate each file
            for file_path in files_to_validate:
                if os.path.exists(file_path):
                    validation = self._validate_single_file(file_path)
                    all_errors.extend(validation.errors)
                    all_warnings.extend(validation.warnings)

                    # Collect test results
                    if validation.test_results:
                        test_results[file_path] = validation.test_results

            # Run integration tests if any
            if files_to_validate:
                integration_result = self._run_integration_tests()
                test_results["integration"] = integration_result

                if not integration_result.get("success", True):
                    all_errors.extend(integration_result.get("errors", []))

            is_valid = len(all_errors) == 0

            return ValidationResult(
                is_valid=is_valid,
                errors=all_errors,
                warnings=all_warnings,
                test_results=test_results,
            )

        except Exception as e:
            logging.error(f"Error during validation: {str(e)}")
            return ValidationResult(
                is_valid=False, errors=[str(e)], warnings=[], test_results={}
            )

    def _validate_single_file(self, file_path: str) -> ValidationResult:
        """Validate a single file"""
        errors = []
        warnings = []
        test_results = {}

        if file_path.endswith(".py"):
            # Python-specific validation

            # Syntax check
            syntax_errors = self._check_python_syntax(file_path)
            errors.extend(syntax_errors)

            # Linting with flake8
            lint_errors, lint_warnings = self._run_flake8(file_path)
            errors.extend(lint_errors)
            warnings.extend(lint_warnings)

            # Code formatting check with black
            format_warnings = self._check_black_formatting(file_path)
            warnings.extend(format_warnings)

            # Run unit tests for this file
            test_results = self._run_unit_tests_for_file(file_path)
            if not test_results.get("success", True):
                errors.extend(test_results.get("errors", []))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            test_results=test_results,
        )

    def _check_python_syntax(self, file_path: str) -> List[str]:
        """Check Python file syntax"""
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try to compile the file
            compile(content, file_path, "exec")
            logging.info(f"Syntax check passed for {file_path}")

        except SyntaxError as e:
            error_msg = f"Syntax error in {file_path}: {e.msg} at line {e.lineno}"
            errors.append(error_msg)
            logging.error(f"{error_msg}")

        except Exception as e:
            error_msg = f"Error checking syntax of {file_path}: {str(e)}"
            errors.append(error_msg)
            logging.error(f"{error_msg}")

        return errors

    def _run_flake8(self, file_path: str) -> tuple[List[str], List[str]]:
        """Run flake8 linting on a file"""
        errors = []
        warnings = []

        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", file_path, "--max-line-length=88"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logging.info(f"Flake8 linting passed for {file_path}")
            else:
                # Parse flake8 output
                for line in result.stdout.strip().split("\n"):
                    if line:
                        if any(code in line for code in ["E9", "F821", "F822", "F823"]):
                            errors.append(f"Flake8 error: {line}")
                        else:
                            warnings.append(f"Flake8 warning: {line}")

                if errors:
                    logging.warning(f"Flake8 found errors in {file_path}")
                else:
                    logging.info(f"Flake8 passed with warnings for {file_path}")

        except subprocess.TimeoutExpired:
            errors.append(f"Flake8 timeout for {file_path}")
        except FileNotFoundError:
            warnings.append("Flake8 not installed, skipping linting")
        except Exception as e:
            warnings.append(f"Error running flake8 on {file_path}: {str(e)}")

        return errors, warnings

    def _check_black_formatting(self, file_path: str) -> List[str]:
        """Check if file is formatted with black"""
        warnings = []

        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logging.info(f"Black formatting check passed for {file_path}")
            else:
                warnings.append(f"File {file_path} is not formatted with black")
                logging.info(f"File {file_path} could be reformatted with black")

        except subprocess.TimeoutExpired:
            warnings.append(f"Black formatting check timeout for {file_path}")
        except FileNotFoundError:
            warnings.append("Black not installed, skipping formatting check")
        except Exception as e:
            warnings.append(
                f"Error checking black formatting for {file_path}: {str(e)}"
            )

        return warnings

    def _run_unit_tests_for_file(self, file_path: str) -> Dict[str, Any]:
        """Run unit tests related to a specific file"""
        test_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
        }

        # Find corresponding test file
        test_file = self._find_test_file(file_path)

        if not test_file or not os.path.exists(test_file):
            test_results["warnings"].append(f"No test file found for {file_path}")
            return test_results

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=self.config.VALIDATION_TIMEOUT,
            )

            # Parse pytest output
            output_lines = result.stdout.split("\n")

            for line in output_lines:
                if "::" in line and "PASSED" in line:
                    test_results["tests_passed"] += 1
                elif "::" in line and "FAILED" in line:
                    test_results["tests_failed"] += 1
                    test_results["errors"].append(f"Test failed: {line}")

            test_results["tests_run"] = (
                test_results["tests_passed"] + test_results["tests_failed"]
            )

            if result.returncode == 0:
                logging.info(f"Unit tests passed for {file_path}")
            else:
                test_results["success"] = False
                logging.error(f"Unit tests failed for {file_path}")

                # Add error details
                if result.stderr:
                    test_results["errors"].append(result.stderr)

        except subprocess.TimeoutExpired:
            test_results["success"] = False
            test_results["errors"].append(f"Unit tests timeout for {file_path}")
        except FileNotFoundError:
            test_results["warnings"].append("Pytest not installed, skipping unit tests")
        except Exception as e:
            test_results["errors"].append(
                f"Error running unit tests for {file_path}: {str(e)}"
            )

        return test_results

    def _find_test_file(self, source_file: str) -> str:
        """Find the corresponding test file for a source file"""
        dir_name = os.path.dirname(source_file)
        base_name = os.path.basename(source_file)
        name_without_ext = os.path.splitext(base_name)[0]

        # Try different test file patterns
        test_patterns = [
            f"tests/test_{name_without_ext}.py",
            f"tests/{dir_name}/test_{name_without_ext}.py" if dir_name else None,
            f"test_{name_without_ext}.py",
            f"{dir_name}/test_{name_without_ext}.py" if dir_name else None,
        ]

        for pattern in test_patterns:
            if pattern and os.path.exists(pattern):
                return pattern

        return ""

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for the entire project"""
        test_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
        }

        try:
            # Run all tests in the tests directory
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=self.config.VALIDATION_TIMEOUT,
            )

            # Parse pytest output
            output_lines = result.stdout.split("\n")

            for line in output_lines:
                if "::" in line and "PASSED" in line:
                    test_results["tests_passed"] += 1
                elif "::" in line and "FAILED" in line:
                    test_results["tests_failed"] += 1

            test_results["tests_run"] = (
                test_results["tests_passed"] + test_results["tests_failed"]
            )

            if result.returncode == 0:
                logging.info("Integration tests passed")
            else:
                test_results["success"] = False
                logging.error("Integration tests failed")

                # Extract error details
                if result.stderr:
                    test_results["errors"].append(result.stderr)

        except subprocess.TimeoutExpired:
            test_results["success"] = False
            test_results["errors"].append("Integration tests timeout")
        except Exception as e:
            test_results["warnings"].append(
                f"Error running integration tests: {str(e)}"
            )

        return test_results

    def auto_fix_common_issues(self, file_path: str) -> bool:
        """Attempt to automatically fix common code issues"""
        try:
            # Auto-format with black
            if file_path.endswith(".py"):
                result = subprocess.run(
                    [sys.executable, "-m", "black", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    logging.info(f"Auto-formatted {file_path} with black")
                    return True
                else:
                    logging.warning(f"Could not auto-format {file_path}")

        except Exception as e:
            logging.error(f"Error auto-fixing {file_path}: {str(e)}")

        return False
