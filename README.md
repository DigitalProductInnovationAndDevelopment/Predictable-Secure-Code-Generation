# Enterprise Code Generation Platform

A clean, enterprise-grade architecture for a Python system with three first-class services:

- **S1 — Code Generation from Requirements**
- **S2 — Metadata Generation from Code**
- **S3 — Validation** (syntax → tests → AI logic checks)

## 🏗️ Architecture

Built using **Hexagonal (Ports & Adapters)** architecture with:

- **Provider pattern** for language-specific behavior
- **Pipeline pattern** for multi-stage validation
- **Command pattern** for consistent execution
- **Registry pattern** for dynamic provider discovery
- **Strategy pattern** for pluggable AI backends

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# or with poetry
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your OpenAI/Azure credentials
```

### 3. Check Platform Status

```bash
python -m platform.interfaces.cli.main status
```

### 4. Generate Code

```bash
# Generate Python code from requirements
python -m platform.interfaces.cli.main s1-generate \
  examples/requirements/sample_calculator.json \
  python \
  --output ./generated \
  --context examples/context/python_context.json
```

### 5. Extract Metadata

```bash
# Extract metadata from generated code
python -m platform.interfaces.cli.main s2-metadata \
  ./generated \
  --output metadata.json
```

### 6. Validate Code

```bash
# Run full validation pipeline
python -m platform.interfaces.cli.main s3-validate \
  ./generated \
  --requirements examples/requirements/sample_calculator.json \
  --metadata metadata.json \
  --ai-check \
  --output validation_report.json
```

## 📁 Project Structure

```
src/platform/
├── app/                        # Application layer (use-cases, pipelines)
│   ├── s1_codegen/            # S1 - Code Generation service
│   ├── s2_metadata/           # S2 - Metadata extraction service
│   └── s3_validation/         # S3 - Validation service
│
├── domain/                     # Pure domain logic
│   ├── models/                # Domain models (Pydantic)
│   ├── errors.py              # Domain errors
│   └── policies.py            # Business policies
│
├── ports/                      # Interfaces (contracts)
│   ├── ai.py                  # LLM & embeddings clients
│   ├── fs.py                  # File system operations
│   ├── providers.py           # Language providers
│   ├── runners.py             # Test runners & sandbox
│   └── observability.py       # Logging, metrics, tracing
│
├── adapters/                   # External system implementations
│   ├── ai/                    # OpenAI, Azure OpenAI
│   ├── fs/                    # Local file system
│   ├── runners/               # pytest, subprocess sandbox
│   └── providers/             # Python, TypeScript, etc.
│
├── kernel/                     # Cross-cutting infrastructure
│   ├── config.py              # Pydantic settings
│   ├── di.py                  # Dependency injection
│   ├── registry.py            # Provider discovery
│   └── logging.py             # Structured logging
│
└── interfaces/                 # CLI & API boundaries
    ├── cli/                   # Typer CLI
    └── api/                   # FastAPI (future)
```

### Legacy Structure (v1)

```
├── function_app.py                # Azure Functions entry
├── config.py                      # High-level config (paths, filters, limits; uses .env)
├── requirements.txt               # Python deps for the v1 toolset
├── quick_setup.py                 # Helper to install minimal deps
├── install_dependencies.py        # Installs broader toolchain (linters, pytest, etc.)
├── check_env.py                   # Verifies env vars (.env) and prints guidance
├── env.template                   # Sample env vars (copy to .env and edit)
├── input/                         # Place your input files here (e.g., CSV requirements)
├── src/
│   ├── HandlePython/              # v1: Python-specific S1/S2/S3 modules
│   │   ├── AIBrain/               # Azure OpenAI wrapper & CLI
│   │   ├── CheckCodeRequirements/ # CSV diff utilities
│   │   ├── GenerateCodeFromRequirements/  # S1: plan, generate, integrate
│   │   ├── GenerateMetadataFromCode/      # S2: AST-based metadata
│   │   └── ValidationUnit/                # S3: syntax / tests / AI checks
│   ├── HandleGeneric/             # v1: language-agnostic base + providers
│   │   ├── core/                  # registry, detection, generic generator/validator
│   │   └── providers/             # python/typescript/java… providers
│   └── HandleGeneric v2/          # v2: layered "platform" (Domain/Adapters/App/Interfaces)
│       ├── pyproject.toml         # can be installed as a package
│       └── src/platform/          # see "v2 platform" above
├── test_ai.py                     # Smoke tests for the AI layer (v1)
├── test_ai_cli.py                 # Smoke tests for AI CLI (v1)
└── src/validate_python_code.py    # Standalone syntax check helper
```

## 🔧 Services Overview

### S1 - Code Generation

Generates production-ready code from requirements:

```bash
# Basic usage
handle s1-generate requirements.json python

# With context and custom output
handle s1-generate requirements.json python \
  --output ./src \
  --context context.json \
  --dry-run
```

**Features:**

- Multi-language support (Python, TypeScript, Java)
- Prompt templating with context
- Automatic formatting (Black, isort)
- Syntax validation
- Cost tracking

### S2 - Metadata Extraction

Extracts structured metadata from codebases:

```bash
# Extract metadata from project
handle s2-metadata ./my-project --output metadata.json

# Filter by language
handle s2-metadata ./my-project \
  --languages python,typescript \
  --exclude node_modules,venv
```

**Features:**

- AST-based parsing
- Multi-language support
- Function/class extraction
- Import analysis
- LOC counting

### S3 - Validation Pipeline

Comprehensive validation in stages:

```bash
# Full validation pipeline
handle s3-validate ./project \
  --requirements requirements.json \
  --ai-check \
  --output report.json

# Syntax only
handle s3-validate ./project --no-tests
```

**Pipeline Stages:**

1. **Syntax**: AST parsing, linting
2. **Tests**: pytest, jest, etc.
3. **AI Logic**: Requirements consistency check

## 🧩 Language Providers

The platform uses providers for language-specific operations:

### Python Provider

- **Code Generation**: PEP 8, type hints, docstrings
- **Metadata**: AST parsing for functions/classes
- **Syntax**: ast.parse validation
- **Tests**: pytest runner

### TypeScript Provider (Planned)

- **Code Generation**: TSDoc, interfaces
- **Metadata**: TS compiler API
- **Syntax**: tsc --noEmit
- **Tests**: jest runner

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# AI Configuration
LLM_BACKEND=openai              # openai | azure
OPENAI_API_KEY=sk-...
MODEL=gpt-4
TEMPERATURE=0.0

# Limits
MAX_TOKENS=4000
MAX_REQUESTS_PER_HOUR=100
DRY_RUN=false

# File Processing
MAX_FILE_SIZE_MB=10
IGNORED_DIRECTORIES=.git,node_modules,dist

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🔍 CLI Commands

### Core Commands

- `handle s1-generate` - Generate code from requirements
- `handle s2-metadata` - Extract metadata from code
- `handle s3-validate` - Validate code (syntax → tests → AI)
- `handle status` - Show platform status
- `handle version` - Show version info

### Examples

```bash
# Generate Python calculator
handle s1-generate examples/requirements/calculator.json python

# Extract metadata with language filter
handle s2-metadata ./src --languages python --output meta.json

# Validate with AI logic check
handle s3-validate ./src --requirements req.json --ai-check

# Check what providers are available
handle status
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/

# With coverage
pytest --cov=platform tests/
```

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t platform:latest .

# Run CLI
docker run -it platform:latest handle status

# Run API (future)
docker run -p 8000:8000 platform:latest uvicorn platform.interfaces.api.app:app
```

### CI/CD

GitHub Actions workflow included for:

- Linting (ruff, mypy)
- Testing (pytest)
- Security (bandit)
- Docker builds

## 🔮 Roadmap

### Phase 1 - MVP ✅

- [x] Python providers (all 3 services)
- [x] CLI interface with Typer
- [x] OpenAI/Azure OpenAI support
- [x] Basic validation pipeline

### Phase 2 - Extensibility

- [ ] TypeScript providers
- [ ] Java providers
- [ ] Plugin system
- [ ] Web dashboard

### Phase 3 - Production

- [ ] FastAPI REST API
- [ ] Authentication & authorization
- [ ] Rate limiting & quotas
- [ ] Metrics & monitoring
- [ ] Multi-tenant support

### Phase 4 - Advanced

- [ ] Custom model fine-tuning
- [ ] Advanced static analysis
- [ ] Integration with IDEs
- [ ] Collaborative features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Adding Language Providers

To add a new language:

1. Create provider directory: `adapters/providers/mylang/`
2. Implement the three providers:
   - `codegen_provider.py`
   - `metadata_provider.py`
   - `syntax_validator.py`
3. Register in `kernel/di.py`
4. Add tests in `tests/unit/providers/mylang/`

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Pydantic for data validation
- Typer for CLI framework
- FastAPI for future API layer
- Rich for beautiful CLI output
