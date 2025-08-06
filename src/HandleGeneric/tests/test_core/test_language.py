"""
Tests for HandleGeneric language-related core functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from HandleGeneric.core.language.registry import LanguageRegistry
from HandleGeneric.core.language.provider import LanguageProvider
from HandleGeneric.core.language.detector import FileDetector


class TestLanguageRegistry:
    """Test cases for LanguageRegistry."""

    def test_init(self):
        """Test initialization of LanguageRegistry."""
        registry = LanguageRegistry()
        assert registry is not None
        assert hasattr(registry, "providers")

    def test_register_provider(self):
        """Test registering a language provider."""
        registry = LanguageRegistry()
        mock_provider = Mock()
        mock_provider.language_name = "python"

        registry.register_provider(mock_provider)
        assert "python" in registry.providers
        assert registry.providers["python"] == mock_provider

    def test_get_provider(self):
        """Test getting a language provider."""
        registry = LanguageRegistry()
        mock_provider = Mock()
        mock_provider.language_name = "python"

        registry.register_provider(mock_provider)
        provider = registry.get_provider("python")
        assert provider == mock_provider

    def test_get_provider_not_found(self):
        """Test getting a non-existent provider."""
        registry = LanguageRegistry()

        with pytest.raises(KeyError):
            registry.get_provider("nonexistent")

    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        registry = LanguageRegistry()
        mock_provider1 = Mock()
        mock_provider1.language_name = "python"
        mock_provider2 = Mock()
        mock_provider2.language_name = "javascript"

        registry.register_provider(mock_provider1)
        registry.register_provider(mock_provider2)

        languages = registry.get_supported_languages()
        assert "python" in languages
        assert "javascript" in languages
        assert len(languages) == 2

    def test_get_supported_extensions(self):
        """Test getting list of supported extensions."""
        registry = LanguageRegistry()
        mock_provider = Mock()
        mock_provider.language_name = "python"
        mock_provider.get_supported_extensions.return_value = [".py", ".pyi"]

        registry.register_provider(mock_provider)
        extensions = registry.get_supported_extensions()
        assert ".py" in extensions
        assert ".pyi" in extensions


class TestLanguageProvider:
    """Test cases for LanguageProvider base class."""

    def test_init(self):
        """Test initialization of LanguageProvider."""
        provider = LanguageProvider()
        assert provider is not None
        assert hasattr(provider, "language_name")

    def test_abstract_methods(self):
        """Test that abstract methods are defined."""
        provider = LanguageProvider()

        # These should raise NotImplementedError when called
        with pytest.raises(NotImplementedError):
            provider.parse_file(Mock())

        with pytest.raises(NotImplementedError):
            provider.validate_file(Mock())

        with pytest.raises(NotImplementedError):
            provider.generate_code([], Mock())


class TestFileDetector:
    """Test cases for FileDetector."""

    def test_init(self):
        """Test initialization of FileDetector."""
        detector = FileDetector()
        assert detector is not None

    @patch("HandleGeneric.core.language.detector.Path")
    def test_detect_languages_basic(self, mock_path):
        """Test basic language detection."""
        detector = FileDetector()

        # Mock project path
        mock_project_path = Mock()
        mock_project_path.exists.return_value = True
        mock_project_path.is_dir.return_value = True

        # Mock file discovery
        mock_py_file = Mock()
        mock_py_file.suffix = ".py"
        mock_js_file = Mock()
        mock_js_file.suffix = ".js"

        mock_project_path.glob.return_value = [mock_py_file, mock_js_file]

        languages = detector.detect_languages(mock_project_path)
        assert isinstance(languages, list)
        assert len(languages) > 0

    def test_get_file_extension_language(self):
        """Test getting language from file extension."""
        detector = FileDetector()

        # Test Python files
        assert detector.get_language_from_extension(".py") == "python"
        assert detector.get_language_from_extension(".pyi") == "python"

        # Test JavaScript files
        assert detector.get_language_from_extension(".js") == "javascript"
        assert detector.get_language_from_extension(".jsx") == "javascript"

        # Test TypeScript files
        assert detector.get_language_from_extension(".ts") == "typescript"
        assert detector.get_language_from_extension(".tsx") == "typescript"

        # Test unknown extension
        assert detector.get_language_from_extension(".unknown") is None
