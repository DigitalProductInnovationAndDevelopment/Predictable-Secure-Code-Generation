"""
Base provider class for language-specific implementations.

This module provides the base class that all language providers should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class BaseLanguageProvider(ABC):
    """
    Base class for language-specific providers.

    All language providers should inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self):
        """Initialize the base provider."""
        self.language_name = self.__class__.__name__.replace("Provider", "").lower()
        self.file_extensions = []
        self.supported_features = []

    @abstractmethod
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a file and extract metadata.

        Args:
            file_path: Path to the file to parse

        Returns:
            Dictionary containing parsed metadata
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a file for syntax errors.

        Args:
            file_path: Path to the file to validate

        Returns:
            Dictionary containing validation results
        """
        pass

    @abstractmethod
    def generate_code(
        self, requirements: List[Dict[str, Any]], output_path: Path
    ) -> Dict[str, Any]:
        """
        Generate code based on requirements.

        Args:
            requirements: List of requirements for code generation
            output_path: Path where generated code should be saved

        Returns:
            Dictionary containing generation results
        """
        pass

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions supported by this provider.

        Returns:
            List of supported file extensions
        """
        return self.file_extensions

    def get_supported_features(self) -> List[str]:
        """
        Get list of features supported by this provider.

        Returns:
            List of supported features
        """
        return self.supported_features

    def is_supported_file(self, file_path: Path) -> bool:
        """
        Check if a file is supported by this provider.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is supported, False otherwise
        """
        return file_path.suffix.lower() in self.file_extensions
