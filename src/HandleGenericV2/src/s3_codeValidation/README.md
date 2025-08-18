# S3 Code Validation

AI-powered code validation and quality monitoring system that validates code against requirements, monitors for problems, and tracks validation results.

## Features

- **🤖 AI-Powered Validation**: Uses Azure OpenAI to analyze code quality and compliance
- **📋 Requirements Coverage**: Validates code against specified requirements
- **🚨 Issue Detection**: Identifies high, medium, and low priority issues
- **📊 Quality Metrics**: Provides comprehensive scoring and recommendations
- **📁 Multi-Language Support**: Works with Python, JavaScript, Java, C++, and more
- **🔄 Continuous Monitoring**: Tracks validation history and trends
- **💡 Smart Recommendations**: AI-generated suggestions for improvement

## Usage

### Command Line Interface

```bash
# Validate all code files
python -m s3_codeValidation.main --validate

# Show current validation status
python -m s3_codeValidation.main --status

# Show comprehensive validation summary
python -m s3_codeValidation.main --summary

# Reset validation log
python -m s3_codeValidation.main --reset

# Test AI client connection
python -m s3_codeValidation.main --test-ai

# Default mode: validate and show summary
python -m s3_codeValidation.main
```

### Programmatic Usage

```python
from s3_codeValidation import CodeValidator
from config import Config

# Initialize validator
config = Config()
validator = CodeValidator(config)

# Validate all code
result = validator.validate_all_code()

# Get validation status
status = validator.get_validation_status()

# Get detailed summary
summary = validator.get_validation_summary()
```

## Configuration

The system uses the following configuration from `config.py`:

- `OUTPUT_CODE`: Directory containing code to validate
- `REQUIREMENTS`: Path to requirements CSV file
- `METADATA`: Path to metadata JSON file
- `WORKSPACE`: Workspace type (LOCAL/CLOUD)
- Azure OpenAI configuration for AI validation

## Validation Process

1. **Code Discovery**: Automatically finds all code files in the output directory
2. **Requirements Analysis**: Loads and analyzes requirements from CSV
3. **AI Validation**: Uses AI to validate each code file against requirements
4. **Issue Classification**: Categorizes issues by severity and type
5. **Coverage Analysis**: Determines requirements implementation coverage
6. **Quality Assessment**: Evaluates code quality across multiple dimensions
7. **Recommendations**: Generates actionable improvement suggestions

## Output

The system provides:

- **Validation Results**: Pass/Fail status for each file
- **Quality Scores**: 0-100 scoring for overall code quality
- **Issue Breakdown**: Categorized by severity and type
- **Requirements Coverage**: Percentage of requirements implemented
- **Recommendations**: Specific suggestions for improvement
- **Validation History**: Track of all validation runs

## Supported Languages

- Python (.py)
- JavaScript (.js, .ts)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- PHP (.php)
- Ruby (.rb)
- Go (.go)
- Rust (.rs)
- And many more...

## Requirements

- Python 3.8+
- Azure OpenAI API access
- Required packages: openai, logging, pathlib
- Configuration file with API credentials
