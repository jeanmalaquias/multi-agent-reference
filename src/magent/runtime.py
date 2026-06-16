"""Provider resolution for agents.

Centralizes the cross-cutting wrapping so every agent's LLM calls are uniformly
guarded and traced: config selects the raw provider, which is then wrapped with
the guardrail orchestrator and an OpenTelemetry span emitter.
"""

from __future__ import annotations

from .config import get_settings
from .guardrails import GuardedProvider, default_orchestrator
from .observability import TracedProvider
from .providers import LLMProvider, get_provider


def resolve_provider(agent: str) -> LLMProvider:
    """Return the fully-wrapped provider for an agent role."""
    raw = get_provider(get_settings().provider_for(agent))
    guarded = GuardedProvider(raw, default_orchestrator())
    return TracedProvider(guarded)
