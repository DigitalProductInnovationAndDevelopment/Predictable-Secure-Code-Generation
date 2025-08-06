"""
Tests for HandleGeneric Python provider.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from HandleGeneric.providers.python.provider import PythonProvider


class TestPythonProvider:
    """Test cases for PythonProvider."""

    def test_init(self):
        """Test initialization of PythonProvider."""
        provider = PythonProvider()
        assert provider is not None
        assert provider.language_name == "python"
        assert ".py" in provider.file_extensions
        assert ".pyi" in provider.file_extensions
        assert "parsing" in provider.supported_features
        assert "validation" in provider.supported_features

    def test_parse_file_basic(self):
        """Test basic file parsing."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = True

        # Mock file content
        mock_content = """
def hello_world():
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
"""

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = provider.parse_file(mock_file)

            assert isinstance(result, dict)
            assert "status" in result
            assert "functions" in result
            assert "classes" in result
            assert "imports" in result

    def test_parse_file_with_imports(self):
        """Test parsing file with imports."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = True

        mock_content = """
import os
import sys
from pathlib import Path
from typing import List, Dict

def test_function():
    pass
"""

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = provider.parse_file(mock_file)

            assert result["status"] == "success"
            assert len(result["imports"]) > 0
            assert "os" in [imp["module"] for imp in result["imports"]]
            assert "sys" in [imp["module"] for imp in result["imports"]]

    def test_parse_file_with_classes(self):
        """Test parsing file with classes."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = True

        mock_content = """
class MyClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

class AnotherClass:
    pass
"""

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = provider.parse_file(mock_file)

            assert result["status"] == "success"
            assert len(result["classes"]) > 0
            assert "MyClass" in [cls["name"] for cls in result["classes"]]
            assert "AnotherClass" in [cls["name"] for cls in result["classes"]]

    def test_validate_file_valid_syntax(self):
        """Test validation of valid Python syntax."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = True

        mock_content = """
def valid_function():
    return 42

class ValidClass:
    def __init__(self):
        pass
"""

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = provider.validate_file(mock_file)

            assert result["status"] == "valid"
            assert len(result["errors"]) == 0

    def test_validate_file_invalid_syntax(self):
        """Test validation of invalid Python syntax."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = True

        mock_content = """
def invalid_function(
    return 42

class InvalidClass
    def __init__(self):
        pass
"""

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = provider.validate_file(mock_file)

            assert result["status"] == "invalid"
            assert len(result["errors"]) > 0

    def test_generate_code_basic(self):
        """Test basic code generation."""
        provider = PythonProvider()
        mock_output_path = Mock()
        mock_output_path.exists.return_value = False

        requirements = [
            {"id": "req1", "description": "Create a function to calculate fibonacci"}
        ]

        result = provider.generate_code(requirements, mock_output_path)

        assert isinstance(result, dict)
        assert "status" in result
        assert "files" in result

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        provider = PythonProvider()
        extensions = provider.get_supported_extensions()

        assert ".py" in extensions
        assert ".pyi" in extensions
        assert ".pyw" in extensions

    def test_is_supported_file(self):
        """Test checking if a file is supported."""
        provider = PythonProvider()

        # Test supported files
        mock_py_file = Mock()
        mock_py_file.suffix = ".py"
        assert provider.is_supported_file(mock_py_file) is True

        mock_pyi_file = Mock()
        mock_pyi_file.suffix = ".pyi"
        assert provider.is_supported_file(mock_pyi_file) is True

        # Test unsupported files
        mock_js_file = Mock()
        mock_js_file.suffix = ".js"
        assert provider.is_supported_file(mock_js_file) is False

    def test_parse_file_nonexistent(self):
        """Test parsing non-existent file."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = False

        result = provider.parse_file(mock_file)

        assert result["status"] == "error"
        assert "File does not exist" in result.get("message", "")

    def test_validate_file_nonexistent(self):
        """Test validating non-existent file."""
        provider = PythonProvider()
        mock_file = Mock()
        mock_file.exists.return_value = False

        result = provider.validate_file(mock_file)

        assert result["status"] == "error"
        assert "File does not exist" in result.get("message", "")
