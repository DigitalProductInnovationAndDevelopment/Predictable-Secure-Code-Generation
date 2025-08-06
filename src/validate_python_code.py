#!/usr/bin/env python3
"""
Simple Python syntax validation script for a directory.
"""

import sys
import os
from pathlib import Path


def validate_python_files(directory):
    """Validate all Python files in the given directory recursively."""
    directory = Path(directory)
    py_files = list(directory.rglob("*.py"))
    results = []
    print(f"🔎 Validating Python files in: {directory}")
    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            compile(source, str(py_file), "exec")
            results.append((py_file, True, None))
        except SyntaxError as e:
            results.append((py_file, False, f"SyntaxError: {e}"))
        except Exception as e:
            results.append((py_file, False, f"Error: {e}"))

    # Print summary
    valid_count = sum(1 for _, valid, _ in results if valid)
    invalid_count = len(results) - valid_count
    print(f"\nValidation Summary:")
    print(f"  Total Python files checked: {len(results)}")
    print(f"  Valid files: {valid_count}")
    print(f"  Invalid files: {invalid_count}")
    if invalid_count > 0:
        print(f"\n❌ Invalid files:")
        for py_file, valid, error in results:
            if not valid:
                print(f"  {py_file}: {error}")
    else:
        print("\n✅ All files are valid!")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_python_code.py <directory>")
        sys.exit(1)
    validate_python_files(sys.argv[1])
