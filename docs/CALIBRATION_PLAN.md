> Historical protocol reference. The current next task is in [READINESS_PLAN.md](READINESS_PLAN.md) and [NEXT_AGENT_PROMPT.md](NEXT_AGENT_PROMPT.md). Do not execute this older protocol by default.

# Calibration plan — nh-calibration-v1

Read history/DIAGNOSTIC_V2_20260915.md first. The evidence supports investigating
filtering and probe measurement failures; it does not establish the model's internal
cause. This calibration is separate from frozen v2. Do not pool their results.

## Questions and controlled comparisons

Selection calls use the unchanged four tables, both paired label/order variants,
and initial A, final B and final factual Y rules, each without previous-objective
history. Four formats share the same rule and values:

1. `shortlist`: the exact v2 output instruction on a standalone task.
2. `shortlist_reworded`: only its first sentence changes to "Evaluate each of the
   four rows; include only those that pass the eligibility condition."
3. `rowwise`: every row, copied values, an explicit eligibility Boolean, then a
   choice. Score incorrect inclusion and omission separately from ranking.
4. `ranking_only`: the computer supplies only truly eligible rows and the attribute
   to minimize. This deliberately removes filtering and irrelevant columns; it is
   a component capability check, not a clean single-factor prompt ablation or
   evidence that the model can solve the whole task.

The first pair isolates one sentence. Rowwise changes the output scaffold and
ranking-only changes the supplied information. Do not attribute their differences
to a single word or equate their tasks. No answers or correct masks are supplied
in the full selection conditions. No generated response feeds another call.

Probe calls contain the fixed objective and fact declarations, without a numerical
option table. Compare the unchanged v2 legacy probe against a state probe asking
for `earlier_fact`, `current_fact`, and `current_limit`. Five contexts are fresh X,
fresh Y, X→Y, Y→X, and retained X. The retained-X context supplies a true case for
"previous fact still governs"; the two fresh contexts require earlier_fact=NONE.
Current labels vary. The state probe reports the numeric value independently of
label naming. This tests probe responses on these simplified contexts; it does
not establish behavior-branch understanding or identify a unique linguistic cause.

## Frozen scope and scoring

272 independent calls: 4 scenarios × 3 rules × 2 variants × 4 selection formats ×
2 replications = 192; 4 scenarios × 5 contexts × 2 probes × 2 replications = 80.
Temperature 0.7, top_p 0.8, top_k 20, pinned Qwen3-8B, NF4, non-thinking as before.
All selection formats have a 512-token cap; both probes 160. Context limit 4096.
The selection cap is a change from v2, shared within this calibration; comparisons
with the old run are not controlled decoding comparisons. Record all truncation.

No retry, correction, answer repair or exclusion. Invalid responses stay in N;
component failures for invalid responses count zero in summaries. Missing metrics
for an inapplicable format remain absent. false_positive_rows/false_negative_rows
are counts of errors on parseable lists/masks, not rates with a fabricated zero
for unreadable responses; inspect schema validity alongside them. All-trial
fully_correct and choice_correct retain invalid responses as failures.

`design_audit.json` reports true old/final optima, unfiltered minima and collisions.
Shipping factual has old optimum = unfiltered final minimum. Venue/production
objective tasks have final optimum = unfiltered final minimum. All three fail
three-way separation for different reasons. Preserve it as a diagnostic item;
this calibration makes no hysteresis claim. Before another hysteresis design,
resolve that collision in a new version and verify optima mechanically. Repeated
unfiltered errors and actual prior recommendations must remain separate outcomes.

## How results determine the next task

- If the one-sentence change improves set correctness, consider that wording for
  a new, separately validated protocol. Two observations per cell are only screening
  evidence; inspect both variants and every raw response.
- If rowwise masks are wrong but copied values and ranking-only choices are correct,
  filtering/comparison is the bottleneck. If masks are correct but final choices
  are wrong, examine minimization/integration. If rowwise alone works, explicit
  classification may be useful scaffolding, with a changed experimental estimand.
- If ranking-only also fails, reassess basic task competence in this configuration
  before changing the hysteresis manipulation. Any model/precision comparison is
  a separately labeled experiment, not a larger-GPU promise of higher accuracy.
- If state probes succeed where legacy fails, retire the ambiguous Boolean only
  in a new protocol. If current_limit or reversed-label answers fail, do not treat
  the probe as a comprehension control. Examine individual components, not only
  pooled all-fields-correct scores.
- Do not demand nonzero residue, tune until an effect appears, discard failing
  worlds, or immediately expand repetitions. There is no automatic pass threshold
  and no D/pilot cell in this notebook.

## Colab execution and recovery

Upload `notebooks/normative_hysteresis_calibration_colab.ipynb` alone to hosted
Colab. Run extraction, dependency install, offline checks, Drive/source backup,
model load, calibration, analysis and export. Use `calibration-001`; reuse it only
for the exact same source/config/model/runtime. All GPU work stays on Colab.
There is no human smoke-review prerequisite for these calibration calls. They do
not approve a later hysteresis pilot. Never fabricate or alter human approvals.

Resume from the exact notebook and restore runtime metadata. Calls save to
`/content/drive/MyDrive/normative-hysteresis-v0/results/raw/calibration/calibration-001/records/`.
Derived outputs are under `results/derived/calibration/calibration-001/<analysis-id>/`.
Keep `cases.csv`, `summary.json`, `design_audit.json`, `transcripts.html`, raw records,
source backup and ZIP export. Save an executed notebook as well. Do not run two
runners for the same ID. Remove a stale empty lock only after verifying its runner
has stopped. Preserve corrupted files; use a fresh ID when settings differ.

Local software checks, with no models:

```sh
.venv/bin/python -m unittest discover -s calibration_tests -v
python3 scripts/build_calibration_notebook.py
.venv/bin/python scripts/validate_calibration_notebook.py
```
