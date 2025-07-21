# GenerateCodeFromRequirements

An AI-powered code generation system that automatically generates Python code from requirements, with intelligent analysis, integration, and validation capabilities.

## 🌟 Features

- **Intelligent Requirement Analysis**: Analyzes requirements against existing codebase metadata
- **AI-Powered Code Generation**: Uses Azure OpenAI to generate high-quality Python code
- **Smart Code Integration**: Intelligently integrates generated code into existing projects
- **Automatic Test Generation**: Creates comprehensive test cases for generated functionality
- **Metadata Synchronization**: Updates project metadata after code generation
- **Validation Pipeline**: Validates generated code using integrated validation systems
- **Multiple Output Formats**: Supports JSON, YAML, and text output formats
- **Configurable Workflow**: Highly customizable generation process

## 🏗️ Architecture

```
GenerateCodeFromRequirements/
├── core/                    # Core generation components
│   ├── generator.py         # Main orchestrator
│   ├── analyzer.py          # Requirement analysis
│   └── integrator.py        # Code integration
├── models/                  # Data models
│   ├── generation_result.py # Result tracking
│   ├── requirement_data.py  # Requirement modeling
│   └── code_change.py       # Change management
├── utils/                   # Utility components
│   ├── config.py           # Configuration management
│   └── helpers.py          # Helper utilities
├── main.py                 # CLI interface
├── config_example.json     # Example configuration
└── README.md              # This file
```

## 🚀 Quick Start

### Installation

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Validate Installation**

```bash
python main.py validate
```

3. **Create Configuration**

```bash
python main.py create-config
```

### Basic Usage

```bash
# Generate code from requirements
python main.py \
  --project-path /path/to/source/project \
  --requirements requirements.csv \
  --metadata metadata.json \
  --output /path/to/output
```

### Using with Calculator Example

```bash
# Using the provided calculator project
python main.py \
  --project-path ../../input/code \
  --requirements ../../input/environment/requirements.csv \
  --metadata ../../output/environment/metadata.json \
  --output ../../output/code \
  --verbose
```

## 📋 Requirements Format

Requirements should be provided in CSV format with columns `id` and `description`:

```csv
id,description
REQ001,Add function to calculate square root of a number
REQ002,Implement input validation for all calculator functions
REQ003,Create CLI interface with menu options
REQ004,Add logging functionality for all operations
```

## 🔧 Configuration

The system uses a JSON configuration file for customization:

```json
{
  "use_ai": true,
  "ai_max_tokens": 2000,
  "ai_temperature": 0.3,
  "include_docstrings": true,
  "include_type_hints": true,
  "generate_tests": true,
  "test_coverage_threshold": 0.8,
  "validate_syntax": true,
  "output_format": "json"
}
```

### Configuration Options

| Option               | Description                    | Default |
| -------------------- | ------------------------------ | ------- |
| `use_ai`             | Enable AI-powered generation   | `true`  |
| `ai_max_tokens`      | Maximum tokens per AI request  | `2000`  |
| `ai_temperature`     | AI creativity level (0.0-2.0)  | `0.3`   |
| `include_docstrings` | Generate docstrings            | `true`  |
| `include_type_hints` | Add type hints                 | `true`  |
| `generate_tests`     | Create test cases              | `true`  |
| `validate_syntax`    | Validate generated code        | `true`  |
| `output_format`      | Result format (json/yaml/text) | `json`  |

## 🎯 Workflow

The system follows a comprehensive workflow:

1. **Requirement Analysis**

   - Load and compare requirements
   - Analyze against existing metadata
   - Determine implementation strategy

2. **Code Generation**

   - Use AI to generate code for each requirement
   - Create appropriate code changes
   - Handle imports and dependencies

3. **Code Integration**

   - Copy source project to output
   - Apply generated code changes
   - Merge with existing codebase

4. **Test Generation**

   - Generate comprehensive test cases
   - Include edge cases and error testing
   - Create pytest-compatible tests

5. **Metadata & Validation**
   - Update project metadata
   - Run validation pipeline
   - Generate final reports

## 📊 Integration with Other Systems

### CheckCodeRequirements

Identifies which requirements need implementation:

```bash
cd ../CheckCodeRequirements
python checkNewRequirements.py
```

### GenerateMetadataFromCode

Updates metadata after code generation:

```bash
cd ../GenerateMetadataFromCode
python main.py --project-path ../../output/code --output-path ../../output/environment
```

### ValidationUnit

Validates the generated code:

```bash
cd ../ValidationUnit
python main.py --project-path ../../output/code
```

### AIBrain

Provides AI-powered code generation capabilities through Azure OpenAI integration.

## 📈 Output and Results

### Generation Result

The system provides comprehensive results including:

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "requirements_analyzed": 5,
  "requirements_implemented": 4,
  "requirements_failed": 1,
  "files_created": ["new_feature.py"],
  "files_modified": ["main.py", "calculator.py"],
  "tests_generated": ["test_new_feature.py"],
  "problems": [],
  "metadata_updated": true,
  "validation_passed": true,
  "execution_time": 45.2,
  "ai_tokens_used": 3450
}
```

### Problem Tracking

Issues are tracked with detailed information:

- Severity levels (error, warning, info)
- Categories (requirement, integration, testing, validation)
- File locations and line numbers
- Requirement associations

## 🛠️ Command Line Interface

### Required Arguments

- `--project-path`: Source project directory
- `--requirements`: Requirements CSV file
- `--metadata`: Project metadata JSON file
- `--output`: Output directory for generated code

### Optional Arguments

- `--existing-requirements`: Existing requirements for comparison
- `--config`: Custom configuration file
- `--format`: Output format (json/yaml/text)
- `--verbose`: Enable detailed logging
- `--dry-run`: Analyze without generating code
- `--no-tests`: Skip test generation
- `--no-validation`: Skip validation step

### Examples

```bash
# Basic generation
python main.py -p ./project -r reqs.csv -m meta.json -o ./output

# With comparison and custom config
python main.py \
  --project-path ./project \
  --requirements new_reqs.csv \
  --existing-requirements old_reqs.csv \
  --metadata meta.json \
  --output ./output \
  --config custom.json \
  --verbose

# Dry run analysis
python main.py -p ./project -r reqs.csv -m meta.json -o ./output --dry-run

# Skip specific steps
python main.py -p ./project -r reqs.csv -m meta.json -o ./output --no-tests --no-validation
```

## 🧪 Testing the System

### Test with Calculator Project

1. **Setup the calculator project** (should already be in `../../input/code`)

2. **Create test requirements**:

```csv
id,description
REQ001,Add function to calculate factorial of a number
REQ002,Implement power function (x^y)
REQ003,Add function to calculate percentage
REQ004,Create memory storage functions (store/recall/clear)
```

3. **Run generation**:

```bash
python main.py \
  --project-path ../../input/code \
  --requirements test_requirements.csv \
  --metadata ../../output/environment/metadata.json \
  --output ../../output/generated_code \
  --verbose
```

4. **Verify results**:

- Check generated code in output directory
- Review test cases
- Examine generation report

## 🔍 Troubleshooting

### Common Issues

1. **AI Client Not Available**

   ```
   Warning: AI client initialization failed
   ```

   - Check Azure OpenAI configuration in config.py
   - Verify API keys and endpoints

2. **Import Errors**

   ```
   ModuleNotFoundError: No module named 'CheckCodeRequirements'
   ```

   - Ensure proper Python path setup
   - Check relative imports in generator.py

3. **Syntax Validation Failures**

   ```
   Generated code has syntax errors
   ```

   - Review AI temperature settings
   - Check generated code manually
   - Enable verbose logging for debugging

4. **File Permission Errors**
   ```
   Failed to prepare output directory
   ```
   - Check write permissions for output directory
   - Ensure source directory is readable

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
python main.py ... --verbose
```

### Configuration Validation

Test your configuration:

```python
from utils.config import GenerationConfig
config = GenerationConfig.load_from_file('config.json')
errors = config.validate()
if errors:
    print("Configuration errors:", errors)
```

## 🎨 Customization

### Custom AI Prompts

Modify the system prompts in `core/generator.py`:

```python
def _get_code_generation_prompt(self) -> str:
    return """Your custom prompt here..."""
```

### Custom Code Analysis

Extend the analyzer in `core/analyzer.py`:

```python
def _extract_keywords(self, description: str) -> List[str]:
    # Add custom keyword extraction logic
    pass
```

### Custom Integration Strategies

Modify integration behavior in `core/integrator.py`:

```python
def _apply_single_change(self, change: CodeChange, ...):
    # Add custom integration logic
    pass
```

## 📚 API Reference

### CodeGenerator

Main orchestrator class:

```python
from core.generator import CodeGenerator

generator = CodeGenerator()
result = generator.generate_from_requirements(
    project_path="./project",
    requirements_path="./reqs.csv",
    metadata_path="./meta.json",
    output_path="./output"
)
```

### RequirementAnalyzer

Analyzes requirements against metadata:

```python
from core.analyzer import RequirementAnalyzer

analyzer = RequirementAnalyzer()
requirement_objects = analyzer.analyze_requirements(
    requirements={"REQ001": "Add new function"},
    metadata=metadata_dict,
    result=generation_result
)
```

### CodeIntegrator

Applies code changes to projects:

```python
from core.integrator import CodeIntegrator

integrator = CodeIntegrator()
success = integrator.apply_code_changes(
    changes=code_changes_list,
    output_path="./output",
    result=generation_result
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the command reference
3. Enable verbose logging for debugging
4. Create an issue with detailed error information

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - AI-powered code generation
  - Requirement analysis and integration
  - Test generation and validation
  - Multiple output formats
  - Comprehensive CLI interface
