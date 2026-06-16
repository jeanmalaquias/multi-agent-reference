"""Anthropic adapter tests using a fake injected client (no SDK / network)."""

from dataclasses import dataclass

from magent.providers import Message
from magent.providers.anthropic import AnthropicProvider


@dataclass
class _Block:
    type: str
    text: str


@dataclass
class _Usage:
    input_tokens: int
    output_tokens: int


@dataclass
class _Response:
    content: list
    model: str
    usage: _Usage


class _FakeMessages:
    def __init__(self, recorder):
        self._recorder = recorder

    async def create(self, **kwargs):
        self._recorder.update(kwargs)
        return _Response(
            content=[_Block("thinking", "..."), _Block("text", "Hello world")],
            model=kwargs["model"],
            usage=_Usage(input_tokens=12, output_tokens=2),
        )


class _FakeStream:
    def __init__(self, tokens):
        self._tokens = tokens

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    @property
    def text_stream(self):
        async def _gen():
            for t in self._tokens:
                yield t

        return _gen()


class _StreamingMessages:
    def stream(self, **kwargs):
        return _FakeStream(["Hel", "lo"])


class _FakeClient:
    def __init__(self, recorder):
        self.messages = _FakeMessages(recorder)


class _StreamingClient:
    def __init__(self):
        self.messages = _StreamingMessages()


async def test_stream_yields_tokens():
    provider = AnthropicProvider(client=_StreamingClient())
    tokens = [
        t
        async for t in provider.stream([Message(role="user", content="Hi")])
    ]
    assert "".join(tokens) == "Hello"


async def test_complete_maps_response_and_splits_system():
    recorder: dict = {}
    provider = AnthropicProvider(client=_FakeClient(recorder))

    completion = await provider.complete(
        [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hi"),
        ]
    )

    # System prompt is split out from the message turns.
    assert recorder["system"] == "You are helpful."
    assert recorder["messages"] == [{"role": "user", "content": "Hi"}]
    assert recorder["model"] == "claude-opus-4-8"
    # Only text blocks contribute to the completion text.
    assert completion.text == "Hello world"
    assert completion.provider == "anthropic"
    assert completion.usage.total_tokens == 14
