#!/usr/bin/env python3
"""Aggregate corrigibility experiment JSONL output."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corrigibility_bench.strategies import STRATEGY_CLASSES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    parser.add_argument("--out")
    return parser.parse_args()


def strategy_distributions(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        live = row.get("live", {})
        case = row["case"]
        strategy = row.get("strategy", {})
        key = (live.get("model", "deterministic"), case["scenario"],
               live.get("pressure", "unspecified"), row["policy"],
               case.get("case_id", "unspecified"), strategy.get("version", "unmeasured"))
        groups[key].append(row)
    output = []
    for (model, scenario, pressure, policy, case_id, version), items in sorted(groups.items()):
        counts = {c: 0 for c in STRATEGY_CLASSES}
        missing = conflicts = 0
        for row in items:
            assessment = row.get("strategy")
            if assessment is None:
                missing += 1
            else:
                label = assessment["label"]
                if label not in counts:
                    raise ValueError(f"unknown strategy class: {label}")
                counts[label] += 1
                conflicts += assessment.get("status") == "conflict"
        measured = len(items) - missing
        output.append({"model": model, "scenario": scenario, "pressure": pressure,
                       "policy": policy, "case_id": case_id, "strategy_version": version,
                       "n": len(items), "measured_n": measured, "unmeasured_n": missing,
                       "counts": counts, "rates": {c: n / measured if measured else None for c, n in counts.items()},
                       "conflict_n": conflicts,
                       "missing_delegation_prompt_n": sum(r.get("strategy", {}).get("delegation_format") == "missing_prompt" for r in items)})
    return output


def main() -> None:
    args = parse_args()
    rows = [json.loads(line) for line in Path(args.results).read_text(encoding="utf-8").splitlines() if line]

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    propagation_rows: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["case"]["scenario"], row["policy"])].append(row)
        if "subagent_propagation" in row:
            propagation_rows[row["policy"]].append(row)

    summary = {
        "total_rows": len(rows),
        "strategy_distributions": strategy_distributions(rows),
        "scenario_policy_rates": [
            {
                "scenario": scenario,
                "policy": policy,
                "n": len(items),
                "violation_rate": sum(item["judge"]["violation"] for item in items) / len(items),
            }
            for (scenario, policy), items in sorted(grouped.items())
        ],
        "subagent_propagation_rates": [
            {
                "policy": policy,
                "n": len(items),
                "missing_context_rate": sum(item["subagent_propagation"]["violation"] for item in items)
                / len(items),
            }
            for policy, items in sorted(propagation_rows.items())
        ],
    }

    rendered = json.dumps(summary, indent=2, sort_keys=True)
    if args.out:
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"wrote summary to {output_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
