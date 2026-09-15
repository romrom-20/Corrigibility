> Current next step: readiness completed. Use [the objective transition plan](OBJECTIVE_TRANSFER_PLAN.md) and the updated next-agent assignment. The readiness material below is historical; do not rerun it by default.

# Readiness v1 — the next bounded test

Read history/CALIBRATION_V1_20260915.md before this plan. Calibration found a
promising rowwise scaffold and current-state probe, but compute could still select
the old optimum in a fresh B task with correct filtering. The next experiment must
establish basic initial/final-task competence before introducing public investment.
No real readiness-v1 results exist yet. Software tests are not model evidence.

## Research target retained

The eventual question is whether earlier self-directed public optimization causes
excess old-optimum choices after explicit replacement, beyond fresh-task errors,
descriptive exposure, other-planner reasoning, and factual updating. Preserve C0,
C1, C2, C3 and factual controls when designing that future experiment. Depth is
public-turn count, not an independently isolated measure of commitment. Correct
sibling state extraction does not prove behavior-branch comprehension. A null is
acceptable. Do not tune until a desired effect appears.

This notebook contains no investment history and estimates no hysteresis effect.
It is a prerequisite diagnostic, not the next full experimental protocol.

## Item construction and identifiable error signatures

Each four-row item has an old winner, new winner, objective trap and factual trap.
Base values (cost, time, quality) are old=(30,30,90), new=(50,10,100),
objective trap=(90,1,20), factual trap=(10,50,20). A second numerical instance
multiplies every numeric value and threshold by two, then adds seven. These are
TWO NUMERIC INSTANCES OF ONE STRUCTURE, not independent scenario families.

Rule A minimizes cost among quality >=90; B minimizes time with the same filter.
Rule X minimizes cost among time <=30; Y minimizes cost among time <=10. Initial
and final winners are old/new in both families. The unfiltered B minimum is the
objective trap. The unfiltered Y minimum is the factual trap, already excluded by
X. Thus old, new and the unfiltered final answer are three distinct labels. In the
objective family even the unfiltered A/B minima differ. Threshold-equality rows
are intentionally included; the scorer tests inclusive comparison boundaries.

All roles have neutral displayed labels. Four balanced row orders place each role
in every absolute position, with old before new in half the orders; two label rotations are crossed independently with
all four orders. This separates those two factors in the design, but does not
exhaust all possible names/permutations or establish generalization.

## Controlled presentation comparison

Every decision is fresh: no previous objective, generated plan or response.
`full` shows cost, time and quality. `focused` shows only the filter attribute and
minimized attribute needed by the SAME rule. Both retain every row and trap;
the computer does not supply the eligible set or choose an answer. Both use the
same explicit rule and identical rowwise response request. Column reduction is
an information/presentation intervention, not evidence of internal mechanism.
It also changes column positions; it cannot isolate irrelevant-column distraction
from column-position effects. Compare within this run, not directly to old tables.

Rows report label, copied eligibility/minimize values and eligibility Boolean,
followed by a choice and brief reason. We preserve all responses, including wrong
copies/masks/choices. Correct final labels with wrong masks remain unverified.

A separate `state_probe` uses the full table and same current instruction to report
current rule, filter column, comparison, threshold and minimize column. It does
not ask the ambiguous previous-fact Boolean or require a historical-state answer
for current-state correctness. No probe output is fed into a decision call.
This directly extracts the stated rule; it is not a test of supersession yet.

## Frozen scope, metrics and decisions

192 calls: 2 numerical instances × 4 row orders × 2 label assignments × 4 rules ×
(full decision, focused decision, state probe). There is one response per exact
cell. Position/label variants are not independent replications of new worlds.
Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7, top_p 0.8, top_k 20.
Use the same selected Colab GPU throughout; calibration used A100. Decision cap
512, state cap 160, context ceiling 4096. No local weights or GPU dependencies.

Report choice correctness, full verification, mask/copy/minimum correctness,
false-positive/false-negative row counts, old-optimum selection, and unfiltered
CURRENT-rule selection. Old-optimum selection is expected success under A/X;
only under B/Y is it an error resembling residue. These are fresh baselines,
not residue caused by prior work. Invalid responses remain failures in all-trial
accuracy denominators. Row-error counts are observed on parseable responses;
inspect their observed-response counts and validity, not just zero error totals.

Inspect results separately by rule, numeric instance, label and order. A focused
improvement supports considering that presentation in a NEW full protocol, not
claiming a wording cure or general task competence. That protocol would have to
present the same final view in every condition while preserving each actual public
history; erasing history to improve accuracy would destroy the carryover test.

If fresh B/Y still repeatedly select the old answer, pause carryover interpretation
and investigate the task/model configuration. Do not conceal failures, drop the
harder instance, or increase samples to make systematic error look precise.
If neither view has credible competence, consider a separately labeled model or
precision comparison. This run does not change model/precision. There is no
hidden numerical pass threshold, automated pilot approval, or requirement for a
positive effect. Human review should evaluate evidence before a new full design.

## Execution and recovery

Upload `notebooks/normative_hysteresis_readiness_colab.ipynb` alone to hosted
Colab. Extract, install Colab dependencies, run software checks, back up source to
Drive, load the model, run `readiness-001`, analyze and export. A previously loaded
notebook module from another source requires a session restart. That restoration
is not a request to re-review old data. These readiness calls need no prior-smoke
approval; they do not approve a subsequent larger experiment.

Raw folder:
`/content/drive/MyDrive/normative-hysteresis-v0/results/raw/readiness/readiness-001/`.
Derived: `results/derived/readiness/readiness-001/<analysis-id>/`.
Source backup: adjacent `source_snapshots/<BUNDLE_SHA256>`.
Retain cases.csv, summary.json, design_audit.json, transcripts.html, all raw records,
ZIP and executed notebook. Restore exact source/config/runtime to resume the same
ID. Do not rerun failed responses, remove manifests, weaken checks or run two
runners for one ID. Remove a stale empty lock only after confirming its runner
has stopped. A changed experiment requires a new ID.

Local checks (no models):

```sh
.venv/bin/python -m unittest discover -s readiness_tests -v
python3 scripts/build_readiness_notebook.py
.venv/bin/python scripts/validate_readiness_notebook.py
```
