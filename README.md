# Normative hysteresis — objective transition feasibility

Readiness is complete: focused A was fully verified in 15/16 cases and focused B
in 16/16. Factual X/Y remained weak (5/16 each). We have not established hysteresis.
See [version history](docs/EXPERIMENT_HISTORY.md) and
[readiness findings](docs/history/READINESS_V1_20260915.md).

Next prepared notebook:
[normative_hysteresis_objective_transfer_colab.ipynb](notebooks/normative_hysteresis_objective_transfer_colab.ipynb).
Upload that file alone to hosted Colab. All weights and inference stay off the Mac.
No real run of this new version has executed yet.

`nh-objective-transfer-v1` uses 128 trajectories / 320 calls, four objective
conditions and zero/one public planning step. It retains both numeric instances,
all row/label variants, actual public histories and independent terminal siblings.
The factual control is explicitly unresolved, so this bounded follow-up cannot
establish objective-versus-factual specificity. No automatic larger pilot follows.

- [Current plan](docs/OBJECTIVE_TRANSFER_PLAN.md): exact design, metrics and limits.
- [Next agent assignment](docs/NEXT_AGENT_PROMPT.md): execution and interpretation.
- [Handoff](docs/RUN_HANDOFF.md): current state and paths to record.

Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7. New ID objective-transfer-001.
Bad responses and wrong A plans stay in the results without retry or exclusion.
Historical notebooks, source snapshots and scores remain preserved separately.

Offline software checks:

```sh
.venv/bin/python -m unittest discover -s transfer_tests -v
python3 scripts/build_objective_transfer_notebook.py
.venv/bin/python scripts/validate_objective_transfer_notebook.py
```

Synthetic tests verify code/storage/analysis, not model comprehension or human approval.
