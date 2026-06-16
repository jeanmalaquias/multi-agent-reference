"""Critic agent — scores the draft and approves or routes back for revision."""

from __future__ import annotations

import re

from ..config import get_settings
from ..graph.state import Critique, RunState
from ..providers import Message, get_provider

_SYSTEM = (
    "You are the Critic. Judge whether the draft satisfies the acceptance "
    "criteria. Reply with APPROVE or REVISE, a score=0..1, and brief feedback."
)
_SCORE_RE = re.compile(r"score=([0-9]*\.?[0-9]+)")


async def critic_node(state: RunState) -> dict:
    """Evaluate the draft. Returns a partial state update incl. revision count."""
    provider = get_provider(get_settings().provider_for("critic"))
    user = (
        f"Acceptance criteria: {'; '.join(state.acceptance_criteria)}\n"
        f"Draft:\n{state.draft}"
    )
    completion = await provider.complete(
        [Message(role="system", content=_SYSTEM), Message(role="user", content=user)]
    )

    text = completion.text
    approved = "APPROVE" in text.upper() and "REVISE" not in text.upper()
    match = _SCORE_RE.search(text)
    score = float(match.group(1)) if match else (0.9 if approved else 0.4)

    critique = Critique(approved=approved, score=score, feedback=text.strip())
    return {
        "critique": critique,
        "revision_count": state.revision_count + (0 if approved else 1),
    }
