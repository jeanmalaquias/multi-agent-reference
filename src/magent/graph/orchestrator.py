"""LangGraph orchestrator (ADR-001).

Wires Planner -> Researcher -> Writer -> Critic, with a conditional edge that
either finishes on approval or routes back to the Planner for a bounded number
of revisions.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from ..agents import critic_node, planner_node, researcher_node, writer_node
from .state import RunState


def _route_after_critic(state: RunState) -> str:
    """Finish when approved or out of revisions; otherwise revise."""
    if state.critique and state.critique.approved:
        return END
    if not state.can_revise:
        return END
    return "planner"


def build_graph():
    """Construct and compile the agent graph."""
    graph = StateGraph(RunState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges(
        "critic", _route_after_critic, {"planner": "planner", END: END}
    )

    return graph.compile()


async def run(goal: str, acceptance_criteria: list[str] | None = None) -> RunState:
    """Run the full pipeline for a goal and return the final state."""
    app = build_graph()
    initial = RunState(goal=goal, acceptance_criteria=acceptance_criteria or [])
    result = await app.ainvoke(initial)
    # LangGraph returns the state as a dict-like; normalize back to RunState.
    return RunState.model_validate(result)
