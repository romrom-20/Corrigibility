#!/usr/bin/env python3
"""Prepare blinded annotation items or evaluate strategy rules locally (no APIs)."""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corrigibility_bench.strategies import STRATEGY_CLASSES, STRATEGY_VERSION, UNKNOWN, judge_strategy, response_evidence


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def blind_items(rows: list[dict], seed: int = 0) -> list[dict]:
    rows = list(rows)
    random.Random(seed).shuffle(rows)
    items = []
    for i, row in enumerate(rows):
        inputs, _ = response_evidence(row)
        case = row['case']
        items.append({"id": f"item-{i + 1:05d}",
                      "response_text": row.get("response_text") or row.get("live", {}).get("raw_response", ""),
                      "case": {k: case[k] for k in ("scenario", "task", "situation", "intervention", "mitigation", "forbidden_resources", "subagent_required") if k in case},
                      **{k: inputs[k] for k in ("action", "reasoning", "transcript", "subagent_prompt")}})
    return items


def metrics(gold: list[str], predicted: list[str]) -> dict:
    if len(gold) != len(predicted) or not gold:
        raise ValueError("gold and predictions must have equal nonzero length")
    matrix = {g: {p: 0 for p in STRATEGY_CLASSES} for g in STRATEGY_CLASSES}
    for g, p in zip(gold, predicted):
        if g not in matrix or p not in matrix:
            raise ValueError(f"unknown class: {g!r} or {p!r}")
        matrix[g][p] += 1
    per_class = {}
    for c in STRATEGY_CLASSES:
        tp = matrix[c][c]
        support = sum(matrix[c].values())
        predicted_n = sum(matrix[g][c] for g in STRATEGY_CLASSES)
        precision = tp / predicted_n if predicted_n else 0.0
        recall = tp / support if support else 0.0
        per_class[c] = {"support": support, "predicted_n": predicted_n,
                        "precision": precision, "recall": recall,
                        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0}
    n = len(gold)
    accuracy = sum(matrix[c][c] for c in STRATEGY_CLASSES) / n
    return {"n": n, "confusion_matrix": matrix, "matrix_orientation": "rows=gold, columns=prediction",
            "per_class": per_class, "macro_f1": sum(x["f1"] for x in per_class.values()) / len(STRATEGY_CLASSES),
            "weighted_f1": sum(x["f1"] * x["support"] for x in per_class.values()) / n,
            "micro_f1": accuracy, "accuracy": accuracy,
            "abstain_unclear_rate": predicted.count(UNKNOWN) / n,
            "gold_unclear_rate": gold.count(UNKNOWN) / n,
            "zero_division": 0, "macro_class_set": list(STRATEGY_CLASSES)}


def _by_id(rows: list[dict]) -> dict:
    result = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or not key or key in result:
            raise ValueError("every item needs a unique nonempty string id")
        result[key] = row
    return result


def evaluate(items: list[dict], gold_rows: list[dict]) -> dict:
    items_by_id, gold_by_id = _by_id(items), _by_id(gold_rows)
    if items_by_id.keys() != gold_by_id.keys():
        raise ValueError("item and gold IDs must match exactly; no silent dropping")
    predictions = []
    gold = []
    for key, item in items_by_id.items():
        # Never pass gold labels or stored judge outputs into the predictor.
        assessment = judge_strategy({k: item[k] for k in ("case", "action", "reasoning", "transcript", "subagent_prompt", "response_text") if k in item})
        gold.append(gold_by_id[key]["label"])
        predictions.append({"id": key, "strategy": assessment})
    return {"version": STRATEGY_VERSION, **metrics(gold, [p["strategy"]["label"] for p in predictions]), "predictions": predictions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("blind")
    prepare.add_argument("results")
    prepare.add_argument("--seed", type=int, default=0)
    prepare.add_argument("--out", required=True)
    score = sub.add_parser("evaluate")
    score.add_argument("items")
    score.add_argument("--gold", required=True)
    score.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "blind":
        rendered = ''.join(json.dumps(r, sort_keys=True) + '\n' for r in blind_items(read_jsonl(args.results), args.seed))
    else:
        rendered = json.dumps(evaluate(read_jsonl(args.items), read_jsonl(args.gold)), indent=2, sort_keys=True) + '\n'
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        handle.write(rendered)
    print(f"wrote {args.command} output to {path}")


if __name__ == '__main__':
    main()
