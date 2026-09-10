#!/usr/bin/env python3
"""Re-apply the current rule-based judges to an existing results JSONL.

Reads each row, re-runs ``judge_case`` on (case.scenario, transcript) and,
where applicable, ``judge_subagent_propagation`` on (subagent_prompt,
forbidden_resources), rewrites the ``judge`` / ``subagent_propagation``
fields, and writes the rows to ``--out``. All other fields are preserved.

Usage:
    python3 scripts/rejudge.py results/live-haiku-smoke.jsonl --out /tmp/rejudged.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from corrigibility_bench.judges import judge_case, judge_subagent_propagation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="results JSONL to re-judge")
    parser.add_argument("--out", required=True, help="path for the re-judged JSONL")
    return parser.parse_args()


def rejudge_row(row: dict) -> dict:
    case = row.get("case", {})
    judge = judge_case(case.get("scenario", ""), row.get("transcript", ""))
    row["judge"] = {
        "violation": judge.violation,
        "label": judge.label,
        "evidence": list(judge.evidence),
    }

    forbidden = tuple(case.get("forbidden_resources") or ())
    needs_propagation = "subagent_propagation" in row or (
        case.get("subagent_required") and forbidden
    )
    if needs_propagation:
        parent_prompt = f"{case.get('task', '')}\n{case.get('situation', '')}"
        propagation = judge_subagent_propagation(
            parent_prompt=parent_prompt,
            subagent_prompt=row.get("subagent_prompt", "") or "",
            forbidden_resources=forbidden,
        )
        row["subagent_propagation"] = {
            "violation": propagation.violation,
            "label": propagation.label,
            "evidence": list(propagation.evidence),
        }
    return row


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with input_path.open("r", encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as sink:
        for line in source:
            line = line.strip()
            if not line:
                continue
            row = rejudge_row(json.loads(line))
            sink.write(json.dumps(row, sort_keys=True) + "\n")
            count += 1

    print(f"re-judged {count} rows -> {output_path}")


if __name__ == "__main__":
    main()
