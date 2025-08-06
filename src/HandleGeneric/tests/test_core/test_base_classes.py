"""
Tests for HandleGeneric core base classes.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from HandleGeneric.core.base.generator import GenericMetadataGenerator
from HandleGeneric.core.base.validator import GenericValidator
from HandleGeneric.core.base.code_generator import GenericCodeGenerator


class TestGenericMetadataGenerator:
    """Test cases for GenericMetadataGenerator."""

    def test_init(self):
        """Test initialization of GenericMetadataGenerator."""
        generator = GenericMetadataGenerator()
        assert generator is not None
        assert hasattr(generator, "exclude_patterns")

    def test_init_with_exclude_patterns(self):
        """Test initialization with exclude patterns."""
        exclude_patterns = ["*.pyc", "__pycache__"]
        generator = GenericMetadataGenerator(exclude_patterns=exclude_patterns)
        assert generator.exclude_patterns == exclude_patterns

    @patch("HandleGeneric.core.base.generator.Path")
    def test_generate_metadata_basic(self, mock_path):
        """Test basic metadata generation."""
        generator = GenericMetadataGenerator()

        # Mock project path
        mock_project_path = Mock()
        mock_project_path.exists.return_value = True
        mock_project_path.is_dir.return_value = True

        # Mock output path
        mock_output_path = Mock()
        mock_output_path.exists.return_value = False

        with patch("HandleGeneric.core.base.generator.FileDetector") as mock_detector:
            mock_detector.return_value.detect_languages.return_value = ["python"]

            result = generator.generate_metadata(
                project_path=mock_project_path,
                output_path=mock_output_path,
                filename="metadata.json",
            )

            assert isinstance(result, dict)
            assert "project_info" in result
            assert "languages" in result


class TestGenericValidator:
    """Test cases for GenericValidator."""

    def test_init(self):
        """Test initialization of GenericValidator."""
        validator = GenericValidator()
        assert validator is not None
        assert hasattr(validator, "exclude_patterns")

    def test_init_with_exclude_patterns(self):
        """Test initialization with exclude patterns."""
        exclude_patterns = ["*.pyc", "__pycache__"]
        validator = GenericValidator(exclude_patterns=exclude_patterns)
        assert validator.exclude_patterns == exclude_patterns

    @patch("HandleGeneric.core.base.validator.Path")
    def test_validate_project_basic(self, mock_path):
        """Test basic project validation."""
        validator = GenericValidator()

        # Mock project path
        mock_project_path = Mock()
        mock_project_path.exists.return_value = True
        mock_project_path.is_dir.return_value = True

        with patch("HandleGeneric.core.base.validator.FileDetector") as mock_detector:
            mock_detector.return_value.detect_languages.return_value = ["python"]

            result = validator.validate_project(project_path=mock_project_path)

            assert hasattr(result, "status")
            assert hasattr(result, "valid_files")
            assert hasattr(result, "total_files")
            assert hasattr(result, "execution_time")


class TestGenericCodeGenerator:
    """Test cases for GenericCodeGenerator."""

    def test_init(self):
        """Test initialization of GenericCodeGenerator."""
        generator = GenericCodeGenerator()
        assert generator is not None
        assert hasattr(generator, "ai_client")

    def test_init_with_ai_client(self):
        """Test initialization with AI client."""
        mock_ai_client = Mock()
        generator = GenericCodeGenerator(ai_client=mock_ai_client)
        assert generator.ai_client == mock_ai_client

    @patch("HandleGeneric.core.base.code_generator.Path")
    def test_generate_from_requirements_basic(self, mock_path):
        """Test basic code generation from requirements."""
        generator = GenericCodeGenerator()

        # Mock requirements
        requirements = [
            {"id": "req1", "description": "Create a function to calculate fibonacci"}
        ]

        # Mock output path
        mock_output_path = Mock()
        mock_output_path.exists.return_value = False

        with patch(
            "HandleGeneric.core.base.code_generator.LanguageRegistry"
        ) as mock_registry:
            mock_provider = Mock()
            mock_registry.return_value.get_provider.return_value = mock_provider
            mock_provider.generate_code.return_value = {"status": "success"}

            result = generator.generate_from_requirements(
                requirements=requirements,
                target_language="python",
                output_path=mock_output_path,
            )

            assert hasattr(result, "status")
            assert hasattr(result, "generated_files")
            assert hasattr(result, "execution_time")
