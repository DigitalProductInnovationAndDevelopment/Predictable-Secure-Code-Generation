"""
S1 Metadata Generation Package

This package handles the initial analysis of codebases to determine
programming language and architecture using AI analysis.
"""

__version__ = "1.0.0"
__author__ = "Predictable Secure Code Generation Team"

from .core.coldStart import analyze_codebase_with_ai

__all__ = ["analyze_codebase_with_ai"]
