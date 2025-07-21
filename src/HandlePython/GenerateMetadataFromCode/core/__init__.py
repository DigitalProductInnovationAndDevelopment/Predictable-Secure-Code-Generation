"""
Core components for metadata generation from code.
"""

from .generator import MetadataGenerator
from .parser import CodeParser
from .analyzer import CodeAnalyzer

__all__ = ["MetadataGenerator", "CodeParser", "CodeAnalyzer"]
