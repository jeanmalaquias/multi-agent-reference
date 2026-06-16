"""Tool registry.

In production these are MCP servers discovered over stdio/HTTP (ADR-002). For
the vertical slice we register an in-process mock ``web_search`` so the
Researcher has a real tool-call path without external dependencies.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


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


def _mock_web_search(query: str) -> str:
    return f"[web_search] top result for '{query}': a relevant, citable source."


def default_registry() -> ToolRegistry:
    """Build the default registry used by the vertical slice."""
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="web_search",
            description="Search the web and return the top result.",
            fn=_mock_web_search,
        )
    )
    return registry
