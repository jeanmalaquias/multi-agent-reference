# Multi-Agent Reference Architecture

> A production-grade, **provider-agnostic** multi-agent system: Planner →
> Researcher → Writer → Critic, with MCP tools, first-class observability,
> guardrails, and evaluation gating. Built as a reference for how agentic AI
> looks in production — not a demo.

<!-- Badges placeholder: CI, eval-gate, license, coverage -->

---

## Why this exists

Most agent demos stop at a single happy path with one provider and no
observability, safety, or evaluation. The hard parts of production agents —
vendor neutrality, tracing every LLM call, moderating inputs and outputs, and
gating releases on quality — are exactly what this repo demonstrates.

## Highlights

- **4-agent pipeline** with conditional routing (the Critic can send work back
  to the Planner) on **LangGraph**, with typed state and durable checkpoints.
- **Switch LLM provider per agent with one config flag** — Azure AI Foundry,
  AWS Bedrock, Vertex AI, or Anthropic. No vendor SDK leaks outside `providers/`.
- **Tools as MCP servers** (stdio + HTTP/SSE): `web_search`,
  `vector_retrieval`, `code_search`.
- **Guardrails on every LLM call** (pre + post): Llama Guard 3 + cloud content
  safety.
- **OpenTelemetry trace** of every run and every LLM call → Langfuse, with token
  usage and cost on each span.
- **Eval gate in CI**: Ragas + LLM-as-Judge over a versioned golden set; a > 5%
  regression fails the build.

## Architecture

```mermaid
flowchart LR
    START([goal]) --> P[Planner]
    P -->|subtasks| R[Researcher]
    R <-->|MCP tools| TOOLS[(web / vector / code)]
    R -->|findings| W[Writer]
    W -->|draft| C[Critic]
    C -->|approved| DONE([artifact])
    C -->|revise| P
```

Full design and decisions:

- [Architecture](docs/architecture.md)
- [ADR-001 — LangGraph vs AutoGen](docs/adr/001-langgraph-vs-autogen.md)
- [ADR-002 — MCP as the tool protocol](docs/adr/002-mcp-as-tool-protocol.md)
- [ADR-003 — Multi-provider strategy](docs/adr/003-multi-provider-strategy.md)

## Tech stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Orchestration | LangGraph |
| Tool protocol | Model Context Protocol (MCP) |
| Providers | Azure AI Foundry · AWS Bedrock · Vertex AI · Anthropic |
| Retrieval | pgvector (+ hybrid search) |
| Memory | Redis (short-term) + PostgreSQL/pgvector (long-term) |
| Observability | OpenTelemetry + Langfuse |
| Guardrails | Llama Guard 3 + cloud content safety |
| Evaluation | Ragas + LLM-as-Judge |
| API | FastAPI + Pydantic v2 |
| Deploy | Docker · Helm · Bicep (Azure) · Terraform (AWS) |
| CI | GitHub Actions (lint, tests, eval gate) |

## Quick start

> Status: scaffolding in progress. Commands below are the target interface.

```bash
# 1. Bring up dependencies (Redis, Postgres/pgvector, Langfuse)
docker compose up -d

# 2. Install
pip install -e ".[dev]"

# 3. Configure providers (copy and fill secrets)
cp .env.example .env

# 4. Run a goal through the pipeline
python -m magent.cli run "Write a one-page brief on X"

# 5. (Optional) run the tools as a standalone MCP server (stdio)
pip install -e ".[mcp]"
python -m magent.mcp_servers.server

# 6. Run the eval gate (fails on >5% regression vs baseline)
magent-eval run
```

## Project layout

```
src/magent/
├── api/            # FastAPI gateway + streaming
├── agents/         # planner, researcher, writer, critic
├── graph/          # LangGraph orchestrator + typed RunState
├── tools/          # MCP client + tool registry
├── mcp_servers/    # web_search, vector_retrieval, code_search
├── memory/         # short_term (Redis), long_term (pgvector)
├── providers/      # azure_foundry, bedrock, vertex, anthropic, router
├── guardrails/     # llama_guard, content_safety, orchestrator
└── observability/  # tracing, metrics
```

## Status / roadmap

- [x] Architecture doc + ADRs
- [x] State schema + LangGraph orchestrator
- [x] End-to-end mock vertical slice (4 agents, mock tool, mock provider)
- [x] Guardrails (pre/post moderation) on every LLM call
- [x] OpenTelemetry tracing on every LLM call (token usage + cost-ready)
- [x] All four provider adapters — Anthropic, AWS Bedrock, Vertex AI, Azure Foundry
- [x] MCP tool layer — FastMCP server (web_search, vector_retrieval, code_search) + MCP client
- [x] Eval harness (keyword coverage + LLM-as-Judge) with CI gate on regression
- [x] FastAPI gateway (`/healthz`, `/run`) + Dockerfile
- [x] Helm chart (Deployment/Service/HPA) + Bicep (Azure Container Apps) + Terraform (AWS ECS Fargate)

## License

MIT (see [LICENSE](LICENSE)).
