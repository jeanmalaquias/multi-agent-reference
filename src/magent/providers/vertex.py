"""Google Vertex AI provider adapter (ADR-003).

Claude on Vertex speaks the same Messages API through ``AsyncAnthropicVertex``.
Install the ``providers`` extra (which pulls ``anthropic[vertex]``) to use it;
region and project are read from the environment by the SDK.
"""

from __future__ import annotations

from ._anthropic_base import DEFAULT_MAX_TOKENS, AnthropicMessagesProvider

DEFAULT_MODEL = "claude-opus-4-8"


class VertexProvider(AnthropicMessagesProvider):
    """Adapter over ``anthropic.AsyncAnthropicVertex``."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: object | None = None,
    ) -> None:
        if client is None:  # pragma: no cover - requires the SDK + GCP creds
            from anthropic import AsyncAnthropicVertex

            client = AsyncAnthropicVertex()
        super().__init__(
            name="vertex", model=model, max_tokens=max_tokens, client=client
        )
