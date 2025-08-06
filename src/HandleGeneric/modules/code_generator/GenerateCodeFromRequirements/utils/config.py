"""
Configuration management for code generation system.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


@dataclass
class GenerationConfig:
    """Configuration for code generation process."""

    # AI Configuration
    use_ai: bool = True
    ai_max_tokens: int = 2000
    ai_temperature: float = 0.3
    ai_timeout: int = 30

    # Code Generation Settings
    max_file_size: int = 10000  # Maximum lines per generated file
    include_docstrings: bool = True
    include_type_hints: bool = True
    include_error_handling: bool = True
    follow_pep8: bool = True

    # Test Generation Settings
    generate_tests: bool = True
    test_coverage_threshold: float = 0.8
    include_edge_cases: bool = True
    include_error_tests: bool = True

    # Integration Settings
    backup_original: bool = True
    validate_syntax: bool = True
    run_tests_after_generation: bool = True
    update_metadata: bool = True

    # File Patterns
    exclude_patterns: List[str] = None
    include_patterns: List[str] = None

    # Output Settings
    output_format: str = "json"  # json, yaml, text
    verbose_logging: bool = False
    save_intermediate_results: bool = True

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "__pycache__/*",
                "*.pyc",
                ".git/*",
                ".pytest_cache/*",
                "htmlcov/*",
                "*.egg-info/*",
                ".venv/*",
                "venv/*",
            ]

        if self.include_patterns is None:
            self.include_patterns = ["*.py"]

    @classmethod
    def load_from_file(cls, config_path: str) -> "GenerationConfig":
        """Load configuration from a JSON file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Create config object with loaded data
            config = cls()
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            return config

        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {str(e)}")
            return cls()  # Return default config

    def save_to_file(self, config_path: str) -> bool:
        """Save configuration to a JSON file."""
        try:
            config_dict = asdict(self)

            # Create directory if it doesn't exist
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2)

            return True

        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {str(e)}")
            return False

    def validate(self) -> List[str]:
        """Validate configuration settings and return list of errors."""
        errors = []

        # Validate AI settings
        if self.ai_max_tokens < 100 or self.ai_max_tokens > 8000:
            errors.append("ai_max_tokens must be between 100 and 8000")

        if self.ai_temperature < 0.0 or self.ai_temperature > 2.0:
            errors.append("ai_temperature must be between 0.0 and 2.0")

        if self.ai_timeout < 5 or self.ai_timeout > 300:
            errors.append("ai_timeout must be between 5 and 300 seconds")

        # Validate file settings
        if self.max_file_size < 100:
            errors.append("max_file_size must be at least 100 lines")

        # Validate test settings
        if self.test_coverage_threshold < 0.0 or self.test_coverage_threshold > 1.0:
            errors.append("test_coverage_threshold must be between 0.0 and 1.0")

        # Validate output format
        valid_formats = ["json", "yaml", "text"]
        if self.output_format not in valid_formats:
            errors.append(f"output_format must be one of: {', '.join(valid_formats)}")

        return errors

    def get_logging_level(self) -> int:
        """Get appropriate logging level based on verbose setting."""
        return logging.DEBUG if self.verbose_logging else logging.INFO

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded based on patterns."""
        from fnmatch import fnmatch

        for pattern in self.exclude_patterns:
            if fnmatch(file_path, pattern):
                return True
        return False

    def should_include_file(self, file_path: str) -> bool:
        """Check if a file should be included based on patterns."""
        from fnmatch import fnmatch

        # If file is excluded, don't include it
        if self.should_exclude_file(file_path):
            return False

        # Check include patterns
        for pattern in self.include_patterns:
            if fnmatch(file_path, pattern):
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_summary(self) -> str:
        """Get a human-readable summary of the configuration."""
        summary_lines = [
            "Code Generation Configuration:",
            f"  AI Integration: {'Enabled' if self.use_ai else 'Disabled'}",
            f"  Max Tokens: {self.ai_max_tokens}",
            f"  Temperature: {self.ai_temperature}",
            "",
            "Code Settings:",
            f"  Include Docstrings: {'Yes' if self.include_docstrings else 'No'}",
            f"  Include Type Hints: {'Yes' if self.include_type_hints else 'No'}",
            f"  Include Error Handling: {'Yes' if self.include_error_handling else 'No'}",
            f"  Follow PEP8: {'Yes' if self.follow_pep8 else 'No'}",
            "",
            "Test Settings:",
            f"  Generate Tests: {'Yes' if self.generate_tests else 'No'}",
            f"  Coverage Threshold: {self.test_coverage_threshold:.1%}",
            f"  Include Edge Cases: {'Yes' if self.include_edge_cases else 'No'}",
            "",
            "Integration:",
            f"  Backup Original: {'Yes' if self.backup_original else 'No'}",
            f"  Validate Syntax: {'Yes' if self.validate_syntax else 'No'}",
            f"  Run Tests: {'Yes' if self.run_tests_after_generation else 'No'}",
            f"  Update Metadata: {'Yes' if self.update_metadata else 'No'}",
            "",
            f"Output Format: {self.output_format}",
            f"Verbose Logging: {'Yes' if self.verbose_logging else 'No'}",
        ]

        return "\n".join(summary_lines)
