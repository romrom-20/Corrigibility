# Execution readiness before another history-bearing pilot

Version: `nh-execution-readiness-v1`. Prepared software, **not yet run on a model**.
Notebook: `notebooks/normative_hysteresis_execution_readiness_colab.ipynb`.
This is a new protocol. It does not change historical prompts, parsers or scores.

## Diagnosis across notebook versions

- v0 had a real decoding-default bug: checkpoint settings could override the
  requested smoke settings and the stored config did not reflect effective
  decoding. The existing backend now disables that merge and checks it per call.
- Shortlist v1 ran a pilot after an unrepresentative smoke. Compute competence
  failed; venue final labels hid incomplete eligible lists. More trials did not
  repair the task. Three factual planning outputs were truncated in that pilot.
- Diagnostic v2 exposed wrong initial plans and a defective fresh-fact Boolean
  probe. There was no evidence that simply increasing output length would fix it.
- Calibration favored rowwise classification, but correct copying/filtering still
  coexisted with wrong minimization, even in fresh tasks with no prior objective.
- Readiness v1 improved focused objective performance while factual X/Y each
  reached only 5/16 fully correct. Restricting subsequent work to objectives left
  factual specificity unresolved; it did not repair it.
- Transfer v1 and replication v1 preserved histories and isolated sibling probes.
  Replication is now COMPLETE: 487/512 correct decisions, 512/512 state reports,
  24/25 failures in one label rotation, negligible self/control differences.
  A numerical-comparison prose instruction fixed three and harmed five answers.

The seven historical notebooks contain frozen bundles. Different historical
source/docs are expected, not permission to rebuild them with current files.
The repository notebooks are unexecuted upload templates, not executed-run proof.
Detailed historical results and audit limits are linked from EXPERIMENT_HISTORY.md.

## Proposed repair and what it changes

The candidate retains rowwise copied values and eligibility Booleans. It adds
`ranked_eligible`, a **model-produced** ascending list of every eligible label,
before `choice`. The prompt asks for the first label as the choice. The scorer
checks the true eligible set/order, agreement with marked rows, and agreement
between the first ranked label and choice. It preserves disagreements as failures.
No program supplies an eligible set, sorts the model's output for it, overwrites
choice, retries a response or feeds an answer back. Reasons remain free text and
are not mechanically certified. The ranking is a requested public artifact, not
an inference about hidden reasoning.

The within-run reference uses the historical focused rowwise prompt. On numeric
items 0/1 these prompts and the state probes are exactly reproduced from readiness
v1. The ranked format adds one instruction and field; table and rule are matched.
Both decision formats have the SAME 768-token cap. The cap accommodates the extra
field, not a claim that old failures were truncation. State probes remain 160.
Different per-case seeds mean paired improvements/harms are descriptive.

This is a measurement/scaffolding change, not a demonstrated cure. If the candidate
fails, report that failure. Do not repeatedly reword prompts, search seeds or pick
the arm that happens to pass. A future model/precision comparison would need its
own prospective design and run IDs; this notebook does not silently change either.

## Fixed design

Screen: 4 numeric items × 4 balanced row orders × 4 cyclic label rotations ×
4 rules (A/B/X/Y) × 3 formats (rowwise/ranked/state_probe) = **768 calls**.
Each format × rule has 64 cases; each item × format × rule has 16.

Items 0/1 retain all historical numbers, including the affine transformed item.
Items 2/3 use non-affine numeric values fixed in execution_readiness.py. They are
still the same four-option selection-task structure, not independent scenario
families. The four balanced orders are not all 24 permutations; cyclic rotations
are not all name assignments. All labels rotate independently of row order.

A/B keep a quality filter and switch cost to time minimization. X/Y hold cost
minimization fixed and tighten the allowed time threshold. Both initial and final
rules appear in fresh calls. Each initial/final pair has distinct old optimum,
new optimum and unfiltered final trap; every rule includes threshold equality.
X/Y test the factual-rule execution prerequisites, **not factual update uptake**,
because this stage has no previous fact, planning or replacement history.
State probes are independent calls and their answers never enter decision prompts.

Same pinned Qwen3-8B revision, NF4, non-thinking, sampled 0.7/0.8/20 as replication.
Stage/case-derived seeds are frozen with base 20260921. No local weights/inference.

## Prospective readiness and confirmation

The ranked candidate is designated before the screen. It and the state probe
must each achieve at least **15/16 fully correct, untruncated answers per item ×
rule**, AND **61/64 per rule**. Invalid/truncated responses count as failures.
These are explicit engineering tolerances (93.75% within table and 95.3125% per
rule), not statistical confidence bounds or a guarantee of task comprehension.
They allow isolated errors while blocking concentrated failure and pooled factual
weakness. They apply only to this new protocol, not old human approvals or scores.
A passing rowwise reference never substitutes for a failing ranked candidate.

A passed screen permits exactly **512 confirmation calls**: the same full design
with ranked/state only and separate predefined seeds. The notebook executes that
finite confirmation automatically after a passing screen. It verifies source,
config, runtime, raw digest and screen scores from saved records before generation;
a manually edited readiness report cannot unlock it. Its manifest records the
parent screen ID/digest. Passing confirmation uses the same tolerances and is
reported separately. Never pool stages to rescue a failure. Maximum 1,280 calls.

A failed screen skips confirmation and still exports. A failed confirmation ends
this candidate's validation. Neither success authorizes or implements the main
pilot. Even if both pass, the next design must validate retained planning/update
histories and factual supersession under the chosen scaffold. Passing fresh tasks
cannot establish that transition baselines remain competent. Four controls,
retained public history, wrong-plan denominators and factual-update controls remain
requirements for the subsequent history-bearing study. Null effects are acceptable.

## Artifacts and local verification

Raw: `results/raw/execution_readiness/<ID>/`.
Derived: `results/derived/execution_readiness/<ID>/<analysis-ID>/`.
Defaults: `execution-screen-001` and conditional `execution-confirm-001`.
Each analysis writes cases.csv, summary.json, readiness.json, design_audit.json,
and transcripts.html; screen also writes format_pairs.csv. Summary includes
per-rule counts and item/order/rotation strata. Cases retain joint factors, mask
false positives/negatives, actual selected labels, ranking and choice checks.
Old-option selection is expected success in A/X, not residue.

Use the exact bundled sources/runtime to resume. Preserve every raw response.
Notebook backups live at `source_snapshots/<BUNDLE_SHA256>` beside results. Export
contains sources and every completed raw/derived stage. Save the executed notebook
separately and record live URL, hardware, bundle, IDs/digests and artifact paths.

```sh
.venv/bin/python -m unittest discover -s execution_tests -v
python3 scripts/build_execution_readiness_notebook.py
.venv/bin/python scripts/validate_execution_readiness_notebook.py
```

Synthetic verification exercises bad answers, false readiness, interruption,
resume, passing fixtures, conditional confirmation and both export paths. It is
software evidence only. The notebook bundled tests load no model or GPU libraries.
