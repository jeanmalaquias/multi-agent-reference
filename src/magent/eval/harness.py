"""Eval runner, report, and baseline comparison."""

from __future__ import annotations

from statistics import mean

from pydantic import BaseModel

from ..graph.orchestrator import run
from .dataset import Case
from .metrics import Metric


class CaseResult(BaseModel):
    """Per-case metric scores."""

    id: str
    scores: dict[str, float]


class EvalReport(BaseModel):
    """The full result of an eval run."""

    cases: list[CaseResult]
    aggregate: dict[str, float]


class Regression(BaseModel):
    """A metric whose aggregate dropped beyond the threshold vs baseline."""

    metric: str
    baseline: float
    current: float

    @property
    def delta(self) -> float:
        return self.current - self.baseline


async def run_eval(cases: list[Case], metrics: list[Metric]) -> EvalReport:
    """Run every case through the pipeline and score the artifacts."""
    results: list[CaseResult] = []
    for case in cases:
        state = await run(case.goal, case.acceptance_criteria)
        artifact = state.draft or ""
        scores = {m.name: await m.score(case, artifact) for m in metrics}
        results.append(CaseResult(id=case.id, scores=scores))

    aggregate = {
        m.name: mean(r.scores[m.name] for r in results) if results else 0.0
        for m in metrics
    }
    return EvalReport(cases=results, aggregate=aggregate)


def compare_to_baseline(
    report: EvalReport, baseline: dict[str, float], threshold: float
) -> list[Regression]:
    """Return metrics that regressed by more than ``threshold`` vs baseline."""
    regressions: list[Regression] = []
    for metric, current in report.aggregate.items():
        if metric not in baseline:
            continue
        if current < baseline[metric] - threshold:
            regressions.append(
                Regression(metric=metric, baseline=baseline[metric], current=current)
            )
    return regressions
