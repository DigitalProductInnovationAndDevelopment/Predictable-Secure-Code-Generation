"""
Language registry for managing language providers.

This module provides a central registry for all language providers,
allowing dynamic registration and lookup of language-specific handlers.
"""

from typing import Dict, Optional, Set, List
from pathlib import Path
import logging

from .language_provider import LanguageProvider


class LanguageRegistry:
    """Central registry for language providers."""

    def __init__(self):
        self._providers: Dict[str, LanguageProvider] = {}
        self._extension_mapping: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)

    def register_provider(self, provider: LanguageProvider) -> None:
        """
        Register a language provider.

        Args:
            provider: The language provider to register
        """
        language_name = provider.language_name.lower()

        if language_name in self._providers:
            self.logger.warning(f"Overriding existing provider for {language_name}")

        self._providers[language_name] = provider

        # Update extension mapping
        for ext in provider.file_extensions:
            ext_lower = ext.lower()
            if ext_lower in self._extension_mapping:
                self.logger.warning(
                    f"Extension {ext} already mapped to {self._extension_mapping[ext_lower]}, overriding with {language_name}"
                )
            self._extension_mapping[ext_lower] = language_name

        self.logger.info(
            f"Registered provider for {language_name} with extensions: {provider.file_extensions}"
        )

    def get_provider(self, language: str) -> Optional[LanguageProvider]:
        """
        Get a provider by language name.

        Args:
            language: Name of the programming language

        Returns:
            Language provider or None if not found
        """
        return self._providers.get(language.lower())

    def get_provider_for_file(self, file_path: Path) -> Optional[LanguageProvider]:
        """
        Get the appropriate provider for a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            Language provider or None if no suitable provider found
        """
        extension = file_path.suffix.lower()
        language = self._extension_mapping.get(extension)

        if language:
            return self._providers.get(language)

        return None

    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported languages.

        Returns:
            List of supported language names
        """
        return list(self._providers.keys())

    def get_supported_extensions(self) -> Set[str]:
        """
        Get set of all supported file extensions.

        Returns:
            Set of supported file extensions
        """
        return set(self._extension_mapping.keys())

    def is_file_supported(self, file_path: Path) -> bool:
        """
        Check if a file is supported by any registered provider.

        Args:
            file_path: Path to check

        Returns:
            True if file is supported
        """
        return file_path.suffix.lower() in self._extension_mapping

    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect the programming language of a file.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if not detected
        """
        extension = file_path.suffix.lower()
        return self._extension_mapping.get(extension)

    def get_providers_info(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about all registered providers.

        Returns:
            Dictionary with provider information
        """
        info = {}
        for language, provider in self._providers.items():
            info[language] = {
                "extensions": list(provider.file_extensions),
                "comment_prefixes": provider.comment_prefixes,
                "provider_class": provider.__class__.__name__,
            }
        return info


# Global registry instance
_global_registry = LanguageRegistry()


def get_global_registry() -> LanguageRegistry:
    """Get the global language registry instance."""
    return _global_registry


def register_provider(provider: LanguageProvider) -> None:
    """Register a provider with the global registry."""
    _global_registry.register_provider(provider)


def get_provider(language: str) -> Optional[LanguageProvider]:
    """Get a provider by language name from the global registry."""
    return _global_registry.get_provider(language)


def get_provider_for_file(file_path: Path) -> Optional[LanguageProvider]:
    """Get provider for file from the global registry."""
    return _global_registry.get_provider_for_file(file_path)
