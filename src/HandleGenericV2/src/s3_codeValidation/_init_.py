"""
S3 Code Validation Package

This package provides comprehensive code validation using AI assistance.
It validates code against requirements, monitors code quality, and tracks validation results.

Components:
- CodeValidator: Main validation engine using AI
- Validation monitoring and tracking
- Issue detection and recommendations
- Requirements coverage analysis
"""

__version__ = "1.0.0"
__author__ = "AI Code Generation Team"
__description__ = "AI-powered code validation and quality monitoring"

# Import core components
from .core.codeValidator import CodeValidator

# Export main components
__all__ = [
    "CodeValidator",
]
