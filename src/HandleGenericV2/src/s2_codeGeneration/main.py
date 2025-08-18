"""
Main CLI interface for S2 Code Generation system.

This module provides command-line interface for checking requirements status
and generating code from requirements with AI assistance.
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path

# Add the HandleGenericV2 directory to the path so we can import config
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate: s2_codeGeneration -> core -> s1_metadataGeneration -> src -> HandleGenericV2
project_root = os.path.join(
    current_dir, "..", "..", "..", ".."
)  # Go to HandleGenericV2
sys.path.insert(0, project_root)

try:
    from config import Config
except ImportError:
    # Try alternative import path
    sys.path.insert(0, os.path.join(project_root, "src"))
    from config import Config


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def check_implemented_requirements_exists() -> bool:
    """
    Check if the IMPLEMENTED_REQUIREMENTS file exists according to config.

    Returns:
        bool: True if file exists, False otherwise
    """
    try:
        config = Config()

        # Debug: Print available attributes
        print(f"🔍 Debug: Config object type: {type(config)}")
        print(
            f"🔍 Debug: Available config attributes: {[attr for attr in dir(config) if not attr.startswith('_')]}"
        )

        # Try different attribute names
        if hasattr(config, "IMPLEMENTED_REQUIREMENTS_FILE"):
            implemented_req_path = config.IMPLEMENTED_REQUIREMENTS_FILE
        elif hasattr(config, "IMPLEMENTED_REQUIREMENTS"):
            implemented_req_path = config.IMPLEMENTED_REQUIREMENTS
        else:
            print(
                "❌ Config object does not have IMPLEMENTED_REQUIREMENTS_FILE or IMPLEMENTED_REQUIREMENTS attributes"
            )
            return False

        # Check if the path is valid (not containing ...)
        if "..." in implemented_req_path:
            print(
                f"⚠️ Warning: Config has invalid path with '...': {implemented_req_path}"
            )
            print("This path needs to be corrected in the config file.")
            return False

        if implemented_req_path and os.path.exists(implemented_req_path):
            print(f"✅ IMPLEMENTED_REQUIREMENTS file exists at: {implemented_req_path}")
            return True
        else:
            print(
                f"❌ IMPLEMENTED_REQUIREMENTS file does not exist at: {implemented_req_path}"
            )
            return False

    except Exception as e:
        print(f"❌ Error checking IMPLEMENTED_REQUIREMENTS file: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="S2 Code Generation - Check requirements status and generate code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check implemented requirements status
  python main.py --check-requirements

  # Check with verbose logging
  python main.py --check-requirements --verbose
        """,
    )

    # Add check requirements option
    parser.add_argument(
        "--check-requirements",
        action="store_true",
        help="Check if IMPLEMENTED_REQUIREMENTS file exists according to config",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.verbose)

    # If just checking requirements, do that and exit
    if args.check_requirements:
        print("🔍 Checking IMPLEMENTED_REQUIREMENTS file status...")
        exists = check_implemented_requirements_exists()
        if exists:
            print("✅ File exists - ready for code generation!")
        else:
            print("❌ File does not exist - needs to be created first")
        return

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    print(
        "❌ No valid command specified. Use --check-requirements to check file status."
    )


if __name__ == "__main__":
    main()
