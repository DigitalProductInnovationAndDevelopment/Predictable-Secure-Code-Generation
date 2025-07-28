"""
Core language abstraction layer for generic code handling.

This module provides the foundation for supporting multiple programming languages
in the code generation, validation, and metadata extraction system.
"""

__version__ = "1.0.0"
__author__ = "Generic Code Handler"

from .language_provider import LanguageProvider
from .language_registry import LanguageRegistry
from .file_detector import FileDetector

__all__ = ["LanguageProvider", "LanguageRegistry", "FileDetector"]
