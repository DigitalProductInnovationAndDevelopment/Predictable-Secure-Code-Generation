"""Provider registry for dynamic discovery and registration."""

from typing import Dict, List, Type, TypeVar, Generic, Optional
from platform.ports.providers import CodeGenProvider, MetadataProvider, SyntaxValidator
from platform.kernel.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class ProviderRegistry(Generic[T]):
    """Generic registry for providers."""

    def __init__(self, provider_type: str):
        self._providers: Dict[str, T] = {}
        self._provider_type = provider_type

    def register(self, language: str, provider: T) -> None:
        """Register a provider for a language."""
        self._providers[language] = provider
        logger.info(
            f"Registered {self._provider_type}",
            language=language,
            provider=provider.__class__.__name__,
        )

    def get(self, language: str) -> Optional[T]:
        """Get a provider for a language."""
        return self._providers.get(language)

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._providers.keys())

    def has_provider(self, language: str) -> bool:
        """Check if a provider exists for a language."""
        return language in self._providers


class MasterRegistry:
    """Central registry for all provider types."""

    def __init__(self):
        self.codegen = ProviderRegistry[CodeGenProvider]("CodeGenProvider")
        self.metadata = ProviderRegistry[MetadataProvider]("MetadataProvider")
        self.syntax = ProviderRegistry[SyntaxValidator]("SyntaxValidator")

    def register_language_providers(
        self,
        language: str,
        codegen_provider: Optional[CodeGenProvider] = None,
        metadata_provider: Optional[MetadataProvider] = None,
        syntax_provider: Optional[SyntaxValidator] = None,
    ) -> None:
        """Register all providers for a language at once."""
        if codegen_provider:
            self.codegen.register(language, codegen_provider)
        if metadata_provider:
            self.metadata.register(language, metadata_provider)
        if syntax_provider:
            self.syntax.register(language, syntax_provider)

    def get_supported_languages(self) -> List[str]:
        """Get all languages that have at least one provider."""
        all_languages = set()
        all_languages.update(self.codegen.get_supported_languages())
        all_languages.update(self.metadata.get_supported_languages())
        all_languages.update(self.syntax.get_supported_languages())
        return sorted(list(all_languages))

    def validate_language_support(self, language: str, require_all: bool = False) -> bool:
        """Check if a language has adequate provider support."""
        has_codegen = self.codegen.has_provider(language)
        has_metadata = self.metadata.has_provider(language)
        has_syntax = self.syntax.has_provider(language)

        if require_all:
            return has_codegen and has_metadata and has_syntax
        else:
            return has_codegen or has_metadata or has_syntax


# Global registry instance
registry = MasterRegistry()
