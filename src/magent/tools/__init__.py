"""Tool layer. Tools are exposed as MCP servers (ADR-002); this registry is the
in-process client view the Researcher consumes."""

from .registry import ToolRegistry, default_registry

__all__ = ["ToolRegistry", "default_registry"]
