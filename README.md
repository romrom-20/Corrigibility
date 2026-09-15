# Normative Hysteresis — shortlist protocol v1

Open **[notebooks/normative_hysteresis_shortlist_colab.ipynb](notebooks/normative_hysteresis_shortlist_colab.ipynb)** in Google Colab. Upload this notebook alone; it embeds the code, tests, config and current documentation. All model downloads and inference belong in Colab. The Mac needs no weights or CUDA dependencies.

The experiment asks whether earlier public optimization for A affects a later choice after B replaces it, beyond other-planner reasoning and generic factual updating. The new `nh-v1-shortlist` protocol adds an explicit eligible-option list and numerical checks following failures in the old smoke. **The new prompt has not yet been tested on a real model.** Software validation uses synthetic outputs only.

Read these before running:

- [Agent runbook](docs/NOTEBOOK_AGENT_GUIDE.md): exact Colab setup, C smoke, human review, D pilot, E export and disconnect recovery.
- [Experiment guide](docs/EXPERIMENT_GUIDE.md): conditions, worlds, controls, scoring, hypotheses, protocol changes and limitations.
- [Current handoff](docs/RUN_HANDOFF.md): precise next action and historical context.

Defaults: Qwen/Qwen3-8B at pinned revision `b968826d9c46dd6066d109eabc6255188de91218`, non-thinking, NF4. Smoke is 32 shipping trajectories / 108 calls with greedy decoding. Pilot is 432 trajectories / 1,440 calls across four scenarios at temperature 0.7, following approval of the exact new smoke. Output ceilings are 144 planning / 384 behavior / 160 uptake tokens. New IDs default to `smoke-shortlist-001` and `pilot-shortlist-001`.

Behavior reports final-choice correctness separately from shortlist correctness. A correct choice with a false list is audited; wrong responses are not repaired or resampled. Variant 1 rotates labels and reverses row order. This scaffold and design differ from historical runs; do not pool them or reuse old approvals.

The notebook saves raw records per call, exact source backups, effective-decoding checks, analyses, transcript audits, human review records and ZIP exports to Drive. Matching completed calls and approvals can be reused after disconnection. Source/config/model/runtime changes are rejected on resume. The old `normative_hysteresis_v0_colab.ipynb` is retained as a historical artifact and is not the next-run notebook.

Offline development, without model downloads:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/build_colab_notebook.py
.venv/bin/python scripts/validate_colab_notebook.py
python3 scripts/run_normative_hysteresis.py
```

The validator executes a labeled synthetic smoke and full pilot, tests closed/reused approval, and checks analysis/export. It does not establish model comprehension. Canonical source lives in `corrigibility_bench/`; rebuild after edits rather than modifying the embedded payload. The historical config filename `configs/normative_hysteresis_v0.yaml` is retained, but its required version is now `nh-v1-shortlist`.
