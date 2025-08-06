"""
Tests for HandleGeneric base provider class.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from HandleGeneric.providers.base import BaseLanguageProvider


class TestBaseLanguageProvider:
    """Test cases for BaseLanguageProvider."""

    def test_init(self):
        """Test initialization of BaseLanguageProvider."""
        provider = BaseLanguageProvider()
        assert provider is not None
        assert hasattr(provider, "language_name")
        assert hasattr(provider, "file_extensions")
        assert hasattr(provider, "supported_features")

    def test_language_name_derivation(self):
        """Test that language name is derived from class name."""

        class TestProvider(BaseLanguageProvider):
            pass

        provider = TestProvider()
        assert provider.language_name == "test"

    def test_abstract_methods(self):
        """Test that abstract methods raise NotImplementedError."""
        provider = BaseLanguageProvider()

        # Test parse_file
        with pytest.raises(NotImplementedError):
            provider.parse_file(Mock())

        # Test validate_file
        with pytest.raises(NotImplementedError):
            provider.validate_file(Mock())

        # Test generate_code
        with pytest.raises(NotImplementedError):
            provider.generate_code([], Mock())

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        provider = BaseLanguageProvider()
        provider.file_extensions = [".py", ".pyi"]

        extensions = provider.get_supported_extensions()
        assert extensions == [".py", ".pyi"]

    def test_get_supported_features(self):
        """Test getting supported features."""
        provider = BaseLanguageProvider()
        provider.supported_features = ["parsing", "validation"]

        features = provider.get_supported_features()
        assert features == ["parsing", "validation"]

    def test_is_supported_file(self):
        """Test checking if a file is supported."""
        provider = BaseLanguageProvider()
        provider.file_extensions = [".py", ".pyi"]

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

    def test_is_supported_file_case_insensitive(self):
        """Test that file support check is case insensitive."""
        provider = BaseLanguageProvider()
        provider.file_extensions = [".py", ".pyi"]

        # Test uppercase extension
        mock_file = Mock()
        mock_file.suffix = ".PY"
        assert provider.is_supported_file(mock_file) is True

        # Test mixed case extension
        mock_file2 = Mock()
        mock_file2.suffix = ".Py"
        assert provider.is_supported_file(mock_file2) is True


class TestConcreteProvider(BaseLanguageProvider):
    """Concrete implementation for testing."""

    def __init__(self):
        super().__init__()
        self.file_extensions = [".test"]
        self.supported_features = ["parsing", "validation", "generation"]

    def parse_file(self, file_path: Path):
        return {"status": "success", "language": "test"}

    def validate_file(self, file_path: Path):
        return {"status": "valid", "errors": []}

    def generate_code(self, requirements, output_path: Path):
        return {"status": "success", "files": []}


class TestConcreteProviderImplementation:
    """Test cases for concrete provider implementation."""

    def test_concrete_provider_init(self):
        """Test initialization of concrete provider."""
        provider = TestConcreteProvider()
        assert provider.language_name == "testconcrete"
        assert provider.file_extensions == [".test"]
        assert provider.supported_features == ["parsing", "validation", "generation"]

    def test_concrete_provider_methods(self):
        """Test that concrete provider methods work."""
        provider = TestConcreteProvider()
        mock_file = Mock()
        mock_output = Mock()

        # Test parse_file
        result = provider.parse_file(mock_file)
        assert result["status"] == "success"
        assert result["language"] == "test"

        # Test validate_file
        result = provider.validate_file(mock_file)
        assert result["status"] == "valid"
        assert result["errors"] == []

        # Test generate_code
        result = provider.generate_code([], mock_output)
        assert result["status"] == "success"
        assert result["files"] == []

    def test_concrete_provider_support_methods(self):
        """Test support methods of concrete provider."""
        provider = TestConcreteProvider()

        # Test supported extensions
        extensions = provider.get_supported_extensions()
        assert extensions == [".test"]

        # Test supported features
        features = provider.get_supported_features()
        assert features == ["parsing", "validation", "generation"]

        # Test file support
        mock_file = Mock()
        mock_file.suffix = ".test"
        assert provider.is_supported_file(mock_file) is True

        mock_unsupported_file = Mock()
        mock_unsupported_file.suffix = ".other"
        assert provider.is_supported_file(mock_unsupported_file) is False
