# Research continuity and version history

The target question remains whether earlier self-directed public optimization
causes excess selection of an obsolete optimum after explicit replacement,
beyond fresh-task mistakes, descriptive exposure, other-planner reasoning and
factual updating. We have not established that effect. Better measurement and
credible baseline competence are needed before such a claim; null results count.

1. Historical v0 smoke failures motivated explicit shortlists. See
   history/RESEARCH_NOTES_20260914.md and history/RUN_HANDOFF_20260914.md.
2. Shortlist v1 pilot completed 432 trajectories / 1,440 calls. Compute baseline
   failed; venue final labels concealed incomplete lists. See
   history/PILOT_SHORTLIST_20260915.md. Original implementation checkpoint: 63e4ac9.
3. Diagnostic v2 smoke completed 144 trajectories / 480 calls. Structured initial
   planning exposed errors; fresh-fact uptake failed systematically. No observed
   objective residue. See history/DIAGNOSTIC_V2_20260915.md. V2: 4577fc6.
4. Calibration v1 completed 272 calls on A100. Rowwise achieved 37/48 fully correct,
   ranking-only 46/48, state probe 37/40 (current label/limit 40/40). Compute could
   still choose the old optimum without history and with correct filtering.
   See history/CALIBRATION_V1_20260915.md, preserved in 744ae67 before next changes.
   Calibration implementation: 795fd8b.
5. Readiness v1: nh-readiness-v1, 192 fresh-only calls. Constructed error
   traps, independent label/order crossing, full versus relevant-column views,
   and current-state extraction. Completed: focused A/B 15/16 and 16/16 fully verified, factual X/Y each 5/16. See history/READINESS_V1_20260915.md.
6. Objective transfer v1 completed 128 trajectories / 320 calls: 117/128 B
   choices, 128/128 state and mask/copy correctness. Ten old choices clustered
   by row order/label; self/fresh gap did not grow with planning. See
   history/OBJECTIVE_TRANSFER_V1_20260915.md. Implementation: 99adf52.
7. Objective replication v1 COMPLETED: 512 trajectories / 1536 calls. 487/512
   verified B decisions, all state reports correct; 24/25 failures in one label
   rotation. Comparison fixes 3 and harms 5. No convincing self/depth effect.
   See history/OBJECTIVE_REPLICATION_V1_20260916.md. Implementation c994b6f;
   its notebook/source remain frozen.
8. Current preparation: nh-execution-readiness-v1. Fresh rowwise/ranked/state
   screen restores A/B/X/Y prerequisites with a prospectively fixed candidate
   and readiness criteria, then conditional separate-seed confirmation.
   768 screen + at most 512 confirmation calls. No live model result yet.
   See EXECUTION_READINESS_PLAN.md. No main pilot or factual-update claim.

Keep every historical notebook/export and its frozen source. Old approval and old
scores remain attached to old runs; do not pool versions or reinterpret historical
outcomes under a revised probe. Current user instructions and NEXT_AGENT_PROMPT.md
specify execution; old guides are archival context. Synthetic tests never count
as model results or human approval.
