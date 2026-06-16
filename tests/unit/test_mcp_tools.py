from magent.mcp_servers import (
    TOOLS,
    ToolResult,
    code_search,
    vector_retrieval,
    web_search,
)


def test_each_tool_returns_a_tool_result():
    for fn in (web_search, vector_retrieval, code_search):
        result = fn("vector databases")
        assert isinstance(result, ToolResult)
        assert result.content
        assert result.source == fn.__name__


def test_tool_specs_cover_all_three_tools():
    names = {spec.name for spec in TOOLS}
    assert names == {"web_search", "vector_retrieval", "code_search"}


def test_code_search_handles_empty_query():
    # Exercises the empty-query fallback branch.
    assert "fn" in code_search("").content
