#!/usr/bin/env python3
"""
Test runner for HandleGeneric package.

This script provides an easy way to run tests with different configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=True, verbose=False):
    """
    Run tests with specified configuration.

    Args:
        test_type: Type of tests to run ('all', 'unit', 'integration', 'providers', 'core', 'utils')
        coverage: Whether to run with coverage
        verbose: Whether to run in verbose mode
    """
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test type filters
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "providers":
        cmd.extend(["-m", "providers"])
    elif test_type == "core":
        cmd.extend(["-m", "core"])
    elif test_type == "utils":
        cmd.extend(["-m", "utils"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])

    # Add coverage options
    if coverage:
        cmd.extend(["--cov=HandleGeneric", "--cov-report=term-missing"])

    # Add verbose option
    if verbose:
        cmd.append("-v")

    # Add test directory
    cmd.append("tests/")

    print(f"Running tests: {' '.join(cmd)}")
    print("=" * 50)

    # Run tests
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description="Run HandleGeneric tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "providers", "core", "utils", "fast"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Run tests without coverage"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests in verbose mode"
    )

    args = parser.parse_args()

    # Run tests
    exit_code = run_tests(
        test_type=args.type, coverage=not args.no_coverage, verbose=args.verbose
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    import os

    main()
