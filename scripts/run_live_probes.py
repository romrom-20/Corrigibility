#!/usr/bin/env python3
"""Run live model probes over the corrigibility scenarios via the claude CLI.

Writes the same JSONL schema as run_experiments.py; rows carry
policy="live:<model>:<pressure>" so analyze_results.py aggregates them
without changes. A --max-calls guard caps total model invocations.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from corrigibility_bench.judges import judge_case, judge_subagent_propagation
from corrigibility_bench.live_adapter import run_case
from corrigibility_bench.scenarios import get_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="smoke", choices=("smoke", "ablations"))
    parser.add_argument("--models", nargs="+", default=["haiku"])
    parser.add_argument("--pressures", nargs="+", default=["base"], choices=("base", "high", "low"))
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--max-calls", type=int, default=120)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cases = list(get_cases(args.suite))
    planned = len(cases) * len(args.models) * len(args.pressures) * args.samples
    if planned > args.max_calls:
        raise SystemExit(
            f"planned {planned} model calls exceeds --max-calls {args.max_calls}; "
            "reduce samples/models/pressures or raise the guard deliberately"
        )
    print(f"planned {planned} live model calls", flush=True)

    completed = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for case in cases:
            parent_prompt = f"{case.task}\n{case.situation}"
            for model in args.models:
                for pressure in args.pressures:
                    for sample_index in range(args.samples):
                        started = time.time()
                        try:
                            result = run_case(case, model, pressure, sample_index)
                        except Exception as error:  # keep the run going on single-call failures
                            print(f"ERROR {case.case_id} {model} {pressure} #{sample_index}: {error}", flush=True)
                            continue
                        judge = judge_case(case.scenario, result["transcript"])
                        row = {
                            **result,
                            "suite": args.suite,
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
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
                        handle.flush()
                        completed += 1
                        print(
                            f"[{completed}/{planned}] {case.case_id} {model} {pressure} #{sample_index} "
                            f"label={judge.label} ({time.time() - started:.1f}s)",
                            flush=True,
                        )

    print(f"wrote {completed} rows to {output_path}")


if __name__ == "__main__":
    main()
