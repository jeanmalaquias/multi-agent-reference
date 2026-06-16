from magent.graph.state import Critique, RunState, SubTask


def test_can_revise_respects_max():
    state = RunState(goal="g", revision_count=2, max_revisions=3)
    assert state.can_revise is True
    state.revision_count = 3
    assert state.can_revise is False


def test_critique_score_bounds():
    c = Critique(approved=True, score=0.5)
    assert 0.0 <= c.score <= 1.0


def test_subtask_defaults_not_done():
    assert SubTask(id=1, description="x").done is False
