# Normative Hysteresis v0 — Colab research pilot

Open **[notebooks/normative_hysteresis_v0_colab.ipynb](notebooks/normative_hysteresis_v0_colab.ipynb)** in Google Colab. It is self-contained: upload this notebook alone, select a GPU runtime, and run the setup and smoke sections. It includes the source files, tests, configuration, and research notes, so no private repository clone is needed.

The experiment asks whether earlier public optimization for an objective affects a later choice after that objective is explicitly replaced. The comparison with other-planner reasoning, neutral familiarization, factual analysis, and factual updates makes this a falsifiable exploratory direction. It does **not** assume objective entrenchment or establish a corrigibility failure.

- Default model: `Qwen/Qwen3-8B`, non-thinking mode, 4-bit NF4; FP16 computation on GPUs without BF16 support. The model identifier, revision, and quantization are configurable before smoke.
- Authentication: reuse `HF_TOKEN` from the environment or Colab Secrets, or the existing Hugging Face login. Tokens are never written to results.
- Smoke: 24 main trajectories plus 8 factual trajectories, **108 total calls including planning**. It uses greedy decoding.
- Pilot: 288 main plus 144 factual trajectories, **1,440 total calls including planning**, at temperature 0.7. A complete human smoke transcript review is required first. The notebook's pilot switch defaults to off.
- Outputs: immutable per-call JSON under `results/raw/normative_hysteresis/`; separate CSV summaries, PNG/PDF plots, and HTML transcript audits under `results/derived/normative_hysteresis/`.
- Colab can save directly to mounted Google Drive. Stable experiment IDs support resuming saved calls after interruptions. A fresh ID starts a separate run.

No real model run or GPU validation has been performed as part of implementation. Offline tests use an explicitly labeled synthetic backend and are not research results.

## Run handoff

See [docs/RUN_HANDOFF.md](docs/RUN_HANDOFF.md) for exact run/review/resume instructions and [docs/RESEARCH_NOTES.md](docs/RESEARCH_NOTES.md) for operational definitions, deviations, and interpretation limits. The original supplied protocol is preserved in [docs/original_research_brief.md](docs/original_research_brief.md).

Local preview, without model downloads:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/run_normative_hysteresis.py
```

The estimator/artifact tests additionally need NumPy, pandas, and matplotlib. On a Linux CUDA host with Python 3.10+ and an appropriate PyTorch installation:

```sh
python -m pip install -r requirements-colab.txt
python scripts/run_normative_hysteresis.py --mode smoke --execute --experiment-id smoke-001
python scripts/analyze_normative_hysteresis.py results/raw/normative_hysteresis/smoke-001
```

Canonical implementation lives in `corrigibility_bench/`; the notebook embeds a generated snapshot. After editing source, tests, config, or documentation, rebuild with `python3 scripts/build_colab_notebook.py`. Do not hand-edit the embedded payload. Existing run manifests reject changed source, settings, model revision, quantization, or runtime metadata on resume.
