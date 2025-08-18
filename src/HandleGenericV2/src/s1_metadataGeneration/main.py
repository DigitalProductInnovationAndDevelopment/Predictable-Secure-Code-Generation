"""
Main entry point for S1 Metadata Generation

This module checks if the required output files exist and runs coldStart
if they don't exist, otherwise generates metadata using the existing language architecture.
"""

import os
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add the HandleGenericV2 directory to the path so we can import config
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")  # Go to HandleGenericV2
sys.path.insert(0, project_root)

# Alternative: use absolute path
sys.path.insert(
    0,
    "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGenericV2",
)

from config import Config
from .core.coldStart import analyze_codebase_with_ai
from .core.generateMetadata import generate_codebase_metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

config = Config()


def check_output_files_exist() -> bool:
    """
    Check if the required output files exist.

    Returns:
        bool: True if all required files exist, False otherwise
    """
    try:
        # Get output directory and filename from config
        output_dir = getattr(config, "OUTPUT_DIR", None) or "./output"
        filename = (
            getattr(config, "LANGUAGE_ARCHITECTURE", None) or "language_architecture"
        )

        # Ensure filename has .json extension
        if not filename.endswith(".json"):
            filename += ".json"

        # Check if the file exists
        file_path = Path(output_dir) / filename
        exists = file_path.exists()

        logger.info(f"Checking for output file: {file_path}")
        logger.info(f"File exists: {exists}")

        return exists

    except Exception as e:
        logger.error(f"Error checking output files: {e}")
        return False


def main():
    """
    Main function that checks output files and runs coldStart or generates metadata accordingly.
    """
    logger.info("Starting S1 Metadata Generation")

    # Check if output files exist
    if check_output_files_exist():
        logger.info("Language architecture already exists - generating metadata")
        print("Language architecture exists - generating metadata...")

        try:
            # Get configuration values
            codebase_root = getattr(config, "CODEBASE_ROOT", None)
            workspace = getattr(config, "WORKSPACE", "LOCAL")
            output_dir = getattr(config, "OUTPUT_DIR", None)

            # Validate required config values
            if not codebase_root:
                raise ValueError("CODEBASE_ROOT must be set in config")
            if not output_dir:
                raise ValueError("OUTPUT_DIR must be set in config")

            logger.info(f"Using CODEBASE_ROOT: {codebase_root}")
            logger.info(f"Using WORKSPACE: {workspace}")
            logger.info(f"Using OUTPUT_DIR: {output_dir}")

            # Generate metadata using the existing language architecture
            metadata_result = generate_codebase_metadata(
                codebase_path=codebase_root, output_dir=output_dir, workspace=workspace
            )

            logger.info("Metadata generation completed successfully")
            print(f"Metadata generation completed successfully!")
            print(f"Total files analyzed: {metadata_result['total_files']}")
            print(f"Output saved to: {os.path.join(output_dir, 'metadata.json')}")

        except Exception as e:
            logger.error(f"Error during metadata generation: {e}")
            print(f"Error during metadata generation: {e}")

    else:
        logger.info("Output files do not exist - running coldStart")
        print("Running coldStart...")

        try:
            # Get codebase root from config
            codebase_root = getattr(config, "CODEBASE_ROOT", None) or "."

            # Run coldStart analysis
            analysis_result = analyze_codebase_with_ai(codebase_root)

            logger.info("ColdStart completed successfully")
            print(f"Analysis completed: {analysis_result}")

        except Exception as e:
            logger.error(f"Error during coldStart: {e}")
            print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
