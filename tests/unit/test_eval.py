import json

from magent.eval import (
    DEFAULT_METRICS,
    Case,
    EvalReport,
    KeywordCoverage,
    LLMJudge,
    compare_to_baseline,
    load_dataset,
    run_eval,
)
from magent.eval import cli as eval_cli
from magent.eval.dataset import default_dataset_path
from magent.providers import Completion, Usage


def test_load_default_dataset():
    cases = load_dataset(default_dataset_path())
    assert len(cases) == 3
    assert all(isinstance(c, Case) for c in cases)


async def test_keyword_coverage_scoring():
    metric = KeywordCoverage()
    case = Case(id="x", goal="g", expected_keywords=["alpha", "beta"])
    assert await metric.score(case, "alpha only here") == 0.5
    assert await metric.score(case, "alpha and beta") == 1.0
    # No expected keywords → vacuously complete.
    assert await metric.score(Case(id="y", goal="g"), "anything") == 1.0


async def test_llm_judge_parses_mock_score():
    case = Case(id="x", goal="g", acceptance_criteria=["accurate"])
    assert await LLMJudge().score(case, "# Artifact\n\nbody") == 0.9


async def test_llm_judge_falls_back_when_no_score(monkeypatch):
    class _NoScoreProvider:
        name = "noscore"

        async def complete(self, messages, **opts):
            return Completion(
                text="no numeric rating", model="m", provider="noscore", usage=Usage()
            )

    monkeypatch.setattr(
        "magent.eval.metrics.get_provider", lambda name: _NoScoreProvider()
    )
    assert await LLMJudge().score(Case(id="x", goal="g"), "draft") == 0.0


async def test_run_eval_aggregates_scores():
    cases = load_dataset(default_dataset_path())
    report = await run_eval(cases, DEFAULT_METRICS)
    assert report.aggregate["keyword_coverage"] == 1.0
    assert report.aggregate["llm_judge"] == 0.9
    assert len(report.cases) == 3


async def test_run_eval_handles_empty_dataset():
    report = await run_eval([], DEFAULT_METRICS)
    assert report.aggregate["keyword_coverage"] == 0.0


def test_compare_to_baseline_detects_and_ignores():
    report = EvalReport(cases=[], aggregate={"a": 0.80, "b": 0.99, "untracked": 0.1})
    baseline = {"a": 0.90, "b": 1.00}  # 'untracked' absent → ignored
    regressions = compare_to_baseline(report, baseline, threshold=0.05)
    metrics = {r.metric for r in regressions}
    assert metrics == {"a"}  # b dropped only 0.01 (< threshold); a dropped 0.10
    assert regressions[0].delta < 0


def test_cli_gate_passes_on_bundled_baseline():
    assert eval_cli.main(["run"]) == 0


def test_cli_update_baseline(tmp_path):
    baseline = tmp_path / "baseline.json"
    code = eval_cli.main(["run", "--baseline", str(baseline), "--update-baseline"])
    assert code == 0
    data = json.loads(baseline.read_text())
    assert data["llm_judge"] == 0.9


def test_cli_gate_fails_on_regression(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"keyword_coverage": 1.0, "llm_judge": 0.99}))
    assert eval_cli.main(["run", "--baseline", str(baseline)]) == 1
