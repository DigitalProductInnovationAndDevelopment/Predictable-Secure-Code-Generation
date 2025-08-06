#!/usr/bin/env python3
"""
Example usage script for GenerateCodeFromRequirements system.

This script demonstrates how to use the code generation system programmatically
and shows the complete workflow from requirements to validated code.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.generator import CodeGenerator
from utils.config import GenerationConfig
from utils.helpers import GenerationHelper
from models.generation_result import GenerationResult, GenerationStatus


def create_sample_requirements():
    """Create a sample requirements CSV file for testing."""
    requirements_data = [
        ("REQ001", "Add function to calculate factorial of a number"),
        ("REQ002", "Implement power function to calculate x raised to power y"),
        ("REQ003", "Add function to calculate percentage"),
        ("REQ004", "Create memory storage functions"),
        ("REQ005", "Add square root calculation function"),
    ]

    # Create temporary requirements file
    import csv
    import tempfile

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)

    writer = csv.writer(temp_file)
    writer.writerow(["id", "description"])
    writer.writerows(requirements_data)

    temp_file.close()
    return temp_file.name


def create_sample_metadata():
    """Create sample metadata for testing."""
    metadata = {
        "project_info": {"source_path": "/example/project", "total_files": 3},
        "files": [
            {
                "path": "calculator.py",
                "functions": [
                    {"name": "add", "args": ["a", "b"], "docstring": "Add two numbers"},
                    {
                        "name": "subtract",
                        "args": ["a", "b"],
                        "docstring": "Subtract numbers",
                    },
                ],
                "classes": [
                    {
                        "name": "Calculator",
                        "methods": [
                            {"name": "multiply", "args": ["self", "a", "b"]},
                            {"name": "divide", "args": ["self", "a", "b"]},
                        ],
                    }
                ],
                "imports": ["math"],
            }
        ],
        "dependencies": {
            "external_dependencies": ["pytest"],
            "internal_dependencies": [],
        },
    }

    # Create temporary metadata file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(metadata, temp_file, indent=2)
    temp_file.close()
    return temp_file.name


def demonstrate_programmatic_usage():
    """Demonstrate programmatic usage of the code generation system."""
    print("=== Programmatic Usage Example ===\n")

    # Create temporary files for demonstration
    print("1. Creating sample requirements and metadata...")
    requirements_file = create_sample_requirements()
    metadata_file = create_sample_metadata()

    # Create temporary directories
    project_dir = tempfile.mkdtemp(prefix="sample_project_")
    output_dir = tempfile.mkdtemp(prefix="generated_output_")

    # Create a simple sample project
    sample_calculator = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
"""

    with open(os.path.join(project_dir, "calculator.py"), "w") as f:
        f.write(sample_calculator)

    try:
        print(f"   Requirements: {requirements_file}")
        print(f"   Metadata: {metadata_file}")
        print(f"   Project: {project_dir}")
        print(f"   Output: {output_dir}")

        # Initialize the code generator
        print("\n2. Initializing CodeGenerator...")
        generator = CodeGenerator()

        # Configure generation settings
        print("3. Running code generation...")

        # Note: This will fail without proper AI setup, but demonstrates the API
        result = GenerationResult(GenerationStatus.SUCCESS)
        result.source_path = project_dir
        result.output_path = output_dir
        result.requirements_path = requirements_file
        result.metadata_path = metadata_file
        result.requirements_analyzed = 5
        result.requirements_implemented = 3
        result.requirements_failed = 2
        result.execution_time = 45.0
        result.ai_tokens_used = 2500

        # Add some sample problems
        result.add_problem("warning", "integration", "Sample warning message")
        result.add_problem("info", "testing", "Sample info message")

        print("\n4. Generation completed!")
        print(result.get_summary())

        # Save results
        result_file = os.path.join(output_dir, "generation_result.json")
        GenerationHelper.save_result_to_file(result.to_dict(), result_file, "json")
        print(f"\n5. Results saved to: {result_file}")

        return result

    finally:
        # Clean up temporary files
        print("\n6. Cleaning up temporary files...")
        for temp_file in [requirements_file, metadata_file]:
            try:
                os.unlink(temp_file)
            except:
                pass


def demonstrate_configuration():
    """Demonstrate configuration management."""
    print("\n=== Configuration Management Example ===\n")

    # Create and customize configuration
    print("1. Creating and customizing configuration...")
    config = GenerationConfig()

    # Modify some settings
    config.ai_max_tokens = 1500
    config.ai_temperature = 0.2
    config.generate_tests = True
    config.verbose_logging = True

    print("   Original configuration:")
    print(config.get_summary())

    # Save configuration
    config_file = tempfile.mktemp(suffix=".json")
    config.save_to_file(config_file)
    print(f"\n2. Configuration saved to: {config_file}")

    # Load configuration
    loaded_config = GenerationConfig.load_from_file(config_file)
    print("\n3. Configuration loaded successfully!")

    # Validate configuration
    errors = loaded_config.validate()
    if errors:
        print(f"   Configuration errors: {errors}")
    else:
        print("   Configuration is valid!")

    # Clean up
    try:
        os.unlink(config_file)
    except:
        pass

    return loaded_config


def demonstrate_helpers():
    """Demonstrate utility helpers."""
    print("\n=== Helper Utilities Example ===\n")

    # Test code validation
    print("1. Testing code validation...")
    valid_code = "def hello():\n    return 'Hello, World!'"
    invalid_code = "def hello(\n    return 'Hello, World!'"

    is_valid, error = GenerationHelper.validate_python_syntax(valid_code)
    print(f"   Valid code check: {is_valid} (error: {error})")

    is_valid, error = GenerationHelper.validate_python_syntax(invalid_code)
    print(f"   Invalid code check: {is_valid} (error: {error})")

    # Test function extraction
    print("\n2. Testing function extraction...")
    sample_code = """
def add(a, b):
    '''Add two numbers'''
    return a + b

def multiply(x, y):
    '''Multiply two numbers'''
    return x * y

class Calculator:
    def subtract(self, a, b):
        return a - b
"""

    functions = GenerationHelper.extract_functions_from_code(sample_code)
    print(f"   Extracted {len(functions)} functions:")
    for func in functions:
        print(f"     - {func['name']}({', '.join(func['args'])})")

    # Test complexity estimation
    print("\n3. Testing complexity estimation...")
    simple_code = "def add(a, b): return a + b"
    complex_code = """
def complex_function(data):
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if value > 0:
                    try:
                        processed = value * 2
                        result.append(processed)
                    except Exception as e:
                        continue
                else:
                    result.append(0)
    return result
"""

    simple_complexity = GenerationHelper.estimate_code_complexity(simple_code)
    complex_complexity = GenerationHelper.estimate_code_complexity(complex_code)

    print(f"   Simple code complexity: {simple_complexity:.2f}")
    print(f"   Complex code complexity: {complex_complexity:.2f}")


def main():
    """Main demonstration function."""
    print("GenerateCodeFromRequirements - Example Usage")
    print("=" * 50)

    try:
        # Demonstrate different aspects of the system
        demonstrate_configuration()
        demonstrate_helpers()
        demonstrate_programmatic_usage()

        print("\n" + "=" * 50)
        print("✅ All demonstrations completed successfully!")
        print("\nNext steps:")
        print("1. Set up AI configuration (Azure OpenAI)")
        print("2. Create your requirements CSV file")
        print("3. Generate metadata for your project")
        print("4. Run the code generation system")
        print("5. Review and test the generated code")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
