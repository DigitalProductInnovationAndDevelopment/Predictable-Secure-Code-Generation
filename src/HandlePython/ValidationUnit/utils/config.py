"""
Configuration management for the validation system.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ValidationConfig:
    """Configuration for the validation system."""

    # General settings
    enable_syntax_validation: bool = True
    enable_test_validation: bool = True
    enable_ai_validation: bool = True
    stop_on_first_failure: bool = False

    # Syntax validation settings
    syntax_check_imports: bool = True
    syntax_check_indentation: bool = True
    syntax_python_version: str = "3.7"

    # Test validation settings
    test_timeout: int = 300  # seconds
    test_patterns: List[str] = field(
        default_factory=lambda: ["test_*.py", "*_test.py", "tests.py"]
    )
    test_directories: List[str] = field(default_factory=lambda: ["tests", "test"])
    required_test_coverage: float = 0.0  # 0-100%
    pytest_args: List[str] = field(default_factory=lambda: ["-v", "--tb=short"])

    # AI validation settings
    ai_validation_prompt_template: str = """
Analyze this Python codebase and validate the logic implementation:

Files and Functions:
{file_functions}

Requirements:
{requirements}

Please check:
1. Does the implementation correctly fulfill each requirement?
2. Are there any logical errors in the algorithms?
3. Are edge cases properly handled?
4. Is error handling appropriate?
5. Are there any security concerns?

Return a JSON response with:
- "valid": boolean
- "problems": list of issues found
- "suggestions": list of improvements
"""

    ai_max_tokens: int = 2000
    ai_temperature: float = 0.1

    # Output settings
    output_format: str = "json"  # json, yaml, text
    save_report: bool = True
    report_filename: str = "validation_report.json"

    # Logging settings
    log_level: str = "INFO"
    verbose_output: bool = False

    def validate(self) -> List[str]:
        """Validate configuration settings."""
        errors = []

        if self.test_timeout <= 0:
            errors.append("Test timeout must be positive")

        if self.required_test_coverage < 0 or self.required_test_coverage > 100:
            errors.append("Test coverage must be between 0 and 100")

        if self.ai_max_tokens <= 0:
            errors.append("AI max tokens must be positive")

        if self.ai_temperature < 0 or self.ai_temperature > 2:
            errors.append("AI temperature must be between 0 and 2")

        if self.output_format not in ["json", "yaml", "text"]:
            errors.append("Output format must be json, yaml, or text")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Invalid log level")

        return errors

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ValidationConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    @classmethod
    def from_file(cls, config_path: str) -> "ValidationConfig":
        """Load configuration from file."""
        import json

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(".json"):
                config_dict = json.load(f)
            elif config_path.endswith((".yml", ".yaml")):
                try:
                    import yaml

                    config_dict = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML config files")
            else:
                raise ValueError("Config file must be JSON or YAML")

        return cls.from_dict(config_dict)

    def save_to_file(self, config_path: str):
        """Save configuration to file."""
        import json

        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            if config_path.endswith(".json"):
                json.dump(self.to_dict(), f, indent=2)
            elif config_path.endswith((".yml", ".yaml")):
                try:
                    import yaml

                    yaml.dump(self.to_dict(), f, default_flow_style=False)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML config files")
            else:
                raise ValueError("Config file must be JSON or YAML")
