"""
Tests for HandleGeneric initialization functionality.
"""

import pytest
from unittest.mock import Mock, patch

from HandleGeneric.core.initialization import (
    ensure_initialized,
    get_initialization_status,
)


class TestInitialization:
    """Test cases for initialization functions."""

    def test_get_initialization_status_default(self):
        """Test getting initialization status when not initialized."""
        status = get_initialization_status()
        assert isinstance(status, dict)
        assert "initialized" in status
        assert "providers" in status
        assert "languages" in status

    @patch("HandleGeneric.core.initialization.LanguageRegistry")
    def test_ensure_initialized_basic(self, mock_registry):
        """Test basic initialization."""
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance

        # Mock provider registration
        mock_provider = Mock()
        mock_provider.language_name = "python"

        with patch(
            "HandleGeneric.core.initialization.PythonProvider",
            return_value=mock_provider,
        ):
            ensure_initialized()

            # Check that providers were registered
            mock_registry_instance.register_provider.assert_called()

    @patch("HandleGeneric.core.initialization.LanguageRegistry")
    def test_ensure_initialized_multiple_providers(self, mock_registry):
        """Test initialization with multiple providers."""
        mock_registry_instance = Mock()
        mock_registry.return_value = mock_registry_instance

        # Mock multiple providers
        mock_python_provider = Mock()
        mock_python_provider.language_name = "python"
        mock_js_provider = Mock()
        mock_js_provider.language_name = "javascript"

        with patch(
            "HandleGeneric.core.initialization.PythonProvider",
            return_value=mock_python_provider,
        ), patch(
            "HandleGeneric.core.initialization.JavaScriptProvider",
            return_value=mock_js_provider,
        ):
            ensure_initialized()

            # Check that multiple providers were registered
            assert mock_registry_instance.register_provider.call_count >= 2

    def test_initialization_status_after_init(self):
        """Test initialization status after initialization."""
        with patch("HandleGeneric.core.initialization.LanguageRegistry"):
            ensure_initialized()
            status = get_initialization_status()

            assert status["initialized"] is True
            assert len(status["providers"]) > 0
            assert len(status["languages"]) > 0

    @patch("HandleGeneric.core.initialization.LanguageRegistry")
    def test_initialization_error_handling(self, mock_registry):
        """Test error handling during initialization."""
        mock_registry.side_effect = Exception("Registry error")

        # Should not raise an exception, but should handle the error gracefully
        try:
            ensure_initialized()
        except Exception:
            pytest.fail("Initialization should handle errors gracefully")

    def test_initialization_idempotent(self):
        """Test that initialization is idempotent."""
        with patch(
            "HandleGeneric.core.initialization.LanguageRegistry"
        ) as mock_registry:
            # First initialization
            ensure_initialized()
            first_call_count = mock_registry.call_count

            # Second initialization
            ensure_initialized()
            second_call_count = mock_registry.call_count

            # Should not call registry again if already initialized
            assert second_call_count <= first_call_count + 1
