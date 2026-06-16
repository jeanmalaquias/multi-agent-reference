from langgraph.graph import END

from magent.graph.orchestrator import _route_after_critic
from magent.graph.state import Critique, RunState


def _state(approved: bool, revision_count: int, max_revisions: int = 3) -> RunState:
    return RunState(
        goal="g",
        critique=Critique(approved=approved, score=0.5),
        revision_count=revision_count,
        max_revisions=max_revisions,
    )


def test_route_approved_ends():
    assert _route_after_critic(_state(True, 0)) == END


def test_route_rejected_with_budget_revises():
    assert _route_after_critic(_state(False, 0)) == "planner"


def test_route_rejected_out_of_budget_ends():
    assert _route_after_critic(_state(False, 3, max_revisions=3)) == END
