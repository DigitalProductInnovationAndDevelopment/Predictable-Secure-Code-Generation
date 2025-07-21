"""
GenerateCodeFromRequirements - AI-powered code generation from requirements

This package provides a comprehensive system for generating code from requirements,
integrating with metadata analysis, requirement checking, and validation systems.

Key Features:
- Requirement analysis and identification of missing functionality
- AI-powered code generation and integration
- Automatic test case generation
- Metadata updating and validation
- Integration with existing codebases

Usage:
    from GenerateCodeFromRequirements import CodeGenerator

    generator = CodeGenerator()
    result = generator.generate_from_requirements(
        project_path="./my_project",
        requirements_path="./requirements.csv",
        metadata_path="./metadata.json",
        output_path="./output"
    )
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .core.generator import CodeGenerator
from .core.analyzer import RequirementAnalyzer
from .core.integrator import CodeIntegrator
from .models.generation_result import GenerationResult, GenerationStatus

__all__ = [
    "CodeGenerator",
    "RequirementAnalyzer",
    "CodeIntegrator",
    "GenerationResult",
    "GenerationStatus",
]
