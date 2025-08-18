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
    METADATA_FILE: str = os.getenv("METADATA_FILE", "data/metadata.json")
    STATUS_LOG_FILE: str = os.getenv("STATUS_LOG_FILE", "data/status_log.json")
    IMPLEMENTED_REQUIREMENTS_FILE: str = os.getenv(
        "IMPLEMENTED_REQUIREMENTS_FILE",
        ".../output/PythonExample/environment/implementedRequirements.csv",
    )
    REQUIREMENTS: str = os.getenv(
        "REQUIREMENTS", "./input/PythonExample/environment/requirements.csv"
    )
    CODEBASE_ROOT: str = os.getenv("CODEBASE_ROOT", "./input/PythonExample/code/")

    # AI Service Configuration - Azure OpenAI
    # NOTE: These must be set in environment variables or .env file
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"
    )
    WORKSPACE: str = os.getenv("WORKSPACE", "LOCAL")
    LANGUAGE_ARCHITECTURE: str = os.getenv("LANGUAGE_ARCHITECTURE")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR")
    # Legacy OpenAI Configuration (kept for backward compatibility)
    # NOTE: These must be set in environment variables or .env file
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    REGION: str = os.getenv("REGION", "swedencentral")

    # AI Parameters
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "4000"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.1"))
    AI_TOP_P: float = float(os.getenv("AI_TOP_P", "1.0"))
    AI_FREQUENCY_PENALTY: float = float(os.getenv("AI_FREQUENCY_PENALTY", "0.0"))
    AI_PRESENCE_PENALTY: float = float(os.getenv("AI_PRESENCE_PENALTY", "0.0"))
    METADATA: str = os.getenv("METADATA")
    OUTPUT_CODE: str = os.getenv("OUTPUT_CODE")
    IMPLEMENTED_REQUIREMENTS: str = os.getenv(
        "IMPLEMENTED_REQUIREMENTS",
        "/Users/abdullahhesham/Documents/GitHub/Predictable-Secure-Code-Generation/output/PythonExample/Example1/environment/IMPLEMENTED_REQUIREMENTS.csv",
    )
    # Default System Prompts
    DEFAULT_SYSTEM_PROMPT: str = os.getenv(
        "DEFAULT_SYSTEM_PROMPT",
        "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
    )

    CODE_CORRECTION_PROMPT: str = os.getenv(
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
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    VALIDATION_TIMEOUT: int = int(os.getenv("VALIDATION_TIMEOUT", "300"))  # 5 minutes

    # Code style settings
    PYTHON_FORMATTER: str = os.getenv("PYTHON_FORMATTER", "black")
    LINTER: str = os.getenv("LINTER", "flake8")
    TEST_COMMAND: str = os.getenv("TEST_COMMAND", "pytest")

    # Directories to exclude from analysis
    EXCLUDE_DIRS: List[str] = None

    # Azure Function specific settings
    FUNCTION_TIMEOUT: int = int(
        os.getenv("AZURE_FUNCTION_TIMEOUT", "600")
    )  # 10 minutes

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    def __post_init__(self):
        """Initialize computed fields after dataclass initialization"""
        if self.EXCLUDE_DIRS is None:
            self.EXCLUDE_DIRS = [
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
        if not os.path.exists(os.path.dirname(cls.REQUIREMENTS)):
            os.makedirs(os.path.dirname(cls.REQUIREMENTS), exist_ok=True)

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
