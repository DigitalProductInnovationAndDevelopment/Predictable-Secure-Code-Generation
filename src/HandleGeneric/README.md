# Generic Code Handler

A comprehensive, language-agnostic code processing system that supports metadata extraction, validation, and AI-powered code generation for multiple programming languages.

## 🌟 Features

- **Multi-language Support**: Python, JavaScript, TypeScript, Java, C#
- **Metadata Extraction**: Unified schema across all languages
- **Code Validation**: Language-specific syntax checking
- **AI Code Generation**: Generate code in any supported language
- **Extensible Architecture**: Easy to add new language support
- **CLI Interface**: Command-line tools for all operations

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# For AI functionality (optional)
pip install openai
```

### Basic Usage

```python
from HandleGeneric import (
    GenericMetadataGenerator,
    GenericValidator,
    GenericCodeGenerator,
    get_supported_languages
)

# Check supported languages
print("Supported languages:", get_supported_languages())

# Generate metadata for a project
generator = GenericMetadataGenerator()
metadata = generator.generate_metadata(
    project_path="./my_project",
    output_path="./output"
)

# Validate code
validator = GenericValidator()
result = validator.validate_project("./my_project")
print(f"Validation status: {result.status.value}")

# Generate code (requires AI client)
from AIBrain.ai import AzureOpenAIClient
ai_client = AzureOpenAIClient()
code_generator = GenericCodeGenerator(ai_client)

requirements = [
    {"id": "req1", "description": "Create a function to calculate fibonacci numbers"}
]

result = code_generator.generate_from_requirements(
    requirements=requirements,
    target_language="python",
    output_path="./generated"
)
```

## 🖥️ Command Line Interface

### Generate Metadata

Extract metadata from any supported codebase:

```bash
# Basic metadata generation
python main.py generate-metadata ./my_project ./output

# Process specific languages only
python main.py generate-metadata ./my_project ./output --languages python javascript

# Show detailed breakdown
python main.py generate-metadata ./my_project ./output --show-details
```

### Validate Code

Validate syntax across multiple languages:

```bash
# Validate entire project
python main.py validate ./my_project

# Validate specific languages
python main.py validate ./my_project --languages python typescript

# Stop on first error
python main.py validate ./my_project --stop-on-error --show-details
```

### Generate Code

Generate code from requirements using AI:

```bash
# Generate Python code from CSV requirements
python main.py generate-code requirements.csv python ./generated

# Generate with custom context
python main.py generate-code requirements.json javascript ./output \
    --context "This is a web application using Express.js" \
    --show-details
```

### List Supported Languages

```bash
python main.py list-languages
```

### Create Templates

```bash
# Create a Python class template
python main.py create-template python class ./templates --filename MyClass.py

# Create a JavaScript module template
python main.py create-template javascript module
```

## 📊 Metadata Schema

The system generates unified metadata across all languages:

```json
{
  "files": [
    {
      "path": "src/main.py",
      "language": "python",
      "size": 1024,
      "lines_of_code": 45,
      "classes": [
        {
          "name": "MyClass",
          "visibility": "public",
          "start_line": 10,
          "end_line": 30,
          "methods": [...],
          "base_classes": [...],
          "interfaces": [...]
        }
      ],
      "functions": [...],
      "imports": [...],
      "constants": {...}
    }
  ],
  "languages": ["python", "javascript"],
  "language_summaries": {
    "python": {
      "file_count": 5,
      "total_lines": 250,
      "total_size": 8192
    }
  },
  "project_info": {
    "main_language": "python",
    "project_type": "web",
    "total_files": 5,
    "generation_time": 1.23
  }
}
```

## 🔧 Language Support

### Currently Supported

| Language   | Extensions      | Features                            |
| ---------- | --------------- | ----------------------------------- |
| Python     | .py, .pyi, .pyw | AST parsing, syntax validation      |
| JavaScript | .js, .jsx, .mjs | Regex parsing, Node.js validation   |
| TypeScript | .ts, .tsx       | Type analysis, tsc validation       |
| Java       | .java           | Method extraction, javac validation |
| C#         | .cs             | XML doc parsing, dotnet validation  |

### Adding New Languages

Create a new language provider:

```python
from HandleGeneric.core.language_provider import LanguageProvider
from HandleGeneric.core.language_registry import register_provider

class MyLanguageProvider(LanguageProvider):
    @property
    def language_name(self) -> str:
        return "mylang"

    @property
    def file_extensions(self) -> Set[str]:
        return {".ml"}

    # Implement other required methods...

# Register the provider
register_provider(MyLanguageProvider())
```

## 🤖 AI Integration

The system integrates with Azure OpenAI for code generation:

```python
from AIBrain.ai import AzureOpenAIClient
from HandleGeneric import GenericCodeGenerator

# Initialize AI client
ai_client = AzureOpenAIClient()

# Create generator with AI support
generator = GenericCodeGenerator(ai_client)

# Generate code with specific context
context = {
    "project_context": "Building a REST API",
    "generate_tests": True,
    "max_tokens": 2000,
    "temperature": 0.7
}

result = generator.generate_from_requirements(
    requirements=[{"description": "Create user authentication endpoint"}],
    target_language="typescript",
    output_path="./api",
    context=context
)
```

## 📁 Project Structure

```
src/HandleGeneric/
├── core/                       # Core abstractions
│   ├── language_provider.py    # Base provider interface
│   ├── language_registry.py    # Provider registry
│   └── file_detector.py        # File detection utilities
├── providers/                  # Language-specific providers
│   ├── python_provider.py      # Python support
│   ├── javascript_provider.py  # JavaScript support
│   ├── typescript_provider.py  # TypeScript support
│   ├── java_provider.py        # Java support
│   └── csharp_provider.py      # C# support
├── generic_metadata_generator.py  # Multi-language metadata
├── generic_validator.py           # Multi-language validation
├── generic_code_generator.py      # Multi-language generation
├── language_init.py               # Provider initialization
└── main.py                        # CLI interface
```

## 🔍 Examples

### Process a Multi-language Project

```python
# Analyze a full-stack web project
generator = GenericMetadataGenerator()
metadata = generator.generate_metadata("./webapp", "./analysis")

# The metadata will include:
# - Python backend files (.py)
# - JavaScript frontend files (.js, .jsx)
# - TypeScript components (.ts, .tsx)
# - All with unified schema
```

### Validate Mixed Codebase

```python
# Validate all supported files
validator = GenericValidator()
result = validator.validate_project("./mixed_project")

# Check results by language
for language, results in result.results_by_language.items():
    valid_count = sum(1 for r in results if r.status.value == "valid")
    print(f"{language}: {valid_count}/{len(results)} files valid")
```

### Generate Code for Multiple Languages

```python
# Same requirements, different target languages
requirements = [{"description": "Create a data validation function"}]

for language in ["python", "javascript", "java"]:
    result = generator.generate_from_requirements(
        requirements=requirements,
        target_language=language,
        output_path=f"./output/{language}"
    )
    print(f"Generated {language} code: {len(result.generated_files)} files")
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Test specific language provider
python -m pytest tests/test_python_provider.py

# Test with coverage
python -m pytest --cov=src/HandleGeneric tests/
```

## 📈 Performance

The system is optimized for large codebases:

- **Parallel processing**: Multiple files processed concurrently
- **Efficient parsing**: Language-specific optimizations
- **Memory management**: Streaming for large files
- **Caching**: Provider instances cached globally

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your language provider in `providers/`
4. Update tests and documentation
5. Submit a pull request

### Adding Language Support

1. Create provider class inheriting from `LanguageProvider`
2. Implement all required abstract methods
3. Add provider to `providers/__init__.py`
4. Update `language_init.py` to register it
5. Add tests in `tests/test_your_language_provider.py`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📖 Documentation: See individual module docstrings
- 🐛 Issues: Create an issue on GitHub
- 💬 Discussions: Use GitHub discussions for questions

## 🗺️ Roadmap

- [ ] Add support for more languages (Go, Rust, Ruby)
- [ ] Implement semantic analysis beyond syntax
- [ ] Add code quality metrics
- [ ] Integration with popular IDEs
- [ ] Web-based interface
- [ ] API documentation generation
- [ ] Code refactoring suggestions

---

**Generic Code Handler** - Making code processing truly language-agnostic! 🚀
