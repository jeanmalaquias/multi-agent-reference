from magent.tools import default_registry


def test_default_registry_has_web_search():
    registry = default_registry()
    assert "web_search" in registry.names()
    assert registry.get("web_search").description


def test_registry_call_returns_tool_output():
    registry = default_registry()
    out = registry.call("web_search", "vector databases")
    assert "vector databases" in out
