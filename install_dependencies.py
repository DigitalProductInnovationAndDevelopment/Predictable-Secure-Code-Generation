#!/usr/bin/env python3
"""
Dependency installation script for the automated code generation system.
This script installs all required dependencies for the project.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"❌ Python 3.8+ is required. Current version: {version.major}.{version.minor}"
        )
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def main():
    """Main installation function"""
    print("🚀 Installing dependencies for Automated Code Generation System")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Change to project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")

    # Installation commands
    install_commands = [
        {
            "command": "python -m pip install --upgrade pip",
            "description": "Upgrade pip to latest version",
        },
        {
            "command": "pip install -r requirements.txt",
            "description": "Install main project dependencies",
        },
        {
            "command": "pip install -r tests/requirements.txt",
            "description": "Install test dependencies",
        },
    ]

    # Optional development tools
    dev_commands = [
        {
            "command": "pip install pre-commit",
            "description": "Install pre-commit hooks (optional)",
        },
        {
            "command": "pip install jupyter",
            "description": "Install Jupyter for development (optional)",
        },
    ]

    success_count = 0
    total_count = len(install_commands)

    # Run main installation commands
    for cmd in install_commands:
        if run_command(cmd["command"], cmd["description"]):
            success_count += 1
        else:
            print(f"⚠️  Failed to install: {cmd['description']}")

    # Install optional development tools
    print("\n📦 Installing optional development tools...")
    for cmd in dev_commands:
        run_command(cmd["command"], cmd["description"])

    # Verify critical imports
    print("\n🔍 Verifying critical imports...")
    critical_imports = [
        "azure.functions",
        "pandas",
        "openai",
        "flake8",
        "black",
        "pytest",
    ]

    import_success = 0
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
            import_success += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print(f"Main dependencies: {success_count}/{total_count} successful")
    print(f"Import verification: {import_success}/{len(critical_imports)} successful")

    if success_count == total_count and import_success == len(critical_imports):
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run:")
        print("   python function_app.py")
        print("   python tests/run_tests.py")
        return 0
    else:
        print("⚠️  Some installations failed. Please check errors above.")
        print("\n🔧 Manual installation:")
        print("   pip install azure-functions pandas openai flake8 black pytest")
        return 1


if __name__ == "__main__":
    sys.exit(main())
