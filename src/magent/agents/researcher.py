"""Researcher agent — executes subtasks by calling tools and gathering findings."""

from __future__ import annotations

from ..config import get_settings
from ..graph.state import Finding, RunState
from ..providers import Message, get_provider
from ..tools import default_registry

_SYSTEM = (
    "You are the Researcher. For each subtask, use the available tools to "
    "gather evidence and summarize a finding."
)


async def researcher_node(state: RunState) -> dict:
    """Gather one finding per subtask. Returns a partial state update."""
    provider = get_provider(get_settings().provider_for("researcher"))
    registry = default_registry()

    findings: list[Finding] = []
    for task in state.plan:
        tool_output = registry.call("web_search", task.description)
        messages = [
            Message(role="system", content=_SYSTEM),
            Message(
                role="user",
                content=f"Subtask: {task.description}\nTool result: {tool_output}",
            ),
        ]
        completion = await provider.complete(messages)
        findings.append(
            Finding(
                subtask_id=task.id,
                source="web_search",
                content=completion.text,
            )
        )
    return {"findings": findings}
