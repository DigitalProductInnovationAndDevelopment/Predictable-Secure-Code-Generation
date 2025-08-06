# 🚀 HandleGeneric Quick Testing Commands

## **Package Testing**

```bash
# Navigate to HandleGeneric directory
cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric

# Run all tests using built-in runner
python run_tests.py --type all --verbose

# Run specific test types
python run_tests.py --type unit --verbose
python run_tests.py --type integration --verbose
python run_tests.py --type providers --verbose
python run_tests.py --type core --verbose
python run_tests.py --type utils --verbose

# Run with coverage
python run_tests.py --type all --verbose

# Run without coverage
python run_tests.py --type all --no-coverage --verbose
```

## **Direct Pytest Commands**

```bash
# Run pytest directly
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=HandleGeneric --cov-report=html --cov-report=term-missing

# Run specific test directories
python -m pytest tests/test_core/ -v
python -m pytest tests/test_providers/ -v
python -m pytest tests/test_utils/ -v
python -m pytest tests/test_integration/ -v

# Run with markers
python -m pytest tests/ -m unit -v
python -m pytest tests/ -m integration -v
python -m pytest tests/ -m providers -v
python -m pytest tests/ -m core -v
python -m pytest tests/ -m utils -v
```

## **CLI Testing**

```bash
# Test CLI help
cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation
PYTHONPATH=src python -m HandleGeneric.cli.main --help

# Test metadata generation
PYTHONPATH=src python -m HandleGeneric.cli.main generate-metadata ../output/PythonExample/generated_code --output ../output/PythonExample/environment/metadata_new.json

# Test validation
PYTHONPATH=src python -m HandleGeneric.cli.main validate ../output/PythonExample/generated_code --metadata ../output/PythonExample/environment/metadata.json --output ../output/PythonExample/environment/validation_report.json

# Test code generation
PYTHONPATH=src python -m HandleGeneric.cli.main generate-code ../output/PythonExample/generated_code --metadata ../output/PythonExample/environment/metadata.json --output ../output/PythonExample/environment/generated_code_new
```

## **3-Layer Validation Testing**

```bash
# Full 3-layer validation
cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps all --output-dir ../output/PythonExample/environment/

# Syntax validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps syntax --output-dir ../output/PythonExample/environment/

# Test validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps test --output-dir ../output/PythonExample/environment/

# AI validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps ai --output-dir ../output/PythonExample/environment/
```

## **Package Installation Testing**

```bash
# Install package in development mode
cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric
pip install -e .

# Test package import
python -c "import HandleGeneric; print('✅ HandleGeneric package imports successfully')"

# Test specific module imports
python -c "from HandleGeneric.core.base.generator import GenericMetadataGenerator; print('✅ Generator imports successfully')"
python -c "from HandleGeneric.core.base.validator import GenericValidator; print('✅ Validator imports successfully')"
python -c "from HandleGeneric.core.base.code_generator import GenericCodeGenerator; print('✅ Code generator imports successfully')"
```

## **Provider Testing**

```bash
# Test provider imports
python -c "from HandleGeneric.providers.python import PythonProvider; print('✅ Python provider imports successfully')"
python -c "from HandleGeneric.providers.javascript import JavaScriptProvider; print('✅ JavaScript provider imports successfully')"
python -c "from HandleGeneric.providers.java import JavaProvider; print('✅ Java provider imports successfully')"

# Test provider initialization
python -c "from HandleGeneric.core.initialization import ensure_initialized; ensure_initialized(); print('✅ Providers initialized successfully')"
```

## **Quick Aliases (add to ~/.bashrc or ~/.zshrc)**

```bash
# HandleGeneric testing aliases
alias hg-test='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric && python run_tests.py --type all --verbose'
alias hg-test-unit='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric && python run_tests.py --type unit --verbose'
alias hg-test-integration='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric && python run_tests.py --type integration --verbose'
alias hg-validate='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps all --output-dir ../output/PythonExample/environment/'
alias hg-validate-syntax='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps syntax --output-dir ../output/PythonExample/environment/'
alias hg-validate-tests='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main ../output/PythonExample/generated_code ../output/PythonExample/environment/metadata.json --steps test --output-dir ../output/PythonExample/environment/'
alias hg-clean='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric && find . -type d -name "__pycache__" -exec rm -rf {} + && find . -name "*.pyc" -delete && rm -rf .pytest_cache htmlcov'
```

## **Most Common Commands**

1. **Run all tests**: `hg-test`
2. **Run unit tests**: `hg-test-unit`
3. **Run integration tests**: `hg-test-integration`
4. **Full validation**: `hg-validate`
5. **Syntax validation**: `hg-validate-syntax`
6. **Test validation**: `hg-validate-tests`
7. **Clean up**: `hg-clean`

## **File Locations**

- **HandleGeneric Package**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric`
- **Test Commands**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric/test_commands.sh`
- **Quick Reference**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric/quick_test_commands.md`
- **Built-in Test Runner**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/src/HandleGeneric/run_tests.py`
