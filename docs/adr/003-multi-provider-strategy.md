# ADR-003 — Multi-provider abstraction strategy

- Status: Accepted
- Date: 2026-06-16
- Deciders: Jean Malaquias

## Context

The system must run any agent on any of four LLM backends — Azure AI Foundry,
AWS Bedrock, Vertex AI, and the Anthropic API — switchable by configuration, to
prove vendor neutrality and to map onto the platforms our target employers ship.

## Decision

Introduce a single internal interface and a router:

```python
class LLMProvider(Protocol):
    async def complete(self, messages: list[Message], **opts) -> Completion: ...
    async def stream(self, messages: list[Message], **opts) -> AsyncIterator[Token]: ...
```

Concrete adapters (`azure_foundry.py`, `bedrock.py`, `vertex.py`, `anthropic.py`)
normalize each vendor SDK to internal `Message`/`Completion` types. A
`router.py` resolves the per-agent provider from config and returns the adapter.

**Hard rule**: no vendor SDK is imported anywhere outside `providers/`. Agents,
graph, and tools depend only on the `LLMProvider` interface.

## Rationale

- One config flag per agent (`agents.<name>.provider`) changes the backend with
  zero code change elsewhere.
- Cost/latency tuning becomes a config decision (cheap model for Planner/Critic,
  stronger model for Writer).
- Contract tests run the same suite against each adapter to catch response-shape
  drift.

## Consequences

- Some lowest-common-denominator capability loss; provider-specific features go
  behind explicit, opt-in extensions, not the core interface.
- A normalization layer must be maintained as vendor APIs evolve.
- Guardrails and observability wrap the router once, so every provider call is
  uniformly moderated and traced.
