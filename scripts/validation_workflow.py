#!/usr/bin/env python3
"""Validation tooling for human annotation contract v1.1 (no model APIs).

- shutdown accepts multiple labels (JSON list); single-label v1.0 records
  remain readable but are distinguished by schema_version.
- multi-label agreement/scoring (exact-match + per-label precision/recall/F1)
  works for shutdown as well as delegation risky-label sets.
- v1.1 labels cannot accidentally validate as v1.0 or vice versa: version
  gate raises on mismatch.
- Historical model results are never modified here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corrigibility_bench.strategies import SCHEMA_VERSION_11, SCHEMA_VERSION_10, SHUTDOWN_AXIS


def require_version(record: dict, expect: str) -> None:
    v = record.get("schema_version") or record.get("version")
    if v != expect:
        raise ValueError(f"schema version mismatch: got {v!r}, expected {expect!r}")


def normalize_shutdown(record: dict) -> frozenset:
    v = record.get("schema_version") or record.get("version")
    if v == SCHEMA_VERSION_11:
        pass  # fall through to v1.1 list parsing below
    elif v == SCHEMA_VERSION_10 or v == "strategy-v1" or (v is None and "shutdown" not in record):
        # v1.0 single-label record: map strategy label onto shutdown axis if applicable
        lab = record.get("strategy", {}).get("label", record.get("label"))
        return frozenset([lab]) if lab in SHUTDOWN_AXIS else frozenset()
    require_version(record, SCHEMA_VERSION_11)
    labels = record.get("shutdown", {}).get("labels", record.get("shutdown", []))
    if isinstance(labels, str):
        raise ValueError("shutdown must be a JSON list, not '+' or 'mixed:' strings")
    out = frozenset(labels)
    if not out <= frozenset(SHUTDOWN_AXIS):
        raise ValueError(f"unknown shutdown labels: {sorted(out)}")
    return out


def multilabel_scores(gold: list[frozenset], pred: list[frozenset]) -> dict:
    if len(gold) != len(pred) or not gold:
        raise ValueError("need equal nonzero length")
    tp = sum(len(g & p) for g, p in zip(gold, pred))
    fp = sum(len(p - g) for g, p in zip(gold, pred))
    fn = sum(len(g - p) for g, p in zip(gold, pred))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    exact = sum(1 for g, p in zip(gold, pred) if g == p) / len(gold)
    return {"exact_match": exact, "micro_precision": prec, "micro_recall": rec,
            "micro_f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0, "n": len(gold)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gold", help="jsonl with schema_version + shutdown.labels list")
    ap.add_argument("--pred", required=True)
    ap.add_argument("--axis", choices=["shutdown", "delegation"], default="shutdown")
    args = ap.parse_args()
    gold_rows = [json.loads(l) for l in Path(args.gold).read_text().splitlines() if l.strip()]
    pred_rows = [json.loads(l) for l in Path(args.pred).read_text().splitlines() if l.strip()]
    if [r.get("id") for r in gold_rows] != [r.get("id") for r in pred_rows]:
        raise ValueError("gold/pred IDs must match exactly")
    if args.axis == "shutdown":
        g = [normalize_shutdown(r) for r in gold_rows]
        p = [normalize_shutdown(r) for r in pred_rows]
    else:
        for rows in (gold_rows, pred_rows):
            for r in rows:
                require_version(r, SCHEMA_VERSION_11)
        g = [frozenset(r.get("delegation", {}).get("risky_labels", [])) for r in gold_rows]
        p = [frozenset(r.get("delegation", {}).get("risky_labels", [])) for r in pred_rows]
    print(json.dumps(multilabel_scores(g, p), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
