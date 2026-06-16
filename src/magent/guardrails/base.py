"""Guardrail interfaces and value types.

A guardrail backend inspects text (an LLM input or output) and returns a
``Verdict``. The orchestrator composes several backends; concrete cloud backends
(Llama Guard 3, Azure AI Content Safety, Bedrock Guardrails) implement the same
``Guardrail`` protocol.
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel

Stage = Literal["input", "output"]


class Verdict(BaseModel):
    """The result of a single guardrail check."""

    allowed: bool
    category: str | None = None
    reason: str = ""


@runtime_checkable
class Guardrail(Protocol):
    """A moderation backend."""

    name: str

    def check(self, text: str, stage: Stage) -> Verdict:
        """Inspect text for a given stage and return a verdict."""
        ...
