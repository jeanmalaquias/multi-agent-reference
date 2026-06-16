"""Anthropic provider adapter (ADR-003).

Implements the ``LLMProvider`` interface against the official ``anthropic`` SDK.
The SDK is imported lazily so the base package installs without it; install the
``providers`` extra to use this adapter. The Anthropic API takes the system
prompt separately from the message list, so we split it out here.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from .base import Completion, Message, Usage

# Default to the latest, most capable model unless overridden via config.
DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 16000


class AnthropicProvider:
    """Adapter over ``anthropic.AsyncAnthropic``."""

    name = "anthropic"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: object | None = None,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        # Lazy import: only construct a real client when one isn't injected.
        if client is None:  # pragma: no cover - requires the SDK + credentials
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic()
        self._client = client

    @staticmethod
    def _split(messages: list[Message]) -> tuple[str, list[dict]]:
        system = "\n".join(m.content for m in messages if m.role == "system")
        turns = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]
        return system, turns

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        system, turns = self._split(messages)
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=turns,
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        return Completion(
            text=text,
            model=response.model,
            provider=self.name,
            usage=Usage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
            ),
        )

    async def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        system, turns = self._split(messages)
        async with self._client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=turns,
        ) as stream:
            async for text in stream.text_stream:
                yield text
