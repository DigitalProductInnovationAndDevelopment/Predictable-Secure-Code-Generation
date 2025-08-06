#!/bin/bash

# =============================================================================
# TESTING COMMANDS FOR GENERATED CODE
# =============================================================================
# This file contains all the testing commands you can run via terminal
# Run this file with: bash test_commands.sh
# Or run individual commands as needed
# =============================================================================

echo "🚀 Testing Commands for Generated Code"
echo "======================================"
echo ""

# Set the project root directory
PROJECT_ROOT="/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation"
GENERATED_CODE_DIR="$PROJECT_ROOT/output/PythonExample/generated_code"
ENVIRONMENT_DIR="$PROJECT_ROOT/output/PythonExample/environment"

# Function to run a command and show its output
run_command() {
    echo "📋 Running: $1"
    echo "----------------------------------------"
    eval "$1"
    echo "----------------------------------------"
    echo ""
}

# =============================================================================
# 1. HANDLEGENERIC 3-LAYER VALIDATION
# =============================================================================

echo "🔍 1. HANDLEGENERIC 3-LAYER VALIDATION"
echo "======================================"

# Full 3-layer validation (syntax + test + AI)
echo "Running full 3-layer validation..."
run_command "cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/"

# Syntax validation only
echo "Running syntax validation only..."
run_command "cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps syntax --output-dir output/PythonExample/environment/"

# Test validation only
echo "Running test validation only..."
run_command "cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps test --output-dir output/PythonExample/environment/"

# AI validation only
echo "Running AI validation only..."
run_command "cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps ai --output-dir output/PythonExample/environment/"

# =============================================================================
# 2. PYTHON TESTING COMMANDS
# =============================================================================

echo "🐍 2. PYTHON TESTING COMMANDS"
echo "============================="

# Navigate to generated code directory
run_command "cd $GENERATED_CODE_DIR"

# Run all Python tests with pytest
echo "Running all Python tests with pytest..."
run_command "python -m pytest tests/ -v"

# Run tests with coverage
echo "Running tests with coverage..."
run_command "python -m pytest tests/ --cov=calculator --cov-report=html --cov-report=term"

# Run specific test files
echo "Running specific test files..."
run_command "python -m pytest tests/test_calculator.py -v"
run_command "python -m pytest test_req001.py -v"
run_command "python -m pytest test_req002.py -v"

# Run tests with different output formats
echo "Running tests with different output formats..."
run_command "python -m pytest tests/ --tb=short"
run_command "python -m pytest tests/ --tb=line"
run_command "python -m pytest tests/ --tb=no"

# Run tests and stop on first failure
echo "Running tests and stop on first failure..."
run_command "python -m pytest tests/ -x"

# Run tests with maximum verbosity
echo "Running tests with maximum verbosity..."
run_command "python -m pytest tests/ -vvv"

# =============================================================================
# 3. PYTHON SYNTAX VALIDATION
# =============================================================================

echo "🔍 3. PYTHON SYNTAX VALIDATION"
echo "=============================="

# Check Python syntax for all .py files
echo "Checking Python syntax for all files..."
run_command "find . -name '*.py' -exec python -m py_compile {} \;"

# Run flake8 for code style checking
echo "Running flake8 for code style..."
run_command "python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"

# Run mypy for type checking
echo "Running mypy for type checking..."
run_command "python -m mypy . --ignore-missing-imports"

# Run pylint for comprehensive analysis
echo "Running pylint for comprehensive analysis..."
run_command "python -m pylint *.py calculator/ tests/"

# =============================================================================
# 4. JAVA TESTING COMMANDS
# =============================================================================

echo "☕ 4. JAVA TESTING COMMANDS"
echo "=========================="

# Check if Java is installed
echo "Checking Java installation..."
run_command "java -version"

# Compile Java files
echo "Compiling Java files..."
run_command "javac CodeUtils.java"

# Run Java program
echo "Running Java program..."
run_command "java CodeUtils"

# =============================================================================
# 5. PROJECT STRUCTURE VALIDATION
# =============================================================================

echo "📁 5. PROJECT STRUCTURE VALIDATION"
echo "================================="

# Check if all required files exist
echo "Checking project structure..."
run_command "ls -la"

# Check if requirements.txt is valid
echo "Checking requirements.txt..."
run_command "pip check -r requirements.txt"

# Check if pyproject.toml is valid
echo "Checking pyproject.toml..."
run_command "python -c \"import tomllib; tomllib.load(open('pyproject.toml', 'rb'))\""

# =============================================================================
# 6. COVERAGE AND QUALITY REPORTS
# =============================================================================

echo "📊 6. COVERAGE AND QUALITY REPORTS"
echo "=================================="

# Generate coverage report
echo "Generating coverage report..."
run_command "python -m pytest tests/ --cov=calculator --cov-report=html --cov-report=term-missing"

# Open coverage report in browser (macOS)
echo "Opening coverage report in browser..."
run_command "open htmlcov/index.html"

# =============================================================================
# 7. QUICK VALIDATION COMMANDS
# =============================================================================

echo "⚡ 7. QUICK VALIDATION COMMANDS"
echo "==============================="

# Quick syntax check
echo "Quick syntax check for all Python files..."
run_command "python -c \"import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('*.py')]\""

# Quick import test
echo "Quick import test..."
run_command "python -c \"import calculator; print('✅ Calculator module imports successfully')\""

# Quick function test
echo "Quick function test..."
run_command "python -c \"from calculator.calculator import Calculator; calc = Calculator(); print('✅ Calculator class works')\""

# =============================================================================
# 8. CLEANUP COMMANDS
# =============================================================================

echo "🧹 8. CLEANUP COMMANDS"
echo "======================"

# Clean Python cache
echo "Cleaning Python cache..."
run_command "find . -type d -name '__pycache__' -exec rm -rf {} +"
run_command "find . -name '*.pyc' -delete"

# Clean test cache
echo "Cleaning test cache..."
run_command "rm -rf .pytest_cache"

# Clean coverage reports
echo "Cleaning coverage reports..."
run_command "rm -rf htmlcov"

# =============================================================================
# 9. USEFUL ALIASES (add to your .bashrc or .zshrc)
# =============================================================================

echo "🔧 9. USEFUL ALIASES"
echo "===================="
echo ""
echo "Add these to your ~/.bashrc or ~/.zshrc:"
echo ""
echo "# Testing aliases"
echo "alias test-all='cd $GENERATED_CODE_DIR && python -m pytest tests/ -v'"
echo "alias test-cov='cd $GENERATED_CODE_DIR && python -m pytest tests/ --cov=calculator --cov-report=html'"
echo "alias validate-full='cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/'"
echo "alias validate-syntax='cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps syntax --output-dir output/PythonExample/environment/'"
echo "alias validate-tests='cd $PROJECT_ROOT && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps test --output-dir output/PythonExample/environment/'"
echo ""

# =============================================================================
# 10. COMMAND REFERENCE
# =============================================================================

echo "📚 10. COMMAND REFERENCE"
echo "========================"
echo ""
echo "Quick Reference:"
echo "• Full 3-layer validation: validate-full"
echo "• Syntax validation only: validate-syntax"
echo "• Test validation only: validate-tests"
echo "• Run all Python tests: test-all"
echo "• Run tests with coverage: test-cov"
echo "• Clean up: find . -type d -name '__pycache__' -exec rm -rf {} +"
echo ""

echo "✅ Testing commands file created successfully!"
echo "Run individual commands or execute the entire file with: bash test_commands.sh" 