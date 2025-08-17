"""
Main CLI interface for GenerateCodeFromRequirements system.

This module provides command-line interface for generating code from requirements,
integrating with metadata analysis, requirement checking, and validation systems.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from core.generator import CodeGenerator
from utils.config import GenerationConfig
from utils.helpers import GenerationHelper
from models.generation_result import GenerationResult, GenerationStatus


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate code from requirements with AI assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic code generation
  python main.py --project-path /path/to/project --requirements requirements.csv --metadata metadata.json --output /path/to/output

  # With existing requirements for comparison
  python main.py --project-path /path/to/project --requirements new_requirements.csv --existing-requirements old_requirements.csv --metadata metadata.json --output /path/to/output

  # With custom configuration
  python main.py --project-path /path/to/project --requirements requirements.csv --metadata metadata.json --output /path/to/output --config config.json

  # Verbose output with JSON format
  python main.py --project-path /path/to/project --requirements requirements.csv --metadata metadata.json --output /path/to/output --verbose --format json
        """,
    )

    # Required arguments
    parser.add_argument(
        "--project-path",
        "-p",
        required=True,
        help="Path to the source project directory",
    )

    parser.add_argument(
        "--requirements", "-r", required=True, help="Path to requirements CSV file"
    )

    parser.add_argument(
        "--metadata", "-m", required=True, help="Path to project metadata JSON file"
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to output directory for generated code",
    )

    # Optional arguments
    parser.add_argument(
        "--existing-requirements",
        "-e",
        help="Path to existing requirements CSV file for comparison",
    )

    parser.add_argument("--config", "-c", help="Path to configuration JSON file")

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "yaml", "text"],
        default="json",
        help="Output format for results (default: json)",
    )

    parser.add_argument(
        "--output-result", "-or", help="Path to save generation result file"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Analyze requirements without generating code",
    )

    parser.add_argument("--no-tests", action="store_true", help="Skip test generation")

    parser.add_argument(
        "--no-validation", action="store_true", help="Skip validation step"
    )

    parser.add_argument(
        "--no-metadata-update", action="store_true", help="Skip metadata update step"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    try:
        # Load configuration
        if args.config and Path(args.config).exists():
            config = GenerationConfig.load_from_file(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        else:
            config = GenerationConfig()
            logger.info("Using default configuration")

        # Override config with command line arguments
        if args.format:
            config.output_format = args.format
        if args.verbose:
            config.verbose_logging = True
        if args.no_tests:
            config.generate_tests = False
        if args.no_validation:
            config.run_tests_after_generation = False
        if args.no_metadata_update:
            config.update_metadata = False

        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            sys.exit(1)

        # Validate input paths
        if not Path(args.project_path).exists():
            logger.error(f"Project path does not exist: {args.project_path}")
            sys.exit(1)

        if not Path(args.requirements).exists():
            logger.error(f"Requirements file does not exist: {args.requirements}")
            sys.exit(1)

        if not Path(args.metadata).exists():
            logger.error(f"Metadata file does not exist: {args.metadata}")
            sys.exit(1)

        if args.existing_requirements and not Path(args.existing_requirements).exists():
            logger.error(
                f"Existing requirements file does not exist: {args.existing_requirements}"
            )
            sys.exit(1)

        # Display configuration summary if verbose
        if args.verbose:
            logger.info("Configuration summary:")
            for line in config.get_summary().split("\n"):
                logger.info(f"  {line}")

        logger.info("Starting code generation process...")
        start_time = time.time()

        # Initialize generator
        generator = CodeGenerator(logger)

        if args.dry_run:
            logger.info("DRY RUN MODE - No code will be generated")
            # TODO: Implement dry run analysis
            result = GenerationResult(GenerationStatus.SUCCESS)
            result.execution_time = time.time() - start_time
        else:
            # Run code generation
            result = generator.generate_from_requirements(
                project_path=args.project_path,
                requirements_path=args.requirements,
                metadata_path=args.metadata,
                output_path=args.output,
                existing_requirements_path=args.existing_requirements,
            )

        # Display results
        if result.status == GenerationStatus.SUCCESS:
            logger.info("✅ Code generation completed successfully!")
        elif result.status == GenerationStatus.PARTIAL_SUCCESS:
            logger.warning("⚠️ Code generation completed with some issues")
        else:
            logger.error("❌ Code generation failed")

        # Display summary
        print("\n" + "=" * 60)
        print("CODE GENERATION SUMMARY")
        print("=" * 60)
        print(result.get_summary())

        # Save result to file if requested
        if args.output_result:
            output_path = args.output_result
        else:
            output_path = str(
                Path(args.output) / f"generation_result.{config.output_format}"
            )

        if GenerationHelper.save_result_to_file(
            result.to_dict(), output_path, config.output_format
        ):
            logger.info(f"Results saved to: {output_path}")
        else:
            logger.error(f"Failed to save results to: {output_path}")

        # Exit with appropriate code
        if result.status == GenerationStatus.FAILED:
            sys.exit(1)
        elif result.status == GenerationStatus.PARTIAL_SUCCESS:
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def create_sample_config():
    """Create a sample configuration file."""
    config = GenerationConfig()
    config_path = "config_example.json"

    if config.save_to_file(config_path):
        print(f"Sample configuration created: {config_path}")
        print("Edit this file to customize your settings.")
    else:
        print("Failed to create sample configuration file.")


def validate_installation():
    """Validate that all dependencies are properly installed."""
    import importlib

    required_modules = ["pathlib", "json", "logging", "ast", "typing"]

    optional_modules = [
        ("yaml", "PyYAML - for YAML output format"),
        ("black", "Black - for code formatting"),
    ]

    print("Validating installation...")

    # Check required modules
    missing_required = []
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_required.append(module)

    if missing_required:
        print(f"❌ Missing required modules: {', '.join(missing_required)}")
        return False

    print("✅ All required modules available")

    # Check optional modules
    missing_optional = []
    for module, description in optional_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_optional.append((module, description))

    if missing_optional:
        print("\n⚠️ Optional modules not available:")
        for module, description in missing_optional:
            print(f"  - {description}")
        print("Install these for enhanced functionality.")

    return True


if __name__ == "__main__":
    # Handle special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-config":
            create_sample_config()
            sys.exit(0)
        elif sys.argv[1] == "validate":
            if validate_installation():
                sys.exit(0)
            else:
                sys.exit(1)

    main()
