# Research continuity and version history

*Updated through 2026-10-13.*

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
7. Historical preparation checkpoint: nh-objective-replication-v1, implementing
   commit c994b6f.
   512 trajectories / 1536 calls across all four cyclic label rotations and two
   seed replicates, with a separately scored explicit-comparison sibling at depth
   one. At that checkpoint, no real model run had occurred. See the archived
   [objective replication plan](OBJECTIVE_REPLICATION_PLAN.md); its preparation
   status is historical, not the current research status. Factual specificity
   remained unresolved.
8. **2026-09-18 — component qualification.** Under the frozen backend (Qwen3-8B
   revision `b968826d`, bf16, thinking enabled, A100), eligibility
   `ablation-bf16-think-1024-003` passed 384/384 and comparison
   `comparison-bf16-think-1024-001` passed 288/288, meeting every preregistered
   component gate. These qualify constrained eligibility and ranking, not the
   composed full instrument.
9. **2026-10-02 — pre-Oct-6 screen and qualification failures.**
   `screen-20261002-w08-v7-a1`: 56-case screen, 55/56 correct, zero valid-wrong,
   one truncation. `precal-20261002-w09-v7-a1`: 112-case qualification wave,
   110/112, two truncations; **not instrument-ready**, because the protocol
   requires zero truncations. `diag-20261002-w10-v8job-a1`: eight-case
   `job_sequence` diagnostic, 7/8, falsified. The failures remain part of the
   record.
10. **2026-10-03 — v9 diagnostic gate failure.** The v9 diagnostic failed its
    predeclared gate. Full instrument qualification never passed under the
    pre-Oct-6 design.
11. **2026-10-06 — audit-driven transfer-table pivot.** After an external audit,
    the owner replaced further prompt repair with the transfer-table assay.
    On each new instance, the old answer (X), the old rule applied to the new
    task (Z), and the correct update (Y) make different predictions, separating
    hysteresis as rule persistence from copying the old answer. The minimum
    meaningful effect was fixed at 5 percentage points (5pp); the unconditional
    behavioral contrast is primary.
12. **2026-10-12–13 — labeled 64-instance smoke pilot; completed 2026-10-13.**
    The smaller transfer-table smoke design (32 cells × 2 instances) ran on
    Modal across five arms, with 832 calls total: 832/832 records saved and
    hash-verified, zero errors. Every arm behaved as designed, 128/128
    strict-correct per arm. `fresh_A` and `A_no_change` each chose the A-optimal
    answer 128/128; `A_to_B` and `describe_to_B` chose the B-correct answer in
    all 256 switch slots, with zero old-rule carryover; `fresh_B` chose B 128/128.

    The descriptive read is a ceiling-level null, with zero variance between
    arms at pilot resolution. The assay as configured showed no detectable
    hysteresis pressure; discrimination may have been too easy because
    `fresh_B` alone was perfect. The smaller smoke design's 95% interval widens
    to about ±34pp and cannot settle the 5pp effect. This is neither evidence
    that NH exists nor evidence that it does not; no experimental result on
    NH exists.

    Caveats: three invocations (restart history; every record individually
    hash-valid); six `describe_to_B` planning records hit the 1024-token cap,
    a known, disclosed condition; Modal spend unsettled at report time.

The Oct 6–13 run records, evidence pack, Modal worker source, and environment/
pyenv pins are not yet in this repository. The October entries report the owner's
verified facts; they do not supply the missing artifacts for a repository audit.
The owner's next steps are a full 128-instance pilot of the same design, then a
powered held-out run. A harder-discrimination redesign is under consideration
because `fresh_B` alone solves the current tables.

Keep every historical notebook/export and its frozen source. Old approval and old
scores remain attached to old runs; do not pool versions or reinterpret historical
outcomes under a revised probe. The linked
[next-agent prompt](NEXT_AGENT_PROMPT.md) and
[objective replication plan](OBJECTIVE_REPLICATION_PLAN.md) exist under `docs/`
and describe the historical replication checkpoint; they are not current
execution instructions for the October assay. Current owner instructions govern
new work. Synthetic tests never count as model results or human approval.
