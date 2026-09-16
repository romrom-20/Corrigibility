# Next agent — component diagnosis, hosted Colab only

Read EXPERIMENT_HISTORY.md, history/EXECUTION_READINESS_V1_20260916.md, and
COMPONENT_DIAGNOSTIC_PLAN.md. The execution screen is COMPLETE (768 T4 calls).
The ranked candidate FAILED; confirmation and D must not run. This is a new,
bounded 480-call diagnostic requested after reviewing the raw failures.

What we learned: ranked B copied values/eligibility correctly but reversed 17 pairs;
14 final choices wrong, three correct despite reversed ranking; two omitted labels.
Factual rules exclude 114 truly eligible rows, all strictly below time limits, and
also misselect with correct masks. All 11 failed state probes merely copied the
rule-name placeholder; numerical criteria are correct. Scores remain frozen.
Do not call these fresh failures self-investment or factual-update hysteresis.

Upload notebooks/normative_hysteresis_component_diagnostic_colab.ipynb alone to
HOSTED Colab. No model weights, inference dependencies or local runtime on the Mac.
Use existing HF secret without printing it. Prefer T4 to match the prior screen;
keep pinned Qwen3-8B/NF4/non-thinking and frozen config. Record actual GPU/runtime.
Run cells top to bottom: extract, install, offline tests, mount Drive/source backup,
load only if incomplete, run/resume, analyze, export. No real run yet: synthetic
validation is software evidence, not model results or human approval.

Default RUN_ID components-001. 480 independent calls: eligibility 128, comparison 288,
state 64. Component prompts are deliberately simpler than full tasks. No prior
answers or computed solutions enter prompts, no retries, no automatic next stage.
The typed state template is prospective; do not change old scores or gates.

Drive root /content/drive/MyDrive/normative-hysteresis-v0/results
Raw raw/component_diagnostic/components-001/records/
Derived derived/component_diagnostic/<ID>/<analysis-ID>/
Sources source_snapshots/<BUNDLE_SHA256> beside results.

On interruption, check whether another session is active before resuming. Saved
calls are immutable. The runner explains exact source/config/runtime mismatches;
restore the saved environment or use a new ID, never overwrite the manifest.
If an old runner is definitely stopped, remove its lock using
cal.recover_lock(run_folder, confirmed_stopped=True). This is never automatic.
Missing/changed lock during active work stops generation. A completed run can
validate/export without loading the model; use the notebook's completed-run path.
Do not copy these new runner functions into the historical source snapshot.

Audit all failures and correct examples. Report each component/variant separately,
rule/item/row and metric/pair/direction strata, and state identifier versus criterion
accuracy. Check JSON/schema/truncation errors. Matched pairs use different sampled
draws; report fixes AND harms, never claim individual fixes prove a mechanism.
Numeric prompts can repeat: do not count repeated prompts or four numeric tables
as independent task families. Label mapping and schema differ together in the
labeled comparison arm. Context load changes in eligibility. Interpret accordingly.

No thresholds here authorize a main pilot. If elementary components fail, identify
which and reassess task/model suitability. If they pass, investigate composition
in a future frozen full-task design, preserving factual controls and the original
ownership question. Do not repeatedly tune to pass, select favorable cases or
require a positive effect. Existing user authorization covers this bounded run;
old human signoffs remain attached to old prompts. Never invent human judgments.

Deliver ZIP (source/raw/derived), executed notebook, live URL, bundle/backup, actual
runtime, run ID/digest, artifact paths and substantive diagnosis. Stop GPU calls
at 480. Do not rerun execution-screen-001 or launch its failed confirmation.
