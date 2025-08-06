#!/bin/bash

# HandleGeneric Essential Testing Commands
# Assumes you are in the project root: /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation

# 1. METADATA GENERATION
# ----------------------
# Generate metadata
PYTHONPATH=src python -m HandleGeneric.cli.main generate-metadata output/PythonExample/generated_code output/PythonExample/environment

# Generate metadata with verbose output and show details
PYTHONPATH=src python -m HandleGeneric.cli.main generate-metadata output/PythonExample/generated_code output/PythonExample/environment --show-details --verbose

# Generate metadata for Python files only
PYTHONPATH=src python -m HandleGeneric.cli.main generate-metadata output/PythonExample/generated_code output/PythonExample/environment --languages python

# Generate metadata with custom filename
PYTHONPATH=src python -m HandleGeneric.cli.main generate-metadata output/PythonExample/generated_code output/PythonExample/environment --filename metadata_custom.json

# 2. CODE VALIDATION
# ------------------
# Full 3-layer validation (syntax, test, AI)
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/

# Syntax validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps syntax --output-dir output/PythonExample/environment/

# Test validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps test --output-dir output/PythonExample/environment/

# AI validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps ai --output-dir output/PythonExample/environment/

# Validate using CLI (simpler syntax)
PYTHONPATH=src python -m HandleGeneric.cli.main validate output/PythonExample/generated_code --show-details

# Validate Python files only
PYTHONPATH=src python -m HandleGeneric.cli.main validate output/PythonExample/generated_code --languages python --show-details

# Validation with verbose output
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/ --verbose

# 3. CODE GENERATION
# ------------------
# Note: Code generation requires a requirements file (JSON or CSV) as input
# Create a simple requirements file first, then generate code

# List supported languages
PYTHONPATH=src python -m HandleGeneric.cli.main list-languages

# Create a template for Python
PYTHONPATH=src python -m HandleGeneric.cli.main create-template python class output/PythonExample/environment/ --filename Calculator.py

# Generate code (example - you'll need to create requirements.json first)
# PYTHONPATH=src python -m HandleGeneric.cli.main generate-code requirements.json python output/PythonExample/environment/generated_code_new

# Generate code with context
# PYTHONPATH=src python -m HandleGeneric.cli.main generate-code requirements.json python output/PythonExample/environment/generated_code_new --context "Create a calculator application"

# Generate code without tests
# PYTHONPATH=src python -m HandleGeneric.cli.main generate-code requirements.json python output/PythonExample/environment/generated_code_new --no-tests

# Generate code with detailed output
# PYTHONPATH=src python -m HandleGeneric.cli.main generate-code requirements.json python output/PythonExample/environment/generated_code_new --show-details 