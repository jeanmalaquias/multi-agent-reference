"""FastAPI gateway.

Thin HTTP surface over the agent pipeline: a health probe for orchestrators
and a ``/run`` endpoint that takes a goal and returns the reviewed artifact.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .. import __version__
from ..graph.orchestrator import run

app = FastAPI(title="Multi-Agent Reference", version=__version__)


class RunRequest(BaseModel):
    """A goal to run through the pipeline."""

    goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)


class RunResponse(BaseModel):
    """The reviewed result of a pipeline run."""

    artifact: str
    approved: bool
    plan: list[str]
    revisions: int


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness/readiness probe for container orchestrators."""
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run_pipeline(request: RunRequest) -> RunResponse:
    """Run a goal through Planner → Researcher → Writer → Critic."""
    state = await run(request.goal, request.acceptance_criteria)
    return RunResponse(
        artifact=state.draft or "",
        approved=bool(state.critique and state.critique.approved),
        plan=[task.description for task in state.plan],
        revisions=state.revision_count,
    )
