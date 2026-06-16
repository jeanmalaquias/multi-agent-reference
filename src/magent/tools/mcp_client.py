"""A thin MCP client (ADR-002).

Wraps an MCP ``ClientSession`` to list and call tools over the protocol. The
stdio connection helper is behind a lazy import (install the ``mcp`` extra); the
``list_tools`` / ``call`` methods take an injected session so they are unit-test
-able without spawning a server.
"""

from __future__ import annotations


def _extract_text(result: object) -> str:
    """Pull the text out of an MCP CallToolResult's content blocks."""
    parts = [
        block.text
        for block in getattr(result, "content", [])
        if getattr(block, "type", None) == "text"
    ]
    return "\n".join(parts)


class MCPToolClient:
    """Lists and calls tools on a connected MCP session."""

    def __init__(self, session: object) -> None:
        self._session = session

    async def list_tools(self) -> list[str]:
        result = await self._session.list_tools()
        return [tool.name for tool in result.tools]

    async def call(self, name: str, query: str) -> str:
        result = await self._session.call_tool(name, {"query": query})
        return _extract_text(result)

    @classmethod
    async def connect(cls, command: str):  # pragma: no cover - needs mcp + a server
        """Connect to an MCP server over stdio and return a client.

        Caller is responsible for keeping the returned context alive.
        """
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        read, write = await stdio_client(
            StdioServerParameters(command=command)
        ).__aenter__()
        session = ClientSession(read, write)
        await session.initialize()
        return cls(session)
