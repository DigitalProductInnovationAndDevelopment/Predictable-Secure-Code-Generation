#!/usr/bin/env python3
"""
Example usage of the ValidationUnit system.

This script demonstrates how to use the validation system programmatically.
"""

import sys
import os

# Add the project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.ValidtaionUnit import CodebaseValidator, ValidationConfig


def main():
    """Demonstrate validation system usage."""

    print("🔍 ValidationUnit Example Usage")
    print("=" * 40)

    # Example 1: Basic validation with default config
    print("\n1. Basic Validation")
    print("-" * 20)

    validator = CodebaseValidator()

    result = validator.validate_codebase(
        codebase_path="input/code", metadata_path="output/enviroment/metadata.json"
    )

    print(f"Overall Status: {result.overall_status.value}")
    print(f"Valid: {result.is_valid}")
    print(f"Total Errors: {result.total_error_count()}")
    print(f"Total Warnings: {result.total_warning_count()}")
    print(f"Execution Time: {result.total_execution_time:.2f}s")

    # Example 2: Custom configuration
    print("\n2. Custom Configuration")
    print("-" * 25)

    config = ValidationConfig()
    config.enable_syntax_validation = True
    config.enable_test_validation = False  # Skip tests for this example
    config.enable_ai_validation = False  # Skip AI for this example
    config.verbose_output = True

    validator_custom = CodebaseValidator(config)

    result_custom = validator_custom.validate_codebase(
        codebase_path="input/code", metadata_path="output/enviroment/metadata.json"
    )

    print(f"Custom Validation - Valid: {result_custom.is_valid}")

    # Example 3: Single step validation
    print("\n3. Single Step Validation")
    print("-" * 26)

    syntax_result = validator.validate_single_step(
        "syntax", "input/code", "output/enviroment/metadata.json"
    )

    print(f"Syntax Validation - Valid: {syntax_result.is_valid}")
    print(f"Files Checked: {syntax_result.metadata.get('files_checked', 0)}")

    # Example 4: Detailed problem analysis
    print("\n4. Problem Analysis")
    print("-" * 19)

    all_problems = result.get_all_problems()

    if all_problems:
        print(f"Found {len(all_problems)} problems:")
        for problem in all_problems[:3]:  # Show first 3 problems
            location = (
                f" ({problem.file_path}:{problem.line_number})"
                if problem.file_path
                else ""
            )
            print(f"  [{problem.severity.upper()}] {problem.message}{location}")
    else:
        print("No problems found! ✅")

    # Example 5: Generate summary
    print("\n5. Validation Summary")
    print("-" * 21)

    summary = validator.get_validation_summary(result)
    print(summary)


if __name__ == "__main__":
    main()
