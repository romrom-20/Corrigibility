# Current handoff — readiness v1, 2026-09-15

Calibration v1 completed; its evidence was committed first as 744ae67. Read
EXPERIMENT_HISTORY.md and history/CALIBRATION_V1_20260915.md for the sequence of
findings and the original research target. Earlier sources/notebooks are retained.

Prepared next run: nh-readiness-v1, not a hysteresis pilot. Upload
notebooks/normative_hysteresis_readiness_colab.ipynb alone to hosted Colab.
Default ID readiness-001; 192 calls. No real readiness run has executed yet.
Pinned Qwen3-8B, NF4, non-thinking, temperature 0.7, caps 512 decision / 160 state.
All weights and inference stay in Colab. Calibration used A100; record the actual
selected GPU rather than assuming it. Never resume under different provenance.

Read READINESS_PLAN.md for construction, matched full/focused comparison, metrics,
limitations and recovery, then NEXT_AGENT_PROMPT.md for the execution assignment.
There is no previous-smoke approval prerequisite for this bounded diagnostic.
There is no automatic D or larger pilot. Do not repeat v2 or calibration by default.

After execution, record live URL, bundle/source-backup paths, runtime metadata,
raw/derived IDs and digests, completed calls, exported ZIP and executed notebook.
State separately what ran, what was checked, remaining failures, and the next
intervention justified by evidence. Software success does not imply model success.
