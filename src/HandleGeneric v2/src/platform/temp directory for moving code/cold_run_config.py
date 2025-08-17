"""
Configuration management for the Cold Run Analyzer.

This module provides configuration settings for the cold run analysis process,
including AI client settings, analysis parameters, and output formatting.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ColdRunConfig:
    """Configuration for cold run analysis."""

    # AI Client Configuration
    AZURE_OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    AZURE_OPENAI_ENDPOINT: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    AZURE_OPENAI_API_VERSION: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )
    AZURE_OPENAI_DEPLOYMENT_NAME: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    )

    # Analysis Configuration
    MAX_FILE_SIZE_MB: int = 10
    IGNORED_DIRECTORIES: List[str] = field(
        default_factory=lambda: [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "dist",
            "build",
            ".pytest_cache",
            ".coverage",
            ".mypy_cache",
        ]
    )
    IGNORED_EXTENSIONS: List[str] = field(
        default_factory=lambda: [
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".log",
            ".tmp",
            ".temp",
            ".cache",
            ".bak",
            ".swp",
        ]
    )

    # AI Analysis Configuration
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.1
    AI_TOP_P: float = 1.0
    AI_FREQUENCY_PENALTY: float = 0.0
    AI_PRESENCE_PENALTY: float = 0.0

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Output Configuration
    DEFAULT_OUTPUT_FILE: str = "cold_run_analysis.json"
    INCLUDE_FILE_CONTENTS: bool = False
    MAX_FILES_TO_ANALYZE: int = 1000

    # Language Detection Configuration
    ENABLE_AI_LANGUAGE_DETECTION: bool = True
    ENABLE_AI_ARCHITECTURE_DETECTION: bool = True
    ENABLE_AI_FRAMEWORK_DETECTION: bool = True

    # Performance Configuration
    PARALLEL_ANALYSIS: bool = True
    MAX_WORKERS: int = 4
    ANALYSIS_TIMEOUT_SECONDS: int = 300

    def validate_config(self) -> List[str]:
        """Validate configuration settings and return list of errors."""
        errors = []

        # Check required AI settings
        if not self.AZURE_OPENAI_API_KEY:
            errors.append("AZURE_OPENAI_API_KEY is required for AI analysis")

        if not self.AZURE_OPENAI_ENDPOINT:
            errors.append("AZURE_OPENAI_ENDPOINT is required for AI analysis")

        # Validate numeric values
        if self.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")

        if self.AI_MAX_TOKENS <= 0:
            errors.append("AI_MAX_TOKENS must be positive")

        if not 0 <= self.AI_TEMPERATURE <= 2:
            errors.append("AI_TEMPERATURE must be between 0 and 2")

        if not 0 <= self.AI_TOP_P <= 1:
            errors.append("AI_TOP_P must be between 0 and 1")

        if not -2 <= self.AI_FREQUENCY_PENALTY <= 2:
            errors.append("AI_FREQUENCY_PENALTY must be between -2 and 2")

        if not -2 <= self.AI_PRESENCE_PENALTY <= 2:
            errors.append("AI_PRESENCE_PENALTY must be between -2 and 2")

        if self.MAX_WORKERS <= 0:
            errors.append("MAX_WORKERS must be positive")

        if self.ANALYSIS_TIMEOUT_SECONDS <= 0:
            errors.append("ANALYSIS_TIMEOUT_SECONDS must be positive")

        return errors

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration as a dictionary."""
        return {
            "api_key": self.AZURE_OPENAI_API_KEY,
            "azure_endpoint": self.AZURE_OPENAI_ENDPOINT,
            "api_version": self.AZURE_OPENAI_API_VERSION,
            "deployment_name": self.AZURE_OPENAI_DEPLOYMENT_NAME,
            "max_tokens": self.AI_MAX_TOKENS,
            "temperature": self.AI_TEMPERATURE,
            "top_p": self.AI_TOP_P,
            "frequency_penalty": self.AI_FREQUENCY_PENALTY,
            "presence_penalty": self.AI_PRESENCE_PENALTY,
        }

    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration as a dictionary."""
        return {
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "ignored_directories": self.IGNORED_DIRECTORIES,
            "ignored_extensions": self.IGNORED_EXTENSIONS,
            "max_files_to_analyze": self.MAX_FILES_TO_ANALYZE,
            "parallel_analysis": self.PARALLEL_ANALYSIS,
            "max_workers": self.MAX_WORKERS,
            "timeout_seconds": self.ANALYSIS_TIMEOUT_SECONDS,
        }

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration as a dictionary."""
        return {
            "default_output_file": self.DEFAULT_OUTPUT_FILE,
            "include_file_contents": self.INCLUDE_FILE_CONTENTS,
            "log_level": self.LOG_LEVEL,
            "log_format": self.LOG_FORMAT,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "ai_config": self.get_ai_config(),
            "analysis_config": self.get_analysis_config(),
            "output_config": self.get_output_config(),
            "language_detection": {
                "enable_ai_language_detection": self.ENABLE_AI_LANGUAGE_DETECTION,
                "enable_ai_architecture_detection": self.ENABLE_AI_ARCHITECTURE_DETECTION,
                "enable_ai_framework_detection": self.ENABLE_AI_FRAMEWORK_DETECTION,
            },
        }

    def save_to_file(self, file_path: Path) -> None:
        """Save configuration to a JSON file."""
        import json

        config_dict = self.to_dict()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "ColdRunConfig":
        """Load configuration from a JSON file."""
        import json

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)

        # Create new instance and update from file
        config = cls()

        # Update AI config
        if "ai_config" in config_dict:
            ai_config = config_dict["ai_config"]
            config.AZURE_OPENAI_API_KEY = ai_config.get("api_key", config.AZURE_OPENAI_API_KEY)
            config.AZURE_OPENAI_ENDPOINT = ai_config.get(
                "azure_endpoint", config.AZURE_OPENAI_ENDPOINT
            )
            config.AZURE_OPENAI_API_VERSION = ai_config.get(
                "api_version", config.AZURE_OPENAI_API_VERSION
            )
            config.AZURE_OPENAI_DEPLOYMENT_NAME = ai_config.get(
                "deployment_name", config.AZURE_OPENAI_DEPLOYMENT_NAME
            )
            config.AI_MAX_TOKENS = ai_config.get("max_tokens", config.AI_MAX_TOKENS)
            config.AI_TEMPERATURE = ai_config.get("temperature", config.AI_TEMPERATURE)
            config.AI_TOP_P = ai_config.get("top_p", config.AI_TOP_P)
            config.AI_FREQUENCY_PENALTY = ai_config.get(
                "frequency_penalty", config.AI_FREQUENCY_PENALTY
            )
            config.AI_PRESENCE_PENALTY = ai_config.get(
                "presence_penalty", config.AI_PRESENCE_PENALTY
            )

        # Update analysis config
        if "analysis_config" in config_dict:
            analysis_config = config_dict["analysis_config"]
            config.MAX_FILE_SIZE_MB = analysis_config.get(
                "max_file_size_mb", config.MAX_FILE_SIZE_MB
            )
            config.IGNORED_DIRECTORIES = analysis_config.get(
                "ignored_directories", config.IGNORED_DIRECTORIES
            )
            config.IGNORED_EXTENSIONS = analysis_config.get(
                "ignored_extensions", config.IGNORED_EXTENSIONS
            )
            config.MAX_FILES_TO_ANALYZE = analysis_config.get(
                "max_files_to_analyze", config.MAX_FILES_TO_ANALYZE
            )
            config.PARALLEL_ANALYSIS = analysis_config.get(
                "parallel_analysis", config.PARALLEL_ANALYSIS
            )
            config.MAX_WORKERS = analysis_config.get("max_workers", config.MAX_WORKERS)
            config.ANALYSIS_TIMEOUT_SECONDS = analysis_config.get(
                "timeout_seconds", config.ANALYSIS_TIMEOUT_SECONDS
            )

        # Update output config
        if "output_config" in config_dict:
            output_config = config_dict["output_config"]
            config.DEFAULT_OUTPUT_FILE = output_config.get(
                "default_output_file", config.DEFAULT_OUTPUT_FILE
            )
            config.INCLUDE_FILE_CONTENTS = output_config.get(
                "include_file_contents", config.INCLUDE_FILE_CONTENTS
            )
            config.LOG_LEVEL = output_config.get("log_level", config.LOG_LEVEL)
            config.LOG_FORMAT = output_config.get("log_format", config.LOG_FORMAT)

        # Update language detection config
        if "language_detection" in config_dict:
            lang_config = config_dict["language_detection"]
            config.ENABLE_AI_LANGUAGE_DETECTION = lang_config.get(
                "enable_ai_language_detection", config.ENABLE_AI_LANGUAGE_DETECTION
            )
            config.ENABLE_AI_ARCHITECTURE_DETECTION = lang_config.get(
                "enable_ai_architecture_detection", config.ENABLE_AI_ARCHITECTURE_DETECTION
            )
            config.ENABLE_AI_FRAMEWORK_DETECTION = lang_config.get(
                "enable_ai_framework_detection", config.ENABLE_AI_FRAMEWORK_DETECTION
            )

        return config


# Default configuration instance
config = ColdRunConfig()


def get_config() -> ColdRunConfig:
    """Get the default configuration instance."""
    return config


def create_custom_config(**kwargs) -> ColdRunConfig:
    """Create a custom configuration with overridden values."""
    config = ColdRunConfig()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
