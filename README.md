# Collaborative Programming Tool - Prototype 2

An intelligent Azure Functions-based system that automatically processes requirement updates and generates/modifies code using AI.

## Features

- **Daily Automated Processing**: Runs on a schedule to check for new requirements
- **Requirements Management**: Supports CSV/Excel files for requirement tracking
- **AI-Powered Code Generation**: Uses OpenAI GPT models to generate and modify code
- **Code Validation**: Automated testing, linting, and syntax checking
- **Retry Logic**: Intelligent retry mechanism for failed operations
- **Comprehensive Logging**: Detailed status tracking and metadata management
- **RESTful API**: HTTP endpoints for manual triggers and status checking

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Requirements   │    │   Code Analyzer  │    │   AI Code       │
│  Checker        │───▶│                  │───▶│   Editor        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Metadata       │    │   Code           │    │   Status        │
│  Manager        │    │   Validator      │    │   Logger        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
automated-code-update-system/
├── function_app.py              # Main Azure Function entry point
├── config.py                    # Configuration management
├── requirements_checker.py      # Requirement update detection
├── code_analyzer.py            # Codebase analysis and change identification
├── ai_code_editor.py           # AI-powered code generation/modification
├── code_validator.py           # Code validation and testing
├── metadata_manager.py         # Metadata and status management
├── requirements.txt            # Python dependencies
├── host.json                   # Azure Functions configuration
├── local.settings.json         # Local environment settings
├── data/                       # Data files
│   ├── requirements.csv        # Requirements file
│   ├── metadata.json          # System metadata
│   └── status_log.json        # Status logs
└── tests/                     # Test files
```

## USER GUIDE - How to start?
Please follow the steps as follows to use this tool. 

### Prerequisites

- Python 3.9+
- Azure Functions Core Tools
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd automated-code-update-system
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Update `local.settings.json` with your settings:

   ```json
   {
     "Values": {
       "OPENAI_API_KEY": "your-openai-api-key",
       "OPENAI_MODEL": "gpt-4",
       "REQUIREMENTS_FILE": "data/requirements.csv"
     }
   }
   ```

4. **Initialize sample data**
   ```bash
   # Sample requirements file is already provided in data/requirements.csv
   # Modify it according to your needs
   ```

### Running Locally

1. **Start the Azure Functions runtime**

   ```bash
   func start
   ```

2. **Access the endpoints**
   - Status: `GET http://localhost:7071/api/status`
   - Manual trigger: `POST http://localhost:7071/api/trigger-manual`

## 📋 Usage

### Requirements File Format

The system expects a CSV or Excel file with the following columns:

| Column          | Description                                 | Required |
| --------------- | ------------------------------------------- | -------- |
| id              | Unique requirement identifier               | Yes      |
| name            | Requirement name                            | Yes      |
| description     | Detailed description                        | Yes      |
| priority        | Priority level (High/Medium/Low)            | Yes      |
| status          | Current status (new/pending/completed)      | Yes      |
| category        | Category (Authentication/API/Database/etc.) | No       |
| estimated_hours | Estimated development time                  | No       |
| created_date    | Creation date                               | No       |

### Workflow

1. **Daily Trigger**: System runs automatically at 9:00 AM UTC
2. **Check Updates**: Compares current requirements file with last processed version
3. **Analyze Changes**: Identifies new requirements and determines needed code changes
4. **Generate Code**: Uses AI to create/modify files based on requirements
5. **Validate**: Runs syntax checks, linting, and tests
6. **Retry Logic**: Retries up to 3 times on validation failures
7. **Update Metadata**: Tracks processing results and system state

## 🔧 Configuration

### Environment Variables

| Variable             | Description                  | Default               |
| -------------------- | ---------------------------- | --------------------- |
| `OPENAI_API_KEY`     | OpenAI API key               | Required              |
| `OPENAI_MODEL`       | AI model to use              | gpt-4                 |
| `REQUIREMENTS_FILE`  | Path to requirements file    | data/requirements.csv |
| `MAX_RETRIES`        | Maximum retry attempts       | 3                     |
| `VALIDATION_TIMEOUT` | Validation timeout (seconds) | 300                   |

### Supported File Types

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C++ (.cpp)
- C# (.cs)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_requirements_checker.py
```

## 📊 Monitoring

### Status Endpoint

```bash
curl http://localhost:7071/api/status
```

Response includes:

- Latest processing status
- Success rate statistics
- Recent activity log
- System metadata

### Logs

The system maintains detailed logs in:

- `data/status_log.json` - Processing status history
- `data/metadata.json` - System metadata and statistics
- Azure Functions logs - Runtime information

## 🛠️ Development

### Adding New Requirement Categories

1. Modify `code_analyzer.py`
2. Update the `_map_requirement_to_changes` method
3. Add keyword mappings for your new category

### Custom AI Prompts

1. Edit `ai_code_editor.py`
2. Modify prompt generation methods:
   - `_generate_creation_prompt`
   - `_generate_modification_prompt`

### Additional Validators

1. Extend `code_validator.py`
2. Add new validation methods to `_validate_single_file`

## 🔒 Security

- Environment variables for sensitive data
- Input validation for all external data
- Backup creation before file modifications
- Sandboxed code execution for validation

## 📈 Performance

- Parallel processing where possible
- Intelligent caching of analysis results
- Configurable timeouts and retry limits
- Automatic cleanup of old data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API errors**: Verify API key and rate limits
2. **File permission errors**: Check directory permissions
3. **Validation failures**: Review code syntax and test cases
4. **Memory issues**: Adjust function memory allocation

### Debug Mode

Set logging level to DEBUG in `local.settings.json`:

```json
{
  "Values": {
    "PYTHON_LOG_LEVEL": "DEBUG"
  }
}
```

## 📞 Support

For questions and support:

- Create an issue in the repository
- Review the troubleshooting section
- Check Azure Functions documentation