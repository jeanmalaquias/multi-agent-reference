from magent.graph.orchestrator import run


async def test_end_to_end_pipeline_produces_approved_artifact():
    state = await run(
        "Write a one-paragraph brief on vector databases",
        ["accurate", "concise"],
    )
    # The full Planner -> Researcher -> Writer -> Critic loop ran.
    assert state.plan, "planner produced subtasks"
    assert len(state.findings) == len(state.plan), "one finding per subtask"
    assert state.draft and "Artifact" in state.draft
    assert state.critique is not None
    assert state.critique.approved is True
    assert state.revision_count == 0
