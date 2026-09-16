# Current handoff — fresh execution readiness before another pilot

**Objective replication is complete. The new execution-readiness protocol has not
run on a real model.** See NEXT_AGENT_PROMPT.md for the executable assignment and
EXECUTION_READINESS_PLAN.md for the design and exact readiness tolerances.

Upload `notebooks/normative_hysteresis_execution_readiness_colab.ipynb` alone to
hosted Colab. Protocol `nh-execution-readiness-v1`. No local weights or inference.
Screen `execution-screen-001`: 768 calls (rowwise/ranked/state, A/B/X/Y, all crossed
items/orders/rotations). If the fixed ranked/state screen passes, confirmation
`execution-confirm-001`: 512 additional calls with separate seeds. Max 1,280.
Failed screen skips confirmation and still exports. Neither stage launches a pilot.

Model-produced ranked eligible labels make selection/choice contradictions
measurable. The scorer never supplies or substitutes the answer. Historic numeric
items and every presentation cell stay included; two additional non-affine tables
remain the same task structure. Factual execution is tested again; actual factual
supersession and history-bearing competence remain future validation requirements.

Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7. Decision/state caps 768/160.
Drive root: `/content/drive/MyDrive/normative-hysteresis-v0/results`.
Raw: `raw/execution_readiness/<ID>/`; derived: `derived/execution_readiness/<ID>/<analysis-ID>/`.
Source backup: `source_snapshots/<BUNDLE_SHA256>` beside results. Record the bundle
from notebook setup. Restore exact source/config/runtime for resume. Never delete
records, retry failures, bypass locks or recycle historical review approvals.

Replication findings: 487/512 correct baseline decisions, all state probes correct,
24/25 errors in one label rotation; explicit comparison fixes 3 and harms 5.
The pasted records match prompts/parsers/seeds/decoding/counts. Original archive
bytes were not supplied. See history/OBJECTIVE_REPLICATION_V1_20260916.md.
This is a task-execution validity issue, not a newly established backend bug.

Local software tests and the portable synthetic validator cover both passing and
failing routes, conditional confirmation, interruption/resume and export. Synthetic
answers are explicitly labeled and are not evidence that Qwen passes the new task.
After Colab, record live URL, actual runtime, source bundle/backup, IDs/digests,
ZIP/executed notebook paths, every denominator and the observed readiness outcome.
