"""Dependency injection container and service factories."""

from typing import Dict, Any
from platform.kernel.config import config
from platform.kernel.registry import registry
from platform.kernel.logging import setup_logging, get_logger

# Import ports
from platform.ports.ai import LLMClient
from platform.ports.fs import FileSystem, ArtifactWriter
from platform.ports.runners import TestRunner, Sandbox
from platform.ports.observability import Logger, Metrics, Tracer

# Import adapters - gracefully handle missing dependencies
try:
    from platform.adapters.ai.openai_client import OpenAIClient

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from platform.adapters.fs.local_fs import LocalFileSystem
from platform.adapters.fs.artifact_writer import LocalArtifactWriter
from platform.adapters.runners.pytest_runner import PytestRunner
from platform.adapters.runners.sandbox_subprocess import SubprocessSandbox

logger = get_logger(__name__)


class ServiceContainer:
    """Dependency injection container."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all services."""
        if self._initialized:
            return

        setup_logging(config.log_level, config.log_format)
        logger.info("Initializing service container")

        # Core services
        self._services["config"] = config
        self._services["registry"] = registry
        self._services["logger"] = logger

        # AI services
        if HAS_OPENAI:
            self._services["llm_client"] = self._create_llm_client()
        else:
            self._services["llm_client"] = None

        # File system services
        self._services["file_system"] = LocalFileSystem()
        self._services["artifact_writer"] = LocalArtifactWriter()

        # Test runners
        self._services["pytest_runner"] = PytestRunner()

        # Sandbox
        self._services["sandbox"] = SubprocessSandbox()

        # Register providers
        self._register_providers()

        self._initialized = True
        logger.info("Service container initialized")

    def get(self, service_name: str) -> Any:
        """Get a service by name."""
        if not self._initialized:
            self.initialize()
        return self._services.get(service_name)

    def _create_llm_client(self) -> LLMClient:
        """Create LLM client based on configuration."""
        if not HAS_OPENAI:
            raise ImportError("OpenAI client not available - install openai package")

        if config.llm_backend == "azure":
            return OpenAIClient(is_azure=True, **config.get_openai_config())
        else:
            return OpenAIClient(is_azure=False, **config.get_openai_config())

    def _register_providers(self) -> None:
        """Register language providers."""
        # Import and register Python providers
        try:
            from platform.adapters.providers.python.codegen_provider import PythonCodeGenProvider
            from platform.adapters.providers.python.metadata_provider import PythonMetadataProvider
            from platform.adapters.providers.python.syntax_validator import PythonSyntaxValidator

            registry.register_language_providers(
                "python",
                codegen_provider=PythonCodeGenProvider(),
                metadata_provider=PythonMetadataProvider(),
                syntax_provider=PythonSyntaxValidator(),
            )
        except ImportError as e:
            logger.warning("Could not register Python providers", error=str(e))

        # Register TypeScript providers (when available)
        try:
            from platform.adapters.providers.typescript.codegen_provider import (
                TypeScriptCodeGenProvider,
            )
            from platform.adapters.providers.typescript.metadata_provider import (
                TypeScriptMetadataProvider,
            )
            from platform.adapters.providers.typescript.syntax_validator import (
                TypeScriptSyntaxValidator,
            )

            registry.register_language_providers(
                "typescript",
                codegen_provider=TypeScriptCodeGenProvider(),
                metadata_provider=TypeScriptMetadataProvider(),
                syntax_provider=TypeScriptSyntaxValidator(),
            )
        except ImportError:
            logger.debug("TypeScript providers not available")


# Global container instance
container = ServiceContainer()


def get_service(name: str) -> Any:
    """Get a service from the global container."""
    return container.get(name)


class ServiceRegistry:
    """High-level service access."""

    @property
    def config(self):
        return get_service("config")

    @property
    def registry(self):
        return get_service("registry")

    @property
    def llm_client(self) -> LLMClient:
        return get_service("llm_client")

    @property
    def file_system(self) -> FileSystem:
        return get_service("file_system")

    @property
    def artifact_writer(self) -> ArtifactWriter:
        return get_service("artifact_writer")

    @property
    def pytest_runner(self) -> TestRunner:
        return get_service("pytest_runner")

    @property
    def sandbox(self) -> Sandbox:
        return get_service("sandbox")


def build_app() -> ServiceRegistry:
    """Build the application with all dependencies."""
    container.initialize()
    return ServiceRegistry()
