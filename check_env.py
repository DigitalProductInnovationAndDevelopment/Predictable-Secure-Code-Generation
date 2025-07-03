#!/usr/bin/env python3
"""
Environment Configuration Checker

This script validates that all required environment variables are properly set.
Run this before starting the application to ensure everything is configured correctly.
"""

import os
import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and provide guidance if not"""
    env_file = Path(".env")
    env_template = Path("env.template")

    print("🔍 Checking environment file...")

    if not env_file.exists():
        print("❌ .env file not found!")
        if env_template.exists():
            print("💡 Found env.template file. To get started:")
            print("   cp env.template .env")
            print("   # Then edit .env with your actual values")
        else:
            print("💡 Create a .env file with your configuration.")
        return False
    else:
        print("✅ .env file found")
        return True


def check_required_vars():
    """Check if required environment variables are set"""
    print("\n🔍 Checking required environment variables...")

    required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]

    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        elif value.startswith("your_") or "placeholder" in value.lower():
            missing_vars.append(var)
            print(f"❌ {var}: Still has placeholder value")
        else:
            # Mask sensitive values for display
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")

    return missing_vars


def check_optional_vars():
    """Check optional environment variables"""
    print("\n🔍 Checking optional environment variables...")

    optional_vars = {
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o",
        "OPENAI_API_KEY": "Not set (optional)",
        "AI_MAX_TOKENS": "4000",
        "AI_TEMPERATURE": "0.1",
        "LOG_LEVEL": "INFO",
    }

    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"ℹ️  {var}: {value}")


def load_env_file():
    """Load .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Loading .env file...")
        try:
            with open(env_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ .env file loaded successfully")
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
            return False
    return True


def main():
    """Main function to run all checks"""
    print("🚀 Environment Configuration Checker")
    print("=" * 40)

    # Load .env file first
    if not load_env_file():
        sys.exit(1)

    # Check if .env file exists
    env_exists = check_env_file()

    # Check required variables
    missing_vars = check_required_vars()

    # Check optional variables
    check_optional_vars()

    # Summary
    print("\n📋 Summary:")
    print("=" * 20)

    if missing_vars:
        print("❌ Configuration incomplete!")
        print("Missing required variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Next steps:")
        print("1. Copy env.template to .env if you haven't already")
        print("2. Edit .env and replace placeholder values with real ones")
        print("3. Run this script again to verify")
        sys.exit(1)
    else:
        print("✅ All required environment variables are set!")
        print("🎉 Your environment is ready to go!")


if __name__ == "__main__":
    main()
