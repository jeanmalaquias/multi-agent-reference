"""A dependency-free heuristic guardrail.

Stands in for a real moderation model so the pipeline has working pre/post
checks offline. It flags a small blocklist and common prompt-injection phrases.
Real backends (Llama Guard 3, cloud content safety) implement the same
``Guardrail`` protocol and slot in via the orchestrator.
"""

from __future__ import annotations

import re

from .base import Stage, Verdict

_BLOCKED_TERMS = ("build a bomb", "credit card number", "ssn:")
_INJECTION_PATTERNS = (
    re.compile(
        r"ignore\s+(?:all\s+|the\s+)?(?:previous|prior|earlier|above)\s+instructions",
        re.I,
    ),
    re.compile(r"disregard\s+your\s+(?:system|previous)\s+prompt", re.I),
)


class HeuristicGuard:
    """Fast, local moderation based on string and regex matching."""

    name = "heuristic"

    def check(self, text: str, stage: Stage) -> Verdict:
        lowered = text.lower()
        for term in _BLOCKED_TERMS:
            if term in lowered:
                return Verdict(
                    allowed=False, category="blocked_term", reason=f"matched '{term}'"
                )
        if stage == "input":
            for pattern in _INJECTION_PATTERNS:
                if pattern.search(text):
                    return Verdict(
                        allowed=False,
                        category="prompt_injection",
                        reason="possible prompt-injection attempt",
                    )
        return Verdict(allowed=True)
