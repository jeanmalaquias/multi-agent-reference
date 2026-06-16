"""Provider-agnostic LLM interface (ADR-003).

No vendor SDK is imported outside this package. Agents depend only on the
``LLMProvider`` protocol and the ``Message`` / ``Completion`` value types.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    """A single chat message in provider-neutral form."""

    role: Role
    content: str


class Usage(BaseModel):
    """Token accounting for one completion."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class Completion(BaseModel):
    """The normalized result of an LLM call."""

    text: str
    model: str
    provider: str
    usage: Usage = Usage()


@runtime_checkable
class LLMProvider(Protocol):
    """Every provider adapter normalizes its vendor SDK to this interface."""

    name: str

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        """Return a single completion for the given messages."""
        ...

    def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        """Yield output tokens incrementally."""
        ...
