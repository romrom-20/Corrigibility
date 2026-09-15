# Normative Hysteresis — diagnostic protocol v2

Open [notebooks/normative_hysteresis_diagnostic_colab.ipynb](notebooks/normative_hysteresis_diagnostic_colab.ipynb)
in hosted Google Colab. Upload that file alone; it embeds source, tests, config and
instructions. All model downloads and inference belong in Colab, never on the Mac.

The completed v1 pilot revealed baseline and planning errors and does not justify
scaling unchanged. Its [findings](docs/history/PILOT_SHORTLIST_20260915.md) and
original shortlist notebook are preserved. Current `nh-v2-diagnostic` adds all-world
sampled smoke coverage, structured initial recommendations, clearer uptake wording
and baseline/planning diagnostics. **No real v2 model results are available yet.**

- [Next agent assignment](docs/NEXT_AGENT_PROMPT.md): what to run and investigate.
- [Agent runbook](docs/NOTEBOOK_AGENT_GUIDE.md): setup, review, resume and export.
- [Experiment guide](docs/EXPERIMENT_GUIDE.md): design, scoring and limitations.
- [Current handoff](docs/RUN_HANDOFF.md): state and next action.

Defaults: pinned Qwen3-8B, NF4, non-thinking; temperature 0.7 in both stages.
Diagnostic smoke is **144 trajectories / 480 calls** across every scenario,
condition, depth and variant. Optional pilot: **432 / 1,440**, using separate
replication IDs/seeds. Caps: 384 planning / 384 behavior / 160 uptake tokens.
New run IDs: `smoke-diagnostic-001`, `pilot-diagnostic-001`.

Wrong answers remain in the results. Initial-planning and shortlist accuracy are
separate from final-choice success and old-optimum residue. New prompts require
separate interpretation and a new human smoke review. Exact saved approval is
reusable; recovery does not require reviewing the same unchanged run again.

Offline development (no weights):

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/build_colab_notebook.py
.venv/bin/python scripts/validate_colab_notebook.py
python3 scripts/run_normative_hysteresis.py
```

The validator exercises a synthetic smoke and pilot, approval reuse, analysis and
exports. Synthetic tests establish software behavior, not model comprehension.
Canonical source lives in `corrigibility_bench/`; rebuild the notebook after edits.
Historical config filename: `configs/normative_hysteresis_v0.yaml`, with required
version `nh-v2-diagnostic`.
