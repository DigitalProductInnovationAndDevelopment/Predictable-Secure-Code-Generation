#!/usr/bin/env python3
"""
CLI entry point that works around Python's built-in platform module collision.
Run this from the project root directory.
"""

import sys
import os
from pathlib import Path

# Add our platform directory to the path first, then remove built-in platform
platform_src_dir = Path(__file__).parent / "src" / "HandleGeneric v2" / "src"
sys.path.insert(0, str(platform_src_dir))

# Remove the built-in platform module from cache if it was imported
if "platform" in sys.modules:
    del sys.modules["platform"]


def main():
    """Main CLI entry point."""
    try:
        # Import our CLI after path manipulation
        from platform.interfaces.cli.main import app

        # Run the CLI
        app()

    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        print("💡 Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
