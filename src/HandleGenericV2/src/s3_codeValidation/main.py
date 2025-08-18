#!/usr/bin/env python3
"""
Main CLI interface for S3 Code Validation system.

This module provides command-line interface for validating code using AI assistance,
monitoring code quality, and tracking validation results.
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path

# Add the HandleGenericV2 directory to the path so we can import config
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")  # Go to HandleGenericV2
sys.path.insert(0, project_root)

try:
    from config import Config
    from .core.codeValidator import CodeValidator
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative import path
    sys.path.insert(0, os.path.join(project_root, "src"))
    try:
        from config import Config
        from .core.codeValidator import CodeValidator
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        # Try absolute path
        absolute_path = "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGenericV2"
        sys.path.insert(0, absolute_path)
        from config import Config
        from .core.codeValidator import CodeValidator


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def validate_code(verbose: bool = False) -> dict:
    """
    Validate all code files using AI assistance.

    Returns:
        dict: Validation results and summary
    """
    try:
        print("🚀 Starting comprehensive code validation...")

        # Initialize configuration and validator
        config = Config()
        validator = CodeValidator(config)

        # Perform validation
        result = validator.validate_all_code()

        if result["status"] == "success":
            summary = result["summary"]
            print(f"\n🎉 Validation completed successfully!")
            print(f"📁 Total Files: {summary['total_files']}")
            print(f"✅ Passed: {summary['passed_files']}")
            print(f"❌ Failed: {summary['failed_files']}")
            print(f"📊 Pass Rate: {summary['pass_rate']:.1f}%")
            print(f"🎯 Overall Score: {summary['overall_score']:.1f}/100")

            # Show detailed summary
            print("\n📋 Detailed Summary:")
            detailed_summary = validator.get_validation_summary()
            if detailed_summary["status"] == "success":
                issue_breakdown = detailed_summary["issue_breakdown"]
                print(f"🚨 High Priority Issues: {issue_breakdown['high_priority']}")
                print(f"⚠️ Medium Priority Issues: {issue_breakdown['medium_priority']}")
                print(f"💡 Low Priority Issues: {issue_breakdown['low_priority']}")

                print("\n💡 Recommendations:")
                for rec in detailed_summary["recommendations"]:
                    print(f"  {rec}")
            else:
                print(
                    f"Could not generate detailed summary: {detailed_summary.get('error', 'Unknown error')}"
                )
        else:
            print(f"❌ Validation failed: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return {"error": f"Validation failed: {str(e)}"}


def show_validation_status() -> dict:
    """
    Show current validation status.

    Returns:
        dict: Current validation status
    """
    try:
        print("📊 Current Validation Status")
        print("=" * 50)

        # Initialize configuration and validator
        config = Config()
        validator = CodeValidator(config)

        # Get status
        status = validator.get_validation_status()

        print(f"📊 Current Status: {status['current_status']}")
        print(f"📋 Total Validations: {status['total_validations']}")
        print(f"✅ Passed: {status['passed_validations']}")
        print(f"❌ Failed: {status['failed_validations']}")
        print(f"🔤 Language: {status['language']}")
        print(f"🌐 Workspace: {status['workspace']}")
        print(
            f"🤖 AI Client: {'Available' if status['ai_client_available'] else 'Not Available'}"
        )

        # Show last validation if available
        if status.get("last_validation"):
            last_val = status["last_validation"]
            print(
                f"\n📅 Last Validation: {last_val.get('validation_timestamp', 'Unknown')}"
            )
            print(f"📁 Files Validated: {last_val.get('total_files', 0)}")
            print(f"✅ Passed: {last_val.get('passed_files', 0)}")
            print(f"❌ Failed: {last_val.get('failed_files', 0)}")
            print(f"📊 Pass Rate: {last_val.get('pass_rate', 0):.1f}%")
            print(f"🎯 Overall Score: {last_val.get('overall_score', 0):.1f}/100")

        return status

    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return {"error": f"Status check failed: {str(e)}"}


def show_validation_summary() -> dict:
    """
    Show comprehensive validation summary.

    Returns:
        dict: Validation summary with recommendations
    """
    try:
        print("📋 Validation Summary")
        print("=" * 50)

        # Initialize configuration and validator
        config = Config()
        validator = CodeValidator(config)

        # Get summary
        summary = validator.get_validation_summary()

        if summary["status"] == "success":
            overall_summary = summary["overall_summary"]
            issue_breakdown = summary["issue_breakdown"]

            print(f"📁 Total Files: {overall_summary.get('total_files', 0)}")
            print(f"✅ Passed: {overall_summary.get('passed_files', 0)}")
            print(f"❌ Failed: {overall_summary.get('failed_files', 0)}")
            print(f"📊 Pass Rate: {overall_summary.get('pass_rate', 0):.1f}%")
            print(
                f"🎯 Overall Score: {overall_summary.get('overall_score', 0):.1f}/100"
            )

            print(f"\n🚨 Issue Breakdown:")
            print(f"  High Priority: {issue_breakdown['high_priority']}")
            print(f"  Medium Priority: {issue_breakdown['medium_priority']}")
            print(f"  Low Priority: {issue_breakdown['low_priority']}")

            print(f"\n💡 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  {rec}")

            validation_history = summary["validation_history"]
            print(f"\n📚 Validation History:")
            print(f"  Total Validations: {validation_history['total_validations']}")
            print(f"  Success Rate: {validation_history['success_rate']:.1f}%")

        else:
            print(
                f"❌ Could not generate summary: {summary.get('error', 'Unknown error')}"
            )

        return summary

    except Exception as e:
        print(f"❌ Error getting summary: {e}")
        return {"error": f"Summary generation failed: {str(e)}"}


def reset_validation_log() -> dict:
    """
    Reset the validation log.

    Returns:
        dict: Reset confirmation
    """
    try:
        print("🔄 Resetting validation log...")

        # Initialize configuration and validator
        config = Config()
        validator = CodeValidator(config)

        # Reset log
        validator.reset_validation_log()

        print("✅ Validation log reset successfully")
        return {"status": "success", "message": "Validation log reset successfully"}

    except Exception as e:
        print(f"❌ Error resetting log: {e}")
        return {"error": f"Log reset failed: {str(e)}"}


def test_ai_connection() -> dict:
    """
    Test AI client connection.

    Returns:
        dict: Connection test results
    """
    try:
        print("🤖 Testing AI client connection...")

        # Initialize configuration and validator
        config = Config()
        validator = CodeValidator(config)

        if validator.ai_client:
            # Test connection
            result = validator.ai_client.test_connection()
            if result:
                print("✅ AI client connection successful")
                return {
                    "status": "success",
                    "message": "AI client connection successful",
                }
            else:
                print("❌ AI client connection failed")
                return {"status": "error", "message": "AI client connection failed"}
        else:
            print("❌ AI client not available")
            return {"status": "error", "message": "AI client not available"}

    except Exception as e:
        print(f"❌ Error testing AI connection: {e}")
        return {"error": f"AI connection test failed: {str(e)}"}


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="S3 Code Validation - Validate code using AI assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all code files
  python main.py --validate

  # Show current validation status
  python main.py --status

  # Show comprehensive validation summary
  python main.py --summary

  # Reset validation log
  python main.py --reset

  # Test AI client connection
  python main.py --test-ai

  # Validate with verbose logging
  python main.py --validate --verbose

  # Run all validations and show summary
  python main.py --validate --summary
        """,
    )

    # Add arguments
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all code files using AI assistance",
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current validation status",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show comprehensive validation summary",
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the validation log",
    )

    parser.add_argument(
        "--test-ai",
        action="store_true",
        help="Test AI client connection",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Handle different command combinations
    if args.validate:
        print("🚀 Starting code validation...")
        result = validate_code(verbose=args.verbose)
        if "error" in result:
            print(f"❌ Validation failed: {result['error']}")
            return 1
        return 0

    elif args.status:
        print("📊 Checking validation status...")
        result = show_validation_status()
        if "error" in result:
            print(f"❌ Status check failed: {result['error']}")
            return 1
        return 0

    elif args.summary:
        print("📋 Generating validation summary...")
        result = show_validation_summary()
        if "error" in result:
            print(f"❌ Summary generation failed: {result['error']}")
            return 1
        return 0

    elif args.reset:
        print("🔄 Resetting validation log...")
        result = reset_validation_log()
        if "error" in result:
            print(f"❌ Log reset failed: {result['error']}")
            return 1
        return 0

    elif args.test_ai:
        print("🤖 Testing AI connection...")
        result = test_ai_connection()
        if "error" in result:
            print(f"❌ AI test failed: {result['error']}")
            return 1
        return 0

    # Default behavior: validate and show summary
    elif not any([args.validate, args.status, args.summary, args.reset, args.test_ai]):
        print("🚀 S3 Code Validation - Default Mode")
        print("=" * 60)
        print("No specific command provided - running full validation workflow")
        print("=" * 60)

        # Validate code
        print("\n🔍 STEP 1: Validating code...")
        validation_result = validate_code(verbose=args.verbose)

        if "error" in validation_result:
            print(f"❌ Validation failed: {validation_result['error']}")
            return 1

        # Show summary
        print("\n📋 STEP 2: Generating summary...")
        summary_result = show_validation_summary()

        if "error" in summary_result:
            print(f"⚠️ Summary generation had issues: {summary_result['error']}")

        print("\n🎉 Default validation workflow completed!")
        return 0

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    print("❌ No valid command specified. Use --help to see available options.")


if __name__ == "__main__":
    main()
