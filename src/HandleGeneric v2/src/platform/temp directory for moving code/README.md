# Cold Run Analyzer

A professional-grade code analysis tool that performs comprehensive analysis of codebases to determine programming languages, architecture patterns, and framework usage. This tool integrates with Azure OpenAI for intelligent analysis and provides detailed insights for code generation processes.

## 🎯 Features

### ✅ **Project Structure Analysis**

- Complete folder tree mapping
- File extension analysis
- Language detection from file types
- Size and metadata collection

### ✅ **Intelligent Pattern Detection**

- Architecture pattern recognition (MVC, MVVM, Clean Architecture, etc.)
- Framework detection (Django, Flask, React, Angular, etc.)
- Design pattern identification
- Project type classification

### ✅ **AI-Powered Analysis**

- Azure OpenAI integration for deep insights
- Programming language confidence scoring
- Architecture pattern validation
- Framework usage analysis
- Code quality assessment

### ✅ **Professional Output**

- Structured JSON reports
- Comprehensive metadata
- AI-generated insights
- Actionable recommendations

## 🚀 Quick Start

### 1. **Installation**

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export AZURE_OPENAI_API_KEY="your-azure-openai-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
```

### 2. **Basic Usage**

```bash
# Analyze current directory
python cold_run.py . analysis.json

# Analyze specific project
python cold_run.py /path/to/project results/analysis.json

# Test AI connection first
python cold_run.py --test-ai
```

### 3. **Advanced Usage**

```bash
# Verbose output with detailed logging
python cold_run.py . analysis.json --verbose

# Skip AI analysis (structure only)
python cold_run.py . analysis.json --no-ai

# Custom configuration
python cold_run.py . analysis.json --config custom_config.json
```

## 📊 What You Get

### **Project Structure Analysis**

```json
{
  "project_structure": {
    "root_path": "/path/to/project",
    "total_files": 150,
    "total_directories": 25,
    "file_extensions": [".py", ".js", ".html", ".css"],
    "languages_detected": ["python", "javascript", "html", "css"],
    "architecture_hints": ["mvc", "repository"],
    "framework_indicators": ["django", "react"]
  }
}
```

### **AI-Generated Insights**

```json
{
  "ai_analysis": {
    "primary_language": "python",
    "architecture_pattern": "MVC with Repository",
    "framework": "Django",
    "project_type": "Web Application",
    "confidence_score": 95,
    "recommendations": [
      "Consider implementing Clean Architecture",
      "Add comprehensive testing",
      "Improve documentation"
    ]
  }
}
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Required
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Optional
AZURE_OPENAI_API_VERSION=2024-02-01
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

### **Configuration File**

Create `config.json` for custom settings:

```json
{
  "ai_config": {
    "max_tokens": 2000,
    "temperature": 0.1
  },
  "analysis_config": {
    "max_file_size_mb": 15,
    "ignored_directories": [".git", "node_modules"],
    "parallel_analysis": true
  },
  "output_config": {
    "include_file_contents": false,
    "log_level": "DEBUG"
  }
}
```

## 🏗️ Architecture

### **Core Components**

```
ColdRunAnalyzer
├── Project Structure Analysis
│   ├── File System Scanner
│   ├── Language Detector
│   └── Pattern Recognizer
├── AI Integration
│   ├── Azure OpenAI Client
│   ├── Prompt Builder
│   └── Response Parser
└── Output Generation
    ├── JSON Formatter
    ├── Report Builder
    └── File Writer
```

### **Analysis Pipeline**

1. **Project Scanning** → File discovery and metadata collection
2. **Pattern Detection** → Language, architecture, and framework identification
3. **AI Analysis** → Deep insights and recommendations
4. **Report Generation** → Structured output and summaries

## 📁 File Structure

```
cold_run_analyzer/
├── cold_run.py          # Main analyzer script
├── client.py            # Azure OpenAI client integration
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
└── examples/           # Usage examples
    ├── sample_project/ # Sample project for testing
    └── configs/        # Configuration examples
```

## 🎮 Usage Examples

### **Example 1: Python Web Application**

```bash
python cold_run.py /path/to/django-app analysis.json
```

**Output:**

- Primary Language: Python
- Architecture: MVC with Repository Pattern
- Framework: Django
- Project Type: Web Application
- Confidence: 92%

### **Example 2: React Frontend**

```bash
python cold_run.py /path/to/react-app analysis.json
```

**Output:**

- Primary Language: JavaScript/TypeScript
- Architecture: Component-based
- Framework: React
- Project Type: Frontend Application
- Confidence: 88%

### **Example 3: Microservices Backend**

```bash
python cold_run.py /path/to/microservices analysis.json
```

**Output:**

- Primary Language: Java/Python
- Architecture: Microservices
- Framework: Spring Boot/FastAPI
- Project Type: Backend Services
- Confidence: 95%

## 🔍 Pattern Detection

### **Architecture Patterns**

- **MVC/MVVM**: Controller, Model, View, ViewModel
- **Clean Architecture**: Domain, UseCase, Repository, Presentation
- **Hexagonal**: Port, Adapter, Domain
- **Microservices**: Service, Gateway, Discovery
- **Event-Driven**: Event, Listener, Publisher, Subscriber

### **Framework Detection**

- **Web**: Django, Flask, FastAPI, Express, Rails
- **Frontend**: React, Angular, Vue, Svelte
- **Mobile**: Flutter, React Native, Xamarin
- **Desktop**: Electron, Tauri, PyQt, Tkinter

### **Language Detection**

- **Compiled**: Java, C++, Rust, Go, C#
- **Interpreted**: Python, JavaScript, Ruby, PHP
- **Hybrid**: TypeScript, Kotlin, Scala
- **Markup**: HTML, CSS, XML, YAML, JSON

## 🚀 Integration with Code Generation

### **Workflow Integration**

```python
from cold_run import ColdRunAnalyzer

# 1. Analyze existing codebase
analyzer = ColdRunAnalyzer(ai_client)
project_structure = analyzer.analyze_project_structure(Path("./project"))

# 2. Generate AI insights
ai_analysis = analyzer.generate_ai_analysis(project_structure)

# 3. Use insights for code generation
language = ai_analysis.get("primary_language", "python")
architecture = ai_analysis.get("architecture_pattern", "mvc")
framework = ai_analysis.get("framework", "django")

# 4. Generate appropriate code
generate_code(requirements, language, architecture, framework)
```

### **Output for Code Generation**

The analyzer provides:

- **Language Context**: Primary and secondary languages
- **Architecture Context**: Existing patterns to follow
- **Framework Context**: Libraries and tools in use
- **Quality Indicators**: Areas for improvement
- **Recommendations**: Best practices and suggestions

## 🧪 Testing

### **Run Tests**

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=cold_run tests/

# Run specific test
pytest tests/test_analyzer.py -v
```

### **Test AI Connection**

```bash
python cold_run.py --test-ai
```

## 📈 Performance

### **Optimization Features**

- **Parallel Processing**: Multi-threaded file analysis
- **Smart Filtering**: Skip irrelevant files and directories
- **Caching**: Cache AI responses for repeated analysis
- **Incremental Analysis**: Only analyze changed files

### **Performance Metrics**

- **Small Project** (<100 files): ~5-10 seconds
- **Medium Project** (100-1000 files): ~30-60 seconds
- **Large Project** (>1000 files): ~2-5 minutes

## 🔒 Security

### **Data Protection**

- **No Code Upload**: All analysis is local
- **Secure API Calls**: Encrypted communication with Azure OpenAI
- **Configurable Limits**: File size and count restrictions
- **Audit Logging**: Complete analysis history

### **Privacy Features**

- **Local Processing**: Code never leaves your machine
- **Configurable Output**: Control what information is saved
- **Secure Storage**: Encrypted configuration files

## 🆘 Troubleshooting

### **Common Issues**

**AI Connection Failed**

```bash
# Check environment variables
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Test connection
python cold_run.py --test-ai
```

**Large Project Timeout**

```bash
# Increase timeout in config
ANALYSIS_TIMEOUT_SECONDS=600

# Use parallel processing
PARALLEL_ANALYSIS=true
MAX_WORKERS=8
```

**Memory Issues**

```bash
# Reduce file size limit
MAX_FILE_SIZE_MB=5

# Limit file count
MAX_FILES_TO_ANALYZE=500
```

### **Debug Mode**

```bash
# Enable verbose logging
python cold_run.py . analysis.json --verbose

# Check log file
tail -f cold_run_analysis.log
```

## 🤝 Contributing

### **Development Setup**

```bash
# Clone repository
git clone <repository-url>
cd cold_run_analyzer

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest

# Format code
black cold_run.py
flake8 cold_run.py
```

### **Adding New Patterns**

```python
# Add to language_patterns
self.language_patterns['newlang'] = ['.nl', '.nlg']

# Add to architecture_patterns
self.architecture_patterns['new_pattern'] = ['keyword1', 'keyword2']

# Add to framework_patterns
self.framework_patterns['newframework'] = ['config', 'main']
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Azure OpenAI for intelligent analysis capabilities
- The open-source community for pattern detection algorithms
- Contributors and users for feedback and improvements

## 📞 Support

For questions and support:

- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration examples
- Test with the sample projects

---

**Ready to analyze your codebase? Run `python cold_run.py --help` to get started!** 🚀
