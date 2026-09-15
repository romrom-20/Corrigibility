# Normative hysteresis — bounded objective replication

Objective transfer v1 is complete: 117/128 final choices were correct, with all
state reports and eligibility masks correct. Remaining old-option errors cluster
by row order and label; self-planning hysteresis has not been established.
Read [findings](docs/history/OBJECTIVE_TRANSFER_V1_20260915.md) and
[version history](docs/EXPERIMENT_HISTORY.md).

Next notebook: [objective replication](notebooks/normative_hysteresis_objective_replication_colab.ipynb).
Upload it alone to hosted Colab. No weights or inference on the Mac.
This prepared version has not run on a real model yet.

`nh-objective-replication-v1`: 512 trajectories / 1536 calls, all four cyclic label
rotations, four row orders, two seed replicates, four conditions and depths 0/1.
Original prompts are retained. Every depth-one trial gets an additional independent
comparison sibling, scored separately. This is a bounded diagnostic, not D.

- [Experiment plan](docs/OBJECTIVE_REPLICATION_PLAN.md)
- [Next agent assignment](docs/NEXT_AGENT_PROMPT.md)
- [Current handoff](docs/RUN_HANDOFF.md)

Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7. ID objective-replication-001.
All failures stay included. Preserve exact source/config/runtime on resume and all
historical artifacts. Factual specificity is unresolved; no automatic larger run.
