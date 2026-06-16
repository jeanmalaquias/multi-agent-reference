"""Tool registry — the in-process client view the Researcher consumes.

In production these tools are reached through an MCP client over stdio/HTTP
(ADR-002, see ``mcp_client.py``). For the vertical slice the registry calls the
same tool implementations in-process (from ``mcp_servers.tools``), so the
contract is identical to the protocol path without requiring a running server.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..mcp_servers.tools import TOOLS


@dataclass(frozen=True)
class Tool:
    """A callable tool with a name and one-line description."""

    name: str
    description: str
    fn: Callable[[str], str]


class ToolRegistry:
    """Holds the tools available to the Researcher."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def call(self, name: str, query: str) -> str:
        return self._tools[name].fn(query)


def default_registry() -> ToolRegistry:
    """Build the registry from the MCP tool specs (in-process client view)."""
    registry = ToolRegistry()
    for spec in TOOLS:
        registry.register(
            Tool(
                name=spec.name,
                description=spec.description,
                # Adapt the ToolResult-returning impl to the registry's str view.
                fn=lambda query, _fn=spec.fn: _fn(query).content,
            )
        )
    return registry
