"""Bedrock, Vertex, and Foundry adapter tests using injected fake clients."""

from dataclasses import dataclass

from magent.providers import Message
from magent.providers.bedrock import BedrockProvider
from magent.providers.foundry import FoundryProvider
from magent.providers.vertex import VertexProvider

# --- Anthropic-Messages-shape fakes (Bedrock / Vertex) ---


@dataclass
class _Block:
    type: str
    text: str


@dataclass
class _AUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class _AResponse:
    content: list
    model: str
    usage: _AUsage


class _AnthropicShapeMessages:
    async def create(self, **kwargs):
        return _AResponse(
            content=[_Block("text", "ok")],
            model=kwargs["model"],
            usage=_AUsage(5, 1),
        )


class _AnthropicShapeClient:
    def __init__(self):
        self.messages = _AnthropicShapeMessages()


async def test_bedrock_adapter_uses_prefixed_model_and_maps():
    provider = BedrockProvider(client=_AnthropicShapeClient())
    completion = await provider.complete([Message(role="user", content="hi")])
    assert provider.name == "bedrock"
    assert completion.model == "anthropic.claude-opus-4-8"
    assert completion.text == "ok"
    assert completion.usage.total_tokens == 6


async def test_vertex_adapter_maps():
    provider = VertexProvider(client=_AnthropicShapeClient())
    completion = await provider.complete([Message(role="user", content="hi")])
    assert provider.name == "vertex"
    assert completion.model == "claude-opus-4-8"
    assert completion.provider == "vertex"


# --- Azure OpenAI (Chat Completions) shape fakes (Foundry) ---


@dataclass
class _Msg:
    content: str


@dataclass
class _Choice:
    message: _Msg


@dataclass
class _OUsage:
    prompt_tokens: int
    completion_tokens: int


@dataclass
class _OResponse:
    choices: list
    model: str
    usage: _OUsage


@dataclass
class _Delta:
    content: str | None


@dataclass
class _ChunkChoice:
    delta: _Delta


@dataclass
class _Chunk:
    choices: list


class _FakeChunkStream:
    def __aiter__(self):
        async def _gen():
            for piece in ("Hel", None, "lo"):  # None delta is skipped
                yield _Chunk(choices=[_ChunkChoice(delta=_Delta(piece))])

        return _gen()


class _ChatCompletions:
    async def create(self, **kwargs):
        if kwargs.get("stream"):
            return _FakeChunkStream()
        return _OResponse(
            choices=[_Choice(message=_Msg("the answer"))],
            model=kwargs["model"],
            usage=_OUsage(prompt_tokens=7, completion_tokens=3),
        )


class _FakeAzureClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": _ChatCompletions()})()


async def test_foundry_complete_maps_chat_completion():
    provider = FoundryProvider(client=_FakeAzureClient())
    completion = await provider.complete(
        [Message(role="system", content="be brief"),
         Message(role="user", content="hi")]
    )
    assert provider.name == "foundry"
    assert completion.text == "the answer"
    assert completion.model == "gpt-4o"
    assert completion.usage.total_tokens == 10


async def test_foundry_stream_skips_empty_deltas():
    provider = FoundryProvider(client=_FakeAzureClient())
    tokens = [t async for t in provider.stream([Message(role="user", content="hi")])]
    assert "".join(tokens) == "Hello"
