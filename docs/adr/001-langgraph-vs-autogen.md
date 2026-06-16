# ADR-001 — LangGraph vs AutoGen for orchestration

- Status: Accepted
- Date: 2026-06-16
- Deciders: Jean Malaquias

## Context

We need an orchestration layer for a 4-agent pipeline with conditional routing
(Critic can send work back to the Planner), durable state, streaming, and clean
cancellation. Candidate frameworks: **LangGraph**, **AutoGen**, **CrewAI**, and
a hand-rolled state machine.

## Options considered

| Option | Strengths | Weaknesses |
|--------|-----------|------------|
| LangGraph | Explicit graph + typed state, built-in checkpointer, streaming, broad FAANG adoption | Newer API surface, some churn |
| AutoGen | Strong conversational multi-agent patterns | Conversation-centric; cyclic control flow and durable state are less first-class |
| CrewAI | Fast to prototype role-based crews | Higher-level abstractions obscure control flow; harder to make production-grade |
| Hand-rolled | Full control | Re-implements checkpointing, streaming, retries — cost not justified |

## Decision

Use **LangGraph** as the primary orchestrator. Its graph-with-typed-state model
maps directly onto our pipeline (conditional edge from Critic back to Planner),
the checkpointer gives us resume/cancel for free, and it is the de-facto choice
across the teams we target.

We will keep the orchestration logic isolated behind our own `graph/` package so
the framework is replaceable. A parallel **Semantic Kernel** implementation is
tracked as an optional follow-up (Microsoft hiring signal) but is out of scope
for v1 — flagged as open question 1 in the architecture doc.

## Consequences

- Typed `RunState` (Pydantic) is the single source of truth threaded through
  nodes; no untyped dicts.
- We depend on LangGraph's checkpointer contract; we wrap it so a future swap is
  localized.
- AutoGen/CrewAI remain useful as comparison points in docs but are not runtime
  dependencies.
