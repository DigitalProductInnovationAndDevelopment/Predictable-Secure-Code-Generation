#!/usr/bin/env python3
"""
Quick setup script to install essential dependencies and fix import errors.
Run this script to quickly resolve the 'openai' module not found error.
"""

import subprocess
import sys


def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False


def main():
    print("🚀 Quick Setup - Installing Essential Dependencies")
    print("=" * 50)

    # Essential packages needed to run the system
    essential_packages = [
        "openai>=1.3.0",
        "azure-functions>=1.14.0",
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
        "requests>=2.25.0",
        "pytest>=7.0.0",
    ]

    print("Installing essential packages...")
    success_count = 0

    for package in essential_packages:
        if install_package(package):
            success_count += 1

    print("\n" + "=" * 50)
    print(
        f"Installation Summary: {success_count}/{len(essential_packages)} packages installed"
    )

    if success_count == len(essential_packages):
        print("🎉 All essential packages installed successfully!")
        print("\nYou can now run:")
        print("  python function_app.py")
        print("  python tests/run_tests.py")

        # Test import
        try:
            import openai

            print("✅ OpenAI package import successful")
        except ImportError:
            print("⚠️  OpenAI import still failing - try restarting your environment")

    else:
        print("⚠️  Some packages failed to install.")
        print("Try running: pip install -r requirements.txt")

    return 0 if success_count == len(essential_packages) else 1


if __name__ == "__main__":
    sys.exit(main())
