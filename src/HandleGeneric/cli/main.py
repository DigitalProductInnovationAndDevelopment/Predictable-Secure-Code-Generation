#!/usr/bin/env python3
"""
Generic Code Handler - Main CLI Interface

This script provides a command-line interface for the generic code handling system
that supports multiple programming languages.

Usage:
    python main.py generate-metadata <project_path> <output_path> [options]
    python main.py validate <project_path> [options]
    python main.py generate-code <requirements_file> <target_language> <output_path> [options]
    python main.py list-languages
    python main.py create-template <language> <template_type> [output_path]
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the parent directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from HandleGeneric.core.base.generator import GenericMetadataGenerator
from HandleGeneric.core.base.validator import GenericValidator
from HandleGeneric.core.base.code_generator import GenericCodeGenerator
from HandleGeneric.core.initialization import get_initialization_status


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_generate_metadata(args):
    """Generate metadata for a project."""
    print(f"🔍 Generating metadata for: {args.project_path}")

    generator = GenericMetadataGenerator(exclude_patterns=args.exclude)

    try:
        metadata = generator.generate_metadata(
            project_path=args.project_path,
            output_path=args.output_path,
            filename=args.filename,
            languages=args.languages,
        )

        print(f"✅ Metadata generation completed successfully!")
        print(f"📁 Output saved to: {Path(args.output_path) / args.filename}")
        print(f"📊 Project summary:")
        print(f"   - Total files processed: {metadata['project_info']['total_files']}")
        print(f"   - Languages detected: {', '.join(metadata['languages'])}")
        print(
            f"   - Main language: {metadata['project_info'].get('main_language', 'Unknown')}"
        )
        print(
            f"   - Generation time: {metadata['project_info']['generation_time']:.2f}s"
        )

        if args.show_details:
            print(f"\n📈 Detailed breakdown:")
            for lang, summary in metadata.get("language_summaries", {}).items():
                print(
                    f"   {lang}: {summary['file_count']} files, {summary['total_lines']} lines"
                )

    except Exception as e:
        print(f"❌ Metadata generation failed: {str(e)}")
        return 1

    return 0


def cmd_validate(args):
    """Validate code in a project."""
    print(f"🔎 Validating code in: {args.project_path}")

    validator = GenericValidator(exclude_patterns=args.exclude)

    try:
        result = validator.validate_project(
            project_path=args.project_path,
            languages=args.languages,
            stop_on_first_error=args.stop_on_error,
        )

        # Print summary
        status_emoji = "✅" if result.status.value == "valid" else "❌"
        print(f"{status_emoji} Validation completed!")
        print(f"📊 Results: {result.valid_files}/{result.total_files} files valid")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")

        if result.invalid_files > 0 or result.error_files > 0:
            print(
                f"⚠️  Issues found: {result.invalid_files} invalid, {result.error_files} errors"
            )

        if args.show_details or result.status.value != "valid":
            print("\n" + validator.get_validation_report(result))

        return 0 if result.status.value == "valid" else 1

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return 1


def cmd_generate_code(args):
    """Generate code from requirements."""
    print(f"🤖 Generating {args.target_language} code from: {args.requirements_file}")

    # Load AI client if available
    ai_client = None
    try:
        from HandleGeneric.ai.client import AzureOpenAIClient

        ai_client = AzureOpenAIClient()
        print("🧠 AI client loaded successfully")
    except ImportError:
        print("⚠️  AI client not available - using template generation only")

    generator = GenericCodeGenerator(ai_client)

    try:
        # Load requirements
        requirements_path = Path(args.requirements_file)
        if not requirements_path.exists():
            print(f"❌ Requirements file not found: {args.requirements_file}")
            return 1

        # Try to load requirements (support JSON or CSV)
        if requirements_path.suffix.lower() == ".json":
            with open(requirements_path, "r", encoding="utf-8") as f:
                requirements_data = json.load(f)
                if isinstance(requirements_data, list):
                    requirements = requirements_data
                else:
                    requirements = [requirements_data]
        else:
            # Assume CSV format
            requirements = []
            with open(requirements_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    requirements.append(
                        {
                            "id": row.get("id", f"req_{len(requirements)}"),
                            "description": row.get("description", ""),
                        }
                    )

        if not requirements:
            print("❌ No requirements found in file")
            return 1

        print(f"📋 Loaded {len(requirements)} requirements")

        # Load implemented requirements to compare
        implemented_requirements_path = (
            Path(args.output_path) / "implementedRequirements.csv"
        )
        implemented_requirements = {}

        if implemented_requirements_path.exists():
            try:
                with open(implemented_requirements_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        implemented_requirements[row.get("id", "")] = row.get(
                            "description", ""
                        )
                print(
                    f"📋 Found {len(implemented_requirements)} implemented requirements"
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not load implemented requirements: {e}")

        # Compare requirements to find new/changed ones
        new_requirements = []
        changed_requirements = []

        for req in requirements:
            req_id = req.get("id", "")
            req_desc = req.get("description", "")

            if req_id not in implemented_requirements:
                new_requirements.append(req)
            elif implemented_requirements[req_id] != req_desc:
                changed_requirements.append(req)

        requirements_to_generate = new_requirements + changed_requirements

        if not requirements_to_generate:
            print("✅ All requirements are already implemented and up to date!")
            print("🚀 No code generation needed.")
            return 0

        print(f"🆕 Found {len(new_requirements)} new requirements")
        print(f"🔄 Found {len(changed_requirements)} changed requirements")
        print(f"⚡ Generating code for {len(requirements_to_generate)} requirements...")

        # Generate code
        context = {
            "project_context": args.context,
            "generate_tests": not args.no_tests,
            "add_standard_imports": not args.no_imports,
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
        }

        result = generator.generate_from_requirements(
            requirements=requirements_to_generate,
            target_language=args.target_language,
            output_path=args.output_path,
            context=context,
        )

        # Print results
        status_emoji = (
            "✅"
            if result.status.value == "success"
            else "⚠️" if result.status.value == "partial_success" else "❌"
        )
        print(f"{status_emoji} Code generation completed!")
        print(f"📁 Output directory: {args.output_path}")
        print(
            f"📊 Results: {result.requirements_implemented}/{result.requirements_implemented + result.requirements_failed} requirements implemented"
        )
        print(f"📄 Generated {len(result.generated_files)} files")
        if result.test_files:
            print(f"🧪 Generated {len(result.test_files)} test files")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")

        if result.ai_tokens_used > 0:
            print(f"🤖 AI tokens used: {result.ai_tokens_used}")

        # Update implementedRequirements.csv if generation was successful
        if (
            result.status.value in ["success", "partial_success"]
            and result.requirements_implemented > 0
        ):
            try:
                # Update implemented requirements with successfully generated ones
                successfully_generated = requirements_to_generate[
                    : result.requirements_implemented
                ]
                for req in successfully_generated:
                    implemented_requirements[req.get("id")] = req.get("description", "")

                # Write updated implementedRequirements.csv
                with open(
                    implemented_requirements_path, "w", encoding="utf-8", newline=""
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "description"])
                    for req_id, req_desc in implemented_requirements.items():
                        if req_id:  # Skip empty IDs
                            writer.writerow([req_id, req_desc])

                print(
                    f"✅ Updated implementedRequirements.csv with {result.requirements_implemented} new/changed requirements"
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not update implementedRequirements.csv: {e}")

        if args.show_details or result.status.value != "success":
            print("\n" + generator.get_generation_report(result))

        return 0 if result.status.value in ["success", "partial_success"] else 1

    except Exception as e:
        print(f"❌ Code generation failed: {str(e)}")
        return 1


def cmd_list_languages(args):
    """List all supported programming languages."""
    print("🌐 Supported Programming Languages:")
    print("=" * 50)

    status = get_initialization_status()

    for language in sorted(status["supported_languages"]):
        provider_info = status["providers_info"][language]
        extensions = ", ".join(provider_info["extensions"])
        print(f"  📝 {language.upper()}")
        print(f"      Extensions: {extensions}")
        print(f"      Provider: {provider_info['provider_class']}")
        print()

    print(f"Total: {len(status['supported_languages'])} languages supported")
    print(f"File extensions: {', '.join(sorted(status['supported_extensions']))}")

    return 0


def cmd_create_template(args):
    """Create a file template for a specific language."""
    print(f"📝 Creating {args.template_type} template for {args.language}")

    generator = GenericCodeGenerator()

    try:
        template_content = generator.generate_file_template(
            language=args.language,
            template_type=args.template_type,
            output_path=args.output_path,
            filename=args.filename,
        )

        if args.output_path and args.filename:
            print(f"✅ Template saved to: {Path(args.output_path) / args.filename}")
        else:
            print("📄 Template content:")
            print("-" * 40)
            print(template_content)
            print("-" * 40)

        return 0

    except Exception as e:
        print(f"❌ Template creation failed: {str(e)}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generic Code Handler - Multi-language code processing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate metadata for a project
  python main.py generate-metadata /path/to/project ./output

  # Validate code in multiple languages
  python main.py validate /path/to/project --languages python javascript

  # Generate Python code from requirements
  python main.py generate-code requirements.csv python ./generated_code

  # List supported languages
  python main.py list-languages

  # Create a Python class template
  python main.py create-template python class ./templates --filename MyClass.py
        """,
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate metadata command
    metadata_parser = subparsers.add_parser(
        "generate-metadata", help="Generate metadata for a project"
    )
    metadata_parser.add_argument("project_path", help="Path to the project directory")
    metadata_parser.add_argument("output_path", help="Path to save the metadata")
    metadata_parser.add_argument(
        "--filename",
        "-f",
        default="metadata.json",
        help="Name of the metadata file (default: metadata.json)",
    )
    metadata_parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        help="Specific languages to process (default: all supported)",
    )
    metadata_parser.add_argument(
        "--exclude", "-e", nargs="+", help="File patterns to exclude"
    )
    metadata_parser.add_argument(
        "--show-details",
        "-d",
        action="store_true",
        help="Show detailed breakdown by language",
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate code in a project"
    )
    validate_parser.add_argument("project_path", help="Path to the project directory")
    validate_parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        help="Specific languages to validate (default: all supported)",
    )
    validate_parser.add_argument(
        "--exclude", "-e", nargs="+", help="File patterns to exclude"
    )
    validate_parser.add_argument(
        "--stop-on-error", action="store_true", help="Stop validation on first error"
    )
    validate_parser.add_argument(
        "--show-details",
        "-d",
        action="store_true",
        help="Show detailed validation results",
    )

    # Generate code command
    generate_parser = subparsers.add_parser(
        "generate-code", help="Generate code from requirements"
    )
    generate_parser.add_argument(
        "requirements_file", help="Path to requirements file (JSON or CSV)"
    )
    generate_parser.add_argument("target_language", help="Target programming language")
    generate_parser.add_argument("output_path", help="Path to save generated code")
    generate_parser.add_argument(
        "--context", "-c", default="", help="Additional context for code generation"
    )
    generate_parser.add_argument(
        "--no-tests", action="store_true", help="Skip test file generation"
    )
    generate_parser.add_argument(
        "--no-imports", action="store_true", help="Skip adding standard imports"
    )
    generate_parser.add_argument(
        "--max-tokens", type=int, default=2000, help="Maximum tokens for AI generation"
    )
    generate_parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for AI generation"
    )
    generate_parser.add_argument(
        "--show-details",
        "-d",
        action="store_true",
        help="Show detailed generation results",
    )

    # List languages command
    list_parser = subparsers.add_parser(
        "list-languages", help="List all supported programming languages"
    )

    # Create template command
    template_parser = subparsers.add_parser(
        "create-template", help="Create a file template for a specific language"
    )
    template_parser.add_argument("language", help="Target programming language")
    template_parser.add_argument(
        "template_type",
        choices=["basic", "class", "module", "interface"],
        help="Type of template to create",
    )
    template_parser.add_argument(
        "output_path", nargs="?", help="Path to save the template (optional)"
    )
    template_parser.add_argument("--filename", "-f", help="Filename for the template")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)

    # Route to appropriate command handler
    command_handlers = {
        "generate-metadata": cmd_generate_metadata,
        "validate": cmd_validate,
        "generate-code": cmd_generate_code,
        "list-languages": cmd_list_languages,
        "create-template": cmd_create_template,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        sys.exit(1)
