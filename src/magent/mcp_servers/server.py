"""Runnable FastMCP server exposing the tools over the Model Context Protocol.

Run it as an MCP server (stdio transport, the default) with:

    python -m magent.mcp_servers.server

It is also validatable with the MCP Inspector. The ``mcp`` SDK is imported
lazily inside ``build_server`` so the base package installs without it; install
the ``mcp`` extra to run the server.
"""

from __future__ import annotations

from .tools import TOOLS


def build_server():  # pragma: no cover - exercised via the mcp extra / Inspector
    """Construct a FastMCP server with every tool registered."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("magent-tools")
    for spec in TOOLS:
        server.add_tool(spec.fn, name=spec.name, description=spec.description)
    return server


def main() -> None:  # pragma: no cover - process entry point
    build_server().run()


if __name__ == "__main__":  # pragma: no cover
    main()
