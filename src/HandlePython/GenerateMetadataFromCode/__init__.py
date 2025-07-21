"""
Generate Metadata From Code Package

A comprehensive tool for extracting metadata from Python codebases including
functions, classes, imports, and entry points.
"""

from .core.generator import MetadataGenerator
from .core.parser import CodeParser
from .core.analyzer import CodeAnalyzer
from .utils.config import Config
from .utils.helpers import FileHelper, PathHelper

__version__ = "1.0.0"
__author__ = "Code Analysis Team"
__description__ = "Extract comprehensive metadata from Python codebases"

__all__ = [
    "MetadataGenerator",
    "CodeParser",
    "CodeAnalyzer",
    "Config",
    "FileHelper",
    "PathHelper",
]
