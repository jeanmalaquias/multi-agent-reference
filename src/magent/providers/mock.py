"""Deterministic mock provider.

Lets the whole pipeline run end-to-end offline (no API keys, no network) so the
vertical slice and CI are fast and reproducible. Real adapters (Anthropic,
Bedrock, Foundry, Vertex) implement the same ``LLMProvider`` interface.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from .base import Completion, Message, Usage


class MockProvider:
    """Returns canned, role-aware responses keyed off the system prompt."""

    name = "mock"

    def __init__(self, model: str = "mock-1") -> None:
        self.model = model

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        system = next((m.content for m in messages if m.role == "system"), "")
        user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        text = self._respond(system, user)
        return Completion(
            text=text,
            model=self.model,
            provider=self.name,
            usage=Usage(
                prompt_tokens=sum(len(m.content.split()) for m in messages),
                completion_tokens=len(text.split()),
            ),
        )

    async def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        completion = await self.complete(messages, **opts)
        for token in completion.text.split():
            yield token + " "

    @staticmethod
    def _respond(system: str, user: str) -> str:
        s = system.lower()
        if "planner" in s:
            return "1. Research the topic\n2. Draft the artifact\n3. Review quality"
        if "researcher" in s:
            return f"Finding: relevant evidence for '{user[:40]}'."
        if "writer" in s:
            return f"# Artifact\n\nA concise response addressing: {user[:60]}."
        if "critic" in s:
            return "APPROVE score=0.9 The draft satisfies the acceptance criteria."
        return "ok"
