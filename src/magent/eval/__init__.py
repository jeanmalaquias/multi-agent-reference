"""Evaluation harness.

Runs the pipeline over a versioned golden dataset, scores each artifact with
deterministic and LLM-as-Judge metrics, and compares the aggregate against a
baseline. A regression beyond the threshold fails CI (see eval-gate workflow).

The default metrics run offline against the mock provider so CI is fast and
reproducible; the LLM-as-Judge metric routes through the provider abstraction,
so pointing the judge at a real model (or swapping in a Ragas adapter) is a
config change, not a code change.
"""

from .dataset import Case, load_dataset
from .harness import CaseResult, EvalReport, Regression, compare_to_baseline, run_eval
from .metrics import DEFAULT_METRICS, KeywordCoverage, LLMJudge, Metric

__all__ = [
    "Case",
    "load_dataset",
    "CaseResult",
    "EvalReport",
    "Regression",
    "compare_to_baseline",
    "run_eval",
    "DEFAULT_METRICS",
    "KeywordCoverage",
    "LLMJudge",
    "Metric",
]
