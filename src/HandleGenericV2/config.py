import os
from dataclasses import dataclass
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration settings for the automated code update system"""

    # File paths
    METADATA_FILE = os.getenv("METADATA_FILE", "data/metadata.json")
    STATUS_LOG_FILE = os.getenv("STATUS_LOG_FILE", "data/status_log.json")
    IMPLEMENTED_REQUIREMENTS_FILE = os.getenv(
        "IMPLEMENTED_REQUIREMENTS_FILE",
        ".../output/PythonExample/environment/implementedRequirements.csv",
    )
    REQUIREMENTS_FILE = os.getenv(
        "REQUIREMENTS_FILE", "./input/PythonExample/environment/requirements.csv"
    )
    CODEBASE_ROOT = os.getenv("CODEBASE_ROOT", "./input/PythonExample/code/")

    # AI Service Configuration - Azure OpenAI
    # NOTE: These must be set in environment variables or .env file
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    WORKSPACE = os.getenv("WORKSPACE", "LOCAL")
    LANGUAGE_ARCHITECTURE = os.getenv("LANGUAGE_ARCHITECTURE")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR")
    # Legacy OpenAI Configuration (kept for backward compatibility)
    # NOTE: These must be set in environment variables or .env file
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    REGION = os.getenv("REGION", "swedencentral")

    # AI Parameters
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4000"))
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.1"))
    AI_TOP_P = float(os.getenv("AI_TOP_P", "1.0"))
    AI_FREQUENCY_PENALTY = float(os.getenv("AI_FREQUENCY_PENALTY", "0.0"))
    AI_PRESENCE_PENALTY = float(os.getenv("AI_PRESENCE_PENALTY", "0.0"))
    IMPLEMENTED_REQUIREMENTS = os.getenv(
        "IMPLEMENTED_REQUIREMENTS",
        "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/Example1/environment/IMPLEMENTED_REQUIREMENTS.csv",
    )
    # Default System Prompts
    DEFAULT_SYSTEM_PROMPT = os.getenv(
        "DEFAULT_SYSTEM_PROMPT",
        "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
    )

    REQUIREMENTS = os.getenv("REQUIREMENTS")

    CODE_CORRECTION_PROMPT = os.getenv(
        "CODE_CORRECTION_PROMPT",
        (
            "You are a Python code corrector. Follow these rules: "
            "1. ALWAYS return the code block first "
            "2. If no corrections are needed, return the original code verbatim with '# No corrections needed' appended "
            "3. If corrections are needed: - Provide the corrected code - Add brief explanations as Python comments - Include any missing imports "
            "4. Never omit the code itself"
        ),
    )

    # Validation settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    VALIDATION_TIMEOUT = int(os.getenv("VALIDATION_TIMEOUT", "300"))  # 5 minutes

    # Code style settings
    PYTHON_FORMATTER = os.getenv("PYTHON_FORMATTER", "black")
    LINTER = os.getenv("LINTER", "flake8")
    TEST_COMMAND = os.getenv("TEST_COMMAND", "pytest")

    # Directories to exclude from analysis
    EXCLUDE_DIRS = [
        "__pycache__",
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "dist",
        "build",
    ]

    # Azure Function specific settings
    FUNCTION_TIMEOUT = int(os.getenv("AZURE_FUNCTION_TIMEOUT", "600"))  # 10 minutes

    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        # Validate required sensitive configuration
        if not cls.AZURE_OPENAI_API_KEY:
            errors.append(
                "AZURE_OPENAI_API_KEY is required but not set in environment variables"
            )

        if not cls.AZURE_OPENAI_ENDPOINT:
            errors.append(
                "AZURE_OPENAI_ENDPOINT is required but not set in environment variables"
            )

        # Validate parameter ranges
        if cls.AI_MAX_TOKENS <= 0:
            errors.append("AI_MAX_TOKENS must be greater than 0")

        if not (0.0 <= cls.AI_TEMPERATURE <= 2.0):
            errors.append("AI_TEMPERATURE must be between 0.0 and 2.0")

        # Ensure required directories exist
        if not os.path.exists(os.path.dirname(cls.REQUIREMENTS_FILE)):
            os.makedirs(os.path.dirname(cls.REQUIREMENTS_FILE), exist_ok=True)

        if not os.path.exists(os.path.dirname(cls.METADATA_FILE)):
            os.makedirs(os.path.dirname(cls.METADATA_FILE), exist_ok=True)

        if not os.path.exists(os.path.dirname(cls.STATUS_LOG_FILE)):
            os.makedirs(os.path.dirname(cls.STATUS_LOG_FILE), exist_ok=True)

        return errors

    @classmethod
    def get_ignored_patterns(cls) -> List[str]:
        """Get gitignore-style patterns for files to ignore during analysis"""
        return [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__/*",
            "*.so",
            ".DS_Store",
            "*.log",
            "*.tmp",
            ".git/*",
            "node_modules/*",
            "venv/*",
            ".venv/*",
        ]

    # File extensions to analyze with their corresponding languages
    SUPPORTED_EXTENSIONS = {
        # Web & Scripting
        ".js": "JAVASCRIPT",
        ".ts": "TYPESCRIPT",
        ".jsx": "JAVASCRIPT (REACT)",
        ".tsx": "TYPESCRIPT (REACT)",
        ".html": "HTML",
        ".htm": "HTML",
        ".css": "CSS",
        ".scss": "SASS",
        ".less": "LESS",
        ".php": "PHP",
        ".rb": "RUBY",
        ".py": "PYTHON",
        ".ipynb": "PYTHON (JUPYTER)",
        ".r": "R",
        ".rmd": "R MARKDOWN",
        ".jl": "JULIA",
        ".pl": "PERL",
        ".sh": "SHELL",
        ".bash": "BASH",
        ".zsh": "ZSH",
        ".ps1": "POWERSHELL",
        # C-family
        ".c": "C",
        ".h": "C HEADER",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".hpp": "C++ HEADER",
        ".hh": "C++ HEADER",
        ".hxx": "C++ HEADER",
        ".java": "JAVA",
        ".class": "JAVA BYTECODE",
        ".scala": "SCALA",
        ".kt": "KOTLIN",
        ".kts": "KOTLIN SCRIPT",
        ".cs": "C#",
        ".vb": "VISUAL BASIC",
        # Data / Config / Query
        ".sql": "SQL",
        ".psql": "POSTGRESQL",
        ".mysql": "MYSQL",
        ".graphql": "GRAPHQL",
        ".gql": "GRAPHQL",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".ini": "INI",
        ".toml": "TOML",
        ".cfg": "CONFIG",
        ".conf": "CONFIG",
        # Functional Languages
        ".hs": "HASKELL",
        ".lhs": "HASKELL",
        ".ml": "OCAML",
        ".mli": "OCAML INTERFACE",
        ".fs": "F#",
        ".fsi": "F# INTERFACE",
        ".erl": "ERLANG",
        ".hrl": "ERLANG HEADER",
        ".ex": "ELIXIR",
        ".exs": "ELIXIR SCRIPT",
        ".clj": "CLOJURE",
        ".cljs": "CLOJURESCRIPT",
        ".edn": "CLOJURE DATA",
        # Systems & Low-level
        ".asm": "ASSEMBLY",
        ".s": "ASSEMBLY",
        ".go": "GO",
        ".rs": "RUST",
        ".zig": "ZIG",
        ".d": "D",
        ".nim": "NIM",
        # Markup / Docs
        ".md": "MARKDOWN",
        ".markdown": "MARKDOWN",
        ".tex": "LATEX",
        ".bib": "BIBTEX",
        ".rst": "RESTRUCTUREDTEXT",
        ".adoc": "ASCIIDOC",
        # Other
        ".lua": "LUA",
        ".dart": "DART",
        ".swift": "SWIFT",
        ".groovy": "GROOVY",
        ".mat": "MATLAB DATA",
        ".m": "MATLAB / OBJECTIVE-C",
        ".mm": "OBJECTIVE-C++",
        ".f": "FORTRAN",
        ".f90": "FORTRAN",
        ".f95": "FORTRAN",
        ".f03": "FORTRAN",
        ".f08": "FORTRAN",
        ".pro": "PROLOG",
        ".lisp": "LISP",
        ".scm": "SCHEME",
        ".rkt": "RACKET",
        ".coffee": "COFFEESCRIPT",
    }
