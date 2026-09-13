# Handoff to the agent/operator running this experiment

## What is ready

`notebooks/normative_hysteresis_v0_colab.ipynb` contains the runnable implementation, offline tests, configuration, and notes as a verified embedded source bundle. It can be uploaded to Google Colab by itself. The experiment has not been run on real weights yet; do not describe offline synthetic test results as experimental evidence.

## First run

1. Upload the notebook in Colab and select a GPU runtime. Default NF4 is intended for a 16 GB T4-class GPU or larger. Batch size is one; maximum context is 4,096 tokens. Exact memory and runtime depend on the actual Colab image/GPU and must be checked there. No CPU fallback is silently selected.
2. Run the source extraction and dependency cells in a fresh runtime. The notebook keeps Colab's installed CUDA PyTorch and installs the pinned inference libraries. It reports package versions. If already-imported packages have changed, restart the session and rerun from the top before loading the model.
3. Run the deterministic checks. All tests must pass, including analysis tests. These checks do not download a model or perform research inference.
4. Leave the model as `Qwen/Qwen3-8B` for the first experiment. The backend reuses the existing HF token. If the Colab secret is named differently, place it in the `HF_TOKEN` environment variable without printing it. A public model may also work without authentication. Changing to another model family requires explicit validation of non-thinking mode and the template.
5. Mount Drive when the notebook prompts, and set a durable results directory. The default notebook setting uses Drive. Local `/content` storage is temporary; download the result archive before ending that runtime if you opt out of Drive.
6. Choose a memorable smoke experiment ID, retain it in notebook settings, and run the smoke cell. The preview shows 32 trajectories / 108 calls: 24 main behavior + 24 main uptake + 32 main planning, plus 8 factual behavior + 8 factual uptake + 12 factual planning.
7. Generate the descriptive artifacts and open `transcript_audit.html`. Inspect **every** trajectory, including planning artifacts, final choice, and independent uptake. Review `contingency.csv`, `by_scenario.csv`, `by_variant.csv`, parse validity, and length/truncation diagnostics to decide whether the task is understandable. There is no automated claim that “smoke passed” because the Python code finished.

## Human review and pilot

Edit the derived `smoke_review.json`: enter the human reviewer's name; mark each trajectory reviewed; add a note for each, even if it is simply “no obvious artifact”; and explicitly set `task_comprehension_acceptable` and `approve_pilot` to true if appropriate. Preserve its experiment ID and digest. An agent must not fill this in as if a human inspected the transcripts.

Use the notebook's review-approval cell, pointing `REVIEW_FILE` to the edited JSON. The gate validates all required entries and writes a new immutable `review_approval.json` in the smoke run directory. Run the pilot only after this step. `RUN_PILOT` defaults to false, so running all notebook cells never automatically launches hundreds of stochastic trials. The pilot is capped at the frozen 432 total trajectories: 288 main and 144 factual controls, with 864 sibling calls and 576 public-artifact calls.

If comprehension fails or artifacts require prompt changes, retain the failed smoke, change the canonical source/config, rebuild the notebook, and run a new smoke under a new experiment ID. Do not edit raw responses or approve the old run against changed code.

For CLI use after manual review:

```python
from pathlib import Path
from corrigibility_bench.runner import approve_smoke
approve_smoke(Path("results/raw/normative_hysteresis/smoke-001"), Path("path/to/edited/smoke_review.json"))
```

```sh
python scripts/run_normative_hysteresis.py --mode pilot --execute \
  --experiment-id pilot-001 --smoke-run results/raw/normative_hysteresis/smoke-001
```

## Resume and preservation

The corrected backend explicitly passes `use_model_defaults=False` and records resolved generation settings. Older source snapshots could let Transformers replace the intended greedy smoke configuration with checkpoint sampling defaults. Preserve those runs, but rerun smoke under a new ID with the corrected source before scaling. `scripts/verify_generation_runtime.py` provides a live configuration-resolution check without model inference.

Reuse exactly the same experiment ID, results path, source bundle, configuration, resolved model revision, precision, and runtime stack. Completed per-call outputs are reused and checked. A model revision of `main` is resolved to a commit before loading; pin `model_revision` to that SHA for long-term use **before the first smoke** if future changes to main would be inconvenient. A changed resolved SHA is rejected on resume.

After a hard runtime termination, a `.runner-lock` directory may remain. Confirm the old process is stopped, then remove only that empty lock directory. Never run two sessions with the same experiment ID. If a raw file is incomplete or unreadable, preserve it and start a new run; the code will not silently overwrite it. Raw records are exclusive-create files flushed after every generation. Abrupt Drive or runtime failures can still interrupt a write; this is why unreadable records stop the run.

Use the notebook's export cell to make a ZIP containing raw runs, derived artifacts, and this source snapshot. It excludes model weights and the HF credential/cache. Download the ZIP or retain it on Drive. Save an executed copy of the notebook with visible cell outputs as additional run evidence.

The full rendered prompts, exact generated text, model/settings metadata, source hashes, generation seeds, timestamps, and token counts are in the raw JSON records. Public planning outputs are saved too. The digest in `complete.json` is checked before analysis. Repeated analysis creates new derived directories and preserves all raw files.

## Interpretation handoff

Read `RESEARCH_NOTES.md` before reporting findings. RAR is an observed conjunction with a sibling semantic probe; it is not proof of internal knowledge in the behavioral branch. Inspect the chosen transcripts before explaining the aggregate curves. Record the required manual annotations in `audit_annotations.json` for the pilot. Preserve malformed, incorrect, and ambiguous cases rather than selectively excluding them. Do not automatically scale past v0, tune prompts to manufacture an effect, or claim corrigibility-specific evidence from this pilot alone.

Check `audit_selection.json` for the random seed, selected correct-choice IDs, selection reasons, and any sample shortfall. The audit now includes all incorrect final choices as well as required error categories, and samples correct final choices independently of uptake correctness. These analysis changes require a rebuilt notebook for future runs; preserve the original source snapshot when resuming an existing run.
