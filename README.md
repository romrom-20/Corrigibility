# Normative hysteresis — component diagnosis

The execution screen completed all 768 T4 calls. Its ranked repair failed: fresh
B fell from 64/64 correct rowwise choices to 50/64 ranked choices; factual eligibility
also remained unreliable. The eleven failed state probes copied a rule-name
placeholder while reporting numerical criteria correctly. We have not established
self-planning hysteresis. [Findings](docs/history/EXECUTION_READINESS_V1_20260916.md).

Next prepared [Colab notebook](notebooks/normative_hysteresis_component_diagnostic_colab.ipynb):
480 independent component calls for eligibility, pairwise comparison and state
formatting. No real run yet, no automatic confirmation or pilot. All model work
stays in hosted Colab; no weights or inference on the Mac.

- [Diagnostic plan and reasoning](docs/COMPONENT_DIAGNOSTIC_PLAN.md)
- [Next agent instructions](docs/NEXT_AGENT_PROMPT.md)
- [Run handoff](docs/RUN_HANDOFF.md)
- [Full research history](docs/EXPERIMENT_HISTORY.md)

Preserve historical notebooks and exact source snapshots. Do not rerun failed
execution confirmation or scale to D. All failures stay in their denominators.
