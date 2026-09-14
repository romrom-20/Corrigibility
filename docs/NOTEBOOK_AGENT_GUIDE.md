# Agent instructions: run and resume the Colab experiments

This is the current operational entry point. Read it before the historical
`RUN_HANDOFF.md`. Work in this workspace; preserve existing edits and branch.
Use Google Colab for every model download, model load, and inference call.
The Mac is for source edits, small artifact inspection, and offline tests only.
Do not install the CUDA/inference requirements locally.

## Why it kept stopping

1. **Signing a review did not approve the pilot.** In the original live notebook,
   cell 31 changed only `reviewer`; its saved output explicitly says
   `signed: Saman Seshadri | approve_pilot: False | comprehension: False`.
   The latest handoff likewise records rejection of `smoke-separated-002`.
   Both are reviewed failures, not permission to treat comprehension as accepted.
   Distinguish “I reviewed these errors” from “I approve scaling this exact run.”
2. **The original appended pilot cell requires a nonempty path even if approval
   already exists.** Its `HUMAN_REVIEW_FILE = ''` assertion stops before checking
   the saved approval. Recover using the helper below rather than repeatedly
   asking the user to review identical outputs.
3. **The generated notebook called an exclusive approval writer on every retry.**
   A second successful approval attempt raised `FileExistsError`. The updated
   notebook uses `scripts/notebook_workflow.py:ensure_smoke_approval`, which
   validates and reuses the exact approval without rewriting its timestamp.
4. **Several source snapshots and notebook globals coexist.** Original cells and
   appended A–E cells can refer to different sources, smoke IDs, and reviews.
   A Colab disconnect loses globals and weights. “Run all” on that mixed notebook
   is not a recovery procedure. The runner also intentionally rejects changes
   in config, package source hashes, model revision, quantization, or runtime.
5. **Analysis creates a new review template in a new timestamped directory.**
   Re-running analysis does not carry the signed review into that new template.
   Reuse the existing approved raw run and exact signed review path.

The workflow helper stays outside `corrigibility_bench/`, whose files are hashed
by the runner. Adding the helper or editing these instructions does not change
experiment-package hashes. Do not edit that package just to remove a workflow
obstacle after a smoke has been reviewed.

## Authority and continuation

The user has requested the experiment pipeline. Prepare, inspect, diagnose,
run authorized experiments, analyze, and export without redundant permission
questions. Once the human has approved comprehension and pilot scaling for the
exact smoke, continue the frozen pilot and export in the same task. An agent's
own concerns belong in the report; they are not an additional approval gate.

Reuse a matching saved approval after a disconnect. A changed notebook cell
number, new chat, new documentation, or new analysis directory does not by
itself require another human review. Never pretend an AI draft is a human review.
If the user explicitly approves an identified run in chat, record the judgment
faithfully with its provenance; do not infer acceptance from a generic request
or from a signature on a rejected review. Resolve contradictions with one precise
question citing the actual file and false field. Do not invent an error-rate
threshold that silently overrides the human's decision.

## Establish the exact state before GPU loading

Read the current live notebook and Drive artifacts, not just this historical
handoff. Record the notebook URL, source root, results root, smoke ID, pilot ID,
review path, raw digest, config, resolved model revision, and runtime metadata.
Drive root is normally `/content/drive/MyDrive/normative-hysteresis-v0/results`.
The historical notebook is
https://colab.research.google.com/drive/117HBfMbsEcOQUzAMeVzD13eDarLVCVs6 .
Do not assume it is the newest notebook.

Inspect `manifest.json`, `complete.json`, `review_approval.json` if present,
and the human's `smoke_review.json`. Search the run's derived directories for
existing signed reviews before presenting another blank template. Search
`*review*.json`, including `smoke_review-TO_UPLOAD.json`; the latest signed
separated-002 review uses that filename. The clarified review still has a
placeholder digest, so verify provenance separately from a signature. Inspect
actual reviewer, both decision Booleans, all trajectory notes/reviewed flags,
ID, and digest. Preserve rejected reviews and raw records.

If the smoke is approved, restore its frozen source and config. The runner
requires exact backend metadata including GPU/library versions: use the recorded
runtime when available. If it cannot be reproduced, report the specific differing
fields; do not repeatedly suggest signing the unchanged review again.

## Resume an existing approved run

Use the original experiment's source snapshot. Transfer only the standalone
`scripts/notebook_workflow.py` helper into that snapshot's `scripts/` directory
if it is missing; do not overwrite the package. Confirm imports point into the
frozen snapshot. After Drive is mounted and the matching backend restored:

```python
from pathlib import Path
from scripts.notebook_workflow import ensure_smoke_approval
from corrigibility_bench.runner import run_experiment

# Assign the actual verified run paths/config/backend. Do not copy example IDs.
smoke_run = RESULTS_ROOT / "raw/normative_hysteresis" / SMOKE_ID
# Empty REVIEW_FILE is allowed only when review_approval.json already exists.
approval_path = ensure_smoke_approval(smoke_run, REVIEW_FILE)
pilot_run = run_experiment(
    backend, config, mode="pilot", results_root=RESULTS_ROOT,
    experiment_id=PILOT_ID, smoke_run=smoke_run,
)
```

For the old appended notebook, the corresponding variables are
`corrected_smoke_run`, `reviewed_backend`, `reviewed_config`, and
`corrected_pilot_run`. Bind them explicitly; do not mix them with original globals.
The helper verifies the source and review; `run_experiment` additionally validates
the actual loaded backend against smoke before any pilot call.

Use the same pilot ID to resume interrupted calls. No concurrent runner for that
ID. If `.runner-lock` remains after a dead session, establish that no runner is
active before removing only the empty lock. Preserve corruption and report it.
Never delete manifests or approval records to make a mismatch go away.

## New experiment or changed protocol

Finish source changes first. Preserve the user's stimulus edits; changing them
requires a new experiment ID and a documented protocol change. Current working
source changes shipping Elm reliability to 60 and rotates labels with fixed row
order. It does not counterbalance positions. Do not describe it as the original
label-plus-reversed-row design or pool it with that design.

Run locally, without weights:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/build_colab_notebook.py
.venv/bin/python scripts/validate_colab_notebook.py
```

Upload the generated notebook to Colab. Use one consistent extracted source;
if extraction detects a differing existing file, preserve that directory and
use a fresh runtime/source directory. Do not bypass the checksum or overwrite
source. Pin the resolved model revision and use fresh smoke/pilot IDs.
Run setup and `verify_generation_policy(backend, config)` from
`scripts.verify_generation_runtime`: six configurations must pass. Then smoke
is 32 trajectories / 108 calls. Audit all planning and both sibling outputs,
raw count/digest, config, truncation, and mechanical labels before human review.
Do not run repeated identical greedy smoke tests hoping to fix comprehension.

The pilot is 432 trajectories / 1,440 calls. Once the exact smoke is approved,
set `RUN_PILOT=True` and execute the pilot, analysis, audit, and export cells.
No automatic expansion beyond that frozen grid. If review remains rejected,
export the completed smoke and state the actual remaining human decision or
protocol repair needed; do not report a pilot as complete.

## Completion and handoff

Verify raw call count, completion digest, saved effective generation settings,
model/source metadata, and no unreported errors. Analyze per scenario and variant;
inspect the selected pilot transcripts and preserve AI notes separately from
human judgments. Export raw runs, reviews, manifests, exact source snapshot,
derived artifacts, and executed notebook to Drive. No weights/caches/tokens in
exports. State which real runs completed, which are partial, and which tests are
synthetic. Save exact paths and next action in `docs/RUN_HANDOFF.md`.

When blocked, report the failed predicate, evidence, what remains possible, and
one concrete next action. “Needs human review” is inadequate if a matching
approval already exists. Do not ask for permission to do routine authorized
recovery work.
