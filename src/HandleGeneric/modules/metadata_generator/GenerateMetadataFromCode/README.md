# Generate Metadata From Code

A comprehensive Python tool for extracting detailed metadata from Python codebases. This tool analyzes your Python projects and generates structured JSON metadata containing information about functions, classes, imports, entry points, and more.

## Features

- **Comprehensive Analysis**: Extracts functions, classes, methods, imports, and entry points
- **AST-based Parsing**: Uses Python's Abstract Syntax Tree for accurate code analysis
- **Configurable**: Highly customizable with extensive configuration options
- **AI Enhancement**: Optional AI-powered insights using Azure OpenAI
- **Multiple Modes**: Support for both full project analysis and single file analysis
- **Entry Point Detection**: Automatically identifies application entry points
- **Dependency Analysis**: Distinguishes between internal and external dependencies
- **Complexity Metrics**: Calculates various code complexity metrics

## Installation

The tool uses only Python standard library modules for core functionality, making it lightweight and dependency-free.

```bash
# Clone the repository
git clone <repository-url>
cd Predictable-Secure-Code-Generation

# No additional installation required for basic usage
```

## Usage

### Basic Usage

```bash
# Generate metadata for a project
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory

# Generate metadata for a single file
python src/GenerateMetadataFromCode/main.py /path/to/file.py /output/directory --single-file

# Custom output filename
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory --output-filename my_metadata.json
```

### Advanced Usage

```bash
# Include private methods and AI enhancement
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory --include-private --ai-enhance

# Exclude certain extractions
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory --exclude-docstrings --exclude-type-hints

# Use custom configuration
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory --config-file config.json

# Dry run to see what would be processed
python src/GenerateMetadataFromCode/main.py /path/to/project /output/directory --dry-run
```

### CLI Options

- `project_path`: Path to the project directory or Python file
- `output_path`: Path to save the metadata.json file
- `--output-filename, -o`: Name of the output file (default: metadata.json)
- `--single-file, -f`: Generate metadata for a single Python file
- `--ai-enhance, -ai`: Enhance metadata with AI insights
- `--include-private`: Include private methods and classes
- `--exclude-docstrings`: Don't extract docstrings
- `--exclude-type-hints`: Don't extract type hints
- `--exclude-decorators`: Don't extract decorators
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--config-file`: Path to JSON configuration file
- `--dry-run`: Show what would be done without actually generating metadata

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "files": [
    {
      "path": "src/app.py",
      "functions": [
        {
          "name": "process_data",
          "args": ["input"],
          "docstring": "Processes input data and returns the result.",
          "start_line": 10,
          "end_line": 25,
          "decorators": ["@property"],
          "return_type": "str",
          "is_async": false
        }
      ],
      "classes": [
        {
          "name": "DataProcessor",
          "docstring": "Class for processing data",
          "start_line": 30,
          "end_line": 60,
          "base_classes": ["BaseProcessor"],
          "decorators": ["@dataclass"],
          "methods": [
            {
              "name": "process",
              "args": ["self", "data"],
              "docstring": "Process the data",
              "start_line": 35,
              "end_line": 45
            }
          ]
        }
      ],
      "imports": ["json", "os", "typing.Dict"]
    }
  ],
  "entry_points": ["src/app.py -> main()"],
  "dependencies": {
    "internal_dependencies": ["utils", "config"],
    "external_dependencies": ["json", "os", "pathlib"],
    "total_internal": 2,
    "total_external": 3
  },
  "metrics": {
    "total_files": 5,
    "total_functions": 12,
    "total_classes": 3,
    "total_methods": 8,
    "estimated_lines_of_code": 250,
    "average_function_complexity": 8.5,
    "average_class_complexity": 25.0,
    "functions_per_file": 2.4,
    "classes_per_file": 0.6
  },
  "project_info": {
    "source_path": "/path/to/project",
    "total_files": 5,
    "generation_time": 0.15,
    "generator_version": "1.0.0"
  }
}
```

## Configuration

You can customize the behavior using a JSON configuration file:

```json
{
  "include_patterns": ["*.py"],
  "exclude_patterns": ["__pycache__/*", "*.pyc", ".git/*", ".pytest_cache/*"],
  "entry_point_functions": ["main", "run", "start"],
  "entry_point_files": ["main.py", "app.py", "run.py"],
  "extract_docstrings": true,
  "extract_type_hints": true,
  "extract_decorators": true,
  "extract_base_classes": true,
  "include_private_methods": false,
  "include_magic_methods": true,
  "output_filename": "metadata.json",
  "indent_json": 2,
  "sort_keys": true,
  "log_level": "INFO"
}
```

## AI Enhancement

When the `--ai-enhance` flag is used and Azure OpenAI is configured, the tool will add AI-generated insights to the metadata:

```json
{
  "ai_insights": {
    "description": "This is a data processing application...",
    "patterns": ["Factory Pattern", "Observer Pattern"],
    "improvements": ["Consider adding type hints", "Add unit tests"],
    "quality_assessment": "Good code structure with clear separation of concerns"
  }
}
```

## Examples

### Example 1: Basic Project Analysis

```bash
python src/GenerateMetadataFromCode/main.py input/code output/environment
```

This will analyze the calculator project in `input/code` and save the metadata to `output/environment/metadata.json`.

### Example 2: Single File Analysis

```bash
python src/GenerateMetadataFromCode/main.py input/code/main.py output/environment --single-file
```

### Example 3: Enhanced Analysis with AI

```bash
python src/GenerateMetadataFromCode/main.py input/code output/environment --ai-enhance --include-private
```

## Architecture

The tool is structured into several key components:

- **`core/generator.py`**: Main orchestrator that coordinates the entire process
- **`core/parser.py`**: AST-based parser for extracting code elements
- **`core/analyzer.py`**: Analyzer for identifying entry points and relationships
- **`utils/config.py`**: Configuration management
- **`utils/helpers.py`**: Utility functions for file operations
- **`main.py`**: CLI interface

## Error Handling

The tool includes comprehensive error handling:

- Graceful handling of syntax errors in source files
- File encoding issues are handled safely
- Missing directories are created automatically
- Detailed logging for troubleshooting

## Logging

The tool provides detailed logging at different levels:

- **DEBUG**: Detailed information for each file processed
- **INFO**: General progress information (default)
- **WARNING**: Non-critical issues (e.g., unreadable files)
- **ERROR**: Critical errors that prevent processing
- **CRITICAL**: Fatal errors that stop execution

## License

This project is part of the Predictable Secure Code Generation system.

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for new features
4. Ensure backward compatibility
