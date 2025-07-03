import pytest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from CodeFromRequirements.code_validator import CodeValidator, ValidationResult


class TestCodeValidator:
    """Test cases for CodeValidator class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        self.sample_changes = {
            "files_created": ["auth/models.py", "auth/services.py"],
            "files_modified": ["function_app.py"],
            "errors": [],
        }

        self.valid_python_code = """
import json
from typing import Dict, List

class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "username": self.username,
            "email": self.email
        }

def validate_user(user_data: Dict) -> bool:
    required_fields = ["username", "email"]
    return all(field in user_data for field in required_fields)
"""

        self.invalid_python_code = """
def invalid_syntax(
    print("Missing closing parenthesis")
    return True
"""

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.code_validator.Config")
    def test_initialization(self, mock_config):
        """Test CodeValidator initialization"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        validator = CodeValidator()

        assert validator.codebase_root == self.temp_dir
        assert validator.python_formatter == "black"
        assert validator.linter == "flake8"
        assert validator.test_command == "pytest"
        assert validator.validation_timeout == 300

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validate_syntax_valid_python(self, mock_config):
        """Test syntax validation with valid Python code"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Create valid Python file
        test_file = os.path.join(self.temp_dir, "valid.py")
        with open(test_file, "w") as f:
            f.write(self.valid_python_code)

        validator = CodeValidator()
        errors = validator._validate_syntax([test_file])

        # Should have no syntax errors
        assert len(errors) == 0

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validate_syntax_invalid_python(self, mock_config):
        """Test syntax validation with invalid Python code"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Create invalid Python file
        test_file = os.path.join(self.temp_dir, "invalid.py")
        with open(test_file, "w") as f:
            f.write(self.invalid_python_code)

        validator = CodeValidator()
        errors = validator._validate_syntax([test_file])

        # Should have syntax errors
        assert len(errors) > 0
        assert (
            "syntax error" in errors[0].lower() or "invalid syntax" in errors[0].lower()
        )

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_run_linter_success(self, mock_subprocess, mock_config):
        """Test running linter with successful result"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Mock successful flake8 run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write(self.valid_python_code)

        validator = CodeValidator()
        warnings = validator._run_linter([test_file])

        # Should have no warnings
        assert len(warnings) == 0
        mock_subprocess.assert_called_once()

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_run_linter_with_warnings(self, mock_subprocess, mock_config):
        """Test running linter with warnings"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Mock flake8 run with warnings
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "test.py:10:80: E501 line too long (85 > 79 characters)"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write(self.valid_python_code)

        validator = CodeValidator()
        warnings = validator._run_linter([test_file])

        # Should have warnings
        assert len(warnings) > 0
        assert "E501" in warnings[0]

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_format_code_success(self, mock_subprocess, mock_config):
        """Test code formatting with black"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Mock successful black run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "reformatted test.py"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Create test file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write(self.valid_python_code)

        validator = CodeValidator()
        formatted_files = validator._format_code([test_file])

        # Should have formatted files
        assert len(formatted_files) == 1
        assert test_file in formatted_files
        mock_subprocess.assert_called_once()

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_run_tests_success(self, mock_subprocess, mock_config):
        """Test running tests with pytest"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Mock successful pytest run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "5 passed, 0 failed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        validator = CodeValidator()
        test_results = validator._run_tests()

        # Should have successful test results
        assert test_results["success"] is True
        assert test_results["tests_passed"] >= 0
        assert test_results["tests_failed"] == 0
        mock_subprocess.assert_called_once()

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_run_tests_failure(self, mock_subprocess, mock_config):
        """Test running tests with failures"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Mock failed pytest run
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "2 passed, 3 failed"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        validator = CodeValidator()
        test_results = validator._run_tests()

        # Should have failed test results
        assert test_results["success"] is False
        assert test_results["tests_failed"] > 0

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validate_changes_success(self, mock_config):
        """Test overall validation with successful changes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Create valid test files
        for file_path in self.sample_changes["files_created"]:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(self.valid_python_code)

        validator = CodeValidator()

        # Mock subprocess calls for linter, formatter, and tests
        with patch("subprocess.run") as mock_subprocess:
            # Mock successful subprocess calls
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "All checks passed"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result

            result = validator.validate_changes(self.sample_changes)

        # Should return valid result
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validate_changes_with_syntax_errors(self, mock_config):
        """Test validation with syntax errors"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Create invalid test file
        invalid_file = os.path.join(self.temp_dir, "invalid.py")
        with open(invalid_file, "w") as f:
            f.write(self.invalid_python_code)

        changes_with_invalid = {
            "files_created": ["invalid.py"],
            "files_modified": [],
            "errors": [],
        }

        validator = CodeValidator()
        result = validator.validate_changes(changes_with_invalid)

        # Should return invalid result due to syntax errors
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0

    @patch("CodeFromRequirements.code_validator.Config")
    def test_get_affected_files(self, mock_config):
        """Test getting list of affected files"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        validator = CodeValidator()
        affected_files = validator._get_affected_files(self.sample_changes)

        # Should include all created and modified files
        expected_files = (
            self.sample_changes["files_created"] + self.sample_changes["files_modified"]
        )

        for file_path in expected_files:
            full_path = os.path.join(self.temp_dir, file_path)
            assert full_path in affected_files

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validation_result_properties(self, mock_config):
        """Test ValidationResult properties"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir

        # Test valid result
        valid_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
            formatted_files=["test.py"],
            test_results={"tests_passed": 5, "tests_failed": 0},
        )

        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0
        assert len(valid_result.warnings) == 1
        assert len(valid_result.formatted_files) == 1
        assert valid_result.test_results["tests_passed"] == 5

        # Test invalid result
        invalid_result = ValidationResult(
            is_valid=False,
            errors=["Syntax error"],
            warnings=[],
            formatted_files=[],
            test_results={"tests_passed": 0, "tests_failed": 1},
        )

        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) == 1
        assert invalid_result.test_results["tests_failed"] == 1

    @patch("CodeFromRequirements.code_validator.Config")
    def test_validate_changes_empty_changes(self, mock_config):
        """Test validation with no changes"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        empty_changes = {"files_created": [], "files_modified": [], "errors": []}

        validator = CodeValidator()
        result = validator.validate_changes(empty_changes)

        # Should handle empty changes gracefully
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

    @patch("CodeFromRequirements.code_validator.Config")
    @patch("subprocess.run")
    def test_subprocess_timeout_handling(self, mock_subprocess, mock_config):
        """Test handling of subprocess timeouts"""
        mock_config.return_value.CODEBASE_ROOT = self.temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 1  # Short timeout

        # Mock subprocess timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("pytest", 1)

        validator = CodeValidator()
        test_results = validator._run_tests()

        # Should handle timeout gracefully
        assert test_results["success"] is False
        assert "timeout" in test_results.get("error", "").lower()


class TestCodeValidatorEdgeCases:
    """Test edge cases and error scenarios"""

    @patch("CodeFromRequirements.code_validator.Config")
    def test_non_existent_files(self, mock_config):
        """Test handling of non-existent files"""
        temp_dir = tempfile.mkdtemp()
        mock_config.return_value.CODEBASE_ROOT = temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        changes_with_missing = {
            "files_created": ["non_existent.py"],
            "files_modified": ["also_missing.py"],
            "errors": [],
        }

        validator = CodeValidator()
        result = validator.validate_changes(changes_with_missing)

        # Should handle missing files gracefully
        assert isinstance(result, ValidationResult)

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("CodeFromRequirements.code_validator.Config")
    def test_binary_files_handling(self, mock_config):
        """Test handling of binary files"""
        temp_dir = tempfile.mkdtemp()
        mock_config.return_value.CODEBASE_ROOT = temp_dir
        mock_config.return_value.PYTHON_FORMATTER = "black"
        mock_config.return_value.LINTER = "flake8"
        mock_config.return_value.TEST_COMMAND = "pytest"
        mock_config.return_value.VALIDATION_TIMEOUT = 300

        # Create a binary file
        binary_file = os.path.join(temp_dir, "image.png")
        with open(binary_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

        changes_with_binary = {
            "files_created": ["image.png"],
            "files_modified": [],
            "errors": [],
        }

        validator = CodeValidator()
        result = validator.validate_changes(changes_with_binary)

        # Should handle binary files (skip syntax validation)
        assert isinstance(result, ValidationResult)

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
