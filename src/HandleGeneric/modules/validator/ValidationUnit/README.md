# ValidationUnit - Comprehensive Codebase Validation System

A structured 3-stage validation system for Python codebases that validates syntax, tests, and logic using AI analysis.

## Overview

The ValidationUnit system provides comprehensive validation through three key stages:

1. **Syntax Validation** - Validates Python syntax, imports, and code structure
2. **Test Validation** - Runs test suites and analyzes test coverage
3. **AI Logic Validation** - Uses AI to analyze code logic and requirement fulfillment

## Features

### 🔍 Comprehensive Analysis

- **Syntax checking** with detailed error reporting
- **Test execution** with pytest/unittest support
- **AI-powered logic analysis** using Azure OpenAI
- **Dynamic configuration** with JSON/YAML support
- **Multiple output formats** (JSON, YAML, text)

### 📊 Detailed Reporting

- Structured problem identification with file locations and line numbers
- Severity levels (error, warning, info)
- Execution time tracking
- Comprehensive metadata collection

### 🚀 Easy Integration

- CLI interface for standalone use
- Programmatic API for integration
- No external dependencies for core functionality
- Graceful degradation when optional tools unavailable

## Installation

The validation system is designed to work with Python standard library only. No installation of external packages is required for basic functionality.

For enhanced features, you can optionally install:

```bash
# For YAML configuration support
pip install PyYAML>=6.0

# For test coverage analysis
pip install coverage>=7.0

# For enhanced test running
pip install pytest>=7.0
```

## Quick Start

### Basic Usage

```bash
# Validate a codebase using metadata
python -m src.ValidtaionUnit.main input/code output/enviroment/metadata.json

# Save report to specific directory
python -m src.ValidtaionUnit.main input/code metadata.json --output-dir validation_results

# Run only specific validation steps
python -m src.ValidtaionUnit.main input/code metadata.json --steps syntax test

# Verbose output
python -m src.ValidtaionUnit.main input/code metadata.json --verbose
```

### Programmatic Usage

```python
from src.ValidtaionUnit import CodebaseValidator, ValidationConfig

# Create validator with default config
validator = CodebaseValidator()

# Run validation
result = validator.validate_codebase(
    codebase_path="input/code",
    metadata_path="output/enviroment/metadata.json",
    output_path="validation_results"
)

# Check results
if result.is_valid:
    print("✅ Validation passed!")
else:
    print(f"❌ Validation failed with {result.total_error_count()} errors")
    for problem in result.get_all_problems():
        print(f"  - {problem.message}")
```

## Command Line Interface

### Required Arguments

- `codebase_path` - Path to the codebase directory to validate
- `metadata_path` - Path to the metadata.json file

### Optional Arguments

| Flag                    | Description                                     | Default           |
| ----------------------- | ----------------------------------------------- | ----------------- |
| `--output-dir`, `-o`    | Directory to save validation report             | current directory |
| `--config`, `-c`        | Path to validation configuration file           | default config    |
| `--steps`               | Validation steps to run (syntax, test, ai, all) | all               |
| `--output-format`, `-f` | Output format (json, yaml, text)                | json              |
| `--stop-on-failure`     | Stop validation on first failure                | false             |
| `--no-ai`               | Disable AI validation                           | false             |
| `--test-timeout`        | Test execution timeout in seconds               | 300               |
| `--verbose`, `-v`       | Enable verbose output                           | false             |
| `--quiet`, `-q`         | Suppress output except errors                   | false             |
| `--no-report`           | Don't save validation report to file            | false             |

### Examples

```bash
# Basic validation
python -m src.ValidtaionUnit.main input/code output/enviroment/metadata.json

# Custom output directory and format
python -m src.ValidtaionUnit.main input/code metadata.json \
    --output-dir results --output-format yaml

# Only syntax and test validation (skip AI)
python -m src.ValidtaionUnit.main input/code metadata.json \
    --steps syntax test

# Stop on first failure with verbose output
python -m src.ValidtaionUnit.main input/code metadata.json \
    --stop-on-failure --verbose

# Use custom configuration
python -m src.ValidtaionUnit.main input/code metadata.json \
    --config custom_validation.json
```

## Configuration

### Default Configuration

The system works out-of-the-box with sensible defaults. You can customize behavior using a configuration file:

```json
{
  "enable_syntax_validation": true,
  "enable_test_validation": true,
  "enable_ai_validation": true,
  "stop_on_first_failure": false,

  "syntax_check_imports": true,
  "syntax_check_indentation": true,
  "syntax_python_version": "3.7",

  "test_timeout": 300,
  "test_patterns": ["test_*.py", "*_test.py", "tests.py"],
  "test_directories": ["tests", "test"],
  "required_test_coverage": 0.0,
  "pytest_args": ["-v", "--tb=short"],

  "ai_max_tokens": 2000,
  "ai_temperature": 0.1,

  "output_format": "json",
  "save_report": true,
  "report_filename": "validation_report.json",

  "log_level": "INFO",
  "verbose_output": false
}
```

### Configuration Options

#### General Settings

- `enable_syntax_validation` - Enable/disable syntax validation
- `enable_test_validation` - Enable/disable test validation
- `enable_ai_validation` - Enable/disable AI validation
- `stop_on_first_failure` - Stop on first validation failure

#### Syntax Validation

- `syntax_check_imports` - Validate import statements
- `syntax_check_indentation` - Check indentation consistency
- `syntax_python_version` - Target Python version

#### Test Validation

- `test_timeout` - Test execution timeout (seconds)
- `test_patterns` - File patterns for test discovery
- `test_directories` - Directories to search for tests
- `required_test_coverage` - Minimum test coverage percentage
- `pytest_args` - Arguments passed to pytest

#### AI Validation

- `ai_max_tokens` - Maximum tokens for AI analysis
- `ai_temperature` - AI response temperature

#### Output Settings

- `output_format` - Report format (json, yaml, text)
- `save_report` - Save report to file
- `report_filename` - Report filename

## Validation Steps

### 1. Syntax Validation

Validates Python code syntax and structure:

- **AST parsing** - Checks for syntax errors
- **Import validation** - Validates import statements and relative imports
- **Indentation consistency** - Checks for mixed tabs/spaces
- **Encoding validation** - Validates file encoding

**Output**: Reports syntax errors with exact line numbers and suggestions.

### 2. Test Validation

Runs and analyzes test suites:

- **Test discovery** - Finds test files using configurable patterns
- **Test execution** - Runs tests with pytest or unittest
- **Coverage analysis** - Analyzes test coverage if available
- **Test structure validation** - Validates test file structure

**Output**: Reports test failures, coverage metrics, and test structure issues.

### 3. AI Logic Validation

AI-powered analysis of code logic:

- **Requirement fulfillment** - Checks if code fulfills stated requirements
- **Logic correctness** - Analyzes algorithms for logical errors
- **Edge case handling** - Identifies missing edge case handling
- **Security analysis** - Basic security vulnerability detection
- **Code quality** - Suggests improvements and best practices

**Output**: AI-generated insights, problems, and improvement suggestions.

## Output Format

### JSON Report Structure

```json
{
  "codebase_path": "input/code",
  "metadata_path": "output/enviroment/metadata.json",
  "overall_status": "valid",
  "is_valid": true,
  "total_execution_time": 2.45,
  "timestamp": "2024-01-01T12:00:00",
  "total_error_count": 0,
  "total_warning_count": 2,
  "step_results": [
    {
      "step_name": "Syntax Validation",
      "status": "valid",
      "is_valid": true,
      "execution_time": 0.15,
      "error_count": 0,
      "warning_count": 1,
      "problems": [
        {
          "severity": "warning",
          "message": "Mixed tabs and spaces in indentation",
          "file_path": "src/example.py",
          "line_number": 15,
          "error_code": "MIXED_INDENTATION"
        }
      ],
      "metadata": {
        "files_checked": 6,
        "syntax_errors": 0
      }
    }
  ]
}
```

### Problem Structure

Each validation problem includes:

- `severity` - "error", "warning", or "info"
- `message` - Human-readable problem description
- `file_path` - File where problem occurred (optional)
- `line_number` - Line number (optional)
- `column` - Column number (optional)
- `error_code` - Machine-readable error code (optional)
- `suggestion` - Suggested fix (optional)

## Integration with Existing AI System

The validation system integrates with your existing AI infrastructure:

```python
# Automatically detects and uses existing AI client
from src.AI.ai import ai_client

# Falls back gracefully if AI not available
if not ai_client:
    print("AI validation will be skipped")
```

## Error Handling

The system provides robust error handling:

- **Graceful degradation** - Continues validation even if one step fails
- **Detailed error reporting** - Exact error locations and descriptions
- **Timeout handling** - Prevents hanging on long-running tests
- **Resource cleanup** - Properly cleans up temporary files

## Best Practices

### For Projects

1. Include validation in your CI/CD pipeline
2. Set appropriate test coverage requirements
3. Use custom configuration for project-specific needs
4. Review AI suggestions regularly

### For Validation

1. Run validation before commits
2. Address syntax errors first
3. Ensure tests pass before logic validation
4. Use verbose mode for debugging

## Troubleshooting

### Common Issues

**AI client not available**

- Ensure AI credentials are configured
- Check network connectivity
- Verify AI service availability

**Tests not found**

- Check test file patterns in configuration
- Verify test directory structure
- Ensure test files follow naming conventions

**Permission errors**

- Check file/directory permissions
- Ensure write access for report output
- Verify Python execution permissions

**Memory issues**

- Reduce AI max tokens
- Increase test timeout
- Use smaller codebases for testing

### Debug Mode

Use verbose output for detailed debugging:

```bash
python -m src.ValidtaionUnit.main input/code metadata.json --verbose
```

## Contributing

The validation system is designed to be extensible:

1. Add new validation steps in `core/`
2. Extend configuration options in `utils/config.py`
3. Add new output formats in `utils/helpers.py`
4. Enhance AI prompts in configuration

## License

This validation system is part of the Predictable Secure Code Generation project.
