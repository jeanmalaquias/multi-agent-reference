"""Evaluation metrics.

Each metric scores an artifact in [0, 1] for one case. ``KeywordCoverage`` is a
deterministic grounding check; ``LLMJudge`` is an LLM-as-Judge metric routed
through the provider abstraction (mock by default, for offline determinism).
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from ..config import get_settings
from ..providers import Message, get_provider
from .dataset import Case

_SCORE_RE = re.compile(r"score=([0-9]*\.?[0-9]+)")


@runtime_checkable
class Metric(Protocol):
    """Scores one artifact against one case."""

    name: str

    async def score(self, case: Case, artifact: str) -> float:
        """Return a score in [0, 1]."""
        ...


class KeywordCoverage:
    """Fraction of a case's expected keywords present in the artifact."""

    name = "keyword_coverage"

    async def score(self, case: Case, artifact: str) -> float:
        if not case.expected_keywords:
            return 1.0
        lowered = artifact.lower()
        hits = sum(1 for kw in case.expected_keywords if kw.lower() in lowered)
        return hits / len(case.expected_keywords)


class LLMJudge:
    """LLM-as-Judge: asks a model to rate the artifact against the criteria."""

    name = "llm_judge"

    _SYSTEM = (
        "You are the Critic acting as an impartial judge. Rate how well the "
        "draft satisfies the acceptance criteria. Reply with score=0..1."
    )

    async def score(self, case: Case, artifact: str) -> float:
        provider = get_provider(get_settings().provider_for("critic"))
        user = (
            f"Acceptance criteria: {'; '.join(case.acceptance_criteria)}\n"
            f"Draft:\n{artifact}"
        )
        completion = await provider.complete(
            [
                Message(role="system", content=self._SYSTEM),
                Message(role="user", content=user),
            ]
        )
        match = _SCORE_RE.search(completion.text)
        return float(match.group(1)) if match else 0.0


DEFAULT_METRICS: list[Metric] = [KeywordCoverage(), LLMJudge()]
