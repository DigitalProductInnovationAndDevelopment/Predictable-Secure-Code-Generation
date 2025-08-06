"""
Generic Code Handler - Language-Agnostic Code Processing System

This package provides a comprehensive, language-agnostic system for:
- Metadata extraction from codebases in multiple programming languages
- Code validation across different programming languages
- AI-powered code generation for any supported language

Supported Languages:
- Python (.py, .pyi, .pyw)
- JavaScript (.js, .jsx, .mjs)
- TypeScript (.ts, .tsx)
- Java (.java)
- C# (.cs)

Key Features:
- Language detection and automatic provider selection
- Unified metadata schema across all languages
- Extensible architecture for adding new language support
- AI-powered code generation with language-specific prompts
- Comprehensive validation with language-specific syntax checking
"""

__version__ = "2.0.0"
__author__ = "Generic Code Handler Team"

# Import core components
from .core.language import LanguageProvider, LanguageRegistry, FileDetector
from .core.initialization import ensure_initialized, get_initialization_status

# Import main functionality
from .core.base.generator import GenericMetadataGenerator
from .core.base.validator import (
    GenericValidator,
    ValidationStatus,
    ValidationResult,
    OverallValidationResult,
)
from .core.base.code_generator import (
    GenericCodeGenerator,
    GenerationStatus,
    GenerationResult,
)

# Import language providers (for advanced usage)
from .providers.python import PythonProvider
from .providers.javascript import JavaScriptProvider
from .providers.typescript import TypeScriptProvider
from .providers.java import JavaProvider
from .providers.csharp import CSharpProvider

# Ensure language providers are initialized on import
ensure_initialized()

__all__ = [
    # Core components
    "LanguageProvider",
    "LanguageRegistry",
    "FileDetector",
    # Main functionality
    "GenericMetadataGenerator",
    "GenericValidator",
    "GenericCodeGenerator",
    # Status enums and result classes
    "ValidationStatus",
    "ValidationResult",
    "OverallValidationResult",
    "GenerationStatus",
    "GenerationResult",
    # Language providers
    "PythonProvider",
    "JavaScriptProvider",
    "TypeScriptProvider",
    "JavaProvider",
    "CSharpProvider",
    # Initialization functions
    "ensure_initialized",
    "get_initialization_status",
]


# Convenience functions
def get_supported_languages():
    """Get list of all supported programming languages."""
    from .core.language.registry import get_global_registry

    return get_global_registry().get_supported_languages()


def get_supported_extensions():
    """Get list of all supported file extensions."""
    from .core.language.registry import get_global_registry

    return list(get_global_registry().get_supported_extensions())


def create_metadata_generator(**kwargs):
    """Create a metadata generator instance."""
    return GenericMetadataGenerator(**kwargs)


def create_validator(**kwargs):
    """Create a validator instance."""
    return GenericValidator(**kwargs)


def create_code_generator(ai_client=None):
    """Create a code generator instance."""
    return GenericCodeGenerator(ai_client)
