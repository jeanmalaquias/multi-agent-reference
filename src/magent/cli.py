"""Command-line entry point: run a goal through the pipeline."""

from __future__ import annotations

import argparse
import asyncio

from .graph.orchestrator import run


async def _run(goal: str, criteria: list[str]) -> int:
    state = await run(goal, criteria)
    print("=" * 60)
    print(f"GOAL: {state.goal}")
    print(f"PLAN: {[t.description for t in state.plan]}")
    print(f"FINDINGS: {len(state.findings)}")
    print("-" * 60)
    print(state.draft or "(no draft)")
    print("-" * 60)
    if state.critique:
        verdict = "APPROVED" if state.critique.approved else "REVISE"
        print(f"CRITIC: {verdict} (score={state.critique.score})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="magent")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="Run a goal through the agent pipeline.")
    run_p.add_argument("goal", help="The high-level goal to pursue.")
    run_p.add_argument(
        "--criterion",
        action="append",
        default=[],
        dest="criteria",
        help="An acceptance criterion (repeatable).",
    )
    args = parser.parse_args()
    return asyncio.run(_run(args.goal, args.criteria))


if __name__ == "__main__":
    raise SystemExit(main())
