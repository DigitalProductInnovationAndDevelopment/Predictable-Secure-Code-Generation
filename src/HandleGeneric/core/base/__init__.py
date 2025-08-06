"""
Base classes for HandleGeneric core functionality.

This module contains the base classes for generators, validators, and code generators.
"""

__version__ = "1.0.0"

from .generator import GenericMetadataGenerator
from .validator import GenericValidator
from .code_generator import GenericCodeGenerator

__all__ = ["GenericMetadataGenerator", "GenericValidator", "GenericCodeGenerator"]
