"""
Language-related core functionality for HandleGeneric.

This module contains language registry, providers, and detection functionality.
"""

__version__ = "1.0.0"

from .provider import (
    LanguageProvider,
    FileMetadata,
    FunctionInfo,
    ClassInfo,
    SyntaxValidationResult,
)
from .registry import LanguageRegistry
from .detector import FileDetector

__all__ = [
    "LanguageProvider",
    "LanguageRegistry",
    "FileDetector",
    "FileMetadata",
    "FunctionInfo",
    "ClassInfo",
    "SyntaxValidationResult",
]
