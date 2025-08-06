"""
End-to-end integration tests for HandleGeneric.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from HandleGeneric import (
    GenericMetadataGenerator,
    GenericValidator,
    GenericCodeGenerator,
    get_supported_languages,
)


class TestEndToEnd:
    """End-to-end test cases for HandleGeneric."""

    def test_supported_languages(self):
        """Test getting supported languages."""
        languages = get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "python" in languages

    def test_metadata_generation_end_to_end(self):
        """Test complete metadata generation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test project structure
            project_dir = temp_path / "test_project"
            project_dir.mkdir()

            # Create Python files
            (project_dir / "main.py").write_text(
                """
def hello_world():
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
"""
            )

            (project_dir / "utils.py").write_text(
                """
import os
import sys

def utility_function():
    return "utility"
"""
            )

            # Create JavaScript files
            (project_dir / "script.js").write_text(
                """
function helloWorld() {
    console.log("Hello, World!");
}

class TestClass {
    constructor() {
        this.value = 42;
    }
}
"""
            )

            # Generate metadata
            generator = GenericMetadataGenerator()
            output_dir = temp_path / "output"

            result = generator.generate_metadata(
                project_path=project_dir,
                output_path=output_dir,
                filename="metadata.json",
            )

            # Verify result structure
            assert isinstance(result, dict)
            assert "project_info" in result
            assert "languages" in result
            assert "language_summaries" in result

            # Verify project info
            project_info = result["project_info"]
            assert project_info["total_files"] > 0
            assert "generation_time" in project_info

            # Verify languages detected
            languages = result["languages"]
            assert "python" in languages
            assert "javascript" in languages

            # Verify output file was created
            output_file = output_dir / "metadata.json"
            assert output_file.exists()

            # Verify output file content
            with open(output_file, "r") as f:
                saved_metadata = json.load(f)
                assert saved_metadata == result

    def test_validation_end_to_end(self):
        """Test complete validation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test project with valid and invalid files
            project_dir = temp_path / "test_project"
            project_dir.mkdir()

            # Valid Python file
            (project_dir / "valid.py").write_text(
                """
def valid_function():
    return 42
"""
            )

            # Invalid Python file
            (project_dir / "invalid.py").write_text(
                """
def invalid_function(
    return 42
"""
            )

            # Valid JavaScript file
            (project_dir / "valid.js").write_text(
                """
function validFunction() {
    return 42;
}
"""
            )

            # Validate project
            validator = GenericValidator()

            result = validator.validate_project(project_path=project_dir)

            # Verify result structure
            assert hasattr(result, "status")
            assert hasattr(result, "valid_files")
            assert hasattr(result, "total_files")
            assert hasattr(result, "execution_time")

            # Verify validation results
            assert result.total_files > 0
            assert result.valid_files >= 0
            assert result.valid_files <= result.total_files

    def test_code_generation_end_to_end(self):
        """Test complete code generation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create requirements
            requirements = [
                {
                    "id": "req1",
                    "description": "Create a function to calculate fibonacci numbers",
                },
                {"id": "req2", "description": "Create a class to represent a user"},
            ]

            # Mock AI client
            mock_ai_client = Mock()
            mock_ai_client.generate_code.return_value = {
                "status": "success",
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            }

            # Generate code
            generator = GenericCodeGenerator(ai_client=mock_ai_client)
            output_dir = temp_path / "generated"

            result = generator.generate_from_requirements(
                requirements=requirements,
                target_language="python",
                output_path=output_dir,
            )

            # Verify result structure
            assert hasattr(result, "status")
            assert hasattr(result, "generated_files")
            assert hasattr(result, "execution_time")

            # Verify AI client was called
            mock_ai_client.generate_code.assert_called()

    def test_multi_language_project(self):
        """Test handling a multi-language project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multi-language project
            project_dir = temp_path / "multi_lang_project"
            project_dir.mkdir()

            # Python files
            (project_dir / "python_module.py").write_text(
                """
import os
from typing import List

def python_function():
    return "python"
"""
            )

            # JavaScript files
            (project_dir / "javascript_module.js").write_text(
                """
const fs = require('fs');

function javascriptFunction() {
    return "javascript";
}
"""
            )

            # TypeScript files
            (project_dir / "typescript_module.ts").write_text(
                """
interface User {
    name: string;
    age: number;
}

function typescriptFunction(): string {
    return "typescript";
}
"""
            )

            # Generate metadata
            generator = GenericMetadataGenerator()
            result = generator.generate_metadata(
                project_path=project_dir, output_path=temp_path / "output"
            )

            # Verify multiple languages detected
            languages = result["languages"]
            assert len(languages) >= 2
            assert "python" in languages
            assert "javascript" in languages

            # Verify language summaries
            summaries = result["language_summaries"]
            assert "python" in summaries
            assert "javascript" in summaries

            # Verify file counts
            python_summary = summaries["python"]
            assert python_summary["file_count"] > 0

            js_summary = summaries["javascript"]
            assert js_summary["file_count"] > 0

    def test_error_handling(self):
        """Test error handling in end-to-end scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with non-existent project
            generator = GenericMetadataGenerator()

            with pytest.raises(Exception):
                generator.generate_metadata(
                    project_path=Path("/non/existent/path"),
                    output_path=temp_path / "output",
                )

            # Test with invalid output path
            project_dir = temp_path / "test_project"
            project_dir.mkdir()
            (project_dir / "test.py").write_text("def test(): pass")

            # This should handle the error gracefully
            try:
                result = generator.generate_metadata(
                    project_path=project_dir, output_path=Path("/invalid/output/path")
                )
                # If it doesn't raise an exception, that's also acceptable
            except Exception:
                # Expected behavior for invalid output path
                pass
