"""Shared base for Anthropic-Messages-API providers (ADR-003).

Anthropic direct, AWS Bedrock, and Google Vertex all speak the same Messages
API through the ``anthropic`` SDK family (``AsyncAnthropic``,
``AsyncAnthropicBedrock``, ``AsyncAnthropicVertex``). This base holds the
message mapping and call logic; each concrete adapter only supplies its client,
default model, and name.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from .base import Completion, Message, Usage

DEFAULT_MAX_TOKENS = 16000


class AnthropicMessagesProvider:
    """Maps the provider-neutral interface onto the Anthropic Messages API."""

    def __init__(
        self, *, name: str, model: str, max_tokens: int, client: object
    ) -> None:
        self.name = name
        self.model = model
        self.max_tokens = max_tokens
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
