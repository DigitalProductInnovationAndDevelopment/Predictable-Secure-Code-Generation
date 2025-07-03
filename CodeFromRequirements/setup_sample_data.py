#!/usr/bin/env python3
"""
Setup script to initialize sample data and test the automated code update system.
"""

import os
import sys
import json
from datetime import datetime
from CodeFromRequirements.requirements_checker import RequirementsChecker
from CodeFromRequirements.metadata_manager import MetadataManager
from config import Config


def setup_directories():
    """Create necessary directories"""
    directories = ["data", "tests", "auth", "database", "api", "features"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def create_sample_requirements():
    """Create sample requirements file"""
    req_checker = RequirementsChecker()
    req_checker.create_sample_requirements_file()
    print(f"Created sample requirements file: {req_checker.requirements_file}")


def initialize_metadata():
    """Initialize metadata file"""
    metadata_manager = MetadataManager()
    metadata = (
        metadata_manager.load_metadata()
    )  # This will create default if not exists
    metadata_manager.save_metadata(metadata)
    print(f"Initialized metadata file: {metadata_manager.metadata_file}")


def create_sample_env_file():
    """Create a sample environment file"""
    env_content = """# Automated Code Update System Environment Variables

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# File Paths
REQUIREMENTS_FILE=data/requirements.csv
METADATA_FILE=data/metadata.json
STATUS_LOG_FILE=data/status_log.json
CODEBASE_ROOT=.

# Validation Settings
MAX_RETRIES=3
VALIDATION_TIMEOUT=300
PYTHON_FORMATTER=black
LINTER=flake8
TEST_COMMAND=pytest

# Azure Function Settings
AZURE_FUNCTION_TIMEOUT=600
"""

    with open(".env.sample", "w") as f:
        f.write(env_content)

    print("Created .env.sample file")
    print("Copy .env.sample to .env and update with your actual API keys")


def validate_configuration():
    """Validate system configuration"""
    try:
        config = Config()
        errors = config.validate_config()

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("Configuration validation passed")

    except Exception as e:
        print(f"Error validating configuration: {str(e)}")


def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Azure Functions
local.settings.json
.azure/
.funcignore

# Environment variables
.env

# Logs
*.log
logs/

# Data files (optional, depending on your needs)
data/metadata.json
data/status_log.json

# Backups
*.backup

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.pytest_cache/
htmlcov/
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

    print("Created .gitignore file")


def create_test_files():
    """Create basic test files"""

    # Test for requirements checker
    test_requirements_checker = '''import pytest
from requirements_checker import RequirementsChecker

def test_requirements_checker_initialization():
    """Test RequirementsChecker can be initialized"""
    checker = RequirementsChecker()
    assert checker is not None
    assert hasattr(checker, 'requirements_file')

def test_check_for_updates_no_file():
    """Test check_for_updates with no requirements file"""
    checker = RequirementsChecker()
    # Temporarily change to non-existent file
    original_file = checker.requirements_file
    checker.requirements_file = "non_existent_file.csv"
    
    has_updates, requirements = checker.check_for_updates()
    
    assert has_updates is False
    assert requirements == []
    
    # Restore original file
    checker.requirements_file = original_file
'''

    os.makedirs("tests", exist_ok=True)
    with open("tests/test_requirements_checker.py", "w") as f:
        f.write(test_requirements_checker)

    # Test for config
    test_config = '''import pytest
from config import Config

def test_config_initialization():
    """Test Config can be initialized"""
    config = Config()
    assert config is not None

def test_config_has_required_attributes():
    """Test Config has required attributes"""
    config = Config()
    assert hasattr(config, 'REQUIREMENTS_FILE')
    assert hasattr(config, 'OPENAI_API_KEY')
    assert hasattr(config, 'MAX_RETRIES')

def test_config_validation():
    """Test configuration validation"""
    config = Config()
    errors = config.validate_config()
    assert isinstance(errors, list)
'''

    with open("tests/test_config.py", "w") as f:
        f.write(test_config)

    # Create __init__.py for tests
    with open("tests/__init__.py", "w") as f:
        f.write("# Test package")

    print("Created basic test files")


def run_basic_tests():
    """Run basic system tests"""
    print("\nRunning basic system tests...")

    try:
        # Test requirements checker
        req_checker = RequirementsChecker()
        has_updates, requirements = req_checker.check_for_updates()
        print(f"   Requirements check: {len(requirements)} requirements found")

        # Test metadata manager
        metadata_manager = MetadataManager()
        metadata = metadata_manager.load_metadata()
        print(f"   Metadata loaded: {len(metadata)} keys")

        # Test configuration
        config = Config()
        errors = config.validate_config()
        print(f"   Configuration: {len(errors)} validation errors")

        print("Basic system tests completed")

    except Exception as e:
        print(f"Error running basic tests: {str(e)}")


def main():
    """Main setup function"""
    print("Setting up Automated Code Update System...\n")

    # Create directories
    setup_directories()
    print()

    # Create sample data
    create_sample_requirements()
    initialize_metadata()
    print()

    # Create configuration files
    create_sample_env_file()
    create_gitignore()
    print()

    # Create test files
    create_test_files()
    print()

    # Validate configuration
    validate_configuration()
    print()

    # Run basic tests
    run_basic_tests()

    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.sample to .env and add your OpenAI API key")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run tests: pytest")
    print("4. Start the function: func start")
    print("5. Test manually: curl http://localhost:7071/api/status")


if __name__ == "__main__":
    main()
