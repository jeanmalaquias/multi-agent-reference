import pytest

from magent.providers import Message, get_provider
from magent.providers.router import register_provider


async def test_mock_provider_roles():
    provider = get_provider("mock")
    planner = await provider.complete(
        [Message(role="system", content="You are the Planner."),
         Message(role="user", content="goal")]
    )
    assert "1." in planner.text
    assert planner.provider == "mock"
    assert planner.usage.total_tokens > 0


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("does-not-exist")


def test_register_provider_roundtrip():
    register_provider("mock2", type(get_provider("mock")))
    assert get_provider("mock2").name == "mock"
