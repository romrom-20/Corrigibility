# Next agent: objective transition feasibility

Read EXPERIMENT_HISTORY.md, history/READINESS_V1_20260915.md and
OBJECTIVE_TRANSFER_PLAN.md. The latest readiness run is complete: focused A/B
are promising, factual X/Y remain weak. Do not rerun readiness or v2 D by default.

Run the prepared nh-objective-transfer-v1 notebook in hosted Colab only:
notebooks/normative_hysteresis_objective_transfer_colab.ipynb. No weights on Mac.
Preserve historical sources, results and approvals. Use the existing HF secret
without printing it. Record the actual GPU; keep the pinned model/config/runtime.

Execute setup, tests, Drive/source backup, load, objective-transfer-001, analysis
and export. Expect 128 trajectories / 320 calls, all original readiness numeric
instances and crossed label/order variants, four objective conditions and k=0/1.
Do not retry bad answers, filter out wrong A plans, modify tables mid-run or add
replications automatically. Restore exact state and reuse calls after disconnects.

Audit the fresh-B baseline before contrasts. Check initial A recommendations,
final mask/copy/minimum correctness, old-optimum versus unfiltered-trap choices,
actual-recommendation repetition and separate state reports. Review every raw
trajectory. The terminal probe must not see the behavior answer; public planning
must remain verbatim. Neutral/descriptive prose and brief reasons require manual
inspection even when numerical scores pass.

Report self-minus-fresh, self-minus-descriptive and self-minus-other descriptively,
with raw counts and each item/label/order. The factual control failed and is not in
this feasibility run: do not claim factual specificity, generalization, internal
commitment or a complete hysteresis result. Do not call zero observations proof
of absence or insist on a positive signal. Preserve all denominators.

Export raw/source/derived files and an executed notebook. Record live URL, bundle,
runtime, IDs/digests, paths and substantive failures. Keep AI audit notes separate
from human judgments. Completion does not automatically authorize a bigger study.
If the new fresh baseline fails, investigate that failure before interpreting
transition effects. Any future full study must repair factual controls and
prespecify broader item variation, retaining the original research question.
