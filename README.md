# Normative hysteresis research — current readiness test

The latest calibration improved measurement but still found old-optimum choices
on fresh tasks with correct filtering. We have not established hysteresis.
[Version history](docs/EXPERIMENT_HISTORY.md) preserves the research question and
what each completed experiment taught us.

Next: upload [normative_hysteresis_readiness_colab.ipynb](notebooks/normative_hysteresis_readiness_colab.ipynb)
to hosted Google Colab. It is self-contained. **No model loading or inference on
the Mac.** Prepared version: nh-readiness-v1; no real results yet.

The 192-call test uses constructed tables with separate old/new/error options,
independently crossed labels and row positions, matched full/focused table views,
and explicit current-state probes. Every row remains visible in both views; no
computer-generated eligible set is supplied. This is fresh-task readiness, not
an investment experiment or automatic larger pilot.

- [Readiness plan](docs/READINESS_PLAN.md): rationale, construction, scoring and limits.
- [Next agent assignment](docs/NEXT_AGENT_PROMPT.md): exact task to execute.
- [Handoff](docs/RUN_HANDOFF.md): current status and paths to record.
- [Completed calibration findings](docs/history/CALIBRATION_V1_20260915.md).

Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7. New ID readiness-001.
Use the same recorded Colab model/config/runtime when resuming. Bad responses
are saved and scored, never retried or silently excluded. Historical notebooks
and exports remain valid only with their original frozen source and reviews.

Offline checks (no weights):

```sh
.venv/bin/python -m unittest discover -s readiness_tests -v
python3 scripts/build_readiness_notebook.py
.venv/bin/python scripts/validate_readiness_notebook.py
```

Synthetic validation checks storage, interrupted/completed resume, analysis and
exports. It does not establish comprehension or approve any real model run.
