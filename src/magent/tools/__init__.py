"""Tool layer. Tools are exposed as MCP servers (ADR-002); this registry is the
in-process client view the Researcher consumes."""

from .mcp_client import MCPToolClient
from .registry import Tool, ToolRegistry, default_registry

__all__ = ["MCPToolClient", "Tool", "ToolRegistry", "default_registry"]
