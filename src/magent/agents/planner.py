"""Planner agent — decomposes the goal into ordered subtasks."""

from __future__ import annotations

from ..config import get_settings
from ..graph.state import RunState, SubTask
from ..providers import Message, get_provider

_SYSTEM = (
    "You are the Planner. Decompose the user's goal into a short ordered list "
    "of concrete subtasks, one per line."
)


async def planner_node(state: RunState) -> dict:
    """Produce a plan from the goal. Returns a partial state update."""
    provider = get_provider(get_settings().provider_for("planner"))
    messages = [
        Message(role="system", content=_SYSTEM),
        Message(role="user", content=state.goal),
    ]
    completion = await provider.complete(messages)

    plan = [
        SubTask(id=i, description=line.lstrip("0123456789. ").strip())
        for i, line in enumerate(completion.text.splitlines())
        if line.strip()
    ]
    return {"plan": plan}
