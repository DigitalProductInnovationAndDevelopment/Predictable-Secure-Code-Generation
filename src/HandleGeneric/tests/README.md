# HandleGeneric Test Suite

This directory contains comprehensive tests for the HandleGeneric package, organized by functionality and type.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_core/                  # Core functionality tests
│   ├── __init__.py
│   ├── test_base_classes.py    # Base class tests
│   ├── test_language.py        # Language-related tests
│   └── test_initialization.py  # Initialization tests
├── test_providers/             # Language provider tests
│   ├── __init__.py
│   ├── test_base_provider.py   # Base provider tests
│   ├── test_python_provider.py # Python provider tests
│   ├── test_javascript_provider.py
│   ├── test_typescript_provider.py
│   ├── test_java_provider.py
│   ├── test_csharp_provider.py
│   └── test_cpp_provider.py
├── test_modules/               # Module-specific tests
│   ├── __init__.py
│   ├── test_metadata_generator/
│   ├── test_code_generator/
│   ├── test_validator/
│   └── test_requirements_checker/
├── test_utils/                 # Utility function tests
│   ├── __init__.py
│   ├── test_file_utils.py      # File utility tests
│   ├── test_config_utils.py    # Configuration utility tests
│   └── test_logging_utils.py   # Logging utility tests
├── test_integration/           # Integration tests
│   ├── __init__.py
│   ├── test_end_to_end.py      # End-to-end workflow tests
│   └── test_cli.py             # CLI tests
└── conftest.py                 # Pytest configuration and fixtures
```

## 🚀 Running Tests

### Using the Test Runner

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type providers
python run_tests.py --type core
python run_tests.py --type utils

# Run fast tests (exclude slow tests)
python run_tests.py --type fast

# Run without coverage
python run_tests.py --no-coverage

# Run in verbose mode
python run_tests.py --verbose
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_core/test_base_classes.py

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m providers

# Run tests with coverage
pytest --cov=HandleGeneric --cov-report=html

# Run tests in parallel
pytest -n auto
```

## 🏷️ Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for workflows
- `@pytest.mark.providers` - Language provider tests
- `@pytest.mark.core` - Core functionality tests
- `@pytest.mark.utils` - Utility function tests
- `@pytest.mark.slow` - Tests that take longer to run

## 📊 Test Coverage

The test suite aims for comprehensive coverage:

- **Core Components**: Base classes, language registry, file detection
- **Providers**: All language-specific implementations
- **Utilities**: File operations, configuration, logging
- **Integration**: End-to-end workflows
- **CLI**: Command-line interface functionality

### Coverage Reports

After running tests with coverage, reports are generated in:

- **Terminal**: Coverage summary with missing lines
- **HTML**: Detailed coverage report in `htmlcov/`
- **XML**: Coverage data for CI/CD integration

## 🧪 Test Types

### Unit Tests

Unit tests focus on individual components in isolation:

```python
def test_python_provider_init():
    """Test initialization of PythonProvider."""
    provider = PythonProvider()
    assert provider.language_name == 'python'
    assert '.py' in provider.file_extensions
```

### Integration Tests

Integration tests verify that components work together:

```python
def test_metadata_generation_end_to_end():
    """Test complete metadata generation workflow."""
    # Create test project
    # Generate metadata
    # Verify results
```

### Provider Tests

Provider tests verify language-specific functionality:

```python
def test_python_provider_parse_file():
    """Test Python file parsing."""
    provider = PythonProvider()
    result = provider.parse_file(mock_file)
    assert result['status'] == 'success'
```

## 🔧 Test Configuration

### pytest.ini

The test configuration is defined in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=HandleGeneric
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
```

### Test Fixtures

Common test fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def temp_project():
    """Create a temporary project for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_ai_client():
    """Create a mock AI client for testing."""
    return Mock()
```

## 📝 Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure

```python
class TestComponent:
    """Test cases for Component."""

    def test_specific_functionality(self):
        """Test specific functionality."""
        # Arrange
        component = Component()

        # Act
        result = component.method()

        # Assert
        assert result == expected_value
```

### Test Data

Use temporary files and directories for test data:

```python
def test_with_temp_files():
    """Test with temporary files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        (temp_path / "test.py").write_text("def test(): pass")

        # Run test
        result = function_under_test(temp_path)

        # Verify results
        assert result['status'] == 'success'
```

### Mocking

Use mocks for external dependencies:

```python
@patch('HandleGeneric.core.base.generator.FileDetector')
def test_with_mock(self, mock_detector):
    """Test with mocked dependencies."""
    mock_detector.return_value.detect_languages.return_value = ['python']

    result = function_under_test()

    assert result['languages'] == ['python']
```

## 🚨 Continuous Integration

### GitHub Actions

Tests are automatically run on:

- Push to main branch
- Pull requests
- Release tags

### Coverage Requirements

- Minimum coverage: 80%
- Core components: 90%
- Critical paths: 95%

## 📈 Test Metrics

### Performance Targets

- Unit tests: < 1 second each
- Integration tests: < 10 seconds each
- Full test suite: < 5 minutes

### Quality Metrics

- Test coverage: > 80%
- Test reliability: > 99%
- False positive rate: < 1%

## 🔍 Debugging Tests

### Running Individual Tests

```bash
# Run specific test
pytest tests/test_core/test_base_classes.py::TestGenericMetadataGenerator::test_init

# Run with debug output
pytest -s -v tests/test_core/test_base_classes.py

# Run with print statements
pytest -s tests/test_core/test_base_classes.py
```

### Test Isolation

```bash
# Run tests in isolation
pytest --dist=no

# Run tests sequentially
pytest -n 0
```

### Coverage Debugging

```bash
# Generate detailed coverage report
pytest --cov=HandleGeneric --cov-report=html --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
