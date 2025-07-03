#!/usr/bin/env python3
"""
Test runner script for the automated code generation system.
This script runs all tests and generates coverage reports.
"""

import subprocess
import sys
import os
import logging


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def run_command(command, description):
    """Run a shell command and log the result"""
    logger = logging.getLogger(__name__)
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        logger.info(f"Success: {description}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False


def main():
    """Main test runner function"""
    setup_logging()
    logger = logging.getLogger(__name__)

    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    logger.info("Starting automated code generation system tests")
    logger.info(f"Working directory: {os.getcwd()}")

    # Test commands to run
    test_commands = [
        {
            "command": "python -m pytest tests/ -v --tb=short",
            "description": "Run all unit tests",
        },
        {
            "command": "python -m pytest tests/ --cov=CodeFromRequirements --cov=function_app --cov=config --cov-report=term-missing",
            "description": "Run tests with coverage",
        },
        {
            "command": "python -m pytest tests/ --cov=CodeFromRequirements --cov=function_app --cov=config --cov-report=html",
            "description": "Generate HTML coverage report",
        },
    ]

    # Optional: Run specific test categories
    specific_tests = [
        {
            "command": "python -m pytest tests/test_config.py -v",
            "description": "Run config tests",
        },
        {
            "command": "python -m pytest tests/test_function_app.py -v",
            "description": "Run function app tests",
        },
        {
            "command": "python -m pytest tests/test_requirements_checker.py -v",
            "description": "Run requirements checker tests",
        },
        {
            "command": "python -m pytest tests/test_code_analyzer.py -v",
            "description": "Run code analyzer tests",
        },
        {
            "command": "python -m pytest tests/test_ai_code_editor.py -v",
            "description": "Run AI code editor tests",
        },
        {
            "command": "python -m pytest tests/test_code_validator.py -v",
            "description": "Run code validator tests",
        },
    ]

    success_count = 0
    total_count = len(test_commands)

    # Run main test commands
    for test_cmd in test_commands:
        if run_command(test_cmd["command"], test_cmd["description"]):
            success_count += 1
        else:
            logger.error(f"Test failed: {test_cmd['description']}")

    # Run specific tests if main tests pass
    if success_count == total_count:
        logger.info("Running specific module tests...")
        for test_cmd in specific_tests:
            run_command(test_cmd["command"], test_cmd["description"])

    # Summary
    logger.info(f"Test Summary: {success_count}/{total_count} test suites passed")

    if success_count == total_count:
        logger.info("All tests completed successfully!")
        logger.info("Coverage report generated in htmlcov/index.html")
        return 0
    else:
        logger.error("Some tests failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
