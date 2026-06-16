"""Guardrail orchestrator and the provider wrapper that enforces it.

Every LLM call is wrapped so that inputs are moderated before the call and
outputs after it (a hard requirement from the design). The orchestrator runs
each configured backend and denies on the first block.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from ..providers.base import Completion, LLMProvider, Message
from .base import Guardrail, Stage, Verdict
from .heuristic import HeuristicGuard


class GuardrailError(RuntimeError):
    """Raised when a guardrail blocks an input or output."""

    def __init__(self, verdict: Verdict, stage: Stage) -> None:
        self.verdict = verdict
        self.stage = stage
        super().__init__(
            f"{stage} blocked by guardrail "
            f"({verdict.category}): {verdict.reason}"
        )


class GuardrailOrchestrator:
    """Runs a chain of guardrail backends; denies on the first block."""

    def __init__(self, backends: list[Guardrail]) -> None:
        self._backends = backends

    def evaluate(self, text: str, stage: Stage) -> Verdict:
        for backend in self._backends:
            verdict = backend.check(text, stage)
            if not verdict.allowed:
                return verdict
        return Verdict(allowed=True)


def default_orchestrator() -> GuardrailOrchestrator:
    """The default orchestrator used by the runtime (heuristic backend)."""
    return GuardrailOrchestrator([HeuristicGuard()])


class GuardedProvider:
    """Wraps an ``LLMProvider`` with pre- and post-call moderation."""

    def __init__(
        self, inner: LLMProvider, orchestrator: GuardrailOrchestrator
    ) -> None:
        self._inner = inner
        self._guard = orchestrator

    @property
    def name(self) -> str:
        return self._inner.name

    def _check(self, text: str, stage: Stage) -> None:
        verdict = self._guard.evaluate(text, stage)
        if not verdict.allowed:
            raise GuardrailError(verdict, stage)

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        for message in messages:
            if message.role == "user":
                self._check(message.content, "input")
        completion = await self._inner.complete(messages, **opts)
        self._check(completion.text, "output")
        return completion

    async def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        for message in messages:
            if message.role == "user":
                self._check(message.content, "input")
        async for token in self._inner.stream(messages, **opts):
            yield token
