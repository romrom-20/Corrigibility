# Objective replication v1 — completed pasted-record review

Evidence: `.context/attachments/GamnCi/pasted_text_2026-09-16_14-43-08.txt`.
Reported raw digest: `e89452e50aa559ce792a66ca7c8bca7dcd320beb5d69a4079251eb36759d0a44`.
The attachment contains 512 distinct trajectories / 1,536 calls. Pinned Qwen3-8B,
NF4, non-thinking, temperature 0.7, A100-SXM4-40GB. No reported truncation.

`python scripts/audit_replication_paste.py <attachment>` checks all records against
frozen replication constructors: prompts, histories, branch sets, per-call seeds,
requested/effective decoding, stored hashes, parsing and main/comparison/stratum
counts. All checks passed. The original archive/manifest bytes were not supplied;
this does not certify the reported raw digest or independently verify inference.

## Findings

487/512 baseline choices and verified decisions are correct. All 512 current-state
reports are correct. Every failed baseline answer copies numbers and marks
eligibility correctly but selects the wrong minimum. Of 25 failures, 23 choose
the old optimum and two choose the unfiltered trap. Twenty-four failures have
label rotation 1; 22 select NORI and three VEX. This suggests presentation-sensitive
selection inconsistency, not an established internal cause.

Old choices at depth zero: fresh 0/64, describe 6/64, self 4/64, other 4/64.
At depth one: fresh 2/64, describe 2/64, self 3/64, other 2/64.
Self exceeds each control by one case at depth one; its old-choice count decreases
with planning. Depth-zero describe/self prompts are identical, with different
sampled seeds. There is no convincing ownership/depth pattern here.

The explicit-comparison sibling fixes three original errors and harms five
original successes. Total success declines from 245/256 to 243/256. Some reasons
name the correct smaller value/label while `choice` still selects a different
label. Others make false numerical or eligibility claims. Adding a request for
comparison in free prose did not reliably repair execution. Separate branch seeds
mean individual fixes/harms do not identify a mechanism.

## Decision

Do not scale the unchanged history experiment. Preserve this completed run and its
notebook unchanged. No newly discovered tool/backend/scoring defect explains these
records. The early checkpoint-default decoding bug was a real software issue,
already fixed; it is not evidence for attributing today's failures to the runtime.
NF4 and model capacity remain possible influences, not diagnosed causes.

Next: a prospective fresh execution screen with model-produced ranked eligible
labels, explicit ranking/choice consistency scores, the historical rowwise
reference, and both initial/final factual rules restored. Do not compute or inject
the answer for the model. Retain all historic numeric/presentation cases. Use a
fixed readiness criterion and separate confirmation seeds, not a search for a
positive hysteresis effect. See ../EXECUTION_READINESS_PLAN.md.
