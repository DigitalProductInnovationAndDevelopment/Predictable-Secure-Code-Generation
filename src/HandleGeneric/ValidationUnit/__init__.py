"""
Validation Unit Package

A comprehensive validation system for Python codebases that performs:
1. Syntax validation
2. Test case validation
3. AI-powered logic validation

Uses metadata.json and source code directory as inputs.
"""

from .core.validator import CodebaseValidator
from .core.syntax_validator import SyntaxValidator
from .core.test_validator import TestValidator
from .core.ai_validator import AIValidator
from .utils.config import ValidationConfig
from .utils.helpers import ValidationHelper
from .models.validation_result import ValidationResult, ValidationStatus

__version__ = "1.0.0"
__author__ = "Validation Team"
__description__ = "Comprehensive codebase validation system"

__all__ = [
    "CodebaseValidator",
    "SyntaxValidator",
    "TestValidator",
    "AIValidator",
    "ValidationConfig",
    "ValidationHelper",
    "ValidationResult",
    "ValidationStatus",
]
