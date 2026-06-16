from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from magent.observability import TracedProvider, configure_tracing
from magent.providers import Message
from magent.providers.mock import MockProvider


async def test_traced_provider_emits_span_with_usage():
    exporter = InMemorySpanExporter()
    configure_tracing(exporter)

    provider = TracedProvider(MockProvider())
    assert provider.name == "mock"
    await provider.complete(
        [Message(role="system", content="You are the Planner."),
         Message(role="user", content="a goal")]
    )

    spans = exporter.get_finished_spans()
    assert any(s.name == "llm.complete" for s in spans)
    span = next(s for s in spans if s.name == "llm.complete")
    assert span.attributes["llm.provider"] == "mock"
    assert span.attributes["llm.usage.total_tokens"] > 0


async def test_traced_provider_streams_tokens():
    exporter = InMemorySpanExporter()
    configure_tracing(exporter)

    provider = TracedProvider(MockProvider())
    tokens = [
        t async for t in provider.stream([Message(role="user", content="hi")])
    ]
    assert tokens
    assert any(s.name == "llm.stream" for s in exporter.get_finished_spans())
