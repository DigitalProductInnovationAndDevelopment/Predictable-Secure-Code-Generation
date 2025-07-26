#!/usr/bin/env python3
"""
Main CLI interface for the validation system.

Usage:
    python -m src.ValidtaionUnit.main <codebase_path> <metadata_path> [options]

Example:
    python -m src.ValidtaionUnit.main input/code output/enviroment/metadata.json --output-dir output/validation
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Optional

from src.HandleCs.ValidationUnit.core.validator import CodebaseValidator
from src.HandleCs.ValidationUnit.utils.config import ValidationConfig
from src.HandleCs.ValidationUnit.models.validation_result import ValidationStatus


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Comprehensive codebase validation system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python -m src.ValidtaionUnit.main input/code output/enviroment/metadata.json
  
  # With custom output directory
  python -m src.ValidtaionUnit.main input/code metadata.json --output-dir validation_results
  
  # Only run syntax validation
  python -m src.ValidtaionUnit.main input/code metadata.json --steps syntax
  
  # Run with custom configuration
  python -m src.ValidtaionUnit.main input/code metadata.json --config validation_config.json
  
  # Verbose output
  python -m src.ValidtaionUnit.main input/code metadata.json --verbose
        """,
    )

    # Required arguments
    parser.add_argument(
        "codebase_path", help="Path to the codebase directory to validate"
    )

    parser.add_argument("metadata_path", help="Path to the metadata.json file")

    # Optional arguments
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory to save validation report (default: current directory)",
    )

    parser.add_argument(
        "--config", "-c", help="Path to validation configuration file (JSON/YAML)"
    )

    parser.add_argument(
        "--steps",
        choices=["syntax", "test", "ai", "all"],
        nargs="+",
        default=["all"],
        help="Validation steps to run (default: all)",
    )

    parser.add_argument(
        "--output-format",
        "-f",
        choices=["json", "yaml", "text"],
        default="json",
        help="Output format for validation report (default: json)",
    )

    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop validation on first failure",
    )

    parser.add_argument("--no-ai", action="store_true", help="Disable AI validation")

    parser.add_argument(
        "--test-timeout",
        type=int,
        default=300,
        help="Test execution timeout in seconds (default: 300)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress output except errors"
    )

    parser.add_argument(
        "--no-report", action="store_true", help="Don't save validation report to file"
    )

    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only show summary, don't save detailed report",
    )

    return parser


def load_config(
    config_path: Optional[str], args: argparse.Namespace
) -> ValidationConfig:
    """Load configuration from file and command line arguments."""
    # Start with default config
    if config_path:
        try:
            config = ValidationConfig.from_file(config_path)
            print(f"Loaded configuration from: {config_path}")
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
            config = ValidationConfig()
    else:
        config = ValidationConfig()

    # Override with command line arguments
    if "all" not in args.steps:
        config.enable_syntax_validation = "syntax" in args.steps
        config.enable_test_validation = "test" in args.steps
        config.enable_ai_validation = "ai" in args.steps and not args.no_ai
    else:
        if args.no_ai:
            config.enable_ai_validation = False

    config.output_format = args.output_format
    config.stop_on_first_failure = args.stop_on_failure
    config.test_timeout = args.test_timeout
    config.save_report = not args.no_report
    config.verbose_output = args.verbose

    if args.quiet:
        config.log_level = "ERROR"
    elif args.verbose:
        config.log_level = "DEBUG"

    return config


def print_summary(validator: CodebaseValidator, result, args: argparse.Namespace):
    """Print validation summary to console."""
    if args.quiet:
        return

    print("\n" + "=" * 60)
    summary = validator.get_validation_summary(result)
    print(summary)

    # Print file location if report was saved
    if not args.no_report and args.output_dir:
        report_file = os.path.join(
            args.output_dir, f"validation_report.{args.output_format}"
        )
        if os.path.exists(report_file):
            print(f"\nDetailed report saved to: {report_file}")


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Validate input paths
        if not os.path.exists(args.codebase_path):
            print(f"Error: Codebase path does not exist: {args.codebase_path}")
            sys.exit(1)

        if not os.path.exists(args.metadata_path):
            print(f"Error: Metadata file does not exist: {args.metadata_path}")
            sys.exit(1)

        # Load configuration
        config = load_config(args.config, args)

        # Initialize validator
        if not args.quiet:
            print(f"Initializing validator...")
            print(f"Codebase: {args.codebase_path}")
            print(f"Metadata: {args.metadata_path}")
            print(
                f"Steps enabled: {', '.join([step for step, enabled in [('syntax', config.enable_syntax_validation), ('test', config.enable_test_validation), ('ai', config.enable_ai_validation)] if enabled])}"
            )

        validator = CodebaseValidator(config)

        # Run validation
        if not args.quiet:
            print(f"\nStarting validation...")

        result = validator.validate_codebase(
            args.codebase_path, args.metadata_path, args.output_dir
        )

        # Print summary
        print_summary(validator, result, args)

        # Exit with appropriate code
        if result.is_valid:
            if not args.quiet:
                print(f"\n🎉 Validation completed successfully!")
            sys.exit(0)
        else:
            if not args.quiet:
                print(
                    f"\n❌ Validation failed with {result.total_error_count()} errors"
                )
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
