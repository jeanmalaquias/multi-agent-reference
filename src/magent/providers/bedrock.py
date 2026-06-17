"""AWS Bedrock provider adapter (ADR-003).

Claude on Bedrock speaks the same Messages API through ``AsyncAnthropicBedrock``;
only the client and the ``anthropic.``-prefixed model ID differ. Install the
``providers`` extra (which pulls ``anthropic[bedrock]``) to use it.
"""

from __future__ import annotations

from ._anthropic_base import DEFAULT_MAX_TOKENS, AnthropicMessagesProvider

DEFAULT_MODEL = "anthropic.claude-opus-4-8"


class BedrockProvider(AnthropicMessagesProvider):
    """Adapter over ``anthropic.AsyncAnthropicBedrock``."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: object | None = None,
    ) -> None:
        if client is None:  # pragma: no cover - requires the SDK + AWS creds
            from anthropic import AsyncAnthropicBedrock

            client = AsyncAnthropicBedrock()
        super().__init__(
            name="bedrock", model=model, max_tokens=max_tokens, client=client
        )
