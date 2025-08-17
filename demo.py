#!/usr/bin/env python3
"""
Demo script showcasing the platform's three services.
This avoids import conflicts by demonstrating core functionality directly.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src" / "HandleGeneric v2" / "src"))


def demo_s2_metadata():
    """Demo S2 - Metadata extraction service."""
    print("🔍 S2 - Metadata Extraction Demo")
    print("=" * 40)

    # Import the metadata provider
    from platform.adapters.providers.python.metadata_provider import (
        PythonMetadataProvider,
    )
    from platform.adapters.fs.local_fs import LocalFileSystem

    # Sample Python code
    sample_code = '''
"""A sample calculator module."""

import math
from typing import Union

class Calculator:
    """A simple calculator with basic operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        result = math.pow(base, exponent)
        self.history.append(f"{base} ** {exponent} = {result}")
        return result

def validate_input(value: Union[int, float]) -> bool:
    """Validate numeric input."""
    return isinstance(value, (int, float)) and not math.isnan(value)

def format_result(result: float) -> str:
    """Format calculation result."""
    return f"{result:.2f}"
'''

    # Extract metadata
    provider = PythonMetadataProvider()
    metadata = provider.parse_file(Path("calculator.py"), sample_code)

    print(f"📄 File: {metadata.path}")
    print(f"🔤 Language: {metadata.language}")
    print(f"📊 Lines of Code: {metadata.loc}")
    print(f"🔧 Functions: {len(metadata.functions)}")
    for func in metadata.functions:
        print(f"   - {func}")
    print(f"🏗️  Classes: {len(metadata.classes)}")
    for cls in metadata.classes:
        print(f"   - {cls}")
    print(f"📦 Imports: {len(metadata.imports)}")
    for imp in metadata.imports[:3]:  # Show first 3
        print(f"   - {imp}")

    print("\n✅ Metadata extraction completed!\n")
    return metadata


def demo_s3_validation():
    """Demo S3 - Validation service."""
    print("🔍 S3 - Validation Demo")
    print("=" * 40)

    from platform.adapters.providers.python.syntax_validator import (
        PythonSyntaxValidator,
    )

    validator = PythonSyntaxValidator()

    # Test valid code
    valid_code = """
def hello_world():
    print("Hello, World!")
    return True
"""

    print("Testing valid Python code:")
    result = validator.validate(Path("valid.py"), valid_code)
    print(f"✅ Status: {result.status}")
    print(f"📝 Issues: {len(result.issues)}")

    # Test invalid code
    invalid_code = """
def broken_function(
    print("Missing closing parenthesis")
    return False
"""

    print("\nTesting invalid Python code:")
    result = validator.validate(Path("invalid.py"), invalid_code)
    print(f"❌ Status: {result.status}")
    print(f"📝 Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"   Line {issue.line}: {issue.message}")

    print("\n✅ Syntax validation completed!\n")


def demo_s1_generation():
    """Demo S1 - Code generation service (prompt building)."""
    print("🚀 S1 - Code Generation Demo")
    print("=" * 40)

    from platform.domain.models.requirements import Requirement
    from platform.adapters.providers.python.codegen_provider import (
        PythonCodeGenProvider,
    )

    # Create a sample requirement
    requirement = Requirement(
        id="CALC-001",
        title="Basic Calculator Function",
        description="Create a function that adds two numbers with error handling",
        acceptance=[
            "Must accept two numeric parameters",
            "Must return the sum of the parameters",
            "Must handle invalid inputs gracefully",
            "Must include type hints and docstring",
        ],
    )

    # Generate prompt
    provider = PythonCodeGenProvider()
    context = {
        "use_type_hints": True,
        "test_framework": "pytest",
        "style_guide": "PEP 8",
    }

    prompt = provider.build_prompt(requirement, context)

    print(f"📋 Requirement: {requirement.title}")
    print(f"📝 Description: {requirement.description}")
    print(f"✅ Acceptance Criteria:")
    for i, criteria in enumerate(requirement.acceptance, 1):
        print(f"   {i}. {criteria}")

    print("\n🤖 Generated Prompt Preview:")
    print("-" * 50)
    # Show first 500 characters of prompt
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 50)

    print("\n✅ Code generation prompt ready!")
    print("💡 With an OpenAI API key, this would generate actual Python code.\n")


def demo_file_operations():
    """Demo file system operations."""
    print("📁 File System Operations Demo")
    print("=" * 40)

    from platform.adapters.fs.local_fs import LocalFileSystem
    from platform.adapters.fs.artifact_writer import LocalArtifactWriter
    from platform.domain.models.generation import GeneratedFile

    fs = LocalFileSystem()
    writer = LocalArtifactWriter()

    # Demo with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write a test file
        test_content = '''# Generated Calculator
def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b
'''

        test_file = temp_path / "calculator.py"
        fs.write_text(test_file, test_content)

        # Read it back
        read_content = fs.read_text(test_file)
        print(f"✅ File write/read successful: {len(read_content)} characters")

        # Scan directory
        files = fs.scan(temp_path)
        print(f"📂 Files found: {len(files)}")
        for file in files:
            print(f"   - {file.name}")

        # Demo artifact writer
        generated_files = [
            GeneratedFile(
                path="main.py", content='print("Hello from main!")', language="python"
            ),
            GeneratedFile(
                path="utils.py", content="def utility(): pass", language="python"
            ),
        ]

        output_dir = temp_path / "generated"
        writer.write(output_dir, generated_files)

        # Verify generated files
        generated_files_found = list(output_dir.rglob("*.py"))
        print(f"🎯 Generated files: {len(generated_files_found)}")
        for file in generated_files_found:
            print(f"   - {file.name}")

    print("\n✅ File operations completed!\n")


def main():
    """Run the full platform demo."""
    print("🏗️  Enterprise Code Generation Platform Demo")
    print("=" * 60)
    print("🎯 Demonstrating three first-class services:")
    print("   S1 - Code Generation from Requirements")
    print("   S2 - Metadata Generation from Code")
    print("   S3 - Validation (syntax → tests → AI logic)")
    print("=" * 60)
    print()

    # Run demos
    try:
        demo_s2_metadata()
        demo_s3_validation()
        demo_s1_generation()
        demo_file_operations()

        print("🎉 Platform Demo Completed Successfully!")
        print("\n📚 What you've seen:")
        print("✅ Metadata extraction from Python code using AST parsing")
        print("✅ Syntax validation with detailed error reporting")
        print("✅ Prompt generation for AI-powered code creation")
        print("✅ File system operations for artifact management")

        print("\n🔧 To use the full platform:")
        print("1. Install dependencies: pip install openai pydantic typer rich")
        print("2. Set up .env file with your OpenAI API key")
        print("3. Use the CLI for full functionality")

        print("\n🚀 The platform is ready for:")
        print("   - Multi-language support (Python, TypeScript, Java)")
        print("   - AI-powered code generation")
        print("   - Comprehensive validation pipelines")
        print("   - Enterprise-grade observability")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
