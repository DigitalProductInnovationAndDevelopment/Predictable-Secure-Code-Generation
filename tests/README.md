# Test Suite for Automated Code Generation System

This directory contains comprehensive Python test cases for the automated code generation and updating system.

## Test Structure

```
tests/
├── test_config.py              # Configuration module tests
├── test_function_app.py         # Azure Function app tests
├── test_requirements_checker.py # Requirements processing tests
├── test_code_analyzer.py        # Code analysis tests
├── test_ai_code_editor.py       # AI code generation tests
├── test_code_validator.py       # Code validation tests
├── test_metadata_manager.py     # Metadata management tests (if created)
├── requirements.txt             # Test dependencies
├── pytest.ini                  # Pytest configuration
├── run_tests.py                 # Test runner script
└── README.md                    # This file
```

## Test Coverage

### 1. **Config Tests** (`test_config.py`)

- Configuration initialization and validation
- Environment variable handling
- Default value verification
- Directory creation logic
- Type conversion testing

### 2. **Function App Tests** (`test_function_app.py`)

- Azure Function trigger testing
- HTTP endpoint validation
- Error handling and retry logic
- Status monitoring
- Integration workflows

### 3. **Requirements Checker Tests** (`test_requirements_checker.py`)

- CSV/Excel file processing
- Hash-based change detection
- Requirement filtering and validation
- File format handling
- Error scenarios

### 4. **Code Analyzer Tests** (`test_code_analyzer.py`)

- Python AST parsing
- File structure analysis
- Requirement mapping logic
- Dependency detection
- Cross-language support

### 5. **AI Code Editor Tests** (`test_ai_code_editor.py`)

- OpenAI API integration
- Code generation and parsing
- File creation and modification
- Backup management
- Error handling

### 6. **Code Validator Tests** (`test_code_validator.py`)

- Syntax validation
- Linting with flake8
- Code formatting with black
- Test execution with pytest
- Multi-step validation pipeline

## Prerequisites

### Required Dependencies

Install test dependencies:

```bash
pip install -r tests/requirements.txt
```

### System Requirements

- Python 3.8+
- pytest 7.0+
- All project dependencies from main `requirements.txt`

## Running Tests

### Option 1: Use the Test Runner Script

```bash
python tests/run_tests.py
```

This script will:

- Run all tests with verbose output
- Generate coverage reports
- Run specific module tests
- Provide detailed logging

### Option 2: Direct Pytest Commands

**Run all tests:**

```bash
pytest tests/ -v
```

**Run with coverage:**

```bash
pytest tests/ --cov=CodeFromRequirements --cov=function_app --cov=config --cov-report=term-missing
```

**Run specific test files:**

```bash
pytest tests/test_config.py -v
pytest tests/test_function_app.py -v
```

**Run with HTML coverage report:**

```bash
pytest tests/ --cov=CodeFromRequirements --cov=function_app --cov=config --cov-report=html
```

### Option 3: Run Specific Test Categories

```bash
# Run unit tests only
pytest tests/ -m unit

# Run integration tests only
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- Test discovery patterns
- Coverage settings
- Output formatting
- Custom markers for test categorization

### Mock Strategy

Tests use extensive mocking to:

- Isolate units under test
- Avoid external API calls
- Control test environment
- Ensure reproducible results

### Key Mock Patterns:

- **Config mocking**: Override configuration values
- **File system mocking**: Test file operations safely
- **API mocking**: Mock OpenAI and Azure services
- **Subprocess mocking**: Mock external tool calls

## Test Data and Fixtures

### Temporary Directories

Tests create isolated temporary directories for:

- File system operations
- Configuration testing
- Metadata storage simulation

### Sample Data

Each test class includes realistic sample data:

- Requirements with various statuses and categories
- Valid and invalid Python code samples
- API response simulations
- Configuration scenarios

## Coverage Goals

Target coverage levels:

- **Overall**: >90%
- **Core modules**: >95%
- **Critical paths**: 100%

### Current Coverage Areas:

- ✅ Configuration management
- ✅ Requirement processing
- ✅ Code analysis and generation
- ✅ Validation pipeline
- ✅ Error handling scenarios
- ✅ Edge cases and boundary conditions

## Common Test Patterns

### 1. Setup and Teardown

```python
def setup_method(self):
    """Setup test fixtures"""
    self.temp_dir = tempfile.mkdtemp()

def teardown_method(self):
    """Cleanup test fixtures"""
    shutil.rmtree(self.temp_dir, ignore_errors=True)
```

### 2. Configuration Mocking

```python
@patch('module.Config')
def test_function(self, mock_config):
    mock_config.return_value.SETTING = "test_value"
    # Test logic here
```

### 3. File System Testing

```python
def test_file_operations(self):
    test_file = os.path.join(self.temp_dir, "test.py")
    with open(test_file, 'w') as f:
        f.write(sample_code)
    # Test file operations
```

## Continuous Integration

### Pre-commit Hooks

Consider adding these pre-commit hooks:

```bash
# Run tests before commit
python tests/run_tests.py

# Check code quality
flake8 tests/
black tests/
```

### CI Pipeline Integration

Tests are designed to work with CI/CD pipelines:

- Exit codes indicate success/failure
- Coverage reports in multiple formats
- Detailed logging for debugging
- Parallel test execution support

## Troubleshooting

### Common Issues:

1. **Import Errors**

   ```bash
   # Add project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Permission Errors**

   ```bash
   # Ensure test runner has execute permissions
   chmod +x tests/run_tests.py
   ```

3. **Missing Dependencies**

   ```bash
   # Install all test requirements
   pip install -r tests/requirements.txt
   pip install -r requirements.txt
   ```

4. **Coverage Issues**
   ```bash
   # Clear coverage cache
   rm -rf .coverage htmlcov/
   ```

## Adding New Tests

### Guidelines for New Tests:

1. **Naming**: Follow `test_*.py` pattern
2. **Structure**: Use class-based organization
3. **Isolation**: Each test should be independent
4. **Documentation**: Include clear docstrings
5. **Assertions**: Use descriptive assertion messages
6. **Coverage**: Aim for comprehensive coverage

### Test Template:

```python
import pytest
from unittest.mock import patch, MagicMock
from module_to_test import ClassToTest

class TestClassToTest:
    """Test cases for ClassToTest"""

    def setup_method(self):
        """Setup test fixtures"""
        # Initialize test data

    def teardown_method(self):
        """Cleanup test fixtures"""
        # Clean up resources

    @patch('module_to_test.dependency')
    def test_specific_functionality(self, mock_dependency):
        """Test specific functionality with mocked dependencies"""
        # Setup
        # Execute
        # Assert
```

## Performance Testing

For performance-critical components, consider:

- Load testing with multiple requirements
- Memory usage monitoring
- Execution time benchmarks
- Concurrent execution testing

## Security Testing

Security-focused test scenarios:

- Input validation and sanitization
- File path traversal prevention
- API key handling
- Permission and access control

## Contributing

When contributing new tests:

1. Follow existing patterns and conventions
2. Ensure tests are deterministic and reliable
3. Add appropriate documentation
4. Update this README if adding new test categories
5. Maintain high coverage standards

## Test Execution Reports

After running tests, check:

- **Terminal output**: Immediate test results
- **htmlcov/index.html**: Detailed coverage report
- **Test logs**: Detailed execution information
- **Coverage metrics**: Line and branch coverage statistics
