"""Anthropic (direct API) provider adapter (ADR-003).

Uses the official ``anthropic`` SDK. The SDK is imported lazily so the base
package installs without it; install the ``providers`` extra to use it.
"""

from __future__ import annotations

from ._anthropic_base import DEFAULT_MAX_TOKENS, AnthropicMessagesProvider

# Default to the latest, most capable model unless overridden via config.
DEFAULT_MODEL = "claude-opus-4-8"


class AnthropicProvider(AnthropicMessagesProvider):
    """Adapter over ``anthropic.AsyncAnthropic``."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: object | None = None,
    ) -> None:
        if client is None:  # pragma: no cover - requires the SDK + credentials
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic()
        super().__init__(
            name="anthropic", model=model, max_tokens=max_tokens, client=client
        )
