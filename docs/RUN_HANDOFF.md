# Current handoff — bounded objective replication

Current implementation: c994b6f, nh-objective-replication-v1. No real model run yet.
Use the latest notebooks/normative_hysteresis_objective_replication_colab.ipynb
from review-pasted-text. It embeds the current plan, findings and agent assignment.
Run hosted Colab only; never load model weights on the Mac.

Transfer v1 is COMPLETE, not pending. Its pasted 128 trajectories / 320 calls
reproduced: 117 correct final choices, all state reports and masks/copies correct,
ten old choices and one trap. Presentation clustering and a one-case self/control
gap motivate this diagnostic, not D. Read history/OBJECTIVE_TRANSFER_V1_20260915.md.
Older calibration/readiness/factual-control findings remain in EXPERIMENT_HISTORY.md.

Follow NEXT_AGENT_PROMPT.md and OBJECTIVE_REPLICATION_PLAN.md. Budget 512 trajectories
/ 1536 calls: all four cyclic label rotations, four existing balanced row orders,
two numeric instances, two seeds, four conditions, depths 0/1. Original prompts are
preserved. An additional comparison sibling runs for every depth-one trial and is
scored separately. It never feeds back into original decisions or state probes.

Default ID objective-replication-001. Drive parent:
/content/drive/MyDrive/normative-hysteresis-v0/results
Raw: raw/objective_replication/objective-replication-001/records/
Derived: derived/objective_replication/<ID>/<analysis-ID>/
Keep pinned Qwen3-8B/NF4/non-thinking/temp 0.7 and exact sources/runtime on resume.
Source backup is source_snapshots/<BUNDLE_SHA256> beside results. A stale empty
.runner-lock can be removed only after establishing no runner remains active.
Do not delete raw responses, retry failures or recycle old approval records.

Software verification: five offline tests plus a complete synthetic notebook run,
1536 saved invalid responses, completed resume without new generation, summary,
comparison output and ZIP export. These are not model results. The notebook's
source_bundle_sha256 identifies the final portable bundle; record it from setup.

After the live run record URL, bundle, hardware/runtime, run ID/raw digest, Drive
paths, ZIP and executed notebook. Report fresh competence, original contrasts and
their depth change, label/order/seed patterns and comparison fixes AND harms.
No automatic bigger run, positive-effect requirement or factual-specificity claim.
