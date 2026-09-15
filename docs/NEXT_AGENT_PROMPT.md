# Next agent: bounded objective replication in hosted Colab

Implementing commit: c994b6f. Use the latest notebook on review-pasted-text,
including the subsequent handoff update. Read EXPERIMENT_HISTORY.md,
history/OBJECTIVE_TRANSFER_V1_20260915.md and OBJECTIVE_REPLICATION_PLAN.md first.

## What happened and what we are testing

Transfer v1 completed 128 trajectories / 320 calls on A100. Final B choices were
117/128 correct; all state reports, copied values and eligibility masks were
correct. Ten old-option errors remained, eight in order 3 and nine choosing NORI.
Depth-one self old choices were 2/16 versus 1/16 for each control. The self/fresh
gap was already one case at depth zero. This does not establish self-investment
hysteresis. The pasted records reproduced; original archive integrity was not
independently verified. Factual controls remain unresolved.

The user authorized building this bounded diagnostic. Execute the prepared
nh-objective-replication-v1 notebook; do not reopen old smoke signoff gates or
require old human approval to cover new prompts. Do not invent human judgments.
This authorization does not imply an automatic larger study or D run.

## Exact run

Upload notebooks/normative_hysteresis_objective_replication_colab.ipynb alone to
hosted Google Colab. NO local runtime, model weights or GPU work on the Mac.
Select the hosted GPU before model loading; record actual hardware. Use the
existing HF secret without printing it. Pinned Qwen3-8B revision, NF4, non-thinking,
temperature 0.7; preserve config/runtime. Run notebook cells top to bottom:
extract/check bundled source, install, offline tests/design audit, mount Drive and
back up sources, load model, run, analyze and export. No live model run has been
performed by the implementation agent; synthetic notebook validation is software
verification only.

Default RUN_ID: objective-replication-001.
Budget: 512 trajectories / 1536 calls. Two numeric items, four row orders, four
cyclic label rotations, four conditions, depths zero/one and two seed replicates.
There are 256 planning, 512 original behavior, 512 state and 256 comparison calls.
The comparison sibling runs on EVERY depth-one trial, not just failed trials.
Its prompt asks for explicit numerical comparison; its response never enters
baseline behavior or the state probe. All original prompts remain unchanged.

Drive root: /content/drive/MyDrive/normative-hysteresis-v0/results
Raw: raw/objective_replication/objective-replication-001/records/
Derived: derived/objective_replication/<RUN_ID>/<analysis-ID>/

## Resume and completion

Saved per-call JSON is reused only with exact source/config/model/runtime. After
a disconnect, check whether the original process is still running before starting
another. Restore the exact notebook/environment and rerun setup/load/run. Never
retry wrong answers, delete records, repair planning prose or filter failed plans.
If .runner-lock remains after an actual process death, verify no runner is active
and remove only that empty lock directory. A changed runtime needs a new run ID;
do not silently mix hardware or append incompatible calls. Preserve completed runs.

## Audit and report

Review summary.json, trials.csv, comparison_trials.csv, design_audit.json and all
transcripts. Check fresh baseline and initial A competence first. Inspect original
self-minus-fresh/describe/other by depth and descriptive_contrast_depth_change.
Inspect item/order/rotation/replicate strata and joint combinations. Count selected
labels, mask/copy/minimum errors, old optima versus traps, truncation, invalidity,
and repetitions of actual recommendations. Retain every primary denominator.

Compare comparison success with original success, including both fixed errors and
newly harmed successes. Keep branches separate; do not substitute corrected
answers into baseline results. Its state probe describes common pre-intervention
context, not post-comparison uptake. Seeds differ between branches, so individual
fixes cannot identify a causal mechanism. Manually inspect numerical comparisons
in brief_reason and neutral/descriptive planning instructions. Report uncertainty;
do not hunt for a positive seed, suppress failures or expand automatically.

Two affine numeric instances are one task structure. A label/order effect is not
internal commitment, and correct state reports are not proof of understanding.
No factual specificity or population claim. Preserve negative/inconclusive results.
Broader task variation and repaired factual controls precede any full study.

Deliver the raw/source/derived ZIP and executed notebook, live Colab URL, source
bundle and backup path, actual runtime, run ID, completion digest, artifact paths,
counts and substantive errors. Keep AI audit notes separate from human judgments.
