"""Typed run state threaded through the agent graph.

The entire pipeline shares one Pydantic model — never untyped dicts (ADR-001).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubTask(BaseModel):
    """A single unit of work produced by the Planner."""

    id: int
    description: str
    done: bool = False


class Finding(BaseModel):
    """A piece of evidence gathered by the Researcher for a subtask."""

    subtask_id: int
    source: str
    content: str


class Critique(BaseModel):
    """The Critic's structured verdict on a draft."""

    approved: bool
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""


class RunState(BaseModel):
    """Single source of truth for one pipeline run."""

    goal: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    plan: list[SubTask] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    draft: str | None = None
    critique: Critique | None = None
    revision_count: int = 0
    max_revisions: int = 3

    @property
    def can_revise(self) -> bool:
        """True while the Critic is still allowed to route back for revision."""
        return self.revision_count < self.max_revisions
