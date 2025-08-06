#!/usr/bin/env python3
"""
Test script for AI command line interface.
"""

import subprocess
import sys
import os


def test_ai_cli():
    """Test the AI command line interface"""
    print("🖥️  Testing AI Command Line Interface")
    print("=" * 50)

    try:
        # Test the --test flag
        print("Testing --test flag...")
        result = subprocess.run(
            [sys.executable, "src/HandleGeneric/ai/client.py", "--test"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )

        if result.returncode == 0:
            print("✅ Command line test flag works")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Command line test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Command line test timed out")
        return False
    except Exception as e:
        print(f"❌ Command line test error: {e}")
        return False


if __name__ == "__main__":
    success = test_ai_cli()
    sys.exit(0 if success else 1)
