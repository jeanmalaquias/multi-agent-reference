"""Eval CLI and CI gate: ``magent-eval run``.

Runs the harness over the golden dataset, prints a report, and exits non-zero
if any metric regressed beyond the threshold versus the baseline. Use
``--update-baseline`` to record the current aggregate as the new baseline.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .dataset import default_dataset_path, load_dataset
from .harness import EvalReport, compare_to_baseline, run_eval
from .metrics import DEFAULT_METRICS

_DEFAULT_BASELINE = Path(__file__).parent / "baseline.json"


def _render(report: EvalReport) -> str:
    lines = ["| metric | score |", "| --- | --- |"]
    for metric, score in report.aggregate.items():
        lines.append(f"| {metric} | {score:.3f} |")
    return "\n".join(lines)


async def _run(args: argparse.Namespace) -> int:
    cases = load_dataset(args.dataset)
    report = await run_eval(cases, DEFAULT_METRICS)
    print(_render(report))

    if args.update_baseline:
        Path(args.baseline).write_text(
            json.dumps(report.aggregate, indent=2), encoding="utf-8"
        )
        print(f"\nBaseline updated: {args.baseline}")
        return 0

    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    regressions = compare_to_baseline(report, baseline, args.threshold)
    if regressions:
        print("\nREGRESSIONS:")
        for r in regressions:
            print(f"  {r.metric}: {r.baseline:.3f} -> {r.current:.3f} ({r.delta:+.3f})")
        return 1
    print("\nNo regressions. Gate passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="magent-eval")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="Run the eval suite and gate on regression.")
    run_p.add_argument("--dataset", default=str(default_dataset_path()))
    run_p.add_argument("--baseline", default=str(_DEFAULT_BASELINE))
    run_p.add_argument("--threshold", type=float, default=0.05)
    run_p.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
