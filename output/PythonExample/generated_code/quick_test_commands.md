# 🚀 Quick Testing Commands

## **HandleGeneric 3-Layer Validation**

```bash
# Full 3-layer validation (syntax + test + AI)
cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/

# Syntax validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps syntax --output-dir output/PythonExample/environment/

# Test validation only
PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps test --output-dir output/PythonExample/environment/
```

## **Python Testing**

```bash
# Navigate to generated code directory
cd output/PythonExample/generated_code

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=calculator --cov-report=html

# Run specific test file
python -m pytest test_req001.py -v

# Quick syntax check
python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('*.py')]"
```

## **Java Testing**

```bash
# Compile Java files
javac CodeUtils.java

# Run Java program
java CodeUtils
```

## **Quick Aliases (add to ~/.bashrc or ~/.zshrc)**

```bash
# Testing aliases
alias test-all='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/generated_code && python -m pytest tests/ -v'
alias test-cov='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/generated_code && python -m pytest tests/ --cov=calculator --cov-report=html'
alias validate-full='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps all --output-dir output/PythonExample/environment/'
alias validate-syntax='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps syntax --output-dir output/PythonExample/environment/'
alias validate-tests='cd /Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation && PYTHONPATH=src python -m HandleGeneric.modules.validator.ValidationUnit.main output/PythonExample/generated_code output/PythonExample/environment/metadata.json --steps test --output-dir output/PythonExample/environment/'
```

## **Most Common Commands**

1. **Full validation**: `validate-full`
2. **Run Python tests**: `test-all`
3. **Check syntax**: `validate-syntax`
4. **Run tests with coverage**: `test-cov`

## **File Locations**

- **Generated Code**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/generated_code`
- **Environment**: `/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/environment`
- **Validation Report**: `output/PythonExample/environment/validation_report.json`
