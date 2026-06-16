"""OpenTelemetry tracing for LLM calls.

Every provider call emits a span carrying the provider, model, and token usage
(a design requirement). Spans export to whatever OTLP collector / Langfuse
backend is configured; tests attach an in-memory exporter.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter

from ..providers.base import Completion, LLMProvider, Message

_TRACER_NAME = "magent.providers"


def configure_tracing(exporter: SpanExporter) -> TracerProvider:
    """Register an exporter for provider spans.

    The OpenTelemetry global tracer provider can only be set once, so if one is
    already installed we attach the exporter to it rather than replacing it.
    """
    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        provider = current
    else:
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider


def get_tracer() -> trace.Tracer:
    """Return the tracer used for provider spans."""
    return trace.get_tracer(_TRACER_NAME)


class TracedProvider:
    """Wraps an ``LLMProvider`` and emits an OpenTelemetry span per call."""

    def __init__(self, inner: LLMProvider) -> None:
        self._inner = inner

    @property
    def name(self) -> str:
        return self._inner.name

    async def complete(self, messages: list[Message], **opts: object) -> Completion:
        with get_tracer().start_as_current_span("llm.complete") as span:
            span.set_attribute("llm.provider", self._inner.name)
            completion = await self._inner.complete(messages, **opts)
            usage = completion.usage
            span.set_attribute("llm.model", completion.model)
            span.set_attribute("llm.usage.prompt_tokens", usage.prompt_tokens)
            span.set_attribute("llm.usage.completion_tokens", usage.completion_tokens)
            span.set_attribute("llm.usage.total_tokens", usage.total_tokens)
            return completion

    async def stream(
        self, messages: list[Message], **opts: object
    ) -> AsyncIterator[str]:
        with get_tracer().start_as_current_span("llm.stream") as span:
            span.set_attribute("llm.provider", self._inner.name)
            async for token in self._inner.stream(messages, **opts):
                yield token
