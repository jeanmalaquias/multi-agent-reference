"""Writer agent — synthesizes findings into the requested artifact."""

from __future__ import annotations

from ..graph.state import RunState
from ..providers import Message
from ..runtime import resolve_provider

_SYSTEM = (
    "You are the Writer. Using the research findings, produce the final "
    "artifact that satisfies the goal and acceptance criteria."
)


async def writer_node(state: RunState) -> dict:
    """Write the artifact draft. Returns a partial state update."""
    provider = resolve_provider("writer")
    evidence = "\n".join(f"- {f.content}" for f in state.findings)
    feedback = state.critique.feedback if state.critique else ""
    user = (
        f"Goal: {state.goal}\n"
        f"Acceptance criteria: {'; '.join(state.acceptance_criteria)}\n"
        f"Findings:\n{evidence}\n"
        f"Reviewer feedback to address: {feedback}"
    )
    completion = await provider.complete(
        [Message(role="system", content=_SYSTEM), Message(role="user", content=user)]
    )
    return {"draft": completion.text}
