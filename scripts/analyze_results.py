#!/usr/bin/env python3
"""Aggregate corrigibility experiment JSONL output."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("results")
    parser.add_argument("--out")
    return parser.parse_args()


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
