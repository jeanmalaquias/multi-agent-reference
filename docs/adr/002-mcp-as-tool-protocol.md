# ADR-002 — Model Context Protocol (MCP) as the tool protocol

- Status: Accepted
- Date: 2026-06-16
- Deciders: Jean Malaquias

## Context

The Researcher agent needs tools (web search, vector retrieval, code search).
We can wire tools as (a) framework-native function-calling bindings, (b) bespoke
HTTP microservices with a custom contract, or (c) **Model Context Protocol
(MCP)** servers.

## Decision

Expose all tools as **MCP servers**, supporting both stdio and HTTP+SSE
transports. The agents consume tools through an MCP client + registry rather
than framework-specific tool wrappers.

## Rationale

- **Portability**: the same MCP servers work with this system, Claude Desktop,
  and any MCP-aware client — tools are not locked to LangGraph.
- **Standardization**: MCP is now cross-vendor (Anthropic-originated, adopted by
  Google and Microsoft tooling), so this is the durable interface.
- **Separation of concerns**: tools become independently deployable, versioned,
  and testable (MCP Inspector) artifacts.
- **Portfolio signal**: production-quality MCP servers are rare and demonstrate
  current agentic fluency.

## Consequences

- A small MCP client + tool registry abstraction is required in `tools/`.
- Each tool ships with input/output schemas and passes MCP Inspector validation.
- HTTP transport requires auth (OAuth2/JWT) — handled at the transport layer.
- Slightly more setup than native function calling, repaid by reuse and testing.
