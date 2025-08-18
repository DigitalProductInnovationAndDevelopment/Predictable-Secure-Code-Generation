"""
Main entry point for S1 Metadata Generation

This module checks if the required output files exist and runs coldStart
if they don't exist, otherwise prints "second run".
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

from config import Config
from .core.coldStart import analyze_codebase_with_ai

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
    Main function that checks output files and runs coldStart if needed.
    """
    logger.info("Starting S1 Metadata Generation")

    # Check if output files exist
    if check_output_files_exist():
        logger.info("Output files already exist - this is a second run")
        print("Second run")
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
