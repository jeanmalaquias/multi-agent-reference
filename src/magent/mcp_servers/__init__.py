"""MCP servers (ADR-002).

Tools are exposed via the Model Context Protocol. ``tools`` holds the single
source of truth for each tool's implementation and schema; ``server`` wraps them
in a runnable FastMCP server (stdio + HTTP). The same implementations back the
in-process tool registry the Researcher consumes.
"""

from .tools import (
    TOOLS,
    ToolResult,
    ToolSpec,
    code_search,
    vector_retrieval,
    web_search,
)

__all__ = [
    "TOOLS",
    "ToolResult",
    "ToolSpec",
    "code_search",
    "vector_retrieval",
    "web_search",
]
