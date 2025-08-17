"""Domain-specific errors and exceptions."""


class PlatformError(Exception):
    """Base error for all platform-related errors."""

    pass


class ValidationError(PlatformError):
    """Raised when validation fails."""

    pass


class CodeGenerationError(PlatformError):
    """Raised when code generation fails."""

    pass


class MetadataExtractionError(PlatformError):
    """Raised when metadata extraction fails."""

    pass


class ProviderError(PlatformError):
    """Raised when a provider fails."""

    pass


class ConfigurationError(PlatformError):
    """Raised when configuration is invalid."""

    pass


class AIClientError(PlatformError):
    """Raised when AI client operations fail."""

    pass


class FileSystemError(PlatformError):
    """Raised when file system operations fail."""

    pass


class TestRunnerError(PlatformError):
    """Raised when test execution fails."""

    pass


class SyntaxValidationError(ValidationError):
    """Raised when syntax validation fails."""

    pass


class LogicValidationError(ValidationError):
    """Raised when AI logic validation fails."""

    pass
