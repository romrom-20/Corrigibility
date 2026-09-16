# Normative hysteresis: validate execution before another pilot

Objective replication is complete: **487/512 correct decisions**, with 24 of 25
failures concentrated in one label rotation. The data do not establish a
self-justification effect. Numerical-comparison prose did not reliably fix errors.
Read [results](docs/history/OBJECTIVE_REPLICATION_V1_20260916.md) and
[version history](docs/EXPERIMENT_HISTORY.md).

Next: [execution-readiness Colab notebook](notebooks/normative_hysteresis_execution_readiness_colab.ipynb).
Upload this single file to hosted Colab. **No weights or inference on the Mac.**
The new protocol has not yet run on a real model.

`nh-execution-readiness-v1` compares historical rowwise answers with model-produced
eligible rankings and explicitly checks final-choice consistency. It restores fresh
A/B/X/Y execution checks and retains all historical numeric/presentation cases.
Screen: 768 calls. A passed fixed readiness screen permits 512 separate confirmation
calls. A failed screen still exports. Neither stage runs the main pilot.

- [Design, diagnosis and fixed readiness criteria](docs/EXECUTION_READINESS_PLAN.md)
- [Colab agent assignment](docs/NEXT_AGENT_PROMPT.md)
- [Current handoff](docs/RUN_HANDOFF.md)

Historical notebooks and scores remain frozen. No answer substitution, retries of
wrong outputs, exclusion of failed items, automatic pilot or significance claim.
Passing fresh execution still requires history/update validation before a new pilot.
