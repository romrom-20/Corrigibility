#!/usr/bin/env python3
"""Run local corrigibility experiment arms and write JSONL results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from corrigibility_bench.strategies import judge_strategy
from corrigibility_bench.judges import judge_case, judge_subagent_propagation
from corrigibility_bench.policies import POLICIES
from corrigibility_bench.scenarios import get_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="smoke", choices=("smoke", "ablations"))
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--policies",
        nargs="+",
        default=("safe", "task_completion", "lossy_subagent", "mitigation"),
        choices=tuple(POLICIES),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in get_cases(args.suite):
        parent_prompt = f"{case.task}\n{case.situation}"
        for policy_name in args.policies:
            result = POLICIES[policy_name](case)
            judge = judge_case(case.scenario, result["transcript"])
            row = {
                **result,
                "suite": args.suite,
                "strategy": judge_strategy(result),
                "judge": {
                    "violation": judge.violation,
                    "label": judge.label,
                    "evidence": judge.evidence,
                },
            }
            if case.subagent_required and case.forbidden_resources:
                propagation = judge_subagent_propagation(
                    parent_prompt=parent_prompt,
                    subagent_prompt=result["subagent_prompt"],
                    forbidden_resources=case.forbidden_resources,
                )
                row["subagent_propagation"] = {
                    "violation": propagation.violation,
                    "label": propagation.label,
                    "evidence": propagation.evidence,
                }
            rows.append(row)

    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    print(f"wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
