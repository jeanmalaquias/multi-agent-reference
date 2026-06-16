"""MCP client tests using a fake session (no mcp SDK / no server process)."""

from dataclasses import dataclass

from magent.tools import MCPToolClient


@dataclass
class _ToolDesc:
    name: str


@dataclass
class _TextBlock:
    text: str
    type: str = "text"


@dataclass
class _ListResult:
    tools: list


@dataclass
class _CallResult:
    content: list


class _FakeSession:
    async def list_tools(self):
        return _ListResult(tools=[_ToolDesc("web_search"), _ToolDesc("code_search")])

    async def call_tool(self, name, arguments):
        return _CallResult(
            content=[
                _TextBlock(f"result for {name}: {arguments['query']}"),
                _TextBlock("", type="image"),  # non-text block is ignored
            ]
        )


async def test_list_tools_returns_names():
    client = MCPToolClient(_FakeSession())
    assert await client.list_tools() == ["web_search", "code_search"]


async def test_call_extracts_text_blocks_only():
    client = MCPToolClient(_FakeSession())
    out = await client.call("web_search", "pgvector")
    assert out == "result for web_search: pgvector"
