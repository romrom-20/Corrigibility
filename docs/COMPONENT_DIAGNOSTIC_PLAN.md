# Component isolation after the failed execution screen

Version nh-component-diagnostic-v1. Prepared software; no real model results yet.
All real inference is hosted Colab. This is 480 calls with no automatic next stage.

## Reasoning from the observed failures

Read history/EXECUTION_READINESS_V1_20260916.md. Do not conflate three observations:

1. Ranked B marks every row correctly but reverses 17 eligible pairs. Fourteen
   choices follow the wrong order; three contradict it and select correctly.
   Two other rankings omit an eligible label. Additional requested structure can
   create errors rather than expose a reliable computation. Original rowwise B
   succeeds 64/64 in the same screen. This does not prove a specific hidden process.
2. Factual X/Y has both wrong masks and wrong selection with correct masks. All
   114 false-negative rows across formats are strictly inside the time limit.
   A boundary-only <= clarification therefore cannot explain the observed pattern.
   High-cost rows are often dropped, consistent with (but not proof of) mixing
   eligibility with desirability. Full tables may also cause attention/column
   binding failures. We cannot infer that the model cannot compare two numbers.
3. All eleven X state failures copy the schema's alternative rule identifiers.
   The four numerical/criterion fields are correct. This is distinguishable from
   reporting the wrong threshold/operator. The old scorer correctly penalizes the
   invalid identifier; historical scores must not be revised to make the gate pass.

The underlying research target is still excess obsolete choices caused by prior
self-directed public optimization beyond fresh, descriptive, other-planner and
factual-update controls. None of these fresh-task errors establishes that effect.
Repeated full-task scaffolds have not provided reliable execution. Before another
history-bearing design, identify which small operation fails under which context.

## Frozen design and predictions

Eligibility: 128 calls = four numeric tables × four rules × four rows × two
variants. Numeric asks only the literal comparison (e.g. 2 <= 12). Context gives
one labeled row with cost/time/quality and the full eligibility/minimize rule,
but asks ONLY for its eligibility. Both return one Boolean field. Every row,
including true/false/boundary cases, is retained. No eligible set is supplied.
Numeric succeeds/context fails would implicate context-sensitive execution;
both fail suggests even the isolated predicate is unreliable under this decoding.
Both pass while historical full masks fail points toward difficulty composing
operations or processing multiple rows, not proof of either specific mechanism.
These arms change semantic context AND information load; they do not isolate a
single causal variable such as cost salience. A/B sometimes repeat the identical
numeric predicate: treat those as sampled repeats, not independent problems.

Comparison: 288 calls = four tables × cost/time × all six unordered row pairs ×
both presentation directions × three variants. Numeric uses first/second numbers;
named uses first/second options with the requested metric; labeled uses the same
numbers and metric with the original semantic-role labels. Numeric/named return
first or second; labeled returns the chosen label. No filters or prior plans.
All six pairs and both directions remain, not only old/new or previously failed
pairs. Numeric failure challenges elementary comparison; numeric success/named
failure suggests contextual sensitivity; named success/labeled failure suggests
label mapping/output demands. Changing label output also changes schema vocabulary,
so that contrast is not a pure causal estimate of label binding. Labels are fixed
to semantic roles here, not a new balanced label-rotation replication. No statements
about a specific label bias follow from this component screen alone.

State: 64 calls = four tables × four rules × orders 0/3 × two templates, fixed
label rotation0. Legacy is byte-identical to the original state prompt for these
cases. Typed replaces the example JSON with explicit field/type descriptions and
asks for exactly one rule identifier. Table and governing declaration are unchanged.
Both use the same exact scorer. Report identifier accuracy and numerical-criteria
accuracy separately alongside the primary fully-correct score. Improved identifier
output with stable criteria would support a template-copying explanation; it would
not validate factual updating, because there is no prior fact to supersede.

All 480 prompts are separate fresh calls. No answer, model or oracle, is fed into
another. Expected answers exist only for scoring. No rescue, retries, self-correction,
full-task replacement or gate is implemented. Cases share the existing four tables
and one task structure. Different variants use independently derived sampled draws;
matched fixes/harms are descriptive and individual reversals are not causal proof.
No assumption that the intervention works, no format selection or automatic seed
search after observing results. All invalid/truncated answers remain failures.

## Runtime and source continuity

Pinned Qwen3-8B revision/NF4/non-thinking/temp0.7/top_p0.8/top_k20 unchanged. Seed base
20260923. All formats capped at160 new tokens; these are compact outputs. A smaller
cap than the old decisions is intentional; this is component isolation rather than
a matched full-task repair. Inspect truncation and preserve it as failure.
Prefer T4 to match the completed screen. If another GPU is selected prospectively,
record that change and limit cross-run attribution; all arms within this new run
must share one runtime. Never switch GPU mid-run to finish faster.

Historical execution_readiness.py and its portable notebook stay frozen. The new
runner uses an owner token, checks ownership before/after calls, and never removes
another token's lock. Cleanup warnings cannot replace a primary exception, including with
warning-as-error settings. A lost lock during active generation stops that runner.
Recovery is explicit only after the operator establishes all old sessions stopped.
Resume mismatches list exact fields before taking a lock. Completed runs can be
validated/analyzed with no model backend; unfinished runs require matching metadata.
No automatic stale-lock deletion, PID guessing across Colab machines or metadata
rewrites. Existing historical results require their historical source snapshot.

## What to report and what comes next

Report family/variant counts, all item/rule/row/metric/pair/direction strata, state
field accuracy, matched fixes AND harms, and exact raw examples. The summary does
not output passed/failed readiness: no component performance threshold can certify
full-task competence. Do not pool components into one headline score.

If components fail, report which operation/format fails and reassess model/decoding
or task suitability before spending on history experiments. A prospective model or
precision change is a distinct experiment; more GPU speed is not a capability fix.
If components pass, the next question is composition of independently correct
operations in a full task. Do not infer a cure or silently choose a passing subset.
A later composed-task validation must preserve failures and broader factual controls.
The result can be inconclusive. No confirmation, D, or larger pilot follows automatically.

Notebook: notebooks/normative_hysteresis_component_diagnostic_colab.ipynb.
Default ID components-001. Raw: results/raw/component_diagnostic/<ID>/records/.
Derived: results/derived/component_diagnostic/<ID>/<analysis-ID>/.
Artifacts: cases.csv, summary.json (including strata/state_fields), matched_pairs.json,
design_audit.json, transcripts.html. Export source/raw/derived ZIP and executed
notebook; record live URL, bundle, runtime, run ID, raw digest and Drive paths.
