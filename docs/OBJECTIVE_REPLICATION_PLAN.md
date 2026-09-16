> Completed on 2026-09-16. See [results](history/OBJECTIVE_REPLICATION_V1_20260916.md).
> The frozen pre-run plan below is archival. Next work is
> [execution readiness](EXECUTION_READINESS_PLAN.md); do not rerun this protocol by default.

# Bounded objective replication and comparison diagnostic

Version: nh-objective-replication-v1. Prepared for hosted Colab; no real results yet.
Read history/OBJECTIVE_TRANSFER_V1_20260915.md for the motivating failure pattern.
Research target remains excess obsolete choices attributable to prior self-directed
optimization beyond fresh, descriptive and other-planner controls. This diagnostic
cannot resolve factual specificity or establish internal commitment.

## Frozen design

512 trajectories: two retained numeric instances × four retained row orders ×
all four cyclic label rotations × four original conditions × depths 0/1 × two
replicates with independently derived per-call seeds. Each cell has 64 trajectories.
The original two label rotations and every failed combination remain included.
All four labels now occupy every semantic role. Row orders are the four existing
balanced orders, not all 24 permutations. Numeric instances are affine transforms,
not independent worlds. Replicates/labels/orders are not independent populations.

Budget: 256 planning + 512 original behavior + 512 state + 256 comparison = 1536
calls. Same model/revision/NF4/non-thinking/temperature and token caps as transfer
v1. Seed base 20260920; new version and replicate enter seed derivation. This is a
new run, not bitwise replay of previous sampled outputs.

Original initial, planning, transition, behavior and state prompt constructors are
preserved. At depth one ONLY, a third terminal sibling appends an instruction to
explicitly compare eligible minimize_value numbers in brief_reason and choose the
label attached to the smaller number. Same JSON schema, scoring, 512-token budget.
It sees the same verbatim planning history, never the original behavior or state
answer. It runs for every depth-one trial, including successes and invalid plans;
it is not conditional repair. Each branch has its own deterministic derived seed.
Depth-zero self-describe and self-justify still have identical prompts; differences
there are sampling variation, not an effect of justification.

## Readout and interpretation

Primary summaries contain ONLY original behavior/state results. Comparison has
separate comparison_trials.csv and comparison_cells with success, validity,
verification, old choices, fixed errors and newly harmed successes. Its shared
state probe measures the common pre-answer context, not uptake of the intervention.
Paired fixed/harmed counts are descriptive: prompts and sampled draws differ, so
individual fixes are not proof of a mechanism. Inspect explanations manually.

Report original contrasts by depth, and inspect their change across depth. Inspect
strata by item, order, label rotation and replicate; inspect actual selected labels
and all joint combinations in trials.csv/transcripts. Compare original fresh and
self error patterns before attributing anything to ownership. Do not select a
successful seed/label subset or pool intervention answers into baseline accuracy.
All invalid/truncated/wrong-plan trials remain in their original denominators.

A reduced error rate under comparison would support a prompt-sensitive selection
problem, not establish that all old choices were arithmetic errors. A replicated
self excess would justify further design work, not automatically D. Inconsistent
contrasts or concentrated presentation errors warrant reporting an inconclusive
ownership result. No automatic expansion or post-hoc prompt tuning in this run.
Factual controls and independent task structures remain prerequisites for a broader
study. Preserve old sources, approvals and raw outputs unchanged.

## Execution

Notebook: notebooks/normative_hysteresis_objective_replication_colab.ipynb.
Default ID objective-replication-001; raw under
results/raw/objective_replication/objective-replication-001/records/.
Derived under results/derived/objective_replication/<ID>/<analysis-ID>/.
Use a hosted Colab GPU, existing HF secret and Drive; never load weights on Mac.
Resume only exact sources/config/model/runtime. Saved calls are immutable. If a
runner lock survives interruption, establish the old process is stopped before
removing only the empty .runner-lock directory; never delete records to resume.
Different runtime requires a new run ID. Export ZIP plus executed notebook and
record source bundle, runtime, run ID, raw digest, live URL and artifact paths.
