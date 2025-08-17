"""Domain policies for validation, generation, and processing."""

from typing import List, Set
from pydantic import BaseModel


class ValidationPolicy(BaseModel):
    """Policy for validation behavior."""

    fail_on_syntax_error: bool = True
    fail_on_test_failure: bool = True
    fail_on_ai_contradiction: bool = False
    syntax_timeout_seconds: int = 30
    test_timeout_seconds: int = 300
    ai_check_timeout_seconds: int = 60


class GenerationPolicy(BaseModel):
    """Policy for code generation behavior."""

    max_files_per_generation: int = 50
    max_file_size_kb: int = 100
    auto_format: bool = True
    auto_validate_syntax: bool = True
    auto_generate_tests: bool = False


class CostPolicy(BaseModel):
    """Policy for cost and resource management."""

    max_tokens_per_request: int = 4000
    max_requests_per_hour: int = 100
    max_cost_per_day_usd: float = 50.0
    dry_run_mode: bool = False


class FilePolicy(BaseModel):
    """Policy for file processing."""

    max_file_size_mb: int = 10
    ignored_extensions: Set[str] = {".pyc", ".pyo", ".pyd", ".so", ".dll"}
    ignored_directories: Set[str] = {
        ".git",
        "node_modules",
        "dist",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".env",
        "target",
        "build",
    }
    allowed_languages: Set[str] = {"python", "typescript", "javascript", "java"}


class SecurityPolicy(BaseModel):
    """Policy for security controls."""

    allow_network_requests: bool = False
    allow_file_system_writes: bool = True
    sandbox_execution: bool = True
    max_execution_time_seconds: int = 300
