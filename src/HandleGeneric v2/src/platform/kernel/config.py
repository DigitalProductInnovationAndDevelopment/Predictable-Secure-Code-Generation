"""Configuration management using Pydantic Settings."""

from typing import Set, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main configuration for the platform."""

    # AI Configuration
    llm_backend: str = Field(default="openai", description="LLM backend: openai | azure")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_deployment: str = Field(
        default="gpt-4", description="Azure OpenAI deployment name"
    )

    # Model Configuration
    model: str = Field(default="gpt-4", description="Default model to use")
    temperature: float = Field(default=0.0, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    request_timeout: int = Field(default=60, description="Request timeout in seconds")

    # Cost & Safety Controls
    max_requests_per_hour: int = Field(default=100, description="Max requests per hour")
    max_tokens_per_day: int = Field(default=50000, description="Max tokens per day")
    dry_run: bool = Field(default=False, description="Enable dry run mode")

    # File Processing
    max_file_size_mb: int = Field(default=10, description="Max file size in MB")
    ignored_directories: Set[str] = Field(
        default={".git", "node_modules", "dist", "__pycache__", ".venv", "venv"},
        description="Directories to ignore",
    )

    # Test Configuration
    test_timeout: int = Field(default=300, description="Test timeout in seconds")
    enable_sandbox: bool = Field(default=True, description="Enable sandbox execution")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format: json | text")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    def get_openai_config(self) -> dict:
        """Get OpenAI configuration."""
        if self.llm_backend == "azure":
            return {
                "azure_endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "api_version": "2023-12-01-preview",
                "azure_deployment": self.azure_openai_deployment,
            }
        else:
            return {
                "api_key": self.openai_api_key,
            }


# Global config instance
config = Config()
