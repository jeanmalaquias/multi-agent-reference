"""Azure AI Foundry provider adapter (ADR-003).

Foundry serves OpenAI-compatible models (gpt-4o, Phi), so this adapter uses the
``openai`` SDK's ``AsyncAzureOpenAI`` and the Chat Completions shape rather than
the Anthropic Messages API. It normalizes that response back to the same
``Completion`` type, proving the abstraction spans dissimilar provider APIs.
Install the ``providers`` extra (which pulls ``openai``) to use it.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from .base import Completion, Message, Usage

DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 16000


class FoundryProvider:
    """Adapter over ``openai.AsyncAzureOpenAI`` (Chat Completions)."""

    name = "foundry"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: object | None = None,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        if client is None:  # pragma: no cover - requires the SDK + Azure creds
            from openai import AsyncAzureOpenAI

            client = AsyncAzureOpenAI()
        self._client = client

    @staticmethod
    def _to_openai(messages: list[Message]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        response = await self._client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self._to_openai(messages),
        )
        usage = response.usage
        return Completion(
            text=response.choices[0].message.content or "",
            model=response.model,
            provider=self.name,
            usage=Usage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            ),
        )

    async def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self._to_openai(messages),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
