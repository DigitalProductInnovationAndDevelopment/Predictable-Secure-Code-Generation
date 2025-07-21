"""
Configuration settings for the metadata generator.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for metadata generation settings."""

    # File patterns to include/exclude
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "__pycache__/*",
            "*.pyc",
            ".git/*",
            ".pytest_cache/*",
            "htmlcov/*",
            ".coverage*",
            "build/*",
            "dist/*",
            "*.egg-info/*",
            ".venv/*",
            "venv/*",
        ]
    )

    # Entry point detection settings
    entry_point_functions: List[str] = field(
        default_factory=lambda: ["main", "__main__", "run", "start", "execute"]
    )
    entry_point_files: List[str] = field(
        default_factory=lambda: [
            "main.py",
            "app.py",
            "run.py",
            "start.py",
            "__main__.py",
        ]
    )

    # Analysis settings
    extract_docstrings: bool = True
    extract_type_hints: bool = True
    extract_decorators: bool = True
    extract_base_classes: bool = True
    include_private_methods: bool = False
    include_magic_methods: bool = True

    # Output settings
    output_filename: str = "metadata.json"
    indent_json: int = 2
    sort_keys: bool = True

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def validate(self) -> List[str]:
        """
        Validate configuration settings.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.include_patterns:
            errors.append("At least one include pattern must be specified")

        if self.indent_json < 0:
            errors.append("JSON indent must be non-negative")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Invalid log level specified")

        return errors

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """
        Create Config instance from dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Config instance
        """
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Config instance to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
