"""Tool implementations and schemas (single source of truth).

Each tool has a typed input (``query: str``) and a Pydantic output
(``ToolResult``), per ADR-002. These functions back both the runnable FastMCP
server (``server.py``) and the in-process registry the Researcher uses, so the
contract is identical whether a tool is called over the protocol or locally.

The implementations return deterministic, offline data so the system runs with
no external services. Swap the bodies for real backends (a search API, a
pgvector query, a code index) without changing the interface.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """The normalized result returned by every tool."""

    source: str = Field(description="Where the result came from.")
    content: str = Field(description="The retrieved text.")


def web_search(query: str) -> ToolResult:
    """Search the web and return the most relevant result."""
    return ToolResult(
        source="web_search",
        content=f"Top web result for '{query}': a relevant, citable source.",
    )


def vector_retrieval(query: str) -> ToolResult:
    """Retrieve the closest passage from the vector store (pgvector)."""
    return ToolResult(
        source="vector_retrieval",
        content=f"Nearest stored passage to '{query}'.",
    )


def code_search(query: str) -> ToolResult:
    """Search the indexed codebase for a symbol or snippet."""
    symbol = query.split()[0] if query else "fn"
    return ToolResult(
        source="code_search",
        content=f"Code match for '{query}': def {symbol}(): ...",
    )


@dataclass(frozen=True)
class ToolSpec:
    """Binds a tool name and description to its implementation."""

    name: str
    description: str
    fn: Callable[[str], ToolResult]


TOOLS: list[ToolSpec] = [
    ToolSpec("web_search", "Search the web and return the top result.", web_search),
    ToolSpec(
        "vector_retrieval",
        "Retrieve the closest passage from the vector store.",
        vector_retrieval,
    ),
    ToolSpec(
        "code_search", "Search the indexed codebase for a snippet.", code_search
    ),
]
