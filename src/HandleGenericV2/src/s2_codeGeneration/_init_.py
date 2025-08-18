"""
S2 Code Generation Package

This package provides a comprehensive system for generating code from requirements,
integrating with metadata analysis, requirement checking, and validation systems.

Key Features:
- Requirement analysis and identification of missing functionality
- AI-powered code generation and integration
- Automatic test case generation
- Metadata updating and validation
- Integration with existing codebases

Usage:
    from s2_codeGeneration import CodeGenerator

    generator = CodeGenerator()
    result = generator.generate_from_requirements(
        project_path="./my_project",
        requirements_path="./requirements.csv",
        metadata_path="./metadata.json",
        output_path="./output"
    )
"""

__version__ = "1.0.0"
__author__ = "Predictable Secure Code Generation Team"

# Import core components
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
