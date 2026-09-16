# Next agent: execution readiness in hosted Colab

Use **notebooks/normative_hysteresis_execution_readiness_colab.ipynb** from the
current workspace branch. Protocol `nh-execution-readiness-v1`. Read
EXPERIMENT_HISTORY.md, history/OBJECTIVE_REPLICATION_V1_20260916.md and
EXECUTION_READINESS_PLAN.md first. Do not run the old replication notebook again.

## What happened

Objective replication COMPLETED: 512 trajectories / 1,536 calls, 487/512 verified
B choices, 512/512 state reports. Twenty-four of 25 behavioral failures share one
label rotation. All failures have correct copied numbers/masks but wrong selection.
Self/control differences are tiny; no established self-justification effect.
Comparison prose fixes three and harms five. The pasted-record audit matches code;
original archive integrity was not independently verified. Earlier factual controls
failed. The early decoding-default bug is already fixed, not a newly diagnosed
cause of these errors.

## Authorized next work

The user requested understanding the versions, implementing a repair and preparing
this handoff for Colab. Execute the prepared finite fresh-task diagnostic when
assigned to run it. Do not reopen old signoff gates, invent a human review, or
interpret the new software as approval of an unseen pilot. This notebook contains
no main pilot. No positive hysteresis result is required.

The candidate asks the model for a sorted `ranked_eligible` list before its choice.
Scoring checks the list and choice independently; it never changes a wrong answer.
The historical rowwise reference and independent state probe stay separate. Both
objective A/B and factual-rule X/Y prerequisites are included. There are no prior
plans or fact updates in this stage; factual supersession remains future work.

## Exact execution

1. Upload the single new notebook to hosted Google Colab. Select a GPU first;
   no local runtime, model weights or GPU work on the Mac. Reuse the existing HF
   secret without printing it. Preserve pinned Qwen3-8B/NF4/non-thinking/0.7 settings.
2. Run top to bottom: extract and verify bundle, install, offline tests, mount
   Drive, back up exact source, load the model, screen, conditional confirmation,
   export. Record actual hardware and library metadata. Restart if another
   notebook's modules are already imported; do not bypass the source check.
3. Default screen ID `execution-screen-001`: **768 calls**. Four numeric tables,
   four row orders, four cyclic label rotations, four rules, three formats.
   Tables 0/1 preserve historical numbers; 2/3 are non-affine numeric additions,
   still one underlying task structure. Decision caps 768 in both formats, state 160.
4. The candidate is fixed as ranked, never whichever format happens to win.
   Require ranked AND state to reach 15/16 verified untruncated per item/rule
   and 61/64 per rule. These prospective tolerances are not significance tests.
   Wrong/invalid/truncated outputs stay in N. Do not alter thresholds after seeing data.
5. If screen fails, confirmation is skipped; continue through export. If it passes,
   the notebook runs exactly **512** fresh ranked/state confirmation calls with
   different predefined seeds, ID `execution-confirm-001`. Maximum total **1,280**.
   The runner independently validates the screen, source/config/runtime and raw
   digest. No manual gate edits. Analyze confirmation separately with the same
   tolerances; never pool it with screen to rescue a failure.

Drive root: `/content/drive/MyDrive/normative-hysteresis-v0/results`.
Raw: `raw/execution_readiness/<ID>/records/`.
Derived: `derived/execution_readiness/<ID>/<analysis-ID>/`.
Backup: `source_snapshots/<BUNDLE_SHA256>` beside results.

## Resume and failures

Reuse an ID only for the exact same sources/config/model/runtime/stage and parent
screen. Calls are immutable and resumed individually. After a disconnect establish
whether the original process is still running before launching another. Remove a
stale empty `.runner-lock` only after its process is confirmed stopped. Never
remove raw outputs/manifests, retry wrong answers or repair model-generated lists.
A different runtime requires a new screen ID and a matching confirmation run;
do not mix an old screen with a new runtime. Preserve all historical runs.

## Audit, report, stop

Review cases.csv, summary.json, readiness.json, design_audit.json, screen
format_pairs.csv and transcripts.html. Inspect every invalid/truncated/wrong or
unverified decision, every ranking/choice contradiction, and at least ten correct
examples. Inspect factual masks, equality boundaries and item/order/label strata.
Report choices AND full verification. Row-error totals need valid-response counts.
Show both fixed and harmed pairs; separate sampled draws do not identify a mechanism.
Reasons are not automatically verified. A separate correct state probe does not
prove understanding within the decision call. Old choice in A/X is correct.

If screen/confirmation fails, report the failed repair; do not keep editing prompts,
select passing labels/tables or switch models/precision during the run. If both
pass, report fresh execution readiness only. Retained-history transition and factual
update validation are still required before a main hysteresis pilot. No automatic
larger study, pilot launch, or claim of factual specificity or internal commitment.

Deliver ZIP with source/raw/derived files, executed notebook, live Colab URL,
bundle/backup, actual runtime, IDs/completion digests, artifact paths, full counts,
readiness failure reasons and substantive transcript errors. Keep AI observations
separate from human judgments. Implementation tests and synthetic notebook runs
are not model evidence; this new protocol has not yet had a live model run.
