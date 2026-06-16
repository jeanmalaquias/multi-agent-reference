"""Provider router — resolves an agent's configured provider to an adapter.

Adding a real provider is a one-line registry entry; agents never change.
"""

from __future__ import annotations

from .base import LLMProvider
from .mock import MockProvider

# Registry of available provider factories. Real adapters register here as they
# are implemented (anthropic, bedrock, azure_foundry, vertex).
_REGISTRY: dict[str, type] = {
    "mock": MockProvider,
}


def get_provider(name: str) -> LLMProvider:
    """Return a provider adapter by name.

    Raises ``ValueError`` for unknown providers so misconfiguration fails loud.
    """
    try:
        factory = _REGISTRY[name]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown provider '{name}'. Known: {known}") from None
    return factory()


def register_provider(name: str, factory: type) -> None:
    """Register a new provider factory (used by real adapter modules)."""
    _REGISTRY[name] = factory
