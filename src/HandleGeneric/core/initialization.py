"""
Language initialization module.

This module initializes and registers all available language providers
with the global language registry.
"""

import logging
from typing import Dict, Any

from .language.registry import register_provider
from ..providers import (
    PythonProvider,
    JavaScriptProvider,
    TypeScriptProvider,
    JavaProvider,
    CSharpProvider,
    CppProvider,
)


def initialize_language_providers() -> Dict[str, Any]:
    """
    Initialize and register all language providers.

    Returns:
        Dictionary with initialization results
    """
    logger = logging.getLogger(__name__)

    providers_to_register = [
        PythonProvider(),
        JavaScriptProvider(),
        TypeScriptProvider(),
        JavaProvider(),
        CSharpProvider(),
        CppProvider(),
    ]

    registered_count = 0
    failed_providers = []

    for provider in providers_to_register:
        try:
            register_provider(provider)
            registered_count += 1
            logger.info(f"Registered {provider.language_name} provider")
        except Exception as e:
            failed_providers.append(
                {"language": provider.language_name, "error": str(e)}
            )
            logger.error(f"Failed to register {provider.language_name} provider: {e}")

    logger.info(
        f"Language initialization complete: {registered_count} providers registered"
    )

    return {
        "registered_count": registered_count,
        "failed_providers": failed_providers,
        "total_attempted": len(providers_to_register),
    }


def get_initialization_status() -> Dict[str, Any]:
    """
    Get the current initialization status.

    Returns:
        Status information about language providers
    """
    from .language.registry import get_global_registry

    registry = get_global_registry()

    return {
        "supported_languages": registry.get_supported_languages(),
        "supported_extensions": list(registry.get_supported_extensions()),
        "providers_info": registry.get_providers_info(),
    }


# Auto-initialize when module is imported
_initialization_result = None


def ensure_initialized() -> Dict[str, Any]:
    """
    Ensure language providers are initialized.

    Returns:
        Initialization result
    """
    global _initialization_result

    if _initialization_result is None:
        _initialization_result = initialize_language_providers()

    return _initialization_result


# Initialize on import
ensure_initialized()
